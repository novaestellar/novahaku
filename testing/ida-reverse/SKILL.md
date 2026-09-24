---
name: ida-reverse
description: Headless reverse engineering with IDA Pro — batch decompilation, IDAPython scripting, xref mapping, and automated function analysis via idat64. Use for scripted binary analysis, decompiler output at scale, and CI-style RE pipelines.
---

# IDA Pro Reverse Engineering (headless)

IDA's advantage over every other RE tool is **automation at scale**: one script,
thousands of functions, decompiler output you can grep. This skill drives
`idat64.exe` in batch mode (`-A`) with IDAPython (`-S`).

## Verified environment

This skill was validated on a real install — use these exact paths on this host:

```bash
IDA="/c/Program Files/IDA Professional 9.0/idat64.exe"   # headless, 64-bit
IDAGUI="/c/Program Files/IDA Professional 9.0/ida64.exe" # GUI, same DB
IDAPYSWITCH="/c/Program Files/IDA Professional 9.0/idapyswitch.exe"
```

Confirm the install before relying on it:

```bash
"$IDA" -h 2>&1 | head -3
"$IDAPYSWITCH" --dry-run 2>&1 | tail -3
```

Expected: IDA 9.0, and IDAPython bound to a Python 3.13 DLL. If
`idapyswitch --dry-run` reports no Python, run `idapyswitch -a` to auto-apply.

**Verified working output** (357 functions from `notepad.exe`, real symbol names —
if you get an empty log, IDAPython is not bound):

```
IDAPY_OK version=9.0
FUNCS=357
  memcpy_s @ 0x1400016c4
  TraceLoggingRegister_EventRegister_EventSetInformation @ 0x140001380
```

## The batch driver

```bash
# -A  autonomous: no dialogs, no prompts (required for scripting)
# -S"script.py"  run this IDAPython script on load
# -c  force a new database even if one exists
# result: <target>.i64  plus whatever your script writes
"$IDA" -A -S"probe.py" target.exe
```

### Rule 1 — IDA's stdout is unreliable, write to a file

Console output from `idat64` is frequently swallowed, especially when launched
from a non-interactive shell. **Always write findings to a log file from inside
the script** and read the file afterwards. A script that only `print()`s will look
like it silently failed.

```python
LOG = r"C:\path\to\out.log"
with open(LOG, "w", encoding="utf-8") as f:
    f.write("IDAPY_OK version=%s\n" % idaapi.get_kernel_version())
```

### Rule 2 — always `qexit(0)`

Without it the process can hang waiting on the database, and your batch job
never returns.

```python
idc.qexit(0)
```

### Rule 3 — `-A -c` for a clean run

`-A` suppresses prompts. `-c` discards any stale `.i64`, which matters because a
cached database silently skips the analysis your script assumes has run.

## Canonical probe script

```python
import idaapi, idautils, idc

LOG = r"C:\path\to\out.log"
with open(LOG, "w", encoding="utf-8") as f:
    f.write("IDAPY_OK version=%s\n" % idaapi.get_kernel_version())
    funcs = list(idautils.Functions())
    f.write("FUNCS=%d\n" % len(funcs))
    for ea in funcs[:8]:
        f.write("  %s @ %#x\n" % (idc.get_func_name(ea), ea))

    # imports the binary actually resolves
    f.write("IMPORTS=%d\n" % len(list(idautils.Entries())))

idc.qexit(0)
```

## Decompiling at scale

```python
import idaapi, idautils, idc
from ida_hexrays import decompile, init_hexrays_plugin

OUT = r"C:\path\to\pseudocode.txt"
init_hexrays_plugin()

with open(OUT, "w", encoding="utf-8") as f:
    for ea in idautils.Functions():
        try:
            cf = decompile(ea)
            f.write("\n/* ==== %s @ %#x ==== */\n" % (idc.get_func_name(ea), ea))
            f.write(str(cf) + "\n")
        except Exception as exc:
            f.write("\n/* %s @ %#x: decompile failed: %s */\n"
                    % (idc.get_func_name(ea), ea, exc))

idc.qexit(0)
```

Then grep the output for your sink:

```bash
grep -n -B4 -A2 'strcpy\|system\|memcpy' pseudocode.txt
```

### Decompiler availability

`init_hexrays_plugin()` returns falsy when the Hex-Rays decompiler is not
licensed or not loaded. Check it — do not assume `decompile()` works:

```python
if not init_hexrays_plugin():
    f.write("NO DECOMPILER — falling back to disassembly only\n")
```

Fall back to `idc.generate_disasm_line(ea, 0)` when it is unavailable.

## Cross-reference mapping

```python
import idautils, idc

def callers(name):
    out = []
    for ea in idautils.Functions():
        if idc.get_func_name(ea) != name:
            continue
        for xref in idautils.CodeRefsTo(ea, 0):
            out.append((idc.get_func_name(xref), xref))
    return out

with open(LOG, "w", encoding="utf-8") as f:
    for ea in idautils.Functions():
        nm = idc.get_func_name(ea)
        if nm in ("memcpy", "memcpy_s", "strcpy", "system"):
            for caller, addr in callers(nm):
                f.write("%s -> %s @ %#x\n" % (caller, nm, addr))
```

For data xrefs (function pointer tables, config globals) use `idautils.DataRefsTo`.
A **writable function-pointer table with a nearby overflow** is the classic
control-flow hijack — find those first.

## Common workflows

**Security triage of an unknown binary**
1. `idautils.Entries()` — import table tells you the capability set.
2. Strings pass: `idautils.Strings()` filtered for URLs, paths, format strings.
3. Xrefs to dangerous sinks (`strcpy`, `system`, `WinExec`, `sprintf`).
4. Decompile only the reaching functions, not the whole binary.

**"Is this mitigated?"**
Check the PE/ELF hardening before anything else — NX/DEP, ASLR, stack canary,
SafeSEH/CFG. `idc.get_inf_attr(INF_.LOADERFLAGS)` and manual segment checks cover
most of it; a missing canary changes the whole exploitation plan.

**Patching**
```
PatchByte / PatchDword  then  idaapi.save_database(path)
```
Patch the **branch condition**, not the whole check — smaller diff, easier to
review, less likely to break the surrounding code.

**Comparing two builds**
Load both, match by symbol and by structural hashing of the decompiled body.
Function-level diff beats byte-level diff for anything compiler-optimised.

## Pitfalls

- **Silent stdout.** Verified here: console prints vanish; the log file is the
  only reliable channel. This is the single most common cause of a "failed" IDA
  script that actually worked.
- **Stale `.i64`.** A database from a prior run skips analysis. Use `-c`.
- **No `qexit`.** The batch never returns; CI jobs hang until timeout.
- **Decompiler not licensed.** `init_hexrays_plugin()` is falsy — guard for it.
- **356 functions is not "the whole binary."** FLIRT/library signatures collapse
  CRT and runtime code; the interesting code is what is *left* after library
  recognition, so check which signatures loaded.
- **Very long function names are normal** in templated C++ (`??$Write@U?...`).
  Truncate for reporting, never for matching.
- **MSYS path conversion.** `idat64.exe` is a native Windows binary: pass it
  `C:/...` paths, not `/c/...`. Pass MSYS paths and it fails to find the target.
- **Antivirus.** IDA creates a large `.i64` next to the target; some AV products
  flag this pattern. Keep test targets outside protected directories.
