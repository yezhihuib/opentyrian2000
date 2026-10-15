# Bounded vertical-clipping validation

Baseline: 17d6d000fe4bf76bc7774f0f636576c63d855515. This follow-up changes one
production predicate and its comment. The original in-bounds compatibility,
source identities, continuous operator and raw indexed blitter remain unchanged.

## Exact files and scope

- src/render_mirror.c
- prototype/test-plasma-projectile-blend.c
- prototype/test-plasma-projectile-blend.py
- prototype/test-plasma-projectile-scope.py
- docs/option-plasma-projectile-blend-v1/README.md
- docs/option-plasma-projectile-blend-v1/VALIDATION.md
- docs/option-plasma-projectile-vertical-v1/README.md
- docs/option-plasma-projectile-vertical-v1/VALIDATION.md

The two historical documents gain a banner identifying their original 17d6d000
scope and linking this follow-up; their recorded results stay unchanged.

The updated scope verifier proves both the combined exact inverse against
d98556a and this step's exact single-production-file inverse against 17d6d000,
across all 153 source files. The latter reverses exactly the comment and vertical
predicate, restoring every baseline source byte. All 6,722 assets retain exact
raw bytes and Git modes. Seven forbidden scope mutations are rejected. There
are no wild-cloud-policy, turret-bookkeeping, gameplay, source-dimension, raw-loop,
header, HDA or art changes.

## Exact-production units

Optimized and AddressSanitizer/UndefinedBehaviorSanitizer builds both pass with
identical deterministic results:

| Check | Per build |
| --- | ---: |
| Draws / candidate raw calls / baseline raw calls | 10,046 / 10,046 / 10,046 |
| Assertions | 64,367,833 |
| Original source-pixel callbacks | 8,888,387 |
| Every-height actual-palette draws | 4,608 |
| Every-height alternate-ramp draws | 864 |
| Edge-crossing ordered/repeated composition draws | 1,872 |
| Wholly offscreen original raw draws | 144 |
| Extreme-origin admission-only guards | 192 |
| Horizontal-wrap original raw draws | 240 |
| Hidden-row value / coverage mutations | 24 / 24 |

All source heights are covered from wholly offscreen through each visible top
and bottom height. Normal/Christmas originals, both densities 4/8, pitches 320/328,
owners 0/1/2 and mixed ownership, repeated pieces and six source-order permutations
are included. Alternate monotone palettes and independently nonmonotone color
channels exercise admission and fallback. All hidden-row mutations reject after
full-source decoding, even when the modified cells would not be visible.

The suite compares complete physical indexed buffers and exact ordered original
write traces against one baseline raw draw for every candidate draw. It also
checks complete RGBA and ownership results against its independent oracle:
3,277,728,512 indexed bytes and 88,629,248,000 RGBA bytes per build. The source-only
check proves the complete pixel helper remains exact and only the intended
vertical condition differs from 17d6d000 after removing comments; the original
raw-loop inverse still matches d98556a.

Extreme INT_MIN/MAX and malformed bytecode are guard-only tests. They do not
execute deliberately unsafe legacy arithmetic or malformed raw loops. The
existing negative-origin raw pointer construction is inherited unchanged;
this patch does not claim to harden it. No new HDA/resource lookup exists.
Unrelated isolated font/effect collaborators remain explicit test stubs.
LeakSanitizer is disabled for executor compatibility; ASan and UBSan are enabled.

Commands, using separate original data and fresh output paths outside checkout:

    python3 prototype/test-plasma-projectile-blend.py --source-only
    python3 prototype/test-plasma-projectile-blend.py --data /path/to/tyrian2000 --out /path/outside/checkout/plasma-vertical-units
    python3 prototype/test-plasma-projectile-scope.py --out /path/outside/checkout/plasma-vertical-scope.json

## Builds

Both 72-unit optimized production builds link and pass -Werror with the same
pre-existing misleading-indentation suppression. Both disabled-renderer
sprite.c/render_mirror.c compile checks pass strict warnings. Both 73-unit private
observer builds link. Zero-fuzz observer inverses restore all 153 frozen
production source files.

