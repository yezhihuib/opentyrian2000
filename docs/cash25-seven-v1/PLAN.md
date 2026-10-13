# 25-credit coin implementation and verification scope

## Frozen resources

The seven generated-only sources are retained unchanged under
`assets/hd/artwork/cash25-seven-v1`. Their inventory SHA256 is
`75b4973e91204d3fd35969237ff2e4d7f217d64ca23c7d15670712f14955697b`.
`contract.json` records resource keys, geometry, cache slots and production hashes.
`prototype/build-cash25-seven-art.py` verifies provenance and a byte-exact rebuild.

Six physical coin frames use global spriteSheet11 IDs 7–12, role 112,
keys 1120007–1120012 and cache slots 472–477. The fixed value uses newsh6 ID 185,
role 113, key 1130185 and slot 478. Each HDR1 file is 43,036 bytes: six header
fields `(key,8,12,14,0,0)` followed by 96×112 straight RGBA. Both existing default
pack identities remain unchanged; each gains these seven resources only.

## Production boundary

- The body branch requires global bank11 pointer identity, record 391, size 0,
  part 0 and base 7–12. It uses original coordinates and filter. Safe indexed
  layout is 320×200, pitch 320, 8-bit/one-byte, x 0–308 and y −13–199.
- Original fixed-value calls pass a one-draw eligibility lease: fixed position,
  no player following, zero deltaY, sprite 184 and ttl ≤8. The renderer consumes
  and clears it before every early return, and clears again at frame begin/end.
  Only explosion-sheet ID 185, TILE, NORMAL/BLEND can use the value resource.
  Generic moving ID 185 remains on the previous path.
- The entire seven-member family must pass density-8 preflight and frozen RGBA
  stamps. Missing, malformed or corrupt resources retain classic output for
  the whole family. There is no density-4 artwork substitution.
- NORMAL uses authored-alpha source-over. BLEND uses the existing continuous
  authored hue/value-average analogue, retaining source channel ratios and
  applying authored alpha as coverage. Exact original 0x90 palette shades are
  an indexed-fallback property, not a claim about redesigned colors.
- Original indexed blits always execute. Allocation, movement, draw gates,
  six-phase cadence, cash, linked-player split, collision, effect lifetime and
  RNG are unchanged. Existing bank8 orb IDs 112/113, keys 80112/80113 and slots
  218/219 remain independent.

## Finite verification

`unit-result.json`, `mutation-result.json` and `art-rebuild.json` record the
extracted-production tests. ASan/UBSan covered both selected packs, context and
surface guards, coherent-family rejection, transparent/fractional alpha,
NORMAL/BLEND, filters, clips and ordered overlaps. The real unchanged indexed
blitters and entity wrapper were tested separately against decoded original
RLE pixels; display hooks are isolated in that subtest. Original gameplay edge
cases are verified by separate extracted units, rather than extra game scenes.

## Bounded actual-engine evidence

Three executions used Episode 1, physical level 9, normal difficulty, seed
0x5eed and the same stationary no-fire input. The scenario included private
survival and one artificial request through the original Pulse155 helper at
1577. No enemy fields were overridden. Original first-hit order selected
carrier slot 26; the original death branch allocated pickup 391 in slot 29
before freeing the carrier. Carrier reward was 15 credits.

Original movement and collision collected the pickup at tick 1655, screen
(98,148), with the player at (100,160). Cash changed 15→40. The original fixed
popup occupied slot 0 and drew in BLEND mode eight times, ticks 1655–1662.
Two clear ticks followed; all runs stopped at 1664 inclusive (1,665 logic ticks),
below the 1,690-tick ceiling.

The no-image baseline froze collection and the input/capture schedule. Native
2x retained exactly 15 consecutive 640×400 frames at 1649–1663; the precollection
body sequence 12,7,8,9,10,11,12 covers all six phases. Native 4x retained only a
1280×800 still at 1656. State, RNG, collision and original indexed surfaces
matched across the three executions. Compact source/runtime receipts identify
external evidence by hash; raw logs, original data and captures are not vendored.

## Limits

The fixture demonstrates the guarded original drop, original-motion collection
and fixed popup under the stated artificial-shot/private-survival conditions.
It does not establish unqualified natural play, baseline RGB before/after
comparison, other cash families, Windows/GPU/manual-input behavior, or FPS and
original-speed performance. The baseline intentionally contains no images.

Author inspection passed the observed six-phase 2x rotation and fixed-popup
readability/clear at 2x and 4x. Bright-cloud readability remains untested; 4x
covers the fixed popup only, not coin rotation. See `author-receipt.json`.
