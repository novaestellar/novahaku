#!/usr/bin/env python3
"""Local vulnerable target for novahaku script functional tests.

Deliberately vulnerable. Binds 127.0.0.1 only. No external exposure.
"""
import base64
import json
import re
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HITS = {"race": 0, "lock": threading.Lock(), "token": 0}
CORRECT_JWT = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9."


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html"):
        raw = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        p = self.path
        q = urllib.parse.parse_qs(urllib.parse.urlparse(p).query)

        # root-level reflected XSS (`/?q=`) — matches webtest mod_xss
        if urllib.parse.urlparse(p).path in ("/", ""):
            # SSRF first: `url` is also a redirect param, and webtest sends
            # internal-looking values for the ssrf module.
            for k in ("url", "uri", "path", "dest", "redirect", "next", "target", "proxy"):
                if k in q and re.search(r"127\.0\.0\.1|localhost|169\.254|file://|gopher://", q[k][0], re.I):
                    return self._send(200, '{"internal":"169.254.169.254 metadata reachable"}', "application/json")
            # traversal bait
            for k in ("file", "page", "path", "include", "load", "doc", "download"):
                if k in q and (".." in q[k][0] or "etc/passwd" in q[k][0]):
                    return self._send(200, "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/bin")
            if "q" in q or "search" in q or "query" in q or "name" in q or "msg" in q or "template" in q:
                val = (q.get("q") or q.get("search") or q.get("query")
                       or q.get("name") or q.get("msg") or q.get("template") or [""])[0]
                # SQLi error bait (checked before SSTI: both send quotes/braces)
                if re.search(r"'|\"|or\s+1|union|select|sleep\(", val, re.I):
                    return self._send(500, f"SQL syntax error near '{val}'")
                # SSTI bait: evaluate the arithmetic templates webtest sends
                for tmpl, res in (("{{7*7}}", "49"), ("${7*7}", "49"),
                                  ("<%= 7*7 %>", "49"), ("#{7*7}", "49")):
                    if tmpl in val:
                        return self._send(200, f"<html>rendered: {val.replace(tmpl, res)}</html>")
                return self._send(200, f"<html>results for {val}</html>")
            # generic param bait for the remaining webtest param lists
            # (sqli params: id,user,page,cat,product,item,news_id,article)
            for k in ("id", "user", "page", "cat", "product", "item", "news_id", "article"):
                if k in q and re.search(r"'|\"|union|select|sleep\(|and\s+1", q[k][0], re.I):
                    return self._send(500, f"SQL syntax error near '{q[k][0]}'")
            # SSTI on the dedicated ssti params (name, msg, template, search)
            for k in ("name", "msg", "template", "search", "query", "q"):
                if k in q:
                    for tmpl, res in (("{{7*7}}", "49"), ("${7*7}", "49"),
                                      ("<%= 7*7 %>", "49"), ("#{7*7}", "49")):
                        if tmpl in q[k][0]:
                            return self._send(200, f"<html>rendered: {q[k][0].replace(tmpl, res)}</html>")
            # root-level open redirect (`/?url=`) — matches webtest mod_redirect
            for k in ("url", "next", "return", "redirect", "goto", "redirect_uri"):
                if k in q:
                    self.send_response(302)
                    self.send_header("Location", q[k][0])
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
            return self._send(200, "<html>home\nTraceback (most recent call last):\n  File \"/app/main.py\", line 42\nDEBUG = True\n</html>")

        # directory listing (dirfuzz bait)
        if p.startswith("/admin") or p.startswith("/backup") or p.startswith("/.git"):
            return self._send(200, "<html><title>Index of /admin</title><a href='../'>Parent</a> secret_admin_panel</html>")

        # CORS reflect with credentials
        if p.startswith("/api/cors"):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin", "*"))
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "27")
            self.end_headers()
            self.wfile.write(b'{"user":"admin","ok":true}')
            return

        # protected endpoint: ENFORCES auth. 401 without token.
        # accepts only the alg:none forged token -> a real, provable bypass.
        if p.startswith("/api/protected"):
            auth = self.headers.get("Authorization") or ""
            if not auth.startswith("Bearer "):
                return self._send(401, '{"error":"missing token"}', "application/json")
            tok = auth[7:]
            hdr_b64 = tok.split(".")[0] if "." in tok else ""
            try:
                hdr = json.loads(base64.urlsafe_b64decode(hdr_b64 + "==="))
            except Exception:
                hdr = {}
            if hdr.get("alg") == "none":
                return self._send(200, '{"secret":"admin data leaked","via":"alg:none"}', "application/json")
            return self._send(403, '{"error":"invalid signature"}', "application/json")

        # JWT debug endpoint leaking a token
        if p.startswith("/api/debug"):
            return self._send(200, json.dumps({"token": CORRECT_JWT, "alg": "none"}), "application/json")

        # IDOR: any id returns data
        if p.startswith("/api/user"):
            return self._send(200, json.dumps({"id": 1, "email": "admin@local.test", "role": "admin"}), "application/json")

        # reflected XSS
        if p.startswith("/search"):
            q = p.split("q=", 1)[1] if "q=" in p else ""
            return self._send(200, f"<html>results for {q}</html>")

        # open redirect
        if p.startswith("/go"):
            tgt = p.split("url=", 1)[1] if "url=" in p else "/"
            self.send_response(302)
            self.send_header("Location", tgt)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        return self._send(404, "<html>404</html>")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Allow", "GET, POST, OPTIONS, TRACE, PUT")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_TRACE(self):
        # XST: echo the request back — matches webtest mod_methods TRACE check
        self.send_response(200)
        self.send_header("Content-Type", "message/http")
        body = f"TRACE / HTTP/1.1\r\nHost: {self.headers.get('Host','')}\r\n\r\n"
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode())

    def do_PUT(self):
        # accepts writes — matches webtest mod_methods PUT check
        n = int(self.headers.get("Content-Length") or 0)
        if n:
            self.rfile.read(n)
        return self._send(200, "written")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""

        # login: reflects error with input (SQLi/error bait)
        if self.path.startswith("/login"):
            try:
                d = json.loads(body or b"{}")
            except Exception:
                d = {}
            u = str(d.get("username", ""))
            if "'" in u or '"' in u or " or " in u.lower():
                return self._send(500, f"SQL syntax error near '{u}'", "application/json")
            return self._send(401, '{"error":"invalid credentials"}', "application/json")

        # SSRF bait
        if self.path.startswith("/fetch"):
            try:
                d = json.loads(body or b"{}")
            except Exception:
                d = {}
            u = str(d.get("url", ""))
            if u.startswith("http://127.0.0.1") or "169.254" in u or "localhost" in u:
                return self._send(200, '{"internal":"169.254.169.254 metadata reachable"}', "application/json")
            return self._send(200, '{"outcome":"fetched"}', "application/json")

        # RACE: non-atomic redeem, deliberately racy
        if self.path.startswith("/redeem"):
            with HITS["lock"]:
                cur = HITS["race"]
                time.sleep(0.002)          # widen the window on purpose
                HITS["race"] = cur + 1
                got = HITS["race"]
            status = "ok" if got <= 1 else "DUPLICATE_REDEEM_SUCCEEDED"
            return self._send(200, json.dumps({"status": status, "count": got}), "application/json")

        return self._send(404, "{}", "application/json")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18080
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print(f"vuln target on http://127.0.0.1:{port}", flush=True)
    srv.serve_forever()
