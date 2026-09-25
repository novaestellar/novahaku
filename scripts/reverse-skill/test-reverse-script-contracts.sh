#!/usr/bin/env bash
# test-reverse-script-contracts.sh — smoke + unit checks for the reverse-skill
# scripts and the per-skill launchers.
#
# Catches the failure class where a script or manifest entry points at a path,
# capability, or bootstrap hook that does not exist. Those failures are silent:
# nothing crashes, the feature simply never works.
#
# No external tool (jadx, apktool, adb, frida, IDA) is required. Argument
# parsing, path resolution, and bootstrap wiring are exercised directly.
#
# Usage: bash scripts/reverse-skill/test-reverse-script-contracts.sh
# Exit:  0 all pass, 1 any fail

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_ROOT/.." && pwd)"
MANIFEST="$SCRIPT_DIR/bootstrap-manifest.json"
TOOL_DISCOVERY="$SCRIPT_DIR/lib/ToolDiscovery.ps1"

PASS=0
FAIL=0

ok()   { PASS=$((PASS + 1)); printf '  [OK]   %s\n' "$1"; }
bad()  { FAIL=$((FAIL + 1)); printf '  [FAIL] %s\n' "$1"; }
check() { if [[ "$2" == "1" ]]; then ok "$1"; else bad "$1"; fi; }

echo "reverse-skill script contracts"
echo "repo=$REPO_ROOT"
echo

# ─── 1. bootstrap hook resolves to a real file ────────────────────────────────
echo "1. bootstrap hook wiring"

for f in testing/radare2/scripts/recon.sh \
         testing/apk-reverse/scripts/decode.sh \
         testing/apk-reverse/scripts/frida-run.sh \
         testing/apk-reverse/scripts/rebuild-sign-install.sh; do
  target="$REPO_ROOT/$f"
  if [[ ! -f "$target" ]]; then bad "$f missing"; continue; fi
  # A script must resolve its bootstrap sibling, never a phantom name.
  if grep -q 'Hermes auto-install' "$target"; then
    bad "$f still references the phantom 'Hermes auto-install'"
  else
    ok "$f has no phantom bootstrap reference"
  fi
  if grep -q 'KALI_BOOTSTRAP' "$target"; then
    bad "$f still defines KALI_BOOTSTRAP"
  else
    ok "$f has no KALI_BOOTSTRAP"
  fi
  # The bootstrap path it declares must exist.
  hook="$(grep -o 'bootstrap-reverse\.sh' "$target" | head -1)"
  check "$f resolves bootstrap-reverse.sh" "$([[ -n "$hook" && -f "$SCRIPT_DIR/bootstrap-reverse.sh" ]] && echo 1 || echo 0)"
done

for f in testing/radare2/scripts/recon.ps1 \
         testing/apk-reverse/scripts/decode.ps1 \
         testing/apk-reverse/scripts/frida-run.ps1 \
         testing/apk-reverse/scripts/rebuild-sign-install.ps1; do
  target="$REPO_ROOT/$f"
  if [[ ! -f "$target" ]]; then bad "$f missing"; continue; fi
  if grep -q 'Hermes auto-install' "$target"; then
    bad "$f still references the phantom 'Hermes auto-install'"
  else
    ok "$f has no phantom bootstrap reference"
  fi
  if grep -q 'bootstrap-reverse\.ps1' "$target"; then
    ok "$f points at bootstrap-reverse.ps1"
  else
    bad "$f does not point at bootstrap-reverse.ps1"
  fi
done

# ─── 2. manifest script paths resolve ────────────────────────────────────────
echo
echo "2. manifest script paths"

if [[ ! -f "$MANIFEST" ]]; then
  bad "bootstrap-manifest.json missing"
else
  ok "bootstrap-manifest.json present"
fi

# Every %REPO_ROOT% / %SKILL_ROOT% path in the manifest must exist.
while IFS= read -r entry; do
  [[ -z "$entry" ]] && continue
  var="${entry%%\\*}"
  rest="${entry#*\\}"
  case "$var" in
    '%REPO_ROOT%')   base="$REPO_ROOT" ;;
    '%SKILL_ROOT%')  base="$SKILL_ROOT" ;;
    *) continue ;;
  esac
  rel="${rest//\\//}"
  if [[ -e "$base/$rel" ]]; then
    ok "manifest path resolves: $entry"
  else
    bad "manifest path is dead: $entry"
  fi
done < <(grep -o '"\(startScript\|setupScript\)": "[^"]*"' "$MANIFEST" \
           | sed 's/.*: "//; s/"$//')

# ─── 3. capability coverage ──────────────────────────────────────────────────
echo
echo "3. capability coverage"

# Every capability a per-skill script bootstraps must exist in the manifest,
# otherwise bootstrap throws "No bootstrap definition for capability".
for cap in r2 rabin2 jadx apktool frida adb zipalign apksigner keytool; do
  if grep -q "\"name\": \"$cap\"" "$MANIFEST"; then
    ok "manifest declares capability: $cap"
  else
    bad "manifest is missing capability: $cap"
  fi
