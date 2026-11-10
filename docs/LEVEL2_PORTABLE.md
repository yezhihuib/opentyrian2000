# Frozen portable level-2 Windows preview

The portable artifact is assembled in the cloud from a clean frozen commit and
an exact caller-pinned `BUILD-MINGW.json` receipt. It is not the historical
Python/PowerShell staging workflow. End users verify the ZIP source and SHA256,
fully extract it into a fresh empty writable directory on a local disk, then
double click `Start-Level2-Preview.exe`. The extraction directory must be outside
the original-data tree, and neither directory may contain the other. Do not
overlay an existing directory or use a network share/mapped network drive.
The engine and adjacent SDL DLLs are under
`bin/`; the native launcher supplies normal controls, a fresh session and the
supported `--level2-preview=asteroid2-v1` mode. Default scale is 4x; `--scale=2`
is the only alternate scale, also available by double-clicking `Start-2x.cmd`.
That small convenience script calls the same native launcher and makes no
security or PowerShell policy changes. No native Windows/GPU/input acceptance is implied.

The launcher's allowlists govern the files it selects and copies. They do not
prove that an unlisted DLL can never load: Windows resolves bootstrap imports
before launcher entry and its file checks. Verify the distributed ZIP hash,
extract into a fresh empty directory and do not add unrelated DLLs to it.

## Assemble explicitly

Run `scripts/build_level2_mingw.py` from the frozen, clean source first, as
described in `WINDOWS_CLOUD_BUILD.md`. Record its receipt SHA256 independently.
`DEPENDENCIES.json` and `runtime-licenses/` must be the reviewed dependency
provenance and notices, with the former also pinned by the caller. For example:

```sh
python3 scripts/package_level2_portable.py \
  --repo /path/to/frozen/checkout \
  --build-dir /path/to/fresh-engine-build \
  --build-sha256 <BUILD-MINGW.json-sha256> \
  --source-revision <full-40-character-commit> \
  --dependencies /path/to/reviewed-dependency-records \
  --dependencies-sha256 <DEPENDENCIES.json-sha256> \
  --output /path/outside/inputs/new-portable-directory \
  --zip /path/outside/inputs/new-portable.zip --check-only
```

The default and `--check-only` perform only reads and validation. They never
compile, write a generated header, create output, launch, download, delete,
change security settings, or touch original game data. Replace `--check-only`
with `--assemble` to create the two fresh outputs and compile the native
launcher with the compiler identity recorded by the engine build. The
compiler toolchain bin directory must be on PATH. Existing destinations,
source/output overlap, traversal and symlink/reparse components are rejected.
On failure, a partial new output is left for inspection, never automatically
deleted or overwritten. Choose another fresh path for a later attempt.

## Evidence and allowlists

The packager verifies the clean revision, each build input against that commit,
source/build-input digests, receipt identity, game/DLL byte identities, AMD64
PE32+ executable versus DLL roles and imported DLL closure. It verifies all
103 fixed public assets in `scripts/HD-ASSET-PINS.json`, plus the separately
approved `gameplay-hud-v1.hda` (4,160,064 bytes). The manifest identities are
hard-pinned. No private redvent, clip extension or new artwork is selected.

The 53 reviewed settings in `packaging/level2-preview-controls.json` must agree
exactly with `launch_level2_family.build_plan` using `--hd --public-candidates
--terrain-fallback --player-fallback --tank-fallback --static-hud`. The stale
23-setting family subset is not used. No probe, debug, scripted-input or
invulnerable-player controls are added.

`packaging/level2-original-data-hashes.json` pins 74 flat original resource
files verified against the stated upstream Tyrian 2000 ZIP. It contains only
names, lengths and hashes. The selected suffixes are `.shp`, `.lvl`, `.dat`,
`.cdt`, `.hdt`, `.snd`, `.mus`, `.pic` and `.anm`. This intentionally preserves
the known original data set rather than claiming an untested minimal subset.
Files such as `user1.shp` are accepted only with their exact upstream bytes,
not arbitrary user files. Saves, configurations, EXEs, demos and extras are
excluded. Original data is never read by the packager or put in the ZIP. The
launcher copies only this whitelist into each fresh local session after the
user selects an existing data folder.

## Reproduction and licensing

`source/` contains the effective C/header/include inputs in their repository
paths, replaced base sources needed by the overlay build, resource/icon,
generated asset headers, build scripts, native launcher, reviewed manifests,
and the exact generated launcher header. Source/build identities and DLL
provenance are in `metadata/`. The engine is GPL-2.0-or-later; preserve the
corresponding source and `COPYING`. SDL2 and SDL2_net upstream revisions,
configure options, signed-registry package versions/hashes and zlib notices
are recorded. MinGW/GCC runtime notices and font notices are also included.

To rebuild the engine from the extracted source, supply the same dependencies
to `source/scripts/build_level2_mingw.py`. There is no `.git` directory in the
ZIP, so its receipt has no source commit until you restore a checkout at the
recorded revision. The source bytes and SHA256 maps remain independently
inspectable. To rebuild the native launcher from the extracted bundle, use
the compiler and flags recorded in `metadata/LAUNCHER-BUILD.json`, replacing
the `<bundle>` and compiler placeholders with local paths. The source header
already binds the intended runtime payload and 74 original hashes.

ZIP timestamps, names, order, permissions and compression settings are fixed.
The launcher linker suppresses timestamps and the compiler remaps build
paths. Every ZIP entry is reopened and compared byte-for-byte to the explicit
allowlist. `PACKAGE.json` lists all prior entries (not itself, to avoid a
self-hash); the final outer ZIP identity is printed to the caller. Repeat
assembly with identical frozen inputs and toolchain produces the same ZIP.
Neither deterministic packaging nor cross-compilation is gameplay acceptance.

Focused tests: `python3 -m unittest discover -s tests -p 'test_package_level2_portable.py' -v`.
