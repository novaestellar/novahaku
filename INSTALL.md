# INSTALL.md — Novahaku Installation Guide

## Quick Start (Hermes)

Novahaku is a Hermes skill. Install via:

1. Clone/copy `novahaku/` to `~/.hermes/skills/security/novahaku/`
2. Restart Hermes gateway
3. Skill auto-loads on trigger keywords

## RE Tool Installation

### Ghidra
```
Download: https://github.com/NationalSecurityAgency/ghidra/releases
Install to: /opt/ghidra/ (Linux/macOS) or C:\tools\ghidra\ (Windows)
Set GHIDRA_HOME in .env
```

### radare2
```
Download: https://github.com/radareorg/radare2/releases
Install to: /usr/local/bin/r2 (Linux/macOS) or C:\tools\radare2\bin\ (Windows)
Set RADARE2_HOME in .env
```

### jadx (Android Decompiler)
```
Download: https://github.com/skylot/jadx/releases
Install to: /opt/jadx/bin/ (Linux/macOS) or C:\tools\jadx\bin\ (Windows)
Set JADX_HOME in .env
```

### apktool
```
Download: https://github.com/iBotPeaches/Apktool/releases
Install to: /opt/apktool/ (Linux/macOS) or C:\tools\apktool\ (Windows)
Set APKTOOL_HOME in .env
```

### Frida
```
pip install frida-tools
Set FRIDA_HOME in .env
```

### YARA
```
Download: https://github.com/VirusTotal/yara/releases
Install to: /usr/local/bin/yara (Linux/macOS) or C:\tools\yara\ (Windows)
Set YARA_HOME in .env
```

### Hashcat
```
pip install hashcat (or install from https://hashcat.net/hashcat/)
```

### SecLists
```
git clone https://github.com/danielmiessler/SecLists.git /opt/SecLists
Set SECLISTS_HOME in .env
```

### ProxyCat
```
pip install proxycat
```

### pwntools
```
pip install pwntools
```

### binwalk
```
pip install binwalk
```

## Python Dependencies for CVE Exploits

GitLab & Keycloak exploits require:
```bash
pip install requests urllib3
```

Optional (for advanced features):
```bash
pip install curl_cffi playwright camoufox  # Anti-detection browser automation
pip install PyGithub PyYAML  # CI/CD workflow scanner (hunt-cicd/scripts/workflow_vuln_scan.py)
```

## MCP Server Setup

### BurpSuite MCP
1. Install BurpSuite with MCP extension
2. MCP bridge runs on port 9876
3. See `testing/frameworks/burpsuite-mcp/SKILL.md`

### Anything Analyzer MCP
1. Server runs on localhost:23816
2. See `testing/frameworks/anything-analyzer-mcp/SKILL.md`

## Local Hermes Patch (optional, local-only)

`scripts/hermes-patch/` defuses Hermes' own prompt-injection scanners on the memory and
cron write paths. It is **not** installed as part of novahaku and is never invoked by the
loader, the routing table, or any skill. Stdlib-only Python — no dependencies.

```bash
export HERMES_AGENT_HOME=/path/to/hermes-agent/app   # the dir containing tools/

python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --check
python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --apply
python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --verify
python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --restore

# prove the tool works before touching a live install (31 assertions, disposable copy)
bash scripts/hermes-patch/test-hermes-patch.sh "$HERMES_AGENT_HOME"
```

Take a manual snapshot of the four target files **before** applying — the tool's own backup
directory is a single point of failure. Scope is platform-wide after a gateway restart.
See `scripts/hermes-patch/README.md` for blast radius and the rollback drill.

## Verification

```bash
# Check all tools
ls $GHIDRA_HOME/support/analyzeHeadless.bat  # or analyzeHeadless on Linux
ls $R2
ls $JADX
python -c "import frida; print(frida.__version__)"
yara --version
hashcat --version

# Hermes patch tool (only if you intend to use it; safe to run against any tree)
python scripts/hermes-patch/hermes_patch.py --help
bash scripts/hermes-patch/test-hermes-patch.sh "$HERMES_AGENT_HOME"   # expect ALL PASS
```
