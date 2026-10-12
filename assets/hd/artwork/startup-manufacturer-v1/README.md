# Generated manufacturer startup artwork, MFG1 V1

Only the frozen, reviewed PIC10 (XSIV) and PIC12 (ECLIPSE) generated artwork is
included. The selected imagegen masters and canonical RGB PNGs are unchanged.
The original offline pilot README and inventories are retained under
`provenance/`; those inventories describe the prior pilot, not this import.
`import.json` records every copied input and the deliberately omitted images.

No original game pixels or runtime captures are shipped. The two labeled
original-vs-pilot comparison PNGs and two full original-reference PNGs were
excluded. The source identities, palette signatures and review results remain
as textual provenance. `FILES.txt`, `SHA256SUMS` and the repository manifest
describe the exact imported source inventory.

## Deterministic build without game files

Use CPython 3.12 and Pillow 12.3.0. From any working directory:

```
python /path/to/startup-manufacturer-v1/build_resource.py --output /new/pack
python /path/to/startup-manufacturer-v1/build_resource.py --from-masters --output /new/source-only-pack
python /path/to/startup-manufacturer-v1/build_resource.py --validate /new/pack/startup-pic10-v1.hda /new/pack/startup-pic12-v1.hda
```

The first form appends alpha 255 to the canonical 1280x800 RGB PNG pixels. The
second rebuilds those pixels directly from the frozen generated masters with
the documented full-image LANCZOS registration. Neither needs original game
files, a game executable, a runtime pack or original-pixel review images.
The preserved `build_previews.py` also regenerates the four reviewed preview
PNGs; its optional external original-reference input is unnecessary.

## Exact resource layout

Each file is exactly 4,096,064 bytes: a 64-byte little-endian `<4s7I4Q>` header
and 4,096,000 row-major RGBA bytes. Header order is magic `MFG1`, version 1,
density 4, one-based PIC ID, zero-based palette ID, logical width 320, logical
height 200, payload bytes 4096000, decoded original index FNV-1a64, original
palette RGB FNV-1a64, payload FNV-1a64, reserved zero. FNV uses offset
14695981039346656037 and prime 1099511628211; these are non-security
compatibility/corruption stamps. Repository SHA-256 checks additionally freeze
the complete generated payload and all retained inputs.

Runtime resources live only in `assets/hd/packs/startup-manufacturer-v1/` and
are described by the separate `startup_manufacturer_v1` manifest section.
They are not HDR1 gameplay entries and do not change gameplay default packs or
their counts. This source package is not evidence of runtime fade/skip testing.
