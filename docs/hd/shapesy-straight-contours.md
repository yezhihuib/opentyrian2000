# ShapesY straight contours

This revision replaces the superseded local corner-shaving proposal. The user
accepted the new full-corner appearance on 2026-10-26. The accepted upper outline,
lower deck/wall seam, narrow apex transition, and crisp material detail are the
visual reference; the implementation must not shrink the platform to preserve an
obsolete all-water-RGB invariant.

## Scope and geometry

The existing finite family of 28 ShapesY tiles, original source bindings, palette,
resource checks, and density-8 requirement remain authoritative. This revision
reconstructs the two right-facing edge classes in the requested view:

- the rising outer deck/shadow/water contour;
- the descending deck/bevel/right-wall seam.

These are separate straight segments. A real apex or material junction is not
joined into one line. Other orientations and runs that do not satisfy the finite
geometry rules retain their original material silhouette; this is not a global
coastline vectorizer.

Runs are derived once from the complete current map's source-semantic geometry,
not from the clipped viewport. Endpoint coordinates are fixed in map space;
scrolling only translates them. The cache is bound to the complete map pointer
fingerprint and the existing exact source witnesses. Runs shorter than ten rows,
longer than 256 rows, outside the admitted slope range, or exceeding a three-native-
pixel **centerline fitting residual** are not reconstructed.

That fitting residual is **not** the changed-pixel band. The authorized mask also
contains the original/new rim or bevel and destination-pixel coverage. In the
accepted native-1280 frame, measured changed-pixel centers relative to the original
raster boundaries extend as follows (negative is left/inward):

| Reference boundary | Left/inward extent | Right/outward extent |
| --- | ---: | ---: |
| Upper outer nonwater boundary | -3.625 native pixels | +2.625 native pixels |
| Lower deck-to-bevel seam | -1.625 native pixels | +4.125 native pixels |
| Lower bevel-to-wall seam | -2.625 native pixels | +3.125 native pixels |

Pixel areas extend another 0.125 native pixel beyond these center measurements at
4x. These figures describe the accepted frame, not a universal bound for every
map/scale. The reproducible per-frame contour/bevel/coverage mask is the exact
change authority. Water and authored interior pixels **outside that mask** must
remain byte-identical. Original water inside the mask may receive fractional or
full material coverage. Native INDEX8, expected indices, tile placement, RNG,
collision, and simulation state are never changed by this operation.

## Materials and ordered composition

`prototype/build-shapesy-contour-materials.py` deterministically exposes the same
master crops, registration, lighting, and UV grids used by the existing material
recipe. It produces `src/current_shapesy_contour_materials.h`. No image is painted,
no new style is introduced, and the existing PNG/HDA/master bytes are unchanged.
The immutable table contains component colors and semantic labels, not native
water RGB or original game-bank pixels.

After all eight qualified native Layer1 rows finish, the existing mirror canvas
is recomposed only within the authorized contour band. Deck, bevel, right wall,
and shadow use their original component UVs. Water comes from verified current
native water pixels, never from a stale pre-terrain underlay. Each edited original
gray cell must still have its exact authored colors, expected INDEX8, and HD owner;
each water tap must still have native indices, palette colors, and classic owner.
Newly covered original-water pixels acquire HD ownership only inside the mask.
No second fullscreen compositor or owner buffer is introduced. Layer2, actors,
effects, and HUD still run afterward in their original order.

The skipped source-index-0 cell in tile 333 is explicitly excluded and retains its
original black-clear proof. The red recess and other nonedge interior detail are
excluded from contour reconstruction.

## Output sampling and fallback

The engine presents the density-8 texture using nearest sampling. A single-HD-
texel half-coverage stripe can disappear during downsampling, so coverage is the
analytic area of the actual destination pixel footprint, using integer arithmetic.
The qualified output sizes are native 640x400 and 1280x800: respectively 4x4 and
2x2 HD-texel footprints. There is no global linear filtering or image-wide blur.

A read-only video geometry query records the renderer identity/generation, output
and window dimensions, destination rectangle, scale, viewport, clip and transform
conditions. The witness is checked at admission, pass completion, frame finish,
and actual Present. Unsupported display geometry declines the Y extension;
geometry changed after contribution rejects the mirror frame. Other renderers,
DPI transforms, output sizes, Windows and full-campaign behavior are not implied
by the bounded Linux qualification.

## Reproduction and evidence

Rebuild the immutable material table without original game data:

```
python3 prototype/build-shapesy-contour-materials.py --out /tmp/contour-materials.h
cmp /tmp/contour-materials.h src/current_shapesy_contour_materials.h
```

The PUBLIC7d inverse proof independently regenerates that table before removing
new Y sources from older current-source, P9 and SHOP oracles. Original public
preimages, historical expected hashes, catalog and HDA identities, and the
independent 44-file density correction remain unchanged.

The focused runtime proof and final bounded qualification receipts are separate
from visual approval. The accepted prototype backup remains a rollback snapshot;
its earlier receipts must not be mistaken for final stabilization evidence.
