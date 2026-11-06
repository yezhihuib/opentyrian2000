# Experimental level-2 family canvas

This opt-in batch combines the building 313–316 canvas, 24 terrain members,
selected 272 lamps, gray 325, normal-state longface 573–576, triple 275, and
the first 269 ember device. Unsupported identities or states retain native
rendering. It does not replace all second-level graphics.

## Build and runtime switches are separate

Install a C compiler, pkg-config, SDL2/SDL2_net development packages, and OpenSSL
development headers and libcrypto. Python 3 is needed for the build, launcher,
and package checks.

```sh
python3 scripts/build_level2_family.py
```

This separate build stages the canonical source together with the overlays in
`experimental/level2-family/src`, then produces `opentyrian2000-family` in the
repository root. The canonical `src`, `Makefile`, and Visual C++ project remain
unchanged. Normal builds do not include these experimental overlays.

Choosing the experimental build compiles family support; it does not activate
it at runtime. Do not manually mix ordinary and experimental object files.

The launcher defaults to a read-only plan and requires both `--launch` to start
the game and `--hd` to enable the family settings:

```sh
python3 scripts/launch_level2_family.py --data /path/to/your/game-data --check-only
python3 scripts/launch_level2_family.py --data /path/to/your/game-data --check-only --hd
python3 scripts/launch_level2_family.py --data /path/to/your/game-data --launch --hd
```

Omit `--hd` for native/default-off family rendering. `--dry-run` is an alias for
`--check-only`; omitting both mode options also only prints the plan. No check-only
operation executes the binary, creates a profile, or generates game reports.
Only the launcher-specific family support is toggled; this does not disable
unrelated rendering features already present elsewhere in the project.

The default executable is `opentyrian2000-family` in the repository root.
`--binary /path/to/executable` selects another build. The launcher verifies that
it exists and is executable, but cannot prove its compile options. Build with
the command above rather than selecting an unrelated executable.

## Data, saves, and environment

Original game data is not included. `--data` must explicitly name your existing
data directory. The launcher checks the directory exists, not that every game
file is valid or compatible. Native source guards decide whether an HD replacement
is applicable at runtime.

The default separate profile is `.level2-family-profile` in this repository;
saves/configuration live in its `config/opentyrian2000` subdirectory. Existing
system profiles are not imported. `--profile /path/to/separate-profile` selects
another profile explicitly. Profiles are created only on `--launch`. Back up
valuable profiles yourself before choosing them; this launcher does not migrate,
back up, or validate saved progress.

Inherited family, building, observer, and diagnostic trace controls are removed.
Only `--hd` supplies the fixed 23 family settings, including repository asset
directories and the three building phase paths. Ordinary display/audio environment
settings remain inherited. The game uses real input and its normal exit path,
with no replay, injected input, or launcher timeout.

Relative `--data`, `--binary`, and `--profile` arguments resolve from the caller's
working directory. Game execution always uses the repository root as CWD because
terrain paths are repository-relative. Enabled diagnostics can create or replace
`building313-family-*.json` reports and corresponding `.tmp` files there. These
reports are not bundled or uploaded by this launcher.

POSIX launch support is provided. Windows packaging is not tested, and this
launcher rejects Windows execution because the game's Windows profile handling
does not honor the isolated HOME/XDG settings.

## Asset identity and provenance

`assets/hd/level2-family-v1/MANIFEST.json` lists SHA-256 hashes for the exact 52
required assets: 11 new files and 41 byte-identical reused files. Both on and off
plans verify this complete set, including the four dormant damaged-longface files.
This checks package identity, not legal ownership or gameplay correctness.

- Building: three 384 × 448 ARGB32LE phase payloads, assembled from vector-authored
  components aligned to original-game landmarks. Disk byte order is B, G, R, A.
- Longface: eight HDR1 components from image-generated normal/damaged artwork,
  deterministically registered and clipped to the original silhouettes.
- Lamps, gray devices, triple lamps, and ember devices reuse existing HDR1 files
  in `assets/hd/packs/asteroid1-ten-v1`.
- Terrain reuses `assets/hd/current-terrain23` and `current-terrain24`.

The source also includes original-game pixel-index and palette references for
identity/ownership checks. These are distinct from the authored HD RGB material.
The manifest records shipped bytes and authoring provenance; it is not a claim
that all upstream art-generation inputs are included.

## Verification and limits

Run the package/launcher tests without starting a game:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_level2_family_release.py
```

These tests verify the manifest, fixed runtime settings, default-off isolation,
profile selection, and check-only behavior from another working directory. They
never run gameplay or malformed-asset tests.

The portable build compiled all 112 translation units from staged source and
three staged generated headers. One 1,320-frame controlled SDL software replay
of those rebuilt objects matched the previously accepted enabled scene: selected
state/RNG, native source/output/palette hashes, and presentation outcomes matched
on every frame; 898 frames presented HD. All 153 raw capture files and four
state/presentation/event streams matched byte-for-byte. The observation harness
was linked separately and is not shipped in the ordinary executable.

The eight package/launcher/builder checks passed. Canonical production validation
and source binding both passed for the unchanged 339-file production tree. The
full legacy package dry run did **not** pass in this environment: projectile61
regeneration differs from its stored asset. The same mismatch was independently
reproduced on the unchanged public baseline; this batch does not alter that asset
or relax its check. Do not describe this as a fully rebuilt legacy runtime pack.

Damaged longface rendering is explicitly rejected before a tile write; all eight
assets remain available for package preflight, but only the four normal-state
components are eligible. Damaged gameplay appearance is unverified. Terrain
retirement's final support exclusion, triple effects, and some lamp/ember shadow
or blend cases also remain unverified. This package does not claim ordinary menu
navigation, save/reload, GPU rendering, Windows packaging, performance, or the
entire second level has been validated.
