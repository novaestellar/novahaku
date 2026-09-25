#!/usr/bin/env python3
"""K12 gate: every corpus page must be reachable, and the index must match disk.

K12 asks whether source techniques are actually represented in the skills,
not merely claimed. "Referenced somewhere" is too weak a test — a page linked
only from an orphan page is still unreachable. This walks the reference graph
from the real entry points and fails on anything it cannot get to.

Entry points (roots of the reachability walk):
  - testing/references/00-INDEX.md   the generated corpus index
  - every SKILL.md outside the corpus

A page passes when it is reachable from a root by following relative Markdown
links through corpus pages. Anything left over is reported, category by
category, because an unreachable category is the shape this failure takes.

Usage:
    python scripts/test/verify-corpus-reachability.py <root>
Exit: 0 all reachable and index fresh, 1 unreachable pages or stale index.
"""

from __future__ import annotations

import os
import sys
import urllib.parse
from collections import deque

SKIP_DIRS = {".git", "__pycache__", ".novahaku-patch-backup", "node_modules"}


def walk_files(root: str, suffixes: tuple[str, ...]) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(suffixes):
                out.append(os.path.join(dirpath, name))
    return out


def links_in(text: str, base_dir: str, universe: set[str]) -> set[str]:
    """Relative link targets that resolve to a file in `universe`."""
    import re

    found: set[str] = set()
    for raw in re.findall(r"\]\(([^)]+)\)", text):
        target = raw.split("#")[0].strip()
        if not target or target.startswith(("http://", "https://", "#", "mailto:", "javascript:")):
            continue
        target = urllib.parse.unquote(target)
        resolved = os.path.normpath(os.path.join(base_dir, target))
        if resolved in universe:
            found.add(resolved)
    return found


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = os.path.abspath(args[0] if args else ".")
    ref_dir = os.path.join(root, "testing", "references")
    if not os.path.isdir(ref_dir):
        sys.stderr.write(f"verify-corpus-reachability: no such directory: {ref_dir}\n")
        return 2

    corpus = set(walk_files(ref_dir, (".md",)))
    if not corpus:
        sys.stderr.write("verify-corpus-reachability: corpus is empty\n")
        return 2

    # Roots: the generated index, plus every SKILL.md in the tree.
    roots: set[str] = set()
    index = os.path.join(ref_dir, "00-INDEX.md")
    if not os.path.exists(index):
        sys.stderr.write("verify-corpus-reachability: "
                         f"{os.path.relpath(index, root)} is missing — run gen_corpus_index.py\n")
        return 1
    roots.add(index)
    for path in walk_files(root, ("SKILL.md",)):
        if not os.path.abspath(path).startswith(os.path.abspath(ref_dir)):
            roots.add(path)

    # Every .md in the tree can forward the walk; build the link map lazily.
    all_md = set(walk_files(root, (".md",)))
    universe = all_md | corpus

    seen: set[str] = set()
    queue: deque[str] = deque(roots)
    graph: dict[str, set[str]] = {}
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        try:
            text = open(node, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        targets = links_in(text, os.path.dirname(node), universe)
        graph[node] = targets
        for t in targets:
            if t not in seen:
                queue.append(t)

    reachable = corpus & seen
    unreachable = sorted(corpus - reachable)

    exit_code = 0

    # Index freshness is part of the gate: a stale index silently un-references pages.
    import importlib.util

    gen = os.path.join(root, "scripts", "test", "gen_corpus_index.py")
    if os.path.exists(gen):
        spec = importlib.util.spec_from_file_location("_gen_corpus_index", gen)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        expected = mod.render(root, ref_dir, mod.collect(ref_dir))
        current = open(index, encoding="utf-8").read()
        if current != expected:
            print(f"  STALE: {os.path.relpath(index, root)} does not match disk "
                  "(run gen_corpus_index.py)")
            exit_code = 1

    if unreachable:
        by_cat: dict[str, list[str]] = {}
        for p in unreachable:
            rel = os.path.relpath(p, ref_dir).replace("\\", "/")
            by_cat.setdefault(rel.split("/")[0], []).append(rel)
        print(f"  UNREACHABLE: {len(unreachable)}/{len(corpus)} corpus page(s)")
        for cat, items in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
            print(f"    {cat}: {len(items)}")
            for rel in items[:4]:
                print(f"      {rel}")
        exit_code = 1
    else:
        print(f"  corpus pages reachable: {len(corpus)}/{len(corpus)}")

    if exit_code == 0:
        print(f"  OK verify-corpus-reachability: all {len(corpus)} corpus page(s) "
              f"reachable, index fresh ({len(roots)} entry point(s))")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
