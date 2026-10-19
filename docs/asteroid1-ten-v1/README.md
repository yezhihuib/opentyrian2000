# ASTEROID1 ten-piece asteroid

This is one coherent second-stage artwork family, not second-stage completion.
The ten original linked actors remain separate and keep their original events,
coordinates, ordering, collision, damage and destruction behavior.

## Separate production opt-in

```
./opentyrian2000 --data=/path/to/original/tyrian2000 --no-xmas \
  --asteroid-hd-assets=/path/to/repo/assets/hd/packs/asteroid1-ten-v1
```

Use the ordinary game menus and campaign progression. This option does not select,
skip or automatically play a level. It is independent of `--manual-hd-assets` and
cannot be combined with that flag, render/asset-debug options, network, recording,
constant, death or loot modes. Existing manual HD eligibility remains unchanged.

Only normal-data, local single-player Episode 1 physical level 1 (ASTEROID1,
campaign section 5) can grant the PIC3 scene lease. Physical level 2, title demos,
Christmas, two-player/linked/Galaga, arcade/action, SuperTyrian, timed and bonus
modes stay classic. An optional independently guarded [four-piece event12 rock
extension](../asteroid1-four-v1/README.md) now shares this runtime directory and
flag. Missing extension resources keep that four-piece family classic while the
original ten-piece family remains available. All other scene artwork, terrain,
HUD, ships, weapons, pickups and effects stays classic in this mode.

## Source and artwork

The earliest structure is original events 5–14 at curLoc 10, link 60. Records
444–453 all have ani=1 and animate=0: they are ten static components, not ten
rotation poses. Original enemy bank 8 resolves through `shapeFile[7]='D'` to
`newshd.shp`; it is separate from player `spriteSheet8` and its overlapping IDs.

| Records | Original base | Logical dimensions |
|---|---|---|
| 444, 446, 447, 451 | 31, 15, 34, 88 | 12×14 |
| 445, 448–450, 452–453 | 13, 49, 51, 53, 89, 91 | 24×28 |

One imagegen reconstruction preserves the asymmetric grey cratered rock and is
split at the original actor coordinates. Global inward-only contour coverage
keeps every nonzero authored subpixel inside original logical support. Interior
component boundaries are not separately feathered. The ten HDA files use their
own role 108 and zero anchors. Original indexed blitters always execute.

Current bank bytes, all ten serialized 77-byte original records, actor record,
size, base, static pose and loaded enemy-bank identity are verified before each
draw. A nonblocking regular-file loader preflights all ten pinned 8× resources.
Missing or invalid members keep the entire family classic. There is no 4× asset
fallback. Warm resources are private and immutable; full payload integrity is
rechecked before the first call of each display frame. Mid-frame dependency
failure rejects the full HD frame. Unsupported geometry and physical-row-wrap
calls stay on the original path.

## Bounded validation

- Recovered Linux `make`, `-Werror`, SDL2 software/dummy: passed. Network was
  disabled for this build because the recovered SDK lacks SDL2_net headers.
- Extracted production C harness: optimized and ASAN/UBSAN passed; 28 original
  ordered calls, scope/geometry/source/record/warm-cache checks, plus 31 negative
  resource fixtures per build. All six deliberate mutants were detected.
- LeakSanitizer could not run under the executor's ptrace environment and was
  explicitly disabled; address and undefined-behavior instrumentation passed.
- 15 production CLI cases passed, including help, empty path, mutually exclusive
  flags and modern/legacy constant/death/record/loot rejection.
- Final physical1 actual-engine pairs: 120 ticks at native 640×400 and 90 ticks at
  native 1280×800. All ten components have admitted witnesses (2,585 and 1,802
  ordered commands respectively); no non-asteroid replacements were admitted.
  These are command-role witnesses, not ten independently legible sprites.
  Record446/base15 is a tiny inward-smoothed contour remnant; its original
  support is documented in the validation receipt.
- In each pair, state/RNG/indexed hashes, collision/enemy/player traces and
  captured original INDEX8 frames are byte-exact. Zero coverage mismatch or
  rejected HD frames. Five native 2× and one native 4× samples were inspected.
- A separate 90-tick engine pair with member 31 absent admitted no HD artwork;
  native output was byte-exact with baseline.
- With the new flag off, a separate 90-tick physical9 first-level regression
  matched baseline state, draw/frame traces and native/display/INDEX8 captures
  byte-for-byte using the existing accepted asset pack.
- Ten HDA payloads rebuild byte-exactly. PNG pixels, manifest hashes, original
  support-subset checks and existing manifest content are verified.

These are finite diagnostic runs with an external shared physical1/export-only
probe copy, fixed seed 0x5eed and stationary enemy-hit input. No original level
events or gameplay handlers were modified. They are not natural campaign
progression, a full level clear, Windows/GPU/fullscreen or performance acceptance.
Timing was recorded for bounded runs, not used as a performance benchmark.

Rebuild art with `prototype/build-asteroid1-ten-art.py --data ORIGINAL --out OUT`.
Run source tests with `tests/test_asteroid1_ten_assets.py --data ORIGINAL --out OUT
--sanitize`; supply SDL include directories if pkg-config is unavailable.
