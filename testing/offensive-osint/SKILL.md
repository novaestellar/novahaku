---
name: offensive-osint
description: "Operational arsenal for external red-team and bug-bounty reconnaissance. Concrete wordlists (28 Swagger paths, 13 GraphQL paths, 35 high-risk ports, 6 missing-header findings, 15 always-on HTTP checks, 5 SAML paths, cloud bucket permutations, JS guess-paths, vendor product fingerprints for Citrix/F5/Pulse/Fortinet/Cisco/PaloAlto/VMware/Exchange, cloud-native service fingerprints, container/K8s exposure paths, CI/CD platform paths, documentation/wiki leak paths, WHOIS/RDAP, DNS record catalog, Wayback CDX recipes), 80-pattern secret-regex catalog (incl. modern AI API keys: Anthropic/OpenAI/HuggingFace/Cloudflare/DigitalOcean/npm/PyPI/Docker Hub/Atlassian/DataDog/Sentry/ngrok; plus a provider-expansion tier: Postman PMAK/GitLab/Square/Shopify/Mailchimp/PagerDuty/Asana/Databricks/Grafana/Terraform Cloud/Fastly/Algolia/Segment/Airtable/GCP+Google OAuth/Azure AD/Facebook OAuth/RubyGems/JFrog/Okta/Slack app-level/Dropbox/Doppler/HashiCorp Vault/Firebase Cloud Messaging), 80+ dork corpus across 9 categories, GitHub code-search dorks, copy-paste curl/httpie probes for every check, post-discovery enumeration workflows (AWS/GitHub/Slack/JWT/PMAK/Anthropic/OpenAI), endpoint interest scoring rubric (0–100), mobile app ownership confidence + APK static-analysis pipeline (acquisition, apktool/aapt2/jadx/androguard decompile, manifest exported-component/deep-link/misconfig extraction, Firebase config, network-security-config, embedded-secret scan), identity-fabric endpoints (Entra/Okta/ADFS/Google/SAML/M365 Teams+SharePoint+OneDrive+OAuth + user-enum), GraphQL field-suggestion enumeration when introspection disabled, 9 read-only secret validators (Postman/AWS/GitHub/Slack/Anthropic/OpenAI/npm/Atlassian/DataDog), Postman workspace search (verified endpoint), Stack Exchange sweep, public SaaS dorks, email security analysis (SPF/DMARC/DKIM/BIMI/MTA-STS/DNSSEC), origin-discovery / CDN bypass techniques, TLS deep audit (sslyze/testssl.sh/JA3/JA4), reverse-DNS sweep + IPv6 enum, vulnerability prioritization data sources (NVD/EPSS/CISA KEV/ExploitDB/Metasploit), 27 attack-path hint templates, 80+ severity-matrix examples, LinkedIn employee enumeration, job posting tech-stack analysis, Slack/Discord workspace discovery, package registry leak hunting (npm/PyPI/Docker Hub/Quay/GHCR), sat imagery for physical recon, tooling quick-install one-liners, sector-specific recon notes (healthcare/finance/ICS-SCADA/IoT/government), runnable stdlib-only secret_scan.py helper, plus the existing tool references for username/email/phone/people/social/breach/infrastructure/crypto/media/geospatial/AI/archiving/automation. Use when you need concrete probe paths, regexes, payloads, scoring rules, curl one-liners, and tool URLs for an authorized external recon engagement."
version: 2.2
sources: hackerone_public, community, public_research
triggers:
 - external recon
 - external red team
 - red team external
 - attack surface management
 - ASM
 - bug bounty recon
 - bug bounty
 - reconnaissance
 - footprinting
 - asset discovery
 - swagger discovery
 - openapi discovery
 - graphql introspection
 - graphql discovery
 - subdomain enumeration
 - subdomain takeover
 - cloud bucket enumeration
 - bucket enum
 - S3 enum
 - GCS enum
 - Azure blob enum
 - identity fabric
 - SSO discovery
 - IdP fingerprinting
 - tenant fingerprinting
 - okta enum
 - entra enum
 - azure AD enum
 - ADFS enum
 - SAML metadata
 - mobile recon
 - APK analysis
 - mobile attack surface
 - secret scanning
 - secret leak
 - leaked credential
 - github dorking
 - google dorking
 - bing dorking
 - DDG dorking
 - postman workspace
 - stack exchange OSINT
 - breach lookup
 - have I been pwned
 - HudsonRock cavalier
 - infostealer
 - dehashed
 - intelx
 - shodan recon
 - censys recon
 - certificate transparency
 - crt.sh
 - JARM
 - favicon mmh3
 - JS endpoint extraction
 - sourcemap leak
 - copy paste probes
 - curl one-liner
 - email security analysis
 - SPF DMARC DKIM
 - origin discovery
 - CDN bypass
 - WAF bypass
 - vendor product fingerprints
 - Citrix Netscaler
 - F5 BIG-IP
 - Pulse Secure
 - FortiGate
 - PaloAlto GlobalProtect
 - Cisco AnyConnect
 - VMware vCenter
 - cloud native fingerprint
 - Lambda function URL
 - Cloud Run
 - kubernetes exposure
 - kubelet
 - etcd
 - CI CD exposure
 - Jenkins recon
 - GitLab self-hosted
 - GitHub Actions secrets
 - documentation leak
 - Notion public
 - Confluence anonymous
 - Trello board
 - WHOIS RDAP
 - DNS record catalog
 - Wayback CDX
 - LinkedIn enumeration
 - job posting tech stack
 - Slack workspace discovery
 - Discord server discovery
 - npm token leak
 - PyPI token leak
 - Docker Hub leak
 - sat imagery physical recon
 - TLS deep audit
 - JA3 JA4
 - reverse DNS sweep
 - IPv6 enumeration
 - CVE prioritization
 - EPSS scoring
 - CISA KEV
 - vulnerability prioritization
 - tooling install
 - sector specific recon
 - healthcare DICOM
 - finance SWIFT
 - ICS SCADA
 - Modbus
 - BACnet
 - post discovery workflow
 - JWT triage
 - AWS key triage
 - GraphQL field suggestion
 - Anthropic API key
 - OpenAI API key
 - Microsoft 365 deep
 - Teams federation
 - SharePoint enum
 - OneDrive enum
 - hackerone reference
 - h1 hacktivity
 - disclosed reports
 - community bug reports
 - prior disclosures
 - bug bounty reference
---

# Offensive OSINT — External Red-Team Arsenal

> Companion skill: `osint-methodology` (the "how to think" skill). This skill is the "what to reach for." Use them together.


## 0. When to use / When NOT

**Use this skill when:**

- You need concrete probe paths, wordlists, regexes, payloads, scoring rules, or tool URLs.
- You're executing reconnaissance and need the actual technical reference (vs. methodology).
- You're building a recon automation and need specific lists to seed it.

**Do NOT use this skill when:**

- The user is asking for active exploitation, post-exploitation, or anything past reconnaissance.
- The user is asking for defensive / blue-team detections.
- The target's authorization isn't established — see §1.

---

## 1. Authorization & Legal Posture

For assets the operator owns or has written authorization to assess. Soft scope check before acting against an unverified third-party target — see methodology skill §1 for the full posture.

---

## 2. Confidence Levels

- **TENTATIVE** — plausible based on indirect evidence (snippet-only dork match, single-source asset, inferred email pattern).
- **FIRM** — directly observed (subdomain resolves, HEAD-confirmed bucket exists, banner returned).
- **CONFIRMED** — verified via independent corroboration OR direct verification (live PMAK validation, multiple sources agree, listable bucket with object retrieval).

---

## 3. Output Format Conventions

Findings should carry: `id`, `module`, `asset_key`, `category`, `severity` (info/low/medium/high/critical), `confidence`, `title`, `description`, `evidence` (url + UTC timestamp + sha256 + raw ≤ 2 KiB), `references`, `remediation`. UTC timestamps everywhere.

---

## 4. Source Hygiene & Citations

URL + UTC timestamp + SHA-256 + tool version + run_id, every artifact. PNG screenshots, JSONL run logs, raw HTTP captures capped at 2 KiB body.

---

## 5. Do NOT

- Don't paste creds/PII/session tokens into cloud LLMs.
- Don't run destructive probes outside DEEP/`--aggressive`.
- Don't use validated credentials for anything except read-only liveness check.
- Don't single-source attribute.
- Don't assume vendor labels are ground truth.

---

## 6. General OSINT (curated tool refs)

