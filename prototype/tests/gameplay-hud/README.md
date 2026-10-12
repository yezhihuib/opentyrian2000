# Asset-only gameplay HUD loader

The core synthetic tests generate their own masks, indexed source arrays and
RGBA bytes. They neither read nor distribute original game data or HUD artwork.
The separately invoked runtime tests read caller-selected external resources;
they never copy them, produce screenshots, or include them in this source patch.

Run from any directory, with Python 3 and a C99 compiler:

```
python3 prototype/tests/gameplay-hud/run_tests.py
python3 prototype/tests/gameplay-hud/run_tests.py --sanitize
```

`--cc clang` or `CC=clang` selects another compiler. ASan/UBSan runs stop on the
first sanitizer finding. Add `--leak-check` to enable LeakSanitizer where the
execution environment supports it (it cannot run under ptrace). Independent
allocation/free instrumentation is always enabled and verifies zero outstanding
loader allocations at completion. Temporary fixtures and executables are
removed at exit.

Coverage includes missing/NULL/empty/overlong paths, immutable failed and
successful attempts, allocation failure, truncated/extra bytes, every header
field, payload checksums, binary/nonempty/limited masks, all four corners of the
playfield and fourteen protected rectangles, exact alpha registration for all
sixteen subpixels, arbitrary hidden RGB, black artwork, source checksum and
zero-index rejection, row padding, failed-capture invalidation, occlusion guard,
coordinate bounds, full-frame 4x/8x sampling, and shutdown/reload. Allocation
instrumentation enforces one exact-size live loader allocation and checks that
capture/sampling/mode verification make no allocations. Expansion tests also
pin all 310 approved coordinates, independently reject all 261 rejected audit
candidates, probe span boundaries, enforce the 6667-pixel cap, corrupt every
glyph-moat point with updated checksums, and check both mode states against
captured PIC3 and per-point opacity. All source indices and RGBA are synthetic.

## `gameplay-hud-v1.hda` contract

Exactly one selected-directory file, 4,160,064 bytes total. All integers are
unsigned little-endian; no native C structure is serialized. Header offsets:

| Offset | Bytes | Required value |
|---:|---:|---|
| 0 | 4 | ASCII `HUD1` |
| 4 | 4 | Version 1 |
| 8 | 4 | Logical width 320 |
| 12 | 4 | Logical height 200 |
| 16 | 4 | Density 4 |
| 20 | 4 | Anchor X 0 |
| 24 | 4 | Anchor Y 0 |
| 28 | 4 | Mask bytes 64000 |
| 32 | 4 | RGBA bytes 4096000 |
| 36 | 8 | Source-index FNV-1a64 |
| 44 | 8 | Mask FNV-1a64 |
| 52 | 8 | RGBA FNV-1a64 |
| 60 | 4 | Reserved 0 |

Header is followed by the 320x200 row-major byte mask, then a 1280x800 row-major
RGBA8 image. Exact EOF is required. FNV-1a64 uses offset basis
14695981039346656037 and prime 1099511628211, with unsigned 64-bit wraparound.
Checksums detect accidental corruption; they do not authenticate an asset.

Mask bytes must be 0 or 255, with 1 through 6667 owned logical pixels. Base ownership
must be outside the half-open playfield `[0,0,264,184)` and outside all these
half-open `[x1,y1,x2,y2)` rectangles:

- Generator window: `[268,10,279,108)`
- Front label/power: `[284,4,312,21)`
- Rear label/power: `[284,25,312,41)`
- Left rear-mode sprite: `[285,44,295,52)`
- Right rear-mode sprite: `[302,44,312,52)`
- Mode label: `[284,53,313,60)`
- Sidekick icons/ammo: `[283,63,313,99)`
- Level name: `[267,115,320,128)`
- Shield window/capacity: `[270,134,279,195)`
- Armor window: `[307,134,316,195)`
- Static shield label: `[284,136,292,177)`
- Static armor label: `[294,136,302,177)`
- Top red lamp: `[269,3,277,8)`
- Message sprite/text: `[16,189,264,200)`

The only exceptions to these holes are the exact 310 approved coordinates in
`approved-rails.spans`, detailed below. The base geometry itself is unchanged.

