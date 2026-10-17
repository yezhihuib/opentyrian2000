# Rear Multi-Cannon P9 mode 1: exact six-shot HD reuse

Baseline commit `24e1557869198b8dfa3cba856600caeb80c3f4c8`, tree
`cae9690193a26f8f59cc141d0f57386dc640ef68`.

## Exact renderer admission

Ordinary player 1, rear Multi-Cannon port 10 / bay 1, power index 8
(display P9), mode index 0 (display mode 1), physical normal-table record 262.
The allocation lease and cyclic phase period are exactly 6, with phases
277, 278, 297, 296, 41, 3. Birth offsets are (-2,0), (2,0), (2,0),
(-2,0), (0,0), (0,0); actual velocities are (-9,-2), (9,-2), (9,2),
(-9,2), (-10,0), (10,0). Original repeat remains 6.

The full 80-byte record FNV1a64 is `5c8e78c68b542a04`; SHA256 is
`a01d0ad1a25bd953954059741705208d0796bcf7dcda53c0d2a8bc831adb58a4`.
The adapter additionally requires record-local `op[0][8]==262` and retains
the original port power-use check of 40. Byte-identical physical alias 1262,
wrong selectors, later powers, alternate episode tables, Christmas banks
and generic/shared/linked consumers remain excluded. Opposite P9 mode 2
record 273 remains unsupported CLASSIC, including its raw 298/299 phases.
The existing first-level scope is unchanged: Normal physical 9 and Hard
physical 15. Indexed shadows retain their original path.

Maximum used-slot storage remains 7. Record 262 admits six valid emissions
and rejects a seventh; all 16 earlier routes retain their exact budgets,
including 261=6 and 272=7. Retained births keep their original record, mode,
phase, raw ID, generation and slot identity across later calls or mode switches.

Only three production files change: `src/rear_multi_p1.c`, `_mirror.inc`
and `_pins.h`, alongside 15 changed or added test files and this document.
The other 157 production files, all 7,188 assets, the catalog and Makefile
remain byte-exact. Drawable 19 / observed 21 IDs, velocities, source and
RGBA pins, slots 80, cells 168 and the 32,060-byte normal bank are unchanged.
One full-record pin is appended, for 17 routes and 17 record pins.
Observed-only 163/164 and density 8-only 182/183 retain their previous behavior.

## Unchanged artwork

All six existing generated shapes are reused at densities 4 and 8,
including all 24 relevant HDA copies in both accepted packs and 12 pinned
source PNGs. Decoded PNG pixels match their HDA payloads. No new artwork,
mask, palette, resampling, reflection, catalog entry or fallback density
is introduced. Missing/corrupt resources remain isolated to the affected
head and density. Original pixels and masks are not new art inputs.

## Source, adapter and production tests

- All 16 strict C99 core suites pass plain and ASan/UBSan, 32 runs. The
  new mode 1 suite passes 2,846,496 checks per build, including 294 cyclic
  partial-continuation designs, capacities 0..6, every 80×80 slot pair,
  exact sixth admission/seventh rejection, birth seals and all 17 routes /
  70 canonical phases.
- The actual allocator/adapter/decoder/loader/wrapper fixture passes
  6,433,197 checks per build, plain and ASan/UBSan. Coverage includes
  608 malformed resource variants, all 640 record-bit mutations at each
  of six phases, record-local failure isolation, gameplay-state equality
  against the observer-stripped allocator, retained earlier routes and
  six-head missing/corrupt resource cases at d4/d8. Its draw stub does not
  establish pixel quality.
- Authentic production-pin tests pass 1,174,442 checks in each of four
  runs: both accepted packs, plain and ASan/UBSan. No pin override is used.
  Coverage includes all 17 routes, 56 excluded shared records, 10 genuine
  alternate mappings, 34 alternate episode payloads, aliases 1261/1262,
  Christmas/source revocation, linked 445/451 and resource-failure isolation.
  Record 273 and raw 298/299 stay generic. Authentic zero-energy rejection
  emits nothing and preserves earlier births; a forged zero-cost map
  remains renderer-ineligible.
- All 20 strictly compiled private core mutants are rejected, including
  wrong five/seven-shot 262 budgets, period/phase errors, prior-budget
  changes, alias/opposite-mode admission and forbidden 298/299 promotion.
- The source inverse and exact delta contract pass. Enabled and
  RENDER_MIRROR_DISABLED uninstrumented production builds each compile
  74 translation units with zero warnings or errors under the inherited
  strict profile.

ASan/UBSan run with halt-on-error and leak detection disabled; LeakSanitizer
is not qualified. Production warning suppressions are misleading-indentation,
format-truncation and missing-field-initializers; the disabled build also
suppresses unused-variable and unused-parameter. This is not an
unsuppressed-all-warning claim.

## Actual compositor before integration

