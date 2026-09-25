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

所有脚本以自身所在位置为基准解析相对路径，代码中不含硬编码的绝对路径。
仅当安装布局不同才需要覆盖 —— 写入 `.env`，不要修改脚本本身。

```bash
# novahaku 技能根目录（留空 = 从脚本位置自动探测）
NOVAHAKU_HOME=/path/to/novahaku

# Windows 测试套件使用的 Python 解释器（留空 = PATH 中的 "python"）
NOVAHAKU_PYTHON=python

# 交战（engagement）工作目录（留空 = <skill_root>/engagements）
# 由 engagement.py、engage_runner.py 和 findings_gen.py 读取
NOVAHAKU_ENGAGEMENT_DIR=/path/to/engagements
```

`scripts/test/novahaku_test_all.ps1` 遵循相同顺序：
`NOVAHAKU_HOME` → 脚本位置。其中不内嵌任何本机路径。

## MCP Server Setup

Novahaku works without any MCP server — every skill runs from its own scripts.
MCP servers add live tool access for a few specialised workflows. All of them
listen on **loopback only**; none should be exposed to a network.

Each server below is independent. Install only the ones you need.

### Overview

| Server | Default endpoint | Transport | Required by |
|--------|------------------|-----------|-------------|
| BurpSuite MCP | `:9876` | local bridge (stdio) | `testing/frameworks/burpsuite-mcp/` |
| Anything Analyzer MCP | `http://localhost:23816/mcp` | remote HTTP | `testing/frameworks/anything-analyzer-mcp/` |
| Binary Ninja MCP | `http://127.0.0.1:24642/mcp` | remote HTTP | `testing/binary-ninja-reverse/` |
| IDA Pro MCP | `http://127.0.0.1:13337/mcp` | remote HTTP | `testing/ida-reverse/` |
| GhidraMCP | wrapper-managed, default `:8089` | stdio bridge over local REST | `testing/ghidra-reverse/` |

### BurpSuite MCP

1. Install Burp Suite with the MCP extension
2. The MCP server listens on port 9876
3. Point your MCP client at the bundled bridge (`mcp-bridge.js`)
4. To move the port, edit `servicePort` for `burpsuite-mcp` in
   `scripts/reverse-skill/bootstrap-manifest.json`
5. See `testing/frameworks/burpsuite-mcp/SKILL.md`

### Anything Analyzer MCP

1. Start the Anything Analyzer server; it serves MCP on `localhost:23816`
2. If the server requires auth, copy the bearer token into
   `ANYTHING_ANALYZER_MCP_TOKEN` in `.env` — `bootstrap-reverse.ps1` reads it
   when wiring the client config
3. See `testing/frameworks/anything-analyzer-mcp/SKILL.md`

### Binary Ninja MCP

1. Install the Binary Ninja MCP plugin and open a target in Binary Ninja
2. The plugin serves MCP natively on `http://127.0.0.1:24642/mcp`
3. No npm bridge and no separate port are involved
4. See `testing/binary-ninja-reverse/SKILL.md`

### IDA Pro MCP

Two transports are available. Pick one; do not register both against the same
port, or the tools will be registered twice.

**GUI plugin (works from IDA 8.3 up, including 9.0):**

1. `pip install ida-pro-mcp` (installs the client and the IDA plugin)
2. Run `ida-pro-mcp --install` to place the plugin in the IDA user plugin dir
3. **Restart IDA**, then open a database
4. Open `Edit → Plugins → MCP` (or press `Ctrl-Alt-M`) to start the server
5. The server listens on `http://127.0.0.1:13337/mcp`
6. Set `IDA_HOME` in `.env` so the launcher scripts find your install

**Headless idalib server (requires IDA 9.1 or newer):**

1. Activate idalib for your IDA install:
   `python <IDA_HOME>/idalib/python/py-activate-idalib.py -d <IDA_HOME>`
2. Run the supervisor: `python -m ida_pro_mcp.idalib_supervisor`
3. It serves MCP on `http://127.0.0.1:8745/mcp`
4. Open binaries with `idb_open(path)` afterwards

> **Version note.** The headless server calls `enable_console_messages` and
> other functions that first appear in the **9.1** `idalib` library. On IDA 9.0
> the library exports only `init_library`, `open_database` and `close_database`,
> so the worker exits immediately. Use the GUI plugin on 9.0, or upgrade.
>
> On Windows, `py-activate-idalib.py` creates a symbolic link and needs either
> Developer Mode or an elevated shell. If it fails with `WinError 1314`, create
> a junction instead:
> `cmd /c mklink /J "<site-packages>\ida\bin" "<IDA_HOME>"`

### GhidraMCP

