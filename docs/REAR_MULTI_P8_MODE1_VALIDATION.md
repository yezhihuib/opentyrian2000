# Rear Multi-Cannon P8 mode 1: exact six-shot HD reuse

Baseline commit `c7aff8d20ca935dac8714b7d5ed5bf9e79146c04`, tree
`eb29d89be5cbbc04bf5e20757f2abe8a268599a5`.

## Exact admission

Ordinary player 1, rear Multi-Cannon port 10 / bay 1, power index 7 (display P8),
mode index 0 (display mode 1), physical normal-table record 261. Its allocation
budget and cyclic phase period are exactly 6. Phases are 277, 278, 297, 296, 39, 1;
birth offsets are (-2,0), (2,0), (2,0), (-2,0), (0,0), (0,0), and actual velocities
are (-9,-2), (9,-2), (9,2), (-9,2), (-10,0), (10,0).

The complete 80-byte record FNV1a64 is `1987ab75603a42b9`; SHA256 is
`4981ef15a19280548f0c65161b665a4e229c29f0460e5c34159e70087d170489`.
The adapter checks the full record and record-local `op[0][7]==261`.
The byte-identical physical 1261 alias is excluded. P8 mode 2 physical 272
has seven allocations/phases and is deliberately excluded, as are later
powers, wrong selectors, alternate episode tables, Christmas banks,
generic/shared/linked consumers and indexed shadows.

The existing first-level scope stays Normal physical 9 and Hard physical 15.
All older routes retain exact previous budgets and birth identities. Raising
the used-slot storage bound 5→6 does not grant an older call a sixth shot or
any call a seventh. Retained births are authenticated by their original
record, mode, phase, raw ID, generation and slot; current mode changes do not
reclassify them.

Only four production files change: `src/rear_multi_p1.c`, `.h`,
`_mirror.inc`, and `_pins.h`. Other 156 production files, all 7,188 assets,
the catalog and Makefile are byte-exact. Drawable 19 / observed 21 source IDs,
velocities, every old source/RGBA pin, slots 80, cells 168 and 32,060-byte normal
bank remain unchanged. One full-record pin is appended. Observed-only 163/164
and density8-only 182/183 stay unchanged.

## Artwork reuse

There is no new artwork, mask, palette, HDA, catalog entry, reflection,
resampling or fallback density. Existing generated 277/278, 297/296 and 39/1
are reused byte-for-byte at densities 4 and 8, including all 24 corresponding
HDA copies in both packs. Original pixels and masks are not art inputs and
are not included in this change. Existing loader failure/fallback behavior
is preserved independently for each of the six assets.

## Source and adapter verification

- 14 strict C99 core suites pass plain and ASan/UBSan: 28 runs. The new P8
 suite performs 2,842,667 checks per build, including all 294 cyclic
 prior/new-capacity designs, exact six-shot saturation and rejected seventh,
 every 80×80 slot pair, duplicate/recycled slots, retained identity seals,
 all 15 admitted routes and 57 canonical phases, aliases and unsupported modes.
- Actual allocator/adapter/decoder/loader/wrapper fixtures pass 3,540,146
 checks per build, plain and ASan/UBSan, including 608 malformed resource
 variants, all 640 record-bit mutations, record-local corruption isolation,
 unchanged gameplay allocation and independent/combined missing/corrupt
 six-head fallback at d4/d8. The adapter drawing stub alone is not a pixel test.
- Authentic no-pin-override checks pass 1,074,293 checks in each of four
 runs: Blue Four and Talon13, plain and ASan/UBSan. These cover all 15
 routes, 58 excluded shared records, 12 genuine alternative mappings, 30
 alternate episode payloads, 1261/future 272, Christmas/source identity,
 linked 445/451 and independent six-head resource failure isolation.
- 16 separately compiled private core mutants are rejected by explicit tests.
- The inherited source inverse and exact delta contract pass. All old ID,
 velocity, source/RGBA and record-pin prefixes are preserved.

