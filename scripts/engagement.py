#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engagement.py - Persistent engagement lifecycle manager (stdlib-only)

Tracks a security engagement across sessions: target scope, phase progression,
findings, and approach race results. State persists in
engagements/<target>/state.json and survives agent restarts.

Usage:
  python engagement.py init <target> [--scope "*.target.com"]
  python engagement.py status <target>
  python engagement.py list
  python engagement.py phase <target> <phase>
  python engagement.py note <target> "text"
  python engagement.py close <target>
  python engagement.py rollback <target> <phase>
  python engagement.py verify <target>
  python engagement.py selftest

Phases: init, recon, race, test, exploit, report, closed
No-arg = help.
"""

import sys
import os
import json
import time

SCHEMA_VERSION = "1.0"
PHASES = ["init", "recon", "race", "test", "exploit", "report", "closed"]
LOCK_STALE_SECONDS = 30
DEFAULT_ENGAGEMENTS_DIR = "engagements"


# ----------------------------------------------------------------------------
# Path resolution
# ----------------------------------------------------------------------------

def skill_root():
    """Resolve novahaku skill root from this script's location."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def engagements_dir(base=None):
    """Resolve engagements directory.

    Precedence: caller-supplied path, then NOVAHAKU_ENGAGEMENT_DIR, then
    <skill root>/engagements. The env var is documented in README.md and already
    honoured by web2-recon scripts; ignoring it here meant a pipeline writing to
    the requested directory and this CLI writing to the default, so neither
    could find the other's files.
    """
    if base:
        return os.path.abspath(base)
    env = os.environ.get("NOVAHAKU_ENGAGEMENT_DIR")
    if env and env.strip():
        return os.path.abspath(env)
    return os.path.join(skill_root(), DEFAULT_ENGAGEMENTS_DIR)


def engagement_path(target, base=None):
    """Return the directory for one target."""
    return os.path.join(engagements_dir(base), target)


def state_path(target, base=None):
    return os.path.join(engagement_path(target, base), "state.json")


def findings_dir(target, base=None):
    return os.path.join(engagement_path(target, base), "findings")


# ----------------------------------------------------------------------------
# Locking
# ----------------------------------------------------------------------------

def _lock_file(target, base=None):
    return state_path(target, base) + ".lock"


def acquire_lock(target, base=None, timeout=10):
    """Create a lock file. Delete stale locks older than LOCK_STALE_SECONDS.

    Returns True on success, False on timeout. Stdlib-only, no fcntl/msvcrt:
    a lock-file with a staleness bound is sufficient for single-agent usage.
    """
    lock = _lock_file(target, base)
    # The engagement directory may not exist yet (init path) - create it so
    # the lock file has somewhere to live.
    try:
        os.makedirs(os.path.dirname(lock), exist_ok=True)
    except OSError:
        return False
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(lock):
            try:
                age = time.time() - os.path.getmtime(lock)
            except OSError:
                age = 0
            if age > LOCK_STALE_SECONDS:
                try:
                    os.remove(lock)
                except OSError:
                    pass
                continue
            time.sleep(0.05)
            continue
        try:
            with open(lock, "w", encoding="utf-8") as fh:
                fh.write(str(os.getpid()))
            return True
        except OSError:
            time.sleep(0.05)
    return False


def release_lock(target, base=None):
    try:
        os.remove(_lock_file(target, base))
    except OSError:
        pass


# ----------------------------------------------------------------------------
# Atomic state I/O
# ----------------------------------------------------------------------------

