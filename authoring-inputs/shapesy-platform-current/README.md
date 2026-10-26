# ShapesY platform: current bitmap authoring candidate

Private candidate artwork route, not evidence of runtime acceptance. One generated
V2 component board supplies every output; no independent finished-tile painting.
`generation-provenance.txt` records both generations; only V2 is used here.

## Reproduction contract

`prototype/build-shapesy-platform-art.py` exposes `generate(root)` returning the
exact 28 ID -> PIL RGBA map and `input_paths(root)` returning exact immutable
package inputs through a finite fixed filename list (excluding diagnostic, non-authoritative SHA inventory). CLI `--out DIR`
exports deterministic 192x224 PNGs. Anchor0,0, logical24x28, density8 only.
No runtime transport, catalog, or formal asset installation is performed here.

`recipe.json` records all component crops/resampling, per-ID plane/UV phase,
semantic-mask hashes, diagnostic original-red-footprint hashes, source-index hashes, and explicit
visual plane annotations. The semantic annotation is a candidate authored
interpretation of the originals, not a claim an original semantic map existed.
Generated top/front/side/rim/recess share a restrained top-left light hierarchy.
Component-only periodic edge registration uses symmetric RGB correction within
2 HD pixels for deck/recess,12 for other component repeats; it never modifies protected water or solves map-edge equality.

## Immutable original geometry constraints

Masks contain semantic labels only, not original palette RGB or original indices.
Original water48..63 is exactly label0; every corresponding8x8 output block is
RGBA0. Runtime must supply CURRENT native water RGB and classic owner, including
shadow-water48..50,322same-phase water and375's single cell. Alpha transparency
alone is not sufficient. Other output blocks are opaque.333's native index0 at
logical9,9 is label8, pinned RGB0 alpha255; its skipped original callback requires
runtime's Layer1 clear/pass proof. None of these rules change original IDX8.

The original dark water-adjacent boundary (index<=1 with a cardinal water neighbor)
is label7. It samples generated side material attenuated0.10. Interior dark
original texels are NOT stencilled over the new walls: that would retain a
pixel-mosaic rather than generated coherent surfaces. The original red footprint in336 is retained as identity/location provenance,
not an output stencil. Following root visual feedback,336 samples one coherent
generated recess crop with centered red conduits; no other tile selects that
component. This removes original low-resolution blockiness without creating
new painted pixels.

Explicit lighting attenuation: front0.72,left0.65,right0.30,rim0.85,recess0.72;
these are deterministic component assembly, not newly painted pixels. The deck
remains unchanged. Full source water and all excluded tiles remain native.

## Review boundary

Exact28:321322323324325326331332333334336341342343346351352353354361362363364365374375384385.
Excludes25,356,coast1–28,Layer2/3 and every Z family. All117 internal pairtypes
need material/UV visual review;21 external candidate-facing boundaries are native
water and preserve original baseline, NOT zero seam difference between native
neighbors. Static fullmap410placements differs from actual runtime coverage.
Private native-water atlas/map/pair previews and hash proof live outside checkout
in `../shapesy-platform-candidate-v1/` and are not authoring inputs.

## V2 visual correction

Measured master repeat:162 horizontal,200 vertical source pixels. The first
crop incorrectly included the master sample outer top-border highlight. Corrected
interior crop409,246–571,446 contains one whole period and centers the T motif.
All top-plane samples use that same phase; only2 HD pixels receive symmetric
terminal registration.336 now uses coherent generated recess crop818,1225–942,1415
instead of source pixel-block red masking. No water/black geometry changed.
