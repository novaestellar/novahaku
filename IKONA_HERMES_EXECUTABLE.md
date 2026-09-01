# IKONA INTEGRATION — Hermes Executable Plan

> **To:** Hermes Agent (you — Haku)
> **Dari:** OpenCode (Sisyphus)
> **Tanggal:** 2026-09-01
> **Tugas:** Eksekusi plan ini STEP BY STEP. Jangan skip.

---

## STEP 0: SETUP

### 0.1 Clone IKONA-Security

```bash
cd D:\Labs\novahaku
git clone https://github.com/KorekKayu/IKONA-Security.git
```

### 0.2 Verify paths

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$NOVAHAKU = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku"
Write-Host "IKONA: $(Test-Path $IKONA)"
Write-Host "Novahaku: $(Test-Path $NOVAHAKU)"
```

If IKONA does not exist, run git clone first.
If novahaku does not exist, STOP and tell user.

---

## STEP 1: RUNTIME TEST (BEFORE integration)

**Goal: Verify novahaku works before adding new content.

### 1.1 Jalankan static test
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\Design\Desktop\novahaku_test_all.ps1"
```
Expected: 121/121 PASS

### 1.2 Kirim test message ke user

Kirim pesan ini ke user di WhatsApp:
```
Novahaku runtime test:
1. python C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing\scripts\webtest.py --help
2. python C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\reframe\reframe_cli.py "bulk account creation" --fresh
3. Baca C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\techniques\methods\01-boundary\m-01003-delimiter-injection.md

Laporkan hasilnya.
```

### 1.3 Tunggu user response
If ALL PASS, continue to Step 2.
If any FAIL, fix it first.

---

## STEP 2: CONFLICT CHECK

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$NOVAHAKU = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku"

# List IKONA modules
Get-ChildItem $IKONA -Directory | Where-Object { $_.Name -match "^IKONA_" } | Select-Object Name

# Count existing references
$existing = (Get-ChildItem "$NOVAHAKU\testing\references" -Recurse -File).Count
Write-Host "Existing: $existing | IKONA payloads: ~64 | IKONA hackskills: ~102"
```

Report to user with gap analysis results.

---

## STEP 2.5: TRANSLATE ALL IKONA FILES

ALL IKONA files are in Bahasa Indonesia. Before copying, translate EVERY file to 简体中文.

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"

# For each IKONA SKILL.md file:
Get-ChildItem "$IKONA\IKONA_*\SKILL.md" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    # Translate Indonesian → Chinese (manual or via translation tool)
    # Keep technical terms (tool names, vulnerability types) as-is
    $content | Set-Content $_.FullName -Encoding UTF8
    Write-Host "Translated: $($_.Name)"
}
```

**Translation rules:**
- Indonesian → 简体中文
- Technical terms (SQLi, XSS, Burp Suite, etc.) → keep as-is
- File names → keep as-is (will be rebranded in Step 10)

---

## STEP 3: PAT MISSING (49 files)

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$TARGET = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing\references\payloadsallthethings"

# Copy categories that are missing
# (49 categories dari IKONA_PAYLOADS)
```

---

## STEP 4: HACKTRICKS MISSING (73 files)

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$TARGET = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing\references\hacktricks"

# Copy techniques that are missing
# (73 techniques dari IKONA_HACKSKILLS)
```

---

## STEP 5: HUNT PLAYBOOKS (83 files)

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$TARGET = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing\hunt"
New-Item -ItemType Directory -Path $TARGET -Force
Get-ChildItem "$IKONA\IKONA_BUGHUNTER\hunt-*.md" | Copy-Item -Destination $TARGET
```

---

## STEP 6: FRAMEWORK AUDITS (4 files)

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$TARGET = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing\frameworks"
New-Item -ItemType Directory -Path $TARGET -Force

# Single files
Copy-Item "$IKONA\IKONA_NEXTJS\SKILL.md" "$TARGET\nextjs-audit.md"
Copy-Item "$IKONA\IKONA_TURNSTILE\SKILL.md" "$TARGET\turnstile-bypass.md"

# Merged: laravel-security.md = IKONA_LARAVEL + IKONA_LARAVEL_AUDIT
# Merged: supabase-baaS-audit.md = IKONA_SUPABASE_AUDIT + IKONA_BAAS
```

---

## STEP 7: SPECIALIZED GUIDES (3 files)

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$TARGET = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing"

Copy-Item "$IKONA\IKONA_BIZLOGIC\SKILL.md" "$TARGET\bizlogic.md"
Copy-Item "$IKONA\IKONA_FORUMHACK\SKILL.md" "$TARGET\forumhack.md"
# Merged: bug-bounty-guide.md = IKONA_BUGHUNT + IKONA_ADVANCED_HUNT
```

---

## STEP 8: WORDLISTS (5 files)

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$TARGET = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing\wordlists"
New-Item -ItemType Directory -Path $TARGET -Force
Copy-Item "$IKONA\wordlists\*" "$TARGET\"
```

---

## STEP 9: EXPLOIT SCRIPTS (17 files)

```powershell
$IKONA = "D:\Labs\novahaku\IKONA-Security"
$TARGET = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\testing\exploits"
New-Item -ItemType Directory -Path $TARGET -Force
Copy-Item "$IKONA\IKONA_EXPLOIT_SCRIPTS\*.py" "$TARGET\"

# Rebrand
Get-ChildItem "$TARGET\*.py" | ForEach-Object {
    (Get-Content $_.FullName) -replace "Cybermes", "novahaku" | Set-Content $_.FullName
}
```

---

## STEP 10: REBRAND

```powershell
$NOVAHAKU = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku"

# IKONA → novahaku
Get-ChildItem "$NOVAHAKU\**\*.md" -Recurse | ForEach-Object {
    $c = Get-Content $_.FullName -Raw
    if ($c -match "IKONA") { $c -replace "IKONA", "novahaku" | Set-Content $_.FullName }
    if ($c -match "KorekKayu") { $c -replace "KorekKayu", "novaestellar" | Set-Content $_.FullName }
}
```

---

## STEP 11: UPDATE SKILL.md + README.md

Tambah capabilities baru: Framework Audits, Exploit Scripts, Hunt Playbooks, Wordlists.

---

## STEP 12: UPDATE TEST SUITE

Add tests for new files.

---

## STEP 13: VERIFY & SYNC

```powershell
# Rebrand check
$refs = Select-String -Path "$NOVAHAKU\**\*.md","$NOVAHAKU\**\*.py" -Pattern "IKONA|KorekKayu|Cybermes" -ErrorAction SilentlyContinue
if ($refs.Count -eq 0) { Write-Host "CLEAN" } else { Write-Host "FOUND $($refs.Count) refs" }

# Sync repo
robocopy "$NOVAHAKU" "D:\Labs\novahaku\github-repo" /MIR /XD __pycache__ .git /XF *.pyc .key vault.dat
cd D:\Labs\novahaku\github-repo; git add -A; git commit -m "IKONA integration"; git push
```

---

## REFERENSI

| File | Lokasi |
|------|--------|
| IKONA-Security | `D:\Labs\novahaku\IKONA-Security\` |
| Novahaku | `C:\Users\Design\AppData\Local\hermes\skills\security\novahaku\` |
| Plan detail | `C:\Users\Design\Desktop\IKONA_INTEGRATION_PLAN.md` |


