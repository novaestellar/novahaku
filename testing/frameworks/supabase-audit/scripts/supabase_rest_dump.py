#!/usr/bin/env python3
"""Read-only Supabase REST probe/dump CLI for black-box audits.

GET-only by design: never mutates target data. Uses the public anon key
(extracted from the client JS bundle — see pos-blackbox-audit.md Phase 0).

Config via env or sidecar files (keep keys OUT of chat context — harness
redaction can corrupt them):
  SUPABASE_URL   or ./sb_url.txt
  SUPABASE_KEY   or ./anon_key.txt
Tables list: ./tables.txt (one per line, from `.from("...")` bundle grep)
            or --tables t1,t2,...

Usage:
  supabase_rest_dump.py                 # help + dump all tables (default)
  supabase_rest_dump.py list            # all tables + row counts
  supabase_rest_dump.py dump            # list + rows for every table with data
  supabase_rest_dump.py dump --limit 50
  supabase_rest_dump.py read orders --limit 5
  supabase_rest_dump.py read orders --where "status=eq.completed" --cols order_number,grand_total
  supabase_rest_dump.py count orders
  supabase_rest_dump.py search apek     # ilike across common text columns

Notes:
- Supabase REST answers filtered reads with HTTP 206 (not 200) — accept both.
- Row counts come from the Content-Range header (`*/N`), not from the body.
- Probe writes (INSERT probe, tamper PoC) are intentionally NOT included here;
  follow Phase 3 of pos-blackbox-audit.md for the sandbox-org method.
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))

SB_URL = os.environ.get("SUPABASE_URL") or (
    open(os.path.join(BASE, "sb_url.txt")).read().strip()
    if os.path.exists(os.path.join(BASE, "sb_url.txt")) else None)

ANON_KEY = os.environ.get("SUPABASE_KEY") or (
    open(os.path.join(BASE, "anon_key.txt")).read().strip()
    if os.path.exists(os.path.join(BASE, "anon_key.txt")) else None)

TABLES_FILE = os.path.join(BASE, "tables.txt")
DEFAULT_TABLES = [
    "orders", "outlets", "menu_items", "profiles", "customers", "payments",
    "discounts", "promo_codes", "dining_tables", "menu_categories",
    "modifiers", "modifier_groups", "organizations", "suppliers",
]

if not SB_URL:
    sys.exit("ERROR: set SUPABASE_URL or write sb_url.txt next to this script")
if not ANON_KEY:
    sys.exit("ERROR: set SUPABASE_KEY or write anon_key.txt next to this script")
SB_URL = SB_URL.rstrip("/")

HEADERS = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "User-Agent": "Mozilla/5.0 (audit-probe; read-only)",
}


def load_tables() -> list[str]:
    if os.path.exists(TABLES_FILE):
        return [t.strip() for t in open(TABLES_FILE) if t.strip()]
    return DEFAULT_TABLES


def api_get(path: str) -> tuple[int, str]:
    req = urllib.request.Request(SB_URL + path, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def count_rows(table: str) -> int | None:
    """Row count via Content-Range header. Accepts 200 AND 206."""
    req = urllib.request.Request(
        SB_URL + f"/rest/v1/{table}?select=id&limit=0",
        headers={**HEADERS, "Prefer": "count=exact"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            cr = r.headers.get("Content-Range", "")
    except urllib.error.HTTPError:
        return None
    if "/" in cr and cr.split("/")[1].isdigit():
        return int(cr.split("/")[1])
    return 0


def cmd_list(_):
    print(f"{'TABEL':<30} {'ROWS':>6}")
    print("-" * 38)
    for t in load_tables():
        try:
            n = count_rows(t)
            print(f"{t:<30} {n if n is not None else 'ERR':>6}")
        except Exception:
            print(f"{t:<30} {'ERR':>6}")


def cmd_read(a):
    params = {"select": a.cols or "*", "limit": str(a.limit)}
    path = f"/rest/v1/{a.table}?{urllib.parse.urlencode(params)}"
    if a.where:
        path += f"&{a.where}"
    code, body = api_get(path)
    if code not in (200, 206):
        print(f"HTTP {code}: {body[:300]}")
        sys.exit(1)
    rows = json.loads(body)
    print(f"-- {a.table}: {len(rows)} row --")
    print(json.dumps(rows, indent=2, ensure_ascii=False))


def cmd_count(a):
    n = count_rows(a.table)
    print(f"{a.table}: {n} row" if n is not None else f"{a.table}: ERROR/blocked by RLS")


def cmd_dump(a):
    cmd_list(a)
    print(f"\n=== ISI TABEL (max {a.limit} row per tabel) ===")
    shown = 0
    for t in load_tables():
        n = count_rows(t)
        if not n:
            continue
        code, body = api_get(f"/rest/v1/{t}?select=*&limit={a.limit}")
        if code not in (200, 206):
            print(f"\n## {t} ({n} row) -> HTTP {code}, skipped")
            continue
        try:
            rows = json.loads(body)
        except json.JSONDecodeError:
            continue
        shown += 1
        print(f"\n## {t} ({n} row, showing {len(rows)}) ##")
        for r in rows:
            compact = {k: v for k, v in r.items() if v not in (None, "", {}, [])}
            line = json.dumps(compact, ensure_ascii=False, default=str)
            print("  ", line if len(line) <= 400 else line[:400] + " ...")
    if not shown:
        print("(no readable tables with data)")


def cmd_search(a):
    kw = a.keyword
    hits = 0
    for t in load_tables():
        filt = f"or=(name.ilike.*{kw}*,address.ilike.*{kw}*,phone.ilike.*{kw}*,customer_name.ilike.*{kw}*)"
        code, body = api_get(
            f"/rest/v1/{t}?select=*&{urllib.parse.quote(filt)}&limit=20")
        if code not in (200, 206):
            continue
        try:
            rows = json.loads(body)
        except json.JSONDecodeError:
            continue
        if rows:
            hits += len(rows)
            print(f"\n== {t}: {len(rows)} hit ==")
            for r in rows:
                print(" ", json.dumps(r, ensure_ascii=False)[:300])
    if not hits:
        print("No results.")


def main():
    p = argparse.ArgumentParser(description="Supabase REST read-only probe")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("list", help="all tables + row counts").set_defaults(fn=cmd_list)
    r = sub.add_parser("read", help="read rows from one table")
    r.add_argument("table")
    r.add_argument("--limit", type=int, default=10)
    r.add_argument("--cols", help="comma-separated columns")
    r.add_argument("--where", help="PostgREST filter, e.g. status=eq.completed")
    r.set_defaults(fn=cmd_read)
    c = sub.add_parser("count", help="row count for one table")
    c.add_argument("table")
    c.set_defaults(fn=cmd_count)
    d = sub.add_parser("dump", help="list + rows for every table with data")
    d.add_argument("--limit", type=int, default=10)
    d.add_argument("--tables", help="comma-separated table list override")
    d.set_defaults(fn=cmd_dump)
    s = sub.add_parser("search", help="ilike search across common text columns")
    s.add_argument("keyword")
    s.set_defaults(fn=cmd_search)
    a = p.parse_args()
    if not getattr(a, "cmd", None):
        p.print_help()
        print("\n=== DEFAULT: DUMP ALL DATA ===")
        a.limit = 10
        cmd_dump(a)
        return
    a.fn(a)


if __name__ == "__main__":
    main()
