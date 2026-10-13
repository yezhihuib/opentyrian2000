# Type15 eight-heading smooth contours v2

This is a finite refresh of the eight bank1/newsh2 type15 composites. The frozen generated art is imported once at `assets/hd/artwork/type15-eightheading-smooth-contour-v2`; all 70 original inventory entries, including the eight PNG/HDR1 outputs, remain exact. `IMPORT.json` records the Library identity and import inventory. Historical v1 art and its acceptance records remain unchanged.

## Scope

- Namespace101; bases39/41/43/45/91/93/129/131; slots396–403; density8; logical24×28; anchor6,7; original parts0/1/19/20.
- Original event selector order91/45/93/39/43/129/41/131. No automatic rotation, collision, RNG, state, input, actor movement, hit, death or drop changes.
- The sole production delta is eight exact RGBA FNV readiness constants and the adjacent obsolete-alpha explanatory comment in `src/render_mirror.c`. Family readiness remains atomic, cached and selected-pack scoped.
- Fractional contours, support additions/removals and the two genuine C93/C129 apertures are the exact approved authored bytes. Original support is not reimposed. Nonzero and alpha≥128 bounds both equal the original registered bounds for each heading.
- Both existing defaults retain507 HDA entries. Sixteen existing HDA files are replaced and eight new canonical PNG references are added; historical PNG references remain.

## Reproducible source and loader gates

Run from a checkout with its required immutable source packages materialized. Every output directory must be fresh and outside the repository.

```
python prototype/build-type15-art.py --output /fresh/C-rebuild --original-data /path/to/tyrian2000
python prototype/test-type15-source-guards.py --out /fresh/C-source-guards
python prototype/test-type15-binding.py --out /fresh/C-binding
python prototype/test-type4-binding.py --out /fresh/B-regression
python prototype/test-type15-preservation.py --out /fresh/C-preservation.json
python prototype/build-hd-assets.py
```

The original-data lane verifies32 source RLE tiles and all1701 enemy records. Generated-only rebuilding verifies all eight PNG/HDR1/RGBA/FNV outputs, complete masks, aperture regions, registration and both defaults. C binding tests extract current production functions under ASan/UBSan and exercise all first-member orders, four quadrants,256 filters, both defaults, missing/corrupt members, allocation/cache/reset, density4 and mixed-v1/v2 rejection. B binding remains runnable using only the exact eight-pin/comment source projection; raw comparison lanes use matching C-v1/C-v2 art. All146 production source paths must otherwise match the immutable baseline, with192 adversarial source mutations rejected.

Startup-manufacturer and title-package tests contain literal C-v2 pins and directly exercise their full C validation/projection, including positive and negative controls. Their preexisting unrelated settings whole-manifest assertion is retained and continues to fail; no current whole-package pass is claimed.

## Bounded runtime contract

The four authorized runs completed once each with14 native captures. `RUNTIME_VALIDATION.json` records the exact numeric acceptance. The diagnostic uses two otherwise-identical private builds with alive-only invulnerability floor2, stationary/no-fire seed0x5eed replay, original events and movement. No instrumentation enters production source.

The authorized four runs comprise six native640×400 captures per v1/v2 lane at4214,4215,4521,4525,4527,4530; one candidate1280×800 capture at4525; and one missing91 capture at4525 with source observation at all six ticks. Maximum600s/96MiB each,4GiB free floor; no discovery or extended window.

A read-only per-quadrant before/original-call/after oracle checks exact renderer equations against the loaded source and original RLE. Post-four-call snapshots serialize clipped RGBA, HD ownership, cloud ownership and indexed pixels. Final output replays the original INSERT COIN glyphs, original glyph/shadow order, rounded HD half-shadow, classic palette-shadow and cloud palette-ratio branches exactly. No pixel exclusions, tolerances, opacity inference or bare-art substitution are permitted. Missing91 is compared against its own original-RLE final composite, with exact neighbor pixels outside actual C rectangles; it is not compared to the v1 HD foreground.

## Limits

NW91 is source/unit-only. The six2× captures cover seven presented headings, not seven wholly unobscured views: N/NE/E/SE are partly covered by later text/shadow; the secondary S atx274 clips at the right edge (x206 is the complete S exposure); C93's rectangle starts aty−4 while its authored nonzero support remains in bounds. No natural-survival, firing/hit/ice/death/drop, manual-input, full-level, GPU/fullscreen or Windows acceptance is implied. Numeric and independent visual gates remain distinct, with their receipts alongside this document.

## Actual result and retained correction

All four executions passed in48.3/46.7/44.8/46.7 seconds, with 3,863,956 / 3,865,683 / 2,881,188 / 2,002,543 evidence bytes, below every admitted budget. The exact gate verifies:

- 4531 original state/indexed/RNG ticks in both2× and missing lanes;4526 in true4×.
- 40/40/32/40 actual C quadrant calls across baseline/candidate/4×/missing; zero mismatched per-call canvas samples.
- 94,368 candidate2× and75,698 true4× fractional-alpha samples.
- 1,512,128 paired native pixels outside the union of actual C rectangles, and253,696 missing91 neighbor pixels.
- 59,264 exact final clipped rectangle pixels across14 native captures, including source apertures/removed support, normal glyphs, HD/classic/cloud shadow branches and unchanged later actors.
- The complete candidate2×/true4× internal8× RGB, original-source and both draw-stream prefixes through4525, plus exact sampled internal8× RGBA/owner/cloud/indexed planes.

The initial offline final-layer model failed112 baseline4214 pixels in the transparent top margin of the secondary right-edge S. This was an omitted later original layer: unchanged newsh2 actors273/277 draw over that margin after C. The versioned offline oracle replays their actual ordered quadrant calls from pinned HDR1 and original RLE, including ownership/index updates; the corrected full-rectangle check passes without excluding any pixels. The failed oracle, exact diagnosis and all original captures are retained. No runtime input changed during any run, no run was repeated and no window was extended.

Final full package runs were15/16 startup-manufacturer and20/21 title-package, each retaining the single unrelated settings-manifest failure. Direct positive/negative C guards pass separately and cannot be short-circuited by that existing failure.
