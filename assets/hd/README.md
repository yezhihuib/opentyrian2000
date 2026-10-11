# Accepted HD resources

The manifest is the finite accepted mapping. Final default packs contain150/154 HDR1 files. The three effect rollback stages contain47/51,95/99 and102/106 files. Shared resources have identical SHA256; no game data or captures are included.

source/*.png are exact RGBA dumps of accepted runtime payloads, with no resizing, color or alpha changes. Header keys, density, logical size and anchor are retained in manifest.json. These are production resource inputs, not screenshots. Regeneration must preserve those header fields.

Run `python prototype/build-hd-assets.py` to verify every source/header/runtime hash. Use `--output NEW_DIRECTORY` to rebuild exact packs from PNGs without overwriting originals.

Defaults and the three recent rollback selectors in start-actual-preview.ps1/start-asset-debug.ps1 use these repository packs. Earlier selectors still refer to preserved local legacy packs. Game data and local SDL SDKs remain separate prerequisites.
