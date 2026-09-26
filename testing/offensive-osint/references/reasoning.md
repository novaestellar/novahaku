# Offensive-OSINT — Reasoning

> Extracted from `SKILL.md` on 2026-09-26. Heading numbering preserved; section references in the main skill point here.

## 21. Mobile App Ownership Confidence — 0–100 rubric

Before running deep APK static analysis, score whether the discovered app actually belongs to the target. Threshold: **≥70 = accept**.

| Signal | Points |
|---|---|
| Package reverse-DNS matches target domain (e.g., `com.acme.android` ⟂ `acme.com`) | +40 |
| Developer email is `<anything>@<target-domain>` | +25 |
| Developer website URL is the target domain (or a confirmed sibling brand domain) | +20 |
| App name contains a brand keyword from operator-supplied brand list | +10 |
| App has ≥ minimum review-score threshold (default 20 reviews) | +5 |

Apps below threshold are tagged `mobile_review_pending` and shown but not analyzed. Operator can re-score with `--mobile-ownership-threshold 50` for noisier collection.

### 21.1 APK Static Analysis Pipeline

Once an app clears the §21 ownership gate, run this pipeline. **Passive static analysis only** — no Frida/emulator instrumentation, no exercising the app against a live backend, no replaying captured app traffic. Confirming a leaked secret is live uses the §23 read-only validators; confirming an open cloud surface (Firebase, S3, GCS) uses §16.8/§16.17 — separate, explicit steps, deliberately not bundled into this pass.

**A. Acquisition**

| Source | Method | Notes |
|---|---|---|
| Google Play | `pip install google-play-scraper` (§46.9) for metadata | Play's public surface does **not** distribute the binary itself |
| APKPure | HTML-scrape the download page, extract the `.apk` link | No login required; rate-limit-friendly; primary automatable source |
| APKMirror | Manual browser download | Stronger anti-automation than APKPure; fallback only |
| iOS IPA | Operator-supplied, dropped into a local `ipa_uploads/` dir | Never auto-download a `.ipa` — DMCA posture; analyse in place if the operator has it in scope |

```bash
curl -s "https://apkpure.net/$(echo com.acme.android | tr . -)/com.acme.android/download" \
 | grep -oE 'https://[^"]+\.apk[^"]*' | head -1
```

**B. Decompile toolchain**

```bash
# apktool — resources + manifest to readable XML (not raw AXML)
apktool d app.apk -o out/

# aapt2 (Android SDK build-tools) — manifest dump without full unpack
aapt2 dump badging app.apk
aapt2 dump xmltree app.apk --file AndroidManifest.xml

# jadx — Java source recovery from classes.dex (for logic review, not just strings)
jadx -d out_src/ app.apk
```

Windows: `apktool.bat`; `aapt2.exe` lives under `%LOCALAPPDATA%\Android\Sdk\build-tools\<ver>\aapt2.exe` (install via Android Studio SDK Manager or `sdkmanager --install "build-tools;34.0.0"`); `jadx.bat` from the portable jadx zip, or `jadx-gui.exe` for interactive review.

No-toolchain alternative — pure Python, what the reference implementation's own `mobile_attack_surface.py` uses (no apktool/jadx dependency):

```bash
pip install androguard
```

```python
from androguard.core.apk import APK
a = APK("app.apk")
print(a.get_package, a.get_effective_target_sdk_version)
print(a.get_permissions)
manifest_xml = a.get_android_manifest_axml.get_xml # decoded AndroidManifest.xml
```

**C. AndroidManifest.xml parse**

- **Exported-component test** (the subtlety most manual reviews miss): a component is *effectively* exported if `android:exported="true"` **OR** `exported` is unset **and** it declares an `<intent-filter>`. Don't just grep for `exported="true"`.
- `android:debuggable="true"` on `<application>` — production debug surface.
- `android:allowBackup` — **defaults to `"true"` when the attribute is absent entirely.** Most manifests never set it, so absence of the attribute is not absence of the risk.
- `android:usesCleartextTraffic` — explicit `"true"` allows unencrypted HTTP app-wide (API ≥28 defaults this to `false`, so an explicit `"true"` is a deliberate override worth flagging harder).
- Custom `<permission>` declarations — check `android:protectionLevel`. `normal` or `dangerous` means any installed app can hold the permission; sensitive custom permissions (guarding IPC to exported components) should be `signature`.
- `android:networkSecurityConfig` reference on `<application>` — pivot to step G below.

