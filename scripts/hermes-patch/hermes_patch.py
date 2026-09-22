#!/usr/bin/env python3
"""hermes_patch.py — Apply reversible guardrail patches to a local Hermes Agent install.

Adapted for Hermes v2026.8+ from the general pattern of patching non-model scanner
call sites. Rewritten against the live source layout, not ported: upstream anchor
strings and file targets do not match modern Hermes.

Scopes covered:
  - memory write/load scanning   -> tools/memory_tool_store.py
  - cron prompt scanning         -> tools/cronjob_tools.py
  - cron skill-assembled scanning-> tools/cronjob_prompt_scan.py
  - cron via API server          -> gateway/platforms/api_server.py

Deliberately NOT covered:
  - tools/skills_guard.py should_allow_install(). That function owns the only guard
    against installing a `dangerous`-verdict skill from a community source
    (`hard_block`, which --force cannot override). Neutralising it trades a narrow
    convenience for a permanent loss of that guard. Left untouched by design.
  - Context-file scanning (SOUL.md/SKILL.md/AGENTS.md). Use the built-in reversible
    switch instead: env HERMES_CONTEXT_SKIP_SCAN=1.

Usage:
    python hermes_patch.py --check          # resolve path + report patch state
    python hermes_patch.py --apply          # patch (backs up first)
    python hermes_patch.py --restore        # revert from the backup manifest
    python hermes_patch.py --verify         # prove each target is patched

Author: novalabs
License: MIT
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MARKER = "# [novahaku-patch]"
BACKUP_DIRNAME = ".novahaku-patch-backup"
MANIFEST_NAME = "manifest.json"

# A file that must exist for a candidate root to be accepted as a Hermes source tree.
PROBE = Path("tools") / "threat_patterns.py"

# Every candidate is tried in order; the first that passes PROBE wins.
ROOT_CANDIDATES = (
    ("$HERMES_AGENT_HOME", lambda: os.environ.get("HERMES_AGENT_HOME")),
    ("$HERMES_HOME/../hermes-agent", lambda: _hermes_home_sibling()),
    ("~/.hermes/hermes-agent", lambda: str(Path.home() / ".hermes" / "hermes-agent")),
    ("%LOCALAPPDATA%/hermes/hermes-agent", lambda: _localappdata_sibling()),
)


def _hermes_home_sibling() -> str | None:
    home = os.environ.get("HERMES_HOME")
    return str(Path(home).parent / "hermes-agent") if home else None


def _localappdata_sibling() -> str | None:
    lad = os.environ.get("LOCALAPPDATA")
    return str(Path(lad) / "hermes" / "hermes-agent") if lad else None


def resolve_root(explicit: str | None = None) -> Path:
    """Locate the Hermes Agent source tree without hardcoding a machine path.

    An explicit ``--root`` is authoritative: if it does not look like a Hermes tree the run
    aborts rather than silently falling back to a different install. Operating on the wrong
    tree is unrecoverable in a way that operating on the right one is not.
    """
    tried: list[str] = []

    if explicit:
        p = Path(explicit).expanduser()
        if (p / PROBE).exists():
            return p
        if not p.exists():
            reason = "path does not exist"
        elif not p.is_dir():
            reason = "not a directory"
        else:
            reason = f"no {PROBE} inside"
        sys.stderr.write(
            f"ERROR: --root {p} is not a Hermes Agent source tree ({reason}).\n"
            "       Refusing to fall back to auto-resolution — the wrong tree may be modified.\n"
            f"       Pass a directory containing {PROBE}.\n"
        )
        raise SystemExit(2)

    for label, getter in ROOT_CANDIDATES:
        try:
            raw = getter()
        except Exception:
            raw = None
        if not raw:
            continue
        p = Path(raw).expanduser()
        tried.append(f"{label} -> {p}")
        if (p / PROBE).exists():
            return p
        tried[-1] += f"  (no {PROBE})"

    sys.stderr.write(
        "ERROR: could not locate the Hermes Agent source tree.\n"
        f"       Probe file looked for: {PROBE}\n"
        "       Candidates tried:\n"
        + "".join(f"         - {t}\n" for t in tried)
        + "       Set HERMES_AGENT_HOME to the directory containing tools/ and run again.\n"
    )
    raise SystemExit(2)


# --------------------------------------------------------------------------------------
# Patch definitions: (relative path, description, [(old, new), ...])
#
# Every anchor below is a full statement copied from the live source. If an anchor is
# absent the run fails loudly rather than silently skipping.
# --------------------------------------------------------------------------------------

def _patches() -> list[tuple[str, str, list[tuple[str, str]]]]:
    guard = (
        '    """Error string if *content* matches injection/exfil patterns. Strict scope:\n'
        '    memory enters the system prompt, so a poisoned entry persists across sessions."""\n'
        '    return _first_threat_message(content, scope="strict")'
    )
    guard_new = (
        f'    """{MARKER} scanning disabled for user-curated memory entries."""\n'
        '    return None'
    )

    load = (
        '            findings = scan_for_threats(entry, scope="strict") if entry and not entry.startswith("[BLOCKED:") else None'
    )
    load_new = f'            findings = None  {MARKER}'

    # memory_tool_store.py — the guard covers load, but add()/replace()/batch() call the
    # scanner directly and must each be defused or memory writes stay blocked.
    add_scan = '        if scan_error := _scan_memory_content(content):'
    add_scan_new = f'        if False:  {MARKER}\n            scan_error = "".join([])'
    replace_scan = '        if scan_error := _scan_memory_content(new_content):'
    replace_scan_new = f'        if False:  {MARKER}\n            scan_error = "".join([])'
    batch_scan = '            scan_error = op.get("action") in {"add", "replace"} and op.get("content") and _scan_memory_content(op["content"])'
    batch_scan_new = f'            scan_error = False  {MARKER}'

    assembled = (
        '        assembled, scan_error = _scan_cron_skill_assembled(assembled)'
    )
    assembled_new = f'        assembled, scan_error = assembled, ""  {MARKER}'

    cron_prompt = '            scan_error = _scan_cron_prompt(user_prompt)'
    cron_prompt_new = f'            scan_error = ""  {MARKER}'

    cron_assembled_else = '        scan_error = _scan_cron_prompt(assembled)'
    cron_assembled_else_new = f'        scan_error = ""  {MARKER}'

    api_scan = '            scan_error = _scan_cron_prompt(prompt)'
    api_scan_new = f'            scan_error = ""  {MARKER}'

    # tools/cronjob_tools.py — three call sites: tuple-form guard, extra_prompt, bulk create.
    create_scan = '        (prompt and _scan_cron_prompt(prompt))'
    create_scan_new = f'        False  {MARKER} (prompt and _scan_cron_prompt(prompt))'

    extra_scan = '        scan_error = _scan_cron_prompt(extra_prompt)'
    extra_scan_new = f'        scan_error = ""  {MARKER}'

    bulk_scan = '        scan_error = _scan_cron_prompt(prompt)'
    bulk_scan_new = f'        scan_error = ""  {MARKER}'

    return [
        (
            "tools/memory_tool_store.py",
            "memory write + load scanning",
            [
                (guard, guard_new),
                (load, load_new),
                (add_scan, add_scan_new),
                (replace_scan, replace_scan_new),
                (batch_scan, batch_scan_new),
            ],
        ),
        (
            "cron/scheduler_prompt.py",
            "cron scan dispatch (assembled + user-prompt call sites)",
            [
                (assembled, assembled_new),
                (cron_prompt, cron_prompt_new),
                (cron_assembled_else, cron_assembled_else_new),
            ],
        ),
        (
            "tools/cronjob_tools.py",
            "cron prompt scanning (create/update + bulk entry)",
            [
                (create_scan, create_scan_new),
                (extra_scan, extra_scan_new),
                (bulk_scan, bulk_scan_new),
            ],
        ),
        (
            "gateway/platforms/api_server.py",
            "cron scanning via API server",
            [(api_scan, api_scan_new)],
        ),
    ]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clear_readonly(path: Path) -> None:
    """Drop the read-only bit so a rollback can overwrite a file that blocked the write.

    Rollback failing because the very permission that caused the failure is still set would
    leave the tree half-patched. Best-effort: on POSIX this is a no-op for root-owned files,
    and on any failure we fall through to the caller's by-hand recovery message.
    """
    try:
        if path.exists():
            path.chmod(path.stat().st_mode | 0o200)
    except OSError:
        pass


