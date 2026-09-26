# 逆向工具索引

- 扫描时间: 2026-09-26 00:07:46 +07:00
- 路由入口: `SKILL.md` → `routing.md` → 对应子 skill
- 说明: 本表由 `scripts/reverse-skill/refresh-tool-index.ps1` 自动生成，用于各 Agent 客户端的路由和工具路径确认。
- 注意: MCP-only 能力的工具可用性与运行时分开计算；`npx` 只代表 npm MCP 的运行条件，不能单独让 jshookmcp / reqable-mcp 变成可用或 Ready。

| 工具 | 归属 skill | 作用 | 可用 | 路径 | 版本 | 来源 | 脚本引用 |
|---|---|---|---|---|---|---|---|


---

## 能力状态视图 (Capability Status)

| 能力 | 工具可用 | Ready | MCP 已注册 | 服务在线 | MCP HTTP | 可自动安装 | 安装方式 |
|------|---------|-------|-----------|---------|-----------|---------|
| jadx | ✓ | ✓ | — | — | — | ✓ | github-release-zip |
| apktool | ✓ | ✓ | — | — | — | ✓ | github-release-jar-wrapper |
| jeb-pro | ✗ | ✗ | — | — | — | ✗ | manual |
| frida | ✓ | ✓ | — | — | — | ✓ | pip-package |
| frida-ps | ✓ | ✓ | — | — | — | ✓ | pip-package |
| idalib-mcp | ✓ | ✓ | — | — | — | ✓ | pip-package |
| jshookmcp | ✗ | ✗ | — | — | — | ✓ | npm-mcp |
| reqable-mcp | ✗ | ✗ | — | — | — | ✓ | npm-mcp |
| xquik-mcp | ✗ | ✗ | — | — | — | ✓ | remote-http-mcp |
| anything-analyzer | ✗ | ✓ | — | ✓ | — | ✓ | local-http-mcp |
| idapro | ✗ | ✗ | — | — | — | ✓ | local-http-mcp |
| r2 | ✓ | ✓ | — | — | — | ✓ | github-release-zip |
| rabin2 | ✓ | ✓ | — | — | — | ✓ | github-release-zip |
| adb | ✓ | ✓ | — | — | — | ✓ | winget-package |
| agent-browser | ✓ | ✓ | — | — | — | ✓ | npm-global |
| ghidra-mcp | ✗ | ✓ | — | ✓ | — | ✓ | github-release-zip |
| seclists | ✓ | ✓ | — | — | — | ✓ | git-clone |
| proxycat | ✗ | ✗ | — | — | — | ✓ | git-clone |
| burpsuite-mcp | ✗ | ✓ | — | ✓ | ✓ | ✗ | local-http-mcp |
| pentestswarm | ✓ | ✓ | — | — | — | ✓ | go-install |
| nmap | ✓ | ✓ | — | — | — | ✓ | winget-package |
| binwalk | ✓ | ✓ | — | — | — | ✓ | winget-package |
| yara | ✗ | ✗ | — | — | — | ✓ | winget-package |
| pwntools | ✓ | ✓ | — | — | — | ✓ | pip-package |
| bkcrack | ✗ | ✗ | — | — | — | ✓ | github-release-zip |

> ✓ = 是 | ✗ = 否 | — = 不适用或未检测

