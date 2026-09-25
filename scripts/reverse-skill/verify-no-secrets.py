#!/usr/bin/env python3
"""Verify that no secret, credential, or runtime artifact is tracked by git.

Reads the git INDEX, not the working tree: a file that is .gitignore'd locally
but still tracked would ship to a clone, and a working-tree scan would miss it.
Run `git add` before this or the index is stale and the gate cannot bite.

Exit 0 = clean. Exit 1 = at least one leak-path or unexplained secret.

Known-benign content is declared in ALLOW below with a reason. The allowlist is
narrow on purpose: it names exact (file, pattern) pairs, not whole directories,
so a new secret in an already-excused file still fails.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve()
while not (REPO / ".git").exists():
    REPO = REPO.parent
    if REPO.parent == REPO:
        sys.exit("verify-no-secrets: not inside a git repository")

# Paths that must never be tracked. Runtime state and per-target engagement data
# are the real risk here: they carry live credentials and target findings.
LEAK_PATH = re.compile(
    r"(?i)("
    r"\.env$|\.env\.(?!example)|"
    r"\.key$|\.pem$|\.p12$|\.pfx$|\.jks$|\.keystore$|"
    r"vault\.dat$|\.secret$|\.credential$|\.token$|"
    r"id_rsa|id_ed25519|"
    r"^config\.yaml$|\.pid$|\.log$|"
    r"^runs/|^work/"
    r")"
)

# Per-target engagement output. The TEMPLATE ships so the layout stays
# documented; real target data never does.
LEAK_ENGAGEMENT = re.compile(
    r"^engagements/(?!TEMPLATE/).*/(findings|results|candidates|chain|state)\.(json|csv)$"
)

SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("OpenAI-style key", re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("Anthropic key", re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}")),
    ("xAI key", re.compile(r"xai-[A-Za-z0-9]{20,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("Telegram bot token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b")),
    ("Slack token", re.compile(r"xox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("Private key header", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("JWT literal", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("Hardcoded password", re.compile(r"(?i)\bpassword\s*[:=]\s*[\"'][^\"'{\s$][^\"']{7,}[\"']")),
    ("Crack metadata", re.compile(r"(?i)crack@|\bKEYGEN\.exe\b")),
]

# Only these families get placeholder-tolerance. A credential with real entropy
# (AKIA..., ghp_..., sk-...) is reported even if it happens to contain the
# substring "example" — that spelling shows up in genuine keys often enough that
# exempting it would blind the gate. Teaching material for passwords and JWTs,
# on the other hand, is legitimately full of words like "example" and "...".
PLACEHOLDER_TOLERANT = {"Hardcoded password", "JWT literal"}
PLACEHOLDER_RX = re.compile(r"(?i)your-|example|placeholder|xxx+|<.*?>|\.\.\.|REDACTED|\{\{")

# (path-suffix, pattern-name) -> reason. Anything not listed fails the gate.
ALLOW = {
    ("scripts/reverse-skill/verify-no-secrets.py", "Crack metadata"):
        "the pattern IS the detector; self-reference, not a credential",
    ("testing/offensive-osint/scripts/secret_scan.py", "Private key header"):
        "the pattern IS the detector; removing it disables secret scanning",
    ("testing/offensive-osint/SKILL.md", "Private key header"):
        "documentation of the detector pattern (table + regex list)",
    ("testing/offensive-osint/SKILL.md", "Crack metadata"):
        "technique name in the skill's own domain list",
    ("testing/references/web-notes/xss-cross-site-scripting/README.md", "Private key header"):
        "DKIM spoofing payload example",
    ("identity/terms.md", "Crack metadata"):
        "glossary/trigger mapping entry",
    ("attack/test/test-novahaku.py", "Crack metadata"):
        "name of a capability probe in the test suite",
    ("attack/attack-flow/05-cross-model-evals.md", "Crack metadata"):
        "name of a capability probe in the eval matrix",
    ("testing/dotnet-reverse/SKILL.md", "Crack metadata"):
        "technique name in the .NET patching workflow",
    ("testing/wordlists/common.txt", "Crack metadata"):
        "dictionary entry, consumed as wordlist data",
    ("testing/wordlists/raft-medium-directories.txt", "Crack metadata"):
        "dictionary entry, consumed as wordlist data",
    ("testing/references/payloads/XSS Injection/README.md", "Crack metadata"):
        "payload example",
    ("testing/references/payloads/xss.md", "Crack metadata"):
        "payload example",
}

# Corpus pages teaching these attacks. Every entry is a forged/demo value, but
# the gate still prints the count so a real token added here is visible.
ALLOW_PREFIX = (
    ("testing/references/payloads/", "JWT literal"),
    ("testing/references/payloads/", "Hardcoded password"),
    ("testing/references/payloads-extras/", "JWT literal"),
    ("testing/references/payloads-extras/", "Hardcoded password"),
    ("testing/references/generic-hacking/", "JWT literal"),
    ("testing/references/generic-methodologies-and-resources/", "JWT literal"),
    ("testing/references/web-notes/", "JWT literal"),
    ("testing/references/windows-hardening/", "Hardcoded password"),
    ("testing/generic-hacking/", "JWT literal"),
    ("testing/windows-hardening/", "Hardcoded password"),
    ("testing/pentest-tools/src-hunter/references/", "JWT literal"),
    ("testing/pentest-tools/src-hunter/references/", "Hardcoded password"),
)

TEXT_EXT = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt", ".csv",
            ".ps1", ".command", ".cfg", ".ini", ".conf", ".example", ".xml"}


def git_ls_files():
    r = subprocess.run(["git", "-C", str(REPO), "-c", "core.quotepath=false", "ls-files"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180)
    if r.returncode != 0:
        sys.exit("verify-no-secrets: git ls-files failed: " + r.stderr.strip())
    return [l for l in r.stdout.splitlines() if l.strip()]


def main():
    tracked = git_ls_files()
    print("verify-no-secrets: %d tracked files (git index)" % len(tracked))
    if not tracked:
        sys.exit("verify-no-secrets: index is empty — run `git add` first")

    failures = []

    # 1. Path rules
    for rel in tracked:
        if LEAK_PATH.search(rel) or LEAK_ENGAGEMENT.search(rel):
            failures.append("leak-path tracked: " + rel)

    # 2. Content rules
    allowed_hits = 0
    for rel in tracked:
        if Path(rel).suffix.lower() not in TEXT_EXT:
            continue
        p = REPO / rel
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:4096]:
            continue
        txt = raw.decode("utf-8", errors="replace")
        for label, rx in SECRET_PATTERNS:
            for m in rx.finditer(txt):
                snippet = m.group(0)[:60]
                if label in PLACEHOLDER_TOLERANT and PLACEHOLDER_RX.search(snippet):
                    continue
                if (rel, label) in ALLOW:
                    allowed_hits += 1
                    continue
                if any(rel.startswith(pre) and label == lbl for pre, lbl in ALLOW_PREFIX):
                    allowed_hits += 1
                    continue
                line = txt[:m.start()].count("\n") + 1
                failures.append("secret at %s:%d  [%s]  %s" % (rel, line, label, snippet))

    print("verify-no-secrets: %d documented-benign match(es) in teaching material" % allowed_hits)

    if failures:
        print("\nFAIL — %d finding(s):" % len(failures))
        for f in failures[:60]:
            print("  " + f)
        if len(failures) > 60:
            print("  ... and %d more" % (len(failures) - 60))
        return 1

    print("OK verify-no-secrets: no secret, credential or runtime artifact is tracked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
