# Accepted HD resources

The manifest is the finite accepted mapping and authoritative default-pack count. Run `python prototype/build-hd-assets.py` to report and verify the current pack, HDR1 and source PNG totals. Historical resource stages remain available as rollback packs; their older counts are not the current defaults. No original game data or runtime captures are included.

Recent scoped validation: `docs/GREEN_RENDER_VALIDATION.md`, `docs/ROTOR_ENEMY_VALIDATION.md`, `docs/GROUND_NINE_VALIDATION.md`, and `docs/ENEMY_ORB_VALIDATION.md`, and `docs/PLATEAU_FOUR_VALIDATION.md`. Each records its finite native-scene checks and remaining limitations. New artwork includes saved generated sources and deterministic registration/rebuild scripts in `artwork/`.

source/*.png are exact RGBA dumps of accepted runtime payloads, with no resizing, color or alpha changes. Header keys, density, logical size and anchor are retained in manifest.json. These are production resource inputs, not screenshots. Regeneration must preserve those header fields.

Run `python prototype/build-hd-assets.py` to verify every source/header/runtime hash. Use `--output NEW_DIRECTORY` to rebuild exact packs from PNGs without overwriting originals.

Defaults and the three recent rollback selectors in start-actual-preview.ps1/start-asset-debug.ps1 use these repository packs. Earlier selectors still refer to preserved local legacy packs. Game data and local SDL SDKs remain separate prerequisites.
