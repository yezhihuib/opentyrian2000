# Optional source-authenticated HD Data portraits

All18 parent-approved faces retain their exact original geometry and palette
selection. The13 intentionally portrait-free entries stay absent. FACE7's
accepted v3 PNG and DPR1 remain byte-identical to the pilot. Native INDEX8/RNG,
palette writes, selection/input, natural Chinese936-paragraph text,1905-glyph
font and large gold EXIT remain unchanged. This is a local integration with
no GitHub publication.

Run with `--data-portrait-assets=/absolute/assets/data-portrait-v1`. Both package
launchers pass an absolute package-relative directory. Eighteen independently
optional `face00-v1.hda` through `face17-v1.hda` resources are selected. Missing,
short, oversized, malformed, wrong-hash or wrong-source entries fall back to that
native face; they do not disable any other face, DFM frame or translated text.
Resource caches are lazy and independent, bounded to18. Changing the directory
frees all cached art and resets the presentation lease.

## Exact per-face source authentication

A compiled descriptor table pins each face's RLE byte count/hash, independently
decoded INDEX8/hash and opaque-mask/hash, native geometry/anchor, effective
RGB palette, exact approved RGBA payload and whole-file hash. Header geometry
never controls allocation. Native center is(77,92), with the engine's integer
anchor `(77-width/2,92-height/2)`. Exact footprints are:

- FACE0..3,5..11:65x55 at45,65; canonical260x220 at180,260
- FACE4:65x53 at45,66; canonical260x212 at180,264
- FACE12:69x64 at43,60; canonical276x256 at172,240
- FACE13:70x63 at42,61; canonical280x252 at168,244
- FACE14:70x59 at42,63; canonical280x236 at168,252
- FACE15:70x77 at42,54; canonical280x308 at168,216
- FACE16:69x71 at43,57; canonical276x284 at172,228
- FACE17:48x63 at53,61; canonical192x252 at212,244

FACE0..11 use palettes1,2,3,4,6,9,11,12,16,13,14,15 respectively. FACE12..17
use palette0. Only indexes1..207 use the selected face palette; index0 and
208..255 retain palette0. All256 resulting RGB samples are authenticated once
per synchronous present. Fades suppress portraits until source palettes return.
Unknown INDEX8 writes, changed surface layout or renderer invalidation revoke
the lease. Rebuilt lists/new faces replace it; reader redraw and F6 retain the
verified underlay. Full-screen cursor restore allowances are cleared on end.

## True alpha and later draw ownership

Redrawn silhouettes intentionally differ from the native masks. Before the
unchanged native blit, presentation captures the complete native rectangle's
true INDEX8 underlay and optional DFM static ownership. At present it restores
that underlay, including independently authenticated DFM metal samples, then
composites every approved straight-RGBA sample. Transparent HD margins expose
the true scene, with no residual native face. There is no clipping to the old
mask, generic oval or frame aperture. FACE15 keeps its original rim overlap.

Every later native opaque pixel or clipped fill owns its complete logical cell,
including same-index writes. Cursor writes use temporary masks; only observed
cursor cells may be restored. Order remains native base, DFM, DPR1, translated
text/EXIT, native cursor. Full-screen1280x800 sparse output and the same nearest
SDL sampler retain exact cell boundaries at640x400 and letterboxed1280x720.
No source INDEX8 buffer is used for HD output. Software SDL round-off against
an independent rendered-underlay oracle is at most2/channel.

Storage is bounded by compiled constants: max5390 logical cells (70x77), max
344960 RGBA bytes per portrait,4420800 total HDA bytes including18 headers,
and4096000 output bytes. Per-face RLE decode uses bounded local arrays. No
resource-driven size, unbounded count or global failure flag is accepted.

## DPR1 and deterministic reproduction

`python3 scripts/export_data_portrait.py` checks all18 retained PNG SHA256s and
exact native4x RGBA geometry before writing output. It copies samples exactly,
without repainting, resampling, alpha/mask clipping, recoloring or sharpening.
The existing FACE7 PNG and whole-DPR1 SHA256 are independently fixed. Python and
Pillow are development dependencies only. `source-pack.json` retains complete
source identities, all136 mappings, selected versions, provenance fingerprints
and per-face native/canonical geometry. Native reference PNGs/data stay external.

Each DPR1 is128 header bytes followed by `width*height*64` RGBA payload bytes.
The15 little-endian uint32 fields at byte4 are version1, logical320,200, scale4,
native width,height, canonical width,height, logical anchor x,y, runtime ID,
source ID(runtime+1), palette index, payload bytes, reserved0. Five uint64 fields
at byte64 pin RLE, INDEX8, mask, effective RGB palette and payload FNV1a64. Bytes
104..127 must be zero. Exact file length and whole-file FNV are also pinned.
`face00-v1.json` through `face17-v1.json` record every resource fingerprint.
Full generation prompts and separate license-status notices remain beside art.

Focused regression: `tests/run_data_portrait_tests.sh ORIGINAL_DATA PORTRAIT_DIR
FRAME_DIR NEW_FIXTURES`. All18+noPortrait run at1280x800,640x400,1280x720 with
INDEX8 exact, every canonical underlay/alpha sample, FACE15 rim, later opaque
same-index/fill/cursor ownership, F6/fade/palette/reset/unknown-write rejection.
All128 header bytes are mutated for every face. Missing-one, truncated, extra,
corrupt payload/source-header, FIFO and allocation failures verify independent
fallback. Python tests reproduce all18 resources/pins, check source/geometry
rejection, package closure and immutable native/text/art baselines. Actual-game
QA and inspected native4x contact sheets are retained outside the repository.
