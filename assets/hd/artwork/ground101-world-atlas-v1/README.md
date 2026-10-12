# Brown ground world atlas, v1

Root accepted the independent continuous v4 material and localized wrap-v2 at native 2×. This source package freezes one 768×896 opaque RGBA atlas, a 96×112 logical (four-by-four tile) world period. Its recognizable large-period motif remains. A short horizontal-wrap shelf around logical x64–72 is a specific 4× runtime inspection target. Actual renderer integration is pending.

The prior regular 24×28 v2 material was rejected by the user. None of its baked outputs is an input here. `contracts/material-bindings.json` lists 61 immutable published-generated source bases and masks plus the unchanged111 guard. It includes file/decoded hashes, original headers, and both119/120 generated footer inputs and extra masks. `contracts/world-sampling.json` is the precise phase/composition contract. Source palette, actual geometry, original alpha, sand, and masked physical objects are protected. Actor sampling uses the same actual Layer1 world transform, without the historical extra8HD offset.

Raster art was authored using the built-in imagegen: one independent material master followed by two localized seam repairs. Registration uses ImageMagick and a C++ weighted composite, preserving540548 interior pixels exactly. All prompts and generated masters are retained. No original game PNGs or runtime screenshots are included.

Run `python3 rebuild.py NEW_EXTERNAL_OUTPUT_DIRECTORY`. The output must not exist and must be outside this package/main checkout. It rebuilds and verifies the selected atlas, both generated footer crops and every base/mask contract. It does not bake16 variants or modify any game resource. Exact decoded pixels are the reproducibility contract; PNG container metadata may differ.

Footer composition must preserve three ordered integer blends: published base→world atlas via material mask; result→generated foot via its generated mask; result→the same world atlas sample via ground mask. Reordering/collapsing these or compositing over rejected baked v2 is invalid. Original source alpha is always retained.

This is an isolated generated-art/source handoff. Production remains at the accepted sand21 checkpoint856a365 until a separately validated finite renderer prototype and runtime review are complete.
