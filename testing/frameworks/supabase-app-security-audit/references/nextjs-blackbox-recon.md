# Blackbox recon: Next.js/Turbopack app on Supabase (no source access)

Proven on gevixa.my.id (Aug 2026): client-rendered Next.js app, all routes return
HTTP 200 without auth (guard is client-side JS). Real attack surface = Supabase
project behind the anon key. Zero source/SQL access needed.

## 1. Extract project ref + anon key from JS bundles

```bash
# Route pages are client-rendered shells — fetch any protected route, e.g. /dashboard/
curl -s https://TARGET/dashboard/ -o dash.html
grep -oE '/_next/static/chunks/[a-z0-9_-]+\.js' dash.html | sort -u > chunks.txt
mkdir gevixa_chunks && cd gevixa_chunks
while read p; do curl -s "https://TARGET$p" -O; done < ../chunks.txt

grep -ohE 'https://[a-z0-9]+\.supabase\.co' *.js | sort -u          # project ref
grep -ohE 'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}' *.js | sort -u  # anon JWT
```

Save the key to a file (`anonkey.txt`). NEVER pipe it through terminal/patch/chat
context — the harness redaction pipeline replaces it with an ellipsis placeholder
silently and every subsequent request 401s "Invalid API key" with a key that LOOKS
fine in logs. Probe scripts read from disk:

```python
key = open(r"C:/.../anonkey.txt").read().strip()
```

Symptom of redaction corruption: `401 {"message":"Invalid API key"}` on requests
that should work, immediately after routing the key through terminal output.

## 2. Enumerate schema from the bundle

```bash
grep -ohE '\.from\("[a-z_]+"\)' *.js | sort | uniq -c | sort -rn   # all tables
grep -ohE '\.rpc\("[a-z_]+"' *.js | sort -u                        # all RPCs
grep -ohE '\.storage\.from\("[a-z_-]+"\)' *.js | sort -u           # buckets
```

This is the complete probe target list — no SQL access required.

## 3. Anon READ sweep (PostgREST)

For each table: `GET /rest/v1/<table>?select=*&limit=2` with
`apikey: KEY` + `Authorization: Bearer KEY` headers only (no session JWT).

Interpretation:
- 200 + rows → RLS missing/open for SELECT → CRITICAL in multi-tenant apps
  (cross-org data visible to anonymous callers).
- 200 + `[]` → policy exists but filters anon out (safe for reads), or table empty.
- 401 → RLS denies anon outright.

Row counts: `?select=id&limit=1` + read `Content-Range: 0-0/N` header.
Cross-tenant proof: `select=organization_id,name&limit=50`, count distinct org ids
visible to anon.

## 4. Anon WRITE probe WITHOUT touching production data

Ambiguity problem: an UPDATE/DELETE with a fake UUID filter returns `200 []` whether
RLS blocked it OR it matched 0 rows. Two safe disambiguation techniques:

a) **Fake-ID probe**: `PATCH /rest/v1/orders?id=eq.00000000-0000-0000-0000-000000000000`
   with `Prefer: return=representation`. 200 [] alone is inconclusive — combine with (b).
b) **No-op update on a REAL row**: PATCH one known row setting a column to its own
   current value (`{"rounding_adjustment": 0}` when it's already 0), with
   `Prefer: return=representation`.
   - 200 + the row returned → UPDATE policy is OPEN to anon → CRITICAL.
   - 200 + `[]` → RLS filtered the row → writes blocked (combined with (a), proven safe).
   - 4xx → denied.
   Zero data mutation occurs because the value is unchanged.
c) Column-existence bonus: PATCH with a wrong column name returns
   `400 PGRST204 "Could not find the 'x' column"` — proof the request reached the
   table (not blocked at policy level) and leaks schema info.

## 5. Auth settings + RPC probes

- `GET /auth/v1/settings` (public): check `mailer_autoconfirm` (true = signup without
  email verification → HIGH), `external.google`/`email`, `anonymous_users`.
- RPCs unauth: `POST /rest/v1/rpc/<fn>` with `{}` body.
  `401 42501 permission denied` = grant revoked (good). `404 PGRST202` = function
  exists but requires named params (probe further). `200` = callable anon → inspect
  the body for auth checks (SECURITY DEFINER bypasses RLS).

## 6. Storage

`POST /storage/v1/object/list/<bucket>` with `{}` body. `404 NoSuchBucket` = bucket
referenced in code but not created (dormant, note only). Public URL probe:
`GET /storage/v1/object/public/<bucket>/` — `InvalidKey` error = bucket exists and
public path is live (probe real object names next).

## 7. Non-Supabase checks that still apply

- Security headers via `curl -sI` (gevixa had excellent headers BUT CSP with
  `unsafe-inline` + `unsafe-eval` → XSS mitigation crippled → MEDIUM).
- `Access-Control-Allow-Origin: *` on all responses → note as finding.
- Placeholder meta still live (e.g. `google-site-verification` =
  "your-google-site-verification-code") → LOW.
- robots.txt disallow list leaks internal route inventory → LOW/info.

## Reporting shape that worked

Severity table (CRITICAL cross-tenant READ leak w/ PoC curl → HIGH autoconfirm →
MEDIUM CSP/ACAO → LOW placeholders/robots), then explicit "proven safe" list
(writes blocked, no .env/.git, headers good), then ordered fix list
(RLS policies first, auth config second). Offer to patch SQL directly when you have
dashboard access.
