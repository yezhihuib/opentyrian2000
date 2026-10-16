# Rear Multi-Cannon P3 mode 1: accepted two-lobe component reuse

Baseline: `8c996513ef83a53cd0384046a32e5701307a3d11`.

Status: **PASS: bounded source, exact component reuse and independent native-runtime qualification.**

## Bounded scope

This candidate adds player-one rear Multi-Cannon 10, power 3, mode 1, record 256,
on episode-one Normal (physical level 9) and Hard (physical level 15). Its static
original source identities 40/2 have two separate lobes. Their shared source IDs
alone cannot grant admission. P1/P2 and P3 mode 2 retain their existing finite
power/mode/record tuples and accepted artwork.

The new exact tuple receives two emissions, explicitly independent of power
index plus one. Existing invocation tokens, original allocation-loop ordinal,
all-prior-slot uniqueness, cyclic phase continuation after partial capacity,
failure cancellation and legitimate retained-birth rules remain authoritative.
The full 80-byte record pin is `336df95c79ab07a6`, including unused tails; exact
port mapping `op[0][2] == 256` is required. Record275, physical alternatives
1256/1275, P4 and other shared consumers receive no new admission.

No original gameplay, allocation, RNG, palette, collision, shadow, INDEX8 writes
or draw ordering changes are intended. Only the four dedicated renderer-owned
rear provenance files change; no new gameplay observation hooks are added.

## Exact accepted component construction

ID2 copies accepted R2 component 1 translated by −2 logical rows and its
whole-canvas vertical reflection translated by +2. ID40 copies the whole-canvas
reflection of accepted component 39 translated by −4 and unreflected component 39
translated by +4. Each canvas remains12×14 with anchor (0,0).

All full-density RGBA values are copied unchanged. Lobe supports are disjoint,
no occupied sample clips, and central logical rows 6 and 7 remain transparent.
Each lobe preserves its component alpha and alpha-weighted RGB totals. These
are independently authored left/right components; one is not substituted with
a mirror of the other. Density 4 and 8 use matching accepted-density components.
No image generation, resampling, blur, halo or brightness normalization occurs.

The accepted HD curves retain their existing differences from original pixel
coverage within the same bounds. Whole-canvas reflection changes the phase of
native nearest sampling, so display-level lobe brightness can differ slightly.
The offline Hard model is an art comparison only; fresh actual runtime checks
must establish ownership, night transfer, covered zero-alpha cells and order.

Both default packs add four exact-density resources, reaching 593 entries each.
New role 131 keys are 1310002 and 1310040. The old six-head resources are unchanged.
See `ART_REUSE.json` and the generated-only artwork package for all transforms,
hashes, exact-byte rebuild instructions and explicit binding records.

## Frozen source qualification

The production source, assets and focused tests were frozen before candidate
runtime launches. Public tests pass 2,374 new mode1 ownership checks and 7,745
mode2 ownership checks per plain and ASan/UBSan build, alongside the P1/P2
suites. The actual public adapter passes 100,900 checks and 256 malformed-resource
variants per build. Private authentic production-pin and real-allocator checks
pass 82,402 assertions per build, using the genuine 1,818-record weapon bound.
They exercise excluded records 1256/1275 as in-range consumers, including the
byte-identical record 1256 alternative, rather than relying on a small test array.

The original 156-file source projection is exact. Only four renderer-owned source
files change; enabled and disabled strict production builds pass. Both old and
new asset verifiers pass; the aggregate verifier checks 3,422 HDA entries and 605
exact source PNGs across 18 packs. Reversing the finite new catalog entries and
two existing-family metadata strings reconstructs the baseline catalog bytes.
All frozen files remain exact after the complete runtime matrix.

## Fresh runtime and independent review

The final frozen candidate passes 20 fresh paired cases, 40 actual game
processes and 5,040 logic ticks. All process exits are zero. The matrix retains
448 actual native gameplay captures and 120 shop captures. Main Normal/Hard
runs cover native 640×400 and 1280×800. Eighteen pairs use unchanged public
manual-HD startup at density 8; two separately labeled private presentation-only
pairs exercise density 4 at native 2×.

Original menus naturally buy rear Multi-Cannon P3 for 3750, leaving 6250. Original
`time(NULL)` seeds are observed equal per pair, without seed/loadout/gameplay
state overrides or discarded mismatched launches. Each main 120-tick case has
eight two-emission mode1 volleys and 232 newly admitted draws: 80 for the first
ordinal/raw 40 and 152 for the second/raw 2. Both original mode2 emission and its
approved HD output remain exact. There are eight natural rear power failures,
36 rear emissions reusing older slots, including 11 previously used by front
shots. Every new admission joins the exact record 256 birth and original slot.

All 20 original parity streams match per pair: complete state/RNG, game/display
INDEX8 buffers, palettes, input, allocation, movement, collision, and original
head/shadow/blitter/scene order. Independent reconstruction exactly matches all
224 candidate native frames. There is no difference outside the union of the
admitted original and authored supports. Brown/cloud witnesses show both lobes
of both heads, their unchanged two-row central gaps and surviving fractional
edges. Actual Hard palette-anchored attenuation, ship occlusion, later writes
and viewport/HUD clipping remain exact.

Fresh missing/corrupt cases fall back exactly with zero new admissions. P1/P2
regressions and P4 shared-source negatives retain complete baseline traces and
pixels, including unrelated established HD rendering. Both 180-tick switch/stop
runs preserve older legitimate births across mode changes and reach exact clear
frame 179. Repeated/skipped actual SDL Present and private density 4 diagnostics
preserve original state, RNG and admission. All six ordinary/Present/density 4
observer inverses restore all 160 production source files with zero fuzz.
Ten strict runtime build variants have zero warnings; the disabled diagnostic
builds retain the same 15 inherited warnings and add none.

Independent frozen-source checks pass 283,597 core, 63,325 adapter plus 256
malformed-resource variants, and 84,716 authentic-source/table/art/allocator
assertions per plain and ASan/UBSan run. Authentic tests use production pins
without overrides and include actual 275/1256/1275, alternate Episode 4/5 and
Christmas-bank inputs. All 7,236 frozen source/art/test/Makefile entries remain
exact after qualification.

Natural new-head alpha overlap was not observed. Separately labeled synthetic
Normal-compositor tests cover both orders and cyclic starts, d4/d8, overlap and
top/bottom clipping: 48 cases, 43,346 overlapping samples, 20,098 clipped samples
and 1,398 assertions per plain and ASan/UBSan run. These use the unchanged actual
compositor with an independent scalar pixel/owner oracle, and are not claimed
as natural or Hard-overlap evidence. See `RUNTIME.json` and
`INDEPENDENT_REVIEW.json` for exact scope, hashes, cases and remaining limits.

## Reproduction and limits

From the repository root:

    python tests/run_rear_multi_p1_core_tests.py
    python tests/run_rear_multi_p1_adapter_tests.py
    python tests/test_rear_multi_p1_source_inverse.py
    python tests/test_rear_multi_p3_mode1_assets.py
    python prototype/build-rear-multicannon-p1-art.py
    python prototype/build-hd-assets.py

Existing P1-prefixed symbols and resource filenames are retained for loader
compatibility. Public tests use generated synthetic fixtures. Original game
payloads, decoded arrays, captures and private observers remain private.
Public manual-HD startup selects density 8; separately labeled private density 4
diagnostics do not introduce a public mode. Linux SDL dummy/software evidence
does not establish Windows, physical-GPU, full-campaign or performance coverage.
ASan/UBSan disable LeakSanitizer under the environment's ptrace setup; there is
no leak-check claim.
