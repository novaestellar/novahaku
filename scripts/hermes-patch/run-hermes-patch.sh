#!/usr/bin/env bash
# run-hermes-patch.sh — ./run-hermes-patch.sh /path/to/hermes/app check|apply|verify|restore
set -euo pipefail
ROOT="${1:?usage: run-hermes-patch.sh <hermes-root> <check|apply|verify|restore>}"
ACTION="${2:?usage: run-hermes-patch.sh <hermes-root> <check|apply|verify|restore>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python}" "$HERE/hermes_patch.py" --root "$ROOT" "--$ACTION"
