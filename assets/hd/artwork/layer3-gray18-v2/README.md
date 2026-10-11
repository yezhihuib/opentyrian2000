# Layer3 gray18 v2 generated-source handoff

This standalone package contains the previously selected gray18 artwork plus the frozen imagegen-authored dark-fringe correction for exactly **134, 141, 142 and 143**. The parent accepted both the bounded offline native 2×/4× review and actual runtime visual review, and authorized publication. **The engineer owns formal integration and its remaining gate.** Source packaging itself is not an integration test. The untouched `formal-layer3-gray18-v1` package remains the complete rollback.

## Finite integration boundary

Base commit: `d351fe256e82216baa5281be552399ea1a276cca`. Layer3, NORMAL mode only. Capacity 290; terrain registry 140. IDs in slot order 272–289:

`121, 122, 123, 124, 125, 131, 132, 133, 134, 135, 141, 142, 143, 144, 151, 152, 153, 154`

Every tile is logical 24×28, scale 8, anchor (0,0), decoded 192×224 straight RGBA. Every HDA is 172,060 bytes: `HDR1`, six little-endian U32 values `[2010000 + ID, 8, 24, 28, 0, 0]`, then 172,032 RGBA bytes. The four overrides preserve every existing header, slot, anchor and binder rule. The other 14 committed PNGs and HDAs are byte-exact to v1. Tile144 PNG remains `c4cd3a9dea6c5ecd14707ec5e0fef822407bb372f47b61cdbedd91da490772e8`.

No engine, main checkout, renderer, palette, indexed resource, gameplay, map, binder, or other accepted art is edited. Integration belongs to the engineer. `runtime-overlay/manifest.json` is the complete 18-tile oracle; `source/frozen-four-rim-manifest.json` is the exact upstream four-tile manifest. The separately frozen PNG, decoded-RGBA and HDA checksums have distinct meanings.

## Authored source and provenance

The source entry points are 18 generated binary-alpha crops in `source/generated-crops/`, plus four exact generated 192×224 quadrant crops in `source/generated-fringe-crops/`. These are generated-only art sources, with the approved original silhouette baked into the baseline RGBA. No original game RGB, separate original masks, game raster/data or reference images are distributed.

The baseline crops and `feather_occupied_alpha.cpp` are unchanged from v1. The first stage exactly reconstructs v1 from those sources. The second stage freshly compiles `compose_rim_fringe.cpp` and applies only the four corresponding generated fringe crops. This is a bounded technical registration of already-authored imagegen pixels.

The four new crops are exact quadrants of the registered 384×448 fringe master, laid out 134 upper-left, 141 upper-right, 142 lower-left, 143 lower-right. The imagegen original was registered using ImageMagick Lanczos. Packaging independently reproduced that registration byte-exact in decoded RGBA, then extracted the crops without further resampling. Full generated and registered masters, and the authoring reference atlas, are excluded. Their dimensions, hashes and prompt are recorded in `source/rim-fringe-provenance.json`. Upstream baseline masters, prompts, crop rectangles and matte/silhouette preparation are recorded in `source/baseline-v1-crop-provenance.json`; its old provisional status is historical. Generating a new image is not claimed to be deterministic.

Original 24×28 reference PNG and RGBA hashes are recorded in `verification/original-support-audit.json`, without distributing those images. Private read-only comparison reconfirmed that all 18 baked source alpha planes equal nearest-neighbor 8× original support and that all selected zero/nonzero support bits remain exact. Standalone rebuilding validates the corresponding immutable baked source hashes; it does not pretend to reconstruct original data absent from this package.

## Fringe scope and limitations

Relative to reconstructed v1, RGB changes occur only in occupied pixels whose old maximum RGB channel is below 52, strictly less than 20 HD pixels from a transparent source sample inside the tile. Lighter stone/highlight RGB remains frozen. Alpha changes only on the occupied side at strictly less than 8 HD pixels, never increasing alpha or removing nonzero support. A floor of 1 retains every occupied subpixel. All original zero RGBA and the outer two HD rows and columns remain byte-exact, including tile joins.

