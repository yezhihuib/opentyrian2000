# Data cube: twelve authored body phases

Status: source/unit checks, bounded numeric evidence and author review pass
for 36 actual native 2× frames and four native 4× bright-body spots.
These are release-preparation notes; publication is a separate action.

## Finite display scope

Record 513 uses twelve authored vector body images across the original twenty
held draws: beige/silver, gold, red-orange and green light groups. This is one
fixed-orientation cube. The original animation order, logical 24×28 canvas,
anchor (6, 7), four ordered quadrant draws, filters and indexed writes remain.
All twelve authored alpha fields are identical. No glow, trail or extra phase
is added. The [art package](../../assets/hd/artwork/data513-twelve-v1/README.md)
contains the approved sources, exact rebuild and authored-only proof contacts.
Those contacts are offline art views, not actual-engine captures.

The display branch is restricted to record 513, size 1 and the actual sprite
sheet 11. Role 124 occupies slots 510–521. Every member must pass the exact
header, density-8 payload and EOF checks; one missing or invalid member returns
the whole Data body family to classic. Record 512, including its shared base
273, is excluded. Original fixed 266 Data lettering and its blend path are
unchanged. The only production source change is in `src/render_mirror.c`;
movement, collision, reward, event, RNG and pool code are unchanged.

## Bounded checks

- Original-source units: 137 scenarios and 2,667 checks in each optimized and
  ASan/UBSan build. These isolated units are separate from engine evidence.
- Renderer units: all twelve resources, all 256 filters, ordered quadrants,
  indexed parity, clipping/row-wrap, wrong-context exclusions and 170 resource
  rejection cases. Independent review passed, including a source-only exact
  art rebuild. LeakSanitizer was disabled; ASan and UBSan were active.
- Actual engine: three starts, one no-image baseline, one native 2× candidate
  and one native 4× candidate, with no retries. Each runs 795 logic ticks through
  tick 794. The deterministic Linux software-renderer
  case uses Episode 1 / physical level 9, Normal/story, seed `0x5eed`, no Christmas
  mode, original movement/fire input, and no shot helper or added protection.
- Observed carrier hits at 713, 716 and 718 produce the drop at 718. There are
  61 body draws / 244 quadrant calls. Collection at 779 changes `cubeMax` from
  0 to 1, with zero pickup cash; the carrier separately contributes 20 cash.
  Original fixed 266 draws fourteen times at 779–792 and is clear at 793/794.
- The candidate's 36 actual 640×400 images cover 739–758 and 779–794. All 18
  baseline comparisons are exact: sixteen original streams, control without
  wall time and fixed-266 render rows. Hashes of both indexed surfaces and
  explicit cube state are included. Each of the twenty canonical body frames
  has 353/353 source-support cells matching the final indexed output. This numeric exposure
  check alone cannot distinguish equal-color overdraw. Separate author review
  of all 36 actual native 2× frames passed on brown stone/earth terrain.

The baseline contains no RGB images, so there is no baseline/candidate RGB
comparison or outside-body RGB equality claim. The four actual 1280×800
captures at 741, 746, 751 and 756 also pass numeric and author review, with the
same eighteen baseline comparisons exact. These are bright body/color spots
only. The native 4× run retains full-lifecycle telemetry, but has no visual
full-cycle, collection, DATA-lifetime or clear-frame acceptance. Fallback is covered by source
units, not a missing-resource engine run. This is not whole-level, other-mode,
all-episode, Windows, manual-play, physical GPU/fullscreen or performance
acceptance. Later Data carriers and result/menu behavior are outside the case.

[Runtime/source summary](runtime-summary.json) and
[author-review status](author-review-summary.json) contain portable hashes and
counts. Original game data, reference pixels/index grids, actual gameplay
images and private fixture logs are excluded from these public notes.
