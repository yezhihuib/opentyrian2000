# Rear MultiCannon P6 FIRST259 / SECOND270 shadows

## Scope and authentic inputs

This local presentation-only batch adds physical FIRST259 mode1 and SECOND270
mode2 to the existing birth-owned density 8 shadow path. All 22 accepted normal
head routes and all 10 P7–P11 shadow routes remain unchanged; the10 P1–P5
physical shadow routes keep their prior behavior. No artwork, global bank8
binding, asset pin, loader, gameplay, coordinates, RNG, allocation, firing,
collision, native indexed darkening or compositor changes are included.

The exact three files are this document, `src/rear_multi_p11_shadow.inc` and
`tests/rear_multi_p11_shadow_test.c`. Historical function/include names remain.
Original assets, private instrumentation, executables and captures stay outside
Git. The local parent is `a5e1bd97236da7b50b9e15128a0a3fa2429d758f` on
`local-hd-shadow-batches`. Its independent local snapshot ancestry is not
GitHub ancestry. Published P9/P8/P7 file provenance is
`7bc896a0ce6adacc27619673303fe11b7499ca62`. There is no remote, promisor or
partial-clone configuration, and this batch does not authorize publication.

Actual original full 80-byte HDT records were inspected before implementation.
The original HDT SHA256 is
`fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b`.
Both records have shotrepeat 6, aim 0 and physical selector power index5. Loader
byte 2 is shotrepeat, byte 3 multi, byte 6 max and byte 9 aim.

- FIRST259: multi/max3/3; phase raws41,3,77. Original sx=-10,10,0;
  sy=0,0,-10; bx/by all 0. Full80 SHA256:
  `744d6ecf94d5b0a58e87e1ec261148cd62f73377f4cf3b1e066b9352146716f4`.
- SECOND270: multi/max5/5; phase raws277,278,183,182,77. Original
  sx=-9,9,6,-6,0; sy=2,2,-6,-6,-10; bx=-2,2,4,-4,0; by all 0.
  Full80 SHA256:
  `752ee35625dd482937b024bc287d993b022f38d992785f02d960f24804427a45`.

The original initializer negates sy for live y velocity. Each phase uses its
own exact accepted density 8 head HDA alpha, never its RGB. All seven unique
payloads match existing production pins; no generated, reflected, substituted
or resampled alpha is introduced. The existing density 4 exclusion for182/183
is preserved. All 22 full 80 record pins and all 27 decoded source pins were
independently verified. Original SHP SHA256 is
`80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0`;
original32060-byte bank8 SHA256 is
`9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68`.

## Admission and preservation

Only the finite record lists change among 161 production files. All existing
qualified birth, live slot/generation/full birth seal, raw/phase/live-shot,
full 80 table integrity, physical selector, original source-bank pointer/size/
decoded pin, resource-root/density and accepted asset checks remain intact.

Scope remains actual Episode1 first-level Normal, physical level 9,
background 2, density 8, authentic INDEX8 surface and canvas layout, safe pitch
and ownership storage, original x=shotX+1, y=shotY+shadowYDist, y<190, admitted
clipping and finite command capacity. Hard/physical15 shadows retain fallback.
Prepared command coverage, pointers, pitches, coordinates, tick and alpha are
revalidated at execution. Switches do not relabel old births, shared raws do
not obtain another physical-record lease, and the original final drawn
counter 0 tick remains eligible. Missing/corrupt/unavailable optional alpha
retains native fallback. Native indexed shadow darkening still runs exactly
once; ordered overlap/cloud ownership, classic restoration and nearest-sampled
SDL upload are unchanged. Preparation alone is not a visible-owner witness.

## Validation

### Code and bounded offline SDL

