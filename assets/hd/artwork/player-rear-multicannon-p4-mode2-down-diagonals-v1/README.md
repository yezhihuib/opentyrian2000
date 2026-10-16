# Rear Multi-Cannon P4 mode2 downward diagonals

This package adds only reviewed density8 heads182/183 for actual main-gameplay
player1, rear weapon10, power4, mode2, exact record268, on first-level
Normal9/Hard15. The runtime call owns five emissions. Source IDs alone do not
authorize this dedicated binding. Runtime ownership, fallback and state parity
require separate qualification.

Head182 is a whole-canvas vertical flip of the accepted front Multi-Cannon
head163; head183 is the same transform of accepted164. Both retain the exact
12×14 logical canvas, anchor(0,0), straight RGBA samples, alpha distribution,
shading and full-density brightness. There is no new drawing, generation,
normalization, blur, filtering, resampling, translation or compositing. No
original game pixels, masks, palettes, extracted sprites or captures are used
or included. Native nearest sampling can change subpixel phase; no brightness
compensation is applied.

The only image inputs are the published PNG files
`../player-front-multi-eight-v1/output/bullet-163-8.png` and
`../player-front-multi-eight-v1/output/bullet-164-8.png`. Their exact repository
paths, encoded PNG hashes and decoded RGBA hashes are pinned in `inputs.json`.
No input copies or original masks are bundled. `provenance.json` records the
published baseline and the independently reviewed generated-only export.
Only its182/183 outputs are selected;77 remains byte-exact in its older package.

There are no density4 variants of182/183. A startup-selected density4 request
retains indexed182/183, without upward fallback. The existing77 density4/8
resources are reused unchanged. Generic163/164 keep their existing resources,
normal/shadow paths and density selection. No new163/164 resource is created.
The old down77 binding describes its historical mode1 introduction; current
record268 reuse is described by this package's catalog descriptor.

With Python3 and Pillow installed, rebuild into fresh separate destinations:

    python3 build.py --output NEW_ART_DIRECTORY --hda-output NEW_HDA_DIRECTORY

The default source is the sibling accepted front package's output directory.
`--source` may point to a relocated directory containing only those two pinned
PNG files. The builder rejects modified input, existing output destinations,
or PNG/HDR1 bytes that differ from the reviewed pins. RGBA PNG encoding uses
compress_level9 and optimizeFalse. The exact-byte check fails with incompatible
encoder output instead of silently changing approved art.

HDR1 uses role131, keys1310182/1310183, density8, logical12×14 and anchor(0,0),
followed by the exact reviewed RGBA payload. Existing filename conventions are
retained as `rear-multicannon-p1-bank8-{182,183}-8.hda`. `binding.json` pins the
builder, contract, payload and both default-pack copies. `file-manifest.json`
covers every file in this generated-only package except itself.
