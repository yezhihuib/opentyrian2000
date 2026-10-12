# Fixed green labels: frozen generated-only trial

This separate, reversible candidate freezes the accepted typography pilot for
MODE, SHIELD, and ARMOR. It owns exactly **370 logical cells** in 12 tiles and
contains no original PIC indices, font bitmaps, palette arrays, screenshots, or
capture payloads. Source references, measurements, and hashes are metadata only.
No repository, runtime, capture, upload, or publication changes are made here.

## Deliverables

- `gameplay-hud-fixed-text-v1.hda`: the 23,744-byte HUT1 resource.
- `tiles/`: 12 authored, opaque RGBA8 PNG tiles, canonical density 4.
- `selected-glyph-paths.json`: only the 10 selected authored vector glyphs.
- `fixed-label-mask-370.bin`: 320 x 200 row-major ownership bytes, 0 or 255.
- `fixed-label-mask-370.png`: the exact same ownership mask as an L-mode PNG.
- `build_assets.py`: deterministic, standalone art reproducer.
- `verify_package.py`: separate resource/layout/hash/pilot comparison verifier.
- `manifest.json`: exact tile offsets, geometry, alpha, hashes, and HUT1 layout.
- `provenance.json`: frozen source metadata and reference identities.
- `verification/`: direct comparison, source-scope, and repeat-build proof.
- `requirements.txt`: exact Python package versions used for the freeze.

Resource SHA256:
`6d096f31085b22fb381761d3c8460bd06956c2bd039a1e0cc97481bc09819745`

Payload FNV-1a64: `a2433de596bd3873`.

## Reproduce and verify

Use Python 3, `Pillow==12.3.0`, `numpy==2.3.5`, and zlib runtime 1.3.2.
The tested interpreter is Python 3.12.14. The reproducer checks the Pillow,
NumPy, and zlib versions before writing to protect PNG byte identity.

```sh
python build_assets.py
python verify_package.py
```

The reproducer reads only its adjacent `provenance.json` and
`selected-glyph-paths.json`. It does not import either pilot script, read game
files or font metrics, open reference images, or require a capture. It generates
the vector strokes and green gradient from formulas. It verifies every PNG
file and decoded RGBA hash against the frozen pilot references before writing.
Existing files with different bytes are refused; no files are deleted.

To preserve a fresh output set:

```sh
python build_assets.py --output /path/to/new-output
```

For a full self-contained package at another location, copy the two input JSON
files, both Python scripts, and `requirements.txt`, then run the reproducer there.
`verification/rebuild-a/` and `verification/rebuild-b/` retain two such independent
builds. Both were run with isolated Python from an unrelated working directory;
all generated outputs, including the manifest, are byte-identical to this freeze.

Optional direct pilot comparison, with no original game data needed:

```sh
python verify_package.py --pilot /path/to/hud-typography-pilot-v1
```

## Exact ownership and order

All logical rectangles are half-open. Each tile owns its entire rectangle,
including black, with alpha 255 everywhere. The payload order is fixed:

| Index | Tile | Logical rectangle | PNG size | Payload offset |
|---:|---|---|---|---:|
| 0 | MODE | [284,54,303,59) | 76 x 20 | 0 |
| 1 | SHIELD S | [285,138,290,143) | 20 x 20 | 6080 |
| 2 | SHIELD H | [285,144,290,149) | 20 x 20 | 7680 |
| 3 | SHIELD I | [285,150,290,155) | 20 x 20 | 9280 |
| 4 | SHIELD E | [285,156,290,161) | 20 x 20 | 10880 |
| 5 | SHIELD L | [285,162,290,167) | 20 x 20 | 12480 |
| 6 | SHIELD D | [285,168,290,173) | 20 x 20 | 14080 |
| 7 | ARMOR A | [296,138,301,143) | 20 x 20 | 15680 |
| 8 | ARMOR R | [296,144,301,149) | 20 x 20 | 17280 |
| 9 | ARMOR M | [296,150,301,155) | 20 x 20 | 18880 |
| 10 | ARMOR O | [296,156,301,161) | 20 x 20 | 20480 |
| 11 | ARMOR R | [296,162,301,167) | 20 x 20 | 22080 |

MODE is the complete accepted 19 x 5 rectangle, including its internal black
letter spacing: 95 cells. The vertical words comprise eleven separate 5 x 5
cells: 275 cells. Their one-row gaps and all surrounding black insets are
excluded. The mask is the exact accepted 370-cell mask, not the larger label
windows. There is no overlap with the existing HUD1 frame, HUC1 components, or
HUL1 indicators. HUC1/HUL1 geometry is independently checked by the verifier;
the actual HUD1 mask comparison is recorded in the source-scope proof.

## Frozen art formula

The selected normalized glyphs use the accepted 4 x 5 centerline grid. The
pilot's affine placement keeps a 0.36-unit inset. Its 0.72-unit strokes are drawn
at 32 samples per logical unit, clipped to the letter cell, then BOX-filtered to
4x. A vertical RGB gradient from (8,182,20) to (0,125,0) is multiplied by the
coverage and truncated to unsigned eight-bit RGB. The result is converted to
opaque RGBA. Black pixels are therefore opaque replacement pixels.

The script retains the pilot's floating-point operation order and Pillow line
join behavior. It reproduces the accepted pixels exactly; it does not use
original font pixels or rasterized source glyphs. Dynamic level text, score,
messages, and the separate 127-glyph atlas are outside this package.

## HUT1 contract

The header is exactly 64 bytes in little-endian format `<4s7I4Q>`.

| Byte offset | Type | Value |
|---:|---|---|
| 0 | 4 bytes | HUT1 |
| 4 | u32 | version 1 |
| 8 | u32 | density 4 |
| 12 | u32 | tile count 12 |
| 16 | u32 | logical cells 370 |
| 20 | u32 | payload bytes 23680 |
| 24 | u32 | layout ID 1 |
| 28 | u32 | reserved 0 |
| 32 | u64 | PIC3 FNV 14c1441f3d5dc0e2 |
| 40 | u64 | palette FNV 5e80e83992be2927 |
| 48 | u64 | source-370 FNV b110512dd1fc63f4 |
| 56 | u64 | payload FNV a2433de596bd3873 |

Payload begins at resource offset 64. Each tile is top-to-bottom, left-to-right,
row-major RGBA8 with no stride padding, separators, or trailing data. MODE is
6,080 bytes; each remaining tile is 1,600 bytes. Total payload is 23,680 bytes.

The 370 original source-index bytes used for source binding are gathered in
the **same tile order**, row-major inside each tile. They are not gathered by
scanning the full-canvas ownership mask. Their SHA256 is
`272f2995359bd118dd62cb3b597ad937034527a25180115b399f8978777c59f6`.
Only their hash is retained, not their bytes.

All FNV values use standard FNV-1a64, offset basis `cbf29ce484222325`, prime
`100000001b3`, modulo 2^64. Hex strings express numeric values; the header stores
those numbers little-endian. The reproducer includes empty, `a`, and `foobar`
known-answer tests.

## Verification boundary

The proof covers the 12 PNG files and decoded RGBA, all alpha bytes, exact mask,
geometry and gaps, source signatures, HUT1 fields, payload order, dimensions,
checksums, total resource size, and repeat builds. All original pilot and
existing package files remain unchanged. Every build and verification
intermediate is retained. This is an art-package freeze; no runtime activation,
fallback, rendering, gameplay, timing, fade, or capture behavior is claimed.
