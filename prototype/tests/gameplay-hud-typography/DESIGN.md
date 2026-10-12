# Gameplay typography: staged design, synthetic evidence only

Base: published `f82630507ab7f405117dc84ca70095ca04dc470a`.
Stage1 HUT1 implementation is in progress; Stage2 has no production hooks.
The isolated sparse worktree contains source/tests, not the published asset pack.
Root/artist approved and froze HUT1 and HUF1 art; Stage2 protocol review is still required.

## Stage1: exact baked370

The fixed MODE/SHIELD/ARMOR labels are independent of the dynamic atlas. Proposed
optional filename `gameplay-hud-fixed-text-v1.hda`, magic HUT1, exactly23744 bytes:
64-byte little-endian `<4s7I4Q>` header and23680 opaqueRGBA8 bytes.

| Offset | Field | Required value |
| --- | --- | --- |
| 0 | magic | HUT1 |
| 4 | version | 1 |
| 8 | authored density | 4 |
| 12 | tile count | 12 |
| 16 | logical cells | 370 |
| 20 | payload bytes | 23680 |
| 24 | fixed layout ID | 1 |
| 28 | reserved | 0 |
| 32 | original PIC3 FNV1a64 | 14c1441f3d5dc0e2 |
| 40 | normal palette RGB FNV1a64 | 5e80e83992be2927 |
| 48 | selected370 source-index FNV1a64 | b110512dd1fc63f4 |
| 56 | opaque RGBA payload FNV1a64 | a2433de596bd3873 |

Tile order is MODE76x20 at logical[284,54,303,59), then six20x20 SHIELD
letters at[285,138+6*i,290,143+6*i), then five20x20 ARMOR letters at
[296,138+6*i,301,143+6*i). Source370 checksum serializes those same logical
rectangles row-major in tile order. Its SHA256 is
272f2995359bd118dd62cb3b597ad937034527a25180115b399f8978777c59f6.
No coordinates, masks, alpha holes, extra tiles or original source pixels are
shipped. Density8 repeats4x texels2x. The one-row letter gaps are excluded.

The Stage1 binding uses an independent bounded loader and persistent PIC3 lease,
retain only runtime-captured370 expected indices, require source/palette/whole-word
or whole-column matching, and participate in existing reset/suspend/fade ownership.
The exact370 footprint is disjoint from HUD1/HUC1/HUL1, so it needs no new overlap
underlay system. Missing/corrupt/unsupported fixed text must leave other components
eligible. The resource is23744bytes, SHA2566d096f31085b22fb381761d3c8460bd06956c2bd039a1e0cc97481bc09819745.

## Stage2: dynamic text protocol is still under review

Initial audited gameplay streams:
- Persistent level name: HUD(268,118), TINY_FONT2, bank12,value4, actual setup draw
- Persistent bottom message: HUD(20,190), TINY_FONT2, bank0,value4, actual message
  draw/erase events and100 eligible HUD ticks; expiry pauses during endLevel
- Per-frame cash: scene(30,175), ordinary output(6,175), TINY_FONT2, bank2,value4,
  FULL_SHADE. Record the actual `%lu` text, not a later global cash value
- Per-frame single-player arcade name: original conditional path, bank2,value6,
  FULL_SHADE and original allocated metrics

Other palettes/modes, lives digits, timer fonts, warnings, diagnostics, shop/menu,
help, pause and results are distinct audited users and remain outside the initial
atlas bind unless their individual scope is approved. Style consistency does not
change their original color role. No global font-table or generic font API swap.

The dynamic resource proposal and exact bounded transaction are in
DYNAMIC_PROTOCOL.md. Root approved reviewedASCII as authored role7; extended
accented runs remain classic. The separate frozen resource is documented in DYNAMIC_PROTOCOL.md; production hooks await protocol approval. A bounded glyph table must preserve font_ascii[256], all127 tiny records,
allocated width/height, exact width+1 advances, opaque offsets/descenders, space6,
tilde highlight0/+4, unmapped0 advance and empty text. The authored canvas cannot
reflow or grow the original logical layout. Table1 timer glyphs are a separate
font and cannot be silently substituted with tiny glyphs.

Palette semantics use the original unsafe OR result, including highlight spill, with the explicitly approved authored role7 and coverage alpha. This replaces original ASCII per-pixel edge shades; it does not claim to retain those shades. Baked labels remain independently colored.

## Lifetime and output requirements

Source-index equality is an occlusion condition, never authority to create a text
record. Authority includes gameplay PIC generation, exact persistent source lease,
explicit call-site ID, surface route, original draw completion, text bytes/metrics,
color/shadow role and either current scene frame or persistent event history.

Scene records expire at each ordinary begin. Equal stale glyph pixels cannot
renew them. Persistent level/message records survive only the original history
and same PIC generation; each has its own state. Modal suspension prevents output,
retains only records whose original route is restorable, and requires revalidation
on ordinary resume. PIC/mode/lease loss revokes all associated records.

An overlong level or message is coherent classic fallback. In particular, an
unsupported message can leave indexed remnants outside OPTION36's228x9 erase
area. A later short message or expiry erases only the original area; it cannot
clean those remnants. The minimal conservative protocol poisons that message
replacement until fresh PIC rather than pretending a later shorter string restored
safe history. Unsupported level history similarly remains classic for that grant.
This affects only that text stream. It never alters the original indexed renderer.

## Transparency and four-pass outline

Cash cannot be painted as an opaque rectangle. An authored glyph may expose a
hole where original ink existed, so drawing RGBA over the final classic glyph can
leave unwanted original fragments. A future compositor must account for the
actual pre-text lower RGB and original write coverage, then reproduce the approved
text at its original command order. This may require a narrowly bounded text-run
underlay; it is not permission for a general scene compositor rewrite.

FULL_SHADE order is four whole-string solid-black passes at(-1,0),(1,0),(0,-1),
(0,1), followed by the foreground string. It is not per-glyph shadow/foreground
interleaving. Empty alpha leaves the lower scene visible. Any later original write
must keep its ordering and occlusion; a finish overlay is acceptable only if the
specific call-site's subsequent writes are proven disjoint or explicitly tracked.
Saved/current ownership and underlay removal must obey existing fade/cache trust
rules, with no fresh glyph composition during fade or Present.

## Minimal design tests and gates

- `test_fixed_contract.py`: synthetic HUT1 finite geometry, exact registration,
  source370 capture independent of current palette, malformed resources and4x→8x repetition; no real art
- `test_original_layout.py`: compile actual original font routines with synthetic
  sprite metadata; independently verify original command sequences and byte rules
- `test_lifetime_protocol.py`: reference protocol only, scene expiry, persistent
  event/erase history, stale equal indices, modal/PIC/mode revocation and coherent
  fallback after overlong text; synthetic transparent compositing demonstrates
  why a black plate or final-classic-glyph overlay is insufficient

These tests do not establish production integration, runtime fade correctness or
accepted artwork. Next gates: review resource/opacity/color contract; root/artist
freeze; implement Stage1 independently; review Stage2 lifetime/underlay protocol
before any production hooks; then bounded Linux/sanitizer/original-state tests and
separate true2x/4x actual sampling. No publication is authorized by this design.
