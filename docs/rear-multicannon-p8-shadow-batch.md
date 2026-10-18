# Rear MultiCannon P8 FIRST261 / SECOND272 shadows

## Scope and local history

This batch extends the existing birth-owned density 8 shadow path to the two
physical P8 records, FIRST261 and SECOND272. All 22 accepted normal-head routes
remain unchanged. The six already admitted P9/P10/P11 shadow routes remain
admitted; the fourteen earlier physical routes retain their previous shadow
behavior. No artwork, generic bank binding, gameplay, allocation, firing,
collision, RNG, original position, or original indexed-darkening code changes.

The batch has exactly three source-control files: this document,
`src/rear_multi_p11_shadow.inc`, and `tests/rear_multi_p11_shadow_test.c`.
The historical include/function names remain unchanged. Assets, original game
data, private harnesses, screenshots, logs and executables are outside the
repository.

The local parent is `80ee87b644e5f84a9d995c159d00e9e451ca52a1`, the P9 shadow
batch. Its parent `3b4d771072f5262ba3aba4975a5bc3f0c2799737` is an independent
local source snapshot with published file provenance from
`73c556905a2f6c7266c911f8016cfe9025b6d934`; it is not GitHub ancestry. This
repository has no remote, promisor or partial-clone configuration. This batch
is local-only. It does not authorize or perform a push or publication.

## Original records and exact accepted alpha

Both records were inspected from the actual original `tyrian.hdt` before
implementation. The original SHA-256 is
`fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b`.
The loader layout is byte 2 = shotrepeat, byte 3 = multi, byte 6 = max and byte 9 = aim.
Both records have shotrepeat 6 and aim 0; the selector power index is7.

- FIRST261: mode index0, actual multi/max 6/6; phase raws
  277,278,297,296,39,1. Original sx is -9,9,9,-9,-10,10; sy is
  2,2,-2,-2,0,0; bx is -2,2,2,-2,0,0; all by values are0.
  Full 80 SHA-256:
  `4981ef15a19280548f0c65161b665a4e229c29f0460e5c34159e70087d170489`.
- SECOND272: mode index1, actual multi/max 7/7; phase raws
  277,278,295,294,77,39,1. Original sx is -9,9,6,-6,0,-10,10; sy is
  2,2,-6,-6,-10,0,0; bx is -2,2,4,-4,0,0,0; all by values are0.
  Full 80 SHA-256:
  `35b7cacbf629d1089e7246c0cdec02781494d4b57b6e236cc13794dc649a6922`.

The original initializer uses negative sy as the live y velocity. No velocity,
offset, phase budget or lifetime is synthesized. SECOND has seven phases,
including its original vertical raw77 phase; it is not an eight-shot route.

Every phase reuses its own exact previously accepted density 8 normal-head HDA
payload's alpha, never its RGB. The nine unique raws are
1,39,77,277,278,294,295,296,297. Their full payloads match the existing
production FNV64 pins. There is no new artwork, mirror-generated alpha,
substitution by another raw, or loader change. The separate authentic-input
receipt also verifies all 22 full 80 record pins and all 27 original decoded
source pins against the original HDT/SHP. Original SHP SHA-256 is
`80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0`;
the original 32060-byte bank 8 SHA-256 is
`9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68`.

## Admission and preservation

Only physical record 261 with sealed mode 1 or record 272 with sealed mode 2 is
newly eligible. The existing path still requires a qualified original birth,
the live slot/generation/birth identity, the exact raw/phase, immutable original
full 80 table fields, the genuine selected physical table entry, original
bank8 pointer/size/decoded-source pins, original live shot fields, current
resource root/density, and exact accepted alpha payload.

All existing scope gates remain: actual Episode 1/first-level Normal, level 9,
background2, density 8, genuine INDEX8 surface and full canvas shape, safe
pitch/ownership storage, original shadow coordinates x=shotX+1 and
y=shotY+shadowYDist, original y < 190 eligibility, admitted clipping bounds and
finite command capacity. Hard/level 15 heads do not gain this shadow path.
Non-admitted or unavailable optional alpha retains the exact native fallback.

The prepared command keeps its original birth identity, source coverage,
pixel/format/canvas pointers, pitch, source-bank binding, logic tick,
coordinates and alpha pointer. Existing epoch/revalidation checks remain in
place through execution. A later equipment or mode switch does not relabel
an older birth. Shared raw 39/1 and other shared raws do not turn this into a
global bank8 binding or grant aliases an original physical-route lease.