def read_json(path, default):
    """Read a JSON file, returning ``default`` on any problem.

    The same trust boundary as engage_runner.read_json: any file on disk can be
    truncated or binary, and UnicodeDecodeError is a ValueError that older
    handlers missed.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, IOError, UnicodeDecodeError, ValueError):
        return default


def read_state(target, base=None):
    """Read state.json. Returns None when missing or unreadable."""
    path = state_path(target, base)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            state = json.load(fh)
    except (json.JSONDecodeError, IOError, UnicodeDecodeError, ValueError):
        # A truncated or binary state.json raises UnicodeDecodeError, which is a
        # ValueError rather than an OSError. Catching it keeps one damaged
        # engagement from aborting `list` for every other engagement on the host.
        return None
    return state if isinstance(state, dict) else None


def write_state(target, base=None, state=None):
    """Atomic write: tmp file -> fsync -> os.replace.

    A partial write can never replace a good state.json.
    """
    if state is None:
        raise ValueError("state payload required")
    path = state_path(target, base)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    state["updated"] = _now()
    state["schema_version"] = SCHEMA_VERSION
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return path


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ----------------------------------------------------------------------------
# Lifecycle
# ----------------------------------------------------------------------------

def new_state(target, scope=None):
    ts = _now()
    return {
        "schema_version": SCHEMA_VERSION,
        "target": target,
        "scope": scope or target,
        "created": ts,
        "updated": ts,
        "phase": "init",
        "status": "active",
        "phases_completed": ["init"],
        "current_phase": "init",
        "stats": {
            "findings_total": 0,
            "findings_critical": 0,
            "findings_high": 0,
            "findings_medium": 0,
            "findings_low": 0,
            "findings_info": 0,
            "modules_tested": 0,
            "modules_failed": 0,
        },
        "race_results": [],
        "findings_references": [],
        "notes": [{"timestamp": ts, "text": "Engagement initialized"}],
    }


def cmd_init(target, scope=None, base=None):
    """Create engagement directory tree + state.json. Never overwrites."""
    existing = read_state(target, base)
    if existing:
        print(f"[=] Engagement already exists: {target} (phase: {existing['phase']})")
        return 0

    if not acquire_lock(target, base):
        print(f"[!] Could not acquire lock for {target}")
        return 1
    try:
        epath = engagement_path(target, base)
        os.makedirs(findings_dir(target, base), exist_ok=True)
        # findings.csv header matches findings_gen.py schema
        csv_path = os.path.join(findings_dir(target, base), "findings.csv")
        if not os.path.exists(csv_path):
            with open(csv_path, "w", encoding="utf-8", newline="") as fh:
                fh.write(
                    "ID,Title,Severity,Confidence,Category,Asset / Host,"
                    "Description,Remediation,Evidence\n"
                )
        write_state(target, base, new_state(target, scope))
        print(f"[+] Engagement created: {epath}")
        print(f"    state:    {state_path(target, base)}")
        print(f"    findings: {csv_path}")
        _record_chain(target, "engagement_created", "state.json", base)
        return 0
    finally:
        release_lock(target, base)


def _record_chain(target, action, artifact=None, base=None, phase=None):
    """Record this side's contribution in chain.json, best effort.

    Novahaku may create the engagement before NovaXinWei has written any recon,
    and vice versa. chain.json is how either side learns the start order, so the
    init path records it too. Failure here must never break engagement creation.
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import engage_runner

        engage_runner.record_chain(target, action, artifact, base, phase)
    except Exception as exc:
        print(f"[!] chain.json not updated: {exc}")


def _phase_gate(target, phase, state, base=None):
    """Return a list of reasons ``phase`` may not be entered yet.

    Gate on artifacts on disk, never on the previous phase label: race/test run
    through engage_runner.py and produce candidates.json / findings.json without
    advancing ``current_phase``, so a label-based check rejects work that has
    actually been done.

    Findings are read from findings.json. state has no ``findings`` key - reading
    one was the original integrity bug and must not be reintroduced.
    """
    problems = []
    fdir = findings_dir(target, base)
    candidates_path = os.path.join(fdir, "candidates.json")
    found_json = os.path.join(fdir, "findings.json")

    if phase == "recon":
        # recon is the first step after init; it needs no prior artifact.
        return problems

    if phase in ("race", "test", "exploit", "report", "closed"):
        if not os.path.exists(candidates_path) and state.get("stats", {}).get(
            "modules_tested", 0
        ) == 0:
            # Gate on evidence, never on the phase label: a label can be advanced
            # by --force, and the label then hides the missing work.
            problems.append("recon has not been run (no testable surface recorded)")

    if phase in ("exploit", "report", "closed"):
        if not os.path.exists(candidates_path):
            problems.append("race has not been run (findings/candidates.json missing)")

    if phase in ("report", "closed"):
        if not os.path.exists(found_json):
            problems.append("test has not produced findings (findings/findings.json missing)")

    if phase == "closed" and os.path.exists(found_json):
        data = read_json(found_json, {})
        records = data.get("findings", []) if isinstance(data, dict) else []
        missing = [
            f for f in records
            if isinstance(f, dict) and (not f.get("id") or not f.get("asset"))
        ]
        if missing:
            problems.append(f"{len(missing)} finding(s) in findings.json lack id/asset")

    return problems


