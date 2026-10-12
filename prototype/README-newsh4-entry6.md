# Newsh4 entry-craft six, bounded validation

Tested local predecessor: fe5f5d7922105dccf67bfe2648ac366c3031bc66. Published spike predecessor 305c43aae91f0a20cc4cd622fc0a99b1bb37a37c has the identical tree e1227fb4ca2f8fe95ae14fa6e614f7d5cdc62f87. Historical source/runtime receipts retain the actual tested IDs. This append binds only bank 2 / newsh4 full composites 81/83/85/119/121/123, namespace 102, slots 410–415. Each is 24×28 logical pixels, anchor (6, 7) and density 8. No raw-cell or boss 86/124 alias is installed; four shared raw cells 86/105/124/143 have zero original opacity.

The 35-file frozen V2 source package is retained unchanged under assets/hd/artwork/newsh4-entry6-v1. Manifest SHA256 96c59e764ab2456d51476ba00f0c27e423fa4758469c512791c95d1e4dd87f04. Exact original RLE support is 263/351/113/365/541/135 cells, totaling 1,768 before overlap. Draw order 123→81→83→85→119→121 and origins (48,24)/(0,0)/(24,0)/(48,0)/(0,24)/(24,24) preserve the 72×52 canvas and 24-pixel row stride. The 133 overlapping cells resolve to 1,635 union cells. Every piece samples the same registered selected V2 material; ordered rejoin is byte-exact. V1 and original RGB/index art inputs are excluded.

The renderer loads and validates every member before the first replacement, using the selected pack's 8× HDR1 identity, dimensions, anchors and full-RGBA FNV stamp. Any missing/corrupt/wrong-density/allocation-failed member keeps all six classic for the current Asset-cache lifetime. SHA256 package receipts remain the authoritative byte identity; FNV is a runtime accidental-corruption guard. Failure and success cache independently of late spikes, linked31, type15 and both other newsh4 families. The selected pack is startup-only; existing reload means a new process.

Geometry fallback is per original quadrant, separately from coherent resource fallback. Original 12×14 RLE writes use linear addresses and may wrap across a physical row. Entry HD is declined unless the target is indexed 320×200, pitch 320, 8 bits / 1 byte per pixel and the quadrant x is 0…308. This preserves the complete original boundary call instead of replacing it with geometric clipping. Calls with y outside −13…199 are also left classic before coordinate subtraction or density scaling; in-row quadrants outside this interval cannot write an inbounds indexed pixel. Every partial top/bottom clip stays eligible. No generic blitter, earlier family guard, original write, ownership path or gameplay function is changed.

Original event 18 sky actors remain independent. Source armor 0 constructs avail 2 / armor 255; normal damaging shot/ram paths do not apply. No new combat state, frame, shadow, turret, drop or six-linked health is introduced. In particular, preserve recycled scoreitem unchanged: the fresh observed state is false, but existing allocation can retain true. Binding must not depend on this field. Original zero-value collection and fixed newsh6:145 effect behavior stay untouched.

## Checks

Use fresh absolute external output paths:

    python3 prototype/build-newsh4-entry6-art.py --output /tmp/entry6-rebuilt
    python3 prototype/build-newsh4-entry6-art.py --output /tmp/entry6-original --original-data /path/to/tyrian2000
    python3 prototype/test-newsh4-entry6-source-guards.py --out /tmp/entry6-source-guards
    python3 prototype/test-newsh4-entry6-binding.py --out /tmp/entry6-binding --original-data /path/to/tyrian2000/newsh4.shp
    python3 prototype/test-newsh4-entry6-preservation.py --out /tmp/entry6-preservation.json
    python3 prototype/build-hd-assets.py
    python3 prototype/tests/startup-manufacturer/test_package.py
    python3 prototype/tests/title-package/test_package.py
    make

The binding recorder is a source/unit fixture. It must establish all six preflight orders, whole-family malformed/missing/allocation fallback, independent neighboring families, all four parts and 256 filters, exact layout/physical bounds/extreme coordinates and the exact previous bank/terrain mapping plus six routes. It is not a game or final-pixel capture.

## Observed source evidence and remaining gate

The existing paired6500–6624 private-survival no-fire census is reused; no second discovery run was made. It contains 150,000 all-100-slot phase rows identical between published 2efdc89 and spike-only ed10ce7 builds, with unchanged original state and material-reference streams. Entry spawned at 6550 in slots 0…5, source draw order 123/81/83/85/119/121, avail 2 / armor 255 and observed scoreitem 0. Top records 468–470 removed during sky update 6619; bottom 471–473 removed 6622. Material references for top 81/83/85 are 6550–6607 (228 each); bottom 119/121/123 are 6550–6611 (208 each), including empty quadrant rectangles.

Applying frozen original alpha to those actual reference coordinates confirms complete six-mask inbounds support 6574–6603 and last bottom opaque support 6610. All observed entry quadrant coordinates pass the new guard. At 6585 the whole craft origin is (135, 95), with 1,635 inbounds union cells and 133 self-overlap cells. This establishes source-aligned geometry, not final unoccluded RGB. Background 3 and later actors/effects/player/UI may occlude it.

Entry was unbound in the original shared discovery builds. The later approved paired actual validation used source checkpoint 7513d828 against tested local spike fe5f5d7, with identical private survival/observation/native-readback units, no forced enemy damage and no production gameplay edits. Fifteen native 2× frames were retained: 6550,6574,6582–6587,6607–6612,6623. A true native 4× readback at 6585 was also executed. All 4,864,000 paired frame pixels reconstruct exactly from the baseline plus frozen V2 art, original ordered overlap and later original operators, with zero mismatches, exclusions or outside-family differences. The original INSERT COIN glyph/shadow is explicitly accounted for at 6607–6609; 6611,6612 and6623 are completely baseline-identical with no residue.

All 6,625 original state rows and 150,000 all-100 phase rows match. Original avail 2 / armor 255 remains unchanged; top actors remove 6619 and bottom actors 6622. Finite actual missing 83 and same-length RGB-corrupt 83 controls match the baseline 8× image exactly, and candidate density 4 matches its density 4 baseline. All six entry HD routes are disabled together while prior callbacks and original references remain identical. These three fallback frame comparisons cover 768,000 additional pixels.

The updated production code is unchanged from tested 7513d828. Published 305c43a has exactly the tested predecessor tree, so no replay was performed solely for the equivalent parent identity. Runtime acceptance is bounded to this private stationary/no-fire player-survival setup and the stated native ticks. No natural survival, forced combat, full-level, hardware GPU or Windows runtime is claimed; source extreme-coordinate tests cover the mirror route, not execution of the unchanged classic blitter at INT_MIN/MAX.

Source/unit history is in docs/NEWSH4_ENTRY6_SOURCE_VALIDATION.json; shared original geometry is in docs/NEWSH4_ENTRY6_CENSUS_REUSE.json. Final actual acceptance, independent source/pixel reviews and 36 native-frame hashes are retained in docs/NEWSH4_ENTRY6_VALIDATION.json, docs/NEWSH4_ENTRY6_INDEPENDENT_SOURCE_REVIEW.json, docs/NEWSH4_ENTRY6_INDEPENDENT_PIXEL_REVIEW.json and docs/NEWSH4_ENTRY6_CAPTURE_HASHES.json. Source guards passed 244 controlled rejections; the sanitizer recorder passed 180 cases and 29,568 original-RLE comparisons. Both default packs preserve 228/232 prior bindings and add exactly six entry routes.