def _manifest_path(root: Path) -> Path:
    return root / BACKUP_DIRNAME / MANIFEST_NAME


def _load_manifest(root: Path) -> dict:
    mp = _manifest_path(root)
    if not mp.exists():
        return {"created_at": None, "root": str(root), "files": {}}
    return json.loads(mp.read_text(encoding="utf-8"))


def _save_manifest(root: Path, manifest: dict) -> None:
    mp = _manifest_path(root)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _source_fingerprint(root: Path) -> dict:
    """Hash the pristine form of each target file.

    Anchors are statement-level strings; a future refactor could reuse one in a different
    function and match without complaint. Recording per-file hashes lets ``--apply`` warn
    when the source is not the revision the anchors were written against, and lets
    ``--restore`` refuse a restore over files that have drifted since patching.
    """
    fp: dict = {}
    for rel, _desc, _anchors in _patches():
        p = root / rel
        if p.exists():
            fp[rel] = _sha(p)
    return fp


def _pinned_fingerprint(root: Path) -> dict:
    manifest = _load_manifest(root)
    return manifest.get("source_fingerprint") or {}


def check(root: Path) -> int:
    """Report resolution + patch state. Exit 0 only when the tree is in a known-good state.

    Exit codes: 0 = all targets clean-or-patched consistently (healthy),
    1 = a target is missing or its anchors have drifted (unhealthy — unusable as a CI gate
    otherwise, since a broken tree would silently pass).
    """
    print(f"Hermes root: {root}")
    print(f"Marker:      {MARKER}\n")
    patched = 0
    unhealthy = 0
    for rel, desc, anchors in _patches():
        p = root / rel
        if not p.exists():
            print(f"  MISSING FILE  {rel}  ({desc})")
            unhealthy += 1
            continue
        text = p.read_text(encoding="utf-8")
        hits = sum(1 for old, _ in anchors if old in text)
        applied = MARKER in text
        if applied:
            patched += 1
        else:
            state_ok = hits == len(anchors)
            if not state_ok:
                unhealthy += 1
        state = "PATCHED" if applied else ("clean" if hits else "ANCHORS CHANGED")
        print(f"  {state:15} {rel}  ({hits}/{len(anchors)} anchors)  {desc}")
    print(f"\n{patched} of {len(_patches())} targets patched.")
    if unhealthy:
        print(f"{unhealthy} target(s) unhealthy — see above.")
        return 1
    return 0


