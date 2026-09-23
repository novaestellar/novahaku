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
    """Resolve engagements directory. Caller-supplied path wins."""
    if base:
        return os.path.abspath(base)
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
        return 0
    finally:
        release_lock(target, base)


def cmd_phase(target, phase, base=None):
    """Advance engagement to a phase. Forward-only, append-only history."""
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

        state["phase"] = phase
        state["current_phase"] = phase
        if phase not in state["phases_completed"]:
            state["phases_completed"].append(phase)
        if phase == "closed":
            state["status"] = "closed"
        state.setdefault("notes", []).append(
            {"timestamp": _now(), "text": f"Phase transition: {current} -> {phase}"}
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


def cmd_close(target, base=None):
    return cmd_phase(target, "closed", base)


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
        print(f"Races:      {len(races)}")
        for r in races[:5]:
            w = r.get("winner") or {}
            print(f"  - {r.get('module')}: winner={w.get('type')} score={w.get('score')}")
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

        print("[+] engagement selftest: 12/12 checks passed")
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
        if len(rest) < 2:
            print("[!] phase requires <target> <phase>")
            return 1
        return cmd_phase(rest[0], rest[1], base)
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
        if not rest:
            print("[!] close requires <target>")
            return 1
        return cmd_close(rest[0], base)
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