Strict C99/O2/Wall/Wextra/Werror full game build passes. All 21 core suites pass
plain and ASan+UBSan,42 runs. The unchanged adapter suite passes 17,080,056 checks
per mode with 800 malformed-resource variants; retained pending-art guards pass
983/1123 checks per mode. Shadow preparation/epoch guards pass 792,788 checks
per mode:12 roles,71 phases, all 80 slots,96 negative families, every serialized
record byte,16 malformed-resource families, aliases and retained/reset births.
An independent reviewer caught a new test expectation that incorrectly assumed
density 4 heads for182/183. It was corrected before shadow-test compilation;
production behavior did not change. Both shadow executions passed first try.

Offline actual decoder/optional-loader/wrapper/native blitter/birth/compositor
checks pass 280 finite scenes plus32 accepted boundaries per side/build,
1248 scene executions total, plain and ASan+UBSan. These include every new
phase, bounded pair orders/cohorts/ages, cloud/terrain/indexed underlays,
switches, restoration, clipping and native-once behavior. All 32 fresh-process
missing/corrupt fallback executions and32 deliberately wrong own-alpha/
double-darkening oracle executions pass. Candidate312 negative checks include
72 independently recomputed full-birth-seal rejections across all 8 new phases;
baseline has 280 negatives. Representative guard/lease families are finite,
not a Cartesian or exhaustive claim.

All 86 protected RGBA/owner/cloud/INDEX8 rows match across four runs. All 48
strict/sanitizer native BMP comparisons are exact. All 20 protected P7–P11
baseline/candidate native pairs are unchanged; only4 P6 pairs differ. All 57
monitored first attempts pass with no failures/reruns. Peak capture RSS is
136,273,920 bytes, minimum free disk17,665,527,808 bytes; offline evidence is
125,311,895 bytes. The 512 MiB child-RSS watchdog and4 GiB disk floor apply from
first execution. Compiler RSS and sanitizer virtual addresses are exempt;
leak detection is disabled.

Offline tests are constructed SDL software-renderer scenes with canonical
starts, finite cohorts/pairs and representative mutations. They do not cover
live gameplay/allocator/lifetime loops or GPU behavior. Generic 13 reuses frozen
accepted loader outputs; its file loader is not independently retested.

### One actual-menu180-tick pair:281/283

One baseline/candidate pair exits0/0 in62.68 seconds through actual NewGame,
FullGame, Episode1, Normal and a genuine rear-port10 shop P4 purchase. The
baseline is the exact P7 local parent. Private instrumentation reverses exactly
to each original src+Makefile. Original HDT/SHP/bank8 and all 637 accepted pack
files are verified before/after launch. Natural seed, all 627 RNG words,
purchasedP4 and entry state match. This is instrumented diagnostic play,
not an uninstrumented playthrough or a render-test/demo admission claim.

Six disclosed single power-byte changes are4->6 at0,6->7 at64,7->8 at88,
8->9 at112,9->10 at136 and10->11 at160, preserving all other state/RNG.
Actual SDL mode keydowns40/76/100/124/148/172 are observed one tick later.
The fixed route order is259/270/271/260/261/272/273/262/263/274/275/264,
with stage boundaries0/40/64/76/88/100/112/124/136/148/160/172/180.

Capture ages were derived from original motion, firing order, eligibility and
viewport geometry before launch:259 age1;270 ages1/4; protected271 has telemetry
only, other9 protected routes age1; terminal 179. The exact13 actual capture
ticks are34,41,44,83,90,108,115,129,143,150,164,178,179. No retuning, additional
capture or rerun follows. No complete protected-native-capture claim is made.

FIRST259 has 5 complete authentic calls/15 births and150 eligible shadows;
SECOND270 has 4 calls/20 births and152 eligible shadows. Every eligible shadow
admits exactly once with zero independent full clipped12x14x8 rectangle-oracle
errors, including own alpha, seal, RGBA/owner/cloud/green/selection state and
whole pre-native INDEX8. All 160/176 eligible new normal heads admit exactly
once. All 10 protected routes retain912 exact paired shadow admissions; actual
complete calls per protected record are1 or2, not an assumed2 each. Ordered
cyclic raw/velocity tuples and allocator slots verify; old births retain their
identity across all 11 stage transitions.

