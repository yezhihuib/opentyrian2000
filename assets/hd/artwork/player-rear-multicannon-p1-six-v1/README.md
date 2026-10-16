# Rear Multi-Cannon 10 P1: six-head art pilot

Status: **R2 approved for actual runtime evaluation; publication not approved**. These generated-only assets do not imply gameplay or publication acceptance.

Six static normal-player bank8 identities: 1, 39, 281, 282, 300, 301. Each keeps a full logical 12×14 canvas with anchor 0,0. Density4 files are 48×56; density8 files are 96×112. The package includes 6 standalone semantic SVGs and 12 PNG/straight-RGBA pairs. No HDA role IDs, keys, or resource slots are assigned by the art package.

## Drawing and provenance

Three new authored cubic-Bezier silhouettes use the accepted front-Multi eight-head art's continuous elliptical yellow/orange/red heat-field vocabulary. There is no gray casing, dark outline, blur, halo, nested highlighted contour, pixel-mask tracing, bitmap input, or added animation. The two lateral heads are independently authored: their tail height, cap proportion, and curvature differ. Four diagonal heads share a single canonical shape and exact full-canvas horizontal/vertical transforms.

Support bounds are exclusive: 1=[1,4,12,8], 39=[0,4,11,8], 281=[0,0,11,6], 282=[1,0,12,6], 300=[0,8,11,14], 301=[1,8,12,14]. All empty margins remain transparent. Every RGB channel under zero alpha is zero. R2 preserves every nonzero R1 sample and every straight-RGB byte; only inward edge coverage is reduced. Bounds encode placement, not a raster silhouette or pixel-index array.

## R2 bounded inward softness

R1 remains the geometric and color control. R2 adds a narrow **0.30-logical-pixel inward coverage falloff** (0.6 display pixels at native2×; 1.2 display pixels at native4×), from approximately 0.62 at the vector boundary to 1 in the interior. A luminance mask composed of 32 nested strokes of the same authored cubic path encodes the smoothstep ramp. These strokes alter opacity only; they are not visible dark outlines or pixel-mask traces. The colored path retains exactly the same silhouette and does not gain any exterior support. No blur filter is used.

To preserve correct straight-alpha color, the renderer separately rasterizes the same SVG with the coverage mask removed, retains its RGB bytes exactly, and substitutes only the masked alpha. Where a formerly nonzero edge sample would round to zero, alpha1 preserves the original support. Canonical diagonal coverage and RGB are then transformed together, exactly as in R1. The source SVG is fully standalone; the render recipe merely avoids color-rounding changes from luminance-mask premultiplication/unpremultiplication.

Tests preserve the identical supported-sample set and RGB values for all 12 payloads. All samples within radius0.55 logical pixel of each heat focus retain identical R1 RGBA and alpha255. The exact unmodified RGB-base hashes and per-output coverage statistics are in the proof bundle. A standalone SVG renderer can differ by rounding; canonical PNG/RGBA output from this recipe is authoritative.

The source references and actual existing-game witnesses were visually inspected before authoring. They are intentionally absent from this package. `author-geometry.cjs` and `semantic-contract.json` describe all authored geometry numerically; rebuilding does not locate or read game data, original art, screenshots, or private previews.

## Exact renderer and rebuild

The measured toolchain is Node v24.19.0, Sharp **0.35.5**, librsvg 2.63.2, libvips 8.18.7, Cairo 1.18.6, on Linux x64. `proof/renderer-versions.json` records every actual Sharp dependency version. The package does not claim reproduction with the older front-Multi Sharp 0.35.4 environment.

With the recorded renderer installed, run from this package:

    node verify.cjs
    node rebuild.cjs /absolute/new-output-directory

The rebuild output directory must not already exist. The frozen inventory checks all input hashes, exact renderer versions, output PNG/RGBA hashes, and the independent standalone SVG comparison metrics. Both densities are independently rasterized from vectors, with no d8→d4 or 1× raster intermediate.

To reconstruct the SVG authoring files separately:

    node author-geometry.cjs /absolute/new-source-directory

This writes the six sources and semantic contract, without original data. Byte-identical reconstructed sources are verified in the proof bundle.

## Exact transforms and standalone SVG rendering

The standalone SVGs describe the exact semantic whole-canvas transforms. Rasterizing reflected Bezier paths separately with librsvg/Cairo can differ slightly at antialiased boundary samples due to scan-conversion rounding; mask processing can also round straight RGB. To enforce the stronger **byte-exact** output contract, the d4/d8 renderer rasterizes canonical 281 once per density and permutes its full RGBA canvas for 282/300/301. It never crops, recenters, traces, or edits a source raster. The two lateral heads are rasterized independently. The same inward-only coverage mask is applied before exact whole-canvas transformation.

Each transformed standalone SVG is also rasterized independently and its difference from the exact-permutation output is recorded in `output/render-receipt.json`. The canonical PNG/RGBA output is authoritative for binding. The proof records the differences rather than claiming independently scan-converted reflections are byte-identical.

## Binder handoff

Use the PNG or raw `.rgba` files from `output/`, together with the per-density SHA256 and FNV1a64 pins in `inventory.json`. Each raw file is row-major straight RGBA, four bytes per pixel, with full-canvas placement. Expected raw sizes are 10,752 bytes at d4 and 43,008 at d8.

An optional `pack-hda.cjs` packs these frozen payloads only after a binder supplies **all twelve explicit bindings**. Its JSON input is an array of objects with `source_id`, `density`, `key`, and `filename`. It has no inferred role or automatic key scheme:

    node pack-hda.cjs /absolute/bindings.json /absolute/new-hda-output-directory

The resulting HDR1 header is key, density, logical width12, logical height14, anchor0,0. The packer checks payload hashes first and writes a separate receipt. Role/key selection, source admission, provenance/lifetime guards, and runtime validation remain the binder's responsibility.

## Review boundaries

Offline native2×/4× comparisons use direct nearest-center sampling from density4 or density8 and the renderer's rounded straight-alpha compositor, without a native1× intermediate. All original references, witness screenshots, game-background crops, and comparisons are maintained outside this package in the private review material. They are not candidate gameplay captures. Existing Hard/night behavior must be preserved in runtime; no night treatment is baked into these warm art sources.

This pilot adds no animation, shadow artwork, alternate powers, shop resources, linked/chain/charge families, enemy IDs, Christmas integration, gameplay changes, or publication authorization.