Each logical mask byte must exactly equal the alpha of its sixteen 4x4 RGBA
subpixels. RGB is unrestricted, including outside ownership.

## Lifecycle and caller obligations

`gameplay_hud_load(directory)` makes one immutable selected-pack attempt,
including NULL, absent, invalid and allocation-failed inputs. It returns asset
validity. `gameplay_hud_shutdown()` frees storage and permits another attempt.
No alternate directories, pack switching, artwork synthesis or source fallback
are performed by the loader.

`gameplay_hud_capture(indices,pitch)` requires 200 readable rows, each at least
320 bytes wide. The full 64000 source bytes, excluding pitch padding, must match
the header checksum. Every masked source index must be nonzero. On any failure,
the previous capture becomes invalid. Success copies into an internal canonical
320x200 source array. `gameplay_hud_ready()` requires both asset and capture.
`gameplay_hud_forget_source()` only invalidates the capture; it retains the asset.

`gameplay_hud_sample(x,y,sx,sy,density,current_index)` returns NULL unless ready,
within bounds, inside ownership, and `current_index` equals the captured source
index. Only densities 4 and 8 are supported. Density 8 uses exact nearest-neighbor
2x replication of each authored subpixel, `sx/2, sy/2`; density 4 uses `sx,sy`.
The returned RGBA pointer is module-owned and lasts until shutdown. An equal
palette index cannot identify a same-index redraw; the caller's mode and
source-lifetime gates remain necessary.

The caller must capture only the compatible, pristine single-player PIC3 source
and restrict sampling to supported gameplay mode and rendering context. The
loader knows no menus, timers, palette state, player count or scene state. It
does not read original game files. It is a single-threaded module.

Resource ceiling: one 4,160,000-byte heap allocation for mask plus RGBA, a
64,000-byte static source capture, small stack buffers, no per-frame allocations
or file I/O. Invalid lengths/header fields are rejected before allocation. The
Unix makefile discovers the source automatically; the Visual C project lists the
new C and header files explicitly.

## Approved 310-pixel expansion loader

The loader adds an exact finite coordinate allowlist without changing the asset
format, selected path, or base geometry. `src/gameplay_hud.c` stores 51 half-open
coordinate rectangles, coalescing identical adjacent row spans. Their union is
exactly the independently checked 310-point fixture `approved-rails.spans`.
Reconstructed 64000-byte 0/255 incremental mask SHA256:
`903328448558ea0a8b7ea1e895339602736664bad73b0828b8ace4b3732263d2`.

The companion `rejected-candidates.spans` contains all 261 rejected candidate
points; reconstructed mask SHA256:
`f318812df425dd11419446752272f32917ee97f2c4e8541893c7bc16ed0fe10e`.
Both fixtures contain coordinates only, without original source indices, RGB,
artwork, or game files. Tests reconstruct them independently and compare the
production allowlist with the frozen approved mask. The cap is 6667 owned pixels
in total (6357 current production pixels plus 310 possible approved additions),
not 6667 additional pixels. The former synthetic 6768-point base-geometry fixture
is now correctly rejected by the cap. Base-only sparse assets remain supported.
The bottom message ribs and all other protected coordinates stay excluded.

`gameplay_hud_has_expansion()` is true exactly when a valid loaded mask owns at
least one of the approved addition coordinates, regardless of capture state.
Any expanded mask additionally requires the complete original-index-zero moat
around all eleven 5x5 SHIELD/ARMOR glyph boxes. SHIELD boxes start at x285 and
rows 138,144,150,156,162,168; ARMOR boxes start at x296 and rows
138,144,150,156,162. Each one-pixel moat covers the full surrounding 7x7 border,
including corners. Shared rows give 201 unique moat points in total. Capture
rejects a nonzero moat even if the full declared source checksum was updated to
match it. Every owned source pixel must still be nonzero and the complete
64000-byte checksum must still match. Base-only masks have no moat requirement.

`gameplay_hud_verify_modes(indices, opaque)` receives two decoded 10x8 source
states, in row-major order, for OPTION18/19. With any expansion it requires a
successful source capture. For each actually owned mode-rim point at the
(285,44) and (302,44) origins, both states must have opacity 255 and identical
raw indices equal to that position in captured PIC3. Under the caller's shared
palette this also proves identical RGBA. It checks all 26 possible mode points,
which correspond to 15 distinct local sprite offsets, only when owned. Invalid
unowned state pixels cannot reject unrelated rails. NULL arrays are allowed only
when no mode point is owned; base-only masks return true without capture or
arrays. These queries make no allocations or file reads. The caller remains
responsible for valid sprite decoding, font/item/player bounds, palette/context
compatibility, and the existing generation and cache lifecycle.

