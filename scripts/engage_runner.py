#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engage_runner.py - Engagement test orchestration with approach racing (stdlib-only)

Races candidate testing approaches in parallel, scores them, and writes
structured findings into the engagement workspace. Reads the approach pool
and scoring tables from config/engagement_phases.json.

Usage:
  python engage_runner.py race      --target <target> [--url URL] [--jwt TOKEN] [--workers N]
  python engage_runner.py test      --target <target> [--url URL] [--jwt TOKEN]
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
FINDINGS_CSV_HEADER = [
    "ID", "Title", "Severity", "Confidence", "Category",
    "Asset / Host", "Description", "Remediation", "Evidence",
]


# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

def load_config(path=None):
    path = path or CONFIG_PATH
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_state(target, base=None):
    path = os.path.join(engagement_dir(target, base), "state.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


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

    # webtest.py writes webtest_results.json next to itself (not to CWD), so
    # parallel approaches would clobber one shared file. Timestamp it before the
    # run and only trust it if this approach actually rewrote it.
    shared_results = os.path.join(SKILL_ROOT, "testing", "scripts", "webtest_results.json")
    before_mtime = os.path.getmtime(shared_results) if os.path.exists(shared_results) else 0

    workdir = tempfile.mkdtemp(prefix="novahaku-approach-")
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=workdir
        )
        # Use the shared file only when this run is the one that wrote it.
        fresh = None
        if os.path.exists(shared_results) and os.path.getmtime(shared_results) > before_mtime:
            fresh = shared_results
        findings = parse_scanner_output(proc.stdout, target, approach, fresh)
        if proc.returncode != 0 and not findings:
            return approach, [], f"exit {proc.returncode}"
        return approach, findings, None
    except subprocess.TimeoutExpired:
        return approach, [], f"timeout after {timeout}s"
    except OSError as exc:
        return approach, [], f"exec failed: {exc}"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


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
        try:
            with open(results_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            findings.extend(_findings_from_json(data, target, approach))
        except (json.JSONDecodeError, IOError):
            pass
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

    state["race_results"] = [
        {"module": r["module"],
         "approaches_tested": len(runnable),
         "winner": {"type": r["module"], "score": r["score"]["composite"]},
         "timestamp": race_payload["timestamp"]}
        for r in results[:10]
    ]
    state["stats"]["modules_tested"] = len(runnable)
    state["stats"]["modules_failed"] = len(errors)
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

    with open(candidates_path, "r", encoding="utf-8") as fh:
        candidates = json.load(fh)

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

    state["stats"]["findings_total"] = len(all_findings)
    for sev in SEVERITY_ORDER:
        state["stats"][f"findings_{sev}"] = sum(
            1 for f in all_findings if str(f.get("severity", "info")).lower() == sev
        )
    state["findings_references"] = [
        {"id": f.get("id"), "file": "findings/findings.json",
         "severity": str(f.get("severity", "info")).lower()}
        for f in all_findings
    ]
    save_state(target, state, base)
    print(f"[+] {len(all_findings)} finding(s) written to {fdir}")
    return 0


def report(target, base=None):
    """Render the engagement markdown report."""
    state = load_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1

    fdir = findings_dir(target, base)
    findings_path = os.path.join(fdir, "findings.json")
    findings = []
    if os.path.exists(findings_path):
        with open(findings_path, "r", encoding="utf-8") as fh:
            findings = json.load(fh).get("findings", [])

    candidates_path = os.path.join(fdir, "candidates.json")
    candidates = {}
    if os.path.exists(candidates_path):
        with open(candidates_path, "r", encoding="utf-8") as fh:
            candidates = json.load(fh)

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
        except (json.JSONDecodeError, IOError):
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
        except (json.JSONDecodeError, IOError) as exc:
            issues.append(f"findings.json unreadable: {exc}")
    else:
        checks += 1
        if state_count:
            issues.append(f"state records {state_count} finding(s) but findings.json absent")

    if os.path.exists(csv_path) and disk_count is not None:
        checks += 1
        try:
            with open(csv_path, "r", encoding="utf-8", newline="") as fh:
                rows = list(csv.reader(fh))
            checks += 1
            if rows and rows[0] != FINDINGS_CSV_HEADER:
                issues.append("findings.csv header diverged from findings_gen.py contract")
            checks += 1
            if len(rows) - 1 != disk_count:
                issues.append(f"CSV rows ({len(rows) - 1}) != findings.json ({disk_count})")
        except (IOError, csv.Error) as exc:
            issues.append(f"findings.csv unreadable: {exc}")

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

    print("[+] selftest: 13/13 checks passed")
    return 0


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _csv_header(path):
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            return next(csv.reader(fh))
    except (IOError, StopIteration):
        return []


def _atomic_json(path, payload):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


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
    if cmd == "report":
        if not target:
            print("[!] report requires --target")
            return 1
        return report(target, base)
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
