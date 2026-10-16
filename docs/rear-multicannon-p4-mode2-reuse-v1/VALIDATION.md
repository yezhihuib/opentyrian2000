# Rear Multi-Cannon P4 mode 2: bounded three-head reuse and five-observation ownership

Baseline: `3b398429ffa4f3e9250d1bd02cc22dab16fc28ad`.

Status: **PASS: bounded P4 mode 2 completion, independently reviewed.**

## Exact scope and pass-through

This extension admits only player-one rear Multi-Cannon 10, power 4, mode 2,
record 268 in the existing episode-one Normal level 9 / Hard level 15 scope.
The full 80-byte record pin is `b0d0e52cca9ff499`, including unused tails. The
conditional port mapping `op[1][3] == 268` cannot affect older record admissions.
Shared raw identities do not establish ownership. Byte-identical record 1268,
other source tables, Christmas banks and all unqualified consumers remain excluded
from the new rear role; their existing unrelated generic rendering is untouched.

All five original phases are validated in order: 163, 164, 183, 182, 77.
The first two are valid pass-through observations. They consume the original
allocation ordinal, finite budget and all-prior-slot uniqueness, clear any
recycled old birth, and keep the call alive. They create no dedicated rear birth
and cannot invoke its resource loader. Both existing generic normal heads and
shadows of 163/164 remain byte-exact on their original rendering paths.

The last three phases may mint record-owned births. Both the budget and cyclic
period are 5, independent of the power index. Partial slot exhaustion advances
original phase only after a successful allocation, so any phase, including 77,
can appear at any ordinal of a later call. Malformed pass-through observations
cancel the remaining grant just like other invalid observations; earlier valid
births in distinct slots survive. Invocation token, tick, original ordinal,
source/table/live-shot pins, duplicate-slot handling and generation rules remain
authoritative. A forged pass-through birth cannot draw.

Flying heads retain their birth record/mode across ordinary mode changes; the
currently equipped mode does not rewrite their identity. Existing P1–P3 and
P4 mode 1 tuples/resources remain unchanged. Only four renderer-owned rear
provenance files change. Gameplay, allocation, RNG, INDEX8 writes, palette,
collision, generic loader, shadow code and original scene order stay exact.

## Accepted-art reuse and density

The original 182 source is a whole-canvas vertical reflection of 163, and 183
is the corresponding reflection of 164. The new generated-only package applies
that same rigid mapping to the accepted front Multi-Cannon v3 PNGs at density 8.
The canvas remains 12×14 with anchor (0,0). All RGBA samples, alpha histograms
and premultiplied RGB totals are preserved exactly. No sample clips and no art
is generated, redrawn, resampled, blurred or brightness-normalized.

Each accepted smooth diagonal touches 60 logical cells versus the original 43,
adding 17 within the exact original bounds. The inherited shape is not an
original-mask trace. Native nearest sampling after reflection may choose a
different subpixel phase, so native brightness is measured rather than normalized.
ART_REUSE.json records exact full-density and native-sampling metrics.

Only role 131 keys 1310182 and 1310183 receive new density 8 resources. Their
four pack copies plus two source PNGs are registered; the previously published
77 density 4/8 resources remain byte-exact. Generic 163/164 resources stay exact.
At public manual-HD density 8, both P4 modes have HD normal heads throughout.
At private diagnostic density 4, 182/183 and generic 163/164 retain their classic
fallback, while 77 may use its existing density 4 head. No upward density
fallback or density 4 diagonal artwork is introduced. The dedicated loader
rejects unsupported densities before any cache/file access.

All 7,048 pre-existing non-manifest assets are unchanged. The catalog is purely
additive; removing the new family and resource rows restores the baseline bytes.
Older package scope descriptions remain historical records of their introduction;
record 268 reuse is qualified here. Both default packs now contain 597 entries.
The aggregate verifier passes 3,430 HDA entries and 609 exact source PNGs across
18 packs. A fresh relocated builder reads only the two accepted PNGs, decodes
pinned RGBA, and reproduces every PNG/RGBA/HDA byte. Corrupt input fails before
output. Original game data, source masks and palettes are never builder inputs.

## Frozen qualification

The immutable freeze contains 160 source files, 7,066 assets, 47 public test
files and Makefile. The original 156-file source projection is exact. All old
record/source/resource pin prefixes are preserved; only new finite entries are
appended. The new mode 2 core passes 105,461 assertions per plain and ASan/UBSan
build. The actual synthetic adapter/allocator passes 471,760 per build, and
private authentic source/table/art/allocator qualification passes 454,718 per
build. All seven core suites, strict enabled/disabled production builds and all
four rear asset tests pass.

