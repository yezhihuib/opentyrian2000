# Original-art Plasma projectile blend compatibility

This records the original 17d6d000 in-bounds batch. Its vertical-edge limitation
is superseded by the [bounded vertical follow-up](../option-plasma-projectile-vertical-v1/README.md);
the historical results below are unchanged.

This finite display-only change prevents the three original Plasma Storm pieces
from restoring classic pixels over an already rendered HD background. It adds no
replacement artwork, HDA resources, asset roles, source dimensions or game rules.

## Exact scope

The raw OPTION_SHAPES table5 sprites22/23/24 are three simultaneous independent
pieces, not animation frames or one combined sprite. Original weapon88 and its
1088 parallel bank select raw60023/60024/60025. Original pool records, allocation,
shot movement, collisions, per-piece positions, draw order and indexed calls are
unchanged. The special shot branch still calls blit_sprite_blend directly, once
per original draw. It does not enter the normal TILE/QUAD replacement pipeline.

Every raw blend draw gets a local boolean admission result. Only the three exact
current source identities can enter this compatibility path. Before every call,
the guard validates dimensions, safely decodes current indexed pixels and full
coverage, and hashes both in that order. There is no resource or source-admission
cache, so repeated draws and same-address reloads are checked again.

| OPTION_SHAPES | Original dimensions | Original writes | FNV1a64 indices + coverage |
| --- | --- | --- | --- |
| 22 | 62 × 24 | 1135 | 6d5e2fcad8f0a564 |
| 23 | 65 × 28 | 1699 | e38948558d55665d |
| 24 | 62 × 23 | 1076 | 2aae962a99b61745 |

Normal and Christmas originals match these identities and use the warm0x70 ramp.
The green Plasma sidekick body and its five replacement resources are unchanged.
Actual-game qualification of this change uses normal game data only.

## Blend and ownership

The original indexed loop always executes. Its exact result remains:

    destination = (source & 0xf0) |
                  (((destination & 0x0f) + (source & 0x0f)) / 2)

This overwrites the hue with the source hue and averages low nibbles with integer
truncation. It is not alpha-over. Indexed engine/display surfaces remain exact.

For true-color subpixels owned by genuine HD drawing (owner1), the existing
explosion_blend_rgba operator supplies a continuous approximation: take the
maximum RGB channel as HSV value, normalize that value to0..15 in fixed-point,
average it with the source low nibble, then interpolate adjacent entries of the
current source hue ramp. This intentionally retains continuous HD detail instead
of quantizing it to an indexed background. The approximation is not an exact
inversion of an arbitrary RGB color into a palette index. All16 reachable warm
ramp entries must be componentwise nondecreasing for admission.

Classic (owner0) and indexed-copy (owner2) subpixels use the exact current indexed
result's palette color. Each piece reads the already composed background, so
later independent pieces retain the original order. HD ownership is preserved
for those later pieces. The normal expected-index ledger advances for every
write; cloud and green-smoke provenance is invalidated at the written pixels.

## Fallbacks and limits

A whole individual piece is rejected if its declared rectangle crosses any
320×200 edge. The original raw blitter uses linear address bounds and horizontal
row wrapping rather than normal XY clipping. Rejected calls keep that exact raw
loop and its previous display fallback. Other sprite sources and effects retain
the previous callback. Wrong source, altered coverage or dimensions, malformed
bytecode, nonmonotone palette, indexed reference mode, unsupported density or
surface, disabled compatibility and rejected frames cannot enter this path.
Malformed source is rejected only at this HD guard; this change does not harden
the existing legacy raw blitter that remains responsible for indexed fallback.

No new resource lookup occurs. Missing or changed underlay resources continue to
use their existing admission and ownership policies; a non-HD pixel remains
indexed. This batch does not add new projectile art, smooth its original contour,
combine pieces, change hue, or expand level/mode eligibility.

See VALIDATION.md for bounded test results and explicit qualification limits.
