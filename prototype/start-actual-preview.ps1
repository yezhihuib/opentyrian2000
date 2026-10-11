param(
    [ValidateRange(60,6000)][int]$Ticks = 600,
    [switch]$Headless,
    [switch]$Before101,
    [switch]$TurretV2,
    [switch]$TurretV4,
    [switch]$BeforeRoad,
    [switch]$Window4x,
    [switch]$Talon13,
    [switch]$Talon5,
    [switch]$BeforeShield,
    [switch]$BeforeWhiteSmoke,
    [switch]$BeforeLargeGround,
    [switch]$BeforeImpact,
    [switch]$BeforeLargeAir,
    [switch]$BeforeSmallExplosion,
    [switch]$BeforeType10,
    [switch]$BeforeFoundation
)
$ErrorActionPreference = 'Stop'
$previewRepoRoot = Split-Path -Parent $PSScriptRoot
$previewTaskRoot = Split-Path -Parent $previewRepoRoot
$previewPython = 'C:\Program Files\Python311\python.exe'
$previewAssets = Join-Path $previewRepoRoot 'assets\hd\packs\packed-talon13-foundation-type10-death-effects-white-smoke-shield-v1-test'
if ($BeforeShield) { $previewAssets = Join-Path $previewRepoRoot 'assets\hd\packs\packed-talon13-foundation-type10-death-effects-white-smoke-v1-test' }
if ($BeforeWhiteSmoke) { $previewAssets = Join-Path $previewRepoRoot 'assets\hd\packs\packed-talon13-foundation-type10-death-effects-v1-test' }
if ($BeforeLargeGround) { $previewAssets = Join-Path $previewRepoRoot 'assets\hd\packs\packed-talon13-foundation-type10-explosion-v2-large-air-v1-impact-v1-test' }
if ($BeforeImpact) { $previewAssets = Join-Path $previewRepoRoot 'assets\hd\packs\packed-talon13-foundation-type10-explosion-v2-large-air-v1-test' }
if ($BeforeLargeAir) { $previewAssets = Join-Path $previewRepoRoot 'assets\hd\packs\packed-talon13-foundation-type10-explosion-v2-test' }
if ($BeforeSmallExplosion) { $previewAssets = Join-Path $previewTaskRoot 'runtime-hd-assets\packed-talon13-foundation-type10-v9-test' }
if ($BeforeType10) { $previewAssets = Join-Path $previewTaskRoot 'runtime-hd-assets\packed-talon13-foundation-v1-test' }
if ($BeforeFoundation) { $previewAssets = Join-Path $previewTaskRoot 'runtime-hd-assets\packed-talon13-test' }
if ($Talon13 -and $Talon5) { throw 'Choose -Talon5 for compatibility or keep the default13.' }
if ($BeforeRoad) { $previewAssets = Join-Path $previewTaskRoot 'runtime-hd-assets\packed-transition-turret-v7-test' }
if ($TurretV4) { $previewAssets = Join-Path $previewTaskRoot 'runtime-hd-assets\packed-transition-turret-v4-test' }
if ($TurretV2) { $previewAssets = Join-Path $previewTaskRoot 'runtime-hd-assets\packed-transition-37-57-test' }
if ($Before101) { $previewAssets = Join-Path $previewTaskRoot 'runtime-hd-assets\packed-scene-v2-test' }
if ($Talon13) {
    if ($Before101 -or $TurretV2 -or $TurretV4 -or $BeforeRoad) { throw 'Talon13 uses the accepted road49/50v4 asset set.' }
}
foreach ($previewPath in @($previewPython, (Join-Path $previewRepoRoot 'opentyrian-x64-Release.exe'), $previewAssets, (Join-Path $previewTaskRoot 'runtime-data\tyrian2000'))) {
    if (-not (Test-Path -LiteralPath $previewPath)) { throw "Existing local preview dependency missing: $previewPath" }
}
$previewPrefix = 'morning-preview-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
if ($Window4x) {
    $previewRun = Join-Path $previewTaskRoot ('controlled-runs\' + $previewPrefix + '-local')
    New-Item -ItemType Directory -Path $previewRun -ErrorAction Stop | Out-Null
    $previewConfig = @"
section 'video'
    item 'fullscreen' '-1'
    item 'scaler' '4x'
    item 'scaling_mode' 'Integer'
"@
    [IO.File]::WriteAllText((Join-Path $previewRun 'opentyrian.cfg'), $previewConfig, [Text.UTF8Encoding]::new($false))
}
$previewArguments = @((Join-Path $PSScriptRoot 'run-controlled.py'), '--modes', 'local', '--ticks', "$Ticks", '--scene', 'banking', '--assets', $previewAssets, '--local-blend', '--scene-assets', 'all', '--known-explosion-blend', '--allow-natural-end', '--prefix', $previewPrefix)
if (-not $Headless) { $previewArguments += '--native-window' }
$previewArguments += @('--talon-bank', $(if ($Talon5) { '5' } else { '13' }))
Push-Location $previewRepoRoot
try {
    & $previewPython @previewArguments
    if ($LASTEXITCODE -ne 0) { throw "Preview failed (exit $LASTEXITCODE); inspect its isolated controlled-runs logs." }
} finally { Pop-Location }
# Bounded scripted playback; creates its own run/config directory and closes.
# Does not build, download, push, change gameplay or provide manual-input QA.
