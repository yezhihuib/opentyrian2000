# Accepted HD resources

Normal Sonic Wave now has all 21 smooth head identities, including the final
four independently positioned green-energy quadrants 105/106/124/125. Prior 17
resources stay unchanged. The quartet also reuses its frozen alpha for guarded
smooth shadows; excluded contexts retain classic drawing. See [finite artwork,
source guards and controlled P7/P11 validation](../../docs/sonic-quadrants.md).
The remaining17 Sonic shadows and shared player-owned Mint27 shadow also reuse
their unchanged accepted head alpha under finite source/resource/mode guards.
See [scope and bounded validation](../../docs/sonic-mint-shadows.md).
Missile31–33, Charge252–254 and green214–217 also reuse their unchanged head
alpha for guarded smooth shadows. See [finite scope and validation](../../docs/ten-weapon-shadows.md).

The manifest is the finite accepted mapping and authoritative default-pack count. `packs` contains only the two installed defaults (629 HDR1 files each); `optional_packs` separately catalogs all 35 images across the fifteen ASTEROID1 opt-in families. `python prototype/build-hd-assets.py --catalog-only` verifies their explicit source PNG, header and runtime byte pins without rebuilding artwork. Missing historical resources are a failure, not a partial pass. Run `python prototype/build-hd-assets.py` to report and verify the current pack, HDR1 and source PNG totals. The two installed gameplay defaults retain their head-v1 directories. The 16 superseded gameplay stage packs and three duplicate startup subset directories have been retired; their recipes, sources and Git history remain available. Historical counts describe their original checkpoints. See [retired packs, recovery and external rebuilds](../../docs/RETIRED_HD_PACKS.md). No original game data or runtime captures are included.

Recent scoped validation: `docs/GREEN_RENDER_VALIDATION.md`, `docs/ROTOR_ENEMY_VALIDATION.md`, `docs/GROUND_NINE_VALIDATION.md`, and `docs/ENEMY_ORB_VALIDATION.md`, and `docs/PLATEAU_FOUR_VALIDATION.md`. Each records its finite native-scene checks and remaining limitations. New artwork includes saved generated sources and deterministic registration/rebuild scripts in `artwork/`.

source/*.png are exact RGBA dumps of accepted runtime payloads, with no resizing, color or alpha changes. Header keys, density, logical size and anchor are retained in manifest.json. These are production resource inputs, not screenshots. Regeneration must preserve those header fields.

Run `python prototype/build-hd-assets.py` to verify the active source/header/runtime hashes and the complete retained startup pack. Use `--output NEW_DIRECTORY` to rebuild the active packs from PNGs without overwriting originals. Historical gameplay recipes are retained separately in `manifest.json` under `retired_packs`; rebuild one externally with `python3 prototype/rebuild_retired_hd_pack.py PACK --output ABS_NEW_EXTERNAL_DIRECTORY`.

The default `start-actual-preview.ps1` and `start-asset-debug.ps1` paths still use their respective installed head-v1 packs. Their eight superseded in-repository stage switches now stop with a retirement message. Older selectors for external `runtime-hd-assets` checkpoints remain available only when those separately managed local inputs exist. Game data and local SDL SDKs remain separate prerequisites.

Static physical installation125–128: [validation](../../docs/INSTALLATION_VALIDATION.md), including the separate pending original-underlay strip.

Physical terrain underlay323/324/333/334: [validation](../../docs/UNDERLAY_VALIDATION.md), preserving original linked-object reveal behavior.

Complete13-member road family with9 additive/revised tiles: [validation](../../docs/ROAD_NINE_VALIDATION.md).

Layer-3 gray island and type-40 turret: [validation](../../docs/GRAY_ISLAND_TURRET_VALIDATION.md), including selected rim revision and original component-local reveal.

Seven enemy-role directional energy sprites: [finite source, unit and actual 2×/4× validation](../../docs/enemy-energy-seven/README.md). Separate role111 preserves player58 and the existing112/113 orbs; shared-enemy and later-episode limits are explicit.
