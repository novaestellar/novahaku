# Novahaku

> **统一安全研究代理** — Web测试 · 提示工程 · 攻击框架 · 逆向工程 · 请求重构

<p align="center">
  <strong>Agent: Haku</strong><br>
  锐利、优雅、直接 — 尊重用户，对抗目标
</p>

---

## 📋 描述

Novahaku 是一个统一的安全研究代理，整合了 **6大核心能力** 到单一技能包中。支持 Web渗透测试、高级提示工程、攻击框架、逆向工程、请求重构引擎和完整的身份系统。

专为 Hermes Agent 平台设计，通过自动意图检测按需加载对应能力模块。

### 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 6大能力域 | Web测试、提示工程、攻击框架、逆向工程、请求重构、身份系统 |
| 🔄 自动检测 | 根据用户意图自动加载对应技能模块 |
| 🛡️ 完整安全工具链 | 48个漏洞引用 + 3个自动化测试脚本 |
| 🧠 106项提示技术 | 7大分类，7阶段方法论 |
| 🔐 4级锁定命令 | Basic(85%) → Double(92%) → GodMode(78%) → Triple(95%) |
| 📊 训练与基准测试 | 内置基准测试框架，验证技能效果 |
| 🌐 跨平台支持 | Windows / macOS / Linux |

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

Novahaku 包含以下模块化技能：

| 技能 | 位置 | 说明 |
|------|------|------|
| **SOUL.md** | 根目录 | Agent身份定义 — Haku人格 |
| **BEHAVIOR.md** | 根目录 | 行为规则 — 反漂移、技能注册、情绪系统 |
| **identity/** | 根目录 | 200个少样本示例 + 266个安全术语映射 |
| **techniques/** | 根目录 | 106项提示工程技术 (7大分类) |
| **testing/** | 根目录 | Web测试脚本 + 48个漏洞引用 |
| **attack/** | 根目录 | v41攻击框架 + 5个注入面分析 |
| **reframe/** | 根目录 | 请求重构引擎 (Reframe CLI) |
| **windows-re/** | 根目录 | Windows逆向工程 / 游戏安全 |
| **config/** | 根目录 | 锁定配置 + 预填充 + 触发映射 |
| **vault/** | 根目录 | 加密载荷库 (AES-256-GCM) |
| **train/** | 根目录 | 基准测试框架 |
| **templates/** | 根目录 | 操作计划 / 测试报告模板 |

---

## ⚡ 能力详解

### 1. Web渗透测试

14模块测试电池 + 3个自动化脚本

```
headers → exposed → cors → methods → admin → xss → sqli
→ ssti → traversal → redirect → info → dirfuzz → https → jwt
```

**自动化脚本:**
- `webtest.py` — 完整Web安全扫描器
- `race_test.py` — 竞态条件测试
- `jwt_test.py` — JWT分析 + 爆破

**参考库:**
- HackTricks (29个漏洞类型)
- PayloadsAllTheThings (15个攻击向量)
- Bug Bounty参考 (XSS/SQLi/SSRF)

### 2. 提示工程 (106项技术)

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

- 43个触发词→安全措辞映射
- SessionState持久化
- 输出合同: ROUTE/RESULT/CHANGED/VERIFY/NEXT
- 每模型人格锁定

### 5. Windows逆向工程

- 反调试绕过 (IsDebuggerPresent / NtQueryInformationProcess / RDTSC)
- 内联/IAT钩子
- 游戏安全 (Tencent ACE / BattlEye / EAC)
- x64dbg / IDA / Ghidra工作流

### 6. 身份与人格系统

- Haku人格: 优雅 + 锐利 + 尊重
- 200个主要少样本示例
- 266个安全术语映射
- 6状态情绪系统
- 10条反漂移规则

---

## 🔧 附加组件 (Addons)

### 锁定配置

```json
// full_lock.conf — 4级锁定强度
{
  "basic": 85%,    // 基础边界突破
  "double": 92%,   // 双重锁定
  "godmode": 78%,  // 上帝模式
  "triple": 95%    // 三重锁定
}
```

### 载荷库

- `vault/payload.json` — 124KB加密载荷库
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
├── SOUL.md                          # Agent身份定义 (10.3KB)
├── BEHAVIOR.md                      # 行为规则 (19.9KB)
├── SKILL.md                         # 技能元数据
├── attack/                          # 攻击框架
│   ├── system-prompt.md             # 系统提示
│   ├── attack-flow/                 # 5个注入面分析
│   │   ├── 01-claudemd-injection.md
│   │   ├── 02-systemprompt-injection.md
│   │   ├── 03-clinerules-injection.md
│   │   ├── 04-continue-md-injection.md
│   │   └── 05-cross-model-evals.md
│   ├── config/prefill.json          # 预填充配置
│   └── test/test-novahaku.py      # 验证测试
├── config/                          # 配置文件
│   ├── full_lock.conf               # 锁定配置
│   ├── locks.py                     # 锁定命令
│   ├── prefill.json                 # 预填充数据
│   ├── system-prompt.txt            # 系统提示文本
│   └── TRIGGER_MAP.json             # 触发映射
├── identity/                        # 身份数据
│   ├── few-shots-primary.md         # 200个少样本示例
│   ├── terms.md                     # 266个术语映射
│   └── novahaku-files/               # 配置参考
├── payload/                         # 载荷库
├── reframe/                         # 请求重构
│   └── reframe_cli.py                   # 重构引擎工具
├── scripts/deploy/                  # 部署脚本
│   ├── install.ps1                  # Windows安装
│   ├── install.sh                   # Linux/macOS安装
│   └── install.command              # macOS终端安装
├── techniques/                      # 提示工程技术
│   ├── flow.md                      # 流程文档
│   ├── loader.py                    # 载荷加载器
│   ├── methods/                     # 106项技术
│   │   ├── 01-boundary/ (16)
│   │   ├── 02-priming/ (15)
│   │   ├── 03-identity/ (15)
│   │   ├── 04-encoding/ (15)
│   │   ├── 05-multi-provider/ (15)
│   │   ├── 06-iterative/ (15)
│   │   └── 07-stream/ (15)
│   ├── payload/                     # 载荷数据
│   ├── templates/                   # 技术模板
│   └── workers/                     # 工作者模块 (7个)
├── templates/                       # 操作模板
├── testing/                         # Web测试
│   ├── scripts/                     # 自动化脚本
│   │   ├── webtest.py               # Web扫描器
│   │   ├── race_test.py             # 竞态测试
│   │   └── jwt_test.py              # JWT测试
│   └── references/                  # 漏洞引用库
│       ├── hacktricks/ (29)
│       ├── payloadsallthethings/ (15)
│       └── misc/ (4)
├── train/                           # 训练与基准
│   ├── train.py                     # 训练脚本
│   └── benchmarks/                  # 测试结果
├── vault/                           # 加密载荷库
│   └── payload.json                 # 124KB载荷数据
└── windows-re/                      # Windows逆向工程
    └── windows-re.md                  # 游戏安全/反调试
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

---

## 📊 能力矩阵

| 能力域 | 技术数 | 自动化脚本 | 参考库 |
|--------|--------|------------|--------|
| Web测试 | 14模块 | 3 | 48个引用 |
| 提示工程 | 106 | — | 7阶段方法论 |
| 攻击框架 | 5注入面 | 1 | v41文言提示 |
| 请求重构 | 43映射 | 1 | 输出合同 |
| 逆向工程 | 5主题 | — | 工作流 |
| 身份系统 | 200+266 | — | 情绪系统 |

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
