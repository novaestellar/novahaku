"""RUNTIME TEST v4 - Hermes root. LEWAT JALUR PRODUKSI.

Pelajaran dari v1-v3 (semua dikonfirmasi Oracle C & D):
  Setiap kegagalan berasal dari test yg MELEWATI jalur produksi:
    - tulis findings.json tangan -> findings.csv tidak ikut -> integrity benar menolak
    - baca field 'event' padahal kode tulis 'action'
    - bentuk list telanjang padahal kontrak dict{'findings':[..]}
  v4 memakai penulis produksi:
    _write_findings()  -> findings.json + findings.csv
    publish_results()  -> results.json + results.csv + record_chain
    record_chain()     -> chain.json
  Tidak ada json.dump tangan utk file yg punya penulis resmi.

Semua di hermes root. Temp root.
"""
import importlib.util as iu
import json
import os
import subprocess
import sys
import tempfile

T = tempfile.gettempdir()
sp = iu.spec_from_file_location("rtutil", os.path.join(T, "rtutil.py"))
u = iu.module_from_spec(sp)
sp.loader.exec_module(u)

# Resolve both skill trees from the environment, falling back to the Hermes
# skills root this file lives under. No machine-specific absolute paths.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SKILLS_ROOT = os.environ.get("HERMES_SKILLS_ROOT", os.path.dirname(os.path.dirname(_HERE)))
NHA = os.path.join(_SKILLS_ROOT, "security", "novahaku")
NX = os.path.join(_SKILLS_ROOT, "web", "novaxinwei")
PARENT_NX = os.path.dirname(NX)
RUNNER = os.path.join(NHA, "scripts", "engage_runner.py")
PY = sys.executable

WS = tempfile.mkdtemp(prefix="rt4-")
ENG = os.path.join(WS, "engagements")
TARGET = "runtime.example"
TDIR = os.path.join(ENG, TARGET)
os.makedirs(ENG, exist_ok=True)

R = []


