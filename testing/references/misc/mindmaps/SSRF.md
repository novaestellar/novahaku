# SSRF (Server-Side Request Forgery) — Mindmap

## Attack Surface
- URL/webhook parameters, import-from-URL, PDF renderers, image proxies
- File upload by URL, XML parsers with external entities, RSS/feed readers
- Webhook callbacks, OAuth callback URLs, thumbnail generators

## Cloud Metadata Endpoints
- **AWS EC2**: `http://169.254.169.254/latest/meta-data/`, IMDSv2 needs `X-aws-ec2-metadata-token`
- **AWS ECS**: `http://169.254.170.2/v2/credentials/<GUID>`
- **GCP**: `http://metadata.google.internal/computeMetadata/v1/` (needs `Metadata-Flavor: Google`)
- **Azure**: `http://169.254.169.254/metadata/instance?api-version=2021-02-01` (needs `Metadata: true`)
- **DigitalOcean**: `http://169.254.169.254/metadata/v1/`
- **Alibaba**: `http://100.100.100.200/latest/meta-data/`

## Bypass Techniques
- **DNS rebinding**: resolve to internal IP after validation
- **Open redirect chaining**: trusted domain redirects to internal host
- **Decimal/octal/hex IP**: `http://2130706433/`, `http://0177.0.0.1/`, `http://0x7f000001/`
- **IPv6 / IPv4-mapped**: `http://[::ffff:127.0.0.1]/`
- **URL parser confusion**: `http://attacker.com@127.0.0.1/`, `http://127.0.0.1#@attacker.com`
- **Redirect-based**: 302 to internal target
- **Protocol smuggling**: `gopher://`, `dict://`, `file://`, `ftp://`

## Exploitation Chains
- Redis via gopher → write SSH key / cron
- FastCGI via gopher → RCE
- Docker API (`2375`) → container escape
- Kubernetes API / etcd → cluster takeover
- Internal admin panels → auth bypass

## Blind SSRF
- Time-based detection, DNS interactions (Collaborator/Burp/burp-collaborator)
- Error-message-based port scanning

## Tools
- Burp Collaborator, interactsh, SSRFmap, Gopherus
