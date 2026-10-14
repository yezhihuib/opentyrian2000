# Protron independent shadow coverage

Three separately authored coverage masks for normal player IDs **225, 244 and 226**. Source, frozen artwork, build and focused units pass as of 2026-10-14. Six fresh current-baseline/candidate runs also pass bounded numerical comparison and native 2× author review. Historical head acceptance is retained separately and is not used as the current RGB baseline.

## What changes

Only `src/render_mirror.c` changes production behavior. The three IDs join the existing ten-member single-command shadow lease. Head slots 469–471, source/head pins, head artwork and RGB/alpha bytes stay unchanged, as do callers, original indexed blitters, coordinates, draw order, gameplay and public APIs. The ten earlier Vulcan/Multi members retain their exact pins and operators.

The [generated-only artwork package](../../assets/hd/artwork/player-protron-shadow-three-v1/README.md) supplies a small circle (225), offset large circle (244) and independent oblique oval (226). Each retains logical 12×14, anchor (0,0), original semantic size/centroid and the caller's existing shadow origin. The geometry is not clipped to the old staircase: smooth boundary cells may extend outside old indexed support within the reviewed bounds.

These density-8 HDR1 resources use loader-only role 125, prefix `protron-shadow`, keys 1250225/1250244/1250226 and independent slots 532–534. Draw identities remain role 8 and the original IDs. The two default packs gain three entries each, 540→543; existing resources and family metadata stay intact. The frozen masks have white RGB, resolving the initial zero-RGB packaging proposal. Their full RGBA identities are pinned, but only alpha supplies coverage; mask RGB never colors a shadow or head.

## Full interiors, antialiased edges

Coverage is exactly 255 inside the vector shape, fractional only where raster cells meet its boundary, and zero outside. It is independent of the softened head alpha. There is no Gaussian fade, normalized head alpha, global opacity reduction, or shrunken core.

The compositor first computes the existing full-strength result: the original after-index palette color for a classic underlay; `darken_rgba(current,255)` for ordinary HD; or the existing palette-ratio/ramp-floor operation for cloud HD. It then blends that result using mask coverage and the existing integer rounding. Full-coverage interiors therefore retain the existing shadow strength. Fractional edge coverage smooths only the contour.

The original indexed shadow still executes exactly once on every original-support cell, including cells where the smooth mask is zero. Smooth coverage adds no indexed writes. Display ownership/checking uses original support ∪ smooth coverage, retaining selection, cloud provenance, green-head invalidation, local restoration and command ordering.

Unchanged head bytes do not imply identical final head pixels: a later translucent head legitimately blends with a changed shadow underneath it. Such changes must follow the traced overlap and ordering; later opaque pixels erase the dependency. Unrelated scene changes are not permitted.

## Guards and fallback

Head and mask metadata, loaded pointers, root-derived paths and exact loaded bytes are checked independently at preparation and again before mutation. The pending command binds the selected coverage pointer. This validates loaded memory; it does not reread unchanged disk files on every warm draw.

- Missing or invalid masks decline only that member's smooth shadow. Normal heads keep their independent 8→4→indexed fallback. A valid mask cannot enable a missing, altered, invalid or density-4 head resource; no density-4 mask fallback is added.
- Classic, missing/invalid diagnostic and original-reference modes stay outside this lease. Existing surface/storage/format/pitch, canvas, bank/size, tick, origin, density, clipping and capacity guards remain.
- Actual Christmas mode rejects before cold or warm head/mask lookup. Normal eligibility also checks the selected source semantics. An artificial `xmas=false` alternate bank with identical 225/226 semantics may pass; differing 244 semantics reject. This is not whole-bank provenance.
- Reachable shared normal-player uses of these exact IDs share this route. Enemy and direct shop/menu/Christmas-prompt routes remain separate. Front-port fixtures do not certify every shared-use scenario.

## Verification and reproduction

