---
name: nextjs-app-audit
description: 'Audit Next.js apps: extract + invoke server actions.'
version: 1.0.0
author: SeaGull Security Lab
license: MIT
metadata:
  hermes:
    tags: [security, pentest, nextjs, server-actions, rsc, api]
    related_skills: [api-gateway-recon, advanced-bug-hunting, web-exploit-test]
---

# Next.js App Audit (Server Actions Pentest)

## When to Use
- Target responds with `x-powered-by: Next.js` / RSC headers and has no visible REST API
- Need to test Next.js auth, order, redeem, admin server actions
- Any Next.js App Router target where the backend is server-action-only

Target stack: `x-powered-by: Next.js`, `/_next/static/chunks/*.js`, `self.__next_f.push(...)` RSC payloads, `vary: rsc, next-router-state-tree`. Backend usually hidden behind **Server Actions** — no REST surface on the main domain. Attack surface = server actions + `NEXT_PUBLIC_*` env leaking backend URLs + the underlying API subdomain.

## 1. Download chunks + extract server actions

```bash
curl -s <target>/<page> -o page.html
grep -oE 'src="/_next/static/chunks/[^"]*\.js"' page.html | sed 's/src="//;s/"//' | sort -u > chunks.txt
while read f; do b=$(basename "$f"); [ -f "$b" ] || curl -sL "https://<target>$f" -o "$b"; done < chunks.txt
```

App Router action ID → name mapping (works across chunk files):
```python
import re, glob
pat = re.compile(r'createServerReference\)\("([0-9a-f]{20,})"[^)]*?,"([A-Za-z][A-Za-z0-9]*)"\)')
for f in glob.glob('*.js'):
    s = open(f, encoding='utf-8', errors='replace').read()
    for m in pat.finditer(s):
        print(f"{m.group(2):40s} {m.group(1)}")
```
Pages Router: look for `"actionId":"..."` or `_next/data` JSON instead.

## 2. Invoke server actions directly

```bash
curl -s -X POST https://<target>/ -H 'Content-Type: text/x-component' \
  -H 'Next-Action: <action-id>' \
  -H 'Origin: https://<target>' \
  -H 'Referer: https://<target>/<page>' \
  -H 'Cookie: accessToken=<jwt>' \
  --data-raw '[{"email":"x@y.com","password":"pass"}]'
```
- POST to `/` (or the page the action lives on) with `Next-Action` header.
- Auth via `Cookie: accessToken=<jwt>` — server actions read JWT from cookie.
- Response is RSC flight: `0:{...}\n1:{JSON}` — extract with `re.search(r'1:(\{.*\})', body)`.
- **Payload shape matters**: object `[{"field":"v"}]` often required; plain array `["a","b"]` fails `Validation failed` (400). Try both. Action args map positionally when declared as `(page, limit, status)` — pass `[1,10,""]`.

## 3. Recover form schemas from chunks

Zod schemas ship in the page chunk with field names + validation messages:
```js
b.z.object({username:..., email:...refine(...), whatsapp:..., password:..., confirmPassword:..., termsAccepted:...})
```
Grep page-specific chunk for `z.object`, `refine(`, `defaultValues:{`, `placeholder:"` to learn exact field names incl. non-obvious ones (e.g. field `nomor` = whatsapp). Then the register/login call succeeds.

## 4. Find the real backend API

- Server actions proxy server-side to a backend; base URL leaks via env constants in chunks:
  `grep -ohE '(NEXT_PUBLIC_[A-Z_]+|https://[a-z0-9.-]+)' *.js | sort -u`
- **CDN subdomain ≠ API**: `cdn.*` is often S3/object storage (XML `<Error>` responses, `x-amz-request-id`). Real API is usually `api-*.domain/api` (Express-style JSON 404 `{"message":"Route not found"}`).
- On the API check CORS: `access-control-allow-origin: *` + `access-control-allow-credentials: true` = critical (any origin can read authenticated responses). Check response headers with `curl -sD -`.
- Fuzz routes: `/api/v1/<res>`, `/api/v1/admin*` — 403 vs 401 vs 404 tells you about authz middleware. `Invalid internal API key` = server-side secret, not client-leaked.

