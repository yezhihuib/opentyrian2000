# Rear Multi-Cannon P4 mode 1: five-head accepted-art reuse

Baseline: `c812f88befb2f5bde9f105852657c914b4aab18f`.

Status: **PASS: bounded five-head reuse with fresh independent native-runtime qualification.**

## Bounded scope

This change admits player-one rear Multi-Cannon 10, power 4, mode 1, record 257,
on episode-one Normal (physical level 9) and Hard (physical level 15). The exact
power/mode/port mapping and all 80 record bytes must match. The original five
phases are 281, 282, 301, 300, 77; the first four reuse their accepted R2 resources.
The fifth, downward 77, gains an exact-density rigid transform of accepted 1.
The record FNV pin is `b2155699efbdb6e3`; source 77 is `ebed26fe15a8012c`.
Shared source IDs alone do not grant admission.

This is partial P4 coverage. Mode 2 record 268 keeps its baseline pass-through:
existing generic HD 163/164 remain unchanged, while 182/183/77 remain classic.
There is no generic 77 mapping or new mode 2 ownership. Existing P1/P2/P3
resources, exact tuples and retained-birth behavior remain in place.

The invocation budget and cyclic period are both 5, explicitly independent of
power index plus one. All prior successful slots must be distinct. Partial slot
exhaustion advances original phase only for successful allocations, so 77 can
be the first emission in a later invocation. Token, original allocation-loop
ordinal, consume-before-validation, failure cancellation, reuse and retained
birth checks remain authoritative. Record 1257 is excluded by identity even
where its bytes equal 257; alternate tables and Christmas banks are excluded.

Only the four renderer-owned rear provenance source files change. Gameplay,
RNG, allocation, palette, collision, shadow, INDEX8 writes, generic mapping,
compositor and original draw order remain unchanged. No observation hook is
added to production code.

## Exact accepted-art construction

At density 4 and 8 independently, source 1 rotates 90 degrees clockwise and shifts
(-2,+2) logical pixels into a 12×14 canvas with anchor (0,0). For density d, input
(x,y) maps to (12d-1-y,x+2d). All nonzero RGBA samples are copied unchanged;
only transparent-black samples fall outside the destination. Alpha histograms,
brightness totals and the full occupied-sample multiset remain exact.
There is no generation, resampling, blur, new halo or brightness normalization.

The authored smooth edge touches 40 logical cells within the original bounds,
compared with 37 original covered cells: four newly touched and one untouched
original cell. This is not a binary-mask equality claim. Native nearest
sampling can select a different subpixel phase after rotation, with a small
measured brightness difference; no display-level correction is applied.

Role 131 key 1310077 receives density 4/8 resources in both default packs, which
now contain 595 entries each. All 7,032 previous non-manifest assets remain
byte-exact. Reversing only the new catalog records and the existing-family
current-scope/current-integration strings restores the baseline catalog bytes. The aggregate verifier
passes 3,426 HDA entries and 607 source PNGs across 18 packs. See ART_REUSE.json
and the generated-only artwork package for inputs, transforms, hashes and
rebuild instructions. No 182/183 resource is included in this change.

## Frozen source and focused tests

The 160 source files, 7,049 asset files, 44 tests and Makefile were frozen before
final qualification. The original 156-file source projection remains exact.
Enabled and disabled strict production builds pass. Existing and new asset
verifiers pass, including a fresh relocated generated-only rebuild.

The new P4 core passes 66,030 checks per plain and ASan/UBSan build. The actual
public adapter passes 183,250 checks and 288 malformed-resource variants per
build. Private authentic production-pin/real-allocator checks pass 169,604
assertions per build using the genuine maximum weapon-record ID 1,818, with
1,638 physical records per source table. They exercise
63 genuine excluded record IDs in both modes, including the in-range,
byte-identical 1257 alternative; every one of the 80 record bytes is mutated and
rejected. Lower-power suites also pass.

Independent review separately runs the public suites, authentic production
pins and actual allocator, generated-art rebuild, source inverse and actual
compositor. Its authentic production-pin suite passes 397,402 assertions per
plain and ASan/UBSan build. Exact final counts and evidence hashes are in
INDEPENDENT_REVIEW.json.

