# Frozen Data513 twelve-phase authored-vector art

Exactly twelve body resources, accepted at native2× on2026-10-14. This freeze preserves the approved vector pilot's pixels, geometry, color and brightness. It does not establish runtime acceptance or authorize publication.

## Design and construction

One fixed oblique physical cube, with simple planar faces and thin bright structural rails. Beige/silver, gold, red-orange and green groups each have three light states. The semantic corner geometry is authored in `sources/cube-template.svg`; all phase color parameters are in `sources/phase-spec.json`. No original source RGB, palette grid, alpha mask, pixel tracing or staircase shape is a build input. There is no raster master edit or copied generated texture. Earlier imagegen candidates were rejected and are excluded completely from this package.

All twelve alpha fields are byte-identical. No rotation, global shrink, contour inflation, glow, trail, shadow, debris, hidden hold or extra phase is introduced. The cube's logical canvas24×28 and anchor6,7 remain unchanged. The authored image is192×224 at density8.

## Finite contract

Role124 / ASSET_DATA513_BODY. Sorted bases159,161,163,197,199,201,235,237,239,273,275,277 map to slots510–521. Resource keys are1240000+base; filenames are `data513-bank11-BASE-8.png` and `.hda`.

The20 eligible draws remain159,161,163,161,159 /197,199,201,199,197 /235,237,239,237,235 /273,275,277,275,273. Record513 only; the shared record512/base273 use must remain classic. Original fixed266 is unchanged. Preserve ordered quadrant0/1/19/20 calls, original filters, clipping, indexed writes, animation and lifecycle. No reward, RNG, pool, mode or other family change belongs to these assets.

Each HDA is exactly172060 bytes: `HDR1`, six little-endian uint32 values[key,8,24,28,6,7], then172032 RGBA bytes and EOF. Twelve HDA files total2064720 bytes. `contract.json` is the finite integration contract; `inventory.json` pins all inputs and twelve outputs with PNG/RGBA/HDA SHA256, RGBA FNV1a64 and alpha evidence.

## Exact rebuild

Run `node rebuild.cjs /absolute/path/to/a-new-output-directory`. The destination must not exist. The script validates every frozen input hash and output against inventory. It needs Node.js with the `sharp` package and its pinned renderer versions recorded in `sources/provenance.json`. It reads only this package. PNG rasterization is directly from the authored SVG, followed only by transparent-RGB zeroing and encoding. HDR1 payloads are exactly those RGBA samples.

`proof/source-only-rebuild.json` records a relocated source-only byte-exact rebuild of all twelve PNG and twelve HDR1 files. No game data or rejected images are needed. The proof contacts are authored-only offline contacts, not gameplay. Native2× selects density8 source samples2,6,10…; native4× selects1,3,5…. Both use floor((target+0.5)*8/scale), with no smoothed preview substitute.

## Geometry disclosure

The source's written353 cells are comparison metadata only. Authored weighted area346.51918 (−1.83593%); alpha128 area346.53125. Centroid offset is(+0.01919,−0.01878) logical pixels. All measured alpha thresholds preserve extent[2,3,22,25). Smooth vector perimeter is deliberately not clipped to the old pixel staircase. Detailed numeric support deltas are in `proof/geometry-and-sampling.json`; it contains no source mask or RGB grid.

Only this explicit package may enter a future public art import. Private source comparisons, terrain, source-data readers and rejected imagegen masters are excluded. This package contains no complete pack, gameplay code or runtime fixture. Publication remains held pending the separate integration/review process.
