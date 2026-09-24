#!/usr/bin/env python3
"""Dependency leak scanner — detect private registry refs and embedded credentials.

Author: novalabs | License: MIT

Coverage note: the original pattern set only matched `"registry": "..."` inside
package.json, so .npmrc files, git URLs with inline credentials, internal tarball
URLs and pip index flags all passed through undetected. Patterns below cover the
vectors that actually leak in practice.
"""
import argparse
import json
import re
from pathlib import Path

# Files that can carry a registry reference or a credential.
MANIFESTS = [
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "requirements.txt", "Pipfile", "Pipfile.lock", "pyproject.toml", "poetry.lock",
    ".npmrc", ".pypirc", ".yarnrc", ".yarnrc.yml", ".gemrc", "setup.py", "setup.cfg",
]

PATTERNS = [
    # -- npm / node ---------------------------------------------------------
    (r'"registry"\s*:\s*"([^"]+)"', "npm_registry", "npm: registry field"),
    (r'^\s*registry\s*=\s*(\S+)', "npm_registry", "npmrc: registry override"),
    (r'^\s*(?://[^\s:]+/)?:_authToken\s*=\s*(\S+)', "npm_token", "npmrc: auth token"),
    (r'^\s*(?://[^\s:]+/)?:_auth\s*=\s*(\S+)', "npm_token", "npmrc: basic auth"),
    (r'^\s*(?://[^\s:]+/)?:(?:_password|password)\s*=\s*(\S+)', "npm_token", "npmrc: password"),
    # Inline credentials in any URL: scheme://user:secret@host
    (r'[a-z][a-z0-9+.-]*://[^\s/@"\']+:[^\s/@"\']+@([^\s/"\']+)', "url_credential",
     "URL with embedded credentials"),
    (r'"resolved"\s*:\s*"(https?://[^"]+)"', "npm_resolved", "lockfile: resolved URL"),
    (r'"([^"]*)"\s*:\s*"(git\+[a-z]+://[^"]+|[a-z]+://[^"]*@[^"]+)"', "git_dep",
     "dependency: remote/git URL"),
    (r'"(?:tarball|dist)"\s*:\s*"(https?://[^"]+)"', "npm_tarball", "npm: tarball URL"),
    # -- pip / python -------------------------------------------------------
    (r'--index-url\s+(\S+)', "pip_index", "pip: custom index URL"),
    (r'--extra-index-url\s+(\S+)', "pip_index", "pip: extra index URL"),
    (r'--trusted-host[= ]\s*(\S+)', "pip_trusted", "pip: trusted host"),
    (r'url\s*=\s*"(https?://[^"]+)"', "pipfile_index", "Pipfile/poetry: source URL"),
    (r'index-url\s*=\s*(\S+)', "pip_config", "pip config: index URL"),
    (r'"?(?:repository_url|upload_url)"?\s*[:=]\s*"?(https?://\S+?)"?\s*$',
     "pip_repo", "python: repository URL"),
    # -- generic private-host heuristics -----------------------------------
    (r'https?://([a-z0-9.-]*(?:internal|private|corp|intranet|lan|local)[a-z0-9.-]*)',
     "private_host", "URL: private-looking hostname"),
]

# Internal-looking hosts are a lead, not proof. Downgrade to a note.
SOFT_CATEGORIES = {"private_host", "npm_resolved", "npm_tarball", "git_dep", "scoped_pkg"}

SCANNER_SELF = Path(__file__).resolve()


def redact(text):
    """Never echo a credential into a report. Keep a 6-char head for correlation."""
    text = re.sub(r'(://[^\s/@"\']+:)[^\s/@"\']+(@)', r'\1***REDACTED***\2', text)
    text = re.sub(r'(_authToken\s*=\s*)(\S+)', r'\1***REDACTED***', text)
    text = re.sub(r'(_auth\s*=\s*)(\S+)', r'\1***REDACTED***', text)
    text = re.sub(r'(_password\s*=\s*)(\S+)', r'\1***REDACTED***', text)
    # bare long secrets (npm_..., ghp_..., sk-..., AKIA...)
    text = re.sub(r'\b((?:npm|ghp|gho|sk|AKIA|xox[bp])[A-Za-z0-9_-]{4})[A-Za-z0-9_-]{6,}', r'\1...REDACTED', text)
    return text


def scan_file(filepath):
    findings = []
    if filepath.resolve() == SCANNER_SELF:
        return findings  # never flag our own pattern table
    try:
        content = filepath.read_text(errors="ignore")
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return findings
    for pat, cat, desc in PATTERNS:
        for m in re.finditer(pat, content, re.IGNORECASE | re.MULTILINE):
            findings.append({
                "file": str(filepath),
                "category": cat,
                "severity": "note" if cat in SOFT_CATEGORIES else "high",
                "description": desc,
                "line": content[:m.start()].count("\n") + 1,
                "match": redact(m.group()[:160]),
            })
    return findings


def dedupe(findings):
    seen, out = set(), []
    for f in findings:
        key = (f["file"], f["line"], f["category"], f["match"])
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Scan dependency manifests for private registry leaks and embedded credentials")
    parser.add_argument("--file", "-f", help="Single file")
    parser.add_argument("--dir", "-d", default=".", help="Directory (recursive)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.file:
        files = [Path(args.file)]
    else:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"[ERROR] not a directory: {d}")
            return 2
        files = []
        for pattern in MANIFESTS:
            files.extend(d.rglob(pattern))

    results = dedupe([f for path in sorted(set(files)) for f in scan_file(path)])

    if args.json:
        print(json.dumps({"total": len(results), "findings": results}, indent=2))
    else:
        high = [r for r in results if r["severity"] == "high"]
        if not results:
            print("No dependency leaks found.")
        for r in sorted(results, key=lambda x: (x["severity"] != "high", x["file"], x["line"])):
            tag = "LEAK" if r["severity"] == "high" else "note"
            print(f"[{tag}] {r['category']}: {r['file']}:{r['line']}")
            print(f"       {r['match']}")
        print(f"\nTotal: {len(results)} finding(s), {len(high)} high severity.")

    return 0


if __name__ == "__main__":
    exit(main())