The independent verifier measures these properties from pixel differences. Maximum observed RGB distance is 19.41649 HD pixels; maximum alpha distance is 7.81025. Newly zero-alpha pixels and new enclosed transparent components are both zero. Occupied-support component counts are unchanged. At the stronger alpha≥128 threshold, tile134 changes from two components to three; this is reported rather than hidden and is not a support-topology failure. No perfect-smoothness, universal seamlessness, broad regression or full scrolling coverage claim is made. Small source steps remain reduced rather than eliminated.

The upstream helper metrics file was generated before the support-floor recount was added. It is deliberately not copied as final evidence. This package freshly builds the current C++ source and includes current helper logs plus independently recomputed metrics. The decoded output is unchanged from the frozen four-tile manifest.

## Standalone rebuild

Requirements: Python3, Pillow, C++17 compiler available as `c++`; Bash for the wrapper. No NumPy, ImageMagick, original game data, game checkout, network or image-generation service is needed for rebuilding. ImageMagick was used only for the separate upstream registration audit.

    bash rebuild-selected.sh "/absolute/new output directory"

Or:

    python3 source/rebuild_selected.py --output-root "/absolute/new output directory"

The output directory must be new and outside this package. Paths containing spaces are supported and tested. The script checks the finite 18-tile and four-override oracles; frozen source, manifest and helper hashes; committed PNG hashes; exact baseline reconstruction; exact decoded selected RGBA and deterministic HDA; all 14 unchanged tiles; frozen144; canonical transparency; baked 8×8 support; and independent fringe scope. It verifies the inventory when present and confirms the source package was not mutated.

The six fully opaque source PNGs are copied without encoding. Other regenerated PNGs use Pillow. In the tested environment, 14/18 regenerated PNG files are byte-identical, and the four fringe PNGs have different encodings with **exactly equal decoded RGBA**. All 18 committed PNG hashes pass independently; all 18 rebuilt HDAs are byte-identical. PNG encoder differences are not artwork differences.

A separate read-only scope check can be run against retained rebuild output:

    python3 source/verify_scope.py --rebuild-root "/absolute/rebuilt output directory"

Compiled helpers and intermediate RGBA files are written only under the chosen disposable output, never in this source package.

## Package boundary and verification

The package contains exactly 22 authored generated source PNGs, 18 selected PNGs and 18 selected HDAs. It excludes original/reference rasters, standalone masks, palette/index samples, original map arrays, full generated masters, runtime screenshots/videos, private hooks, prebuilt executables and rejected diagnostics. Numeric hashes and bounded topology facts are provenance, not bundled source-game assets.

`handoff-inventory.json` lists every other file's byte length and SHA-256, excluding itself from self-hashing. `verification/` contains reproducibility, relocation, boundary, ownership, original-support, scope and status records. The package was tested relocated into a directory with spaces, with fresh native compilation and inventory checking. No game or Git command was run by this packaging task.

## Bounded visual acceptance receipt

The parent reports root acceptance of actual 4× frame2564, all 120 exact SDL RGBA frames2490–2609 and their moving left/lower rim crops. No new seam, black-pad recurrence, background leak or flicker was observed; every v1→v2 pixel difference remained inside the four changed-tile rectangles. All 168 distinct whole-map 3×3 neighborhoods were reviewed at native2×, covering 275 placements, 79 directed pair types and 867 edge placements; edge signatures remain unchanged. These are bounded visual observations, not universal coverage. Small left silhouette steps remain, and source131 was covered offline only. The parent also reports a technical supplement covering 468 rendered frames, 120 cross-scale RGB-exact comparisons, unchanged state/material/effects/collision and 294 other resources. The packaging task did not run those engine tests. Receipt hashes and external evidence references are in `verification/runtime-visual-acceptance.json`; no captures or private hooks are included.
