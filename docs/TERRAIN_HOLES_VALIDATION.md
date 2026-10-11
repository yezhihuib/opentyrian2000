# Finish terrain 111/114 and the audited first-30-second segment

Two authored shapesZ layer1 tiles complete the remaining observed terrain: 111 is a brown stone cluster with interior gaps; 114 is a distinct gray boulder. Both use 24×28 logical pixels, anchor (0,0), density 8. Exact slots are 241/242, capacity 243 and terrain registry 115. This change adds only finite binding and formal artwork; existing compositing, shadows, indexed drawing, simulation, events and map data are unchanged.

## Artwork and reproducibility

`python prototype/build-terrain-holes-art.py --output <new-external-directory>` rebuilds both selected HDA/RGBA outputs from authored crops and 13 hash-frozen accepted HD neighbors. The fresh rebuild also produced byte-identical PNG files. Original context masters, game references, standalone original masks and private test hooks are excluded from Git. The source README records all 36 map placements, 33 cardinal adjacency types/140 edges, the fixed geometry and the remaining maximum 11 RGB boundary residual against mutually inconsistent old neighbors.

Tile 111 preserves all 88 original logical holes (5,632 zero-alpha HD pixels), every zero/nonzero support bit and all generated RGB. Exactly 5,090 occupied HD pixels receive a smooth inward alpha transition within 0.5 logical pixel of a hole. The outer perimeter stays opaque. Tile 114 preserves its nine holes (576 zero-alpha HD pixels) and binary alpha. This is a deliberately bounded artwork-alpha change, not an alpha-compositor change. Some turns of the original hole topology remain visible; the artwork is not claimed geometrically round everywhere.

## Merged regression

- Ordinary runs through ticks 0–1052 pass at native 4× and 2×. All prior state/RNG/indexed operations, material ordering, effects and collision streams match the accepted road checkpoint. Each scale adds exactly 432 NORMAL/HD calls: 415 for 111 and 17 for 114. Missing both resources reproduces road-baseline RGB and all deterministic logs exactly.
- The paired processorType4 window (868–1052) exercises both new tiles without changing cloud BLEND fallback. New tiles remain layer1 NORMAL. Only explicitly documented HD-ownership diagnostics may change; simulation does not. In ordinary runs, 546 `hd_subpixels_before` fields reflect the new HD ownership; original blend indices, palette operations and results remain exact.
- Six focused ASan/UBSan binder/compositor suites pass 27,785,703 checks. They cover all 52 simultaneously bound terrain assets, ordered/partial rows, exact banks/layers/slots, unknown IDs, malformed headers/payloads, each missing resource and inherited disable guards. Actual selected fractional alpha and transparent holes preserve the expected underlying RGBA and ownership in the real production pixel functions at densities 2 and 8, including clipping and shadows. LeakSanitizer is disabled in the ptrace environment.
- All previously accepted authored resource bytes remain exact. The manifest verifies 18 packs, 2,734 HDA entries and 259 formal PNGs; current preview/debug packs contain 247/251 resources.

The separately documented integrated green lifecycle, installation collision/destruction, actual window and streamed-video checks are summarized in [FIRST30_HD_COVERAGE.md](FIRST30_HD_COVERAGE.md). Neither the bounded ordinary run nor static whole-map adjacency inspection is whole-level visual acceptance. Full tile 114 is outside the first-30-second ordinary window and is reviewed in the clearly labeled private-survival continuation.
