# Explicit RFR3 reconstruction

These 171 whole-run resources are a new, versioned reconstruction, not byte-identical recovery of the missing RFR1/RFR2 files. The original target metadata remains unchanged in `assets/hd/manifest.json`; new output hashes and original comparison hashes are in `reconstructed-manifest.json`. Only the separately identified numeric NFR1 file is byte-identical to its original target.

## Header and compiled admission

Every resource has exactly 64 header bytes. All integers are little-endian. Python serialization is `<4s4I2i3I3Q`.

| Offset | Type | Meaning |
| --- | --- | --- |
| 0 | four bytes | `RFR3` |
| 4 | u32 | version 3 |
| 8 | u32 | header size 64 |
| 12 | u32 | width |
| 16 | u32 | height |
| 20 | i32 | signed x bearing |
| 24 | i32 | signed y bearing |
| 28 | u32 | natural whole-run advance256 |
| 32 | u32 | planes, 2 or 3 |
| 36 | u32 | compiled role-profile ID |
| 40 | u64 | exact display ASCII text FNV1a64 |
| 48 | u64 | payload FNV1a64 |
| 56 | u64 | first eight font SHA256 bytes, interpreted little-endian |

Width, height and bearings are canonical4 pixels: four canonical pixels per logical pixel. `advance256` is canonical4-pixel advance multiplied by 256. For example, None's 16948 represents 66.203125 canonical pixels or 16.55078125 logical pixels. Density is compiled as 4; the file cannot choose it.

Payload is face alpha8, then palette-role8, then full contour alpha8 only for MAIN. Each plane is width times height. The resource is exactly 64 + planes times width times height bytes. MAIN contour includes the face and must satisfy contour >= face at every sample. Face alpha is zero exactly where role is zero. Transparent counter interiors stay transparent.

`reconstructed_run_specs.h` is the generated admission authority: fixed family and ID, filename, exact display text, metrics, profile, plane count, role interval, text/font/payload pins, full-header FNV, full-file FNV, and file SHA256. Header values are claims to compare with this compiled specification, not instructions to broaden bounds or select arbitrary rendering behavior. Reject truncation, extra bytes and any mismatched metadata. Family count/order and aggregate byte accounting are generated too.

Families are ESC0, MAIN1, SHOP2, CATEGORY3, PRODUCT4 and NAMES5. Profiles1..9 are ESC medium; MAIN contour; SHOP heading/choice; CATEGORY heading/choice; PRODUCT heading/tiny; NAMES upright. Runtime must retain each original family's source witnesses, shadow/color operators and independent failure/cache lifecycle. The resource generator does not authorize a draw by itself.

## Typography and visual review

Pinned DejaVu Sans Condensed Bold at supersampled sizes219/288/131 supplies medium/heading/fixed-tiny whole runs. Pinned upright OSIfont at size128 supplies names. Natural RAQM advances and source word spacing are preserved; there is no per-glyph or per-run scaling or stretch. Name baseline96 is an explicit reconstruction decision, not a claim of recovering the missing generator's baseline.

Rasters use whole-string FreeType rendering and BOX reduction by4. MAIN uses true FreeType stroke radius8 supersampled pixels, equal to2 canonical pixels or0.5 logical pixel, not four shifted face masks. Medium and heading gold roles13..15 continue through descenders without a baseline stripe. Fixed tiny PRODUCT and NAMES are role7. Original family-specific native brightness, hue, shadow, ordering and hitboxes are runtime responsibilities.

The representative specimen was inspected before generating all171 runs, including MAIN High Scores/Instructions and upright Pulse-Cannon/Multi-Cannon/Vulcan Cannon. Open C and counters, natural spaces, continuous descenders and lighter OSIfont were checked. `representative-rfr3-specimens.png` is a font specimen with an illustrative background and colors, not a native engine screenshot or evidence of indexed/runtime parity. The right column is labeled `2x scale specimen`.

## Reproduce

Run `python assets/hd/shared-menu-runs-v1/rebuild_reconstructed.py --out NEW_DIRECTORY` from the repository. Pinned Pillow12.3.0, FreeType2.14.3 and RAQM0.10.5 are required. The script never writes to a directory named frozen and never writes numeric NFR. An existing RFR1/RFR2 resource cannot be overwritten. It validates all original geometry/size constraints and127 retained advances while recording new hashes.

## Exact numeric resource and new specs

`numeric-runs-v1.nfr` remains the exact original 41,110-byte resource, SHA256 `7becf23de59c40582992f3c8caeea4b953405f014f86a070b0d25cef63f4878d`, Git blob `9fb2d2fb5f3c8adbfa3da7fb51609db6e7cab99c`.

`rebuild_numeric_reference.py` reproducibly creates this exact resource and new C/reference specs. It verifies an existing resource without rewriting it. `reconstructed_numeric_specs.h` exposes64 mask offset/width/height records,12x64 phase records, token literals and advances64, plus file/header/payload/font pins. Numeric advances64 are canonical4 pixels multiplied by64. For signed cumulative pen P64, use a floor quotient and nonnegative residue modulo64. Descriptor x/y are already offsets relative to that quotient and the caller's top; do not apply an additional baseline transform. The entire Cost prefix includes its trailing space in the natural advance. Never round each character independently.

Fresh resource verification includes1,832 independent whole-string RAQM comparisons with zero mismatches and zero nonzero-alpha overlaps. These do not replace runtime source, malformed-resource, support, ordering, lifecycle, cross-family isolation, gameplay/INDEX8/RNG/input/audio/settings/Present tests.
