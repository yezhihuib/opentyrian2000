# Vulcan: two authored player tracer heads

Historical head-only checkpoint: `4e75dbda875922303fda92d514fe6d9755e40696`.
The coarse shadows described below belong to that retained baseline. The current
[finite shadow follow-up](../player-vulcan-shadow-v1/README.md) has separate source and actual-runtime evidence.
Head-only binding-test commands below target that historical checkout; current
shadow tests are described in `docs/PLAYER_VULCAN_SHADOWS.md`.


Status: Source/unit checks, independent numeric review and author review pass for the bounded P1/P7 native 2× cases.
These are release-preparation notes; publication is a separate action.

## Finite display scope

Normal player bank 8 IDs 67 and 70 use two frozen, newly authored vector tracers:
a narrow single head for front Vulcan port 7 powers 1–6, and parallel bright
cores for powers 7–11. Both are static images on the original logical 12×14
canvas, anchor (0, 0), with density-8 straight RGBA sources. Shot phase cycling
remains original gameplay, not added art animation. The [frozen art package](../../assets/hd/artwork/player-vulcan-two-v1/README.md)
contains the sources, deterministic rebuild and authored-only checks.

The only production source change is in `src/render_mirror.c`: role 8 slots
522/523, capacity 524, a normal-only `!xmas` guard before cache lookup, and
explicit preservation of original indexed shadows. Slots 507–521 remain unused
in this independent candidate. Both current default packs add only the two
head resources; each moves from 515 to 517 manifest entries and from 521 to
523 effective physical HDA files. Existing resources, including six unlisted
HDA files in each pack, remain unchanged. Each head independently retains the
existing density 8 → 4 → indexed fallback.

The same normal player identities are also used by Single Shot Option 1,
Satellite Marlo 30 and rear weapon 15 charge stages 0/1. Their two heads share
this display route; option bodies, later charge stages, linked fire and the
ordinary rear Vulcan heads are outside this change. Enemy and shop routes stay
original. Christmas retains its original ice-blue heads, including with warm
normal caches. The original coarse gray indexed shadows remain a known visual
limitation; this pair does not redraw them.

## Bounded checks

- Exact original-source units cover all 11 powers in all three table groups,
  including two phase cycles per row, creation, drift clamp, movement, cadence
  and power failure. Renderer checks cover both packs, finite routing, cache
  transitions, indexed shadows, malformed/missing resources, clipping, alpha
  and ordered composition. Independent source review and exact art rebuild
  pass. ASan/UBSan are active; leak detection is disabled.
- Four actual Linux SDL dummy/software engine runs compare baseline and
  candidate at P1 and P7. Each executes 90 logic ticks (0–89) in Episode 1,
  physical level 9, Normal story mode, with seed `0x5eed`. The loadout is set
  once by diagnostic setup. A deterministic input-only adapter supplies native
  demo-key bits to original movement and firing routines. This is not natural
  weapon acquisition or manual input. No projectile helper, power refill or
  added protection is used; original spawn protection counts down from 100
  to 10 and original shield recharge remains active.
- Each run retains six actual native 640×400 frames and six palette-correct
  320×200 INDEX8 frames at ticks 38–43: 24 native and 24 INDEX8 images total.
  P1 records 39 requests and emissions, 19 complete phase cycles, 497 head
  draws and 465 indexed shadows. P7 records 27 requests, 26 emissions, six
  complete phase cycles, 334 head draws and 312 indexed shadows. Its one
  original power failure at tick 16 is preserved. Counts are per run and match
  within each baseline/candidate pair.
- All 90 ticks match in recorded original state, RNG, shot/request/result/
  emission/draw/collision and other original traces. Paired captured INDEX8
  output is exact, non-target draws match, and native RGB changes are confined
  to target-head rectangles. Every candidate capture contains exact authored
  fully opaque core samples; the window includes visible shots born with both
  negative and positive player drift. Full arbitrary fractional-alpha runtime
  composition is not inferred from these image pairs; that coverage is from
  the reviewed source/compositor units. Collision logs contain no observed
  collision events, so their equality does not establish collision coverage.

The author directly reviewed all twelve candidate and twelve paired baseline
native frames. The single and twin warm tracers remain readable over bright
clouds and brown rocky terrain; the P7 pair retains separate luminous cores.
No added halo, trail or visible head-form/color flicker appears in this
six-frame window. The original coarse indexed shadows remain visible.

No native 4× game, Christmas game, other-episode game, all-eleven-power game
matrix, shared-option/rear-charge live play, natural upgrade acquisition,
long-tail motion, unprotected survival, manual Windows play, physical
GPU/fullscreen or performance acceptance is claimed. The all-power and
Christmas checks above are source/unit evidence.

[Runtime/source summary](runtime-summary.json) and [author-review summary](author-review-summary.json)
contain portable hashes and bounded results. The earlier [implementation
checkpoint](../PLAYER_VULCAN_TWO.md) and its source-only receipts remain
historical records. Original game data, reference RGB/index grids, actual
gameplay images and private fixture logs are excluded from these public notes.