done

# The bash dispatcher must handle every capability it can be handed.
# A case arm may list several alternatives (`zipalign|apksigner)`), so match any
# arm whose alternative list contains the capability, not just the first slot.
for cap in zipalign apksigner keytool; do
  if grep -qE "^[[:space:]]*[a-z0-9_-]+(\|[a-z0-9_-]+)*\)[[:space:]]" "$SCRIPT_DIR/bootstrap-reverse.sh" \
     && grep -qE "^[[:space:]]*[a-z0-9_|-]*\b${cap}\b[a-z0-9_|-]*\)" "$SCRIPT_DIR/bootstrap-reverse.sh"; then
    ok "bootstrap-reverse.sh dispatches: $cap"
  else
    bad "bootstrap-reverse.sh cannot dispatch: $cap"
  fi
done

# ToolDiscovery must know the tools the apk/ida skills resolve.
for tool in apksigner zipalign keytool idat64; do
  if grep -q "Name = '$tool'" "$TOOL_DISCOVERY"; then
    ok "ToolDiscovery declares: $tool"
  else
    bad "ToolDiscovery is missing: $tool"
  fi
done

# ─── 4. argument parsing (no external tools needed) ──────────────────────────
echo
echo "4. argument parsing"

# recon.sh must reject a missing target and a missing file without side effects.
out="$(bash "$REPO_ROOT/testing/radare2/scripts/recon.sh" 2>&1)"; rc=$?
check "recon.sh exits non-zero with no target" "$([[ $rc -ne 0 ]] && echo 1 || echo 0)"
check "recon.sh prints usage when no target"    "$(grep -q '用法\|usage' <<<"$out" && echo 1 || echo 0)"

out="$(bash "$REPO_ROOT/testing/radare2/scripts/recon.sh" /nonexistent/binary 2>&1)"; rc=$?
check "recon.sh rejects a missing file" "$([[ $rc -ne 0 ]] && echo 1 || echo 0)"

# decode.sh must reject a missing APK.
out="$(bash "$REPO_ROOT/testing/apk-reverse/scripts/decode.sh" /nonexistent.apk 2>&1)"; rc=$?
check "decode.sh rejects a missing APK" "$([[ $rc -ne 0 ]] && echo 1 || echo 0)"

# rebuild-sign-install.sh must reject a missing project dir.
out="$(bash "$REPO_ROOT/testing/apk-reverse/scripts/rebuild-sign-install.sh" /nonexistent/dir 2>&1)"; rc=$?
check "rebuild-sign-install.sh rejects a missing project" "$([[ $rc -ne 0 ]] && echo 1 || echo 0)"

# start-idapro.sh must refuse to run without a target rather than launching blind.
out="$(bash "$SCRIPT_DIR/start-idapro.sh" --port 59999 --timeout 1 2>&1)"; rc=$?
check "start-idapro.sh requires a target" "$([[ $rc -ne 0 ]] && echo 1 || echo 0)"

# ─── 5. bash syntax across every shipped shell script ────────────────────────
echo
echo "5. shell syntax"

while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  if bash -n "$f" 2>/dev/null; then
    ok "syntax: ${f#"$REPO_ROOT"/}"
  else
    bad "syntax error: ${f#"$REPO_ROOT"/}"
  fi
done < <(find "$SCRIPT_DIR" "$REPO_ROOT/testing" "$REPO_ROOT/scripts/deploy" \
           -name '*.sh' -not -path '*/.git/*' 2>/dev/null | sort)

# ─── 6. no machine-specific absolute paths in shipped scripts ────────────────
echo
echo "6. portability"

# A hardcoded user profile or lab root in a shipped script is a machine leak.
# Exclude this test file itself: it has to name the pattern it forbids.
SELF="$(basename "${BASH_SOURCE[0]}")"
leaks=0
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  [[ "$(basename "$f")" == "$SELF" ]] && continue
  if grep -qE 'C:\\+Users\\+[A-Za-z]+|D:/Labs' "$f"; then
    bad "machine path leak in ${f#"$REPO_ROOT"/}"
    leaks=$((leaks + 1))
  fi
done < <(find "$SCRIPT_DIR" "$REPO_ROOT/testing" -type f \
           \( -name '*.sh' -o -name '*.ps1' -o -name '*.py' \) \
           -not -path '*/.git/*' -not -path '*__pycache__*' 2>/dev/null | sort)
check "no machine-specific paths in shipped scripts" "$([[ $leaks -eq 0 ]] && echo 1 || echo 0)"

# ─── summary ─────────────────────────────────────────────────────────────────
echo
echo "────────────────────────────────────────"
printf 'reverse-skill script contracts: %d passed, %d failed\n' "$PASS" "$FAIL"
[[ $FAIL -eq 0 ]] || exit 1
