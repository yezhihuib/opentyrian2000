# ShapesY gray platform28 — bounded local qualification

This document records the finite implementation boundary and bounded Linux
qualification below. It does not claim Windows or full-campaign acceptance.

## Exact scope

One-based `shapesy.dat` IDs:

`321 322 323 324 325 326 331 332 333 334 336 341 342 343 346 351 352 353 354 361 362 363 364 365 374 375 384 385`

- Exactly28 platform tiles, each24×28, anchor(0,0), only density8.
- Water25, bronze356, coast1–28, and all Y Layer2/3 remain classic.
- No native source data, game palette RGB, or original water pixels are stored
  in the generated master. Original maps, indexed writes, scroll, collision,
  simulation state, RNG and layer order remain authoritative.
- First observed context: E1 physical12, map3, shapesY, palette5, unfiltered.
  This is not Windows, GPU, full-campaign, or unknown-context acceptance.

## Single creative source

`authoring-inputs/shapesy-platform-current/master-platform.png` is the generated
five-component V2 material board (deck, front wall, side wall, bevel, red recess).
The deterministic recipe selects these components using fixed UVs and immutable
source-derived semantic geometry. It does not create28 independently painted
images. Cropping, resampling, bounded component-repeat registration and original
shadow-mask lighting are assembly operations, not a second creative source.

`prototype/build-shapesy-platform-art.py` exposes `generate(root)` and
`input_paths(root)`. `scripts/current_shapesy_platform_compatibility.py`
independently checks exact family membership, dimensions, binary per-cell alpha,
all672-cell source-water mask hashes, and the one source-black cell in333.
The same generated PNG bytes feed both selected default HD packs. Role202 is
separate from role201 shapesZ and from all other finite families.

## Water and source-black semantics

A transparent terrain texel alone is **not** native passthrough in this renderer.
Ordinary tile replacement suppresses the subsequent native mirror write, leaving
older RGBA under transparent texels. Y therefore uses a finite Layer1 pass/row
lease, validated source slots and source bytes, and current cell coordinates to
allow only source-water cells48–63 through the existing native mirror callback.
Their actual palette RGB and classic ownership replace earlier scene pixels.
Nonwater cells remain HD-owned. No additional full-screen owner buffer exists.

The original HDA/native-pass contract protects all5261 source water cells, including
322's water phase, shadow indices48–50 and375's single water cell. These are not
new water animation frames. The later straight-contour pass may recompose only
water inside its explicit two-sided transition mask; outside-mask water and all
native INDEX8 writes remain unchanged.

The original blitter skips index0. Tile333 has one such cell at logical(9,9).
Its generated64 subpixels must be opaque black, but that is accepted only with
proof of the actual Layer1 indexed/RGBA black clear and zero-cell owner state.
It cannot depend on a nonexistent672nd pixel callback or stale earlier RGBA.

Unsupported palettes/styles/effects/density, wrong layer/source/pointer, absent
or corrupt required resources and failed proofs retain classic fallback. All28
resources preflight as one family; Z and other existing families remain separate.
Frame/map/pass/row endings invalidate leases. Source aliases are revalidated.

## Rebuild workflow

Authoring requires Python3, Pillow and NumPy; the game runtime does not.

1. Edit the shared master only; preserve immutable geometry.
2. Prepare a selection with the exact input hash closure.
3. Stage outside the repository:

   `python3 scripts/build_current_shapesy_platform.py --root . stage --selection <selection.json> --destination <new-external-stage-dir>`

4. Inspect the complete28 atlas and actual-map assembly before applying.
5. Apply only the reviewed, unchanged staged plan:

   `python3 scripts/build_current_shapesy_platform.py --root . apply --destination <stage-dir>`

Stage/apply rederives every byte and checks old hashes before replacement. It is
not a permission to update source-qualification pins or repin old acceptance.
Handled write errors roll back; process/power loss is not transactional.

## Proof boundaries

The finite PUBLIC7d inverse ledger restores exact public preimages and removes
only the new Y source/resource closure before older current-source/P9/runtime/
SHOP oracles run. Historical expected hashes remain unchanged. Verification does
not read private Git objects or require original game data.

Static map3 review covers410 placements,138 touching cardinal pair types and960
instances:117 internal platform contacts and21 external classes. Every external
candidate edge is source water, so it must equal its native baseline; this does
not claim the original two facing edge samples were numerically equal. Actual
run coverage is reported separately, including later326 when observed.

## Prior material qualification result (2026-10-26; contour superseded)

