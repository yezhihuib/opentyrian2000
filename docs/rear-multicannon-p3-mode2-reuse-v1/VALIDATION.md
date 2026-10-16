# Rear Multi-Cannon P3 mode2: bounded reuse of the four diagonal R2 heads

This is the historical mode2-only qualification. The later bounded mode1
two-lobe integration is documented in
[`../rear-multicannon-p3-mode1-reuse-v1/VALIDATION.md`](../rear-multicannon-p3-mode1-reuse-v1/VALIDATION.md).

Baseline: `76689b78e75727af767b8083d5282214135d7d6c`.

Status: **PASS: bounded source, unchanged-art reuse and independent native-runtime qualification**.

## Partial P3 scope

This candidate adds only player-one rear Multi-Cannon 10, power three, mode two,
record 267, on episode-one Normal (physical level 9) and Hard (physical level 15).
P3 mode1 record 256 and its two-lobe source heads 2/40 remain classic. This is
partial P3 coverage, not a full-power or sprite-ID-wide replacement. P1 and P2
keep their four existing exact power/mode/record tuples.

The four original diagonal identities 281/282/301/300 use the accepted R2
whole-canvas resources unchanged. Record 267 has four allocations per successful
call, repeat 6 and the same original source geometry, static heads, velocity and
anchor contract. No artwork, resource payload, role 131 identity, resource key,
logical canvas or density behavior changes. Original gameplay, INDEX8 writes,
palette, RNG, collision, shadow and draw ordering remain authoritative.

## Finite invocation ownership

The exact new tuple receives an explicit budget of four observations. It is not
computed as power index plus one. The real original create invocation claims its
renderer-owned token, and each observation carries the original allocation-loop
ordinal. All earlier allocated slots are tracked, so ordinals three and four
cannot reuse either the first or a later prior slot. Any rejected observation
cancels all remaining permits; an invalid actual reused slot first loses its
previous renderer birth without revoking valid unrelated births.

Any canonical first phase is allowed, followed only by cyclic successors. This
preserves original continuation after capacity stops a prior call after zero,
one, two or three allocations. A fifth observation, nested or unwrapped entry,
wrong token, wrong tuple, wrong ordinal or stale invocation cannot obtain a
permit. Every original return, outer-wrapper end and reset retains the existing
cancellation rules. The renderer sidecar still uses ordinary slots 0–79 only;
reserved slot 80 is excluded and no token enters the original gameplay structure.

The full 80-byte original-loader-order pin for record 267 is
`9a813af3656072f5`, including unused tails. The exact port mapping
`op[1][2] == 267` is checked with the previous mappings, op count and power use.
All previous full-record pins, normal-bank identity and coverage checks,
immutable-shot validation, one-way revocation, resource payload/layout checks,
cache lifetime, regular-file restrictions, clipping and original scope
exclusions remain in force. P4 record 257 shares the four diagonal source
identities but remains excluded.

## Fresh runtime qualification

Final immutable source/art/tests pass 20 fresh paired cases, 40 actual game
processes and 5,040 logic ticks. All process exits are zero. The matrix includes
828 actual native gameplay captures and 120 shop captures, with Normal/Hard at
native 640×400 and 1280×800. Eighteen pairs retain unchanged public manual-HD
startup at density 8; two explicitly labeled reversible private presentation-only
pairs exercise density-4 payloads.

Natural original menus buy rear Multi-Cannon P3 for 3750, leaving 6250. No
loadout, gameplay-state, original-data or seed override is used. Every paired
process independently uses original `time(NULL)`, with its seed observed equal;
there are no discarded mismatched launches. Each standard 120-tick P3 run has
eight successful mode2 four-head volleys and 408 newly admitted head draws,
split by actual ordinal as 82/137/107/82. Every new admission joins to the exact
record267 birth and allocated slot. There are eight natural rear power failures,
36 rear emissions reusing older slots, including 11 previously used by front
shots. P3 mode1 record256 remains classic.

All 20 original trace categories per pair are byte-exact: complete state/RNG,
INDEX8 game/display buffers, palettes, allocation, movement, collision, input and
original head/shadow/blitter/scene order. Only the intended renderer HD-admission
bits change. Uploaded/native difference support, final Normal/Hard composition,
fractional alpha and native 2×/4× sampling are reconstructed exactly. The
near-emission witness preserves 115–119 changed final pixels per head at native
2× and 466–469 at 4×, including fractional edges and real ship occlusion.
Original Hard Night darkening and viewport/HUD clipping remain exact. Natural
authored head-to-head support overlap measures zero; separately labeled
synthetic compositor cases below cover overlap and ordering.

