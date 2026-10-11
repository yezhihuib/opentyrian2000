# Physical terrain underlay323/324/333/334

Four static shapesZ layer1 tiles now bind at slots237–240. Each is24×28, anchor(0,0), density8; arrangement323/324 above333/334 forms one fully opaque48×56 assembly. The exact14×300 layer1 map has three complete occurrences, top-left zero-based(row,col)(266,11),(277,11),(285,6). All4,200 map bytes were checked. This is distinct from the600-row cloud maps.

Original terrain contains its own dark steel/ochre structure and baked earth. The separately accepted enemy125–128 overlay starts one logical pixel lower. Original linked destruction reveals the already-present terrain; this change does not create a new damage entity, move the overlay, erase the metal into dirt, or change collision/effects. The four IDs use the existing ordered terrain path and missing/invalid gate. Capacity241 and registry104 reserve the independent road slots220–226 and235–236.

Four formal PNGs, the selected generated earth-corrected whole assembly, prompts and byte-exact exporter are included. Original game references, full-map imagery and captures are excluded. All prior assets remain byte-identical; default packs236/240,18 total packs,2712 HDA entries and248 unique PNGs. `python prototype/build-underlay-art.py --output <new-external-directory>` reproduces all four outputs without original data.

## Actual and technical checks

- Natural0–929 at native4×/2×, presentation132–929:2,688 new NORMAL/HD terrain calls per scale,672 per ID. All original state/RNG/indexed/material/collision/effect behavior and prior scene rows remain exact. Actual intact overlays at232/456/764 preserve placement and cloud/rotor foreground ordering.
- Supported artificial-shot diagnostic uses the original player-shot/collision functions, with no source hooks. Four nonlethal hits233–236 retain the original overlay; lethal shot238 removes the linked group by239. At281 both explosion pools are empty and the new persistent terrain structure is visible. Baseline/candidate native4×/2× captures show differences confined to the four terrain rectangles, with HUD and all outside pixels exact. Root and independent art review pass. This diagnostic is explicitly separate from natural player input.
- The88-frame real2× transition232–319 shows intact overlay, original hit/destruction effects and revealed terrain. Every lossless frame hash and noncapture state/RGB matches; no synthetic scrolling or ordinary BMP batch. The terrain intentionally differs after destruction, so final RGB equality there is not claimed.
- Missing all four at4× retains the prior final RGB and deterministic logs. Highest-detail processorType4 pair232–319 has352 new NORMAL/HD calls,88 per ID; original cloud BLEND fallback remains unchanged.
- Finite binder/loader ASan/UBSan oracle passes43,805 checks: exact IDs/layer/bank/slots, all header words, missing-all/each, payload rejection, reserved road slots, classic/disabled paths and prior ground/cloud mappings. Existing installation58,769,920-pixel, rotor101,573,120-pixel, orb46,024,704-pixel, ground/plateau, cloud/green ownership regressions and15 strict fixture tests pass. Formal PNG/HDA reproduction and production build pass.

## Boundaries and limits

All three source placements and15 external edge types/24 occurrences were audited, including7 road-edge types/10 occurrences. Road candidate context is independent and not included in this commit. Accepted sibling321/322/331/332 and all other ground are unchanged. Outside earth texture phases improve but are not pixel-identical at every boundary; no universal seamless claim. Right edges are partly cloud-obscured in the reveal view. Current first30-second coverage is finite; Windows/GPU/fullscreen/physical2K and whole-level performance remain unverified.

For later Windows acceptance, use the current manifest default_debug_pack and the installation commands in INSTALLATION_VALIDATION.md. Inspect intact targets232/456/764 at2x/4x. Use the existing asset-debug control file with hit29, hit30, hit31, hit32, step, destroy29, resume on separate newline-delimited lines to reproduce the labeled original-shot transition from232 through319; capture only a few requested frames.