## Renderer and lifecycle oracle

```
python3 prototype/tests/gameplay-hud/test_renderer.py
python3 prototype/tests/gameplay-hud/test_renderer.py --sanitize
```

The runner extracts the actual production HUD, begin/finish, fade and presentation
function bodies into a synthetic SDL-surface harness. It uses the real loader
and generated four-pixel / exact310 masks with coordinate-pattern RGBA. It also extracts
the pre-HUD renderer at `a49e46e5f8880b98cfb41028b6389e97d0636433`, then compares
no-asset classic/density4/density8 output and fade/presentation state exactly.
It requires that base commit in the repository. All fixture files are temporary.

The oracle checks whole-output pixels, including unchanged playfield, dynamic
holes and occluded owned pixels; 4-to-8 exact replication; immutable indexed
buffers; no additional ordinary-frame surface allocation; one-shot presentation;
PIC replacement with coincident indices; revocation until a new source capture;
mode changes at finish/fade/present; interrupted-frame/modal suspension and next-
begin resumption; black/white and restoration fades; HUD-only and scene-plus-HUD
cache removal; stale index/palette cache rejection; repeated reset/suspension;
benign renderer recreation; teardown; special-output/gamma rejection; and
original-copy/disabled/missing/invalid-mode fallback. Source assertions check the
actual PIC, level, early-return, modal and teardown callsites. These are focused
production-helper and source-callsite tests, not interactive gameplay acceptance.
The expanded fixture exercises all 29 static/live font, RLE, item, mode, name,
and player bound mutations; cache-preserving failure; all guard boundaries;
and nine persistent surface identity/layout losses, freeing the old surface,
pixels or format before the guard executes. No stale allocation is read.

```
python3 prototype/tests/gameplay-hud/test_writers.py
```

The finite writer oracle pins the independent approved/rejected coordinate
fixtures and checks source expressions plus extracted drawing helpers against
all supported generator, power, gauge and ammunition values. It checks full
conservative icon/font footprints and the static-label boxes. Mode-state
invariance is verified separately by the loader and runtime-binding tests.

A separate Linux-only, hash-streaming real-executable regression is available:

```
python3 prototype/tests/gameplay-hud/test_no_asset_runtime.py \
  --baseline /path/to/baseline/opentyrian2000 \
  --candidate /path/to/candidate/opentyrian2000 \
  --pack /path/to/existing/pack-without-HUD \
  --data /path/to/existing/tyrian2000-data \
  --output /path/to/new/bounded-proof-directory
```

This runs 120 ticks in classic and density8 modes for both executables, with
`--render-no-capture`, SDL dummy/software and an isolated default configuration
(native 640x400 / 2x window). TSVs stream through FIFOs into SHA256; only small
important gzip streams, command/exit logs and summary hashes remain. It never
copies the data or selected pack. It verifies every emitted TSV, original
state/RNG/indexed output/collision equality, exact pre/post rendered-RGB equality,
and equal gameplay state/collisions across classic/HD. A short scene may contain
no collision events; inspect the retained collision line count when interpreting
coverage. This does not verify actual display scaling or visual artwork quality.

A private, actual-resource ownership diagnostic can be run after a Linux build:

```
python3 prototype/tests/gameplay-hud/test_asset_runtime.py \
  --pack /path/to/HUD-only-resource-directory \
  --data /path/to/existing/tyrian2000-data \
  --output /path/to/new/bounded-proof-directory
```

It compiles only a temporary instrumented renderer object and executable, leaving
production source/object/binary unchanged. A 60-tick HUD-off/HUD-on pair uses
FIFO/hash logs. Every frame must own exactly 6667 logical pixels; each owned
subpixel must equal the loaded resource RGBA, some must differ from classic,
and no scene HD sprite may be drawn. Original state/collision streams must be
identical. It records source/resource hashes and finite guard cost counters.
This diagnostic is for the full approved mask, not sparse synthetic packages.
It proves source/data binding and active output ownership, not physical display
sampling, interactive modal behavior, eventful collisions, or visual quality.

