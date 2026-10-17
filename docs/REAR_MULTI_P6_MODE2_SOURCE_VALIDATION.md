# Rear Multi-Cannon P6 mode 2 validation

Status: PASS for the bounded controlled-source and native software-rendered qualification below. Publication and remote verification are separate operations.

## Exact change

Based on published commit `5be64ad63d3ff61629a8f99081afbf6bdfa1655e`, tree `d12b826c38736725a5b267426577c43802de5289`.

Only three production files change: `rear_multi_p1.c`, `rear_multi_p1_mirror.inc`, and `rear_multi_p1_pins.h`. The admitted addition is ordinary player 1, rear port 10/bay 1, power index 5, mode index 1, exact record 270 selected by `op[1][5] == 270`. Its finite successful-emission budget and cyclic period are five. Phase order is 277, 278, 183, 182, 77. The appended twelfth full-record FNV1a64 pin is `c779039b7362d0f6`. Byte-identical record 1270 is not admitted.

All eleven earlier routes, slot limits, record-local checks, birth seals, resource indexes, caches, gameplay, allocation, RNG, shops and wrapper hooks remain unchanged. The source header still defines HEADS 15, OBSERVED 17 and MAX_BUDGET 5. The other 157 production source files and all 7,123 accepted asset/catalog files are byte-exact to the baseline.

## Density and existing-art boundary

No artwork is created or changed. Density 4 draws HD 277/278/77 with indexed 183/182; those two diagonals do not access either HD cache or open a resource. Density 8 supports all five existing HD heads. Original generic 163/164 consumers retain their unmodified paths. Missing, malformed or invalid cached resources fall back without changing gameplay or indexed bytes.

## Controlled verification

- Eleven core executables pass strict C99 plain and ASan/UBSan builds, 22 runs. The new suite performs 3,810,039 checks per build, including all 180 cyclic continuation designs, all ordered 80-slot pairs, 6,000 duplicate cases, sixth rejection, seal isolation and physical-alias exclusion.
- Eighteen isolated private core mutants compile and fail explicit checks; the unchanged control passes. No mutation is retained in production.
- The synthetic actual-source allocator/adapter/loader/wrapper passes 1,389,084 checks per build, with 480 malformed-resource variants.
- Private original-data adapter qualification passes 1,395,906 checks per pack/build, for both default packs in plain and ASan/UBSan builds. Production pins are not overridden. It checks every one of the 640 record bits at every phase, exact physical aliases, 24 alternative episode records, Christmas, 78 other original record identities and 21 genuine other-weapon source routes.
- Authentic linked record 451, selected Rear Mega Pulse 22/38, both directional remaps, both densities and all three creator contexts remain excluded. Recycling a stale record-270 slot clears its provenance without a rear resource lookup, and the real allocator/direction state equals its observer-stripped baseline.
- Retained 270/269/268 shared-head births, same-head mode1 births, record-local table/payload mutations, copied seals and restoration non-resurrection pass. Shared-cache payload corruption rejects every dependent HD draw.
- Enabled and renderer-disabled production builds pass the established strict warning profile. The source inverse restores all 156 original baseline files after removal of inherited observation hooks. This inverse count is separate from the 157 of 160 files unchanged by this addition.

ASan/UBSan use `halt_on_error=1`; leak detection is disabled and is not qualified. Full game builds use established warning suppressions, rather than an unsuppressed all-warning claim. Controlled draw calls use an observer stub and do not establish native compositor pixels.

## Fresh native qualification

All 38 baseline/candidate pairs passed using the exact reviewed source, existing assets and frozen private observers: 76 qualifying fresh processes, 9,600 logic ticks, 1,064 actual native game captures and 228 shop captures.

- Four main pairs cover Normal and Hard at actual native 2x and 4x (640x400 and 1280x800), with all five record-270 heads witnessed over brown terrain and clouds.
- Twelve symmetric missing/corrupt-resource pairs cover each head and the all-missing case on both difficulties. Each rejected head keeps its indexed identity; both all-missing cases have complete baseline/candidate native equality.
- Twelve prior-power pairs cover P1 through P5 and P6 mode 1 only on both difficulties, with no new admissions or changed original/HD drawing.
- Four 180-tick transition pairs cover mode switches, retained births across switches, fire stop and exact shot-free clear-frame equality.
- Two same-natural-seed Present repeat/skip pairs match their corresponding main cases in all 20 original streams, full startup state, RNG and birth ownership.
- Four density-4 pairs cover Normal/Hard at native 2x/4x: 277/278/77 are HD, while 183/182 remain indexed with zero observed cache or resource-open access.

Every qualifying pair compares all 20 original gameplay/input/collision/projectile/draw-order/indexed-image/palette/seed streams exactly. Every HD admission delta joins to a live exact-record-270 birth and its canonical phase. Full-density compositing checks cover integer alpha, owned footprints, later occlusion, clipping and unchanged outer regions; actual native captures match nearest-sampled final uploads. Wrong-channel-shift and colored Hard-scene controls reject incorrect pixel oracles. Native-size visual review retains the original warm palette and Hard lighting.

The original time-based RNG seed is never replaced. Two four-process main/Present cohorts and the remaining ordinary pairs begin in the same real second, with later processes waiting only before SDL initialization. The full 784-byte player startup image and all 5,016 RNG bytes are exact before/after waiting and across each cohort; all RNG words are independently reconstructed from the observed seed.

For diagnostic high-power acquisition, raw player snapshots are retained. Within a process the preset changes only byte 14, leaving the other 783 player bytes and all RNG bytes exact. Across separate PIE processes, only the two 8-byte lives-pointer fields at offsets 40 and 432 are represented by their independently verified own-player target offsets 12 and 406; all remaining 768 raw bytes are exact. No gameplay state is rewritten for this comparison.

One execution interruption occurred during an earlier Normal P3 pair: its baseline completed and its candidate stopped mid-run. Both original attempt records and all available bytes are retained separately, excluded from qualification. A new naturally seeded pair passed. There are 76 qualifying processes plus these two interrupted-attempt processes; completed qualifying pairs were not rerun.

The initial density-4 brown-background classifier omitted a classic terrain path that does not emit the HD scene trace. A separately reviewed, read-only supplement establishes the missing terrain provenance through exact retained indexed/palette/draw-stream parity and independently decoded original terrain pixels. Current-case exact-record ownership, complete exposure, fractional samples and native compositing checks remain required. Each original density-4 diagnostic failure and cohort record is retained; all four pairs are qualified on the same acquired processes without replaying games.

All archived binary/image observations from qualifying processes were losslessly reconstructed and byte-compared before raw replacement, then covered by final storage/recovery review. The interrupted candidate retains its available partial raw evidence. Ten strict production/observer builds and six zero-fuzz observer inverses pass, each restoring all 160 production source files. Independent final review confirms the frozen source, tests, artwork, runtime evidence and stated coverage.

## Acquisition and qualification limits

Ordinary fresh-start P6 purchase is not established. P6 costs 27,000 against opening funds of 10,000. Diagnostic P6 processes first genuinely purchase P4 for 8,250, retain 1,750 cash, then apply the disclosed private rear-power 4-to-6 single-byte preset before the first gameplay tick. P5 regression processes analogously use 4-to-5. No cash, seed, RNG, allocator, collision or shop logic is overridden.

This is bounded 120/180-tick first-level software-SDL native qualification, not full-level, hardware-GPU, performance, ordinary-P6-acquisition or Windows-package qualification. Public tests use synthetic fixtures; original game payloads, raw captures, private observers, binaries and process addresses are not included. All 7,123 accepted artwork/catalog files remain unchanged.
