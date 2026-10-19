# Shop root whole-run typography v1

Optional DejaVu Sans Bold typography for exactly seven English labels on the
Game Menu root. Other menus, shared SFN1 resources, tiny text, cash and footer
remain unchanged. The original indexed text draw and its validation are retained.
Natural advances, bearings and descenders are rasterized as a whole run. There
is no per-glyph box fitting and no runtime FreeType dependency.

Install the seven `shop-menu-run0-v1.hda` through `shop-menu-run6-v1.hda` files
and `LICENSE-DejaVu.txt` into the existing `--startup-assets` directory alongside
the three `settings-font-*-v1.hda` files. Each run is independently optional;
missing, invalid or unallocatable files fall back to the existing SFN1 run.
The metal and Talon resources remain independent optional siblings.

Reproduce from this directory's unmodified font with:

    python3 scripts/export_shop_menu_font.py

The exporter pins Pillow 12.3.0, FreeType 2.14.3 and libraqm 0.10.5. It exports
1280×800-output-space alpha8/role8 planes and generated C metadata. The font,
complete Bitstream/Arev license, source provenance and JSON manifest are included.
The preview was reviewed at 640×400; the runtime retains palette-based gold,
selected pale gold, fades and the original (+2,+2) logical shadow arithmetic.

SMR1 files have a fixed 128-byte little-endian header. The loader pins each run's
identity, coordinates, dimensions, text and payload hash, rejects non-regular
files or extra/truncated bytes, validates alpha/role semantics and reserved
fields, and never parses arbitrary text or fonts. Total pixel payload: 227,286
bytes. Original graphics are neither input to the exporter nor redistributed.

Focused checks:

    bash tests/run_shop_menu_font_tests.sh ORIGINAL_DATA_DIR COMPLETE_STARTUP_DIR
    bash tests/run_shop_menu_font_tests.sh --ubsan ORIGINAL_DATA_DIR COMPLETE_STARTUP_DIR

These tests cover six selection states, 0/4 cubes, exact original INDEX8 writes,
ordered natural-run composition, same-index classic occlusion, cursors, fades,
category exclusion and independent loader corruption/allocation failures.
