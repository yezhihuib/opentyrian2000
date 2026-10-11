# Layer3 purple13 v3 generated-source handoff

The 13 selected terrain tiles are frozen to `runtime-overlay/manifest.json`, SHA-256
`b733a687a181ab6f1d7ec8d5d6bafdd4af91cd4d9c4cc956de4293ad3ee0b26a`.
The parent approved offline material, all nine static modular placements, shared
actor pairing and connector-tone-v3. **Actual component-death runtime acceptance
is pending.** This package does not claim integration or gameplay verification.
The engineer owns the main repository and integration. This packaging task ran
neither the game nor Git, and did not edit the main checkout or private v1/v2/v3 work.

## Finite integration contract

Layer3 terrain IDs in ascending slot order 290–302:

`150, 156, 157, 158, 159, 160, 166, 168, 169, 170, 176, 177, 178`

All have scale 8, logical size 24×28, anchor (0,0), decoded size 192×224 and alpha
255 everywhere. Each HDA is exactly 172,060 bytes: `HDR1`, six little-endian U32
values `[2010000 + ID, 8, 24, 28, 0, 0]`, then 172,032 straight RGBA bytes. Slot
assignment belongs to the manifest, not to the HDA header. No palette, geometry,
map placement, renderer, binder, gameplay or other asset is changed here.

## Authored source and selected transformation

The standalone source entry points are the 13 v1 generated PNGs in
`source/generated-crops/`. Each was cropped from the registered generated
2112×1344 atlas using `source/selected-crops.json`, then made opaque without
changing RGB. Private read-only comparison confirmed all 13 crops exactly.
`source/authored-crop-provenance.json` records the private generated/registered
master hashes and normalization. The full masters and authoring reference canvas
are excluded. Image generation is not claimed reproducible from the prompt;
deterministic reproduction begins with the included authored source crops.

The builder assembles nine of these crops as a 576×672 foundation:

    156 157 158
    166 150 168
    176 177 178

It freshly compiles the exact frozen `source/match_exposed_connector.cpp` as
C++17 and runs it with `source/actor-adjacent-strip16.png`, decoded as actual
576×16 pixels. Any virtual-canvas/page metadata is irrelevant. This generated-only
reference consists of the last eight rows of partner actor frames 245/169/207
above the first eight rows of 273/275/277. The six sources, crop rectangles,
hashes, ownership and private master hash are documented in
`source/actor-reference-provenance.json`. Packaging independently reassembled the
strip from those six generated frames and verified exact RGBA. Full actor frames,
masters, masks and original references are not distributed.

The helper changes only RGB in assembled rows 440–455 inclusive. Cropping back
produces exactly six overrides: 166/150/168 rows 216–223 and 176/177/178 rows 0–7.
Maximum absolute per-channel RGB delta is 20. The actual changed pixels are
gated within those row bounds; every other pixel, alpha sample and geometry field
stays exact. Seven tiles remain unchanged: 156/157/158/159/160/169/170. All 13 HDAs
are then packed from reconstructed pixels, never copied as a substitute for
reconstruction. Independent comparison counts exactly 6,054 changed HD pixels.

## Static coverage versus runtime evidence

The upstream static family audit covers **64 cells in nine motif placements**:
one 5×2, two 3×2, two 3×3, three 2×2, and one cross with 4×4 bounds and 12 occupied
cells. Nine means placements, not nine distinct dimensional shape classes.
The recorded 2088–2609 window observed only nine unique purple IDs:
150/156/157/158/166/168/176/177/178. The cross-center IDs 159/160/169/170 are static
family completion. Neither that window nor offline composites establish all-13
runtime coverage. No original map arrays are included.

The paired actor rows are 279/281/283, 245/169/207, 273/275/277, with logical
row origins 0/27/57 against terrain 0/28/56. Preserve the entity offsets 0/−1/+1,
actor anchor (6,7), and terrain anchor (0,0). Actor pieces have independent link0
death: only the struck component disappears and reveals the persistent broken
terrain; the other pieces remain. Do not flatten the assembly or convert it to
group removal. Actual component hits/deaths and all-nine removal remain a
separate runtime gate. See `verification/topology-and-runtime-boundary.json`.

## Standalone rebuild

Requirements: Python3 with Pillow, a C++17 compiler available as `c++`, and Bash
for the wrapper. No game files, original art, NumPy, ImageMagick, network, image
generation service or main checkout is needed.

    bash rebuild-selected.sh "/absolute/new output directory"

Or:

    python3 source/rebuild_selected.py --output-root "/absolute/new output directory"

The destination must be new and outside this immutable package. The builder
checks source and selected hashes, the fixed manifest, all IDs/slots/HDR1 headers,
the exact six finite RGB regions and alpha255. It verifies the inventory when
present, freshly compiles the helper, rebuilds all 13 RGBA/HDA payloads and
checks that the package was not modified. Intermediate raw RGBA and the compiled
helper live only in the disposable output's `work/` directory.

The committed PNG byte hashes are checked separately from regenerated PNG
encoding. A PNG encoder may produce different file bytes with identical RGBA.
The seven unchanged source PNGs are copied byte-exact; the six transformed PNGs
are freshly encoded by Pillow. Exact decoded RGBA and HDA equality, not encoder
identity, are the reproduction guarantees. The report also records the number
of regenerated PNG files that happen to be byte-identical in the tested environment.
In this tested environment, 7/13 regenerated PNG files are byte-identical; all six
newly encoded overrides differ only in PNG encoding. All 13 committed selected
PNG hashes pass independently, and all 13 reconstructed RGBA/HDA payloads are exact.

Independent read-only scope check, using the packaged selected output by default:

    python3 source/verify_scope.py
    python3 source/verify_scope.py --rebuild-root "/absolute/rebuilt output directory"

## Package boundary and evidence

This package contains 14 generated source PNGs (13 authored terrain crops plus
one tiny generated tone reference), 13 selected PNGs and 13 selected HDAs, along
with prompts, source, provenance and verification records. It excludes original
game rasters/data/masks, full masters, runtime captures, prebuilt executables and
archives. `OWNERSHIP.md` distinguishes project source attribution from licensing
claims about game assets or AI output.

`handoff-inventory.json` lists every other file's bytes and SHA-256, excluding
itself to avoid self-hashing. The verification records include exact rebuilding,
independent finite-region auditing, generated-source provenance, package boundary,
and a second rebuild after relocating the package into a path containing spaces.