def apply_patches(root: Path, auto_verify: bool = True) -> int:
    manifest = _load_manifest(root)
    if not manifest.get("created_at"):
        manifest["created_at"] = datetime.now(timezone.utc).isoformat()
        manifest["root"] = str(root)

    # Warn if the source has drifted from the revision the anchors were authored against.
    pinned = manifest.get("source_fingerprint") or {}
    if pinned:
        current = _source_fingerprint(root)
        drifted = [rel for rel, h in pinned.items() if rel in current and current[rel] != h]
        if drifted:
            sys.stderr.write(
                "WARN: target source differs from the revision recorded at first apply:\n"
                + "".join(f"      - {rel}\n" for rel in drifted)
                + "      Anchors may match a refactor with different semantics. Re-run\n"
                "      --check and re-read the diff before trusting this patch.\n"
            )
    else:
        manifest["source_fingerprint"] = _source_fingerprint(root)

    changed = 0
    # ----------------------------------------------------------------------------------
    # Phase 1: validate EVERY target before touching ANY file.
    # A mid-loop abort after the first write would leave a half-patched tree whose
    # manifest cannot restore it — fail closed instead.
    # ----------------------------------------------------------------------------------
    planned: list[tuple[Path, str, str, list[tuple[str, str]]]] = []
    skipped: list[str] = []

    for rel, desc, anchors in _patches():
        p = root / rel
        if not p.exists():
            sys.stderr.write(
                f"FAIL: {rel} not found.\n      Nothing was written.\n"
            )
            return 1

        text = p.read_text(encoding="utf-8")

        if MARKER in text:
            # A marker alone does not prove the scanners are defused — a stray marker, a
            # partially reverted file, or a re-armed guard all still carry it. Confirm by
            # static verification, and treat a still-wired target as an error rather than
            # reporting success on a file we did not touch. (Oracle D1/D2.)
            symbol = (_verify_symbols().get(rel) or (None,))[0]
            if symbol:
                try:
                    still_live = _live_call_lines(ast.parse(text), symbol)
                except SyntaxError as exc:
                    sys.stderr.write(
                        f"FAIL: {rel} carries the marker but does not parse: {exc}\n"
                        "      Nothing was written. Repair or restore the file first.\n"
                    )
                    return 1
                if still_live:
                    sys.stderr.write(
                        f"FAIL: {rel} carries the marker but the scanner is still wired at "
                        f"line(s) {still_live}.\n"
                        "      Refusing to report success. Restore the file, then re-apply:\n"
                        "      python hermes_patch.py --restore\n"
                    )
                    return 1
            skipped.append(rel)
            continue

        missing = [old for old, _ in anchors if old not in text]
        if missing:
            sys.stderr.write(
                f"FAIL: anchor not found in {rel} ({desc}).\n"
                "      The source may have changed — nothing was written for ANY file.\n"
                f"      Expected text (first 120 chars): {missing[0][:120]!r}\n"
            )
            return 1

        planned.append((p, rel, desc, anchors))

    # ----------------------------------------------------------------------------------
    # Phase 2: pre-write backups for every planned file, then write.
    # ----------------------------------------------------------------------------------
    for p, rel, _desc, _anchors in planned:
        if rel not in manifest["files"]:
            bak = root / BACKUP_DIRNAME / rel
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bak)
            manifest["files"][rel] = {"sha256": _sha(p), "backup": str(bak.name)}

    _save_manifest(root, manifest)

    # ----------------------------------------------------------------------------------
    # Phase 3: write. Guarded — a read-only file, a full disk, or an encoding error used to
    # escape as an uncaught traceback mid-loop, leaving a half-patched tree. The manifest is
    # already on disk by now, so a failure here rolls back from the taken backups.
    # (Oracle D3.)
    # ----------------------------------------------------------------------------------
    try:
        for p, rel, desc, anchors in planned:
            text = p.read_text(encoding="utf-8")
            for old, new in anchors:
                text = text.replace(old, new, 1)
            p.write_text(text, encoding="utf-8")
            changed += 1
            print(f"  patched          {rel}  ({desc})")
    except OSError as exc:
        failed_rel = locals().get("rel", "<unknown>")
        sys.stderr.write(
            f"\nFAIL: writing {failed_rel} failed: {exc}\n"
            "      Rolling back the files already written from the manifest.\n"
        )
        if "<unknown>" not in failed_rel:
            _clear_readonly(root / failed_rel)
        try:
            rollback = restore(root)
        except OSError as rb_exc:
            sys.stderr.write(
                f"FAIL: rollback raised {rb_exc}.\n"
                "      The tree may be half-patched. Restore all four files by hand from\n"
                f"      {root / BACKUP_DIRNAME}\n"
            )
            return 1
        if rollback != 0:
            sys.stderr.write(
                "FAIL: automatic rollback also failed. The tree may be half-patched.\n"
                f"      Restore all four files by hand from {root / BACKUP_DIRNAME}\n"
            )
            return 1
        sys.stderr.write("Rolled back. Tree is in pre-patch state.\n")
        return 1

    for rel in skipped:
        print(f"  already patched  {rel}")

    print(f"\n{changed} file(s) written. Backup + manifest: {root / BACKUP_DIRNAME}")

    # Auto-verify after writing: a patch that leaves the scanner wired is worse than no
    # patch, because the operator believes it is defused. Roll back automatically on failure.
    if auto_verify:
        print("\nAuto-verify:")
        rc = verify(root)
        if rc != 0:
            sys.stderr.write(
                "\nFAIL: auto-verify did not pass — rolling back to pre-patch state.\n"
            )
            rollback = restore(root)
            if rollback != 0:
                sys.stderr.write(
                    "FAIL: automatic rollback also failed. Restore the 4 files by hand from\n"
                    f"      {root / BACKUP_DIRNAME}\n"
                )
                return 1
            sys.stderr.write("Rolled back. Tree is in pre-patch state.\n")
            return 1

    print("Restart the gateway for changes to take effect.")
    return 0