The original indexed shadow function still runs exactly once, including
after successful HD preparation. Existing ordered true-color darkening,
cloud provenance, restoration, overlapping ownership and nearest-sampled SDL
upload paths are unchanged. The final drawn lifetime counter 0 remains valid
when the original draw does. No current-pixel visual claim follows solely
from a successful preparation guard.

## Validation

### Code and authentic-input checks

The full C99/O2/Wall/Wextra/Werror build links successfully. All 21 core suites
pass in plain and ASan+UBSan modes, 42 runs total. The actual adapter/loader/
wrapper suite passes 17,080,056 checks per mode with 800 malformed resource
variants; retained P10/P11 pending-art gates pass 983/1123 checks per mode.
The extended shadow preparation/epoch suite passes 593,472 checks per mode:
eight physical roles, 54 phases, all80 slots, 96 negative families, every one
of the80 serialized record bytes, 16 malformed resource types, aliases,
independent role tables, original last drawn lifetime tick, mode switches,
retained birth identities and reset epochs. These synthetic guards do not
replace SDL or actual-game observation.

The only production difference among161 source files is the finite admission
list in the shadow include. The parent snapshot and all93 historical metadata/
blocked-index files remain intact. Two initial receipt-only assertions were
corrected without rerunning or changing production: path enumeration needed
sorting, and four original core success lines say `passed` instead of `PASS`.
All original successful test outputs remain preserved.

### Scoped offline SDL

Both HEAD80ee baseline and frozen candidate pass 299 scoped scenes plus52
accepted-boundary scenes in strict and ASan+UBSan builds: 1404 executions.
The matrix covers every new phase on indexed/terrain/cloud scenes, four
representative phase pairs in both orders and several ages, full authentic
cohorts, switches, intervening clouds/heads, classic restoration, repeated
indexed ramp-floor darkening and independent birth seals. The52 edge cases
cover every phase at accepted x0/x308/y-13/y189. Rejected clipping, 44 guard
mutations and eight prepared-lease invalidations on representative first/last
phases remain checked. Candidate runs have260 negative checks each.

All26 deliberately wrong own-alpha/double-darkening expectations are rejected
in both builds. All52 fresh-process missing/corrupt optional-loader fallback
executions pass. All62 protected RGBA/ownership/cloud/INDEX8 digest rows match
across the four runs, including all six P9/P10/P11 routes and generic13.
All32 native640x400 BMP strict/sanitizer comparisons are byte-identical;
baseline/candidate protected review pairs are identical. Generic13 checks
unchanged admission/compositing with accepted frozen loader outputs, without
claiming an independent generic-loader retest. These are constructed offline
SDL software-renderer scenes, without gameplay or GPU claims.

The capture watchdog used10ms process-group sampling plus kernel child
maximum RSS from the first run. Peak observed capture RSS is126,627,840 bytes;
minimum observed free disk is19,680,489,472 bytes. The512MiB capture RSS limit
and4GiB minimum free-space guard held. Compiler RSS and ASan virtual-address
space are exempt. Leak detection is disabled, so there is no leak-check claim.

### One actual-menu pair: bounded253/254

One instrumented180-tick baseline/candidate pair exits0/0 in66.37seconds after
actual NewGame -> FullGame -> Episode1 -> Normal and a genuine rear-port10
shop P4 purchase. It is not a `--render-test` demo. Baseline is the exact local
P9-shadow parent; candidate differs only in the reviewed shadow include.
Private instrumentation reverses exactly to copied src+Makefile, and frozen
original source, original HDT/SHP/bank8 and all637 accepted pack files are
verified before and after launch.

The disclosed artificial inputs are power-byte4->8 at tick0,8->9 at80,
9->10 at112 and10->11 at144. Actual SDL mode keydowns at40/96/128/160 are
observed at41/97/129/161. Each power change preserves all other game state;
original coordinates, firing, allocator and RNG are unchanged. Original
fades remain active. The frozen plan visits all eight P8-P11 physical routes.

Before launch, actual original phase velocities/offsets, draw-before-fire
order, original viewport and unchanged eligibility gates were used to derive
the capture schedule. New P8 cohorts are sampled at ages1/4, protected cohorts
at age1, and tick179 is terminal. The11 paired capture ticks are
34,37,41,44,83,97,115,129,150,164,179. Every P8 phase is sampled inside an actual
eligible window, including SECOND272 phase5's age1-only window. No schedule
is retuned after observing the result.

