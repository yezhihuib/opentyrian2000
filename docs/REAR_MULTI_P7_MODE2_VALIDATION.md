# Rear Multi-Cannon P7 mode2: bounded HD qualification

Baseline: `a54277a30811f5beb49afca3140b723ebeb0be47`, tree
`61d45a0f5111598ca4448da209f5c2ab4ea95e1d`.

## Exact renderer scope

Ordinary player 1, rear Multi-Cannon port 10 / bay 1, power index 6
(display P7), mode index 1 (display mode 2), physical normal-table record 271.
Its five-allocation budget and cyclic period are both 5. Canonical phases are
277, 278, 295, 294, 77; actual velocities are (-9,-2), (9,-2), (6,6),
(-6,6), (0,10), with birth X offsets -2, +2, +4, -4, 0.

The complete 80-byte record FNV1a64 is `fb03d1fdaa0f2c6e`; its SHA-256 is
`1e0fa572aeea693627cd059f794ac45b353694ec13d4dc0cd927e17cc3a8577d`.
The source adapter checks the entire record, normal bank identity, and the
record-local port selection `op[1][6] == 271`. Physical alias 1271 is excluded
even though its original record is byte-identical. Records 272–275 and their
physical aliases, wrong selected routes, alternate episode tables, Christmas,
generic/shared/linked consumers and indexed shadows remain excluded.

The existing first-level scope remains Normal physical level 9 and Hard
physical level 15. Existing record 260 stays mode 1. Prior admitted records
and the shared 277/278/77 assets retain their own birth identities; changing
current mode does not reclassify an existing shot. Observed-only 163/164 and
density8-only 182/183 remain unchanged.

Only four production files change: `rear_multi_p1.c`, `.h`, `_mirror.inc`,
and `_pins.h`. The remaining 156 production files are byte-identical to the
baseline, including gameplay, allocation, movement, collision, RNG, cash,
indexed images and shadow logic. Existing ID/velocity/pin prefixes are exact.
Drawable count grows 17→19, observed count 19→21; the maximum budget 5,
80 slots, 168 cells and original 32,060-byte bank size stay unchanged.

## Generated artwork and additive binding

The new 294/295 resources are a generated-only semantic twin-streak design,
using the accepted seven yellow/orange/red heat-field stops, rounded luminous
caps and smooth tapered tails. Two newly authored 9×10 members are displaced
(+3,+3), perpendicular to down-left travel. Original twin topology and the
12×14 canvas / anchor (0,0) are preserved without tracing original pixels or
masks. No original area or energy equality is claimed.

294 is directly rendered from SVG independently at density 4 and 8; 295 is
an exact full-canvas horizontal RGBA reflection at each density. The standalone
295 SVG comparison has separately disclosed antialias rounding variance and
is not its canonical payload. There is no casing, outline, gray border,
external halo, native1× intermediate or brightness compensation. The logical
top row stays empty, and visible twin components remain separate at all four
density/native-scale combinations.

Role 131 resources use keys 1310294 and 1310295. Four exact PNG/RGBA/HDR1
variants, four catalog-source PNGs and eight pack copies are additive. All
7,150 pre-existing non-catalog assets are byte-identical. The compact generated
source/output package and catalog add 37 paths. Missing or invalid resources
retain indexed rendering at the exact startup-selected density; there is no
cross-density fallback, hot reload or raw-ID promotion.

The new asset oracle validates the exact catalog inverse and old-asset
inventory, PNG/RGBA/HDR1/header/EOF equivalence, reflection, zero-alpha RGB,
native twin separation, isolated source-only rebuild, source regeneration and
tamper rejection. Four affected historical asset suites pass through an exact
new-family projection, preserving their previous acceptance oracles.

## Source and loader checks

- 13 strict C99 core suites passed both plain and ASan/UBSan: 26 runs.
  The new P7 mode2 suite has 2,265,242 checks per build, 180 cyclic
  prior/new-capacity designs, all 80×80 slot pairs, retained birth seals,
  ordinal 1–5 and rejected sixth, all 14 routes / 51 canonical phases,
  duplicate/recycled slots and cross-record 277/278/77 identity controls.