- [OSINT Bookmarks](https://tools.myosint.training/) — comprehensive bookmarks.
- [OSINT Framework](https://osintframework.com/) — tool/resource directory.
- [IntelTechniques Tools](https://inteltechniques.com/tools/) — investigative suite.
- [Bellingcat Toolkit](https://www.bellingcat.com/resources/2024/09/24/bellingcat-online-investigations-toolkit/) — investigative journalism.
- [CyberSudo OSINT Toolkit](https://docs.google.com/spreadsheets/d/1EC0sKA_W9znzsxUt0wye9UYtyATXw5m8) — OSINT websites list.
- [Google Dorks](https://dorksearch.com/) — efficient Google searching.
- [Distributed Denial of Secrets](https://ddosecrets.com/) — leaked datasets.
- [Country-Specific Resources](https://digitaldigging.org/osint/) — country-targeted OSINT.

## 7. Search Engines

| Tool | Notes |
|------|-------|
| [Carrot2](https://search.carrot2.org/#/search/web) | Clusters results by topic |
| [etools](https://www.etools.ch/) | Metasearch |
| [Kagi](https://kagi.com/) | Privacy-first, non-personalized |
| [Brave Search](https://search.brave.com/) | Independent index; Goggles for custom ranking |
| [PDF Search](https://www.pdfsearch.io/) | PDF + table of contents |
| [Google Fact Check Explorer](https://toolbox.google.com/factcheck/explorer) | Cross-site fact-check |

---

## 8. Username & Email Investigation

| Tool | Purpose |
|------|---------|
| [Sherlock](https://github.com/sherlock-project/sherlock) | Username search across social networks |
| [Maigret](https://github.com/soxoj/maigret) | Profile collector by username |
| [What's My Name](https://whatsmyname.app/) | Username search |
| [Holehe](https://github.com/megadose/holehe) | Email registration check |
| [Epieos](https://epieos.com/) | Email pivots and metadata |
| [OSINT Industries](https://osint.industries/) | Email/username/phone lookups |
| [Hunter.io](https://hunter.io/) | Domain → emails |
| [EmailRep](https://emailrep.io/) | Email reputation |
| [Emailable](https://emailable.com/) | Email verification |
| [Mugetsu](https://mugetsu.io/) | X/Twitter username history |
| [RocketReach](https://rocketreach.co/) / [Apollo](https://www.apollo.io/) | Email enrichment + pattern guessing |
| [PhoneInfoga](https://github.com/sundowndev/phoneinfoga) | Phone number intelligence |

Browser extensions: [GetProspect](https://chromewebstore.google.com/detail/email-finder-getprospect/bhbcbkonalnjkflmdkdodieehnmmeknp), [SignalHire](https://chrome.google.com/webstore/detail/signalhire-find-email-or/aeidadjdhppdffggfgjpanbafaedankd).

---

## 9. People Search

- [TruePeopleSearch](https://www.truepeoplesearch.com/) — free U.S. people search.
- [WhitePages](https://www.whitepages.com/), [Spokeo](https://www.spokeo.com/), [Webmii](https://webmii.com/), [Pipl](https://pipl.com/) (paid).
- [Clearbit](https://clearbit.com/) — company/individual data enrichment.
- [FaceCheck](https://facecheck.id/) / [FaceSeek](https://faceseek.online/) — reverse face search.

---

## 10. Phone Number OSINT

- [TrueCaller](https://www.truecaller.com/) — caller ID + spam blocking.
- [ThatsThem](https://thatsthem.com/) — reverse phone search.
- [Infobel](https://infobel.com/) — non-USA phone search.
- [FreeCarrierLookup](https://freecarrierlookup.com/) — carrier/type (US).
- [NumlookupAPI](https://numlookupapi.com/) [Freemium] — programmatic carrier checks.
- [CallerIDTest](https://calleridtest.com/), [Advanced Background Checks](https://www.advancedbackgroundchecks.com/).

---

## 11. Email-Pattern Inference (TENTATIVE candidates)

Given a `(first_name, last_name, domain)`, generate these 8 candidate addresses for breach pre-hits, phishing list curation, and downstream enrichment. Mark as **TENTATIVE** confidence until corroborated.

```
{first}.{last}@{domain} # john.doe@example.com
{first}{last}@{domain} # johndoe@example.com
{first}@{domain} # john@example.com
{first[0]}{last}@{domain} # jdoe@example.com
{first}.{last[0]}@{domain} # john.d@example.com
{last}@{domain} # doe@example.com
{first}_{last}@{domain} # john_doe@example.com
{first}-{last}@{domain} # john-doe@example.com
```

Lowercase before lookup. Strip diacritics for ASCII fallback. If the org uses a known pattern (e.g., Hunter.io shows `{first}.{last}` is dominant), prioritize that one and mark FIRM.

---

## 12. Email-Harvest Source Stack

Six parallel sources, dedup at the end:

1. **IntelX phonebook API** — 2-step search + poll. Largest single source for breach-era addresses.
2. **Hunter.io** — domain-search endpoint. ~25 free/month. Returns verified emails + roles.
3. **crt.sh** — extract X.509 SAN extensions. Many certs include admin/contact emails.
4. **DuckDuckGo SERP scrape** — HTML scrape of `"@{target-domain}"` results.
5. **Bing SERP scrape** — same query, complementary index.
6. **Wayback CDX** — historic snapshots of the target's homepage / contact / about pages often contain emails removed from the live site.

**Email regex:**

```regex
\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b
```

**Noise filter (reject numeric-only locals):**

```regex
^[0-9]+$
```

(Discards garbage like `12345@example.com` from random tokens.)

---

## 13. Social Media

| Platform | Tool |
|----------|------|
| Instagram | [Picuki](https://www.picuki.com/) — profile view without account |
| X/Twitter | [snscrape](https://github.com/snscrape/snscrape) — preferred CLI scraper; Twint as fallback |
| Facebook | [Graph Search](https://inteltechniques.com/tools/Facebook.html), [sowsearch.info](https://sowsearch.info/), [lookup-id.com](https://lookup-id.com/), [whopostedwhat.com](https://whopostedwhat.com/) |
| Facebook (research) | [Meta Content Library](https://transparency.meta.com/researcher) — CrowdTangle successor (researcher-gated) |
| YouTube/Twitch | [Social Blade](https://socialblade.com/) — analytics |
| TikTok | [Tokboard](https://tokboard.com/) — trends + profile analytics |
| Reddit | [Reveddit](https://www.reveddit.com/) — removed content; [RedTrack.social](https://redtrack.social/) — user history |
| Bluesky | [Firesky](https://firesky.tv/) — real-time firehose; [SkyView](https://bsky.jazco.dev/) — follower graphs |
| Mastodon | [FediSearch](https://fedisearch.skorpil.cz/) — cross-instance search; [Fedifinder](https://fedifinder.glitch.me/) — find Twitter users on Mastodon |
| Faces | [Search4Faces](https://search4faces.com/) |

---

## 14. Public Records & Company Information

- [OpenCorporates](https://opencorporates.com/) — world's largest open company DB.
- [SEC EDGAR](https://www.sec.gov/edgar.shtml) — U.S. company filings.
- [OpenOwnership Register](https://register.openownership.org/) — beneficial ownership.
- [MuckRock](https://www.muckrock.com/) — FOIA repository + request tracking.
- [EU Tenders (TED)](https://ted.europa.eu/) — EU procurement notices.
- [World Bank Projects](https://projects.worldbank.org/) — project + procurement records.
- [UK Companies House](https://find-and-update.company-information.service.gov.uk/) — UK companies + officers + filings.

### 14.1 RU registries

[Rusprofile](https://www.rusprofile.ru/), [Kontur.Focus](https://focus.kontur.ru/) (freemium), [zakupki.gov.ru](https://zakupki.gov.ru/) (procurement), EGRUL/EGRIP (official, captcha-gated).

### 14.2 CN registries + USCC + ICP

- **GSXT** — [gsxt.gov.cn](https://www.gsxt.gov.cn/) National Enterprise Credit Info; cross-check with Tianyancha / Qichacha.
- **USCC (Unified Social Credit Code)** — 18-character entity ID assigned to all CN legal entities. Format: `<region:6><authority:2><type:1><serial:9>`. Useful for joining GSXT records to ICP filings.
- **ICP Beian** — [beian.miit.gov.cn](https://beian.miit.gov.cn/) — every domain serving traffic in mainland CN must register an ICP filing; the filing links the domain to a USCC, which links to the legal entity in GSXT.
- Workflow: `target.cn` domain → ICP lookup → USCC → GSXT → entity name + officers + adjacent registered entities.

### 14.3 Sanctions & Compliance

- [OFAC SDN List](https://sanctionssearch.ofac.treas.gov/), [EU Sanctions Map](https://www.sanctionsmap.eu/).
- [OpenSanctions](https://www.opensanctions.org/) — aggregated.
- [OCCRP Aleph](https://aleph.occrp.org/) — investigative documents, leaks, company records.

---

## 15. Breach & Leak Data

- [Have I Been Pwned](https://haveibeenpwned.com/) — breach lookup; Pwned Passwords API (k-anonymity).
- [Dehashed](https://dehashed.com/) — credential search (paid).
- [IntelX](https://intelx.io/) — data intelligence.
- [LeakCheck](https://leakcheck.io/), [Snusbase](https://snusbase.com/), [BreachDirectory](https://breachdirectory.org/), [Scattered Secrets](https://scatteredsecrets.com/), [Phonebook](https://phonebook.cz/), [LeakPeek](https://leakpeek.com/).
- [Cavalier (Hudson Rock)](https://cavalier.hudsonrock.com/) — **infostealer log lookups; FREE; highest single-source ROI for finding compromised employee credentials in corporate SSO**.

### 15.0.1 HudsonRock Cavalier — direct API recipe

The web UI wraps a **public, unauthenticated JSON API**. Hit it directly:

```bash
# By domain (canonical first call)
curl -sk -m 30 "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-domain?domain=target.com" | jq .

# By email (single-account check)
curl -sk -m 30 "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email=alice@target.com" | jq .

# By URL (when target's app is the breach victim)
curl -sk -m 30 "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-url?url=https://app.target.com" | jq .
```

PowerShell:

```powershell
$hr = Invoke-RestMethod -Uri "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-domain?domain=$D" -TimeoutSec 30
"Employees: $($hr.employees) | Users: $($hr.users) | Third-party: $($hr.third_parties) | Total: $($hr.total)"
$hr.data.employees_urls | Sort-Object -Property occurrence -Descending | Select-Object -First 20
$hr.data.clients_urls | Sort-Object -Property occurrence -Descending | Select-Object -First 15
```

**Top-level JSON fields:**

- `total` — total stealer entries touching this domain.
- `totalStealers` — global stealer-log corpus size (context only).
- `employees` — count of `<*>@<domain>` accounts found.
- `users` — count of accounts where the domain appeared as a *visited* URL (customers/vendors).
- `third_parties` — accounts touching adjacent domains in the org.
- `data.employees_urls` — `{occurrence, type, url}` — internal apps where employees were logging in when stolen. **Subdomain hits here = recon gold.**
- `data.clients_urls` — same shape; user-facing apps (often reveals undocumented public portals).
- `data.stealer_families` — `{_key, _value}` → which stealer (RedLine / Lumma / StealC / Vidar / Raccoon).
- `data.dates_compromised` — `{_key, _value}` → temporal distribution.

**Free-tier caveats (CRITICAL to know):**

- Subdomain hostnames in `data.*_urls` past the first few are **redacted with asterisks** (`*****.target.com`). Pivot to paid Cavalier tier or other sources for unredacted.
- Free endpoint returns counts + sample URLs only. Cleartext passwords + emails are **never** in the free response.
- Rate limit ~1 req/sec/IP; 429 on burst. Sleep 1s between calls.
- For unredacted creds + bulk enumeration → paid Cavalier portal.

**Severity mapping (per §15.1 + §15.2):** `employees ≥ 10` → CRITICAL, **regardless of whether the breached service is still online** (legacy Lotus Domino / on-prem mail decommissioned + cloud SSO migration → employees almost always reuse passwords → SSO_EXPOSURE escalates CRITICAL).

### 15.1 Domain-Level Breach Severity Mapping

When you query a breach corpus by domain, map the result to severity like so:

| Stat | Severity |
|---|---|
| ≥ 10 employees compromised | **CRITICAL** |
| 1–9 employees compromised | **HIGH** |
| ≥ 1 end-user (non-employee) compromised | **MEDIUM** |
| Domain seen in breach with 0 named accounts | **INFO** |

**Employees vs end-users distinction:** an employee account is `<anything>@<target-domain>` (the breach victim is the target's own staff). An end-user account is the target's customer who reused a password — useful for credential-stuffing risk awareness but not directly compromising the target's identity fabric.

### 15.2 SSO_EXPOSURE finding

When a discovered SSO tenant (Entra GUID / Okta slug / Google Workspace domain) intersects with the breach corpus on its domain → `SSO_EXPOSURE` finding, severity **CRITICAL**. Evidence: tenant ID + product + employee count + per-account source attribution.

**Legacy-mail-decommissioned pattern (high-value variant):**

If `mail.<domain>` / `webmail.<domain>` returns **NXDOMAIN today** but HudsonRock/HIBP corpus still has historical employee credentials against it AND `autodiscover.<domain>` resolves to Microsoft IPs (M365) or `aspmx.l.google.com` MX (Workspace), the org migrated from on-prem to cloud — and the stolen passwords almost certainly survived the migration via password reuse. **Escalate to CRITICAL `SSO_EXPOSURE`** even when the legacy host is dead.

Concrete triggers (all three together):

1. `Resolve-DnsName mail.<domain> -Type A` → NXDOMAIN (legacy gone)
2. HudsonRock corpus has employee URLs against the *old* host (e.g. `mail.<domain>/names.nsf` for Lotus Domino, `mail.<domain>/owa/` for Exchange, `mail.<domain>/iwaredir.nsf` for iNotes, `mail.<domain>/zimbra/` for Zimbra)
3. Current MX → M365 / Google Workspace / Zoho cloud (DNS confirms migration)

Evidence pack: tenant GUID + breach count + 3+ legacy URLs from corpus + autodiscover Microsoft IPs + current MX. Recommend forced password rotation + MFA audit + Conditional Access review.

---

## 16. Pre-built Wordlists & Probe Paths

> **Content moved to [`references/wordlists.md`](references/wordlists.md).** Section numbering preserved — reference `§16` points here.

Sub-sections:
- `16.1 Swagger / OpenAPI discovery — 28 paths`
- `16.2 GraphQL discovery — 13 paths`
- `16.3 High-risk ports — 35 services`
- `16.4 Missing security headers — 6 findings`
- `16.5 Always-on HTTP checks — 15 paths`
- `16.6 SAML metadata — 5 paths`
- `16.7 SSO subdomain prefixes — 8 prefixes`
- `16.8 Cloud bucket permutation arsenal`
- `16.9 JS guess-paths for endpoint discovery`
- `16.10 Endpoint extraction regex tiers`
- `16.11 Internal-host leakage regexes`
- `16.12 Subdomain-takeover provider fingerprints (summary, 27 providers)`
- `16.13 Copy-Paste Probes (curl one-liners)`
- `16.14 Email Security Analysis (SPF/DMARC/DKIM/BIMI/MTA-STS/DNSSEC)`
- `16.15 Origin Discovery / CDN Bypass`
- `16.16 Vendor Product Fingerprints`
- `16.17 Cloud-Native Service Fingerprints`
- `16.18 Container & Kubernetes Exposure`
- `16.19 CI/CD Platform Exposure`
- `16.20 Documentation / Wiki Leak Paths`
- `16.21 WHOIS / RDAP / Historical`
- `16.22 DNS Record Catalog (TXT verification tokens, MX→IdP)`
- `16.23 Wayback CDX Deep Usage`
- `16.24 Common-Prefix Subdomain Sweep (active, low-detectability)`

## 17. Secret-Pattern Catalog — 80 patterns (29 base + 19 modern + 32 provider expansion)

> **Content moved to [`references/arsenal.md`](references/arsenal.md).** Section numbering preserved — reference `§17` points here.

## 18. Dork Corpus — 80+ templates, 9 categories

Substitute `{domain}` with the target domain (e.g., `example.com`) and `{company}` with the company name (e.g., `Acme Corporation`). Run via Google, Bing, Brave, DuckDuckGo, Yandex, Baidu — engines surface different results.

### 18.1 Files

```
site:{domain} filetype:env
site:{domain} ext:env OR ext:ini OR ext:cfg OR ext:conf
site:{domain} ext:sql OR ext:sqlite OR ext:dump OR ext:bak
site:{domain} ext:pem OR ext:key OR ext:p12 OR ext:pfx
site:{domain} ext:log
site:{domain} intitle:"index of"
site:{domain} inurl:.git OR inurl:/.git/
site:{domain} inurl:backup OR inurl:.bak OR inurl:old
site:{domain} ext:yml OR ext:yaml
site:{domain} ext:properties
```

### 18.2 Admin / login panels

```
site:{domain} inurl:admin OR inurl:login OR inurl:sso OR inurl:dashboard
site:{domain} intitle:"phpMyAdmin"
site:{domain} intitle:"Jenkins"
site:{domain} intitle:"Grafana"
site:{domain} intitle:"Kibana"
site:{domain} intitle:"Splunk"
site:{domain} (intitle:"login" OR intitle:"sign in")
site:{domain} intitle:"GitLab"
site:{domain} intitle:"Swagger" OR intitle:"OpenAPI"
site:{domain} inurl:phpinfo
```

### 18.3 Secrets / credential leakage

```
"{domain}" ("api_key" OR "apikey" OR "access_token")
"{domain}" (password OR passwd OR pwd)
site:pastebin.com "{domain}"
site:ghostbin.com "{domain}"
site:rentry.co "{domain}"
site:gist.github.com "{domain}"
site:hastebin.com "{domain}"
"{domain}" "BEGIN RSA PRIVATE KEY"
```

### 18.4 Cloud / CI / shadow-IT

```
site:s3.amazonaws.com "{domain}"
site:storage.googleapis.com "{domain}"
site:blob.core.windows.net "{domain}"
site:digitaloceanspaces.com "{domain}"
site:trello.com "{domain}"
site:*.atlassian.net "{domain}"
site:dev.azure.com "{domain}"
site:bitbucket.org "{domain}"
site:firebaseio.com "{domain}"
site:herokuapp.com "{domain}"
```

### 18.5 Docs / intel mining

```
site:{domain} filetype:pdf (confidential OR internal OR restricted)
site:{domain} filetype:xlsx OR filetype:csv
site:{domain} filetype:docx
site:scribd.com "{company}"
"{company}" filetype:pdf (salary OR payroll OR org-chart OR "organization chart")
site:linkedin.com/in "{company}"
site:slideshare.net "{company}"
```

### 18.6 Vuln indicators

```
site:{domain} intext:"sql syntax" OR intext:"you have an error in your sql"
site:{domain} intext:"Warning: mysql_"
site:{domain} intext:"Fatal error:" intext:"on line"
site:{domain} intext:"stack trace" OR intext:"Traceback (most recent call last)"
"Apache/2.4.49" site:{domain}
"Server: nginx/1.14" site:{domain}
site:{domain} inurl:wp-content OR inurl:wp-includes
```

### 18.7 Internal tool exposure

```
site:{domain} intitle:"Splunk"
site:{domain} intitle:"Grafana"
site:{domain} intitle:"Kibana"
site:{domain} intitle:"Prometheus Time Series"
site:{domain} intitle:"Jaeger UI"
site:{domain} intitle:"AlertManager"
site:{domain} intitle:"Argo CD"
site:{domain} intitle:"Sonarqube"
site:{domain} intitle:"Sentry"
site:{domain} intitle:"Confluence"
site:{domain} intitle:"Jira"
site:{domain} intitle:"GitLab"
site:{domain} intitle:"Gitea"
site:{domain} intitle:"Drone CI"
site:{domain} inurl:"/jenkins/"
```

### 18.8 Backup / dump file extensions

```
site:{domain} ext:bak OR ext:backup OR ext:old OR ext:orig OR ext:save OR ext:swp
site:{domain} ext:tar OR ext:tar.gz OR ext:tgz OR ext:zip OR ext:rar OR ext:7z
site:{domain} ext:db OR ext:sqlite OR ext:sqlite3 OR ext:mdb
site:{domain} ext:dump OR ext:rdb OR ext:bson
site:{domain} (intext:"-- MySQL dump" OR intext:"PostgreSQL database dump")
site:{domain} ext:pcap OR ext:pcapng OR ext:cap
site:{domain} ext:core OR ext:hprof OR ext:dmp
```

### 18.9 Sector-specific (healthcare / finance / gov)

```
# Healthcare
site:{domain} (filetype:pdf OR filetype:xlsx) (HIPAA OR PHI OR "patient records")
site:{domain} ("DICOM" OR "HL7" OR "ICD-10")

# Finance
site:{domain} (filetype:pdf OR filetype:xlsx) (SOC OR "audit report" OR "internal control")
site:{domain} (filetype:pdf OR filetype:xlsx) ("Form 10-K" OR "Form 10-Q" OR earnings)
site:{domain} ("SWIFT" OR "BIC" OR IBAN OR "wire transfer")

# Gov / public sector
site:{domain} (filetype:pdf OR filetype:doc) (FOUO OR "controlled unclassified" OR CUI)
site:{domain} (filetype:pdf OR filetype:xlsx) ("personnel security" OR clearance)
```

### 18.10 Result classification

After running, score each result via URL signature → title hint → snippet regex:

- **CRITICAL URL signatures:** `.pem`, `.p12`, `.pfx`, `.key` extensions; `id_rsa` filename.
- **HIGH URL signatures:** `/.env`, `/.git/`, database dumps, `wp-config.bak`, `/phpmyadmin`, `/jenkins`, `/phpinfo.php`.
- **MEDIUM URL signatures:** `/admin`, `/login`, `/swagger`, `.log`, `/backup`, `.DS_Store`.
- Snippet content (e.g., a secret regex hit in the snippet) overrides URL signature only if higher severity.
- Confidence: snippet-only match = TENTATIVE (operator must visit URL to confirm; tag detectability=medium).

---

## 19. GitHub Code-Search Dorks for Targets — 13 dorks

Apply each template to `{target}` (root domain stem like `acme`), `{domain}` (full root domain like `acme.com`), and optionally `{company}` (`Acme Corporation`):

```
"{target}" filename:.env
"{target}" filename:.env.example
"{target}" filename:config
"{target}" AWS_ACCESS_KEY_ID
"{target}" AWS_SECRET_ACCESS_KEY
"{target}" password
"{target}" api_key
"{target}" secret
"{target}" authorization: Bearer
"{target}" filename:id_rsa
"{target}" filename:.git-credentials
"{target}" filename:wp-config.php
"@{domain}" password # emails + password context
```

**Requirements:** GitHub personal access token (any scope; recommend a fine-grained PAT with read-only repo access). Rate limit per token; concurrency cap ≤5.

**For each result:**

1. Fetch the file (or relevant fragment) via the GitHub Contents API.
2. Run the secret catalog (§17).
3. If a secret hits → `SECRET_LEAK` finding with catalog severity, evidence = repo URL + file path + matched secret (truncated, last 4 chars only).
4. Optional: clone the repo to a tempdir, run `trufflehog`/`gitleaks` for full history scan.

---

## 20. Endpoint Interest Score — 0–100 rubric

For every classified endpoint (§22 in methodology skill), apply this rubric:

| Signal | Points | Conditions |
|---|---|---|
| **Unauth write** | +40 | POST/PUT/DELETE/PATCH endpoint returns 200/201/202/204 anonymously. |
| **Open GraphQL introspection** | +35 | `__schema` query returns full type list anonymously. |
| **Verb tampering bypass** | +30 | OPTIONS reveals method not documented; that method is accessible. |
| **Reflected CORS + credentials** | +25 | `Access-Control-Allow-Origin` reflects request `Origin` AND `Access-Control-Allow-Credentials: true`. |
| **Sensitive keyword in path** | +20 | Path matches one of: `admin`, `internal`, `debug`, `user`, `password`, `token`, `key`, `export`, `upload`, `backup`, `config`, `secret`, `private`, `delete`, `purge`, `wipe`. |
| **Schema leak in error** | +20 | Response body contains stack trace, ORM error class, framework signature (e.g., `ActiveRecord::RecordNotFound`, `org.hibernate.exception.*`, `django.db.utils.IntegrityError`). |
| **API key in URL** | +15 | Path or query string contains `api_key=`, `apikey=`, `token=`, `access_token=`. |
| **Wildcard CORS** | +10 | `Access-Control-Allow-Origin: *`. |
| **Missing rate-limit headers** | +10 | No `RateLimit-*` / `X-RateLimit-*` headers; no `Retry-After` after rapid requests. |

**Thresholds:**

| Score | Severity |
|---|---|
| ≥ 90 | **CRITICAL** |
| 70–89 | **HIGH** |
| 50–69 | MEDIUM |
| 25–49 | LOW |
| < 25 | INFO |

For score ≥ 70, attach an `attack_path_hint` in evidence (see §29).

---

## 21. Mobile App Ownership Confidence — 0–100 rubric

> **Content moved to [`references/reasoning.md`](references/reasoning.md).** Section numbering preserved — reference `§21` points here.

Sub-sections:
- `21.1 APK Static Analysis Pipeline`

## 22. Identity Fabric — Concrete Endpoints

> **Content moved to [`references/arsenal.md`](references/arsenal.md).** Section numbering preserved — reference `§22` points here.

Sub-sections:
- `22.1 Microsoft Entra (Azure AD)`
- `22.2 Okta`
- `22.3 ADFS`
- `22.4 Google Workspace`
- `22.5 Generic OIDC (Keycloak / Auth0 / Ping / OneLogin / Duo)`
- `22.6 SAML metadata`
- `22.7 AWS account-ID extraction`
- `22.8 Microsoft 365 Deep Enumeration (Teams / SharePoint / OneDrive / OAuth)`
- `22.9 GraphQL Field-Suggestion Enumeration (when introspection disabled)`

## 23. Read-Only Secret Validators

> **Content moved to [`references/arsenal.md`](references/arsenal.md).** Section numbering preserved — reference `§23` points here.

Sub-sections:
- `23.1 Postman API Key (PMAK-*)`
- `23.2 AWS Access Key`
- `23.3 GitHub PAT`
- `23.4 Slack Token`
- `23.5 Anthropic API Key`
- `23.6 OpenAI API Key`
- `23.7 npm Token`
- `23.8 Atlassian API Token`
- `23.9 DataDog API + APP Key`
- `23.10 Validator output schema`
- `23.11 Hard rules`
- `23.12 Post-Discovery Enumeration Workflows`

## 24. Postman Public Workspace Universal Search

Postman's public-search endpoint is unauthenticated and indexes every workspace marked public.

**Verified endpoint shape (mid-2025 onward):**

```bash
curl -sk -m 15 \
 "https://www.postman.com/_api/ws/proxy" \
 -H 'Content-Type: application/json' \
 -H 'X-Entity-Team-Id: 0' \
 -d '{
 "service":"search",
 "method":"POST",
 "path":"/search-all",
 "body":{
 "queryIndices":["collaboration.workspace","runtime.collection","runtime.request"],
 "queryText":"acme.com",
 "size":100,
 "from":0,
 "clientTraceId":"",
 "queryAllIndices":false,
 "domain":"public"
 }
 }' | jq '.data'
```

This proxies through Postman's web app to their internal search service. Pagination via `from` (0, 100, 200, ...).

**If the proxy shape changes** (it has historically): inspect a real search request from the Postman web UI:

1. Open `https://www.postman.com/explore` in a browser.
2. Open DevTools → Network tab.
3. Search for any term.
4. Find the request to `_api/...` — copy as cURL — adapt.

**Per-workspace walk:**

For each matching workspace ID:

```bash
WS_ID="<workspace-id>"
# Workspace metadata (name, description, team, visibility)
curl -sk -m 10 "https://www.postman.com/_api/workspace/$WS_ID" | jq .

# List collections + environments + monitors in workspace
curl -sk -m 10 "https://www.postman.com/_api/workspace/$WS_ID/collection" | jq '..id'
curl -sk -m 10 "https://www.postman.com/_api/workspace/$WS_ID/environment" | jq '..id'

# Per-collection: full content (requests, headers, scripts, env vars)
COL_ID="<collection-id>"
curl -sk -m 10 "https://www.postman.com/_api/collection/$COL_ID" | jq '.collection.item'
```

**Ownership scoring signals:**

- Creator/team name mentions target domain or brand → strong.
- Workspace name/description mentions target → strong.
- Request URLs contain `*.target.com` → strongest signal (workspace is actively used against target's APIs).

**Run secret catalog (§17) over every text blob extracted** from the requests, env vars, pre-request scripts, and test scripts.

---

## 25. Stack Exchange OSINT Sweep

Stack Exchange and its sister sites collect code paste-ins from developers — many include secrets, internal hostnames, and proprietary code excerpts.

**Sites to query (8 with highest signal):**

```
stackoverflow.com
serverfault.com
dba.stackexchange.com
devops.stackexchange.com
security.stackexchange.com
superuser.com
sharepoint.stackexchange.com
salesforce.stackexchange.com
```

**API:**

```
GET https://api.stackexchange.com/2.3/search/advanced
 ?site=<site>
 &q=<target>
 &filter=withbody
 &pagesize=100
```

**Code block extraction regex:**

```regex
<pre><code>([\s\S]*?)</code></pre>
```

(Stack Exchange wraps code in `<pre><code>` HTML.)

**Pipeline:**

1. Search each site for the target name, brand, root domain.
2. Extract code blocks from `body` HTML.
3. Run secret catalog (§17) over each block.
4. Cross-reference post author email (where exposed in profile) against email_osint discoveries — confirms employee posting target's internal code.
5. Extract hostnames from code blocks → upsert as `subdomain` assets.

**Quota:** Stack Exchange API permits 30 requests/day without a key; with a free key, 10,000/day. Throttle with 2-second min interval per call.

---

## 26. Public SaaS Collaboration Surfaces

Many SaaS collaboration tools allow public sharing. Dork them like search engines.

**Platforms with high incident rate:**

```
trello.com
notion.so / notion.site
*.atlassian.net (Jira / Confluence)
miro.com
asana.com
clickup.com
airtable.com
```

**Dork template:**

```
site:{platform} "{target-keyword}"
```

**Run via search-engine adapter** (DDG default; Bing / Brave / Yandex / SerpAPI optional). The same classification logic from §18.7 applies.

**Common findings:**

- Public Trello board with credentials in card titles or attached config files.
- Public Notion page with internal SOPs, API keys in code blocks, customer data.
- Public Confluence space with onboarding docs containing seed creds.
- Public Miro board with architecture diagrams revealing internal hostnames.

---

## 27. Subdomain-Source Stack (Passive)

Practical "what actually returns useful data in 2026" reference, ordered by recall:

| Source | Tier | Notes |
|---|---|---|
| crt.sh | Free | Best single source for cert-derived subdomains; **frequently 502s during peak hours — see fallback chain below**. |
| VirusTotal | Freemium | Domain → passive DNS history. |
| AlienVault OTX | Free | Passive DNS + URL data. |
| Shodan | Paid (low tier) | Subdomain enum via `domain:` filter. |
| BinaryEdge | Paid | Comparable to Shodan. |
| FOFA | Freemium | Strong China-side coverage. |
| ZoomEye | Freemium | Comparable to Shodan; CN-strong. |
| Netlas | Paid | Large-scale HTTP/DNS/cert pivots. |
| SecurityTrails | Paid | Passive DNS + asset discovery. |
| RapidDNS | Free | Public passive DNS. |
| Subfinder bundled | Free | Aggregates 30+ free sources via one CLI. |
| Amass | Free | Comparable, more thorough, slower. |
| Recon-ng | Free | Modular framework; many free providers built in. |

**DNS AXFR opportunism:** for every name server discovered, attempt zone transfer:

```
dig @<ns-host> <target-domain> AXFR
```

Most NSs reject; those that don't = full zone disclosure (CRITICAL).

**Brute-force tier:** Subfinder/Subbrute against `assetnote.io` wordlists (best-curated public wordlist source).

### 27.0.1 crt.sh down? Fallback chain (try in order)

crt.sh runs on a single nginx in front of a busy Postgres; 502 / 503 / timeout in peak hours is routine. Don't retry-loop — pivot:

```bash
D="target.example"

# 1. Censys cert search (free 250 queries/month with key) — same data, different infra
censys search "names: ${D}" --index-type certificates --fields names | jq -r '.names' | sort -u

# 2. Cert Spotter API (sslmate) — free w/ rate limits
curl -sk "https://api.certspotter.com/v1/issuances?domain=${D}&include_subdomains=true&expand=dns_names" | \
 jq -r '..dns_names' | sort -u

# 3. CertStream archive (Calidog) — historical CT log mirror
curl -sk "https://crt.calidog.io/?q=${D}" | jq -r '..name_value' | sort -u

# 4. Subfinder bundled aggregator (uses 30+ sources internally — Chaos, Anubis, BinaryEdge, BufferOver, Censys, CertSpotter, Crobat, Crtsh, DNSDumpster, FOFA, Fullhunt, GitHub, HackerTarget, IntelX, PassiveTotal, Quake, Rapiddns, Shodan, Spyse, ThreatBook, ThreatMiner, URLScan, VirusTotal, WhoisXML, ZoomEye, etc.)
subfinder -d ${D} -all -recursive -silent

# 5. AlienVault OTX — free, no key
curl -sk "https://otx.alienvault.com/api/v1/indicators/domain/${D}/passive_dns" | \
 jq -r '.passive_dns.hostname' | sort -u

# 6. ThreatMiner — free
curl -sk "https://api.threatminer.org/v2/domain.php?q=${D}&rt=5" | jq -r '.results'

# 7. URLScan — passive DNS via past scans
curl -sk "https://urlscan.io/api/v1/search/?q=domain:${D}" | \
 jq -r '.results.page.domain' | sort -u

# 8. Anubis-DB / DNSDumpster (HTML scrape, last resort)
curl -sk -A "Mozilla/5.0" "https://anubisdb.com/anubis/subdomains/${D}" | jq -r '.'
```

PowerShell crt.sh wrapper with retry + fallback to Subfinder:

```powershell
function Get-Subs {
 param($D)
 for ($i=0; $i -lt 3; $i++) {
 try {
 $r = Invoke-WebRequest -Uri "https://crt.sh/?q=%25.$D&output=json" -UseBasicParsing -TimeoutSec 90 -UserAgent "Mozilla/5.0"
 return ($r.Content | ConvertFrom-Json | %{ $_.name_value -split "`n" } | %{ $_.Trim.ToLower } | ?{ $_ -and $_ -notlike "*@*" -and $_ -notmatch "^\*\." } | Sort -Unique)
 } catch {
 "crt.sh attempt $($i+1) failed; sleep 5s..." | Out-Host
 Start-Sleep -Seconds 5
 }
 }
 "crt.sh down — pivot to Subfinder: subfinder -d $D -all -silent" | Out-Host
 return @
}
```

### 27.1 Wordlist Sources for Subdomain + Content Brute-Force

| Source | URL | Notes |
|---|---|---|
| **Assetnote Wordlists** | `https://wordlists.assetnote.io/` | Best-curated; updated regularly. Subdomain top-N (1k, 10k, 100k, 1M, 10M); content-paths per CMS/framework; per-vendor (AWS, Azure, GitLab, etc.). |
| **SecLists** | `https://github.com/danielmiessler/SecLists` | Massive collection. Subdomains: `Discovery/DNS/subdomains-top1million-110000.txt`. Content: `Discovery/Web-Content/`. |
| **jhaddix all.txt** | `https://gist.github.com/jhaddix/86a06c5dc309d08580a018c66354a056` | Long-running curated list. |
| **OneListForAll** | `https://github.com/six2dez/OneListForAll` | Aggregated; very large (millions). |
| **dirsearch wordlists** | `https://github.com/maurosoria/dirsearch` | Bundled with the tool. |
| **raft-large-words.txt** | inside SecLists `Discovery/Web-Content/raft-large-words.txt` | Time-tested content wordlist. |
| **bo0om wordlist** | `https://github.com/bo0om/wordlists` | Russian-language-aware. |
| **commonspeak2** | `https://github.com/assetnote/commonspeak2-wordlists` | Generated from BigQuery commit data. |
| **fuzzdb** | `https://github.com/fuzzdb-project/fuzzdb` | Fuzzing payloads + wordlists. |
| **payloads** | ` | Per-vuln-class payloads (less for enum, more for follow-on). |
| **Custom per-target** | n/a | Best practice: derive a custom wordlist from the target's own content (extract every word from their public website + LinkedIn + careers page → unique → use as seed). |

**Size guidance:**

- **<10k entries** → fast subdomain check (1–2 min); use for opportunistic/passive-supplement.
- **10k–100k entries** → standard depth (10–30 min); use as default brute-force.
- **100k–1M entries** → thorough; use when the target is a known high-value engagement (1–4 hours).
- **>1M entries** → exhaustive; reserve for week-long engagements; expect rate-limiting.

**Tooling:**

```bash
# Subfinder + brute-force with assetnote 100k
subfinder -d target.example -all -recursive | tee passive.txt
puredns bruteforce assetnote-best-dns-wordlist.txt target.example -r resolvers.txt | tee brute.txt
cat passive.txt brute.txt | sort -u > all-subs.txt

# Content brute-force on alive hosts
ffuf -u "https://target.example/FUZZ" -w raft-large-words.txt -mc 200,301,403 -t 50 -ac
```

---

## 28. Infrastructure & Attack-Surface OSINT

> **Content moved to [`references/reasoning.md`](references/reasoning.md).** Section numbering preserved — reference `§28` points here.

Sub-sections:
- `28.1 ASN/BGP & Internet Measurement`
- `28.2 Certificates & CT Monitoring`
- `28.3 Web tech / TLS / fingerprinting`
- `28.4 TLS Deep Audit`
- `28.5 Reverse DNS Sweep & IPv6 Enumeration`

## 29. Threat Intel & IOCs

> **Content moved to [`references/reasoning.md`](references/reasoning.md).** Section numbering preserved — reference `§29` points here.

Sub-sections:
- `29.1 Malware Analysis & Sandboxes`
- `29.2 Vulnerability Prioritization Data Sources`
- `29.3 HackerOne Disclosed Reports Reference`

## 30. Cryptocurrency OSINT

### 30.1 Blockchain Explorers

| Chain | Explorer |
|-------|---------|
| Bitcoin | [Blockchain.com](https://www.blockchain.com/explorer), [Blockchair](https://blockchair.com/) |
| Ethereum | [Etherscan](https://etherscan.io/) |
| BNB Chain | [BSCScan](https://bscscan.com/) |
| Polygon PoS | [PolygonScan](https://polygonscan.com/) |
| Solana | [Solscan](https://solscan.io/) |
| Multi-chain | [OKLink](https://www.oklink.com/) (freemium), [Cielo](https://cielo.io/) |

### 30.2 L2 / Rollup Explorers

| L2 | Explorer | Notes |
|---|---|---|
| Arbitrum | [Arbiscan](https://arbiscan.io/) | Optimistic rollup; 7-day challenge window. |
| Optimism | [Optimistic Etherscan](https://optimistic.etherscan.io/) | Optimistic rollup; 7-day challenge window. |
| Base | [BaseScan](https://basescan.org/) | OP Stack. |
| Blast | [Blastscan](https://blastscan.io/) | OP Stack derivative. |
| Scroll | [Scrollscan](https://scrollscan.com/) | zkEVM. |
| zkSync Era | [zkSync Era Block Explorer](https://explorer.zksync.io/) | zkRollup; faster finality. |
| Polygon zkEVM | [PolygonScan zkEVM](https://zkevm.polygonscan.com/) | zkEVM. |
| StarkNet | [Voyager](https://voyager.online/), [StarkScan](https://starkscan.co/) | Cairo VM; different address derivation. |
| Cross-L2 | [L2Beat](https://l2beat.com/) | Risk framework + TVL comparison. |

### 30.3 Transaction Tracking & Analytics

- [Arkham](https://www.arkhamintelligence.com/) — multichain, entity labels, graphs, alerts.
- [TRM](https://www.trmlabs.com/) — address/tx graphs.
- [MetaSleuth](https://metasleuth.io/) — visual flow.
- [Breadcrumbs](https://www.breadcrumbs.app/) (freemium) — visual graphing + labels.
- [Bubblemaps](https://bubblemaps.io/) — holder concentration.
- [Whale Alert](https://whale-alert.io/) — large transaction monitoring.
- [Chainalysis](https://www.chainalysis.com/) / [Crystal Blockchain](https://crystalblockchain.com/) — pro analytics.
- [GraphSense](https://graphsense.info/) — open-source crypto analytics.
- [Nansen](https://www.nansen.ai/) — Smart Money labels (paid).
- [Dune](https://dune.com/) — custom queries.
- [Token Sniffer](https://tokensniffer.com/) — honeypot/scam detection.

### 30.4 NFT / Exchange / Bridges

- [OpenSea](https://opensea.io/), [NFTScan](https://www.nftscan.com/), [DappRadar](https://dappradar.com/), [CoinGecko](https://www.coingecko.com/), [CoinMarketCap](https://coinmarketcap.com/), [Glassnode](https://glassnode.com/).
- Bridges: [Socketscan](https://socketscan.io/), [L2Beat Bridges](https://l2beat.com/bridges), [Pulsy](https://pulsy.io/).

---

## 31. Media Intelligence

### 31.1 Reverse Image & Facial Search

- [Google Images](https://images.google.com/), [TinEye](https://tineye.com/), [Yandex Images](https://yandex.com/images/) (Russian/East European strong), [PimEyes](https://pimeyes.com/en), [FaceCheck](https://facecheck.id/).

### 31.2 Image Forensics

- [Forensically](https://29a.ch/photo-forensics/), [ExifTool](https://exiftool.org/), [Jimpl](https://jimpl.com/), [Jeffrey's EXIF Viewer](http://exif.regex.info/exif.cgi), [FOCA](https://www.elevenpaths.com/labstools/foca), [Metagoofil](https://www.edge-security.com/metagoofil.php), [C2PA Verify](https://verify.contentauthenticity.org/).

### 31.3 Video Analysis

- [YouTube Data Viewer](https://citizenevidence.amnestyusa.org/), [InVID & WeVerify](https://www.invid-project.eu/tools-and-services/invid-verification-plugin/), [YouTube Geo Tag](https://mattw.io/youtube-geofind/location), [MediaInfo](https://mediaarea.net/en/MediaInfo), Snap Map.

### 31.4 Browser Extensions for Media

- [Fake News Debunker (InVID & WeVerify)](https://chrome.google.com/webstore/detail/fake-news-debunker-by-inv/mhccpoafgdgbhnjfhkcmgknndkeenfhe).
- [RevEye Reverse Image Search](https://chrome.google.com/webstore/detail/reveye-reverse-image-sear/kejaocbebojdmebagkjghljkeefgimdj).
- [EXIF Viewer Pro](https://chrome.google.com/webstore/detail/exif-viewer-pro/mmbhfeiddhndihdjeganjggkmjapkffm).
- [Wayback Machine Extension](https://chrome.google.com/webstore/detail/wayback-machine/fpnmgdkabkmnadcjpehmlllkndpkmiak).
- [Search by Image](https://chromewebstore.google.com/detail/search-by-image/cnojnbdhbhnkbcieeekonklommdnndci).

---

## 32. Geospatial Intelligence

### 32.1 Satellite & Mapping

- [Google Maps](https://www.google.com/maps), [Bing Maps](https://www.bing.com/maps/).
- [Sentinel Hub EO Browser](https://apps.sentinel-hub.com/eo-browser/), [NASA Worldview](https://worldview.earthdata.nasa.gov/), [Zoom Earth](https://zoom.earth/).
- [Wayback Imagery](https://livingatlas.arcgis.com/wayback/) — historical satellite.
- [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/map/), [Open Infrastructure Map](https://openinframap.org/), [Windy](https://www.windy.com/).

### 32.2 Geolocation Tools

- [Mapillary](https://www.mapillary.com/app), [KartaView](https://kartaview.org/), [Overpass Turbo](https://overpass-turbo.eu/), [SunCalc](https://www.suncalc.org/), [GeoNames](https://www.geonames.org/), [PeakVisor](https://peakvisor.com/), [GeoGuesser tips](https://somerandomstuff1.wordpress.com/2019/02/08/geoguessr-the-top-tips-tricks-and-techniques/).

**Street View:** Google Street View, [Apple Maps](https://maps.apple.com/), [Yandex Maps](https://yandex.com/maps/), [Baidu Maps](https://map.baidu.com/).

### 32.3 Flight OSINT

- [FlightRadar24](https://www.flightradar24.com/), [FlightAware](https://www.flightaware.com/), [RadarBox](https://www.radarbox.com/).
- [ADSBExchange](https://www.adsbexchange.com/) — unfiltered.
- [Planespotters](https://www.planespotters.net/) — fleet/airframe history.
- [AirFrames](https://www.airframes.org/), [JetPhotos](https://www.jetphotos.com/).

### 32.4 Maritime OSINT

- [MarineTraffic](https://www.marinetraffic.com/), [VesselFinder](https://www.vesselfinder.com/), [FleetMon](https://www.fleetmon.com/).
- [Global Fishing Watch](https://globalfishingwatch.org/map/) — vessel behavior + AIS gap analysis.

---

## 33. AI-Assisted OSINT

> **Warning:** Never paste PII, sensitive IOCs, or unique pivots into cloud LLMs. They log inputs and may use them for training. Use local models for sensitive analysis.

| Tool | Strength |
|------|---------|
| [ChatGPT](https://chat.openai.com/) (paid) | Log parsing, dataset analysis, Code Interpreter for CSV/JSON, Vision OCR. |
| [Claude](https://claude.ai/) (paid) | 200K-token context for large doc dumps + report synthesis. |
| [Gemini](https://gemini.google.com/) | Long-context; Deep Research mode with citations. |
| [Perplexity Pro](https://www.perplexity.ai/) (paid) | Real-time web search + reasoning. |

**Local / privacy-preserving:** [Ollama](https://ollama.com/), [LM Studio](https://lmstudio.ai/), [GPT4All](https://gpt4all.io/).

### 33.1 Commercial AI OSINT Platforms

- [Cylect](https://www.cylect.io/) — entity extraction + link analysis.
- [Fivecast Matrix](https://www.fivecast.com/products/matrix/) — generative-AI triage for social-media datasets.
- [Recorded Future](https://www.recordedfuture.com/) — AI-driven threat intel.
- [DarkOwl Vision](https://www.darkowl.com/) — darknet data analysis.

### 33.2 Deepfake & Synthetic Media Detection

- [Sensity AI](https://sensity.ai/), [Reality Defender](https://realitydefender.com/), [Adobe Content Credentials Verify](https://contentcredentials.org/verify), [CarNet](https://carnet.ai/).

---

## 34. Archiving & Evidence Preservation

- [archive.today](https://archive.today/) — one-page archiver + screenshot.
- [URLScan.io](https://urlscan.io/) — webpage scan + resource map.
- [ArchiveBox](https://archivebox.io/) — self-hosted (HTML, PDF, screenshots, media).
- [Hunchly](https://www.hunch.ly/) — investigator evidence capture (paid).
- Wayback SavePageNow API v3 — on-demand archiving with job IDs.
- [SingleFileZ](https://github.com/gildas-lormeau/SingleFileZ) — browser ext for offline HTML.
- [Kasm Workspaces](https://kasmweb.com/) — containerized OSINT browser isolation.

**Evidence handling:** URL + UTC timestamp + PNG + WARC/SingleFileZ archive, SHA-256 hash all downloads, separate work profiles per case, store evidence read-only, JSONL run logs with `run_id` + tool versions.

---

## 35. Automation & Workflows

- [n8n](https://n8n.io/) — self-hosted workflow automation (RSS → scrape → alert pipelines).
- [Huginn](https://github.com/huginn/huginn) — agent-based monitoring/scraping/alerting.
- [Playwright](https://playwright.dev/) — headless browser automation with stealth plugins.
- [Browsertrix Crawler](https://github.com/webrecorder/browsertrix-crawler) — archival crawling with WARC export.
- [Prefect](https://www.prefect.io/) / [Apache Airflow](https://airflow.apache.org/) — workflow orchestration.

---

## 36. Cross-Module Sidecar Coordination

When you run a multi-module recon, late-arriving outputs need to feed into already-running modules. The pattern:

1. Each module writes a sidecar JSON to a known location when it finishes:
 - `<scan>/mobile_endpoints.json` — endpoints + hostnames extracted from APK static analysis.
 - `<scan>/secrets_sidecar.json` — hostnames + endpoints + Firebase project IDs from secrets-beyond-github sweep.
 - `<scan>/sso_tenants.json` — discovered IdP tenants for breach correlation.
2. Downstream modules check for sidecars on start; if present, ingest.
3. Cross-feed: API discovery consumes both `mobile_endpoints.json` and `secrets_sidecar.json`; SSO×breach correlation consumes `sso_tenants.json` and the breach DB.

**Sidecar shape (mobile_endpoints.json example):**

```json
{
 "endpoints": [
 {"method": "GET", "url": "https://api.acme.com/v1/users", "source": "apk:com.acme.android"},
 {"method": "POST", "url": "https://api.acme.com/v1/login", "source": "apk:com.acme.android"}
 ],
 "hostnames": ["api.acme.com", "cdn.acme.com"],
 "firebase_project_ids": ["acme-prod-12345"]
}
```

When you implement an ad-hoc multi-tool recon (no platform), use a `tmpdir + JSON sidecars + a one-line manifest` pattern. Composable, debuggable, replay-able.

---

## 37. Regional Search Engines

- **Russia / CIS:** [Yandex](https://yandex.com/), [Mail.ru Search](https://go.mail.ru/).
- **China:** [Baidu](https://www.baidu.com/), [Sogou](https://www.sogou.com/), [360 Search](https://www.so.com/).
- **Russia social:** [VK](https://vk.com/), [OK.ru](https://ok.ru/).
- **China social:** [Weibo](https://weibo.com/), [Bilibili](https://www.bilibili.com/), [Zhihu](https://www.zhihu.com/), [Douyin](https://www.douyin.com/).

---

## 38. Telegram & Messaging Intelligence

- [TGStat](https://tgstat.com/) — channel analytics + search.
- [Telemetr](https://telemetr.io/) — channel growth, overlaps, forwards.
- [Combot](https://combot.org/) — group analytics (partial paid).
- [TelegramDB Search Bot](https://t.me/TGdb_bot) — basic Telegram OSINT.
- [Discord ID](https://discord.id/) — basic Discord account info.
- [Sogou Weixin search](https://weixin.sogou.com/) — WeChat Official Accounts.
- View public Telegram channels: `https://t.me/s/<channel>`.

---

## 39. Attack-Path Hint Patterns

When emitting a HIGH/CRITICAL API endpoint finding (score ≥ 70), include a one-sentence `attack_path_hint` in evidence so the operator knows where to start exploiting. Templates:

| Trigger | Attack-path hint |
|---|---|
| Unauth POST / PUT / DELETE | *"Unauthenticated {method} {path} — try IDOR + privilege escalation; check whether numeric IDs are sequential or guessable."* |
| Open GraphQL introspection | *"Open GraphQL introspection on {path} — enumerate mutations, look for `createUser`, `setRole`, `transferFunds`-shaped names; pivot to broken-auth or business-logic flaws."* |
| Reflected CORS + creds | *"Reflected CORS with credentials on {path} — host CSRF page on attacker-controlled origin; victim's browser will leak {sensitive-data-hint}."* |
| Wildcard CORS + sensitive | *"Wildcard CORS on {path} returning user-tied data without creds — exfiltrate via cross-origin fetch from any page victim visits."* |
| Verb tampering | *"Verb tampering: {hidden-method} allowed on documented-{visible-method}-only endpoint → likely missing-method-check authz bug; try {hidden-method} {path} with valid auth."* |
| API key in URL | *"API key in URL: `?{param}=...` — token leaks to access logs, browser history, Referer headers, third-party CDNs. Check Wayback / Google for cached copies."* |
| Schema leak in error | *"Schema leak in error response — framework signature `{framework}` exposed; map to known {framework} vulns and craft targeted payloads."* |
| Sensitive keyword | *"Path contains '{keyword}' — review for direct object reference, mass-assignment, or hidden admin functionality."* |
| Open RTDB Firebase | *"Open Firebase RTDB at https://{project}.firebaseio.com/.json — read everything, then test write at `/<random-key>.json` with PUT to gauge ACL scope."* |
| Listable cloud bucket | *"Listable {provider} bucket `{bucket}` — recursive object listing + content-type analysis; look for backups, logs, customer data, AWS keys in JSON configs."* |
| .git exposed | *"Exposed .git/config on {host} — reconstruct repository with git-dumper or githacker; full source history."* |
| .env exposed | *"Exposed .env on {host} — grep for `_KEY`, `_SECRET`, `_TOKEN`, `_PASSWORD`; validate all credentials read-only via §23 validators."* |
| /actuator/env | *"Spring Boot /actuator/env exposed — dump environment variables; look for `spring.datasource.password`, JWT secrets, cloud creds."* |
| /actuator/heapdump | *"Spring Boot /actuator/heapdump exposed — download HPROF, run `jhat` or VisualVM, search for cleartext secrets in heap strings."* |
| Open Elasticsearch | *"Open Elasticsearch on {host}:9200 — `/_cat/indices?v` for index list; sample documents from each high-value index; test write to `/test-idx/_doc` to gauge ACL."* |
| Open Redis | *"Open Redis on {host}:6379 — `INFO`, `KEYS *`, sample reads; check for write access via `CONFIG SET` then `BGSAVE` to write `authorized_keys`."* |
| Open MongoDB | *"Open MongoDB on {host}:27017 — `show dbs`, `show collections`, sample find queries; check user collection for password hashes."* |
| Subdomain takeover | *"CNAME for {host} points to unclaimed {provider} resource → register `{takeover-target}` on {provider} to serve content from {host}; pivot to phishing or content injection on the trusted domain."* |
| Open kubelet | *"Open kubelet on {host}:10250 — `GET /pods` to list; `POST /run/<ns>/<pod>/<container>` for in-container exec without K8s API auth."* |
| Open etcd | *"Open etcd on {host}:2379 — `etcdctl get / --prefix --keys-only` for full cluster state; secrets stored under `/registry/secrets/`."* |
| K8s API anonymous | *"Kubernetes API on {host}:6443 with anonymous-auth — `kubectl --server=https://{host}:6443 --insecure-skip-tls-verify get pods --all-namespaces`."* |
| Citrix unpatched | *"Citrix NetScaler version {ver} on {host} — vulnerable to CVE-{cve} (KEV-listed); see vendor advisory; do not exploit but flag for client immediate patching."* |
| F5 BIG-IP TMUI exposed | *"F5 BIG-IP TMUI on {host} reachable; CVE-2022-1388 / CVE-2023-46747 KEV applicable; advise immediate patching to vendor-released hotfix."* |
| VMware vCenter accessible | *"vCenter at {host} accessible without VPN; CVE-2021-21972 RCE if unpatched; check version banner."* |
| Cloud function URL unauth | *"AWS Lambda Function URL at {url} accessible anonymously — review IAM auth configuration; if unauthenticated by design, audit input validation aggressively."* |
| npm typosquat candidate | *"Package name `{candidate}` is unregistered + similar to target's published `{official}` — typosquat takeover risk; advise client to defensively register."* |
| DMARC missing/permissive | *"DMARC `p=none` on {domain} — spoof of `{anything}@{domain}` deliverable to recipients; recommend enforcement to `p=quarantine` or `p=reject` after observing reports."* |
| Live AI API key (Anthropic/OpenAI) | *"Validated `sk-{provider}-...` key with model access — quota cost can be exfiltrated; rotate immediately + audit usage logs in provider console."* |
| Public Slack invite link | *"Slack workspace invite link discoverable via search engine — anyone can join the workspace without approval; trivially access internal channels."* |
| Open Docker registry | *"Public Docker registry at {host} — `GET /v2/_catalog` lists images; pull and scan layers for embedded secrets."* |
| Telegram bot token live | *"Telegram bot token validated — `getUpdates` reveals bot recipients (admin chats); if `getMe` shows bot is in channels, full message read access."* |
| Sourcemap with `sourcesContent` | *"Sourcemap on {host} includes embedded original sources — full frontend code reconstructable; grep for inline secrets and internal hostnames."* |

---

## 40. Severity Decision Matrix — Worked Examples

> **Content moved to [`references/reasoning.md`](references/reasoning.md).** Section numbering preserved — reference `§40` points here.

## 41. LinkedIn Employee Enumeration

LinkedIn is the highest-signal source for employee enumeration during external red-team work. Use it for: target list generation, role prioritization, email-pattern derivation, pretext development.

### 41.1 Search techniques

**Free LinkedIn (no Sales Navigator):**

- People-search by company: `https://www.linkedin.com/search/results/people/?currentCompany=["<company-id>"]`. Get company-id from the company's LinkedIn URL or profile JSON.
- Bypass connection-degree filter: search shows 1st/2nd-degree only by default; use Google dorking instead.

**Google dork for LinkedIn employee enum:**

```
site:linkedin.com/in "<company name>"
site:linkedin.com/in "<company name>" "engineer" # role filter
site:linkedin.com/in "<company name>" "<location>" # location filter
site:linkedin.com/in "<company name>" -inurl:/posts
```

**Bing/DuckDuckGo equivalents** — sometimes return different result sets; cross-engine union.

**LinkedIn Sales Navigator (paid):**

- Most efficient if available. Lead lists by company × role × seniority. Export CSV.

**Tools:**

- **theHarvester** with `-b linkedin` source (uses search-engine-driven enum).
- **CrossLinked** — `https://github.com/m8r0wn/CrossLinked` — CLI tool that does the LinkedIn dorking.
- **LinkedInDumper** / **Linkook** — open-source enum tools (verify currency; they break frequently).
- **PhantomBuster** / **Apollo.io** / **RocketReach** / **Hunter.io Email Finder** — paid SaaS that does the enum + email derivation in one workflow.

### 41.2 Role inference for prioritization

For each enumerated employee, capture:

- **Name** (canonical form: First Last; remove suffixes like "PMP", "PhD" for email-pattern matching).
- **Job title** (raw + normalized to a role tier).
- **Tenure** (years at company; longer = more access typically).
- **Location** (city / region; informs phishing time-of-day).
- **Recent activity** (posts, comments, articles — informs pretext).

**Role priority for breach lookup + phishing target list:**

| Role tier | Examples | Why |
|---|---|---|
| **P0** | CEO, CFO, CTO, CISO, CIO, COO, GC, CRO | Exec accounts; BEC + finance + legal authority. |
| **P1** | VP / Director of IT / Security / Engineering / Finance / HR | Privileged tool access; reset workflows. |
| **P2** | DevOps, SRE, Platform, Security Engineer, DBA | GitHub / cloud / CI access; secrets in their accounts. |
| **P3** | Software Engineer, Architect, Senior Developer | Code + occasional cloud access. |
| **P4** | Sales, Marketing, HR, Finance Analyst, Customer Support | SaaS access (Salesforce, HubSpot, Workday); BEC enabler. |
| **P5** | Generic individual contributor, intern, contractor | Lowest single-account value but breadth matters. |

### 41.3 Email-pattern derivation from confirmed names

For each captured name, derive candidate emails using §11 templates. Cross-reference against:

- Hunter.io `domain-search` to confirm pattern.
- Breach corpus (HudsonRock + HIBP + DeHashed + IntelX) to find matches.

### 41.4 Sock-puppet considerations

- **Never connect from the corporate persona.** LinkedIn shows "viewed your profile" notifications.
- **Use a sock puppet** with a plausible profile (5+ years built history, similar industry, mutual connections to throw off correlation). Tools: persona-builder workflows.
- **LinkedIn "private mode" (anonymous viewing)** — toggle in settings; reduces one signal but Sales Navigator can still see anonymized "someone viewed your profile."
- **Connection requests are detectable.** Don't send any during recon.
- **Profile views accumulate suspicion** if you view 100+ employees of one company in a day. Throttle: <20/day per persona.

### 41.5 Output

Per discovered employee:

```
Person:
 name: "Alice Doe"
 title: "Senior DevOps Engineer"
 role_tier: P2
 company: "Acme Corp"
 location: "Boston, MA"
 linkedin_url: https://www.linkedin.com/in/alicedoe
 derived_emails:
 - alice.doe@acme.com (TENTATIVE)
 - adoe@acme.com (TENTATIVE)
 - alice@acme.com (TENTATIVE)
 breach_hits:
 - alice.doe@acme.com (HudsonRock; cleartext password redacted; FIRM)
 pretext_hooks:
 - "DevOps tooling vendor evaluation" (recent posts)
 - "Boston DevOps Days speaker" (conference activity)
```

---

## 42. Job Posting Tech-Stack Analysis

Job postings reveal the target's internal tech stack with surprising precision. Free, public, and they include the exact vendor names.

### 42.1 Sources

| Platform | URL | Notes |
|---|---|---|
| LinkedIn Jobs | `https://www.linkedin.com/jobs/search/?keywords=&f_C=<company-id>` | Most current; require LI account. |
| Indeed | `https://www.indeed.com/cmp/<company>` | Company page with job feed. |
| Glassdoor | `https://www.glassdoor.com/Jobs/<company>-Jobs-E<id>.htm` | Plus salary data + employee reviews. |
| Lever (ATS) | `https://jobs.lever.co/<company>` | Direct ATS — full job descriptions. |
| Greenhouse (ATS) | `https://boards.greenhouse.io/<company>` | Direct ATS. |
| Workable (ATS) | `https://apply.workable.com/<company>/` | Direct ATS. |
| AshbyHQ (ATS) | `https://jobs.ashbyhq.com/<company>` | Direct ATS. |
| AngelList / Wellfound | `https://wellfound.com/company/<company>/jobs` | Startup-focused. |
| BuiltIn | `https://builtin.com/companies/view/<company>` | Tech-focused. |
| Stack Overflow Jobs | (deprecated 2022 but archive available) | Historical tech-stack data. |
| Company careers page | `https://careers.<target>.com` or `https://<target>.com/careers` | Direct source; sometimes more detail than ATS. |

### 42.2 What to extract

For each job posting, harvest:

- **Required technologies** ("must have experience with X, Y, Z") → confirmed in-use.
- **Nice-to-have technologies** → likely in use but maybe in transition.
- **Vendor names** (Workday, Salesforce, Snowflake, Databricks, Datadog, etc.) → SaaS tenants.
- **Internal tool / project codenames** (often slip into "you'll work on Project Aurora") → recon vocabulary.
- **Team size hints** ("part of a 12-person platform team") → org-structure intel.
- **Office locations** ("hybrid 3 days in Boston office") → physical recon.
- **Cloud + on-prem ratio hints** ("migrating from on-prem to AWS") → posture intel.
- **Compliance frameworks mentioned** (SOC2, FedRAMP, HIPAA, PCI) → defensive priorities + reporting context.

### 42.3 Tooling

- **scrapy / BeautifulSoup** — custom scrapers per ATS.
- **theHarvester** with appropriate sources.
- **JobScraper** scripts on GitHub.
- **Manual** — for small targets, manual review of 20–30 postings is fast and high-fidelity.

### 42.4 Output

Per discovered tech mention:

```
Tech_inferred:
 product: "Snowflake"
 category: "data warehouse"
 source: "linkedin job posting #<id>"
 source_url: https://www.linkedin.com/jobs/view/...
 confidence: TENTATIVE (job listing implies in-use; not yet confirmed by direct probe)
 posting_date: 2026-03-15
 required_or_nice: "required"
```

Aggregate to a **target tech-stack profile** that informs:

- Which secret patterns to look for (Snowflake-specific keys, Databricks tokens).
- Which SaaS tenants to fingerprint (Snowflake account URL pattern).
- Which vendor-product fingerprints to probe (Snowflake DSN paths in JS).

---

## 43. Slack / Discord / Telegram Workspace Discovery

### 43.1 Slack

- **Public workspace search** (limited; Slack used to have one but deprecated):
 - **Slofile** (third-party): `https://slofile.com/` — community Slack workspace directory.
 - **Slacklist** / **Slack Communities** — community-curated lists.
- **Invite-link enumeration** — Slack invite URLs follow `https://join.slack.com/t/<workspace-slug>/shared_invite/<token>`. Common discovery:
 - Google: `site:join.slack.com "{target}"` or `inurl:slack.com inurl:shared_invite "{target}"`.
 - GitHub: `"join.slack.com/t/<target-stem>"` filename:README.
 - Twitter/X / Reddit: search for shared invite links.
- **Confirm workspace exists**: visit `https://<slug>.slack.com/api/auth.test` (returns workspace metadata when called by an authenticated session, but the page itself returns differently per workspace existence).
- **High-value finding**: any open invite link that bypasses the target's normal member-approval flow → operator can join workspace without authorization → MEDIUM/HIGH finding (depending on what's in the workspace).

### 43.2 Discord

- **Discord server discovery** is harder (no central public directory).
- **DiscordServers.com** — third-party directory.
- **Discord.me** / **Top.gg** — community directories.
- Google: `site:discord.gg "{target}"` or `site:discord.com "{target}"`.
- **Confirm server**: invite URLs `https://discord.gg/<token>` resolve to a JSON via `https://discord.com/api/v9/invites/<token>?with_counts=true`. Returns server name, ID, member count, channel info.
- **Bot enumeration**: if you find a bot token (catalog §17 row 47), use `getMe` to get bot identity + servers it's joined to (read-only check).

### 43.3 Telegram

Already covered in §38. Quick reference:

- TGStat — channel analytics + search.
- Telemetr — channel growth + overlaps.
- Combot — group analytics.
- View public channels: `https://t.me/s/<channel>`.
- Invite link enum: search Google `site:t.me "{target}"`.

### 43.4 Microsoft Teams (federation)

- See companion methodology skill §11.10.
- Federation status check via Microsoft Graph (auth-required).
- Open-federation default = anyone can chat target's users with `<email>@<target>` lookup.

### 43.5 Mattermost / Rocket.Chat / self-hosted

- `https://mattermost.<target>.com` or `chat.<target>` patterns.
- Open registration check: probe `/signup` page; if accessible without invite → anyone joins.
- Check version disclosure (`/api/v4/system/ping`) for known CVEs.

---

## 44. Package Registry Leak Hunting

Public package registries (npm, PyPI, RubyGems, Docker Hub, etc.) often contain inadvertent secrets in published packages.

### 44.1 npm

- **Search packages by org / scope:**

 ```bash
 npm search "<target-keyword>"
 npm view @<scope>/<package-name>
 ```

- **List org's packages:** `https://www.npmjs.com/org/<org>` or `https://registry.npmjs.org/-/org/<org>/package`.
- **Per-package historical versions:** `https://registry.npmjs.org/<package>` — JSON with all versions.
- **Tarball download for scan:**

 ```bash
 npm pack <package>@<version>
 tar -xzf package-version.tgz
 # Run secret catalog (§17) on extracted files
 ```

- **Common leaks:** `.env` files included in published tarball, `package.json` `scripts` references to internal CI secrets, hardcoded API keys in `dist/` builds.

### 44.2 PyPI

- **Search packages:** `https://pypi.org/search/?q=<target>`.
- **Per-package metadata + history:** `https://pypi.org/pypi/<package>/json`.
- **Download wheel/sdist for scan:**

 ```bash
 pip download <package>==<version> --no-deps -d /tmp/pkg
 unzip /tmp/pkg/*.whl -d /tmp/pkg/extracted
 # Run secret catalog
 ```

- **Common leaks:** `setup.py` with hardcoded URLs, embedded test fixtures with real credentials, accidentally-included `.pypirc` files.

### 44.3 RubyGems

- **Search:** `https://rubygems.org/search?query=<target>`.
- **Per-gem metadata:** `https://rubygems.org/api/v1/gems/<gem-name>.json`.
- **Download:**

 ```bash
 gem fetch <gem-name>
 gem unpack <gem-name>-<version>.gem
 ```

### 44.4 Cargo (Rust crates)

- **Search:** `https://crates.io/search?q=<target>`.
- **Per-crate metadata:** `https://crates.io/api/v1/crates/<crate-name>`.

### 44.5 Packagist (PHP / Composer)

- **Search:** `https://packagist.org/search/?q=<target>`.
- **Per-package metadata:** `https://packagist.org/packages/<vendor>/<package>.json`.

### 44.6 NuGet (.NET)

- **Search:** `https://www.nuget.org/packages?q=<target>`.

### 44.7 Maven Central (Java)

- **Search:** `https://search.maven.org/?q=<target>`.

### 44.8 Docker Hub / Quay / GHCR / ECR Public

Already covered in §16.18; worth noting for completeness as part of registry-sweep workflow.

### 44.9 Workflow

For each registry, for each candidate package owned-by-target:

1. List all historical versions (often `<package>@1.0.0` was clean but `<package>@0.9.0` had a leaked key).
2. Download each version's archive.
3. Extract; run secret catalog (§17) over all files.
4. Note `.env`, `package.json`/`setup.py`/`Cargo.toml` for hardcoded values.
5. For Docker images: scan each layer (use `dive` or `skopeo` + `docker save` + extract layers).

### 44.10 Typosquat surveillance

For every published package the target owns, generate typosquat candidates (similar names, common substitutions) and check whether they're already taken by attackers (supply-chain attack surface).

```bash
# Example: target package "acme-utils"
# Candidates: acme-util, acmeutils, acme_utils, acme.utils, ac-me-utils, etc.
for candidate in acme-util acmeutils acme_utils acme.utils ac-me-utils; do
 npm view $candidate 2>&1 | head -3
done
```

If a candidate is registered to a non-target party → MEDIUM finding (typosquat, possible supply-chain attack vector).

---

## 45. Sat Imagery for Physical Recon

For engagements that include a physical-touch component (badge access, tailgating, dumpster diving, on-site network), public imagery helps scout the target.

### 45.1 Sat imagery sources

| Source | URL | Notes |
|---|---|---|
| **Google Earth Pro** | desktop app | Historical timeline; high resolution (sub-meter) for major cities. |
| **Google Maps** | maps.google.com | Current; satellite layer; street view inside building lobbies sometimes. |
| **Bing Maps Bird's Eye** | bing.com/maps | Oblique/45-degree imagery for many regions; sometimes shows building facades better than top-down. |
| **Apple Maps Look Around** | (iOS / Mac) | Street-level; 3D in major cities. |
| **Yandex Maps Panorama** | yandex.com/maps | Russia + global; sometimes higher-resolution street-level than Google. |
| **NearMap** (paid) | nearmap.com | Highest-resolution commercial; updated frequently in served regions (US/AU/NZ/CA mostly). |
| **Maxar / Planet Labs** (paid) | maxar.com / planet.com | Tasking + recent imagery. |
| **Sentinel Hub EO Browser** | apps.sentinel-hub.com | Free Sentinel-2 (10m); good for change detection. |
| **NASA Worldview** | worldview.earthdata.nasa.gov | Free; multiple sensors. |
| **Wayback ArcGIS** | livingatlas.arcgis.com/wayback/ | Historical satellite. |
| **OpenStreetMap** | openstreetmap.org | Crowd-sourced map data with building outlines. |

### 45.2 What to extract for physical recon

- **Building entrance count + locations** — main entrance, employee entrances, loading docks, fire exits.
- **Parking lot ingress / egress** — single guarded entry vs open lot.
- **Fence lines + camera locations** — physical perimeter.
- **HVAC / utility access** — roof access, service entries.
- **Adjacent occupants** — neighboring tenants in same building / business park.
- **Vehicle types in lot** — proxy for executive presence + employee count.
- **Smoking area locations** — common social-engineering staging area.

### 45.3 OSINT-derived physical intel beyond satellites

- **LinkedIn employee photos** — badge templates often visible in profile photos taken at the office.
- **Glassdoor "office tour" photos** — employees post interior photos.
- **Indeed / Glassdoor reviews** — sometimes describe security culture ("loose badge enforcement", "tailgating common").
- **Instagram geotagged photos** — at the office address; reveals interior layout, badge designs, kitchen / common-area locations.
- **Public press releases** — often contain "ribbon cutting" photos of new offices showing layout + executive faces.
- **Conference talks by IT/security staff** — sometimes describe physical security setup.
- **Meetup / workshop event listings** — at the target's office; may include photos.

### 45.4 Vehicle / fleet intel

- **License plates** in LinkedIn/Instagram backgrounds — sometimes correlates to specific exec.
- **Company-branded vehicles** in sat imagery — fleet count + location.
- **Helicopter pad** / **executive parking** — clue to senior-leadership routine.

### 45.5 Discipline

- Document that imagery + photos are public-source.
- Don't trespass for "verification" — physical recon during OSINT phase = look only.
- Note imagery date — buildings change.

---

## 46. Tooling Quick-Install

One-liner installs for the most-used external recon tools. All assume Linux/Mac with go/python/git installed.

### 46.1 Subdomain enumeration

```bash
# Subfinder (passive, fast)
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Amass (thorough, slow)
go install github.com/owasp-amass/amass/v4/...@master

# Assetfinder
go install github.com/tomnomnom/assetfinder@latest

# DNSx (resolution + brute)
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# Puredns (brute-force with wildcard handling)
go install github.com/d3mondev/puredns/v2@latest
```

### 46.2 HTTP probing & enrichment

```bash
# httpx (tech-detect, status, JARM, favicon)
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

# Gowitness (screenshots)
go install github.com/sensepost/gowitness@latest

# Aquatone (screenshots + clustering)
go install github.com/michenriksen/aquatone@latest
```

### 46.3 Vulnerability scanning

```bash
# Nuclei (template scanner)
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -ut # update templates

# Naabu (port scan)
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

# Masscan (fast port scan; requires sudo)
git clone https://github.com/robertdavidgraham/masscan && cd masscan && make
```

### 46.4 Content discovery

```bash
# Ffuf (fuzzer / dirbuster)
go install github.com/ffuf/ffuf/v2@latest

# Gobuster
go install github.com/OJ/gobuster/v3@latest

# Feroxbuster (recursive content disco)
cargo install feroxbuster
```

### 46.5 JS / endpoint extraction

```bash
# Katana (crawler)
go install github.com/projectdiscovery/katana/cmd/katana@latest

# GoSpider
go install github.com/jaeles-project/gospider@latest

# LinkFinder (JS endpoint regex)
git clone https://github.com/GerbenJavado/LinkFinder && cd LinkFinder && pip install -r requirements.txt

# Subjs (extract JS URLs from HTML)
go install github.com/lc/subjs@latest
```

### 46.6 Wayback / archive

```bash
# gau (get all urls from Wayback + others)
go install github.com/lc/gau/v2/cmd/gau@latest

# Waybackurls
go install github.com/tomnomnom/waybackurls@latest
```

### 46.7 Cloud / AWS

```bash
# AWS CLI
pip install awscli
# or: brew install awscli

# Cloud_enum (S3/Azure/GCP enum)
git clone https://github.com/initstring/cloud_enum && cd cloud_enum && pip install -r requirements.txt

# S3Scanner
pip install s3scanner

# CloudSploit
git clone https://github.com/aquasecurity/cloudsploit && cd cloudsploit && npm install
```

### 46.8 Identity / SSO

```bash
# o365creeper / o365enum
git clone https://github.com/gremwell/o365enum

# CredMaster (per-protocol auth probe)
git clone https://github.com/knavesec/CredMaster
```

### 46.9 Mobile

```bash
# google-play-scraper (Python)
pip install google-play-scraper

# androguard (APK static analysis — pure Python, no apktool/jadx needed; §21.1)
pip install androguard
# or: brew install androguard

# apkleaks (secret scan in APK)
pip install apkleaks

# apktool (decompile APK to readable resources + manifest; §21.1)
# macOS/Linux:
brew install apktool
# Windows: download apktool.jar + apktool.bat wrapper from
# https://apktool.org/ , or `choco install apktool`

# aapt2 (manifest/badging dump — ships with Android SDK build-tools)
sdkmanager --install "build-tools;34.0.0"
# Windows path: %LOCALAPPDATA%\Android\Sdk\build-tools\<ver>\aapt2.exe

# jadx (Java source recovery from classes.dex)
brew install jadx
# Windows: unzip the jadx release zip, run jadx.bat / jadx-gui.exe
```

### 46.10 TLS / cert

```bash
# sslyze
pip install sslyze

# testssl.sh
git clone --depth 1 https://github.com/drwetter/testssl.sh.git

# JARM
pip install pyjarm

# Cert-spotter / certgraph
go install github.com/lanrat/certgraph@latest
```

### 46.11 Misc utilities

```bash
# Anew (line-dedup that streams)
go install github.com/tomnomnom/anew@latest

# Gf (regex-based grep templates)
go install github.com/tomnomnom/gf@latest

# Hakrawler (web crawler)
go install github.com/hakluke/hakrawler@latest

# Trufflehog (secret scanner)
go install github.com/trufflesecurity/trufflehog@latest

# Gitleaks
go install github.com/zricethezav/gitleaks/v8@latest

# jq (JSON parsing)
sudo apt install jq # or brew install jq
```

### 46.12 Frameworks / orchestration

```bash
# ProjectDiscovery's "PDTM" (manages the full PD toolkit)
go install -v github.com/projectdiscovery/pdtm/cmd/pdtm@latest
pdtm -install-all

# reconftw (scripted recon framework)
git clone https://github.com/six2dez/reconftw && cd reconftw && ./install.sh

# Axiom (distributed recon on cloud nodes)
git clone https://github.com/pry0cc/axiom && cd axiom && ./interact/axiom-configure
```

---

## 47. Sector-Specific Recon Notes

Most recon generalizes; some sectors have unique attack-surface elements worth flagging.

### 47.1 Healthcare

- **DICOM** (medical imaging) — port 11112, sometimes 4242 (testing).
- **HL7 v2** (clinical messaging) — port 2575 (TCP, often plaintext).
- **HL7 FHIR** (modern REST API) — typically `/fhir/R4/<resource>` paths; OAuth / SMART-on-FHIR auth posture varies wildly.
- **PACS / RIS / EHR systems** — Epic (`*.epic.com` SaaS), Cerner/Oracle Health, Allscripts/Veradigm, Athenahealth, NextGen, Meditech, eClinicalWorks. Each has known CVE history.
- **Searches:** `site:{domain} ("EHR" OR "PACS" OR "PHI" OR "HIPAA")`, `intitle:"Epic Systems" "{target}"`.
- **Severity escalation:** any PHI exposure → CRITICAL (regulatory + reputational); HL7/DICOM open without auth → CRITICAL.

### 47.2 Finance

- **SWIFT terminals** — typically internal-only; if external-facing, CRITICAL. Look for SWIFT Alliance Web Platform.
- **FIX protocol** (electronic trading) — port 9876 (common); cleartext.
- **Bloomberg terminals** — typically VDI; check for `bloomberg.com`-related auth surfaces.
- **Trading platform vendors** — Fidessa, Charles River, Eze Software, Aladdin (BlackRock).
- **Banking middleware** — Temenos T24, Finacle (Infosys), FIS, Jack Henry, Fiserv. Each has known CVE history.
- **Searches:** `site:{domain} ("PCI" OR "SOX" OR "GLBA" OR "MAS")`, `intitle:"Temenos" "{target}"`.
- **Severity escalation:** any account/balance data exposure → CRITICAL; SWIFT exposure → CRITICAL; trade-execution surface exposure → CRITICAL.

### 47.3 ICS / SCADA / OT

> **Caution:** ICS/SCADA assets often run on legacy systems where even passive scanning can cause disruption. **Do not actively probe ICS without explicit RoE coverage and operator coordination with the OT team.**

- **Modbus** — port 502 (TCP).
- **BACnet** — port 47808 (UDP).
- **Siemens S7** — port 102 (ISO-TSAP).
- **DNP3** — port 20000 (TCP).
- **EtherNet/IP** — port 44818 (TCP).
- **Niagara Framework** — port 1911, 4911, 5011, 502.
- **Honeywell EBI / Tridium** — varies.
- **GE Proficy / iFIX** — varies.
- **Common findings:** unauthenticated read access (BACnet point list, Modbus register read), default credentials on HMI panels, public-facing engineering workstations.
- **Sources:** Shodan ICS-specific filters (`port:502`, `tag:ics`), Censys, Onyphe.
- **Detectability:** medium-to-high; ICS networks often have low background traffic and are heavily monitored.

### 47.4 IoT / Consumer / SOHO

- **MQTT** — port 1883 (cleartext), 8883 (TLS). Topics often readable without auth.
- **CoAP** — port 5683 (UDP).
- **UPnP / SSDP** — port 1900 (UDP); often discloses internal device map.
- **Common router admin patterns:** `/cgi-bin/`, `/setup.cgi`, `/admin/index.html`. Default creds are the norm.
- **Camera DVRs / NVRs** — Hikvision, Dahua, Axis. Multiple CVEs.
- **Smart-home hubs** — exposed APIs sometimes leak auth tokens.

### 47.5 Government

- **`.gov` and `.mil` domains** require special engagement-scope discipline.
- **FedRAMP / FISMA / DoD CMMC** — defensive posture is generally above baseline.
- **OSINT data sources:** USAspending.gov, SAM.gov (System for Award Management), FBO.gov / sam.gov (procurement).
- **Common findings:** vendor of record disclosed in public contracts → adjacent-vendor pivot.
- **Severity:** as high or higher than commercial; political sensitivity layered on top of technical impact.

### 47.6 Maritime / Aviation / Auto

- **Maritime:** AIS (Automatic Identification System) — vessel positions; tools MarineTraffic, VesselFinder. Engine telemetry sometimes exposed via VSAT.
- **Aviation:** ADS-B (already covered §32.3); operator/airline-specific OPS data sometimes exposed.
- **Automotive:** OEM telematics backends (Tesla, GM OnStar, etc.) — typically authenticated, but APIs leak via mobile-app reverse engineering.

### 47.7 Universal sector caveat

**Most external recon techniques apply universally.** Sector-specific protocols add attack surface; sector-specific compliance regimes add reporting requirements. Don't assume "healthcare/finance/etc. has different OSINT" — the OSINT is the same; the targeted services differ.

---

## 48. Runnable Helper — `secret_scan.py`

> **Content moved to [`references/arsenal.md`](references/arsenal.md).** Section numbering preserved — reference `§48` points here.

## 49. Skill Self-Test

Drop these prompts into a fresh Claude session to verify the skill loads correctly.

1. *"What paths should I probe to find Swagger or OpenAPI specs on a webapp?"* → §16.1.
2. *"Give me the GraphQL introspection query I should POST."* → §16.2.
3. *"What are the high-risk ports to flag from a Shodan scan?"* → §16.3.
4. *"Show me the secret regex catalog."* → §17 (80 patterns) + §48 (runnable Python).
5. *"How do I score an API endpoint by attack interest?"* → §20.
6. *"Validate a leaked Postman API key — what URL?"* → §23.1.
7. *"Give me dorks for pastebin/gist/ghostbin leaks for a target."* → §18.3.
8. *"What endpoints fingerprint a Microsoft Entra tenant?"* → §22.1 + §22.8 for M365 deep.
9. *"How do I score whether a discovered Android app belongs to my target?"* → §21.
10. *"What attack-path hint when I find unauth POST on `/api/users`?"* → §39 (first row).
11. *"Curl one-liner to test for `/actuator/env`."* → §16.13.
12. *"Show me the GraphQL field-suggestion enumeration trick when introspection is disabled."* → §22.9.
13. *"Found a hard-coded JWT in JS. Walk me through full triage."* → §23.12 (JWT workflow).
14. *"Generate cloud bucket candidates for `Target` with subdomains api/billing/hr."* → §16.8.
15. *"How do I find Microsoft 365 Teams federation status + SharePoint subdomains?"* → §22.8.
16. *"Probe paths for Citrix Netscaler / F5 BIG-IP / Pulse Secure."* → §16.16.
17. *"Find the origin behind Cloudflare on `target.example`."* → §16.15 + companion methodology §27.
18. *"What ports/paths probe for Kubernetes/etcd/kubelet exposure?"* → §16.18.
19. *"Audit `acme.com`'s SPF/DMARC for spoof feasibility."* → §16.14.
20. *"List wordlist sources for subdomain bruteforce + content discovery."* → §27.1.
21. *"Run reverse-DNS sweep across a /22 the target owns."* → §28.5.
22. *"Validate an OpenAI API key without burning quota."* → §23.6 + §23.12.
23. *"Find leaked secrets across npm/PyPI/Docker Hub for the target."* → §44.
24. *"How do I enumerate target employees on LinkedIn for a phishing list?"* → §41.
25. *"What's a Slack invite link enumeration technique?"* → §43.1.
26. *"What's the EPSS score and KEV status for CVE-2024-3400?"* → §29.2.
27. *"What modern AI API keys (Anthropic / OpenAI / HuggingFace / Cloudflare) match catalog patterns?"* → §17 rows 30–48.
28. *"Severity matrix for `android:debuggable=true` on prod app?"* → §40.
29. *"Install commands for the standard recon toolkit (subfinder/httpx/nuclei/etc.)?"* → §46.
30. *"For a healthcare engagement, what additional ports / protocols matter?"* → §47.1.
31. *"Pull HudsonRock breach corpus for `target.com` via direct API (no UI)."* → §15.0.1.
32. *"Run the full §16.14 email security audit from a Windows box (PowerShell)."* → §16.14 PowerShell parallel.
33. *"crt.sh just 502'd. What's the fallback chain?"* → §27.0.1.
34. *"Bulk IP → ASN lookup for 200 IPs without burning bgpview rate limit."* → §28.1 (Cymru bulk).
35. *"Common-prefix subdomain sweep for `target.example` covering vpn / api / staging / portal / intranet."* → §16.24.
36. *"Legacy mail (`mail.<domain>`) is NXDOMAIN today but breach corpus has employee URLs against it. What's the finding?"* → §15.2 legacy-mail-decommissioned pattern.
37. *"Confirm M365 tenancy when MX is wrapped by Mimecast (so MX doesn't reveal underlying mail platform)."* → §22.1 autodiscover IP correlation + §16.22 autodiscover-as-confirmation.
38. *"DMARC RUA points to `kdmarc.com` — what does that tell me?"* → §16.14 DMARC reporting-vendor table.
39. *"SharePoint HEAD probe returns HTTP 200. Does that mean anonymous access is granted?"* → §22.8 (no — tenant exists, not anonymous access; distinguish).
40. *"Wayback `*.js` query returned empty for a brochure-ware site. Pivot?"* → §16.23 legacy-app pivot (.asp / .php / .jsp / .cfm / .aspx).
41. *"Found a leaked GitLab / Shopify / Databricks / Okta / Vault token in a repo — does the catalog cover it?"* → §17 rows 49–80 (provider expansion) + §48.
42. *"Walk me through pulling and statically analysing an Android APK for a target."* → §21.1 (acquisition → decompile → manifest/deep-link/Firebase extraction → §17 secret scan → findings).

---

## 50. Changelog

> **Content moved to [`references/changelog.md`](references/changelog.md).** Section numbering preserved — reference `§50` points here.
