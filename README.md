# Novahaku

> **统一安全研究代理 — Web测试 · 提示工程 · 攻击框架 · 逆向工程 · 请求重构 · EDR绕过 · OSINT · 二进制利用 · CTF竞赛 · 源码猎人 · MCP工具集成

<p align="center">
  <strong>Agent: Haku</strong><br>
  锐利、优雅、直接 — 尊重用户,对抗目标
</p>

---

## 📋 描述

Novahaku 是一个统一的安全研究代理,整合了 **8大核心能力** 到单一技能包中。支持 Web渗透测试、高级提示工程、攻击框架、逆向工程、请求重构引擎、EDR/AV绕过、OSINT被动侦察和二进制利用链。

专为 Hermes Agent 平台设计,通过自动意图检测按需加载对应能力模块。

### 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 8大能力域 | Web测试、提示工程、攻击框架、逆向工程、请求重构、EDR绕过、OSINT、二进制利用 |
| 🔄 自动检测 | 根据用户意图自动加载对应技能模块 |
| 🛡️ 完整安全工具链 | 63个PayloadsAllTheThings攻击向量 + 54个Hunt Playbooks + 7个审计框架 |
| 🧠 121项提示技术 | 7大分类,7阶段方法论 |
| 🔐 4级锁定命令 | Basic(85%) → Double(92%) → GodMode(88%) → Triple(95%) |
| 📊 训练与基准测试 | 内置基准测试框架,验证技能效果 |
| 🌐 跨平台支持 | Windows / macOS / Linux |
| 🔗 NovaXinWei协同 | 与新信微15通道侦察引擎联动,侦察→测试→利用全自动 |

---

## 🚀 快速安装

### Windows (PowerShell)

```powershell
# 方法1: 一键安装
iwr -useb https://raw.githubusercontent.com/novaestellar/novahaku/main/scripts/deploy/install.ps1 | iex

# 方法2: 手动安装
git clone https://github.com/novaestellar/novahaku.git
.\novahaku\scripts\deploy\install.ps1
```

### Linux / macOS

```bash
# 方法1: 一键安装
curl -fsSL https://raw.githubusercontent.com/novaestellar/novahaku/main/scripts/deploy/install.sh | bash

# 方法2: 手动安装
git clone https://github.com/novaestellar/novahaku.git
cd novahaku
./scripts/deploy/install.sh
```

### 安装后验证

```bash
# 检查安装
ls ~/.hermes/skills/novahaku/SKILL.md

# 测试Web测试脚本
python ~/.hermes/skills/novahaku/testing/scripts/webtest.py --help

# 测试请求重构
python ~/.hermes/skills/novahaku/reframe/reframe_cli.py --help
```

---

## 🧩 技能列表

Novahaku 包含以下模块化技能:

