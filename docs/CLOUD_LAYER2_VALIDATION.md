# Finite layer2 HD clouds and palette-floor shadows

Selected family: shapesZ layer2 IDs41–45,51–55,61–65. Fifteen192×224 RGBA assets replace original24×28 cells at8× density and anchor0,0. Existing current preview/debug packs gain15 entries each; every prior resource, including accepted green and orange bullets, is preserved. No new duplicate stage-pack pair is added. Earlier Git commits provide rollback.

Generated source, prompt, selected inventory and the deterministic extraction/reconciliation pipeline are under `assets/hd/artwork/cloud-layer2-v1/`. Original RGB tiles/game data/maps/captures are excluded. Rebuilding uses an external legal `shapesz.dat` for only the15 original opacity contours. Run `python prototype/build-cloud-art.py --output ../cloud-art-check --data <legal-data>` with ImageMagick7, GEGL0.4 Python bindings, Pillow and C++17. All15 decodedRGBA images and HDR bytes reproduce exactly; PNG date metadata varies and is not represented as byte-identical regenerated encoding. Committed PNG file hashes and every pack byte are still strictly verified by `prototype/build-hd-assets.py`.

## Renderer scope

- Only the15 new layer2 IDs bind. Highest-detail/wild palette-blended clouds deliberately retain their original path. The binder skips HD loading/drawing before generic blend restoration can affect the canvas.
- Existing original indexed green shadows legitimately overlap up to7 times in the fixture. Generic HD RGB halving made a cloud sample189,222,228 become2,2,2, whereas the original0x80 ramp bottoms at36,85,109. No duplicate shadow draws were found.
- Only cloud-provenance HD subpixels with a verified original same-hue nibble-halving transition use per-channel `round(currentHD * paletteAfter / paletteBefore)`. Equal indexed before/after is an exact no-op; a zero denominator preserves that channel. The example now ends29,74,97, retaining cloud texture and the nonblack relative floor.
- Unrelated drawing, brightness or restoration invalidates cloud provenance. No global shadow, blur, palette, green head-layer, physics, collision, RNG or original indexed draw change is made. The original indexed shadow contour remains pixel-shaped. A transparent intervening terrain pixel can update the indexed hue while leaving visible cloud; the correction then follows that current indexed ramp. This conservative behavior is covered by focused tests.

## Finite acceptance

Actual scene is episode1 physical-level9. Family coverage spans the first522 ticks, approximately15 configured seconds, including all15 IDs and22302 mapped cloud references. The final corrected continuous comparison contains120 consecutive real2× frames, ticks90–209, checked against uncaptured runs and encoded lossless-frame hashes; labels sit outside the game image. The full UI remains exact. Native4×/2× samples show coherent soft clouds, continuous covered boundaries, readable green cores and textured blue shadows.

Source/gameplay/collision/indexed/RNG logs remain exact; no-cloud fallback is byte/pixel-exact. Highest-detail/wild output stays original and was checked byte-for-byte. Missing54 falls back only54. New cloud arithmetic/provenance/floor/zero-denominator tests and the original1,935,360 green head-layer comparisons pass at densities2/4/8 under ASan/UBSan. The346,480 background interpolation checks and12 strict fixture-preparation tests also pass. Archived fixture preparation strips only the exact reviewed one-line layer2 registration and still requires the original historical hash; current preparation restores the current production binding.

The15-second map sample has77 observed cloud adjacency relations, all included in97 compatible reconciled pairs. Three incompatible full-map pairs are intentionally not forced equal:43 below62,45 below54, and45 right54. Those out-of-sample relations remain a known continuity limit. Ground terrain is unchanged. No arbitrary/full-level adjacency, native Windows, GPU/fullscreen, physical2K or full-level FPS acceptance is claimed.

## Cloud55 edge revision2

The first unpublished cloud candidate retained an overly straight repeated notch from the old cloud55 mask, made conspicuous by brighter HD shading. At original tick144 the same tile repeats at map rows585–588,column5. The selected imagegen-authored free perimeter replaces that local contour, retaining the cloud interior and exact four tile-edge RGBA samples. Only55 PNG/HDR pixels change;14 other tiles and all renderer/gameplay code stay byte-identical. All97 compatible edge constraints remain matched. The source regenerator now reconstructs the base and then applies the saved edge revision. Native tick144 and120-frame scroll were reviewed; the original three out-of-sample full-map adjacency limitations above still apply.
