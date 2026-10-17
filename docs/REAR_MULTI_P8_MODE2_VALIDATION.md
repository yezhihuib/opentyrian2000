# Rear Multi-Cannon P8 mode 2: exact seven-shot HD reuse

Baseline commit `ec46da1abf95f501f3caa9106f5371bb00d941d5`, tree
`42291956ff42c55b88f537471b2283e2b9c2bf71`.

## Exact renderer admission

Ordinary player 1, rear Multi-Cannon port 10 / bay 1, power index 7
(display P8), mode index 1 (display mode 2), physical normal-table record 272.
The allocation lease and cyclic phase period are exactly 7, with phases
277, 278, 295, 294, 77, 39, 1. Birth offsets are (-2,0), (2,0), (4,0),
(-4,0), (0,0), (0,0), (0,0); actual velocities are (-9,-2), (9,-2),
(6,6), (-6,6), (0,10), (-10,0), (10,0). Original repeat remains 6.

The full 80-byte record FNV1a64 is `1bc76a0fe7b06f72`; SHA256 is
`35b7cacbf629d1089e7246c0cdec02781494d4b57b6e236cc13794dc649a6922`.
The adapter additionally requires record-local `op[1][7]==272`.
Byte-identical physical alias 1272, later powers, wrong selectors, alternate
episode tables, Christmas banks and generic/shared/linked consumers remain
excluded. The existing first-level scope is unchanged: Normal physical 9
and Hard physical 15. Indexed shadows retain their original path.

The maximum used-slot storage grows 6 to 7, but record 261 retains its exact
six-shot lease and all 15 earlier routes retain their previous budgets.
A seventh valid 272 emission is admitted; an eighth is rejected. Each
retained birth keeps its original record, mode, phase, raw ID, generation
and slot identity across later calls or mode switches.

Only four production files change: `src/rear_multi_p1.c`, `.h`,
`_mirror.inc`, and `_pins.h`. Other 156 production files, all 7,188 assets,
the catalog and Makefile remain byte-exact. Drawable 19 / observed 21 IDs,
velocities, source and RGBA pins, slots 80, cells 168 and the 32,060-byte
normal bank are unchanged. One full-record pin is appended, for 16 routes
and 16 record pins. Observed-only 163/164 and density 8-only 182/183 retain
their previous behavior.

## Unchanged artwork

All seven existing generated shapes are reused at densities 4 and 8,
including all 28 relevant HDA copies in both accepted packs and 14 pinned
source PNGs. Decoded PNG pixels match their HDA payloads. No new artwork,
mask, palette, resampling, reflection, catalog entry or fallback density
is introduced. Missing/corrupt resources remain isolated to the affected
head and density. Original pixels and masks are not new art inputs.

## Source, adapter and production tests

- All 15 strict C99 core suites pass plain and ASan/UBSan, 30 runs. The
  new mode 2 suite passes 3,527,616 checks per build, including 448 cyclic
  prior/new-capacity designs, capacities 0..7, every 80×80 slot pair,
  exact seventh admission/eighth rejection, duplicate/recycled slots,
  identity seals and all 16 routes / 64 canonical phases.
- The actual allocator/adapter/decoder/loader/wrapper fixture passes
  5,194,898 checks per build, plain and ASan/UBSan. Coverage includes
  608 malformed resource variants, all 640 record-bit mutations for each
  of seven phases, record-local failure isolation, complete gameplay-state
  equality against the observer-stripped allocator, retained earlier routes,
  and independent/combined missing/corrupt seven-head resources at d4/d8.
  The adapter's draw stub alone does not establish pixel quality.
- Authentic production-pin tests pass 1,651,261 checks in each of four
  runs: both accepted packs, plain and ASan/UBSan. No pin override is used.
  These cover all 16 selected routes, 57 excluded shared records, 11
  genuine alternative mappings, 32 alternate episode payloads, 1272 and
  future routes, Christmas/source identity revocation, linked 445/451,
  and seven-head resource-failure isolation.
- All 16 strictly compiled private core mutants are rejected, including
  wrong six/eight-shot 272 budgets and incorrectly promoting 261 to seven.
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
synthetic scenery. Before integration, experimental 272 art dispatch is
narrowly shimmed only after authentic record/phase/slot/raw/position/shot-field
observations. The unchanged baseline ownership core still rejects 272.
No game is launched and original data stays in process.

Each strict plain/sanitized executable passes 1,178 rendered cases,
1,291 allocator/baseline comparisons, 4,704 real draws, 48 actual SDL nearest
native 2×/4× output comparisons, 24 foreground/restoration and 24 original
shadow/brightness cases. Every compositor pixel and ownership byte agrees
with independent ordered integer-alpha arithmetic after every draw, including
2,081,184 original-covered samples with zero authored alpha. Plain and
sanitized check counts are 31,293,116 and 31,293,068; the difference is 48
plain-only saved-preview assertions.

All 21 unordered phase pairs at ages 1/2/3 and both densities are checked:
126 measurements. Age 1 has six indexed-support overlaps but five HD-alpha
overlaps. The 294/39 pair shares one original covered cell and has zero
HD-alpha overlap at either density, exercising original ownership with
transparent authored pixels. At age 2 only 277/39 and 278/1 overlap.
Every indexed/HD support pair is disjoint at age 3, though allocation
rectangles can still overlap. Normal/reversed draws have expected ordered
alpha differences at ages 1/2, and all age 3 native outputs are identical.
The reverse-slot fixture is artificial stress, not a production reordering.

