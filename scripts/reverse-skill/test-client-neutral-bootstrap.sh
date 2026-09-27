#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP="$SCRIPT_DIR/bootstrap-reverse.sh"
REFRESH="$SCRIPT_DIR/refresh-tool-index.sh"
SCRATCH="$(mktemp -d /tmp/reverse-client-neutral-XXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT

# On Windows (Git Bash/MSYS) python3 is the MS Store stub; resolve a real
# interpreter, and convert its path (and every file argument below) to
# Windows form — MSYS argv conversion is disabled in this shell, so native
# Python would otherwise receive literal /d/labs/... paths and resolve them
# against the current drive root.
REAL_PYTHON=""
for cand in python python3 py; do
  if command -v "$cand" >/dev/null 2>&1 && \
     "$cand" -c 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)' \
       >/dev/null 2>&1; then
    REAL_PYTHON="$(command -v "$cand")"
    break
  fi
done
: "${REAL_PYTHON:?no Python 3 interpreter found on PATH}"
if command -v cygpath >/dev/null 2>&1; then
  REAL_PYTHON="$(cygpath -w "$REAL_PYTHON")"
fi
wpath() { command -v cygpath >/dev/null 2>&1 && cygpath -w "$1" 2>/dev/null || printf '%s' "$1"; }

HOME_DIR="$SCRATCH/home"
BIN_DIR="$SCRATCH/bin"
TOOLS_DIR="$SCRATCH/tools"
CLAUDE_CFG="$SCRATCH/client/claude.json"
CODEX_CFG="$SCRATCH/client/codex.toml"
mkdir -p "$HOME_DIR" "$BIN_DIR" "$TOOLS_DIR" "$(dirname "$CLAUDE_CFG")"

for name in node npm npx; do
  cat > "$BIN_DIR/$name" <<'STUB'
#!/usr/bin/env bash
if [[ "${1:-}" == "--version" ]]; then echo 1.0.0; fi
exit 0
STUB
  chmod +x "$BIN_DIR/$name"
done

export PATH="$BIN_DIR:$PATH"
export HOME="$HOME_DIR"
export REVERSE_SKILL_TOOLS_DIR="$TOOLS_DIR"
export CLAUDE_MCP_CONFIG="$CLAUDE_CFG"
export CODEX_CONFIG_PATH="$CODEX_CFG"

MD="$SCRATCH/tool-index.md"
JSON="$SCRATCH/tool-index.json"
bash "$REFRESH" "$MD" "$JSON" >/dev/null

"$REAL_PYTHON" - "$(wpath "$JSON")" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding='utf-8'))
tools = data['tools']
assert sum(t['name'] == 'binwalk' for t in tools) == 1, 'binwalk must appear exactly once'
by_tool = {t['name']: t for t in tools}
assert by_tool['npx']['available'] is True
assert by_tool['jshookmcp']['available'] is False, 'npx must not masquerade as jshookmcp'
assert by_tool['reqable-mcp']['available'] is False, 'npx must not masquerade as reqable-mcp'
by_cap = {c['name']: c for c in data['capabilities']}
assert by_cap['jshookmcp']['ready'] is False
assert by_cap['reqable-mcp']['ready'] is False
PY

cat > "$CODEX_CFG" <<'EOF'
[mcp_servers.jshook]
command = "npx"
args = ["-y", "@jshookmcp/jshook@0.3.4"]
EOF
bash "$REFRESH" "$MD" "$JSON" >/dev/null
"$REAL_PYTHON" - "$(wpath "$JSON")" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding='utf-8'))
cap = {c['name']: c for c in data['capabilities']}['jshookmcp']
assert cap['mcp_registered'] is True, 'Codex-only MCP registration must be discovered'
assert cap['runtime_available'] is True
assert cap['ready'] is True, 'registered npm MCP + npx runtime should be ready'
PY

rm -f "$CLAUDE_CFG" "$CODEX_CFG"
default_out="$(bash "$BOOTSTRAP" jshookmcp --skip-refresh)"
[[ "$default_out" == *'"status":"registration-required"'* || "$default_out" == *'"status": "registration-required"'* ]]
[[ ! -e "$CLAUDE_CFG" ]]
[[ ! -e "$CODEX_CFG" ]]

codex_out="$(bash "$BOOTSTRAP" jshookmcp --skip-refresh --mcp-host=codex)"
[[ "$codex_out" == *'"status":"ready"'* || "$codex_out" == *'"status": "ready"'* ]]
[[ ! -e "$CLAUDE_CFG" ]]
grep -Eq '^\[mcp_servers\.jshook\]$' "$CODEX_CFG"

rm -f "$CLAUDE_CFG" "$CODEX_CFG"
claude_out="$(bash "$BOOTSTRAP" jshookmcp --skip-refresh --mcp-host=claude)"
[[ "$claude_out" == *'"status":"ready"'* || "$claude_out" == *'"status": "ready"'* ]]
[[ -f "$CLAUDE_CFG" ]]
[[ ! -e "$CODEX_CFG" ]]
"$REAL_PYTHON" - "$(wpath "$CLAUDE_CFG")" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding='utf-8'))
assert 'jshook' in data.get('mcpServers', {})
PY

echo 'client-neutral Bash bootstrap/discovery regression passed'
