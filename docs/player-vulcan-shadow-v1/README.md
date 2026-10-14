# Vulcan: finite smooth player shadows

Local source, numerical and author checks pass. Publication is a separate action.
This follows the two authored heads; it adds no assets and leaves their pixels,
positions and animation unchanged. Only normal player bank8/TILE IDs67 and70
use their frozen alpha at the original shadow origin, ten logical rows below
the head, when the original shadow condition is true. Protron and other families
retain their prior behavior.

The complete smooth contour includes78/110 density8 samples beyond the old RLE
support, bounded inside the original12x14 rectangle. This extension is display-only.
Every original indexed write still occurs once in its original order. Actual
shadow-blitter entry checks surface/bank/ID/origin before composing; one-call
state clears on exit. Palette-ramp darkening, existing cloud transfer and ordinary
HD darkening are retained with alpha coverage. Later draws overwrite normally.
See [source contract](../PLAYER_VULCAN_SHADOWS.md) for rounding, ownership, immutable
loaded-cache epochs and safe fallback details. There is no global shadow pass.

## Evidence

- Three production files changed: renderer, declarations/stubs, and tiny original
  darken-blitter entry/end calls. Exact source inverses preserve indexed operations.
- Both-pack ASan/UBSan units pass4,574 transactions,16 ordered actual-support overlap
  cases,186 lifecycle cases and12 extracted reset/finish/fade/Present checks per pack.
  Each pack compares69,677,568 subpixels and524,288 alpha checks. Original all11-power
  gameplay units also pass. These are source tests, not extra game runs.
- Exactly two new90-tick P1/P7 candidates reuse verified original six-frame baselines
  at ticks38–43. There are12 new640x400 native images and12 new320x200 INDEX8 images;
  all48 old/new image files are independently hash/dimension checked.
- Original state, RNG, requests/emissions, indexed surfaces/palettes and draw order
  match. Every native RGBA pixel outside actual admitted shadow rectangles is exact.
  Surviving opaque head cores match. No full fractional-alpha runtime oracle is
  claimed; that operator/overlap coverage is supplied by source units.
- P1 admits460 of465 shadows; P7 admits309 of312. The5/3 negative-x calls retain
  classic behavior to preserve legacy physical-row wrapping. All497/334 head draws
  remain unchanged. P1 has39 emissions; P7 has26 emissions and its original power
  failure at tick16. Empty collision traces do not establish collision coverage.
- The author directly inspected all12 new and12 retained native frames. Single/twin
  shadows taper cleanly at the original offset, replacing block-shaped ends; heads
  remain warm and clear over clouds and brown terrain. No residue, halo or popping
  was observed within these six-frame windows.

Starting P1/P7 loadouts are diagnostic configuration. The reused original demo-key
adapter drives movement/fire; original spawn protection counts down, with no added
protection, projectile helper or power refill. No natural upgrade acquisition,
unprotected survival, live shared-option/rear-charge mode, Christmas game, native4x,
full gameplay overlap, Windows/GPU/fullscreen or performance acceptance is claimed.
The retained windows have no actual different-projectile support overlap; ordered
overlap is covered by focused units. Missing/invalid/non-frozen/density4 resources
and unsupported geometry keep classic shadows. Source checks cover these fallbacks.

[Numeric summary](runtime-summary.json) and [author summary](author-review-summary.json)
contain portable pins. Historical head-only runtime/author JSON remains unchanged.
Original game data, reference pixel grids and private fixture logs are not included.
