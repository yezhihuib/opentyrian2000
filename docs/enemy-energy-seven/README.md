# Seven-direction enemy energy family

## Accepted finite result

The original bank8 IDs **77, 58, 182, 163, 1, 183, 164** now have one coherent warm-energy family in the enemy-shot role. These are seven static directions, not animation phases. Native 2× and 4× actual-engine comparisons at tick 7378 pass, including the fractional-alpha underlay and later original orb overlap. Source, unit, engineering and visual review receipts are retained here; raw logs, snapshots and reference pixels are external.

Runtime source: `f292a2cf59678a23b538f7ee6f7287cad68fa833`; test-only addition: `8adbbe6dbb2d72a4c229cb266191167aaaadbab0`; baseline: `e50fff31057ee08cca6c27bb7c56f4df06f28b5a`. Subsequent publication changes normalize provenance metadata and add these documents. They do not change runtime code or artwork pixels.

## Binding and original behavior

- Distinct resource role **111**, keys `1110000 + ID`, filenames `enemy-energy-{ID}-8.hda`, cache slots **462–468** in the order above.
- Exact 12×14 logical canvas, anchor (0,0), 96×112 straight RGBA. Each file is 43,036 bytes: HDR1, six little-endian u32 values `(1110000+ID,8,12,14,0,0)`, 43,008 payload bytes and EOF.
- Seven files enter each existing default pack, with seven canonical PNGs. All previous asset bytes and player paths remain unchanged. Player58 retains `bullet-58-8.hda`, role8/key80058/slot321. Enemy112/113 keeps its old branch and density fallback.
- The existing surviving enemy-shot hook retains exact original coordinates, state, update order, one indexed blit and one suppression reset. There is no rotation-to-velocity, new animation, shadow, trail, additive blend or gameplay provenance state.
- Full frozen RGBA stamps preflight all seven before any new-family replacement. Missing or corrupt any member disables only this family for the existing startup-selected cache lifetime. New-family resources are 8× only; density 1/4 stays classic. Native 2×/4× output uses the existing density8 presentation route.
- The new hook accepts the original 320×200, pitch320, 8-bit/one-byte target with `VGAScreen == game_screen`, x 0…308 and y −13…199. Physical-row wrapping or unsupported layout stays classic; ordinary partial vertical clipping is preserved.
- Fractional alpha and zero-alpha samples inside the old support are intentional. Coverage is zero outside the enlarged original RLE support. The unchanged ordered compositor preserves the real same-call underlay; indexed original writes still cover the original support.

## Source and unit verification

Frozen reconstruction is byte-exact. The aggregate validates 18 packs, 3,186 HDA entries and 489 referenced source PNGs; current defaults have 473 and 477 entries. The original source-preservation gate verifies 6,901 earlier files unchanged outside the five finite integration files and exact inverse restoration of those five.

Both defaults pass the extracted-production ASan/UBSan suite: **964 transactions per pack**, including 644 fallbacks, 176 player cases, 342 guards, 12,989,984 pixel/ownership comparisons, 62 full-frame checks and 393,216 exact alpha-operator cases. Every missing or changed member triggers coherent fallback. Player58 normal/shadow, the other shared player IDs, old112/113 and their density8→4 fallback remain isolated. The disabled build executes all nine original blits. This is a source unit, with explicitly reported font/material stubs and LeakSanitizer disabled.

Reproduce source-only checks with Python3, Pillow, NumPy and SciPy:

    python3 prototype/build-enemy-energy-seven-art.py
    python3 prototype/build-hd-assets.py

Run the unit with a fresh external output directory, an unchanged baseline checkout and separately supplied original game data:

    python3 prototype/test-enemy-energy-seven.py --out <new-external-directory> --baseline <e50fff3-checkout> --original-data <original-tyrian.shp>

The source-data and source-audit paths in the portable artwork metadata are logical provenance references. Original game data and original-source contact images are not shipped. The unchanged reconstruction recipe needs only its packaged generated master, masks and sprite registration; see [portable-provenance.json](portable-provenance.json).

## Actual tick7378 verification

Exactly **four** original replays ran from 0 through 7378: baseline/candidate at each native scale. They produced **four native captures and four indexed references**, all at 7378. Each lane has the same 7,379 state/index/RNG rows, 22,137 phase/event/RNG rows and original surviving-shot draw order. All four indexed BMP hashes are identical. The actual trial uses SDL dummy/software rendering and the existing symmetric private survival convention; it contains no seed restore or gameplay checkpoint.

For each candidate, seven actual before/after draw transactions verify **75,264 density8 RGB/ownership subpixels**, using the actual underlay. Original indexed writes match the baseline; all seven final directions have positive and fractional-alpha visible witnesses.

- 2×: 256,000 native-frame pixels compared; 1,132 original-support pixels verified in each lane; 1,125 changed pixels.
- 4×: 1,024,000 native-frame pixels compared; 4,528 original-support pixels verified in each lane; 4,497 changed pixels.
- Both pairs: zero mismatches, zero exclusions and zero tolerance. Full-frame changes remain within original support; complete support is checked in both lanes.

The first 2× final-pixel proof stopped on24 changed pixels because five unchanged enemy113 orb draws followed the seven new shots. The original FAIL remains in external evidence. A separate reviewed offline correction applies exactly those five observed normal-alpha operations, also explaining98 changed pixels at 4×. It checks both lanes including unchanged/obscured support pixels. No additional game run, capture, source change or exclusion was used. See [proof-correction-review.json](proof-correction-review.json), [pair-2x.json](pair-2x.json) and [pair-4x.json](pair-4x.json).

## Scope and remaining limits

- ID58 deliberately includes its declared shared enemy uses in weapons78/125/126. It remains up-facing even when the original shot travels sideways or down. Those alternate emitters have static/source-unit coverage; their direct first-level spawns are fire-dormant under the audited events. They were not newly exercised in this actual scene.
- Episode4/5 weapon81 adds leftward39. The approved seven-ID family leaves39 classic, as well as201/202. There is no whole later-episode or whole directional-player-family replacement claim.
- The actual trial has no player fire. Player/shadow/orb isolation and missing/corrupt fallback are established by the separate source/unit gate, not extra gameplay lanes.
- Author review passes the seven warm cores, tapered tails and smooth edges over boss material at 2×/4×. This one shot cluster does **not** establish bright-cloud or unobstructed-grass readability, motion or full-lifetime visual quality. Some source samples remain obscured by the original orbs.
- No physical-GPU, Windows, fullscreen, full-level performance, natural manual-play or full-campaign acceptance is claimed.

See [engineering-review.json](engineering-review.json) and [author-review.json](author-review.json) for the independent final reviews. [receipt-index.json](receipt-index.json) pins compact receipts and owner-scoped durable evidence backups. Historical source-review pending stages are superseded by these final reviews.
