# Plateau cap continuous material, v1

This is an additive, generated-art-only source package. The selected warm cap material was approved in offline native 2× repeated-field and existing-frame compositions. Actual cap/cliff joins, scrolling registration, and finite fallback behavior remain integration gates.

## Selected scope

- One opaque 768 × 896 RGBA atlas, density 8, covering a 96 × 112 logical period. It repeats every four source tiles in each axis; it is not a claim of zero repetition.
- Eleven finite Layer 1 / NORMAL cap masks: 96, 97, 99, 100, 106, 107, 108, 109, 110, 119, 120.
- Two zero-mask guard records, 98 and 118, retain their entire current image.
- All thirteen source bases and their HDA headers/hashes are frozen references. No replacement HDA is emitted.
- Reuse the already accepted Layer 1 world-coordinate transform. Only 109 needs an additional cap base record; the other ten enabled bases already exist in the lower-ground bundle.

The cap is geometrically restricted to top-facing areas. Every positive existing lower-ground or footer weight excludes cap support. Tiles 119 and 120 additionally protect the entire lower 40 HD rows. Current lower atlas, ordered footer inputs/weights, sand, alpha, logical bounds, anchors, and indexed gameplay remain unchanged. The integration must not invert the lower masks, blend over the rejected baked 101 version, or add a second actor offset.

## Source provenance and processing

The initial independent imagegen master established broad irregular warm facets. A second imagegen edit reduced peppery detail while retaining large-plane contrast. A third imagegen edit repaired the central cross of a half-offset field. The exact prompts and generated results are retained in `source/`.

Rebuilding registers the cleaned master to 768 × 896, applies the recorded uniform RGB calibration, offsets it by half a period, and applies the generated wrap repair only inside a smooth central cross. The C++ compositor reverses the offset. Pixels outside the wrap-edit support remain exact to the cleaned field. This is a localized generated seam repair, not whole-image blur.

Semantic cap domains are stored as explicit geometric polygons with inward distance feathers. Revision3 narrows only108 and110 at definite projecting rim bodies. The thin108 connector uses a width-limited horizontal inward feather that keeps x190–191 fully connected;110 uses a6HD inner feather capped by the prior16HD weight. No weights are expanded. They are neither complements of the lower-ground masks nor traced copies of original indexed pixel stairs. Generated historical base PNGs are verification/reference assets, not new paint inputs for the atlas.

## Rebuild

Requirements: Python 3, Pillow, NumPy, SciPy, ImageMagick `convert`, and a C++17 compiler.

Run `python3 rebuild.py --out /absolute/path/to/a-new-external-directory`.

The output must not exist or use symlink components, and must be outside this package and other repository checkouts. A fresh directory receives the atlas, thirteen masks, intermediate registration evidence, and a receipt. Existing output is rejected; it is not overwritten. The package itself is read-only during rebuild.

`inventory.json` freezes all package files except itself. The rebuilder verifies that inventory before writing output, then checks exact decoded RGBA/L pixels for every selected result, all source-base HDA hashes, and zero lower/footer overlap. Source PNG file hashes are verified separately. Regenerated PNG file-byte identity is not promised because encoder metadata may vary.

## Integration contract and qualification

Read `contracts/cap-bindings.json`, `composition.json`, and `registration.json`. Composition uses `(old * (255 - weight) + atlas * weight + 127) / 255` with integer floor per RGB channel and unchanged alpha. The cap and all lower/footer weights are disjoint, so lower-ground pixels must remain byte-exact.

The offline frame composition used a limited unobscured right-cap region from existing tick 1104 and a provisional presentation phase. It was a material review, not an engine capture or proof of final world phase. Test actual native 2×/4× compact, narrow and diagonal plateau joins, repeated 109, the 4×4 atlas wrap, and missing/invalid sidecar fallback before publication. Do not infer a visual pass solely from bind counters.