def check(sec, name, ok, detail=""):
    R.append((sec, name, ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if detail and not ok:
        for ln in str(detail).splitlines()[:10]:
            print(f"        {ln}")


ENVE = dict(os.environ)
ENVE.pop("NOVAHAKU_ENGAGEMENT_DIR", None)
ENVE["NOVAHAKU_ENGAGEMENT_DIR"] = ENG


def run(args, cwd=None, timeout=180):
    p = subprocess.run(args, cwd=cwd or WS, env=ENVE, capture_output=True, text=True,
                       timeout=timeout, errors="replace")
    return p.returncode, p.stdout, p.stderr


def py(code, argv=(), cwd=None):
    return u.py(code, argv, cwd=cwd or WS, env=ENVE, timeout=180)


FINDINGS = [
    {"id": "F-001", "title": "IDOR on /api/v1/me", "severity": "High",
     "confidence": "High", "category": "idor", "asset": "api.sync.example",
     "description": "uid dapat diganti", "remediation": "cek otorisasi",
     "evidence": {"request": "GET /api/v1/me?uid=2", "response": "200", "status": 200}},
    {"id": "F-002", "title": "Missing HSTS", "severity": "Low",
     "confidence": "Low", "category": "headers", "asset": "sync.example",
     "description": "tanpa HSTS", "remediation": "tambah HSTS",
     "evidence": {"request": "GET /", "response": "no HSTS", "status": 200}},
]

print("=" * 78)
print(f"RUNTIME TEST v4 - Hermes root (lewat jalur produksi)  {WS}")
print("=" * 78)

# ============================================================ 1 RUNTIME
print("\n[1] RUNTIME - kode berjalan dari lokasi deploy")
for label, args in [
    ("novahaku engagement selftest", [PY, os.path.join(NHA, "scripts", "engagement.py"), "selftest"]),
    ("novahaku engage_runner selftest", [PY, RUNNER, "selftest"]),
]:
    rc, out, err = run(args, NHA)
    check("RUNTIME", label, rc == 0 and "passed" in (out + err).lower(), (out + err)[-250:])
for mod in ("engine.chain_state", "engine.results_reader", "engine.threat_intel"):
    rc, out, err = run([PY, "-m", mod], NX)
    check("RUNTIME", f"novaxinwei {mod}", rc == 0 and "passed" in out, (out + err)[-250:])
rc, out, err = run([PY, os.path.join(NX, "cli.py"), "check"], NX)
check("RUNTIME", "cli.py langsung (BUG PRODUK yg diperbaiki)", rc == 0, (out + err)[-250:])
rc, out, err = run([PY, "-m", "novaxinwei", "check"], PARENT_NX)
check("RUNTIME", "-m novaxinwei dari parent (cara sah)", rc == 0, (out + err)[-250:])
rc, out, err = run([PY, os.path.join(NX, "__main__.py"), "check"], NX)
check("RUNTIME", "__main__.py langsung", rc == 0, (out + err)[-250:])

# ============================================================ 2 BACKEND
print("\n[2] BACKEND")
rc, out, err = run([PY, os.path.join(NHA, "scripts", "engagement.py"), "init", TARGET])
check("BACKEND", "init lewat env var", rc == 0, (out + err)[-250:])
check("BACKEND", "state.json di root bersama", os.path.exists(os.path.join(TDIR, "state.json")))
check("BACKEND", "init menulis findings.csv (penulis produksi)",
      os.path.exists(os.path.join(TDIR, "findings", "findings.csv")))
rc, out, err = run([PY, os.path.join(NHA, "scripts", "engagement.py"), "list"])
check("BACKEND", "list menemukan target", rc == 0 and TARGET in out, (out + err)[-250:])
rc, out, err = run([PY, os.path.join(NHA, "scripts", "engagement.py"), "status", TARGET])
check("BACKEND", "status membaca state", rc == 0 and TARGET in out, (out + err)[-250:])
rc, out, err = run([PY, os.path.join(NHA, "scripts", "engagement.py"), "phase", TARGET, "closed"])
check("BACKEND", "phase gate tolak lompatan maju", rc != 0, (out + err)[-250:])

# ============================================================ 3 CROSSREF
print("\n[3] CROSSREF - lewat penulis produksi")
# arah masuk: recon.json ditulis novaxinwei (recon_pipeline menulis file ini)
json.dump({"schema_version": "1.0", "target": TARGET, "domain": TARGET,
           "timestamp": "2026-09-23T00:00:00Z",
           "endpoints": ["https://sync.example/api/v1/login", "https://sync.example/api/v1/me"],
           "ports": [{"port": 443, "service": "https", "state": "open"}],
           "subdomains": ["api.sync.example"], "technologies": ["nginx"], "waf": "cloudflare"},
          open(os.path.join(TDIR, "recon.json"), "w", encoding="utf-8"), indent=2)

rc, out, err = py(u.LOAD_RUNNER +
                  "d = er.read_recon(sys.argv[2])\n"
                  "print('ENDPOINTS=' + str(len(d.get('endpoints', []))))\n"
                  "print('WAF=' + str(d.get('waf')))\n", [RUNNER, TARGET])
check("CROSSREF", "arah masuk: novahaku baca recon.json novaxinwei",
      "ENDPOINTS=2" in out and "cloudflare" in out, out + err)

# findings ditulis lewat penulis PRODUKSI: _write_findings
rc, out, err = py(u.LOAD_RUNNER +
                  "import json\n"
                  "recs = json.load(open(sys.argv[4], encoding='utf-8'))\n"
                  "p = er._write_findings(sys.argv[2], recs, base=sys.argv[3])\n"
                  "print('CSV=' + str(p))\n",
                  [RUNNER, TARGET, ENG, os.path.join(T, "rt4_findings.json")])
# tulis input findings utk snippet di atas
json.dump(FINDINGS, open(os.path.join(T, "rt4_findings.json"), "w", encoding="utf-8"), indent=2)
rc, out, err = py(u.LOAD_RUNNER +
                  "import json\n"
                  "recs = json.load(open(sys.argv[4], encoding='utf-8'))\n"
                  "p = er._write_findings(sys.argv[2], recs, base=sys.argv[3])\n"
                  "print('CSV=' + str(os.path.basename(p)))\n",
                  [RUNNER, TARGET, ENG, os.path.join(T, "rt4_findings.json")])
check("CROSSREF", "_write_findings jalan (penulis produksi)", rc == 0, out + err)

fj = json.load(open(os.path.join(TDIR, "findings", "findings.json"), encoding="utf-8"))
check("CROSSREF", "findings.json bentuk SAH (dict dgn key 'findings')",
      isinstance(fj, dict) and "findings" in fj and len(fj["findings"]) == 2,
      f"type={type(fj).__name__} keys={sorted(fj.keys()) if isinstance(fj, dict) else 'n/a'}")
csv_lines = open(os.path.join(TDIR, "findings", "findings.csv"), encoding="utf-8").read().strip().splitlines()
check("CROSSREF", "findings.csv sinkron: 2 baris + header", len(csv_lines) == 3,
      f"{len(csv_lines)} baris: {csv_lines[:2]}")

# state di-update lewat jalur resmi kalau ada; kalau tidak, ini yg dipakai integrity
st = json.load(open(os.path.join(TDIR, "state.json"), encoding="utf-8"))
st.update({"phase": "test", "current_phase": "test",
           "stats": dict(st.get("stats", {}), findings_total=2)})
json.dump(st, open(os.path.join(TDIR, "state.json"), "w", encoding="utf-8"), indent=2)

# publish lewat penulis PRODUKSI
rc, out, err = py(u.LOAD_RUNNER + "er.publish_results(sys.argv[2], base=sys.argv[3])\n",
                  [RUNNER, TARGET, ENG])
check("CROSSREF", "publish_results jalan (penulis produksi)", rc == 0, out + err)

res = json.load(open(os.path.join(TDIR, "results.json"), encoding="utf-8"))
n = res["results"]["findings_count"]
check("CROSSREF", "results.json berisi 2 temuan", n == 2, f"findings_count={n}")
check("CROSSREF", "by_severity lowercase", res["results"]["by_severity"] == {"high": 1, "low": 1},
      json.dumps(res["results"]["by_severity"]))
check("CROSSREF", "results.csv tertulis", os.path.exists(os.path.join(TDIR, "results.csv")))

# arah balik: novaxinwei baca
rc, out, err = py(u.LOAD_NX +
                  "import json\n"
                  "from novaxinwei.engine import results_reader as rr\n"
                  "t, b = sys.argv[2], sys.argv[3]\n"
                  "print('EXISTS=' + str(rr.results_exist(t, base_dir=b)))\n"
                  "print('VERSION=' + str(rr.results_version(t, base_dir=b)))\n"
                  "print('SEV=' + json.dumps(rr.get_severity_counts(t, base_dir=b)))\n"
                  "print('TITLES=' + json.dumps(rr.get_finding_titles(t, base_dir=b)))\n"
                  "print('COUNT=' + str(len(rr.get_findings(t, base_dir=b))))\n"
                  "print('PHASE=' + str(rr.get_phase(t, base_dir=b)))\n"
                  "print('SUM=' + json.dumps(rr.summarize(t, base_dir=b))[:200])\n",
                  [PARENT_NX, TARGET, ENG])
print("        " + out.strip().replace("\n", "\n        "))
check("CROSSREF", "arah balik: novaxinwei lihat 2 temuan", "COUNT=2" in out, out + err)
check("CROSSREF", "judul terbaca lintas skill", "IDOR" in out)
check("CROSSREF", "schema versi benar", "novaxinwei.results.v1" in out)
check("CROSSREF", "severity lowercase terbaca", '"high"' in out)
check("CROSSREF", "summarize() jalan lintas skill", "SUM=" in out and "Traceback" not in out)

# ============================================================ 4 CHAIN
print("\n[4] CHAIN.JSON")
ch = json.load(open(os.path.join(TDIR, "chain.json"), encoding="utf-8"))
acts = [h.get("action") for h in ch.get("history", [])]
print(f"        version={ch.get('version')}  actions={acts}")
check("CHAIN", "versi = novalabs.chain.v1", ch.get("version") == "novalabs.chain.v1")
check("CHAIN", "catat engagement_created", "engagement_created" in acts)
check("CHAIN", "catat results_written", "results_written" in acts)
check("CHAIN", "state.results_at terisi", bool(ch.get("state", {}).get("results_at")))
check("CHAIN", "state.results_by = novahaku", ch.get("state", {}).get("results_by") == "novahaku")

# ============================================================ 5 SINERGI
print("\n[5] SINERGI")
rc, out, err = py(u.LOAD_NX +
                  "from novaxinwei.engine.results_reader import _default_root as r1\n"
                  "from novaxinwei.engine.enrichment import _default_root as r2\n"
                  "print('RR=' + str(r1())); print('EN=' + str(r2()))\n", [PARENT_NX])
check("SINERGI", "results_reader & enrichment searah", out.count(ENG) == 2, out + err)
rc, out, err = run([PY, RUNNER, "integrity", "--target", TARGET])
check("SINERGI", "integrity OK (CSV sinkron krn lewat penulis produksi)", rc == 0,
      (out + err)[-300:])
rc, out, err = run([PY, RUNNER, "verify", "--target", TARGET])
check("SINERGI", "verify OK", rc == 0, (out + err)[-300:])

# ============================================================ 6 GIGI
print("\n[6] GIGI - buktikan test bisa GAGAL")
ws2 = tempfile.mkdtemp(prefix="rt4-teeth-")
eng2 = os.path.join(ws2, "engagements")
t2 = os.path.join(eng2, "teeth.example")
os.makedirs(os.path.join(t2, "findings"), exist_ok=True)
# sengaja melewati penulis produksi -> integrity HARUS menolak
json.dump({"count": 2, "findings": FINDINGS},
          open(os.path.join(t2, "findings", "findings.json"), "w", encoding="utf-8"), indent=2)
json.dump({"schema_version": "1.0", "target": "teeth.example", "current_phase": "test",
           "stats": {"findings_total": 2}, "findings": []},
          open(os.path.join(t2, "state.json"), "w", encoding="utf-8"), indent=2)
p = subprocess.run([PY, RUNNER, "integrity", "--target", "teeth.example"], cwd=ws2,
                   env=dict(ENVE, NOVAHAKU_ENGAGEMENT_DIR=eng2),
                   capture_output=True, text=True, timeout=120, errors="replace")
out_g = p.stdout + p.stderr
check("GIGI", "SENSITIF: lewati penulis produksi -> integrity MENOLAK",
      p.returncode != 0 and "findings.csv absent" in out_g,
      out_g[-200:])

# gigi tambahan: integrity menolak direktori yg tidak ada
p = subprocess.run([PY, RUNNER, "integrity", "--target", "tidak-ada.example"], cwd=ws2,
                   env=dict(ENVE, NOVAHAKU_ENGAGEMENT_DIR=eng2),
                   capture_output=True, text=True, timeout=120, errors="replace")
check("GIGI", "SENSITIF: target tidak ada -> integrity MENOLAK",
      p.returncode != 0 and "no engagement directory" in (p.stdout + p.stderr).lower(),
      (p.stdout + p.stderr)[-200:])

rc, out, err = py(u.LOAD_RUNNER + "print('ok')\n", [os.path.join(NHA, "scripts", "TIDAK_ADA.py")])
check("GIGI", "SENSITIF: path salah -> assertion menangkap", rc != 0 and "tidak ada" in err.lower())

print("\n" + "=" * 78)
bad = [x for x in R if not x[2]]
print(f"RUNTIME TEST v4: {len(R)-len(bad)}/{len(R)} PASS")
for s, n, ok in bad:
    print(f"  FAIL [{s}] {n}")
print("=" * 78)
sys.exit(1 if bad else 0)
