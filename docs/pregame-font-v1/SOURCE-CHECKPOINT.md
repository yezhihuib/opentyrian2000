# Pre-game root and Upgrade category SFN1 typography

Source/core candidate based on published `317bf551db59df9c4e3754d2072446c7313ab1f4`. This checkpoint is not a Windows package or a native-game acceptance claim. No original or accepted HD art changes.

## Boundary

Only ordinary single-player `MENU_FULL_GAME` (0) and `MENU_UPGRADES` (1) acquire the lease. Network, arcade, two-player, SuperTyrian, timed battle and constant-play paths decline. Category selections are enhanced, but item/purchase contexts and weapon previews are outside this change. Inputs, sounds, choices, cash, equipment, save behavior and all original indexed drawing remain original source operations.

The explicit lifetime starts after the raw PIC1 restore, observes header, rows, cube icons, cash, bars, equipment illustration and footer in their original order, then retains that validated frame for idle/cursor presentations. It ends before ordinary actions, quick-load/save and nested help. The outgoing original ten-step F1 fade remains owned until its completion; return from Help reauthenticates the restored PIC1 and accepts the original black-to-PIC1 ten-step fade. Unrecognized work declines the complete enhancement, with fresh acquisition on a later verified restore.

## Source and pixel contracts

- PIC1/palette0 have independent runtime identities. Accepted SFN1 palette7 fields remain unchanged provenance. The large/medium/tiny SFN1 reader retains schema, file length/type, mapping, source metrics/RLE, eligibility, padding, payload and role checks.
- Menu/header strings (capacity18) and footer help strings (capacity66) are bounded snapshots of the loaded source arrays. Cash is the source decimal value. No translated or invented English allowlist.
- `JE_dString` is per-glyph destination-dark shadow followed by unsafe face, with selected `~` toggling brightness by2. Cash/footer use DARKEN's actual extra coordinate shift: face `(66,174)` / `(11,188)`, shadow `(67,175)` / `(12,189)`.
- Shadow is indexed `H(i)=(i&240)|((i&15)/2)`, then current-palette lookup. Unsafe face preserves the existing OR and overflow semantics. No RGB-half or clamped-face replacement.
- Original sprite banks5/6 and the shop compressed sheet are authenticated separately. Qualified original non-font operations retain ordered opaque indexed events. Opaque and dark writes clear authored coverage, including writes that repeat the same index. Unknown pixels/operators decline.
- The unchanged `selector_font_output` sampler consumes a premultiplied canonical layer over the original indexed underlay. It retains the accepted output-footprint mapping, aspect/odd-output behavior and classic cursor/filter neighborhood. This module adds no output-size whitelist.

The core has a fixed745,352-byte record and at most5,881,856 bytes of owned payload/output allocation on the tested64-bit host. A9MiB compile-time CPU budget includes all other finite font records and sampler staging; only one lease owns payloads. Commands and classic event counts do not accumulate during idle. Allocation failure falls classic. Inactive pregame teardown does not release the shared sampler.

## Reproducible source/core verification

Set `ORIGINAL_DATA_DIR` to a locally owned original Tyrian2000 data tree. Set `SFN1_RESOURCE_DIR` to `assets/hd/packs/startup-title-settings-v1`.

```
make -j4
python3 tests/test_pregame_font_integration.py
python3 tests/test_selector_font_integration.py
bash tests/run_pregame_font_tests.sh ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR
ASAN_OPTIONS=detect_leaks=0 bash tests/run_pregame_font_tests.sh --sanitize ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR
bash tests/run_selector_font_tests.sh ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR
bash tests/run_settings_font_tests.sh ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR
bash tests/run_load_font_tests.sh ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR
ASAN_OPTIONS=detect_leaks=0 bash tests/run_selector_font_output_tests.sh --sanitize
python3 prototype/test-manual-hd.py --out NEW_OUTPUT_DIRECTORY
python3 prototype/test-datacube-blend.py --data ORIGINAL_DATA_DIR --out NEW_OUTPUT_DIRECTORY
```

Manual/Data source units require a prior default network-enabled make build, because those historical drivers compile with `WITH_NETWORK`. ASan/UBSan can run here with LeakSanitizer disabled: this executor's traced process setup makes LeakSanitizer itself fail at exit. The core's own allocation accounting independently requires zero remaining owned allocations and tests each allocation failure.

The new core fixture draws all14 selections across cube counts0…4, bar remainders, real source sidekick tile families (including option13's283/284/302/303), and rear equipment. It compares exact original indexed images and ordered primitive traces with the inactive observer. It checks glyph coordinates/operators, source/resource corruption and bounded-string fallback, arbitrary-palette rejection, help fades, cursor restoration, idle reuse, output geometries and reacquisition. A longer bounded synthetic source string exercises real cube/authored overlap; a separately identified private primitive fixture proves same-index occlusion at authored support. These fixtures do not claim those synthetic values occurred in native gameplay.

`pregame_font_projection.py` reverses only the finite exact observer insertions to recover every byte of317bf55. Mutation tests reject unrelated changes. Historical selector/manual/Data assertions run on that exact projected source, retaining their earlier source/palette/art checks. Existing font implementations, selector sampler, original text functions, input/save/player code and all691,873,108 prior asset bytes remain exact. MSVC registers the new `.c` and `.h` once; no Windows compile, hardware-DPI or runtime claim follows from that inventory.

## Native acceptance still separate

Use a reviewed private copy of the successful selector transport and route. The bounded seven-process matrix covers paired2x/4x/odd output and missing-tiny fallback, with root2 → root3 → root4 → category2 → category9 → root4 → category9 → root4. Never activate an item category. Match cached natural-frame context, selected source strings, full palette, cash and semantic equipment fields to each capture. Every process gets fresh HOME/XDG/cwd; normal LAST LEVEL backup writes stay there. No user saves, production inspection callbacks, source pixel writes or game-state injection. Source/fixture review and the serialized runtime-slot release precede any game launch.