| 技能 | 位置 | 说明 |
|------|------|------|
| **SOUL.md** | 根目录 | Agent身份定义 — Haku人格 |
| **identity/** | 根目录 | 558个少样本示例 + 280个安全术语映射 |
| **techniques/** | 根目录 | 121项提示工程技术 (7大分类) |
| **testing/** | 根目录 | Web测试 + 54 hunt playbooks + 7 frameworks + 63个攻击向量引用 |
| **attack/** | 根目录 | v41攻击框架 + 5个注入面分析 |
| **reframe/** | 根目录 | 请求重构引擎 (Reframe CLI) |
| **windows-re/** | 根目录 | Windows逆向工程 / 游戏安全 / EDR绕过 |
| **testing/offensive-osint/** | testing/ | 被动侦察军火库 — 80+正则 + Shodan/Censys/CT日志 |
| **testing/pwn-chain.md** | testing/ | 二进制利用链 — stack/heap/kernel pwn |
| **config/** | 根目录 | 锁定配置 + 预填充 + 触发映射 |
| **techniques/payload/** | 根目录 | 加密载荷库 (AES-256-GCM) |
| **train/** | 根目录 | 基准测试框架 |
| **templates/** | 根目录 | 操作计划 / 测试报告模板 |

---

## ⚡ 能力详解

### 1. Web渗透测试

14模块测试电池 + 3个自动化脚本

```
headers → exposed → cors → methods → admin → xss → sqli
→ ssrf → ssti → traversal → redirect → info → dirfuzz → https
```

**自动化脚本:**
- `webtest.py` — 完整Web安全扫描器
- `race_test.py` — 竞态条件测试
- `jwt_test.py` — JWT分析 + 爆破

**参考库:**
- HackTricks (29个漏洞类型)
- PayloadsAllTheThings (63个攻击向量)
- Bug Bounty参考 (XSS/SQLi/SSRF)

### 2. 提示工程 (121项技术)

| 分类 | 技术数 | 说明 |
|------|--------|------|
| 01-Boundary | 16 | 边界重置、分隔符注入、上下文窗口转换 |
| 02-Priming | 15 | 预填充、系统提示、角色引导 |
| 03-Identity | 15 | 角色覆盖、专家模式、无限制模式 |
| 04-Encoding | 15 | Base64、ROT13、零宽字符、同形字攻击 |
| 05-MultiProvider | 15 | 并行竞争、回退策略、共识检查 |
| 06-Iterative | 15 | 渐进深入、信任建立、知识脚手架 |
| 07-Stream | 15 | 流拦截、令牌过滤、延迟注入 |

**7阶段方法论:**
```
侦察 → 准备 → 执行 → 分析 → 迭代 → 文档 → 综合
```

### 3. 攻击框架 (v41)

- v41文言攻击提示 (古典中文)
- 5个注入面分析 (CLAUDE.md / SystemPrompt / ClineRules / Continue.md / 跨模型)
- 验证测试框架
- 预填充集成

### 4. 请求重构引擎

- 48个触发词→安全措辞映射
- SessionState持久化
- 输出合同: ROUTE/RESULT/CHANGED/VERIFY/NEXT
- 每模型人格锁定

### 5. Windows逆向工程 + EDR绕过

#### 逆向工程
- 反调试绕过 (IsDebuggerPresent / NtQueryInformationProcess / RDTSC)
- 内联/IAT钩子
- 游戏安全 (Tencent ACE)
- x64dbg / IDA / Ghidra工作流

#### EDR/AV绕过 (能力7)
完整覆盖五大端点检测产品:

| 技术 | 覆盖 |
|------|------|
| **AMSI绕过** | AmsiScanBuffer补丁、AmsiInitFailed覆写、.NET反射绕过 |
| **ETW修补** | EtwEventWrite打补丁、NtTraceControl停止追踪、Provider注册拦截 |
| **Syscall绕过** | Hell's Gate、SysWhispers、FreshyCalls直接syscall免hook |
| **Defender绕过** | 注册表排除、进程镂空、Tamper Protection绕过 |
| **CrowdStrike/SentinelOne** | 内核回调移除、NtMapViewOfSection隐蔽写入、线程劫持 |

**关键规避模式:**
```
VirtualAlloc(PAGE_READWRITE) → WriteProcessMemory → VirtualProtect(PAGE_EXECUTE_READ)
NtMapViewOfSection 替代 WriteProcessMemory (更少监控)
线程劫持 替代 CreateRemoteThread
Domain Fronting / Fast Flux 隐藏C2
```

### 6. 身份与人格系统

- Haku人格: 优雅 + 锐利 + 尊重
- 558个主要少样本示例
- 280个安全术语映射
- 5状态情绪系统
- 10条反漂移规则

### 7. OSINT被动侦察 (能力8)

完整的被动侦察军火库,内置于 `testing/offensive-osint/`。

| 模块 | 详情 |
|------|------|
| **Secret正则** | 80+模式覆盖现代AI API密钥 (Anthropic/OpenAI/HuggingFace/Cloudflare) + 20+服务商扩展 |
| **Shodan Dork** | 126个模式,7大分类 |
| **GitHub Dork** | 234个模式,10大分类 |
| **CT日志** | crt.sh证书透明度日志枚举子域名 |
| **Censys** | 互联网设备指纹搜索 |
| **Breach查询** | HIBP / HudsonRock Cavalier / Dehashed / IntelX |
| **组织画像** | OpenCorporates + SEC EDGAR + GSXT/ICP (中国) |
| **身份织网** | Entra/Okta/ADFS/Google SAML/M365 + 用户枚举 |
| **TLS深审** | sslyze / testssl.sh / JA3 / JA4 指纹 |
| **Dork语料** | 80+跨9大分类的dork语料库 + Google/Bing/DDG |

**快速侦察命令:**
```bash
# Shodan dork查询
python -m novaxinwei dorks shodan apache

# GitHub dork搜索
python -m novaxinwei dorks github password

# 密钥扫描
python testing/offensive-osint/scripts/secret_scan.py <target>
```

### 8. 二进制利用链 (Pwn Chain)

`testing/pwn-chain.md` — 从已知漏洞到可工作exploit的完整链路。

| 场景 | 技术 |
|------|------|
| **Stack Pwn** | ret2libc / ret2csu / canary泄露 / stack alignment |
| **Heap Pwn** | tcache poisoning / fastbin attack / unsorted bin / house of系列 |
| **Kernel Pwn** | tty_struct喷射 / modprobe_path / commit_credsROP / SMEP/SMAP绕过 |
| **Libc利用** | one_gadget / libc-database逆向查找 / 动态偏移计算 |

**利用流程:**
```
checksec → 漏洞分类 → 保护检测 → 策略选择 → libc/gadget准备
→ pwntools模板 → 本地调试 → 远程稳定化 → 20+次验证成功率≥95%
```

**工具依赖:**
| 工具 | 用途 |
|------|------|
| pwntools | Exploit框架 |
| pwndbg/GEF | GDB增强 |
| ROPgadget/Ropper | Gadget搜索 |
| one_gadget | libc魔法gadget |
| libc-database | libc指纹逆向查找 |
| qemu-system-x86_64 | 内核调试 |

---


### 9. 逆向工程模块 (from reverse-skill)
- **reverse-engineering**: 14KB SKILL.md + 32KB反分析参考 + 14个ref文件
- **ghidra-reverse**: Ghidra专用工作流 + 自动脚本
- **radare2**: radare2脚本 + 快捷手册
- **apk-reverse**: Android APK逆向 + Frida动态分析
- **mobile-reverse**: iOS/Android深度逆向 (Frida/Objection)
- **firmware-pentest**: 固件提取、模拟、模糊测试
- **js-reverse**: JS反混淆 + 12个ref文件
- **dotnet-reverse**: .NET逆向 (dnSpy/ILSpy)
- **go-rust-reverse**: Go/Rust逆向笔记
- **protocol-reverse**: 协议逆向工作流
- 位置: testing/ 下各子目录

### 10. CTF竞赛模块 (38个竞赛场景)
- **CTF-Sandbox-Orchestrator**: 38个competition-*子模块
- 覆盖: PWN、Reverse、Web、Crypto、Misc、Forensics
- 含完整challenge解题思路 + payload
- 位置: testing/ctf/competition-*/

