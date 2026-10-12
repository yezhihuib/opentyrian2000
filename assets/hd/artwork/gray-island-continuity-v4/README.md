# Gray floating-island continuity repair, v4

Frozen art candidate; runtime acceptance is pending. Replaces41 existing assets without changing the renderer, indexed gameplay, anchors, resource IDs or capacity.

- Eighteen Layer3 gray terrain IDs:121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154.
- Twelve purple-foundation exterior stone backings:156,157,158,159,160,166,168,169,170,176,177,178. Terrain150 is an unchanged guard.
- Eight intact purple-object exterior stone backings:newsh2 bases207,245,273,275,277,279,281,283. Entity169 is an unchanged guard.
- Three existing turret bodies/cores153,155,157 reassembled over revised terrain144. The turret artwork, transformations and six-logical-pixel core box are unchanged.

## Rebuild

Run `python3 rebuild.py /an/output/directory/outside/this/package` with Python/Pillow, ImageMagick `convert`, and a C++17 compiler. No original game files, network, game executable or repository checkout are needed. The script checks every decodedRGBA and HDA hash in `expected-output.json`. PNG file encoding is separately inventoried; decodedRGBA/HDA is the portable content contract. It rejects output paths inside the immutable source package or its ancestors.

`source/registered` contains frozen registered authoring inputs. `source/imagegen-originals` retains the selected generated originals and the established turret atlas. Registered-input authoring and pixel-composition stages are explicit in the source; rebuilding does not rerun stochastic image generation. `source/accepted-*` contains only previously generatedHD art, not original game sprite PNGs. Prompts and the short reusable method are included. Rejected art and diagnostic game captures remain outside this package.

## Geometry and interfaces

The new field uses one authored opposite-edge seam repair and shared fill interfaces.132/152/153 preserve distinct center variations;144/154 are natural dark-red recessed pits. Outer-rim composition is derived from a clean structural guide rather than copying square highlights or pixel stairs. Lateral face shading applies only where the tile itself has an exposed transparent margin, never an opaque internal tile boundary.

Tile bounds/anchors stay fixed. Compared with original nearest8× support, the reviewed visible(alpha>=128) contour has a maximum14.765HD-pixel outward and18HD-pixel inward displacement (1.846/2.25 logical pixels). This is deliberately not exact original support.56 detached, non-border pixels with alpha<=6 were removed.134 retains a small legitimate edge-facing fragment already visually present in prior art; no invisible bridge was added to game the connectivity test.

The whole-map audit covers994 gray placements,349 physical cardinal classes and746 unique3×3 contexts. Visual review is selected coverage: the actual tick2700 islands, four-/five-tile upper rims, seven132 repeats, lower-rim repeats, all original gray members and purple interfaces. Offline contacts are not runtime proof.

## Purple backing contract

The C++ mask protects purple/teal chromatic seeds, enclosed plate/crack/lens regions, and a conservative shadow collar. Protection masks are included in `contracts/foreground-masks`. All pixels at mask255, all chromatic seeds, and all original alpha bytes remain exact. New stone is blended only outside that protected footprint; purple geometry, broken shapes, lens and row offsets do not move.

Actor top-row backing phase is0HD pixels, middle−8HD, bottom+8HD, preserving original0/−1/+1 logical placement relative to terrain. This keeps the exposed connector gap and component-local reveal aligned. Terrain150 and entity169 remain byte-identical as HDA guards.

## Required runtime gate

Use the existing private-survival tick2700 baseline with the same state and no new weapon/control injections. Review native2×/4× and the bounded2640–2759 scrolling segment. Recheck earlier2490–2609 routes/state; original turret firing/removal/reveal; all nine independently removable purple components with the established diagnostic controls; unchanged indexed logs, missing-art fallback and exact unrelated assets. Label survival/control footage as diagnostic. Publication belongs to the main engineering owner after this gate.
