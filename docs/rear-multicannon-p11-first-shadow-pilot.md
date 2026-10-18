# Rear Multi-Cannon P11 FIRST shadow pilot

This finite presentation-only pilot reuses the accepted head alpha for physical
weapon record264, FIRST mode, in Episode1's first Normal level (physical level9).
It covers the six existing phases277,278,297,296,43,5 at density8. No new artwork
or resource files are required. All head RGB/RGBA, source/record pins, original
weapon data, allocator limits, movement, damage, energy, phase timing and RNG
remain unchanged.

The shadow uses the original position: shotX+1, shotY+shadowYDist. The original
INDEX8 darken blitter still runs exactly once. It halves the low palette nibble
with the original integer rounding. The optional RGBA compositor applies that
existing operation through the frozen head alpha; it never draws the head RGB
as a shadow, writes INDEX8, adds blur/glow, or changes the shadow offset.

Admission requires the original sealed record264 birth in its actual renderer
slot, exact live shot/source/record identity, the captured resource root and
density, and safe surface/canvas geometry. The lease belongs to one immediately
following original darken command. It is rechecked before visual composition
and cannot cross a frame/reset, source epoch, birth replacement or mismatched
command. A final lifetime counter of zero is valid because the original movement
function decrements it before drawing.

The existing13 generic shadow entries are unchanged. Other rear records,
record aliases, slot80, density4, Hard level15, unsafe horizontal bounds,
missing/corrupt resources and unqualified contexts keep their existing native
fallback. Current equipment changes do not reclassify retained births. Ordered
head/shadow/cloud composition and overlap-expanded restoration continue through
the existing command compositor.

## Reproducible synthetic checks

Use fresh output directories. No game data or original artwork is needed:

```sh
python tests/run_rear_multi_p1_core_tests.py /tmp/rear-core-new
python tests/run_rear_multi_p1_adapter_tests.py /tmp/rear-adapter-new
python tests/run_rear_multi_p11_shadow_tests.py /tmp/rear-adapter-new /tmp/rear-shadow-new
python tests/test_rear_multi_p1_source_inverse.py
```

The shadow preparation test compiles the actual adapter and guard code with
synthetic source/record/resource pins in strict C99 and ASan/UBSan. It covers all
six phases in all80 renderer slots, density4 fallback,27 negative families,
the21 earlier routes, retained births and reset epochs. It does not claim to
exercise SDL output or gameplay.

Private validation additionally uses authentic inputs and the unchanged accepted
art with the actual decoder, loader, command compositor, original blitters and
SDL software readback. A separate integer oracle checks the complete synthetic
canvas, alpha, ownership, cloud provenance, original indexed writes, overlap and
restoration, including the13 existing generic shadow branches. Contrasting
terrain/cloud layouts in those tests are synthetic arrangements, not background
changes in this pilot. They are not whole-level, campaign, Windows or GPU proof.

The bounded integration check ran one180-tick pair through the actual SDL
New Game / Full Game / Episode1 / Normal menus and a genuine P4 shop purchase.
Two documented diagnostic power-byte changes selected P10 and P11; both mode
changes used the actual SDL key handler. This is not evidence of an ordinary
P11 purchase. Both processes used the same accepted637-file pack and natural
paired RNG state. All20 named original observation streams and the four
explicit mixed-stream original-field projections stayed equal.

All668 eligible record264 shadows were admitted exactly once, with zero
per-command alpha/owner/cloud/INDEX8 diagnostic errors. All three retained
normal-head routes remained complete. Final native640×400 samples matched
the uploaded texture, with differences confined to admitted264 shadow
rectangles. Each phase had an isolated final difference after excluding every
other shadow's whole original rectangle and all current projectile heads.
The same-tick118 native pair received limited visual approval. These are
bounded per-draw and sampled-final-pixel witnesses, not an ideal whole-frame
compositor reconstruction or a full-level acceptance claim.
