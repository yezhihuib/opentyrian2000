# ASTEROID1 paired industrial installation

This bounded checkpoint adds three original image identities for the upright
industrial installation, records 287 and 288, under the separate normal-data
Episode 1 physical level 1 ASTEROID1 opt-in. Upper 287/base245 and lower
288/base283 or281 remain separate independently allocated 24×28 actors. The
24×56 assembly is a visual reference only, never a merged runtime role.

Use --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1 through ordinary campaign
progression. The option does not select or play a level. The optional catalog
contains 38 images, 44 source records and 16 independently preflighted families.
All prior 35 optional PNG/HDR1 pairs and both 629-entry default catalogs remain
unchanged. Other second-stage artwork remains outside this checkpoint.

## Original source and behavior

Both complete serialized 77-byte records and the current loaded bank8/newshd.shp
are independently pinned. Record287 is static base245 with nineteen zero tail
entries; record288 has twenty entries, base281 at cycles7 and10 and base283 in
all eighteen other entries. The original engine advances the cycle before
lookup, even while vertically offscreen. No new delay or interpolation exists.
Each image uses the original four tiles at offsets0/1/19/20. Upper support is
672 cells; lower support is670, including grey rail and support pixels. The
two lower masks are identical and only23 original lamp cells change indices.

Seven original linked installations occur at curLoc4164 (links24/25), 5200
(link28), 5676 (links30/31), 6544 (link34) and6628 (link35). Original event6
allocates lower288 first and upper287 second, independently in pool25–49.
Original actor creation and its RNG consumption remain unchanged. Either
allocation may fail, either actor may clip or cull independently, and no live
partner is required. The renderer does not change scrolling, armor, cash value,
ice, damage or destruction. Explosion27 retains enemyground=false and
explonum13. Ordinary lethal player-shot damage retains original destruction
of actors sharing the link; nonlethal damage changes only the struck actor.

## Artwork and guards

The built-in image generator authored a common opaque aligned metal master and
an alternate amber indicator state. Steel rails, black/silver upper housing,
red stripe, gold seam and gold/red lower housing follow the original design.
The deterministic converter crops only the generated magenta exterior, scales
once, splits at the original seam and retains exact source coverage. Only the
original23 lamp cells sample the alternate generated state; every other lower
pixel is identical. Masters and provenance are retained with the final PNGs.
Density8 is internal raster resolution, distinct from native2x/4x displays.
Original game data and runtime captures remain external.

All three resources preflight coherently, requiring roles1080245/1080281/
1080283, density8, logical24×28, zero anchors, exact lengths and payload pins.
Missing or corrupt one disables this family. The other fifteen families are
independent. Selected-root failures are sticky until shutdown/reset. Current
bank bytes are compared against the renderer-owned immutable source snapshot
on every accepted call, including address-reused banks. Either source record
is mandatory even when only one actor is alive. A source/resource failure
after the first accepted quadrant rejects the whole HD frame.

Live admission checks the exact type and record pointer, pool25–49, availability,
size1, non-score/non-damaged state, positive current armor, one of the seven
links, source bank/filter/context equality, full twenty-entry graphics array,
exact per-type animation state, selected base, original zero intrinsic motion,
reversal100, enemyground=false, explonum13, zero drop/turret/launch/damage-image
fields and original quadrant origin. It does not pin current screen position,
scroll, armor or value. Every original ordered quadrant call and clipping rule
remains authoritative. Existing level/mode/lease/INDEX8 gates are retained.

## Finite validation and limits

See validation.json for precise optimized/sanitized unit, shared-snapshot,
preceding capsule regression, catalog, strict build, independent review and
actual-engine receipts. Extracted production tests cover154 cold plus154 warm
record-byte mutations, all20 cycles, seven links, both pool boundaries, all255
positive armor values, all256 ice states, independent actors, six clipping
origins, three filters, three-resource coherent failures,48 malformed/missing
fixtures and bidirectional independence from all fifteen peer families. The
shared snapshot suite covers16 families and44 dependencies in764 checks.
Optimized and ASan/UBSan pass; LeakSanitizer is disabled. Compiler address
space is capped at1GiB and runtime RSS at512MiB. Catalog-only verification
checks1258 default and38 optional entries using an explicit historical input
root; no historical local path is a public runtime setting.

Actual-engine evidence uses explicitly assisted original-event windows, not
natural campaign completion. Selectors replay original setup/spawn events and
retain eventRec bytes and RNG. No actor is injected, revived or healed. Native
2x/4x baseline/candidate comparisons cover all seven pairs, both lower lamp
states, independent clipping/culling and original linked destruction through
ordinary player firing. Missing/corrupt each member and flag-off preserve
classic fallback. Acceptance details and measured limits are in validation.json.

All24 paired runs (48 engine processes) exit0: ten enabled pairs and fourteen
fallback pairs. Per scale, ordinary windows accept5548 new-family commands and
preserve2326 prior-family commands. All14 gameplay/RNG/INDEX8 traces plus seven
original actor/event/shot traces are byte-exact. HD-only effects bookkeeping
counters change with intended new coverage; their gameplay fields stay exact.
Every missing/corrupt member and flag-off keeps complete frames, commands and
native PNG bytes equal. No coverage mismatch or rejected frame occurs.

Selectors directly memcmp-check all5772 active eventRec bytes, raw FNV
b839e2440d1b5eff and serialized FNV01d73c470a9401b1, preserving selector RNG
8005e0d4ef40f5b1. In4080 the lower actors cull at152 while the upper actors
remain until166. Ordinary weapon155 shots reduce lower armor16 to2 without
changing upper armor10; the lethal eighth shot at51 destroys both link28 actors.
Independent review reports no blocking finding and raw-compares1008 named trace
files,22320 original actor/call rows and28 fallback native PNG pairs. Tested and
strict production renderer objects are byte-identical. Native PNGs
are640×400/1280×800 unresized readbacks. Peak sampled runtime RSS is95.71MB.

This is not whole-level or natural-campaign acceptance, Windows/fullscreen/GPU,
performance or LeakSanitizer acceptance. No Windows package or push is included.

Rebuild: prototype/build-asteroid1-paired287-288-art.py --data ORIGINAL --out OUTPUT

Runtime tests: tests/test_asteroid1_paired287_288_runtime.py --data ORIGINAL
--out OUTPUT --sanitize. Add explicit --sdl-include paths if needed.
