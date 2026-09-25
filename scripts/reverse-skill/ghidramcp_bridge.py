#!/usr/bin/env python3
"""MCP wrapper for the GhidraMCP headless REST server.

GhidraMCP exposes ~260 analysis endpoints over plain HTTP; an MCP client cannot
register a REST service directly. This bridge starts the headless server on
demand, reads its self-published schema, and republishes every endpoint as a
first-class MCP tool with typed parameters.

Design notes:
  - Tool definitions come from the server's own /mcp/schema (about 170 KB of
    path, method, description and per-parameter metadata). Nothing about the
    tool surface is hardcoded, so a plugin upgrade adds tools with no edit here.
  - The Ghidra server starts lazily, on the first tool call rather than at
    import. A client that loads this at agent startup must not pay two minutes
    of Ghidra boot for a session that never touches Ghidra.
  - The wrapper picks its own free port and never assumes 8089: that port is
    shared with the GUI plugin, and whichever process boots first wins.

Environment:
  GHIDRA_HOME            Ghidra install root (required for autostart)
  GHIDRA_MCP_PORT        preferred port, a free one is used if busy (default 8089)
  GHIDRA_MCP_AUTOSTART   "0" disables launching the server (default enabled)
  GHIDRA_MCP_PROJECT     project directory (default: <temp>/ghidramcp-project)
  GHIDRA_MCP_BOOT_TIMEOUT  seconds to wait for boot (default 300)
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    sys.stderr.write("mcp SDK missing: pip install mcp\n")
    raise

DEFAULT_PORT = int(os.environ.get("GHIDRA_MCP_PORT", "8089"))
BOOT_TIMEOUT = int(os.environ.get("GHIDRA_MCP_BOOT_TIMEOUT", "300"))
AUTOSTART = os.environ.get("GHIDRA_MCP_AUTOSTART", "1") != "0"

_state: dict[str, Any] = {"proc": None, "port": None, "project": None, "schema": None}
_warned: set[str] = set()


def _warn_once(key: str, msg: str) -> None:
    """Stderr at most once per key. Never stdout — that is MCP's channel."""
    if key not in _warned:
        _warned.add(key)
        sys.stderr.write(msg.rstrip() + "\n")
        sys.stderr.flush()


# --------------------------------------------------------------------------
# Server lifecycle
# --------------------------------------------------------------------------

def _port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _free_port(preferred: int) -> int:
    if not _port_open(preferred):
        return preferred
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _ghidra_home() -> Path:
    home = os.environ.get("GHIDRA_HOME") or os.environ.get("GHIDRA_INSTALL_DIR")
    if not home:
        raise RuntimeError(
            "GHIDRA_HOME is not set. Point it at the Ghidra install root, e.g. "
            "/opt/ghidra_12.1.2_PUBLIC or C:\\\\Tools\\\\ghidra_12.1.2_PUBLIC"
        )
    p = Path(home)
    if not p.is_dir():
        raise RuntimeError(f"GHIDRA_HOME does not exist: {p}")
    return p


def _extension_jar(home: Path) -> Path:
    ext = home / "Ghidra" / "Extensions"
    if not ext.is_dir():
        raise RuntimeError(f"no Extensions directory under {home}")
    for d in sorted(ext.iterdir()):
        libs = d / "lib"
        if "mcp" in d.name.lower() and libs.is_dir():
            jars = sorted(libs.glob("*.jar"))
            if jars:
                return jars[0]
    raise RuntimeError(f"GhidraMCP extension not found under {ext}")


def _java() -> str:
    java = shutil.which("java")
    if not java:
        raise RuntimeError("java not on PATH; a JDK 21+ is required")
    return java


def _http(url: str, timeout: float = 30.0) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _health(port: int) -> dict[str, Any] | None:
    try:
        data = _http(f"http://127.0.0.1:{port}/health", timeout=5)
    except (urllib.error.URLError, OSError):
        return None
    return data if isinstance(data, dict) and data.get("status") == "healthy" else None


