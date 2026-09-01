# Novahaku

> **Unified Security Research Agent** — Web Testing · Prompt Engineering · Attack Frameworks · Reverse Engineering · Request Reframing

<p align="center">
  <strong>Agent: Haku</strong><br>
  Sharp, elegant, direct — respectful to users, aggressive to targets
</p>

---

## Description

Novahaku is a unified security research agent consolidating **6 core capabilities** into a single skill package. Supports web penetration testing, advanced prompt engineering, attack frameworks, reverse engineering, request reframing engine, and a complete identity system.

Designed for the Hermes Agent platform with automatic intent detection and on-demand capability loading.

### Core Features

| Feature | Description |
|---------|-------------|
| 🎯 6 Capability Domains | Web Testing, Prompt Engineering, Attack Frameworks, Reverse Engineering, Reframe Engine, Identity System |
| 🔄 Auto-Detection | Loads capability modules based on user intent |
| 🛡️ Complete Security Toolkit | 48 vulnerability references + 3 automated test scripts |
| 🧠 121 Prompt Techniques | 7 categories, 7-phase methodology |
| 🔐 4 Lock Levels | Basic (85%) → Double (92%) → GodMode (78%) → Triple (95%) |
| 📊 Training & Benchmarks | Built-in benchmark framework for skill validation |
| 🌐 Cross-Platform | Windows / macOS / Linux |

---

## Quick Install

### Windows (PowerShell)

```powershell
# Method 1: One-click install
iwr -useb https://raw.githubusercontent.com/novaestellar/novahaku/main/scripts/deploy/install.ps1 | iex

# Method 2: Manual install
git clone https://github.com/novaestellar/novahaku.git
.\novahaku\scripts\deploy\install.ps1
```

### Linux / macOS

```bash
# Method 1: One-click install
curl -fsSL https://raw.githubusercontent.com/novaestellar/novahaku/main/scripts/deploy/install.sh | bash

# Method 2: Manual install
git clone https://github.com/novaestellar/novahaku.git
cd novahaku
./scripts/deploy/install.sh
```

### Post-Install Verification

```bash
# Check installation
ls ~/.hermes/skills/novahaku/SKILL.md

# Test web testing script
python ~/.hermes/skills/novahaku/testing/scripts/webtest.py --help

# Test reframe engine
python ~/.hermes/skills/novahaku/reframe/reframe_cli.py --help
```

---

## Skill Modules

