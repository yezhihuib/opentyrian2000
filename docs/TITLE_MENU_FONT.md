# Title-only medium typography trial

This optional display-only observer replaces the seven main-title menu rows with
approved V3.1 vector geometry (1.90 logical stroke). It is deliberately separate from
gameplay HUF1, large bank0 headings, setup/pickers, and tiny bank2 load rows. Existing
indexed rendering is still executed exactly. Source/module and bounded actual-engine validation pass; see
`TITLE_MENU_FONT_VALIDATION.json` for exact scope, cases and receipt identities.

## Explicit selection and compatible resources

Use the existing release/local-startup option:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-menu-v1
```

The six-file directory contains byte-exact copies of the original five files in
`startup-title-v1`, plus `title-menu-font-v1.hda`. Neither the old pack, manufacturer
pack, gameplay default selections nor the HDR1 inventory is changed. Typography
requires a valid title-art lease; it does not take ownership on its own. A missing,
invalid, unsupported or allocation-failed font uses the original menu plane while
retaining independently valid title artwork. Invalid title source/owner/palette/
checkpoint/layout still invokes the existing whole-title fallback.

Frozen art source: `assets/hd/artwork/title-menu-font-v3-1` (17 exact files).
Manifest SHA256: `ab89e4bff91beab301ba334ed6cf202d656a21d48f12e94cbe0abbe4102c385c`.
TMF1 SHA256: `26e4f9eabed4f90bfe74896e04ee59e647e445ffd44a9feaf003c91444275a4d`.
Payload FNV64: `08f9609583417c89`.

The authored package contains vector geometry, technical metrics/hash identities,
canonical alpha/roles, reproducible source and receipts. It contains no original
game sprite bytes, original palette arrays, original bitmaps or comparison images.
The source-only relocated rebuild reads only the vector JSON, contract and builder.

## Finite TMF1 protocol

All fields are little endian. The 128-byte header is `<4s15I8Q`, followed by 344064
coverage bytes then 344064 role bytes. Total file size is exactly688256 bytes.

- Magic: `TMF1`.
- Fifteen u32 fields: `[1,4,896,384,85,76,56,64,4,1,344064,344064,12,15,0]`.
  These are version, density, atlas width/height, slot/ink counts, cell width/height,
  inset, original font table, alpha/role sizes, role lower/upper bounds and reserve.
- Eight u64 fields: ASCII map, metrics, encoded glyphs, ink mask, title palette8,
  combined alpha+role payload FNV64, reserved zero, reserved zero.
- ASCII pin `845b16939661b466`:256 signed LE32 map values.
- Metrics pin `f0dec0f37828f1c4`:85 consecutive width,height,width+1 LE16 triples.
- Encoded pin `96f0e4e668876f23`:85 consecutive width,height,size LE16 triples,
  each followed by its source RLE; no table count or presence bytes.
- Ink pin `a3861b64f710cb1f`:85 eligibility bytes,0 for blank and255 for ink.
- Palette pin `8f64628a08533287`:256 expanded palette8 RGB triples.

The runtime independently validates original table1 count, pointers, dimensions,
encoded bytes and map against compiled source pins. It checks all96 atlas cells:
only the85 original metric rectangles may contain coverage, the9 original blank
slots and11 unused cells must be entirely zero, covered texels must have role12–15,
and uncovered texels must have role0. Every ink slot must contain coverage. File
size, regular-file status, header, complete bounded reads, payload checksum, trailing
EOF and close are checked. The payload checksum is corruption detection; the source
and packaging verifier pin the exact reviewed authored bytes.

## Ordered observer and fallback

Six explicit bracket pairs surround the existing five row passes and one selected
row draw in `titleScreen`. The arguments are identical to the enclosed original
calls. No shared font function or sprite writer changes. Each supported run builds
bounded glyph commands and the expected ordered classic pixel events from verified
source glyphs. Actual original pixel callbacks must match their positions and colors
one-for-one. A missed, extra, reordered, wrong-color or unbracketed write disables
new typography for this entire title epoch.

The finite caller protocol requires seven rows at y104+13×row, x160−width/2, the four
diagonal passes in original order (−1,−1),(+1,+1),(+1,−1),(−1,+1) at value−10, then
base value−3. Selection uses the same row/text centered at160 with value−1. Hue is15.
There are at most63 text bytes per run and2304 glyph commands. Width is bounded318;
every original metric box must fit the logical320×200 screen. Original blank slots
advance width+1; space advances6; tilde toggles+4 without advance. Absent equals85,
extended bytes and unmapped bytes force whole-menu classic fallback. Existing
original unsupported-width/draw quirks are not modified.

The completed base command prefix is immutable and its count is saved with
`menu_base`. Restore discards the previous highlight tail before appending the new
selection. Typography is composited instead of the old menu plane, in order:
background → version → Tyrian logo → 2000 logo → ordered glyphs → cursor. Coverage
uses integer straight-alpha source-over with +127 rounding. Roles are clamped after
the original signed brightness and resolved through the current expected palette,
so UI240–255 fades remain live and legitimate index255 remains red. Font RGB never
passes through the artwork fade channel.

At native640×400 only, the font compositor initializes four independent canonical
subsamples from the same unchanged nearest-sampled title-underlay color. It replays
all original ordered outline/base/selected passes separately into each subsample,
with the existing integer source-over rounding. Only after the entire stack is
complete does it reduce each2×2 group as `(sumRGB+2)/4`. This preserves correlated
coverage where outline copies overlap; reducing each pass first is forbidden.
Only the texels the existing nearest2× presenter samples are updated. Uncovered
cells reproduce the exact original title art. No palette indices are averaged.

Native1280×800 retains the exact canonical4× path. Other output dimensions use the
classic menu plane while retaining valid title artwork. They are not silently
filtered or treated as approved native scales. Cursor composition remains last.

A reusable1904640-byte scratch buffer covers only logical x[0,320),y[103,196),
which is1280×372 canonical texels. Every queued glyph checks that its metric box is
within both the original screen and this envelope. The buffer is allocated once
with the optional font and released on every typography invalidation. Allocation
failure uses classic menu text without disabling valid title art; no allocator is
called during presentation.

Source/table1 reset, font pointer/content/metric changes and all typography protocol
failures release only the optional font. Existing title end/foreign-screen paths
release it with title resources. Renderer recreation retains CPU data but recreates
the existing title texture. There is no per-presentation CPU allocation or file I/O.

On the tested64-bit build, additional fixed state is69896 bytes, optional payload is
688128 bytes, scratch is1904640 bytes, and the combined title dynamic peak is13802496
bytes. Including prior fixed title data and resource specs, explicit title CPU
storage is14738416 bytes;
the existing nominal4096000-byte SDL texture is unchanged. Allocations are tracked
independently in synthetic tests.

## Source and synthetic gates

```sh
python3 prototype/tests/title-menu-font/test_source.py
python3 prototype/tests/title-menu-font/test_runtime.py
python3 prototype/tests/title-menu-font/test_runtime.py --sanitize
python3 prototype/tests/title-menu-font/test_package.py
python3 prototype/title_menu_font_bundle.py --verify-rebuild
python3 prototype/tests/title-layers/test_source.py
python3 prototype/tests/title-layers/test_runtime.py
```

The Linux release build passes with existing unrelated warnings. The new source
guard removes only the12 explicit bracket statements and recovers all original
`tyrian2.c` bytes against e6fd18a (the title inputs also equal the tested 305c43a baseline). Shared fonts, gameplay HUF1, indexed sprite writes,
inputs/timing, manufacturer code and excluded submenu files remain byte-exact.

The existing title suite retains736 synthetic presentations. The new suite checks381
presentations against an independently recorded run/alpha compositor, including all
seven selections, selected-prefix restore, cursor overlay/erase, settled restart,
20-step UI and10/15-step outgoing fades, correlated native2× reduction, unchanged4×,
3× classic-menu fallback, blank advances, tilde255,
font source/reload changes, unsupported runs and missing/allocator fallback. Every
header byte, short/long files, hash errors, invalid role/padding/blank/unused texels,
nonregular files, FIFO, bounded read/stat/close failures and both optional allocation failures are
rejected. Normal and ASan/UBSan builds pass; LeakSanitizer is disabled under executor
tracing and an independent finite allocation ledger must empty.

## Bounded actual-engine validation

Paired release-engine runs pass at native 2× and 4×. Each preserves the original
82 intro plus 60 title presentations, waits, indexed state, palette, RNG and input.
Every title output is independently reconstructed, with zero changes outside the
old/new glyph coverage. Additional paired native 2× cases cover all seven selected
rows, visible cursor movement/erase, Instructions → title return → Quit, and key
input during the original fade. Missing and corrupt TMF1 cases retain valid title
art and match every classic-menu baseline readback. Ownership releases through the
submenu and final cleanup. The private instrumentation never enters production.

The tested code is f067d30 against 305c43a; the later e6fd18a merge retains all
tested title sources and resources byte-exact, while preserving the entry/spike
families. Root accepted the actual native 2× appearance. The artist directly reviewed
and accepted the native 2×/4× core, all seven selected states and retained
cursor/submenu/return/exit PNGs; `TITLE_MENU_FONT_AUTHOR_REVIEW.json` pins that
bounded actual-frame review separately from the earlier offline approval.

These runs use SDL software/dummy output, with retained original PPMs and lossless
PNGs. They do not establish physical GPU/fullscreen, Windows runtime, joystick,
setup/load activation or gameplay acceptance. See `TITLE_MENU_FONT_VALIDATION.json`
for exact case counts, receipt identities and remaining scope limits.
