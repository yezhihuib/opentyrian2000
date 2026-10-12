# Layer3 right mechanical assembly

Four shapesZ tiles (188, 189, 198, 199) replace one complete 48×56 logical mechanical assembly. The map has three complete placements. Original insert200, the separate left assembly and actor-linked debris remain outside this batch. Existing gray stone, canopy, lower material, HUD and other artwork are unchanged.

The finite Layer3 NORMAL binder uses slots359–362, with363 asset records and189 terrain-pointer records. Logical tile size24×28, density8 and anchor0,0 are unchanged. Tiles188/198 are opaque;189/199 retain their34 original transparent logical cells each. No new sampler, map, gameplay, collision, RNG or source draw-order change is introduced.

## Reproduction

`assets/hd/artwork/mechanical-right4-v1` retains the generated master, prompt, exact alpha support, selected outputs and standalone recipe. No original RGB is required to rebuild it. The optional mask audit documents its original-data hash without bundling game data. The integration omits the author's one-time local inventory constructor; `IMPORT.json` records the selected immutable files.

Run `python prototype/build-mechanical-right4-art.py --output NEW_OUTPUT` in a fresh directory outside the repository. The wrapper rejects existing, ancestor, nested-repository and symlink paths, then verifies exact canonical PNG/RGBA/HDR1 hashes for both selected packs. Independent and repository rebuilds pass, including an output path containing spaces. PNG encoder differences are distinguished from decoded RGBA; the selected canonical PNG hashes are pinned.

## Fresh bounded verification

The source baseline is published56efa261. Tests and runtime evidence were recreated after an execution-workspace replacement; unavailable earlier raw traces are not reused as proof.

- The complete original assembly is visible from ticks5625–5667. Fresh map/event/scroll validation covers90,911 ordered Layer3 source rows through5667. All three static placements are reviewed against accepted gray neighbors; insert200 is static-only here.
- A matched normal-layer private-survival sample covers28 frames5630–5657. All112 intended HD draws activate, all16 original state/RNG/clock/collision/material ledgers match, and original indexed blend results are exact. This fixture preserves original input and ordering; it is not a natural-survival claim.
- Every native2× pixel outside the original nonzero machinery mask is exact to baseline. At5640,10,448 pixels change inside that mask. Transparent cells preserve the underlying scene. The author and integrator inspected every target context in chronological order; no seam popping or registration drift was observed.
- A true1280×800 native4×5640 spot matches original state and internal density8 RGB audit of the640×400 sample. Native cross-scale images are not asserted identical.
- With all four assets absent, the same candidate reproduces all28 baseline native frame hashes and renderer/state ledgers exactly. With only189 malformed, the remaining three activate84 draws and original state/indexed results remain exact; this latter case is log-only.
- The source-extracted ASan/UBSan oracle passes707,489 assertions plus six forest fallback processes. It covers exact slots, bank/layer/style exclusions, malformed and missing assets, selected4× fallback, pointer identity/duplicates/capacity, existing mappings and family isolation. All21 deliberate negative-control mutations are rejected. Draw/material callbacks are test doubles, so this is not pixel evidence.
- Linux build and Windows project XML/source inventory checks pass. Windows compilation/runtime and whole-level coverage are not claimed. Private survival/readback hooks remain outside production.

Preflight caught a symlinked forest policy in the temporary candidate overlay before any run. Replacing it with the exact regular policy file preserved the accepted canopy. The final repository packs use regular files. The long brown actor visible behind the assembly remains original and is not part of this art acceptance.