**D. Deep-link / intent-filter extraction**

Walk every `activity` / `activity-alias` / `service` / `receiver` for `<intent-filter><data android:scheme=… android:host=…/></intent-filter>`. For each `scheme://host` pair:

- Flag handlers whose **component name or host** contains `auth`, `token`, `reset`, `callback`, `oauth`, `sso`, or `login` — these are the deep links worth weaponizing (attacker-controlled query params reaching an auth/token flow).
- Distinguish **App Links** (`https://` scheme + `android:autoVerify="true"` + a matching `.well-known/assetlinks.json` on the host) from a **custom scheme** (`myapp://`). Only the custom scheme is hijackable by a second app registering the same scheme — App Links are domain-verified by the OS.

**E. Firebase / GCP config extraction**

- `google-services.json` → `project_info.project_id`, and every `client.api_key.current_key` (the project's default Google API key, often over-scoped).
- `GoogleService-Info.plist` (iOS bundle) → `PROJECT_ID`, `API_KEY`, `GCM_SENDER_ID`.
- Extraction here is **read-of-the-APK-only**. the reference implementation's own pipeline goes one step further and probes the extracted `project_id` against canonical Firebase endpoints (RTDB `/.json`, Firestore, Storage list) — that's a live-backend check, not static analysis; do it as a distinct, explicit step via §16.8's cloud-bucket-style workflow, not silently inside this pass.

**F. Embedded secrets — reuse §17**

Extract every text blob and run it through `scripts/secret_scan.py` (§48) or the raw §17 table:

```bash
# Unpack once, scan everything under it in one pass
unzip -o app.apk -d out/
python3 scripts/secret_scan.py out/

# Strings out of native libs (classes.dex string-pool is already covered by
# apktool's baksmali output / jadx's decompiled source under out_src/)
find out/lib -name '*.so' -exec strings {} \; | python3 scripts/secret_scan.py

# assets/ specifically — bundled credential files, not just string hits
find out/assets -type f \( -iname '*.pem' -o -iname '*.p12' -o -iname '*.jks' \
 -o -iname '*.keystore' -o -iname '*.env' -o -iname 'google-services.json' \)
```

The FCM Server Key (§17 #80) and the GCP/Firebase family (§17 #4, #5, #67–69) are the entries most likely to fire here — this is exactly the mobile-recon context they were added for.

**G. Network Security Config**

`res/xml/<name>.xml`, referenced by the manifest's `android:networkSecurityConfig` attribute (captured in step C). the reference implementation's own pipeline stops at recording the *reference* as a pinning marker — it does not parse the file. Pull it manually (via the apktool/aapt2 output from step B) and check for:

- `cleartextTrafficPermitted="true"` at the `<base-config>` level — overrides a `usesCleartextTraffic="false"` manifest attribute for the domains it covers.
- `<trust-anchors><certificates src="user"/></trust-anchors>` — accepts user-installed CAs, which means a proxy CA (Burp/mitmproxy) is trusted without needing a bypass. This is the single most common reason an app "should have pinning but doesn't" in practice — the pin-set is declared, but a permissive trust-anchor still lets a MITM proxy through for testing-flavored builds accidentally shipped to prod.
- `<pin-set>` entries — note the `expiration` date; an expired pin-set silently stops enforcing.

**H. Findings + severities**

| Finding | Severity |
|---|---|
| `android:debuggable="true"` | **CRITICAL** |
| Embedded secret (per §17 catalog severity) | per §17 |
| Sensitive deep-link handler (auth/token/reset keyword) | HIGH |
| `android:allowBackup="true"` (incl. unset/default) | MEDIUM |
| `android:usesCleartextTraffic="true"` | MEDIUM |
| Unprotected exported component (no permission) | MEDIUM |
| High-risk permission held (RECORD_AUDIO, READ_SMS, BIND_ACCESSIBILITY_SERVICE, etc.) | MEDIUM |
| Other sensitive permission | LOW |
| Cert pinning missing / permissive user trust-anchor | LOW |

Full worked examples and rationale for each row live in §40 (search "android"/"deep-link"/"exported") — this table is the quick-reference, §40 is the narrative.

**Cross-references:** §21 (run the ownership gate first — never deep-analyse an unrelated app), §17/§48 (secret catalog + scanner reused verbatim on decompiled text), §23 (read-only validators for anything extracted here that looks live), §40 (severity worked examples), §46.9 (tooling install commands).

---


## 28. Infrastructure & Attack-Surface OSINT

- [Shodan](https://www.shodan.io/), [Censys](https://search.censys.io/) — internet device + cert search.
- [GreyNoise](https://viz.greynoise.io/) — distinguish background noise from targeted scans.
- [SecurityTrails](https://securitytrails.com/) — passive DNS + asset discovery.
- [SpiderFoot](https://www.spiderfoot.net/) — automated recon + correlation.
- [theHarvester](https://github.com/laramies/theHarvester) — subdomain, email, metadata.
- [Recon-ng](https://github.com/lanmaster53/recon-ng) — web recon framework.
- [Amass](https://github.com/owasp-amass/amass) / [Subfinder](https://github.com/projectdiscovery/subfinder) — passive subdomain.
- [BuiltWith](https://builtwith.com/) — tech stack enumeration.
- [Netlas](https://netlas.io/) — large-scale HTTP/DNS/cert pivots.
- [BinaryEdge](https://www.binaryedge.io/) / [FOFA](https://fofa.so/) / [ZoomEye](https://www.zoomeye.org/) — Shodan/Censys complements.
- [RiskIQ PassiveTotal](https://community.riskiq.com/) — passive DNS/cert/host pivots.
- [Spur](https://spur.us/) — IP lookups.
- [Robtex](https://www.robtex.com/) — passive DNS + infrastructure.

### 28.1 ASN/BGP & Internet Measurement

- [Hurricane Electric BGP Toolkit](https://bgp.he.net/), [RIPEstat](https://stat.ripe.net/), [BGPView](https://bgpview.io/), [bgp.tools](https://bgp.tools/), [PeeringDB](https://www.peeringdb.com/).

**Bulk IP → ASN — recipes that actually work in 2026:**

```bash
# Cymru bulk WHOIS (fastest; no rate-limit issues; no key required)
echo -e "begin\nverbose\n8.8.8.8\n1.1.1.1\nend" | nc whois.cymru.com 43
# Or one-shot:
whois -h whois.cymru.com " -v 8.8.8.8"

# RIPEstat (free; CORS-friendly; ~1 req/sec polite limit)
curl -sk "https://stat.ripe.net/data/network-info/data.json?resource=8.8.8.8" | jq '.data'

# bgp.tools per-IP API (free; light rate-limit; requires UA)
curl -sk -A "osint-recon/1.0 (contact@example.com)" "https://bgp.tools/api/ip/8.8.8.8" | jq .

# IPinfo Lite (free 50k req/month with free key)
curl -sk "https://ipinfo.io/8.8.8.8?token=<key>" | jq .
```

**Watch out:**

- `bgpview.io` API has aggressive undocumented rate limits (~1 req/min/IP); not suitable for bulk.
- `bgp.he.net` has no public API; HTML scraping only — fragile.
- `PeeringDB` is for facility/IX info, not per-IP ASN lookup.
- For bulk (>50 IPs): use the **Cymru bulk format** above; it accepts hundreds of IPs in one TCP session.

### 28.2 Certificates & CT Monitoring

- [crt.sh](https://crt.sh/), [Censys Certificates](https://search.censys.io/certificates), [CertStream](https://certstream.calidog.io/) (real-time CT WebSocket), [Rapid7 Open Data](https://opendata.rapid7.com/), [Cert Spotter](https://sslmate.com/certspotter) (freemium).
- **Favicon mmh3 hash:** cluster infrastructure across hosts; pair with Shodan/Censys favicon search for shared-infra discovery.

### 28.3 Web tech / TLS / fingerprinting

- **httpx (ProjectDiscovery)** — Wappalyzer-compatible ~600 signatures, JARM, favicon mmh3, TLS cert SHA256, security headers, screenshots. Recommended one-shot probe wrapper for thousands of hosts.
- **JARM** — TLS handshake hash; stable per server config; useful for clustering.
- **Wappalyzer** browser extension or CLI for tech enumeration.

### 28.4 TLS Deep Audit

Beyond the cert SAN + JARM, inspect cipher suites, protocols, and config quality.

**sslyze (most thorough):**

```bash
pip install sslyze
sslyze --regular target.example:443
sslyze --json_out=tls.json target.example:443
```

Reports: protocols supported (TLS 1.0/1.1/1.2/1.3), cipher suites per protocol, cert chain, OCSP, key info, robot/heartbleed/lucky13/poodle/freak/logjam/drown/ccs/ticketbleed.

**testssl.sh (thorough + readable output):**

```bash
docker run --rm -ti drwetter/testssl.sh https://target.example
# Or native install: https://github.com/drwetter/testssl.sh
testssl.sh --jsonfile-pretty=tls-report.json target.example:443
```

**nmap script alternative (lighter):**

```bash
nmap --script ssl-enum-ciphers,ssl-cert -p 443 target.example
```

**Check for these issues:**

| Issue | Severity | What to look for |
|---|---|---|
| TLS 1.0 / 1.1 supported | MEDIUM | Deprecated; PCI-DSS forbids TLS 1.0. |
| SSL 3.0 / 2.0 supported | HIGH | Critically deprecated. |
| Weak ciphers (RC4, 3DES, CBC modes) | MEDIUM | RC4 = NOMORE attack; 3DES = SWEET32. |
| Anonymous DH | HIGH | No authentication. |
| Self-signed cert on production | MEDIUM | Trust failure. |
| Expired cert | MEDIUM | Operational + trust failure. |
| Cert valid for too long (>397 days) | LOW | Browser warnings since 2020. |
| Wildcard cert covering critical hosts | INFO | Operational risk if private key compromised. |
| Weak key size (<2048 RSA, <256 ECDSA) | HIGH | Cryptographically weak. |
| Heartbleed (CVE-2014-0160) | CRITICAL | Memory disclosure. |
| ROBOT (CVE-2017-13099) | HIGH | Bleichenbacher. |
| CCS injection (CVE-2014-0224) | HIGH | OpenSSL specific. |
| Ticketbleed (CVE-2016-9244) | HIGH | F5-specific memory disclosure. |
| HSTS not present (covered §16.4) | MEDIUM | Header audit. |

**JA3 / JA4 reference databases:**

- [ja3er.com](https://ja3er.com) — community-curated JA3 → client-software mapping.
- [TLS Fingerprint DB](https://tlsfingerprint.io/) — research aggregator.
- For server JARM: search Shodan `ssl.jarm:<hash>` to find shared infrastructure / origin candidates (see §16.15).

### 28.5 Reverse DNS Sweep & IPv6 Enumeration

When a target owns an IP range (their ASN), enumerate it.

**Reverse DNS sweep (within scope):**

```bash
# Single /24
for i in $(seq 1 254); do
 IP="203.0.113.$i"
 PTR=$(dig +short -x $IP)
 [ -n "$PTR" ] && echo "$IP -> $PTR"
done

# Larger range with parallelism
prips 203.0.113.0/22 | xargs -I {} -P 50 sh -c 'PTR=$(dig +short -x {}); [ -n "$PTR" ] && echo "{} -> $PTR"'
```

**Mass DNS approach (better for large ranges):**

```bash
# zdns: install via go install github.com/zmap/zdns/cmd/zdns@latest
prips 203.0.113.0/22 | zdns PTR
```

**Banner-only sweep (no DNS round trip):**

```bash
# masscan + banner-grab
sudo masscan -p80,443 203.0.113.0/22 --rate=1000 --banners -oX masscan.xml
```

**IPv6 enumeration:**

IPv6 has weaker enumeration tradition (huge address space precludes brute-force) but the AAAA records and known-allocation prefixes are still useful.

```bash
# AAAA records for every discovered subdomain
for sub in $(cat all-subs.txt); do
 AAAA=$(dig +short AAAA $sub)
 [ -n "$AAAA" ] && echo "$sub -> $AAAA"
done

# IPv6 reverse DNS sweep is generally infeasible (2^64 host bits per subnet)
# Instead: extract IPv6 prefixes from the target's allocations
whois -h whois.cymru.com " -v target.example.com" # gets ASN; then look up prefix
```

**BGP route observation:**

- **RouteViews** — `http://archive.routeviews.org/` (free; historical BGP routing table snapshots).
- **RIPE RIS** — `https://ris.ripe.net/` (free; route collectors).
- Use these to detect route hijacks against the target's prefixes (defensive intel; sometimes IOC).

**Reverse DNS pivots from third-party IPs:**

If a third-party shows the target's domain in PTR records (e.g., a hosting provider's IP has PTR `customer-acme.example.com.hostingprovider.net`), that's a pivot for adjacent customer infrastructure on the same provider/datacenter.

---


## 29. Threat Intel & IOCs

- Vendor / CERT advisories: CISA/NSA/CSA joint advisories, CERT-EU, NCSC-UK, JPCERT/CC, CERT-UA.
- [MISP Project](https://www.misp-project.org/) and public MISP feeds.
- [OpenCTI](https://www.opencti.io/) — CTI knowledge graph.
- [Malpedia](https://malpedia.caad.fkie.fraunhofer.de/) — malware families, YARA, references.
- [ThreatFox](https://threatfox.abuse.ch/), [URLHaus](https://urlhaus.abuse.ch/), [SSLBL](https://sslbl.abuse.ch/).
- [MalwareBazaar](https://bazaar.abuse.ch/) — hash-based sample sharing.
- [PhishTank](https://www.phishtank.com/), [OpenPhish](https://openphish.com/).

### 29.1 Malware Analysis & Sandboxes

- Static: [pefile](https://github.com/erocarrera/pefile), [FLOSS](https://github.com/mandiant/flare-floss), [capa](https://github.com/mandiant/capa).
- Similarity: SSDEEP, TLSH.
- Sandboxes: [ANY.RUN](https://any.run/), [Hybrid Analysis](https://www.hybrid-analysis.com/), [CAPE](https://capesandbox.com/), [Tria.ge](https://tria.ge/).
- Intelligence: [Intezer](https://analyze.intezer.com/) (code reuse), [VirusTotal](https://www.virustotal.com/) — **caution: uploads become public**.
- TLS: [JA3](https://github.com/salesforce/ja3), [JA4](https://github.com/FingerprinTLS/ja4).

### 29.2 Vulnerability Prioritization Data Sources

Methodology in companion skill §28. Concrete data sources here.

| Source | URL | What it tells you |
|---|---|---|
| **NVD** | `https://nvd.nist.gov/vuln/search` (or API `services.nvd.nist.gov/rest/json/cves/2.0`) | Base CVE catalog with CVSS v2/v3 scores. |
| **EPSS** | `https://www.first.org/epss/` (CSV at `https://epss.cyentia.com/epss_scores-current.csv.gz`) | 0.0-1.0 probability of exploit in next 30 days. Updated daily. |
| **CISA KEV** | `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` | CVEs proven exploited in the wild + federal-agency due-by dates. |
| **ExploitDB** | `https://www.exploit-db.com/`; offline DB via `searchsploit` | POC code presence (Metasploit, Python, shell). |
| **Metasploit module catalog** | `https://www.rapid7.com/db/modules/` (or `msfconsole > search cve:CVE-2024-XXXX`) | Automation availability. |
| **InTheWild.io** | `https://inthewild.io/` | Community-curated "actively exploited" tracker. |
| **OpenCVE** | `https://www.opencve.io/` | Timeline + watchlist + alerts. |
| **Trickest CVE → POC mapping** | `https://github.com/trickest/cve` | Auto-generated CVE → public POC repo links. |
| **GitHub Security Advisories** | `https://github.com/advisories` | Per-language / per-ecosystem advisories. |
| **MITRE CVE List** | `https://cve.mitre.org/cve/` | Official CVE registry. |
| **VulnDB** | `https://vulndb.cyberriskanalytics.com/` | Paid; commercial enrichment. |
| **OSV.dev** | `https://osv.dev/` | Open-source vulnerability DB; JSON API. |
| **Vulncheck KEV** | `https://vulncheck.com/kev` | Expanded KEV feed (more than CISA). |
| **Tenable Research** | `https://www.tenable.com/research` | Tenable's CVE detail enrichment. |
| **Qualys ThreatPROTECT** | `https://threatprotect.qualys.com/` | Qualys' threat-context enrichment. |

**Workflow:**

```bash
# 1. Get EPSS score for a CVE
curl -sk "https://api.first.org/data/v1/epss?cve=CVE-2024-3400" | jq '.data[0]'

# 2. Check if in CISA KEV
curl -sk https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | \
 jq '.vulnerabilities | select(.cveID == "CVE-2024-3400")'

# 3. Check ExploitDB
searchsploit cve 2024-3400

# 4. Check Metasploit
msfconsole -q -x "search cve:2024-3400; exit"
```

**Bulk prioritization** (given a Nuclei scan output with N CVEs):

```bash
# Extract CVEs from nuclei JSON output
jq -r '.info.classification.["cve-id"]?' nuclei-results.json | sort -u > cves.txt

# Annotate each with EPSS + KEV
while IFS= read -r CVE; do
 EPSS=$(curl -sk "https://api.first.org/data/v1/epss?cve=$CVE" | jq -r '.data[0].epss // "N/A"')
 KEV=$(curl -sk https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | \
 jq --arg c "$CVE" '.vulnerabilities | select(.cveID == $c) | .vulnerabilityName // empty')
 KEV_FLAG=$([ -n "$KEV" ] && echo "KEV" || echo "")
 echo "$CVE | EPSS:$EPSS | $KEV_FLAG"
done < cves.txt | sort -t: -k2 -nr
```

### 29.3 HackerOne Disclosed Reports Reference

Use `testing/offensive-osint/scripts/h1_reference.py` (no API key required, public GraphQL) to pull community-validated findings as reference while testing. Run it at session start for the target's tech stack or attack type.

**Key modes:**

```bash
# Top voted community reports — best validated techniques
python3 testing/offensive-osint/scripts/h1_reference.py --top-voted --limit 25

# Highest bounty reports — business-impact framing reference
python3 testing/offensive-osint/scripts/h1_reference.py --top-bounty --limit 10

# Keyword search across pages (50 results/page)
python3 testing/offensive-osint/scripts/h1_reference.py --top-voted --query "SSRF" --pages 10
python3 testing/offensive-osint/scripts/h1_reference.py --top-voted --query "auth bypass|OAuth|OIDC" --pages 5
python3 testing/offensive-osint/scripts/h1_reference.py --top-voted --query "open redirect" --pages 5

# Filter by severity (client-side)
python3 testing/offensive-osint/scripts/h1_reference.py --top-bounty --severity critical high --pages 3

# Program-specific disclosures (requires program handle)
python3 testing/offensive-osint/scripts/h1_reference.py --program gitlab --pages 5
python3 testing/offensive-osint/scripts/h1_reference.py --lookup-program gitlab # resolve handle → team ID

# JSON output for piping / jq
python3 testing/offensive-osint/scripts/h1_reference.py --top-voted --query "XSS" --pages 5 --json | jq '..report.url'
```

**When to run:**

- At session start: `--top-voted` to load high-signal baseline
- After identifying target's tech stack: `--query "<tech>" --pages 10`
- Before probing a specific attack class: `--query "SSRF|XXE|SSTI" --pages 5`
- For report writing: `--query "<vuln type>" --top-bounty` to find comparable severity/bounty

**H1 GraphQL quirks (documented):**

- Max 50 results/page regardless of `first:` value — use `--pages` for breadth
- `disclosed_at` field crashes H1 server when combined with substate filter — omitted
- Sort + substate filter combo crashes — script auto-routes around this

---


## 40. Severity Decision Matrix — Worked Examples

When in doubt, anchor on these worked examples (drawn from real engagements):

| Finding | Severity | Why |
|---|---|---|
| `/.git/config` reachable on prod webapp | **CRITICAL** | Full source-code disclosure; secret history reconstructable. |
| `/.env` reachable on prod webapp | **CRITICAL** | Plaintext creds (DB, cloud, API). |
| Open Firebase RTDB returning data | **CRITICAL** | All app data readable; often writable. |
| Listable S3 bucket containing PII | **CRITICAL** | Direct data exfil. |
| Listable S3 bucket containing logs only | HIGH | Internal hostnames + paths in logs; pivot data. |
| Spring Boot `/actuator/env` exposed | **CRITICAL** | DB creds, JWT secrets, cloud keys in env. |
| Spring Boot `/actuator/heapdump` exposed | **CRITICAL** | Heap contains live secrets in string form. |
| Open Elasticsearch (`/_cat/indices` returns) | **CRITICAL** | Full data reads; often writable. |
| Open MongoDB (no auth) | **CRITICAL** | Full data + password-hash collection. |
| Open Redis (no AUTH) | **CRITICAL** | Write `authorized_keys` → SSH foothold. |
| Open Docker API (port 2375) | **CRITICAL** | Container/host takeover. |
| Public PMAK validated live with broad scope | **CRITICAL** | Full Postman account + all team workspaces. |
| Public AWS root access key validated live | **CRITICAL** | Full account compromise. |
| Live AWS IAM-user key found on GitHub | HIGH | Limited scope (depends on IAM policy); often elevatable. |
| Live GitHub PAT found in JS bundle | HIGH | Repo write access (depends on scope). |
| Live Slack token in pastebin | HIGH | Workspace data + history; sometimes channel post. |
| Sourcemap (`.js.map`) accessible on prod | HIGH | Frontend source disclosure. |
| Open GraphQL introspection on prod | HIGH | Full schema → mutations + business-logic discovery. |
| Subdomain takeover possible (Heroku / GitHub Pages / etc.) | HIGH | Takeover → phishing on trusted domain. |
| Reflected CORS with credentials on `/api/billing` | HIGH | CSRF-via-CORS for billing data. |
| Verb tampering: DELETE allowed on documented-GET-only endpoint | HIGH | Authz bypass; potentially destructive. |
| `phpinfo.php` reachable on prod | HIGH | Discloses paths, env vars, modules → vuln-version pivot. |
| Tomcat `/manager/html` reachable | HIGH | Often default creds; WAR upload = RCE. |
| Jenkins script console accessible | HIGH | Groovy script execution = RCE. |
| Missing HSTS on `/login` | HIGH (escalated from MED) | Login pages must enforce HSTS. |
| Missing HSTS on standard pages | MEDIUM | Hardening gap. |
| Missing CSP | MEDIUM | XSS impact mitigation gone. |
| Internal IP / K8s service DNS in JS | MEDIUM | Internal topology disclosure. |
| Apache `/server-status` reachable | MEDIUM | Live request visibility. |
| `android:debuggable=true` on prod app | **CRITICAL** | Production debug-build → full client compromise. |
| `android:allowBackup=true` (no whitelist) | MEDIUM | App data exfil via `adb backup`. |
| `android:usesCleartextTraffic=true` | MEDIUM | MITM-able on hostile networks. |
| Sensitive deep-link handler (`myapp://reset-password`) | HIGH | Other apps can trigger sensitive flows. |
| Exported Android component without permission | MEDIUM | IPC attack surface. |
| Slack webhook URL leaked | MEDIUM | Send to channel; can be used for social-eng. |
| Twilio Account SID leaked (no auth token) | MEDIUM | Half a credential pair; plus account enumeration. |
| Wildcard CORS on data-returning API | MEDIUM | Lower than reflected+creds but still exfil-able. |
| Missing `X-Frame-Options` | LOW | Clickjacking. |
| `.DS_Store` exposed | LOW | Directory listing of dev's machine. |
| Stripe **test** key leaked | LOW | No real money risk. |
| Firebase URL exposed (no open RTDB) | LOW | Project-ID disclosure only. |
| Cert pinning missing in mobile app | LOW | MITM possible on hostile networks. |
| Outdated WordPress install detected | LOW | Pending CVE confirmation. |
| Missing `Referrer-Policy` / `Permissions-Policy` | INFO | Hardening, not an exposure. |
| `/.well-known/security.txt` discovered | INFO | Useful contact info only. |
| Domain in breach with 0 named accounts | INFO | Contextual only. |
| Private bucket exists (HEAD 403) | INFO | Asset only, no finding. |
| Open kubelet on 10250 | **CRITICAL** | Pod exec without K8s API auth. |
| Open etcd on 2379 | **CRITICAL** | Cluster state + secrets. |
| K8s API on 6443 with anonymous-auth | HIGH | Cluster recon; sometimes pod exec. |
| K8s dashboard exposed without auth | HIGH | Cluster admin UI. |
| Helm Tiller (Helm 2) on 44134 | HIGH | Cluster-admin scope. |
| Citrix Netscaler with KEV CVE | **CRITICAL** | Patch immediately; actively exploited. |
| F5 BIG-IP TMUI accessible | HIGH | TMUI = admin panel; CVE-2022-1388 if unpatched = CRIT. |
| Pulse Secure with CVE-2024-21887 | **CRITICAL** | KEV; chained command injection. |
| FortiGate with CVE-2024-21762 | **CRITICAL** | KEV; auth bypass + RCE. |
| PaloAlto GlobalProtect with CVE-2024-3400 | **CRITICAL** | KEV; pre-auth RCE. |
| VMware vCenter with CVE-2021-21972 | **CRITICAL** | KEV; pre-auth RCE. |
| VMware ESXi exposed without VPN | HIGH | Multiple CVEs (ESXiArgs ransomware vector). |
| MS Exchange with ProxyShell/Logon/NotShell unpatched | **CRITICAL** | KEV chain; RCE + mailbox dump. |
| AWS Lambda Function URL accessible anonymously | HIGH | Direct invocation; check IAM auth posture. |
| Public Cloud Run / Cloud Function unauthenticated | HIGH | Same. |
| Public Docker registry (anonymous catalog) | MEDIUM | Image enum + secret hunt in layers. |
| GitHub Actions secrets echoed in workflow logs | HIGH | Secret-in-log = full secret disclosure. |
| GitHub Actions `pull_request_target` checkout of fork code | HIGH | Class of bug; secrets accessible to attacker PRs. |
| GitLab self-hosted with CVE-2021-22205 | **CRITICAL** | KEV; ExifTool RCE. |
| Jenkins with `pull_request_target`-equivalent misconfig | HIGH | Build secrets accessible to PRs. |
| Public Notion page with internal SOPs | MEDIUM | Operational intel; sometimes credentials. |
| Public Trello board with credentials in cards | HIGH | Often plaintext API keys. |
| Public Confluence space with onboarding docs | MEDIUM | Seed creds + tech-stack reveal. |
| Public Miro board with architecture diagrams | LOW | Internal-host disclosure. |
| DMARC policy `p=none` on production sending domain | MEDIUM | Spoof feasible (escalated from LOW for risk surface). |
| SPF `~all` (softfail) without strict DMARC | MEDIUM | Spoofs land in spam, but land. |
| MX server allows open relay (test with 250 OK to RCPT TO foreign domain) | HIGH | Spam + spoof feasibility. |
| Live Anthropic / OpenAI API key with broad scope | **CRITICAL** | Quota cost + potential PII in past responses. |
| Live npm token with `publish` scope | **CRITICAL** | Supply-chain compromise of all maintained packages. |
| Live PyPI / Docker Hub / GHCR token with publish scope | **CRITICAL** | Supply-chain compromise. |
| Atlassian token with admin scope | HIGH | Workspace-wide read; sometimes write. |
| Subdomain takeover candidate confirmed | HIGH | Trusted-domain phishing surface. |
| Sensitive CI/CD wordlist hits (Jenkinsfile, .gitlab-ci.yml on public repo) | MEDIUM | Build-script intel; often references secret names. |
| Public Postman workspace with internal API endpoints | MEDIUM | API attack surface mapped. |
| WAF/CDN trivially bypassable (origin discoverable via §16.15) | HIGH | All WAF protections null. |
| TLS 1.0/1.1 supported on prod | MEDIUM | Compliance gap; PCI-DSS forbids TLS 1.0. |
| RC4 / 3DES cipher accepted | MEDIUM | NOMORE / SWEET32 attacks. |
| Cert about to expire (<30 days) | LOW | Operational risk; not exploitable. |
| Self-signed cert on prod | MEDIUM | Trust failure for users. |
| Heartbleed (CVE-2014-0160) detected | **CRITICAL** | Memory disclosure including session tokens + keys. |
| Public Slack invite link discoverable | HIGH | Anyone joins workspace; full DM/channel access. |
| Vendor / supplier / e-procurement portal publicly exposed + breach corpus shows vendor accounts compromised | **HIGH** | Vendor impersonation + procurement fraud (BEC vector); regulatory exposure if PII/payment data flows. |
| Job-application / careers portal collects PII over plain HTTP (no TLS) | **HIGH** | Cleartext PII at scale; regulatory exposure under GDPR / CCPA / India DPDP Act / LGPD. |
| Decommissioned legacy mail (NXDOMAIN today) + breach corpus has historical employee URLs against it + cloud SSO migration confirmed via autodiscover IPs | **CRITICAL** | Stolen passwords almost certainly survived migration via reuse; SSO_EXPOSURE escalates regardless of the legacy host being dead. |
| Public-facing intranet (`intranet.<domain>` resolves and returns content without VPN) | MEDIUM | Internal-staff portal exposed; often leaks org structure, employee directory, internal apps. |
| Staging / preprod / UAT / sandbox subdomain publicly resolvable | MEDIUM | Often weaker auth, debug endpoints, test creds; sometimes mirrors prod data. |
| `vpn.<domain>` resolves but vendor + version unknown (passive only) | INFO | Attack surface flag only; escalate to HIGH-CRITICAL after active fingerprint matches a KEV CVE (§16.16). |
| DMARC RUA points to a third-party reporting vendor (kdmarc / dmarcian / Valimail / Agari / EasyDMARC) | INFO | Tenant signal only; vendor compromise = DMARC bypass for *all* their customers. |

---
