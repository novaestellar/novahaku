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
