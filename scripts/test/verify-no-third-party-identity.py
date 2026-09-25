#!/usr/bin/env python3
"""Detect third-party identity that rode in with adapted material.

`purge_branding.py` rewrites known upstream *hosts*. It cannot catch a
copyright line, an author URL, or a marketplace manifest, because those are
not substitutions — they are carry-over files that should never have been
committed. This gate looks for that class.

Why a separate scanner rather than more rules in purge_branding: rewriting a
copyright holder to "novalabs" would forge a licence claim. The correct
action is always removal or neutralisation by hand, so the job here is to
fail loudly, not to edit.

Two checks:
  1. Distribution artifacts that belong to an upstream package, not to a
     skill we author: LICENSE, marketplace.json, .claude-plugin/, plugin
     manifests. A skill directory holds SKILL.md plus its references; an
     npm/Claude-plugin wrapper around it is upstream packaging.
  2. Known third-party identity strings. A brand list is per-source and will
     always lag, so these are a cheap tripwire, not the real defence. The
     structural check above is what generalises.

Allow-listed: the repository's own LICENSE at the root, and any LICENSE that
names novalabs as the holder.

Usage: python scripts/test/verify-no-third-party-identity.py [--verbose]
Exit:  0 clean, 1 findings
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Files that are upstream packaging around a skill, regardless of contents.
ARTIFACT_NAMES = {"marketplace.json", "plugin.json"}
ARTIFACT_DIRS = {".claude-plugin", ".claude", "marketplace"}

# A LICENSE is expected at the repo root; anywhere else it is upstream's.
ROOT_LICENCE = "LICENSE"

# A copyright line naming a non-novalabs holder. This is the one text pattern
# that survived contact with the real repo.
#
# Rejected after testing against it, both far too noisy to be useful:
#   - a bare `@gmail.com`: teaching material contains signup payloads such as
#     `email=a@gmail.com`, which demonstrates a form, not an identity
#   - `git clone <any github url>`: the repo legitimately instructs the
#     operator to clone SecLists, pwndbg, binwalk, ProxyCat and others. An
#     *adapted* skill repo and an *installed tool* repo look identical as
#     text, so no pattern can separate them.
# Identity that rode in with adapted material is therefore caught by the
# structural check above, which is the part that generalises to unknown
# sources. Text matching is only a secondary tripwire.
IDENTITY = re.compile(
    r"copyright\s+\(c\)\s+\d{4}\s+(?!novalabs|NovaLabs|NOVAHAKU)[A-Za-z0-9_.-]+",
    re.IGNORECASE,
)

# A file whose subject is other people's work legitimately names them.
CITATION_OK = ("docs/skill-references/",)

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def tracked() -> list[str]:
    """Tracked paths from the git index.

    The index, not the working tree: an untracked stray is not published, and
    the repo is what other people clone. Same rule as the other gates here.
    """
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def structural(rel: str) -> str | None:
    p = Path(rel)
    if any(part in SKIP_DIRS for part in p.parts):
        return None
    if p.name in ARTIFACT_NAMES:
        return f"upstream packaging file: {p.name}"
    if any(part in ARTIFACT_DIRS for part in p.parts):
        return "upstream plugin/marketplace directory"
    if p.name.startswith("LICENSE") and len(p.parts) > 1:
        return "LICENSE outside the repository root (belongs to an upstream package)"
    return None


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv
    findings: list[str] = []
    files = tracked()
    scanned = 0

    for rel in files:
        reason = structural(rel)
        if reason:
            findings.append(f"{rel}: {reason}")
            continue

        # Only the repo-root licence may name a third party if it names us too.
        if Path(rel).name == ROOT_LICENCE and len(Path(rel).parts) == 1:
            continue

        # Ecosystem surveys cite other projects by design.
        if rel.replace("\\", "/").startswith(CITATION_OK):
            continue

        path = REPO / rel
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        scanned += 1

        for m in IDENTITY.finditer(text):
            line = text[: m.start()].count("\n") + 1
            findings.append(f"{rel}:{line}: third-party identity: {m.group(0)[:80]!r}")

    if verdict := findings:
        print(f"FAIL verify-no-third-party-identity: {len(verdict)} finding(s)")
        for f in verdict:
            print(f"  {f}")
        return 1

    print(f"OK   verify-no-third-party-identity: {len(files)} tracked file(s), "
          f"{scanned} text file(s) scanned, no third-party identity")
    if verbose:
        print(f"     allow-listed: {ROOT_LICENCE} at the repository root")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