The offline fixture runs source-extracted production allocator, movement,
wrapper, indexed RLE blitter, alpha compositor and ownership transfer on
synthetic scenery. Experimental 262 art dispatch is narrowly shimmed only
after authentic record/phase/slot/raw/position/shot-field observations.
The unchanged baseline ownership core still rejects 262 and alias 1262.
No game is launched and original data stays in process.

Each strict plain/sanitized executable passes 1,442 rendered cases,
883 allocator/baseline comparisons, 5,040 actual draws, 80 actual SDL
nearest native 2×/4× output comparisons, 40 foreground/restoration and
40 original-shadow/brightness cases. Every compositor pixel and ownership
byte agrees with independent ordered integer-alpha arithmetic after every
draw, including 2,584,680 original-covered samples with zero authored alpha.
Plain and sanitized check counts are 52,076,475 and 52,076,395; the difference
is 80 plain-only saved-preview assertions.

All 15 unordered phase pairs at ages 1–5 and both densities are checked:
150 measurements. Numbers of pairs with nonempty indexed/HD-alpha overlap
are 6, 4, 4, 4, 0.
Age 1 adds 277/296 and 278/297 to the four pairs 277/41, 278/3, 297/3 and
296/41 that persist through age 4. All indexed/HD support pairs are disjoint
at age 5, although allocation rectangles can still overlap. Normal/reversed
draws retain expected ordered-alpha differences through age 4; all eight
native age 5 order pairs are byte-identical. Reverse iteration is artificial
stress, not a production reordering.

A separate 360-case mixed-birth supplement covers older 262/261/258,
gaps 1/2/7, new ages 1–5, both densities, both orders and both backgrounds.
Per build it passes 3,600 draws, 720 native 2×/4× comparisons, 151 allocator
comparisons, 4,560 movement comparisons, 1,440 retained identity checks and
360 each of foreground/restoration and original-shadow/brightness checks.
Accepted 261 receives four available slots and genuinely emits its first
four phases; accepted 258 emits 41/3. Their production birth identities
remain intact through the later experimental 262 call. Gaps 1/2 are
synthetic direct-call stress; gap 7 is cadence-consistent with repeat 6.
Actual lifetimes remain valid through maximum older age 12. Initial power
900 is the source ceiling; normal calls debit 40 each, with no recharge or
energy override. Pixels and HD-owner bytes match independent oracles.

Independent pre-integration review reparses the authentic record and alias,
verifies existing record/source pins, extraction and art equality, recomputes
all 150 intersections, and independently reconstructs all 80 saved native
frames, 51,200,000 pixels, byte-for-byte. Contact sheets, actual BMPs and
exact native crops were inspected across densities/scales/backgrounds/orders:
compact early fans open gradually and separate at age 5. The twin horizontal
41/3 shapes remain recognizable; no visible clipping, dark fringe, rectangular
contamination or original-sprite leak was found. Mixed surfaces remain in
memory, so no mixed screenshot visual review is claimed. These are synthetic
offline previews, not gameplay or purchase evidence.

Independent source/harness review verifies the frozen source, authentic
records, literal route/phase oracles, all 20 mutant failures and strict build
receipts. The actual built-input review also verifies both instrumented source
copies, exact observer inverse restoration, binaries, dependencies and the
predeclared one-pair capture policy before the separate launch release.

## Actual-game diagnostic

One baseline/candidate pair completed on the first Normal level at native
2× (640×400), using density 8 art. Both fresh processes exit successfully
after 180 gameplay ticks with 32 gameplay and three shop captures each.
All 20 original trace streams, four full startup streams and player/RNG
state match. The 902 new replacement draws belong solely to record 262;
all 580 opposite 273 head draws remain CLASSIC, and every other protected
draw/style/shadow remains unchanged.

The menu genuinely buys P4 for 8,250 from 10,000, leaving 1,750. A private
post-shop diagnostic changes only the rear-power byte from P4 to P9;
all other 783 player bytes and 5,016 RNG bytes are unchanged. Cross-process
player pointers are independently proved as self-relative relocations.
This is explicitly not a genuine P9 purchase or progression test.

Both processes use their unmodified natural time seed. The candidate waits
before SDL until the baseline completes and validates. No energy, firing
cadence, allocation, collision, movement, mode or RNG rule is overridden.
Each side has 24 rear requests: 16 complete volleys and eight legitimate
zero-emission energy rejections. Capture selection uses the first complete
262 birth in each of five predeclared time windows, ages 1–5, plus seven
fixed ticks. Unselected births and rejections add no captures; selection
does not inspect background pixels or survival. The sealed pair evidence
uses 229,584,326 bytes within the unchanged 512 MiB/process and 1 GiB/pair
guards. There is no additional gameplay pair or broad runtime matrix.

