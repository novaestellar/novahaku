# Worked Example: premiumportal.id Audit (2026-08)

Full audit of a Next.js App Router e-commerce/premium-access portal. Credentials provided by the operator were valid; test account created for deeper testing.

## Stack fingerprint
- `x-powered-by: Next.js`, `Server: cloudflare`, `vary: rsc, next-router-state-tree`
- Turbopack chunks: `/_next/static/chunks/<hash>.js`
- `robots.txt` = Cloudflare-managed content signals (not useful)
- Subdomains: `ppe.premiumportal.id` (extended app), `api-ppe.premiumportal.id/api` (Express backend), `cdn.premiumportal.id/be` (S3 storage!), `reseller.premiumportal.id`

## Key extraction results

### Server actions (main site) — 35 total
```
loginAction               7f62d629ee4fd10eb00208cd9008d0cac92ae31733
registerAction            7fee68acc0316ecdf20801eaa8acfeef15c7af6d17
logoutAction              7f9f0adccbc8e2aa75e11b76b6bbd0fdbbf111224a
refreshTokenAction        7f00682afb453bb96fe3040cb0583d2215afefe97e
forgotPasswordAction      7f3542e2e006275803e41ed42e3dfd0b6afbb047eb
resetPasswordAction       7f2ab3491c4ac633017f2fa142b9767205e8463c4d
loginAdminAsUserAction    7ff6b5f13543871095793f9a3f823398433d275e13
logoutAdminAsUserAction   7fdf659bed65727513d7a79fd9779841cf1d3f7bd0
getPackage                009e30211f74f6218a2d82f149abae48be3d9e7602
getExtendedPackage        000d43365013d55dc17982bd79171fbd9d04b2fc2d
getPackageItem            009a003c47a79028a75fd707ff7e7ebaf6124f14c6
getTermsAndConditions     002f68473b47f91c52e6c5393d4549cde13b5da3c5
getVideoLandingPage       00842713917ce11ccee0398f52b74018af9df1d7da
getUserPackages           009433f401d4480e0391f8fb91a7714969803c7812
getUserAccounts           40b913ee00a4431eb4e8979f2f90018d45cc639506
getAffiliateProfile       40ecfb17f6b1f363fd6c854b60818c4fa58567cf2e
getReferredUsers          789a4ec8192bedf1b0291419c648b0c1e42046bcf0
getWithdrawalHistory      7c9550752f5f3fbb875097dc28313d58d4ea7ade53
getAffiliatorByCode       4078d80f417ed100562f99fab3e9b102b11d8ee421
checkAffiliatePayment     00fd916cf256bbb8b19c8da6ed83df9ffa3974a6f7
redeemResellerCode        4003204908402c99b78884a316a9e8687d428c3b9d
registerAffiliate         40d07f8f86248b1001369e0a1802055c54466ba182
requestWithdrawal         401394ad1aecf310adb5022fdb717935bff8c13d28
updateAffiliate           401fd05b26bf83ea503df8ad1e3bcb1ce74b1edf6f
updateUserProfile         40a5f9b6a556bc6e4f3a975c7627cad00851a83896
updateUserPassword        40c55b58a58726ef9f2b2ba94628b2806a40576b3e
getUserCanva              00a6864a834a6bcd3c6c3b89c3f7f89ecc2d1b9b13
getInformation            406fc2ec1736a79fe574eec42ed5d4be3ef3380142
getActivePromotionalDialog 00c796b0eb38414b7595af9c1ea2f3e7c0cc50535f
getDownload*              00ba29f8... / 00dc000f... / 00a99433... / 00843003...
record*Download            40dbf302... / 40981a82...
```

