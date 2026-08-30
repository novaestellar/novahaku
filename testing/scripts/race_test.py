#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
race_test.py — concurrent request tester (stdlib-only)
Usage:
  python race_test.py <url> [--method POST] [--data 'k=v&k2=v2' | --json '{"a":1}']
                    [--n 30] [--workers 15] [--cookie "sid=x"] [--jwt TOKEN]
                    [--header "X-CSRF: abc"]
No-arg = help. Fire N identical requests in parallel; print status/body signature distribution.
Different responses or duplicate side-effects = race condition candidate.
"""
import sys, os, json, ssl, hashlib, time
import urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) race-test/1.0"

def build_opener():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

def one(opener, url, method, data, headers, timeout):
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = opener.open(r, timeout=timeout)
        body = resp.read(100000)
        sig = hashlib.md5(body).hexdigest()[:10]
        return resp.status, sig, body[:200].decode(errors="replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read(100000)
            sig = hashlib.md5(body).hexdigest()[:10]
            return e.code, sig, body[:200].decode(errors="replace")
        except Exception:
            return e.code, "ERR", ""
    except Exception as e:
        return None, "ERR", str(e)[:150]

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    url = sys.argv[1]
    method, data, n, workers = "POST", None, 30, 15
    headers = {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"}
    i = 2
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--method":
            method = sys.argv[i + 1]; i += 2
        elif a == "--data":
            data = sys.argv[i + 1].encode(); i += 2
        elif a == "--json":
            data = sys.argv[i + 1].encode()
            headers["Content-Type"] = "application/json"; i += 2
        elif a == "--n":
            n = int(sys.argv[i + 1]); i += 2
        elif a == "--workers":
            workers = int(sys.argv[i + 1]); i += 2
        elif a == "--cookie":
            headers["Cookie"] = sys.argv[i + 1]; i += 2
        elif a == "--jwt":
            headers["Authorization"] = "Bearer " + sys.argv[i + 1]; i += 2
        elif a == "--header":
            k, _, v = sys.argv[i + 1].partition(":")
            headers[k.strip()] = v.strip(); i += 2
        else:
            i += 1

    print(f"[*] race: {method} {url}  x{n}  workers={workers}")
    opener = build_opener()
    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one, opener, url, method, data, headers, 15) for _ in range(n)]
        for f in as_completed(futs):
            results.append(f.result())
    dt = time.time() - t0
    print(f"[*] done in {dt:.2f}s")

    status_c = Counter(r[0] for r in results)
    sig_c = Counter(r[1] for r in results)
    print("status distribution:", dict(status_c))
    print("body-signature distribution:", dict(sig_c))

    if len(sig_c) > 1:
        print("\n[!!] RESPONSES DIFFER — race condition candidate. Examples:")
        seen = set()
        for st, sig, prev in results:
            if sig not in seen:
                seen.add(sig)
                print(f"  status={st} sig={sig} body={prev!r}")
    else:
        print("\n[-] all responses identical — no obvious race at response level")
        print("[i] catatan: race bisa terjadi tanpa beda response (e.g. DB double-write).")
        print("    Verifikasi efeknya langsung di DB/state (saldo? stok? duplikat row?).")

if __name__ == "__main__":
    main()
