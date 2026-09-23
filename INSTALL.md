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

## Environment Overrides

Semua script menyelesaikan path relatif ke lokasi skripnya sendiri, jadi tidak ada
path absolut yang di-hardcode di dalam kode. Override hanya perlu kalau layout
instalasi Anda berbeda — isi di `.env`, jangan edit skripnya.

```bash
# Root skill novahaku (kosongkan = auto-detect dari lokasi skrip)
NOVAHAKU_HOME=/path/to/novahaku

# Interpreter Python untuk test suite Windows (kosongkan = "python" di PATH)
NOVAHAKU_PYTHON=python

# Direktori kerja engagement (kosongkan = <skill_root>/engagements)
# Dibaca oleh engagement.py, engage_runner.py, dan findings_gen.py
NOVAHAKU_ENGAGEMENT_DIR=/path/to/engagements
```

`scripts/test/novahaku_test_all.ps1` memakai urutan yang sama:
`NOVAHAKU_HOME` → lokasi skrip. Tidak ada path mesin yang tertanam di dalamnya.

## MCP Server Setup

### BurpSuite MCP
1. Install BurpSuite with MCP extension
2. MCP bridge runs on port 9876
3. See `testing/frameworks/burpsuite-mcp/SKILL.md`

### Anything Analyzer MCP
1. Server runs on localhost:23816
2. See `testing/frameworks/anything-analyzer-mcp/SKILL.md`

## Persistent Engagement (cross-session state)

Tidak perlu instalasi tambahan — stdlib-only, tanpa dependency.

```bash
# Buat engagement untuk target
python scripts/engagement.py init target.com --scope "*.target.com"

# Cek status kapan saja (termasuk setelah sesi baru)
python scripts/engagement.py status target.com
python scripts/engagement.py list

# Jalankan testing paralel
python scripts/engage_runner.py race      --target target.com --url https://target.com
python scripts/engage_runner.py integrity --target target.com
python scripts/engage_runner.py selftest
```

Data engagement tersimpan di `engagements/<target>/` dan **gitignored** — state
per-target, evidence, dan findings tidak pernah ikut ter-commit. Hanya
`engagements/TEMPLATE/` yang di-track sebagai dokumentasi layout.

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
```

### Before you apply — rehearsal and snapshot

```bash
# 1. Prove the tool works on a disposable copy. 31 assertions, never touches the live
#    install. If this does not print ALL PASS, do not proceed.
bash scripts/hermes-patch/test-hermes-patch.sh "$HERMES_AGENT_HOME"

# 2. Take your OWN snapshot. This is the real rollback — the tool's backup directory is a
#    single point of failure, and a rolling back over drifted source destroys that drift.
mkdir -p /path/to/hermes-snapshot-manual
cp "$HERMES_AGENT_HOME/tools/memory_tool_store.py" \
   "$HERMES_AGENT_HOME/cron/scheduler_prompt.py" \
   "$HERMES_AGENT_HOME/tools/cronjob_tools.py" \
   "$HERMES_AGENT_HOME/gateway/platforms/api_server.py" \
   /path/to/hermes-snapshot-manual/

# 3. Record the upstream revision. The tool warns on drift but does not pin it.
git -C "$HERMES_AGENT_HOME" rev-parse HEAD 2>/dev/null || echo "not a git checkout"
```

### Apply

```bash
python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --check
# expect: 4/4 targets "clean", exit 0

python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --apply
# expect: "4 file(s) written", an "Auto-verify:" block, "0 failing check(s)", exit 0
```

`--apply` runs `--verify` automatically and rolls back on failure. Do **not** pass
`--no-verify`. Then restart the gateway in a quiet window — the scanners are only reloaded
on restart, and the restart kills any in-flight agent task. Run the commands from a shell
you own, so you are not depending on the agent surviving its own restart.

```bash
python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --verify
# expect: "0 failing check(s)" and "skills_guard : untouched (intended)"
```

### Rollback

```bash
# 1. Restore from YOUR snapshot first — fastest, and proof against a missing backup dir.
cp /path/to/hermes-snapshot-manual/*.py ...   # back to their original locations

# 2. Then let the tool agree:
python scripts/hermes-patch/hermes_patch.py --root "$HERMES_AGENT_HOME" --restore

# 3. THE LOAD-BEARING CHECK — verify against upstream, not against the tool.
git -C "$HERMES_AGENT_HOME" diff --stat     # expect EMPTY
grep -rn "novahaku-patch" \
  "$HERMES_AGENT_HOME/tools/memory_tool_store.py" \
  "$HERMES_AGENT_HOME/cron/scheduler_prompt.py" \
  "$HERMES_AGENT_HOME/tools/cronjob_tools.py" \
  "$HERMES_AGENT_HOME/gateway/platforms/api_server.py"    # expect ZERO hits

# 4. Restart the gateway again — scanning is only live after a restart.
```

`--restore` reporting "N file(s) restored to pre-patch state" is **not** proof the tree
matches upstream. `git diff --stat` is. Scope is platform-wide after a gateway restart:
every session on the machine runs with memory and cron scanning defused. See
`scripts/hermes-patch/README.md` for the blast radius and what still stays defended.

If the goal is only to stop context-file scanning from blocking security skills, use the
supported `HERMES_CONTEXT_SKIP_SCAN=1` switch instead — no source edits, no restart risk,
no memory/cron blast radius.

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
