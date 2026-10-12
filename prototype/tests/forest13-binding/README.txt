Forest13 and circuit10 renderer binding oracle
================================

Portable test-only package for the finite shapesZ / Layer1 forest family:
211, 212, 213, 215, 221, 222, 223, 224, 225, 231, 232, 233, 234.
Expected asset slots: 336..348. Circuit slots: 349..358. Asset capacity: 359. Pointer registry: 185.

Run from any directory with Python 3 and a C99 GCC/Clang-compatible compiler:

  python /path/to/forest13-binding-tests/run-oracle.py \
    --candidate /path/to/opentyrian2000-atlas-integration \
    --out /path/to/new-output-directory

  python /path/to/forest13-binding-tests/run-mutants.py \
    --candidate /path/to/opentyrian2000-atlas-integration \
    --run /path/to/new-output-directory \
    --out /path/to/new-mutation-output-directory

Output directories must be new and outside the candidate checkout and this
package. Set CC to a compiler executable if desired. Python standard library
only; no SDL, game data, image packages, network, baseline checkout or asset
pack is needed. The runner generates bounded synthetic HDAs, hardlinks shared
fixtures locally, extracts current production helpers unchanged, compiles with
ASan and UBSan, and records commands, input hashes and logs in result.json.
Compile and each execution have 90-second ceilings. The suite runs seven fresh
processes so production process-lifetime lower source caching is not rewritten
or reset by a test-only source substitution.

Leak detection defaults off because LeakSanitizer cannot run under ptrace-based
executors. ASan and UBSan are always enabled. Use --leak-detection for the main
runner on a host that supports LSan. All fixture allocations are explicitly
freed by the harness. Compiler flags include -fno-pie/-no-pie for deterministic
ASan mappings on the current Linux toolchain; ports can adjust those platform
flags without changing assertions or extracted source.

Executed production code
------------------------
- read_asset and scene_asset, including real HDA header/length validation and
  ordinary 8x-to-4x density fallback.
- map_begin, every finite terrain slot helper, bind_terrain and the actual
  selected-source callback.
- render_mirror_ground101_layer1 and render_mirror_terrain_row.
- The exact 600-shape / three-layer engine source-registration loop from
  tyrian2.c, including its 72/71/70 usable slots and distinct stored pointers.

Explicit test doubles
---------------------
- Forest declaration/readiness, payload availability and source validation.
  The double uses the real selected-source callback for all 13 synthetic HDAs;
  it distinguishes accepted density8 bytes from missing, invalid, altered RGB,
  altered alpha or density4 sources. This is a routing boundary, NOT a test of
  the real forest policy/sidecar parser or canonical source checksums.
- Lower/cap bundle readiness, source record inventory and world preflight/row
  context. The lower stub presents one synthetic record through the existing
  61-iteration production validation loop. It does NOT validate ground101's
  actual 61 records, phase arithmetic or world sampling.
- draw_asset_filtered and scene tracing are recorders. No pixels are rendered.
  They verify material/cap/forest arguments, coordinates, densities, source
  bytes, replacement bits, suppress cleanup, order and no-call fallback.

Coverage
--------
- All 13 exact slots, UINT_MAX and ID/layer/bank exclusions; 359/185 bounds.
- Every existing terrain mapping exercised and finite selector fingerprints
  (including player, enemy and explosion selection) frozen from pre-forest
  commit 75f4dcf5033c9e2455eaf96563aba606dac61c67.
- Existing lower/cap and scalar/fast world source files remain byte-identical
  to the pre-forest baseline, by stored SHA256 fingerprints. This is a selected
  source-scope check, not a whole-repository or asset-integrity attestation.
- Distinct source pointers with the same numeric ID; same pointer repeated;
  equal contents at unrelated pointers; first-match order for conflicting IDs.
