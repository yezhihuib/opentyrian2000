# Shop product text

The optional pregame font presenter now covers ordinary single-player equipment
product pages as well as the existing shop root and category pages. It reuses the
accepted `settings-font-{large,medium,tiny}-v1.hda` SFN1 resources supplied through
`--startup-assets`. No new font or artwork is introduced.

Product titles use the original large-font metrics. Item names, Cost, remaining
cash and help use the original tiny DARKEN placement; simulator Power, upgrade and
downgrade amounts and rear-mode instructions use tiny face-only placement. The
original INDEX8 draws, palettes, purchase calculations, equipment changes, inputs
and simulation still run unchanged.

The product lease accepts categories 2–8 and up to five items plus Done, provided
all text fits the original screen and authenticated glyph coverage. Missing or
invalid fonts, unsupported glyphs/layouts, unexpected surface/palette changes,
unobserved writes and finite command/event exhaustion fall back to classic output.

Static title/list/help commands survive idle updates. Each idle update replaces
its dynamic simulator/cash tail. Contiguous classic writes are collapsed to the
last observed write per pixel only until the next font command; a later classic
write still occludes that text, even when it writes the same palette index.
Dynamic classic writes are confined to x < 154, y < 185, including the original
153 × 185 upgrade-interface sprite. All indexed writes are checked. Render replay
must also agree, apart from current Cash glyph ink where the original repeated
DARKEN call progressively darkens old indexed shadows. Scratch composition removes
the original font pixels without modifying the game surfaces.

## Verification

- Fresh strict Unix build of every C translation unit, including the HQ scaler
- Existing root/category core cases plus focused product cases in
  `run_pregame_font_tests.sh`, passed in plain and UBSan builds
- Bounded tests cover categories 2–8, selected/unselected and unaffordable shades,
  Power 1/11, long costs, shorter cash, rear-mode text, repeated ticks, classic
  writes before/after a text run, missing/corrupt fonts and fallback bounds
- `test_shop_product_font_integration.py` checks that the original menu lines
  remain unchanged and only observer calls were added
- Actual SDL software-renderer before/after runs at native 640 × 400: Front Gun
  Power 1 → 2 → 1, selecting Multi-Cannon, Done/help change, Ship Type, Rear Gun
  None/idle, and return to categories/root. Eleven INDEX8 frames and recorded
  cash/equipment/selection/mode/RNG states match; non-font output regions match
- One actual 1280 × 800 Front Gun output checks font edges

The Ship Type long name retains the original tight spacing against the owned-item
marker; no layout adjustment is included. Actual rear dual-mode equipment,
shield/generator/sidekick product pages, later inventories, Windows and GPU output
were not runtime-verified in this batch. Rear-mode switching and the other
category grammars have core coverage only. This is a text-only extension, not a
complete shop-art upgrade.
