# Original cloud palette-blend extracted units

The finite regression runner is `prototype/test-original-cloud-blend.py`, with
its isolated C harness in `prototype/test-original-cloud-blend.c`. It does not
launch the engine, read authored HD assets, or modify the original game data.
A C99 compiler and Python 3 are sufficient; SDL is not required.

Run with the user's original data and a **fresh directory outside the checkout**:

```sh
python3 prototype/test-original-cloud-blend.py \
  --data /path/to/tyrian2000 \
  --out /path/to/new-private-cloud-unit-results
```

A data-free source check is also available:

```sh
python3 prototype/test-original-cloud-blend.py --source-only
```

Both optimized and ASan/UBSan builds run in distinct output subdirectories.
Original tile bytes, extracted function includes, executables, logs, and
`result.json` stay in the external output directory. Existing output directories
are rejected. The test retains all evidence and never deletes earlier results.
LeakSanitizer is disabled for executor compatibility; AddressSanitizer and
UndefinedBehaviorSanitizer are enabled with halt-on-error.

## Exact source boundaries

The source baseline is commit `16810f07ce6ffe58df04f07d97287b5329450d9b`.
Removing the cloud compatibility block must restore the **entire** original
`render_mirror.c`. Removing the admission line and reversing the pixel callback
must restore the **entire** original `backgrnd.c`. Removing the four declaration
and macro lines must restore the **entire** original `render_mirror.h`.

The runner extracts the actual current cloud row and pixel helpers, the actual
candidate raw background blit, and the exact baseline raw blit. It also extracts
and requires byte-for-byte baseline equality for all terrain whitelist helpers,
the terrain binder and terrain pixel callback, monotone-ramp checks, continuous
explosion color operator, palette lookup, cloud shadow operator, ordinary shadow
operator, turret grouping, local classic restoration, generic pixel callback,
and unsupported-path handling. Function names alone change where observation
wrappers count callbacks; the tested bodies are otherwise byte-exact.

## Original-source identity and provenance

`shapesz.dat` must have SHA-256
`3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248`.
The runner independently parses its blank flags and raw 24 × 28 tile records.
It checks all 672 bytes of each original cloud, records per-tile SHA-256 and
FNV-1a64, and requires every one of the production's 15 FNV pins to agree.
The source IDs are exactly 41–45, 51–55, and 61–65; the slots are 186–200.

Nonzero source indices use hues 0x30, 0x60, and 0x80. Only index 0 is transparent.
Covered 0x80 pixels have a zero low nibble and are explicitly required to reach
the candidate callback, retain an indexed write, and transform HD owner 1 color.
All original tiles are required to reach real callbacks; every original tile
with zero-valued ramp coverage or transparent support must exercise it.

The real binder is tested across IDs 0–700 and layers 0–4. Cloud registration
requires layer 2 and shapesZ, rejects other layers/maps, and respects its capacity.
The cloud ID set must be disjoint from every other registered terrain whitelist.
Unregistered equal bytes are rejected; equal newly registered backing is accepted.
Wrong IDs, source swaps, null cells, repeated pointers, current value changes,
and transparent-to-covered support changes exercise per-tile admission.
Same-address first/last byte changes also run when the changed byte is vertically
clipped away. Restoration of the original bytes must immediately restore admission.

## Indexed and display oracles

Every raw draw executes the baseline and candidate original loops once each.
An independent cell-by-cell oracle computes hue overwrite and **truncated**
low-nibble averaging at each write. It compares the complete indexed allocation,
including row padding and allocation guards, against both baseline and candidate.
The full ordered callback trace must agree on address, source, and final index.
Admission bits and replacement bits must also match at every callback.

The display oracle computes the continuous source-hue operator independently
with explicit channels and widened integer arithmetic. Owner1 keeps its original
true-color subpixel variation. Owners 0 and 2 use the exact indexed palette color.
Ownership and cloud provenance, green-head invalidation, selected pixels, and
the full logical expected-index buffer are checked after each draw.

The existing generic pixel callback and local-restoration body execute for
rejected draws. A synthetic full-screen live HD region makes the restoration's
command-position indexed reads independently auditable. Existing replacement
suppression is tested through the real terrain pixel callback with alternating
replacement bits. Font and Vulcan claim collaborators return no claim; minimal
SDL layouts and a supplied terrain replacement mask are the only presentation
scaffolding. This test does not claim to validate authored replacement loading.

## Matrix

- Original palette5 and three additional monotone ramps, including unequal and
  flat channels; three nonmonotone controls separately break red, green, and blue
- All 256 HD peak values × all 16 source values × all three original source hues
  against every tested palette
- A hue-specific rejection check that leaves cloud tiles using other hues valid
- Densities 4 and 8; pure owner0, owner 1, owner2, and mixed subpixel ownership
- Indexed pitches 320 and 328; both admitted horizontal limits; every visible
  height 1–27 at both vertical edges, for all 15 originals and ownership classes
- Every visible height under each synthetic palette class; repeated same-row
  draws and overlapping rows; alternating replacement suppression
- Safe padded whole-offscreen and horizontal-wrap legacy fallback draws;
  extreme integer coordinates are admission-only
- Known-blend off, original-reference on, local-blend off, surface identity,
  format, density, buffer, map, suppression, bank, and layout guards
- Actual post-cloud shadow callbacks for all 15 originals, both densities, all
  owner classes, and every monotone palette; six repeats reach the indexed floor
- Normal writes invalidate cloud provenance, followed by later shadows and
  overlapping cloud draws; zero-channel shadow-ratio and unchanged-floor controls
- Pixel-level wrong source, zero source, mismatched index result, rejected context,
  replaced state, invalid address, and pitch-padding guards

Five external extracted-unit negative controls must fail: treating covered 0x80
as transparent, flattening owner 1 to palette, bypassing the current source hash,
clearing cloud shadow provenance, and rounding the indexed average. Their source
changes are confined to generated external test includes. They never touch
production files.

## Limits

These units establish finite source, byte-buffer, ownership, color-operator,
clipping, and callback-order properties. They do not establish visual aesthetics,
real gameplay composition, frame pacing, performance, GPU/Windows behavior, or
successful HD asset loading. Synthetic underlay colors and ownership are test
inputs. Extreme-coordinate raw loops are deliberately not executed because the
legacy loop's signed coordinate arithmetic is outside this compatibility change.

## Verified candidate result

The 2026-10-15 candidate run passed in both optimized and ASan/UBSan builds with
identical totals: 73,554,050 assertions, 2,878 original row draws, 9,252,348 pixel
callbacks, 34,421 covered 0x80 callbacks, 2,337,984 shadow pixel writes, 86,016
independent palette-formula cases, and 419 real generic local restorations.
Each build compared 1,380,264,192 indexed bytes and 26,222,592,000 RGBA bytes.
All five extracted-unit negative controls were rejected as expected. Source
inverse checks passed, and the original data files retained their initial hashes.