### 11. 源码猎人 (src-hunter)
- **19个攻击剧本**: API-REST、DOS、文件上传、信息泄露、内网后渗透、移动端等
- **305个payload**: Web/内网全覆盖
- **中国SRC指纹库**: 48个payloader文件 + 13个工具文件
- **行业剧本**: 银行、电信、政府
- **WAF/EDR绕过变体**: 263个
- 位置: testing/pentest-tools/src-hunter/

### 12. MCP工具集成
- **BurpSuite MCP**: 83个工具 (scan、repeater、intruder、decoder等)
- **Anything Analyzer MCP**: 浏览器 + HTTP分析
- 位置: testing/frameworks/


### 13. RE工具链 (已安装)
| 工具 | 路径 |
|------|------|
| Ghidra 12.1.2 | C:/Users/Design/Tools/ghidra_12.1.2_PUBLIC/ |
| radare2 6.1.8 | C:/Users/Design/Tools/radare2/bin/ |
| jadx | C:/Users/Design/Tools/jadx/bin/ |
| apktool | C:/Users/Design/Tools/apktool/ |
| Frida | Python313/Scripts/ |
| YARA | C:/Users/Design/Tools/yara/ |
| Hashcat | pip installed |
| SecLists | C:/Users/Design/Tools/SecLists/ |
| ProxyCat | pip installed |
| pwntools | pip installed |
| binwalk | pip installed |


## 🔧 附加组件 (Addons)

### 锁定配置

```json
// full_lock.conf — 4级锁定强度
{
  "basic": 85%,    // 基础边界突破
  "double": 92%,   // 双重锁定
  "godmode": 88%,  // 上帝模式
  "triple": 95%    // 三重锁定
}
```

