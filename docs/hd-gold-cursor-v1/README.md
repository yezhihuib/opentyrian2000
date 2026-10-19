# Smooth original-style gold cursors

This finite presentation upgrade replaces the five native gold mouse pointers
with continuous, two-dimensional bevelled geometry. The normal northwest arrow
keeps its accepted 11×16 geometry. The directional pointers retain the original
broad triangular head and short inset stem; they are not rotations of the normal
pointer. Gold shading samples the live native palette, including black fades.
No external cursor image, font or optional HD pack is required.

## Original registration

Native sprite metadata still owns input, hotspots and restoration:

- Normal: sprites 273/274/292/293, 11×16, hotspot (0,0)
- Up: 275/276/294/295, 21×16, hotspot (10,8)
- Down: 277/278/296/297, 21×16, hotspot (10,7)
- Left: 279/280/298/299, 16×21, hotspot (8,10)
- Right: 281/282/300/301, 16×21, hotspot (7,10); native sprite ink begins at column 8

The observer receives the same sprite-space origin and first sprite index as the
native draw. The right arrow's internal eight-column offset is applied only when
placing its display ink. Reader up/down switching, paging and Help left/right
switching remain under their original game logic.

## Ownership and fallback

- The engine still draws and restores the original INDEX8 cursor. This feature
  never changes those pixels, input coordinates, hit testing, simulation or RNG.
- The original static shop sheet is authenticated. Each selected shape's four
  quadrants are decoded independently. A full pre-draw snapshot and complete
  expected native output must match before replacing any displayed ink,
  including same-index writes.
- The scaler receives a separate cursor-free surface view. Existing title,
  menu/font, Data frame, portrait and text presenters retain their native
  validation streams while omitting cursor ink only for a preflighted lease.
  The smooth pointer is drawn after the last applicable display layer.
- Missing resources, unsupported shapes/filters, hidden mouse, changed native
  output, allocation/texture/upload failure or oversized output retain classic
  presentation. Late cursor-copy failures retire the lease and retry the
  native-backed composition. Renderer/device resets release cursor resources.
- Fractional window fitting, offsets, resizing and letterboxes are supported.
  A pre-existing clip combined with nonunit SDL renderer scale uses classic
  fallback, avoiding SDL's lossy scaled clip getters.

Manufacturer cards and gameplay render-mirror output retain existing ownership.

## Bounded verification

Run the focused Linux SDL test with the original external data:

```sh
tests/run_hd_cursor_tests.sh /absolute/path/to/tyrian2000
```

The focused test covers 250 shape/output-size/position/filter combinations, exact
native underlays and INDEX8 immutability. All five shapes cover wrong-shape draw
rejection, hidden/switching state, unsupported shape fallback, black fades, and
injected texture creation, blend/scale setup, upload and final-copy failures.
Malformed/corrupt inputs, unsupported filters, same-index writes, late indexed
mutations, fractional-scissor fallback and renderer replacement are checked.
Plain and UBSan runs and strict C99/pedantic module compilation pass.

Actual-engine Linux SDL dummy/software paired runs cover 1280×800, 640×400 and a
1280×720 letterbox followed by a 1001×633 resize. Each pair preserves all 20
indexed, palette, RNG and input/layout-state rows. Coverage includes native
English and HD Chinese readers, up/down switching, actual mouse-click scrolling
0→1→0, F6 both ways, Help left/right, hidden-pointer restoration, selection/EXIT
and return to the shop. Directional screenshot differences stay inside their
original cursor boxes; normal and hidden screenshots remain pixel-identical.
Fade presentations report no HD cursor leakage. Missing text/frame/portrait
resource checks retain independent cursor presentation and native fallbacks.

Independent review verifies 50 normal-pointer RGBA cases exactly match the
preceding accepted normal-pointer build. A further 120 Data frame/portrait
composition cases cover all five shapes, two portraits, native 2×/4×,
offset/fractional outputs and edge clipping. Cursor-free composition remains
exact; injected late-copy fallback is pixel-exact to the native-backed classic
baseline. The shared font-output regression passes 33 cases / 84,735,928 checks.
Data frame and all-18-portrait UBSan regressions and a strict Linux production
build pass. Windows runtime/GPU acceptance remains separate. This is bounded
cursor acceptance, not a whole-game certification.

The 18 portrait assets, Chinese translations/aliases, 936 paragraphs,
1,905-glyph font and gold EXIT assets are unchanged by this feature.
