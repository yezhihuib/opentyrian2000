# Settings and Load font output portability

This font-only correction removes the native-size-only output restriction from
Setup, Graphics, Sound, their pickers and the bounded Load menu. Use the existing
`--startup-assets=assets/hd/packs/startup-title-settings-v1` option and unchanged
SFN1 files. No new pack, font artwork, save format or gameplay change is required.

## Rendering and fallback

- Exact native nearest 2× (640×400) and 4× (1280×800) keep their existing opaque
  compositor and rounding. Those composition bodies remain byte-exact.
- Other valid SDL output/viewport geometry uses a transparent 1280×800 font layer.
  Original glyph, outline, highlight and palette operations are resolved in order.
  Reduced axes integrate coverage; enlarged axes linearly reconstruct premultiplied
  color and alpha together. Only the font layer uses this sampling.
- Original colors, indexed draws, strings, metrics, positions, input, fades,
  settings and saves remain authoritative. PIC2, bars, borders and Load arrows
  retain the selected classic scaler. Primitives erase earlier font coverage even
  when they write the same palette index. The classic cursor and its scaler
  neighborhood are restored last.
- The existing replay buffer is verified against the complete original frame
  before being reused as the font-free underlay. Existing bounded buffers and
  shared tiles are reused; font storage does not grow with physical output size.
- Unsupported names, bytes, source/order, resources or ownership still trigger
  whole-frame classic fallback. Valid title resources remain independent. Invalid
  output state or resource failures also return to the classic presenter.

Renderer, output identity or size changes invalidate the recorded frame until an
original complete menu rebuild. A resize during a fade can therefore leave the
remaining fade classic; this change does not promise uninterrupted enhancement
through resize. Original fade timing and input handling are unchanged.

Title typography has its own [output-portability note](TITLE_MENU_FONT_PORTABILITY.md).
Existing selector/pre-game callers retain their previous sampler behavior.

## Verification

Source, normal unit and ASan/UBSan checks pass. The Settings suite reports 372
portable layer states, seven renderer cases and five geometry states; Load reports
183, seven and five respectively, separate from its 192 source layouts
(144 eligible, 48 fallback). These extend the existing native raster,
source/resource, cursor, fade and lifecycle checks. The portable cases include
1920×1200, odd sizes, filtered output, viewport/clip/scale state and a 1920×1080
letterbox with destination (96, 0, 1728, 1080). Unit/oracle checks cover ordered
font layers, underlays, same-index occlusion and recovery. LeakSanitizer is disabled
under executor ptrace; explicit allocation/texture ledgers must balance.

Four bounded actual-engine runs form two reference/candidate pairs:

- 1920×1200 with the ordinary 2× scaler: 32 Settings and 35 Load presentations
  per side.
- 1365×853 with a normal Graphics-picker transition to Scale2x: 34 Settings and
  35 Load presentations per side. Fit 8:5 uses a 1364×853 destination with one
  right border column. The broad letterbox above is a unit case, not this run.

The paired indexed/palette streams, recorded command/input/fade/wait semantics,
final profile/save bytes and 502 source-observed file-access events match exactly.
The enhanced owner remains active throughout the captured menu presentations.
Each side retains eight named stills covering Setup, the scaler picker, Graphics,
Sound, both Load pages, footer and cursor. All 16 candidate stills passed producer
review. Independent review found no visual blocker in eight candidate and three
reference stills, and verified all 32 decoded-RGB hashes and all 136 paired
presentations. This is retained-still review, not continuous visual playback.
Actual outside-glyph-support RGB-mask equality was not separately measured;
font-only output scope is covered by the synthetic oracles.

These runs use the original menu loop, normal inputs, fixed-seed synthetic saves
and SDL dummy/software. They do not establish Windows runtime, physical GPU,
physical display/fullscreen, joystick or performance acceptance.

## Reproducible source checks and historical records

- [Settings unit runner](../tests/run_settings_font_tests.sh)
- [Load unit runner](../tests/run_load_font_tests.sh)
- [Shared output runner](../tests/run_selector_font_output_tests.sh)
- [Exact source/asset projection and negative controls](../tests/test_portable_font_integration.py)
- [Historical Settings acceptance](settings-font-v1/ACCEPTANCE.txt)
- [Historical Load usage](load-font-v1/USAGE.txt)

The new exact inverse projection restores the immutable `4597e39` source baseline;
previous acceptance files and pins remain unchanged. Historical Settings and Load
source guards already have stale `src/opentyr.c` and README pins respectively;
those failures are recorded separately, not treated as passing tests. This note
updates the old output-geometry limits without changing their historical results.