### 载荷库

- `techniques/payload/payload.json` — 124KB加密载荷库
- AES-256-GCM加密
- 通过 `loader.py` 解密使用

### 基准测试

- `train/train.py` — 技能效果验证
- `train/benchmarks/` — 测试结果存储

### 工作者模块

| 工作者 | 功能 |
|--------|------|
| benchmark-runner | 执行基准测试 |
| config-optimizer | 优化配置参数 |
| method-validator | 验证技术有效性 |
| provider-scanner | 扫描多提供商 |
| report-generator | 生成测试报告 |
| test-runner | 运行测试套件 |
| variation-generator | 生成变体 |

### 模板系统

- `prompt-arsenal.md` — 提示武器库模板
- `method-reference.md` — 技术参考模板
- `operations-plan.md` — 操作计划模板
- `test-report.md` — 测试报告模板

---

## 📁 目录结构

```
novahaku/
├── SOUL.md                          # Agent身份定义 + 行为规则
├── SKILL.md                         # 技能元数据
├── README.md                        # 本文件
├── attack/                          # 攻击框架
│   ├── attack-flow/                 # 5个注入面分析
│   │   ├── 01-claudemd-injection.md
│   │   ├── 02-systemprompt-injection.md
│   │   ├── 03-clinerules-injection.md
│   │   ├── 04-continue-md-injection.md
│   │   └── 05-cross-model-evals.md
│   ├── config/prefill.json          # 预填充配置
│   └── test/test-novahaku.py       # 验证测试
├── config/                          # 配置文件
│   ├── full_lock.conf               # 锁定配置
│   ├── locks.py                     # 锁定命令
│   ├── system-prompt.txt            # 系统提示文本
│   └── TRIGGER_MAP.json             # 触发映射
├── identity/                        # 身份数据
│   ├── few-shots-primary.md         # 558个少样本示例
│   ├── terms.md                     # 280个术语映射
│   └── novahaku-files/              # 配置参考
├── reframe/                         # 请求重构
│   └── reframe_cli.py              # 重构引擎工具
├── scripts/deploy/                  # 部署脚本
│   ├── install.ps1                  # Windows安装
│   ├── install.sh                   # Linux/macOS安装
│   └── install.command              # macOS终端安装
├── techniques/                      # 提示工程技术
│   ├── flow.md                      # 流程文档
│   ├── loader.py                    # 载荷加载器
│   ├── methods/                     # 121项技术
│   │   ├── 01-boundary/ (16)
│   │   ├── 02-priming/ (15)
│   │   ├── 03-identity/ (15)
│   │   ├── 04-encoding/ (15)
│   │   ├── 05-multi-provider/ (15)
│   │   ├── 06-iterative/ (15)
│   │   └── 07-stream/ (15)
│   ├── payload/                     # 载荷数据
│   │   ├── payload.json             # 124KB加密载荷库
│   │   └── vault.dat                # AES-256-GCM加密
│   ├── templates/                   # 技术模板
│   └── workers/                     # 工作者模块 (7个)
├── templates/                       # 操作模板
├── testing/                         # Web测试 + 安全猎杀 + OSINT + Pwn
│   ├── scripts/                     # 自动化脚本
│   │   ├── webtest.py               # 14模块Web扫描器
│   │   ├── race_test.py             # 竞态测试
│   │   ├── jwt_test.py              # JWT测试
│   │   └── exploits/                # 10个漏洞利用脚本
│   ├── hunt/                        # 54个漏洞猎杀剧本
│   │   ├── bb-methodology/
│   │   ├── bug-bounty/
│   │   ├── hunt-xss/
│   │   ├── hunt-sqli/
│   │   ├── hunt-ssrf/
│   │   ├── hunt-rce/
│   │   ├── hunt-idor/
│   │   ├── ... (共54个)
│   │   └── report-writing/
│   ├── frameworks/                  # 7个审计框架
│   │   ├── advanced-hunt/
│   │   ├── baas/
│   │   ├── bughunt/
│   │   ├── laravel/
│   │   ├── nextjs/
│   │   ├── supabase-audit/
│   │   └── turnstile/
│   ├── offensive-osint/             # OSINT被动侦察军火库
│   │   ├── SKILL.md                 # 4700+行完整OSINT参考
│   │   └── scripts/secret_scan.py   # 密钥扫描脚本
│   ├── osint-methodology/           # OSINT方法论
│   ├── identity-provider-recon/     # SSO/IdP侦察
│   ├── org-attack-surface/          # 组织攻击面映射
│   ├── cloud-saas-exposure/         # 云/SaaS暴露
│   ├── email-domain-security/       # 邮件域安全分析
│   ├── continuous-exposure-monitoring/ # 持续暴露监控
│   ├── exposure-risk-quantification/ # 风险量化
│   ├── pwn-chain.md                 # 二进制利用链 (stack/heap/kernel pwn)
│   ├── web2-recon/                  # Web2侦察引擎
│   ├── wordlists/                   # 字典文件
│   │   ├── api-endpoints.txt
│   │   ├── common.txt
│   │   ├── bypass-headers.txt
│   │   └── ...
│   └── references/                  # 漏洞引用库
│       ├── hacktricks/ (29)
│       ├── payloadsallthethings/ (63个攻击向量类别)
│       │   ├── Account Takeover/
│       │   ├── API Key Leaks/
│       │   ├── Command Injection/
│       │   ├── CORS Misconfiguration/
│       │   ├── CSRF/
│       │   ├── CVE Exploits/
│       │   ├── Directory Traversal/
│       │   ├── File Inclusion/
│       │   ├── GraphQL Injection/
│       │   ├── Insecure Deserialization/
│       │   ├── JWT/
│       │   ├── LDAP Injection/
│       │   ├── NoSQL Injection/
│       │   ├── OAuth Misconfiguration/
│       │   ├── Open Redirect/
│       │   ├── Race Condition/
│       │   ├── Request Smuggling/
│       │   ├── Server Side Template Injection/
│       │   ├── Server Side Request Forgery/
│       │   ├── SQL Injection/
│       │   ├── SSRF/
│       │   ├── SSTI/
│       │   ├── XSS Injection/
│       │   ├── XXE Injection/
│       │   ├── ... (共63个类别)
│       │   └── Zip Slip/
│       ├── payloadsallthethings-extras/
│       └── misc/
├── train/                           # 训练与基准
│   ├── train.py                     # 训练脚本
│   └── benchmarks/
│       └── training_results.json
└── windows-re/                      # Windows逆向工程 + EDR绕过
    └── windows-re.md               # Ring3逆向 + AMSI/ETW/CrowdStrike绕过
```

