# Isolated Windows build candidate

This source checkpoint adds a portability header for four experimental overlay
units, an isolated MSVC staging/build workflow and offline tests. It is **not a
verified Windows build or playable Windows package**. The Windows build could
not be attempted because the available Windows computer went offline before
source transfer. No game, graphics or save/load acceptance was performed.

The 68-test offline aggregate and complete 112-unit POSIX build pass. The three
staging tests were repeated after the final script-only fixes. These results do
not prove MSVC compatibility or Windows runtime behavior. The ordinary launcher
continues to reject Windows execution; its safety check has not been removed.

## Separate source stage

Use existing x64 SDL2 and SDL2_net development dependencies and an installed
Visual Studio Build Tools toolchain. No dependency is downloaded or installed.
The current reviewed staging settings are SDK 10.0.26100.0, v143 and MSVC
14.44.35207. Change and revalidate these settings for another toolchain.

```sh
python scripts/stage_level2_windows.py --repo /path/to/checkout \
  --output /path/to/new-external-windows-stage \
  --sdl2 'C:\Dependencies\SDL2-2.32.10' \
  --sdl-net 'C:\Dependencies\SDL2_net-2.4.0'
```

The output must be new and outside the checkout. It contains the exact 112-unit
production-plus-overlay merge, three generated asset headers and its own MSVC
project, with copied-input hashes in `STAGE.json`. It does not use or modify the
old Visual Studio project, installation, runtime resources or saved games.

On Windows, run the generated `build_level2_windows.ps1` without arguments to
check inputs and print the plan. Only `-Build` invokes MSBuild. Do not bypass
execution policy or access approvals. Existing bin/obj/log outputs are rejected;
use a new stage for a later attempt rather than overwriting an earlier one.

The build driver records staged-input, tool, selected dependency and resulting
EXE hashes, and requires PE x64 output. Post-build validation errors produce a
failure receipt. Compiler identity is explicitly selected; official Microsoft
C++ toolchain imports remain necessary and are not claimed hermetic.
Directory.Build.props/targets, automatic response files and known CL/LINK command
environment overrides are disabled or rejected.

## Preserved integrity and remaining work

Windows SHA256 uses system BCrypt; POSIX retains OpenSSL. File identity/length
checks remain fail-closed. Observational report publication remains exclusive
and non-overwriting, using a hard link after flushing and synchronizing the
completed temporary file. Unsupported file systems fail rather than falling
back to a replacing copy. No security settings or existing ACLs are changed.

A successful future build will still require DLL-resolution checks and a new
isolated run/profile layout. Windows saves currently use the working directory,
while family terrain paths are relative, so simply removing the launcher guard
or changing the working directory is unsafe. Runtime art, original game data,
menu/input/audio, combined scenes, performance and save/reload must be checked
separately before claiming a playable release.
