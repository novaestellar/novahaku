---
name: novahaku-pwn-chain
description: "Binary Exploitation — from vulnerability to working exploit. Stack overflow, heap, kernel pwn."
version: 1.0.0
license: MIT
platforms: [linux, windows]
metadata:
  hermes:
    tags: [pwn, exploit-development, binary-exploitation, ctf, kernel, heap]
---

# Binary Exploitation — From Vulnerability to Working Exploit

## When to Use
1. **Got binary + known vuln** — static/audit/fuzz found overflow/UAF/double-free, need to write exploit
2. **CTF works locally, fails remotely** — environment differences broke the script
3. **Real target binary exploit** — SRC/red team, identified memory corruption, need RCE
4. **Linux kernel driver ioctl bug** — user-mode trigger, goal = root

**Prerequisite**: You already know "where it crashes." This skill does NOT discover vulns (that's fuzzing/audit). It writes exploits from known vuln points.

### Division of Labor
| Scenario | Use |
|----------|-----|
| Custom VM / anti-debug / obfuscation | `windows-re/windows-re.md` |
| Zero-day static analysis | `windows-re/` or Ghidra/IDA |
| **Known vuln → write exploit → remote** | **This file** |
| Post-exploitation chain | `attack/attack-flow/` |

## Core Workflow

```
Step 1: Identify Vuln Type + Protections
   ├─ checksec ./vuln (NX / Canary / PIE / RELRO / Fortify)
   ├─ file ./vuln + readelf -d ./vuln
   ├─ Classification: stack overflow / format string / heap (UAF/DF/OF) / integer / race / kernel
   └─ → Decide which technique to use

Step 2: Choose Exploit Strategy
   ├─ NX off + no ASLR → direct shellcode
   ├─ NX on + libc given → ret2libc / one_gadget
   ├─ NX on + no libc → leak then libc-database reverse lookup
   ├─ Heap → match glibc version (tcache/fastbin/unsorted/large)
   └─ Kernel → commit_creds / modprobe_path / core_pattern

Step 3: Prepare libc + gadgets
   ├─ libc-database: ./find puts 0x6f0
   ├─ ROPgadget --binary ./libc.so.6 --only "pop|ret"
   ├─ one_gadget ./libc.so.6
   └─ Calculate base: leak_addr - libc.sym['puts']

Step 4: Write pwntools template (local process)
   ├─ context.binary = ELF('./vuln')
   ├─ p = process('./vuln') / p = gdb.debug('./vuln','b *main+xx')
   ├─ payload = cyclic(N) + p64(ret) + ...
   └─ p.interactive()

Step 5: Local success
   ├─ Attach + inspect registers + adjust offsets
   ├─ Use pwndbg/GEF vmmap / heap / bins / telescope
   └─ After local success, switch to remote()

Step 6: Remote stabilization
   ├─ libc offset: use leak + libc-database, don't guess
   ├─ Stack alignment: 16-byte misalignment → movaps crash → add ret gadget
   ├─ Remote latency: recvuntil with exact anchors, no fuzzy sleep
   ├─ Remote buffering: sendlineafter more stable than sendline
   ├─ Heap spray: increase spray count + padding chunks to prevent consolidation
   └─ Run 20+ times: verify success rate ≥ 95%
```

## Scenarios

### Scenario 1: Remote 64-bit Binary (NX+PIE+canary, libc given)

```
Given: ./vuln (64-bit ELF, NX, PIE, canary) + ./libc.so.6 + nc host port
Vuln: read(buf, 0x200) but buf is only 0x40 bytes → stack overflow
Protections: canary blocks, PIE randomizes .text

Strategy:
1. Leak canary (stack/format string/partial read)
2. Leak libc function address (puts@got)
3. Calculate libc base: libc.address = leaked - libc.sym['puts']
4. one_gadget ./libc.so.6 — pick gadget whose constraints are satisfied
5. payload = padding + canary + saved_rbp + (pop_rdi + bin_sh + system) or one_gadget
6. Add ret gadget for stack alignment (CRITICAL!)
```

### Scenario 2: Linux Kernel Driver OOB Write → Root

```
Given: vmlinux + bzImage + initramfs.cpio.gz + custom vuln.ko
Vuln: ioctl(0x1337, ptr) with controllable copy_from_user length → kernel heap overflow (kmalloc-64 slab)
Protections: SMEP, SMAP, KASLR, KPTI

Strategy:
1. Modify init script to get root shell (CTF) or leak KASLR base first (real)
2. Leak kernel base via /proc/kallsyms or uninitialized heap spray
3. Spray tty_struct / msg_msg / pipe_buffer in kmalloc-64 slab
4. Overwrite vtable pointer → fails (SMEP), use stack pivot + kernel ROP instead
5. ROP chain: prepare_kernel_cred(0) → commit_creds → swapgs+iretq → usermode execve("/bin/sh")
6. Or simpler: overwrite modprobe_path to "/tmp/x", write /tmp/x, trigger modprobe
```

## Tool Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| pwntools | Exploit framework | `pip install pwntools` |
| GEF | GDB enhancement (kernel + usermode) | `git clone https://github.com/bata24/gef` |
| pwndbg | GDB enhancement (best heap debugging) | `git clone https://github.com/pwndbg/pwndbg && ./setup.sh` |
| ROPgadget | Gadget search | `pip install ropgadget` |
| Ropper | Gadget search (multi-arch) | `pip install ropper` |
| one_gadget | Libc magic gadget finder | `gem install one_gadget` (needs ruby) |
| libc-database | Libc fingerprint reverse lookup | `git clone https://github.com/niklasb/libc-database` |
| qemu-system-x86_64 | Kernel debugging | `apt install qemu-system-x86` |
| binwalk / cpio | Initramfs extraction | `apt install binwalk cpio` |
| patchelf | Switch libc versions | `apt install patchelf` |

## Critical Pitfalls

- **Never commit after local-only success** — local libc/ASLR/network differ from remote, run 20+ times remotely
- **Libc version must be confirmed** — use leak + libc-database reverse lookup, don't assume Ubuntu 22.04 default
- **Stack alignment is the #1 64-bit pitfall** — `movaps xmm0, [rsp]` crashes when rsp not 16-byte aligned, fix with empty `ret` gadget
- **Heap exploitation is glibc-version-sensitive** — tcache introduced in 2.27, safe-linking in 2.32, hooks removed in 2.34, each version has different exploit path
- **Kernel pwn: check CPU flags first** — qemu boot params with/without +smep +smap +pku determines ROP chain structure
- **KASLR leak once is enough** — once you have one kernel address, all others are offset calculations

## References

See `novahaku/testing/references/hacktricks/` for:
- `Methoden Methoden.html#stack-based-buffer-overflow` — stack overflow methodology
- `Methoden Methoden.html#ret2libc` — ret2libc technique
- `Methoden Methoden.html#ret2csu` — __libc_csu_init universal gadget
