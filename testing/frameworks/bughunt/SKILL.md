---
name: bug-hunting
description: "Automated bug bounty hunting pipeline: scrape programs, scan vulnerabilities, generate PoC, send reports via email"
version: 1.0.0
author: SeaGull Security Lab
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, bug-bounty, vulnerability-scanning, ethical-hacking, automation]
    related_skills: [himalaya, har-capture, security-checklist, web-api-debugging]
prerequisites:
  commands: [himalaya, python, curl]
---

# Bug Hunting - Automated Bug Bounty Pipeline

Full-stack bug bounty automation: scraping platforms → scanning targets → generating PoCs → sending reports via email.

## When to Use

- Starting bug bounty hunting career
- Need passive income from security research
- Want to automate vulnerability discovery
- Building security research portfolio
- Learning ethical hacking workflows

## Prerequisites

**Required:**
- Python 3.8+
- Himalaya CLI (email sender)
- Internet connection

**Optional:**
- Configured email account for sending reports
- Bug bounty platform accounts (HackerOne, Bugcrowd, Intigriti)

## Installation

```bash
# Install Himalaya email CLI
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
himalaya --version

# Configure email account
himalaya account configure
```

## Project Structure

```
bug-hunter/
├── bug_bounty_scraper.py    # Scrape programs from platforms
├── vulnerability_scanner.py  # Scan for common vulnerabilities
├── poc_generator.py          # Generate PoC reports
├── email_sender.py           # Send via Himalaya
├── run_bug_hunt.py           # Full pipeline orchestrator
├── bug_bounty_targets.json   # Scraped programs (output)
├── vulnerability_findings.json # Found vulnerabilities (output)
├── poc_reports/              # Generated PoC markdown files
└── email_templates/          # Draft emails ready to send
```

## Quick Start

### Full Automated Pipeline

```bash
cd D:/d/projects/bug-hunter
python run_bug_hunt.py
```

This runs:
1. Scrapes 50+ bug bounty programs (HackerOne, Bugcrowd, Intigriti)
2. Scans top 5 targets for vulnerabilities
3. Generates detailed PoC reports
4. Creates email templates

### Manual Step-by-Step

```bash
# Step 1: Scrape programs
python bug_bounty_scraper.py
# Output: bug_bounty_targets.json

# Step 2: Scan for vulnerabilities
python vulnerability_scanner.py
# Output: vulnerability_findings.json

# Step 3: Generate PoC reports
python poc_generator.py
# Output: poc_reports/*.md, email_templates/*.txt

# Step 4: Send reports (dry run first)
python email_sender.py
# Review drafts, then set dry_run=False and re-run
```

## Vulnerability Detection

### Current Checks

| Check | Severity | What It Finds |
|-------|----------|---------------|
| Security Headers | Medium | Missing HSTS, CSP, X-Frame-Options, X-Content-Type-Options |
| CORS Configuration | High | Wildcard origins, reflected origins |
| Sensitive Files | High | .git/HEAD, .env, .DS_Store exposure |
| Admin Panels | Medium | /admin, /phpmyadmin, /wp-admin accessible |
| Info Disclosure | Low | Server version in headers, exposed endpoints |
| Common Endpoints | Variable | /robots.txt, /sitemap.xml, /swagger.json, /api/docs |

### Detection Methodology

**Security Headers:**
- Fetches target URL
- Checks response headers for required security headers
- Reports missing headers with severity rating

**CORS Misconfiguration:**
- Sends request with `Origin: https://evil.com`
- Checks if `Access-Control-Allow-Origin` reflects arbitrary origin
- Reports if wildcard (*) or reflected origin found

**Sensitive Files:**
- Probes common sensitive file paths
- Reports 200 OK responses
- High severity for .git, .env exposure

**Admin Panels:**
- Checks common admin URL patterns
- Reports accessible admin interfaces
- Medium severity (increases attack surface)

## PoC Report Generation

Each finding generates a markdown report with:

```markdown
# Vulnerability Report

## Summary
- Target URL
- Vulnerability type
- Severity rating
- Discovery timestamp

## Description
Detailed explanation of the issue

## Proof of Concept
Step-by-step reproduction:
1. Navigate to URL
2. Execute command
3. Observe result

## Impact
Real-world consequences

## Remediation
Specific fix recommendations with code examples

## References
- OWASP links
- CWE database
```

## Email Automation

### Himalaya Integration

Email sender uses Himalaya CLI to send reports:

