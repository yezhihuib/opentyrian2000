# Matte sand, coordinated road and grass backing refresh

This is one bounded material revision, based on the user-approved fresh sand47 pilot. It changes 21 existing terrain assets and has one unchanged guard:
- Road13: 36,37,38,39,40,46,47,48,49,50,56,57,58.
- Grass-backed8: 66,67,76,78,79,80,89,90.
- Full-green69 is reconstructed byte-identically as a guard.

No asset IDs, slots, headers, logical24×28 bounds, anchors, opacity, map, gameplay or renderer are changed. The brown101 rock field, plateau, cloud and accepted island artwork are outside this revision.

## Material and protection

The new master was generated from a clean material description and original warm-earth palette numbers, with no old raster as a visual input. It represents matte compacted fine sand with restrained grains and broad, low-contrast variation. It is registered to192×224, periodized with native GEGL, and uniformly color-registered to the current47 mean. The prompt and generated master are retained.

Road sources are flattened accepted HD artwork, not authored foreground layers. Explicit HD-coordinate curves delimit a conservative sand domain. The selected C++ compositor additionally protects coherent dark stone-outline components and enclosed interiors, with a small collar. Protected-mask pixels remain exactly unchanged. Only a near-boundary scalar diffuse-shading field is retained from accepted road art; new sand supplies the texture. This is not a whole-image blur, and the explicit protection mask is not claimed to be a perfect semantic segmentation of every decorative grain.

Grass masks are derived from the accepted source generation weights, not final RGB coincidence or original-game alpha. All green pixels and18,627 mixed-transition pixels are protected. Of207,954 proven backing pixels,196,877 change after inward-only feathering. ID69 is independent of sand and remains exact. Existing grass shape, palette, opacity and green/mixed colors are unchanged.

## Rebuild

Run `bash rebuild-selected.sh /absolute/path/to/a/new-output-directory`.
Requires Python3 with Pillow/NumPy, ImageMagick, C++17, and system Python GObject/GEGL0.4. No original game data, game execution, network or main checkout access is required. The complete generated inputs, authored masks and source-weight proof inputs are retained here.

The rebuilder rejects existing output paths and symlinks, and paths overlapping this immutable package. It reconstructs22 PNG/HDA outputs and verifies exact decodedRGBA, exact HDA and exact protection weights. PNG encoding hashes describe the committed files; decodedRGBA/HDA are the portable output contract. Only21 changed HDA files belong in the runtime overlay.

The prior road-nine-v2 recipe intentionally requires the historical frozen37/49/50/57. Do not point its historical-base dependency at the newly revised pack and expect old hashes. This package retains exact baseline generated inputs and headers for reproducibility.

## Evidence and limits

The pilot native2×/4× and original-map contacts are offline material previews. Actual background-only replacement mockups preserve captured foreground/shadows and are explicitly labeled OFFLINE. They are not runtime acceptance.

Static coverage includes every363 road occurrence and every26 non69 grass occurrence in this level, all five79 reuses,855 cardinal edges and869 diagonal contacts touching the coordinated family. Original forest neighbors remain outside the material scope. Runtime scrolling, foreground, missing-art fallback and state-parity acceptance are required before publication.
