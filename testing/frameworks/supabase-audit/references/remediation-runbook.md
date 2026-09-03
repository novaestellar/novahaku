# Remediation Runbook — executing the fix phase (payment bypass)

Battle-tested PayStore 2026-08-18: migration execution, token rotation, fake-order cleanup, attacker BAN, verification — all agent-driven. Prereq: dashboards (Supabase + Cloudflare) already logged in on the host browser; wrangler auth active.

## 0. Principle
Never hand the user "run this in SQL Editor." User expects the agent to execute everything ("do it all for me, just open the browser"). browser_exec session cookies persist across calls; no re-login.

## 1. Running migrations in SQL Editor (browser_exec)
- Navigate `https://supabase.com/dashboard/project/<ref>/sql/new`, wait ~8s for Monaco (`window.monaco.editor.getEditors()[0]` exists).
- Inject: `eds[0].setValue(sql)` with the SQL passed through `json.dumps()` into the JS template.
- Run: `document.querySelector('[data-testid="sql-run-button"]').click()`.
- **Destructive modal**: DROP/UPDATE triggers "Potential issue detected". After the first click, wait ~2s, then click the modal's orange button whose exact textContent is `Run query` (filter enabled buttons by text match; NOT data-testid).
- Results: grid is virtualized — extract `[...document.querySelectorAll('.rdg-cell, [class*="cell"]')].map(c=>c.textContent).filter(t=>t&&t.trim())`; each cell text appears TWICE (dedupe). Only the LAST statement's result shows — run one query per click.
- Fallback when DOM extraction is flaky: `capture_screenshot()` + `vision_analyze`.
- Split migrations: run schema/token patches first, review the cleanup SELECT results, THEN run the cleanup UPDATEs. One batch aborting on error aborts everything.

## 2. Token rotation order (DB secret ↔ Worker secret)
Wrong order breaks legit payments. Correct order:
1. Run SQL migration that writes the NEW token to the secrets table first (e.g. `paystore_secrets` upsert on conflict).
2. Then update the Worker secret: `printf '<new-token>' | npx wrangler@4.115.0 secret put VERIFY_TOKEN`. Workers read secrets at runtime — **no redeploy needed**.
3. **Sync diagnostic**: hit a Worker endpoint that calls the token-gated RPC with a fake order id.
   - `{"error":"order tidak ditemukan"}` → token matches (RPC passed the auth gate, failed on lookup) = SYNCED.
   - `unauthorized` → desync = fix secret.

## 3. Fake-order cleanup + attacker BAN
```sql
-- A: REVIEW FIRST — group by buyer_email to identify the attacker
select id, total, buyer_email, paid_at, product_name
from orders where status='PAID' and saweria_tx_id is null order by paid_at;

-- B: restore stock-item-based stock (legacy products.stock decrements
--    cannot be auto-restored — flag for manual check)
update stock_items set is_sold=false, order_id=null, sold_at=null
where order_id in (select id from orders where status='PAID' and saweria_tx_id is null);

-- C: cancel fake orders
update orders set status='CANCELLED' where status='PAID' and saweria_tx_id is null;

-- BAN all throwaways by email DOMAIN pattern (attackers reuse one domain)
update auth.users set banned_until = now() + interval '100 years'
where email like '%<attacker-domain>%';
```
Verify zero left: `select count(*) from orders where status='PAID' and saweria_tx_id is null;` → 0.

## 4. Privilege matrix verification
```sql
select p.proname,
       has_function_privilege('anon', p.oid, 'EXECUTE') as anon,
       has_function_privilege('authenticated', p.oid, 'EXECUTE') as authenticated
from pg_proc p join pg_namespace n on n.oid = p.pronamespace
where n.nspname='public'
  and p.proname in ('mark_order_paid','worker_mark_paid','worker_set_order_tx',
                    'worker_get_payment_info','get_order_payment_info','create_order');
```
Expected after fix: dropped functions ABSENT from output; worker RPCs anon=t/authenticated=f; `create_order` anon=f/authenticated=t.