```python
# Compose email
email_content = f"""From: bug-hunter@your-domain.com
To: security@target.com
Subject: Security Vulnerability Report - {target_name}

{body}
"""

# Send via pipe
cat email_draft.txt | himalaya template send
```

### Email Template Structure

```
Subject: Security Vulnerability Report - [Target]

Dear Security Team,

I am reporting [N] security vulnerability/vulnerabilities I discovered
in [Target] as part of your bug bounty program.

FINDING #1: [Type] ([Severity] Severity)
Description...
PoC: curl command...

[Additional findings...]

Detailed PoC reports attached.

Best regards,
Bug Hunter
```

### Dry Run Mode

By default, `email_sender.py` runs in DRY RUN mode:
- Shows what would be sent
- Doesn't actually send emails
- Allows review before real submission

To send real emails:
1. Configure Himalaya with your email
2. Update `load_program_contacts()` with real contacts
3. Set `dry_run=False` in code
4. Re-run script

## Customization

### Add New Platform Scraper

Edit `bug_bounty_scraper.py`:

```python
def fetch_yeswehack_programs():
    """Fetch YesWeHack programs"""
    targets = []
    try:
        url = "https://api.yeswehack.com/programs"
        # Your scraping logic
        return targets
    except Exception as e:
        print(f"[-] YesWeHack fetch failed: {e}")
    return targets

# In main():
all_targets.extend(fetch_yeswehack_programs())
```

### Add New Vulnerability Check

Edit `vulnerability_scanner.py`:

```python
def check_sql_injection(url):
    """Check for SQL injection"""
    findings = []
    
    payloads = ["'", "' OR '1'='1", "1' AND '1'='1"]
    
    for payload in payloads:
        test_url = f"{url}?id={payload}"
        # Test logic here
        
    return findings

# In scan_target():
findings.extend(check_sql_injection(target_url))
```

### Customize PoC Template

Edit `poc_generator.py` → `generate_poc_report()`:

```python
report = f"""# Custom Report Template

## Your Custom Sections
{custom_content}

## Standard Sections
{standard_content}
"""
```

### Update Target Contacts

Edit `email_sender.py` → `load_program_contacts()`:

```python
contacts = {
    "target1.com": "security@target1.com",
    "target2.com": "bugbounty@target2.com",
    # Discover via:
    # - Program page
    # - security.txt
    # - WHOIS lookup
}
```

## Configuration

### Rate Limiting

Adjust delays between requests:

```python
# In bug_bounty_scraper.py
time.sleep(2)  # Between platform fetches

# In vulnerability_scanner.py
time.sleep(3)  # Between target scans
```

### Scan Depth

Change target limit:

```python
# In vulnerability_scanner.py
for target in targets[:5]:  # Scan first 5 targets
    scan_target(target['url'])

# Increase to scan more:
for target in targets[:20]:  # Scan first 20 targets
```

### Timeout Settings

Adjust request timeouts:

```python
with urlopen(req, timeout=10) as response:  # 10 second timeout
```

## Best Practices

### Legal & Ethical

1. **Scope**: Only test targets explicitly in-scope
2. **Authorization**: Respect program rules and exclusions
3. **Disclosure**: Never publish findings before vendor fixes
4. **Rate Limiting**: Don't overload target servers
5. **Professional**: Maintain clear, respectful communication

### Technical

1. **Verify Findings**: Manually confirm automated findings
2. **False Positives**: Check for false positives before reporting
3. **Context**: Include full context in PoC (versions, configs)
4. **Reproducible**: Ensure steps are clear and reproducible
5. **Impact**: Explain real-world security impact

### Workflow

1. **Start Small**: Begin with 5-10 targets
2. **Review Output**: Always review before sending
3. **Track Progress**: Keep logs of submitted reports
4. **Learn**: Study accepted/rejected reports
5. **Iterate**: Improve detection based on feedback

## Expected Results

Typical pipeline run (5-10 minutes):

**Scraping:**
- HackerOne: 20-50 programs
- Bugcrowd: 10-30 programs
- Intigriti: 5-20 programs
- Total: 50-100 programs

**Scanning (5 targets):**
- Security headers: 3-5 findings per target
- CORS issues: 0-2 findings per target
- Exposed files: 0-1 findings per target
- Total: 10-25 findings

**Reporting:**
- 10-25 PoC reports generated
- 1-5 email templates (grouped by target)

## Troubleshooting

### Himalaya Not Found

