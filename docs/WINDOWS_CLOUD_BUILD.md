# Cloud Windows x64 engine build

`scripts/build_level2_mingw.py` is an isolated cross-compilation route for the
optional level-2 engine. It is separate from the existing MSVC staging workflow.
It builds the real engine, not a simulation or a Linux binary renamed to `.exe`.
Compilation is not Windows runtime, GPU, fullscreen, audio or input acceptance.

## Inputs

Supply an existing x86_64-w64-mingw32 GCC toolchain and a cross-built SDL prefix:

- SDL 2.32.4, upstream commit `2359383fc187386204c3bb22de89655a494cd128`.
- SDL_net 2.2.0, upstream commit `669e75b84632e2c6cc5c65974ec9e28052cb7a4e`.
- The prefix must contain SDL2 headers, import libraries, SDL2main, SDL2.dll,
  and SDL2_net.dll. Both DLLs must be PE32+ AMD64.
- The tested cloud toolchain is GCC 14.2.0, MinGW-w64 12.0.0, and binutils 2.44
  from Debian trixie packages. Package downloads were checked against SHA256s in
  the signed Debian archive index and extracted only into an isolated directory.
- SDL and SDL_net were built without source modifications using their configure
  scripts with `--host=x86_64-w64-mingw32 --disable-static --enable-shared`.

This builder does not download or install dependencies, use a user's computer,
run a game, copy original game data, or modify an existing output directory.

## Invocation

From a frozen checkout, with the toolchain's bin directory on PATH:

```sh
python3 scripts/build_level2_mingw.py \
  --output /path/outside/checkout/new-windows-stage \
  --sdl-prefix /path/to/windows-sdl-prefix \
  --cc x86_64-w64-mingw32-gcc-posix \
  --jobs 8 --check-only
```

Omit `--check-only` to compile. The output directory must not already exist.
`--cc`, `--windres`, and `--objdump` can each name an explicit local executable.
No shell fragments are accepted as compiler arguments. The builder supplies
its own flags rather than inheriting ambient `CFLAGS`, `CPPFLAGS` or `LDFLAGS`.

The builder snapshots 112 production-plus-overlay translation units and all
local C headers/includes, three generated asset headers, the icon/resource,
and both relevant build scripts. It records hashes before compilation and
checks both staged and checkout inputs again afterward. It also verifies the
SDL input files did not change. A changed input invalidates the result.

The Windows data-text resource loader uses `_WIN32`, not `_MSC_VER`, to select
Windows `_stat` / `_fstat` APIs. This lets both MSVC and MinGW use the existing
Windows path without weakening the POSIX nonblocking regular-file checks.

## Outputs and interpretation

The new directory contains:

- `bin/opentyrian2000-level2.exe`, `bin/SDL2.dll`, `bin/SDL2_net.dll`.
- `BUILD-MINGW.json`, including source/repository identity, per-input and output
  hashes, tool identity, full compiler/link commands, and import inventories.
- Compilation/link logs, PE inspection reports, and the snapshotted source.

A successful receipt says `BUILT_NOT_RUN`, `game_started: false`, and leaves
native Windows and physical GPU acceptance false. The builder validates PE32+
AMD64 and rejects imports not supplied alongside the executable or in its
explicit Windows-system DLL allowlist. Windows BCrypt supplies SHA256, with
no OpenSSL runtime requirement. Static libgcc avoids a separate libgcc DLL.
The inspected tested outputs do not require libwinpthread.

`repository_revision` alone does not identify uncommitted work. For development
builds, inspect `repository_dirty`, `repository_status` and `input_sha256`.
A distributable package should use a clean frozen source revision matching all
recorded inputs, and include the corresponding source and licensing notices.

For the first cloud build, Wine 10 failed during initialization even for an
unrelated minimal Windows executable, before the game was started. This is an
unavailable cloud-runtime check, not an engine failure or a Windows pass.
Linux SDL software tests and later Windows desktop tests must be labeled
separately.

## Distribution notices

The engine is GPL-2.0-or-later; preserve `COPYING` and provide the corresponding
source and build scripts. SDL2 and SDL2_net use the zlib license; preserve their
upstream notices. Include MinGW-w64 runtime copyright/license notices and GCC
runtime license/exception notices for linked runtime code. Do not distribute
the compiler or Wine as game runtime dependencies. Do not include original
game data, user profiles/saves, private screenshots or private test fixtures.

## Focused checks

```sh
python3 -m unittest discover -s tests -p 'test_level2_mingw.py' -v
python3 -m unittest discover -s tests -p 'test_windows_data_dir_macro.py' -v
python3 -m unittest discover -s tests -p 'test_data_text_*.py' -v
```

These focused checks validate source selection, staging/PE guards, and affected
resource behavior. They are not a complete engine regression or runtime pass.
