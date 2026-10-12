# HUL1 top lens and MODE assembly trial

Separate from the accepted HUD1 static frame and HUC1 labels/shield. The source
checkpoint is `dc1a2cf3e175e5e28f6c9f67df6ff614aa1c5c74`. No artwork or original
PIC/sprite/palette bytes are included in this source patch.

## Finite resource and source contract

Optional `gameplay-hud-indicators-v1.hda`: exactly 29,072 bytes, 80-byte
little-endian `<4s7I6Q>` header followed by 28,992 opaque RGBA8 bytes. The header
contains HUL1, version1, density4, top28x12, mode108x32, payload bytes, source
PIC3/palette/top21/mode1-216/mode2-216 FNV guards and payload FNV. Runtime source
signatures use standard FNV-1a64. The finite source guards are pinned in code;
the art payload is integrity checked but may be independently replaced by a
future approved resource using the same source contract. Density8 repeats each
canonical4x texel exactly2x.

- Top: half-open `[269,4,276,7)`, 21 logical cells
- MODE assembly: `[285,44,312,52)`, 216 cells, state1 `(OPTION18,OPTION19)`,
  state2 `(OPTION19,OPTION18)`, original PIC3 center grille
- Overlap: exactly82 HUD1 cells, 26 invariant rims plus the7x8 center grille
- HUC1 labels and shield are disjoint

The loader retains only21 top indices and two216-byte expected assembly rasters,
built from the runtime PIC3 and decoded opaque10x8 OPTION18/19 sprites. Source
PIC3 is captured only from the explicit successful gameplay PIC3 grant. An
independent persistent `VGAScreenSeg` surface/pixels/format/pitch lease is checked
before dereferencing; 320x200 indexed8 layout is mandatory. Replaced/freed old
buffers cannot qualify by coincident values. Sprite dimensions, bounded bytecode,
all80 opaque flags, and pinned sprite hashes are rechecked during lifecycle
checks. Normal palette is checked at ordinary composition, not during fades.

The only new game-writer call is a display notification after both original
`JE_drawPortConfigButtons` blits. It records mode1/2 without modifying original
state. No sprite-bank substitution or shop hook exists. Exact216 indexed equality
and that real draw event are required; a foreign raster mismatch revokes the mode
stamp until another actual draw. The top independently requires whole21 equality.
Unsupported modes, missing/corrupt files, unsupported source/palette, and source
lease failure cannot disable independent accepted components except where their
own pre-existing guards also reject the same invalid input.

## Overlapping output and fades

Composition happens last, after HUD1 and HUC1, only in an accepted ordinary
finish. Current/saved ownership has237 entries. The82 possible lower HUD1 cells
retain the actual composed RGB subpixels only where HUD1 owned the cell. Two
fixed `Uint32[82][64]` arrays consume41,984 bytes, plus bounded flags and metadata.
There is no per-frame allocation or additional I/O after the one resource attempt.

At solid fade start, saved hidden underlay and flags are snapshotted with the
visible cache. Hidden HD RGB follows precisely the same integer channel recurrence
as visible HD, targeting its own saved underlay during restoration. Hidden pixels
are not counted twice in visible-HD diagnostics. Upper removal restores its faded
underlay; unowned lower cells use the verified indexed/palette snapshot.

HUD1 removal while HUL1 covers it clears the corresponding hidden owner flags
without painting over the upper layer, so later HUL1 removal cannot resurrect
revoked frame pixels. Normal reset/suspension order is HUL1, HUC1, HUD1; repeated
and reverse-order removal are covered. Cache restoration checks source identity,
whole indexed snapshot, current palette, density/layout, upper/lower generations,
and corresponding current/saved lower owner bits. If any trust condition fails,
pending output and fade cache are rejected rather than reconstructed from stale
or freed data. Independent assets remain eligible for the next ordinary frame
under their existing leases; actual PIC/mode/video revocations still require a
fresh explicit grant. No fresh art is composed during fade or Present.

Modal entry strips all cached HUD layers. Resume occurs at the next ordinary
render begin under the same lease; a restored MODE raster and retained real draw
stamp must still pass all216 cells. Benign renderer recreation follows this
suspension route. PIC/level/teardown clears the grant. End-level active flight may
retain the last displayed mode until the next original draw or reset. A modal
transition pop remains possible, as with the accepted HUD1/HUC1 path.

## Tests

Run from the repository root (append `--sanitize` for ASan/UBSan):

    python prototype/tests/gameplay-hud-indicators/run_tests.py
    python prototype/tests/gameplay-hud-indicators/test_mode_writer.py
    python prototype/tests/gameplay-hud-indicators/test_renderer.py

The loader suite covers882 valid/malformed fixtures,1600 whole-source mutations,
474 whole-ROI mutations, every sprite byte and every nonopaque alpha value, both
states,237 finite cells, exact4x/8x registration, one28,992-byte allocation and
allocation/free/descriptor accounting. The production pinned guards are checked
separately. Fixtures are synthetic and never distribute original indices.

The writer oracle executes the original function and scalar blits for modes1/2,
unsupported modes0/3/UINT_MAX, and two-player early return. After removing the sole
notification its source is token-identical to the accepted checkpoint; all64,000
indexed bytes and notification-after-both-blits ordering are checked.

The renderer oracle extracts the actual production helpers and links all three
real loaders. It tests144 whole-image no-HUL1 counterfactuals at density4/8, every
step of7-step black/white fade and5-step restore, upper/lower removal in both
orders, HUD1 absent,41-of82 partial lower ownership, repeated modal/reset flows,
mode events, foreign writes, special/gamma fallback, recreated renderers, freed
surface/pixels/format, layout/source/palette/generation/owner-bit faults, and no
per-frame allocation. Prior static and HUC1 suites are rerun unchanged in scope.

`test_no_indicators_runtime.py` performs four bounded120-tick classic/density8
baseline/candidate runs, with the accepted HUD1+HUC1 pack lacking HUL1. All runtime
TSV/RGB hashes must match, using FIFOs and small compressed evidence, no captures
or pack/data copies. Collision streams in this short case are header-only; actual
mode-transition and combined visual trial remain a separate publication gate.

Linux build and renderer-disabled syntax are checked. All Windows source project
entries are included; no Windows build claim is made. Optional LeakSanitizer may
be unavailable under ptrace; explicit allocation/free/descriptor tests still run.

Finite cost: one ordinary begin/finish/present sequence checks two80-cell sprites
three times, hashes768 palette bytes at composition, checks237 displayed source
indices, and samples237*density² upper subpixels. At most82*density² lower
subpixels are copied or advanced per fade step; source-cache verification compares
64,000 indexed bytes. Actual mode-draw notifications add one sprite validation.
No timing optimization is claimed; the bounded no-HUL1 runs establish exactness,
not a hardware-independent performance guarantee.
