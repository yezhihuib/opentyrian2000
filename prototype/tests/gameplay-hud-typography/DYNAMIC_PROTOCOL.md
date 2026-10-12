# HUF1 ordered-context proposal, awaiting runtime-hook approval

Production Stage2 is not implemented. Root approved the reviewed86 ASCII glyphs
with authored role7 style; extended/accented runs stay wholly classic. Stage1
HUT1 is separate. This revision supersedes the earlier deferred-finish proposal.

## Frozen finite resource

`gameplay-hud-font-v1.hda`:163952 bytes, SHA256
3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e.
Header112 bytes `<4s11I8Q>` followed by163840 alpha8 bytes, row-major512x320.
No original glyph bitmap is shipped. Artist's vector-only repeated/isolated build
matches the canonical atlas, alphaFNV85cddeb8bd7ea09a, alphaSHA256
e4f245519b2922b3f3575ae499f0419bfc85742d059a07680f3693e68ddbaeb7.

Offsets4..44,11u32: version1,density4,width512,height320,glyph_count127,
eligible_count86,cell_width32,cell_height40,inset4,payload_bytes163840,role7.
Offsets48..104,8u64: PIC3FNV14c1441f3d5dc0e2,paletteFNV5e80e83992be2927,
fontAsciiFNV845b16939661b466,metricsFNV0908ca85cbf2a1e3,
tinyEncodedFNV2ed2973d82ce6f3d,alphaFNV85cddeb8bd7ea09a,
eligibilityFNV68e8c2bab3c43d0d,reserved0.

All hashes use standard FNV1a64 basis14695981039346656037,prime1099511628211.
Map serialization:256 signedLE32 values (-1=ffffffff),1024bytes.
Metrics:127 ID-ordered triples ofu16LE(width,height,width+1),762bytes.
Tiny encoded: countu32LE127, then each ID0..126 hasu16LE(width,height,size),
followed by original encodedbytes; total3221bytes. No populated flag or padding.
Eligibility:127bytes,255 for IDs0..85,0 for86..126. Only86 are runtime eligible;
127 authored shapes exist. Atlas slot=id in16columns,32x40cells,inset4. Everything
outside verified original w*4 byh*4 must be zero, including unused slot127.
Density8 repeats4x samples exactly. Whole-run extended-byte fallback includes
unmapped highbytes, not merely mapped accent glyphs.

Foreground color is the original caller's unsafe OR index with authored role7,
including tilde+4. Original ASCII edge values3/7 or2/4/5/6 are intentionally
replaced by authored coverage; source shade preservation is not claimed. Negative
brightness shadow calls stay solid palette index0. Integer alpha composition is
channel=(source*alpha+destination*(255-alpha)+127)/255, in exact command order.

## Allowed calls and lifetimes

- `JE_inGameDisplays`: cash(30,175),TINY_FONT,bank2,value4,FULL_SHADE; source
  string is the actual `%lu` buffer, maximum20decimal digits, not a later cash
  lookup. Alternate smoothie bank8/value8 stays classic.
- Same function's original single-player arcade-name call,bank2,value6,FULL_SHADE,
  actual up-to20bytes. Network/two-player/galaga stay classic.
- Gameplay PIC3 level setup `JE_outText(268,118,...,12,4)`: one capture opportunity
  per fresh grant, consumed even on rejection. Repeated equal writes cannot grant.
- `JE_drawTextWindow`: actual message(20,190),bank0,value4 and original erase/draw
  order; source textErase remains entirely game-owned. Expiry only outside endLevel.

No shared font table/layout function changes. Two blitter entry/end notifications
(`blit_sprite_hv_unsafe`, `blit_sprite_dark` only) are no-ops except within an
explicit approved context. Shop/menu/help/debug/lives/timer fonts never grant one.
Original indexed writes, random calls, input and simulation stay unchanged.

PIC3 capture is palette-independent because it precedes gamma/fade setup. Normal
palette is checked when the ordinary scene context or persistent composition runs.
All paths bind exact persistent surface,pixels,format,pitch,320x200 dimensions and
PICgeneration. Each scene run also leases game_screen surface,pixels,format,pitch
and dimensions independently; its identity must remain exact until finish. Scene records expire at ordinary begin; persistent records require
actual draw/erase history. No fade/Present path creates or redraws typography.

## Scene: ordered glyph transaction

