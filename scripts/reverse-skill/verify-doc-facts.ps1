<#
.SYNOPSIS
  Verify doc fact tables (capability list, MCP endpoints) against the manifest.

.DESCRIPTION
  Guard against doc drift: the MCP server table in README.md and the per-server
  endpoint lines in the reverse-skill docs must match bootstrap-manifest.json.
  Exit 1 on mismatch.

  Rewritten when the old version pointed at retired paths (skills/, RULES.md,
  burp-mcp-full/). A gate that silently checks nothing is worse than no gate.
#>
$ErrorActionPreference = 'Stop'

# repo root = scripts/reverse-skill/ -> ../../
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$fail = 0

function Check([string]$Name, [bool]$Ok, [string]$Detail) {
  if ($Ok) { Write-Host "OK   $Name" } else { $script:fail++; Write-Host "FAIL $Name : $Detail" }
}

$manifestPath = Join-Path $Root 'scripts\reverse-skill\bootstrap-manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) { throw "manifest not found: $manifestPath" }
$manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$caps = @($manifest.capabilities)
Write-Host "source-of-truth: $($caps.Count) capabilities"

# --- Every documented endpoint must exist as a manifest servicePort ---
$readme  = Get-Content (Join-Path $Root 'README.md') -Raw -Encoding UTF8
$install = Get-Content (Join-Path $Root 'INSTALL.md') -Raw -Encoding UTF8

$portCaps = @($caps | Where-Object { $_.PSObject.Properties['servicePort'] })
Check 'manifest declares at least one servicePort' ($portCaps.Count -gt 0) 'no servicePort found in manifest'

foreach ($c in $portCaps) {
  $port = [string]$c.servicePort
  Check "README.md documents port $port ($($c.name))" ($readme.Contains($port)) "missing $port in README.md"
  Check "INSTALL.md documents port $port ($($c.name))" ($install.Contains($port)) "missing $port in INSTALL.md"
}

# --- The 5 MCP skills must each name their own endpoint ---
$skillEndpoints = @{
  'testing\ghidra-reverse\SKILL.md'       = @('8089')
  'testing\ida-reverse\SKILL.md'          = @('13337')
  'testing\binary-ninja-reverse\SKILL.md' = @('24642')
}
foreach ($rel in $skillEndpoints.Keys) {
  $p = Join-Path $Root $rel
  if (-not (Test-Path -LiteralPath $p)) { Check "$rel exists" $false 'file missing'; continue }
  $t = Get-Content $p -Raw -Encoding UTF8
  foreach ($needle in $skillEndpoints[$rel]) {
    Check "$rel names endpoint $needle" ($t.Contains($needle)) "missing $needle in $rel"
  }
  Check "$rel states MCP is optional" ($t -match 'optional|可选') "no optionality note in $rel"
}

# --- Retired references must not reappear ---
$retired = @('localhost:9009', 'binary-ninja-mcp@1.0.0', 'binary_ninja_mcp')
$self = $PSCommandPath
$skipDirs = @('\.git\', '__pycache__', 'novahakupast', 'novaxinweipast', '_recovered')
$hits = 0
$scanned = 0
foreach ($f in Get-ChildItem -LiteralPath $Root -Recurse -File) {
  if ($f.Extension -notin @('.md', '.json')) { continue }
  if ($f.FullName -eq $self) { continue }        # this file names the patterns it forbids
  $skip = $false
  foreach ($d in $skipDirs) { if ($f.FullName.Contains($d)) { $skip = $true; break } }
  if ($skip) { continue }
  $scanned++
  $t = Get-Content $f.FullName -Raw -Encoding UTF8
  if ($null -eq $t) { continue }
  foreach ($r in $retired) {
    if ($t.Contains($r)) {
      $hits++
      Write-Host "FAIL retired reference '$r' in $($f.FullName.Substring($Root.Length + 1))"
    }
  }
}
Check 'no retired Binary Ninja references' ($hits -eq 0) "$hits occurrence(s) across $scanned file(s)"

Write-Host "verify-doc-facts: $fail failure(s)"
if ($fail -gt 0) { exit 1 }
