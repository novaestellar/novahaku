---
name: laravel-security-audit
description: Systematic vulnerability assessment of Laravel applications
---

# Laravel Security Audit Skill

This skill encodes a structured approach to auditing Laravel applications for common security misconfigurations and vulnerabilities. Use when reviewing any Laravel-based web application.

## Core Principles

1. **Debug mode is the #1 production killer** — if APP_DEBUG=true in production, everything else becomes easier (stack traces leak full path structure)
2. **Route configuration errors are common** — POST methods often blocked while GET works, leading to confusing "MethodNotAllowedHttpException" errors that actually disclose more info than expected
3. **Laravel's Whoops/Pahele error pages are dangerous** — they're meant for development only, never for production

## Reconnaissance Sequence

### Phase 1: Framework Detection & Debug Mode Check

```bash
# Check if Laravel by looking for specific headers/meta tags
curl -sIL https://target.com/ | grep -iE 'X-Powered-By|Set-Cookie|laravel_session'
curl -sL https://target.com/ | grep -oP '<meta name="csrf-token"[^>]*>'

# Probe debug mode via intentional error triggering
curl -sL 'https://target.com/nonexistent-route' | head -50
# If you see stack trace with /vendor/laravel/framework/... paths = DEBUG ON
```

**CRITICAL INDICATOR:** Stack trace reveals `/home/*/public_html/vendor/` or `C:\xampp\htdocs\vendor\` — this means debug mode is ACTIVE in production. Every subsequent attack vector becomes trivial.

### Phase 2: Route Method Analysis

Many Laravel apps have misconfigured routes where only GET is allowed but HTML forms specify POST. This creates two problems:
1. Forms simply don't work → user-facing bug
2. The error page exposes more information → **security risk**

**Detection Pattern:**

```bash
# Try POST to auth endpoints
curl -sL 'https://target.com/login' -X POST --data-urlencode 'user=test' --data-urlencode 'pass=test123' 2>/dev/null | grep -iE 'MethodNotAllowed|POST.*not supported'

