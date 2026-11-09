# LAMP272 top-edge candidate

This default-off adapter adds HD writes for a narrowly bounded top-edge gap,
using the existing four lamp materials (229/231/233/235). No new art is added.
It is separate from the unchanged complete-body path and shared family guards.

Only body x=24..264 and y=-13..-1 are eligible. All four real native calls
must occur in order 0,1,19,20. Each quadrant checks the existing event/slot/
generation/bank/source/palette contracts. A dense 12x14 native source is decoded
read-only; only the exact visible native stores may write corresponding HD cells.
Transparent or unknown layouts, filters, blends, side/bottom clipping, wholly
invisible top quadrants, unexpected order or counts retain native fallback or
invalidate the provisional family frame. Later native writers keep the existing
ownership retirement rules. No simulation or shared admission rule is changed.

`LAMP272_TOP_CLIP_ENABLE=1` is an additional explicit candidate control alongside
the existing base 23 family values and manifest-verified 52 assets. It is sampled
at tick begin and checked again while writing and at finish. No control enables
the parent family. The existing launcher clears inherited `LAMP272_` controls;
this change adds no launcher preset. Use a separately reviewed, isolated bounded
test entry, with the actual Windows child CWD as its new native profile root.

The saved 600-tick audit contained 564 complete-body calls and 106 clipped-body
calls: **52 top calls and 54 bottom calls**. Bottom calls remain unsupported.
Offline checks replayed all 52 top samples / 208 quadrant calls through the
original native blit body: 26,208 visible stores and 1,677,312 independently
decoded HD sample positions matched. All four existing art states were checked
for this offline mapping; that does not qualify their final gameplay appearance.

One no-window SDL software pair compared the new control ON against OFF, both
with base23/base52. Each process had a 600-total-tick, 90-second, 64-MiB limit and
quit normally after the one selected sample. At tick380, actual Present136,
ordinal1, real event23/24 lamps in slots29/30, generation1, epoch58, body y=-11,
base235 produced 816 native stores. After subsequent writers, 694 conservative
surviving cells / **44,416 final pixels** matched independent HDR1 decoding with
zero differences; 44,402 pixels differed from the previous native lamp route.
The remaining 122 logical cells are not included in the material pass.

At the same actual checkpoint, native INDEX8, palette, recorded state and
collisions matched byte-for-byte. Public debug quit cleared observed frame,
ready, observer, cache and candidate-call state. There were also 2,991 changed
RGB pixels outside the conservative surviving-cell mask; they are not covered
by the material pass. No whole-frame RGB acceptance is claimed.

Only base235 has final-visible evidence. Normal gameplay, pause/resume,
return-to-title, other boundary types and native GUI/4x display remain untested.
Existing delivered entries are not changed or upgraded by this candidate.

The data-free C contract test never launches a game:

```sh
cc -std=c99 -Wall -Wextra tests/lamp272_top_clip_contract_test.c -o lamp272-clip-test
./lamp272-clip-test
```
