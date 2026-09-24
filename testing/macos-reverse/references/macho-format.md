# Mach-O Format Reference

## Header (mach_header_64)

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 4 | `magic` | `0xFEEDFACF` = 64-bit LE; `0xCFFAEDFE` = 64-bit BE; `0xFEEDFACE`/`0xCEFAEDFE` = 32-bit |
| 4 | 4 | `cputype` | `0x01000007` = x86_64, `0x0100000C` = arm64 |
| 8 | 4 | `cpusubtype` | arm64e = `0x80000002` |
| 12 | 4 | `filetype` | 2=MH_EXECUTE, 6=MH_DYLIB, 8=MH_BUNDLE, 11=MH_KEXT_BUNDLE |
| 16 | 4 | `ncmds` | number of load commands |
| 20 | 4 | `sizeofcmds` | total size of load command area |
| 24 | 4 | `flags` | `0x00200000` = MH_PIE |
| 28 | 4 | `reserved` | 64-bit only |

## Load commands worth reading

| Command | Why it matters |
|---|---|
| `LC_SEGMENT_64` | Defines `__TEXT`, `__DATA`, `__LINKEDIT` with vmaddr/fileoff |
| `LC_SYMTAB` | Symbol table + string table offsets |
| `LC_DYLD_INFO_ONLY` | Binding/export info in compressed trie form |
| `LC_CODE_SIGNATURE` | Offset+size of the embedded signature blob |
| `LC_MAIN` | Entry point as file offset (`entryoff`) |
| `LC_ENCRYPTION_INFO_64` | Cryptid + cryptoff — nonzero cryptid means encrypted |
| `LC_LOAD_DYLIB` | Runtime dependency; also an injection point for dylib hijack |

## Sections that matter for RE

| Section | Contents |
|---|---|
| `__TEXT,__text` | Executable code |
| `__TEXT,__cstring` | C string literals |
| `__TEXT,__const` | Read-only constants |
| `__DATA,__data` | Initialized writable data |
| `__DATA_CONST,__got` | Global offset table |
| `__DATA,__la_symbol_ptr` | Lazy symbol pointers |
| `__DATA,__objc_classlist` | ObjC class list (pointer array) |
| `__DATA,__objc_selrefs` | ObjC selector references |

## Code signature blob

At `LC_CODE_SIGNATURE.fileoff`:

- `CS_SuperBlob` magic `0xFADE0CC0`
- Followed by `CS_CodeDirectory` (`0xFADE0C02`) holding the hash of each page
- Entitlements live in a `CS_GenericBlob` with magic `0xFADE7171`

Patching code without re-signing breaks the page hash. Detection is trivial
unless the binary was ad-hoc signed (`codesign --force --sign -`).

## Ad-hoc vs Developer ID

| Signature | `codesign -dv` shows | Re-signable locally |
|---|---|---|
| Ad-hoc | `Signature=adhoc` | yes |
| Developer ID | `Authority=Developer ID Application: ...` | locally yes, distribution no |
| Apple | `Authority=Software Signing` | no |

## Universal binary container

```
FAT header: magic 0xCAFEBABE | nfat_arch | then per-arch {cputype, cpusubtype, offset, size, align}
```

Each arch entry points at a full independent Mach-O. Offsets do not transfer
between slices.

## Quick triage

```bash
file ./target                       # confirm Mach-O + arch
lipo -info ./target                 # slices in a FAT binary
otool -h ./target                   # header fields
otool -l ./target | grep -E 'segname|fileoff|vmsize'
codesign -d --entitlements :- ./target 2>/dev/null
```
