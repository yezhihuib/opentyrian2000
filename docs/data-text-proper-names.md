# Consistent Chinese Data names

Data titles, sender labels and stories use a single project glossary across all
five episodes. The glossary covers 213 names of people, places, organizations,
ships, species and named works or technologies. It is a project translation,
not a claim of official Chinese canon.

The reproducible inputs live in
`assets/data-text-zh-CN-v1/source-translations/`:

- `zh-CN-episode-1.json` through `zh-CN-episode-5.json`: all 149 original
  occurrence identities, naturally reflowed prose and all explicit empty originals.
- `glossary.json`: canonical English names, Chinese components, aliases,
  contextual distinctions and source occurrences.
- `remaining-latin-whitelist.json`: all 89 retained literal occurrences.
  This covers exact key combinations, serials, model identifiers, units and the
  unexplained damaged transmission and exact computer-song output. These literals must remain usable as given.

The approved concise project aliases are Ixmucane → 伊克斯 and Microsol → 米克罗.
Their compound names use the same components: 伊克斯阿尔法特遣队,
米克罗阿尔法超级舰队 and 米克罗研究控制中心. The glossary retains each
canonical English identity and the previous long Chinese form for traceability.
These aliases are project choices, not official Chinese names.

Transon Lohk is 特兰森·洛克 and Harble Wom is 哈布尔·沃姆 in formal
introductions and signatures. Ordinary dialogue uses 特兰森 and 哈布尔.
Trent Hawkins remains 特伦特·霍金斯, and Tyrian remains 泰瑞安. Display titles,
reader headings, portrait sender labels and bodies follow these same components.
Source spelling variants are documented in the glossary rather than silently
rewritten in the original English. The native English presentation remains
available with F6.

## Regenerate

From the repository root, with the documented font and build-time dependencies:

```sh
python scripts/export_data_font.py \
  --source assets/data-text-zh-CN-v1/source-catalog.json \
  --translations assets/data-text-zh-CN-v1/source-translations/zh-CN-episode-*.json \
  --out assets/data-text-zh-CN-v1 --preview
python scripts/export_data_text.py \
  --catalog assets/data-text-zh-CN-v1/source-catalog.json \
  --translations assets/data-text-zh-CN-v1/data-text-zh-CN-v1.json \
  --font assets/data-text-zh-CN-v1/data-text-zh-CN-v1.dzf \
  --output assets/data-text-zh-CN-v1/data-text-zh-CN-v1.dct \
  --pins src/data_text_pins.inc
python scripts/render_data_font_proof.py
python tests/test_data_text_names.py
```

The 1,905-glyph alpha atlas includes every scalar needed by all final titles,
sender labels and bodies. Noto Sans CJK SC Regular, the source font SHA256,
TTC face, rasterizer and SIL Open Font License remain pinned in the manifest and
font provenance. The existing body metrics are unchanged: 20px with 26px leading
at a native 1280x800 game viewport, and a 16px floor at 640x400.

Only the `.dct`, `.dzf`, optional gold EXIT `.hda` and required notices are runtime resources. Translation
inputs, glossary, literal whitelist and previews are development material.
Original game files are never modified. The normal source bindings and resource
pins apply to the updated resources, preserving English fallback when optional
resources are missing, incompatible or corrupt.
