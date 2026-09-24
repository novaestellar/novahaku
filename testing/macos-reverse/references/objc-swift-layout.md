# Objective-C and Swift Runtime Layout

## Objective-C

### Message send

`objc_msgSend(receiver, selector, ...)` is the single hot path. Look for calls to
`_objc_msgSend` to map call sites to selectors.

```asm
mov  rdi, <receiver>
lea  rsi, [rip + <selref>]   ; selector reference
call _objc_msgSend
```

### Class structure (`objc_class`, 64-bit)

| Offset | Field |
|---|---|
| 0x08 | `superclass` pointer |
| 0x10 | `cache` (buckets of method→imp) |
| 0x18 | `vtable` (buckets of selector→imp) |
| 0x20 | `data` bitfield → `class_ro_t` |

### Class realization

Methods are not in `__objc_classlist` directly. The runtime parses
`class_ro_t` from `__objc_const`, then populates the cache on first message
send. Static analysis of `methods` arrays is more reliable than tracing
`objc_msgSend` for coverage.

### Useful layout commands

```bash
otool -ov ./target | grep -A2 'class name'      # class + method names
otool -v -s __DATA __objc_classlist ./target    # class list
otool -v -s __TEXT __objc_methname ./target     # method name strings
class-dump ./target > classes.h                 # reconstruct headers
```

## Swift

### Name mangling

`_$s<module><name><typeencoding>` — demangle with:

```bash
echo '_$s6MyApp8MyClassC5hello_yyF' | swift demangle
xcrun swift-demangle '_$s6MyApp8MyClassC5hello_yyF'
```

Common prefixes:

| Prefix | Meaning |
|---|---|
| `_$s` (was `_T`) | Swift mangled symbol |
| `_$s...C` | class |
| `_$s...V` | struct |
| `_$s...O` | enum |
| `_$s...P` | protocol |
| `_$s...F` | function |

### Swift metadata

Swift classes embed a metadata record with a vtable of function pointers. In a
stripped binary the vtable slot count is still intact, so you can recover call
targets even without symbols.

`swift_demangle` in Ghidra or `xcrun swift-demangle` on exported symbol dumps
recovers most names.

### Strings

Swift string literals land in `__TEXT,__cstring` as UTF-8 and are referenced via
`__swift5_reflstr`/`__swift5_fieldmd` metadata. Grep for business-logic strings
first — they orient you faster than chasing metadata.

## XPC services

XPC is macOS IPC. Attack surface is the `xpc_connection_handler` block.

```bash
ls -la /Library/PrivilegedHelperTools/          # privileged helpers
launchctl list | grep -i <vendor>               # registered services
plutil -p /Library/LaunchDaemons/*.plist | grep -A3 MachServices
```

An XPC service missing `ShouldAcceptNewConnection` validation accepts
connections from any local process — that is the classic escalation path.

## References

- Apple: `objc4` runtime source (`objc-runtime-new.h`)
- Apple: Swift ABI stability docs (mangling grammar)
- `codesign -d --entitlements :-` to read what the process is allowed to do