GhidraMCP serves the same 250+ analysis tools two ways. Pick one.

**Bridged headless server (recommended, no GUI required).** `ghidramcp_bridge.py`
starts the headless server on demand and republishes every endpoint as an MCP
tool. Because the server is REST and not MCP, a bridge is required; this one
reads the server's own `/mcp/schema` rather than hardcoding a tool list, so a
plugin upgrade adds tools with no edit here.

Register it once:

```bash
hermes mcp add ghidra-mcp \
  --command python \
  --env GHIDRA_HOME=/opt/ghidra_12.1.2_PUBLIC \
  --args /path/to/novahaku/scripts/reverse-skill/ghidramcp_bridge.py
```

Then, from a new session:

```
ghidra_status()                          # is it up, what is loaded
ghidra_open(binary="/path/to/target")    # boots the server, loads, analyses
ghidra_decompile_function(address="0x140001870")
ghidra_call("/list_segments")            # any endpoint not registered by name
```

The server starts lazily on the first call, so a session that never touches
Ghidra pays nothing. A cold boot takes roughly 7-10 s for a small PE.

Environment: `GHIDRA_HOME` (required for autostart), `GHIDRA_MCP_PORT`
(preferred port; a free one is chosen when busy, because `:8089` is shared with
the GUI plugin), `GHIDRA_MCP_AUTOSTART=0` to forbid launching, `GHIDRA_MCP_PROJECT`
(project directory, default under the temp dir), `GHIDRA_MCP_BOOT_TIMEOUT`.

**Starting the server by hand** — useful when debugging the bridge itself:

```bash
GH="<ghidra-root>"                      # e.g. /opt/ghidra_12.1.2_PUBLIC
JAR="$GH/Ghidra/Extensions/GhidraMCP/lib/GhidraMCP-<version>.jar"
CP=$(find "$GH" -name '*.jar' | tr '\n' ':')

java -Djava.system.class.loader=ghidra.GhidraClassLoader \
     -cp "$CP$JAR" ghidra.Ghidra \
     com.xebyte.headless.GhidraMCPHeadlessServer \
     --port 8089 --file /path/to/binary \
     --project /path/to/project-dir
```

Options: `--port` (default 8089), `--bind` (default 127.0.0.1), `--file`,
`--project`, `--program`. Set `GHIDRA_MCP_BIND_ADDRESS` to override the bind
address.

The `--project` directory must already exist. On a missing directory the server
still starts and logs `ERROR No .gpr file found in: <dir>`, then creates a
temporary project in memory — the program loads and the endpoints work, but
nothing persists after exit. Create the directory first; the error is a warning
about persistence, not a startup failure. Confirm it came up:

```bash
curl -s http://127.0.0.1:8089/health
# {"status":"healthy","program_loaded":true,"program_name":"..."}
```

Useful endpoints: `/mcp/schema` (full tool + parameter metadata, the bridge's
input), `/health`, `/server/status`, `/load_program`, `/decompile_function?address=0x...`,
`/list_methods`, `/list_segments`, `/list_imports`, `/analyze_call_graph`.

**GUI plugin (talks MCP natively).** Install the extension, open a program, then
start the server from the GhidraMCP panel. It binds an MCP endpoint that an MCP
client can register directly. A program must be open, or every request returns
`404 No context found for request` — that message means "nothing loaded", not
"wrong path".

> **Port sharing.** The GUI plugin and the headless server both default to
> `:8089`. Whichever starts first holds it, and the other fails to bind. That is
> why the bridge picks a free port instead of a fixed one — a hardcoded URL would
> point at the GUI, or at nothing, depending on what the operator did last.
>
> `:8080` is not Ghidra. That port belongs to the Burp proxy listener.

Either way the server is loopback-only. Do not expose it to a network.

## Persistent Engagement (cross-session state)

无需额外安装 —— 仅使用标准库，无外部依赖。

```bash
# 为目标创建交战（engagement）
python scripts/engagement.py init target.com --scope "*.target.com"

# 随时查看状态（包括新会话之后）
python scripts/engagement.py status target.com
python scripts/engagement.py list

# 运行并行测试
python scripts/engage_runner.py race      --target target.com --url https://target.com
python scripts/engage_runner.py integrity --target target.com
python scripts/engage_runner.py selftest
```

交战数据存放于 `engagements/<target>/` —— 每个目标的状态、证据、报告和侦察结果
永不提交。纳入追踪的只有 `engagements/TEMPLATE/`（布局文档）以及每个目标的
`state.json` + `findings/findings.csv`。忽略规则基于文件名而非整个目标目录，
这样新的交战仍可提交其文档（git 不会遍历被忽略的目录，因此其中的
`!re-include` 规则永远不会生效）。

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
