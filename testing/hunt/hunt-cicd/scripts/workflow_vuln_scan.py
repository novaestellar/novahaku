#!/usr/bin/env python3
"""GitHub Actions workflow vulnerability scanner
Author: novalabs
License: MIT

Scans GitHub repositories for vulnerable workflow patterns:
- pull_request_target with secrets access
- Script injection via github.event.*
- Unpinned actions (not SHA-locked)
"""
import argparse
import json
try:
    from github import Github
    import yaml
except ImportError:
    print("[!] Missing dependencies. Install: pip install PyGithub PyYAML")
    exit(1)

def analyze_workflow(workflow_content, workflow_name):
    """Analyze workflow YAML for vulnerabilities"""
    findings = []
    
    try:
        data = yaml.safe_load(workflow_content)
    except yaml.YAMLError:
        return findings
    
    # Pattern 1: pull_request_target with secrets
    triggers = str(data.get("on", {}))
    if "pull_request_target" in triggers:
        jobs = data.get("jobs", {})
        for job_name, job in jobs.items():
            job_str = str(job)
            if "secrets" in job_str or "${{ secrets." in job_str:
                findings.append({
                    "severity": "CRITICAL",
                    "issue": "pull_request_target with secrets access",
                    "workflow": workflow_name,
                    "description": f"Job '{job_name}' grants untrusted PR access to repo secrets"
                })
    
    # Pattern 2: Script injection (github.event.* in run:)
    for job_name, job in data.get("jobs", {}).items():
        for step in job.get("steps", []):
            run_cmd = step.get("run", "")
            if "${{ github.event" in run_cmd:
                findings.append({
                    "severity": "HIGH",
                    "issue": "Script injection via github.event",
                    "workflow": workflow_name,
                    "description": f"User input in shell: {run_cmd[:100]}"
                })
    
    # Pattern 3: Unpinned actions (not SHA)
    for job_name, job in data.get("jobs", {}).items():
        for step in job.get("steps", []):
            uses = step.get("uses", "")
            if uses and "@" in uses:
                ref = uses.split("@")[1]
                # Check if not a 40-char SHA
                if len(ref) != 40 or not all(c in "0123456789abcdef" for c in ref):
                    findings.append({
                        "severity": "MEDIUM",
                        "issue": "Unpinned action version",
                        "workflow": workflow_name,
                        "description": f"{uses} not pinned to SHA"
                    })
    
    return findings

def scan_repo(repo, github_token=None):
    """Scan a single repository for workflow vulnerabilities"""
    all_findings = []
    
    try:
        workflows = repo.get_contents(".github/workflows")
    except Exception:
        return all_findings
    
    for wf in workflows:
        if not wf.name.endswith((".yml", ".yaml")):
            continue
        
        try:
            content = wf.decoded_content.decode()
            findings = analyze_workflow(content, wf.name)
            for f in findings:
                f["repo"] = repo.full_name
            all_findings.extend(findings)
        except Exception:
            pass
    
    return all_findings

def scan_target(target, github_token):
    """Scan organization or user for vulnerable workflows"""
    g = Github(github_token)
    all_findings = []
    
    try:
        repos = g.search_repositories(query=f"user:{target}")
        for repo in repos:
            findings = scan_repo(repo, github_token)
            all_findings.extend(findings)
    except Exception as e:
        print(f"[!] Error scanning {target}: {e}")
    
    return all_findings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Actions workflow vulnerability scanner")
    parser.add_argument("--target", required=True, help="GitHub org or username")
    parser.add_argument("--token", required=True, help="GitHub PAT (required for API access)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()
    
    print(f"[*] Scanning {args.target}...")
    findings = scan_target(args.target, args.token)
    
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        if not findings:
            print("[+] No vulnerabilities found")
        for f in findings:
            print(f"[{f['severity']}] {f['repo']}/{f['workflow']}: {f['issue']}")
            print(f"    {f['description']}")
