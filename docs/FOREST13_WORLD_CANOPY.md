# Finite continuous forest canopy

This batch adds shapesZ Layer1 IDs **211,212,213,215,221,222,223,224,225,231,232,233,234**. Each fixed base is an opaque24×28 tile at density8, anchor0,0. Slots336–348 are finite; no other bank or layer is enabled.

One opaque768×896 canopy atlas has a **96×112 logical repeat period**. Thirteen canopy-only weights blend it over fixed silhouettes, front trunks and ground interfaces. It reduces the rejected24×28 clump rhythm; it is still periodic, not an infinite or random material. All original map, collision, RNG, scroll and indexed writes remain unchanged. Accepted69/66, lower-rock and warm-cap resources are unchanged.

## Runtime and fallback contract

The sampler reuses the existing saved Layer1 world transform, positive modulo and fast lookup tables. There is no additional phase table or per-frame allocation. Only NORMAL draws with valid current Layer1 context receive canopy material. Existing source density, logical size and anchors are checked before source bytes are accepted.

The default packs include a regular `forest13.policy` file containing exactly `forest13-coupled-original-v1` followed by a newline. A valid declaration requires the whole sidecar, all13 source HDAs, every attempted forest pointer registration and current world context. Any missing, malformed or incompatible required input disables all13 replacements coherently to original indexed forest. It does not reject the whole frame or disable other HD families.

A present-invalid declaration, including a link/reparse point or unreadable/non-regular entry, is conservative forest-only fallback. A genuinely absent declaration means ordinary selected-pack artwork, including normal per-asset density fallback. Removing the declaration opts out; there is no coupled-original guarantee after that removal. Directory names and source fingerprints do not infer policy. Selected files are immutable for a process lifetime, matching existing HDA caches.

All file sizes, dimensions, record IDs/order/offsets and ranges are checked before the one bounded allocation. The existing64-bit FNV convention detects accidental corruption; it is **not authentication**. Formal source and delivery receipts retain SHA256. The13 selected bases and atlas are opaque; an authored intermediate cutout intentionally contains transparency before composition onto generated grass.

Memory: the sidecar is3,311,804bytes, including3,311,616bytes of atlas/masks. Thirteen HDA RGBA caches add2,236,416bytes. Combined incremental image memory is about**5.29MiB**, plus small static metadata. Existing material buffers are reused, not copied.

## Bounded actual acceptance

The original no-injection private-survival replay runs0–4020. Normal foreground heavily obscures the first forest island. A separate private authoring build suppresses only Layer2/Layer3 row drawing while still executing their scroll/state updates; actors and UI remain. That toggle and capture hooks are excluded from production.

- Actual normal and isolated native2× stills at4020; isolated28 ordered frames3993–4020; native4× isolated4020.
- All4,021 state rows and original gameplay ledgers match the corresponding baseline.61 rendered warm-up/window frames are healthy in each replay.
- At4020,28,916 isolated and122 normal output pixels differ; every difference stays inside the17 forest tile rectangles. Outside pixels and HUD are exact.
- The open canopy patch is byte-identical across all28 frames after logged scroll compensation. No sliding, flashing join or trunk registration defect was found.
- Nine IDs have actual draw/visual context. **212,223,224,225 remain static-phase/source coverage only**. Actual visibility is further limited by retained actors.
- Full static proof covers208 tile phases,1,040 pair phases and2,733 assertions, including small2×2 and inward corners. Small2×2 wood is shallower than the original; this is disclosed in the accepted source review.215’s exceptional north edge intentionally begins canopy/shadow rather than grass.

These are bounded survival/authoring checks, not ordinary full-game forest coverage. Native4× output is1280×800; native2× is640×400. Cross-scale original state and internal density8 RGB are compared separately from same-scale pixels.

Three alternating baseline/candidate pairs measured median**+5.79% whole diagnostic elapsed**, range+3.07% to+7.14%. Each includes startup, indexed fast-forward,61 rendered frames and diagnostic logging. This is not an FPS measurement or isolated renderer benchmark.

## Reproduction and tests

`prototype/build-forest13-world-material.py` verifies the frozen generated-only package and builds the finite sidecar/index in a fresh external directory. `--verify-pack` checks the sidecar, regular declaration and all13 selected HDA hashes. The central `prototype/build-hd-assets.py` also verifies/reproduces both forest files in each default pack.

`prototype/tests/forest13/run_tests.py` checks malformed declarations, structural bounds, corruption, every missing/mismatched source and an independent scalar sampler oracle. The final suite covers484 loader cases and9,599,296 sampler pixels under ASan/UBSan. `prototype/tests/forest13-binding/run-oracle.py` checks extracted production routing/loader functions:34,417 assertions, seven processes and nine rejected negative-control mutations. Its draw/material stubs are not pixel evidence.

Linux production and private builds pass. LeakSanitizer is unavailable under this executor’s ptrace restrictions; ASan/UBSan and explicit allocation/free assertions run. Windows code is source-reviewed only. The material-module source-list gap identified during this batch is addressed by the subsequent Windows project maintenance. Windows compilation and execution remain unverified; see WINDOWS_HANDOFF.md.

The prior published checkpoint is75f4dcf5033c9e2455eaf96563aba606dac61c67. Formal source and compact receipts are retained; original game data, private survival/layer-isolation/capture hooks and test media are not repository content.
