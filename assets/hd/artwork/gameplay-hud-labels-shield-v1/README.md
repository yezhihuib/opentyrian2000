# Fixed labels + shield V2: frozen trial art

Generated-only art for the explicitly approved actual trial. This package does
not modify the repository, runtime, V5 frame, or V1/V2 pilot artifacts. It contains
no original PIC pixels/indices, screenshots, captures, or full original palette.
The source references and checksums in `provenance.json` are audit records only.

## Deliverables

- `gameplay-hud-components-v1.hda`: the integrator-specified HUC1 resource,
  **38,592 bytes**, SHA256
  `c40c9ecf16a0d654876597195880deb484c17e36b1d1a17a9c1a241fb2b26d33`.
- `tiles/`: 20 opaque RGBA8 PNGs: four fixed labels, 14 V2 blue bands,
  one black track and one brown marker. Every alpha byte is 255, including black.
- `build_assets.py`: standalone deterministic authoring/reproduction script.
- `manifest.json`: resource layout, assembly contract, source references/hashes,
  checks, and both decoded/file SHA256 and standard FNV-1a64 for every tile.
- `provenance.json`: frozen input references/hashes and reference-region hashes.
- `verification.json`: direct source comparisons and repeat-build result.

The track and marker are standalone assembly/proof tiles. They are deliberately
absent from HUC1: the runtime retains the original indexed black/marker output.

## Reproduce

Use Python 3 with `Pillow==12.3.0` and `numpy==2.3.5`, as in `requirements.txt`:

```
python build_assets.py
```

The script reads only its own `provenance.json` and writes only inside this
package. It does not import or execute either pilot script, read game files, open
source images, or require reference captures. It recreates the label vector
strokes, constrained phosphor halo, and exact V2 scalar-luminance material from
readable formulas and explicit needed palette-role RGB constants. Frozen decoded
hashes assert the exact accepted 4x label and M10 shield pixels on every rebuild.
PNG encoding and rasterization dependency versions are checked before writing.
The generated RGBA and HUC1 bytes are authoritative.

## Label scope

Logical coordinates are half-open; the density is exactly 4 pixels per logical
unit. The four boxes total **350 logical pixels** (source audit: 215 ink, 135
black). Ownership includes every black pixel in each box.

| Ordered label | Logical rectangle | RGBA tile size |
|---|---|---|
| FRONT | [285,5,309,10) | 96 x 20 |
| GUN front | [285,11,299,16) | 56 x 20 |
| REAR | [285,26,303,31) | 72 x 20 |
| GUN rear | [285,32,299,37) | 56 x 20 |

MODE, live digits, level bars, lamps, generator, and sidekick art are not included.

## Shield assembly

The channel is [270,137,279,195), exactly 9 x 58 logical or 36 x 232 at 4x.
`assemble_shield` is a reference assembler; it does not infer game events or
simulate state. It rejects non-integer values and values outside 0 <= S <= M <= 28.

1. Begin with the opaque black 36 x 232 track.
2. For an explicit active draw, draw **z=0 through S inclusive**. The tile role is
   `146 + max(0, floor((z-1)/2))`. Paste each 36 x 8 tile at local
   `(0, 4*(56-2*z))`, equivalent to logical [270,193-2z,279,195-2z).
3. If S differs from M, paste the opaque 36 x 4 marker, RGB (85,28,16), at local
   `(0, 4*(56-2*M))`, equivalent to logical [270,193-2M,279,194-2M).
4. A wipe-only/inactive event returns just the black track. It never manufactures
   a baseline by inspecting S=0. An active S=0 draw does contain its one baseline.

S=0/M=0 therefore has one band at 4x rows 224..231. Active S=28/M=28 has 29
bands covering the entire channel, with role159 at the top. Capacity is never
normalized to the channel height. The marker does not appear when S=M.

Every blue band preserves V2's hue-preserving scalar luminance lift, narrow ridge,
side recession, and internal seam at the exact 4x pixels. Roles 146..159 all have
fixed generated tiles. The same bounds/formula assemble every valid S/M pair;
only the three supplied M10 fixtures were compared with captures, with no sweeps.
For density8, replicate every 4x RGBA pixel exactly 2 x 2 using nearest neighbor.
Do not rerasterize, interpolate, or resample the material at density8.

## HUC1 binding

All integers are little-endian. The header is exactly 64 bytes, followed by
22,400 label RGBA bytes and 16,128 band RGBA bytes, with no padding or other data.
The Python struct layout is `<4s7I4Q`.

| Offset | Type | Value |
|---|---|---|
| 0 | 4 bytes | HUC1 |
| 4 | u32 | version 1 |
| 8 | u32 | density 4 |
| 12 | u32 | label count 4 |
| 16 | u32 | label RGBA bytes 22400 |
| 20 | u32 | band count 14 |
| 24 | u32 | band width 36 |
| 28 | u32 | band height 8 |
| 32 | u64 | PIC3 index FNV 14c1441f3d5dc0e2 |
| 40 | u64 | labels FNV c24e8ce447f9f0e8 |
| 48 | u64 | bands FNV 20b6e884fe4a23ce |
| 56 | u64 | normal palette RGB FNV 5e80e83992be2927 |

Label payload at offset64 uses the ordered labels above. Bands at offset22464
use palette roles146 through159 in ascending order. Each tile is top-to-bottom,
left-to-right row-major RGBA8 without stride padding. Density4 sizes are fixed.
The PIC3 source signature was supplied by the integrator. The palette signature
was verified over the reference indexed PNG's 256 expanded RGB triples (768
bytes), before gamma/fade. Only its checksum and needed RGB roles are retained.

All FNV values use standard FNV-1a64, offset basis14695981039346656037
(hex cbf29ce484222325), prime1099511628211 (hex 100000001b3), unsigned modulo2^64.
Hex strings express the numeric value, not the little-endian byte order.
Known-answer checks for empty input, `a`, and `foobar` are built into generation.

## Verification scope

- All four generated label tiles equal their supplied V1 counterparts after
  explicit opaque RGBA conversion, byte for byte.
- The complete assembled channel and all four labels equal the corresponding
  regions in each supplied V2 S10/M10, S5/M10, and S1/M10 4x frame, byte for byte.
- Every generated tile is RGBA with alpha255 everywhere.
- Active S0/M0 and wipe-only blank are demonstrably different outputs.
- HUC1 header, counts, dimensions, checksums, offsets, and total size match the
  supplied binding exactly; two successive builds produced identical files.
- This is an art-package proof. It does not claim runtime activation, lifecycle,
  fallback, collision, gameplay, timing, fade, or rendering integration tests.