def _maybe_start(binary: str | None = None) -> int:
    """Port of a running headless server, starting one when necessary."""
    port = _state.get("port") or DEFAULT_PORT
    if _health(port):
        _state["port"] = port
        return port

    if not AUTOSTART:
        raise RuntimeError(
            f"no GhidraMCP server on {port} and GHIDRA_MCP_AUTOSTART=0. Start "
            "one, or unset that variable to let the wrapper do it."
        )

    home = _ghidra_home()
    jar = _extension_jar(home)
    port = _free_port(DEFAULT_PORT)

    # The project directory must exist. A missing one silently downgrades the
    # server to a throwaway in-memory project, losing the analysis on exit.
    project = os.environ.get("GHIDRA_MCP_PROJECT") or str(
        Path(os.environ.get("TEMP") or "/tmp") / "ghidramcp-project"
    )
    Path(project).mkdir(parents=True, exist_ok=True)

    sep = ";" if os.name == "nt" else ":"
    cp = sep.join(str(j) for j in sorted(home.rglob("*.jar")))
    cmd = [
        _java(),
        "-Djava.system.class.loader=ghidra.GhidraClassLoader",
        f"-Duser.home={Path.home()}",
        "-cp", f"{cp}{os.pathsep}{jar}",
        "ghidra.Ghidra",
        "com.xebyte.headless.GhidraMCPHeadlessServer",
        "--port", str(port),
        "--project", project,
    ]
    if binary:
        cmd += ["--file", binary]

    _warn_once("boot", f"[ghidramcp] starting headless Ghidra on port {port} "
                       f"(first call; may take a minute)")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, text=True)
    _state.update(proc=proc, port=port, project=project)

    deadline = time.time() + BOOT_TIMEOUT
    while time.time() < deadline:
        if proc.poll() is not None:
            err = (proc.stderr.read() if proc.stderr else "") or ""
            tail = "\n".join(err.strip().splitlines()[-6:])
            raise RuntimeError(
                f"Ghidra headless exited with code {proc.returncode}:\n{tail}"
            )
        if _health(port):
            _warn_once("ready", f"[ghidramcp] ready on port {port}")
            return port
        time.sleep(2)

    proc.terminate()
    raise RuntimeError(f"Ghidra headless did not start within {BOOT_TIMEOUT}s")


def _schema(port: int) -> list[dict[str, Any]]:
    """Fetch and cache the server's self-published tool schema."""
    if _state.get("schema"):
        return _state["schema"]
    try:
        data = _http(f"http://127.0.0.1:{port}/mcp/schema", timeout=30)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        _warn_once("schema", f"[ghidramcp] /mcp/schema unavailable ({e})")
        return []
    tools = data.get("tools", []) if isinstance(data, dict) else []
    if not isinstance(tools, list):
        return []
    _state["schema"] = tools
    return tools


