# Original wild-cloud blend compatibility

This finite display-only extension starts from `16810f07ce6ffe58df04f07d97287b5329450d9b`.
It keeps HD terrain detail under the original translucent layer2 clouds instead
of restoring overlapping whole HD regions to indexed presentation.

## Contract

The engine still executes the original 24 × 28 cloud pixels, ordering, scrolling,
source hue overwrite, and truncated low-nibble value average. Index 0 alone is
transparent; nonzero ramp-zero pixels such as 0x80 remain covered. There is no
new artwork, HDA lookup, palette change, level/input change, or gameplay/RNG change.

Only the 15 registered shapesZ layer2 cloud IDs 41–45, 51–55, 61–65 are eligible.
Every current 672-byte tile is checked against a finite original-source pin at
every row call, including clipped-away bytes. Each used current palette hue ramp
must be monotone in all channels. Changed, unregistered, missing, or incompatible
sources use the existing fallback. Normal authored HD cloud rendering is unchanged.

For genuine HD owner 1 pixels, the existing continuous source-hue/value operator
maps true-color maximum-channel brightness into the original source hue ramp.
Classic and indexed-copy owners retain the exact indexed palette result. The
cloud tag preserves the existing palette-floor shadow behavior. Global local
restoration, turret grouping, Plasma compatibility, and other blend operators
are byte-identical to the baseline.

This is a continuous true-color approximation of hue/value blending, not exact
indexed brightness equivalence or a 50% RGB-alpha overlay. Native review finds
crisper, more terrain-textured and somewhat brighter clouds. Underlying brown
hue does not leak into the blue cloud.

## Validation

The [extracted-unit specification](unit-tests.md) gives reproducible commands,
source inverses, negative controls and test limits. Optimized and ASan/UBSan runs
both pass 73,554,050 assertions, 2,878 original row draws and 9,252,348 callbacks.
Five deliberate faults are detected, including ignoring the current source hash,
flattening HD to palette and treating covered 0x80 as transparent.

Six fresh isolated Linux SDL dummy/software processes form three matched pairs:

- Wild processor 4, native 640 × 400, original replay ticks 0–522
- Wild processor 4, native 1280 × 800, original replay ticks 0–209
- Normal processor 3 control, native 640 × 400, original replay ticks 0–209

The verified 4x pair uses the supported scaler name `4x`; every capture is
explicitly required to be 1280 × 800. A preliminary attempt used the unsupported
name `Scale4x`, silently retained Scale2x, and actually produced 640 × 400. That
pair is preserved as an additional 640-repeat control and is excluded from 4x
acceptance. No capture is classified by its requested label alone. Across all
eight starts, including that retained attempt, there are 2,306 state rows and
90 native captures. The three accepted pairs below account for 1,886 rows and
80 captures.

Each uses the existing Episode 1 physical-level 9 enemy-hit scene, seed 0x5eed,
stationary player, no firing, natural enemies/projectiles, and existing selected
art pack. No survival override or injected shot is used. All 1,886 state rows
across the six processes match their paired original state, RNG, indexed game
and output hashes. Original draw/collision/pose/projectile records and logged
blend before/source/after arithmetic agree. Frame coverage, rejection,
restoration residue and boundary-crossing failures are zero.

The wild 640 pair removes 25,412 cloud-triggered restoration records; wild 1280
removes 7,901. Candidate compatible writes preserve 1,039,632,832 existing HD
subpixels across these two runs. These are display-only counts, not new asset
coverage. Normal-control RGBA hashes agree for all 210 ticks.

Actual native readback contains 80 images: 30 consecutive640 × 400 frame pairs
at 132–161, five 1280 × 800 spot pairs at 0/90/144/145/200, and five normal 640 × 400
spot pairs. Every decompressed frame matches its direct SDL readback hash.
All native wild differences remain inside baseline-restored regions; this is
broader than the visible blue pixels because baseline restoration affected
surrounding terrain. HUD and bottom strips are exact in every pair. Two lossless
30-frame videos decode byte-for-byte to their original native captures. Review
MP4s use explicitly slowed 10 fps playback and do not establish real-time cadence.
Independent still-image review inspects 132/140/144/145/151/161 and finds no new
halo, obvious tile seam or isolated restoration block in this bounded window.

## Build and regression boundaries

Both complete 72-unit optimized production builds pass the strict warning flags.
Complete classic-disabled builds pass with inherited warnings. The scoped disabled
`backgrnd` check needs the inherited unused-variable warning suppressed; the same
issue occurs on the baseline. This is not a warning-free whole-classic-build claim.
The full existing Plasma regression passes optimized and ASan/UBSan with 64,367,833
assertions per build. All 6,722 asset files are unchanged and the asset verifier passes.

Headers are SDL 2.26.5 from the retained build prefix; the actual linked runtime
is system SDL 2.32.4, with the same dependency for both sides. The old prefix's
`libSDL2.so` is a symlink to that system library. No 2.26.5-runtime claim is made.
SDL2_net remains the retained static dependency.

The historical `prototype/fixtures/test-cloud-shadow.py` fails compilation before
execution because its older draw signature and collaborator declarations no
longer match the baseline renderer. Its extracted production helpers are unchanged
by this patch. The new current-source suite independently tests cloud shadow
floors and provenance. The historical failure is retained, not counted as a pass.

This is bounded Linux software-renderer acceptance. Full-level play, all palettes,
all input routes, Windows/GPU/fullscreen behavior, frame pacing and performance
remain unverified. Original data, private observer hooks, captures and executables
are external and are not part of this source package.
