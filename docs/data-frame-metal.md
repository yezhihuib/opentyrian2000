# Optional Data static metal frame

The independent optional Data frame upgrades static metal on Data list/reader
pages (menu IDs 7/8), including the distinctive oval portrait surround. All 18
portraits remain native dynamic sprites in this pass. List cubes, English
glyphs, Chinese text, progress/Exit and cursor stay live. No text, characters,
equipment or shop armor/shield widgets are baked into the art. Other menus,
Help and the existing PSP1 source-projection policy are unchanged.

## Installation and fallback

Pass the resource's absolute directory independently of startup/shop and text:

    ./opentyrian2000 --data=/absolute/original-data \
      --data-frame-assets=/absolute/assets/data-frame-v1

Only `data-frame-v1.hda` is a runtime art input. Both packaged launchers pass the
package-relative directory as an absolute path before entering the save profile.
Without the option, the default relative directory is `assets/data-frame-v1`.
An unavailable resource (or an explicit empty/missing directory) retains the
native background. A missing, malformed or
unauthenticated frame must fall back to the native background without disabling
valid optional Chinese resources. The frame does not depend on loading a Chinese
font, and native English cursor preservation remains required.

## Source and reproducibility

`assets/data-frame-v1/source-v3.png` is the accepted 676x744 RGBA imagegen output,
SHA256 `34c464d5a05d0dd091a4d1cb3a11d53567ab094768bdb8253b27fcd35d53904d`.
It was normalized once with Lanczos from the generated 1195x1316 v3. The retained
PNG is unchanged. Full v1/v2/v3 generation prompts, source/generated hashes,
and original source identities are retained beside it. No earlier large
generated PNG, original game-data file, native portrait PNG, or font source is
needed to reproduce this resource. Added PNG payload is 701041 bytes.

Run with Python and Pillow 12.3.0:

    python3 scripts/export_data_frame.py

The exporter authenticates all retained inputs. It decodes accepted PMF1
without changing any RGBA samples, discards its contribution in cells owned by
the original clear rectangle `[1,1,146,171)` or exact OPTION20 opaque source
mask, then alpha-composites the surround at `(4,4)` on the 1280x800 canvas.
Same-index writes still own their cells; ownership is never inferred from final
pixel colors. The retained 64000-byte 0/1 support mask maps exact OPTION20
ownership at logical `(1,1)`. Its fingerprint is checked against the original
169x186 0/255 mask. The runtime pins include its 3930-byte LSB-first bitpack,
local bit index `y*169+x`, with six final zero padding bits.

The candidate's resource contribution alone is clipped to exact source support
dilated by two logical cells, 8 canonical pixels, using Chebyshev distance.
This explicitly reviewed geometry bound belongs only to DFM1 Data static metal;
PSP1 retains its separate one-logical-cell rule. The source PNG is not painted,
hard-cut, resaved, recolored, made opaque, or sharpened. The resource clip removes
13598 faint alpha > 0 samples (alpha sum 13683), with zero removed alpha > 127
samples. Every allowed candidate sample remains unchanged before compositing.
Slight missing source-core coverage is not concealed by forcing opacity;
runtime reconstruction of the true pre-OPTION underlay prevents old ring pixels
from leaking through transparent samples.

See the retained [provenance](../assets/data-frame-v1/DATA-FRAME-PROVENANCE.txt)
and [license status](../assets/data-frame-v1/LICENSE-Data-Frame.txt). The GPL
code license does not invent a license grant for original game artwork.

## DFM1 format

The whole file is 4096128 bytes: 128 header bytes followed by a fixed
4096000-byte full 1280x800 straight-RGBA8 payload. Allocation sizes never come
from an untrusted file. The loader must pin all fixed/header/reserved fields,
exact file length, payload FNV1a64, whole-file FNV1a64, original source identity
and effective high-palette identity.

Header bytes 0..3 are DFM1. Fifteen little-endian uint32 values at byte 4 are:

    1,320,200,4,1280,800,4096000,169,186,1,1,2,0,0,0

Eight little-endian uint64 values start at byte 64: PIC1 decoded index hash,
OPTION20 RLE hash, OPTION20 decoded index hash, OPTION20 opaque mask hash,
palette 0 high 208..255 RGB hash, payload hash, zero, zero. RGB uses VGA
expansion `(v<<2)|(v>>4)`.