def _call(path: str, method: str, params: dict[str, Any]) -> Any:
    """Invoke one endpoint. Query params go in the URL, body params in the body."""
    port = _maybe_start()
    base = f"http://127.0.0.1:{port}{path}"

    entry = next((t for t in (_state.get("schema") or []) if t.get("path") == path), {})
    desk = {p["name"]: p for p in entry.get("params", [])}

    query, body = {}, {}
    for k, v in params.items():
        if v is None:
            continue
        spec = desk.get(k, {})
        src = spec.get("source", "query")
        name = spec.get("param_type", k)
        if src == "query":
            query[name] = v
        elif src == "path":
            base = base.replace("{%s}" % k, urllib.parse.quote(str(v)))
        else:
            body[name] = v

    url = base + (("?" + urllib.parse.urlencode(query)) if query else "")
    try:
        if method.upper() == "POST" or body:
            data = json.dumps(body).encode() if body else None
            req = urllib.request.Request(
                url, data=data, method=method.upper() if body else "GET",
                headers={"Content-Type": "application/json"} if data else {},
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read().decode("utf-8", "replace")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        return _http(url, timeout=120)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"HTTP {e.code} from {path}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"{path} unreachable ({e.reason}); server may have died") from e


# --------------------------------------------------------------------------
# MCP surface
# --------------------------------------------------------------------------

mcp = FastMCP("ghidramcp")


@mcp.tool()
def ghidra_status() -> dict:
    """Report whether the headless Ghidra server is up and which program is loaded."""
    port = _state.get("port") or DEFAULT_PORT
    health = _health(port)
    if not health:
        return {"running": False, "port": port,
                "hint": "It starts automatically on the first analysis call."}
    return {"running": True, "port": port, **health}


@mcp.tool()
def ghidra_open(binary: str) -> dict:
    """Load a binary into the headless server, starting the server if needed.

    The first call on a cold server can take a minute while Ghidra boots and
    auto-analyses the file.
    """
    if not Path(binary).is_file():
        return {"ok": False, "error": f"no such file: {binary}"}
    try:
        port = _maybe_start(binary) if not (
            _state.get("proc") and _state["proc"].poll() is None
        ) else _state["port"]
        result = _call("/load_program", "POST", {"file": binary})
        return {"ok": True, "port": port, "result": result}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


@mcp.tool()
def ghidra_call(endpoint: str, params: dict | None = None) -> Any:
    """Call any Ghidra REST endpoint directly.

    Use when a named tool is not registered, e.g.
    endpoint='/decompile_function', params={'address': '0x140001870'}.
    """
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    _maybe_start()
    return _call(endpoint, "POST", params or {})


def _register_all() -> None:
    """Publish one MCP tool per endpoint, typed from the server's own schema."""
    try:
        port = _maybe_start()
    except Exception as e:  # noqa: BLE001
        _warn_once("offline",
                   f"[ghidramcp] server unreachable at startup ({e}); "
                   f"only ghidra_status/ghidra_open/ghidra_call are registered")
        return

    entries = _schema(port)
    if not entries:
        _warn_once("noschema",
                   "[ghidramcp] no schema available; only the generic "
                   "ghidra_call tool is registered")
        return

    import inspect

    for entry in entries:
        raw_path = entry.get("path")
        if not isinstance(raw_path, str) or not raw_path.startswith("/"):
            continue
        method = str(entry.get("method", "POST")).upper()
        desc_parts = [entry.get("description") or raw_path]

        # Python requires non-default params before defaulted ones, or the
        # signature is rejected outright. Order by requiredness, preserving
        # the server's own ordering inside each group.
        ordered: dict[str, Any] = {}
        for req_pass in (True, False):
            for p in entry.get("params", []):
                pname = p.get("name")
                if not isinstance(pname, str) or not pname.isidentifier():
                    continue
                if bool(p.get("required")) is not req_pass:
                    continue
                ptype = str(p.get("type", "string")).lower()
                src = p.get("source", "query")
                pt = p.get("param_type", pname)
                doc = (p.get("description") or "").strip()
                tag = f"[{src}:{pt}]"
                if p.get("default") not in (None, ""):
                    doc = f"{doc} (default {p.get('default')!r})"
                doc = f"{doc} {tag}".strip()

                if ptype in ("int", "integer", "long", "number"):
                    ann, default = int, None
                elif ptype in ("bool", "boolean"):
                    ann = bool
                    default = bool(p.get("default")) if p.get("default") not in (None, "") else None
                else:
                    ann, default = str, None
                if req_pass:
                    ordered[pname] = (ann, inspect.Parameter.empty)
                else:
                    ordered[pname] = (ann | None, default)  # type: ignore[operator]
                desc_parts.append(f"{pname}: {doc}")

        fields = ordered

        def make(p: str, m: str, decl: dict):
            def tool(**kwargs: Any) -> Any:
                return _call(p, m, kwargs)
            tool.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
                parameters=[
                    inspect.Parameter(k, inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                      annotation=spec[0],
                                      default=spec[1])
                    for k, spec in decl.items()
                ],
                return_annotation=Any,
            )
            tool.__name__ = "ghidra_" + p.strip("/").replace("/", "_").replace("-", "_")
            tool.__doc__ = "\n".join(desc_parts)
            return tool

        desc = "\n".join(desc_parts)
        if not fields:
            mcp.add_tool(functools_partial(make, raw_path, method, {})(),
                         name="ghidra_" + raw_path.strip("/").replace("/", "_"),
                         description=desc)
        else:
            fn = make(raw_path, method, fields)
            mcp.add_tool(fn, name=fn.__name__, description=desc)

    _warn_once("tools", f"[ghidramcp] registered {len(entries)} endpoint tool(s)")


def functools_partial(fn, *a, **kw):
    from functools import partial
    return partial(fn, *a, **kw)


if __name__ == "__main__":
    _register_all()
    mcp.run()
