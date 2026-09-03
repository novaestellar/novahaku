---
name: baas-security-audit
description: "Use when auditing Supabase/BaaS web apps."
version: 1.0.0
author: SeaGull Security Lab
license: MIT
metadata:
  hermes:
    tags: [security, audit, supabase, rls, payment, cloudflare-pages]
    related_skills: [advanced-bug-hunting, security-checklist, bug-hunting]
---

# BaaS Web App Security Audit

Audit playbook for frontend-only apps on a BaaS backend (Supabase primarily) where
the anon/publishable key is public and RLS is the whole backend. Battle-tested over
7 passes against a production Supabase + Cloudflare Pages + Worker storefront.

## When to use

- User asks "check this web security" / audit a storefront or dashboard on Supabase.
- Before shipping any Supabase frontend: RLS + RPCs + storage are the attack surface.

## Audit workflow (order matters — each pass assumes the last)

1. **Inventory + read every SQL migration.** Enumerate all public functions:
   `grep "create or replace function public\." *.sql | sort -u` and audit EVERY
   `grant execute` / `revoke execute` line. An RPC is callable by anyone with the
   anon key unless explicitly revoked — grants are the real gate, not RLS.
2. **Live config + headers:** `curl -sI <site>` for CSP/HSTS/X-Frame-Options;
   fetch the frontend config JS to grab the anon key (public by design) for probes.
3. **Anon probe pass:** REST reads on every table (profiles, orders, secrets),
   storage public URLs, admin RPCs. Expect empty `[]` / auth errors.
4. **RPC exploit pass with CONTROL tests:** for each secret-gated RPC call it with a
   WRONG token first (must say "unauthorized") — only then is a success with the real
   token meaningful. Use fictitious IDs (`ORDER-DEADBEEF`); stop before any probe
   would create/alter a real production row.
5. **Payment-flow pass:** who can mark PAID? Is QR amount set server-side from DB?
   Is `message = order_id` binding validated? Order-ID entropy check. See references.
6. **Deploy-artifact pass:** curl sensitive paths (`*.sql`, `.md`, `security-audit/`,
   backups, `.gitignore`) and INSPECT CONTENT — HTTP 200 is ambiguous on Pages (SPA
   fallback). `0 bytes` = absent; real file content = leaked.
7. **Frontend DOM pass:** every `innerHTML` sink vs `sanitizeText()` coverage,
   open redirects (`location.href =`), third-party exfil URLs in CSP
   (`img-src`/`connect-src` hosts that receive payment/auth data).

## Critical pitfalls (all found live — see references/supabase-baas-audit.md)

- `uuid <> auth.uid()` is NULL for anon → auth bypass. Use `is distinct from` +
  explicit `auth.uid() is null` guard.
- `security definer` RPCs bypass RLS internally — must self-validate auth.
- Storage `/object/public/` render path IGNORES RLS; `name like '%images/%'` is a
  substring match (`notimages/` passes).
- Migration `.sql` files deployed with the site leak INSERT-ed secrets — rotate the
  secret AND redeploy with `--exclude`; rotation alone is not enough while live.
- `.pagesignore` unreliable — use explicit `wrangler pages deploy --exclude=...`.
- Fresh-signup test for email confirmation (re-signup of existing user proves nothing).
- Client-side Origin/Referer checks are spoofable from curl.
- QR render fallbacks sending the QRIS string to third-party hosts = payment data exfil.

## Tooling notes

- Write multi-step probes as Python scripts with `urllib.request`, NOT inline bash
  curl — nested `$(...)` + mixed quotes break repeatedly on Windows git-bash.
- Supabase `sb_publishable_*` keys are NOT JWTs (base64 decode fails) — new format.

## Reporting

Deliver: findings table (severity, evidence from live probes, fix SQL/command),
a "proven safe" section (what was tested and held), and an ordered fix list
(rotate → redeploy-exclude → revoke grants → guards). Keep PoC scripts alongside
the report with destructive-action warnings.

## References

- `references/supabase-baas-audit.md` — detailed findings, SQL patterns, verified
  probe techniques from the PayStore production audit.