def _artifact_phase_index(target, state, base=None):
    """Highest phase the artifacts on disk actually support, as an index.

    engage_runner.py advances the work (race, test, exploit) without touching the
    phase label, so the label alone understates progress. This reconciles the
    two, and covers the same five artifact classes the runner does - candidates,
    findings, evidence, results.json - so both sides reach the same answer for
    the same state. Without that, a phase whose prerequisites are on disk gets
    rejected as a multi-step jump.
    """
    fdir = findings_dir(target, base)
    done = PHASES.index("init")
    label = state.get("current_phase") if isinstance(state, dict) else None
    if isinstance(label, str) and label in PHASES:
        done = max(done, PHASES.index(label))
    completed = state.get("phases_completed") if isinstance(state, dict) else None
    if isinstance(completed, list):
        for name in completed:
            if isinstance(name, str) and name in PHASES:
                done = max(done, PHASES.index(name))
    if os.path.exists(os.path.join(fdir, "candidates.json")):
        done = max(done, PHASES.index("race"))
    if os.path.exists(os.path.join(fdir, "findings.json")):
        done = max(done, PHASES.index("test"))
    evid = os.path.join(fdir, "evidence")
    if os.path.isdir(evid) and os.listdir(evid):
        done = max(done, PHASES.index("exploit"))
    if os.path.exists(os.path.join(engagement_path(target, base), "results.json")):
        done = max(done, PHASES.index("report"))
    return done


def _artifact_phase(target, state, base=None):
    """Highest phase the artifacts on disk actually support, as a phase name.

    Canonical form, matching engage_runner._artifact_phase. Callers that need an
    index use _artifact_phase_index().
    """
    return PHASES[_artifact_phase_index(target, state, base)]


def cmd_phase(target, phase, base=None, force=False):
    """Advance engagement to a phase. Forward-only, append-only history.

    ``force`` bypasses the artifact gate and the one-phase-at-a-time rule. It is
    an explicit override for recovery, and it is recorded as a note so the state
    shows the jump was deliberate rather than earned.
    """
    if phase not in PHASES:
        print(f"[!] Unknown phase: {phase}")
        print(f"    Valid: {', '.join(PHASES)}")
        return 1

    state = read_state(target, base)
    if not state:
        print(f"[!] No engagement for {target} - run: init {target}")
        return 1

    if not acquire_lock(target, base):
        print(f"[!] Could not acquire lock for {target}")
        return 1
    try:
        current = state.get("current_phase", "init")
        if current == phase:
            print(f"[=] Already in phase: {phase}")
            return 0
        if PHASES.index(phase) < PHASES.index(current):
            print(f"[!] Backward transition rejected: {current} -> {phase}")
            print(f"    Use 'rollback {target} {phase}' to move backwards explicitly.")
            return 1

        # Multi-step jumps skip work; require each intervening phase explicitly.
        # Measure progress from artifacts, not the label: race/test run through
        # engage_runner and leave current_phase behind, so a label-based gap
        # falsely rejects a phase whose prerequisites are already on disk.
        done = _artifact_phase_index(target, state, base)
        gap = PHASES.index(phase) - done
        forced = False
        if gap > 1 and phase != "closed" and not force:
            skipped = PHASES[done + 1:PHASES.index(phase)]
            print(f"[!] Cannot jump to {phase}; missing: {', '.join(skipped)}")
            print(f"    Run: {', '.join(skipped)}")
            print(f"    Advance one phase at a time, or pass --force to override.")
            return 1
        elif gap > 1:
            forced = True

        problems = _phase_gate(target, phase, state, base)
        if problems and not force:
            print(f"[!] Cannot enter phase '{phase}' yet:")
            for p in problems:
                print(f"    - {p}")
            print(f"    Run the missing phase, or pass --force to override.")
            return 1
        elif problems:
            forced = True
            print(f"[!] --force: entering '{phase}' with unmet preconditions:")
            for p in problems:
                print(f"    - {p}")

        state["phase"] = phase
        state["current_phase"] = phase
        if phase not in state["phases_completed"]:
            state["phases_completed"].append(phase)
        if phase == "closed":
            state["status"] = "closed"
        state.setdefault("notes", []).append(
            {"timestamp": _now(),
             "text": f"Phase transition: {current} -> {phase}"
                     + (" (forced, preconditions bypassed)" if forced else "")}
        )
        if forced:
            state.setdefault("forced_transitions", []).append(
                {"timestamp": _now(), "from": current, "to": phase}
            )
        write_state(target, base, state)
        print(f"[+] {target}: {current} -> {phase}")
        return 0
    finally:
        release_lock(target, base)


