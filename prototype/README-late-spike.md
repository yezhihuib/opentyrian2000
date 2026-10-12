# Late spike six-member finite append

Predecessor: 2efdc890217330e75a873252ca96b576495b23b9. Bank1/newsh2 bases1/3/5/7/9/11 map to types23/22/21/18/19/20. Six complete24×28 composites, anchor6,7, density8, occupy slots404–409. They form four separately linked, outward-moving rows of7/9/8/9 actors on links7/8/9/10, not one six-part game object.

The28-file frozen generated source package is retained unchanged under assets/hd/artwork/late-spike-v1. Manifest SHA256618dd16ebcecddb12bfe6fbfbd3d3327d9f03453ea965ee178026c6911ba564b; contract SHA2566e4ce3085bac59d7b9256b937e34ee5604f10f176b2a316d91d53d528d2489e2. Exact original RLE support totals1482 logical cells; all six distinct masks remain unchanged and transparentRGB is zero. No original RGB/index assets are included.

The original quadrant calls0/1/19/20 and every existing filter, coordinate, clipping, movement, collision, reward, effect and layer function remain unchanged. No terrain mapping or new namespace is added. One independent all-six readiness cache requires valid8x headers and complete frozenRGBA FNV stamps before any replacement. FNV detects accidental modification; SHA256 source receipts are authoritative. Missing/corrupt/wrong-density/allocation-failed resources cause coherent family-local classic fallback; no4x substitution. Existing type15, linked31 and newsh4 families remain independent.

Geometric fallback is separate from resource-family fallback. The original 12-pixel RLE blitter clips linear addresses, so a quadrant crossing a physical row can write onto a neighboring scanline. Only this family declines HD replacement unless the original target has the verified indexed layout (320 × 200, pitch 320, 8 bits and 1 byte per pixel) and quadrant x is 0 through 308 inclusive. The original blitter and ownership updates still execute once. A boundary-crossing quadrant remains classic while an adjacent safely in-row quadrant may remain HD; this is intentionally partial HD coverage at physical edges. The visible playfield boundary (source x 24 through 287) is not the physical row boundary. The original blitter, global clipping and all older family routes are unchanged.

Run source and binding checks using fresh output paths outside the checkout:

    python3 prototype/build-late-spike-art.py --output /tmp/late-spike-rebuilt
    python3 prototype/build-late-spike-art.py --output /tmp/late-spike-original --original-data /path/to/tyrian2000
    python3 prototype/test-late-spike-source-guards.py --out /tmp/late-spike-guards
    python3 prototype/test-late-spike-binding.py --out /tmp/late-spike-binding
    python3 prototype/test-late-spike-preservation.py --out /tmp/late-spike-preservation.json
    python3 prototype/build-hd-assets.py
    python3 prototype/tests/startup-manufacturer/test_package.py
    python3 prototype/tests/title-package/test_package.py
    make

Source completeness is not natural visibility: at stationary playerX100, base1 is entirely offscreen and base11 has at most28/294 projected opaque cells. Even legal camera extremes cannot show either cap in full. Actual shared discovery confirmed spawns 6506/6515/6526/6535, all 33 original actors and bounds removal through tick 6613. The separate unbound avail2 entry craft spawned at 6550 and its last allocation left at 6622. The original source has no alternate damaged/wreck image; hit/ice use original palette filters, ice does not stop motion, and each link dies independently. Revised source checkpoint 24fb535 passes the paired native 2× lifecycle at ticks 6541–6578: all 38 full frames reconstruct exactly, with zero excluded pixels or changes outside original alpha. Three guarded original Pulse155 requests at 6542/6544/6546 apply damage 1, ice code 99 and live-armor lethal damage 49 to unique slot 31. Exactly seven link-7 actors die, with 500 cash and seven kills; the other three links and later avail2 craft match no-pulse state. Original effects clear their pool after update 6571 and first present completely clean at 6572. Missing3, same-length corrupt3 and paired density4 actual controls reproduce classic fallback exactly.

Normal tick 6541 exposes complete instances of bases 3/5/7/9, with some upper-row original text overlap; base 11 is partial and base 1 has no geometric HD exposure. Original opposite-edge wrapped palette writes do not count as cap exposure. A true 1280×800 spot was executed at 6541 on the earlier source; the final boundary guard has a separately verified equivalent visible output, not a fresh revised 4× capture. The failed earlier candidate and its 288 suppressed original edge pixels are preserved in the diagnostic receipt; all are restored by the finite guard. Full source, runtime, author and capture pins are in docs/LATE_SPIKE_*.json. No ordinary survival, full-level, all-six-natural-visible, GPU or Windows runtime claim is made.
