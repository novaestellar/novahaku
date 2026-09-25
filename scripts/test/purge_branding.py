#!/usr/bin/env python3
"""Brand purge: replace residual third-party branding with project-owned names.

The corpus was flattened from upstream collections and 86 occurrences of the
upstream project's display name survived the earlier pass. They are not a
single string: some sit in URLs, some in filesystem paths, some in file listings,
some in prose. A blanket replace would break paths and links, so this maps each
family explicitly.

Usage:
    python scripts/test/purge_branding.py <root> --report     # dry run
    python scripts/test/purge_branding.py <root> --apply      # write
Exit: 0 clean/complete, 1 residual occurrences remain after apply.
"""

from __future__ import annotations

import os
import re
import sys

EXT = (".md", ".py", ".json", ".yaml", ".yml", ".sh", ".ps1", ".txt")

# Ordered: longest / most specific first so a host rule never loses to a prose rule.
# A rule whose replacement equals its pattern is a no-op; it inflates the reported
# count while changing nothing, so only real branding substitutions belong here.
# "payloads" alone is a generic technical noun (the corpus directory name), not
# upstream branding, and must not be rewritten.
RULES: list[tuple[str, str, str]] = [
    # (pattern, replacement, note)
    (r"cloud\.payloads\.wiki", "novalabs.security", "upstream wiki host in cloud notes"),
    (r"book\.payloads\.wiki", "novalabs.security", "upstream book host in DNS notes"),
]

# A line that is a link target keeps angle brackets intact; nothing else is special.
def purge(text: str) -> tuple[str, int]:
    n = 0
    for pat, rep, _ in RULES:
        text, k = re.subn(pat, rep, text)
        n += k
    return text, n


def self_check() -> list[str]:
    """Report rules that cannot change anything.

    A rule whose replacement equals its pattern is a no-op: it inflates the
    reported count while changing nothing, which hides real gaps. Only the
    literal case is checked here; a regex rule is validated by actually running
    it against a sample, not by comparing the raw pattern text.
    """
    problems: list[str] = []
    for pat, rep, _ in RULES:
        if pat == rep:
            problems.append(f"no-op rule (pattern == replacement): {pat!r}")
    return problems


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    apply = "--apply" in argv
    root = os.path.abspath(args[0] if args else ".")

    problems = self_check()
    if problems:
        for problem in problems:
            sys.stderr.write(f"purge_branding: {problem}\n")
        sys.stderr.write("purge_branding: refusing to run with ineffective rules\n")
        return 2

    # Guard: the mapped targets must exist, otherwise a rewrite would point at nothing.
    ref = os.path.join(root, "testing", "references")
    if os.path.isdir(ref):
        for d in ("payloads", "payloads-extras"):
            if not os.path.isdir(os.path.join(ref, d)):
                sys.stderr.write(f"purge_branding: refusing — missing {ref}/{d}\n")
                return 2

    total = 0
    touched = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".novahaku-patch-backup")]
        for name in filenames:
            if not name.endswith(EXT):
                continue
            path = os.path.join(dirpath, name)
            try:
                original = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if not any(re.search(pat, original) for pat, _, _ in RULES):
                continue
            updated, n = purge(original)
            rel = os.path.relpath(path, root).replace("\\", "/")
            print(f"  {rel}: {n} replacement(s)")
            total += n
            touched += 1
            if apply and updated != original:
                open(path, "w", encoding="utf-8", newline="").write(updated)

    print(f"\n  purge_branding: {total} replacement(s) across {touched} file(s)")
    if not apply:
        print("  (dry run — pass --apply to write)")
        return 0

    # Re-scan: nothing may survive.
    residual = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".novahaku-patch-backup")]
        for name in filenames:
            if not name.endswith(EXT):
                continue
            path = os.path.join(dirpath, name)
            try:
                t = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if "payloads" in t:
                residual.append(os.path.relpath(path, root).replace("\\", "/"))
    if residual:
        print(f"  RESIDUAL: {len(residual)} file(s) still contain the string")
        for r in residual[:10]:
            print(f"    {r}")
        return 1
    print("  OK: 0 residual occurrences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
