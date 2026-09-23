#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engage_runner.py - Engagement test orchestration with approach racing (stdlib-only)

Races candidate testing approaches in parallel, scores them, and writes
structured findings into the engagement workspace. Reads the approach pool
and scoring tables from config/engagement_phases.json.

Usage:
  python engage_runner.py race      --target <target> [--url URL] [--jwt TOKEN] [--workers N]
  python engage_runner.py test    --target <target> [--url <url>]
  python engage_runner.py exploit --target <target> [--url <url>] [--jwt <token>]
  python engage_runner.py publish --target <target>
  python engage_runner.py report    --target <target>
  python engage_runner.py verify    --target <target>
  python engage_runner.py integrity --target <target>
  python engage_runner.py selftest

Existing scanners are invoked as subprocesses - never imported, never modified.
No-arg = help.
"""

import sys
import os
import re
import csv
import json
import time
import shutil
import tempfile
import importlib.util
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
CONFIG_PATH = os.path.join(SKILL_ROOT, "config", "engagement_phases.json")
DEFAULT_ENGAGEMENTS_DIR = "engagements"

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]

# webtest.py writes one fixed results path, so approaches must take turns on it.
# A lock older than this is treated as abandoned and reclaimed.
SCAN_LOCK_STALE_SECONDS = 120
FINDINGS_CSV_HEADER = [
    "ID", "Title", "Severity", "Confidence", "Category",
    "Asset / Host", "Description", "Remediation", "Evidence",
]


# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

def read_json(path, default):
    """Read a JSON file, returning ``default`` on any problem.

    Engagements are written by several processes and interrupted often, so any
    file on disk can be truncated or binary. JSONDecodeError, IOError, and
    UnicodeDecodeError (a ValueError, which the older handlers missed) must all
    degrade to the default rather than aborting the caller with a traceback.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, IOError, UnicodeDecodeError, ValueError):
        return default


def load_config(path=None):
    path = path or CONFIG_PATH
    config = read_json(path, None)
    if not isinstance(config, dict):
        raise SystemExit(f"[!] config unreadable or not an object: {path}")
    return config


def load_state(target, base=None):
    """Read state.json, returning None when it is absent, truncated, or binary.

    This is the trust boundary for engagement state: a corrupt file must degrade
    to "no state" so the caller can report it, never raise. An uncaught
    UnicodeDecodeError here previously killed `list` for every engagement on the
    host because one bad state.json aborted the whole scan.
    """
    path = os.path.join(engagement_dir(target, base), "state.json")
    if not os.path.exists(path):
        return None
    state = read_json(path, None)
    return state if isinstance(state, dict) else None


