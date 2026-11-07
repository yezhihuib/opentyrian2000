# Experimental late-level source candidate

This is an isolated **source-only, default-off candidate**, not a validated
late-level gameplay release. It includes the cumulative family renderer and
lineage/continuity integration for later actors, normal linked 338–342,
normal turret 273, tall structures and launcher 271/child 463, together with
the production source needed to compile it. Unsupported identities/states
must continue through native rendering.

No runtime art, original game-data files, saved profiles, captured frames,
private reports, prebuilt objects, binaries, system headers or libraries are
included. No activation launcher is supplied. Existing production files and
the earlier `level2-family` build/launcher are not replaced or reconfigured.
This candidate does not claim complete second-level replacement coverage.

## Portable build

Use Python 3.9 or newer, a POSIX C99 compiler, pkg-config, SDL2 and SDL2_net
development packages, and OpenSSL development headers/libcrypto. For example,
the corresponding Debian/Ubuntu package names are `build-essential`,
`pkg-config`, `libsdl2-dev`, `libsdl2-net-dev` and `libssl-dev`.

From the repository root:

```sh
python3 experimental/late-level/build.py --check-only
python3 experimental/late-level/build.py --jobs 2
PYTHONDONTWRITEBYTECODE=1 python3 experimental/late-level/test_release.py -v
```

The output is `experimental/late-level/build/opentyrian2000-late-level`.
The builder compiles **all 112 production translation units** from the 475
shipped C/header/include files, then links once. It never executes the game.
`opentyr.c` supplies the ordinary `main`; there is no renamed-main define,
entry shim, observation harness, or reused object in the executable.

Every build requires a new output directory. To rebuild without overwriting
an earlier attempt, pass `--build-dir /path/to/new-output`. `CC`, `PKG_CONFIG`,
`CPPFLAGS`, `CFLAGS` and `LDFLAGS` are supported. Standard pkg-config environment
variables can select an external development sysroot; its files are not part
of this package. Build receipts and compiler diagnostics stay in that output
directory. The check-only command resolves dependencies and verifies source
hashes without writing or compiling.

The complete build was validated on Linux using an external SDL development
sysroot and system libcrypto. It produced 413 compiler warnings, not a
warning-clean build. This establishes source/dependency closure and linking,
not cross-platform runtime correctness. No byte-identical binary promise is
made across compilers, dependencies or build flags.

## Source and header identity

`SOURCE.json` records every shipped source SHA-256, per-unit compile definitions,
ordered include directories, and the expected local dependency set. Thirteen
normalized source sets preserve header variants. Three header basenames have
nine distinct content versions; flattening these sets would be incorrect.
The builder compares each compiler-generated dependency list with the pinned
per-unit selection and fails on a mismatch. System dependencies come from
pkg-config and are deliberately not bundled.

The public-scope changes are small and explicit:

- Two machine-specific terrain file locations become repository-relative
  `assets/hd/current-terrain23` and `assets/hd/current-terrain24` locations.
- The normal production entry point replaces the renamed-main/shim build.
- Damaged longface 573–576 is rejected before canvas acquisition or tile writes,
  retaining the earlier public release's normal-only boundary.
- Package-local Git attributes preserve source bytes with automatic newline
  conversion enabled. Build outputs are ignored locally.

Upstream license notices and native source-reference tables remain intact.
Those tables are source-side identity checks, not a distributable game-data
installation. `COPYING` contains the GPL license; individual third-party source
notices continue to apply.

## Runtime dependencies and default-off boundary

Compiling family support does not enable it. New family switches still require
exact `1` values and their existing prerequisites. The builder does not set any
runtime switches. Inherited environment settings are not sanitized by the
executable, so this package supplies no run or enable command.

Running the executable would still require a separately obtained, compatible
original game-data installation. The build's fallback data location is the
relative `data` directory. Optional HD rendering additionally requires matching
authored asset bytes, roots and configuration not supplied by this candidate.
Source contracts name these inputs, including the `*_ASSET_DIR` family settings,
`PERSISTENT_HUD_ASSET_DIR`, and repository-relative terrain assets. Existing
public assets are not claimed to satisfy every new family's requirements.
Diagnostic controls may create runtime reports if explicitly enabled elsewhere.
The source-only build must not be treated as an enabling or asset-install step.

Damaged longface art is not promoted. The 18 final-scene art backlog items are
not included and do not count as delivered or renderer-qualified coverage.
Launcher 271 shared-body phase identity is also not accepted.

## Verification boundary

The release tests check source hashes, all 112 real units, unflattened headers,
absence of machine paths/system files/runtime art, package isolation, the
normal main, and the damaged-longface early rejection. They also compile and
execute isolated switch predicates for 18 controls against missing, zero,
invalid, exact-1, and missing-prerequisite values. These tiny tests do not link
the game or read assets. They retain their output under `.test-build` (or the
`LATE_LEVEL_TEST_OUTPUT` directory).

No new gameplay, replay, screenshot comparison, malformed-asset decode, save
operation or real-scene acceptance was performed for this release. Prior
real-scene evidence reached **2,052 frames / curLoc 1,959**, ending in natural
death. **curLoc 4,920, 6,264 and 7,482 were never accepted.** Real lineage,
blit/writer/canvas/SDL integration, clipping, later interactions, art alignment
and runtime performance remain unverified for these late groups. Build and
switch checks do not resolve those gaps.
