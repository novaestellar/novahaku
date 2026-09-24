#!/usr/bin/env python
"""PIPELINE TEST (test category 13) — whole-chain, cross-repo, real execution.

Why this exists
---------------
Every defect found in this project was an INTER-FILE defect:
  BUG 1  engagement_writer -> engine.chain_state  (ImportError swallowed)
  BUG 2  three different "engagements root" resolvers disagreeing
  BUG 8  probe() got a URL that already carried a query string
  BUG 9  `if r else` discarded HTTP >= 400, i.e. the strongest vuln signal
Each file was individually correct. Only running the CHAIN exposes them.

Chain under test
----------------
  recon (novaxinwei recon_schema) -> findings -> chain.json -> engagement -> report

What this asserts
-----------------
  P1  novahaku writes chain.json that novaxinwei can READ back
  P2  novaxinwei writes chain.json that novahaku can READ back
  P3  both agree on schema version and state-key names
  P4  start-order (is_stale / started_by) is consistent from both sides
  P5  novahaku findings.csv is consumable downstream
  P6  the engagements-root contract is ONE root, not three
  P7  concurrent writers do not corrupt the ledger (lock actually holds)

Run:  python _pipeline_test.py
Exit: 0 all pass, 1 any fail. Prints per-check evidence.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

NOVAHAKU = Path("D:/Labs/novahaku")
NOVAXINWEI = Path("D:/Labs/novaxinwei")
PY = sys.executable

checks: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, evidence: str = "") -> None:
    checks.append((name, bool(cond), evidence))


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# P3 first: the contract itself. If these disagree, nothing else can work.
# ============================================================================
er = load(NOVAHAKU / "scripts" / "engage_runner.py", "engage_runner_pipe")

cx_path = NOVAXINWEI / "engine" / "chain_state.py"
if cx_path.exists():
    # novaxinwei is a package; chain_state uses plain `from chain_state import ...`
    # style fallbacks, so load it standalone too.
    sys.path.insert(0, str(NOVAXINWEI / "engine"))
    try:
        cx = load(cx_path, "chain_state_pipe")
    except Exception as exc:  # noqa: BLE001
        cx = None
        check("P3a novaxinwei chain_state importable", False, f"{type(exc).__name__}: {exc}")
    finally:
        sys.path.pop(0)
else:
    cx = None
    check("P3a novaxinwei chain_state present", False, f"missing {cx_path}")

if cx is not None:
    check("P3a novaxinwei chain_state importable", True, "loaded")
    check(
        "P3b schema version matches across repos",
        getattr(er, "CHAIN_VERSION", None) == getattr(cx, "CHAIN_VERSION", None),
        f"novahaku={getattr(er, 'CHAIN_VERSION', None)!r} "
        f"novaxinwei={getattr(cx, 'CHAIN_VERSION', None)!r}",
    )
    check(
        "P3c filename matches across repos",
        getattr(er, "CHAIN_FILENAME", None) == getattr(cx, "CHAIN_FILENAME", None) == "chain.json",
        f"novahaku={getattr(er, 'CHAIN_FILENAME', None)!r} "
        f"novaxinwei={getattr(cx, 'CHAIN_FILENAME', None)!r}",
    )
    er_keys = getattr(er, "_CHAIN_STATE_KEYS", None)
    cx_keys = getattr(cx, "_STATE_KEY", None)
    if er_keys is not None and cx_keys is not None:
        same = all(er_keys.get(k) == cx_keys.get(k) for k in ("novahaku", "novaxinwei"))
        check(
            "P3d state-key names identical in both repos",
            same,
            f"novahaku={er_keys} novaxinwei={cx_keys}",
        )
    else:
        check("P3d state-key tables discoverable", False, f"er={er_keys} cx={cx_keys}")

# ============================================================================
# P6: one root, not three. The three-root bug is the BUG 2 class.
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    root_env = Path(td) / "engagements_root"
    root_env.mkdir()

    def roots_from(mod) -> list[str]:
        out = []
        for fn_name in ("engagements_root", "_engagements_root", "resolve_engagements_root"):
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    out.append(str(fn(str(root_env))))
                except Exception as exc:  # noqa: BLE001
                    out.append(f"ERR:{type(exc).__name__}")
        return out

    er_roots = roots_from(er)
    check("P6a novahaku exposes exactly one root resolver", len(er_roots) == 1, f"{er_roots}")

    default_root = er.engagements_root(None) if hasattr(er, "engagements_root") else None
    check(
        "P6b default root is absolute and stable",
        isinstance(default_root, str) and os.path.isabs(default_root),
        f"{default_root!r}",
    )
    check(
        "P6c repeated calls return the same root (no cwd drift)",
        er.engagements_root(None) == default_root,
        "two calls compared",
    )

    # The resolver must honour an explicit base, not ignore it.
    if hasattr(er, "engagements_root"):
        check(
            "P6d explicit base is honoured",
            er.engagements_root(str(root_env)).rstrip("\\/") == str(root_env).rstrip("\\/"),
            f"got={er.engagements_root(str(root_env))!r}",
        )

    # ========================================================================
    # P1 / P2 / P4: cross-repo chain.json interoperability, real files.
    # ========================================================================
    target = "127.0.0.1"
    (root_env / target).mkdir(parents=True, exist_ok=True)

    # novahaku writes
    try:
        er.record_chain(target, "test-run", phase="test", base=str(root_env))
        wrote = True
        err = ""
    except Exception as exc:  # noqa: BLE001
        wrote = False
        err = f"{type(exc).__name__}: {exc}"
    check("P1a novahaku can write chain.json", wrote, err or "ok")

    p = root_env / target / "chain.json"
    check("P1b chain.json exists on disk", p.exists(), str(p))

    if p.exists():
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            check("P1c chain.json is valid JSON object", isinstance(raw, dict), f"keys={sorted(raw)}")
            check("P1d version stamped correctly",
                  raw.get("version") == er.CHAIN_VERSION,
                  f"{raw.get('version')!r}")
            check("P1e target recorded", raw.get("target") == target, f"{raw.get('target')!r}")
            check("P1f state holds novahaku keys",
                  "results_at" in raw.get("state", {}) and "results_by" in raw.get("state", {}),
                  f"state={raw.get('state')}")
        except Exception as exc:  # noqa: BLE001
            check("P1c-P1f chain.json parseable", False, f"{type(exc).__name__}: {exc}")

        # novaxinwei reads what novahaku wrote
        if cx is not None:
            try:
                back = cx.read_chain(target, base_dir=str(root_env))
                check("P1g novaxinwei READS novahaku's chain.json",
                      isinstance(back, dict), f"got={type(back).__name__}")
                check("P1h novaxinwei agrees on version",
                      isinstance(back, dict) and back.get("version") == cx.CHAIN_VERSION,
                      f"{back.get('version') if isinstance(back, dict) else None!r}")
                sb = cx.started_by(target, base_dir=str(root_env))
                check("P1i novaxinwei started_by() readable",
                      sb is None or isinstance(sb, str), f"started_by={sb!r}")
            except Exception as exc:  # noqa: BLE001
                check("P1g-P1i novaxinwei reads novahaku output", False,
                      f"{type(exc).__name__}: {exc}")

            # P2: novaxinwei writes, novahaku reads
            try:
                cx.record(target, "novaxinwei", "recon", base_dir=str(root_env))
                check("P2a novaxinwei can record into the same chain", True, "record() ok")
                raw2 = json.loads(p.read_text(encoding="utf-8"))
                check("P2b novaxinwei wrote recon_* keys",
                      "recon_at" in raw2.get("state", {}) and "recon_by" in raw2.get("state", {}),
                      f"state={raw2.get('state')}")
                check("P2c novahaku keys survived novaxinwei's write",
                      raw2.get("state", {}).get("results_by") == "novahaku",
                      f"results_by={raw2.get('state', {}).get('results_by')!r}")

                # P4: start order consistent
                stale_er = er.recon_is_stale(target, base=str(root_env)) if hasattr(er, "recon_is_stale") else None
                stale_cx = cx.is_stale(raw2, "novahaku")
                check("P4a both repos compute staleness",
                      stale_er is not None and isinstance(stale_cx, bool),
                      f"novahaku={stale_er} novaxinwei={stale_cx}")
                if stale_er is not None:
                    check("P4b staleness verdict AGREES across repos",
                          bool(stale_er) == bool(stale_cx),
                          f"novahaku={stale_er} novaxinwei={stale_cx}")
            except Exception as exc:  # noqa: BLE001
                check("P2/P4 cross-write", False, f"{type(exc).__name__}: {exc}")

    # ========================================================================
    # P5: findings.csv is consumable — header contract downstream depends on.
    # ========================================================================
    findings_dir = root_env / target / "findings"
    findings_dir.mkdir(parents=True, exist_ok=True)
    fcsv = findings_dir / "findings.csv"
    header = ["ID", "Title", "Severity", "Confidence", "Category",
              "Asset / Host", "Description", "Remediation", "Evidence"]
    try:
        with open(fcsv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerow(["1", "Reflected XSS", "High", "High", "xss",
                        target, "q param reflects", "encode output", "payload=..."])
        with open(fcsv, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        check("P5a findings.csv roundtrips with expected header",
              list(rows[0].keys()) == header if rows else False,
              f"header={list(rows[0].keys()) if rows else None}")
        check("P5b findings row readable", rows and rows[0].get("Title") == "Reflected XSS",
              f"rows={len(rows)}")
    except Exception as exc:  # noqa: BLE001
        check("P5 findings.csv contract", False, f"{type(exc).__name__}: {exc}")

    # ========================================================================
    # P7: the ledger lock must actually hold under concurrent writers.
    # ========================================================================
    workers = 6
    sfile = Path(td) / "worker.py"
    worker_src = f"""
