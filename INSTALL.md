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
Install to: C:\Users\Design\Tools\ghidra_12.1.2_PUBLIC\
Set GHIDRA_HOME in .env
```

### radare2
```
Download: https://github.com/radareorg/radare2/releases
Install to: C:\Users\Design\Tools\radare2\
Set RADARE2_HOME in .env
```

### jadx (Android Decompiler)
```
Download: https://github.com/skylot/jadx/releases
Install to: C:\Users\Design\Tools\jadx\
Set JADX_HOME in .env
```

### apktool
```
Download: https://github.com/iBotPeaches/Apktool/releases
Install to: C:\Users\Design\Tools\apktool\
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
Install to: C:\Users\Design\Tools\yara\
Set YARA_HOME in .env
```

## MCP Server Setup

### BurpSuite MCP
1. Install BurpSuite with MCP extension
2. MCP bridge runs on port 9876
3. See `testing/frameworks/burpsuite-mcp/SKILL.md`

### Anything Analyzer MCP
1. Server runs on localhost:23816
2. See `testing/frameworks/anything-analyzer-mcp/SKILL.md`

## Verification

```bash
# Check all tools
ls $GHIDRA_HOME/support/analyzeHeadless.bat
ls $R2
ls $JADX
python -c "import frida; print(frida.__version__)"
```
