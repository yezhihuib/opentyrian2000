# HUF1: finite gameplay tiny-font contexts

This source-only candidate was reconstructed after executor replacement, on
published56efa26181cd342347f8645f1c9adefc1e45d4ef. Historical tests from the lost
worktree do not certify this revision. All candidate tests must be rerun.

## Contract

Original indexed glyph writers, shared font tables, game state/RNG/input and
message counters remain unchanged. Only four explicit source call sites activate:

- Ordinary single-player, non-network cash at(30,175), hue2/value4, decimalASCII,
  at most20bytes, FULL_SHADE. The alternate smoothie color stays classic.
- Single-player non-network arcade name at(28,8) or(28,28), hue2/value6,
  at most20ASCII bytes, FULL_SHADE.
- One level setup call per fresh PIC3 at(268,118), hue12/value4, at most10bytes,
  confined to[268,118,320,126). A rejected or repeated attempt consumes/poisons it.
- JE_drawTextWindow at(20,190), hue0/value4, confined to[20,190,244,198).
  Messages are gray, not green. The original textErase counter owns their lifetime.

86 mappedASCII glyphs use the reviewed authored role7 coverage style. Original
per-pixel edge shades are intentionally replaced, not claimed preserved. Exact
source advances, space6, unmapped zero advance, tilde+4 and unsafe caller hue/value
OR arithmetic remain. All extended/accented byte runs fall back wholly. Full runs
are preflighted before drawing. The original four *whole-string* black L/R/U/D
passes precede foreground; every glyph command must match surface, table, id,
origin, black/foreground role, hue and value.

Cash/name are composed at their actual ordered draw position. Authored alpha-zero
holes preserve earlier RGB and cannot introduce a black plate over the scene.
The ownership union covers authored nonzero alpha and original glyph writes,
including removed original ink. This prevents old indexed ink reappearing in fades.
A command mismatch or early end strips the partially authored run to its actual
no-HUF counterfactual, preserving unrelated HD. Defensive missing-end abort runs
BEFORE finish copies canvas to output. Later normal writes retire only their
current text-owned blocks, so removing the remaining record cannot undo newer ink.

Each scene run captures its exact game_screen surface/pixels/format/pitch lease,
plus pre-text RGB, HD owner, cloud owner, green-first, live green-under RGB/owner,
and the independent logical selected bit. Original glyph callbacks advance the
counterfactual ledger even though original RGB is suppressed. Active cloud/green
provenance is supported; it is not treated as rare or rejected preemptively.
Inactive green-under bytes are undefined and are neither restored nor compared.

Typography never enters regions[]. Original restore closure remains unchanged;
strip happens after closure but before restoring pixels or reading owners. Every
other effect strips intersecting records before its read/write. Green smoke's
12x14 snapshot additionally reads[ x-1,x+13 ) by[ y-1,y+15 ); halo-only intersections
strip before snapshot, even when the asset's write rectangle does not intersect.

Persistent fields capture pre/post indexed history. Capture is allowed before
normal palette installation; ordinary composition requires the pinned RGB palette.
A first no-erase message requires pristine known PIC3 backdrop. Replacement requires
an actual complete228x9 opaque OPTION36 erase at(16,189), verified after writing.
Explicit expiry/help erase revokes old history even with coincident indices.
Help's own prompt cannot become a gameplay record. End-level pauses preserve the
record when the game performs no erase. Unsupported/extended/overflow history stays
poisoned until fresh PIC3, retaining original remnants rather than cleaning them.

PIC/mode/lease/teardown reset and modal suspension reuse the existing HUD lifecycle.
Texture recreation suspends; same-generation ordinary begin resumes. Fade/present
never freshly draw glyphs. Current/saved hidden RGB follows exact rounded integer
fade recurrence; removal restores only font-owned pixels. Actual fade-start,
fade-step and present guard generations, source leases and corresponding HD owner
bits before using hidden state. Failed trust rejects cached presentation safely.
Last-font removal recomputes scene-HD/cache eligibility; other scene/HUD owners
remain independently authoritative. Missing/invalid HUF1 leaves existing HUD art.

## Resource and source guards

