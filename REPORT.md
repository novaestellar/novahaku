# NOVAHAKU 报告 — 2026-08-30

## 发现的问题

### 1. 路径错误（严重）
**修复前：** 所有文件复制到 `HERMES_HOME/hermes-cs/skills/novahaku/`
**问题：** Hermes 不扫描 `hermes-cs/skills/`。Hermes 扫描 `HERMES_HOME/skills/`。
**修复：** 复制到 `HERMES_HOME/skills/novahaku/` → 然后 `skills/security/novahaku/`

### 2. NOVAHAKU 重复（中等）
**发现：** 2份 novahaku — `skills/novahaku/` 和 `skills/security/novahaku/`
**修复：** 删除 `skills/novahaku/`。规范路径：`skills/security/novahaku/`

### 3. VAULT.DAT + .KEY 缺失（严重）
**发现：** `loader.py` 需要 `techniques/payload/.key` 和 `techniques/payload/vault.dat` — 两者都不存在（被 .gitignore 排除）
**修复：** 从备份恢复：`D:\Labs\novahaku\skills-backup-20260829-224444\inces\payload\`
**位置：** `skills/security/novahaku\vault\` 和 `skills/security/novahaku\techniques\payload\`

### 4. PAYLOAD/ 文件夹为空（低）
**发现：** `skills/novahaku/payload/` 存在但为空（修复前被复制）
**修复：** 已复制到 `skills/security/novahaku/payload/`

### 5. 自动加载有效但有限制
**事实：** SKILL.md 自动加载规则有效。Hermes 读取 SKILL.md → 扫描意图 → 加载对应文件。
**限制：**
- 文件过大（58KB + 61KB）无法完全自动加载
- vault.dat + .key 缺失 → 解密失败（已修复）
- 脚本必须手动执行（webtest.py、reframe_cli.py 等）

---

## 修复后状态

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| novahaku 路径 | hermes-cs/skills/（错误） | skills/security/novahaku/（正确） |
| 重复 | 2份 | 1份规范路径 |
| vault.dat | 不存在 | ✅ 156KB |
| .key | 不存在 | ✅ 32 bytes |
| payload.json | ✅ 123KB（2份） | ✅ 123KB |
| 测试 | 121/121 | 121/121 |
| 121 methods | 121 实际内容 | 121 实际内容 |
| 558 few-shots | ✅ | ✅ |
| 278 terms | ✅ | ✅ |

---

## 6个来源 → NOVAHAKU：状态

| # | 来源 | 文件 | 状态 | 自动加载？ |
|---|------|------|------|-----------|
| 1 | haiou | few-shots (58KB), terms (14KB), novahaku-files/ (71KB), scripts/deploy/ | ✅ | ❌ 手动读取 |
| 2 | inces | 121 methods, loader.py, flow.md, workers/7, templates/4, locks.py, vault.dat+.key, train.py | ✅ | ❌ 手动读取+执行 |
| 3 | web-exploit | webtest.py (16KB), race_test.py (4KB), jwt_test.py (6KB), references/ (48) | ✅ | ❌ 手动执行 |
| 4 | prometheus | system-prompt.md, attack-flow/ (5), test-novahaku.py, prefill.json | ✅ | ❌ 手动读取 |
| 5 | dmf | reframe_cli.py (12KB), full_lock.conf | ✅ | ❌ 手动执行 |
| 6 | agents-1 | windows-re.md (3.8KB) | ✅ | ❌ 手动读取 |

**总计：6/6 来源已适配。0 自动加载（全部手动）。**

---

## 规范路径

```
C:\Users\Design\AppData\Local\hermes\
├── skills/
│   └── security/
│       └── novahaku/         ← 规范路径（不要删除）
├── SOUL.md
├── BEHAVIOR.md
├── config.yaml
├── plugins/
│   ├── hermes-lcm/
│   ├── mnemosyne-dashboard/
│   └── opencode/
└── gateway-service/
```

---

## 文件参考

| 文件 | 位置 | 大小 | 功能 |
|------|------|------|------|
| HANDOFF | `Desktop\HANDOFF_HAKU_AGENT.md` | 20KB | Hermes 操作指南 |
| 测试套件 | `Desktop\novahaku_test_all.ps1` | 34KB | 121 项自动检查 |
| 仓库 | `github.com/novaestellar/novahaku` | — | 公开 GitHub |
| 备份 | `D:\Labs\novahaku\skills-backup-20260829-224444\` | — | 原始6个技能 |

---

*由 OpenCode (Sisyphus) 于 2026-08-30 创建。*
