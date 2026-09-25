#!/usr/bin/env python
"""Skill frontmatter audit — self-contained, no external harness.

Supersedes the throwaway `test_skills.py` that produced the 27 findings in
05-TRACKING section 6.4. That harness read frontmatter line-by-line with a
regex, so every skill whose `description` used a YAML block scalar (`|`)
looked like a one-character description. 7 of the 8 S4 findings were that
artefact, not real drift.

Checks, each of which must be able to fail (sabotage-verified):
  S1  SKILL.md parses as YAML with a mapping at the top
  S2  `name` present and equal to the containing directory name
  S3  `description` present and >= 40 characters
  S4  no stray zero-width U+200B outside a ZWSP-KEEP exempt line
  S5  every relative Markdown link resolves (outside code fences, where
      `[...](...)`-shaped text is usually a payload or a regex)

Exempt marker: a line containing `<!-- ZWSP-KEEP` is excluded from S4. The
llm-security skill demonstrates zero-width-space prompt injection, so those
characters are the payload, not stray noise.

Usage:
    python scripts/test/audit_skills.py <repo-root> [--json]
Exit: 0 all clean, 1 any finding.
"""

from __future__ import annotations

import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a declared requirement
    sys.stderr.write("audit_skills: PyYAML is required (pip install pyyaml)\n")
    raise SystemExit(2)

ZWSP = "\u200b"
EXEMPT_MARKER = "<!-- ZWSP-KEEP"
MIN_DESC = 40
FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`]*`")
REL_LINK = re.compile(r"\]\((?!https?:|#|mailto:|javascript:)([^)]+)\)")


def split_frontmatter(text: str) -> str | None:
    """Return the frontmatter block, or None when the file has none."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return None if end == -1 else text[3:end]


def find_skills(root: str) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        if "SKILL.md" in filenames:
            out.append(os.path.join(dirpath, "SKILL.md"))
    return sorted(out)


def audit(root: str) -> tuple[list[tuple[str, str]], int]:
    findings: list[tuple[str, str]] = []
    skills = find_skills(root)

    for path in skills:
        rel = os.path.relpath(path, root).replace("\\", "/")
        dirname = os.path.basename(os.path.dirname(path))
        text = open(path, encoding="utf-8", errors="replace").read()

        block = split_frontmatter(text)
        if block is None:
            findings.append(("S1", f"{rel}: no YAML frontmatter"))
            continue
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            findings.append(("S1", f"{rel}: frontmatter is not valid YAML ({type(exc).__name__})"))
            continue
        if not isinstance(data, dict):
            findings.append(("S1", f"{rel}: frontmatter is not a mapping"))
            continue

        name = data.get("name")
        if not name:
            findings.append(("S2", f"{rel}: missing `name`"))
        elif str(name) != dirname:
            findings.append(("S2", f"{rel}: name={name!r} != directory {dirname!r}"))

        desc = data.get("description")
        if not desc:
            findings.append(("S3", f"{rel}: missing `description`"))
        elif len(str(desc)) < MIN_DESC:
            findings.append(("S3", f"{rel}: description is {len(str(desc))} chars (< {MIN_DESC})"))

        for lineno, line in enumerate(text.splitlines(), 1):
            if ZWSP in line and EXEMPT_MARKER not in line:
                findings.append(("S4", f"{rel}:{lineno}: stray U+200B (add {EXEMPT_MARKER} if it is the payload)"))

        stripped = INLINE_CODE.sub("", FENCE.sub("", text))
        for target in REL_LINK.findall(stripped):
            bare = target.split("#")[0].strip()
            if not bare:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), bare))
            if not os.path.exists(resolved):
                findings.append(("S5", f"{rel}: link does not resolve: {target}"))

    return findings, len(skills)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    as_json = "--json" in argv
    root = args[0] if args else "."
    if not os.path.isdir(root):
        sys.stderr.write(f"audit_skills: not a directory: {root}\n")
        return 2

    findings, total = audit(os.path.abspath(root))

    if as_json:
        print(json.dumps({"skills": total, "findings": len(findings),
                          "items": [{"code": c, "detail": d} for c, d in findings]}, indent=2))
    else:
        for code, detail in findings:
            print(f"  [{code}] {detail}")
        print(f"\n  audit_skills: {total} SKILL.md scanned, {len(findings)} finding(s)")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
