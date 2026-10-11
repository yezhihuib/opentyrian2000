# Layer-3 gray island and type-40 turret

This bounded batch adds 18 shapesZ layer-3 terrain tiles and three newsh2 turret designs to checkpoint d351fe256e82216baa5281be552399ea1a276cca. The surrounding purple nine-piece installation and its special foundation remain original. This is not a complete 60–75-second HD milestone.

## Finite contracts

Gray IDs are 121, 122, 123, 124, 125, 131, 132, 133, 134, 135, 141, 142, 143, 144, 151, 152, 153 and 154, occupying slots 272–289. Each remains 24×28 with anchor (0,0), density 8 and the original layer-3 NORMAL draw order. The source loader now registers only these approved layer-3 pointers. Other layers, IDs and non-NORMAL styles retain their prior behavior. Missing or invalid new resources fall back without restoring a whole tile. No global alpha, cloud blend or shadow equation changes.

The registry has capacity 140. This map uses 78 pointers: 45 ground slots (including a duplicate ID 351), 15 cloud slots and 18 gray slots. Overflow preserves earlier entries and leaves later unregistered pointers on the original path. This is a bounded-map guarantee, not a claim about every possible map.

Type 40 uses newsh2 bases 153/155/157 in slots 269–271, each 24×28 with anchor (6,7). The original nine-step firing sequence remains 153,155,157,157,155,155,155,153,153. The three opaque designs share every pixel outside their 6×6 luminous core window. The backing is byte-identical to selected terrain 144. Original turret timing, enemy orbs 112/113, filters, independent removal and collision geometry remain unchanged. Terrain 153 and enemy 153 have separate source roles and caches.

## Selected art and rim revision

The gray family retains natural generated RGB rather than globally averaging reused boundaries. Twelve rim tiles use a half-logical-pixel occupied-side alpha transition. The final revision of 134/141/142/143 also rounds inherited near-black lower pads: dark RGB changes stay within 20 HD pixels of the free silhouette, and alpha recession stays below 8 HD pixels (one logical pixel). All original zero/nonzero support and each tile's outer two HD rows/columns remain exact. No new enclosed hole is introduced. The other 14 tiles, including fully opaque 144, are unchanged.

Original versus HD same-frame review established that the dark rectangular pads were inherited art, not a renderer ownership bug. The targeted revision reduces them without changing the renderer. Reused terrain texture phases and some edge differences remain; seamless whole-map equality is not claimed.

## Runtime and lifecycle checks

All runs replay from tick 0 with private survival and no injected weapon 71. Ordinary play ends at 1052. Private survival, read-only observers, control helpers and readback transport are excluded from production.

Paired baseline and candidate runs through tick 2679 match all 2,680 original state rows, 420,089 material rows and collision, RNG, projectile, pose, clock and effect logs. The 280 rendered frames at native 2× and 4× have identical logical RGB hashes and zero coverage, RGB-classic, restoration or rejection failures. There are 11,768 successful gray callbacks, 832 turret quadrants and 248 orb calls. All new gray draws are NORMAL. Four original nine-step firing cycles are measured unchanged.

ID 131 has no visible material rows in this interval. Its sole callback at tick 2679 is wholly above the viewport. Its complete source, resource and oracle checks plus 42 offline placements are accepted; visible runtime coverage is explicitly deferred.

Supported original Pulse155 controls at 2561 and 2563 hit the actual type-40 victim in slot 50, reducing armor 10→9 and then removing it. All nine independent purple components survive. Terrain 144 persists. The last explosion draws at 2580; clear intervals are 2581–2609 and 2617–2627, with an unrelated enemy-shot effect between them. A matched gray-only comparator differs only while the turret is visible, then is RGB-identical throughout 2564–2627. This comparator proof used the first gray selection; the four-tile rim revision preserves all turret/control callbacks and original state, without claiming an unrun final-revision gray-only comparison.

Processor-type-4 wild runs preserve original state, material, effects and blend before/source/after values. Clouds retain original BLEND fallback. Expected HD-ownership counts change only with added HD terrain.

The four-tile final revision preserves every other one of the 298 resources. Its scoped repeat passes state/material/effect/collision parity, 468 rendered-frame checks and 120 cross-scale RGB comparisons. Final actual evidence comprises 120 consecutive native 2× scrolling/firing frames, 68 original-hit/removal frames and the native 4× view at 2564. Every lossless frame matches direct SDL readback. Root and independent reviewers pass the rounded rim, stable turret body/core, foundation reveal and foreground order. No BMP capture batch was generated.

## Oracles and limits

ASan/UBSan checks include 301,188,958 binder/loader assertions, 287,886,969 original-row/compositor assertions, 17 prior suites, 15 preparation-unit cases and nine detected deliberate binder faults. Turret tests cover 1,013,760,000 pixel comparisons and 325,632 original-wrapper cases, including all 256 filters, 24 quadrant orders, missing quadrants/assets, malformed/null/wrong-bank inputs and exact nine-phase selection. Legacy harness capacity/whitelist updates retain their negative guards; four deliberate wrong-ID/bank/layer mutations are rejected. LeakSanitizer is disabled in this environment; ASan and UBSan remain enabled.

Final selected source and generated output are reproducible without original game RGB. Run the asset verifier and the two family regeneration scripts. Linux SDL software rendering is the actual target tested; Windows, physical 2K performance, alternate gameplay inputs and full-level acceptance remain outside scope. The original central purple structure and its complete hidden foundation are the next separate family.
