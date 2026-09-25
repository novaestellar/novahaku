# Storage RLS RETURNING-bug & Auth Escalation Attack Matrix

Two battle-tested procedures from PayStore (2026-08-15). Run both in the Supabase SQL Editor (dashboard session already logged in on the host).

## 1. `INSERT ... RETURNING` / upsert SELECT-policy denial

**Signature**: upload to a PRIVATE storage bucket fails with `new row violates row-level security policy`, while a sibling bucket with an identical INSERT policy succeeds. supabase-js `.upload()` upserts → SELECT before INSERT → SELECT policy evaluated on a row that doesn't exist yet.

**Diagnose (impersonate the real uploader, RLS ON):**
```sql
set request.jwt.claims to '{"sub":"<USER_UUID>","email":"x@y.z","role":"authenticated"}';
set role authenticated;

-- bare INSERT (may pass even when the bug exists)
insert into storage.objects (bucket_id, name, metadata)
values ('<bucket>', '<USER_UUID>/t.txt', '{"mimetype":"text/plain"}');

-- RETURNING variant (this is what supabase-js effectively does)
insert into storage.objects (bucket_id, name, metadata)
values ('<bucket>', '<USER_UUID>/t2.txt', '{"mimetype":"text/plain"}')
returning id;
```
If bare INSERT passes but RETURNING fails → SELECT policy is the culprit. Compare `pg_policies` for both buckets; the private one's SELECT usually gates on a paid-order helper (`can_access_delivery`) that can't be true for a new file.

**Fix (owner can read own folder; buyer still needs PAID order):**
```sql
drop policy if exists "delivery read check" on storage.objects;
create policy "delivery read check" on storage.objects
  for select to authenticated
  using (bucket_id = '<private-bucket>'
    and ((storage.foldername(name))[1] = auth.uid()::text
         or public.can_access_delivery(name)));
```
Verify with RLS ON: INSERT ✅, `INSERT ... RETURNING` ✅, UPDATE/upsert path ✅, then clean up test rows. No frontend redeploy needed — policy-only fix.

**Cleanup note**: don't `DELETE FROM storage.objects` raw if avoidable; use Storage dashboard UI or `storage.move_object`. Small 0-byte artifacts are acceptable leftovers — note them, don't block on them.

## 2. Role-escalation attack matrix