Preflight the entire run before first authored write: supported source bytes,
font map/metrics/encoded checksum, exact caller role, normal palette, active scene,
finite box wholly inside scene[24,0,288,184), no active replacement nesting, and
capacity for its fixed record/command plan. Typography does not consume or alter
existing HdRegion slots. Plan at most100glyph commands per record
(20characters*5passes), comparing each actual command's surface,font/glyph,origin,
black/foreground mode,hue/value. FULL_SHADE order remains four entire-string
passes left,right,up,down,then foreground. Spaces,tilde,unmapped ASCII and empty
runs preserve original advances and command count.

There are only two disjoint scene records. At begin capture current canvasRGB and
HDowner for that actual box as the counterfactual no-HUF buffer. Initialize its
finite text-owner mask to zero. Original ink coverage is known from the verified
runtime glyph data, but is never embedded in the resource or distributed tests.

Retain exact current cloud_owner,green_first,green_under and green_under_owner
metadata in the same bounded transaction. Read green_under only when green_first
is nonzero; otherwise store an inert value. This allows common cloud crossings
without alternating HD/classic font activation. Existing green-head entries are
immutable for the frame and remain identified by their captured slot. Also retain
counterfactual logical selected[] bits. Original normal glyph writes update the
counterfactual provenance/selected bits exactly as the original mirror would
(clear them), while alpha-zero unwritten holes preserve lower visible metadata.
A strip restores only remaining text-owned subpixels and the corresponding
counterfactual RGB/HD/effect state; selected is reconstructed from remaining
original/lower ownership. Never restore metadata over a later normal write.

At each validated glyph entry, draw authored alpha into canvas at that exact
command position. Preserve lower RGB/HD ownership at alpha0. Mark finite
text-owner subpixels wherever authored alpha is nonzero. The
following unchanged original blitter still writes indexed pixels. Its guarded
mirror callback advances expected indices, updates the no-HUF RGB to the actual
classic palette color and lower HDowner to0 for each original covered block, and
suppresses only that original RGB replacement. Mark all original covered
subpixels as text-owned too, even if authored alpha is0: removed original ink
must not resurrect in fade. Thus ownership is the union of original write and
authored nonzero coverage. Unwritten spaces/holes retain prior scene metadata.

If a command mismatches, strip the run's already-owned subpixels to its updated
no-HUF buffer BEFORE handling that current original command normally. Cancel the
context so subsequent original commands stay classic. An incomplete end sequence
also strips it. This yields whole-run classic output without rollback of original
indexed writes or cleaning later content. Source preflight makes malformed source
ineligible before any authored write.

Later normal indexed writes keep their real order: clear text ownership only at
the actual overwritten logical blocks, then execute the ordinary mirror write.
Never retain ownership there for future whole-record stripping. Later non-normal
writes, HD draws or expanded local restores strip the entire affected remaining
record FIRST, before any existing path reads HDowner or color. Only still-owned
subpixels restore, so newer normal writes are never undone. The separate text record is
retired; existing scene regions stay unchanged. This is finite coherent fallback
for an unsupported subsequent effect, rather than introducing new blend semantics.

### Complete canvas-write notification inventory

The implementation must prove coverage at these production mutation entry points:
- `render_mirror_pixel`: normal clear; blend/shadow pre-strip, before owner tests
- `render_mirror_rect`: delegates each original changed logical pixel above
- `render_mirror_brightness_pixel`: pre-strip before reading canvas/owner
- `render_mirror_sprite2_blend_pixel`: pre-strip before its direct RGBA branch
- `draw_asset_filtered`: pre-strip intersecting record before region creation,
  green snapshot/composite or alpha/owner updates; all existing HD families route here
- `restore_classic_rect`: typography stays OUTSIDE regions[], so it cannot
  enlarge the original-region expansion fixpoint. After that unchanged closure,
  pre-strip records intersecting the final rectangle before region invalidation
  and painting. Test direct intersection plus text reached only through another
  region’s expansion, with exact no-HUF closure and unrelated scene RGB
- `render_mirror_terrain_pixel` and `render_mirror_terrain_row`: audit their direct
  branches explicitly, even though whitelisted scene text occurs after terrain;
  reject/strip an unexpected later terrain draw before it reads ownership
- `render_mirror_begin`/upscale/finish: begin expires scene records before resetting
  canvas; finish performs the existing ordinary crop without another text overlay

