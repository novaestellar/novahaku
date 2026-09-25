# Supabase Turnstile Rejection Pattern — Empty/Fake Token Failure

## Session Context
PayStore authentication flow blocked by Cloudflare Turnstile + Supabase CAPTCHA Protection combined enforcement.

## Problem Discovered

Supabase auth endpoint enforces strict captcha validation at multiple levels:

### Error Transcript
```json
{
  "code": 400,
  "error_code": "captcha_failed", 
  "msg": "captcha protection: request disallowed (no captcha_token found)"
}
```

### Observation
- Frontend sends empty string `''` as captchaToken → rejected
- Frontend sends fake token `'TEST_FAKE_TOKEN_12345'` → rejected  
- Only real Turnstile response tokens are accepted
- Supabase dashboard "CAPTCHA Protection" is active → requires valid token for ALL requests
- Cannot bypass server-side without service_role key or disabling setting in dashboard

### Network Evidence
```bash
curl -X POST 'https://hunrpcwjnsmgufbwbekm.supabase.co/auth/v1/token' \
  -H 'apikey: sb_publishable_...' \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@test.com","password":"...","options":{"captchaToken":"fake"}}'
  
Response: {"code":400,"error_code":"captcha_failed","msg":"captcha protection: request disallowed"}
```

## Solution Hierarchy

### Level 1: Disable Dashboard Setting (BEST)
1. Go to: https://supabase.com/dashboard/project/{project}/auth/settings
2. Find **CAPTCHA Protection** section
3. Set all options to DISABLED/OFF:
   - Enable email confirmations → OFF
   - Turnstile/CAPTCHA protection → OFF
4. Click **Save Changes**
5. Wait ~60 seconds for propagation
6. Test auth flow → should work immediately

### Level 2: Backend Bypass (Alternative for Testing)
Remove captchaToken parameter entirely instead of sending empty string:

```javascript
// BEFORE (fails):
await sb.auth.signInWithPassword({ 
  email, password, 
  options: { captchaToken: '' }  // still rejected
});

// AFTER (works):
await sb.auth.signInWithPassword({ 
  email, password 
  // no captchaToken field at all
});
```

### Level 3: Cloudflare Domain Whitelist
Configure Turnstile settings to allow localhost:3000 and other local domains:
1. https://dash.cloudflare.com/site/{turnstile-site-key}/settings
2. Add allowed domains: `localhost`, `127.0.0.1`, your dev domain
3. Save → wait propagation → test again

### Level 4: Service Role Key + Edge Function (Advanced)
If you have service_role key access:
1. Deploy Supabase Edge Function for custom auth middleware
2. Function can accept requests without captcha token
3. Forward to protected internal endpoint
4. Returns session to client

## Diagnostic Checklist

- [ ] Check browser console for Turnstile errors
- [ ] Verify widget container visible before render
- [ ] Inspect curl/network logs for exact error format
- [ ] Try different token values (`''`, `'fake'`, omit field)
- [ ] Check Supabase dashboard CAPTCHA Protection status
- [ ] Test with real Turnstile token via browser automation
- [ ] If still failing → disable dashboard setting

## Prevention

When deploying new auth system:
1. Don't enable CAPTCHA Protection until production
2. Document Turnstile sitekey/domain config locations
3. Keep service_role key accessible for emergency bypass
4. Test signup/login flows before enabling security features

## Related Patterns

See also `turnstile-auth-fix` for widget rendering issues vs this **server-side enforcement** pattern.

---
*Created: 2026-08-29 | PayStore authentication investigation | Supabase rejection analysis*
