# Reproduce the terrain113 candidate

This bounded package contains one authored gray-rock ground tile, terrain113. The selected PNG was accepted offline at native 2x and 4x. Runtime verification and approval are still pending; this package makes no runtime, scrolling, or broad regression claim.

## Integration boundary

Immutable accepted base: `51d4bc4af5ab63c1357e11911c8013e8e028e68b`. Proposed slot: 246. Logical dimensions: 24x28; scale: 8; anchor: (0,0); decoded image: 192x224 straight RGBA. Only terrain113 is supplied. No engine, renderer, gameplay, palette, map, or other accepted asset is changed by this package.

The 172060-byte HDA contains `HDR1`, six little-endian U32 values `[2010113,8,24,28,0,0]`, and 172032 RGBA bytes. `runtime-overlay/terrain113-manifest.json` records the selected PNG, RGBA, and HDA hashes separately. The package is a source/art handoff; integration remains the engineer's responsibility.

## Authored source and provenance

`source/generated-crops/terrain-shapesz-113-8.png` is the newly imagegen-authored central tile with its approved binary alpha already baked in. It is the deterministic rebuild entry point. The prompt and full-master SHA-256 are included. The full 1160x1355 imagegen master remains preserved in the author's workspace and is not bundled because it includes contextual reference cells.

The original upstream process used ImageMagick Lanczos resize to 576x672, followed by the literal central crop `[192,224,384,448]`. Native CopyOpacity applied the approved silhouette. Every source-crop RGB byte is identical to the literal generated crop before edge processing, including hidden RGB. `source/crop-provenance.json` records the operations and checksums. Re-running imagegen is not claimed to be deterministic.

The seven logical transparent pixels remain precisely 448 zero-alpha HD pixels. Every other HD alpha is 255; all four outer borders are opaque. There is no fractional-alpha step. The approved alpha is part of the authored RGBA, not a separately distributed source mask. Native registration preserves alpha exactly and canonicalizes RGB to zero only where output alpha is zero.

## Standalone deterministic rebuild

Requirements: Python 3, Pillow, a C++17 compiler, and Bash for the convenience wrapper. No game checkout, original-game data, map, base asset pack, image-generation service, ImageMagick, or network access is needed to rebuild the selected result.

From this directory, use a new output directory outside the package:

    bash rebuild-selected.sh /absolute/new-output-directory

The native C++ edge solver is unchanged from the selected candidate. It applies a harmonic RGB correction in a 32-HD-pixel inward border band. Only terrain113 is written. The six frozen accepted generated neighbors are IDs 36, 58, 98, 101, 110, and 118. Their perimeter RGB samples and immutable HDA/RGBA provenance hashes are frozen in `source/frozen-edge-constraints.json`; full neighboring rasters are not distributed. The wrapper reconstructs disposable opaque neighbor inputs with exactly those boundaries and zero-color interiors. The solver uses only their perimeters, so no accepted neighbor interior is needed.

The rebuild verifies every input checksum, exact selected decoded RGBA and HDA, unchanged alpha, exact logical occupancy, opaque outer borders, unchanged frozen inputs, and all nine static border-pair residuals. The 40 audited cardinal adjacencies cover the ten known placements. The largest RGB border residual is 12 because the accepted frozen neighbors have intrinsic differences; this is not a claim of a perfectly zero-difference seam.

The same Pillow PNG save wrapper is used as in the selected candidate. PNG file identity is reported separately from mandatory RGBA/HDA identity so an encoder-version difference cannot be mistaken for changed artwork. The packaged verification records the exact encoder/compiler versions and the relocation test. Existing output directories are refused.

## Package boundary

Included image colors are the authored generated crop, its registered output, and numerical boundary constraints from accepted generated art. No original-game PNG, reference image, standalone original mask, palette/index data, original map data, runtime screenshot, executable, or capture/test hook is included. The source master and earlier candidates remain preserved outside this formal package.

`handoff-inventory.json` lists every other package file with size and SHA-256; its own file is explicitly excluded from self-hashing. Verification concerns this immutable art/source snapshot. Runtime approval must be established independently before treating terrain113 as a completed integration.

## Repository layout

Use `python prototype/build-next-terrain-art.py --output <new-external-directory>` from the repository. Formal PNGs are stored once under `assets/hd/source`; the wrapper verifies their hashes and supplies temporary copies in the standalone package layout before rebuilding. This preserves the original committed-PNG hash check without duplicating formal PNGs in Git. No original game data is required.
