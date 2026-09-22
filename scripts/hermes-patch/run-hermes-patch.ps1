<#
.SYNOPSIS
  Drive hermes_patch.py against a local Hermes Agent install.

.DESCRIPTION
  Thin wrapper so the patcher can be run the same way as the other novahaku
  scripts. Passes -Action straight through and propagates the exit code.

.EXAMPLE
  .\run-hermes-patch.ps1 -Root /path/to/hermes-agent/app -Action check
  .\run-hermes-patch.ps1 -Root /path/to/hermes-agent/app -Action apply
  .\run-hermes-patch.ps1 -Root /path/to/hermes-agent/app -Action restore
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][ValidateSet('check', 'apply', 'verify', 'restore')][string]$Action
)

$ErrorActionPreference = 'Stop'
$tool = Join-Path $PSScriptRoot 'hermes_patch.py'

if (-not (Test-Path $tool)) { throw "hermes_patch.py not found at $tool" }

$python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }
& $python $tool --root $Root "--$Action"
exit $LASTEXITCODE