### PPE (extended) server actions — 5 total
```
loginAction                   40c24e889c95095fa333cd663878d9dcbd2dc41ee4
logoutAction                  00e53a48a649be416999e08a86dc50953c3cf5873a
getUserExtendedPackageAction  00bec3c120eca125cef95250841c79645b1c995e03
listStorageAction             40ce49c2abd4190aa85ee7b2c10d9e6c73b5699055
updateUserProfileAction       400744d5a882ff28e07a5b350c9776213330573dea
```

### PPE env constants (leaked in chunk 0q9qvsi3d9y3n.js)
```js
NEXT_PUBLIC_API_URL: "https://api-ppe.premiumportal.id/api"
NEXT_PUBLIC_CDN_URL: "https://cdn-ppe.premiumportal.id/be"
```

### PPE API routes (from chunk, fetchWithAuth template literals)
```
POST /v1/chat/conversations/{id}/messages          (multipart FormData)
GET  /v1/chat/conversations/{id}/messages/{mid}/stream
POST /v1/chat/conversations/{id}/messages/retry
POST /v1/chat/conversations/{id}/messages/abort
PATCH /v1/chat/conversations/{id}/messages/{mid}/activate
GET  /v1/chat/conversations
GET  /v1/storage   → {files, currentUsage, limitBytes: 104857600, ...} pagination
GET  /v1/projects  → {"message":"Berhasil","status":200,"data":[]}
GET  /v1/admin*    → 403 "Invalid internal API key"
```

## Payload formats that worked

### Login (main site)
```bash
curl -s -X POST https://premiumportal.id/ -H 'Content-Type: text/x-component' \
  -H 'Next-Action: 7f62d629ee4fd10eb00208cd9008d0cac92ae31733' \
  -H 'Origin: https://premiumportal.id' \
  --data-raw '[{"email":"...","password":"..."}]'
# → {"success":true,"data":{"data":{"accessToken":"...","refreshToken":"...","exp":...}}}
```
Plain array `["email","pass"]` → `Validation failed`. Object wrapper required.

### Register (field names recovered from zod schema in chunk a4e644f07d8e6b3c.js)
```js
// email restricted to gmail.com / yahoo.com / yahoo.co.id via refine()
// fields: username, email, nomor (whatsapp), password, confirmPassword, termsAccepted (boolean, true required)
```
Working call:
```bash
--data-raw '[{"username":"testuser001","email":"user+test001@example.com","nomor":"6281234567890","password":"TestPass123!","confirmPassword":"TestPass123!"}]'
# → {"success":true,"data":{"data":null,"message":"Pendaftaran berhasil"}}
```
Gmail alias `user+tag@gmail.com` accepted — no email verification enforced.

### Authenticated read (JWT in cookie, NOT Authorization header)
```bash
curl -s -X POST https://premiumportal.id/ -H 'Next-Action: 009433f401d4480e0391f8fb91a7714969803c7812' \
  -H 'Cookie: accessToken=<jwt>' --data-raw '[{}]'
# → getUserPackages returns own user data; userId param IGNORED (no IDOR)
```

### listStorageAction (PPE) — string pagination args
```bash
--data-raw '[{"page":"1","limit":"20"}]'
# limit clamps to 200, page echoes back — no traversal beyond own quota
```

## Findings summary
- **HIGH** CORS wildcard on api-ppe: `access-control-allow-origin: *` + `access-control-allow-credentials: true`
- **MED-HIGH** 5+ public server actions leak catalog/pricing (getPackage etc.) without auth
- **MED** No email verification on register; no HSTS/CSP/XFO; login no rate limit
- **LOW** Tawk.to chat widget (supply-chain); ipinfo.io client-side token call
- Not exploitable: JWT alg:none rejected (401), HS256 secret not in common wordlist, admin API key server-side only, IDOR params ignored

## JWT notes
- HS256, payload `{id, username, email, iat, exp}`; exp = ms epoch in login response but s in JWT
- Cookies: `accessToken` / `refreshToken`, domain `.premiumportal.id` (shared across subdomains)
- PPE login uses same creds, returns separate PPE JWT