Fresh P1 and P2 pairs preserve their HD traces and pixels exactly. P4 is bought
naturally for 8250, leaving 1750; its shared diagonal heads receive no new
rear-role admission. Its complete baseline output, including unrelated existing
HD rendering, stays exact. Missing/corrupt cases alter only the eight diagonal
resource files and fall back exactly. Mode1→2→1, retained older mode2 births,
stopped firing and clear frame179 pass. Repeated/skipped actual SDL Present and
private density-4 diagnostics preserve original state, RNG and admission.

All six ordinary, Present and density-4 observer inverses restore all 160
production source files with zero fuzz. Ten strict runtime build variants have
zero warnings under the documented inherited-warning suppression policy.
Disabled diagnostic builds retain the same 15 inherited warnings and add none.
All source, asset and focused-test file hashes are reverified after the matrix.

Independent review recomputes all 414 paired native frames and all 20 original
parity files per pair, verifies 56 unresized preview crops and 50 full-frame PNG
exports, and visually inspects every density/difficulty quartet and clear frame.
See `RUNTIME.json` and `INDEPENDENT_REVIEW.json` for complete case counts, pins,
pixel evidence and coverage boundaries. Existing P2 qualification
is historical and does not substitute for these fresh candidate runs.

## Source and adapter qualification

- Public focused tests pass 7,636 new P3 ownership checks plus unchanged P1/P2
  suites, and 86,129 actual-adapter checks with 192 malformed-resource variants
  per plain and ASan/UBSan build.
- Private authentic production-pinned source/table/art and actual-allocation
  checks pass 70,396 assertions per plain and ASan/UBSan build. Authentic checks
  use production pins without overrides; public suites contain generated
  synthetic fixtures only.
- Independent checks pass 71,833 core, 55,098 adapter and 72,721 authentic-source
  and actual-create assertions per plain and ASan/UBSan build. Independent
  mutation tests cover every byte of the new full record, including unused tails.
- Actual original allocation is compared with its observer-stripped baseline
  across capacities zero through five, all four cyclic starts, slot 79/reserved
  80, genuine partial continuation and rejection at every emission ordinal.
- Independent synthetic actual-compositor overlap tests pass 192 cases covering
  all 24 four-head draw permutations, 403,584 overlapping samples and 9,797
  assertions per plain and ASan/UBSan build. These separately labeled synthetic
  cases do not substitute for natural-gameplay display evidence.
- Only four renderer-owned production files change. Actual create/token/ordinal
  plumbing, gameplay and generic compositor/filter/shadow sources remain
  byte-identical to the published P2 baseline. The original 156-file gameplay
  inverse passes. No new gameplay observation hooks are introduced.

## Unchanged artwork

All 6,987 assets except the existing current catalog remain byte-exact. The
catalog changes only the scope string and current-integration pointer; reversing
those two strings reconstructs the complete baseline bytes. The original P1 art
binding remains immutable historical provenance. Both default packs retain 589
resources, including the same 24 density-4/density-8 copies of six accepted heads.
Only the four diagonal members gain the new P3 mode2 source admission. See
`ART_REUSE.json` for all unchanged resource hashes and fresh aggregate checks.

## Reproduction and limits

Run from the repository root:

    python tests/run_rear_multi_p1_core_tests.py
    python tests/run_rear_multi_p1_adapter_tests.py
    python tests/test_rear_multi_p1_source_inverse.py
    python prototype/build-rear-multicannon-p1-art.py
    python prototype/build-hd-assets.py

The established test and resource filenames retain their original P1 prefix for
compatibility. Public tests use synthetic fixtures. Authentic game-data checks
and gameplay captures remain private. No original game payloads, decoded arrays,
private observers or screenshots are distributed here.

Public manual-HD startup continues to select density 8. Separately labeled
private density-4 presentation diagnostics do not add a new public startup mode.
Linux SDL dummy/software-renderer readbacks do not establish Windows,
physical-GPU, full-campaign or performance coverage. ASan/UBSan disable
LeakSanitizer under the environment's ptrace setup; there is no leak-check claim.
