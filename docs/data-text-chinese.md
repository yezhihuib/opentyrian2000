# Optional Simplified Chinese Data text

Only Data cube titles, portrait headers and stories have a Chinese presentation.
Other menus stay English. The default is English.

- Open Data, then press F6 to switch English / 简体中文. The choice is saved
  immediately in `opentyrian.cfg`, section `data`, item `language` (`en` or `zh-CN`).
- Scroll Chinese with Up/Down, PageUp/PageDown, Home/End, the mouse wheel,
  the existing reader click areas, or joystick Up/Down. Chinese has a separate
  reading position; switching back retains the original English position.
- 中文使用说明：进入 Data 后按 F6 切换简体中文或英文，语言选择会自动保存。
  方向键、翻页键、Home/End 和鼠标滚轮可阅读完整内容。其他菜单保持英文。

## Reading size and layout

Chinese body type follows the actual game viewport, including renderer output
scaling and letterboxing. At a 1280x800 game viewport it uses 20px type and 26px
line spacing, fitting 16 full text rows without paragraph gaps. A 640x400
viewport keeps a readable 16px floor instead of halving the 1280 font to 10px.
The main reader header is approximately 24px at 1280 width.
The list and reader EXIT labels retain large gold menu type and a down-right
3D shadow in both languages. The bounded optional `data-exit-v1.hda` is derived
from the accepted shop menu DejaVu Sans Bold face, with its original gold palette
and list selection brightness. No separate button background is added.
Their original navigation and mouse hit regions stay unchanged.

Each original blank paragraph line contributes half a text line of space;
consecutive blank lines remain distinct. PageUp/PageDown use the content that
actually fits, including these gaps. End shows the complete final line, and
resizing keeps the same passage in view when possible.

The game aspect ratio is 8:5. A 1280x720 window in Fit 8:5 mode has a centered
1152x720 viewport (18px type, 24px line spacing); Integer mode instead uses a
centered 960x600 viewport (16px type, 22px line spacing). To use either window
height, choose a scaler whose minimum window size fits, such as 2x: the existing
4x scaler enforces a minimum 1280x800 window. These native scaler rules are
unchanged. English body layout and reading position are unchanged.

## Resources and fallback

The default directory is `assets/data-text-zh-CN-v1`; use
`--data-text-assets=/absolute/directory` to relocate it. Packaged launchers pass
an explicit absolute directory, including when the working directory is the
separate save profile. Runtime uses `data-text-zh-CN-v1.dct`, `data-text-zh-CN-v1.dzf`, and the optional
10.5 KiB `data-exit-v1.hda`, plus the accompanying font licenses and provenance.
A missing or invalid EXIT resource keeps the native gold lettering. Rebuild the
EXIT run with `python scripts/export_data_exit_font.py`; the DejaVu source font
and license remain under `assets/shop-menu-font-v1`.
Python, Pillow, fontTools and the full source font are build-time tools only.

The original encrypted `cubetxt1.dat` through `cubetxt5.dat` remain unchanged.
Exact whole-file and occurrence-byte FNV1a64 pins prevent applying a translation
to different game data. Source SHA256, byte ranges and translation identity are
retained in the development catalog. Occurrence numbers define identity:
Episode 5's last marker repeats `07`, but its identity is occurrence 12.
All 149 original occurrences are accounted for. Episode 4's first three slots
and Episode 5's final Todo body are empty in the original; no story is invented.

Missing, corrupt, oversized or incompatible optional resources preserve native
English. Different original story bytes disable the translation and retain the
native loader. Original game data remain required; the native behavior for a
missing or unreadable original game file is unchanged. UTF-8 is strictly checked
before layout; unknown glyphs, failed
layout and absent translations never replace a nonempty English story with an
empty view. A failed optional atlas also retains the local English F6 hint.
The native English loader, fixed text arrays and scrolling remain intact.
The new Data-local discovery hint is the intentional English-screen difference.

The overlay draws after the original game texture and before renderer readback.
It never writes Chinese into native INDEX8 text buffers. It is suspended outside
Data and before help; font textures are invalidated on renderer/texture recreation
and SDL device/target-reset events. Layout is bounded to 512 lines per selected
entry and retains every paragraph, including original empty paragraph slots.

## Rebuild

`scripts/export_data_font.py` verifies all 149 identities, source hashes,
explicit empty separators, emphasis, strict Unicode, cmap coverage and cell bounds. Feed
it `source-catalog.json` and translated episode JSON files (or the merged JSON),
using `--source`, `--translations`, and `--out`. The source font is Noto Sans CJK
SC Regular, face 2 of the documented Noto TTC; its source hash and OFL notice
are retained. Only the 1,905-glyph derived alpha atlas is shipped.

Then run `scripts/export_data_text.py --catalog CATALOG --translations MERGED`
`--font ATLAS --output TEXT.dct --pins src/data_text_pins.inc`. The exporter
requires every original occurrence and exact source/paragraph identity.
Runtime pins cover both complete resource files in addition to payload checks.

## Validation

`tests/run_data_text_tests.sh ORIGINAL_DATA_DIR RESOURCE_DIR NEW_CAPTURE_DIR`
checks all 149 entries, all nonempty bodies without scalar loss, four original
empty bodies, strict/malformed UTF-8, malformed/truncated font/text, glyph order,
source mismatch/missing resources, scrolling bounds, toggles, native-surface
immutability, four effective wrap widths, compact paragraph spacing, dynamic
paging, complete last-page bounds, cross-entry resize anchors, and offset/
letterboxed output rectangles. Actual SDL game checks cover 640x400, 1280x800,
and 1280x720 in both Fit 8:5 and Integer modes.
Set `SANITIZER_FLAGS='-fsanitize=undefined -fno-sanitize-recover=all'` for UBSan.

The Linux build and SDL software renderer are tested. The Visual C++ project
lists the new module; Windows runtime execution is a separate acceptance step.

## Consistent proper names

All five episodes use the same Chinese components for people, places,
organizations and ships, including titles and portrait sender labels.
The 213-name project glossary, exact translation inputs and retained literal
codes are described in [Consistent Chinese Data names](data-text-proper-names.md).

## Natural Chinese prose

All 149 entries have been rewritten and independently reviewed against the
original English for complete facts and straightforward, natural Chinese.
Paragraphs can be split or joined within a passage to improve reading. The
current text has 936 paragraph fields and preserves all 14 explicit empty
source separators, the three source placeholders and the final bodyless Todo
occurrence. All 213 glossary identities remain intact; the approved concise Chinese aliases
are documented above. The exact remaining Latin
literals, including source abbreviations and the computer song's original
output, are accounted for in the reviewed whitelist.

Transmissions use conversational Chinese. Reference entries, advertisements,
guides and songs retain their factual detail, distinct voices and jokes. The
computer song includes its exact original mixed-case output after the Chinese
line, without asserting it is a password. Other songs remain Chinese.
The five episode inputs, DCT text, complete glyph atlas and resource pins are
reproducible with the commands above. Default English, F6 switching, native
English positions, large gold EXIT, the HD frame, FACE7 portrait and compact
20px/26px Chinese reading metrics are unchanged.