All 20 original observation streams and4 explicitly listed original/nonchanging
mixed-field projections match. Each of1304 original shadows per side executes
the native darkener exactly once; all 64000 INDEX8 bytes match the independent
one-pass original-RLE model. All 13 native640x400 readbacks match nearest
sampling of final2560x1600 uploads, and paired differences remain inside new
259/270 rectangles.

Strict isolated final-native witness counts are259 phases1/2=3/7 and270
phases1/2/3/4=2/2/1/1. FIRST259 phase 3 and SECOND270 phase 5 remain failed
visibility gates, so runtime is281/283. They have5/4 zero-error age1 admissions
respectively. In each sampled phase 130 authored native-grid alpha points
include128 below the528x368 gameplay viewport; the remaining2 overlap an
original head rectangle. There is no isolated final difference. Every original
head and every OTHER whole original shadow rectangle remains excluded from
attribution, including fallback/protected routes. Gates are unchanged.

Root and parent inspected all six actual unchanged-size640x400 BMPs at34/41/44:
cleaner cloud-shadow profiles with no obvious head/background movement. This
bounded visual acceptance does not close either phase's visibility gap.

Both strict private game builds pass first try. Final prelaunch selfchecks
pass plain/ASan+UBSan:71 cyclic starts,426 hostile mutations, exact17-action
controller/shop schedule, independent oracle and cap/owner guards. Two earlier
oracle-selfcheck compile setup failures lacked SDL include paths; retained logs
and corrected exact flags precede the sole game launch. No game rerun occurred.

Raw pair output is463,170,218 bytes; sealed runtime attempt465,381,649 bytes;
whole runtime directory484,756,806 bytes. Each game has a512 MiB address-space
cap; peak observed game RSS145,817,600 bytes and minimum free disk
17,687,519,232 bytes. The frozen runtime worst-case budget is516,328,004 bytes,
below512 MiB, including reserved analysis and six PNG exports. Compiler/ASan
virtual addresses are exempt. The 512 MiB limits apply per run/process. Combined retained offline+runtime
BMP/PNG files total560,723,815 bytes; this is disclosed separately from the
per-run caps. More than17 GB remains free. No cleanup or artificial retest was
needed, and all evidence is preserved.

## Receipts and inherited failure

External reproducibility receipts are adjacent to the checkout:

- `p6-shadows-code-checks-20261018/code-checks-summary.json`
- `p6-shadows-code-checks-20261018/authentic-inputs-and-alpha.json`
- `p6-shadows-private-validation-20261018/offline-validation-receipt.json`
- `p6-shadows-runtime-validation-20261018/bounded-runtime-technical-receipt.json`
- `p6-shadows-runtime-validation-20261018/RUNTIME_RESULT.md`
- `p6-shadows-runtime-validation-20261018/runtime-pair-attempt1/runtime-evidence-manifest.json`
- `p6-shadows-final-review-20261018/static-scope-review.json`

Offline receipt SHA256:
`20cc84ceb76f0c8d4fbeeaefffdcbf65156a27e7c93971d3d6c21c6689aa476c`.
Frozen runtime input manifest SHA256:
`9a4c2bd0b68e945007ced5638f34aed7ecfcef467e121ef7b9d93b9f2421e721`.
Runtime evidence manifest SHA256:
`3e91395058c9753bf7fd258ac016d8a21476467e46d76e37baba6d77f05bc956`.

The inherited source-inverse test still exits1: the preserved published
21517-byte projection expects the older head-only wrapper. It and the inverse
test are unchanged. This is not an all-repository-tests-pass claim. The denied
replacement projection was never opened, copied, repackaged or transferred.
All 93 historical metadata/blocked-index files remain exact. There is no Git
network operation, lazy fetch, push, publication or original-asset transfer.