ASan/UBSan use halt-on-error with leak detection disabled; LeakSanitizer is
not qualified. Both uninstrumented enabled and RENDER_MIRROR_DISABLED
production builds compile 74 translation units with zero warnings/errors under
the inherited profile. Suppressions are misleading-indentation,
format-truncation and missing-field-initializers, with unused-variable and
unused-parameter also suppressed in the disabled build. This is not an
unsuppressed-all-warning claim.

Independent review recomputed all 15 authentic record pins and verified the
freeze and source inverse. Its baseline/candidate probes produce identical
logical-state digests across 5,680 snapshots for all 14 previous routes,
including old budgets, cyclic calls, invalid emissions and duplicate slots.
A 15-route/six-slot candidate probe passes 6,778 snapshots in plain and
ASan/UBSan builds.

## Actual compositor and native sampling

The unchanged production compositor, actual indexed RLE blitter, allocator,
movement and wrapper execute in a separate offline fixture. Its narrow
test-only 261 grant observes authentic allocation/phase/slot/raw/position and
shot fields. Original bank/record data is read only in memory. Scenery and
palette anchors are synthetic; this test launches no game.

Each plain/sanitized run passes 866 rendered cases, 879 allocator/baseline
comparisons, 3,024 actual shot draws, 48 real SDL nearest native2×/4× outputs,
24 foreground/restoration and 24 original shadow/brightness cases. Every
compositor pixel and ownership byte matches an independent integer-alpha
reference after each shot. This includes 1,076,040 original-covered samples
with zero authored alpha. Plain/sanitized counts are 31,129,843 / 31,129,795;
the difference is 48 saved preview assertions.

All 15 unordered phase pairs are checked at ages 1/2/3 and both densities,
90 measurements independently crosschecked against authored alpha sets.
Age 1 has six nonzero HD overlaps (d4/d8 sample counts):

- 277/296: 76/250; 277/39: 293/1094
- 278/297: 76/250; 278/1: 324/1206
- 297/1: 147/517; 296/39: 97/313

Age 2 still overlaps 277/39 by 131/449 and 278/1 by 88/278. Age 3 is disjoint
at both indexed/HD support levels, though allocation rectangles overlap
through age 6. Age 7 is rectangle-disjoint. Native normal/reversed order
outputs differ at ages 1/2 as expected for ordered alpha composition; all
age 3 order comparisons are identical. No phase sorting was introduced.

A further bounded mixed-birth supplement passes 93,432,298 checks per build:
72 cases, 144 actual allocator comparisons, 720 actual draws and 144 actual
SDL native outputs. Existing record 255 keeps 39/1 and 260 keeps the other
four shapes across later experimental 261 births, using birth-age gaps 1/2/7
and forward/reversed draw iteration. All pixels, ownership and original
shadow/foreground restoration agree. Gaps 1/2 are explicitly synthetic
stress, not claims about the authentic firing cadence; gap 7 matches repeat 6.

Offline native contact sheets and exact pixel crops show a compact readable
three-direction fan on each side at age 1, opening at age 2 and separating
at age 3. These are synthetic previews, not actual game captures or proof of
ordinary purchase/progression.

## Actual-game diagnostic

One corrected baseline/candidate pair passed on the first Normal level at
native 2× (640×400), using the frozen source and existing density-8 art.
Both fresh processes exited successfully after 180 gameplay ticks, with 24
actual SDL gameplay captures and three shop captures per process. This is
one bounded Normal/2× qualification, not an actual-game Hard/4× run.

The shop genuinely buys P4 for 8,250 from 10,000, leaving 1,750. A private
post-shop diagnostic changes only the rear power byte from P4 to P8; every
other player-state byte and the full RNG state are unchanged. Cross-process
player pointers are independently validated as relocations, not silently
ignored. This is explicitly not a genuine P8 purchase or progression test.
No energy, firing cadence, allocation, collision, movement or gameplay rule
is overridden.