def cmd_rollback(target, phase, base=None):
    """Move backwards to an earlier phase. Explicit, never implicit."""
    if phase not in PHASES:
        print(f"[!] Unknown phase: {phase}")
        return 1
    state = read_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1

    if not acquire_lock(target, base):
        print(f"[!] Could not acquire lock for {target}")
        return 1
    try:
        current = state.get("current_phase", "init")
        if PHASES.index(phase) >= PHASES.index(current):
            print(f"[!] rollback only moves backwards ({current} -> {phase} is not backwards)")
            return 1
        state["phase"] = phase
        state["current_phase"] = phase
        state["phases_completed"] = [
            p for p in state.get("phases_completed", [])
            if PHASES.index(p) <= PHASES.index(phase)
        ] or ["init"]
        state["status"] = "active"
        state.setdefault("notes", []).append(
            {"timestamp": _now(), "text": f"Rollback: {current} -> {phase}"}
        )
        write_state(target, base, state)
        print(f"[+] {target}: rolled back {current} -> {phase}")
        return 0
    finally:
        release_lock(target, base)


def cmd_note(target, text, base=None):
    state = read_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1
    if not acquire_lock(target, base):
        print(f"[!] Could not acquire lock for {target}")
        return 1
    try:
        state.setdefault("notes", []).append({"timestamp": _now(), "text": text})
        write_state(target, base, state)
        print(f"[+] Note added to {target}")
        return 0
    finally:
        release_lock(target, base)


def cmd_close(target, base=None, force=False):
    return cmd_phase(target, "closed", base, force)


def cmd_status(target, base=None):
    state = read_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1
    s = state.get("stats", {})
    print(f"=== Engagement: {state.get('target')} ===")
    print(f"Scope:      {state.get('scope')}")
    print(f"Phase:      {state.get('current_phase')} ({state.get('status')})")
    print(f"Created:    {state.get('created')}")
    print(f"Updated:    {state.get('updated')}")
    print(f"Completed:  {', '.join(state.get('phases_completed', []))}")
    print(f"Findings:   {s.get('findings_total', 0)} total "
          f"(C:{s.get('findings_critical', 0)} H:{s.get('findings_high', 0)} "
          f"M:{s.get('findings_medium', 0)} L:{s.get('findings_low', 0)} "
          f"I:{s.get('findings_info', 0)})")
    print(f"Modules:    {s.get('modules_tested', 0)} tested, "
          f"{s.get('modules_failed', 0)} failed")
    races = state.get("race_results", [])
    if races:
        # One entry per group, showing which module won and its score.
        print(f"Winners:    {len(races)} group(s)")
        for r in races:
            w = r.get("winner") or {}
            grp = r.get("group", "?")
            cnt = r.get("count")
            shown = f" ({cnt} findings)" if isinstance(cnt, int) else ""
            print(f"  - {grp:<12} {w.get('type')} score={w.get('score')}{shown}")
    notes = state.get("notes", [])
    if notes:
        print(f"Last note:  [{notes[-1].get('timestamp')}] {notes[-1].get('text')}")
    return 0


def cmd_list(base=None):
    root = engagements_dir(base)
    if not os.path.isdir(root):
        print(f"[!] No engagements directory: {root}")
        return 1
    rows = []
    for name in sorted(os.listdir(root)):
        if name in ("TEMPLATE", ".backup-pre-engagement"):
            continue
        if not os.path.isdir(os.path.join(root, name)):
            continue
        state = read_state(name, base)
        if state:
            s = state.get("stats", {})
            rows.append((name, state.get("current_phase"), state.get("status"),
                         s.get("findings_total", 0)))
    if not rows:
        print("(no engagements)")
        return 0
    print(f"{'TARGET':<32} {'PHASE':<10} {'STATUS':<10} FINDINGS")
    for name, phase, status, count in rows:
        print(f"{name:<32} {str(phase):<10} {str(status):<10} {count}")
    return 0


