# Protron three semantic shadow masks

Frozen generated-only artwork after the root contour gate, 2026-10-14. This package contains no original game pixels, copied source contour, head artwork, production code, or runtime claim.

## Exact resource contract

| Source ID | Mask role | Slot | HDR1 key | Output |
|---|---:|---:|---:|---|
|225|125|532|1250225|`output/protron-shadow-225-8.hda`|
|244|125|533|1250244|`output/protron-shadow-244-8.hda`|
|226|125|534|1250226|`output/protron-shadow-226-8.hda`|

Each resource retains logical 12×14, density 8, 96×112 RGBA, anchor (0,0). HDR1 is the existing 28-byte little-endian header plus 43,008 RGBA bytes, totaling 43,036 bytes. The alpha channel is the separately authored geometric coverage. RGB is plain vector-mask output and is not a head color input. Original head resources 469–471 are outside this package and unchanged.

## Geometry and strength

- 225: circle centered at (6,7), radius 2; exact bbox [4,5,8,9].
- 244: circle centered at (5.5,6.5), radius 5.5; exact bbox [0,1,11,12]. Its asymmetric placement within the 12×14 canvas is retained.
- 226: independent, smooth four-cubic oblique oval; exact bbox [3,4,8,9], centroid (5.5,6.5). Opposite cubic segments have central symmetry. Polynomial integration independently verifies its centroid.
- Interior alpha is exactly 255. Only raster cells intersecting the vector boundary have fractional alpha. There is no Gaussian, opacity fade, halo, head-alpha normalization, or source-support clipping.
- Geometry preserves original semantic width, height and centroid. It was not globally shrunk to fit the old stair-stepped support. Smooth contour corners may differ within those semantic bounds; the compositor must cover original support UNION display support without changing indexed writes.
- The original shadow origin remains the caller's (x+1, y+shadowYDist). No caller, gameplay, head, or runtime file is modified by this package.

## Reproduction

Run `node rebuild.mjs` in this directory. Dependencies used for the frozen result:

- Node v24.19.0
- Inkscape 1.4 (e7c3feb100, 2024-10-09)
- ImageMagick 7.1.1-43 Q16

The rebuilder runs `source/render.mjs` in a clean temporary directory without game data, checks the approved SVG/PNG/coverage hashes, checks the retained standalone SVGs, decodes PNG RGBA, verifies its alpha byte-for-byte, writes HDR1 resources, and updates the inventory and generated geometry proof. The SVG alpha is rendered at density 8 only; native review sampling uses A8[4y+2,4x+2] for 2× and A8[2y+1,2x+1] for 4×.

`source/render.mjs` and the SVG descriptions retain their original pilot provenance labels. `contract.json` is the authoritative approval/status document. The formal rebuild promotes only the proof status; it cannot alter approved geometry, PNG or coverage bytes.

`inventory.json` pins all generating inputs, outputs, expanded RGBA and coverage. `proof/geometry.json` records continuous and raster areas, bboxes, centroids, exact alpha counts and native samples. `proof/verification.json` records isolated rebuild checks. The private original/semantic review panels and original head references are deliberately absent.

## Integration status

Art frozen; implementation and runtime acceptance are separate. Consume the mask alpha as coverage of the existing full-strength shadow operation, preserving its cloud/indexed/HD behavior and ownership rules. Do not reinterpret this package as permission to change head color or general opacity policy.