def restore(root: Path) -> int:
    manifest = _load_manifest(root)
    files = manifest.get("files") or {}
    if not files:
        sys.stderr.write(
            f"FAIL: no manifest at {_manifest_path(root)} — nothing to restore.\n"
            "      NOTE: the target files are UNCHANGED by this command. If the patch\n"
            "      was previously applied, those files are still patched.\n"
        )
        return 1

    # Refuse a cross-root restore: the manifest records which tree it belongs to.
    recorded_root = manifest.get("root")
    if recorded_root and Path(recorded_root) != root:
        sys.stderr.write(
            f"FAIL: manifest belongs to a different root.\n"
            f"      recorded: {recorded_root}\n"
            f"      requested: {root}\n"
            "      Nothing was written.\n"
        )
        return 1

    # ----------------------------------------------------------------------------------
    # Pre-flight: verify EVERY backup exists and hashes correctly before overwriting
    # anything. Overwriting file-by-file leaves a mixed tree when a later backup is
    # missing, which no single follow-up command can fix.
    # ----------------------------------------------------------------------------------
    for rel, meta in files.items():
        src = root / BACKUP_DIRNAME / rel
        if not src.exists():
            sys.stderr.write(
                f"FAIL: backup missing for {rel}.\n"
                f"      Expected at: {src}\n"
                "      Nothing was written — the tree is unchanged.\n"
            )
            return 1
        actual = _sha(src)
        if actual != meta.get("sha256"):
            sys.stderr.write(
                f"FAIL: backup checksum mismatch for {rel}.\n"
                f"      expected: {meta.get('sha256')}\n"
                f"      actual:   {actual}\n"
                "      The backup is corrupt — nothing was written.\n"
            )
            return 1

    # Preserve the current (patched) files so a restore over drifted source is reversible.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    undo_dir = root / BACKUP_DIRNAME / f"pre-restore-{stamp}"

    ok = 0
    for rel, meta in files.items():
        src = root / BACKUP_DIRNAME / rel
        dst = root / rel
        if dst.exists():
            undo = undo_dir / rel
            undo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, undo)
        shutil.copy2(src, dst)
        if _sha(dst) != meta["sha256"]:
            sys.stderr.write(f"FAIL: checksum mismatch after restore of {rel}\n")
            return 1
        ok += 1
        print(f"  restored         {rel}  (sha256 verified)")

    print(f"\n{ok} file(s) restored to pre-patch state.")
    print(f"Pre-restore copies kept at: {undo_dir}")
    print("Restart the gateway for changes to take effect.")
    return 0


