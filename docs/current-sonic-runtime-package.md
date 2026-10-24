# Current Sonic formal runtime closure

The current formal package contains **1029 destinations**, four more than public
`013560593b3ea9e033906116b849a9508f6d621a`. The only additions are:

- `assets/gameplay/bullet-105-8.hda`
- `assets/gameplay/bullet-106-8.hda`
- `assets/gameplay/bullet-124-8.hda`
- `assets/gameplay/bullet-125-8.hda`

All four use the existing `gameplay` group, revision
`current-single-source-sonic`, and sources under
`assets/hd/current-compat/sonic/`. They are rederived from the two current
masters, not copied from the frozen artwork directory. Every previous 1025
manifest row and its source bytes is unchanged at bootstrap. The global
registry remains 120 entries, and no C source, header, render eligibility,
default option, input, gameplay, or artwork changes in this packaging update.

Together with the already-packaged 20/21, these resources complete the existing
P02/P04 atomic family. File inclusion is not renderer enablement: the executable's
default-off rules remain in force.

## Build and edit

Use the [current Sonic authoring workflow](current-sonic-authoring.md), then
export a new runtime:

```sh
python3 scripts/build_current_sonic.py check
python3 scripts/package_runtime.py --build --output /absolute/new/runtime-directory
```

The output must be a new directory outside the source checkout. `--platform
windows` selects the Windows packaging format; it does not compile an EXE or
test Windows. The source remains unchanged. Playing the exported assets still
requires separately supplied original game data, a compatible binary and platform
dependencies.

Stage/apply recomputes the current runtime rows after editing either master.
Editing 105 changes only 105/106; editing 124 changes only 124/125. A rebuilt
binary is needed after artwork edits because its payload pins are compiled in.
Do not combine edited resources with an old executable or manually change the
manifest to make inconsistent bytes look current.

## Narrow, fail-closed boundary

The manifest rebuilder admits these exact four consumers in a separate additive
block. The prior residual check still rejects unknown historical art consumers;
there is no permissive filename glob. The default runtime manifest and explicitly
current Sonic references require all four rows, their fixed destinations and
metadata, and a successful master/recipe/HDA/header rederivation. This includes
extra rows falsely labeled as current Sonic, not only known filenames.

Generic custom manifests remain generic if they have no current Sonic source
or revision references. A historical Sonic file can still be copied through an
explicit historical manifest without requiring current authoring inputs. A
legitimate unrelated generic extra file is not prohibited by the Sonic closure.

## Verification and limits

Packaging tests use real isolated builder inputs, actual master edits,
stage/apply/check and Linux/Windows-format asset exports. They check all 1029
copied payloads, the old 1025-row identity, pair-local edit propagation, stale and
tampered stage rejection, and rollback on an injected runtime-manifest write
failure. Missing consumers and transport corruption with self-consistent hashes
are rejected by the current-source contract. Generic historical export remains
available. These tests do not execute the game or establish Windows/GPU gameplay.

Historical runtime tests retain their 1025 baseline through an explicit strict
four-row projection. It verifies the current quartet and the exact old destination
set before removal; a missing member, fifth current member or old destination
replacement cannot silently become a historical pass. Historical source pins,
fixtures and validation JSON remain unchanged. The original C/render tests and
assisted captures retain their earlier scopes, rather than being presented as
new native runs of this packaging-only update.

The [packaging validation receipt](current-sonic-runtime-package-validation.json)
records the final bounded tests and unchanged-source evidence.
