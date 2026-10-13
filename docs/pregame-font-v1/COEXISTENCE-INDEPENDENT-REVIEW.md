# Independent pre-game / published-C coexistence review

2026-10-13 UTC. **PASS** for the narrow integration, subject to the sole integrator's publication decision.

Qualified published parent: `a35747a9b25a0e7a296165e802e0777a3aaee511`, tree `cc1f5da9feeea8d12407bd7e5a079981ef711d13`. Native-tested pre-game source: `c9232d59778c8689d85f9e87e8fee260b4c3187a` (production/unit implementation `bf301cb37d0fe619f1ca7bf90c23f8e3580874e7`). The final test bytes are recorded in `final-test-pins-before.txt` / `final-test-pins-after.txt` and remained unchanged through the independent reruns.

## Independently verified

- All 148 production files equal the native-tested pre-game source after reversing only C's exact eight ordered FNV constants and the adjacent contract comment. The existing finite validator rejects 194 altered constants, ordering, comment, other-byte and source-path cases. No production edit was added during coexistence work.
- The exact pre-game observer/test reversal qualifies all 7,499 files of the published parent. All 703,167,400 asset bytes equal published C, including B/C artwork. Source/assets path sets reject unlisted additions. All nine accepted startup/title/settings font resources are byte-identical to native-tested c9232d5.
- Independently rerun final pre-game source integration: 45 mutation rejections across 15 exact existing-file projections. Independently rerun coexistence: 194 production controls, 159 asset-byte mutations and 27 old-art reversions rejected. Independently rerun historical selector integration: PASS with nine original source-token projections.
- Historical selector/manual/Data bridges qualify the actual current C files before any idempotent legacy projection. Asset mutations invoke the same strict validator as current-tree qualification. Two early reviewer concerns about those details were corrected; no wildcard, arbitrary token stripping or expanded gameplay exception was introduced.
- The type15 preservation bridge retains its original finite C allowlist after exact pre-game reversal; the B/C unit baseline is the immutable native-tested c9232d5 source. Existing C eight-pin validation and negative-control logic are unchanged apart from the qualified baseline and explanatory text.
- Reviewed both forced Linux builds: `make -B -j4 WITH_NETWORK=false` and `make -B -j4`, each recompiling all 71 translation units, with the correct network define on every compile and matching SDL_net link flags. Both link successfully. The final default ELF matches its recorded SHA-256 `86919cbe3c474537234e74cf296fd58c06919251245c3ca262857b6ab9012bb7`; no-network recorded SHA-256 is `3205e7abcba2de6c66938bd4721f34641aecbc65cd3d47c7066fd66b823ecf49`. A post-link digest command initially used the wrong basename; its corrected receipt is explicit and this was not a compilation failure.
- Independent MSVC inventory check: all 71 C files listed exactly once; pregame_font.c and pregame_font.h each included once. No Windows compilation/runtime claim.
- The thirteen retained historical artwork blobs plus the unchanged remaining pack entries reconstruct the entire original native input manifest exactly. The frozen original manifest is byte-identical to the original collection manifest. Historical native acceptance documents and failed/corrected runtime evidence are preserved.

## Reviewed worker regression receipts

Pre-game ASan/UBSan: 78 states / 9,327,126 checks. Portable sampler: 33 cases / 28,246,374 checks. Existing selector 203 states, Settings 359 states, Load 832 draws; manual and Data suites pass. Type4 67 cases / 55 per-member rejection cases; type15 262 cases / 256 per-member rejection cases; original generated-source guard/preservation suites pass. These were inspected worker reruns, distinct from this reviewer's independently rerun projections above. LeakSanitizer remains disabled under the traced environment, as previously qualified.

## Scope and evidence

No new game launch or capture was performed for coexistence. The accepted seven-case / forty-capture typography matrix remains eight starts because the failed original R4 and its one reviewed correction are retained. It remains synthetic SDL input with Linux software/dummy output, no purchase, and no physical Windows evidence. Native same-index font/cube overlap is not claimed; positive overdraw coverage is the previously labeled synthetic source/core fixture. Exact byte correspondence carries that accepted text-only behavior onto C; it does not broaden root/category admission or introduce gameplay writes.

Review evidence is alongside this report: `production-and-inputs.json`, `final-source-integration.json`, `final-coexistence.json`, `final-selector-integration.json`, `forced-build-review.json`, `msvc-inventory.json`, and matching test pins/logs.
