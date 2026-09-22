#!/usr/bin/env python3
"""Dependency leak scanner — detect private registry refs in package manifests.
Author: novalabs | License: MIT
"""
import argparse
import json
import re
from pathlib import Path

PATTERNS = [
    (r'"registry"\s*:\s*"([^"]+)"', "npm_registry", "npm: registry field"),
    (r'"resolved"\s*:\s*"https://([^/]*private[^"]*)"', "private_npm", "npm: private resolved URL"),
    (r'@scope[^\s]+@(\d+\..+?)\s', "scoped_pkg", "npm: scoped package"),
    (r'requirements.*--index-url\s+(https://[^\s]+)', "pip_index", "pip: custom index URL"),
    (r'requirements.*--extra-index-url\s+(https://[^\s]+)', "pip_index", "pip: extra index URL"),
    (r'requirements.*\[trusted-host=([^\]]+)\]', "pip_trusted", "pip: trusted host"),
    (r'Pipfile.*url\s*=\s*"(https://[^"]+)"', "pipfile_index", "Pipfile: private source"),
]

def scan_file(filepath):
    findings = []
    try:
        content = filepath.read_text(errors="ignore")
        for pat, cat, desc in PATTERNS:
            for m in re.finditer(pat, content, re.IGNORECASE):
                findings.append({
                    "file": str(filepath),
                    "category": cat,
                    "description": desc,
                    "match": m.group()[:120],
                })
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
    return findings

def main():
    parser = argparse.ArgumentParser(description="Scan dependency manifests for private registry leaks")
    parser.add_argument("--file", "-f", help="Single file")
    parser.add_argument("--dir", "-d", default=".", help="Directory (recursive)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.file:
        files = [Path(args.file)]
    else:
        d = Path(args.dir)
        files = []
        for pattern in ["package.json", "package-lock.json", "yarn.lock",
                         "requirements.txt", "Pipfile", "pyproject.toml"]:
            files.extend(d.rglob(pattern))

    results = []
    for f in files:
        results.extend(scan_file(f))

    if args.json:
        print(json.dumps({"total": len(results), "findings": results}, indent=2))
    else:
        for r in results:
            print(f"[{r['category']}] {r['description']}: {r['file']}")

    return 0

if __name__ == "__main__":
    exit(main())