Authentic qualification uses all 1,638 physical records per source table and
the original maximum record ID 1,818. It includes 62 genuine excluded record IDs,
including byte-identical 1268, alternate-table records and Christmas sources.
Every new record byte is pinned. Tests cover all cyclic starts, partial capacity,
pass-through at every ordinal, all-prior duplicate slots, power failures,
slot reuse, malformed observations, map isolation, forged pass-through births,
retention, missing/corrupt exact-density resources and cache restrictions.

## Fresh native runtime and independent review

The completed matrix passes 24 fresh paired cases, 48 qualifying processes and
6,000 original logic ticks: Normal/Hard at native 2×/4×, four resource-negative
variants per difficulty, P1–P3 regressions, transition/clear, repeated/skipped
Present and private density 4 diagnostics. There are 736 native gameplay and
144 native shop captures. Four baseline-only schedule-preparation processes
remain separate; every candidate qualification process completed on its first
launch. Ordinary menus purchase P4 for 8,250, leaving 1,750 before later ordinary
pickups. Ordinary movement and mode input provide brown/cloud exposures. No
seed, loadout, gameplay-state or phase overrides were used; each independently
launched pair observed equal original time(NULL) seeds.

All 20 original-state streams and original draw order are pairwise identical,
including gameplay, RNG, INDEX8 surfaces, palette, collision, allocation and
shot state. The first 60-tick mode 1 segment is baseline-exact. Generic 163/164
normal-head and shadow draw records remain exact. The four main pairs contain
1,060 newly owned HD head draws, each linked to its exact record 268 birth.
Every main head has full authored-support brown and cloud witnesses at both
native scales and difficulties. Fractional-alpha composition, original final
Normal/Hard transfer and native sampling are recomputed exactly; zero changes
escape admitted original/authored support. The original dark Hard filter remains.

Missing 182, corrupt 183, both missing, and all three target resources missing
fall back correctly. The last case also intentionally removes the old 77
resource, and its prior mode 1 fallback is explicitly accounted for. Both
private density 4 diagnostics keep 182/183 and generic 163/164 classic while 77
uses its existing density 4 art. P1–P3 regressions preserve both original modes.
Transitions retain earlier mode 1 births after switch 60 and retain natural
mode 2 births of all three IDs, including 77, after switch 100. Clear tick 179
is baseline-exact. Repeated/skipped Present does not advance shot ownership;
no native readback is claimed at intentionally skipped ticks 32 or 80.

Natural ship-bound occlusion, viewport clipping, insufficient power and slot
reuse are observed. Whole-run ID-filtered occlusion counters include the prior
mode 1 ID 77; they are not exclusively new record 268 observations. Independent
Normal 2× admission-filtered evidence separately confirms 2,775 later fractional
writes, 5,071 clipped points and 1,201 ship-bound writes from new mode 2 heads. Natural partial capacity, all cyclic starts and authored
head/head overlap are not claimed. Those are separately controlled tests,
including the independent 120-case actual-compositor overlap/occlusion matrix.
All six reversible observer projections restore source exactly with zero fuzz
or offset. Strict production and diagnostic builds introduce no warnings;
the 15 disabled-mode diagnostics are unchanged from baseline.

RUNTIME.json records the final numerical evidence and qualifications. Independent review passes source/ownership, all 24 runtime pairs, all 368
candidate native frames, resource fallbacks and density diagnostics. Its separate
authentic adapter passes 354,500 checks per plain/ASan+UBSan build; the public
adapter passes 471,760 plus 352 malformed variants. INDEPENDENT_REVIEW.json
records the full disposition. Final archive and remote byte checks are separate
publication gates.

## Reproduction and limits

From the repository root:

    python tests/run_rear_multi_p1_core_tests.py
    python tests/run_rear_multi_p1_adapter_tests.py
    python tests/test_rear_multi_p1_source_inverse.py
    python tests/test_rear_multi_p3_mode1_assets.py
    python tests/test_rear_multi_p4_mode1_assets.py
    python tests/test_rear_multi_p4_mode2_assets.py
    python prototype/build-rear-multicannon-p1-art.py
    python prototype/build-hd-assets.py

P1-prefixed names are retained for compatibility. Public tests use synthetic
fixtures; original data, decoded arrays, observers and gameplay captures remain
private. Missing art falls back at draw time without invalidating a legitimate
call observation. No disk hot-reload or performance claim is made. Linux SDL
software/dummy testing does not qualify Windows, physical GPU or full campaign.
ASan/UBSan use detect_leaks=0; no LeakSanitizer qualification is claimed. Natural
capacity, head overlap and retention witnesses are distinguished from separately
labeled controlled tests in the receipts.
