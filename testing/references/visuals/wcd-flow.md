# Web Cache Deception — request flow

Reproduction of the demonstration diagram. Four actors:

- **Victim** — a logged-in user
- **Attacker** — unauthenticated
- **Proxy Server** — a cache in front of the application
- **Main Server** — the application

## Phase 1 — the victim's request seeds the cache

1. **Victim → Proxy Server**
   ```
   GET http://www.example.com/home.php/non-existent.css
   ```
2. **Proxy Server → Main Server**
   ```
   GET http://www.example.com/home.php/non-existent.css
   ```
3. **Main Server → Proxy Server**
   ```
   Content of http://www.example.com/home.php
   ```
4. **Proxy Server → Victim**
   ```
   Content of http://www.example.com/home.php
   ```

The victim appends a fake `.css` path to a dynamic endpoint. The main server
ignores the suffix and returns the content of the base `home.php` page — the
victim's own authenticated content. The proxy sees a `.css` path, treats it as
static, cacheable content, and stores the response under that URL.

## Phase 2 — the attacker reads the cached copy

5. **Attacker → Proxy Server**
   ```
   GET http://www.example.com/home.php/non-existent.css
   ```
6. **Proxy Server → Attacker**
   ```
   Content of Victim's http://www.example.com/home.php
   ```

The attacker requests the same suffix-appended URL. The proxy serves the cached
copy instead of going upstream, so the attacker receives the victim's private
dynamic page without ever authenticating.

## Why it works

The bug is a disagreement about what a URL means. The cache keys and decides
cacheability on the path extension; the application routes on the path prefix and
ignores the rest. Any route where the application tolerates trailing garbage that
the cache reads as a static asset is a candidate:

- `home.php/nonexistent.css`
- `api/user/profile/foo.js`
- `account/../../static/x.png` (when normalisation differs)

The attack needs the victim to make one request to the crafted URL — a link or an
image tag on a page the victim visits is enough.

## Fixes

- Cache only what is safe to cache: never cache a response whose content type
  contradicts the extension in the URL.
- Normalise the path before the cache key is computed, and reject paths with
  trailing segments the route does not consume.
- Do not let the application route on a prefix while the cache keys on the full
  path; both layers must agree.
- Set `Cache-Control: private, no-store` on authenticated responses.