`gameplay-hud-font-v1.hda`:163952bytes =112-byte little-endian`<4s11I8Q>` header
plus163840 alpha bytes512x320. MagicHUF1. Eleven u32 values:
1,4,512,320,127,86,32,40,4,163840,7.
Eight u64 values: PIC3 FNV14c1441f3d5dc0e2; normal palette5e80e83992be2927;
font_ascii845b16939661b466; metrics0908ca85cbf2a1e3;
encoded tiny2ed2973d82ce6f3d; declared alphaFNV;
eligibility68e8c2bab3c43d0d; zero.
FNV-1a64 basis14695981039346656037, prime1099511628211.

Map serialization:256 signedLE32 values. Metrics:127LE16(width,height,width+1)
triples. Encoded source:LE32 count127, then each LE16(width,height,size) and original
encoded bytes. Eligibility:127bytes,255 for0..85 and0 thereafter. No original PIC,
font bitmap or palette arrays are embedded or distributed. Every original RLE stream
is bounded/validated. Glyph slot=id,16columns,32x40,inset4. Padding outside runtime-
verified original allocation and all slot127 must be zero. Density8 repeats4x alpha
texels exactly2x. File size, regular-file status, reads, close, allocation, header,
checksum and padding fail closed. Frozen reviewed resource SHA256:
3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e.
Art stays outside this source commit.

## Bounded cost

Maximum scene boxes101x8 cash and141x10 name:2218 logical cells. History allocates
2850090bytes once, plus163840-byte alpha. At max8x there are20bytes per scene
subpixel: current/saved lower RGB, live green-under RGB, green-first, current/saved
lower owner, current/saved font owner, cloud and green-under owner. Logical selected
bits take2218bytes. Persistent pre/post/current/saved fields take8832bytes.
Descriptors/commands/palette/loader metadata stay under4096bytes. Total bound
3018026bytes excludes allocator bookkeeping, bounded stack and existing renderer.
Focused C reports actual sizeof totals and intercepts history calloc/free; ordinary
draws allocate nothing. Inactive calls skip capacity work. Only actual record extents
are copied/cleared; revoked state skips begin work.

Maximum per-run capture/copy/clear is2129280bytes at8x or532320 at4x, plus2218
selected bytes across both maximal runs. Previous-record begin clearing separately
adds at most283904bytes at8x (70976 at4x), plus4416 persistent owner bytes.
Actual retained object sizes sum3016953bytes, including3023bytes of descriptors/
metadata/constants; linker alignment and allocator bookkeeping are excluded.
Fade save copies at most851712bytes at8x or212928 at4x. Compatibility guards hash
map1024+metrics762+encoded3221+eligibility127bytes and validate bounded RLE at
lifecycle/run boundaries. Palette checks hash768bytes. PIC grant additionally
hashes64000indices and scans163840registration bytes. Cached checks scan the existing
64000index snapshot plus only current scene-font owner extents.

## Reproducible verification

From repository root:

    python prototype/tests/gameplay-hud-font/test_loader.py --sanitize
    python prototype/tests/gameplay-hud-font/test_renderer.py --sanitize

Loader suite separately pins production constants, then tests synthetic fixtures,
malformed/short/growing/corrupt/FIFO resources, fixed/metric-specific padding,
source mutations, legal and illegal original RLE, and11 intercepted I/O/allocation
failures with descriptor/allocation accounting.

Renderer oracle extracts actual C functions: render_mirror_pixel/rect/brightness,
sprite2_blend_pixel, draw_asset_filtered, restore_classic_rect, terrain_row/pixel,
both tiny glyph blitters, JE_outText, JE_textShade, JE_drawTextWindow, lifecycle,
finish, fade and present. Only unrelated asset/material lookup and family eligibility
are stubbed; accepted writer bodies, palette math and read footprints are real.
Compare whole canvas/output/saved RGB, HD/cloud/green owners, logical selected,
original indices and region closure against actual no-HUF rendering. Independent
scalar alpha covers whole-string ordering, highlights, descenders and maximum run
bounds. Tests include unfinished contexts at finish, generation faults through
actual fade/present, all halo-only integer placements, transparent holes, later
normal occlusion, local abort, persistent replacement/poison/expiry/help/end-level,
last-font cache status, mode/lease failures, black/white/restore and repeated suspend.

Optional test_real_source.py reads original runtime files and frozen HUF read-only,
without saving original bytes. test_no_font_runtime.py compares four120-tick
classic/HD A/B runs against exact published56efa261 using an existing pack without
HUF. No captures or pack copies. A header-only collision trace is explicitly not
active-collision coverage. Native2x/4x readability and real active-font state/lifetime
trials remain separate gates. No Windows build is claimed; project entries and
disabled translation-unit syntax are inspected.
