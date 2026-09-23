#!/usr/bin/env bash
# Self-check for the domain-argument guard on all three entry points.
# Usage: bash test_domain_guard.sh      (no network, no writes outside a temp HOME)
# Asserts on the guard's own error string, not merely a non-zero exit, so a script
# that dies for some unrelated reason cannot make this pass vacuously.
set -uo pipefail
# pwd -W yields a native path (D:/...) on MSYS/Git-Bash. Plain `pwd` yields
# /d/... which a native python.exe cannot open, and the .py cases then fail with
# "can't open file" - which reads as the guard being broken rather than the path
# being wrong. -W is MSYS-only, so fall back to pwd elsewhere.
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && { pwd -W 2>/dev/null || pwd; })"
SANDBOX="$(mktemp -d)"; trap 'rm -rf "$SANDBOX"' EXIT
fail=0

BAD=('..' '.' '../../tmp/pwned' '-rf' '--help' 'a b' 'example.com;id' 'nodot' 'example..com' '-example.com' 'example.com.')
for s in "$S/recon_pipeline.sh" "$S/findings_gen.py" "$S/build_xlsx.py"; do
  # PYTHON first, then python3, then python: Windows has no python3 on PATH and
  # the Store app-alias stub answers instead, which failed every .py case with
  # "Python was not found" and looked like the guard was broken.
  runner=bash
  [[ "$s" == *.py ]] && runner=${PYTHON:-$(command -v python3 || command -v python)}
  for d in "${BAD[@]}"; do
    out=$(HOME="$SANDBOX" "$runner" "$s" "$d" 2>&1)
    case "$out" in
      *"invalid domain"*) ;;
      *) echo "FAIL: $(basename "$s") did not reject '$d' (got: ${out:-<no output>})"; fail=1;;
    esac
  done
done
# A rejected input must not have created anything.
found=$(find "$SANDBOX" -mindepth 1 2>/dev/null)
[ -z "$found" ] || { echo "FAIL: rejected input still wrote: $found"; fail=1; }

# A real domain must still pass the guard (python entry points only — the shell one starts a live run).
for s in "$S/findings_gen.py" "$S/build_xlsx.py"; do
  out=$(HOME="$SANDBOX" ${PYTHON:-python3} "$s" sub.example.com 2>&1)
  case "$out" in *"invalid domain"*) echo "FAIL: $(basename "$s") rejected sub.example.com"; fail=1;; esac
done

[ $fail -eq 0 ] && echo "PASS: domain guard holds on all three entry points"
exit $fail
