$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$dependencyRoot = Join-Path (Split-Path -Parent $repoRoot) 'project-deps'
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$installation = & $vswhere -latest -products '*' -requires Microsoft.Component.MSBuild Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $installation) { throw 'Visual Studio Build Tools is required; no software is installed by this script.' }
$msbuild = Join-Path $installation 'MSBuild\Current\Bin\MSBuild.exe'
& $msbuild (Join-Path $repoRoot 'visualc\opentyrian.sln') /t:Build /p:Configuration=Release /p:Platform=x64 /p:PlatformToolset=v143 /p:PreferredToolArchitecture=x64 "/p:SDL2BaseDir=$dependencyRoot\SDL2-2.32.10" "/p:SDL2netBaseDir=$dependencyRoot\SDL2_net-2.4.0" /v:minimal /nologo
if ($LASTEXITCODE -ne 0) { throw "Game build failed (exit $LASTEXITCODE)" }