## Fresh runtime

The frozen candidate passes 22 fresh paired cases, 44 actual game processes and
5,520 logic ticks. All exits are zero. There are 656 actual native gameplay
captures across both sides and 132 shop captures. Independent reconstruction
checks all 328 candidate native gameplay frames. Main Normal/Hard pairs cover
640×400 and 1280×800 with public manual-HD density 8. Twenty pairs use the public
density 8 startup; two separately labeled private diagnostics select density 4.
Original menus naturally purchase P4 for 8,250, leaving 1,750 from 10,000.
Original time-based seeds are observed equal per pair, without seed, loadout or
gameplay-state overrides or discarded mismatched launches.
Each main 120-tick case has eight full five-emission mode 1 volleys and 562 newly
admitted draws. Every admission joins the exact record 257 birth and original
slot. Mode 2, established generic 163/164 and shadows stay exact.

Twenty original parity streams match per pair, including state/RNG, INDEX8
buffers, palettes, input, allocation, movement, collision and original scene
order. Forty independently checked brown/cloud head witnesses and 80 exact
native plate tiles show all five shapes, fractional edges and Hard attenuation.
Downward 77 is fully exposed in selected frames: all 2,074 authored density 8
samples survive later writes. Native 2× shows 130 nonzero samples, 40 fractional;
native 4× shows 519 and 148. Ship occlusion is conservatively associated with the
original 24×28 command bounds, not claimed as an exact per-pixel ship mask.

Missing/corrupt 77 yields zero 77 admission while the valid quartet retains 496
HD draws; all-five-missing falls back to exact baseline output. Fresh P1/P2/P3
Normal/Hard regressions retain exact baseline traces and native frames in both
modes. Transition tests naturally retain six oblique mode 1 draws at tick 64 after
switching to mode 2, and nine unchanged mode 2 draws at 104 after switching back.
Clear 179 is exact. Downward 77 has already exited at the natural switch witness;
its retained lifetime is covered by authentic/core/adapter tests instead.

Repeated/skipped actual SDL Present controls preserve state, RNG and admission.
Each makes 127 Present calls and saves 21 selected native frames; tick 32 is
correctly absent because the diagnostic skips Present at ticks 30–32. A private
post-run expectation initially required that absent frame. Only the validator
expectation was corrected; the original successful processes, binaries, receipts
and observations were retained and revalidated. No capture is invented for the
skipped frame. Separate continuation pins remain exact. Density 4 diagnostics
pass all 44 saved native frames across both pairs. All six ordinary/Present/
density 4 observer inverses restore all 160 production source files with zero
fuzz or offset. Ten strict runtime builds pass with zero warnings; disabled
diagnostic warnings are unchanged. All frozen production files remain exact.

Natural head-head authored overlap was not observed. Separately labeled
synthetic actual-compositor tests cover 120 forced overlap/clipping cases,
both orders and density 4/8, with 34,542 overlapping and 25,856 clipped samples
and 3,606 checks per plain and ASan/UBSan build. They do not establish
natural or Hard-overlap coverage. See RUNTIME.json and INDEPENDENT_REVIEW.json
for completed cases, pixel evidence, observer inverses and remaining limits.

## Reproduction and limits

From the repository root:

    python tests/run_rear_multi_p1_core_tests.py
    python tests/run_rear_multi_p1_adapter_tests.py
    python tests/test_rear_multi_p1_source_inverse.py
    python tests/test_rear_multi_p3_mode1_assets.py
    python tests/test_rear_multi_p4_mode1_assets.py
    python prototype/build-rear-multicannon-p1-art.py
    python prototype/build-hd-assets.py

P1-prefixed symbols and filenames are retained for compatibility. Public tests
use generated synthetic fixtures. Original game data, decoded arrays, private
observers and gameplay captures are excluded from publication. Public manual-HD
startup selects density 8; private density 4 diagnostics add no public mode.
Linux SDL dummy/software checks do not establish Windows, physical-GPU,
full-campaign or performance coverage. ASan/UBSan use detect_leaks=0 under the
environment's ptrace setup; no LeakSanitizer qualification is claimed.
