# Isolated Windows build candidate

This source checkpoint now has a real MSVC x64 build of all 112 production-plus-
overlay translation units. It is **not a playable Windows package or gameplay
acceptance claim**. The game executable was not started.

The first native attempt stopped at the missing `TYRIAN_DIR` definition. The
staging generator now supplies the same `C:\TYRIAN` default as the canonical
Windows project; explicit runtime `--data` still takes precedence. A fresh
independent stage then built successfully with MSVC 14.44.35207, SDK 10.0.26100.0,
SDL2 2.32.10 and SDL2_net 2.4.0. All 448 staged inputs were unchanged after build,
and the output was verified as AMD64 PE (3,700,224 bytes). No old installation,
project, runtime resources or saved games were modified.

A separate native executable passed SHA256 known-vector and file-lifecycle /
non-overwriting publication assertions using system BCrypt. This small test is
not the game. Six focused portability/staging tests pass after the macro fix;
the preceding 68-test offline aggregate and 112-unit POSIX build also passed.
The ordinary launcher still rejects Windows execution; its safety check has not
been removed. DLL resolution, actual graphics, input, audio and save/load remain
unverified.

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

The successful native build still requires DLL-resolution checks and a new
isolated run/profile layout. Windows saves currently use the working directory,
while family terrain paths are relative, so simply removing the launcher guard
or changing the working directory is unsafe. Runtime art, original game data,
menu/input/audio, combined scenes, performance and save/reload must be checked
separately before claiming a playable release.

## Source encoding across Windows entry points

The generated 112-unit family project now uses `/source-charset:utf-8`, matching the ordinary 86-unit generator. The shared
font table contains UTF-8 comments: decoding as CP936 previously changed the
compiled table and correctly caused authenticated HD font admission to fail.
`CharacterSet` alone does not select source decoding. Execution-string encoding,
font data, renderer guards and source pins are not changed.

Generated-project XML checks cover the option and unchanged
source copies. They are not a new native compilation or window acceptance result.
Existing EXEs, prepared directories and build receipts remain untouched; rebuild
in a fresh stage to use the option.

The historical checked-in Visual Studio project is bound by the existing
production-validation receipt and is not modified by this patch. Use one of the
explicitly source-encoded isolated generators for new Windows builds; updating
that historical project requires a separately revalidated production binding.
