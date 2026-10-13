# Title menu font output portability

This font-only rendering correction extends the accepted V3.1 title typography
to arbitrary valid SDL output geometry. The previous title compositor accepted only destination
640×400 and 1280×800 and displayed classic menu text at 1920×1200 while retaining HD
art. No font atlas, original title artwork, game source data, indexed draw, palette
operation, menu input/layout, timing or cursor write is changed.

## Rendering contract

The historical native 640×400 and 1280×800 compositor remains the exact path when
renderer scale is one. Its per-operation rounded RGB histories are unchanged.
Other geometry first resolves the original recorded outline/base/selection order
into a transparent 1280×800 premultiplied font layer using the live expected palette.
The existing title RGBA texture is drawn normally, with its original nearest art
sampling. Only the font layer is then sampled in physical output space:

- Reduced axes integrate the complete correlated premultiplied layer over the
  output pixel footprint. Individual glyph passes and palette indices are not
  averaged independently.
- Enlarged axes linearly reconstruct premultiplied color and alpha together at
  `(pixel_center - destination_origin) * canonical_extent / output_extent - 0.5`.
  Two neighboring canonical samples contribute on each enlarged axis. Flat fully
  covered interiors retain their color; this does not filter the background.
- Support includes a one-canonical-pixel reconstruction halo on enlarged axes.
  Clip, viewport, renderer scale, letterboxing and negative origins use the same
  bounded geometry code as the accepted selector sampler.
- The title cursor is copied last as its exact opaque write mask, through the same
  nearest canonical texture and destination. Transparent cursor holes retain the
  new text, without the conservative cursor rectangle used by indexed selectors.
- An actual output resource/state failure redraws the original menu plane over the
  unchanged title underlay. The normal caller still owns presentation.

The additive `selector_font_output_overlay` does not clear or present.
`selector_font_output_present_smooth` provides an explicit opt-in to the same
reconstruction for other menus. Existing selector/pregame callers retain the
behavior of `selector_font_output_present`.

The portable arithmetic reference is the 8-bit premultiplied completed layer with
one final rounded composite. It is not the historical native paths' per-operation
opaque RGB rounding. Those native paths remain unchanged.

## Bounded storage and lifecycle

The optional title scratch allocation is now 4,096,000 bytes (formerly 1,904,640),
independent of output size. The same allocation serves either native histories or
the transparent canonical layer. It is allocated with the optional font and freed
on title/font invalidation. The existing title texture and output CPU buffer are
reused for the cursor-only pass; no extra full-size cursor texture is allocated.
Shared staging is less than 35,000 bytes and a 128×64 streaming tile. Shared texture
resources release before title renderer teardown, and actual SDL failures release
the shared sampler resources. The title synthetic ledger measures 15,993,856 bytes
of title dynamic CPU storage and 69,896 bytes of optional font fixed state; shared
sampler and SDL allocations are accounted separately by their own tests.

## Verification

The original title suite passes 736 synthetic presentations. The extended title
font suite passes 434 presentations, including exact native 2×/4× results, all seven
selections, original fallback/protocol/source/file checks, independent portable
ordered-layer and output oracles, 1920×1200, odd letterbox, anisotropic reduction,
sparse cursor holes/erase, renderer recreation, and intermediate UI/outgoing
fades. ASan/UBSan pass with LeakSanitizer disabled because the executor uses ptrace;
independent allocation and texture ledgers must empty.

The shared sampler suite passes 33 renderer cases and 84,735,928 checks for legacy
presentation, the smooth opt-in and RGBA overlay. It covers viewport/clip/scale,
logical size, offscreen origins, existing scaler/filter combinations, cursor
neighborhoods, and direct overlay create/read/update/copy faults and recovery.

Actual-engine capture pairs use the original startup/menu loop, fixed
seed, ordinary resize/key input and shared read-only assets. Verified actual
1920×1200 and 1365×767 output with centered 1022×767 letterboxed content retains
byte-exact indexed state, palette and RNG. Independent original glyph decoding
and authored coverage mapping establishes zero changed pixels outside original
or authored font coverage. Native 640×400 and 1280×800 old/new actual RGB is exact.
The enlarged-edge revision visibly removes nearest-magnification stair blocks;
it changes only font coverage and was accepted after actual before/after review.

These are SDL dummy/software results, not a Windows runtime, physical GPU,
fullscreen or joystick claim. The prior historical title source guard already
fails on clean 4597e39 because of outdated Settings source pins; current-main
preservation and the composed compatibility checks are recorded separately.
Original V3.1 artwork/contracts remain immutable historical artifacts.

See the [historical title contract](TITLE_MENU_FONT.md),
[Settings/Load output note](SETTINGS_LOAD_FONT_PORTABILITY.md) and
[exact current-source projection](../tests/test_portable_font_integration.py).