- The actual allocator/adapter/loader/decoder/wrapper fixture passes
  2,457,251 checks per build, including 608 malformed resource variants,
  all 640 record-bit mutations, source identity, density 4/8 and independent
  or combined missing294/corrupt295 isolation. Observer-stripped original
  allocator state is equal. Its drawing stub is not pixel qualification.
- Authentic private no-pin-override verification passes 658,000 checks per
  run, both Blue Four and Talon13 packs, plain and ASan/UBSan. It covers
  42 excluded shared records, 11 genuine foreign routes, 28 alternate
  episode4/5 payloads, Christmas source identity and linked22/38 directions.
  Original data is read in memory and never included in public tests.
- 15 independently compiled private core mutants are rejected.
- Strict uninstrumented enabled and RENDER_MIRROR_DISABLED builds pass:
  74 translation units each, zero warnings/errors under the established
  warning profile. The profile suppresses misleading-indentation,
  format-truncation and missing-field-initializers; disabled also suppresses
  unused-variable/unused-parameter. This is not an unsuppressed-all-warning
  claim. ASan/UBSan use halt_on_error=1 with detect_leaks=0; LeakSanitizer is
  not qualified.

## Actual compositor and offline native gate

The unchanged production compositor, original RLE blitter, allocator, movement
and wrapper are extracted into an offline fixture with a narrow test-only
admission shim. It reads authentic record/bank data only in memory and uses
synthetic scenery and palette anchors; it launches no game.

Strict and ASan/UBSan runs pass 402 single-volley rendered cases, 563 allocator/baseline
comparisons, 1,200 wrapper draws each with exactly one original RLE blit, and
32 actual SDL native2×/4× nearest outputs. Every pixel matches an independent
integer-alpha reference after each shot. Ownership checks include 621,600
original-covered / zero-HD-alpha visits, foreground restoration and original
shadow/brightness transfer. All five cyclic starts, partial capacities,
continuation and reversed slot order are covered.

All ten support pairs are measured from the final art. At age 1, only
277↔294 and 278↔295 intersect, by 17 samples per pair at density 4 and 47 at
density8. The center77 has zero HD/original support intersections despite
allocation-rectangle overlap. All ten age2 pairs are disjoint, and normal versus
reversed age2 outputs are byte-identical. Order-dependent age1 differences are
expected ordered alpha composition. Plain/sanitizer counts are 20,796,836 /
20,796,804; the difference is the 32 plain-only preview-save assertions.

These checks establish offline compositor interaction and native sampling,
not ordinary acquisition or actual game difficulty/lighting acceptance.

## Bounded actual-game Normal diagnostic

One pair used the frozen baseline/candidate source trees with the same additive
asset pack, physical Normal level 9, density 8 and actual SDL native2× output
(640×400). Both processes completed 180 original ticks. The predeclared 24
capture ticks were 1,59,60,61,62,63,64,65,66,67,68,69,70,76,82,88,94,99,
100,101,119,120,130,179. Fire was held through119 and stopped at120; mode
changes were requested at60/100. The fixed movement crossed brown terrain
and cloud. There was no gameplay retry or capture reschedule.

The actual shop path bought Rear Multi-Cannon and upgraded to P4 for 8,250,
leaving 1,750 of 10,000 cash. A private one-byte diagnostic preset changed rear
power4→7. The other 783 player bytes and all 5,016 RNG bytes remained exact
across that preset. Across processes, the complete 784-byte player state was
compared after proving and canonicalizing only two self-relative lives
pointers; each startup MT state was independently reconstructed from its
observed natural seed. This establishes a controlled P7 diagnostic, not
ordinary P7 purchase, progression or balance acceptance.

All 20 original observation streams match byte-for-byte. Exactly 407 newly
admitted draws belong to normal record271; all 690 observed protected260
head draws and other protected/generic/shadow observations remain unchanged.
All five phases are observed. Independent integer-alpha recomputation matches
290 selected patches across the two processes, and all selected actual SDL
frames match the real upload samples. The same complete five-phase birth at 61
provides ages 1/2 at 62/63: only the two expected outer/twin pairs overlap at
age1 (47 density8 samples each); all ten pairs are disjoint at age 2. Each of
the five phases has a full-support brown witness and cloud witness. Eighteen
selected record271 draws survive the switch back at100; fire cessation and
shot-free 179 match exactly. Native frames passed visual review: distinct warm twins, readable center, smooth edges and no
sampled stray alteration.

