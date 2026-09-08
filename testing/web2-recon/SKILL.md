---
name: web2-recon
description: "Recon pipeline orchestrator — subfinder→httpx→gau→nmap. Findings engine, XLSX report generation. Integrates with offensive-osint for operational arsenal."
version: 1.0.0
---

# web2-recon — Recon Pipeline Orchestrator

## Purpose
End-to-end recon pipeline: asset discovery → live host validation → URL harvesting → port scanning → findings generation → XLSX report.

## Pipeline Stages
1. **Seed** — email security (SPF/DKIM/DMARC), DNS records
2. **Expand** — subdomain enumeration (subfinder, amass)
3. **Validate** — live host detection (httpx)
4. **Enrich** — URL discovery (gau, waybackurls), JS analysis
5. **Scan** — port scanning (nmap), service detection
6. **Report** — findings generation (findings_gen.py), XLSX workbook (build_xlsx.py)

## Scripts
| Script | Purpose |
|--------|---------|
| `scripts/recon_pipeline.sh` | Full pipeline orchestration |
| `scripts/findings_gen.py` | Evidence → findings.csv rules engine |
| `scripts/build_xlsx.py` | findings.csv → multi-tab XLSX workbook |
| `scripts/wordlist.txt` | Domain patterns for enumeration |
| `scripts/test_domain_guard.sh` | Domain safety validation |
| `scripts/requirements.txt` | Python dependencies |

## Usage
```bash
# Full pipeline
bash testing/web2-recon/scripts/recon_pipeline.sh example.com

# Findings only
python testing/web2-recon/scripts/findings_gen.py example.com

# XLSX report
python testing/web2-recon/scripts/build_xlsx.py example.com findings.csv
```

## Integration
- **offensive-osint** — operational arsenal (wordlists, probes, regexes)
- **hunt playbooks** — after recon, load topic-matched hunt-* skills
- **evidence-hygiene** — before saving, validate evidence quality

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
- `tests/fixtures/engagements/clean.example/` — clean engagement template
- `tests/fixtures/engagements/vuln.example/` — vulnerable engagement template
- `tests/test_findings_gen.py` — regression test for findings engine
