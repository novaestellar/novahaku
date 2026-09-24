#!/usr/bin/env python
"""Selftest for hermes_patch.py — pure-logic checks, no Hermes tree touched.

Scope note: this verifies the *mechanism* (string matching, AST liveness, manifest
shape). It does NOT and cannot judge whether defusing the scanner is desirable —
that is a product decision, already taken. The module stays INACTIVE here.

Run:  python _selftest_hermes_patch.py
Exit: 0 all pass, 1 any fail.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("hermes_patch", HERE / "hermes_patch.py")
hp = importlib.util.module_from_spec(_spec)
sys.modules["hermes_patch"] = hp
_spec.loader.exec_module(hp)

checks: list[tuple[str, bool]] = []


def check(name: str, cond: bool) -> None:
    checks.append((name, bool(cond)))


# --- _patches(): structural contract -----------------------------------------
patches = hp._patches()

check("_patches returns a list", isinstance(patches, list) and len(patches) >= 3)
check(
    "every patch is (path, label, pairs)",
    all(
        isinstance(p, tuple)
        and len(p) == 3
        and isinstance(p[0], str)
        and isinstance(p[1], str)
        and isinstance(p[2], list)
        for p in patches
    ),
)
check(
    "every pair is a 2-tuple of str",
    all(
        isinstance(pair, tuple) and len(pair) == 2
        and all(isinstance(x, str) for x in pair)
        for _, _, pairs in patches
        for pair in pairs
    ),
)
check(
    "no empty old/new strings (empty old would match everywhere)",
    all(pair[0].strip() and pair[1].strip() for _, _, pairs in patches for pair in pairs),
)
check(
    "every replacement carries the MARKER",
    all(hp.MARKER in pair[1] for _, _, pairs in patches for pair in pairs),
)
check(
    "every replacement old->new actually differs",
    all(pair[0] != pair[1] for _, _, pairs in patches for pair in pairs),
)
check(
    "paths are relative, no traversal",
    all(not p[0].startswith(("/", "\\")) and ".." not in p[0] for p in patches),
)
check(
    "no duplicate target file",
    len({p[0] for p in patches}) == len(patches),
)
check(
    "each target has at least one pair",
    all(len(pairs) >= 1 for _, _, pairs in patches),
)

# The three files the module claims to cover — if a name drifts, verify() silently
# checks nothing. Pin them.
targets = {p[0] for p in patches}
check("targets memory_tool_store.py", "tools/memory_tool_store.py" in targets)
check("targets cron/scheduler_prompt.py", "cron/scheduler_prompt.py" in targets)
check("targets cronjob_tools.py", any("cronjob_tools" in t for t in targets))

# --- _live_call_lines(): AST liveness, both directions ------------------------
def live(src: str, func: str) -> list[int]:
    return hp._live_call_lines(ast.parse(src), func)


# live call -> detected
check("live bare call detected", live("scan(x)\n", "scan") == [1])
# if False: dead
check("call inside `if False:` is dead", live("if False:\n    scan(x)\n", "scan") == [])
# if 0: dead (any falsy constant, not just False)
check("call inside `if 0:` is dead", live("if 0:\n    scan(x)\n", "scan") == [])
# if True: live
check("call inside `if True:` is LIVE", live("if True:\n    scan(x)\n", "scan") == [2])
# False and f()
check("`False and scan(x)` is dead", live("y = False and scan(x)\n", "scan") == [])
# True and f() -> live
check("`True and scan(x)` is LIVE", live("y = True and scan(x)\n", "scan") == [1])
# attribute call by .attr
check("attribute-form call detected", live("obj.scan(x)\n", "scan") == [1])
# other function not reported
check("unrelated function not reported", live("other(x)\n", "scan") == [])
# mixed: one live, one dead -> only live line
mixed = "scan(a)\nif False:\n    scan(b)\nscan(c)\n"
check("mixed dead/live reports only live lines", live(mixed, "scan") == [1, 4])
# dedupe: same call twice on one line
check("duplicate line deduped", live("scan(a); scan(b)\n", "scan") == [1])

# the exact pattern the patch itself injects must read as dead
check(
    "injected guard pattern reads as dead",
    live('if False:  # [novahaku-patch]\n    scan_error = "".join([])\n', "scan") == [],
)
check(
    "injected `False and` pattern reads as dead",
    live("(False and scan(prompt))  # [novahaku-patch]\n", "scan") == [],
)

# --- resolve_root(): explicit is authoritative, auto never raises SystemExit -----
# resolve_root() with no explicit path is designed to SystemExit(2) when no Hermes
# tree exists (refusing to guess is the point). A selftest must survive that.
try:
    r = hp.resolve_root()
    check("resolve_root() returns Path or None", r is None or isinstance(r, Path))
except SystemExit as exc:
    check("resolve_root() SystemExit(2) when no tree found", exc.code == 2)
except Exception as exc:  # noqa: BLE001
    check(f"resolve_root() raised unexpected {type(exc).__name__}", False)

import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    try:
        r2 = hp.resolve_root(td)
        check("resolve_root(explicit) returns that Path", str(r2) == str(Path(td)))
    except Exception as exc:  # noqa: BLE001
        check(f"resolve_root(explicit) raised {type(exc).__name__}", False)

    # An explicit path that is NOT a Hermes tree must abort, never fall back.
    try:
        hp.resolve_root(str(Path(td) / "not-a-tree"))
        check("resolve_root(bogus explicit) aborts instead of falling back", False)
    except SystemExit as exc:
        check("resolve_root(bogus explicit) aborts instead of falling back", exc.code == 2)
    except Exception as exc:  # noqa: BLE001
        check(f"resolve_root(bogus) raised {type(exc).__name__}, want SystemExit", False)

    # manifest roundtrip, isolated in temp
    root = Path(td)
    try:
        mp = hp._manifest_path(root)
        check("_manifest_path is under root", str(mp).startswith(str(root)))
        hp._save_manifest(root, {"patched": ["a", "b"], "fingerprint": {"x": "y"}})
        loaded = hp._load_manifest(root)
        check("manifest roundtrips", loaded.get("patched") == ["a", "b"])
        check("manifest fingerprint preserved", loaded.get("fingerprint") == {"x": "y"})
        # missing manifest -> empty dict, not a crash
        hp._manifest_path(root).unlink(missing_ok=True)
        check("missing manifest yields dict", isinstance(hp._load_manifest(root), dict))
    except Exception as exc:  # noqa: BLE001
        check(f"manifest roundtrip raised {type(exc).__name__}: {exc}", False)

    # _sha on a real file and on a missing file
    try:
        f = root / "probe.txt"
        f.write_text("hello", encoding="utf-8")
        s1 = hp._sha(f)
        check("_sha returns 64-hex", isinstance(s1, str) and len(s1) == 64)
        f.write_text("hello2", encoding="utf-8")
        check("_sha changes with content", hp._sha(f) != s1)
        try:
            hp._sha(root / "nope.txt")
            check("_sha(missing) raises (caller relies on it)", False)
        except Exception:  # noqa: BLE001
            check("_sha(missing) raises (caller relies on it)", True)
    except Exception as exc:  # noqa: BLE001
        check(f"_sha raised {type(exc).__name__}: {exc}", False)


# --- report -------------------------------------------------------------------
fails = [n for n, ok in checks if not ok]
for name, ok in checks:
    print(f"  [{'OK' if ok else 'FAIL'}] hermes_patch: {name}")
print(f"\n  hermes_patch selftest: {len(checks) - len(fails)}/{len(checks)} checks passed")
sys.exit(1 if fails else 0)
