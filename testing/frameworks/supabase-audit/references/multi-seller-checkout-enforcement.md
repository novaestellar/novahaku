# Multi-Seller Checkout Enforcement (single payment recipient)

For marketplaces where each order settles to ONE seller handle (Saweria QRIS username, single QRIS merchant, non-split payment rails): enforce **1 cart → 1 seller → 1 order → 1 QRIS → 1 recipient**. Mixed-seller orders misroute money: QRIS pays one seller, delivery includes the other seller's product.

## Layered enforcement (all four layers required)

Frontend layers are UX/guidance. The RPC check is the actual gate — direct REST/RPC calls skip everything else.

### Layer 1: addToCart blocks mixed sellers (frontend UX)
On add, compare the cart's current seller vs the new product's seller. Different → confirm dialog: "Clear cart and start with the new seller's products?" Accept = replace cart; decline = abort. Never allow two sellers in one cart.

```js
const cartSellerId = this.getCartSellerId(); // seller of first valid cart item
if (cartSellerId && cartSellerId !== product.sellerId) {
  this.askConfirm(`Keranjang sudah berisi produk dari ${oldSeller.name}. Checkout hanya bisa 1 toko per pesanan. Kosongkan keranjang dan mulai dengan produk dari ${newSeller.name}?`, true)
    .then(ok => { if (!ok) return; this.cart = [{ productId, quantity: cappedQty }]; this.saveState(); this.updateCartBadge(); });
  return;
}
```

### Layer 2: sanitize persisted carts on load
Carts persisted in localStorage from older versions may already be mixed or reference deleted products. Run once after products load: keep only items of the first valid seller, drop deleted/out-of-stock items, cap qty to current stock, toast how many were dropped.

### Layer 3: guard at checkout entry
`items.some(i => i.prod.sellerId !== sellerId)` or empty → reject before RPC.

### Layer 4: server-side RPC check (the real gate)
Inside `create_order` (SECURITY DEFINER), in the item loop with `for update` row locks:

```sql
if v_prod.seller_id <> p_seller_id then
  raise exception 'Produk bukan milik toko ini';
end if;
```

The order row stores `seller_id` + `saweria_username` once from the target seller, so payment + payout attribution is unambiguous.

## Companion money-flow checks

- **Stock race**: `create_order` that only checks `stock >= qty` but decrements at payment-confirm leaves a double-sell window (both buyers can pay the last item). Fix if it matters: reserve stock at order creation, restore on EXPIRED/CANCELLED.
- **Multi-item delivery aggregation**: `string_agg(...)` for keys/content covers all products; `min(case when file_path <> '' ...)` returns only the FIRST file — multi-file orders need an array/array_agg or multiple delivery rows.

## Auditing offline (no live SQL needed)

When the Supabase dashboard SPA goes blank (body empty, Monaco never hydrates), trace logic from local dumps instead of blocking:

```bash
# funcdefs dumps are lists of {"proname": ..., "def": <pg_get_functiondef>}
python -c "import json; [print(f['proname']) for f in json.load(open('funcdefs_full.json', encoding='utf-8'))]"
# then print f['def'] for the function under review
```

Search for the single-seller check, item loop, and status transitions directly in the dumped SQL. Live probing via RPC probes (curl with anon key) still works independently of the dashboard.