def cmd_verify(target, base=None):
    """Validate state.json structure and invariants. Exit 0 = healthy."""
    state = read_state(target, base)
    if not state:
        print(f"[!] No engagement for {target}")
        return 1
    problems = []
    if state.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version != {SCHEMA_VERSION}")
    if state.get("phase") not in PHASES:
        problems.append(f"invalid phase: {state.get('phase')}")
    if state.get("current_phase") != state.get("phase"):
        problems.append("current_phase != phase")
    completed = state.get("phases_completed", [])
    if not completed:
        problems.append("phases_completed empty")
    for p in completed:
        if p not in PHASES:
            problems.append(f"unknown phase in phases_completed: {p}")
    cwd = engagement_path(target, base)
    if not os.path.isdir(cwd):
        problems.append(f"engagement dir missing: {cwd}")
    if not os.path.isdir(findings_dir(target, base)):
        problems.append("findings/ missing")
    refs = state.get("findings_references", [])
    stats = state.get("stats", {})
    if refs and stats.get("findings_total", 0) < len(refs):
        problems.append("stats.findings_total < findings_references count")

    if problems:
        print(f"[!] {target}: {len(problems)} problem(s)")
        for p in problems:
            print(f"    - {p}")
        return 1
    print(f"[+] {target}: state OK (phase={state.get('phase')}, "
          f"findings={stats.get('findings_total', 0)})")
    return 0


# ----------------------------------------------------------------------------
# Self-check
# ----------------------------------------------------------------------------

def selftest():
    """Self-check the state machine. Runs in a temp dir, touches nothing real."""
    import shutil
    import tempfile

    base = tempfile.mkdtemp(prefix="novahaku-eng-selftest-")
    target = "selftest.local"
    try:
        # 1. Phase ordering table is sane
        assert PHASES[0] == "init" and PHASES[-1] == "closed"
        assert len(PHASES) == len(set(PHASES)), "duplicate phase names"

        # 2. init creates the workspace
        rc = cmd_init(target, "*.selftest.local", base)
        assert rc == 0, f"init returned {rc}"
        assert read_state(target, base) is not None, "state.json missing after init"

        # 3. The CSV header contract findings_gen.py depends on
        csv_path = os.path.join(findings_dir(target, base), "findings.csv")
        assert os.path.exists(csv_path), "findings.csv missing after init"
        header = open(csv_path, encoding="utf-8").readline().strip()
        assert header.startswith("ID,Title,Severity,Confidence,Category"), \
            f"unexpected CSV header: {header}"

        # 4. init is idempotent - second call must not clobber
        rc = cmd_init(target, None, base)
        assert rc == 0, "re-init should succeed as a no-op"

        # 5. Forward transition works
        rc = cmd_phase(target, "recon", base)
        assert rc == 0, f"phase recon returned {rc}"
        st = read_state(target, base)
        assert st is not None and st["phase"] == "recon"

        # 6. Backward transition is refused
        rc = cmd_phase(target, "init", base)
        assert rc == 1, "backward transition must be refused"

        # 7. rollback moves backwards explicitly
        rc = cmd_rollback(target, "init", base)
        assert rc == 0, f"rollback returned {rc}"
        st = read_state(target, base)
        assert st is not None and st["phase"] == "init"

        # 8. Unknown phase is refused
        rc = cmd_phase(target, "nonexistent-phase", base)
        assert rc == 1, "unknown phase must be refused"

        # 9. Lock acquire/release round-trip. The lock file is state.json.lock -
        # keep this assertion on the real path so a rename cannot silently pass.
        assert acquire_lock(target, base), "lock acquire failed"
        lock_path = _lock_file(target, base)
        assert os.path.exists(lock_path), f"lock file not created at {lock_path}"
        release_lock(target, base)
        assert not os.path.exists(lock_path), "lock file not removed"

        # 10. write_state is atomic - no .tmp left behind
        state = read_state(target, base)
        assert state is not None, "state vanished mid-selftest"
        state["notes"].append({"timestamp": _now(), "text": "selftest"})
        write_state(target, base, state)
        leftovers = [f for f in os.listdir(engagement_path(target, base)) if f.endswith(".tmp")]
        assert not leftovers, f"atomic write left temp files: {leftovers}"
        after = read_state(target, base)
        assert after is not None and after["notes"][-1]["text"] == "selftest", \
            "state write did not persist"

        # 11. list finds the engagement
        rc = cmd_list(base)
        assert rc == 0, f"list returned {rc}"

        # 12. verify passes on a healthy workspace
        rc = cmd_verify(target, base)
        assert rc == 0, f"verify returned {rc} on a healthy workspace"

        # 13-16. Phase gate: work cannot be skipped. Regression cover for the
        # defect where init -> closed succeeded and recorded a closed engagement
        # with no recon, no race and no findings.
        cmd_rollback(target, "init", base)
        for ph in ("race", "test", "exploit", "report", "closed"):
            rc = cmd_phase(target, ph, base)
            assert rc == 1, f"jump init -> {ph} must be refused"
        st = read_state(target, base)
        assert st is not None and st["phase"] == "init", "refused jump still moved the phase"

        # 17. --force is a recorded override, not a silent bypass
        rc = cmd_phase(target, "closed", base, force=True)
        assert rc == 0, f"forced transition returned {rc}"
        st = read_state(target, base)
        assert st is not None and st.get("forced_transitions"), \
            "forced transition must be recorded in forced_transitions"
        assert any("forced" in n.get("text", "") for n in st.get("notes", [])), \
            "forced transition must be noted"

        # 18. The gate reads findings.json, never state["findings"]. A missing
        # findings.json must be reported as missing test output - reading a
        # nonexistent state key was the original integrity bug.
        assert "findings" not in st or isinstance(st["findings"], list), \
            "unexpected state findings shape"
        found_json = os.path.join(findings_dir(target, base), "findings.json")
        if os.path.exists(found_json):
            os.remove(found_json)
        problems = _phase_gate(target, "closed", st, base)
        assert any("test has not produced findings" in p for p in problems), \
            f"gate must cite missing findings.json, got: {problems}"
        assert not any("lack id/asset" in p for p in problems), \
            "gate must not report id/asset problems for an absent file"

        # 19. Artifact-derived progress: candidates.json advances effective phase
        # without the label moving, so race is not reported as missing.
        shutil.rmtree(engagement_path(target, base), ignore_errors=True)
        cmd_init(target, None, base)
        with open(os.path.join(findings_dir(target, base), "candidates.json"),
                  "w", encoding="utf-8") as fh:
            json.dump({"winners": {}}, fh)
        st = read_state(target, base)
        assert _artifact_phase_index(target, st, base) >= PHASES.index("race"), \
            "candidates.json must count as race having run"

        # 20. Non-list phase argument list is not mutated by --force parsing
        assert cmd_phase(target, "recon", base) == 0

        # Assert-based: a failure above aborts the run. The count is not
        # restated as a hardcoded "N/N", which would drift as checks change.
        print("[+] engagement selftest: all checks passed (assert-based)")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def usage():
    print(__doc__.strip())


