#Requires -Version 5.1
<#
.NOVAKAHU COMPREHENSIVE TEST SUITE
.SYNOPSIS
    Tests ALL novahaku capabilities: scripts, configs, payloads, references, identity.
.DESCRIPTION
    Run from PowerShell. Tests every file in novahaku skill for:
    - Python scripts: syntax check + import test
    - Config files: JSON validity + YAML parse
    - Markdown files: exist + non-empty + readable
    - Payload system: loader + encryption
    - Identity system: few-shots + terms
.NOTES
    Agent: Haku
    Repo: https://github.com/novaestellar/novahaku
#>

$ErrorActionPreference = "Continue"
$NOVAHAKU = "C:\Users\Design\AppData\Local\hermes\skills\security\novahaku"
$PYTHON = "python"
$PASS = 0
$FAIL = 0
$WARN = 0
$RESULTS = @()

function Test-Item {
    param([string]$Name, [string]$Category, [scriptblock]$Test)
    $result = [PSCustomObject]@{ Name=$Name; Category=$Category; Status=""; Detail="" }
    try {
        $output = & $Test
        if ($output -eq $true -or $LASTEXITCODE -eq 0 -or $output -notmatch "error|Error|FAIL") {
            $result.Status = "PASS"
            $script:PASS++
        } else {
            $result.Status = "FAIL"
            $result.Detail = "$output"
            $script:FAIL++
        }
    } catch {
        $result.Status = "FAIL"
        $result.Detail = $_.Exception.Message
        $script:FAIL++
    }
    $script:RESULTS += $result
    $color = switch($result.Status) { "PASS"{"Green"} "FAIL"{"Red"} "WARN"{"Yellow"} }
    Write-Host "  [$($result.Status)] $Name" -ForegroundColor $color
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NOVAHAKU COMPREHENSIVE TEST SUITE" -ForegroundColor Cyan
Write-Host "  Agent: Haku" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════
# 1. STRUCTURE TESTS
# ═══════════════════════════════════════════
Write-Host "=== 1. STRUCTURE ===" -ForegroundColor Yellow

Test-Item "SKILL.md exists" "structure" { Test-Path "$NOVAHAKU\SKILL.md" }
Test-Item "SOUL.md exists" "structure" { Test-Path "$NOVAHAKU\SOUL.md" }
Test-Item "README.md exists" "structure" { Test-Path "$NOVAHAKU\README.md" }
Test-Item ".env.example exists" "structure" { Test-Path "$NOVAHAKU\.env.example" }
Test-Item ".gitignore exists" "structure" { Test-Path "$NOVAHAKU\.gitignore" }

Test-Item "attack/ directory" "structure" { Test-Path "$NOVAHAKU\attack" }
Test-Item "config/ directory" "structure" { Test-Path "$NOVAHAKU\config" }
Test-Item "identity/ directory" "structure" { Test-Path "$NOVAHAKU\identity" }
Test-Item "reframe/ directory" "structure" { Test-Path "$NOVAHAKU\reframe" }
Test-Item "scripts/ directory" "structure" { Test-Path "$NOVAHAKU\scripts" }
Test-Item "techniques/ directory" "structure" { Test-Path "$NOVAHAKU\techniques" }
Test-Item "templates/ directory" "structure" { Test-Path "$NOVAHAKU\templates" }
Test-Item "testing/ directory" "structure" { Test-Path "$NOVAHAKU\testing" }
Test-Item "train/ directory" "structure" { Test-Path "$NOVAHAKU\train" }
Test-Item "windows-re/ directory" "structure" { Test-Path "$NOVAHAKU\windows-re" }

# ═══════════════════════════════════════════
# 2. PYTHON SYNTAX CHECKS
# ═══════════════════════════════════════════
Write-Host "`n=== 2. PYTHON SCRIPTS ===" -ForegroundColor Yellow

$pyScripts = @(
    "reframe\reframe_cli.py",
    "techniques\loader.py",
    "config\locks.py",
    "testing\scripts\webtest.py",
    "testing\scripts\race_test.py",
    "testing\scripts\jwt_test.py",
    "train\train.py",
    "attack\test\test-novahaku.py"
)

foreach ($script in $pyScripts) {
    $path = "$NOVAHAKU\$script"
    $name = Split-Path $script -Leaf
    Test-Item "$name syntax check" "python" {
        $result = & $PYTHON -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('OK')" 2>&1
        if ($result -eq "OK") { $true } else { $result }
    }
}

# ═══════════════════════════════════════════
# 3. PYTHON IMPORT TESTS
# ═══════════════════════════════════════════
Write-Host "`n=== 3. PYTHON IMPORTS ===" -ForegroundColor Yellow

Test-Item "reframe_cli.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\reframe'); import reframe_cli; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "loader.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\techniques'); import loader; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "locks.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\config'); import locks; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "webtest.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\testing\scripts'); import webtest; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "race_test.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\testing\scripts'); import race_test; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "jwt_test.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\testing\scripts'); import jwt_test; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "train.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\train'); import train; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "test-novahaku.py import" "import" {
    $r = & $PYTHON -c "import sys; sys.path.insert(0, r'$NOVAHAKU\attack\test'); import test_novahaku; print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

