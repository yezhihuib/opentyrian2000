# Rear Multi-Cannon P11 mode 1: exact six-shot route

Baseline commit `aa6525857f45bc5d434142060da9bb02788f72ce`, tree
`5bfd67a6577c003842e1b01e31afee1467235ff9`.

## Exact scope

Adds ordinary player 1, rear port 10 / bay 1, power index 10, mode index 0,
physical normal record 264. Full 80-byte FNV-1a64 is `88af50784f345394`;
SHA256 is `b1f371caa5d050fc279aa63b3dcccaefff3a1c00c7f8351edc5cccea83a43adb`.
All nonzero inactive entry-7/8 tails are authenticated. Identical physical
alias 1264 remains excluded.

Ordered raws: 277, 278, 297, 296, 43, 5. Exact budget / period / repeat are
6 / 6 / 6. Original velocities are (-9,-2), (9,-2), (9,2), (-9,2),
(-10,0), (10,0); birth dx is -2,2,2,-2,0,0 and dy is zero. Damage is
2,2,2,2,5,5 and lifetime 255. Drawing stays at current (shotX+1, shotY),
12x14 canvas, anchor (0,0). Admission requires exact op[0][10]==264,
full record/source pins, live-shot integrity and original birth identity.

Only four production files change: renderer provenance core, its header,
dedicated adapter and pin header. All other 156 current source files are
byte-identical to the published baseline; the unchanged inherited
original-source inverse passes all 156 applicable files. Renderer cap 8 and
80 owned slots remain. Original allocator 81 slots, first-free allocation,
partial-capacity phase progression, power-40 charge, repeat spacing,
movement, collision and RNG logic are unchanged. Slot 80 remains native
fallback. Observed-only 163/164 remain pass-through. All 21 older routes,
especially 263/274/275, retain their source/resource indices and pins.
Totals are now 22 exact routes / 105 canonical phases, 25 drawable and
27 observed identities.

Normal physical level 9 / Hard physical level 15 scope and all other
Christmas, network, multiplayer, linked, galaga, demo, record, action,
super, timed and bonus exclusions are unchanged. The role applies only to
qualified normal heads, never generic/shared bank-8 or shadow consumers.

## New five-lobe artwork

Original 43/5 each cover 115 cells with five isolated brightest highlights,
and are exact horizontal source reflections. No accepted rigid transform
or translation equivalence is established. Selected A2 is newly authored
smooth cubic semantic geometry: outer, shoulder and central lobes with
vertical counterparts, warm yellow/orange/red heat fields and inward soft
coverage. Original pixel staircases are not SVG geometry. Rebuild needs no
original game source raster or capture.

The parent reviewed actual 1x/2x/4x small previews across neutral/dark/bright
backgrounds. Initial open A was chosen over fuller B, then its d8-to-1x
strict yellow-threshold projection exposed only four bright-core groups.
A2 preserves A paths, support and alpha exactly, expanding only center
heat-field width 1.13 to 1.30. Renewed small-size review selected exact A2,
replacing A approval. Original A/B/A2 evidence remains private. Both IDs at
both densities have five finite yellow-threshold groups in every 1x/2x/4x
projection; the d8-to-1x middle group is only one sample. This metric is not
an all-scene visibility guarantee.

Densities 4 and 8 are independently vector-rendered, without a native-1x
intermediate or cross-density resampling/fallback. Canonical raw-5 RGBA is
exact full-canvas byte reflection of raw 43. Independently rasterizing the
transformed raw-5 SVG has disclosed antialiasing differences; it is not the
canonical packed payload. Transparent pixels have zero RGB, no supported
pixel is black, and no external halo is added. Inward softening changes
alpha only without adding/removing support or changing straight RGB.

