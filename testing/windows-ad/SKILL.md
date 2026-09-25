---
license: MIT
author: novalabs
name: windows-ad
description: Use for authorized Active Directory and Windows identity attacks including Kerberos, AD CS, BloodHound paths, NTLM relay, and domain privilege escalation research.
---

# Windows / Active Directory Security

## ACTION REQUIRED（读完后立刻执行）

1. `NOW`: 读取 `../field-journal/precedent-pentest.md`
2. `NOW`: **域/AD 测试必须明确授权范围**（含 DC、是否允许投毒/中继）
4. `NEXT`: tool-index（impacket/certipy/bloodhound 等常手动）
5. `ACT`: 从身份枚举与 BloodHound 图开始，不先上破坏性利用

## 适用场景

- 域渗透、Kerberoasting、AS-REP、委派
- AD CS（ESC1–ESC8 等）证书攻击
- BloodHound / SharpHound 攻击路径
- NTLM Relay / Coercer 强制认证
- 本地提权到域路径（Potato 等作为跳板）

## 与 attack-chain 关系

- **多阶段从外网到域控** → PRIMARY 可仍是 `attack-chain/`，本 skill 为 **AD 专科**
- **已在域内专注身份** → PRIMARY = 本 skill

## 工作流

### 1. 枚举

```bash
# 示例 Impacket / 内置（需凭据与授权）
nxc smb <range> -u user -p pass
bloodhound-python -d domain.local -u user -p pass -c All -ns <DC>
```

### 2. 常见路径（先图后枪）

```text
□ Kerberoast / AS-REP → 离线破解
□ ACL 滥用（GenericAll/WriteDacl）
□ 委派（非约束/约束/基于资源）
□ AD CS 模板错误 → Certipy
□ 中继：LLMNR/NBT-NS + ntlmrelayx（确认授权）
```

### 3. 凭证与横向

```text
□ secretsdump / lsassy / mimikatz（严格授权与清理）
□ PtH / PtT / 黄金票仅在授权红队范围
□ 每步写 Evidence；高危等用户确认
```

## 本地提权：令牌与 SeImpersonate

服务账号（IIS APPPOOL、MSSQL$、NETWORK SERVICE 等）常带 `SeImpersonate`。
拿到这类令牌后，从服务账号到 SYSTEM 有一条稳定路径。

### 1. 令牌特权枚举

```text
whoami /priv
# 关注：SeImpersonatePrivilege / SeAssignPrimaryTokenPrivilege / SeDebugPrivilege
```

### 2. Potato 家族（SeImpersonate → SYSTEM）

由拥有 `SeImpersonate` 的服务账号强制一个高权限进程向自己认证，再假冒其令牌。

```text
□ JuicyPotato   — Windows Server 2019 之前，需可用的 CLSID
□ RoguePotato   — 2019+，走 OXID resolver 回连
□ SweetPotato   — 合并多种触发，自动挑可用 CLSID
□ PrintSpoofer  — 利用 Spooler 命名管道，2016/2019 常用
□ GodPotato     — 覆盖面最广，2012–2022 通吃
```

```text
# PrintSpoofer 典型形态
PrintSpoofer.exe -i -c "cmd /c whoami"
PrintSpoofer.exe -c "C:\path\payload.exe"
```

### 3. 命名管道客户端假冒

原理：服务端创建管道并持有 `SeImpersonate`，客户端写入时服务端可冒充客户端令牌。

```text
□ 找到以 SYSTEM 运行、且会连接外部管道的服务
□ 抢夺管道名 → 服务连上来 → 冒充其令牌
□ meterpreter getsystem 用的就是这条路
```

配套工具：`PipeViewer`（列出所有管道找提权点）、`pipe-intercept`（拦截管道通信）。

### 4. SeDebug + SeImpersonate 复制令牌

拥有这两个特权时可打开任意非保护进程、复制其令牌、以该令牌创建进程。

```text
□ 挑一个以 SYSTEM 运行且持有全部令牌特权的进程
□ OpenProcess(SeDebug) → OpenProcessToken → DuplicateTokenEx
□ CreateProcessWithTokenW → SYSTEM shell
```

### 5. 相关

- High Integrity → System（命名管道）：`references/windows-local-privilege-escalation/`
- Token 窃取后横向：`#secretsdump` / PtH
- 每次都记 Evidence；提权动作只限授权范围

## 工具链

| 工具 | 用途 |
|------|------|
| BloodHound / SharpHound | 路径图 |
| Certipy | AD CS |
| Impacket / NetExec | 横向与枚举 |
| Rubeus / Mimikatz | 票据与凭证（授权） |
| Coercer / Responder | 强制认证 / 投毒 |

## 参考

- `references/ad-attack-paths.md`
- `../pentest-tools/references/network-attack-defense.md`
- `../attack-chain/`
- seeds: `field-journal/seed-005_ad-certipy-esc1.md` `seed-007_ntlm-relay-coercer.md` `seed-013_kerberoasting-spn.md`

## 路由上下文

**上游**: MASTER R24  
**下游**: 报告 `docs-generator`；需 EDR 研究 `edr-bypass-re`  
**MUST NOT**: 无授权 DCSync / 黄金票打生产

## 任务完成自检

- [ ] 是否先有图/枚举再有利用？
- [ ] 是否记录可复现命令并脱敏？
- [ ] 是否遵守 scope 禁止项？
- [ ] Checklist？