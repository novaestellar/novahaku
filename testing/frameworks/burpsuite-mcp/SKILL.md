---
name: burpsuite-mcp
description: "Use when testing web applications via BurpSuite MCP integration. Provides access to 83 BurpSuite tools including Proxy, Intruder, Repeater, Scanner, Collaborator. Use for HTTP interception, request modification, automated scanning, and vulnerability verification."
author: novalabs
version: 1.0.0
license: MIT
---

# BurpSuite MCP Wrapper

Wraps BurpSuite MCP server (stdio, port 9876) for Hermes agent use.

## Activation

Load via `skill_view(name="novahaku", file_path="testing/frameworks/burpsuite-mcp/SKILL.md")`

## Available Tool Groups

- **Proxy**: HTTP request/response interception and modification
- **Intruder**: Automated attack string injection
- **Repeater**: Manual request crafting and replay
- **Scanner**: Automated vulnerability scanning
- **Collaborator**: Out-of-band interaction detection
- **Target**: Site map and scope management
- **Decoder**: Encoding/decoding utilities
- **Comparer**: Response diffing

## Setup

1. BurpSuite must be running with MCP extension loaded
2. MCP bridge runs on port 9876 (stdio transport)
3. Verify: `mcp__burpsuite__` tools should appear in tool list

## Usage Pattern

```
1. Intercept request via Proxy
2. Send to Repeater for manual testing
3. Use Intruder for parameter fuzzing
4. Verify findings with Collaborator
```

## Verified Working (2026-09-10)

All 83 tools tested against Burp Community 2026.8. Key usage notes:

| Tool | Notes |
|------|-------|
| `burp_jwt_attack` | `attack` param must be `"none"` (not `"alg:none"`). Returns forged token with `alg: none`. |
| `burp_repeater_send` | Pass raw request; LF line endings accepted (auto-normalized to CRLF). |
| `burp_repeater_modify_send` | Supports `add_header`, `replace_header`, `replace_body`. |
| `burp_race_condition` | Concurrent send; returns per-request status/length + `verdict`. |
| `burp_access_control_sweep` | `auth_headers` is pipe-separated; empty entry = unauthenticated baseline. |
| `burp_inline_fuzzer` | FUZZ marker replacement with wordlist. |

**Not available in Community Edition:** `burp_scan_active` (active scan), `burp_crawl` (needs Pro).

### CRLF patch
Raw-request tools originally required CRLF line endings; LF-only input (as delivered over JSON/MCP)
produced malformed requests that failed over TLS (status 0). Fixed in
`burp-mcp-full/src/main/java/com/burpmcp/McpHttpServer.java` via a `crlf()` normalizer applied at
every raw-request call site. Jar rebuilt; extension reloads automatically (`auto_reload: true`).