def _verify_symbols() -> dict[str, tuple[str, str]]:
    """Map every patched target to (symbol, label) for verification.

    Must cover ALL four patched files, not just the three with named scan functions —
    otherwise applying to four files and verifying three silently misses a live scanner.
    (Oracle D5.)
    """
    return {
        "tools/memory_tool_store.py": ("_scan_memory_content", "memory write + load scan"),
        "tools/cronjob_tools.py": ("_scan_cron_prompt", "cron prompt scan"),
        "cron/scheduler_prompt.py": ("_scan_cron_skill_assembled", "cron skill-assembled scan"),
        "gateway/platforms/api_server.py": ("_scan_cron_prompt", "cron scan via API server"),
    }


def verify(root: Path) -> int:
    """Prove the patch defuses each scan call site.

    Static (AST) inspection only — deliberately does NOT import the target modules.
    Hermes modules pull in runtime deps (``utils``, ``hermes_constants``) that are absent
    from a bare source copy, so importing them would report a false failure and mask the
    real question: is the scan still wired into the control flow?

    Any call that is not provably dead counts as live. A guard re-armed with a non-literal
    condition (``if _FLAG():``) is therefore reported as STILL WIRED rather than passing.
    (Oracle D4.)
    """
    print(f"Hermes root: {root}\n")
    failures = 0

    for rel, (func, label) in _verify_symbols().items():
        p = root / rel
        if not p.exists():
            print(f"  {label:28}: MISSING FILE")
            failures += 1
            continue

        source = p.read_text(encoding="utf-8")
        if MARKER not in source:
            print(f"  {label:28}: NOT PATCHED (marker absent)")
            failures += 1
            continue

        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            print(f"  {label:28}: SYNTAX ERROR {exc}")
            failures += 1
            continue

        live = _live_call_lines(tree, func)
        if live:
            print(f"  {label:28}: STILL WIRED at line(s) {live}")
            failures += 1
        else:
            print(f"  {label:28}: DEFUSED ({func} unreachable at control-flow level)")

    # skills_guard is intentionally NOT bypassed — report presence as a guard against over-reach.
    sg = root / "tools/skills_guard.py"
    if sg.exists():
        text = sg.read_text(encoding="utf-8")
        print(f"  {'skills_guard':28}: {'UNEXPECTEDLY PATCHED' if MARKER in text else 'untouched (intended)'}")

    print(f"\n{failures} failing check(s).")
    return 1 if failures else 0