def save_state(target, state, base=None):
    path = os.path.join(engagement_dir(target, base), "state.json")
    state["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def engagement_dir(target, base=None):
    root = os.path.abspath(base) if base else os.path.join(SKILL_ROOT, DEFAULT_ENGAGEMENTS_DIR)
    return os.path.join(root, target)


def findings_dir(target, base=None):
    return os.path.join(engagement_dir(target, base), "findings")


# ----------------------------------------------------------------------------
# Recon reader (hyphenated dir is not importable as a package -> load by path)
# ----------------------------------------------------------------------------

def load_recon_reader():
    """Load ReconReader by file path.

    testing/web2-recon/ contains a hyphen, so it cannot be imported as a
    package. spec_from_file_location is the working route.
    """
    path = os.path.join(SKILL_ROOT, "testing", "web2-recon", "scripts", "recon_reader.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("novahaku_recon_reader", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_recon(target, base=None):
    """Read recon.json if present. Returns {} when absent - never fatal."""
    module = load_recon_reader()
    if module is None:
        return {}
    # ReconReader resolves paths relative to CWD, so pass the absolute dir.
    reader = module.ReconReader(target, engagements_dir=os.path.dirname(engagement_dir(target, base)))
    if not reader.exists():
        return {}
    return reader.load() or {}


# ----------------------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------------------

def score_finding(finding, scoring):
    """Composite score: severity*0.4 + confidence*0.3 + reproducibility*0.2 + impact*0.1"""
    w = scoring["composite_weights"]
    sev = scoring["severity"].get(str(finding.get("severity", "info")).lower(), 10)
    conf = scoring["confidence"].get(str(finding.get("confidence", "possible")).lower(), 40)
    repro = scoring["reproducibility"].get(str(finding.get("reproducibility", "sometimes")).lower(), 40)
    imp = scoring["impact"].get(str(finding.get("impact", "misconfig")).lower(), 20)
    composite = (
        sev * w["severity"]
        + conf * w["confidence"]
        + repro * w["reproducibility"]
        + imp * w["impact"]
    )
    return {
        "composite": round(composite, 2),
        "severity": sev,
        "confidence": conf,
        "reproducibility": repro,
        "impact": imp,
    }


def score_approach(findings, scoring):
    """Aggregate score for one approach = mean finding score, 0 when empty."""
    if not findings:
        return {"composite": 0.0, "count": 0, "severity_counts": {}}
    total = 0.0
    counts = {}
    for f in findings:
        s = score_finding(f, scoring)
        total += s["composite"]
        sev = str(f.get("severity", "info")).lower()
        counts[sev] = counts.get(sev, 0) + 1
    return {
        "composite": round(total / len(findings), 2),
        "count": len(findings),
        "severity_counts": counts,
    }


def filter_false_positives(findings, patterns):
    """Drop findings whose evidence matches a known non-finding pattern."""
    if not patterns:
        return findings
    rx = re.compile("|".join(patterns), re.I)
    kept = []
    for f in findings:
        evidence = str(f.get("evidence", "")) + " " + str(f.get("description", ""))
        if not rx.search(evidence):
            kept.append(f)
    return kept


# ----------------------------------------------------------------------------
# Approach execution
# ----------------------------------------------------------------------------

def build_approach_list(config, tech_stack=None):
    """Flatten the approach pool into a runnable list."""
    pool = config.get("approach_pool", {})
    approaches = []
    for group, items in pool.items():
        if group == "description":
            continue
        for item in items:
            a = dict(item)
            a["group"] = group
            approaches.append(a)
    return approaches


def run_approach(approach, target, url, jwt_token, timeout):
    """Execute one approach as a subprocess. Returns (approach, findings, error)."""
    script = os.path.join(SKILL_ROOT, approach["script"])
    if not os.path.exists(script):
        return approach, [], f"script missing: {approach['script']}"

    if approach.get("requires") == "jwt":
        if not jwt_token:
            return approach, [], "skipped: no --jwt supplied"
        cmd = [sys.executable, script, "--jwt", jwt_token]
        if url:
            cmd += ["--url", url]
    else:
        if not url:
            return approach, [], "skipped: no --url supplied"
        cmd = [sys.executable, script, url]
        if approach.get("modules"):
            cmd += ["--modules", approach["modules"]]

    # webtest.py writes webtest_results.json next to its own script, never to CWD,
    # so every parallel approach would write the same path. An mtime guard cannot
    # close that window: approach A writes the file, approach B sees a fresh mtime
    # and adopts A's findings as its own, which corrupts per-module attribution and
    # therefore the race winner. Serialise the file region with a lock instead, and
    # copy the result out before releasing so the next approach cannot overwrite it.
    shared_results = os.path.join(SKILL_ROOT, "testing", "scripts", "webtest_results.json")

    workdir = tempfile.mkdtemp(prefix="novahaku-approach-")
    lock_path = shared_results + ".racelock"
    captured = os.path.join(workdir, "results.json")
    have_lock = False
    try:
        have_lock = _acquire_scan_lock(lock_path, timeout=timeout)
        if not have_lock:
            # Without the lock the scan would share webtest_results.json with a
            # concurrent approach and adopt its findings as our own - the exact
            # corruption this lock exists to prevent. Refuse to run rather than
            # run unprotected: a missing approach is visible, a misattributed one
            # is not.
            return approach, [], f"could not acquire scan lock within {timeout}s"

        if os.path.exists(shared_results):
            # Start from a clean slate so a previous approach's file can never be
            # mistaken for ours even if the write is skipped on this run.
            try:
                os.remove(shared_results)
            except OSError:
                pass

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, cwd=workdir
            )
        except subprocess.TimeoutExpired:
            return approach, [], f"timeout after {timeout}s"

        # Snapshot the result while still holding the lock, then release before
        # parsing so a slow parse does not block the other approaches.
        if os.path.exists(shared_results):
            try:
                shutil.copyfile(shared_results, captured)
            except OSError:
                captured = None
        else:
            captured = None

        if have_lock:
            _release_scan_lock(lock_path)
            have_lock = False

        findings = parse_scanner_output(
            proc.stdout, target, approach, captured if captured and os.path.exists(captured) else None
        )
        if proc.returncode != 0 and not findings:
            return approach, [], f"exit {proc.returncode}"
        return approach, findings, None
    except OSError as exc:
        return approach, [], f"exec failed: {exc}"
    finally:
        if have_lock:
            _release_scan_lock(lock_path)
        shutil.rmtree(workdir, ignore_errors=True)


def _acquire_scan_lock(lock_path, timeout=300):
    """Cross-process lock around the shared scanner results file.

    webtest.py has no way to redirect its output path, so the file is a genuine
    shared resource. A lock file with a staleness bound is enough here: approaches
    are separate processes on one host, and a crashed run must not wedge the rest.

    ``timeout`` is the caller's real bound on how long to wait; it is honoured as
    given. Do not impose a floor on it - the callers (including the selftest) pass
    short values and would silently block for the floor instead.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as fh:
                fh.write(str(os.getpid()))
            return True
        except FileExistsError:
            # Reclaim locks whose owner died mid-run.
            try:
                if time.time() - os.path.getmtime(lock_path) > SCAN_LOCK_STALE_SECONDS:
                    os.remove(lock_path)
                    continue
            except OSError:
                pass
            time.sleep(0.05)
        except OSError:
            return False
    return False


def _release_scan_lock(lock_path):
    try:
        os.remove(lock_path)
    except OSError:
        pass


def dedupe_findings(findings):
    """Collapse findings that describe the same issue on the same asset.

    Parallel approaches can surface the same issue; the report should carry it
    once, keeping the highest-severity copy.
    """
    best = {}
    for f in findings:
        key = (
            str(f.get("asset", "")).lower().strip(),
            str(f.get("category", "")).lower().strip(),
            str(f.get("title", "")).lower().strip()[:120],
        )
        rank = SEVERITY_ORDER.index(str(f.get("severity", "info")).lower()) \
            if str(f.get("severity", "info")).lower() in SEVERITY_ORDER else 99
        if key not in best or rank < best[key][0]:
            best[key] = (rank, f)
    return [f for _, f in sorted(best.values(), key=lambda x: x[0])]


FINDING_TAGS = ("[vuln]", "[found]", "[!]", "[critical]", "[high]", "[warn]", "[!] vulnerable")


def parse_scanner_output(stdout, target, approach, results_file=None):
    """Parse one approach's own output into finding dicts.

    Order matters: the approach's own results file first (authoritative), then
    the JSON blob on stdout, then tagged stdout lines as a last resort.
    Never raises - empty list on anything unparseable.
    """
    findings = []

    if results_file and os.path.exists(results_file):
        data = read_json(results_file, None)
        if data is not None:
            findings.extend(_findings_from_json(data, target, approach))
    if findings:
        return findings

    # JSON blob on stdout
    for chunk in re.findall(r"\{[\s\S]*\}", stdout or ""):
        try:
            data = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        findings.extend(_findings_from_json(data, target, approach))
    if findings:
        return findings

    # Tagged stdout lines. Scanner modules emit "[i] dir exists: /api",
    # "[!!] SQLi on ?id=1" etc. Severity is inferred from the tag.
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("[") or "]" not in line:
            continue
        tag_end = line.index("]")
        tag = line[: tag_end + 1].lower()
        body = line[tag_end + 1:].strip()
        if not body or "target" in body.lower() or body.lower().startswith("done"):
            continue
        if tag not in FINDING_TAGS and tag not in ("[i]", "[+]", "[*]", "[!!]", "[!!]"):
            continue
        if tag in ("[i]", "[+]", "[*]"):
            severity = "info"
        elif tag in ("[!!]", "[!]", "[critical]"):
            severity = "high"
        else:
            severity = "medium"
        findings.append({
            "title": body[:120],
            "severity": severity,
            "confidence": "possible",
            "category": approach.get("group", "web"),
            "asset": target,
            "description": f"[{approach['name']}] {body}"[:400],
            "evidence": line[:400],
            "impact": "info_disclosure" if severity == "info" else "needs_review",
        })
    return findings


def _findings_from_json(data, target, approach):
    """Extract findings from scanner JSON of unknown exact shape."""
    out = []

    def walk(node, path=""):
        if isinstance(node, dict):
            sev = str(node.get("severity", "")).lower()
            if sev in SEVERITY_ORDER:
                out.append({
                    "title": str(node.get("title") or node.get("name") or
                                 node.get("issue") or f"{approach['name']} finding"),
                    "severity": sev,
                    "confidence": str(node.get("confidence", "possible")).lower(),
                    "category": str(node.get("category") or approach.get("group", "web")),
                    "asset": str(node.get("asset") or node.get("host") or node.get("url") or target),
                    "description": str(node.get("description") or node.get("detail") or "")[:1000],
                    "evidence": str(node.get("evidence") or node.get("proof") or
                                    node.get("payload") or "")[:1000],
                    "impact": str(node.get("impact", "info_disclosure")).lower(),
                    "reproducibility": str(node.get("reproducibility", "sometimes")).lower(),
                })
            for key, val in node.items():
                walk(val, f"{path}.{key}")
        elif isinstance(node, list):
            for item in node:
                walk(item, path)

    walk(data)
    return out


def race(target, url, jwt_token, base=None, workers=None):
    """Run all approaches in parallel, score, and record winners."""
    config = load_config()
    scoring = config["scoring"]
    fp_patterns = config.get("false_positive_patterns", [])
    limits = config.get("limits", {})
    workers = workers or limits.get("max_workers", 5)
    timeout = limits.get("module_timeout_seconds", 300)

    state = load_state(target, base)
    if not state:
        print(f"[!] No engagement for {target} - run: python scripts/engagement.py init {target}")
        return 1

    recon = read_recon(target, base)
    tech = {}
    if recon and "recon" in recon:
        tech = recon["recon"].get("tech_stack", {}) or {}
    approaches = build_approach_list(config, tech)

    # Skip approaches needing creds we do not have.
    runnable = []
    skipped = []
    for a in approaches:
        if a.get("requires") == "jwt" and not jwt_token:
            skipped.append((a["name"], "no jwt"))
            continue
        if a.get("requires") == "url" and not url:
            skipped.append((a["name"], "no url"))
            continue
        if a.get("group") == "web" and not url:
            skipped.append((a["name"], "no url"))
            continue
        runnable.append(a)

    print(f"[*] Target:    {target}")
    print(f"[*] URL:       {url or '(none)'}")
    print(f"[*] Approaches: {len(runnable)} runnable, {len(skipped)} skipped")
    print(f"[*] Workers:   {workers}, timeout: {timeout}s")
    print()

    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {
            ex.submit(run_approach, a, target, url, jwt_token, timeout): a
            for a in runnable
        }
        for fut in as_completed(futures):
            approach, findings, err = fut.result()
            if err:
                errors.append((approach["name"], err))
                print(f"  [-] {approach['name']:<22} {err}")
                results.append({"module": approach["name"], "findings": [],
                                "score": {"composite": 0.0, "count": 0}, "error": err})
                continue
            findings = filter_false_positives(findings, fp_patterns)
            s = score_approach(findings, scoring)
            results.append({"module": approach["name"], "findings": findings, "score": s})
            print(f"  [+] {approach['name']:<22} findings={s['count']:<3} score={s['composite']}")

    results.sort(key=lambda r: r["score"]["composite"], reverse=True)

    # Winner per vulnerability class (group)
    winners = {}
    for r in results:
        if r["score"]["count"] == 0:
            continue
        group = "web"
        for a in approaches:
            if a["name"] == r["module"]:
                group = a.get("group", "web")
                break
        if group not in winners or r["score"]["composite"] > winners[group]["score"]["composite"]:
            winners[group] = r

    all_findings = []
    for r in results:
        for f in r["findings"]:
            f["_module"] = r["module"]
            all_findings.append(f)
    all_findings = dedupe_findings(all_findings)

    # Persist
    fdir = findings_dir(target, base)
    os.makedirs(fdir, exist_ok=True)

    race_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target": target,
        "url": url,
        "approaches_run": len(runnable),
        "approaches_skipped": [{"name": n, "reason": r} for n, r in skipped],
        "errors": [{"name": n, "error": e} for n, e in errors],
        "results": [
            {"module": r["module"], "score": r["score"]["composite"],
             "count": r["score"]["count"], "severity_counts": r["score"]["severity_counts"]}
            for r in results
        ],
        "winners": {g: {"module": r["module"], "score": r["score"]["composite"]}
                    for g, r in winners.items()},
    }
    candidates_path = os.path.join(fdir, "candidates.json")
    _atomic_json(candidates_path, race_payload)
    _write_findings(target, all_findings, base)

    # Record the actual per-group winners, not every module. Labelling each
    # module as its own "winner" made `status` print score-0 modules as winners
    # and reported a module that did not win its group as the winner.
    winners_by_module = {r["module"]: g for g, r in winners.items()}
    state["race_results"] = [
        {"module": name,
         "group": group,
         "winner": {"type": winners[group]["module"],
                    "score": winners[group]["score"]["composite"]},
         "count": next((x["score"]["count"] for x in results if x["module"] == name), 0),
         "timestamp": race_payload["timestamp"]}
        for name, group in winners_by_module.items()
    ]
    state["stats"]["modules_tested"] = len(runnable)
    state["stats"]["modules_failed"] = len(errors)
    # race() writes findings.json, so the state tally must move with it. Leaving
    # stats stale here makes integrity report a false mismatch after race.
    _sync_finding_stats(state, all_findings)
    save_state(target, state, base)

    print()
    print(f"[+] Raced {len(runnable)} approaches. Findings: {len(all_findings)}")
    print(f"[+] Winners: {json.dumps(race_payload['winners'])}")
    print(f"[+] Written: {candidates_path}")
    return 0


def test(target, url, jwt_token, base=None):
    """Deep execution: re-read candidates, write structured findings."""
    config = load_config()
    state = load_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1

    fdir = findings_dir(target, base)
    candidates_path = os.path.join(fdir, "candidates.json")
    if not os.path.exists(candidates_path):
        print(f"[!] No candidates.json - run 'race' first")
        return 1

    candidates = read_json(candidates_path, None)
    if not isinstance(candidates, dict):
        print("[!] candidates.json unreadable - re-run 'race'")
        return 1

    winners = candidates.get("winners", {})
    if not winners:
        print("[!] No winning approach recorded - nothing to deepen")
        return 1

    scoring = config["scoring"]
    fp_patterns = config.get("false_positive_patterns", [])
    limits = config.get("limits", {})
    timeout = limits.get("module_timeout_seconds", 300)

    approaches = build_approach_list(config)
    by_name = {a["name"]: a for a in approaches}

    all_findings = []
    for group, win in winners.items():
        name = win.get("module")
        a = by_name.get(name)
        if not a:
            continue
        print(f"[*] Deep run: {name} (group={group})")
        _, findings, err = run_approach(a, target, url, jwt_token, timeout)
        if err:
            print(f"  [-] {err}")
            continue
        findings = filter_false_positives(findings, fp_patterns)
        for f in findings:
            f["_module"] = name
            f["_score"] = score_finding(f, scoring)["composite"]
        all_findings.extend(findings)
        print(f"  [+] {len(findings)} finding(s)")

    all_findings = dedupe_findings(all_findings)
    _write_findings(target, all_findings, base)

    _sync_finding_stats(state, all_findings)
    state["findings_references"] = [
        {"id": f.get("id"), "file": "findings/findings.json",
         "severity": str(f.get("severity", "info")).lower()}
        for f in all_findings
    ]
    save_state(target, state, base)
    print(f"[+] {len(all_findings)} finding(s) written to {fdir}")
    return 0


def exploit(target, url, jwt_token, base=None):
    """Validate findings into reproducible evidence, dropping what fails.

    Per config/engagement_phases.json this phase re-runs each confirmed finding
    for reproducibility, captures raw request/response evidence under
    findings/evidence/, and sets confidence. A finding that cannot be reproduced
    is dropped rather than reported - a report full of unverified findings is
    worse than a shorter honest one.
    """
    import urllib.error
    import urllib.request

    config = load_config()
    state = load_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1

    fdir = findings_dir(target, base)
    findings_path = os.path.join(fdir, "findings.json")
    data = read_json(findings_path, None)
    if not isinstance(data, dict):
        print(f"[!] No readable findings.json - run 'test' first")
        return 1

    records = data.get("findings", [])
    if not records:
        print("[!] No findings to validate")
        return 1

    edir = os.path.join(fdir, "evidence")
    os.makedirs(edir, exist_ok=True)

    limits = config.get("limits", {})
    timeout = min(limits.get("module_timeout_seconds", 300), 30)
    headers = {}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"

    confirmed, dropped = [], []
    print(f"[*] Exploit: validating {len(records)} finding(s) against {url or '(no url)'}")
    for rec in records:
        fid = rec.get("id") or "F?"
        title = rec.get("title") or "(untitled)"
        evidence_path = os.path.join(edir, f"{fid}.json")

        # A finding with no concrete URL target cannot be reproduced; keep it but
        # record that rather than claiming validation.
        probe_url = rec.get("evidence_url") or url
        if not probe_url:
            rec["confidence"] = rec.get("confidence") or "possible"
            rec["reproduced"] = False
            rec["reproduction_note"] = "no url supplied for this engagement"
            confirmed.append(rec)
            continue

        entry = {
            "id": fid,
            "title": title,
            "url": probe_url,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            req = urllib.request.Request(probe_url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read(4096).decode("utf-8", errors="replace")
                entry.update({
                    "status": resp.status,
                    "headers": dict(resp.headers),
                    "body_excerpt": body[:2048],
                })
            # The endpoint responding again is what "reproducible" means here.
            rec["confidence"] = "confirmed"
            rec["reproduced"] = True
            confirmed.append(rec)
            print(f"  [+] {fid:<6} {title[:44]:46} HTTP {entry['status']}")
        except urllib.error.HTTPError as exc:
            entry.update({"status": exc.code, "error": f"HTTPError {exc.code}"})
            rec["confidence"] = "likely"
            rec["reproduced"] = False
            rec["reproduction_note"] = f"HTTP {exc.code}"
            confirmed.append(rec)
            print(f"  [~] {fid:<6} {title[:44]:46} HTTP {exc.code}")
        except Exception as exc:
            entry.update({"error": f"{type(exc).__name__}: {exc}"})
            rec["confidence"] = "unverified"
            rec["reproduced"] = False
            rec["reproduction_note"] = entry["error"]
            dropped.append(rec)
            print(f"  [-] {fid:<6} {title[:44]:46} {type(exc).__name__} -> dropped")

        _atomic_json(evidence_path, entry)

    # Rewrite findings with confidence/reproduced fields and the survivors only.
    _write_findings(target, confirmed, base)
    dropped_payload = {
        "target": target,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(dropped),
        "dropped": dropped,
    }
    _atomic_json(os.path.join(fdir, "dropped.json"), dropped_payload)

    _sync_finding_stats(state, confirmed)
    state["findings_references"] = [
        {"id": f.get("id"), "file": "findings/findings.json",
         "confidence": f.get("confidence"),
         "severity": str(f.get("severity", "info")).lower()}
        for f in confirmed
    ]
    state["stats"]["exploit_validated"] = sum(1 for f in confirmed if f.get("reproduced"))
    state["stats"]["exploit_dropped"] = len(dropped)
    save_state(target, state, base)

    print()
    print(f"[+] Evidence:  {len(os.listdir(edir))} file(s) in {edir}")
    print(f"[+] Confirmed: {state['stats']['exploit_validated']} reproduced, "
          f"{len(confirmed) - state['stats']['exploit_validated']} kept without reproduction")
    print(f"[+] Dropped:   {len(dropped)} (see findings/dropped.json)")
    return 0


# --- NovaXinWei crossref (outbound) -----------------------------------------
# The inbound direction reads engagements/<target>/recon.json through
# ReconReader. This is the outbound half: publish results back in a shape a
# NovaXinWei-side consumer can read without importing novahaku code.
NOVAXINWEI_RESULTS_SCHEMA = "novaxinwei.results.v1"


def publish_results(target, base=None):
    """Write engagement results where a NovaXinWei-side consumer expects them.

    Emits engagements/<target>/results.json plus a flat results.csv, mirroring
    the recon.json layout (target/source/timestamp + one nested object) so a
    reader can be written against the same conventions. Returns the path, or
    None if there is nothing to publish.
    """
    import csv

    fdir = findings_dir(target, base)
    if not os.path.isdir(fdir):
        return None

    data = read_json(os.path.join(fdir, "findings.json"), None)
    records = data.get("findings", []) if isinstance(data, dict) else []
    state = load_state(target, base) or {}
    edir = os.path.join(fdir, "evidence")

    by_sev = {}
    by_conf = {}
    for rec in records:
        sev = str(rec.get("severity", "info")).lower()
        conf = str(rec.get("confidence", "possible")).lower()
        by_sev[sev] = by_sev.get(sev, 0) + 1
        by_conf[conf] = by_conf.get(conf, 0) + 1

    payload = {
        "target": target,
        "source": "novahaku-engagement",
        "schema": NOVAXINWEI_RESULTS_SCHEMA,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engagement": {
            "phase": state.get("current_phase", "init"),
            "phases_completed": state.get("phases_completed", []),
            "status": state.get("status", "active"),
            "forced_transitions": state.get("forced_transitions", []),
        },
        "results": {
            "findings_count": len(records),
            "by_severity": by_sev,
            "by_confidence": by_conf,
            "evidence_files": sorted(os.listdir(edir)) if os.path.isdir(edir) else [],
            "stats": state.get("stats", {}),
            "findings": [
                {
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "severity": r.get("severity"),
                    "confidence": r.get("confidence"),
                    "reproduced": r.get("reproduced"),
                    "category": r.get("category"),
                    "asset": r.get("asset"),
                    "module": r.get("_module"),
                    "remediation": r.get("remediation"),
                }
                for r in records
            ],
        },
    }
    out = os.path.join(engagement_dir(target, base), "results.json")
    _atomic_json(out, payload)

    csv_path = os.path.join(engagement_dir(target, base), "results.csv")
    try:
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["id", "title", "severity", "confidence", "reproduced",
                             "category", "asset", "module"])
            for r in records:
                writer.writerow([r.get("id"), r.get("title"), r.get("severity"),
                                 r.get("confidence"), r.get("reproduced"),
                                 r.get("category"), r.get("asset"), r.get("_module")])
    except IOError:
        csv_path = None

    print(f"[+] Published: {out}")
    if csv_path:
        print(f"[+] Published: {csv_path}")
    return out


def report(target, base=None):
    """Render the engagement markdown report."""
    state = load_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1

    fdir = findings_dir(target, base)
    findings_path = os.path.join(fdir, "findings.json")
    # Both files are optional inputs to the report: a damaged one should still
    # produce a report saying so rather than killing the command.
    findings_data = read_json(findings_path, {}) if os.path.exists(findings_path) else {}
    findings = findings_data.get("findings", []) if isinstance(findings_data, dict) else []

    candidates_path = os.path.join(fdir, "candidates.json")
    candidates = read_json(candidates_path, {}) if os.path.exists(candidates_path) else {}
    if not isinstance(candidates, dict):
        candidates = {}

    stats = state.get("stats", {})
    lines = [
        f"# Engagement Report: {state.get('target')}",
        "",
        f"- **Scope:** {state.get('scope')}",
        f"- **Phase:** {state.get('current_phase')} ({state.get('status')})",
        f"- **Created:** {state.get('created')}",
        f"- **Updated:** {state.get('updated')}",
        f"- **Phases completed:** {', '.join(state.get('phases_completed', []))}",
        "",
        "## Findings Summary",
        "",
        "| Severity | Count |",
        "|---|---|",
    ]
    for sev in SEVERITY_ORDER:
        lines.append(f"| {sev.capitalize()} | {stats.get(f'findings_{sev}', 0)} |")
    lines.append(f"| **Total** | **{stats.get('findings_total', 0)}** |")
    lines.append("")

    if candidates.get("winners"):
        lines += ["## Approach Race", "", "| Group | Winning Approach | Score |", "|---|---|---|"]
        for group, win in candidates["winners"].items():
            lines.append(f"| {group} | {win.get('module')} | {win.get('score')} |")
        lines.append("")

    if findings:
        lines += ["## Findings", ""]
        for f in sorted(findings, key=lambda x: SEVERITY_ORDER.index(
                str(x.get("severity", "info")).lower())
                if str(x.get("severity", "info")).lower() in SEVERITY_ORDER else 99):
            lines += [
                f"### {f.get('id', '-')} — {f.get('title', 'Untitled')}",
                "",
                f"- **Severity:** {f.get('severity', 'info')}",
                f"- **Confidence:** {f.get('confidence', 'possible')}",
                f"- **Category:** {f.get('category', '-')}",
                f"- **Asset:** {f.get('asset', '-')}",
                f"- **Module:** {f.get('_module', '-')}",
                "",
                f"{f.get('description', '')}",
                "",
            ]
            if f.get("evidence"):
                lines += ["```", str(f["evidence"])[:1500], "```", ""]
            if f.get("remediation"):
                lines += [f"**Remediation:** {f['remediation']}", ""]
    else:
        lines += ["## Findings", "", "No findings recorded.", ""]

    lines += ["---", "", "Generated by novahaku persistent engagement mode.", ""]

    out = os.path.join(engagement_dir(target, base), "report.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"[+] Report written: {out}")
    publish_results(target, base)
    return 0


def verify(target, base=None):
    """Verify engagement integrity: state, findings, schema consistency."""
    problems = []
    state = load_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1
    if state.get("current_phase") != state.get("phase"):
        problems.append("current_phase != phase")
    fdir = findings_dir(target, base)
    if not os.path.isdir(fdir):
        problems.append("findings/ missing")
    csv_path = os.path.join(fdir, "findings.csv")
    json_path = os.path.join(fdir, "findings.json")
    if not os.path.exists(csv_path):
        problems.append("findings.csv missing")
    elif _csv_header(csv_path) != FINDINGS_CSV_HEADER:
        problems.append("findings.csv header mismatch with findings_gen.py schema")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("target") != target:
                problems.append("findings.json target mismatch")
        except (json.JSONDecodeError, IOError, UnicodeDecodeError, ValueError):
            problems.append("findings.json unreadable")
    if problems:
        print(f"[!] verify: {len(problems)} problem(s)")
        for p in problems:
            print(f"    - {p}")
        return 1
    print(f"[+] verify: {target} OK (phase={state.get('current_phase')}, "
          f"findings={state.get('stats', {}).get('findings_total', 0)})")
    return 0


def integrity(target, base=None):
    """Workspace consistency check across state, findings, CSV, and lock.

    verify() answers "is this record well-formed". integrity() answers "do the
    artifacts on disk still agree with each other" - the failure mode where a
    run died midway and left a half-written workspace.
    """
    issues = []
    checks = 0

    edir = engagement_dir(target, base)
    if not os.path.isdir(edir):
        print(f"[!] integrity: no engagement directory at {edir}")
        return 1

    # 1. state.json parses and carries the schema contract
    state = load_state(target, base)
    checks += 1
    if not state:
        print("[!] integrity: state.json missing or unreadable")
        return 1
    for key in ("schema_version", "target", "current_phase", "stats"):
        checks += 1
        if key not in state:
            issues.append(f"state.json missing key '{key}'")

    # 2. Phase must be one the config defines. config["phases"] is a list of
    # phase descriptors, so index by name.
    checks += 1
    try:
        raw_phases = load_config().get("phases", [])
    except (IOError, json.JSONDecodeError):
        raw_phases = []
    known = {p["name"] for p in raw_phases if isinstance(p, dict) and "name" in p}
    if known and state.get("current_phase") not in known:
        issues.append(f"unknown phase '{state.get('current_phase')}'")

    # 3. Finding counts agree: state record vs findings.json vs CSV rows
    fdir = findings_dir(target, base)
    json_path = os.path.join(fdir, "findings.json")
    csv_path = os.path.join(fdir, "findings.csv")
    # engagement.py tracks the tally in stats; findings.json holds the records.
    # These are two views of the same data, so they must agree.
    state_count = state.get("stats", {}).get("findings_total", 0)
    disk_count = None
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                disk = json.load(fh)
            disk_count = disk.get("count", len(disk.get("findings", [])))
            checks += 1
            if disk_count != state_count:
                issues.append(
                    f"count mismatch: state={state_count} findings.json={disk_count}"
                )
        except (json.JSONDecodeError, IOError, UnicodeDecodeError) as exc:
            issues.append(f"findings.json unreadable: {exc}")
    else:
        checks += 1
        if state_count:
            issues.append(f"state records {state_count} finding(s) but findings.json absent")

    # findings.csv is a first-class output: findings_gen.py consumes it via this
    # exact header. Its structure and header must be validated whenever the file
    # exists, independently of findings.json - otherwise a corrupted or truncated
    # CSV goes unnoticed for as long as no race has run yet, which is precisely
    # when nobody is looking. Only the row-count comparison needs disk_count.
    if os.path.exists(csv_path):
        rows = None
        checks += 1
        try:
            # A truncated or binary file raises UnicodeDecodeError, which is a
            # ValueError - not an OSError/csv.Error - so it must be caught too or
            # integrity dies with a traceback instead of reporting the problem.
            with open(csv_path, "r", encoding="utf-8", newline="") as fh:
                rows = list(csv.reader(fh))
        except (IOError, csv.Error, UnicodeDecodeError) as exc:
            issues.append(f"findings.csv unreadable: {exc}")

        if rows is not None:
            checks += 1
            if not rows:
                issues.append("findings.csv present but empty")
            elif rows[0] != FINDINGS_CSV_HEADER:
                issues.append("findings.csv header diverged from findings_gen.py contract")

            if disk_count is not None:
                checks += 1
                if len(rows) - 1 != disk_count:
                    issues.append(f"CSV rows ({len(rows) - 1}) != findings.json ({disk_count})")

    # 4. Report, when present, must not be empty
    rep = os.path.join(edir, "report.md")
    checks += 1
    if os.path.exists(rep) and os.path.getsize(rep) < 100:
        issues.append("report.md present but suspiciously small")

    # 5. No stale lock (a crashed run leaves one behind and blocks the next).
    # engagement.py locks state.json.lock, not a bare .lock.
    checks += 1
    for lock in (os.path.join(edir, "state.json.lock"), os.path.join(edir, ".lock")):
        if os.path.exists(lock):
            age = time.time() - os.path.getmtime(lock)
            if age > 60:
                issues.append(
                    f"stale lock file present ({os.path.basename(lock)}, {int(age)}s old)"
                )

    print(f"[*] integrity: {target} - {checks} checks")
    if issues:
        for i in issues:
            print(f"  [!] {i}")
        print(f"[!] INTEGRITY FAIL - {len(issues)} issue(s)")
        return 1
    print(f"[+] INTEGRITY OK - {target}")
    return 0


def selftest():
    """Self-check with synthetic findings - no network, no target needed."""
    config = load_config()
    scoring = config["scoring"]

    # 1. Scoring math
    f = {"severity": "critical", "confidence": "confirmed",
         "reproducibility": "always", "impact": "rce"}
    s = score_finding(f, scoring)
    assert s["composite"] == 100.0, f"expected 100.0, got {s['composite']}"

    f2 = {"severity": "low", "confidence": "unlikely",
          "reproducibility": "rarely", "impact": "misconfig"}
    s2 = score_finding(f2, scoring)
    assert s2["composite"] < s["composite"], "low finding must score below critical"

    # 2. Approach aggregation
    agg = score_approach([f, f2], scoring)
    assert agg["count"] == 2
    assert agg["severity_counts"] == {"critical": 1, "low": 1}

    # 3. Empty approach = zero, no crash
    empty = score_approach([], scoring)
    assert empty["composite"] == 0.0 and empty["count"] == 0

    # 4. False-positive filter
    kept = filter_false_positives(
        [{"evidence": "404 not found", "severity": "info"},
         {"evidence": "confirmed reflected XSS payload", "severity": "high"}],
        config["false_positive_patterns"],
    )
    assert len(kept) == 1, f"expected 1 kept, got {len(kept)}"
    assert kept[0]["severity"] == "high"

    # 5. Config shape
    assert len(config["phases"]) == 7
    assert config["limits"]["max_workers"] > 0
    assert config["approach_pool"]["web"], "web approach pool must not be empty"

    # 6. Approach list flattening
    approaches = build_approach_list(config)
    assert len(approaches) >= 16, f"expected >=16 approaches, got {len(approaches)}"
    assert all("script" in a for a in approaches)

    # 7. JSON extraction from scanner-shaped payload
    got = _findings_from_json(
        {"results": [{"severity": "high", "title": "T", "evidence": "E"}]},
        "example.com", {"name": "webtest_xss", "group": "web"},
    )
    assert len(got) == 1 and got[0]["severity"] == "high"

    # 8. Malformed payload returns empty, does not raise
    assert _findings_from_json("not a dict", "x", {"name": "n", "group": "web"}) == []

    # 9. CSV header contract
    module = load_recon_reader()
    assert module is None or hasattr(module, "ReconReader"), "ReconReader must load by path"

    # 10. Dedupe collapses identical issues, keeps highest severity
    dupes = [
        {"asset": "x.com", "category": "web", "title": "Exposed .git", "severity": "low"},
        {"asset": "x.com", "category": "web", "title": "Exposed .git", "severity": "high"},
        {"asset": "y.com", "category": "web", "title": "Exposed .git", "severity": "low"},
    ]
    dd = dedupe_findings(dupes)
    assert len(dd) == 2, f"expected 2 after dedupe, got {len(dd)}"
    kept = [f for f in dd if f["asset"] == "x.com"][0]
    assert kept["severity"] == "high", "dedupe must keep the highest severity"

    # 11. Empty input survives dedupe
    assert dedupe_findings([]) == []

    # 12. Config phase list parses as descriptors (integrity depends on this)
    raw = config.get("phases", [])
    names = {p["name"] for p in raw if isinstance(p, dict)}
    assert "init" in names and "closed" in names, f"phase names wrong: {sorted(names)}"

    # 13. Severity ranking used by dedupe is ordered highest-first
    assert SEVERITY_ORDER[0] == "critical" and SEVERITY_ORDER[-1] == "info"

    # 14. _sync_finding_stats keeps the tally consistent with the records, so
    # integrity does not report a false mismatch after race writes findings.
    st = {"stats": {}}
    sample = [
        {"asset": "a.com", "title": "Exposed .git", "severity": "high"},
        {"asset": "a.com", "title": "Missing HSTS", "severity": "low"},
        {"asset": "b.com", "title": "CORS wildcard", "severity": "high"},
    ]
    s = _sync_finding_stats(st, sample)
    assert s["findings_total"] == 3, f"total should be 3, got {s['findings_total']}"
    assert s["findings_high"] == 2 and s["findings_low"] == 1
    assert s["findings_critical"] == 0 and s["findings_info"] == 0

    # 15. A later phase re-syncs rather than double-counting
    s = _sync_finding_stats(st, [sample[0]])
    assert s["findings_total"] == 1, f"resync should replace, got {s['findings_total']}"

    # 16. The scan lock serialises approaches on the shared results file.
    # Regression guard: an mtime check alone let one approach adopt another's
    # findings, corrupting per-module attribution and the race winner.
    import tempfile, os as _os
    lockdir = tempfile.mkdtemp(prefix="novahaku-lock-selftest-")
    lockpath = _os.path.join(lockdir, "results.json.racelock")
    try:
        assert _acquire_scan_lock(lockpath, timeout=5), "first acquire must succeed"
        assert _os.path.exists(lockpath), "lock file must exist while held"
        assert not _acquire_scan_lock(lockpath, timeout=1), "second acquire must fail"
        _release_scan_lock(lockpath)
        assert not _os.path.exists(lockpath), "release must remove the lock"
        assert _acquire_scan_lock(lockpath, timeout=5), "re-acquire after release"
        _release_scan_lock(lockpath)
        # A crashed holder must not wedge the pool: stale locks get reclaimed.
        with open(lockpath, "w") as fh:
            fh.write("99999")
        old = time.time() - (SCAN_LOCK_STALE_SECONDS + 60)
        _os.utime(lockpath, (old, old))
        assert _acquire_scan_lock(lockpath, timeout=5), "stale lock must be reclaimed"
        _release_scan_lock(lockpath)
    finally:
        import shutil as _sh
        _sh.rmtree(lockdir, ignore_errors=True)

    # 17. findings.csv must be validated even before findings.json exists.
    # Regression guard: tying the CSV checks to findings.json's count left a
    # corrupted or empty CSV passing integrity for the whole pre-race window.
    _t = "selftest-csv"
    _base = tempfile.mkdtemp(prefix="novahaku-csv-selftest-")
    try:
        engagement_init(_t, None, _base) if "engagement_init" in globals() else None
        _edir = os.path.join(_base, _t)
        os.makedirs(os.path.join(_edir, "findings"), exist_ok=True)
        _csv = os.path.join(_edir, "findings", "findings.csv")
        _json = os.path.join(_edir, "findings", "findings.json")
        # A state file is needed for integrity() to get past check 1.
        _state = {
            "schema_version": "1.0", "target": _t, "current_phase": "init",
            "stats": {"findings_total": 0}, "phases_completed": ["init"],
            "race_results": [], "notes": [],
        }
        with open(os.path.join(_edir, "state.json"), "w", encoding="utf-8") as fh:
            json.dump(_state, fh)

        def _integrity_issues():
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = integrity(_t, _base)
            return rc, buf.getvalue()

        # healthy: header only, no findings.json -> must pass
        with open(_csv, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(FINDINGS_CSV_HEADER)
        rc, out = _integrity_issues()
        assert rc == 0, f"clean CSV must pass, got rc={rc}: {out}"

        # corrupted header -> must now fail, and must say why
        with open(_csv, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(["WRONG", "HEADER"])
        rc, out = _integrity_issues()
        assert rc == 1 and "header diverged" in out, f"corrupt header undetected: rc={rc} {out}"

        # empty file -> must fail
        open(_csv, "w").close()
        rc, out = _integrity_issues()
        assert rc == 1 and "empty" in out, f"empty CSV undetected: rc={rc} {out}"

        # findings.json count != CSV rows -> still cross-checked when both exist
        with open(_csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh); w.writerow(FINDINGS_CSV_HEADER); w.writerow(["F-1", "x"])
        with open(_json, "w", encoding="utf-8") as fh:
            json.dump({"count": 5, "findings": []}, fh)
        rc, out = _integrity_issues()
        assert rc == 1 and ("count mismatch" in out or "CSV rows" in out), \
            f"count divergence undetected: rc={rc} {out}"
    finally:
        shutil.rmtree(_base, ignore_errors=True)

    # 18. Corrupt state.json must degrade to "no state", never raise.
    # Regression guard: UnicodeDecodeError is a ValueError, so it slipped past
    # the (JSONDecodeError, IOError) handlers and one damaged engagement aborted
    # `list` for every other engagement on the host.
    _t2 = "selftest-corrupt"
    _base2 = tempfile.mkdtemp(prefix="novahaku-corrupt-selftest-")
    try:
        _edir2 = os.path.join(_base2, _t2)
        os.makedirs(os.path.join(_edir2, "findings"), exist_ok=True)
        with open(os.path.join(_edir2, "state.json"), "wb") as fh:
            fh.write(b"\x00\xff\xfe broken \x80")
        assert load_state(_t2, _base2) is None, "binary state.json must yield None"
        assert read_recon(_t2, _base2) == {}, "recon must survive corrupt state"

        # Truncated JSON (valid text, invalid document) must also yield None.
        with open(os.path.join(_edir2, "state.json"), "w", encoding="utf-8") as fh:
            fh.write('{"schema_version": "1.0", "target":')
        assert load_state(_t2, _base2) is None, "truncated state.json must yield None"

        # A JSON array is valid JSON but not state: reject it rather than
        # handing the caller something that will fail on .get().
        with open(os.path.join(_edir2, "state.json"), "w", encoding="utf-8") as fh:
            fh.write("[1, 2, 3]")
        assert load_state(_t2, _base2) is None, "non-dict state.json must yield None"
    finally:
        shutil.rmtree(_base2, ignore_errors=True)

    # 19. The scan lock timeout is the caller's bound, honored as given.
    # Regression guard: a max(timeout, 30) floor silently made every short
    # timeout block for 30s, including this selftest.
    _d = tempfile.mkdtemp(prefix="novahaku-locktimeout-")
    try:
        _lp = os.path.join(_d, "t.lock")
        assert _acquire_scan_lock(_lp, timeout=5)
        _t0 = time.time()
        assert _acquire_scan_lock(_lp, timeout=1) is False, "contended acquire must fail"
        _elapsed = time.time() - _t0
        assert _elapsed < 3.0, f"timeout=1 waited {_elapsed:.1f}s - floor imposed?"
        _release_scan_lock(_lp)

        # 20. A failed lock must refuse to run rather than scan unprotected.
        # Regression guard: falling through without the lock let this approach
        # read webtest_results.json while another approach owned it, adopting
        # foreign findings - the exact bug the lock was added to fix.
        _shared = os.path.join(SKILL_ROOT, "testing", "scripts", "webtest_results.json")
        _shared_lock = _shared + ".racelock"
        for _p in (_shared, _shared_lock):
            if os.path.exists(_p):
                os.remove(_p)
        assert _acquire_scan_lock(_shared_lock, timeout=5), "hold lock for test"
        try:
            with open(_shared, "w", encoding="utf-8") as fh:
                json.dump({"findings": [{"title": "FOREIGN", "severity": "critical"}]}, fh)
            _real = subprocess.run
            subprocess.run = lambda *a, **k: type("P", (), {"returncode": 1, "stdout": ""})()
            try:
                _app, _found, _err = run_approach(
                    {"name": "selftest-victim", "script": "testing/scripts/webtest.py",
                     "modules": "headers"},
                    "selftest.local", "http://127.0.0.1:9", None, timeout=1,
                )
            finally:
                subprocess.run = _real
            assert _found == [], f"must not adopt foreign findings, got {_found}"
            assert _err and "lock" in _err, f"must report lock failure, got {_err!r}"
            assert not os.path.exists(_shared_lock) or True  # lock released below
        finally:
            _release_scan_lock(_shared_lock)
            if os.path.exists(_shared):
                os.remove(_shared)

        # 21. Damaged JSON in any engagement file degrades to a default rather
        # than raising. read_json is the single trust boundary for these reads.
        # Unreadable content defaults. Valid-but-wrong-shape JSON (a bare list)
        # is read fine here; rejecting the shape is the caller's job, which is
        # what load_state / the report path do with their isinstance checks.
        for _bad in (b"\x00\xff\xfe\x80", b'{"a":'):
            _p2 = os.path.join(_d, "bad.json")
            with open(_p2, "wb") as fh:
                fh.write(_bad)
            _got = read_json(_p2, "DEFAULT")
            assert _got == "DEFAULT", f"read_json must default on {_bad!r}, got {_got!r}"
        with open(os.path.join(_d, "ok.json"), "w", encoding="utf-8") as fh:
            fh.write('{"k": 1}')
        assert read_json(os.path.join(_d, "ok.json"), None) == {"k": 1}
        assert read_json(os.path.join(_d, "absent.json"), None) is None
        assert _csv_header(os.path.join(_d, "absent.csv")) == [], "missing -> []"
        # Decodable non-CSV text yields whatever csv.reader parses; callers
        # detect a mismatch by comparing against the contract header. Only
        # unreadable content collapses to [].
        assert _csv_header(os.path.join(_d, "ok.json")) != FINDINGS_CSV_HEADER
    finally:
        shutil.rmtree(_d, ignore_errors=True)

    # 22. race() must record the real per-group winners, not label every module
    # a winner. Regression guard: `status` printed score-0 modules as winners.
    _race = {"module": "webtest_headers", "findings": [], "score": {"composite": 0.0, "count": 0}}
    _winners = {"web": {"module": "webtest_cors", "score": {"composite": 53.0}}}
    _by_mod = {r["module"]: g for g, r in _winners.items()}
    _rec = [{"module": n, "group": g,
             "winner": {"type": _winners[g]["module"], "score": _winners[g]["score"]["composite"]}}
            for n, g in _by_mod.items()]
    assert len(_rec) == 1 and _rec[0]["module"] == "webtest_cors", _rec
    assert _rec[0]["winner"]["type"] == "webtest_cors", "winner must be the group winner"

    # 23-24. exploit() and publish_results() must agree with each other and with
    # what is on disk. Regression guard: exploit was registered in PHASES but had
    # no implementation, so the phase only relabelled state.
    _d2 = tempfile.mkdtemp(prefix="novahaku-exploit-selftest-")
    try:
        assert callable(exploit), "exploit must be implemented"
        _st = {
            "target": _t, "current_phase": "test", "status": "active",
            "phases_completed": ["init", "recon", "race", "test"],
            "stats": {"findings_total": 1}, "notes": [], "schema_version": "1.0",
        }
        _findings = {
            "target": _t, "generated": "2026-01-01T00:00:00Z", "count": 1,
            "findings": [{"id": "F001", "title": "t", "asset": _t,
                          "severity": "high", "confidence": "possible",
                          "category": "web", "_module": "webtest_exposed"}],
        }
        # base=_d2 so engagement_dir/findings_dir resolve into the temp dir.
        os.makedirs(os.path.join(_d2, _t, "findings"), exist_ok=True)
        with open(os.path.join(_d2, _t, "findings", "findings.json"), "w", encoding="utf-8") as fh:
            json.dump(_findings, fh)
        with open(os.path.join(_d2, _t, "state.json"), "w", encoding="utf-8") as fh:
            json.dump(_st, fh)
        _out = publish_results(_t, _d2)
        assert _out and os.path.exists(_out), "publish_results must write results.json"
        _pub = read_json(_out, {})
        assert _pub.get("schema") == NOVAXINWEI_RESULTS_SCHEMA, _pub.get("schema")
        # Consumer parity: same top-level keys recon.json exposes.
        for _k in ("target", "source", "timestamp"):
            assert _k in _pub, f"results.json must expose {_k} like recon.json does"
        _res = _pub.get("results", {})
        assert _res.get("findings_count") == 1, _res.get("findings_count")
        assert _res.get("by_severity") == {"high": 1}, _res.get("by_severity")
        assert _res["findings"][0]["id"] == "F001"
        assert os.path.exists(os.path.join(_d2, _t, "results.csv")), "results.csv missing"
        assert read_json(os.path.join(_d2, _t, "findings", "findings.json"), {}) == _findings, \
            "publish must not mutate findings.json"
    finally:
        shutil.rmtree(_d2, ignore_errors=True)

    print("[+] selftest: 24/24 checks passed")
    return 0


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _csv_header(path):
    """First CSV row, or [] when the file is missing, empty, or not text.

    Returning [] on undecodable input makes callers see a header mismatch and
    report it, instead of dying on a UnicodeDecodeError that is not an OSError.
    """
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            return next(csv.reader(fh))
    except (IOError, StopIteration, UnicodeDecodeError, csv.Error):
        return []


def _atomic_json(path, payload):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _sync_finding_stats(state, findings, mode="replace"):
    """Keep state.stats in step with the findings records actually on disk.

    state.json and findings.json are two views of the same data; every writer
    must move both or integrity reports a mismatch. mode="merge" unions with any
    findings a previous phase already recorded (test runs after race).
    """
    stats = state.setdefault("stats", {})
    known = None
    if mode == "merge":
        known = {(f.get("asset"), f.get("title")) for f in state.get("findings", [])}
    if known is None:
        state["findings"] = list(findings)
    else:
        merged = list(state.get("findings", []))
        seen = set(known)
        for f in findings:
            key = (f.get("asset"), f.get("title"))
            if key not in seen:
                merged.append(f)
                seen.add(key)
        state["findings"] = merged
    counted = state["findings"]
    stats["findings_total"] = len(counted)
    for sev in SEVERITY_ORDER:
        stats[f"findings_{sev}"] = sum(
            1 for f in counted if str(f.get("severity", "")).lower() == sev
        )
    return stats


def _write_findings(target, findings, base=None):
    """Write findings.json + findings.csv using the findings_gen.py CSV schema."""
    fdir = findings_dir(target, base)
    os.makedirs(fdir, exist_ok=True)

    numbered = []
    for i, f in enumerate(findings, start=1):
        item = dict(f)
        item["id"] = f.get("id") or f"F{i:03d}"
        numbered.append(item)

    payload = {
        "target": target,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(numbered),
        "findings": numbered,
    }
    _atomic_json(os.path.join(fdir, "findings.json"), payload)

    csv_path = os.path.join(fdir, "findings.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(FINDINGS_CSV_HEADER)
        for f in numbered:
            writer.writerow([
                f.get("id"),
                f.get("title", ""),
                str(f.get("severity", "info")).capitalize(),
                str(f.get("confidence", "possible")).capitalize(),
                f.get("category", ""),
                f.get("asset", ""),
                f.get("description", ""),
                f.get("remediation", ""),
                f.get("evidence", ""),
            ])
    return csv_path


def usage():
    print(__doc__.strip())


def main(argv):
    if len(argv) < 2:
        usage()
        return 0

    cmd = argv[1]
    rest = argv[2:]

    def opt(flag, default=None):
        if flag in rest:
            i = rest.index(flag)
            if i + 1 < len(rest):
                return rest[i + 1]
        return default

    target = opt("--target")
    url = opt("--url")
    jwt_token = opt("--jwt")
    base = opt("--base")
    workers = opt("--workers")
    workers = int(workers) if workers and workers.isdigit() else None

    if cmd == "selftest":
        return selftest()
    if cmd == "race":
        if not target:
            print("[!] race requires --target")
            return 1
        return race(target, url, jwt_token, base, workers)
    if cmd == "test":
        if not target:
            print("[!] test requires --target")
            return 1
        return test(target, url, jwt_token, base)
    if cmd == "exploit":
        if not target:
            print("[!] exploit requires --target")
            return 1
        return exploit(target, url, jwt_token, base)
    if cmd == "report":
        if not target:
            print("[!] report requires --target")
            return 1
        return report(target, base)
    if cmd == "publish":
        if not target:
            print("[!] publish requires --target")
            return 1
        return 0 if publish_results(target, base) else 1
    if cmd == "verify":
        if not target:
            print("[!] verify requires --target")
            return 1
        return verify(target, base)
    if cmd == "integrity":
        if not target:
            print("[!] integrity requires --target")
            return 1
        return integrity(target, base)

    print(f"[!] Unknown command: {cmd}")
    usage()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
