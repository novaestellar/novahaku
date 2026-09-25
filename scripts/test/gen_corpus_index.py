#!/usr/bin/env python3
"""Generate the corpus entry-point index from disk.

K12 requires that source techniques are actually represented in the skills,
not merely claimed. Measured on this tree, 136 of 281 corpus .md files had no
inbound reference from anywhere outside the corpus, and no category had an
entry point from a skill: the corpus was an island.

This emits testing/references/00-INDEX.md — one row per reference page, grouped
by category — so every page has at least one path that reaches it from the
skill layer. Generated, never hand-written: the file lists what exists on disk,
so it cannot drift.

Usage:
    python scripts/test/gen_corpus_index.py <root>            # write
    python scripts/test/gen_corpus_index.py <root> --check    # verify up to date
Exit: 0 ok, 1 stale (--check), 2 bad invocation.
"""

from __future__ import annotations

import os
import sys

INDEX_NAME = "00-INDEX.md"
CATEGORY_BLURB = {
    "payloads": "Fast per-topic payload sheets (one file per class) plus per-class deep dives.",
    "payloads-extras": "Additional per-class reference material beyond the fast sheets.",
    "web-notes": "Long-form web exploitation notes (deserialization, cookies, smuggling, XSS).",
    "misc": "Bug-bounty writeup notes and mindmap outlines.",
    "network-services-pentesting": "Network service testing: DNS, nginx, Cloudflare discovery.",
    "generic-methodologies-and-resources": "Methodology and external recon playbooks.",
    "generic-hacking": "Service-agnostic brute-force technique notes.",
    "linux-hardening": "Linux restriction bypass notes.",
    "windows-hardening": "Windows local privilege escalation.",
    "pentesting-web": "Web tooling and takeover notes.",
    "dangling-markup-html-scriptless-injection": "Scriptless HTML injection notes.",
    "sql-injection": "SQL injection reference material.",
}


def collect(ref_dir: str) -> dict[str, list[tuple[str, str, int]]]:
    """category -> [(relative path from ref_dir, title-ish name, size)]"""
    out: dict[str, list[tuple[str, str, int]]] = {}
    for cat in sorted(os.listdir(ref_dir)):
        cat_path = os.path.join(ref_dir, cat)
        if not os.path.isdir(cat_path):
            continue
        rows: list[tuple[str, str, int]] = []
        for dirpath, dirnames, filenames in os.walk(cat_path):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for name in sorted(filenames):
                if not name.endswith(".md"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ref_dir).replace("\\", "/")
                rows.append((rel, name[:-3], os.path.getsize(full)))
        if rows:
            out[cat] = rows
    return out


def render(root: str, ref_dir: str, data: dict) -> str:
    total = sum(len(v) for v in data.values())
    lines = [
        "# Reference corpus — index",
        "",
        "Entry point for the third-party reference corpus integrated under this tree.",
        "Every page below is reachable from this file; nothing here is decorative.",
        "",
        f"**{total} pages across {len(data)} categories.** Generated from disk by",
        "`scripts/test/gen_corpus_index.py` — do not edit by hand, regeneration",
        "overwrites it and drift is caught by `--check`.",
        "",
        "Consumed by: root `SKILL.md`, `testing/hunt/*`, and any skill that needs a",
        "payload class or methodology page. Absolute paths assume the skill root.",
        "",
        "---",
        "",
    ]
    for cat, rows in data.items():
        blurb = CATEGORY_BLURB.get(cat, "")
        lines.append(f"## `{cat}` — {len(rows)} page(s)")
        if blurb:
            lines.append("")
            lines.append(blurb)
        lines.append("")
        for rel, title, size in rows:
            lines.append(f"- [{title}]({rel}) — `{rel}` ({size:,} B)")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    check = "--check" in argv
    root = os.path.abspath(args[0] if args else ".")
    ref_dir = os.path.join(root, "testing", "references")
    if not os.path.isdir(ref_dir):
        sys.stderr.write(f"gen_corpus_index: no such directory: {ref_dir}\n")
        return 2

    target = os.path.join(ref_dir, INDEX_NAME)
    content = render(root, ref_dir, collect(ref_dir))

    if check:
        existing = open(target, encoding="utf-8").read() if os.path.exists(target) else ""
        if existing != content:
            sys.stderr.write(f"gen_corpus_index: {INDEX_NAME} is stale — regenerate\n")
            return 1
        print(f"  OK gen_corpus_index: {INDEX_NAME} matches disk")
        return 0

    open(target, "w", encoding="utf-8", newline="\n").write(content)
    data = collect(ref_dir)
    print(f"  gen_corpus_index: wrote {sum(len(v) for v in data.values())} page(s) "
          f"across {len(data)} categor(ies) -> {os.path.relpath(target, root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