All 20 original trace streams match byte-for-byte, and full startup/player
and RNG parity passes. The corrected run observes 902 newly admitted record
261 draws. All 638 record 272 head draws remain unsupported and unchanged;
all other protected draws and indexed shadows are unchanged. The input
switches to unsupported mode 2 at tick 60, back to mode 1 at tick 100, and
stops firing at tick 120. One complete six-phase birth from tick 54 retains
its original identity through the mode switch.

A complete six-phase birth at tick 107 is captured at ages 1/2/3 in frames
108/109/110. All 15 phase-pair overlaps match the density-8 authored support
at each age; every phase has changed samples that survive into the actual
native image. All 48 gameplay captures match their real SDL-upload sampling.
Independent integer-alpha checking passes 188 selected patches with zero
errors. Each of the six phases has both brown-ground and white-cloud native
witnesses, including samples that are simultaneously fractional-alpha,
changed and fully surviving later draws. Shop images and the shot-free frame
179 are pixel-exact between baseline and candidate. Runtime ownership bytes
are retained as evidence but are not independently semantically asserted;
the offline compositor fixture supplies the ownership/restoration oracle.

Independent visual review inspected all 24 baseline/candidate pairs at
native 640×400 plus all 12 background witness crops. The reused orange/gold
heads form readable fans and show no visible opaque rectangular matte,
dark fringe, missing phase or unrelated HUD, terrain or player change in
these comparisons. The actual age-3 fan is separated; ages 1/2 retain their
expected ordered overlap. Post-run source, art, helper, binary and dependency
freezes were rechecked successfully.

### Attempt accounting

The initial pair attempt did not pass. Its baseline completed 180 ticks and
24 gameplay captures; its candidate was held before SDL/gameplay and then
stopped by the controller. A newly added harness assertion incorrectly
required every rear-fire request to produce a complete volley. The original
game legitimately rejected eight of 24 requests for insufficient power,
with zero emissions; all 16 successful volleys were otherwise correct.
The initial capture schedule also lacked one surviving complete birth at
all three consecutive ages. These were harness/coverage issues, not a
candidate renderer failure, and the initial evidence is retained.

Code/trace inspection and independent review justified one corrected
replacement pair. The corrected guard requires exact request/result call
coverage and permits only a verified zero-emission power rejection; unknown,
partial or capacity-related outcomes still block. Its negative controls
passed before the replacement launch. Four of the 24 capture ticks were
changed to cover the required ages; input, original energy behavior,
rendering observers and parity requirements were unchanged. The replacement
results above are the successful pair. No additional gameplay runs were
used.

## Evidence seals

Private evidence is kept outside the public repository. Aggregate receipt
SHA256 values bind the qualified source and checks:

- Unified source/art freeze:
  `f5a5d4020627e901f901484187f0fa1a69441a3f1be0f01c355f7c8335c329c2`
- Source test receipt:
  `dd27731b7e1bc3a6daf443eda8db4aa43ccd45a6746b57685794360169c012ad`
- Independent source review:
  `2fec65b2388dac7287b034ffe8b3aec87bcdd94b565238509780a504379f93d3`
- Corrected pair validation:
  `b3cefcdfd16ea4f1c0557e15013f882b20ce81fc6f278a8a3c6b5e3f27c2f598`
- Independent native review:
  `29ebb95b414fb17fd45b410d0ee6bc490df653d3f5eb4d2fefaae00549a2cdf2`

## Reproduce and limits

Run the focused core/adapter runners:

```
python3 tests/run_rear_multi_p1_core_tests.py
python3 tests/run_rear_multi_p1_adapter_tests.py
python3 tests/test_rear_multi_p1_source_inverse.py
```

Public tests use synthetic records and generated assets. Authentic original
data, raw indexed frames, private native gameplay captures, full parsed
weapon records, decoded original pixels/masks and runtime instrumentation
are not published. This is a bounded first-level renderer qualification;
it does not claim every level, difficulty, ship, mode, power, resolution,
ordinary P8 purchase or complete game validation.