import sys, importlib.util, pathlib
root = pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location('er', r'{NOVAHAKU / "scripts" / "engage_runner.py"}')
m = importlib.util.module_from_spec(spec); sys.modules['er'] = m
spec.loader.exec_module(m)
for i in range(5):
    m.record_chain('127.0.0.1', 'w' + sys.argv[1] + '-' + str(i), phase='test', base=str(root))
print('done')
"""
    sfile.write_text(worker_src, encoding="utf-8")
    procs = [subprocess.Popen([PY, str(sfile), str(i), str(root_env)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for i in range(workers)]
    outs = [pr.communicate() for pr in procs]
    rcs = [pr.returncode for pr in procs]
    errs = [e for _, e in outs if e.strip()]
    if errs and any(r != 0 for r in rcs):
        print("    worker stderr sample:", errs[0].strip().splitlines()[-2:])
    check("P7a all concurrent writers exited 0",
          all(r == 0 for r in rcs), f"rcs={rcs}")

    try:
        final = json.loads(p.read_text(encoding="utf-8"))
        check("P7b ledger still valid JSON after concurrent writes",
              isinstance(final, dict), f"keys={sorted(final) if isinstance(final, dict) else None}")
        check("P7c no torn write (version key intact)",
              final.get("version") == er.CHAIN_VERSION, f"version={final.get('version')!r}")
        hist = final.get("history") or final.get("entries") or []
        check("P7d contribution history recorded",
              len(hist) >= 1, f"history_len={len(hist)}")
    except Exception as exc:  # noqa: BLE001
        check("P7b-P7d ledger integrity", False, f"{type(exc).__name__}: {exc}")

    # ========================================================================
    # P8: absent / corrupt chain must degrade, never crash the chain.
    # ========================================================================
    if cx is not None:
        try:
            none_chain = cx.read_chain("no-such-target-xyz", base_dir=str(root_env))
            check("P8a absent chain returns None (not exception)", none_chain is None,
                  f"got={none_chain!r}")
        except Exception as exc:  # noqa: BLE001
            check("P8a absent chain returns None", False, f"{type(exc).__name__}: {exc}")

        bad = root_env / "corrupt" / "chain.json"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("{not json", encoding="utf-8")
        try:
            got = cx.read_chain("corrupt", base_dir=str(root_env))
            check("P8b corrupt chain returns None (not crash)", got is None, f"got={got!r}")
        except Exception as exc:  # noqa: BLE001
            check("P8b corrupt chain returns None", False, f"{type(exc).__name__}: {exc}")


# ============================================================================
# Report
# ============================================================================
fails = [n for n, ok, _ in checks if not ok]
for name, ok, ev in checks:
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f"  <{ev}>" if ev else ""))
print(f"\n  pipeline test: {len(checks) - len(fails)}/{len(checks)} checks passed")
if fails:
    print("  FAILED: " + ", ".join(fails))
sys.exit(1 if fails else 0)
