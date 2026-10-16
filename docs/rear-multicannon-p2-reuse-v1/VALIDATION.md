# Rear Multi-Cannon P2: bounded reuse of the six R2 heads

Baseline: `311de82e7557b9df172a1cb19d94115609512a81`.

Status: **PASS: bounded source, unchanged-art reuse and native runtime qualification**.

## Scope

This candidate extends the existing player-one rear Multi-Cannon 10 renderer
provenance from power one to power two on episode-one Normal (physical level 9)
and Hard (physical level 15). It does not introduce artwork or a generic sprite-ID
binding. Existing P1 records 254/265 retain their one-emission semantics. P2
records 255/266 use the same six static source heads, velocities and full-canvas
12×14 geometry, but emit two heads per successful call with shot repeats 6/4.

All existing R2 SVG, PNG, RGBA and HDA bytes, role 131, resource keys, logical
anchors, density selection and cache contracts are reused unchanged. The artwork
package and P1 qualification record describe the original P1 delivery; this
separate integration record describes the later P2 extension. Resource filenames
retain their existing P1 prefix for compatibility.

The source guard must qualify each emission using its original main-weapon call,
exact full-record identity, phase, slot allocation, source bank and immutable
shot fields. A finite call-scoped budget must cover both P2 heads, clear on call
return and preserve cyclic phase continuation after partial slot exhaustion.
Original gameplay, INDEX8 writes, palette, RNG, collision and draw ordering remain
authoritative. P3 and other consumers of the same six sprites remain excluded.

## Finite call ownership

The existing main-gameplay wrapper arms an exact power/mode/record grant. The
next actual `player_shot_create` entry claims a renderer-owned invocation token.
An unwrapped or nested entry invalidates the outer grant, even when its tuple and
logic tick match. Each allocation observation supplies that token and the
original loop ordinal; P1 has one permit and P2 has two. Every create return and
the outer wrapper end clear any remainder. No gameplay structure stores a token.

The first canonical phase may be any position in the record's original cycle.
The second must be its cyclic successor, with a distinct allocated slot. This
preserves valid continuation after the original allocator exhausts capacity
mid-pair. A rejected allocation cancels all remaining permits; it never donates
one to a later observation. Every actual reused ordinary slot first loses its
previous renderer birth. A valid first birth remains independent when a later
allocation elsewhere fails or capacity is exhausted.

All four exact records are stamped in original loader order, including unused
array tails. New P2 FNV1a64 pins are `f92503c1cf7f8a67` for record 255 and
`16186b7836a64d47` for record 266. Existing source-bank size, normal-bank pointer,
decoded indices/coverage, exact density/payload, alignment, non-aliasing,
nonblocking regular-file load and cache-lifetime checks remain in force.

## Fresh runtime results

Final hardened V2 source passed 18 fresh paired cases, 36 game processes and
4,560 logic ticks. Sixteen pairs retain unmodified manual-HD startup at density 8;
two Normal/Hard native 2× pairs use separately pinned reversible private
presentation-only density 4 selection. All 748 native gameplay captures and
108 shop captures pass the recorded full-frame pixel checks. Four preliminary
pairs on the superseded source freeze are excluded.

Natural menus buy rear Multi-Cannon P2 for 1500, leaving 8500. Original
`time(NULL)` seeds are observed independently and match within each pair; no
seed, gameplay-state, loadout or original-data override is used. Each standard
P2 run has 20 successful two-head calls, 5 natural power failures and 32 rear slot
reuses, including 12 slots previously used by front shots. Both ordinal 1 and 2
receive HD: 529 admitted head draws split 216/313 across their original births.

