param(
    [ValidateSet('blue','type10','turret','custom')][string]$Preset = 'blue',
    [ValidateRange(1,5)][int]$Episode = 1,
    [ValidateRange(1,255)][int]$Level = 9,
    [ValidateRange(-1,5999)][int]$Tick = -1,
    [ValidateRange(0,65534)][int]$Event = 0,
    [ValidateRange(60,6000)][int]$Until = 6000,
    [switch]$Talon13,
    [switch]$Talon5,
    [switch]$BeforeGreenV2,
    [switch]$BeforeGreenTrail,
    [switch]$BeforeShield,
    [switch]$BeforeWhiteSmoke,
    [switch]$BeforeLargeGround,
    [switch]$BeforeImpact,
    [switch]$BeforeLargeAir,
    [switch]$BeforeSmallExplosion,
    [switch]$BeforeType10,
    [switch]$BeforeFoundation,
    [switch]$Headless,
    [switch]$Running,
    [switch]$Reference,
    [switch]$Capture,
    [ValidateRange(-1,5999)][int]$CaptureStart = -1,
    [ValidateRange(1,120)][int]$CaptureCount = 36,
    [switch]$WindowOnly,
    [switch]$ExplosionLog,
    [switch]$IndexOnly,
    [string]$Assets
)
$ErrorActionPreference = 'Stop'
function Get-DebugSha256([string]$Path) {
    $debugHasher = [Security.Cryptography.SHA256]::Create()
    $debugStream = [IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($debugHasher.ComputeHash($debugStream))).Replace('-','').ToLowerInvariant() }
    finally { $debugStream.Dispose(); $debugHasher.Dispose() }
}
if ($Tick -ge 0 -and $Event -gt 0) { throw 'Choose -Tick or -Event.' }
if (($CaptureStart -ge 0 -or $CaptureCount -ne 36 -or $WindowOnly) -and -not $Capture) { throw 'CaptureStart/CaptureCount/WindowOnly require -Capture.' }
if ($Talon13 -and $Talon5) { throw 'Choose -Talon5 for compatibility or keep the default13.' }
$debugRepoRoot = Split-Path -Parent $PSScriptRoot
$debugTaskRoot = Split-Path -Parent $debugRepoRoot
$debugExe = Join-Path $debugRepoRoot 'opentyrian-x64-Release.exe'
$debugData = Join-Path $debugTaskRoot 'runtime-data\tyrian2000'
$debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-test'
if ($BeforeGreenV2) { $debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v1-test' }
if ($BeforeGreenTrail) { $debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-death-effects-white-smoke-shield-v1-test' }
if ($BeforeShield) { $debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-death-effects-white-smoke-v1-test' }
if ($BeforeWhiteSmoke) { $debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-death-effects-v1-test' }
if ($BeforeLargeGround) { $debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-explosion-v2-large-air-v1-impact-v1-test' }
if ($BeforeImpact) { $debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-explosion-v2-large-air-v1-test' }
if ($BeforeLargeAir) { $debugAssets = Join-Path $debugRepoRoot 'assets\hd\packs\packed-blue-four-foundation-type10-explosion-v2-test' }
if ($BeforeSmallExplosion) { $debugAssets = Join-Path $debugTaskRoot 'runtime-hd-assets\packed-blue-four-foundation-type10-v9-test' }
if ($BeforeType10) { $debugAssets = Join-Path $debugTaskRoot 'runtime-hd-assets\packed-blue-four-foundation-v1-test' }
if ($BeforeFoundation) { $debugAssets = Join-Path $debugTaskRoot 'runtime-hd-assets\packed-blue-four-v4-test' }
if ($Assets) { $debugAssets = [IO.Path]::GetFullPath($Assets) }
foreach ($debugPath in @($debugExe,$debugData,$debugAssets)) { if (-not (Test-Path -LiteralPath $debugPath)) { throw "Existing dependency missing: $debugPath" } }
$debugSavedEnv = @{}
foreach ($debugKey in @('SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER')) { $debugSavedEnv[$debugKey] = [Environment]::GetEnvironmentVariable($debugKey,'Process') }
try {
    if ($Headless) { $env:SDL_VIDEODRIVER='dummy'; $env:SDL_AUDIODRIVER='dummy'; $env:SDL_RENDER_DRIVER='software' }
    do {
        $debugRun = Join-Path $debugTaskRoot ('controlled-runs\asset-debug-' + (Get-Date -Format 'yyyyMMdd-HHmmss-ffff'))
        New-Item -ItemType Directory -Path $debugRun -ErrorAction Stop | Out-Null
        $debugConfig = "section 'video'`n    item 'fullscreen' '-1'`n    item 'scaler' '4x'`n    item 'scaling_mode' 'Integer'`n"
        [IO.File]::WriteAllText((Join-Path $debugRun 'opentyrian.cfg'),$debugConfig,[Text.UTF8Encoding]::new($false))
        $debugControl = Join-Path $debugRun 'debug-control.txt'
        [IO.File]::WriteAllText($debugControl,'',[Text.UTF8Encoding]::new($false))
        $debugArgs = @("--data=$debugData",'--no-sound','--no-joystick','--no-xmas',"--asset-debug=$Preset", "--asset-debug-episode=$Episode", "--asset-debug-level=$Level", "--render-ticks=$Until", "--render-assets=$debugAssets", "--asset-debug-control=$debugControl",'--render-talon-bank=13')
        if ($Tick -ge 0) { $debugArgs += "--asset-debug-tick=$Tick" }
        if ($Event -gt 0) { $debugArgs += "--asset-debug-event=$Event" }
        if ($Talon5) { $debugArgs = @($debugArgs | Where-Object { $_ -notlike '--render-talon-bank=*' }); $debugArgs += '--render-talon-bank=5' }
        if ($Running) { $debugArgs += '--asset-debug-running' }
        if ($Reference) { $debugArgs += '--asset-debug-reference' }
        if ($Capture) { $debugArgs += '--asset-debug-capture'; $debugArgs += "--asset-debug-capture-count=$CaptureCount" }
        if ($CaptureStart -ge 0) { $debugArgs += "--asset-debug-capture-start=$CaptureStart" }
        if ($WindowOnly) { $debugArgs += '--asset-debug-window-only' }
        if ($ExplosionLog) { $debugArgs += '--asset-debug-explosion-log' }
        if ($IndexOnly) { $debugArgs += '--asset-debug-index-only' }
        $debugSources = @{}
        foreach ($debugSource in @('src/asset_debug.c','src/tyrian2.c','src/game_probe.c','src/render_mirror.c')) {
            $debugSources[$debugSource] = Get-DebugSha256 (Join-Path $debugRepoRoot $debugSource)
        }
        $debugMetadata = @{ argv = @($debugExe) + $debugArgs; exe_sha256 = (Get-DebugSha256 $debugExe); source_sha256 = $debugSources; launcher = 'start-asset-debug.ps1'; start_utc = [DateTime]::UtcNow.ToString('o') }
        [IO.File]::WriteAllText((Join-Path $debugRun 'asset-debug-run.json'),($debugMetadata | ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
        Write-Host "ASSET DEBUG run: $debugRun"
        Write-Host 'Space/P pause/resume; N single tick; R fresh replay; H hit; D destroy; Esc quit.'
        Write-Host "Optional control queue: $debugControl (pause,step,resume,hit SLOT,destroy SLOT,reload,quit)."
        $debugQuotedArgs = @($debugArgs | ForEach-Object { '"' + $_ + '"' })
        $debugStdout = Join-Path $debugRun 'launcher-game-stdout.log'
        $debugStderr = Join-Path $debugRun 'launcher-game-stderr.log'
        $debugProcess = Start-Process -FilePath $debugExe -ArgumentList $debugQuotedArgs -WorkingDirectory $debugRun -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput $debugStdout -RedirectStandardError $debugStderr
        $debugExit = $debugProcess.ExitCode
        $debugMetadata['exit_code'] = $debugExit
        $debugMetadata['end_utc'] = [DateTime]::UtcNow.ToString('o')
        [IO.File]::WriteAllText((Join-Path $debugRun 'asset-debug-run.json'),($debugMetadata | ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
        Get-Content -LiteralPath $debugStdout
        Get-Content -LiteralPath $debugStderr | Write-Host
    } while ($debugExit -eq 75)
    if ($debugExit -ne 0) { throw "Asset debug failed (exit $debugExit); inspect this isolated run." }
} finally {
    foreach ($debugKey in $debugSavedEnv.Keys) { [Environment]::SetEnvironmentVariable($debugKey,$debugSavedEnv[$debugKey],'Process') }
}
# This starts from the original level-data entry and deterministically replays.
# No build/download, save-state system, pointer teleport, push, or PR.