### Retained analysis failure and correction

The original frozen validator predicted first target draw 65 and required
selected earlier frames to remain equal. That extra prediction failed. Original
power gating produced insufficient-energy returns at 1/2/3/11 and shifted
successful births; the first valid record271 draw was 62. The controller's
failed-cohort record, frozen validator, capture plan and all observations are
preserved. A separate read-only reanalysis changed only this pre-target equality
boundary to the first actual already-validated target draw, redirected its
report, and disclosed the false positive. Every substantive admission, parity,
alpha, overlap, background and cessation criterion stayed unchanged. An
independent reviewer inspected that difference, reran the reanalysis and
obtained a byte-identical receipt. This was an analysis correction on retained
data, not a new game or a hidden failed run.

Selected mixed260/271 and multiple-birth patches demonstrate coexistence.
Their cross-volley rectangles/support do not intersect; this diagnostic and
the single-volley offline fixture do not establish general cross-volley
pixel-overlap behavior. Runtime owner bytes were retained but not semantically
certified; restoration and reversed-slot proofs are the separate offline cases.

## Complementary Hard diagnostic

One corrected baseline/candidate pair completed physical Hard level 15 at density 4
and actual SDL native 4× (1280×800), with the same 180-tick control schedule and
24 fixed capture ticks. Both private diagnostic copies select density 4 through
the same reversible presentation-only startup override; the production default,
CLI and gameplay are unchanged. The exact strict-built C observers and binaries
were reused, with their original source inverses and hashes reverified. This
does not introduce a shipped density-selection setting. A fresh pair used only
its own naturally seeded baseline/candidate observations.

The pack has no density 4 terrain resources, so this run's brown/cloud scenery
uses its existing indexed fallback. Current terrain identity and decoded-in-memory
original tile support establish witnesses from this run; no density 8 scenery,
previous-run pixels or previous-run positions were substituted.

Both processes pass the same genuine-P4/one-byte-P7 diagnostic protocol and all
20 original-stream, full startup, RNG and preset parity checks. Exactly 407 new
normal-record-271 admissions and 690 protected record-260 head observations are verified.
There are 290 independent integer-alpha and selected final-output patch checks
(86 baseline, 204 candidate), including 118 selected target patches. The same
complete five-phase birth at 61 gives ages 1/2 at 62/63, with 17/17 density-4 support
intersections at age 1 and all ten pairs disjoint at age 2. Each phase has a full-
support brown and cloud witness; 18 selected target draws remain after switch 100.
Stopped fire and shot-free 179 are exact.

### Original Hard lighting and native output

The independently verified original sequence is ordinary output at tick 0,
then night transfer on ticks 1–179. Source initializes the night flag off and
samples output mode before processing the time-0 level event that enables it;
there is no later night-mode event. The oracle verifies the exact 264×184
transfer region on every tick: source x=24..287/y=0..183 to destination
x=0..263/y=0..183, or 8,743,680 indexed pixels per process. This indexed proof
excludes the 56-pixel sidebar and bottom 16 rows.

Separately, an independent RGB residual oracle uses observed source/destination
palette indices, final pre-transfer canvas and owner bytes. It matches 181,888
selected final-output pixels in the baseline and 476,096 in the candidate, using
RGB shifts 0/8/16. These are 290 selected patches, not a claim that every composed
pixel or every owner transition was independently recomputed. All selected
1280×800 native SDL frames match the real uploaded image pixel-for-pixel:
density 4→native 4× is stride 1, offset 0. Every target phase has a transfer-exact
selected patch. The combined observations include lit and unlit support and
nonzero sensitivity to incorrect channel shifts and grayscale palette anchors;
each individual phase is not required to exercise every lighting condition.

Native visual review passed: readable twin caps and soft edges on brown/cloud,
proper original night attenuation, retained births and the clear final frame.
No brightness compensation or production adjustment was made after either run.

### Preserved Hard preflight failure

