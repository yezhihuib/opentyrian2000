# Rear Multi-Cannon P7 mode 1 validation

Status: PASS for the bounded controlled-source, compositor and native software-rendered qualification below. Publication and remote verification are separate operations.

## Exact change

Baseline: published commit `a4d01b3184ff94ecd99a9fdb03e6ee6647998e67`, tree `35efc54f0637b2d5177f1fc3fb881c8ad43cb467`.

The only new admission is ordinary player 1, rear port 10/bay 1, power index 6, mode index 0, exact normal-bank record 260 selected by `op[0][6] == 260`. The successful-emission budget and cyclic period are four, with phases 277, 278, 297, 296. The full 80-byte record pin is `cd5735a99bbecb93`. Byte-identical physical alias 1260 and P7 mode 2 record 271 remain excluded.

Only four production files change: `rear_multi_p1.c`, `rear_multi_p1.h`, `rear_multi_p1_mirror.inc` and `rear_multi_p1_pins.h`. The other 156 production source files remain byte-exact. HEADS grows from 15 to 17 and OBSERVED from 17 to 19; MAX_BUDGET remains 5. Earlier route and pin prefixes remain intact. Gameplay, allocator, movement, RNG, collision, shop logic, generic renderer, wrapper hooks, original shadows and Hard lighting code are unchanged.

## Exact reflected artwork

New 296 is the full-canvas vertical reflection of accepted, already-composited 277; new 297 similarly reflects 278. Both densities 4 and 8 retain the 12x14 logical canvas and anchor (0,0). Every RGBA sample, including zero-alpha samples, is permuted exactly. No component ordering is reconstructed, and no tint, redraw, resampling, blur or brightness correction is applied.

The four variants preserve the full sample multiset, alpha sums and RGB-times-alpha totals. Native nearest sampling can select a different source residue after reflection: measured native alpha differences are -0.543% to +0.438%, with no compensation. Full-density energy preservation is not a claim of identical downsampled brightness.

The addition contains 28 asset paths: a 16-file reproducible artwork package, four catalog source PNGs and eight HDR1 copies across the two default packs. The catalog is additive. All 7,122 pre-existing non-catalog assets are byte-exact. Validating and removing only the pinned P7 additions recovers the exact baseline catalog. The [artwork package](../assets/hd/artwork/player-rear-multicannon-p7-mode1-reflections-v1/README.md) records input/output hashes, payload headers and a standard-library-only builder. Two independent relocated rebuilds produce byte-identical outputs; seven bounded invalid-input/output cases reject safely.

## Controlled verification

- Twelve core suites pass strict C99 plain and ASan/UBSan builds, 24 executables. The P7 suite performs 1,941,518 checks per build, including all four cyclic starts, 100 prior/new capacity designs, all 80x80 ordered slot pairs, thirteen retained routes and 46 coexisting phases.
- The actual-source allocator/adapter/loader/wrapper passes 1,781,960 checks per build and 544 malformed-resource variants. All 640 record bits are checked at each phase. Missing 296 and corrupt 297 leave 277/278 functional and preserve rejected indexed draws. Both stored densities are covered.
- Private original-data adapter verification uses unmodified production pins and holds original inputs only in memory. Both default packs pass plain and ASan/UBSan runs, 1,640,533 checks per pack/build. Checks include 24 shared records, nine genuine foreign routes, 26 alternate payloads, Christmas, exact alias 1260 and linked/shared 22/38 consumers.
- Fourteen isolated private core mutants compile strictly and are rejected by explicit P7 assertions. No mutation is retained in production.
- Seven public rear-art asset suites pass, including the historical catalog/inventory checks after an exact, independently pinned P7 projection.
- Uninstrumented enabled and renderer-disabled production builds each compile 74 translation units from the exact frozen source with zero warnings/errors under the established strict profile. The profile uses `-Werror` with existing misleading-indentation, format-truncation and missing-field-initializer suppressions; the disabled build additionally suppresses unused-variable and unused-parameter warnings. No unsuppressed all-warning claim is made.

ASan/UBSan run with halt-on-error; leak detection is disabled and LSan is not qualified. Public synthetic source tests do not themselves establish native game pixels.

## Actual compositor and allocation proof

A separate offline harness uses the actual unchanged C compositor, indexed blitter, allocator, movement/draw source, wrapper and SDL nearest renderer. It supplies a disclosed test-only role admission; its assertions are not passed off as production route qualification.

Each strict plain/sanitized executable covers 256 rendered cases and 428 allocator comparisons against an observer-stripped baseline. Independent reruns pass 20,714,485 checks per build. Native 2x/4x output is checked at both densities. Tests cover every original-covered zero-alpha point visited by those cases, all cyclic starts, natural and reversed slot order, partial allocation, ownership restoration, later foreground occlusion and shadow transfer.