# If you see "The POST method is not supported for this route. Supported methods: GET, HEAD." 
# → Debug mode is exposing routing configuration details
```

**Action:** Document all routes that reject POST with verbose errors. These become evidence chains showing:
- Debug mode active (you wouldn't get stack traces otherwise)
- Application structure (file paths in trace)
- Possible SQL injection vectors (even if blocked, the input parameters exist)

### Phase 3: Sensitive File Probing

Test these common targets:

| Path | Purpose |
|------|---------|
| `/.env` | Laravel environment config (DB creds, API keys) |
| `/.env.backup`, `/.env.example` | Fallback configs |
| `/storage/logs/laravel.log` | Application logs (often contain PII/error details) |
| `/vendor/` | Full dependency list (helps identify known CVEs) |
| `/.git/config` | Source code access if exposed |
| `/backup.sql`, `/dump.sql` | Database dumps |
| `/api/*`, `/auth/*` | Often unauthenticated endpoints |

Use:
```bash
for p in /.env /.env.backup /.env.example /storage/logs/laravel.log /.git/config; do
  curl -sI "https://target.com$p" | head -1
done
```

Look for: HTTP 200 (accessible), HTTP 403 (protected), HTTP 404 (doesn't exist)

### Phase 4: Authentication Endpoint Survey

Map all login/register forms and test for:

1. **CSRF token handling** — check if token exposed in `<meta name="csrf-token">` vs hidden input field
   - If in meta tag → attacker can read via JavaScript + CSRF bypass
   - If in input field with proper HttpOnly flag → harder to extract
   
2. **Input validation** — look at HTML constraints (`maxlength`, `pattern`, `type`)
   - Only client-side validation? Bypassable with curl/postman
   - Regex patterns exposed? Helps craft SQLi payloads
   
3. **Multiple entry points** — check mobile/wap/desktop variants
   ```bash
   curl -sL 'https://target.com/desktop/login?platform=desktop' > /tmp/dt_desktop.html
   curl -sL 'https://target.com/mobile/login?platform=mobile' > /tmp/dt_mobile.html
   diff /tmp/dt_desktop.html /tmp/dt_mobile.html  # Find differences
   ```

### Phase 5: Alternative Method Injection

Some Laravel apps support method spoofing via headers:

```bash
# X-HTTP-Method-Override header
curl -sL 'https://target.com/login' \
  -H 'X-HTTP-Method-Override: POST' \
  --data-urlencode 'username=admin' \
  --data-urlencode 'password=test'

# PUT/PATCH as fallback
curl -sL 'https://target.com/resource' -X PUT --data '{"test":"value"}'
curl -sL 'https://target.com/resource' -X PATCH --data '{"test":"value"}'
```

If these succeed where normal POST fails → routing misconfiguration detected.

### Phase 6: Error Page Analysis

When Laravel throws errors (404, 405, 500), check what's leaked:

**SAFE response:** Generic "Sorry, something went wrong" with no technical details  
**UNSAFE response:** Full stack trace including:
- File paths (`/home/dollarto/public_html/vendor/laravel/framework/src/...`)
- Line numbers
- Class/method names
- Request URIs
- Query strings with values

Example UNSAFE trace snippet:
```php
Symfony\Component\HttpKernel\Exception\MethodNotAllowedHttpException:
The POST method is not supported for this route.
Supported methods: GET, HEAD.
in file /home/dollarto/public_html/vendor/laravel/framework/... on line 256
Stack trace:
  1. Symfony\Component...\->() ...
  2. Illuminate\Routing\RouteCollection->methodNotAllowed() ...
  3. Illuminate\Foundation\Http\Kernel->handle() ...
```

**Implication:** Attacker knows exact Laravel version, vendor directory structure, deployment path, and can reconstruct the application's internal architecture.

## Common Attack Vectors to Test

Once you confirm debug mode is OFF and routes accept POST:

1. **SQL Injection** — Test username/password fields:
   - `admin' OR '1'='1`
   - `' OR 1=1--`
   - `admin' AND SLEEP(5)--` (time-based blind)
   
2. **Mass Assignment** — Register endpoint often vulnerable:
   - Add extra fields like `is_admin=1`, `role_id=1`, `banned_at=null`
   
3. **Unauthenticated APIs** — Check `/api/v1/users`, `/api/auth/register`, etc.

4. **Backup files** — Some developers accidentally leave backup SQL dumps accessible at `/backup/.sql`, `/database.sql`, etc.

5. **Directory traversal** — Try `../../.env`, `../../../../var/www/html/.env`

## Immediate Recommendations to Admin

When you find these issues, prioritize remediation:

1. 🔴 **DISABLE DEBUG MODE** — Set `APP_DEBUG=false` in `.env` immediately
2. 🟡 **Fix route definitions** — Add `Route::post('/login', ...)` instead of relying on GET-only
3. 🟡 **Custom error pages** — Use Laravel's `render()` exception handler to hide stack traces from users
4. 🟢 **Rate limiting** — Add throttle middleware to login/register endpoints
5. 🟢 **CAPTCHA** — Implement reCAPTCHA/hCaptcha on authentication forms
6. 🟢 **WAF rules** — Enable Cloudflare WAF with rules to block sensitive file probes (.env, .git, .sql)

## Session Artifacts

Save key findings to:
- `/tmp/laravel_recon.md` — Main report
- `/tmp/{domain}_debug_error.html` — Save error page for documentation
- `/tmp/sensitive_files.txt` — List of accessible sensitive paths
- `/tmp/routes.json` — All discovered endpoints with HTTP methods tested

## Pitfalls

- **Don't assume POST rejection = functional app** — it might just be misconfigured routes
- **Stack trace exposure is worse than direct exploitation** — debugging info leakage gives attackers a roadmap
- **Meta-tag CSRF tokens are still dangerous** — many think hidden inputs are required for CSRF protection; they're not. Meta tags are readable via JS, so same-origin scripts can steal them easily.
- **Method override headers are rare but impactful** — always probe them early in audit sequence. They expose if Laravel accepts non-standard HTTP verbs through custom middleware.
- **Cloudflare protection doesn't prevent framework-level vulns** — WAF hides underlying server IPs but debug mode leaks everything from within

## Tooling Stack

- `curl` for HTTP probing
- `grep` for pattern matching in responses
- `diff` to compare variants (desktop vs mobile vs wap)
- Browser console for reading CSRF tokens via DOM inspection
- Execute-code wrapper for automated multi-endpoint scanning

## Next Steps After Initial Scan

1. Compile findings into vulnerability report (prioritize by severity)
2. Create patch recommendations for each issue
3. If admin allows: test actual exploits (SQLi, auth bypass) once blocking config bugs are fixed
4. For gamblers/betting sites: note jurisdiction/regulatory compliance requirements

---

**Related Skills:**
- [security-master](#) — General web pentesting workflow
- [laravel-pentest](#) — Specific Laravel framework vulnerabilities
- [debugging-bugs](#) — Diagnosing application errors

**References:**
- references/debug-mode-disclosure.md — Detailed examples of stack trace leakage
- references/laravel-routes-misconfiguration.md — Case studies of POST rejection patterns
- templates/laravel_audit_report.md — Template for reporting findings