After confirming defenses EXIST (pg_trigger list, trigger bodies, RPC bodies, constraints), PROVE they hold by attacking. Impersonate a real non-admin user (use the seller's own UUID so policies apply honestly):

```sql
set request.jwt.claims to '{"sub":"<USER_UUID>","email":"x@y.z","role":"authenticated"}';
set role authenticated;

-- A1: escalate own role
update public.profiles set role = 'ADMIN' where id = '<USER_UUID>';
-- A2: insert a rogue ADMIN profile
insert into public.profiles (id, name, role) values (gen_random_uuid(), 'hacker', 'ADMIN');
-- A3: self-approve / self-unsuspend
update public.sellers set approved = false, suspended = true where user_id = '<USER_UUID>';
-- A4: call admin RPC as non-admin
select public.admin_set_seller_approved(id, true) from public.sellers limit 1;
```

Expected results (all blocked):
- A1 → `Success. No rows returned` (RLS silently filters; user has no UPDATE on others'/own admin fields)
- A2 → `ERROR: Hanya super admin yang dapat memiliki role ADMIN` (protect_admin_role trigger)
- A3 → `ERROR: Hanya ADMIN yang bisa mengubah status approval` (protect_seller_flags trigger)
- A4 → `ERROR: Hanya ADMIN yang bisa melakukan ini` (is_admin() gate inside SECURITY DEFINER RPC body)

**Critical: always `reset role;` between attack blocks** or subsequent queries run as the impersonated user.

**A3 false-positive trap**: if the seller is already `approved=true` and you only set `approved=true`, the trigger never fires (no actual change) → looks like it passed. Always flip to a DIFFERENT value than current state, or verify the row didn't change after a "successful" update.

**Defense inventory to confirm first** (all must be present):
```sql
-- triggers
select tgrelid::regclass, tgname from pg_trigger
where tgrelid in ('public.profiles'::regclass,'public.sellers'::regclass,'auth.users'::regclass)
  and not tgisinternal;
-- expect: on_auth_user_created, trg_protect_admin_role, trg_protect_seller_flags, (+cooldown)

-- sellers constraints: user_id UNIQUE, saweria_username UNIQUE, approved NOT NULL default false
select conname, pg_get_constraintdef(oid) from pg_constraint where conrelid='public.sellers'::regclass;

-- is_admin must resolve via profiles.role, not raw metadata
select prosrc from pg_proc where proname='is_admin';
```

## 3. Supabase SQL Editor automation quirks (browser_exec)

- Monaco is `monaco.editor.getEditors()[0]`; set query with `editor.getModel().setValue(sql)`.
- Run button: prefer the stable selector `document.querySelector('[data-testid="sql-run-button"]')` (text "Run Ctrl ↵") over index-based button hunting.
- Destructive statements (DROP FUNCTION, UPDATE, etc.) trigger a "Potential issue detected" confirmation modal — after clicking Run, click the modal's orange `Run query` button. Full remediation-phase details in `references/remediation-runbook.md`.
- SQL Editor executes ALL statements but the Results panel only shows the LAST statement's output. Run one query per execution to read each result.
- An error in any statement aborts the whole batch — split independent checks.
- Dashboard session cookies persist across browser_exec calls; no re-login needed.

### Dashboard SPA blank recovery (observed 2026-08-18)

The Supabase dashboard SPA can go fully blank mid-session: `document.body.innerText.length === 0` on every `supabase.com/dashboard/*` URL, reloads and new tabs stay blank, no console errors, `performance` shows the JS chunks loaded (Next.js hydration just never completes). Working recovery, in order:

1. `Target.getTargets` — list browser tabs; if an ALREADY-loaded dashboard tab exists (title like "SQL Editor | MULTI SELLER..."), `Target.activateTarget` it instead of navigating.
2. **Close every OTHER `type=page` target** so the harness binds to the live tab. If any other tab exists, `js()` keeps executing in the stale one and `window.monaco` stays undefined even though the SQL Editor tab is fine — this was the actual fix.
3. After consolidation: `ensure_real_tab()`, then Monaco `setValue` + run works.

If no loaded dashboard tab exists at all, the SPA is genuinely stuck. Do NOT burn calls re-navigating (each attempt lands blank). Fall back to finish the audit pass without the dashboard: cached dumps (`funcdefs*.json`, `rls_all.json`, `triggers_schema.json` in %TEMP% from earlier passes) + PostgREST probes with the anon key cover most remaining checks.

## 4. Business-logic audit (post-hardening pass)

After grants/RLS/RPCs are clean, trace the multi-item purchase flow end to end — access control can be perfect while the commerce logic leaks value. Known-class findings from PayStore (2026-08-18):

- **Multi-product delivery drops files**: delivery aggregation returns `min(case when ps.file_path <> '' then ps.file_path end)` — an order containing two file-products delivers only the first file. Keys and text content aggregate fine (`string_agg`), files do not. Fix: return a file list (array/rows), not a single path; frontend renders one download button per file.
- **Stock checked but not reserved at order creation**: `create_order` validates `stock >= qty` but only decrements on PAID (`worker_mark_paid`). With a 15-minute PENDING window, two buyers can both pass the check and both pay for the last unit; the `greatest(0, stock - qty)` floor lets the second order go PAID with 0 items delivered. Fix: reservation column/table at order creation + restore on EXPIRED/CANCELLED.

Both are invisible to the anon/grant/RLS probes of passes 1–3 — they only surface by reading `create_order`/`worker_mark_paid`/`get_order_delivery` bodies as a commerce flow, or from real multi-item order rows.
