#!/usr/bin/env python3
"""Verify backtick skill-name references resolve to a real skill directory.

Why this exists: verify-doc-links.py checks only Markdown links `[](...)`.
Skill names written as inline code (`hunt-sharepoint`, `triage-validation`)
in routing tables are invisible to it — seven skills dangled for whole
sessions because nothing checked the backtick form.

Narrow scope (deliberate): only `hunt-*` and `competition-*` namespaces are
checked. A lowercase-slug backtick span in those namespaces is unambiguously
a skill-name reference. Matching every backtick span is a 1000+ false-positive
trap: payload category tags (`sqli-union`, `ssrf-gopher`), CSP directives
(`style-src`), header names (`x-api-key`), and CLI verbs (`ssh-add`) all look
like slugs but are not skills.

Allowlist: known-intentional references (future-skill suggestions, sibling
cross-refs, hypothetical examples). Each entry records why it is allowed.

Reads from the git index, like verify-doc-links.py.

Exit 1 if a `hunt-*` / `competition-*` backtick slug is neither a tracked
skill directory nor allowlisted. Run from the repo root:
    python3 scripts/test/verify-skill-refs.py
"""
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Namespaced slugs that are unambiguously skill-name references.
SLUG = re.compile(r"^(hunt|competition)-[a-z0-9][a-z0-9-]*$")
INLINE_CODE = re.compile(r"`([^`]+)`")
FENCE = re.compile(r"^\s*(```|~~~)")

# Intentional references that do not (yet) resolve to a skill directory.
# Do not add entries casually — every entry hides a real dangling ref.
ALLOWLIST = {
    # Sibling cross-reference; the actual skill is `hunt-subdomain`
    # (hunt-auth-bypass names both, the takeover primitive lives there).
    "hunt-subdomain-takeover",
    # Hypothetical example in redteam-mindset §10 ("No hunt-zoho skill exists").
    "hunt-zoho",
    # Future-template suggestion in field-journal seed-010; the routing docs
    # name it as a planned lane, not a shipped skill.
    "competition-reverse-pwn",
}


def tracked_paths():
    out = subprocess.run(
        ["git", "-c", "core.quotePath=false", "ls-files", "-z"],
        capture_output=True, check=True,
    ).stdout.decode("utf-8")
    return {p for p in out.split("\0") if p}


def skill_names(files):
    names = set()
    for f in files:
        if f.endswith("SKILL.md"):
            names.add(os.path.basename(os.path.dirname(f)))
    return names


def main():
    files = tracked_paths()
    known = skill_names(files) | ALLOWLIST
    dangling = {}
    for f in sorted(p for p in files if p.endswith(".md")):
        result = subprocess.run(
            ["git", "show", f":{f}"], capture_output=True, check=False
        )
        if result.returncode != 0:
            continue
        text = result.stdout.decode("utf-8-sig")
        in_fence = False
        for line in text.splitlines():
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for span in INLINE_CODE.findall(line):
                slug = span.strip()
                if SLUG.match(slug) and slug not in known:
                    dangling.setdefault(slug, []).append(f)

    if dangling:
        print(f"FAIL verify-skill-refs: {len(dangling)} unresolved skill-name reference(s)")
        for slug in sorted(dangling):
            for f in dangling[slug]:
                print(f"  `{slug}` <- {f}")
        print("  (fix the reference, or add to ALLOWLIST in this script if intentional)")
        return 1
    print("OK verify-skill-refs: all hunt-*/competition-* skill-name references resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
