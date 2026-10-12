# Coordinated matte sand material refresh

## Scope

21 existing Layer1 assets are replaced together: road13 IDs36/37/38/39/40/46/47/48/49/50/56/57/58 and grass-backed8 IDs66/67/76/78/79/80/89/90. Full-green69 is an unchanged guard. IDs, slots, headers,24×28 bounds, anchors and alpha are unchanged. No production source file changes; original shadows, foreground order, collision, RNG and gameplay remain unchanged. All317 other debug-pack assets are exact.

The selected matte sand reduces dense gravel highlights. Explicit generated-art masks protect346,583 road pixels and all accepted green and mixed-transition pixels.207,954 grass backing pixels are eligible;196,877 actually change.18,627 mixed grass pixels remain exact. These are conservative authored masks, not a claim that every decorative grain is semantically segmented. No global frame blur or alpha erosion is used.

Current totals remain18 packs and2,908 HDA entries, preview334/debug338. There are350 active canonical PNGs because four historical-stage sources remain in use alongside the new material. Historical sources are retained.

## Reproducibility

The immutable source package is `assets/hd/artwork/sand-road-grass21-v1`, inventory revision1 SHA256 d92297015681a78336e32acf2b75d46dea82986388f42ceeaa6c5ef3c72af87e. All133 listed files verify. Two independent standalone builds and the repository wrapper reproduce all22 PNG/RGBA/HDA outputs exactly, including69. Original game data is unnecessary. Fresh output, symlink and package-overlap guards pass.

Run `python prototype/build-sand-road-grass-art.py --output NEW_EXTERNAL_DIRECTORY` and `python prototype/build-hd-assets.py`.

The historical nine-road recipe still requires its original18 frozen neighbor inputs. `prototype/build-road-art.py` now reconstructs historical37/49/50/57 from retained generated baseline PNGs and headers, hash-checks those plus the other14 inputs, and supplies a fresh external historical base. The original recipe and expected hashes are unchanged. Its nine historical PNG/RGBA/HDA outputs reproduce exactly after this refresh.

## Bounded runtime acceptance

Matched current-code baseline/candidate runs cover ordinary road ticks500–619 and private-survival grass-tail ticks3480–3599 at2×/4×. Road missing-pack and processor4 pairs are also checked. Twelve runs total1,440 renderer frames. All six matched pairs preserve25 retained deterministic TSVs; only expected HD RGB and control wall-clock fields differ. Missing-pack RGB is exact. Wild processor4 verifies3,200,181 restored classic-block checks. Grass2×/4× each preserve32,099 normalized indexed blend writes. New blend logs use the reviewed streaming whole/per-tick proof mechanism rather than retaining bulk TSV copies. Raw candidate blend rows are not replayable; this limitation is explicit in the machine report.

Four actual native2× lossless streams provide120 frames per side in each scene. Two additional native4× stills check510/3490. All240 candidate frames were visually inspected in chronological order and passed; all480 baseline/candidate frame hashes match, and every A/B difference stays inside the21 terrain rectangles. This is sequential frame inspection, not a separate real-time playback claim. Every video frame is actual SDL readback and losslessly round-trips to its recorded hash. The grass tail uses only the previously documented env-gated private-survival fixture; it is not an ordinary-life continuation. No weapon injection or hit controls are used. Unrelated original later enemies remain visible and outside scope.

A120-frame production-binary smoke matches the private road candidate's all26 retained deterministic TSVs, including state, collisions, effects, RGB, draw commands and frame ledger. All338 tested-pack assets equal the formally imported debug pack. Private readback/survival hooks are not committed.

The two presentation windows exercise20 of21 revised IDs. Road38 has static and reproducibility coverage but was absent from these windowed draws; no in-game visual claim is made for38.

Static whole-map review covers363 road and26 non69 grass placements,855 cardinal and869 diagonal contacts, including all five79 reuses. This does not imply every such placement was visually tested in-game. Existing brown101 stone, plateau, clouds and gray islands are outside this material revision; minor texture-phase differences elsewhere remain. No whole-game or Windows acceptance is claimed.

Final independent runtime and ordered-motion review receipts are recorded in `SAND_ROAD_GRASS_VALIDATION.json`.
