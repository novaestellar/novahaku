# Client-Side Role Spoofing Prevention

**Attack vector**: a non-admin user intercepts the `profiles` response in DevTools (fetch interceptor, `fetch` override, proxy) and overrides `role` to `'ADMIN'`. The frontend trusts `currentUser.role` from the intercepted response and renders the full admin dashboard — user data tables, suspend buttons, delete controls, revenue stats, all seller/order details. The backend RPCs (`admin_set_user_suspended`, `admin_delete_user`) are `SECURITY DEFINER` + `is_admin()` and WILL reject the actual mutation call, so the attacker can't mutate anything, but the admin UI with all sensitive data is fully exposed.

**Root cause**: frontend gates admin UI on `profiles.role` from a client-side response that can be spoofed. The RLS policy `profiles read own or admin` returns the real row, but the attacker overrides it before JavaScript reads it.

## Fix pattern (4 changes, all frontend)

### 1. Add `adminVerified` flag (constructor)

```js
this.adminVerified = false; // only true after server-side RPC verification
```

Reset on logout:
```js
this.currentUser = null;
this.adminVerified = false;
```

### 2. Server-side role verification RPC

```js
async verifyServerRole() {
  try {
    const { data, error } = await sb.rpc('current_role');
    if (error || !data) return null;
    return data;
  } catch {
    return null;
  }
}
```

`current_role` is a SECURITY DEFINER SQL function that reads `profiles.role` where `id = auth.uid()` — the real JWT, not a spoofable response. It must exist in the DB (it's a standard helper; create it if missing):
```sql
CREATE OR REPLACE FUNCTION public.current_role()
RETURNS text LANGUAGE sql STABLE SECURITY DEFINER
SET search_path TO 'public'
AS $$ SELECT role FROM public.profiles WHERE id = auth.uid(); $$;
```

### 3. Gate admin entry on RPC, not `currentUser.role`

```js
async enterAdminRoute() {
  if (!this.currentUser) {
    this.showToast('Login dulu sebagai ADMIN untuk membuka panel ini.', 'warning');
    this.openAuthModal('login');
    return;
  }
  const serverRole = await this.verifyServerRole();
  if (serverRole !== 'ADMIN') {
    this.adminVerified = false;
    this.showToast('Akses ditolak: akun kamu bukan ADMIN.', 'warning');
    history.replaceState(null, '', window.location.pathname + window.location.search);
    this.switchView('catalog');
    return;
  }
  this.adminVerified = true;
  this.switchView('admin');
}
```

### 4. Swap all admin UI guards from `currentUser.role` to `adminVerified`

```js
// switchView guard
} else if (viewName === 'admin') {
  if (!this.adminVerified) return;
  // ...
}

// renderAdminDashboard guard
async renderAdminDashboard() {
  if (!this.adminVerified) return;
  // ...
}

// navAdminBtn click handler
this.dom.navAdminBtn.addEventListener('click', () => {
  this.verifyServerRole().then(role => {
    if (role === 'ADMIN') window.location.hash = 'kasus';
  });
});
```

### 5. Default HTML state: hidden

```html
<button class="nav-btn admin-mode-btn hidden" id="nav-admin-btn">
```

Prevents flash before JS runs. JS reveals it only for verified admins.

## What the attacker CANNOT do (backend defense holds)

- **Suspend users**: `admin_set_user_suspended` → `is_admin()` gate → raises "Hanya ADMIN yang bisa melakukan ini"
- **Delete users**: `admin_delete_user` → same gate
- **See other users' data**: RLS `profiles read own or admin` → `is_admin()` returns false for the real JWT → only own row returned
- **Escalate own role**: `protect_admin_role` trigger blocks any role change to ADMIN

The attack is purely a **UI data exposure** — the attacker sees the dashboard layout, user list ROWS THAT THE RLS ALLOWS (which for a non-admin is just their own row, so the table is empty), and fake buttons that don't work. Still, the layout itself leaks admin features (stat formulas, seller approval workflows, revenue totals) and should be prevented.

## Verification after fix

1. Login as BUYER → `#kasus` should redirect to catalog + toast "Akses ditolak"
2. Install fetch interceptor in console, set `role=ADMIN`, navigate to `#kasus` → still redirects (RPC returns BUYER)
3. Login as ADMIN → `#kasus` opens dashboard normally
4. Check `navAdminBtn` visibility: BUYER/SELLER = hidden, ADMIN = visible