Four exact resources add 43/5 at d4/d8 to each existing default pack,
four global source PNG mappings and one family descriptor. The portable
generated-only artwork package includes exact rebuild/version pins and a
self-excluding file manifest. Removing catalog additions recovers the
baseline manifest byte-exact. Default pack counts are 621 to 625 each;
the separate private common selected runtime pack is 633 to 637 files,
with all 633 predecessor files byte-exact. Relocated package-only rebuild
reproduces all 11 frozen outputs and four HDR1 resources exactly.

## Core, adapter, inputs and build

- 21 core fixtures pass strict C99 plain and ASan/UBSan, 42 runs. New 264
  executes 3,305,349 checks per lane: 294 cyclic prior/new capacity designs,
  every 80x80 slot pair, leases, repeated-slot rejection, seals, wrong
  modes/aliases and all 22 routes / 105 phases in bounded mixed cohorts.
- Four authentic-input checkers validate 22 full80 record pins and 27 decoded
  source pins. New 264 covers exact fields, nonzero inactive tails, 80
  single-byte mutations and excluded 1264. Independent review checks all
  640 single-bit mutations and all older pin/map prefixes.
- Initial attempts failed on a stale P5 FIRST negative oracle expecting
  exact-264 admission to fail. Migrated P2/P5/P6 fixtures require that exact
  grant while still rejecting their mismatched old shots. Failed logs and
  one helper failure remain preserved. No negative emit was skipped and no
  production rejection assertion was weakened.
- Full adapter strict/plain and ASan/UBSan each pass 17,080,056 checks and
  800 malformed variants. Preserved P10 pending-art lanes each pass 983
  checks; P11 pending-art lanes each pass 1,123. Synthetic pin overrides are
  explicitly verified before guarded production headers, so later production
  artwork pins cannot change those synthetic fixture identities.
- Reviewed A2 generated-art plain and ASan/UBSan each pass 1,420,050 checks,
  24 whole-pack missing/corrupt isolation cases and 64 malformed 43/5 variants.
  All 48 nonzero RGBA roles match production pins; all four new payloads
  match exact approved A2 hashes. Source/record fixtures remain synthetic;
  RGBA payloads and pins are production-exact. No density fallback is added.
- Full uninstrumented strict build passes the inherited pedantic / Wall /
  Wextra / Werror policy and existing warning exclusions, with no new
  suppression. No Windows build is claimed.

## Actual offline compositor and fallback

Private authentic original records/source and reviewed A2 artwork execute
copied actual adapter/core/decoder/loader, extracted compositor/classic
blit/normal wrapper and SDL software path in finite synthetic scenes.
These are separate from ordinary gameplay timing/acquisition evidence.

Main: 42,337,191 checks, 431 scenes, 1,548 admitted draws and 163 native
640x400 readbacks. All 15 new phase pairs, both orders, ages 0/1/2/4/8/16
and d4/d8 yield 360 cases, 60 ordered pair/density tuples and 30 disjoint
original-rectangle pair/density tuples at age 16. Full six-head ages 0..16,
clipping, and 32 mixed protected-275/new-264 retained-identity/restoration
cases match independent ordered integer-alpha, full-canvas, owner-mask and
native-nearest oracles. Bounds tests do not claim every head is visible.

56 separate cold-cache missing/corrupt processes cover all six new-264 and
eight protected-275 phases at both densities. Optional failure preserves
qualified birth and unaffected siblings. Actual classic normal wrapper,
indexed blit and native output equal direct original blit and independent
decoded classic oracle. Unrelated generic/font/shadow families are stubbed
in this finite fallback fixture. Intentional alpha-rounding, owner-write
and restoration-pixel mutations each fail the independent oracle; expected
failures remain preserved.

Offline processes/builds have 512MiB address-space caps, aggregate evidence
512MiB cap and 4GiB free-disk floor. Main peak virtual memory is 116,412,416
bytes. The parent inspected all three actual 640x400 bright/separated/initial-
overlap images: five warm lobes read clearly when separated, no black box
or pixel-mosaic highlight; initial overlap follows original birth positions.
Only this bounded offline visual scope is accepted.

## One bounded ordinary runtime pair