- Unrelated registry overflow leaves forest live. Lost later repeated-ID
  pointer, null forest source or ambiguous forest association disables only
  the declared forest family. The same failed registry does not opt unmarked
  packs into coupled fallback. Capacity boundary, reset and one-ID subset maps.
- Real 213-registration engine loop preserves the first 185 sources, including
  forest pointer loss after earlier numeric nonforest IDs; no bitset shortcut.
- Declared success supplies all 13 forest records. Invalid declaration,
  unavailable payload (missing/invalid simulated), each of 13 missing/invalid/
  corrupt-RGB/corrupt-alpha/density4 sources, missing lower, failed lower source,
  failed preflight, missing frame context, unrelated row, terrain-only scope,
  indexed density and original-reference mode all keep declared forest indexed.
- All policy combinations preserve independent selected lower/cap art and,
  where eligible, their material/cap arguments, including mixed ordered rows.
- No declaration retains all supplied synthetic selected RGBA bytes: arbitrary
  custom, canonical-like, mixed, alpha127 and 4x fallback, even with missing
  lower/world context. A declared registry failure does not alter custom mode.
- Non-NORMAL forest styles skip before any asset initialization. Original row
  layout and world-context mismatch rejection remain exercised. 182 ordered
  full/partial forest rows cover bit masks, order, clipping-safe origins and
  draw failures without claiming the underlying rasterizer is exercised.
- Source assertions AND fresh-process runtime checks establish independent
  declaration detection before lower early returns.
- Seventeen negative-control mutations of extracted copies must be rejected:
  slot shift, lost-registration ignored, missing map reset, style leakage,
  declared fixed-base leakage, registry/row readiness bypass, omitted policy
  detection and wrong-layer binding; circuit slot/191/style/missing-art trace
  faults, old registry capacity, one-past registry bound, lost selected4 fallback,
  and pointer first-match corruption. No candidate file is mutated.

Circuit10 coverage (additive; prior forest regressions retained)
-------------------------------------------------------------
- Exact Layer3 shapesZ IDs 181,182,184,185,192,193,194,195,201,202 map to
  slots349..358. Exhaustive ID/layer checks and all256 bank values apply.
-191 is excluded even with a valid synthetic191 HDA present. Null pointers,
  same bytes at unrelated pointers, repeated-ID pointers, conflicting pointer
  aliases, wrong layers and every non-NORMAL style retain established routing.
- Every member gets missing and malformed8x tests, wrong bank/id/density/size/
  anchor headers, truncated payload and trailing bytes, absent8x/valid4x,
  invalid8x/valid4x, explicit density4 and arbitrary selected RGBA checks.
  A failed member does not disable its circuit neighbors or accepted gray art.
- All prior finite selector/loader fingerprints and lower/cap files retain
  their frozen pre-forest checks. No expected mapping hash was loosened.
- Capacity tests now check185 exactly:184 earlier sources plus the last
  accepted source; the186th distinct pointer must not register. Declared
  forest pointer loss still triggers only forest fallback. Reset recovers.
- The real engine loop still attempts213 source registrations. With71 cloud
  plus70 circuit/other Layer3 sources sorted before forest, exactly44 of72
  forest pointers fit185. The original175 fixture expected34; this expectation
  is updated to44, not removed. Another fixture puts200 nonforest sources
  before13 forest sources and still proves true forest loss.
- Circuit art remains independent of all forest policies, declared forest
  registry failure and lower/cap material state. Mixed circuit/gray/cloud rows
  check exact replacement bits, order, positions and draw-failure cleanup.
- HDA bytes are synthetic. Raster drawing, real material parsing and native
  gameplay/capture evidence remain outside this oracle.

Limits
------
This is an isolated binding/routing oracle, NOT pixel validation, art review,
canonical source/payload integrity, policy-file parsing, SDL integration,
gameplay/state/RNG testing, or full-game execution. Those need independent
checks. No game runs, screenshots, authored art changes, repository edits,
commits, pushes or publication are performed by these scripts.
