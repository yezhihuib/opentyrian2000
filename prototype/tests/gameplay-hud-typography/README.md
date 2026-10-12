# Separate fixed-label candidate and dynamic typography design

Stage1 is a reversible HUT1 implementation based on published
f82630507ab7f405117dc84ca70095ca04dc470a. It adds exactly370 logical cells:
MODE95,SHIELD150,ARMOR125. Missing/corrupt/unsupported HUT1 falls back independently
while the existing HUD1,HUC1,HUL1 and scene paths remain available. The resource is
optional `gameplay-hud-fixed-text-v1.hda` in the already-selected asset directory.
No artwork or original runtime asset bytes are included in this patch.

The loader has one bounded regular-file attempt, one23680-byte allocation, opaque
payload/checksum checks, pinned original source/palette/layout compatibility, and
only370 runtime-captured indices. Capture occurs before palette installation;
normal palette is checked at ordinary composition. Three whole-word/column guards
prevent partial label substitution. Source/pixels/format/pitch/dimensions and PIC
lifecycle are independently leased. Fade/cache removal restores only owned cells
using a verified indexed/palette snapshot; untrusted cache is rejected safely.

Authored4x texels repeat exactly at8x. Added retained memory is23680 payload bytes,
370 source bytes,740 owner bytes,1024 palette bytes and small lease/generation
metadata. Ordinary active composition checks370 indexed cells and emits5920 or
23680 subpixels. No per-frame allocation, file I/O, gameplay state or RNG mutation.
The fade loop uses a constant-time finite coordinate lookup rather than scanning
all12tiles per output subpixel. Modal transitions retain the already-documented
classic-to-HD resume pop until the next ordinary frame.

## Tests

Run from the repository root:

```
python prototype/tests/gameplay-hud-typography/test_loader.py --sanitize
python prototype/tests/gameplay-hud-typography/test_renderer.py --sanitize
python prototype/tests/gameplay-hud-typography/test_fixed_contract.py
python prototype/tests/gameplay-hud-typography/test_original_layout.py --sanitize
python prototype/tests/gameplay-hud-typography/test_lifetime_protocol.py
python prototype/tests/gameplay-hud/test_renderer.py --sanitize
python prototype/tests/gameplay-hud-components/test_renderer.py --sanitize
python prototype/tests/gameplay-hud-indicators/test_renderer.py --sanitize
```

Loader:328 malformed/missing/FIFO cases,11 allocation/read/stat/close/short/racing
file failures, separate production-source pin checks,370 coherent-group mutations,
29600 exact4x/8x sample comparisons. Mock accounting checks no live descriptor or
allocation survives a failed load/shutdown. ASan/UBSan use LeakSanitizer disabled
because this executor's tracing environment does not support LeakSanitizer.

Renderer:370 exact cells,3 coherent groups,48 whole-image black/white/restore
removal counterfactuals,all other HUD families retained,missing/corrupt/fixed-only
paths,source-before-palette timing,13 stale-source/cache faults,mode/modal/texture
recreation/reset/teardown and no per-frame allocation. Original-layout tests are
source-extracted command oracles, not a claim that dynamic runtime is implemented.

`test_no_fixed_runtime.py` compares a published baseline and candidate using the
same existing pack without HUT1,classic and native2x/8x-internal120ticks each. It
retains only FIFO hashes and compact important gzip logs, with no captures or pack
copies. The bounded current scenario has header-only collision logs, so it proves
collision-stream equality but does not exercise actual collision events.

Linux build and disabled-renderer syntax are tested. All62 Windows C source entries
are present and unique; no Windows build is claimed. Actual HUT1 native2x/4x
readability and visual acceptance remain the parent's separate runtime gate.

## Stage2 remains a proposal

DESIGN.md,DYNAMIC_PROTOCOL.md and the layout/lifetime models describe the approved
ASCII role7 geometry and a proposed bounded ordered scene context. HUF1 art is
frozen, but there are no HUF1 loader, scene hooks, dynamic glyph ownership or
persistent text production changes in this checkpoint. Protocol approval and
implementation/counterfactual tests are separate gates.
