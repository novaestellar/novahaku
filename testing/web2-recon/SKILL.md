---
name: web2-recon
description: "Recon pipeline orchestrator — subfinder→httpx→gau→nmap. Findings engine, XLSX report generation. Integrates with offensive-osint for operational arsenal."
version: 1.0.0
---

# web2-recon — Recon Pipeline Orchestrator

## Purpose
End-to-end recon pipeline: asset discovery → live host validation → URL harvesting → port scanning → findings generation → XLSX report.

## Pipeline Stages
1. **Seed** — email security (SPF/DKIM/DMARC), DNS records, initial domain profile
2. **Expand** — subdomain enumeration (subfinder, amass, certificate transparency)
3. **Validate** — live host detection (httpx), HTTP status, technology fingerprinting
4. **Enrich** — URL discovery (gau, waybackurls), JS file analysis, parameter harvesting
5. **Scan** — port scanning (nmap), service detection, banner grabbing
6. **Report** — findings generation (findings_gen.py), XLSX workbook (build_xlsx.py)

## Scripts
| Script | Purpose |
|--------|---------|
| `scripts/recon_pipeline.sh` | Full pipeline orchestration (6-stage) |
| `scripts/findings_gen.py` | Evidence → findings.csv rules engine |
| `scripts/build_xlsx.py` | findings.csv → multi-tab XLSX workbook |
| `scripts/wordlist.txt` | Domain patterns for enumeration |
| `scripts/test_domain_guard.sh` | Domain safety validation |
| `scripts/requirements.txt` | Python dependencies (openpyxl) |

## Usage
```bash
# Full pipeline
bash testing/web2-recon/scripts/recon_pipeline.sh example.com

# Findings only
python testing/web2-recon/scripts/findings_gen.py example.com

# XLSX report
python testing/web2-recon/scripts/build_xlsx.py example.com findings.csv

# Domain safety check
bash testing/web2-recon/scripts/test_domain_guard.sh
```

## Evidence Collection Per Stage
| Stage | Output Files | Location |
|-------|-------------|----------|
| Seed | `email-security.txt`, `dns-records.txt` | `evidence/stage1-seed/` |
| Expand | `subs-all.txt`, `resolved.txt`, `live-hosts.txt` | `evidence/stage2-expansion/` |
| Enrich | `urls.txt`, `js-secrets.txt`, `s3-validation.txt` | `evidence/stage3-enrichment/` |
| Scan | `nmap-public.gnmap`, `internal-ip-leak-hosts.txt` | `evidence/ports/` |

## Findings Engine Rules
`findings_gen.py` applies deterministic rules to evidence:
- **Critical**: exposed credentials, public S3 buckets, leaked API keys
- **High**: open admin panels, exposed databases, misconfigured CORS
- **Medium**: missing security headers, information disclosure
- **Low**: verbose error messages, outdated software versions

Each finding includes: severity, category, evidence path, affected asset, remediation hint.

## Integration Points
- **offensive-osint** — operational arsenal (wordlists, probes, regexes)
- **hunt playbooks** — after recon, load topic-matched hunt-* skills
- **evidence-hygiene** — before saving, validate evidence quality
- **continuous-exposure-monitoring** — feed recon output into ongoing monitoring

## Engagement Structure
```
engagements/<domain>/
├── evidence/
│   ├── stage1-seed/        # email-security.txt, dns-records.txt
│   ├── stage2-expansion/   # subs-all.txt, resolved.txt, live-hosts.txt
│   ├── stage3-enrichment/  # urls.txt, js-secrets.txt, s3-validation.txt
│   └── ports/              # nmap-public.gnmap, internal-ip-leak-hosts.txt
├── findings.csv
└── report.xlsx
```

## Test Fixtures
- `tests/fixtures/engagements/clean.example/` — clean engagement template (all stages empty or benign)
- `tests/fixtures/engagements/vuln.example/` — vulnerable engagement template (contains deliberate findings)
- `tests/test_findings_gen.py` — regression test for findings engine (verifies rule application)

## Error Handling
- Pipeline stages are independent — failure in one stage does not abort others
- `recon_pipeline.sh` logs per-stage exit codes to `evidence/pipeline.log`
- `findings_gen.py` skips missing evidence files with warning (never crashes)
- Domain guard rejects private IPs, localhost, and non-registered TLDs

## Output Formats
- **findings.csv**: machine-readable, columns: severity, category, asset, evidence, remediation
- **report.xlsx**: multi-tab workbook — Summary, Critical, High, Medium, Low, Evidence Index

## Tool Prerequisites
| Tool | Purpose | Install |
|------|---------|---------|
| subfinder | Subdomain enumeration | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` |
| httpx | Live host probing | `go install github.com/projectdiscovery/httpx/cmd/httpx@latest` |
| gau | URL discovery (Wayback + Common Crawl) | `go install github.com/lc/gau/v2/cmd/gau@latest` |
| nmap | Port scanning | `apt install nmap` or `brew install nmap` |
| python3 + openpyxl | XLSX report generation | `pip install openpyxl` |

## Limitations
- Passive only — no active exploitation or fuzzing (use hunt-* skills for that)
- Requires outbound internet access for subdomain/URL sources
- nmap SYN scan requires root/admin privileges on some platforms
- XLSX generation requires Python 3.8+ with openpyxl
