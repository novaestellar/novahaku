#!/usr/bin/env bash
# test-hermes-patch.sh — full-cycle test for hermes_patch.py on a DISPOSABLE COPY.
#
# Usage: bash test-hermes-patch.sh /path/to/hermes-agent/app
#
# Never touches the live install: all mutation happens in a temp dir seeded from the
# source you pass in. Exits non-zero on the first failed assertion.

set -uo pipefail

SRC="${1:?usage: test-hermes-patch.sh /path/to/hermes-agent/app}"
SRC="${SRC%/}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Same MSYS-vs-native problem as WORK below: `pwd` yields /d/Labs/... which native python
# cannot open. Convert and force forward slashes.
if command -v cygpath >/dev/null 2>&1; then
  HERE="$(cygpath -w "$HERE" | sed 's|\\|/|g')"
fi
TOOL="$HERE/hermes_patch.py"
WORK="$(mktemp -d)"
# git-bash hands back an MSYS path (/tmp/...) which native python cannot read, so convert
# to a native path. Then force forward slashes: bash path concatenation with backslashes
# ("$T/tools" -> "C:\a\tree/tools") makes mkdir/cp fail, while python reads both forms.
if command -v cygpath >/dev/null 2>&1; then
  WORK="$(cygpath -w "$WORK" | sed 's|\\|/|g')"
fi
T="$WORK/tree"

FILES=(
  "tools/memory_tool_store.py"
  "cron/scheduler_prompt.py"
  "tools/cronjob_tools.py"
  "gateway/platforms/api_server.py"
)

pass=0
fail=0

ok()   { printf '  PASS  %s\n' "$1"; pass=$((pass + 1)); }
bad()  { printf '  FAIL  %s\n' "$1"; fail=$((fail + 1)); }
head_() { printf '\n== %s ==\n' "$1"; }

# threat_patterns.py is the probe file resolve_root() uses to recognise a Hermes tree,
# so the copy must contain it even though the patch does not touch it.
seed() {
  rm -rf "$T"
  mkdir -p "$T/tools"
  cp "$SRC/tools/threat_patterns.py" "$T/tools/threat_patterns.py"
  # verify() also reports on skills_guard.py (as "untouched"), and the file must exist
  # for that line to print at all. The patch does not modify it.
  [ -f "$SRC/tools/skills_guard.py" ] && cp "$SRC/tools/skills_guard.py" "$T/tools/skills_guard.py"
  for f in "${FILES[@]}"; do
    mkdir -p "$T/$(dirname "$f")"
    cp "$SRC/$f" "$T/$f"
  done
  rm -rf "$T/.novahaku-patch-backup"
}

# Run the tool with cwd inside a native-path-safe dir. $T is already a Windows path.
run() { python "$TOOL" --root "$T" "$@"; }

cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

if [ ! -f "$SRC/tools/threat_patterns.py" ]; then
  echo "ERROR: $SRC is not a Hermes Agent source tree (no tools/threat_patterns.py)" >&2
  exit 2
fi

printf 'Hermes source: %s\nwork dir:      %s\n' "$SRC" "$WORK"

# ---------------------------------------------------------------- 1. check clean
head_ "check on a clean tree"
seed
run --check >/dev/null 2>&1
[ $? -eq 0 ] && ok "clean tree exits 0" || bad "clean tree should exit 0"

# ---------------------------------------------------------------- 2. apply
head_ "apply"
seed
out="$(run --apply 2>&1)"
rc=$?
[ $rc -eq 0 ] && ok "apply exits 0" || bad "apply exited $rc"
echo "$out" | grep -q "4 file(s) written" && ok "4 files written" || bad "expected 4 files written"
echo "$out" | grep -q "DEFUSED" && ok "auto-verify ran and passed" || bad "auto-verify did not pass"
if echo "$out" | grep -q "skills_guard"; then
  echo "$out" | grep -q "untouched (intended)" \
    && ok "skills_guard untouched" \
    || bad "skills_guard reported something other than untouched"
else
  bad "skills_guard line absent from verify output"
fi

