# POS / SaaS Black-Box Audit via Next.js Bundle Mining + Sandbox-Org PoC

Recipe proven against a production Next.js + Supabase POS platform (multi-tenant,
RPC-based business logic) with zero access to source or Supabase dashboard.
Read-only against other tenants; invasive PoCs only inside a self-created sandbox org.

## Phase 0 — Bundle mining (schema + RPC discovery)
The OpenAPI endpoint `/rest/v1/` with `Accept: application/openapi+json` often
returns **empty `definitions`** under the anon role. The JS bundle is the better source:

1. Fetch `/`, `/login/`, `/daftar/`, `/dashboard/` etc.; collect every
   `/_next/static/chunks/*.js` ref; download each chunk.
2. Grep chunks for:
   - `.from("table_name")` → table list
   - `.rpc("fn_name", {p_x: ..., p_y: ...})` → RPC names **and exact payload keys**
     (JS object literal right at the call site — this IS the signature).
3. If a bundle call site is minified past recognition, POST the RPC with a bogus
   single param: the `PGRST202` error message enumerates all overloads, and the
   `"hint"` field sometimes lists the full parameter set of the nearest match.
4. `?select=zzz_nonexistent_col` on a table confirms table existence via
   `column <table>.zzz does not exist` (mild schema disclosure; note it, but RLS
   hardening is the real fix, not error suppression).

## Phase 1 — Anon read sweep
- `GET /rest/v1/<table>?select=id&limit=0` + `Prefer: count=exact` → row count from
  `Content-Range` header (`*/N` or `0-0/N`) without downloading data.
- **Server returns HTTP 206 (not 200) for this** — scripts that only accept 200
  report every table as broken. Accept both.
- `GET /auth/v1/settings` → `mailer_autoconfirm`, `anonymous_users`, enabled providers.
- Read every table that counts >0; record which columns carry PII (phone, address).

## Phase 2 — RPC authorization probe matrix
Probe **every** RPC from the bundle list, as both **anon** and **authenticated**
(sign up one test account; `mailer_autoconfirm=true` hands back a token instantly),
always with **nil-UUID args** so nothing real is touched:

```
POST /rest/v1/rpc/<fn>  {"p_order_id":"00000000-...","p_outlet_id":"00000000-...", ...}
```

Classify responses:
| Response | Meaning |
|---|---|
| 401 `permission denied for function` | EXECUTE revoked — good |
| 400 `Akses ditolak` / `Anda tidak berwenang` | auth check runs FIRST — good |
| 400 `Order tidak ditemukan` / data lookup error | **lookup runs BEFORE authz check — suspicious**; a real ID may pass. Flag for source review. |
| 200 with business error (`order_not_found`) | function EXECUTES for the caller — authorization missing or downstream-only |
| **204 / 200 success on nil ID** | **no authz at all** (e.g. a counter-increment RPC) — vulnerability |

Same-nil-ID comparison across RPCs localizes per-function gates cheaply.

## Phase 3 — Price-tamper PoC (the money bug)
POS/order RPCs commonly accept client-computed money: `unit_price`, `p_subtotal`,
`p_discount_total`, `p_tax_total`, `p_grand_total`, `p_amount_paid`. Server never
reconciles against `menu_items.base_price` + modifier deltas → free products.

**Do NOT prove this on another tenant's outlet.** Use the sandbox-org method:

1. With the test account, call the app's own onboarding RPC
   (`create_organization_and_outlet` pattern) → get your own `org_id` + `outlet_id`.
2. INSERT one menu item at a round price (e.g. 50000) into YOUR outlet.
3. Create a payment method row (cash) in YOUR outlet — order RPCs usually
   NOT-NULL-require `payment_method_id`; a nil UUID fails with a constraint error
   that itself confirms server-side payment row creation.
4. Call the order RPC with `unit_price=1, grand_total=1, amount_paid=1`.
5. Read back the order: if stored totals are 1.00 → **proven**. Screenshot/record
   the exact JSON in/out.
6. **Cleanup, in FK-safe order** (child rows first):
   orders → payments (filter by `order_id`, there is usually no `outlet_id` column)
   → payment_methods → menu_items → outlet →
   null out `profiles.organization_id` (PATCH) → organizations.
   Verify each with a follow-up GET returning `[]`.
   Note the audit account still exists in `auth.users`; tell the owner to delete it.

This method upgrades "logic-level suspicion" to "production-proven exploit"
while touching zero rows of any real tenant — it satisfies the consent gate
because the invasive act happens entirely inside attacker-owned data.

## Phase 4 — Report shape that owners act on
Two files work well: main audit (findings + what's already good) + bypass addendum
(PoC transcripts + per-finding SQL fix). Always include:
- **PROVEN SAFE list** (write paths denied, cross-tenant read empty, HSTS, etc.)
  so the owner doesn't break working defenses while panic-fixing.
- Reproduction one-liners per finding.
- Explicit note that the **anon key itself is not a finding** (owners always ask;
  the leak is the RLS, not the key).

## Phase 5 — Re-audit after owner patching
Owners patch between audits. Verify what actually changed — never assume a fix
covered everything:

1. **Full table sweep again.** Owners revoke grants on the headline tables
   (`orders`, `profiles`, `promo_codes`, `loyalty_*`) and miss sibling
   menu/config tables. Observed after one fix round: `dining_tables`,
   `discounts`, `menu_categories`, `menu_item_variants`,
   `menu_item_modifier_groups`, `modifier_groups`, `modifiers` still leaked.
   401 = grant removed; 200+data = still open.
2. **RPC matrix again, as anon.** Previously exploitable RPCs should now be
   401 `permission denied for function`. If an old signature returns PGRST202
   `no matches found`, the **signature changed** (params added/removed) — re-run
   Phase 0 on the fresh bundle and retry with the new call site.
3. **Watch for new tables** (e.g. `audit_logs` added between audits). Probe them:
   DELETE may return 204 while RLS silently drops the row — verify with GET and
   report leftover IDs for admin cleanup. They also create FK cleanup blockers
   (outlet/org delete fails with 23503 until the referencing rows are gone).
4. **Re-check auth settings** (`mailer_autoconfirm` often stays `true` through
   patch rounds) and storage object URLs (harvest `image_url` from readable
   tables; `/storage/v1/bucket` returning `[]` does NOT mean no buckets —
   object paths can still be world-readable).
5. **Re-run the sandbox PoC with the NEW RPC signature** to prove whether the
   core money bug is fixed. Signature churn (e.g. dropping `p_cashier_id` in
   favor of shift-based auth) is NOT price validation — the tamper may still
   land end-to-end (order stored with tampered totals, payment completed).
6. **Output a status table** — patched / still open / new — against the previous
   report's finding IDs so the owner sees progress and gaps in one view.