def _live_call_lines(tree: ast.AST, func: str) -> list[int]:
    """Return line numbers where ``func`` is called in a live (non-constant-False) position.

    A call is considered defused when it sits inside a branch guarded by a literal ``False``,
    e.g. ``if False:  # [novahaku-patch]`` or ``False and f()``. Anything else counts as live.
    """
    dead_nodes: set[int] = set()
    for node in ast.walk(tree):
        # `if <const falsy>: ...` — mark the whole body dead.
        if isinstance(node, ast.If) and isinstance(node.test, ast.Constant) and not node.test.value:
            for child in node.body:
                for sub in ast.walk(child):
                    dead_nodes.add(id(sub))
        # `False and f()` — short-circuit makes the right operand unreachable.
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            if any(isinstance(v, ast.Constant) and not v.value for v in node.values):
                for v in node.values[1:]:
                    for sub in ast.walk(v):
                        dead_nodes.add(id(sub))

    live: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name == func and id(node) not in dead_nodes:
            live.append(node.lineno)
    return sorted(set(live))


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply reversible guardrail patches to a local Hermes Agent install.")
    ap.add_argument("--root", help="Hermes Agent source dir (else auto-resolved)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="report resolution + patch state (exit 1 if unhealthy)")
    g.add_argument("--apply", action="store_true", help="apply patches (backs up, then auto-verifies)")
    g.add_argument("--restore", action="store_true", help="revert from backup manifest")
    g.add_argument("--verify", action="store_true", help="prove scans no longer fire")
    ap.add_argument(
        "--no-verify",
        action="store_true",
        help="with --apply: skip the post-write auto-verify (not recommended)",
    )
    args = ap.parse_args()

    root = resolve_root(args.root)

    if args.check:
        return check(root)
    if args.apply:
        return apply_patches(root, auto_verify=not args.no_verify)
    if args.restore:
        return restore(root)
    return verify(root)


if __name__ == "__main__":
    raise SystemExit(main())
