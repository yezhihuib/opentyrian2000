# Layer3 static round inserts 190/200

Exactly two shapesZ tiles, 190 and 200, append slots 367/368 to the existing finite Layer3 NORMAL mechanical binder. Right-four slots 359–362 and left-four slots 363–366 stay unchanged. Asset capacity is 369 and the source-pointer registry is 195. Each new tile remains 24×28 logical pixels, density 8, anchor 0,0, with exact original fully opaque alpha. The two independently generated designs preserve their separate projections; neither is a mirrored copy of the other.

Only the two manifest-selected default packs gain the two PNG/HDR1 assets. Previous artwork, selected material/HUD sidecars, gameplay, map data, collision, RNG, source registration order and draw order remain unchanged. Renderer changes only append the two finite IDs and raise the two fixed bounds; there is no new sampler, compositor, animation or actor behavior.

## Frozen source and reproduction

`assets/hd/artwork/mechanical-round-inserts-v1` contains two generated masters and prompts, the finite contract, input/output hashes, source-index/opacity and unchanged-neighbor proofs, seven offline-context receipts, standalone recipe and selected outputs. `IMPORT.json` pins every imported file. No original RGB or game data is bundled or needed for artwork reconstruction.

Run `python prototype/build-mechanical-round-inserts-art.py --output NEW_OUTPUT` into a fresh directory outside the repository. Add `--original-data PATH_TO_SHAPESZ_DAT` for the optional local exact source-index/opacity audit. The wrapper checks the complete imported file inventory, canonical PNG bytes as well as decoded RGBA/HDR1, every accepted neighbor hash, both selected packs and finite manifest scope. Existing, ancestor, nested-repository and symlink output paths are rejected. The canonical PNG encoding was produced with Pillow 12.3.0.

Prior right-four and left-four wrappers still rebuild the original eight outputs exactly. The live left-four wrapper recognizes the separately declared round-insert family; the historical left-four masters, contracts, source proofs and excluded190 provenance are unchanged.

## Source-stage checks

The baseline is 8227affc09edf11499885b896338f5318be3d424. Both standalone sprites and all seven offline source contexts were approved before integration: 190 at 276,11; 279,11; 290,11; 322,12, and 200 at 260,3; 261,3; 293,4. The vertically adjacent 200 placements were checked together. Offline context receipts record zero changed tiles outside the pair.

The source-extracted ASan/UBSan binder oracle passes seven process modes and 1,056,583 assertions. It covers exact slots, bank/layer/style exclusions, each missing or malformed member, the jointly absent/invalid pair, selected 4× fallback, exact selected bytes, pointer identity/order, registry boundaries and existing-family isolation. All 29 deliberate renderer mutations are rejected. Its draw/material/font callbacks are test doubles, so these are routing checks, not pixel evidence.

Exact pair PNG/RGBA/HDR1 reconstruction, both original source-index hashes and 672/672 occupied cells per tile pass. All eight previous mechanical PNG/HDR1 rebuilds remain byte-exact. Ten source-negative controls and five output-path guards reject invalid inputs. The full asset verifier checks 18 packs, 2,986 HDR1 entries, 389 canonical PNGs and all existing material/HUD sidecars; selected pack counts are 373/377. Linux compilation and Windows project XML/source-inventory checks pass. No Windows compilation or runtime is claimed.

## Bounded actual normal-layer acceptance

All 24 matched native2× frames5858–5881 pass. Both IDs appear once per frame,
48 replacement draws total. Every changed pixel stays inside their combined
5,376-pixel original opaque support; the rest of the scene and HUD are exact.
The two registered motif templates remain identical throughout scrolling.
The actual normal still is5868; true4×5868 independently preserves original
state/indexed output and the same internal8× RGB hash as the2× run. This is not
a claim that differently sized native output images are byte-identical.

All16 compared original ledgers, RNG, indexed output, source/event/scroll clocks
and indexed blend proofs match. The private min2 survival/readback fixture keeps
original layers and fixed-player/no-fire behavior; it is not natural manual play
and none of its hooks is included in production.

Missing both files produces complete baseline-equivalent HD output in the24
selected ticks. A corrupt190 header fails closed locally while200 retains all24
draws. Fallback tests save no native media. Five game processes total cover the
matched window,4×spot and two failures; no blind discovery or extra long capture
was needed. Source, executable, packs and original data were pinned before and
after every run and remained exact.

Root and author inspected native2×/4×; author reviewed all24 frames and verified
their decoded readback hashes. Actual exposure is one placement per ID:190 at
map290,11 and200 at293,4. The other five placements and200's vertical self-repeat
remain independently checked offline contexts, not additional gameplay views.
The exact outside-support pixel proof is native2×; internal8× evidence is full
frame/cross-scale hash parity. Windows runtime and full-level acceptance remain
outstanding. See `MECHANICAL_ROUND_INSERTS_VALIDATION.json` for exact proof pins.