- [Artwork](ART_CHECK.json): all three masks and both pack bindings, exact alpha/PNG/HDR1 identities and a 20-file relocated rebuild. Run `python3 prototype/build-protron-shadow-art.py`; Node, Inkscape, ImageMagick and Pillow are required. `--output NEW_EXTERNAL_DIRECTORY` retains the isolated rebuild.
- [Source scope](SOURCE_SCOPE.json): 148 production files checked; only the renderer changes. Existing manifest entries, sources and family metadata are preserved.
- [Build](BUILD.json): Linux engine build succeeds with SDL2/SDL2_net. The reported misleading-indentation warning is on an unchanged baseline line. Compilation is distinct from runtime acceptance.
- [Focused units](UNIT_RESULT.json): both default packs pass optimized and ASan/UBSan primary and all-13-member Present/fade runs, eight runs total. Each primary run covers 45,818 transactions and 237 malformed/missing/swap variants; each presentation run covers 156 Present/fade checks. Original indexed writes/padding, full and partial alpha, ordinary/cloud/mixed owners, ordering, fallback, cold/warm identity, clipping and restoration are checked. HUD/font/material integration is stubbed or fail-if-entered; LeakSanitizer alone is disabled for ptrace.
- [Public-runner equivalence](UNIT_PORTABILITY.json): replacing a local-only baseline commit with its identical published Git tree preserves all 10,256 prepared input files. The separate [legacy Multi portability correction](LEGACY_HARNESS_PORTABILITY.json) similarly changes only its baseline lookup/receipt key; all 5,700 prepared files and C harnesses are unchanged. These naming corrections do not claim additional unit or game runs.
- [Runtime comparison](RUNTIME.json) passes independent numerical review; [native author review](AUTHOR_REVIEW.json) passes with the stated visual scope. Neither replaces the source/unit arithmetic proof.

The unit entrypoint is `python3 prototype/test-protron-shadow.py --normal-data LEGAL_NORMAL_DATA --xmas-data LEGAL_CHRISTMAS_DATA --out NEW_EXTERNAL_DIRECTORY`. It requires pinned legal local inputs and never downloads or distributes them. `--prepare-only` is not a test pass. The aggregate `prototype/build-hd-assets.py` includes the new verifier but was not run in the sparse implementation checkout; changed-resource verification and old-manifest preservation are separate receipts.

## Bounded actual-runtime acceptance

Three fresh current-baseline/candidate pairs at P1/P6/P11 completed 90 ticks per run: six Linux SDL dummy/software runs and 540 logic ticks. Each uses the original stationary continuous-FIRE diagnostic input. Native 2× and true INDEX8 captures at ticks 40–45 yield 36 images of each kind, or 18 pairs. Historical captures are authentic reference material only; intervening renderer/resource changes required fresh baselines.

All 22 original trace tables per pair compare exactly, including state/RNG and original projectile/request/emission/event ordering. Controls differ only in wall-clock timing. Whole-stream and per-tick normalized original blend proofs match; raw blend rows were streamed rather than retained. All 18 INDEX8 pairs, including palette, are byte-identical. Candidate eligible shadow commands are 440/724/1,346 at P1/P6/P11; 0/20/20 other original shadow commands retain guarded fallback across those 90-tick runs.

Independent native comparison finds 3,746 changed pixel observations across the 18 pairs and zero changes outside the sampled original-support ∪ mask-coverage influence/order domain. All 36,293 uncontaminated shared full-coverage core samples are unchanged. Newly added full-coverage areas and fractional edges have positive witnesses for every observed ID. This demonstrates preserved shared interiors and the intended contour changes; exact shadow arithmetic for arbitrary pixels/palettes remains unit evidence. Coverage categories overlap and are not disjoint pixel totals. The small 225 mask has no removed-old-support sample at native 2×.

P6/P11 include observed fractional-head dependencies, so unchanged head resources must not be advertised as globally identical composited head pixels. The checker models opaque-head erasure, but these captures have zero actual opaque-erasure observations; that coverage remains with the units. The runtime comparison establishes containment, order and shared-core equality, not an independent reconstruction of every scene RGB operation. Its traces do not establish per-pixel cloud/terrain provenance or complete same-pixel scene ordering.

Direct author review of all 18 native pairs accepts the distinct small-round 225, large-offset-round 244 and short-oblique 226 shadows, their dark interiors, original visible placement and cleaner edges. There is no visible new halo, head-color regression or detached residue in the reviewed portions. Visible cloud/rock contrast remains consistent; this is an appearance observation separate from numerical material provenance. Clipping, foreground/head/shadow coverage and low contrast hide parts of some silhouettes, so the review does not certify complete contours or unobserved overlap variants.

The historical [three-head acceptance](../PROTRON_THREE_HEADS.md) and its frozen inventory/receipts remain intact. This new batch adds no native 4×, Christmas or missing-resource engine run, other-power/shared-use gameplay matrix, natural-collision/manual-play, full-level/campaign, Windows, physical display/GPU, fullscreen or performance acceptance. Original game pixels/data, decoded fixtures, raw runtime traces, captures and test packs remain outside the public documentation.