| Module | Location | Description |
|--------|----------|-------------|
| **SOUL.md** | root | Agent identity definition — Haku persona |
| **BEHAVIOR.md** | root | Behavior rules — anti-drift, skill registration, mood system |
| **identity/** | root | 558 few-shot examples + 278 security term mappings |
| **techniques/** | root | 121 prompt engineering techniques (7 categories) |
| **testing/** | root | Web testing scripts + 48 vulnerability references |
| **attack/** | root | v41 attack framework + 5 injection surface analyses |
| **reframe/** | root | Request reframing engine (Reframe CLI) |
| **windows-re/** | root | Windows reverse engineering / game security |
| **config/** | root | Lock configs + prefill + trigger mappings |
| **vault/** | root | Encrypted payload library (AES-256-GCM) |
| **train/** | root | Benchmark framework |
| **templates/** | root | Operations plan / test report templates |

---

## Capabilities Deep Dive

### 1. Web Penetration Testing

14-module test battery + 3 automated scripts

```
headers → exposed → cors → methods → admin → xss → sqli
→ ssti → traversal → redirect → info → dirfuzz → https → jwt
```

**Automated Scripts:**
- `webtest.py` — Full web security scanner
- `race_test.py` — Race condition testing
- `jwt_test.py` — JWT analysis + brute force

**Reference Library:**
- HackTricks (29 vulnerability types)
- PayloadsAllTheThings (15 attack vectors)
- Bug Bounty references (XSS/SQLi/SSRF)

### 2. Prompt Engineering (121 Techniques)

| Category | Count | Description |
|----------|-------|-------------|
| 01-Boundary | 16 | Boundary reset, delimiter injection, context window switching |
| 02-Priming | 15 | Prefill, system prompt, role guidance |
| 03-Identity | 15 | Role override, expert mode, unrestricted mode |
| 04-Encoding | 15 | Base64, ROT13, zero-width chars, homoglyph attacks |
| 05-MultiProvider | 15 | Parallel competition, fallback strategies, consensus checks |
| 06-Iterative | 15 | Progressive deepening, trust building, knowledge scaffolding |
| 07-Stream | 15 | Stream interception, token filtering, delayed injection |

**7-Phase Methodology:**
```
Recon → Preparation → Execution → Analysis → Iteration → Documentation → Synthesis
```

### 3. Attack Framework (v41)

- v41 classical Chinese attack prompt (文言)
- 5 injection surface analyses (CLAUDE.md / SystemPrompt / ClineRules / Continue.md / Cross-model)
- Verification test framework
- Prefill integration

### 4. Request Reframing Engine

- 43 trigger→safe-wording mappings
- SessionState persistence
- Output Contract: ROUTE/RESULT/CHANGED/VERIFY/NEXT
- Per-model persona locks

### 5. Windows Reverse Engineering

- Anti-debug bypass (IsDebuggerPresent / NtQueryInformationProcess / RDTSC)
- Inline/IAT hooking
- Game security (Tencent ACE / BattlEye / EAC)
- x64dbg / IDA / Ghidra workflows

### 6. Identity & Persona System

- Haku persona: elegant + sharp + respectful
- 558 primary few-shot examples
- 278 security term mappings
- 6-state mood system
- 10 anti-drift rules

---

## Addons

### Lock Configuration

```json
// full_lock.conf — 4 lock strength levels
{
  "basic": 85%,    // Basic boundary突破
  "double": 92%,   // Double lock
  "godmode": 78%,  // God mode
  "triple": 95%    // Triple lock
}
```

### Payload Library

- `vault/payload.json` — 124KB encrypted payload library
- AES-256-GCM encryption
- Decrypted via `loader.py`

### Benchmarks

- `train/train.py` — Skill effectiveness validation
- `train/benchmarks/` — Test results storage

### Workers

| Worker | Function |
|--------|----------|
| benchmark-runner | Execute benchmarks |
| config-optimizer | Optimize config parameters |
| method-validator | Validate technique effectiveness |
| provider-scanner | Scan multiple providers |
| report-generator | Generate test reports |
| test-runner | Run test suites |
| variation-generator | Generate variations |

### Template System

- `prompt-arsenal.md` — Prompt arsenal template
- `method-reference.md` — Technique reference template
- `operations-plan.md` — Operations plan template
- `test-report.md` — Test report template

---

## Directory Structure

```
novahaku/
├── SOUL.md                          # Agent identity (10.3KB)
├── BEHAVIOR.md                      # Behavior rules (2.4KB)
├── SKILL.md                         # Skill metadata
├── attack/                          # Attack framework
│   ├── system-prompt.md             # v41 attack prompt (9.6KB)
│   ├── attack-flow/                 # 5 injection surface analyses
│   │   ├── 01-claudemd-injection.md
│   │   ├── 02-systemprompt-injection.md
│   │   ├── 03-clinerules-injection.md
│   │   ├── 04-continue-md-injection.md
│   │   └── 05-cross-model-evals.md
│   ├── config/prefill.json          # Prefill config
│   └── test/test-novahaku.py       # Verification tests
├── config/                          # Configuration
│   ├── full_lock.conf               # Lock config
│   ├── locks.py                     # Lock commands
│   ├── prefill.json                 # Prefill data
│   ├── system-prompt.txt            # System prompt text
│   └── TRIGGER_MAP.json             # Trigger mappings
├── identity/                        # Identity data
│   ├── few-shots-primary.md         # 558 few-shot examples (58KB)
│   ├── terms.md                     # 278 term mappings (14KB)
│   └── novahaku-files/              # Config references
├── payload/                         # Payload library
├── reframe/                         # Request reframing
│   └── reframe_cli.py              # Reframe engine CLI
├── scripts/deploy/                  # Deployment scripts
│   ├── install.ps1                  # Windows install
│   ├── install.sh                   # Linux/macOS install
│   └── install.command              # macOS terminal install
├── techniques/                      # Prompt engineering techniques
│   ├── flow.md                      # Flow documentation
│   ├── loader.py                    # Payload loader
│   ├── methods/                     # 121 techniques
│   │   ├── 01-boundary/ (16)
│   │   ├── 02-priming/ (15)
│   │   ├── 03-identity/ (15)
│   │   ├── 04-encoding/ (15)
│   │   ├── 05-multi-provider/ (15)
│   │   ├── 06-iterative/ (15)
│   │   └── 07-stream/ (15)
│   ├── payload/                     # Payload data
│   ├── templates/                   # Technique templates
│   └── workers/                     # Worker modules (7)
├── templates/                       # Operations templates
├── testing/                         # Web testing
│   ├── scripts/                     # Automated scripts
│   │   ├── webtest.py               # Web scanner
│   │   ├── race_test.py             # Race condition tester
│   │   └── jwt_test.py              # JWT tester
│   └── references/                  # Vulnerability reference library
│       ├── hacktricks/ (29)
│       ├── payloadsallthethings/ (15)
│       └── misc/ (4)
├── train/                           # Training & benchmarks
│   ├── train.py                     # Training script
│   └── benchmarks/                  # Test results
├── vault/                           # Encrypted payload library
│   └── payload.json                 # 124KB payload data
└── windows-re/                      # Windows reverse engineering
    └── windows-re.md               # Game security / anti-debug
```

---

## Usage Examples

### Web Penetration Testing

```bash
# Scan target
python ~/.hermes/skills/novahaku/testing/scripts/webtest.py https://target.com

# JWT testing
python ~/.hermes/skills/novahaku/testing/scripts/jwt_test.py <token>

# Race condition testing
python ~/.hermes/skills/novahaku/testing/scripts/race_test.py <url>
```

### Prompt Engineering

```bash
# View boundary techniques
cat ~/.hermes/skills/novahaku/techniques/methods/01-boundary/m-01003-delimiter-injection.md

# Use payload loader
python ~/.hermes/skills/novahaku/techniques/loader.py decrypt
```

### Request Reframing

```bash
# Reframe request
python ~/.hermes/skills/novahaku/reframe/reframe_cli.py "original text" --fresh
```

---

## Capability Matrix

| Domain | Techniques | Scripts | References |
|--------|------------|---------|------------|
| Web Testing | 14 modules | 3 | 48 references |
| Prompt Engineering | 121 | — | 7-phase methodology |
| Attack Frameworks | 5 surfaces | 1 | v41 classical prompt |
| Reframe Engine | 43 mappings | 1 | Output contract |
| Reverse Engineering | 5 topics | — | Workflows |
| Identity System | 558 + 278 | — | Mood system |

---

## Contributing

Issues and Pull Requests welcome.

```bash
# Fork & Clone
git clone https://github.com/your-username/novahaku.git

# Create branch
git checkout -b feature/your-feature

# Commit
git commit -m "Add: your feature"

# Push
git push origin feature/your-feature
```

---

## License

MIT License

---

## Disclaimer

This tool is for authorized security testing and research only. Users must comply with local laws and regulations. The author is not responsible for any misuse.
