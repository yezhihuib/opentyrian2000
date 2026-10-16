# Rear Multi-Cannon P5 mode 1: bounded HD triple heads

## Scope

Baseline: `4eeaf3a9fef3cb0f9ce1ac83ecc06cfb0194e3b4`, tree
`575fdf66659881c99c4204791df02f85b8e291c2`.

This change admits only player 1, rear bay 1, port 10, power index 4, mode index
0, exact original record 258. Its two successful emissions have cycle 41, 3,
with an exact invocation budget of two. Existing episode-1 physical level
9/Normal and 15/Hard, normal-data and ordinary-context restrictions remain.
P6/P9 shared sprites, physical aliases, wrong bay/player/port/mode, linked,
network, two-player, Galaga, demo, Christmas and other excluded contexts gain
no new permission. This is source-specific renderer provenance, not a generic
bank-8 raw-ID replacement.

Only four dedicated renderer files change. All 156 other source files and all
7,093 pre-existing non-manifest asset files are byte-exact. The catalog addition
is reversible to the exact baseline. Generic 163/164 heads and their shadows,
P1-P4, and the already qualified P5 mode 2 remain unchanged.

The explicit two-emission budget does not use `power_index + 1`. Both cyclic
starts survive prior partial capacity. Existing generation/token/tick ownership,
original allocation ordinal, cyclic successor, all-slot duplicate checks,
per-allocation recycled-slot clearing, and retained birth identity seal remain.
Record 258 has its own full 80-byte semantic pin and conditional port-table
cell check. Existing births do not depend on the new cell. Separate append-only
drawable and observed indexes preserve every prior cache and pin position.

## Accepted artwork deviation

The new role-131 resources are IDs 3 and 41 at authored densities 4 and 8,
12x14 logical canvas, anchor 0,0. Existing accepted R2 components are reflected
across their whole canvas and translated by exact integer offsets:

- 3: flipY(1)+(-2,-5), flipY(1)+(0,-1), 1+(-2,+5)
- 41: 39+(+2,-3), 39+(0,+1), flipY(39)+(+2,+3)

Original component geometry reproduces the target after two original tail
cells clip. Generated components do not overlap, even before clipping; all six
orders are byte-identical. Retained RGBA samples and bright heads are unchanged.
There is no redraw, blur, recoloring, normalization, resampling or new margin.

Real red/orange outer tail samples, including two opaque density-8 samples for
ID3, are discarded. Mild flat tips at native 4x, especially over clouds, were
explicitly accepted after visual review. Independent technical review passes
with that accepted deviation; seamless taper and whole-lobe brightness are not
preserved. Authored alpha loss reaches 0.812253%; native sampled loss can reach
0.964561%. These encoded-RGB alpha/luma measures are not linear-light photometry.

The exact footprint claim is limited to canvas, anchor and occupied bounds
[0,1,12,13]. Smooth accepted-art support is not the original indexed coverage
mask. Expanded diagnostic margins are not production output. ART_REUSE.json
and the artwork-family README retain the full clipping and support limits.

## Controlled source and resource qualification

Nine core suites pass strict plain and ASan+UBSan builds. The new P5 mode-1
suite performs 534,347 checks per build; 14 compiled faulty private variants
are rejected. The synthetic actual-allocator adapter performs 675,357 checks
with 480 malformed-resource variants. Private original-data qualification uses
unoverridden production pins in both default packs, with 684,129 checks per
pack/build. An independent original-table adapter adds 230,020 checks per build.

Coverage includes exact two-emission ownership, both cyclic starts, zero/full/
partial capacity, all 80x80 slot pairs, slot 79/80 boundaries, power failures,
recycling, nested/unwrapped calls, stale tokens, immutable birth mutations,
real later-power/alias negatives, and all prior qualified records. Independent
seal tests cover 8,032,140 checks over 32 births and 80 slots per build. The seal
is an integrity check, not a cryptographic memory-security boundary.

Cold/warm cache, exact density, header/layout/identity, source/table mutation,
missing/corrupt files and payload pins pass. All six old/new asset suites pass;
old baseline catalog/hash checks remove exactly the bounded additive family.
Generated source PNGs equal frozen output PNG bytes, and eight HDR1 copies carry
exact reviewed RGBA. Relocated rebuilds and unsafe-destination/corruption
rejection pass. Source/test statistics and warning limits are in SOURCE_TESTS.json.