FIRST261 has five complete original calls and30 births. All390 eligible
shadow draws admit, per phase55/100/45/45/50/95. SECOND272 has six complete
original calls and42 births. All402 eligible draws admit, per phase
66/120/18/18/6/60/114. All original ordered cyclic phase/raw/velocity tuples
and unique allocator slots match. Every admitted draw passes its independent
full clipped rectangle shadow oracle with zero errors. All20 original
observation streams and four explicitly defined mixed-stream original-field
projections match. All eight normal-head routes have exact paired original
rows, one admitted HD counterpart per eligible original draw and zero
alpha/owner errors. Existing P9/P10/P11 shadow identities, admissions, seals
and oracles are preserved.

The native indexed darkener is entered exactly once for each of1786 original
shadows per side. Every resulting64000-byte framebuffer equals an independent
one-pass original-RLE model, with zero errors. All11 actual640x400 readbacks
match the nearest sampled2560x1600 final uploads. Differences are confined
to admitted new261/272 rectangles; the no-new-shadow terminal capture is
identical. Native fallback is never counted as an HD admission.

All six FIRST261 phases have finite isolated final-native authored-alpha
witnesses, counts3/9/2/2/3/9. SECOND272 phases1/2/6/7 have counts3/4/2/3.
Its phases3/4/5 still have no strict isolated final-native witnesses, so the
all-seven-phase gate remains failed and the overall result is253/254.
Their actual admission/oracle counts are18/18/6, all with zero errors and
with actual age1 captures. For phases3/4, all136/135 in-viewport sampled
native-grid alpha points overlap other whole original shadow rectangles.
For phase5,128 of130 points lie below the gameplay viewport and the remaining
two overlap an original head rectangle. There is no isolated visible owner
sample. This is a viewport/overlap limitation, not a missed eligibility
window or zero runtime admission. All other full original shadow rectangles,
including native fallbacks and protected routes, and all original head
rectangles remain excluded from attribution. No relaxed gate, extra capture,
rerun, whole-frame ideality or uninstrumented-playthrough claim is made.

The raw pair output is392,978,797 bytes; sealed evidence including six lossless
native PNG review exports is395,220,883 bytes, under512MiB. Observed game RSS
peaks are143,806,464/143,974,400 bytes; observed free disk stays above
19,700,613,120 bytes. Each game has a512MiB virtual-address cap; compiler and
ASan virtual-address spaces are exempt. Both strict private full builds,
54 cyclic sampler starts,324 hostile sampler mutations, exact controller,
cap/strict-owner guards and plain+ASan/UBSan independent shadow-oracle checks
pass. No LeakSanitizer claim is made.

The root parent inspected the actual unchanged-size640x400 FIRST261 tick34
and SECOND272 tick41 baseline/candidate PNG pairs and accepted the limited
visual review: smoother cloud-shadow silhouettes with consistent heads and
background positions. The implementation task also viewed the age4 tick37
pair. This inspection does not close the three remaining attribution gaps.

### External receipts

The adjacent task workspace retains full commands, source/asset pins, attempts,
outputs and honest limits in:

- `p8-shadows-code-checks-20261018/code-checks-summary.json`
- `p8-shadows-code-checks-20261018/authentic-inputs-and-alpha.json`
- `p8-shadows-private-validation-20261018/offline-validation-receipt.json`
- `p8-shadows-runtime-validation-20261018/bounded-runtime-technical-receipt.json`
- `p8-shadows-runtime-validation-20261018/RUNTIME_RESULT.md`
- `p8-shadows-runtime-validation-20261018/runtime-pair-attempt1/runtime-evidence-manifest.json`
- `p8-shadows-final-review-20261018/static-scope-receipt.json`

Frozen runtime input manifest SHA-256:
`3c0f26e65fe05581b021a4a9819a4d03f2cdb3ca3f1a5e1cf5eb2f7b6207574a`.
Prelaunch schedule proof SHA-256:
`268a099a9cddfc59ed0526ada23fbc1f63042ef189c07d12c6f3c756f6e0010b`.
Runtime evidence manifest SHA-256:
`a78214a9c1cd02c607d4eea02af6fc1285fdf240d99a886af45cb36d386d3cf1`.
Offline receipt SHA-256:
`a84f57795e0f607d5cd970ed4413a738002ed383e0c65923700240881563b903`.

## Known inherited failure

The source-inverse test still exits 1 because its preserved published
21517-byte fixture expects the older head-only `entity_draw.c` wrapper. That
failure predates this batch and remains explicitly open. This batch does not
claim that all repository tests pass.

The separately denied replacement projection JSON was not opened, copied,
repackaged or transferred. The old published fixture and inverse test remain
unchanged. Historical Git metadata and previously blocked indexes are
preserved. No fresh repository snapshot, lazy fetch, Git network operation,
push or publication is part of this batch.
