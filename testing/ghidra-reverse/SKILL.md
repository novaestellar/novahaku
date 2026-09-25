---
license: MIT
author: novalabs
name: ghidra-reverse
description: Use for free/open reverse engineering with Ghidra (headless or GUI), including decompile, cross-refs, and optional Ghidra MCP workflows when IDA is unavailable.
---

# Ghidra Reverse Engineering

## ACTION REQUIRED（读完后立刻执行）

1. `NOW`: 读取 `../field-journal/precedent-reverse.md`
2. `NOW`: 确认需要 **Ghidra**（无 IDA / 偏好开源 / 批量 headless）
3. `NEXT`: 读 `../tool availability table` 查 ghidra / ghidra-mcp 路径
4. `NEXT`: 缺工具 → bootstrap `ghidra-mcp`（若 manifest 支持）或按手动步骤装 Ghidra
5. `ACT`: 导入样本 → 自动分析 → 导出关键函数反编译

## 适用场景

- 无 IDA 许可证时的主逆向入口
- 批量 headless 分析 / CI 中反编译
- Ghidra 脚本（Java/Python Jython/PyGhidra）自动化
- 与 `binary-diff` / `patch-diff-exploit` 的 ghidriff 联动

## 与 IDA 分工

| 需求 | 优先 |
|------|------|
| 已有 IDA MCP 深挖 | `ida-reverse/` |
| 开源 / 批量 / 教学 | **本 skill** |
| 仅 CLI 快速侦察 | `radare2/` |

## 工作流

### 1. 项目与自动分析

```text
□ 新建 Project → Import 文件 → Analyze（默认分析器）
□ 记录语言/编译器识别结果与基址
□ 标记入口、导出表、字符串 xref
```

### 2. 关键函数

```text
□ 从字符串 / 导入 API 反查
□ Decompile 窗口还原算法
□ 重命名函数/变量；写 Plate comment
□ 需要动态时交接 Frida/GDB（reverse-engineering 动态章）
```

### 3. Headless（批量）

```bash
# 示例：analyzeHeadless 路径因安装而异，MUST 从 tool-index 取
analyzeHeadless /path/to/project Proj -import sample.bin -postScript ExportDecomp.py
```

### 4. MCP（若已配置）

MCP 是**可选**的实时接入，不是使用 Ghidra 的前提。手动与 headless 路径无需它。

```text
GhidraMCP 有两条路，都提供同一套 250+ 工具。选一条。

【A】Headless —— 不需要 GUI，推荐用于批量与自动化：

```bash
GH="<ghidra-root>"
JAR="$GH/Ghidra/Extensions/GhidraMCP/lib/GhidraMCP-<version>.jar"
CP=$(find "$GH" -name '*.jar' | tr '\n' ':')

java -Djava.system.class.loader=ghidra.GhidraClassLoader \
     -cp "$CP$JAR" ghidra.Ghidra \
     com.xebyte.headless.GhidraMCPHeadlessServer \
     --port 8089 --file /path/to/binary --project /path/to/project-dir
```

参数：`--port`（默认 8089）、`--bind`（默认 127.0.0.1）、`--file`、
`--project`、`--program`。绑定地址可用环境变量 `GHIDRA_MCP_BIND_ADDRESS` 覆盖。

先探测再使用，禁止猜端口：

```bash
curl -s http://127.0.0.1:8089/health
# {"status":"healthy","program_loaded":true,"program_name":"..."}
```

仅监听回环。此传输是 **REST，不是 MCP**：端点是路径形式，
如 `/decompile_function?address=0x...`、`/list_methods`、`/list_segments`、
`/analyze_call_graph`。注意 `decompile_function` 用 `address=` 参数，
不是 `name=`。要注册进 MCP 客户端，需要一个把 MCP 调用翻译成这些路径的包装层。

【B】GUI 插件 —— 原生说 MCP，可被 MCP 客户端直接注册：

安装扩展 → 打开程序 → 从 GhidraMCP 面板启动服务器。
必须有程序打开，否则每个请求返回 `404 No context found for request`——
这条消息的意思是「没有载入任何程序」，不是「路径错了」。

### 无 GUI 的批量反编译（不经过 MCP）

`analyzeHeadless` 走的是另一条路：不加载插件，不提供上面这些端点，
但可以在无 GUI 下跑任意 GhidraScript，适合成千上万个二进制。

```bash
"<ghidra-root>/support/analyzeHeadless"   /path/to/project ProjName   -import /path/to/binary   -scriptPath /path/to/scripts   -postScript YourScript.java
```
```

装好后 MCP 提供 `list_methods` / `decompile_function` / `list_xrefs` 等实时工具，
适合交互式追问；批量场景仍走 `analyzeHeadless`（第 3 节），两者不冲突。

## 工具链

| 工具 | 用途 | 自举 |
|------|------|------|
| Ghidra | 反编译主工具 | 手动 release / 包管理器 |
| ghidra-mcp | AI 桥 | bootstrap 能力名 `ghidra-mcp` |
| ghidriff | 补丁差分 | 见 `patch-diff-exploit` |

## 参考

- `references/ghidra-cheatsheet.md`
- `../ida-reverse/` `../radare2/` `../binary-diff/`

## 路由上下文

**上游**: MASTER R22  
**下游**: 动态验证 → Frida/GDB；利用 → `pwn-chain`  
**同级**: `ida-reverse`（商业深挖）

## 任务完成自检

- [ ] 是否基于真实 Ghidra/tool-index 路径？
- [ ] 是否标注函数地址与重命名？
- [ ] 是否有可复现步骤？
- [ ] Checklist / journal？