Original per-tick state/RNG, INDEX8 buffers, palettes, allocation, movement,
collision, input and original head/shadow/scene order remain exact. Full uploaded
and native differences stay inside admitted original/authored head support.
Fractional alpha is checked against the ordered underlay at every admitted draw;
ordinary and Hard night output are reconstructed pixel-for-pixel. Each member of
the three near-emission pairs contributes 115–130 changed final pixels at native
2×, including fractional samples surviving partial ship occlusion. Original
movement occurs before drawing: first rendered origins are 20/22 logical pixels
apart. Measured natural authored head-head overlap is 0; 48 independent synthetic
actual-compositor cases separately exercise overlap and ordering.

Fresh P1 regression, P3 shared-ID negatives and missing/corrupt-resource cases
are native-exact against the published P1 baseline. Mode 1→2→1, stopped firing
and clear frame 179 pass; repeated/skipped actual SDL Present does not change
state, RNG or admission. Private observers are removed with zero-fuzz inverses
for all six build variants, recovering all 160 production source files exactly.

Independent review recomputed 120 full native frames, all 20 original parity files
per pair and 96 exact native crop regions. Both exact-density routes and all six
shapes passed visual review. See `RUNTIME.json` and `INDEPENDENT_REVIEW.json` for
case details, pins, pixel evidence and coverage boundaries.

## Source and asset qualification

- The public actual-adapter suite passes 44,571 checks and 192 malformed-resource
  variants per plain and ASan/UBSan build. Direct ownership tests cover the
  stricter failed-first cancellation and repeated-slot rejection contract.
- Independent checks pass 48,267 core assertions, 33,230 authentic-source and
  actual-allocation checks, 41,651 adapter checks and 192 malformed-resource
  variants per plain and ASan/UBSan build. Every original 80-byte source record
  field, including unused tails, is mutation-tested.
- Actual original allocation functions are compared with their observer-stripped
  baseline across zero/one/two/three available slots, reserved slot 80 and cyclic
  partial continuation. No renderer observer changes original return values or
  gameplay writes.
- The public renderer-hook inverse restores all 156 pre-P1 original source files.
  All gameplay bytes outside the enumerated observation hooks remain exact.
- Ten strict runtime build variants have no warnings under the documented
  inherited-warning suppression policy. Disabled diagnostic builds retain the
  same 15 inherited warnings and add none.
- All 6,987 asset files other than the current catalog remain byte-exact. The
  catalog changes only integration-scope text and pointers; reversing those
  metadata fields recovers its entire baseline. No artwork, resource payload,
  resource key, pack count or rollback-pack byte changes.
- Aggregate verification passes 18 packs, 3,414 HDA entries, 601 exact source PNGs
  and all existing sidecars. Both default packs remain at 589 resources. The
  frozen original art-stage binding stays unchanged, with the later integration
  scope explicitly identified by the current catalog and this document.

Completed immutable observations can be byte-compared and hard-linked for
storage after execution. Every original path/hash/process receipt is preserved;
no observation is substituted for fresh execution.

## Reproduction and limits

Run from the repository root:

    python tests/run_rear_multi_p1_core_tests.py
    python tests/run_rear_multi_p1_adapter_tests.py
    python tests/test_rear_multi_p1_source_inverse.py
    python prototype/build-rear-multicannon-p1-art.py
    python prototype/build-hd-assets.py

The established script names remain for compatibility and now include bounded
P1/P2 provenance checks. Public tests use synthetic source records and sprite
banks. Authentic original-data checks and actual gameplay captures are separate
private evidence; no original payloads or screenshots are distributed here.
The aggregate verifier reconstructs all runtime RGBA/header bytes in memory and
compares them to the installed files. An output directory is unnecessary for
this integration because no resource bytes change.

Public manual-HD startup continues to select density 8. Separately labeled
private density 4 presentation diagnostics do not add a new public startup mode.
Linux SDL dummy/software renderer readbacks establish actual native output in
that environment; they are not Windows, physical-GPU or full-campaign coverage.
ASan/UBSan runs disable LeakSanitizer because of the environment's ptrace setup;
there is no leak-check claim. Synthetic source/ownership tests do not stand in
for final display-pixel checks.