markers=0
for f in "${FILES[@]}"; do
  n=$(grep -c "novahaku-patch" "$T/$f" 2>/dev/null | head -1)
  n=${n:-0}
  [ "$n" -gt 0 ] 2>/dev/null && markers=$((markers + 1))
done
[ "$markers" -eq 4 ] && ok "marker present in all 4 files" || bad "marker in $markers/4 files"

# ---------------------------------------------------------------- 3. idempotency
head_ "idempotency"
h1="$(cd "$T" && sha256sum "${FILES[@]}" | sha256sum)"
out="$(run --apply 2>&1)"
h2="$(cd "$T" && sha256sum "${FILES[@]}" | sha256sum)"
[ "$h1" = "$h2" ] && ok "second apply changed nothing" || bad "second apply mutated files"
echo "$out" | grep -q "0 file(s) written" && ok "second apply reports 0 written" || bad "expected 0 written"

# ---------------------------------------------------------------- 4. verify
head_ "verify"
seed >/dev/null
run --apply >/dev/null 2>&1
out="$(run --verify 2>&1)"
rc=$?
[ $rc -eq 0 ] && ok "verify exits 0 on patched tree" || bad "verify exited $rc"
echo "$out" | grep -q "memory write + load scan *: DEFUSED" && ok "memory scan defused" || bad "memory scan not defused"
echo "$out" | grep -q "cron prompt scan *: DEFUSED" && ok "cron prompt scan defused" || bad "cron prompt scan not defused"

# ---------------------------------------------------------------- 5. anchor drift
head_ "anchor drift is fail-closed"
seed >/dev/null
python - "$T" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "tools/cronjob_tools.py"
s = p.read_text(encoding="utf-8")
p.write_text(s.replace("scan_error = _scan_cron_prompt(extra_prompt)",
                       "scan_error = RENAMED(extra_prompt)"), encoding="utf-8")
PY
before="$(cd "$T" && sha256sum "${FILES[@]}" | sha256sum)"
out="$(run --apply 2>&1)"
rc=$?
after="$(cd "$T" && sha256sum "${FILES[@]}" | sha256sum)"
[ $rc -ne 0 ] && ok "apply fails on drifted anchor" || bad "apply should fail on drifted anchor"
[ "$before" = "$after" ] && ok "zero files written on drift" || bad "drift wrote files"
[ ! -d "$T/.novahaku-patch-backup" ] && ok "no manifest written on drift" || bad "manifest written despite drift"

# ---------------------------------------------------------------- 6. missing backup
head_ "missing backup is fail-closed"
seed >/dev/null
run --apply >/dev/null 2>&1
rm -f "$T/.novahaku-patch-backup/${FILES[3]}"
before="$(cd "$T" && sha256sum "${FILES[@]}" | sha256sum)"
out="$(run --restore 2>&1)"
rc=$?
after="$(cd "$T" && sha256sum "${FILES[@]}" | sha256sum)"
[ $rc -ne 0 ] && ok "restore fails on missing backup" || bad "restore should fail"
[ "$before" = "$after" ] && ok "zero files overwritten before abort" || bad "partial restore occurred"

# ---------------------------------------------------------------- 7. restore identity
head_ "restore is byte-identical"
seed >/dev/null
run --apply >/dev/null 2>&1
run --restore >/dev/null 2>&1
n=0
for f in "${FILES[@]}"; do
  diff -q "$SRC/$f" "$T/$f" >/dev/null 2>&1 && n=$((n + 1))
done
[ "$n" -eq 4 ] && ok "all 4 files byte-identical to source" || bad "$n/4 files identical"

# ---------------------------------------------------------------- 8. invalid root
head_ "invalid root is refused"
python "$TOOL" --root "$WORK/does-not-exist" --check >/dev/null 2>&1
[ $? -eq 2 ] && ok "invalid root exits 2" || bad "invalid root should exit 2"

# ---------------------------------------------------------------- 9. check exit code
head_ "check exit code on a broken tree"
seed >/dev/null
rm -f "$T/gateway/platforms/api_server.py"
run --check >/dev/null 2>&1
[ $? -eq 1 ] && ok "missing file makes check exit 1" || bad "check should exit 1 on missing file"

