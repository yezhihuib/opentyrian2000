# Accepted MODE assembly V2: frozen HUL1 trial package

The accepted art covers both MODE lamp sockets and their center grille, plus the
unchanged top red lens. This is a separate runtime trial package. Runtime behavior
has not been tested here; the indicator trial follows the label/shield trial.

## Selected art and placement

Coordinates are logical pixels, with half-open rectangles.

| Asset | RGBA size at 4x | Logical placement | State |
| --- | --- | --- | --- |
| `lens-top-4x.png` | 28 x 12 | [269, 4, 276, 7) | Fixed red, both modes |
| `assembly-mode1-4x.png` | 108 x 32 | [285, 44, 312, 52) | Left lit, right unlit |
| `assembly-mode2-4x.png` | 108 x 32 | [285, 44, 312, 52) | Left unlit, right lit |

All three PNGs are byte-identical to their accepted pilots, with alpha 255 in
every pixel. `placement-state.csv` is the machine-readable state table.

The complete assembly owns 216 logical pixels: 82 locally replace existing frame
pixels (26 socket-rim and 56 grille pixels), and 134 are live-sprite-area pixels.
The separate top lens owns 21 pixels, for a combined 237. The four exact masks
are supplied as 320 x 200 L-mode PNGs and headerless row-major `.mask` files;
every mask byte is 0 or 255. The old 85-pixel lens-only scope is superseded.

## Deterministic generation

Both generated masters and both original generation prompts are included.
`reproduce_generated_only.py` reads only those masters, `manifest.json`, and
numeric geometry. It does not read game assets, a checkout, captures, or guides.

- Assembly: convert its master to RGBA, crop [138, 221, 1638, 666), then resize
  once to 108 x 32 with Pillow LANCZOS.
- Lenses: use the prior whole-crop RGB-to-LANCZOS-to-RGBA recipe recorded in the
  manifest. Paste the unchanged 32 x 16 lit/unlit lenses at (4, 8) and (72, 8),
  swapping their state for mode 2. The unchanged top lens is 28 x 12.
- Density 8 repeats each canonical 4x pixel as a 2 x 2 block. The native 2x
  preview uses nearest sampling of canonical 4x, not a new painting or filter.

Verified encoder environment: Python 3.12.14, Pillow 12.3.0, zlib 1.3.2. The Pillow
version is pinned in `requirements.txt`; matching the encoder environment is
necessary for byte-identical PNGs, in addition to matching decoded pixels.

Run twice into separate empty directories:

    python reproduce_generated_only.py --output-dir /tmp/hul1-build-a
    python reproduce_generated_only.py --output-dir /tmp/hul1-build-b
    diff -r /tmp/hul1-build-a /tmp/hul1-build-b

Both completed verification builds produced identical files and matched the
frozen expected exports. `repeat-build-proof.json` records the checks, decoded
sampling hashes, and an independent header-offset audit. SHA-256 and standard
FNV-1a64 are recorded for PNG file bytes and native decoded pixels. `SHA256SUMS`
and `FNV1A64SUMS` cover every package file except those two checksum indexes.

## HUL1 binding

`gameplay-hud-indicators-v1.hda` is exactly 29,072 bytes: an 80-byte little-endian
header (`<4s7I6Q>`) followed by 28,992 bytes of opaque RGBA8. Payload order:

1. Top lens: 1,344 bytes, file offset 80.
2. Mode 1 assembly: 13,824 bytes, file offset 1,424.
3. Mode 2 assembly: 13,824 bytes, file offset 15,248.

The header contains magic HUL1; version 1; density 4; sizes 28 x 12 and 108 x 32;
payload byte count; PIC3, palette, top-21, mode-1-full-216 and mode-2-full-216
source guards; and combined-payload FNV-1a64 `9496d22c5cd69c6e`. The manifest
lists every field offset and value. Masks are not stored in HUL1: fixed placement
and the exact 82-pixel overlap are compiled integration guards.

## Source guards and provenance

`source-state-contract.json` is reconciled for the accepted 237-pixel scope.
It retains all audited source hashes and the full-state construction recipe.
The old nested lens-only runtime paragraph is omitted; its original file hash
is retained in `provenance.json`. The authoritative mode guards cover all 216
original indexed pixels, including both full sprites and the PIC3 center.

Integration must respect source, palette, mode, fade, and modal ownership and
suppress unsupported or stale states. Do not replace the shared OPTION sprite
bank globally; shop use remains classic. No original PIC pixels or indices,
original sprite files, captures, or old edit guides are included. HUC1, HUD1,
the V5 frame, prior drafts, and the source repository were not modified. Nothing
was uploaded or published.
