# Component-focused gameplay HUD candidate

Status: frozen candidate for a bounded engineering trial and user review. Not final user acceptance; no publication by the art worker. V1/V2 were rejected, V3 style was accepted as the direction but criticized as insufficiently refined, and the full-frame V4 change was withheld as too marginal. This candidate preserves the retro layered warm cast-metal character while using a component atlas to spend image-generation resolution on the instruments.

## Asset production

One built-in imagegen call produced `generated-component-master.png` (1254x1254) from a clean component-layout guide and V3 mechanical-character reference. Actual top/lower rails are547/548pixels wide, versus roughly280pixels in earlier full-screen generations. `pilot-prompt.txt` records the exact request. `export_frozen.py` assembles whole-component crops at the unchanged original coordinates. No internal seam warping, recoloring, sharpening or invented readouts. Reproduction of the selected4xPNG is byte-exact.

The runtime filename `gameplay-hud-v1.hda` names the HUD1 resource FORMAT, not art revision1. The contents are this component-focused candidate. Header is64bytes, then64000binary mask bytes, then4096000RGBA bytes. Original game RGB/indices are not bundled. Runtime must snapshot and bind the real decoded PIC3.

## Ownership contract

- Original320x200 logical coordinates; gameplay rectangle x0..263,y0..183 has zero alpha.
- Base6357 owned static pixels plus EXACTLY310 additions from the reviewed audit, total6667. Incremental mask SHA256903328448558ea0a8b7ea1e895339602736664bad73b0828b8ace4b3732263d2. No other expansion.
- All261 rejected candidates, every original glyph/readout, red power prefixes, top lamp/lens and changing mode-rim pixels remain original. The entire228x9message erase/rib slot at(16,189) remains original.
- The26 approved rear-mode-rim pixels require both OPTION18/19 to be opaque, identical in index and RGBA and equal to PIC3 at their exact positions. The other284 additions require the finite source/data bounds in the audit: power0..900, shield/armor<=28, correct sidekick icons/ammo sizes, font width/height and level-name limits.
- Both source-picture equality and explicit finite mode/generation/lifecycle guards remain mandatory. No fallback rule may use broad palette thresholds or arbitrary similarity.
- PIC6/two-player/Galaga and unsupported modes/data must use classic fallback. Missing/corrupt/incompatible resources must use classic fallback. Menus/modal transitions/end-level and black/white fade/restoration must not retain a stale or bright overlay.
- Current source PIC3 standard FNV-1a64:14c1441f3d5dc0e2, offset14695981039346656037. Decoded64000-byte PIC3 SHA25683c5979f54de07f79e0c13970f242ae6f7435d4d396a168b340458c955c0e0f4.

## Verification already done

- Offline compositions over the two prior verified screenshots (stone4320 and missile0245) at2x/4x: zero changed gameplay or unowned pixels.
- Exact per-coordinate proof that all261 rejected candidates and the message erase/rib slot remain pixel-identical at2x/4x.
- The4x artifact sampled from the atlas is byte-exact through the packaged reproducer.
- The2x design preview directly downsamples source components; it is not a runtime capture. The4x design preview places4xHUD art over the existing2xgame screenshot enlarged nearest. Neither substitutes for actual renderer verification. Current hook samplers support4x/8x; actual native2x window presentation must be reviewed for thin-edge behavior.

## Required before activation/publication

Apply the exact reviewed allowlist and source/data bindings, then run finite writer-oracle, loader/corruption/fallback, normal/sanitizer lifecycle, palette fade and modal-return tests. Compare indexed state/RNG with no-art baseline. Start actual UI review with one bounded native2xstill; avoid broad log/capture sprays. Root/integrator controls final acceptance and publication. Keep this style unchanged unless the user gives further feedback.
