---
name: ctf-sandbox
description: "CTF competition sandbox: dispatcher over 38 competition scenario modules."
---

# CTF Sandbox (Dispatcher)

## ACTION REQUIRED

1. Identify the CTF category from the challenge.
2. List modules: `ls testing/ctf-sandbox/competition-*/`
3. Open the matching `SKILL.md` under `testing/ctf-sandbox/competition-<name>/`.

## Module index (38)

| Category | Modules |
|---|---|
| Crypto | `competition-crypto-mobile` |
| Web | `competition-jwt-claim-confusion`, `competition-oauth-oidc-chain`, `competition-request-normalization-smuggling`, `competition-graphql-rpc-drift`, `competition-race-condition-state-drift`, `competition-template-render-path` |
| Cloud/K8s | `competition-agent-cloud`, `competition-cloud-metadata-path`, `competition-k8s-control-plane`, `competition-container-runtime`, `competition-ssrf-metadata-pivot` |
| Windows/AD | `competition-identity-windows`, `competition-kerberos-delegation`, `competition-lsass-ticket-material`, `competition-dpapi-credential-chain`, `competition-windows-pivot`, `competition-ad-certificate-abuse`, `competition-relay-coercion-chain` |
| Linux | `competition-linux-credential-pivot`, `competition-kernel-container-escape` |
| Mobile | `competition-android-hooking`, `competition-ios-runtime` |
| Forensics | `competition-forensic-timeline`, `competition-malware-config`, `competition-pcap-protocol`, `competition-stego-media`, `competition-file-parser-chain`, `competition-zip-archive` |
| Firmware/IoT | `competition-firmware-layout` |
| Supply chain | `competition-supply-chain` |
| Browser | `competition-browser-persistence`, `competition-bundle-sourcemap-recovery` |
| Runtime | `competition-runtime-routing`, `competition-websocket-runtime`, `competition-queue-worker-drift`, `competition-custom-protocol-replay`, `competition-mailbox-abuse` |

## Keywords
CTF, AWD, sandbox, competition, 靶场, 比赛题, challenge, jeopardy