The first complementary attempt completed the baseline's 180 ticks, but the
frozen validator incorrectly required night-transfer output on every tick.
Original Hard level 15 legitimately uses ordinary output at tick 0 and night
transfer from tick 1. The assertion therefore stopped the controller before
candidate release; that candidate had only seeded and remained pre-SDL when
terminated. It did not complete gameplay and cannot supply paired evidence.
The original freeze, failed cohort, baseline observations and gated candidate
state are preserved. An explicit review decision authorized one replacement
pair with the original tick-0 branch independently verified, all remaining
checks and fixed captures unchanged, and no production source or art changes.
This is a disclosed validator-repair retry, not an additional test matrix or a
retroactive pass for the failed cohort.

## Public reproduction and evidence limits

From the repository root, public checks requiring no original game-data files:

    python3 tests/run_rear_multi_p1_core_tests.py
    python3 tests/run_rear_multi_p1_adapter_tests.py
    python3 tests/test_rear_multi_p1_source_inverse.py
    python3 tests/test_rear_multi_p4_mode2_assets.py
    python3 tests/test_rear_multi_p5_mode1_assets.py
    python3 tests/test_rear_multi_p5_mode2_assets.py
    python3 tests/test_rear_multi_p7_mode1_assets.py
    python3 tests/test_rear_multi_p7_mode2_assets.py

Core/adapter checks require a C99 compiler with ASan/UBSan. Asset checks use
Python/Pillow and the pinned Node/Sharp rendering environment documented by
the artwork package; different rasterizer versions deliberately fail closed.
Authentic-data, actual-compositor and actual-game checks use separately held
original inputs and private observations. Their detailed logs, state dumps,
source records, indexed art, raw captures, seeds and diagnostic builds are
excluded from this public change. Generated art and synthetic public fixtures
are the only new visual/fixture payloads.

The supported claims are the exact source/asset gates and the bounded diagnostic
pairs reported above. Genuine P7 progression, long play, a full difficulty ×
density × scale matrix, performance benchmarking, actual-game resource-failure
injection, cross-volley pixel overlap and semantic final-runtime-owner proof
remain outside this qualification. No source, shared-art or gameplay change
was made in response to a capture or analysis result.

### Checkpoint hashes

The following SHA-256 values identify retained evidence; the evidence itself
is not part of the public repository:

- Scope evidence: `4be582c200d0afb097109e281012474e1fc0963a4ea05407686725e5f9455682`
- Source tests: `0708909bd45f9c3049e4c53488e3a465a286282042034d36843e008dc6e556ea`
- Authentic input checks: `af8d4a7156003a4011b44b8b42086e7437d0bbf34b859c359f439912dfc6619e`
- Strict production builds: `e08a26ca30608261d15152fa20276451c9181658241977c342f65e1e2e187c08`
- Bound source/art freeze: `2cdcd98b1ced914022304322d4107326bb2b4162acdcf4e4cd4bfe6fbfc91618`
- Final five asset suites: `df26e661c57b43983f73db4b830f5757047c0a21147ec4ed4dd1578c33880e22`
- Normal prepared runtime freeze: `deb20ae3cd9a8dd7c0f657f500e6cbca521912c8eb32bc0a78da71ae05007b00`
- Normal retained-data reanalysis: `dd09a4ce8021d82aa4afab496387638347bd00871cf9c44210b889ccb0f43c92`
- Normal independent runtime review: `edffe0c0f23e1e56c706ff1fac1c968af6361d4ea3a29912c4bf0c99560d93e4`
- Actual compositor receipt: `7fbaad4e521c5179cea20fb016282c1aef146efcd0281360cc02eed37f96c6d5`
- Actual compositor report: `f1fd25ffe886113e72dde906fc30e636073083fbaf1f164591bfd33b7b6be1ee`
- Hard initial failed-attempt freeze: `e2a3717cff2abb147ab492181a594cedfcd87440233be68e28f038799c6b1915`
- Hard initial failure source review: `53a0ecb421158ec08768df6932c81b839aa05937a6ce0bedff4fce7d98b89542`
- Hard corrected replacement freeze: `1c96930826187b9028af3e157bb31794c0b356bda10fa6707aa221700bf27992`
- Hard corrected replacement validation: `8285d74870c065beec0ed697edf8edcc78a6d2556ac26377b38dfddda9a8222f`
- Hard independent replacement runtime review: `2fd4955a31556e599583c0751872c1399e981338149d5cf7f8332890999720b6`
