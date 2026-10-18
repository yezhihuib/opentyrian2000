# Rear MultiCannon P7 FIRST260 / SECOND271 shadows

## Scope and local history

This presentation-only batch extends the existing birth-owned density8 shadow
path to physical P7 FIRST260 and SECOND271. All22 accepted normal-head routes
and the eight existing P8/P9/P10/P11 shadow routes remain admitted. The twelve
earlier physical routes retain their previous shadow behavior. No new artwork,
global bank8 binding, gameplay, allocation, firing, collision, RNG, original
position, indexed darkening, asset loader, resource pin or compositor change.

The batch has exactly three source-control files: this document,
`src/rear_multi_p11_shadow.inc` and `tests/rear_multi_p11_shadow_test.c`.
The historical include and function names remain unchanged. Original assets,
private harnesses, captures, logs and executables stay outside the repository.

The local parent is `2d3bd1118f3da650c5d0fcf47530a69e37aaeb50`, the P8 batch.
Its parent is the P9 batch `80ee87b644e5f84a9d995c159d00e9e451ca52a1`.
The independent local snapshot ancestor is
`3b4d771072f5262ba3aba4975a5bc3f0c2799737`, with published file provenance from
`73c556905a2f6c7266c911f8016cfe9025b6d934`; this is not GitHub ancestry.
There is no remote, promisor or partial-clone configuration. This batch is
local-only and does not authorize a push or publication.

## Actual original records and accepted alpha

Both complete physical80-byte records were inspected from actual original
`tyrian.hdt` before implementation. The original SHA256 is
`fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b`.
The loader uses byte2=shotrepeat, byte3=multi, byte6=max and byte9=aim.
Both P7 records have shotrepeat6 and aim0; selector power index is6.

- FIRST260: mode index0, actual multi/max4/4. Phase raws277,278,297,296.
  Original sx=-9,9,9,-9; sy=2,2,-2,-2; bx=-2,2,2,-2; all by=0.
  Full80 SHA256:
  `f3010ca4409303531f0daf0d40fc272a9d216c246d942df178c8988bf0ac4b9e`.
- SECOND271: mode index1, actual multi/max5/5. Phase raws277,278,295,294,77.
  Original sx=-9,9,6,-6,0; sy=2,2,-6,-6,-10; bx=-2,2,4,-4,0;
  all by=0. Full80 SHA256:
  `1e0fa572aeea693627cd059f794ac45b353694ec13d4dc0cd927e17cc3a8577d`.

The original initializer negates sy for live y velocity. No motion, offset,
phase, allocation budget or lifetime is synthesized. FIRST is four phases;
SECOND is five phases including its original vertical raw77 phase.

Every phase reuses its own exact accepted density8 normal-head HDA alpha,
never its RGB. The seven unique raws are77,277,278,294,295,296,297. All exact
payloads match existing production FNV64 pins. No reflection, resampling,
new generation or substitute alpha is used. Authentic-input checks also bind
all22 complete80-byte records and all27 original decoded source pins.
Original SHP SHA256 is
`80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0`;
the original32060-byte bank8 SHA256 is
`9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68`.

## Admission and preservation

The only production difference among161 source files is the finite physical
record admission list. New eligibility is restricted to sealed FIRST260 mode1
or SECOND271 mode2 births. Existing qualified birth, live slot/generation/seal,
raw/phase/live-shot identity, full80-byte original table integrity, genuine
physical selector entry, original bank pointer/size/decoded-source pins,
resource root/density and exact accepted asset checks remain unchanged.

All scope gates remain: actual Episode1 first-level Normal, physical level9,
background2, density8, authentic INDEX8 surface and full canvas layout, safe
pitch/ownership storage, original shadow x=shotX+1 and y=shotY+shadowYDist,
original y<190 eligibility, admitted clipping bounds and finite command
capacity. Hard/physical level15 heads do not gain this shadow path. Missing,
corrupt, ineligible or unavailable optional alpha keeps native fallback.

Prepared commands retain original birth identity, source coverage, surface,
pixel/format/canvas pointers and pitches, source-bank binding, logic tick,
coordinates and alpha pointer. Execution epoch/revalidation gates remain.
Equipment or mode switches do not relabel old births; shared raws do not grant
aliases a physical-record lease or create a global bank8 binding. The last
original drawn lifetime counter0 tick remains eligible.

The original indexed shadow function still runs exactly once, including after
HD preparation. Ordered true-color darkening, clouds and overlapping ownership,
classic restoration and nearest-sampled SDL upload paths are unchanged.
Preparation alone is not evidence of a final visible authored-alpha sample.

## Validation

### Code, authentic inputs and preparation guards

The full C99/O2/Wall/Wextra/Werror game build links successfully. All21 core
suites pass plain and ASan+UBSan,42 runs total. The unchanged adapter/loader/
wrapper suite passes17,080,056 checks per mode, including800 malformed resource
variants. Retained P10/P11 pending-art gates pass983/1123 checks per mode.
The shadow preparation and epoch suite passes697,908 checks per mode: ten
physical roles,63 phases, all80 slots,96 negative families, every serialized
record byte,16 malformed resource families, aliases, independent role tables,
original last drawn counter0, mode switches, retained births and reset epochs.
These guards are synthetic; they do not replace actual SDL or game evidence.