The unchanged input switches to opposite mode 2 at tick 60, back at 100,
and stops firing at 120. The same complete 262 birth at tick 19 supplies
all six original identities and changed surviving native support at ages
1–5, captured at ticks 20–24. Independent review also qualifies births at
33 and 47 for this stronger five-age claim. All 15 pair intersections at
each age agree with density 8 authored support: 6, 4, 4, 4, 0 nonempty pairs. Fourteen
262 heads retain their birth/slot identities across tick 60, including the
complete birth at 54; thirteen unsupported 273 heads retain theirs across
tick 100, including the complete seven-phase birth at 96.

Actual SDL pixels match their true upload samples in all 64 gameplay
captures. Independent integer-alpha checks pass all 304 stored selected
262 patches with zero errors; baseline has no rear-HD alpha patches.
Each of the six phases has brown-ground and white-cloud witnesses with
full authored support surviving later draws and changed opaque-head and
fractional-rim samples, 12 strict witnesses in total. These background
witnesses may come from different births/ticks; no single volley uniformly
on cloud at all five ages is claimed. The selected cloud birth at tick 107
reaches the left screen edge at ages 4/5 and is not included in the stronger
in-view full-volley claim. The three shop pairs and shot-free frame 179
are byte-exact. Runtime ownership bytes are retained but not
independently semantically asserted; the offline fixture supplies the
ownership/restoration oracle.

Independent native review passes with these explicit coverage limits. It
reconstructs all 304 stored alpha patches and verifies 182,288 final/native
samples with zero errors. It inspects all 32 full baseline/candidate game
pairs, three shop pairs and 27 exact native comparison crops at original
1:1 pixels; all 124 displayed source rectangles match their original BMPs.
The qualified six-phase fans remain readable through age 5 separation.
No rectangular matte, dark rim halo, misplaced or stale HD head, unrelated
background deletion or mode-switch recolor is found. Original indexed
shadows remain unchanged; the 99/100 and shot-free 179 pairs are exact.

A review-only extra assertion requiring one selected volley to place all
six heads on classified cloud at every age 1–5 failed; that condition was
not part of the frozen gate. The failed review attempt is retained, and
neither the frozen source nor runtime evidence was changed. No game was retried.

The original runtime completion receipt intentionally retains its
pending-independent-visual-review status. The later completed independent
native review supersedes that status; the earlier receipt is not rewritten.

## Reproduce and limits

Run the focused public tests:

```
python3 tests/run_rear_multi_p1_core_tests.py
python3 tests/run_rear_multi_p1_adapter_tests.py
python3 tests/test_rear_multi_p1_source_inverse.py
```

Public tests use synthetic records and generated assets. Authentic original
records, parsed payloads, decoded original pixels/masks, raw native captures
and runtime instrumentation are not published. No new art is included.
This is a bounded first-level renderer qualification with one actual-game
Normal/native2×/density 8 diagnostic pair. It does not claim full-level or
full-game completion, actual Hard/4× testing, every ship/resolution/power,
ordinary P9 acquisition or later progression. Runtime lower-power switching,
reversed slots, partial allocation and semantic ownership are not claimed.
Earlier-route retention and offline 2×/4×/d4/d8 coverage remain explicitly
separate from the live diagnostic.

## Evidence seals

Private evidence remains outside the public repository. SHA256 seals bind
the tested source and completed gates:

The historical integration release pinned the preview seal immediately
before report whitespace cleanup. An additive reconciliation reconstructs
that exact earlier seal, proves only report whitespace changed and verifies
all 11 other entries unchanged. Both historical and final evidence are retained.

- Unified source/art/test freeze:
  `9c3e66c564f992127e85c74c03fc84399d53801408aafdfaede13bb0d4a2c487`
- Source test receipt:
  `c81305e5f39e1cdf241894b15c86c614ee4c321f7cb439627e3d34a66d466bd5`
- Independent pre-integration preview review:
  `29f263f745f838e653e2a1bdaa512d2cec80a92f1c959eaa4508999638a39817`
- Independent actual built-input review:
  `667b718ef8c937b9cdf8eb9db964e33574f8b4eb27105d794b9be10a03fabf99`
- Actual pair validation:
  `1e0724b0c0079853bc68c00f4d205ed1b28875198091992f221ee8a2c9344a34`
- Independent native data review:
  `b38b590a7a7d2609000c3696426debed0ee32fd6466f56e350043184bf972895`
- Independent native visual review:
  `46eb25869164758a75dd14dd64a8be96175a4388dd9d58da2400ff2e1babb1ec`
- Independent native review completion:
  `e4ee446227e109f24f52a2e7903a27e4250001799ba518eb997bcf29e0c4f709`
- Preview-seal historical reconciliation:
  `ebdbd2e267590507f85e66f0201f2e101b10bffe71c6713a891eadda9e21f507`
