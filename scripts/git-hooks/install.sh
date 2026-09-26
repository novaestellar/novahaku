#!/usr/bin/env bash
# install.sh — put the repository gates in front of `git commit`.
#
# git deliberately never ships `.git/hooks/` with a clone: a hook is code that
# runs on your machine, so it must be installed deliberately. This script is
# that deliberate step, and it is idempotent — run it any time.
#
# Usage:
#     bash scripts/git-hooks/install.sh            # install / refresh
#     bash scripts/git-hooks/install.sh --check    # report state, change nothing
#     bash scripts/git-hooks/install.sh --remove   # uninstall
#
# Exits 0 when the hook is in place, 1 otherwise.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$HERE/pre-commit"

MODE="install"
case "${1:-}" in
  --check)  MODE="check" ;;
  --remove) MODE="remove" ;;
  ""|--install) MODE="install" ;;
  *) echo "install.sh: unknown option: $1" >&2; exit 2 ;;
esac

if [[ ! -f "$SOURCE" ]]; then
  echo "install.sh: missing $SOURCE" >&2
  exit 1
fi

# Target the repository this script lives in, not the caller's cwd: someone
# may install from anywhere.
#
# `$HERE` is an MSYS path (/d/labs/repo/scripts/git-hooks) under Git Bash, and
# git.exe is a native Windows binary that cannot chdir to it — `git -C /d/...`
# dies with "cannot change to '/d/labs/...'". Convert to a Windows path first
# when cygpath is available; it is a no-op on Linux/macOS where the command is
# absent and `$HERE` is already a native path.
HERE_NATIVE="$HERE"
if command -v cygpath >/dev/null 2>&1; then
  HERE_NATIVE="$(cygpath -w "$HERE")"
fi
REPO_ROOT="$(git -C "$HERE_NATIVE" rev-parse --show-toplevel 2>/dev/null)" || {
  # Converted path can still fail if cygpath is missing; retry with the raw
  # path so a POSIX-only host is never regressed by the Windows fix.
  REPO_ROOT="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "install.sh: not inside a git repository (looked from $HERE)" >&2
    exit 1
  }
}
TARGET="$REPO_ROOT/.git/hooks/pre-commit"

echo "repository : $REPO_ROOT"
echo "hook path  : $TARGET"

installed() {
  [[ -f "$TARGET" ]] || return 1
  # Compare contents, not just existence: a stale hook from an older version is
  # worse than none, because it looks installed while checking the wrong things.
  cmp -s "$SOURCE" "$TARGET"
}

case "$MODE" in
  check)
    if installed; then
      echo "state      : installed and current"
      exit 0
    elif [[ -f "$TARGET" ]]; then
      echo "state      : STALE — differs from $SOURCE"
      echo "             run: bash scripts/git-hooks/install.sh"
      exit 1
    else
      echo "state      : NOT INSTALLED"
      echo "             run: bash scripts/git-hooks/install.sh"
      exit 1
    fi
    ;;

  remove)
    if [[ -f "$TARGET" ]]; then
      rm -f "$TARGET"
      echo "state      : removed"
    else
      echo "state      : nothing to remove"
    fi
    exit 0
    ;;

  install)
    if [[ ! -d "$REPO_ROOT/.git/hooks" ]]; then
      mkdir -p "$REPO_ROOT/.git/hooks"
    fi
    if [[ -f "$TARGET" ]] && ! cmp -s "$SOURCE" "$TARGET"; then
      # Keep one backup so a hand-edited hook is recoverable, then refresh.
      cp "$TARGET" "$TARGET.bak-$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
      echo "note       : existing hook differed; backup written next to it"
    fi
    cp "$SOURCE" "$TARGET"
    chmod +x "$TARGET" 2>/dev/null || true
    if installed; then
      echo "state      : installed"
      echo "verify     : bash scripts/git-hooks/install.sh --check"
    else
      echo "install.sh: copy did not land as expected" >&2
      exit 1
    fi
    exit 0
    ;;
esac