At age 1, same-side pairs intersect in exactly 76 density-4 samples or 250 density-8 samples. At age 2 they are disjoint. Slot order legitimately changes age-1 native pixels; it is preserved rather than normalized. Reversed-slot, ownership/restoration and original-covered zero-alpha stress evidence comes from this controlled compositor harness. The first pair retains owner bytes without semantically asserting them. Extension validators use observed owner bytes as inputs to finish-transfer checks; ownership lifecycle and restoration correctness are qualified by the separate offline proof, not inferred from those runtime bytes.

## Fresh bounded native qualification

Five baseline/candidate pairs pass: ten fresh processes, 1,800 logic ticks, 240 actual native game captures and 30 shop captures. Four ordinary density-8 pairs cover Normal and Hard at native 2x and 4x (640x400 and 1280x800). A fifth Normal/native2x pair uses a symmetric pack with 296 missing and 297's magic corrupted; it reuses the first pair's unchanged binaries.

The four ordinary pairs each record 620 new exact-record-260 HD draws. The negative pair records 310, exclusively 277/278. The bounded plan completed without interrupted attempts or repeated game runs.

Every pair compares all 20 original input/gameplay/collision/projectile/draw-order/indexed-image/palette/seed streams byte-for-byte. Every new HD draw joins to a live exact-record-260 birth and canonical phase. Record 271, original shadows and protected consumers have no new admissions. The ordinary pairs witness all four heads over actual brown terrain and clouds with complete surviving authored support and fractional alpha. The negative pair retains 277/278 HD ownership, keeps 296/297 indexed, opens each resource only once, and does not switch density or retry failed resources.

The ordinary input schedule fires through tick 119, switches mode at 60 and 100, then stops firing at 120 and ends at 180. Retained mode1 births remain correctly owned after the first switch. Player-shot-free frame 179 is exactly equal. Actual age-1 same-side overlap is 250 density-8 samples; age-2 examples are disjoint. These age-1 and age-2 witnesses come from separately traced volleys, not consecutive captures of one birth.

Independent integer-alpha checks cover retained pre/post head patches. All 240 actual native game images match the corresponding center-nearest samples of real SDL uploads. Extension checks additionally confine selected native differences to exact-record-260 support and retain identical HUD, outer region and all three shop images. Hard qualification reproduces the original Normal15 indexed/palette anchors, cone branches and integer residual transfer at actual native coordinates. Colored wrong-channel-shift and gray-palette controls reject incorrect transfer oracles. Native-size visual review accepts the reflected warm heads, age overlap/separation, brown/cloud contrast and Hard dimming.

Four private observer builds each compile 74 translation units; every zero-fuzz observer inverse restores all 160 exact production source files. The baseline is the canonical published Git object, not a stale checkout. Both sides of each pair use the same additive pack or same negative variant. Two fresh processes naturally begin within one time(NULL) second; only the candidate waits after original seeding and before SDL until its baseline exits and validates. There is no seed override, post-release timing gate, replay or automatic retry. Full 784-byte player and 5,016-byte MT state are checked around startup, and every MT word is independently reconstructed from the original seed.

## Acquisition and limits

These are diagnostic P7 runs, not genuine fresh-start P7 purchase qualification. Each process first genuinely purchases P4 for 8,250, retaining 1,750 cash, then applies a disclosed private P4-to-P7 preset before gameplay. Within each process this changes only byte 14 of the 784-byte player image; the other 783 bytes and all RNG bytes stay exact. Across separate PIE processes, only two lives-pointer fields are represented by their independently verified own-player target offsets; the other 768 raw bytes compare exactly. No cash, shop rules, allocator, collision, seed or RNG is overridden.

Density 8 has bounded actual-game coverage. Density 4 is qualified by exact asset/loader tests and actual C-compositor/SDL offline checks at native 2x/4x; no density-4 game run is claimed. Earlier powers are covered by controlled source/adapter regressions, not a repeated runtime matrix. This is 180-tick first-level software-SDL qualification, not full-level, hardware-GPU, performance, ordinary-P7-progression, LSan or Windows-package qualification. Public files contain synthetic test fixtures, authored artwork and sanitized results only; original game payloads, decoded masks, raw captures, private observers, binaries and process addresses remain private.

## Public verification commands

Run from the repository root with Python3 and a C99 compiler:

    python3 tests/run_rear_multi_p1_core_tests.py
    python3 tests/run_rear_multi_p1_adapter_tests.py
    python3 tests/test_rear_multi_p7_mode1_assets.py

The core and adapter scripts run both plain and ASan/UBSan executables. The adapter uses synthetic fixtures and does not require SDL or original game data. Rebuild instructions for the four reflected resources are in the linked artwork README. Private original-data and native runs require separately held game data and are not reproduced by these public commands.
