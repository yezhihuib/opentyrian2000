# Cloud64 lower free-edge correction, v3

Small, generated-art-only delta for the existing OpenTyrian2000 HD cloud family. Replace only cloud64 in the current selected pack. This is a prepared formal artifact. A bounded late actual-runtime window has been verified; ordinary replay and missing/wild regressions remain pending in a separate engineering task.

## Exact contract

- shapesz.dat, layer2, one-based offline ID64, existing slot199.
- Logical cell24×28, density8, anchor0,0; saved output192×224, straight RGBA8.
- HDA is `HDR1`, six little-endian u32 values `[2010064,8,24,28,0,0]`, then row-major RGBA bytes.
- Only ID64 changes. All other14 cloudIDs, especially55/63/65, stay unchanged. No binder, renderer, shadow-path, layer3, sprite or terrain changes are included.
- All four outermost RGBA faces and rows0..127/200..223 are exact against the prior generated v2 tile. Changed bounds are x1..190,y129..199 (inclusive), 12,987 pixels.

Merge only `runtime-overlay/terrain-shapesz-64-8.hda` into the current selected resource pack, preserving every other byte. Do not replace the entire resource pack with a historical test pack. `contract.json` records the selected hashes and scope. Publication or integration is not performed by this package.

## Two-input reconstruction

Requirements: Python3.9+ with Pillow and a C++17 compiler (`c++` by default; override `--cxx` or the single-executable `CXX` variable). Tested with Python3.12.14, Pillow12.3.0, GCC14.2.0. No ImageMagick, GEGL, original game data, original masks, game executable, map files, network access or image-generation service is needed for rebuilding.

From any working directory:

    python3 /path/to/formal-cloud64-v3/rebuild.py --output-dir /path/to/empty-build-directory

The wrapper loads exactly these two bundled, hash-checked, regular files:

1. `source/prior-generated64-v2.png`: the prior generated HD64 tile from `formal-cloud-v2-edge/output/terrain-shapesz-64-8.png`. It contains generated RGB and the prior registered alpha. It is explicitly not the original game64 raster or an original mask file.
2. `source/generated64-bottom-reference.png`: the saved canonical crop of the newly generated lower-edge artwork.

It compiles the bundled helper in a temporary directory, reconstructs RGBA, verifies its hash, and writes one PNG, one HDA and a rebuild report. It never reads the selected output as a reconstruction input. It rejects modified canonical sources and external source symlinks. The output directory must be empty; selected committed files are preserved.

`provenance.json` documents source hashes, generation context, the omitted1500×1049 master, historical Lanczos registration to960×672 and crop192×224 at+384+448. The prompt is included as provenance, not a deterministic instruction to regenerate art. Reconstruction starts at the two saved PNGs. Original low-resolution art was historical visual/registration reference only; no original raster, mask or data file is distributed here.

## Deterministic correction

The unchanged selected C++ helper samples generated y+20 to retain the established mean boundary height. Smooth weights localize the correction to x1..190,y128..199, with zero change at y128. Generated low-alpha RGB is replaced by the nearest sufficiently opaque sample above; source alpha≥250 becomes255 and alpha<4 becomes0 before blending. Four-neighbor cleanup removes the single detached alpha4 residue at(104,176). The connected feather is preserved. Independent Python implementation reproduces every output byte.

Expected decoded RGBA SHA-256:

    fc88d9e42885e523c54111ab8e9a833a887256b222e97549d9d972bec988480f

Expected HDA SHA-256:

    1f9378615e16157f59113a47066dd28a52433c28e5a36d8845491b355e64a3b8

Selected committed PNG SHA-256:

    5a7b79fac3399d87cde0fb2d855e92e2121ed127a5112f7afcb5216e70deead3

Pillow's rebuilt PNG has different encoding bytes from the committed ImageMagick PNG. This is expected. The tested rebuilt PNG SHA-256 is `986921691218e7643090a2849a103fa6085760819d92ae7bfbf547da2009e1b3`; decoded RGBA and HDA remain exact. The selected PNG file hash is verified separately rather than confusing image equivalence with file equivalence.

## Verification

Run:

    python3 /path/to/formal-cloud64-v3/verify.py

Optional report:

    python3 /path/to/formal-cloud64-v3/verify.py --report /path/to/report.json

The included verifier checks canonical ownership/hashes, selected PNG and HDA, independent pixel reconstruction, exact changed bounds, preserved regions, detached-pixel cleanup and connected alpha thresholds1/16/128/240. It separately rebuilds from only four files (wrapper, C++ source, two source PNGs), without selected outputs, in a fresh directory and a relocated directory containing spaces, from an unrelated working directory. It also checks that mutated sources and external symlinks are rejected before creating outputs. Temporary compiled/raw files are removed automatically.

- `verification/independent-package-check.json`: reproducibility and pixel-scope results.
- `verification/source-and-neighbor-check.json`: canonical crop derivation independently matched; all10 nonzero neighboring pair types touching64 have exact RGBA faces. The other14 external v2 PNG/HDA files were checked against the existing v2 manifest; their hashes are listed, but their art is not copied here.
- `verification/runtime-status.json`: bounded actual late-window results and the still-pending engineering regressions.
- `verification/author-static-contract.json`: the artwork task's original static evidence, copied verbatim before the later actual-window review. The author reports visually reviewing all98 full-map placements in context. This package review does not claim to have repeated that visual review.
- `handoff-inventory.json`: exact files, byte counts and SHA-256 values, excluding the inventory itself. Its own hash is supplied separately with the handoff.

## Why this narrow change

The read-only neighbor audit traced the straight-looking lower edge to original64's near-flat registered silhouette, amplified by brighter generated cloud RGB. The16-pixel connector reconciliation did not create that interior shelf. ID64 occurs98 times in37 runs;21 runs repeat it, creating61 self-joins. The early row595 pattern, checked at tick20, repeats the same corner pattern as the reported defect at row438/tick2178. Therefore the issue was not a new uncovered adjacency. Previous exposure did not establish aesthetic acceptance.

All10 touching nonzero pair types remain exact. Preserving the four faces retains existing corner connections, including accepted55 through unchanged65. The two seven-tile runs at rows244 and304 have static context review only. The correction targets64's lower free contour and graded blue shading without rerunning family-wide reconciliation.

The artwork task verified a bounded private-survival actual-runtime window: ticks2118–2237, 120 frames, every direct RGBA readback hash exact, 93 changed frames strictly within cloud64's lower source ROI, and HUD exact. It reports reviewing all visible cloud-edge frames with no cusps flashing or new seam leak. The package reviewer checked the source report's consistency, not the raw capture. Ordinary replay ticks0–1052 baseline/candidate and missing64/wild fallback regressions are still pending. This package does not assert full-level actual gameplay acceptance, Windows/GPU coverage or physical2K validation. No original game raster/mask/data, full master, map array, screenshot, private executable, compiled helper or archive is included.
