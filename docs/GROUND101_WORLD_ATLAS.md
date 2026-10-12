# Finite Layer 1 world-material atlas

This optional material extension replaces the one-tile rock 101 repetition with an authored four-by-four-tile field. It covers the reviewed 41 terrain backings and 20 static-object backings. The 61 existing HDA files remain unchanged and remain the selected pack's fallback. Terrain 111 is an unchanged guard.

The earlier single-cell coordinated v2 material was rejected because its repeated diagonal pattern looked too regular. None of its baked outputs is used here. The new generated-only source package is `assets/hd/artwork/ground101-world-atlas-v1`.

## Rendering contract

The atlas is opaque 768×896 RGBA at density 8, or 96×112 logical pixels. It repeats at that larger period; this is not a nonrepeating or whole-level texture claim. Its source, masks and original compatible generated bases are frozen in the package contracts.

Layer 1's actual map-cell pointer and unclipped draw origin establish the world transform before any terrain draw. All eight rows are checked first. The renderer retains that transform for the actor pass, because original scroll globals advance between terrain and actor drawing. Atlas coordinates use signed positive modulo; clipping never restarts the material phase.

Only the finite Layer 1 terrain records and verified static actor type/bank/base/state combinations participate. Shared numerical IDs in other banks, pickups, independent movement, unsupported contexts and other layers keep their existing paths. Quad origins retain their original anchor and draw order. The actors' one-logical-row offset follows from actual positions, rather than an additional hard-coded shift.

Material RGB is composed before the existing hit filter. Original alpha, protected pixels, original indexed writes, filters, shadows, collisions, RNG, physics, TTL and ownership/restoration rules stay on their existing paths. The 119/120 cliff feet retain their three ordered integer blends: historical base with material; generated footer with that result; material with that result. They are not blended a second time over baked artwork.

## Optional bundle and fallback

The selected pack may contain `ground101-world-material.g101.0` and `.1`. The fixed parts are8,388,608 and7,998,204 bytes. In that order they reproduce the original16,386,812-byte verified stream exactly. This transport partition adds no compression or rendering change. The loader requires the complete finite bundle and compatible existing HDA base pixels before enabling any of the material family. Missing, malformed or incompatible inputs disable the entire extension. The renderer then uses the user's selected pack as before; it does not force a historical pack or claim that arbitrary custom-pack pixels equal 856a365.

The runtime 64-bit checksum detects accidental corruption only. It is not authentication. Exact counts, dimensions, identities, duplicate keys, record spans, integer bounds and file size are validated independently before allocation and activation. Formal source and bundle reproduction use SHA-256 manifests. No external cryptographic runtime library is required.

The additional fixed payload is 16,386,048 bytes, including the atlas, 61 historical bases and masks, and two generated footer inputs with four extra masks. Small frame-scoped lookup tables avoid per-pixel modulo work. There is no per-frame allocation, random variant choice, map edit or gameplay-pool increase.

## Bounded validation and limitations

The synthetic oracle checks negative coordinates, all tile phases, scrolling rollover, pointer jumps, quadrant clipping, frame reset, masks and ordered footer arithmetic. A repeated old-material atlas reconstructs all 61 historical recipe results and the 111 guard exactly; this is a reconstruction test, not renewed acceptance of the rejected v2 appearance.

Actual prototype evidence covers ordinary road 500–559 and six original-control/private-survival lifecycle windows: foundation and installation 232–287, rocks 1094–1121, intact stone 1378–1405, linked removal 1348–1407 and the later remnant 1940–1999. All 348 candidate frames have retained direct-SDL readback hashes. A paired native 4× spot at 510 supplements native 2× motion. Performance revisions must match the reviewed output before these images are used as final evidence.

The six lifecycle windows have independent chronological visual review. They preserve intentional damaged hardware/rubble underneath removed objects. The later remnant remains right-clipped: newshE 9/47 are partial and 11/49 are offscreen, so full six-component geometry there has static/source coverage rather than complete runtime visibility. Repeated large atlas motifs and some material transitions remain perceptible. This does not establish full-game, all-map-occurrence, Windows or CI acceptance.

Final build, loader, performance and merged-runtime results are recorded separately in the validation receipt. The frozen artwork package's own README describes its earlier handoff-time status and is intentionally not rewritten.

## Reproduction

Run `python prototype/build-ground101-world-material.py --verify` to check the
committed sidecar parts and C contract. For an independent authored-source rebuild,
use `--output ../NEW_EMPTY_DIRECTORY`. The wrapper verifies the immutable
source inventory, reconstructs atlas/footer pixels and emits the identical
bundle plus generated C header without original game data.

The standalone source tests live in `prototype/tests/world-material`; their
README documents compiler prerequisites and the cloud sanitizer limitation.
The optimized sampler reduced the measured diagnostic median from10.40s to8.84s
for the same56-frame process; the feature-off comparison was6.64s. This leaves
approximately33% overhead in that instrumented software-renderer harness.
Maximum complete child-process RSS during the final six-context matrix was
560,036KiB, including existing renderer buffers and asset caches; it is not the
incremental cost of the15.63MiB atlas payload.

The published packaging uses two bounded transport parts, required together.
Their ordered reconstruction retains the same full SHA-256 and runtime FNV64.
The loader checks both lengths and the fixed inventory before its single
allocation, then verifies the complete reconstructed stream before activation.
Missing, truncated, swapped, oversized, mixed or corrupted parts disable the
whole extension. Seven repeated log-only windows verify the same348 reviewed
outputs after this packaging change; no new visual capture was needed.
