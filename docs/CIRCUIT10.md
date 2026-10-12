# Finite Layer3 circuit/deck family

Ten shapesZ IDs181,182,184,185,192,193,194,195,201,202 replace the physically placed dark circuit/deck family. Intentional straight circuitry and distinct181/201 routing are preserved. Unplaced191 remains unbound. All images are opaque192×224, density8, logical24×28, anchor0,0.

The existing Layer3 NORMAL binder gains slots349–358; asset capacity is359 and the finite terrain-pointer registry is185. No new sampler, gameplay hook or map/RNG/collision change is introduced. Accepted gray terrain, sand, lower-rock, cap, canopy and all other HD inputs remain byte-exact. Non-NORMAL or wrong-layer calls retain existing routing. Missing/invalid individual art falls back through the existing selected-pack/original path without disabling unrelated art.

## Source reproduction

`assets/hd/artwork/circuit10-v1` is the immutable generated-only package. Its inventory SHA256 is a8b806d31062e3355449f1475bede7f6596ca643ac145a59542cbb3d575e0281. `python prototype/build-circuit10-art.py --output OUTPUT` requires a fresh external directory and verifies ten exact decoded RGBA/HDA outputs and canonical repository inputs. The author's numeric HDA filenames are mapped by exact bytes to the loader's `terrain-shapesz-ID-8.hda` names; headers are unchanged.

Two standalone builds, including relocation, reproduced all ten images and HDAs exactly. Canonical PNG encoding hashes are checked separately. Static review covers197 placements,252 adjacency types and1,244 occurrences. All28 active metal-facing pairs (187 occurrences) have exact RGB face joins; all24 accepted external tiles remain unchanged.

## Bounded actual verification

The matched private-survival replays preserve original scene layers, actors and controls. No weapon injection or layer suppression is used. The three retained native2× windows are4303–4330,4731–4758 and4933–4960:84 frames per side, not a continuous658-frame movie.

- All ten IDs are fully framed at least once. ID182's left edge is still partly covered by original foreground; complete geometry also has static source/adjacency proof.
- Every candidate frame was visually reviewed in chronological order. All168 decoded A/B readback hashes match. Every pixel difference is within actual circuit rectangles; HUD and all outside pixels are exact.
- State/RNG, map clock, material, collision/effect and original indexed blend proofs match the baseline. Wall-clock timing is excluded from deterministic comparisons.
- Native4×4320 (1280×800) and native2×4320 (640×400) have identical original state and internal density8 RGB audit. Native readback hashes are separately checked; cross-scale images are not asserted byte-identical.
- Missing all ten replacements reproduces baseline full ledgers and all28 internal8× RGB hashes exactly. Invalid182 removes only its HD draw while other scene commands and original state remain exact. That latter log-only test makes no spatial-pixel claim.
- An initial numeric-filename trial correctly fell back and was retained as a failed activation diagnostic. Canonical names fixed packaging only; no renderer behavior was changed to hide it.

These samples do not certify the whole later level. Existing original machinery/debris is outside the batch. Runtime source has private diagnostic hooks excluded from production; the private copy's older Windows S_ISREG guard differs textually, but UNIX-preprocessed forest code is exact to production.

## Engineering checks and limits

The portable extracted-production oracle passes479,985 assertions plus six forest fallback processes under ASan/UBSan. All17 negative-control mutations are rejected. It checks all ten IDs, forbidden191, banks/layers/styles, HDA validation, selected4× fallback, missing art, prior bindings, pointer ambiguity/reset and registry boundaries. Draw/material functions are test doubles, so these assertions do not substitute for actual pixel evidence. LeakSanitizer is unavailable under this executor's ptrace restrictions.

Final Linux build and Windows project XML/source-list checks pass. Windows compilation/runtime and CI are not claimed. The preview/debug packs now contain363/367 HDAs; all18 pack manifests,2,966 HDA entries,379 canonical PNGs and existing material sidecars verify. Raw game data, private hooks, full logs and captures are excluded from the repository. The previous published checkpoint a49e46e5f8880b98cfb41028b6389e97d0636433 remains the rollback reference.