Authentic checks verify all22 full80 original record pins, all27 decoded source
pins and all7 own accepted P7 density8 payloads. Independent static review
reconstructs the finite admission delta exactly and finds no blocking defect.
Of264 existing files,262 remain byte-identical; only the intended include and
guard test differ. The new document is the third file. All93 historical Git
metadata and blocked-index files remain unchanged.

### Scoped offline SDL

The frozen baseline/candidate actual decoder, optional loader, wrappers,
original indexed blitters, birth/provenance core and ordered compositor pass
291 scoped scenes plus36 accepted-boundary cases per strict/ASan+UBSan side,
1308 scene executions total. Every new phase is exercised separately with its
own accepted alpha on indexed, terrain and cloud backgrounds. The matrix also
covers four representative phase pairs per new route, both orders and ages0/2/8,
authentic4/5-shot cohorts at ages0/1/4/8/16, switches, intervening clouds/heads,
classic restoration and repeated indexed low-nibble floor darkening. All36
accepted x0/x308/y-13/y189 edge cases pass per side/build.

Each main side/build performs1269 shadow commands and18 restorations. Baseline
has293 negative checks and candidate325, including81 independently checked
full-birth-seal rejections. Every created birth recomputes record/mode/phase/
raw/generation/slot identity as six little-endian uint64 values without struct
padding. Each of9 new phases separately rejects qualification, shared-raw
same-mode record substitution, mode, phase, raw, generation, cross-slot copied
tuple, corrupted identity and zero identity. The44 guard kinds and8 prepared-
lease invalidations use first/last phase representatives. Broader all-phase
synthetic preparation tests are separate; no Cartesian/exhaustive claim.

All18 deliberately wrong own-alpha/double-darken expectations are rejected in
each build. All36 fresh-process missing/corrupt optional-loader fallback runs
pass. All74 protected RGBA/ownership/cloud/INDEX8 digest rows are identical
across four runs, covering all8 P8–P11 routes and generic13. All40 strict/
sanitizer native640x400 BMP comparisons are byte-identical. Of20 baseline/
candidate native pairs, only four new260/271 pairs differ; all16 protected
P8–P11 pairs are identical. Generic13 uses accepted frozen loader outputs for
unchanged admission/compositing, without independently retesting its file
loader. Actual SDL software readback is covered; gameplay, live allocator/
lifetime loop and GPU are outside this constructed offline suite. Offline
cohorts start at canonical phase1; live cyclic starts are checked separately.

The10ms process-group watchdog plus kernel child maximum RSS runs from the
first actual execution. Peak capture RSS is131,379,200bytes; minimum free disk
is18,681,053,184bytes. The512MiB capture RSS cap and4GiB free-space minimum hold.
Compiler RSS and ASan virtual addresses are exempt. Leak detection is disabled.

Two precompile setup failures are retained openly: the inherited preparation
logic requested d4 provenance absent from its own d8-only receipt, and a
premature extraction check could not find its not-yet-generated script. Before
any compilation or production test, the scaffold was corrected to copy only
the19 required pinned d8 assets. Setup and extraction then passed; all frozen
compilations and actual test executions passed on their first attempts. No
production/runtime rerun or test gate was relaxed.

### One actual-menu pair: bounded270/271

One instrumented180-tick baseline/candidate pair exits0/0 in83.48seconds after
actual NewGame -> FullGame -> Episode1 -> Normal and a genuine rear-port10
shop P4 purchase. This is not a render-test/demo admission claim. Baseline is
the exact local P8 parent; only the finite shadow include differs in candidate.
Private instrumentation reverses exactly to each original src+Makefile. The
original Hdt/Shp/bank8 and all637 accepted common-pack files are hash-verified
before and after launch. Both starts have matching natural seed, all627 RNG
words, purchasedP4 and game-entry state before release.

Five disclosed diagnostic one-byte power changes are4->7 at tick0,7->8 at68,
8->9 at96,9->10 at124 and10->11 at152. Each preserves all other game state and
all627 RNG words. Actual SDL mode keydowns40/82/110/138/166 are observed at
41/83/111/139/167. Original coordinates, firing, allocation and fades remain
unchanged. This is instrumented diagnostic play, not an ordinary
uninstrumented playthrough.

The frozen plan visits260[0,40),271[40,68),272[68,82),261[82,96),
262[96,110),273[110,124),274[124,138),263[138,152),264[152,166),
275[166,180). Original movement, draw-before-fire order, velocities, offsets,
viewport and unchanged admission gates derive the capture ages before launch.
New P7 cohorts are sampled at ages1/4, protected cohorts at age1 and terminal179.
SECOND271 phase5 has only age1 eligibility; phases3/4 have ages1–3. FIRST260
phases3/4 have cohort-isolated opportunities at1, and phases1/2 gain isolation
at4. This is a schedule opportunity, not an assertion that every actual sample
will have a visible final owner. The13 actual capture ticks are
34,37,41,44,69,83,97,115,129,143,157,171,179. No retuning or rerun follows.