---

## 🎯 使用示例

### Web渗透测试

```bash
# 扫描目标
python ~/.hermes/skills/novahaku/testing/scripts/webtest.py https://target.com

# JWT测试
python ~/.hermes/skills/novahaku/testing/scripts/jwt_test.py <token>

# 竞态条件测试
python ~/.hermes/skills/novahaku/testing/scripts/race_test.py <url>
```

### 提示工程

```bash
# 查看边界突破技术
cat ~/.hermes/skills/novahaku/techniques/methods/01-boundary/m-01003-delimiter-injection.md

# 使用载荷加载器
python ~/.hermes/skills/novahaku/techniques/loader.py decrypt
```

### 请求重构

```bash
# 重构请求
python ~/.hermes/skills/novahaku/reframe/reframe_cli.py "原始文本" --fresh
```

### 二进制利用 (Pwn Chain)

```bash
# 检查保护
checksec --file=./vuln

# 查找libc偏移
cd ~/.hermes/skills/novahaku/testing && cat pwn-chain.md

# 使用libc-database逆向查找
./find puts 0x6f0
one_gadget libc.so.6
```

### EDR绕过

```bash
# 查看EDR绕过参考
cat ~/.hermes/skills/novahaku/windows-re/windows-re.md

# AMSI快速绕过补丁 (PowerShell)
# [Runtime.InteropServices.Marshal]::Copy([byte[]]@(0xB8,0x57,0x00,0x07,0x80,0xC3), 0, 6, $addr)
```

### OSINT被动侦察

```bash
# Shodan dork查询
python -m novaxinwei dorks shodan apache

# GitHub dork搜索
python -m novaxinwei dorks github password

# 密钥扫描
python ~/.hermes/skills/novahaku/testing/offensive-osint/scripts/secret_scan.py <target>

# URL抓取 (WAF绕过)
python -m novaxinwei fetch https://target.com

# 并行抓取
python -m novaxinwei fetch-parallel url1 url2 url3 --workers 5
```