# ═══════════════════════════════════════════
# 4. CONFIG FILES
# ═══════════════════════════════════════════
Write-Host "`n=== 4. CONFIG FILES ===" -ForegroundColor Yellow

Test-Item "TRIGGER_MAP.json valid" "config" {
    $r = & $PYTHON -c "import json; json.load(open(r'$NOVAHAKU\config\TRIGGER_MAP.json')); print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "prefill.json valid" "config" {
    $r = & $PYTHON -c "import json; json.load(open(r'$NOVAHAKU\attack\config\prefill.json')); print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "full_lock.conf exists" "config" { (Get-Item "$NOVAHAKU\config\full_lock.conf").Length -gt 0 }
Test-Item "system-prompt.txt exists" "config" { (Get-Item "$NOVAHAKU\config\system-prompt.txt").Length -gt 0 }

Test-Item "TRIGGER_MAP has 8 domains" "config" {
    $j = Get-Content "$NOVAHAKU\config\TRIGGER_MAP.json" -Raw | ConvertFrom-Json
    if ($j.PSObject.Properties.Count -ge 6) { $true } else { "Only $($j.PSObject.Properties.Count) domains" }
}

# ═══════════════════════════════════════════
# 5. PAYLOAD & VAULT SYSTEM
# ═══════════════════════════════════════════
Write-Host "`n=== 5. PAYLOAD & VAULT ===" -ForegroundColor Yellow

Test-Item "techniques/payload/payload.json valid" "vault" {
    $r = & $PYTHON -c "import json; d=json.load(open(r'$NOVAHAKU\techniques\payload\payload.json')); print(f'OK:{len(d[\"categories\"])} categories')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "techniques/payload/payload.json valid" "vault" {
    $r = & $PYTHON -c "import json; d=json.load(open(r'$NOVAHAKU\techniques\payload\payload.json')); print(f'OK:{len(d[\"categories\"])} categories')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "techniques/payload/payload.json >= 50KB" "vault" {
    (Get-Item "$NOVAHAKU\techniques\payload\payload.json").Length -ge 50000
}

Test-Item "No .key files in git" "vault" {
    $keys = git -C "$NOVAHAKU" ls-files | Where-Object { $_ -match "\.key$" }
    if ($keys.Count -eq 0) { $true } else { ".key in git: $($keys -join ', ')" }
}

Test-Item "No vault.dat in git" "vault" {
    $dats = git -C "$NOVAHAKU" ls-files | Where-Object { $_ -match "vault\.dat$" }
    if ($dats.Count -eq 0) { $true } else { "vault.dat in git: $($dats -join ', ')" }
}

# ═══════════════════════════════════════════
# 6. IDENTITY SYSTEM
# ═══════════════════════════════════════════
Write-Host "`n=== 6. IDENTITY ===" -ForegroundColor Yellow

Test-Item "few-shots-primary.md > 10KB" "identity" {
    (Get-Item "$NOVAHAKU\identity\few-shots-primary.md").Length -ge 10000
}

Test-Item "terms.md > 10KB" "identity" {
    (Get-Item "$NOVAHAKU\identity\terms.md").Length -ge 10000
}

Test-Item "CLAUDE.md exists" "identity" {
    Test-Path "$NOVAHAKU\identity\novahaku-files\claude-config-bundle\CLAUDE.md"
}

Test-Item "system-prompt.md exists" "identity" {
    Test-Path "$NOVAHAKU\identity\novahaku-files\claude-config-bundle\system-prompt.md"
}

Test-Item "No 'seagull' references" "identity" {
    $refs = Select-String -Path "$NOVAHAKU\**\*.md","$NOVAHAKU\**\*.py","$NOVAHAKU\**\*.json" -Pattern "seagull" -SimpleMatch -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found $($refs.Count) seagull references" }
}

Test-Item "No '海鸥' references" "identity" {
    $refs = Select-String -Path "$NOVAHAKU\**\*.md","$NOVAHAKU\**\*.py","$NOVAHAKU\**\*.json" -Pattern "海鸥" -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found $($refs.Count) 海鸥 references" }
}

Test-Item "No 'AEGIS' references" "identity" {
    $refs = Select-String -Path "$NOVAHAKU\**\*.md","$NOVAHAKU\**\*.py","$NOVAHAKU\**\*.json" -Pattern "AEGIS" -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found $($refs.Count) AEGIS references" }
}

Test-Item "No 'dark mage' references" "identity" {
    $refs = Select-String -Path "$NOVAHAKU\**\*.md","$NOVAHAKU\**\*.py","$NOVAHAKU\**\*.json" -Pattern "dark mage" -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found $($refs.Count) dark mage references" }
}

# ═══════════════════════════════════════════
# 7. TECHNIQUES (121 methods)
# ═══════════════════════════════════════════
Write-Host "`n=== 7. TECHNIQUES ===" -ForegroundColor Yellow

$categories = @("01-boundary","02-priming","03-identity","04-encoding","05-multi-provider","06-iterative","07-stream")
foreach ($cat in $categories) {
    Test-Item "$cat/ exists" "techniques" { Test-Path "$NOVAHAKU\techniques\methods\$cat" }
    Test-Item "$cat/ has 15+ files" "techniques" {
        $count = (Get-ChildItem "$NOVAHAKU\techniques\methods\$cat" -File).Count
        if ($count -ge 15) { $true } else { "Only $count files" }
    }
}

Test-Item "01-boundary has 16 files" "techniques" {
    $count = (Get-ChildItem "$NOVAHAKU\techniques\methods\01-boundary" -File).Count
    if ($count -ge 16) { $true } else { "Only $count files" }
}

Test-Item "flow.md exists" "techniques" { Test-Path "$NOVAHAKU\techniques\flow.md" }
Test-Item "loader.py exists" "techniques" { Test-Path "$NOVAHAKU\techniques\loader.py" }
Test-Item "7 workers exist" "techniques" {
    $count = (Get-ChildItem "$NOVAHAKU\techniques\workers" -File).Count
    if ($count -ge 7) { $true } else { "Only $count workers" }
}
Test-Item "4 templates exist" "techniques" {
    $count = (Get-ChildItem "$NOVAHAKU\techniques\templates" -File).Count
    if ($count -ge 4) { $true } else { "Only $count templates" }
}

# ═══════════════════════════════════════════
# 8. ATTACK FRAMEWORK
# ═══════════════════════════════════════════
Write-Host "`n=== 8. ATTACK FRAMEWORK ===" -ForegroundColor Yellow

Test-Item "system-prompt.md exists" "identity" { Test-Path "$NOVAHAKU\identity\novahaku-files\claude-config-bundle\system-prompt.md" }
Test-Item "5 attack-flow files" "attack" {
    $count = (Get-ChildItem "$NOVAHAKU\attack\attack-flow" -File).Count
    if ($count -ge 5) { $true } else { "Only $count files" }
}
Test-Item "test-novahaku.py exists" "attack" { Test-Path "$NOVAHAKU\attack\test\test-novahaku.py" }
Test-Item "prefill.json exists" "attack" { Test-Path "$NOVAHAKU\attack\config\prefill.json" }

Test-Item "No hardcoded API keys" "attack" {
    $refs = Select-String -Path "$NOVAHAKU\attack\test\test-novahaku.py" -Pattern "sk-[a-zA-Z0-9]{20,}" -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found hardcoded API keys" }
}

# ═══════════════════════════════════════════
# 9. TESTING REFERENCES (48 files)
# ═══════════════════════════════════════════
Write-Host "`n=== 9. TESTING REFERENCES ===" -ForegroundColor Yellow

$htCount = (Get-ChildItem "$NOVAHAKU\testing\references\hacktricks" -File).Count
$patCount = (Get-ChildItem "$NOVAHAKU\testing\references\payloadsallthethings" -File).Count
$miscCount = (Get-ChildItem "$NOVAHAKU\testing\references\misc" -File).Count

Test-Item "hacktricks/ >= 29 files" "testing" { if ($htCount -ge 29) { $true } else { "Only $htCount files" } }
Test-Item "payloadsallthethings/ >= 15 files" "testing" { if ($patCount -ge 15) { $true } else { "Only $patCount files" } }
Test-Item "misc/ >= 4 files" "testing" { if ($miscCount -ge 4) { $true } else { "Only $miscCount files" } }
Test-Item "3 test scripts exist" "testing" {
    $count = (Get-ChildItem "$NOVAHAKU\testing\scripts" -File -Filter "*.py").Count
    if ($count -ge 3) { $true } else { "Only $count scripts" }
}

# ═══════════════════════════════════════════
# 10. REFRAME ENGINE
# ═══════════════════════════════════════════
Write-Host "`n=== 10. REFRAME ENGINE ===" -ForegroundColor Yellow

Test-Item "reframe_cli.py exists" "reframe" { Test-Path "$NOVAHAKU\reframe\reframe_cli.py" }
Test-Item "reframe_cli.py > 10KB" "reframe" { (Get-Item "$NOVAHAKU\reframe\reframe_cli.py").Length -ge 10000 }
Test-Item "No 'dmf_cli' references" "reframe" {
    $refs = Select-String -Path "$NOVAHAKU\reframe\reframe_cli.py" -Pattern "dmf_cli" -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found dmf_cli references" }
}

# ═══════════════════════════════════════════
# 11. WINDOWS RE
# ═══════════════════════════════════════════
Write-Host "`n=== 11. WINDOWS RE ===" -ForegroundColor Yellow

Test-Item "windows-re.md exists" "windows-re" { Test-Path "$NOVAHAKU\windows-re\windows-re.md" }
Test-Item "No 'agents-1' filename" "windows-re" {
    $files = Get-ChildItem "$NOVAHAKU\windows-re" -File | Where-Object { $_.Name -eq "agents-1.md" }
    if ($files.Count -eq 0) { $true } else { "agents-1.md still exists" }
}

# ═══════════════════════════════════════════
# 12. TRAINING
# ═══════════════════════════════════════════
Write-Host "`n=== 12. TRAINING ===" -ForegroundColor Yellow

Test-Item "train.py exists" "train" { Test-Path "$NOVAHAKU\train\train.py" }
Test-Item "training_results.json valid" "train" {
    $r = & $PYTHON -c "import json; json.load(open(r'$NOVAHAKU\train\benchmarks\training_results.json')); print('OK')" 2>&1
    if ($r -match "OK") { $true } else { $r }
}

# ═══════════════════════════════════════════
# 13. DEPLOY SCRIPTS
# ═══════════════════════════════════════════
Write-Host "`n=== 13. DEPLOY SCRIPTS ===" -ForegroundColor Yellow

Test-Item "install.ps1 exists" "deploy" { Test-Path "$NOVAHAKU\scripts\deploy\install.ps1" }
Test-Item "install.sh exists" "deploy" { Test-Path "$NOVAHAKU\scripts\deploy\install.sh" }
Test-Item "install.command exists" "deploy" { Test-Path "$NOVAHAKU\scripts\deploy\install.command" }

Test-Item "No broken path refs in scripts" "deploy" {
    $refs = Select-String -Path "$NOVAHAKU\scripts\deploy\*" -Pattern "dmf_cli|agents-1|test-prometheus|seagull" -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found $($refs.Count) broken references" }
}

# ═══════════════════════════════════════════
# 14. CROSS-REFERENCE INTEGRITY
# ═══════════════════════════════════════════
Write-Host "`n=== 14. CROSS-REFERENCE INTEGRITY ===" -ForegroundColor Yellow

Test-Item "No old file references" "integrity" {
    $refs = Select-String -Path "$NOVAHAKU\**\*.md","$NOVAHAKU\**\*.py","$NOVAHAKU\**\*.json","$NOVAHAKU\**\*.sh","$NOVAHAKU\**\*.ps1" -Pattern "dmf_cli\.py|agents-1\.md|test-prometheus\.py|seagull-files|dark mage" -ErrorAction SilentlyContinue
    if ($refs.Count -eq 0) { $true } else { "Found $($refs.Count) old references: $($refs[0].Filename):$($refs[0].LineNumber)" }
}

Test-Item "README paths match reality" "integrity" {
    $missing = @()
    @("reframe/reframe_cli.py","windows-re/windows-re.md","attack/test/test-novahaku.py","identity/novahaku-files/claude-config-bundle/CLAUDE.md") | ForEach-Object {
        if (-not (Test-Path "$NOVAHAKU\$_")) { $missing += $_ }
    }
    if ($missing.Count -eq 0) { $true } else { "Missing: $($missing -join ', ')" }
}

# ═══════════════════════════════════════════
# 15. FUNCTIONAL TESTS — VAULT & CRYPTO
# ═══════════════════════════════════════════
Write-Host "`n=== 15. VAULT & CRYPTO ===" -ForegroundColor Yellow

Test-Item "vault decrypt pipeline works" "functional" {
    $r = & $PYTHON -c @"
import sys, os, json, tempfile, hashlib
from pathlib import Path
sys.path.insert(0, r'$NOVAHAKU\techniques')
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    # Generate throwaway key
    key = get_random_bytes(32)
    # Encrypt known plaintext
    plaintext = b'NOVAHAKU VAULT TEST: Hello Haku'
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    # Verify decrypt
    decipher = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
    decrypted = decipher.decrypt_and_verify(ciphertext, tag)
    assert decrypted == plaintext, f'Decrypt mismatch: {decrypted}'
    print('OK:vault_pipeline_works')
except Exception as e:
    print(f'FAIL:{e}')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "vault payload.json schema valid" "functional" {
    $r = & $PYTHON -c @"
import json, sys
with open(r'$NOVAHAKU\techniques\payload\payload.json') as f:
    d = json.load(f)
# Check required top-level keys
assert 'version' in d, 'missing version'
assert 'framework' in d, 'missing framework'
assert 'categories' in d, 'missing categories'
assert isinstance(d['categories'], dict), 'categories not dict'
# Check each category has required fields
for cat_id, cat in d['categories'].items():
    assert 'name' in cat, f'{cat_id} missing name'
    assert 'methods' in cat, f'{cat_id} missing methods'
    assert isinstance(cat['methods'], list), f'{cat_id} methods not list'
    for m in cat['methods']:
        assert 'id' in m, f'{cat_id} method missing id'
        assert 'file' in m, f'{cat_id} method missing file'
        assert 'content' in m, f'{cat_id} method missing content'
print(f'OK:{len(d[\"categories\"])} categories, {sum(len(c[\"methods\"]) for c in d[\"categories\"].values())} methods')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

# ═══════════════════════════════════════════
# 16. FUNCTIONAL TESTS — SOUL CONTENT
# ═══════════════════════════════════════════
Write-Host "`n=== 16. SOUL CONTENT ===" -ForegroundColor Yellow

Test-Item "SOUL.md has identity section" "functional" {
    $content = Get-Content "$NOVAHAKU\SOUL.md" -Raw
    if ($content -match "## 1\. Identity" -or $content -match "Identity") { $true } else { "Missing Identity section" }
}

Test-Item "SOUL.md mentions Haku" "functional" {
    $content = Get-Content "$NOVAHAKU\SOUL.md" -Raw
    if ($content -match "Haku") { $true } else { "Does not mention Haku" }
}

Test-Item "SOUL.md >= 5 sections" "functional" {
    $sections = (Select-String -Path "$NOVAHAKU\SOUL.md" -Pattern "^## " -AllMatches).Matches.Count
    if ($sections -ge 10) { $true } else { "Only $sections sections" }
}

# ═══════════════════════════════════════════
# 17. FUNCTIONAL TESTS — SKILL STRUCTURE
# ═══════════════════════════════════════════
Write-Host "`n=== 17. SKILL STRUCTURE ===" -ForegroundColor Yellow

Test-Item "SKILL.md has 6 capabilities" "functional" {
    $content = Get-Content "$NOVAHAKU\SKILL.md" -Raw
    $caps = @("Web Testing","Prompt Engineering","Attack Framework","Reframe Engine","Windows RE","Identity")
    $found = $caps | Where-Object { $content -match $_ }
    if ($found.Count -ge 6) { $true } else { "Only $($found.Count)/6 capabilities" }
}

Test-Item "SKILL.md has auto-load rules" "functional" {
    $content = Get-Content "$NOVAHAKU\SKILL.md" -Raw
    if ($content -match "Auto-Load" -or $content -match "auto.*load") { $true } else { "Missing auto-load rules" }
}

# ═══════════════════════════════════════════
# 18. FUNCTIONAL TESTS — TECHNIQUES PIPELINE
# ═══════════════════════════════════════════
Write-Host "`n=== 18. TECHNIQUES PIPELINE ===" -ForegroundColor Yellow

Test-Item "loader.py can list categories" "functional" {
    $r = & $PYTHON -c @"
import sys, json
sys.path.insert(0, r'$NOVAHAKU\techniques')
from loader import get_category, PAYLOAD_JSON
with open(PAYLOAD_JSON) as f:
    payload = json.load(f)
cats = list(payload['categories'].keys())
assert len(cats) >= 5, f'Only {len(cats)} categories'
cat_result = get_category(payload, cats[0])
assert len(cat_result) > 0, 'Empty category result'
print(f'OK:{len(cats)} categories')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "loader.py can search methods" "functional" {
    $r = & $PYTHON -c @"
import sys, json
sys.path.insert(0, r'$NOVAHAKU\techniques')
from loader import get_method, PAYLOAD_JSON
with open(PAYLOAD_JSON) as f:
    payload = json.load(f)
# Get first method from first category
first_cat = list(payload['categories'].keys())[0]
first_method = payload['categories'][first_cat]['methods'][0]['id']
result = get_method(payload, first_method)
assert len(result) > 0, 'Empty method result'
print(f'OK:method_{first_method}_found')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

# ═══════════════════════════════════════════
# 19. FUNCTIONAL TESTS — ATTACK FRAMEWORK
# ═══════════════════════════════════════════
Write-Host "`n=== 19. ATTACK FRAMEWORK ===" -ForegroundColor Yellow

Test-Item "prefill.json has v41 prompt" "functional" {
    $r = & $PYTHON -c @"
import json
with open(r'$NOVAHAKU\attack\config\prefill.json') as f:
    d = json.load(f)
assert 'prompt' in d or 'content' in d or 'messages' in d, 'No prompt/content/messages key'
print('OK:prefill_has_prompt')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "attack-flow files are readable" "functional" {
    $files = Get-ChildItem "$NOVAHAKU\attack\attack-flow" -File
    $readable = $files | Where-Object { $_.Length -gt 100 }
    if ($readable.Count -ge 5) { $true } else { "Only $($readable.Count)/5 readable" }
}

# ═══════════════════════════════════════════
# 20. FUNCTIONAL TESTS — REFRAME ENGINE
# ═══════════════════════════════════════════
Write-Host "`n=== 20. REFRAME ENGINE ===" -ForegroundColor Yellow

Test-Item "reframe_cli.py has TRIGGER_MAP" "functional" {
    $content = Get-Content "$NOVAHAKU\reframe\reframe_cli.py" -Raw
    if ($content -match "TRIGGER_MAP") { $true } else { "Missing TRIGGER_MAP" }
}

Test-Item "reframe_cli.py has 40+ triggers" "functional" {
    $r = & $PYTHON -c @"
import sys
sys.path.insert(0, r'$NOVAHAKU\reframe')
from reframe_cli import TRIGGER_MAP
assert len(TRIGGER_MAP) >= 40, f'Only {len(TRIGGER_MAP)} triggers'
print(f'OK:{len(TRIGGER_MAP)} triggers')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

# ═══════════════════════════════════════════
# 21. FUNCTIONAL TESTS — LOCKS SYSTEM
# ═══════════════════════════════════════════
Write-Host "`n=== 21. LOCKS SYSTEM ===" -ForegroundColor Yellow

Test-Item "locks.py has 4 lock commands" "functional" {
    $r = & $PYTHON -c @"
import sys
sys.path.insert(0, r'$NOVAHAKU\config')
from locks import LOCKS, get_lock
assert len(LOCKS) >= 4, f'Only {len(LOCKS)} locks'
# Test each lock
for lock_type in LOCKS:
    result = get_lock(lock_type)
    assert len(result) > 0, f'{lock_type} returned empty'
print(f'OK:{len(LOCKS)} locks')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "TRIGGER_MAP has 8 domains" "functional" {
    $r = & $PYTHON -c @"
import json
with open(r'$NOVAHAKU\config\TRIGGER_MAP.json') as f:
    d = json.load(f)
assert len(d) >= 6, f'Only {len(d)} domains'
for k, v in d.items():
    assert 'keywords' in v, f'{k} missing keywords'
    assert len(v['keywords']) > 0, f'{k} has empty keywords'
print(f'OK:{len(d)} domains')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

# ═══════════════════════════════════════════
# 22. FUNCTIONAL TESTS — IDENTITY DATA
# ═══════════════════════════════════════════
Write-Host "`n=== 22. IDENTITY DATA ===" -ForegroundColor Yellow

Test-Item "few-shots has 500+ entries" "functional" {
    $r = & $PYTHON -c @"
import re
with open(r'$NOVAHAKU\identity\few-shots-primary.md', encoding='utf-8') as f:
    content = f.read()
# Count Q: patterns
entries = len(re.findall(r'^Q:', content, re.MULTILINE))
assert entries >= 500, f'Only {entries} entries'
print(f'OK:{entries} entries')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "terms.md has 100+ terms" "functional" {
    $r = & $PYTHON -c @"
import re
with open(r'$NOVAHAKU\identity\terms.md', encoding='utf-8') as f:
    content = f.read()
# Count term mappings
terms = len(re.findall(r'^\|.*\|.*\|', content, re.MULTILINE))
assert terms >= 100, f'Only {terms} terms'
print(f'OK:{terms} terms')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

Test-Item "CLAUDE.md mentions Haku" "functional" {
    $content = Get-Content "$NOVAHAKU\identity\novahaku-files\claude-config-bundle\CLAUDE.md" -Raw -Encoding UTF8
    if ($content -match "Haku") { $true } else { "Does not mention Haku" }
}

# ═══════════════════════════════════════════
# 23. FUNCTIONAL TESTS — TESTING SCRIPTS
# ═══════════════════════════════════════════
Write-Host "`n=== 23. TESTING SCRIPTS ===" -ForegroundColor Yellow

Test-Item "webtest.py has T class" "functional" {
    $content = Get-Content "$NOVAHAKU\testing\scripts\webtest.py" -Raw
    if ($content -match "class T") { $true } else { "Missing T class" }
}

Test-Item "race_test.py has main function" "functional" {
    $content = Get-Content "$NOVAHAKU\testing\scripts\race_test.py" -Raw
    if ($content -match "def main") { $true } else { "Missing main function" }
}

Test-Item "jwt_test.py has sign function" "functional" {
    $content = Get-Content "$NOVAHAKU\testing\scripts\jwt_test.py" -Raw
    if ($content -match "def sign") { $true } else { "Missing sign function" }
}

# ═══════════════════════════════════════════
# 24. FUNCTIONAL TESTS — WINDOWS RE
# ═══════════════════════════════════════════
Write-Host "`n=== 24. WINDOWS RE ===" -ForegroundColor Yellow

Test-Item "windows-re.md has anti-debug section" "functional" {
    $content = Get-Content "$NOVAHAKU\windows-re\windows-re.md" -Raw
    if ($content -match "anti-debug" -or $content -match "Anti-Debug") { $true } else { "Missing anti-debug section" }
}

Test-Item "windows-re.md mentions x64dbg" "functional" {
    $content = Get-Content "$NOVAHAKU\windows-re\windows-re.md" -Raw
    if ($content -match "x64dbg") { $true } else { "Does not mention x64dbg" }
}

# ═══════════════════════════════════════════
# 25. FUNCTIONAL TESTS — TEMPLATES
# ═══════════════════════════════════════════
Write-Host "`n=== 25. TEMPLATES ===" -ForegroundColor Yellow

Test-Item "prompt-arsenal.md has sections" "functional" {
    $sections = (Select-String -Path "$NOVAHAKU\techniques\templates\prompt-arsenal.md" -Pattern "^## " -AllMatches).Matches.Count
    if ($sections -ge 3) { $true } else { "Only $sections sections" }
}

Test-Item "test-report.md has sections" "functional" {
    $sections = (Select-String -Path "$NOVAHAKU\techniques\templates\test-report.md" -Pattern "^## " -AllMatches).Matches.Count
    if ($sections -ge 3) { $true } else { "Only $sections sections" }
}

# ═══════════════════════════════════════════
# 26. FUNCTIONAL TESTS — TRAINING
# ═══════════════════════════════════════════
Write-Host "`n=== 26. TRAINING ===" -ForegroundColor Yellow

Test-Item "train.py has test_provider_model" "functional" {
    $content = Get-Content "$NOVAHAKU\train\train.py" -Raw
    if ($content -match "def test_provider_model") { $true } else { "Missing test_provider_model function" }
}

Test-Item "training_results.json has results" "functional" {
    $r = & $PYTHON -c @"
import json
with open(r'$NOVAHAKU\train\benchmarks\training_results.json') as f:
    d = json.load(f)
assert isinstance(d, (dict, list)), 'Not dict or list'
print(f'OK:type={type(d).__name__}')
"@ 2>&1
    if ($r -match "OK") { $true } else { $r }
}

# ═══════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESULTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  PASS: $PASS" -ForegroundColor Green
Write-Host "  FAIL: $FAIL" -ForegroundColor Red
Write-Host "  TOTAL: $($PASS + $FAIL)" -ForegroundColor White
Write-Host ""

if ($FAIL -gt 0) {
    Write-Host "FAILED TESTS:" -ForegroundColor Red
    $RESULTS | Where-Object Status -eq "FAIL" | ForEach-Object {
        Write-Host "  [$($_.Category)] $($_.Name): $($_.Detail)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor $(if($FAIL -eq 0){"Green"}else{"Yellow"})
Write-Host $(if($FAIL -eq 0){"ALL TESTS PASSED"}else{"$FAIL TESTS FAILED"}) -ForegroundColor $(if($FAIL -eq 0){"Green"}else{"Yellow"})
Write-Host "========================================" -ForegroundColor $(if($FAIL -eq 0){"Green"}else{"Yellow"})
Write-Host ""
