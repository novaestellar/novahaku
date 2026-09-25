# Pentest akundigital.id — Laravel + klikqris MY PG (2026-08-23)

Authorized pentest (friend asked for it to be tested). Detailed technical notes from a real session.

## Stack fingerprint
- Laravel (PHP) + Vite assets `/build/assets/app-*.js`, `app-*.css`
- Cloudflare CDN in front; hosting CloudLinux shared `/home/robt4485/laravel/`
- Session cookie custom: `akundigitalid-session`; `XSRF-TOKEN` cookie
- WAF: Imunify360 (CloudLinux) — blocks curl on some endpoints, JS challenge on `/admin`
- Payment gateway: **klikqris.com** mode **MY PG** (own QRIS merchant, funds directly to merchant account)

## Finding: debug mode ON (HIGH)
```
curl -H "Accept: application/json" https://akundigital.id/api/nonexistent
```
→ Full JSON: exception class, file paths (`/home/robt4485/laravel/vendor/laravel/framework/...`), line numbers, full trace. Confirmed info disclosure.

## Finding: model enumeration via NotFoundException
| Path | Error |
|---|---|
| `/kategori/abc` | `No query results for model [App\Models\Category] abc` |
| `/produk/abc` | `No query results for model [App\Models\Product] abc` |
| `/toko/abc` | `No query results for model [App\Models\SellerProfile] abc` |
| `/blog/abc` | `No query results for model [App\Models\Post] abc` |
Route that does not exist: `The route X could not be found.`

## Finding: cart qty mass assignment
`POST /cart/update` with `items[52][qty]=99999` → total Rp 35,000 → **Rp 3,499,965,000**. Negative qty `-1` → item removed from cart (not negative total). No upper bound validation.

## Finding: direct checkout skip cart
`POST /checkout/{product_id}` (from form `#directCheckoutForm`) only needs `_token` + `additional_info` → directly creates order:
```
Location: /pay/INV-20260823181344-1PHIYQ   (order #465)
Total: Rp 35.000 + kode unik 363 = Rp 35.363
Status: UNPAID → EXPIRED ±30 minutes
```

## Payment page (`/pay/{invoice}`)
- Displays invoice, subtotal, unique code, total, QRIS image, WIB countdown, order chat
- QRIS image URL: `https://klikqris.com/storage/qris_mypg/qris_{invoice}_{unix_ts}.png`
- `Refresh status` button = `<a href="/pay/{invoice}">` → only reloads page (not a status endpoint)

## Webhook endpoint discovery (key!)
Probe `POST /webhook/{provider}`:
```
/webhook/klikqris  → 422 "Payload tidak valid."              (route EXISTS)
/webhook/mypg      → 401 "Merchant ID tidak valid."           (route EXISTS)
/webhook/my-pg     → 404 "The route webhook/my-pg could not be found." (does not exist)
```

**Validation-order leak** (different payload → different error):
```
order_id + status=PAID + amount                → 422 "Payload tidak valid."
+ signature=abc                                → 422 "Metode pembayaran order (MYPG) tidak sesuai dengan webhook endpoint (KLIKQRIS)."
order_id + status=settlement + signature       → 422 "Status pembayaran tidak valid."
merchant_id=1 + ...                            → 401 "Merchant ID tidak valid."
```
Error order = validation order: schema → merchant_id → method → status → (signature).

## Provider docs (klikqris.com/dokumentasi-api) — original format
**MY PG webhook payload** (that must be received by `/webhook/mypg`):
```json
{
  "status": "success",
  "message": "Payment received successfully",
  "data": {
    "order_id": "INV-123456",
    "amount_request": 30000,
    "amount_paid": 30021,
    "payment_date": "2026-01-22 08:44:52",
    "status": "PAID",
    "merchant_id": "MERCHANT_ID_ANDA",
    "via": "QRIS",
    "signature": "8n3v9z...1738681234"
  }
}
```
Signature scheme: "compare callback signature with the initial create response signature". Auth header: `x-api-key` + `id_merchant`.

**PG KlikQRIS webhook payload**:
```json
{
  "order_id": "DIRECT-176835469862-8460-202601252147",
  "status": "PAID",
  "amount": 1000,
  "total_amount": 1215,
  "payment_date": "2026-01-25 21:48:01",
  "created_at": "2026-01-25 21:47:42",
  "updated_at": "2026-01-25 21:48:01",
  "keterangan": "Pembayaran Paket A",
  "direct_url": "https://klikqris.com/payqris/176835469862/INV-123456",
  "signature": "8n3v9z...1738681234"
}
```
Sandbox: `https://klikqris.com/api/sandbox/qris/create` + public simulator at `/public/sandbox/simulate` (needs signature from create response).

## Rate limit & timing
- `POST /checkout/{id}` → 429 `ThrottleRequestsException` after several attempts (strict rate limit)
- Order EXPIRED ±30 minutes; creating new order must wait for rate limit reset

## Not yet complete (for follow-up)
1. `/webhook/mypg` needs valid `merchant_id` + real signature — merchant id not found from page/source (try: register free klikqris → get own merchant_id → check if validation is only "field exists" not "value matches")
2. `/pay/{invoice}/confirm` route exists (POST) but response only reloads page — parameters not yet found
3. Price manipulation checkout (price=0, total=0) — cannot test yet due to rate limit; order already expired
