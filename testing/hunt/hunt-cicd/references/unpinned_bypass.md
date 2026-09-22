# Unpinned Actions — Attack & Detection Reference

## Overview

GitHub Actions that reference tags (`@v4`, `@main`) instead of commit SHAs are vulnerable to tag hijacking, maintainer compromise, and supply-chain attacks.

## Attack Patterns

### 1. Tag Rewrite Attack

Attacker compromises action maintainer → force-pushes malicious commit to tag.

```bash
# Attacker (compromised maintainer)
git tag -f v4 malicious_commit
git push -f origin v4
```

**Impact:** Every workflow using `@v4` executes malicious code in CI runner.

### 2. New Maintainer Takeover

Action transferred to new maintainer who pushes backdoor to main.

```yaml
# Vulnerable: tracks main branch
- uses: some-org/some-action@main
```

### 3. Dependency Chain Attack

Malicious update in transitive dependency of action.

```yaml
- uses: some/action@v2
  # action depends on compromised npm package
```

## Real-World Incidents

| Incident | Date | Impact |
|----------|------|--------|
| tj-actions/changed-files | 2025-03 | CI secrets exfiltrated across ~23,000 repos |
| actionlint supply chain | 2024-06 | Typosquatting on `reviewdog/action-pyang` |
| GitHub Actions cache poisoning | 2023 | Malicious cache artifact on `actions/cache` |

## Detection Patterns

```yaml
# Search for unpinned versions
grep -rn '@v[0-9]' .github/workflows/
grep -rn '@main' .github/workflows/
grep -rn '@latest' .github/workflows/

# Search for SHA-pinned (secure)
grep -rn '@[0-9a-f]\{40\}' .github/workflows/
```

### Workflow Scanner Usage

```bash
python workflow_vuln_scan.py --target <org> --token $GITHUB_TOKEN
```

Detects:
- `pull_request_target` with secrets access (CRITICAL)
- Unpinned action versions (MEDIUM)
- Script injection via `github.event.*` (HIGH)

## Mitigation

1. **Pin to commit SHA** — `@8f4b7f84864484a7bf31766abe9204da3cbe65b3`
2. **Use Dependabot** — auto-update pinned references
3. **Verify provenance** — `actions/attest-build-provenance`
4. **Environment protection** — require approval for first-time contributors

## References

- https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- https://slsa.dev/
- https://www.stepsecurity.io/blog/harden-runner-detection-tj-actions-changed-files-action
