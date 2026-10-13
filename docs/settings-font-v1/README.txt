Settings-only SFN1 source candidate

Scope: setupMenu Setup, Graphics, Sound and their pickers. No load screen,
gameplay, title, shared font-table, indexed-render, input or configuration change.
Resources are optional. Put the three .hda files from canonical/ alongside the
existing startup resources passed with --startup-assets. Missing or invalid
families keep the entire settings epoch classic. Accepted output is exact
native nearest2x640x400 or nearest4x1280x800 with supported32-bit format;
filtered/aspect/transformed/foreign-owned presentations remain classic.

Frozen design receipt: independent review PASS, DESIGN.txt SHA256
6c6e5d44ba038dbcd8b03b2eda141cc3e23e8b0e575a9d22e291c331b71d009f.
Tiny fixed-role7 author approval is separate from runtime acceptance.
The implementation additionally pins the normal cursor's original source
newsh1.shp length29941/FNV8c478c429071f043, tiles273/274/292/293. It validates
clipped source event order with a168-event fixed scratch array; unrelated
same-index cursor-bracket writes are rejected. No original cursor bytes ship.

Reproduce source/core tests (requires SDL2 development files and original data):
  tests/run_settings_font_tests.sh ORIGINAL_DATA_DIR RESOURCE_DIR
  ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 \
    tests/run_settings_font_tests.sh --sanitize ORIGINAL_DATA_DIR RESOURCE_DIR
The test compiles actual original sprite/font/fonthand/bar/rectangle writers,
plus the scoped observers. It never executes setupMenu or the game loop.
A separate per-sample oracle decodes the original RLE independently and checks
ordered canonical4x and final correlated2x output. SDL lifecycle tests use only
a software renderer over a memory surface. No screenshots are generated.
LeakSanitizer is unavailable in the current ptrace executor; explicit allocator
instrumentation covers all four owned allocations and teardown balance.

Exporter: tools/export_settings_fonts.py --large LARGE_V2_DIR --repo REPO_DIR
--out OUTPUT_DIR. It requires frozen largeV2, mediumV3.1 and published tiny
canonical planes and independently checks their SHA256 identities. The SFN1
files contain authored coverage/roles only, never original game data.

The historical source checkpoint claims remain in SOURCE_TEST_REPORT.json.
Finished independent source review and actual paired acceptance now PASS within
the limits in ACCEPTANCE.txt/ACCEPTANCE.json. Use the new nine-file optional pack
assets/hd/packs/startup-title-settings-v1; all prior packs remain byte-exact.