Full 72-unit classic-disabled builds link with standard flags in both variants;
the same 20 pre-existing warning lines occur. A strict full-classic baseline
attempt fails unused-variable warnings, and a second baseline diagnostic attempt
also fails unused-parameter warnings. Candidate strict full-classic is not run.
No unrelated warning is fixed or described as a warning-free strict build.

## Four original-engine processes

Exactly four original-menu Linux SDL dummy/software processes completed in one
attempt: Normal physical 9 and Hard physical 15, baseline/candidate, 320 logic ticks
each. All exit 0 with matching original time(NULL) seeds. No seed, time, RNG,
position, money, equipment, protection, refill, animation or gameplay state is
overridden. Complete frozen production/observer sources, binaries, live/frozen
physical packs, original private data, helpers and dependency pins stay unchanged.

All processes use the same original first-shop RIGHT Plasma9 purchase at 9500
from 10000, committed cash 500 and left 0/right 9. Default Space is held from tick 0;
six one-tick default Right-secondary LeftAlt pulses occur at 100/108/116/124/132/140,
plus the empty seventh at 148. Six requests naturally emit 18 independent original
pieces; no additional request occurs at the empty attempt. This does not qualify
a later refill event or an actual left/dual purchase.

Every one of the 320 paired ticks in both difficulties has identical original
indexed game/display surfaces, palette, player/enemy/shot/particle/global hashes,
RNG fingerprints and original input/body/shot/emission/collision/raw-write traces.
Apart from screenshot fingerprints, the only expected diagnostic difference
is the newly successful vertical admission. Source dimensions, radii, original writes and ordered raw calls remain
exact.

Direct begin-return records and complete ordered pixel records agree for every
raw draw in both variants. Per difficulty:

| Witness | Baseline | Candidate |
| --- | ---: | ---: |
| Original raw draws | 312 | 312 |
| Original indexed writes | 391,968 | 391,968 |
| Admitted pieces | 276 | 312 |
| Fallback pieces in this fixture | 36 | 0 |

The 36 newly admitted pieces are exactly 30 top-clipped draws with 24,270 original
writes and 6 bottom-clipped draws with 6,312 writes. All have horizontally contained
rectangles; total new vertical writes are 30,582. Both variants independently pass
the RGB/owner/expected-index oracle at every eligible callback. Newly admitted
candidate writes observe 1,952,829 genuine-HD owner 1 subpixels, all actually
modulated, plus 4,419 exact indexed owner 0 subpixels, with zero formula, owner or
ledger mismatches. Owner 2 does not naturally occur here and remains unit-only.

## Same-HD native-scale controls

Both variants already include the published in-bounds compatibility, identical
manual-HD flags and density 8, and byte-identical 565-file/560-HDA selected packs.
No earlier HD upgrade or source art is added by this comparison.

All 92 actual 640×400 native 2× screenshots pass every PNG chunk CRC, including
IEND. All shop pairs and captured prefire 0..100 frames match byte-for-byte.
In-bounds shot controls at 103/107/111/140/148 also match, as do post-shot 190/220/319.
Actual bottom clipping at 101 and top clipping at 149/160 show the new result;
115 is another mixed-frame difference. Native comparison sheets use unchanged
full screenshot pixels with labels outside them, without resampling, recoloring,
reconstruction or repair.

The first board helper incorrectly expected a difference at 140. Its assertion
and logs are retained; analysis-only board labels were corrected using the same
captured 149 top-clipping frame. There was no engine rerun, source change or
pixel repair. Both original traces and pixel-oracle analysis had already passed.

Avoiding the generic restoration path can retain connected HD objects beyond
the clipped source cells. That mechanism follows the unchanged frozen source
and the same-HD controls; direct per-restore rectangle/count logs are not claimed.

## Qualification limits

The original source art remains pixelated at native 2×; there is no contour
redesign. Horizontal-wrap, wholly offscreen, incompatible source/palette/context
and unrelated effects retain fallback. Zero fallback in this finite fixture does
not mean all fallback is removed. Wild-cloud policy and turret bookkeeping are
untouched.

This is bounded first-level, normal-data, local single-player RIGHT-weapon 88
qualification. No actual owner 2, weapon 1088 firing, left/dual purchase, Christmas,
later refill, native 4× runtime, full-level/campaign, Windows, physical GPU or
performance qualification is claimed. No screenshots or original game data are
uploaded.