### Multi-tenant / brand-code API detection

Gambling/white-label Next.js apps often use a **multi-tenant API gateway** where the same backend serves multiple brands. Detection pattern:

1. **Env constants** in JS bundles reveal multiple API URLs:
   - `NEXT_PUBLIC_PORTAL_API_URL` — main player-facing API
   - `NEXT_PUBLIC_INTEGRATION_API_URL` — integration/third-party API
   - `NEXT_PUBLIC_COMPANY_API_URL` — admin/company API (often 403 from outside)
   - `NEXT_PUBLIC_MULTIBRAND_INTEGRATION_API_URL` — multi-brand variant
   - `NEXT_PUBLIC_PILOT_INTEGRATION_API_URL` — pilot/test variant
   - `NEXT_PUBLIC_WEBSOCKET_URL` — WebSocket (usually `wss://<host>/ws/v1`)
   - `NEXT_PUBLIC_BRAND_CODE` — brand identifier (e.g. `V1008`)
   - `NEXT_PUBLIC_SANITY_DOMAIN` — CMS/sanity domain

2. **X-Realm header**: these platforms require `X-Realm: <BRAND_CODE>` on every request. Without it, the API returns 404 (nginx `404 Not Found`, not JSON). With it, endpoints resolve. Always set this header when testing:
   ```bash
   curl -sk -X POST "https://<portal-api>/v1/public/auth/login/" \
     -H "Content-Type: application/json" \
     -H "X-Realm: V1008" \
     -d '{"username":"test","password":"test"}'
   ```

3. **Multi-brand base URL**: `NEXT_PUBLIC_PORTAL_API_MULTI_BRAND_URL` points to a `/v2` variant that accepts registration/player endpoints. The regular `/v1` portal often returns 404 for player endpoints, while `/v2` multi-brand resolves them.

4. **Backoffice prefix**: JS bundles may reference `/api/bo` as a backoffice API prefix. This is usually proxied server-side, not directly accessible from the client domain. Try on the admin API subdomain or through server actions.

5. **CDN distinction**: `NEXT_PUBLIC_CDN_URL` = static chunks (BunnyCDN, Cloudflare R2). `NEXT_PUBLIC_STATIC_FILES_URL` = image/media assets. Neither is the API — don't waste time fuzzing them.

## 5. Server action attack patterns

- `loginAdminAsUserAction` / impersonation — test, expect 403 without admin role.
- Public read actions (`getPackage`, `get*List`, `get*Page`) — test WITHOUT auth; often leak pricing/catalog data.
- IDOR: pass `userId` params — but many actions IGNORE client params and derive user from JWT; verify by calling with another user's id and comparing output before claiming IDOR.
- JWT in cookie: decode payload (`base64.urlsafe_b64decode`), test alg:none + weak secrets; HS256 + `exp` check usually solid.
- `redeem*` / `requestWithdrawal` / `updateProfile` — business-logic surface; errors like `Gift card not found` confirm validation exists.

## Pitfalls

- **Tokens get masked in terminal output** (`eyJhbG...xxxx`) — ALWAYS `curl -o resp.txt` and process via Python; never read tokens from stdout.
- 200 + generic RSC body without `1:{...}` JSON = action rendered page / auth failed. Check for `Unauthorized` in JSON.
- `{"code":400,"errors":"Validation failed"}` is generic — recover the schema from JS first (step 3), don't blind-guess.
- 500 `An unknown error occurred` on empty/invalid input = server error, not necessarily a vuln.
- Registration may be restricted to specific email domains (zod `refine` on gmail/yahoo) — use a Gmail alias (`user+tag@gmail.com`) for test accounts.
- Rate limits: keep probes polite; parallel bursts on money endpoints (redeem/withdraw) = race-condition candidates worth a separate test.

## Worked example

See `references/premiumportal-audit.md` — full premiumportal.id audit (action IDs, payload formats, findings) as a reference case.

See `references/white-label-gambling-audit.md` — superjponfire.com white-label gambling platform: multi-tenant `/v1` vs `/v2` base split, `X-Realm` brand header, username enumeration, the `errorObject.count` false-SQLi-oracle trap, and env leaks (K8s Unleash URLs).
