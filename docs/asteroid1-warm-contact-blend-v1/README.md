# ASTEROID1 authenticated warm/contact blend

This display-only follow-up fixes the witnessed whole-body rollback caused by
original warm explosions overlapping accepted optional ASTEROID1 HD artwork.
It adds no art or animation and changes no gameplay, indexed writes, RNG,
allocation, damage processing or original draw order. The existing 57 optional
images, 20 families, 52 source dependencies and all asset catalogs remain exact.

## Witness and result

The retained [pre-fix regression](../asteroid1-pulsing272-v1/tick 28-shared-blend-regression.json)
records four accepted material 136/base 233 quadrants at (95,21), followed by a
24x28 classic-region restore replacing 590 HD blocks. An unchanged-rendering
attribution diagnostic identifies the triggering original command as
explosionSpriteSheet index 151, origin (93,42), source 112/0x70, first overlap (98,43).

At native 2x and 4x tick 28, those same four HD commands remain accepted, original
warm effects remain visibly overlaid and the whole-body restore is zero. The HD
housing and unaffected body detail survive. Pixel differences are confined
exactly to the survivor: native 2x bbox (142,42,190,98), native 4x bbox (284,84,380,196).
Everything outside that actor is pixel-identical. Across each 80-tick ordinary
partial/lethal 3940 window, 78 original restore regions become zero, with 3395
verified HD-subpixel blend callbacks. This is a corrected effect composition,
not a new damage pose.

## Finite compatibility policy

The new private helper admits only the normal loaded explosionSpriteSheet,
17810-byte newsh6.shp, and 116 pinned original warm/contact frames:

- 3..14,22..33,41..52,60..71
- 122..133,145..152
- 154..165,173..184,192..203,211..222

Every callback decodes the current 12x14 frame into 168 palette bytes and 168
coverage bytes, checks its semantic pin and verifies the actual source pixel
and coordinates. Wrong banks, changed same-address bytes, coverage or offsets,
unknown frames and source-coordinate mismatches cannot reuse trust. Only source
hues 0x70/0x40 with a current channelwise-monotone ramp and the exact original
indexed blend result qualify. Conventional origins and disjoint INDEX8/ARGB8888
surface layouts are checked; horizontal-wrap cases retain their original path.

Only already-authored owner 1 subpixels use the existing first-level continuous
palette-ramp blend. Classic/original-reference copies use the exact current
palette index. HD ownership remains intact; touched green/cloud provenance and
selected-cell bookkeeping advance at the original callback position. Original
INDEX8 pixels are never written by the helper.

The ASTEROID1 existing probe/live-lease policy stays in place. The global
known-blend flag remains false. First-level behavior, filter handling, generic
asset admission and all integrity guards are unchanged. Failed admission still
runs the complete-region classic restore or original rejection. Fallback traces
now identify the actual source index instead of 0.

## Verification

- Extracted production helper, indexed blitter and real fallback: optimized and
  ASan/UBSan each pass 3,190,088 checks, including all 116 frames, densities 4/8,
  mixed ownership, repeated ordered blends, 45 negative callbacks and 5 actual
  indexed blits. Source/coverage/header mutations, cross-bank sources, arithmetic,
  palettes, layouts, origins, suppressed/reference/rejected paths, exact whole-
  rectangle fallback and no-write boundaries are covered.
- Exact baseline-source comparisons preserve the first-level callback tail,
  indexed blitter and existing pixel/blend/ramp helpers.
- DATA glyph and fixed flash 145 actual-data adapters pass plain/UBSan.
- Pulsing 272, linked 338, firing 325, ember 269, paired 287/288 runtime suites pass
  optimized and ASan/UBSan, including 356 negative fixtures per mode.
- All 81 production C sources compile and link with strict warnings-as-errors,
  zero warnings. Independent code/pin/native review passes.
- 14 paired actual-engine cases / 28 runs cover all four original-event sites,
  genuine partial/lethal fire, flag-off, and missing/corrupt 272 controls at
  native 2x/4x. All 392 named trace comparisons and 2240 logic ticks preserve
  state/RNG/INDEX8/events/actors/calls exactly; no frame rejection, coverage
  mismatch or restored-pixel mismatch occurs. The 72 native captures have no
  changes outside original restored HD regions. Flag-off and missing/corrupt 272
  tick 28 captures remain byte-identical.
- Shared-source guards pass 6812 checks per optimized/ASan/UBSan mode across
  20 families and 52 independent source dependencies.
- All 57 actual optional HDR1/PNG pairs and finite catalog identity/mutation
  checks pass, using the explicitly required external historical asset root.

Run the focused fixture with local original data, keeping its outputs outside
this checkout:

```
python3 tests/run_asteroid_effect_blend_tests.py --repo . \
  --source-sheet /path/to/TYRIAN2000/newsh6.shp --output /path/to/new-output
```

See validation.json for exact small witnesses and source identities. Full logs,
receipts and native captures remain external under
`tyrian-asteroid-blend-validation-20261020`, including
`runtime/tick28-native2x4x-before-after.png`. Original game data is not included.

## Remaining limits

At this warm-contact checkpoint, shield, green, smoke, value, other sheets and
unknown/incompatible sources or ramps retained conservative fallback. A later
[finite authenticated cyan-shield extension](../asteroid1-shield-blend-v1/README.md)
adds 22 nonempty shield frames without broadening the other effect policies. This is not an all-effects fix. All 116 source frames
are exercised by extracted tests; actual engine captures witness only the frames
reached in the finite original-event windows. Those windows are explicitly
ASSISTED, preserving original setup/events/allocators/physics/RNG while omitting
prefix actors; they do not establish a natural campaign or whole-level pass.
Captures use headless SDL dummy/software rendering, not a desktop window check.
The existing native side-clipping evidence gap remains; extracted bounds tests
pass. No Windows build or external push is included. LeakSanitizer is disabled
for executor ptrace incompatibility; AddressSanitizer and UBSan remain enabled.
Runtime stays below 512 MiB, compilers below 1 GiB and free disk above 5 GB.
