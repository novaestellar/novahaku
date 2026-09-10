---
name: anything-analyzer-mcp
description: "Use when analyzing web applications via Anything Analyzer MCP. Browser automation, HTTP capture, request replay, and API discovery. Use for web scraping, traffic analysis, and hidden endpoint discovery."
author: novalabs
version: 1.0.0
license: MIT
---

# Anything Analyzer MCP Wrapper

Wraps Anything Analyzer MCP server (remote, localhost:23816).

## Activation

Load via `skill_view(name="novahaku", file_path="testing/frameworks/anything-analyzer-mcp/SKILL.md")`

## Capabilities

- **Browser automation**: Navigate, click, fill forms, extract data
- **HTTP capture**: Record and replay HTTP traffic
- **API discovery**: Find hidden endpoints from traffic analysis
- **Request replay**: Modify and resend captured requests
- **WebSocket inspection**: Monitor and interact with WS connections

## Setup

1. Anything Analyzer server must be running on port 23816
2. Verify connectivity before use
3. Browser profile must be configured for target site

## Usage Pattern

```
1. Start capture session
2. Navigate target site naturally
3. Review captured traffic
4. Identify API endpoints and parameters
5. Replay with modifications for testing
```