A separate 72-case retained-birth supplement passes 93,859,413 checks per
build: 840 draws, 144 allocator comparisons, 1,960 movement comparisons,
336 retained identity checks and 144 actual native 2×/4× comparisons.
Accepted 271/255 births preserve their original identities through a later
experimental 272 call. Gaps 1/2 are synthetic stress; gap 7 matches repeat 6.
Reverse iteration does not relocate slots or birth identities. Foreground,
shadows, integer-alpha pixels and HD-owner bytes match the reference.

Independent review derives the authentic 272 record address from the data
header/loader layout, verifies its complete pin and all 15 old record pins,
checks all 21 source pins, verifies extracted functions and seals, recomputes
all 126 intersections, and independently recomposes all 48 saved native
images byte-for-byte. Both contact sheets and exact native crops were
visually inspected: the initial fan is compact, opens at age 2 and separates
at age 3; central 77 and outer 39/1 remain visible without clipping or matte.
These are synthetic offline previews, not gameplay or purchase evidence.

Independent source probes additionally compare 64,495 semantic snapshots
across all 15 prior routes with byte-identical baseline/candidate output,
and 18,571 new-route states in strict and sanitizer builds. The extracted
actual table adapter matches 1,638 physical record serializations, scans
all 1,819 record IDs and rejects all 640 bit mutations of 272 while retaining
earlier records. Comparisons exclude ABI padding and normalize the extra
unused storage slot; they do not conceal logical state differences.

## Actual-game diagnostic

One baseline/candidate pair completed on the first Normal level at native
2× (640×400), using density 8 art. Both fresh processes exit successfully
after 180 gameplay ticks with 31 gameplay and three shop captures each.
The baseline already supports P8 mode 1 record 261. All 20 original trace
streams and full startup/player/RNG state match. The 576 new replacement
draws belong solely to record 272; 1,005 protected261 draws and every other
protected draw/style/shadow remain unchanged.

The menu genuinely buys P4 for 8,250 from 10,000, leaving 1,750. A private
post-shop diagnostic changes only the rear-power byte from P4 to P8;
all other 783 player bytes and 5,016 RNG bytes are unchanged. Cross-process
player pointers are independently proved as self-relative relocations.
This is explicitly not a genuine P8 purchase or progression test.

Both processes use their unmodified natural time seed. The candidate waits
before SDL until the baseline completes and validates. No energy, firing
cadence, allocation, collision, movement, mode or RNG rule is overridden.
Zero-emission power rejections are validated as such and schedule no
capture. Capture selection follows actual complete seven-shot results,
within the existing 512 MiB/process and 1 GiB/pair guards; the declared
maximum is 32 gameplay frames per side. Final sealed pair evidence uses
259,996,886 bytes. There is no additional gameplay pair or broad matrix.

The unchanged input switches from mode 1 to mode 2 at tick 60, back at 100,
and stops firing at 120. Complete272 births occur at 61,68,75,82,89,96;
all six retain seven original draw identities at ages1/2/3. Independent
changed-and-surviving native-support qualification passes for five births
(68,75,82,89,96); birth at tick 61 is not included in that stronger claim. The selected
birth at tick 68 is captured at ticks 69/70/71. All 21 pair intersections at each age agree
with density 8 authored support, and every phase changes samples that
survive into the native image. Complete261 birth at tick 54 retains identity
across tick 60; complete272 birth at tick 96 retains identity after returning to mode 1.

Actual SDL pixels match their true upload samples in all 62 gameplay
captures. Independent integer-alpha checks pass 269 selected new-route
patches with zero errors; both-side checks also cover 141 baseline and 410
candidate selected patches, including prior261. Each of the seven phases
has brown-ground and white-cloud witnesses with changed opaque-head and
fractional-rim samples and full authored support surviving later draws.
The three shop images and shot-free frame 179 image are byte-exact between sides.
Runtime ownership bytes are retained but not independently semantically
asserted here; the offline fixture supplies the ownership/restoration
oracle. Runtime lower-power switching, reversed slots and partial
allocation are not claimed by this pair.

Independent native review reconstructs all 551 stored alpha patches and
314,240 samples from the final density 8 patches with zero errors. It inspects
all 31 full baseline/candidate native pairs, three shop pairs and 14 individual
brown/cloud witness crops at original 1:1 pixels. The seven-phase fan remains
readable from compact age 1 to separated age 3; central 77 and outer 39/1
remain distinct. No visible rectangular matte, clipped head, dark fringe or
unrelated HUD/terrain/player change is found. Original indexed shadows stay
unchanged. The 130/179 pairs are exact, with 179 shot-free.

The original runtime completion receipt intentionally retains its
pending-independent-visual-review status. The later independent native
review supersedes that pending status; the earlier receipt is not rewritten.

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
ordinary P8 acquisition or later progression. Offline 2×/4× and d4/d8
coverage remains explicitly separate from the live diagnostic.

## Evidence seals

Private evidence remains outside the public repository. SHA256 seals bind
the tested source and completed gates:

- Unified source/art/test freeze:
  `707d1ef81b2b7d5dc7517600d36a57f11ea412a04d6bb36a653e3a1d332a6a20`
- Source test receipt:
  `d9a7ea126251ec82823496350974caaaa3d3b9128268dfcdf6ea54fe3a340351`
- Independent prelaunch review:
  `a5cb261af118bc19e7a732ff23ee13d4d473c2074809d965e2b491f6574e78de`
- Actual pair validation:
  `69647292bce0046ab19b0f11b0786e68f690c206930bc745fd160c5b45772232`
- Independent native data review:
  `f72ca733fc7cf039d0d42f177e1b323474873f997e4b91b3e5a6bf34b7b1a98e`
- Independent native visual review:
  `2ca75118d39fbbf5682c9e23bbaff0478803b44c526b02ecc336ee43f3d843f1`
