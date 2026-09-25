# Supabase / BaaS Security Audit — Field Notes

Proven findings and verification techniques from auditing a production Supabase +
Cloudflare Pages + Worker storefront (PayStore). Applies to any BaaS frontend where
the anon/publishable key is public and RLS is the only backend.

## 1. SQL / RLS pitfalls

- **NULL comparison bypass**: `if v.buyer_id <> auth.uid() then raise ...` — when
  called unauthenticated `auth.uid()` is NULL, `uuid <> NULL` is NULL, the IF never
  fires. Use `is distinct from` AND an explicit `if auth.uid() is null then raise`
  first line.
- **`security definer` functions run as owner** — RLS does NOT protect the caller
  inside them. Every definer RPC must validate auth/role itself; a missing check =
  full-table privilege.
- **Grants are the real gate for RPCs**: `grant execute ... to authenticated, anon`
  means the function is callable by anyone with the anon key. Audit every
  `grant execute`/`revoke execute` line; a later `create or replace` migration can
  silently re-grant. Always audit the FINAL version of each function, not the first.
- **Storage policy substring matching**: `name like '%images/%'` matches
  `x/notimages/y.png` too. Use `(storage.foldername(name))[2] = 'images'` instead.
- **The `/storage/v1/object/public/...` render endpoint ignores RLS.** Securing a
  public bucket requires BOTH a tight SELECT policy and keeping non-public paths out
  of the bucket. Test: upload a `.txt` under a sneaky path, then GET it
  unauthenticated via the public URL.
- **Error-message oracles**: an RPC returning different messages for
  not-found / not-paid / access-denied lets anon probe order status. Unify messages
  on public functions.
- **Idempotency guards**: a worker RPC like `worker_set_order_tx` should include
  `and saweria_tx_id is null` so a leaked token can't overwrite an existing tx.

## 2. Secrets in migration SQL

- Migration files often contain `insert into secrets ... values ('token', '...')`.
  If those `.sql` files ship in the static-site root, the secret is PUBLIC — grep all
  `*.sql` for `insert into.*secret|token|password` before any deploy.
- Remediation order: rotate the secret in DB AND in the worker secret store, then
  redeploy excluding the file. Rotation alone is not enough while the file is live.

## 3. Cloudflare Pages deploy-artifact leakage

- `.pagesignore` support proved unreliable in practice. `--exclude` is NOT a valid
  flag on `wrangler pages deploy` (tested wrangler 4.115.0 — rejected). Working
  pattern: build a staging directory containing ONLY allow-listed files
  (`_deploy_clean.py` style: copy whitelist → deploy the staging dir), or try
  `.cfignore` (untested).
- **HTTP 200 on a missing path is ambiguous**: Pages serves the SPA fallback
  (index.html) for unknown routes. Verify with content inspection
  (`curl -s URL | head -c 200`), not status codes. A 0-byte body means genuinely
  absent; real file content means leaked.
- After deploy, re-curl every sensitive path and confirm fallback HTML, not content.
- `_headers` file at root sets CSP/HSTS/X-Frame-Options; verify via `curl -sI`.

## 4. Payment-flow audit (Saweria/QRIS pattern)

- Client must never mark orders PAID. Only a server-side worker holding a shared
  secret may call the mark-paid RPC after verifying payment status upstream.
- Check the payment QR is created server-side with amount from DB (anti-underpay)
  and `message = order_id` binding validated on verify (anti-replay across orders).
- **Order ID entropy**: `ORDER-` + 8 hex from `md5(random())` = 32 bits. With a
  public unauthenticated `get_order_payment_info` and no rate limit, the ID space is
  enumerable → status oracle. Use ≥12 hex / uuid and revoke anon grants.
- **Third-party render exfiltration**: a QR fallback like
  `https://api.qrserver.com/create-qr-code?data=<full QRIS string>` leaks the payment
  credential outside your system, and CSP whitelisting the host authorizes it.
  Fail closed instead; drop the host from CSP.
- Worker `/uid` + `/donate` "compat" routes left after a v2 rewrite remain an open
  relay (lookup/donate to ANY Saweria user). Remove dead routes.
- Worker down → silent fake-QR fallback (invalid CRC) = buyers shown unpayable QRs.
  Fail with a clear error instead.

## 5. Auth checks that look fine but aren't

- **Email confirmation**: Supabase toggle. Test with a FRESH signup (fresh random
  email): if the response contains `access_token` or `confirmed_at`, confirmation is
  OFF. Re-signups of an existing confirmed user return 200 with metadata — not proof.
- **Origin/Referer validation on Workers**: spoofable from curl/scripts (they are
  arbitrary headers outside browsers). Sufficient against casual browser abuse only;
  pair with a shared secret or CF headers for real trust.
- Suspended users keep valid JWTs ~1h; check `suspended` inside RPCs that matter.
- Seller DELETE on own shop can CASCADE buyer orders — check FK behavior before
  granting delete policies.

## 6. Probe technique (verified workflow)

- Use **control tests**: call the secret-gated RPC with a WRONG token first; it must
  fail with "unauthorized". Only if the wrong-token call fails is a success with the
  real token meaningful.
- **Non-destructive probes only** against production: use fictitious IDs
  (`ORDER-DEADBEEF`), expect "not found". Stop before any probe would create/alter a
  real order.
- Write multi-step probes as Python scripts (`urllib.request`) instead of inline curl
  in bash: nested `$(...)` + mixed quotes break repeatedly on Windows git-bash.
  Pages may 403 bare urllib — add a browser-like `User-Agent` header.
- Enumerate all public functions: `grep "create or replace function public\." *.sql`,
  sort -u, then audit every grant line. Unaudited RPC = untested gate.
- Supabase `sb_publishable_*` keys are NOT JWTs (base64 decode fails) — new key format.
