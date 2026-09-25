# start-idapro.ps1 — launch IDA Pro so the idalib MCP plugin listens on the
# loopback service port declared in bootstrap-manifest.json (capability: idapro).
#
# IDA's stdout is unreliable, so this launcher reports what it did through its
# own exit code and lets the caller probe the port.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File start-idapro.ps1 [-Target <file>] [-Port 13337] [-Gui]
#
# Exit codes:
#   0  port already listening, or IDA launched and the port came up
#   1  IDA not found
#   2  IDA launched but the service port never came up

[CmdletBinding()]
param(
    [string]$Target,
    [int]$Port = 13337,
    [switch]$Gui,
    [int]$TimeoutSeconds = 60
)

$ErrorActionPreference = 'Stop'

function Test-Port([int]$P) {
    # A failed connect is the normal "not up yet" answer, so this must not throw.
    # Test-NetConnection would print a banner and is slow; a raw async connect is
    # quiet and bounded by the same millisecond timeout.
    $client = [System.Net.Sockets.Socket]::new(
        [System.Net.Sockets.AddressFamily]::InterNetwork,
        [System.Net.Sockets.SocketType]::Stream,
        [System.Net.Sockets.ProtocolType]::Tcp)
    try {
        $async = $client.BeginConnect('127.0.0.1', $P, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(500)) { return $false }
        $client.EndConnect($async)
        return $true
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

if (Test-Port -P $Port) {
    Write-Host "idapro service already listening on 127.0.0.1:$Port"
    exit 0
}

# Resolve the IDA executable. Headless is the default (no GUI session needed);
# -Gui pulls in the GUI binary for interactive work.
# IDA 9.3 dropped the "64" suffix: ida.exe/idat.exe. On 9.0-9.2 they are
# ida64.exe/idat64.exe. We try new names first, then the old.
$exeNameNew = if ($Gui) { 'ida.exe' } else { 'idat.exe' }
$exeNameOld = if ($Gui) { 'ida64.exe' } else { 'idat64.exe' }
$candidates = @()
if (-not [string]::IsNullOrWhiteSpace($env:IDA_HOME)) {
    $candidates += Join-Path $env:IDA_HOME $exeNameNew
    $candidates += Join-Path $env:IDA_HOME $exeNameOld
}
foreach ($v in @('9.3', '9.4', '9.2', '9.1', '9.0')) {
    foreach ($n in @($exeNameNew, $exeNameOld)) {
        $candidates += Join-Path $env:ProgramFiles "IDA Professional $v\$n"
        $candidates += Join-Path $env:ProgramFiles "IDA Pro $v\$n"
    }
}

$exe = $null
foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) { $exe = $candidate; break }
}

if (-not $exe) {
    Write-Warning "IDA not found. Looked for $exeName under: $($candidates -join '; ')"
    Write-Warning "Set IDA_HOME to your IDA install directory, or install IDA Pro."
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Target)) {
    Write-Warning "No -Target supplied. IDA needs a target open before the MCP plugin starts listening on port $Port."
    Write-Warning "Re-run with: start-idapro.ps1 -Target <path-to-binary>"
    exit 1
}

if (-not (Test-Path -LiteralPath $Target)) {
    Write-Warning "Target does not exist: $Target"
    exit 1
}

Write-Host "Launching $exe on $Target (expect MCP on 127.0.0.1:$Port)"

if ($Gui) {
    Start-Process -FilePath $exe -ArgumentList @($Target) | Out-Null
} else {
    # -A autonomous (no dialogs), -c discard any stale database.
    Start-Process -FilePath $exe -ArgumentList @('-A', '-c', $Target) | Out-Null
}

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    if (Test-Port -P $Port) {
        Write-Host "idapro service is listening on 127.0.0.1:$Port"
        exit 0
    }
    Start-Sleep -Seconds 2
}

Write-Warning "IDA started but nothing is listening on 127.0.0.1:$Port after ${TimeoutSeconds}s."
Write-Warning "Open a target in IDA and check its Output window for the [MCP] port= line."
exit 2
