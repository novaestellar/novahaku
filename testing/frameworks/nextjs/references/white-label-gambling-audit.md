# Worked example: superjponfire.com (white-label gambling platform)

Full reverse-engineering of a multi-tenant white-label gambling site's API surface.

## Stack fingerprint
- Next.js Pages Router (Build ID from `_next/data/<buildId>/<locale>/<page>.json`; pages served as `/<locale>/<page>`).
- Static assets on BunnyCDN: `NEXT_PUBLIC_CDN_URL=https://imajadulu.b-cdn.net/<version-tag>`.
- Real API is a multi-tenant gateway: `NEXT_PUBLIC_PORTAL_API_URL=https://v1008.p120p0ap1.xyz/v1` (brand `V1008`).
- Admin API: `NEXT_PUBLIC_COMPANY_API_URL=https://api.vsuperadmin.com/api/v1/` — nginx 403 from public internet, no bypass found.

## Env leak (all in client JS / `_next/data` JSON)
- `NEXT_PUBLIC_UNLEASH_FRONTEND_API_URL=http://unleash.unleash.svc.cluster.local:4242` — internal K8s hostname leaked client-side.
- `NEXT_PUBLIC_UNLEASH_FRONTEND_API_TOKEN=*:production.<hex>` — unleash token (not reachable externally; unleash is cluster-internal).
- WebSocket: `wss://v1008.wesopro.xyz/ws/v1`.
- Domain: `NEXT_PUBLIC_DOMAIN=https://superjp.com`, brand `V1008`, site `superjp`.

## Endpoint discovery (chunk grep)
Per-page chunk (`_next/static/chunks/pages/register-<hash>.js`) contains the full per-page API surface. Auth + player endpoints live in the app-level bundle. Grep patterns that worked:
```bash
grep -oP 'post\("[^"]+"' chunk.js | sort -u
grep -oP '"/public/[a-zA-Z0-9_/-]+' app.js | sort -u
grep -oP '.{0,50}public/auth/login.{0,50}' app.js   # context slice to recover request shape
```

## API surface found
- `/public/auth/login/` (POST) — live, username+password
- `/public/auth/me/`, `/public/auth/refresh/`, `/public/auth/logout/` (POST, 401 without auth)
- `/public/captcha/generate/` (POST) — returns `{captcha_key, captcha_image(base64 PNG)}` + `Set-Cookie: INGRESSCOOKIE=...`
- `/public/player/register/` — on `/v2` multi-brand URL only
- `/public/player/get/`, `/public/player/check/referral/?code=` — no-auth probes
- `/public/wallet/balance/`, `/public/rebate/balance/`, `/public/referral/`, `/public/promotion/*` — 401 (auth-gated)
- `/public/cms/web-images/` — public, returns logo/favicon paths
- `/api/bo` — backoffice prefix, not directly reachable (server-side proxy)

## Key gotchas
1. **`/v1` vs `/v2` split**: `public/captcha/generate` resolves ONLY on `/v1` with trailing slash (`/v1/public/captcha/generate/`); `public/player/register` resolves ONLY on the `/v2` multi-brand URL. Endpoints are spread across the portal and multi-brand bases.
2. **Missing `X-Realm` header → nginx 404**, not a JSON error. Add `-H "X-Realm: V1008"` to everything.
3. **Username enum confirmed**: `playerNotFound` vs `incorrectPassword` vs `locked` on `/public/auth/login/` distinguishes nonexistent vs wrong-pass vs brute-locked accounts.
4. **Login `errorObject.count` is a brute-force lockout counter, NOT a SQLi oracle.** `' OR '1'='1` changed the count (2→4) purely because each attempt increments the counter — the query is parameterized. Do not misread counter deltas as injection evidence.
5. **SQLi probes**: username validated `alphanumeric or a dot` server-side (injection dies immediately); password passes through but query is parameterized (count-delta is lockout). `--` triggers Cloudflare WAF; `' OR '1'='1` doesn't.
6. **Register requires**: `captcha_key`+`captcha_value` (from `/public/captcha/generate/`), `email`, `phone` (E.164 `+62...`), `payment_type` (`BANK` or `EPAYMENT`). Missing fields returned as a JSON validation map.
7. **Unleash/K8s URLs leak but aren't externally reachable** — they resolve only inside the cluster. Report as info-leak, don't chase them.

## Defensive report items (for the owner)
- `NEXT_PUBLIC_*` leaks internal K8s hostname (`unleash.unleash.svc.cluster.local`) + Unleash token to client.
- Username enumeration on login (`playerNotFound` vs `incorrectPassword`).
- No rate-limit on `/public/captcha/generate/` (returns captcha + sets cookie freely).
- Admin/company API (`api.vsuperadmin.com`) correctly firewalled with 403.
