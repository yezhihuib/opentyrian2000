# Direct level-2 preview for frozen Windows 562e8fc

This companion bypasses the menu and level 1 using the existing, unchanged
asset-debug entry. It is **scripted, bounded preview playback**, not ordinary
interactive gameplay or a full-level entry. No engine source or artwork changes
are made. In particular, this does not import the newer development branch's
player invulnerability or tank-shell implementation into the frozen executable.

## Fixed identity and scope

- Frozen source: `562e8fc4ad0f7916734bc40624b867a152d89b0c`.
- Merged 112-unit source digest:
  `8c85faa18d5427e4f3af2015cbdbbae2e82b3631d27ef0774236c22be106ca54`.
- Input archive: `OpenTyrian-HD-PreparedInputs-562e8fc.zip`, SHA-256
  `32865c3f820bae65757a266f5b85149d94706fe222197b98510e6903c7bd1ce3`.
- Preserve all **101 pinned public assets**, totaling 18,410,168 bytes. Only the
  existing **23 base family controls** are selected for this preview. Several
  ordinary-only extensions reject asset-debug, so presence is not display coverage.
- Fixed arguments: `--asset-debug=custom --asset-debug-episode=1
  --asset-debug-level=2 --asset-debug-event=18 --asset-debug-running
  --render-ticks=600 --render-no-capture`, plus the verified external data directory.
- 600 is the total tick ceiling from the original beginning, not 600 additional
  ticks after event 18. No level pointers, events, save states or renderer guards
  are rewritten. Display starts after reaching the existing event target.

## Prepare from the existing verified frozen runtime

Use Python 3.11 or later and the new `scripts/preview_level2_frozen.py` companion.
Supply the existing frozen 101-asset runtime and its independently retained
`RUNTIME.json` digest. The source runtime may already contain menu-run logs or
saves: they are neither read nor copied. Its immutable executable, DLLs, tools,
art, source/build receipts and original-data inventory must still match.

```text
python preview_level2_frozen.py prepare --runtime OLD_FROZEN_RUNTIME
  --trust-sha256 VERIFIED_RUNTIME_SHA256 --output NEW_ABSOLUTE_PREVIEW_DIRECTORY
```

Default is check-only. Add `--prepare` to copy verified immutable inputs into a
**new, nonexistent directory whose parent exists**. Preserve the returned
`preview_sha256` independently. Existing directories, source/data overlap,
symlinks/junctions, modified art/tools, foreign source digests and a broken build
chain are refused. No existing output is cleared or overwritten.

The new root receives its own windowed 4x/Integer configuration and becomes the
child's actual CWD. This is essential: `TARGET_WIN32` uses `.` for native saves
and settings. Existing user configuration and saves remain untouched. Original
game data remains external; no original game files are included in this patch.
Windows native copies retain alternate streams and ordinary security prompts.

Check the copied entry without starting the game:

```text
python NEW_ROOT/preview_level2_frozen.py run --root NEW_ROOT
  --trust-sha256 VERIFIED_PREVIEW_SHA256
```

Only when a person is ready to watch, append `--launch --observer-present`.
Actual dispatch is Windows-only. This implementation never launches implicitly
or relaunches a used profile. Each subsequent trial needs a fresh prepared root.
The supervising Python process must remain open until the preview finishes.

## Controls, bounds and outcomes

- Input follows the existing controlled script; ordinary flying controls are
  not being qualified. P/Space toggles debug pause; Esc requests debug exit.
- The frozen debug handler also has N/period step, R request fresh-process reload,
  H artificial hit and D artificial destroy controls. Do not use those diagnostic
  controls for the fixed preview check. This companion never automatically reloads.
- The child is stopped after 90 wall-clock seconds, including time spent paused.
  Captured stdout is capped at 64 MiB; aggregate new/generated-file growth is
  sampled every 25 ms and checked again after exit against the same 64 MiB budget.
  The file check is a supervisory stop threshold, not a hard disk quota, and may
  transiently overshoot. Forced stop does not prove renderer/cache retirement.
- The environment is explicitly allowlisted; inherited SDL dummy drivers,
  ordinary-world, public-extension, probe and development controls are discarded.
- Post-run checks rehash immutable inputs and original startup data. A successful
  bounded result requires event target admission, positive family HD admission,
  exit code zero and the full 600-tick completion marker. Early closing is recorded
  as `ENDED_EARLY`, not a completed preview. Missing target/HD admission is a failure.
- `preview-start.json`, `preview-end.json` and `preview-output.log` remain in the
  private new root. They prevent accidental reuse. Do not delete them to bypass it.

## Verification and boundaries

The exact frozen source was independently rebuilt in cloud with all 112 units.
With original input data kept private, SDL dummy video/software rendering reached
**event 18 at tick 245 / eventLoc 19**, completed **600 logic ticks**, exited zero
and recorded **218 HD-accepted frames**. Original data hashes remained unchanged.
This was a Linux software execution, **not the frozen Windows PE, a physical
window/GPU test, or a visual acceptance result**. No gameplay screenshots, native
maps, original data or diagnostic dumps are included in this source checkpoint.

The companion's offline tests use synthetic PE files and the real frozen 101
public assets. They cover read-only defaults, exact closure after removing the
source package, no save import, tampering, fresh-profile enforcement, Unicode
paths, environment filtering, launch gating, timeout/kill/reap, slow and fast
output overflows, failed logging and native-admission result parsing.

```sh
OPENTYRIAN_FROZEN_PACKAGE=/absolute/extracted/frozen/package \
  python3 -m unittest discover -s tests -p test_frozen_level2_preview.py -v
```

The package group is explicitly skipped if that separate frozen input is absent;
do not call such a run full package validation. The current 103-asset development
package is not an acceptable substitute. Neither these tests nor the bounded
software replay establish full level completion, ordinary input, pause/menu/save
lifecycle, all 101 assets being visible, performance, or Windows GUI acceptance.
