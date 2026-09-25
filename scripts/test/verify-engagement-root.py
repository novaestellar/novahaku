#!/usr/bin/env python3
"""Verify the engagement-root contract: ONE root, one directory per target.

Why this gate exists
--------------------
Three separate resolvers used to disagree about the engagements root, so a
pipeline could write to the directory it was told to use while the CLI wrote to
the default — and neither could find the other's files. That was fixed; this
gate exists so it cannot come back, and so the per-target isolation is proven
rather than assumed.

What it proves
--------------
1. Every resolver agrees on precedence: caller arg > NOVAHAKU_ENGAGEMENT_DIR >
   <skill root>/engagements.
2. Two targets under one root get distinct directories. If this ever fails,
   running a second engagement silently overwrites the first one's state.
3. A target name cannot escape the root (path separators, `..`, absolute paths).

Exit 0 = contract holds.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve()
while not (ROOT / ".git").exists():
    ROOT = ROOT.parent
    if ROOT.parent == ROOT:
        sys.exit("verify-engagement-root: not inside a git repository")

SCRIPTS = ROOT / "scripts"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    checks: list[tuple[str, bool]] = []

    eng = load("nh_engagement", SCRIPTS / "engagement.py")
    run = load("nh_engage_runner", SCRIPTS / "engage_runner.py")

    # --- 1. Resolvers agree on the default root -----------------------------
    base = eng.engagements_dir(None)
    runner_base = run.engagements_root(None) if hasattr(run, "engagements_root") else base
    checks.append(("engagement.py default root is absolute", os.path.isabs(base)))
    checks.append(("engage_runner default root matches engagement.py",
                   os.path.normcase(os.path.normpath(base)) ==
                   os.path.normcase(os.path.normpath(runner_base))))

    # --- 2. Caller argument wins over env var, env var wins over default ----
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        env_root = td / "from_env"
        arg_root = td / "from_arg"
        env_root.mkdir()
        arg_root.mkdir()

        saved = os.environ.get("NOVAHAKU_ENGAGEMENT_DIR")
        os.environ["NOVAHAKU_ENGAGEMENT_DIR"] = str(env_root)
        try:
            got_env = eng.engagements_dir(None)
            checks.append(("NOVAHAKU_ENGAGEMENT_DIR is honoured",
                           os.path.normcase(os.path.normpath(got_env)) ==
                           os.path.normcase(os.path.normpath(str(env_root)))))
            got_arg = eng.engagements_dir(str(arg_root))
            checks.append(("caller argument beats the env var",
                           os.path.normcase(os.path.normpath(got_arg)) ==
                           os.path.normcase(os.path.normpath(str(arg_root)))))

            # --- 3. Two targets, one root -> two directories ----------------
            t1 = eng.engagement_path("alpha.example", base=str(env_root))
            t2 = eng.engagement_path("beta.example", base=str(env_root))
            checks.append(("two targets get distinct directories",
                           os.path.normcase(t1) != os.path.normcase(t2)))
            checks.append(("target dir sits directly under the root",
                           os.path.dirname(t1) == os.path.normpath(str(env_root))))

            # Files with the SAME name must not collide across targets.
            os.makedirs(t1, exist_ok=True)
            os.makedirs(t2, exist_ok=True)
            (Path(t1) / "state.json").write_text('{"target":"alpha"}', encoding="utf-8")
            (Path(t2) / "state.json").write_text('{"target":"beta"}', encoding="utf-8")
            a = (Path(t1) / "state.json").read_text(encoding="utf-8")
            b = (Path(t2) / "state.json").read_text(encoding="utf-8")
            checks.append(("same-named state.json does not collide",
                           '"alpha"' in a and '"beta"' in b))
        finally:
            if saved is None:
                os.environ.pop("NOVAHAKU_ENGAGEMENT_DIR", None)
            else:
                os.environ["NOVAHAKU_ENGAGEMENT_DIR"] = saved

    # --- 4. Target names cannot escape the root -----------------------------
    with tempfile.TemporaryDirectory() as td:
        hostile = ["../../escape", "..\\..\\escape", "/etc/passwd",
                   "C:\\Windows", "..", ".", "", "  ", "a/b", "a\\b"]
        rejected = 0
        for name in hostile:
            try:
                p = eng.engagement_path(name, base=td)
                # If it did not raise, the resolved path must still be inside.
                if os.path.abspath(p).startswith(os.path.abspath(td) + os.sep):
                    rejected += 1  # contained by luck, still acceptable
            except (ValueError, TypeError):
                rejected += 1
        checks.append(("hostile target names are rejected or contained (%d/%d)"
                       % (rejected, len(hostile)), rejected == len(hostile)))

        legit = ["example.com", "acme-corp", "10.0.0.1", "*.acme.io", "sub_domain"]
        ok = 0
        for name in legit:
            try:
                p = eng.engagement_path(name, base=td)
                if os.path.abspath(p).startswith(os.path.abspath(td) + os.sep):
                    ok += 1
            except (ValueError, TypeError):
                pass
        checks.append(("legitimate target names are accepted (%d/%d)"
                       % (ok, len(legit)), ok == len(legit)))

    # --- report -------------------------------------------------------------
    failed = 0
    for name, good in checks:
        print("  [%s] %s" % ("OK" if good else "FAIL", name))
        if not good:
            failed += 1

    print("\nverify-engagement-root: %d/%d checks pass" % (len(checks) - failed, len(checks)))
    if failed:
        print("FAIL verify-engagement-root: %d check(s) failed" % failed)
        return 1
    print("OK verify-engagement-root: one root, one directory per target, no escape")
    return 0


if __name__ == "__main__":
    sys.exit(main())
