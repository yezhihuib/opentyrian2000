# Ordinary manual play. No Python wrapper, replay, forced input or time limit.
param(
    [Parameter(Mandatory = $true)][string]$DataDirectory,
    [string]$Executable,
    [string]$AssetsDirectory,
    [string]$StartupAssetsDirectory,
    [string]$ProfileDirectory,
    [ValidateSet('2x', '4x')][string]$InitialScale = '2x',
    [string]$MusicDirectory
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Executable) { $Executable = Join-Path $repoRoot 'opentyrian-x64-Release.exe' }
if (-not $AssetsDirectory) {
    . (Join-Path $PSScriptRoot 'current-craft267-pack.ps1')
    $AssetsDirectory = New-CurrentCraft267Pack $repoRoot 'preview'
}
if (-not $ProfileDirectory) {
    if (-not $env:LOCALAPPDATA) { throw 'Specify an absolute dedicated -ProfileDirectory.' }
    $ProfileDirectory = Join-Path $env:LOCALAPPDATA 'OpenTyrian2000-HD\manual-first-level'
}
function Resolve-ManualPath([string]$Path, [string]$Kind) {
    if (-not [IO.Path]::IsPathRooted($Path)) { throw "Use an absolute path: $Path" }
    if (-not (Test-Path -LiteralPath $Path -PathType $Kind)) { throw "Missing $Kind path: $Path" }
    return (Resolve-Path -LiteralPath $Path).ProviderPath
}
$Executable = Resolve-ManualPath $Executable 'Leaf'
$DataDirectory = Resolve-ManualPath $DataDirectory 'Container'
$AssetsDirectory = Resolve-ManualPath $AssetsDirectory 'Container'
if (-not (Test-Path -LiteralPath (Join-Path $DataDirectory 'tyrian1.lvl') -PathType Leaf)) {
    throw 'The data directory must contain your separately obtained complete Tyrian 2000 data.'
}
if ($StartupAssetsDirectory) { $StartupAssetsDirectory = Resolve-ManualPath $StartupAssetsDirectory 'Container' }
if ($PSBoundParameters.ContainsKey('MusicDirectory')) {
    if ([string]::IsNullOrWhiteSpace($MusicDirectory)) { throw 'Specify a nonempty absolute -MusicDirectory.' }
    # IsPathRooted alone accepts drive-relative C:music and root-relative \music.
    if ($MusicDirectory -notmatch '^(?:[A-Za-z]:[\\/]|[\\/]{2}[^\\/]+[\\/][^\\/]+(?:[\\/]|$))') {
        throw 'Use an absolute drive or UNC path for -MusicDirectory.'
    }
    $MusicDirectory = Resolve-ManualPath $MusicDirectory 'Container'
}
if (-not [IO.Path]::IsPathRooted($ProfileDirectory)) { throw 'Use an absolute dedicated -ProfileDirectory.' }
New-Item -ItemType Directory -Path $ProfileDirectory -Force | Out-Null
$ProfileDirectory = (Resolve-Path -LiteralPath $ProfileDirectory).ProviderPath
$marker = Join-Path $ProfileDirectory '.manual-hd-profile'
if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) {
    if (Get-ChildItem -LiteralPath $ProfileDirectory -Force | Select-Object -First 1) {
        throw 'This directory already contains files. Choose a new dedicated profile to preserve existing saves.'
    }
    [IO.File]::WriteAllText($marker, 'Dedicated OpenTyrian2000 manual first-level HD profile.')
}
$config = Join-Path $ProfileDirectory 'opentyrian.cfg'
if (-not (Test-Path -LiteralPath $config)) {
    $initialConfig = @"
section 'video'
    item 'fullscreen' '-1'
    item 'scaler' '$InitialScale'
    item 'scaling_mode' 'Integer'
"@
    [IO.File]::WriteAllText($config, $initialConfig, [Text.UTF8Encoding]::new($false))
}
# Start-Process joins ArgumentList; quote each whole argument for Windows argv.
function Quote-ManualArgument([string]$Value) {
    if ($Value -match '["\r\n]') { throw 'Paths cannot contain quotes or line breaks.' }
    $tail = $Value.Length - $Value.TrimEnd('\').Length
    return '"' + $Value + ('\' * $tail) + '"'
}
$arguments = @((Quote-ManualArgument "--data=$DataDirectory"), (Quote-ManualArgument "--manual-hd-assets=$AssetsDirectory"))
if ($StartupAssetsDirectory) { $arguments += Quote-ManualArgument "--startup-assets=$StartupAssetsDirectory" }
if ($MusicDirectory) { $arguments += Quote-ManualArgument "--music-dir=$MusicDirectory" }
Write-Host "Profile: $ProfileDirectory"
Write-Host 'Choose New Game and Episode 1 normally. HD is limited to its first level; other gameplay stays classic.'
$game = Start-Process -FilePath $Executable -ArgumentList $arguments -WorkingDirectory $ProfileDirectory -Wait -PassThru
if ($game.ExitCode -ne 0) { throw "Game exited with code $($game.ExitCode)." }
