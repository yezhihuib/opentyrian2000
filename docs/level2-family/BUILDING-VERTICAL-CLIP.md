# Building vertical clipping: coverage checkpoint, not a flicker fix

The reported frozen Windows preview used asset-debug, not ordinary play. Its
23 base controls do not enable all installed public assets; many extensions
explicitly reject asset-debug. Its family output also leaves the HUD classic.
The frozen launcher and immutable Windows runtime are unchanged by this work.

## Reproduced cause

The current 88dbfb9 source, rebuilt in Linux with original Tyrian 2000 data and
the same base preview controls, reproduced the reported tick303 scene. Baseline
600-tick output had 218 HD presentations and 382 classic frames, matching the
previous frozen-source count. The first 245 logic ticks are hidden fast-forward;
the visible interval is ticks245–599, with 218 HD /137 classic presentations.

At tick303, eight building quadrants had already been admitted. Additional
quadrants in slots27/28 were wholly or partly above the screen, so the old
full-visibility planner rejected them (B313FO_PLAN). Failed consumption then
rejected the entire canvas (FC_SOURCE), including otherwise valid HD terrain.
All 20 normal animation cycles have phase mappings; this was not missing art.

## Narrow change

The building planner now derives the exact visible vertical rows of each pinned,
opaque 12×14 tile. The native-store guard checks that exact row-major callback
sequence and final count, including zero callbacks for a completely hidden tile.
The native blitter, original INDEX8 data, actor state, collision, events and RNG
are unchanged. Horizontal row wrapping remains rejected. Signed bounds precede
arithmetic. Identity, source, allocation, lifetime, event, palette, surface and
post-lock validation remain in force.

This is new, checked clipping support. It is not permission to reuse a stale
building lease or suppress a failed lifecycle check.

## Bounded validation

- All 112 staged translation units rebuilt successfully with the pinned local
  SDL2 2.32.4 / SDL_net 2.2.0 dependencies.
- One counted native contract test passes 73,280 combinations under UBSan:
  four components ×20 cycles ×four quadrants ×229 vertical positions. It uses
  the actual original blitter body and the actual production callback guard,
  checks source-byte order and untouched pixels, and rejects malformed sequences,
  horizontal wrapping, invalid phases/states and extreme signed coordinates.
- Six continuity-accounting tests, eight family release tests and two manifest
  path tests pass. This is focused validation, not the full repository suite.
- The corrected actual-Present observer ran 600 original-data ticks at native2×.
  Its 355 visible presentations contain **276 HD /79 classic frames**. Tick303
  now displays the HD terrain/building. Twelve actual output captures cover
  ticks298–309.
- Six complete native streams are byte-identical to baseline: state (including
  original INDEX8 output and RNG fingerprints), collisions, player projectiles,
  shot emissions, shot results and enemy-hit records. Original input hashes
  remain unchanged.
- An earlier observer attempt also completed all 600 ticks and obtained the same
 276/79 result, but its checker incorrectly counted the initial black startup
  Present as gameplay. That attempt remains recorded as failed. The observer now
  excludes only frames before the family frame counter starts, and the corrected
  rerun passes. No missing gameplay frame was silently removed.

## Important remaining limitation

**This checkpoint increases coverage but does not solve overall flicker.**
Visible HD/classic transitions increase from **78 to86**, because newly admitted
entry frames expose event gaps previously hidden inside a long classic interval.
Do not ship this as the completed flicker fix or ask for acceptance on that basis.

The retained baseline trace identifies at least26 event-invalidated building
frames and29 group-lifetime frames among the remaining classic intervals, plus
six unsupported blend frames. A four-member building group becomes invalid when
one member leaves or changes state; its surviving members then reject the whole
scene. Other nonfault fallback occurs when the terrain token is unavailable.
Those need independently proven local rollback/terrain continuity, not removal
of identity or event guards. Static HUD work is a separate adapter.

No Windows PE, physical window, GPU, full-level, input/menu/save lifecycle,
performance, damaged-building or final UI acceptance is claimed here. All
original data and screenshots remain outside the repository.

## Reproduce privately

Build the family binary with the desired source/toolchain, then run:

```sh
python3 -m unittest discover -s tests -p test_b313_vertical_clip.py -v
python3 -m unittest discover -s tests -p test_level2_preview_continuity.py -v
python3 tests/check_level2_preview_continuity.py \
  --data /absolute/original-data \
  --out /absolute/new-private-output \
  --baseline /absolute/previous-private-output
```

The checker defaults to the current verified build. `--build-receipt` explicitly
selects an existing immutable staged build for before/after work; it rehashes all
staged sources, headers and objects and labels that historical snapshot in its
receipt. It does not re-label an older binary as current. The output directory
must be fresh, outside the repository and separate from original data. Only a
read-only Present wrapper is linked; normal game builds never include it.