## Actual-game diagnostic qualification

Ordinary fresh-start P5 purchase is not established. Starting cash is 10,000;
P5 costs 15,750. Every diagnostic case first completes the genuine ordinary
P4 purchase costing 8,250, leaving 1,750. A private pre-first-tick fixture then
changes only rear power 4 to 5 in both baseline and candidate. Exactly one of
784 player bytes changes; reversing it restores every byte. All 5,016 canonical
RNG bytes, funds and other setup fields remain unchanged. Original RNG seeding
is retained. Later ordinary pickups may change the wallet normally.

The fresh matrix contains 26 paired cases and 52 qualifying processes:

|Cases|Coverage|
|---:|---|
|4|Normal/Hard actual native 2x and 4x|
|6|Missing 3, corrupt 41, and both missing in both difficulties|
|8|Genuine P1-P4 purchases, both modes, no diagnostic preset|
|4|Normal/Hard 2x/4x mode switches, retention and fire-stop clearing|
|2|Exact authored density-4 controls|
|2|Repeated/skipped Present controls|

All 52 processes exit 0: 6,720 logic ticks, 928 native game captures and 156
shop captures. Two separate baseline preparations also exit 0; including them,
54 processes cover 6,960 ticks, 984 game captures and 162 shop captures. No
candidate game rerun or frozen production change is used to obtain a pass.

All 20 original state streams are exact per pair. Each main case has 226 new
record-258 draws (41:122, 3:104), live exact payload identities and fully exposed
brown/cloud witnesses. Independent reconstruction covers all 464 candidate
native frames, including original Hard lighting. Fractional alpha survives;
changed pixels stay within the qualified original-plus-authored support.

Missing 3 admits only 41, corrupt 41 only 3, and both missing is baseline-exact.
All ordinary P1-P4 cases have no new admissions or changed native pixels. Pure
record-269 frames 80/88/96 in every main and transition case preserve all four
prior P5 mode-2 heads and exact native/uploaded output. Mixed retained births
are recorded separately. Density 4 adds both new triples while preserving the
older documented classic fallback for 182/183.

Ordinary mode switches at ticks 60 and 100 retain existing births from their
original records. Fire stops at 120; all four transition cases are baseline-exact
at tick 179, with zero player-shot draws and new admissions. Present repeat/skip
cannot advance ownership or alter original traces. Skipped ticks and second
repeated presentations do not claim extra native readbacks.

Natural authored new-head/head overlap is zero. Controlled compositor tests
separately exercise 96 forced overlap/clipping cases, including 198,252 overlap
samples and 61,212 clipped samples per build. Natural partial slot exhaustion,
every cyclic start and in-game power changes are not claimed. Ten strict builds
and six zero-fuzz/offset observer inverses pass, restoring all 160 source files.

One early preview helper enumerated a just-completed 4x case before its derived
birth file existed. The failed check is retained; deriving that file first fixes
the preview on unchanged game observations, without rerunning any game or
changing the source/art/fixture freeze. RUNTIME.json retains this correction,
exact process accounting, storage verification and remaining scope limitations.

## Reproduction and publication boundaries

From the repository root:

    python3 tests/run_rear_multi_p1_core_tests.py
    python3 tests/run_rear_multi_p1_adapter_tests.py
    python3 tests/test_rear_multi_p1_source_inverse.py
    python3 tests/test_rear_multi_p5_mode1_assets.py

The art builder is
`assets/hd/artwork/player-rear-multicannon-p5-mode1-triples-v1/build.py`.
Use fresh isolated output destinations as its README requires. P1-prefixed
loader and test names remain for compatibility.

Public fixtures are synthetic. Original game data, original-derived masks,
private observer fixtures, captures and executables are excluded. The reported
Linux SDL dummy/software 120/180-tick runs do not establish full-level/campaign,
ordinary P5 acquisition, Windows, physical-display/GPU performance, disk
hot-reload or LeakSanitizer qualification. Leak detection is explicitly disabled.

INDEPENDENT_REVIEW.json records the final bounded review. Final archive integrity,
remote exact bytes, expected-parent non-force publication and CI status are
separate publication gates; local test success must not be called green CI.
