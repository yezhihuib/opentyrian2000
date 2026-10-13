# Finite 25-credit coin family

Six physical bronze coin frames and one fixed cyan 25-credit value replace
only the finite routes described below. The immutable source inventory is
75b4973e91204d3fd35969237ff2e4d7f217d64ca23c7d15670712f14955697b.

## Scope

- Global spriteSheet11, record391, size0, part0, IDs7–12: role112,
  keys1120007–1120012, cache472–477,12x14 at original origin.
- The original fixed newsh6 ID185 call alone gets role113/key1130185/cache478.
  Its one-call lease requires fixed, no follow, deltaY0, sprite184 and ttl<=8;
  it clears before every render early return, at end and at frame begin.
- All seven8x resources must pass preflight and full RGBA stamps. No4x resource
  substitution or partial-family replacement. Unsafe contexts retain classic.
- NORMAL uses authored alpha. BLEND uses the established continuous authored
  hue/value-average analogue, with authored alpha only for coverage. Exact
  original0x90 palette shades are preserved in the indexed fallback only.
- Original indexed draws always execute. Coin movement, six-phase cadence,
  allocation, drop conditions,25-credit reward, linked12+12 split, effect
  admission/eight-draw lifetime, collision and RNG remain original.
- Existing bank8 orb112/113 and their keys80112/80113/cache218/219 are unchanged.

## Verification commands

From this checkout with Python/Pillow/NumPy/SciPy and a C compiler:

    python3 prototype/build-cash25-seven-art.py
    python3 prototype/test-cash25-seven.py --original-data /path/to/tyrian2000 --out /fresh/external/unit-output
    python3 prototype/test-cash25-mutations.py --units /fresh/external/unit-output --out /fresh/external/mutation-output

The units use the exact extracted production loader, binder, one-shot hook and
compositor. They also extract unchanged real RLE blitters and the entity
wrapper for indexed-pixel differential tests. Display hooks in the indexed-only
subtest are isolated; the separate authored-color oracle covers actual RGBA
composition. The single temporary seven-file pack is reused across93 rejected
resource cases, rather than copied into large per-case fixture trees.

Production build, immutable exact rebuild, finite ASan/UBSan tests and
source-preservation checks passed. The bounded actual-engine fixture used
private survival and one artificial original-Pulse155 request at tick 1577.
The original drop was collected by original movement/collision at tick 1655;
cash rose by 25, and the fixed value drew eight times before clear. All three
executions stopped at tick 1664 with matching original state/RNG/indexed and
collision evidence.

The no-image baseline established the schedule. Native 2x evidence contains
15 consecutive 640×400 frames at 1649–1663, showing all six coin phases, eight
popup draws and clear. Native 4x contains one 1280×800 popup still at 1656.
See `PLAN.md` for the route and limits, `runtime-receipt.json` for hashes,
and the exact `technical-review.json` and `author-receipt.json` for the release
gates. This does not claim unqualified natural play, baseline RGB comparison,
other cash families or platform/performance coverage beyond the stated fixture.
The author review passes the observed terrain/actor context; bright-cloud
readability and 4x coin rotation remain untested.
