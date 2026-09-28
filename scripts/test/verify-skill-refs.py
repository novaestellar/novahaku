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
# Matched on the WHOLE line (not just inside backticks) because routing tables
# reference skills as bare paths (`competition-runtime-routing/`) and as vars
# (`$competition-supply-chain`), not always in `backticks`. The namespace
# filter keeps this exact: probing showed only hunt-*/competition-* slugs are
# skill names — payload tags (`sqli-union`), CSP directives, and header names
# are NOT in these namespaces.
SLUG = re.compile(r"(?:hunt|competition)-[a-z0-9][a-z0-9-]*")
FENCE = re.compile(r"^\s*(```|~~~)")

# References that do not resolve to a skill directory. Two classes:
#
# 1. INTENTIONAL — genuinely fine, never a bug:
#    - hunt-subdomain-takeover: sibling cross-ref; the real skill is
#      `hunt-subdomain` (hunt-auth-bypass names both, the takeover primitive
#      lives under hunt-subdomain).
#    - hunt-zoho: hypothetical example in redteam-mindset §10
#      ("No hunt-zoho skill exists, so I logged a v1.1 gap").
#
# 2. RESOLVED (2026-09-28) — three phantom competition lanes (reverse-pwn,
#    web-runtime, prompt-injection) were named by routing docs but never adapted
#    into novahaku. Their references are now redirected to the real skills that
#    own the territory (competition-kernel-container-escape,
#    competition-runtime-routing, competition-agent-cloud), and the cookie-HMAC
#    auth-bypass reference was adopted under competition-jwt-claim-confusion.
ALLOWLIST = {
    "hunt-subdomain-takeover",
    "hunt-zoho",
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
            for slug in SLUG.findall(line):
                if slug not in known:
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
