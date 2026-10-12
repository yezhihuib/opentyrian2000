# Coordinated gray-island continuity correction

This addresses the already-HD floating islands reported around tick2700:
stepped upper highlights, black lower-rim pads, internal tile joins and bright
block-like crater rims. The prior HD assets were correctly bound; this is an art
correction, not an old-sprite fallback or a renderer bug.

## Exact scope

41 existing resources change:18 gray Layer3 terrain tiles,12 purple terrain
stone backings,8 purple object stone backings and3 turret sprites reassembled
over terrain144. Terrain150 and entity169 are unchanged guards. All292 other
default-debug resources, including the new Pulse heads, remain exact.
No production source, slots, logical bounds, anchors, physics or timing change.

The gray art now shares continuous stone interfaces and natural recessed pits.
Its visible contour deliberately departs slightly from the original pixel steps
(maximum reviewed alpha128 displacement1.846px outward/2.25px inward), within
existing tile canvases. Every purple alpha byte and protected purple/teal/plate
pixel remains exact. Turret source/body/core transforms are unchanged; only its
144 backing changes. Object row offsets0/−1/+1 and independent removal remain.

## Runtime evidence

Private-survival replay uses current b1c7d77 production functions, without
weapon/loadout injection. Both baseline and candidate use the same survival
floor. This is a bounded diagnostic, not ordinary no-assistance gameplay.

- Eight normal/missing cases at2×/4×,270 rendered frames each, ticks2490–2759:
 state/RNG, collisions, original materials, enemy/player emissions and draw
 commands match byte-for-byte. Missing-pack RGB matches exactly. Zero coverage
 errors or rejected operations.
- Two processor4 wild cases add540 rendered frames with exact original logs
 and zero coverage errors; existing cloud blend fallback remains unchanged.
- Native2× scrolling2640–2759:all120 frames independently reviewed; native4×
2700 also inspected. Former steps/bands are corrected without contour popping,
background leaks, foreground regressions or new interface jumps. Repeated
stone pattern remains visible; this is not a claim of nonrepeating texture.
- Prior captured2640–2759 RGB audit exactly equals the current baseline, grounding
 the before/after video without a redundant baseline capture. All120 pixel
 differences stay inside the41 changed resource rectangles; HUD stays exact.
- Original turret hit/removal,68 frames2560–2627, and nine independent purple
 component hit/removal controls,120 frames2540–2659:original state/collision/
 effect/material/emission logs match. Controls are explicitly synthetic uses of
 the existing hit functions. They do not imply a natural encounter.

All lossless capture frames are checked against direct SDL readback hashes;
no raw/BMP batch is retained. Main production source contains no capture or
survival hook. Earlier/full-map modular contacts supplement these windows;
not every map placement or Windows path has been visually tested.

## Reproduction and provenance

Frozen source inventory revision3: dffca3e0dc90c7b8945b4a4425e077acf9ee39540d5da6ddba6550bdd2f914d7.
Standalone and independent rebuilds reproduce all43 PNG/RGBA/HDA outputs.
Generated masters, registered authored inputs and prior generated-HD dependencies
are included; original game RGB and test captures are excluded.

`python prototype/build-island-continuity-art.py --output /new/external/path`
recreates the artwork. `python prototype/build-hd-assets.py` verifies the full
18-pack manifest:2898 HDA entries,341 active canonical PNGs, defaults329/333.
Historical sources and rollback commits remain available.