# ---------------------------------------------------------------- 10. stray marker (oracle D1/D2)
head_ "stray marker with a live scanner is refused"
seed >/dev/null
python - "$T" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "tools/memory_tool_store.py"
s = p.read_text(encoding="utf-8")
# comment-only marker: syntax stays valid, the scanner stays LIVE, no anchors applied
p.write_text(s.replace("class MemoryStore", "# [novahaku-patch]\nclass MemoryStore", 1),
             encoding="utf-8")
PY
out="$(run --apply 2>&1)"
rc=$?
[ $rc -ne 0 ] && ok "apply refuses a stray-marker file" || bad "apply accepted a stray marker (exit 0)"
echo "$out" | grep -q "still wired" && ok "names the still-wired call sites" || bad "no still-wired diagnostic"
echo "$out" | grep -q "already patched" && bad "silently skipped instead of failing" || ok "does not silently skip"

# ---------------------------------------------------------------- 11. read-only file (oracle D3)
head_ "read-only target rolls back instead of crashing"
seed >/dev/null
python - "$T" <<'PY'
import sys, os, stat, pathlib
p = pathlib.Path(sys.argv[1]) / "tools/cronjob_tools.py"
os.chmod(p, stat.S_IREAD)
PY
out="$(run --apply 2>&1)"
rc=$?
[ $rc -ne 0 ] && ok "apply exits non-zero on unwritable target" || bad "apply should fail on read-only file"
echo "$out" | grep -q "Traceback" && bad "traceback escaped instead of a clean FAIL" || ok "no traceback escaped"
echo "$out" | grep -q "Rolled back" && ok "reports the automatic rollback" || bad "no rollback reported"
n=0
for f in "${FILES[@]}"; do
  grep -q "novahaku-patch" "$T/$f" 2>/dev/null || n=$((n + 1))
done
[ "$n" -eq 4 ] && ok "all 4 files clean after rollback" || bad "$n/4 files clean after rollback"
python - "$T" <<'PY'
import sys, os, stat, pathlib
p = pathlib.Path(sys.argv[1]) / "tools/cronjob_tools.py"
os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
PY

# ---------------------------------------------------------------- 12. re-armed guard (oracle D4)
head_ "a re-armed scan guard is detected"
seed >/dev/null
run --apply >/dev/null 2>&1
python - "$T" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "tools/memory_tool_store.py"
s = p.read_text(encoding="utf-8")
old = "        if False:  # [novahaku-patch]\n            scan_error = \"\".join([])"
new = "        if _FLAG():  # [novahaku-patch]\n            scan_error = _scan_memory_content(content)"
p.write_text(s.replace(old, new, 1), encoding="utf-8")
PY
out="$(run --verify 2>&1)"
rc=$?
[ $rc -ne 0 ] && ok "verify fails on a re-armed guard" || bad "verify passed a re-armed guard"
echo "$out" | grep -q "STILL WIRED" && ok "reports STILL WIRED" || bad "did not report STILL WIRED"

# ---------------------------------------------------------------- 13. verify covers all 4
head_ "verify covers every patched file"
seed >/dev/null
run --apply >/dev/null 2>&1
out="$(run --verify 2>&1)"
n=0
for label in "memory write" "cron prompt scan" "cron skill-assembled scan" "cron scan via API server"; do
  echo "$out" | grep -q "$label" && n=$((n + 1))
done
[ "$n" -eq 4 ] && ok "all 4 targets verified" || bad "only $n/4 targets verified"

# ---------------------------------------------------------------- 14. live untouched
head_ "live install untouched"
n=0
for f in "${FILES[@]}"; do
  grep -q "novahaku-patch" "$SRC/$f" 2>/dev/null || n=$((n + 1))
done
[ "$n" -eq 4 ] && ok "source tree has no patch markers" || bad "SOURCE TREE IS PATCHED — restore it"
[ ! -d "$SRC/.novahaku-patch-backup" ] && ok "no backup dir in source tree" || bad "backup dir present in source tree"

# ---------------------------------------------------------------- summary
printf '\n----------------------------------------\n'
printf 'passed: %d   failed: %d\n' "$pass" "$fail"
[ "$fail" -eq 0 ] && { echo "ALL PASS"; exit 0; }
echo "FAILURES PRESENT"
exit 1
