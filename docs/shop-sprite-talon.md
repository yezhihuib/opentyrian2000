# Optional shop Talon hull

This local candidate replaces one large shop sprite: OPTION table 5, zero-based
index 31, the 85 × 112 Talon hull drawn at (35, 33). Ordinary single-player root,
upgrade-category, Ship Type and Shield pages can use it. In this hull-only
batch, other ships, weapons, generators, sidekicks, shield arcs, the trial
display and Ship Specs stayed on their existing paths. Later independent
equipment extensions are documented in `shop-front-sprite.md` and
`shop-generator-sprite.md`. Original INDEX8 draws and every observed write
still execute.
Purchase calculations, player state, inputs, RNG and logical coordinates are
unchanged. There are no game-menu, sprite-blitter or gameplay-mirror changes.

## Artwork and export

`assets/shop-talon-v1/source-imagegen.png` is the retained 1093 × 1439 transparent
OpenAI imagegen output `exec-33bfe602-3004-4c52-b55b-79ee48a8cdbd`, SHA256
`62b83ef444e0c767cb41f5d087d09f6f5e236533049a48f8f20c7b7347766476`.

The exporter crops only the transparent lower margin at (0, 0, 1093, 1390), then
uses Lanczos to map the original RGBA directly to 340 × 448. It globally clears
alpha below 8, including 1,427 nonzero near-transparent resampling samples, and
zeros RGB wherever alpha is zero. It never clips the artwork to the original
binary pixel silhouette. All retained authored alpha is within a one-logical-
pixel Chebyshev dilation of the authenticated original support. The exporter
checks this bound; the runtime independently checks it as well.

Reproduce with Pillow 12.3.0 and original external game data:

    python3 scripts/export_shop_sprite.py --data /absolute/original/data

The resulting straight-RGBA payload is 609,280 bytes, FNV1a
`3f8eb4a3ad911236`; the complete resource is 609,408 bytes, SHA256
`708c0421a5228c0bacc59873f62a4f44c5d2c8f3dc0a38526a765b2f661ca099`.
The JSON manifest records the crop, threshold, source and output checksums.
The exporter also updates the resource pins in `src/shop_talon_sprite_pins.h`.

Copy `shop-talon-option31-v1.hda` beside the three accepted SFN1 font resources
in a separate `--startup-assets` directory. Metal is optional and independent.
No selected gameplay pack or original game-data file is modified.

## PSP1 format

The 128-byte little-endian header begins with `PSP1`. Fifteen uint32 values at
offsets 4–60 are, in order: version 1, bank 5, index 31, logical width 85,
logical height 112, density 4, raster width 340, raster height 448, draw anchor
x 35, draw anchor y 33, payload bytes 609280, channels 4, straight-alpha mode 1,
original-support outward bound 1 logical pixel, reserved 0.

Eight uint64 values at offsets 64–120 are: original PIC1 FNV1a, palette0 RGB
FNV1a, original OPTION31 encoded RLE FNV1a, decoded index FNV1a, original
binary-support FNV1a, approved RGBA payload FNV1a, reserved 0 and reserved 0.
Decoded transparent indices are zero; binary support is 0 or 255. The RLE,
index and support fingerprints are respectively `1cdda2674a130af2`,
`46b339e8cc2fd434` and `cdbc751beacea75c`.

The payload immediately follows the header in tightly packed row-major straight
RGBA8. Every field, source fingerprint, approved payload hash, exact file length,
regular-file type, transparent RGB and support bound is checked. Allocation or
validation failure disables only this hull; fonts and valid metal remain active.
The existing pregame lease still requires valid SFN1 fonts. Resources are loaded
once per lease and freed on the existing end/reset path. The full bounded lease
budget remains 11 MiB; no extra framebuffer or output-sized allocation is added.

## Ordered composition

The existing OPTION blit begin/end observer brackets create one `C_SPRITE`
command while predicting and checking the exact original RLE write events.
The original indexed events update replay for validation and later classic
arithmetic. They do not overwrite the scratch underlay or erase lower HD art.
The new RGBA hull is composited at that exact command position. Its transparent
samples therefore expose the real pre-hull underlay, without any old hull ink.

Later original equipment, same-index writes and text retain their real ordering.
Every later classic event clears its complete 4 × 4 authored footprint, as
before. Product pages explicitly break the classic last-write merge on both
sides of the hull command. Idle updates retain the immutable hull command and
replace only their usual dynamic tail. The source hull's replaced writes do not
set the classic interpolation guard; later unreplaced writes still do.

The existing continuous premultiplied sampler is used when either metal or this
hull is actually drawn. It integrates reductions and reconstructs enlargements;
cursor/filter neighbourhoods retain the exact classic reference. Existing fade
gain affects RGB, with straight alpha retained throughout the ten-step fade.

## Verification

Run the original font and metal checks plus the optional sprite checks:

    PREGAME_TEST_MAX_KIB=524288 tests/run_pregame_font_tests.sh DATA SFN1_DIR METAL_DIR SPRITE_DIR
    PREGAME_TEST_MAX_KIB=524288 tests/run_pregame_font_tests.sh --ubsan DATA SFN1_DIR METAL_DIR SPRITE_DIR

Use absolute resource-directory paths. `SDL_CFLAGS` and `SDL_LIBS` can supply
local SDL headers and libraries when system pkg-config metadata is unavailable.
`PREGAME_SPRITE_CAPTURE_DIR` optionally saves bounded 640, 1280 and 2560-wide
actual SDL software-renderer readbacks from the core fixture.

Coverage includes original write-trace/INDEX8 equality; independent ordered
underlay and per-sample RGBA oracles; opaque same-index occlusion; later HD text;
actual product-pixel classic → hull → classic merge boundaries; retained product
commands across idle updates; other-ship and trial fallback; sprite without
metal; missing/corrupt/truncated/extra/directory/FIFO/allocation-failed resources;
valid metal surviving a corrupt hull; fades, cursor, reset and invalidation.
Synthetic markers exist only inside private test memory and are never exported
or used as substitute artwork.

Plain and bounded UBSan core runs pass (88 states / 10,768,455 checks, plus
three optional actual SDL screenshot states in the plain run). The bounded
lease peaks at 7,767,956 owned heap bytes; static state is 809,416 bytes.

Private paired actual-engine SDL key navigation against baseline `39fa56a`
covers 15 frames: root, categories, front Power 1 → 2 → 1, Multi-Cannon, Done,
Ship Type, Shield current/preview, return pages and F1 help/return. All 15
INDEX8 frames and all recorded cash, equipment, selection, rear-mode and RNG
states match exactly. The nine applicable page differences are confined to
the original 85 × 112 hull rectangle. All five trial frames and the help frame
are RGB-identical. Missing/corrupt hulls reproduce the baseline root RGB exactly.
A native 2560 × 1600 root readback also completes. These software-renderer runs
have a 512 MiB address-space limit and retain under 128 MiB of captures.

The modified presenter independently passes strict warning-as-error syntax
compilation. Normal production release build succeeds. A full-project strict
build without warning suppression is blocked by an existing unrelated
`asset_debug.c:161` misleading-indentation warning; that source is unchanged.
Actual purchases, Ship Specs navigation, later inventories, Windows and GPU
rendering are not covered by this bounded batch.
