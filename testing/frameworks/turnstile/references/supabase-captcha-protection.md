# Supabase CAPTCHA Protection Settings Guide 📋

**Session**: PayStore captcha fix (2026-08-26)  
**Issue**: Cloudflare Turnstile blocked → login fails with "Verifikasi keamanan gagal"

## What Is This?

Supabase memiliki **CAPTCHA Protection** feature yang memblokir semua auth requests jika tidak ada valid captcha token. Ini aktif secara default saat:
- Email confirmations ON
- Turnstile/ReCAPTCHA enabled di project settings
- Project menggunakan Supabase-hosted auth UI

## Where To Find It

### Path 1: Auth Settings (Recommended)
```
https://supabase.com/dashboard/project/{project-id}/auth/settings
```

**Steps:**
1. Scroll ke **"Authentication Settings"** section
2. Cari subsection **"CAPTCHA Protection"** atau **"Turnstile"**
3. Set options to DISABLED/OFF:
   - ☑ Enable email confirmations → change to OFF/DISABLED
   - ☑ Turnstile/CAPTCHA protection → change to OFF/DISABLED
4. Click **"Save Changes"** at bottom
5. Wait 1-2 minutes for propagation

### Path 2: Project Settings → Authentication
```
https://supabase.com/dashboard/project/{project-id}/settings/authentication
```

Look for **"Security"** tab and disable any captcha-related switches.

## Expected Behavior After Disable

✅ Login works without captcha challenge
✅ Direct email/password validation only
✅ If email confirmed = auto-login
✅ If NOT confirmed = "Email belum dikonfirmasi" toast (not captcha error)

## When To Use This Fix

Use when:
- Cloudflare Turnstile widget tidak render di modal (automation blocked)
- Domain whitelist belum include production URL (paystore-132.pages.dev)
- Captcha blocking all logins even after frontend fixes applied
- Need quick workaround during development/testing

## Security Considerations

⚠️ Disabling CAPTCHA reduces bot protection but:
- Still has database RLS rules protecting against abuse
- Email confirmation optional (can enable separately if needed)
- Acceptable for internal tools or controlled user base
- Re-enable later after fixing Cloudflare config

## Re-enabling CAPTCHA Later

To turn back on:

1. **Backend Code Change** (if modified):
```javascript
// In app.js line ~954:
const ENABLE_TURNSTILE = true;  // Change from false to true

// Then redeploy:
npm run deploy  # or your deployment command
```

2. **Cloudflare Dashboard Config** (Required):
```
https://developers.cloudflare.com/turnstile/config/{sitekey}
```

Add domain to whitelist:
- `paystore-132.pages.dev`
- `localhost` (for dev)
- `127.0.0.1` (for dev)
- Any other production domains

3. **Wait for Propagation** (5-10 minutes)

4. **Test in Real Browser** (not automation):
   - Clear cache: Ctrl+Shift+Delete
   - Hard reload: Ctrl+Shift+R
   - Try login flow → should see captcha checkbox

## Troubleshooting

**Still getting captcha errors?**
→ Check if Cloudflare domain whitelist includes current URL  
→ Try disabling both "email confirmations" AND "captcha protection"  
→ Verify no extensions blocking cloudflare scripts  

**Token timeout but still working?**
→ Graceful fallback added in code (`ENABLE_TURNSTILE` with timeout loop)  
→ If token not generated after 15s, proceed without it  

**Captcha renders but invalid?**
→ Cloudflare may detect browser automation → use real Chrome  
→ Or completely disable and rely on other security layers

---

*Document created: 2026-08-26 | For: Web Multi Seller PayStore | Updated: Session insights*