```bash
# Check PATH
which himalaya

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify
himalaya --version
```

### Email Send Failed

```bash
# Check Himalaya configuration
himalaya account list

# Test connectivity
himalaya envelope list

# Manual send test
echo "Test email body" | himalaya template send
```

### No Targets Found

- API rate limited → wait and retry
- Network issues → check connectivity
- Platform API changed → update scraper code

### Scan Timeout

- Reduce target count in `vulnerability_scanner.py`
- Increase timeout values in requests
- Check target is actually accessible

### False Positives

Common false positives:
- 200 OK doesn't always mean vulnerable
- Some headers optional depending on context
- Admin panels may be intentionally public
- Verify findings manually before reporting

## Integration with Hermes

### As Cron Job

```bash
# Daily bug hunting scan
hermes cron create --schedule "0 2 * * *" \
  --prompt "Run bug hunting pipeline and notify results" \
  --name "daily-bug-hunt"
```

### With Other Skills

- **har-capture**: Deep API endpoint discovery
- **security-checklist**: Validate findings against checklist
- **web-api-debugging**: Debug false positives
- **research-tools**: Research disclosed vulnerabilities

### Notification

Add Telegram notification after pipeline:

```python
# In run_bug_hunt.py after pipeline completes
import requests

telegram_bot_token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"

message = f"""
🔍 Bug Hunt Complete

Targets: {len(all_targets)}
Findings: {len(all_findings)}
PoCs: {len(poc_files)}

Top Finding: {top_finding['vuln_type']} ({top_finding['severity']})
"""

requests.post(
    f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
    json={"chat_id": chat_id, "text": message}
)
```

## Monetization Potential

Average bug bounty rewards:

| Severity | Typical Range | Your Finding |
|----------|---------------|--------------|
| Low | $50-$200 | Info disclosure, missing headers |
| Medium | $200-$1000 | CORS, exposed admin panels |
| High | $1000-$5000 | Sensitive file exposure |
| Critical | $5000-$20000+ | RCE, Auth bypass, PII leak |

**Realistic expectations:**
- Automation finds mostly Low-Medium issues
- 1-2 valid findings per day = $100-$500/day
- Manual verification + deeper testing for High/Critical
- Build reputation → private invites → higher rewards

## Advanced Workflows

### Continuous Monitoring

```bash
# Run daily, track new programs
python bug_bounty_scraper.py
diff bug_bounty_targets.json bug_bounty_targets_prev.json

# Scan only new targets
python vulnerability_scanner.py --targets-diff
```

### Integration with Other Tools

```bash
# After scanning, run deeper tools
python vulnerability_scanner.py
cat vulnerability_findings.json | jq -r '.[].target' | nuclei -t ~/nuclei-templates

# Or with subfinder
cat bug_bounty_targets.json | jq -r '.[].url' | subfinder | httpx
```

### Reporting Dashboard

Create simple HTML dashboard:

```python
# dashboard_generator.py
import json
from pathlib import Path

findings = json.load(open('vulnerability_findings.json'))

html = """
<html>
<head><title>Bug Hunt Dashboard</title></head>
<body>
  <h1>Findings: {count}</h1>
  <table>
    <tr><th>Target</th><th>Type</th><th>Severity</th></tr>
    {rows}
  </table>
</body>
</html>
""".format(
    count=len(findings),
    rows="\\n".join(f"<tr><td>{f['target']}</td><td>{f['vuln_type']}</td><td>{f['severity']}</td></tr>" for f in findings)
)

Path('dashboard.html').write_text(html)
```

## Roadmap

- [ ] XSS detection (reflected, stored, DOM-based)
- [ ] SQL injection scanner with blind detection
- [ ] Subdomain enumeration integration
- [ ] Screenshot automation for visual proof
- [ ] Multi-threaded scanning for speed
- [ ] Machine learning for false positive reduction
- [ ] Web UI dashboard with real-time updates
- [ ] Integration with Burp Suite / ZAP
- [ ] Automatic retest of previously found issues

## References

- [HackerOne Directory](https://hackerone.com/directory)
- [Bugcrowd Programs](https://bugcrowd.com/programs)
- [Intigriti Programs](https://www.intigriti.com/programs)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [Bug Bounty Hunting Essentials](https://www.bugcrowd.com/resources/levelup/)

---

**Disclaimer**: This tool is for authorized bug bounty programs and ethical hacking only. Users are responsible for compliance with program rules and applicable laws.