## Runtime bounds and source lease

An expanded resource enables repeated, allocation-free compatibility checks:

- All mapped TINY_FONT glyphs have valid bounded RLE, at most 6x8; levelName is
  NUL-terminated within its 11-byte storage. Ten characters at (268,118) cannot
  reach the approved rail at y126/127, including linear-address row wrapping.
- All 38 item options use at most ten ammo segments and referenced icon RLE at
  most 28x13. Both 10x8 OPTION18/19 states bind owned points to captured PIC3.
- All 12 shield definitions have mpwr at most14, so doubled shield capacity is
  at most28. The earliest capacity marker and gauge extent is row137; the
  approved top rail ends at136. Armor is also bounded to28.
- Once the first simulation begin occurs: power at most900, previous power
  at most90, shield/capacity/armor at most28, weapon powers at most11, valid
  sidekick IDs, and nonnegative current/max ammo fitting the same ten-segment
  bound. PIC3 capture precedes initial stat assignment, so live bounds start at
  the first begin; static asset/data checks run immediately.

Any unsupported binding revokes the whole HUD until a fresh eligible PIC3
capture. Original scene HD remains independent. Checks run at begin, finish,
fade start/step, present, and suspension; they are not cached across mutations.
Each successful expanded check scans 256 font map entries, 38 options, 12 shield
records, two mode sprites and bounded live values. At most152 distinct font
sprites, 38 icon sprites and two mode sprites are decoded, with at most44,302
RLE bytes inspected. The tested original dataset decodes143 sprites /5458 bytes
per check. An ordinary begin/finish/present sequence makes three checks; fade
and suspension add their own checks. This is intentionally conservative.

A valid grant requires decoded_pic3 == VGAScreenSeg, a non-null pixels pointer,
320x200 geometry, pitch at least320 and an 8-bit/one-byte format. It binds the
persistent surface pointer, pixels pointer, format pointer, pitch, width and
height. Every lifecycle guard validates identity before indexed dereferences.
A replaced surface, pixel allocation, format or layout revokes and rejects
pending/saved cache without reading the old allocation. Equal index bytes never
renew the grant. Reset clears the lease; texture recreation preserves it while
suspended, and true video teardown revokes before freeing the surface.

## Integration boundaries

Only the explicit successful single-player gameplay PIC3 load grants ownership,
before options/text modify its decoded indices. Every generic PIC load revokes it;
a same-index replacement cannot activate it. Start-level, before map loading,
probe/debug early returns and true video teardown also revoke. Two-player or
Galaga observed at begin, finish, fade or present revokes until a fresh eligible
PIC3 capture. `endLevel` alone does not revoke while its active flight frames
continue; the ensuing `start_level` transition revokes before results/loading.

Pause, help and in-game setup suspend immediately, including removal of any
already-baked HUD in pending/saved output. Resume occurs only at the next ordinary
begin with the same unrevoked source capture. Renderer/texture recreation uses
this same suspension path, while true video teardown also releases the asset.
Cached scene HD survives HUD removal only when its indexed and current-palette
snapshot is verified; stale caches are rejected safely. HUD ownership and its
saved fade generation are separate from scene-space ownership. The HUD palette
snapshot is separate too, preserving the existing no-HUD scene fade behavior.

Composition happens only in an accepted ordinary finish, after original upscale
and scene crop, before output audit/export/cache. Neither fade nor present applies
fresh artwork. Original dynamic writes, gameplay state, RNG, input and timing
logic are unchanged. Startup/fade-in before the first ordinary frame, modal
screens, results and rejected/special output retain indexed HUD. A classic-to-HD
transition on modal return is an intentional bounded fallback and still needs
visual inspection with final approved artwork. No artwork is included or selected
by this source patch. Final artwork/source/mask checksums belong to its separately
reviewed resource package. This revision permits only the approved 310 additions,
for a total 6667-pixel ceiling; all 261 rejected candidates and bottom message
ribs remain excluded. Any further expansion requires a new source/writer audit.

The Windows source project is registered, but no Windows build or interactive
end-to-end pause/death/restart/next-level visual pass is claimed by these tests.
