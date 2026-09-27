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

# The MCP plugin publishes mcp/instances/instance_<port>.json. When IDA exits
# uncleanly (kill, crash, task manager) that file survives and keeps claiming the
# port. A later run then waits out the full timeout with "nothing listening" even
# though IDA is fine — the stale claim is the actual blocker. Reap the ones whose
# PID is gone before asking whether the port is up.
function Clear-StaleInstanceFiles([int]$P) {
    $dir = Join-Path $env:APPDATA 'Hex-Rays/IDA Pro/mcp/instances'
    if (-not (Test-Path -LiteralPath $dir)) { return }
    foreach ($f in Get-ChildItem -LiteralPath $dir -Filter 'instance_*.json' -ErrorAction SilentlyContinue) {
        $claimed = $null
        try { $claimed = (Get-Content -LiteralPath $f.FullName -Raw | ConvertFrom-Json).pid } catch { }
        $alive = $false
        if ($claimed) {
            $alive = [bool](Get-Process -Id $claimed -ErrorAction SilentlyContinue)
        }
        if (-not $alive) {
            Remove-Item -LiteralPath $f.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "Reaped stale MCP instance claim: $($f.Name) (pid $claimed is gone)"
        }
    }
}

Clear-StaleInstanceFiles -P $Port

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

if (-not $Gui) {
    # The MCP plugin starts its HTTP server only under the Qt GUI (is_idaq());
    # in idalib/headless mode it stays loaded but never binds a port. Saying so
    # up front beats waiting $TimeoutSeconds for something that cannot happen.
    Write-Warning "Headless idat.exe loads the plugin but does not open a port (plugin starts its server only in GUI mode). Use -Gui for an MCP endpoint, or idapro.open_database() for headless scripting."
}

# -c discards the packed database when the target already has one, and -A keeps
# IDA autonomous. Both modes need them: with only -A, the GUI still pops
# "database already exists / not closed properly" modal dialogs, and an
# unattended run then blocks forever on a dialog no one clicks.
if ($Gui) {
    Start-Process -FilePath $exe -ArgumentList @('-A', '-c', $Target) | Out-Null
} else {
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