- PIC1: `45a77a2246c174b9`
- OPTION20 RLE/index/mask: `3c232016c519ed17` / `03a1b83be967efe2` / `2f1faa16b55f7cfc`
- High-palette RGB: `dda550ae729ffb73`
- Payload FNV1a64: `9ea9dd7097643604`
- Whole-file FNV1a64: `f0ff3afc4b257334`
- Whole-file SHA256: `585ab4852480e2a4ff3e8df86bbc3a56d25ad797daafda83df54fa4015bc9f5e`

`src/data_frame_pins.inc` is generated with the resource. Bytes 112..127 are
reserved zero. This format does not reuse PMF1 or expand its menu allowlist.

## Composition and acceptance boundary

Keep the authoritative INDEX8 render, palette, game state, RNG and saves intact.
Capture authenticated PIC1 before clearing/drawing OPTION20, reconstruct the
native clear rectangle separately, and restore that true underlay across the
complete OPTION20 opaque support even when the candidate is transparent.
The independent frame then composes below native faces, cubes/English glyphs,
Chinese panels/text and actual cursor. Exact dynamic write masks must protect
same-index writes. Face sprites, including the 60 native occupied cells that
overlap original OPTION20 support, remain above the metal.

Fades/transitions and invalid ownership conservatively use native fallback.
Help/exit/load/save and public renderer invalidation revoke ownership; after a
reset the frame stays native until the next authenticated Data background
rebuild. Output
mapping respects letterbox offsets and repeated/changed output sizes. The
cursor uses a sparse full-canonical nearest-sampled plane to exactly match
native scaler footprints at fractional output sizes. Temporary cursor cells
also exclude static art, and cursor allocation failure suppresses optional
text panels before they can cover the native pointer.

Frame CPU buffers are fixed: 4,096,000-byte art, 4,096,000-byte output,
four 64,000-byte native arrays, plus a 4,096,000-byte SDL texture. Cursor
replay adds at most one 4,096,000-byte CPU plane and one SDL texture, both
released on text/renderer invalidation. Chinese atlas allocations retain their
existing bounds; no frame allocation size is taken from a resource header.

Renderer acceptance belongs to integration tests and real captures: list and
reader; English and Chinese; FACE0/FACE7/FACE15 and no portrait; 0/100% progress;
cube animation; cursor/F6/F1 return/fades; 1280x800, 640x400 and letterboxed
output; missing/corrupt resource with text still active; and native indexed/
simulation invariance for the same input. Offline exporter previews are art-fit
evidence, not renderer captures or a Windows/GPU acceptance claim.

Runtime selection adds only this HDA and provenance/license notices. Source
PNG, prompts, JSON, support binary and authoring code remain development-only.
Refreshing the source manifest does not rebuild any prior runtime directory
or ZIP, and no existing resource pack is regenerated.

## Local verification, 2026-10-19

- Strict production build and plain/UBSan core tests pass under separate 1 GiB
  build and 512 MiB runtime address-space bounds.
- Core tests preserve all 18 native portraits plus the intentional no-portrait
  state at 640x400, 1280x800 and letterboxed output, using native 2x/4x bases.
  They also cover 128 header-byte mutations, malformed/truncated/extra/payload
  resources, palette/source mismatch, FIFO/missing/allocation fallback, clipped
  rectangle and same-index writes, transition suppression and reset revocation.
- Final cursor replay compares whole output buffers against actual SDL nearest
  native textures at five viewports and two scaler densities, including
  fractional 1152x720, 1000x625 and 853x533 output.
- Paired actual software-renderer game runs cover English/Chinese list/reader,
  FACE0/FACE7/FACE15/no portrait, 0/100% reading, cube animation, F6, F1 return,
  cursor and native fallback during fades. INDEX8, palette and RNG match the
  same-input native-frame runs; Help and root output remain native.
- Original game data, native sprites, existing PSP1 one-cell guards, existing
  Chinese typography layout and translation/font resources are unchanged.

Windows source inventory is checked; Windows execution and GPU acceptance are
outside this local bounded verification. No resource pack or existing runtime
ZIP was regenerated, and nothing was uploaded.