Every bypass found during implementation is a blocker, not a reason to rely only
on equal final RGB/indices. Post-source/indexed checks are secondary verification.

## Persistent level/message transaction

Level support[268,118,320,126),52x8; message support[20,190,244,198),224x8.
These boxes overlap zero accepted HUD1/HUC1/HUL1/HUT1 cells and lie outside the
viewport. Capture only actual pre-text indexed backdrop and post-text raster at
the explicit original event; ordinary composition reconstructs the indexed
backdrop and applies the same authored coverage. Own the union of original ink
and authored coverage including alpha-zero removed-ink holes. Original posttext
raster remains the verified classic counterfactual for cache removal/fade.

A first message with textErase==0 can use the known fresh-PIC/verified empty
backdrop only. Replacement requires observing the actual OPTION36 erase and then
capturing its fully opaque backdrop BEFORE the original new text. Never capture
old text as new backdrop. Expiry observes the actual erase, not a substitute clock.
`JE_inGameHelp` explicitly erases OPTION36 and draws its own prompt, then sets
textErase=1; revoke the message record at that event even in endLevel, where the
usual expiry may stay paused. Generic modal suspend/index equality cannot regrant.

Overlong or unsupported persistent text poisons its stream for the rest of the
PICgeneration. Original tails can extend beyond OPTION36, and later short text,
help or expiry cannot silently clean them. FreshPIC alone resets that history.
The independently proposed corner[248,184,269,200) remains outside this support;
overlong indexed tails remain available to its independent source-equality guard.

## Bounded storage and copying work

Scene cash maximum101x8=808logicalcells; arcade-name141x10=1410; total2218.
Current+saved no-HUF RGB arrays:283904bytes at4x /1135616bytes at8x.
Current+saved lower-HDowner bytes:70976 /283904.
Current+saved actual text-owner bytes:70976 /283904.
Current-only cloud/green provenance adds8bytes per subpixel:283904 /1135616.
Total709760 /2839040bytes, plus2218logical selected bits/bytes. The current-only
provenance is used before ordinary finish; fades/presents have no ordered scene
operations, and next begin resets the whole scene. Allocate maximum8x once only
when HUF1 is available.
Records, command plans and persistent indexed data add a small bounded amount;
exact sizeof totals are a required implementation receipt, not guessed here.

At each active scene begin, copy only actual area A,13*A*d*d bytes (RGB+owner+effect metadata),
and zero only A*d*d text-owner bytes. At both maxima,496832bytes at4x /1987328at8x,
plusA selected bits/bytes.
No full-capacity scan/clear on inactive draws. Each context immediately rejects
inactive or unavailable cases; only two fixed record descriptors are checked.
At fade start, copy active no-HUF RGB,lowerowner,textowner: maximum
212928 /851712bytes. Ordinary finish does not copy/replay text pixels again.
Original glyph callback work and alpha blending are bounded by the actual command
count<=100 and each verified glyph<=6x8logicalcells, per record. Fade/removal scans
only active extents/owned subpixels, never the full image for this feature alone.

Persistent backdrop/post arrays cost2*(416+1792)=4416indexedbytes. Ownership may
use one logical bit/byte per cell because output-stage reconstruction owns each
modified wholelogical block for fade, including removed classic ink. No RGB
underlay is needed because the approved boxes have no otherHD owners.

## Fade, removal and required proofs

At solid fade start, save the current no-HUF underlay and masks. Hidden lowerHD
pixels follow the exact rounded per-channel fade recurrence; hidden classic
pixels use their verified original posttext index under the current palette.
Restore targets saved no-HUF RGB, not the authored glyph image. Removing text
restores only still-owned current/saved subpixels and corresponding sceneHDowner;
other scene/HUD families survive. Lease/layout/density/generation or palette trust
failure rejects pending cache rather than reading a freed source or guessing.

Required scalar/source tests: all byte/control/metric commands, exact fivepass
ordering, every mismatch point, unsupported late equal-index writes, later normal
occlusion then whole-record strip, non-normal/direct/expanded writer coverage,
alpha holes over original ink, source replacement, no glyph provenance leaks,
empty/missing/gamma/unsupported-context exactness, coherent accent/overflow fallback,
message shortening/replacement/expiry/endLevel/help erase history, and current/saved
black/white/restore no-HUF counterfactuals at4x/8x. Actual2x thin-gray readability,
score update and outside-owned/state/RNG exactness remain separate trial gates.