The approved V2 recipe uses an interior162×200 deck period (not the master
board's exceptional outer border), scaled to192×224;336 uses a coherent generated
recess rather than an original-red-pixel stencil. In that prior version, source water and its original
edge silhouette were intentionally unchanged. The inward contour revision below
supersedes that silhouette decision; the material and water qualifications remain.

- Linux native HD-on, default-off and mirror-disabled builds passed. No Windows
  build or full-campaign acceptance is claimed.
- Optimized and ASan+UBSan native compositor fixtures passed for all28 IDs using
  real art and real RGB888 palette representation;65 missing/corrupt/header/alpha
  family negatives passed per run. Leak detection was disabled.
- Natural E1 physical12 map3 replay rendered all160 frames0–159 with no rejection
  or coverage mismatch:8040 accepted Y draws,27 distinct IDs. Tile326 has exact
  source/static-map and full native-fixture coverage, **not natural-game capture**.
- True640×400 and1280×800 captures both use internal density8. The window scalers
  are2x and4x; they are not resource densities. Effective density4 was separately
  confirmed in telemetry and produced zero Y replacements/classic Y fallback.
- Same-input present/reference/missing-resource pairs preserve INDEX8, original
  state/RNG, coordinates, native material/layer log, projectiles and collisions.
  Present does not advance RNG.
- At ticks158/159, all protected embedded-water pixels match missing-Y native
  baseline exactly in both resolutions. Early20/21 captures additionally confirm
 333's visible black cells,375's single water cells and shadow-water48–50.

The replay naturally ended at568 before the proposed1000 capture. A later350
window was valid and state-equivalent but did not reach326. No survival edits,
actor/map injection or eligibility broadening was used. E1 physical8/17 lack five
required bindings354/374/375/384/385 and remain classic under this family-wide
preflight; physical17 also enables an unsupported water filter. Do not describe
this as universal shapesY map reuse.

The corrected zero333 proof compares the canvas against `palette_rgb(0)`, not
raw `rgb_palette[0]`: actual SDL RGB888 stores black as0x00000000 while the mirror
uses opaque ARGB0xff000000. Tests model that real representation. Earlier
synthetic alpha-prefilled evidence is superseded for zero333 qualification.


## Superseded inward-only prototype (2026-10-26)

This section records the earlier proposal, not the current accepted result.
The user subsequently requested genuinely straight upper and lower edges. See
[the current straight-contour contract](shapesy-straight-contours.md), which permits
a tight two-sided contour band while preserving native gameplay and all pixels
outside that exact band. The earlier all-water-RGB constraint is superseded.

The user-requested edge correction is code-native coverage, not new artwork or
image-wide filtering. The source PNG/HDA/master material bytes remain identical.
After all eight qualified Layer1 rows finish, and before Layer2/actors/HUD, the
existing mirror canvas receives a narrow source-semantic contour operation:

- Recognize a gray-cell convex corner only when two outward cardinal cells and
  their diagonal are qualified native water, two inward cardinals are gray, and
  at least one adjacent corner continues the same45-degree staircase. Isolated
  true90-degree corners, interior material edges and non-Y coastlines are excluded.
- Clip only the outward half of that original gray cell. At density8, triangle
  interiors use read-only neighboring native water RGB and the crossing diagonal
  gets exact half coverage. Maximum geometric inward extent is one native pixel
  along an axis, or1/sqrt(2) pixel normal to the45-degree contour (2.83 output pixels
  at4x). No original water pixel is changed.
- Reuse the existing canvas and HD ownership. A compact8×12 pointer witness and
  eight replaced-bit fields bind the complete pass; there is no second fullscreen
  compositor or ownership buffer. Water taps must match actual INDEX8, expected
  indices, classic ownership and all64 current palette-colored canvas samples.
  Each gray center must retain all64 exact authored samples with HD ownership
  and no cloud ownership; unexpected intervening draws fail closed.
- Preserve native INDEX8/expected bytes, tile placement, state/RNG/collisions,
  crisp deck/recess detail and source333's skipped index0 cell. That zero cell
  has no immediately adjacent water and cannot enter the radius-one contour.
- Final pass/source/palette/resource/context checks remain mandatory. Rejection
  clears pass state before reporting failure, avoiding recursive invalidation.

Actual native1280 same-input frame158 baseline/prototype comparisons preserve all
160 logical state rows and26 trace files byte-for-byte; only the intended RGB
hashes and elapsed wall time differ. Final focused qualification is recorded in
separate edge-AA receipts; this section alone is not a Windows/full-campaign claim.

Focused postpass qualification passed against the actual pinned pack, plain and
ASan/UBSan: all28 static members, all28 scroll phases, six horizontal offsets,
278 original-map cross-tile candidates, and exact full-canvas independent coverage
oracles. Water/interior/source333-zero, INDEX8/expected, and owner arrays remain
byte-identical. Dirty water taps (5), dirty gray centers (3), changed map pointer,
omitted native callbacks, draw-capacity reset and six late-frame mutations fail
closed. LeakSanitizer was disabled because this executor's ptrace environment
prevents it; this is an address/undefined-behavior pass, not a leak-check claim.
The existing runtime suite additionally passed all65 finite-resource negatives.

Reproduce focused AA checks with original data kept outside the checkout:

```
python3 tests/test_shapesy_platform_edge_aa.py --data "$DATA" --pack "$PACK" \
  --out "$OUT" --sdl-include "$SDL_INCLUDE" --sdl-include "$SDL_MULTIARCH_INCLUDE"
```

Add `--sanitize` for address/undefined checks. The separate bounded production
inverse gate is `tests/run_shapesy_edge_qualification.py --out <fresh-external-dir>`;
it executes each source-positive phase once and never reads private historical
Git objects or rewrites the current Git index.