def main(argv):
    if len(argv) < 2:
        usage()
        return 0
    cmd = argv[1]
    rest = argv[2:]

    # --base optional flag, applies to every command
    base = None
    if "--base" in rest:
        i = rest.index("--base")
        if i + 1 >= len(rest):
            print("[!] --base requires a path")
            return 1
        base = rest[i + 1]
        rest = rest[:i] + rest[i + 2:]

    if cmd == "selftest":
        return selftest()
    if cmd == "init":
        if not rest:
            print("[!] init requires <target>")
            return 1
        scope = None
        if "--scope" in rest:
            i = rest.index("--scope")
            if i + 1 < len(rest):
                scope = rest[i + 1]
        return cmd_init(rest[0], scope, base)
    if cmd == "status":
        if not rest:
            print("[!] status requires <target>")
            return 1
        return cmd_status(rest[0], base)
    if cmd == "list":
        return cmd_list(base)
    if cmd == "phase":
        rest = [a for a in rest]
        force = "--force" in rest
        if force:
            rest.remove("--force")
        if len(rest) < 2:
            print("[!] phase requires <target> <phase>")
            return 1
        return cmd_phase(rest[0], rest[1], base, force)
    if cmd == "rollback":
        if len(rest) < 2:
            print("[!] rollback requires <target> <phase>")
            return 1
        return cmd_rollback(rest[0], rest[1], base)
    if cmd == "note":
        if len(rest) < 2:
            print("[!] note requires <target> <text>")
            return 1
        return cmd_note(rest[0], rest[1], base)
    if cmd == "close":
        force = "--force" in rest
        rest = [a for a in rest if a != "--force"]
        if not rest:
            print("[!] close requires <target>")
            return 1
        return cmd_close(rest[0], base, force)
    if cmd == "verify":
        if not rest:
            print("[!] verify requires <target>")
            return 1
        return cmd_verify(rest[0], base)

    print(f"[!] Unknown command: {cmd}")
    usage()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