FIRST260 has five complete authentic calls and20 births; each phase occurs
five times. All245 eligible shadows admit, per-phase55/100/45/45, and all285
eligible normal heads admit exactly once. SECOND271 has four complete calls
and20 births; every phase occurs four times. All152 eligible shadows admit,
per-phase44/80/12/12/4, and all176 eligible normal heads admit exactly once.
All8 protected routes have two complete authentic calls each. Every ordered
cyclic raw/velocity tuple and unique allocator slot verifies. Older births
retain their identities across all9 diagnostic stage transitions.

All20 original observation streams and four explicitly named mixed-stream
original/nonchanging-field projections match. All ten visited normal-head
routes have exact paired per-draw rows. Protected P8/P9/P10/P11 shadow
identities and admissions match. Every admitted shadow passes its independent
full clipped12x14x8 rectangle oracle, including own authored alpha, birth seal,
owner/cloud/green/selection state and whole INDEX8 before native darkening,
with zero errors. Native fallback is never counted as an HD admission.

The native indexed darkener runs exactly once for each of1518 original shadows
per side. Every64000-byte INDEX8 result equals the independent one-pass
original-RLE model, with zero errors. All13 actual640x400 readbacks equal the
nearest sampled2560x1600 final uploads. Paired differences stay inside newly
admitted260/271 rectangles. Captures83,97,115,129,143,157,171,179 are identical
after the new shadows disappear.

All four FIRST260 phases have finite isolated final-native authored-alpha
witnesses, counts3/9/2/2. SECOND271 phases1/2/3/4 have counts3/4/1/1. Phase5 has
no strict final-owner witness, so the all-five-phase gate remains failed and
the overall runtime result is270/271. It has4 actual zero-error age1 admissions,
including capture41. Of130 native-grid authored-alpha samples,128 lie below
the gameplay viewport; the remaining2 overlap an original head rectangle and
have no native difference. There is no isolated visible owner sample. Every
original head rectangle and every other whole original shadow rectangle,
including fallback and protected routes, remains excluded from attribution.
No relaxed gate, extra capture, rerun, ideal whole-frame acceptance or
uninstrumented-playthrough proof is claimed.

Raw pair output is463,286,487bytes; sealed attempt evidence including six
lossless native PNGs is465,522,750bytes, below512MiB. The prelaunch worst-case
budget including reserved telemetry/analysis/manifests and six PNG exports is
516,328,004bytes, also below512MiB. Both sampled game RSS peaks are145,494,016
bytes; minimum observed free disk is18,811,863,040bytes. Each actual game has a
512MiB virtual-address cap. Compiler and sanitizer virtual addresses are exempt.
Both strict private builds,63 cyclic sampler starts,378 hostile sampler
mutations, exact14-action schedule/shop controller, cap/strict-owner guards
and plain+ASan/UBSan independent shadow-oracle corruption checks pass. Leak
detection is disabled; there is no LeakSanitizer claim.

The actual unchanged-size640x400 FIRST260 tick34 and SECOND271 tick41 BMP
pairs were inspected: smoother cloud-shadow profiles and no visible head/
background displacement. This bounded visual result was accepted with all
technical limits retained. The age4 FIRST260 tick37 PNG pair was also viewed.
This does not close SECOND271 phase5's visibility gap.

### External receipts

Full commands, source and asset pins, retained attempts and honest limits stay
in the adjacent task workspace:

- `p7-shadows-code-checks-20261018/code-checks-summary.json`
- `p7-shadows-code-checks-20261018/authentic-inputs-and-alpha.json`
- `p7-shadows-private-validation-20261018/offline-validation-receipt.json`
- `p7-shadows-runtime-validation-20261018/bounded-runtime-technical-receipt.json`
- `p7-shadows-runtime-validation-20261018/RUNTIME_RESULT.md`
- `p7-shadows-runtime-validation-20261018/runtime-pair-attempt1/runtime-evidence-manifest.json`
- `p7-shadows-final-review-20261018/static-scope-review.json`

Frozen runtime input manifest SHA256:
`8cab1d8a6bca8564ea7fe118aca26f377bf5a80b0a4469b221a1b0c79a46cb36`.
Prelaunch capture-schedule proof SHA256:
`6e9190549c2d4526acfb876e30c2319b716c2b136111577d3d15d949bcca6223`.
Runtime evidence manifest SHA256:
`dea2410262d26f4f2059344b78570607d027a5853b5fd043639c5895ed518b50`.
Offline receipt SHA256:
`e17cd4548a367d2c70ff832313443a287d2231a158796c0820f5661372aade83`.

## Known inherited failure

The source-inverse test retains its inherited exit1: the preserved published
21517-byte projection fixture expects the older head-only `entity_draw.c`
wrapper. This batch does not claim all repository tests pass. The old fixture
and inverse test remain unchanged.

The separately denied replacement projection JSON was not opened, copied,
repackaged or transferred. Historical Git metadata and previously blocked
indexes remain preserved. No new repository snapshot, lazy fetch, Git network
operation, push or publication is part of this batch.
