# Stable terrain23 deterministic authoring

This is the authoring portion of an independent **private candidate**. It reproduces the accepted23 terrain HDA files from three frozen, source-referenced generated raw PNGs and the caller's matching, legally obtained original game data. It does not run the game, compile, download data, regenerate artwork, publish, or establish redistribution rights.

## Scope and ownership

- Ground10, selected calibrated v2:372,380,390,367,368,376,378,386,387,388.
- Cliff12, selected v1:361,362,363,364,365,371,373,374,375,381,382,383.
- Corner366, selected v1:366.
- Pit4, redlamp, rejected380v3 and rejected380v4 are excluded. Accepted380 remains unchanged.
- Runtime integration, registration rows and the selected runtime pack are maintained separately. **The existing runtime loader's12×84=1,008-byte original-derived cliff mask table remains unchanged and is explicitly disclosed.** This producer does not delete/rewrite that table or alter its alpha-validation contract.

## Caller-supplied legal original data

No original `.dat`/`.lvl` data, fixed full palette, original indices, source reference PNGs or copied native masks are included in this authoring directory. Supply these exact supported inputs yourself:

| File | Bytes | Required SHA256 |
| --- | ---: | --- |
| shapesz.dat | 318976 | 3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248 |
| palette.dat | 18432 | f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0 |

The producer derives palette bank5, **zero-based**, at offset3840, length768, with `(v << 2) | (v >> 4)` per channel. Its expanded hash must be `d4c24a49efb588abd6dc1ffd0f0d1279a498c422cdd26fba4fc921b07f8c159f`. It does not substitute bank0 or use a captured live-palette file.

Shape parsing follows600 records with one-byte blank flags and672 index bytes for each nonblank24×28 tile. The supported file has520 trailing bytes after the records. Input hashes, parsing bounds and selected native tile hashes are checked. There is no download or bundled-original fallback. Input files, raw PNGs and output-pin metadata must be regular files, with no symlink in their path. Before opening them, the producer checks file type and fixed original/raw sizes or a64KiB metadata limit. It then verifies the opened descriptor and uses a bounded read. FIFOs, devices, directories, oversized files and input symlinks are refused without waiting for data. Provenance JSON is documentation, not read by the producer.

## Replay environment

The producer enforces the exact environment used for byte reproduction:

- CPython3.12.14
- Pillow13.0.0
- NumPy2.3.5
- SciPy1.17.0

`requirements-terrain23-authoring.txt` pins the three packages. SciPy supplies Euclidean contour distance. Other dependencies are Python's standard library. The script never installs dependencies. No game executable, SDL, compiler, OpenCV, image-generation call or C2PA verifier is required for byte reproduction.

## Run

From the source root, with your original files outside this source tree:

```sh
python -B scripts/build_current_terrain23.py \
  --shapesz /absolute/path/to/legal-data/shapesz.dat \
  --palette /absolute/path/to/legal-data/palette.dat \
  --output /absolute/path/to/new-terrain23-output
```

The output parent must already exist. The output directory must not exist and must be outside the source/artwork tree and not overlap an input. Existing empty/nonempty output directories and dangling output symlinks are refused. There is no force/overwrite mode. All input, raw, palette and output byte checks complete in memory before output creation. A second build needs a different new directory.

Success writes exactly23 `terrain-shapesz-ID-8.hda` files and `authoring-report.json`. It does not write source images, palette copies, indices or masks. Each HDA is172060 bytes: little-endian `<4s6I` header (`HDR1`,2010000+ID,8,24,28,0,0) followed by192×224 RGBA8. `OUTPUT-PINS.json` contains all expected native/raw-derived PNG/HDA/payload hashes and crop boxes, not source pixel arrays.

## Frozen generated inputs and provenance

All are under `assets/hd/artwork/shapesz-terrain23-v1/`:

| File | SHA256 |
| --- | --- |
| ground10/raw-family-v2.png | 14c51a8b55e21846de4afabcb06c8ea61559b7148cddca1ce1d7f7b38bd389fe |
| cliff12/raw-cliff-v1.png | b39c7f2883eb50b137a82325f0c3aed2362c1986af1e8c09a9c41da49d9b9c6b |
| corner366/raw-v1.png | a7246580459c9fc6d0e06ba65b33e67da4a8ff554fb53b30a756bfc9f7fa4680 |