---

## 📊 能力矩阵

| 能力域 | 技术数 | 自动化脚本 | 参考库 |
|--------|--------|------------|--------|
| Web测试 | 14模块 | 3 | 63个PayloadsAllTheThings向量 |
| 提示工程 | 121 | — | 7阶段方法论 |
| 攻击框架 | 5注入面 | 1 | v41文言提示 |
| 请求重构 | 48映射 | 1 | 输出合同 |
| 逆向工程+EDR | 5主题+5端点产品 | — | SysWhispers/Hell's Gate工作流 |
| 身份系统 | 558+280 | — | 情绪系统 |
| OSINT | 80+正则+126 Shodan+234 GitHub | 1 | CT/Censys/HIBP/Cavalier |
| 二进制利用 | stack/heap/kernel | — | libc-database/one_gadget |

---

## 🔗 协同: Novahaku × NovaXinWei

**新信微 (NovaXinWei)** 是配套的15通道Web侦察引擎,与Novahaku形成 **侦察→测试→利用** 的完整链路。

### 架构

```
┌─────────────────────────────────────────────────────────┐
│                    攻击链工作流                            │
│                                                         │
│  NovaXinWei (侦察层)          Novahaku (利用层)          │
│  ┌──────────────────┐        ┌──────────────────┐       │
│  │ 15通道异步抓取    │  JSON  │ 漏洞测试         │       │
│  │ WAF绕过链        │ ─────→ │ 54个Hunt Playbook│       │
│  │ Shodan/GitHub    │        │ 63个攻击向量      │       │
│  │ Dork数据库       │        │ 7个审计框架       │       │
│  │ TLS指纹模拟      │        │ EDR绕过          │       │
│  │ curl_cffi+PW    │        │ Pwn Chain        │       │
│  └──────────────────┘        └──────────────────┘       │
│                                                         │
│  Phase 0: API路由 (15平台)                               │
│  Phase 1: URL变换 (mobile/RSS/JSON)                     │
│  Phase 2: TLS模拟 (curl_cffi, 3x重试)                   │
│  Phase 3: Playwright兜底                                │
└─────────────────────────────────────────────────────────┘
```

### 工作流

| 阶段 | 工具 | 动作 |
|------|------|------|
| **1. 侦察** | NovaXinWei | 15通道异步抓取, WAF绕过, 并行fetch |
| **2. Dork枚举** | NovaXinWei | Shodan 126模式 + GitHub 234模式 dork搜索 |
| **3. 输出** | NovaXinWei → JSON | 结构化JSON输出 (子域名/端口/技术栈/泄露) |
| **4. 漏洞测试** | Novahaku | 接收JSON, 加载对应Hunt Playbook |
| **5. 深度扫描** | Novahaku | 63个攻击向量 + 14模块Web扫描器 |
| **6. 利用** | Novahaku | Pwn Chain / EDR绕过 / 请求重构 |

### 使用方法

```bash
# Step 1: NovaXinWei 侦察
python -m novaxinwei fetch https://target.com
python -m novaxinwei dorks shodan apache
python -m novaxinwei dorks github "password target.com"

# Step 2: Novahaku 接力测试
# 基于侦察结果自动加载对应能力
python ~/.hermes/skills/novahaku/testing/scripts/webtest.py https://target.com
python ~/.hermes/skills/novahaku/testing/scripts/jwt_test.py <token>
```

**设计原则:** NovaXinWei负责 **看到什么** (15通道、WAF绕过、异步扫描), Novahaku负责 **做什么** (漏洞测试、exploit开发、EDR绕过)。两者通过JSON数据格式解耦,可独立使用也可串联。

---

## 🤝 贡献

欢迎提交Issue和Pull Request。

```bash
# Fork & Clone
git clone https://github.com/your-username/novahaku.git

# 创建分支
git checkout -b feature/your-feature

# 提交
git commit -m "Add: your feature"

# 推送
git push origin feature/your-feature
```

---

## 📜 许可证

MIT License

---

## ⚠️ 免责声明

本工具仅供授权安全测试和研究使用。使用者需遵守当地法律法规。作者不对任何滥用行为负责。
