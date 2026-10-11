# 75–90 seconds: mapping and logic closure

Ticks2610–3131,522 ticks, current original level replay from0. This is a
**private-survival/no-injection/no-control** trace; the ordinary fixture ends
at1052. There is no save-state restoration claim.

The baseline inventory contains91 visible material identities and89,967
references.90 were already mapped; the sole gap was Layer1 shapesZ80, entering
at3099 as a four-pixel-wide sand sliver. The grass9 integration closes that gap:
33 visible and3 fully offscreen NORMAL calls now use the selected HD80.
Accepted gray131 has actual reuse in this window, rather than only static coverage.
No grass is visibly demonstrated by the entering80 sliver.

Candidate replay has3,132 exact original state/clock/pose records,495,951
material rows,54 collisions and3,535 enemy-projectile rows. The previous
0–2609 prefix also matches. All522 render-health records have zero coverage,
RGB/restoration mismatches or rejections. All prior HD resource bytes remain
unchanged. The identity ledger preserves the observed counts; IDs are not
summed across overlapping windows.

The final **522-frame native 2× visual review passed** after mapping and
original-logic verification. Every lossless decoded frame matches direct SDL
RGBA/BGRA readback, and all 22 deterministic logs match the noncapture run.
Sequential visual inspection plus native frames 2700/2842/3131 found no old-art
flashes, registration seams or ordering defects. Minor terrain texture-phase
variation remains. The player is alive and the level active at tick 3131; this
is not a clear-tail test. The separate accepted
120-frame grass-family tail 3480–3599 is documented in
[GRASS_SAND_VALIDATION.md](GRASS_SAND_VALIDATION.md); its later grass visibility is a separate claim. HUD, future forest, unrelated later enemies and
whole-level coverage remain outside the claim. Windows acceptance is pending.

Final rendered checkpoint: `e2d443a51dde676883497d9d8eb9217d8bf251b8`,
tree `23776bb933f33ad688c8c676005718614279e81d`. The presentation is a 640×400
native 2× SDL software-renderer readback, streamed without an intermediate BMP
batch. The delivered video adds a 28-pixel label above the unchanged game image.
It runs 15.0075 seconds; the source/render loop advances once per original tick.