## 5. Post-fix live probes (anon key, no login)
- Dropped RPC → PostgREST 404 `PGRST202` "Could not find the function".
- Token-gated RPC with wrong token → 400 `unauthorized`.
- Removed Worker compat routes (`/uid`, `/donate`, `/status`) → 403/404.
- Worker `POST /pay` with empty body → validation error message, not 500.
- Sensitive live paths (`*.sql`, audit docs, deploy scripts) → SPA fallback BODY (Pages returns 200 for unknown paths — check content, not status code).

## 6. Signup restriction (e.g. Gmail-only) — two-layer enforcement
Battle-tested 2026-08-18. Frontend check = UX only; the real gate is a BEFORE INSERT trigger on `auth.users` (frontend is bypassable via direct API).

```sql
-- batch 1: validator function
create or replace function public.enforce_gmail_signup()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if lower(new.email) not like '%@gmail.com' then
    raise exception 'Hanya email @gmail.com yang bisa mendaftar';
  end if;
  return new;
end;
$$;

-- batch 2 (SEPARATE Run): trigger
drop trigger if exists trg_enforce_gmail_signup on auth.users;
create trigger trg_enforce_gmail_signup before insert on auth.users
for each row execute function public.enforce_gmail_signup();
```

**Pitfall — DDL batches can silently no-op in SQL Editor.** A batch combining CREATE FUNCTION + CREATE TRIGGER reported "Success. No rows returned" yet the function did not exist afterwards (batch swallowed by the destructive-confirm modal flow). Run DDL **one statement per Run click** and verify each two ways:
- Catalog: `select proname from pg_proc where proname = '<fn>';`
- Behavioral test, BOTH directions: direct INSERT into `auth.users` with a non-matching email → must fail with the trigger's RAISE message; matching email → must succeed. Then DELETE both test rows. `pg_trigger`/`information_schema.triggers` queries against auth.users can come back empty even when the trigger works — the behavioral test is the proof, not the catalog.

Notes:
- Existing accounts are unaffected (trigger fires on INSERT only). Banning pre-existing non-conforming accounts is a separate `update auth.users set banned_until...` step — confirm intent first.
- Frontend pair: block submit + toast before the API call; update input label/placeholder so users see the constraint.

## 7. Grant hygiene sweep (v15 pattern) — revoke over-granted EXECUTE

Deep-audit finding class: a SECURITY DEFINER RPC with no internal auth/ownership check but `grant execute to anon` (or authenticated) = anyone can run it. Example: stock-pop helper callable by anon → attacker marks seller stock "sold" without buying (inventory DoS). Also revoke EXECUTE on trigger functions — they only fire as triggers and need no callable grant.

```sql
-- internal helper only called from security definer RPCs: revoke all API roles
revoke execute on function public.pop_stock_items(text, uuid, integer)
  from public, anon, authenticated;
-- leftover test/dev functions with security definer: DROP them
drop function if exists public.tmp_test_del() cascade;
-- admin-gated RPCs: keep authenticated (is_admin() gate is internal), drop anon
revoke execute on function public.admin_delete_user(uuid) from public, anon;
-- trigger helpers: no EXECUTE needed by any API role
revoke execute on function public.handle_new_user() from public, anon, authenticated;
```

Revoke is SAFE for internal call paths — SECURITY DEFINER bodies run as the owner, so they can still call revoked functions. Verify live after:
```python
# anon probe of formerly vulnerable RPC → must be 401 now
POST /rest/v1/rpc/pop_stock_items {...nonexistent id...}
# 401 {"code":"42501","message":"permission denied for function ..."} = FIXED
```
Then re-dump the full grant matrix (json_agg one-shot, §4 style) and eyeball every row. Keep the migration file numbered in the project (`supabase-migration-v15.sql` style) so state is reproducible.
