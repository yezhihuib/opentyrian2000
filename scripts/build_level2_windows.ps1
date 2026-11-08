# Isolated staged project only. No installer, game, DLL-copy or old-repo writes.
param(
    [switch]$Build,
    [string]$MSBuild = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe',
    [string]$Compiler = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe',
    [string]$VCToolsVersion = '14.44.35207'
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
function FileHash([string]$p) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "Missing input: $p" }
    return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
}
function FileEntry([string]$p) {
    return @{ path=$p; sha256=(FileHash $p); bytes=(Get-Item -LiteralPath $p).Length }
}
$receiptPath = Join-Path $root 'STAGE.json'
$receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
if ($receipt.schema -ne 1 -or $receipt.status -ne 'STAGED_NOT_BUILT' -or $receipt.translation_units -ne 112) { throw 'Unrecognized stage receipt.' }
# No command lines from the receipt are evaluated. Only checked data paths.
foreach ($entry in $receipt.inputs_sha256.PSObject.Properties) {
    $relative = $entry.Name
    if ([IO.Path]::IsPathRooted($relative) -or $relative -match '(?:^|[\\/])\.\.(?:[\\/]|$)') { throw 'Stage contains an outside path.' }
    if ((FileHash (Join-Path $root $relative)) -ne $entry.Value) { throw "Changed staged input: $relative" }
}
if ($receipt.sdk -ne '10.0.26100.0' -or $receipt.toolset -ne 'v143' -or $VCToolsVersion -ne '14.44.35207') { throw 'Toolchain differs from the reviewed inventory; prepare a new reviewed stage.' }
$dependencies = @{}
foreach ($pair in @(@('SDL2',$receipt.dependencies.SDL2,'SDL.h','SDL2.lib'),@('SDL2_net',$receipt.dependencies.SDL2_net,'SDL_net.h','SDL2_net.lib'))) {
    $name=$pair[0];$depRoot=[string]$pair[1]
    if (-not [IO.Path]::IsPathRooted($depRoot)) { throw 'Dependency root must be absolute.' }
    $dependencies[$name] = @{
        header=(FileEntry (Join-Path $depRoot ('include\'+$pair[2])))
        import_library=(FileEntry (Join-Path $depRoot ('lib\x64\'+$pair[3])))
    }
    $dll = Join-Path $depRoot ('lib\x64\'+$name+'.dll')
    if (Test-Path -LiteralPath $dll -PathType Leaf) { $dependencies[$name]['runtime_dll_inventory'] = FileEntry $dll }
}
$dependencies['SDL2main'] = FileEntry (Join-Path $receipt.dependencies.SDL2 'lib\x64\SDL2main.lib')
$installation=$MSBuild
for ($i=0;$i -lt 4;$i++) { $installation=Split-Path -Parent $installation }
$expectedCompiler=Join-Path $installation ("VC\Tools\MSVC\"+$VCToolsVersion+"\bin\Hostx64\x64\cl.exe")
$actualCompiler=(Resolve-Path -LiteralPath $Compiler).ProviderPath
if (-not [string]::Equals($actualCompiler,(Resolve-Path -LiteralPath $expectedCompiler).ProviderPath,[StringComparison]::OrdinalIgnoreCase)) { throw 'Compiler must match the checked MSBuild installation and VCToolsVersion.' }
$compilerDirectory=Split-Path -Parent $actualCompiler
$tools=@{msbuild=(FileEntry $MSBuild);compiler=(FileEntry $actualCompiler);compiler_binding='Explicit CLToolPath/CLToolExe';vc_tools_version=$VCToolsVersion;sdk=$receipt.sdk}
foreach ($name in @('CL','_CL_','LINK','_LINK_')) {
    if ([Environment]::GetEnvironmentVariable($name,'Process')) { throw "Unexpected compiler/linker environment override: $name. Use a clean build shell." }
}
$project=Join-Path $root 'level2-family.vcxproj'
$arguments=@($project,'/t:Build','/p:Configuration=Release','/p:Platform=x64','/p:PlatformToolset=v143',"/p:VCToolsVersion=$VCToolsVersion",'/p:PreferredToolArchitecture=x64',"/p:CLToolPath=$compilerDirectory\",'/p:CLToolExe=cl.exe','/p:ImportDirectoryBuildProps=false','/p:ImportDirectoryBuildTargets=false','/noAutoResponse','/v:minimal','/nologo')
$plan=@{schema=1;status='CHECK_ONLY';stage_sha256=(FileHash $receiptPath);source_digest=$receipt.source_digest;tools=$tools;dependencies=$dependencies;argv=$arguments;build_started=$false;game_started=$false;runtime_acceptance=$false}
if (-not $Build) { $plan | ConvertTo-Json -Depth 12; return }
foreach ($name in @('bin','obj','BUILD-WINDOWS.json','build.stdout.log')) {
    if (Test-Path -LiteralPath (Join-Path $root $name)) { throw "Existing build output: $name. Use a fresh stage; nothing will be overwritten." }
}
$plan.status='BUILDING';$plan.build_started=$true;$plan.started_utc=[DateTime]::UtcNow.ToString('o')
# Invoke the checked MSBuild directly. Never invoke the old solution/CopyPropsTemplates.
$previousErrorAction=$ErrorActionPreference
try {
    $ErrorActionPreference='Continue'
    & $MSBuild @arguments 2>&1 | Tee-Object -FilePath (Join-Path $root 'build.stdout.log')
    $code=$LASTEXITCODE
} finally { $ErrorActionPreference=$previousErrorAction }
$plan.msbuild_exit_code=$code
$plan.inputs_unchanged_after_build=$false
try {
    foreach ($entry in $receipt.inputs_sha256.PSObject.Properties) {
        if ((FileHash (Join-Path $root $entry.Name)) -ne $entry.Value) { throw "Staged input changed during build: $($entry.Name)" }
    }
    $plan.inputs_unchanged_after_build=$true
    $exe=Join-Path $root 'bin\opentyrian2000-level2.exe'
    if ($code -eq 0) {
        $plan.binary=FileEntry $exe
        $raw=[IO.File]::ReadAllBytes($exe)
        if ($raw.Length -lt 64 -or $raw[0] -ne 77 -or $raw[1] -ne 90) { throw 'Output is not PE.' }
        $pe=[BitConverter]::ToInt32($raw,60)
        if ($pe -lt 0 -or $pe+6 -gt $raw.Length -or [BitConverter]::ToUInt32($raw,$pe) -ne 17744 -or [BitConverter]::ToUInt16($raw,$pe+4) -ne 34404) { throw 'Output is not PE x64.' }
        $plan.pe_machine='AMD64'
    }
} catch {
    $plan.validation_error=$_.Exception.Message
    $code=3
}
$plan.exit_code=$code;$plan.ended_utc=[DateTime]::UtcNow.ToString('o')
$plan.status=if ($code -eq 0) { 'BUILT_NOT_RUN' } else { 'BUILD_FAILED' }
$plan | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $root 'BUILD-WINDOWS.json') -Encoding UTF8
if ($code -ne 0) { throw "Build or output validation failed with exit $code. See isolated log/receipt; no runtime was started." }
Write-Host 'Built isolated x64 candidate. No game launched; DLL resolution and runtime acceptance remain pending.'
