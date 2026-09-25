---
name: binary-ninja-reverse
description: Reverse engineering with Binary Ninja — HLIL/MLIL/LLIL intermediate languages, cross-references, type recovery, and headless batch analysis. Use for Binja-specific decompilation, IL-level analysis, and BN API scripting.
---

# Binary Ninja Reverse Engineering

Binary Ninja's strength is its **multi-level intermediate language (IL)** view.
Where IDA gives one pseudocode view, BN exposes LLIL, MLIL and HLIL separately —
which makes it the better tool for understanding optimizer behaviour, dataflow,
and what a compiler actually did to your code.

## Capability gate — read this first

Confirm what the local install can actually do before planning work:

```bash
binaryninja.exe --version          # prints the running build, e.g. "Binary Ninja 6.0"
```

| Capability | Availability |
|---|---|
| GUI analysis, HLIL / decompiler | yes — always |
| Debugger plugins | yes — always |
| **Python API / headless `-p` batch** | **depends on the licence on this machine** |
| **MCP over loopback** | **yes — works with GUI-only installs** |

**The Python API and headless batch mode require a licence that is valid in the
running process.** Do not assume they are available, and do not report a scripted
result you did not actually obtain.

MCP access is **optional** — the GUI and the manual workflow need nothing extra.

**When the API is not available, use MCP over loopback instead.** The MCP plugin
runs *inside* the Binary Ninja GUI process, so it reaches the API from the inside
and does not need an externally licenced interpreter:

```
Binary Ninja GUI  ->  MCP plugin (in-process)  ->  MCP over HTTP on 127.0.0.1:24642
                                                       ^
                                       MCP client  <-- native MCP, no bridge
```

The endpoint speaks MCP natively — there is **no npm bridge and no second port**.
Setup: install the MCP plugin, open a binary, and confirm the endpoint responds.

```bash
# Probe before trusting it. A 405 with "Allow: POST" is the expected answer to a
# plain GET: it means the MCP endpoint is up and only accepts POST.
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:24642/mcp
```

Tool names are prefixed `bn_*` (`bn_binary_view_list`, `bn_function_decompile`,
`bn_entry_point_list`, `bn_function_complexity`, and 71 more). Typical first calls:

```text
bn_open_item_list()                     # what is open, and its path
bn_binary_view_list()                   # architecture, address range, entry point
bn_function_decompile(name="wWinMain")  # pseudocode for one function
```

Files opened by hand in the GUI need `bn_binary_view_set_active` before their
tools accept calls; files opened through `bn_open_item_open` activate themselves.

Keep the plugin out of this repository — consume it over loopback.

Probe the API before writing any script that imports it:

```bash
python -c "import binaryninja; print(binaryninja.core_version())"
# ModuleNotFoundError / RuntimeError -> the API is not usable from this interpreter
```

If that fails, take one of two paths:

- **MCP over loopback** (preferred) — scripted access from inside the GUI
  process, see above.
- **GUI-only** — do the analysis by hand in the BN window and record the result,
  or route the automated part to IDA headless (`idat64.exe -A -S script.py`).

Never fabricate scripted output.

## IL levels — what each one answers

Pick the level that matches the question. Going too high loses the detail; going
too low drowns you in noise.

| Level | Form | Use it for |
|---|---|---|
| **HLIL** | near-C pseudocode | fastest read of intent; algorithm recovery |
| **MLIL** | typed SSA-ish IR | dataflow, where a value came from, optimiser output |
| **MLIL SSA** | explicit def-use | taint-style tracing, constant propagation |
| **LLIL** | register/flag level | what the machine actually executes; CET, stack layout |
| **Disassembly** | raw mnemonics | architecture quirks, alignment, AVX/NEON specifics |

### HLIL for intent
Read HLIL first. It inlines helpers and rebuilds loops, so a crypto routine or a
length check becomes readable C-like structure.

### MLIL for provenance
When you need to know *where* a value came from:

1. Select the variable in HLIL, press the IL-level hotkey to drop to MLIL.
2. Right-click the definition -> **Show all cross-references**.
3. Walk `MLIL_VAR_SSA` / `MLIL_SET_VAR_SSA` to trace the chain.

This is the fast path for "is this size field attacker-controlled?" — follow the
SSA chain back and see whether it bottoms out in a read from a network buffer.

### LLIL for the machine truth
Use LLIL when the decompiler is lying to you (it happens with hand-written asm,
obfuscated code, and packed regions). LLIL cannot hide a stack pivot or a
manual `jmp` into a gadget.

## Cross-references

`Ctrl+Shift+X`-equivalent — **Show cross-references** on any symbol or address.
For exploit work the useful views are:

- **Code xrefs** to a dangerous call (`memcpy`, `system`, `strcpy`) — shows every
  call site and the argument setup at each one.
- **Data xrefs** to a global — reveals which code writes a config value or a
  function pointer table. Writable function-pointer tables plus an overflow
  nearby is a classic control-flow hijack.
- **String xrefs** — fastest way into error paths and feature flags.

## Type recovery

BN's type propagation is its second strength. When a struct is wrong:

1. Open the **Types** view, define or import the struct.
2. Apply it to the variable (`Y` in HLIL).
3. Wrong field offsets usually mean the struct is mis-sized — check `size_t` vs
   `int` members on 64-bit, and check whether the compiler inserted padding.

Importing real headers beats guessing:

```
File -> Load Header File ->  <windows.h | your SDK header>
```

Then re-run analysis (**Actions -> Reanalyze**, or `Ctrl+P` -> reanalyze) so the
type library is applied to call sites.

## Common workflows

**"What does this function do?"**
1. HLIL, read the structure.
2. Rename variables as you understand them (`N`).
3. Set the function's type signature so call sites become readable.
4. Reanalyze. Callers now show typed arguments.

**"Where is this buffer written?"**
1. Find the allocation (`malloc` xrefs) or the stack slot in LLIL.
2. Data xrefs on the address -> every writer.
3. For each writer compare the copy length against the allocation size. That is
   the overflow, or the proof there isn't one.

**"Is this binary packed?"**
High entropy section, few cross-references, tiny import table, and an entry point
that does nothing but unpack = packed. Dump at the OEP and re-analyze the dump.

**"Patch it"**
BN writes patches back into the file: right-click an instruction -> **Patch**.
For a persistent change, patch bytes, then `File -> Save`. Prefer patching the
branch condition over NOP-ing a whole check — it keeps the diff readable.

## Comparisons to IDA

Use BN when: you need IL levels, SSA dataflow, or type propagation across a large
binary. Use IDA when: you need the widest decompiler coverage of exotic
architectures, mature idapython automation, or the largest plugin ecosystem.

For headless/automated reverse engineering prefer IDA (`idat64.exe -A -S script.py`).
If BN is on a paid licence, the equivalent is `binaryninja -p` with a script.

## Pitfalls

- **API may be unavailable.** Confirm with the import probe above before scripting.
  When it fails, use MCP over loopback — do not silently fabricate a scripted result.
- **Analysis cache.** Re-running analysis after a type change does not always
  refresh HLIL. Close and reopen the view.
- **`-p` still loads debugger plugins** on some builds. If startup hangs, use
  `-p` plus `--help` first to confirm the flag is honoured.
- **Do not trust the decompiler on obfuscated code.** Verify at LLIL, and verify
  again in a debugger before writing an exploit around it.
- **Probe first, always.** Reporting a scripted result you did not obtain is a
  fabricated result.
