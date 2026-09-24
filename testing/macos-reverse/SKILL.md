---
name: macos-reverse
description: "Use for authorized macOS reverse engineering: Mach-O binaries, code signing, Objective-C/Swift, XPC services, and notarization analysis."
---

# macOS Reverse Engineering

## ACTION REQUIRED

1. Identify the binary form: Mach-O vs FAT/universal, 32/64-bit.
2. Confirm which architecture slice you are analysing before any offset work.
3. Read `references/macho-format.md` for header/load-command layout.

## When to use

- Mach-O binary analysis (`.dylib`, `.app` bundles, kexts)
- Code signature / entitlement inspection
- Objective-C or Swift symbol recovery
- XPC service surface mapping
- Notarization and hardened-runtime checks

## Core tooling

| Task | Tool |
|---|---|
| File type / arch | `file`, `lipo -info`, `otool -h` |
| Load commands | `otool -l`, `otool -L` |
| Symbols | `nm -a`, `dyld_info -exports` |
| ObjC headers | `class-dump`, `otool -ov` |
| Signature | `codesign -dv --verbose=4`, `codesign -d --entitlements :-` |
| Disassembly | Ghidra, Hopper, `objdump -d --macho` |
| Dynamic | `lldb`, `dtrace`, Frida |

## Workflow

```bash
# 1. Classify
file ./target && lipo -info ./target

# 2. Load commands + linked libraries
otool -l ./target | grep -A4 LC_CODE_SIGNATURE
otool -L ./target

# 3. Entitlements (often the real attack surface)
codesign -d --entitlements :- ./target 2>/dev/null

# 4. Signature validity
codesign -dv --verbose=4 ./target

# 5. Symbols and ObjC classes
nm -a ./target | head -50
otool -ov ./target | grep 'class name'
```

## Hardened runtime and notarization

Check for `runtime` flag in `codesign -dv` output. Hardened runtime blocks
`DYLD_INSERT_LIBRARIES`, so injecting without re-signing fails. Re-sign locally
only on binaries you are authorized to modify:

```bash
codesign --force --sign - --entitlements ent.plist ./target
```

## FAT/universal binaries

A universal binary holds multiple Mach-O slices. Offsets from one slice are
invalid in another. Always `lipo -thin <arch>` into a working copy first.

## References

- `references/macho-format.md` — header, load commands, segment/section layout
- `references/objc-swift-layout.md` — ObjC runtime structures, Swift mangling

## Keywords
macos, mach-o, macho, codesign, objective-c, objc, swift reverse, xpc,
dylib, dyld, entitlements, notarization, hardened runtime, 苹果逆向, mac 逆向