Exactly one independently reviewed 180-tick baseline/candidate pair ran.
Both retain ordinary title / New Game / Full Game / Episode 1 / Normal /
shop acquisition at P4. The original time(NULL) seed and complete natural
RNG, player/shop and entry snapshots match through read-only rendezvous.
No render-test/demo bootstrap is used.

Two explicit diagnostic rear-power-byte changes are P4 to P10 at tick 0,
and P10 to P11 at tick 50 while in mode 1. Each changes only that byte,
with exact player/RNG snapshots checked. Actual SDL handlers switch mode 1
to 2 at tick 50 (observed 51) and mode 2 to 1 at tick 110 (observed 111).
The resulting cohorts are protected 263, protected 275, then new 264.
This does not claim ordinary P10/P11 purchases or P11 acquisition gameplay.

Both processes exit 0 at exactly 180 ticks in 45.11 seconds. One attempt,
no rerun. Each captures 16 groups / 48 BMPs: baseline output 284,259,868
bytes, candidate 284,306,645 bytes. Each process has 512MiB address-space
and capture caps, pair cap 1GiB and 4GiB free-disk guard, with live kernel
limit observations. The approved manifest seals recursive source inputs,
including nested third-party headers; independent inverse application only
in fresh audit copies restores each authorized build input byte-exact.

All 132 analyzer checks pass with no gaps. All 20 named telemetry streams
are byte-identical. Four mixed streams compare explicitly listed original /
nonchanging fields and all four projections match; renderer fields are
excluded explicitly. Every one of 180 frames is hd-ordered with zero
coverage mismatch and exactly empty rejection text. The original writer's
empty text means no rejection; nonempty/unknown text fails.

- Actual request outcomes: 69 complete and 12 original power failures.
  Complete sampled cohorts start at ticks 4,54,114 with exact 6/8/6 ordered,
  unique-slot births and original phase/raw/velocity tuples.
- Eligible/admitted normal-head draws are 263:602/602, 275:608/608 and
  264:732/732, with no missing/unexpected draw. Old 263/275 retain 113/73
  admitted draws after their switches. Protected draw rows are byte-identical;
  new 264 has all six phases with stable original birth/slot seals. Baseline
  264 remains genuine classic fallback despite the same common pack.
- Every optional draw checks ordered alpha/ownership. Actual uploaded output
  equals native SDL 640x400 nearest readback at every sample. Observed
  baseline/candidate differences remain inside actual-264 viewport rectangles.
  This is not an ideal whole-game-frame reconstruction.
- Original fades remain intact. All sampled pre-110 native/upload whole
  frames are unconditionally equal, and every protected 263/275 phase has
  final visible support in a fullframe-equal capture. Protected faded art is
  not compared to raw unfaded RGB. New-264 finite visibility is tied to
  uncovered exact-owner opaque authored support that differs from both
  baseline and classic, without requiring unfaded RGB equality.
- All six new phases have final visible support at tick 115, counts
  73,78,73,79,180,186. Mixed old/new support is visible after both switches.
  Cropping and initial overlap remain natural; broad all-pair separation
  is proved only in the independent offline scenes.

The parent personally reviewed unchanged raw native frames 55,115,118 at
640x400 and accepted the bounded runtime visual scope: five separated warm
lobes, clear yellow cores/orange-red edges on bright clouds, no black box
or obvious pixel stairs, and no obvious older-mode degradation.

## Remaining limits and publication boundary

No full campaign, ideal whole-game-frame, Windows, GPU, fullscreen,
performance or broader acquisition certification. Runtime uses SDL dummy /
software at native 2x; d4/d8 asset and compositor checks are separate from a
native-4x ordinary game run. Natural RNG is matched for this one pair only.
A one-sample 1x yellow-core witness is a limited metric. Optional resources
remain fail-closed and per-head classic fallback is intentional.

All work is local. No GitHub write, commit, branch update or publication is
authorized by these checks. The final exact file/byte/hash batch needs
separate user approval before upload.