Each group retains its exact prompt and a small provenance record. Ground10v2 came from a generated v1 edit using the original atlas as geometry/brightness reference; v1 hashes and that dependency are disclosed without bundling original references. Cliff used original cliff geometry plus accepted372 material. Corner used original366 geometry plus accepted367/376 material. Prompts record provenance; they cannot deterministically regenerate these exact raw bytes.

The raw files are copied **byte for byte**, retaining their original `caBX`/C2PA metadata. Marker/container presence was checked. **No cryptographic C2PA signature-chain verification is claimed.** Registered PNG calculations and HDA outputs are separately hashed derivatives, not C2PA-verified outputs. Metadata preservation and generated provenance do not settle rights to source-referenced artwork.

## Exact registration

Ground10 uses5×2 crops in the listed order, Python-rounded crop boundaries, LANCZOS resize to192×224, original-minus-generated8×8 block-mean RGB correction expanded as float32 with BILINEAR, then clamping. It blends with original nearest8× RGB using `clip((zero_based_rectangle_edge-1)/7,0,1)`, rounds with NumPy `rint`, and quantizes by squared RGB distance to each source tile's sorted unique indices. Outer2 HD pixels stay exact original RGB. All pixels are opaque.

Cliff12 uses6×2 crops;366 uses its full raw. Both use the same block-mean correction, with zero correction in native source0 cells. The source nonzero mask is locally derived and expanded8×. Boundary distance is the minimum of padded-mask Euclidean distance and one-based rectangle edge. Distance≤2 keeps original colors; `clip((distance-2)/6,0,1)` gives the feather. Raw alpha multiplies the blend weight over original pixels. Quantization excludes index0 and uses only each tile's original palette. Output alpha is the original nonzero mask, not generated alpha; transparent RGB is0. Tile366 is fully opaque.

The producer preserves crop order, rounding, float operations, palette tie order and PNG encoding for an in-memory intermediate-hash check before writing HDA. Any mismatch fails rather than selecting a nearby result or adjusting art. There are no variants, rerolls or automatic tuning.

## Original-content disclosure and future scope

These assets intentionally retain original geometry, palette colors, broad lighting and boundaries. Across23 tiles, **36,781 HD pixels lie in mandatory exact original-RGB lock regions**. Cliff raw-alpha gaps additionally retain original pixels. This count does not imply all other pixels are wholly new. The generated raws themselves follow original references; the accepted HDA are not “100% newly drawn.”

The runtime's retained1,008-byte cliff mask table can reconstruct the12 original native silhouettes. It is deliberately disclosed and preserved for this private candidate. A separate mask file is unnecessary as an authoring input because masks are derived from the caller's indices; that does **not** exclude the existing runtime table from this repository. Future public distribution of raw derivatives, HDA or runtime mask constants needs a separate explicit scope review. Local derivation or removal of runtime masks is only a possible future design, not implemented or required here. Excluding original DAT files is not redistribution clearance.

## Tests

Non-data negative checks and frozen-input checks:

```sh
python -B -m unittest discover -s tests -p test_terrain23_authoring.py -v
```

This explicitly skips data-dependent reproduction tests unless both legal input paths are supplied. To include them:

```sh
TERRAIN23_TEST_SHAPESZ=/absolute/path/to/legal-data/shapesz.dat \
TERRAIN23_TEST_PALETTE=/absolute/path/to/legal-data/palette.dat \
python -B -m unittest discover -s tests -p test_terrain23_authoring.py -v
```

Checks cover all23 exact HDA hashes/headers/alpha classes, frozen raw/C2PA presence, wrong/missing inputs, truncated parsing, source-tree/input overlap, missing output parent, input/ancestor symlinks, existing-output refusal and preservation of existing files. Additional negative cases cover a writerless temporary FIFO with bounded subprocess timeout, a directory, a safe character-device fixture rejected before opening, and oversized raw/metadata rejected before opening. The earlier14-test result did not cover the FIFO read-blocking gap; this extended suite addresses that gap without changing pixel registration. Explicitly supplied bad data fails the tests rather than being skipped. Tests create only temporary external outputs; no game, compilation, publication or user-computer action is involved. Authoring pass is not full runtime or platform acceptance.
