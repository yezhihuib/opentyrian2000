# Vertically clipped original Plasma pieces

This follow-up extends the original-art compatibility introduced in 17d6d000 to
partially visible top/bottom pieces. It adds no art, resource, sprite dimension,
projectile behavior or new blend operator. Original source pixels remain visibly
pixelated at native 2×; the improvement preserves HD detail beneath the original blend.

## One production condition

Only render_mirror_plasma_projectile_begin changes. The same three exact current
OPTION_SHAPES 22/23/24 source identities, full decoded indices and coverage,
warm 0x70 ramp, palette monotonicity, surface and ownership policies remain.

Horizontal bounds remain x>=0 and x<=320-width. Horizontal row wrapping is still
unsupported. A piece is vertically eligible precisely when its declared rectangle
intersects the logical height: y>-height and y<200. Wholly offscreen calls at
y<=-height or y>=200 retain their old fallback. Full-source identity is checked
even when some of that source is invisible.

The raw blitter itself is unchanged. With a horizontally contained source and
pitch >= 320, a top-clipped source row stays below the buffer and a bottom-clipped
row reaches its upper limit. Its original per-write address bounds determine
which indexed writes actually run. Only those surviving original writes invoke
the unchanged display callback; that callback derives x/y from the valid address
before accessing its ledger or canvas. No new origin-based canvas access exists.
Padded pitches retain the same physical-row behavior.

Each surviving indexed write still runs exactly once, in original order and
with its original source hue plus truncated low-nibble average. Owner 1 keeps
the documented continuous HD-value approximation; owners 0/2 keep the exact
indexed result's palette color. No per-piece draw lease or cleanup is added,
so early bottom-edge return, transparency and later independent pieces retain
their original order.

## Deliberate remaining limits

- Horizontal-wrap, wholly offscreen, incompatible source/palette/context and
  unrelated effects retain existing fallback. This does not remove all fallback.
- The three pieces remain independent original projectiles, with original
  positions, collisions, pool rules, timing and original sprite art.
- Wild-cloud compatibility and turret-region bookkeeping are unchanged.
- The legacy raw blitter's negative-origin pointer construction is inherited.
  This display-only change does not claim to harden that C arithmetic.
- No new HDA/resource lookup exists. Prior resources and their ownership guards
  continue to determine whether a surviving subpixel is HD or indexed.

See [validation](VALIDATION.md) for focused and bounded actual-engine evidence.
The [original blend documentation](../option-plasma-projectile-blend-v1/README.md)
explains the unchanged continuous approximation and source identities.
