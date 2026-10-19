# Optional shop generator v9

This extension adds one independent PSP1 sibling to the accepted Talon hull,
Pulse front weapon and natural menu typography: WEAPON table 6, zero-based
shape 16, 31 × 35 logical pixels at the unchanged anchor (62, 84), density 4.
The fixed runtime list contains exactly those three sprite identities. Resource
headers never supply allocation geometry, source identity or draw placement.

## Ordered scope and independence

The observer first authenticates the original OPTION31 hull at (35, 33).
Generator16 can then replace its own original indexed draw at (62, 84), before
the front weapon. The original hull observer works even without the optional
Talon resource; the generator therefore loads and draws independently of both
Talon and Pulse resources. Missing, malformed or allocation-failed generator
art disables only that resource. Fonts are required by the existing lease;
metal, Talon, Pulse and natural root typography remain separately optional.

Other hulls, generator shapes, anchors, repeated equipment calls, rear reuse,
trial pages, Ship Specs, idle-tail writes and foreign pages retain their
original paths. No game-menu, sprite-blitter, gameplay, purchase, input, RNG,
equipment-state or logical-coordinate code changes are made. Every original
INDEX8 write and observer still executes. The existing replay-only original
sprite events and ordered continuous-alpha composition also apply to this
third command, preserving the real underlying HD hull. Later classic writes,
including same-index writes, clear their full 4 × 4 authored cell footprint.
Product classic/HD/classic boundaries and retained idle commands stay intact.

## Reproducible artwork

`assets/shop-generator-v1/source-imagegen.png` retains reviewed OpenAI imagegen
generator v9, SHA256
`da19e9514a9f5874f2366f8e1123588994aaea454d2b8c1b31e359fd30755206`.
The fixed whole-subject crop (0, 0, 1180, 1323) from the 1180 × 1333 source is
resized directly to 124 × 140 RGBA using Lanczos. Alpha below 8 and its RGB are
zeroed. The resulting PNG exactly matches the accepted candidate SHA256
`055fac0da3b71700e9616af36d78bd0664376a45bb81175f41057cea271218cc`.
It retains all 13,438 partial-alpha samples and 368 opaque samples. The
original binary silhouette is validation-only, never a clipping mask.

Run:

    python3 scripts/export_shop_generator.py --data ORIGINAL_DATA

This produces `shop-generator-weapon16-v1.hda`, its exact PNG, JSON manifest
and fixed `src/shop_generator_sprite_pins.h`. The unmodified three-by-three
logical-cell Chebyshev support guard admits every nonzero-alpha sample. The
PSP1 header pins source RLE/index/support FNV1a values `ef17480633ee6a68`,
`f4c1e126306f62fa`, `80b82cd8620511c6`; payload size is 69,440 bytes and
FNV1a is `8df7cb1657cdd101`. The complete resource SHA256 is
`1ea5097527e947be2d984fbbda94408af942d2c6bbd305a79e96873498c96756`.

Install this optional HDA beside valid SFN1 resources in the separate absolute
`--startup-assets` directory. No original game data or selected gameplay pack
is edited. Every header field, exact file length, regular-file type, payload,
transparent RGB and original source fingerprint is checked by the existing
loader. The unchanged end/reset path frees the new independent payload. The
complete reserved lease remains below the existing 11 MiB cap.

## Bounded verification

Use absolute resource-directory paths; each optional directory contains SFN1
resources plus the relevant previously accepted optional art:

    PREGAME_TEST_MAX_KIB=524288 tests/run_pregame_font_tests.sh DATA FONTS METAL TALON FRONT GENERATOR
    PREGAME_TEST_MAX_KIB=524288 tests/run_pregame_font_tests.sh --ubsan DATA FONTS METAL TALON FRONT GENERATOR
    PREGAME_TEST_MAX_KIB=524288 tests/run_shop_menu_font_tests.sh DATA GENERATOR_WITH_MENU
    PREGAME_TEST_MAX_KIB=524288 tests/run_shop_menu_font_tests.sh --ubsan DATA GENERATOR_WITH_MENU
    python3 tests/test_shop_generator_boundary.py

The finite generator boundary is based on the accepted front commit
`d97783b0ad24cce20d1cecfe0afc6890ac7943df`. Historical frozen font/front
boundary tests and fixtures remain byte-identical. It checks every other
production source and existing asset unchanged, with no projection imports,
external fixture reads or blanket exemptions.

Core coverage includes original write-trace/INDEX8 equality; root/category and
product selection; exact assembly command order; continuous per-sample alpha
accumulation and underlay oracles; same-index occlusion; later HD text; product
merge boundaries and retained idle updates; other hull/generator/anchor/rear
and repeated-call fallback; fades, cursor and reset; malformed headers,
truncation, extra bytes, payload corruption, directory/FIFO and allocation
failure; and valid generator surviving missing or corrupt hull/front siblings.

Actual-engine testing uses the established private SDL key-navigation route
against the accepted Talon+Pulse baseline. It covers root selections,
categories, front power and Multi-Cannon trials, Ship Type, Shield, help and
returns. Paired INDEX8 bytes and recorded equipment/cash/selection/rear-mode/
RNG states must remain exact. All RGB changes must remain in the original
generator rectangle; the entire fixed right-menu region must remain identical.
Missing/corrupt generator roots must reproduce baseline RGB. Separate actual
runs verify generator independence with Talon, Pulse or both absent and native
1280 × 800 output. Runtime address space is bounded to 512 MiB, builds to 1 GiB,
captures below 128 MiB, and disk free space remains at least 4 GiB.

Plain and bounded UBSan core suites both pass 121 states / 13,145,147 checks.
Plain and UBSan natural-menu coexistence both pass 16 states / 411,592 checks.
The combined lease peaks at 8,136,490 owned heap bytes; static state is 809,488
bytes. The full compile-time reservation including header allowance is
10,818,794 bytes, below 11 MiB. Strict C99/pedantic warning-as-error presenter
compilation, normal release build and exact finite source/asset boundary pass.

Twelve bounded actual-engine runs pass: twenty paired INDEX8 frames and all
recorded state/RNG lines are exact. Fourteen applicable RGB pairs change only
inside (124, 168)–(186, 238) at 640 × 400; five front-trial frames and help are
RGB-identical. All right-menu regions are pixel-identical, including the
paired native 1280 × 800 root. Missing/corrupt generator roots match baseline
RGB/INDEX8/state exactly. Actual hull-missing, front-missing and both-missing
pairs each retain generator-only RGB changes and exact INDEX8/state. Captures
total 67,707,474 bytes; maximum observed runtime RSS is 23,240 KiB under the
512 MiB address-space cap.

Windows/GPU rendering, actual purchases and exhaustive later inventories are
outside this bounded batch.
