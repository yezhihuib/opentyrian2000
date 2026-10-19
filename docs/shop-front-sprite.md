# Optional shop front weapon

This local extension adds one independent optional PSP1 sibling to the accepted
Talon and natural root-menu typography: WEAPON table 6, zero-based shape 0,
33 × 34 logical pixels at the existing front anchor (61, 48), density 4.
This document records the front-only batch. Its fixed runtime list contained
OPTION31 Talon and this front shape; geometry never comes from a file. The
later independent generator extension is documented in `shop-generator-sprite.md`.

## Placement and fallback

The original draw observer must first see the full OPTION31 hull at (35, 33),
then one of the five authenticated original generator shapes at its exact
existing generator anchor, then shape 0 at the front anchor. Missing Talon art
does not prevent observing its original indexed draw. The front resource is
therefore independent of the hull resource. The later rear draw can reuse
shape 0 but cannot acquire this front replacement.

Other hulls, front shapes or anchors, trial pages, idle-tail redraws, Ship Specs
and foreign pages keep their existing paths. All original INDEX8 writes still
execute and are observed. Purchase calculations, equipment state, RNG, input,
logical coordinates, sprite blitters and gameplay are unchanged.

Each sprite command replays its own original RLE only for indexed validation
and later classic arithmetic. Its replacement composites over the existing HD
layer at the exact command position, without adding old sprite pixels to the
underlay. Partial alpha therefore accumulates across Talon and front artwork.
Later classic writes, including same-index writes, erase all 4 × 4 authored
samples of their own cell. Product classic/HD/classic boundaries and immutable
commands retained across idle updates use the same rules.

## Artwork and export

`assets/shop-front-v1/source-imagegen.png` retains OpenAI imagegen output
`exec-af83d411-da96-4062-9f42-61d53c38f630`, SHA256
`a8ffaf746ee2a81a62aaadcbd0f6c3b720165392c8a2d94d6279f4ed03692365`.
The fixed crop (27, 33, 1209, 1233) from the 1236 × 1273 source is resized
using Lanczos directly to 132 × 136 RGBA. Alpha below 8 and its RGB are zeroed.
The original silhouette is used only for validation, never clipping.
The exact runtime 3 × 3 logical-cell Chebyshev support guard admits all authored
samples; no bound is loosened for this resource.

Run `python3 scripts/export_shop_equipment.py --data ORIGINAL_DATA --part front`
to reproduce the PNG, HDA, JSON and fixed front payload pin. The optional
resource is `shop-front-weapon00-v1.hda` beside valid SFN1 resources in the
separate `--startup-assets` directory. The natural root-menu SMR1 resources can
be installed independently in that directory as well. No original game data
or selected gameplay pack is changed.

The existing 128-byte PSP1 header pins bank/index, logical and raster sizes,
anchor, density, channel/alpha mode, contour bound, source RLE/decoded-index/
support hashes, palette, PIC1 and approved RGBA payload hash. The front RLE,
index and support FNV1a values are `1a232f9fc3e904b2`, `db89c876a399ba93` and
`1ea87c3f611af9a4`; the straight-RGBA payload is 71,808 bytes, FNV1a
`d930cdf47ff0e77c`. Missing, malformed or allocation-failed front art disables
only this optional resource. Lease/reset behavior and the 11 MiB cap remain.

## Bounded verification

Use absolute resource-directory paths. The inherited core suite takes one
additional optional front-resource directory after the Talon directory:

    PREGAME_TEST_MAX_KIB=524288 tests/run_pregame_font_tests.sh DATA FONTS METAL TALON FRONT
    PREGAME_TEST_MAX_KIB=524288 tests/run_pregame_font_tests.sh --ubsan DATA FONTS METAL TALON FRONT

`tests/run_shop_menu_font_tests.sh DATA FRONT_WITH_MENU` checks coexistence with
the unchanged natural whole-run font resources. `tests/test_shop_front_boundary.py`
checks this finite source/asset delta against the accepted typography commit.
Historical frozen boundary fixtures remain unchanged and are not expanded into
blanket source or asset exemptions.

Plain and bounded UBSan core checks both pass 98 states / 11,374,552 checks.
Plain and UBSan natural-menu coexistence both pass 16 states / 411,591 checks.
The combined lease peaks at 8,067,050 owned heap bytes; static state is 809,480
bytes and the complete reserved budget is 10,748,578 bytes, below 11 MiB.

Seven bounded actual-engine software-SDL runs compare the accepted typography
baseline with this extension. Twenty paired INDEX8 frames and all recorded
cash, equipment, selection, rear-mode and RNG states are exact. Fourteen RGB
frames change only inside the original front rectangle; five trial frames and
the help frame are RGB-identical. Every paired right-menu region is pixel-
identical, and a native 1280 × 800 root capture preserves the natural menu.
Missing/corrupt front resources reproduce the baseline root exactly. A missing
Talon resource still permits the front replacement over the original hull.
Captures total 57,707,460 bytes, with 512 MiB address-space limits and a maximum
observed runtime RSS of 23,172 KiB.

Strict C99/pedantic warning-as-error compilation of the changed presenter and
the exact finite source/asset boundary pass. Normal production release build
also passes. Windows and GPU rendering, actual purchases and exhaustive later
inventories are outside this batch.
