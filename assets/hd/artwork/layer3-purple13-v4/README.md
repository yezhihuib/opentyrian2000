# Layer3 purple13 v4 generated-source handoff

This standalone package selects the same 13 terrain tiles as v3 and adds only the
approved backing-fringe adjustment on terrain 176/177/178. The current selected
manifest SHA-256 is
`8b0d2ad2f11125657f5fea3739c5fae9368cc12a0e0e512919fc73ed5b936f3a`.
Offline amplitude and the bounded actual 120-frame replay were accepted by the
parent and entity reviewer. **The runtime label is private-survival plus controlled
independent removals, ticks 2540–2659.** All frame readback hashes matched; v3-to-v4
differences stayed within the six approved terrain/actor fringe regions; HUD was
exact. Actual crops at 2540/2625 matched the approved offline prediction. A minor
remaining cobble-phase difference is explicitly accepted. This is not a claim of
normal-play difficulty/timing, all-map coverage, or absence of every texture seam.
See `verification/runtime-acceptance.json` for bounded evidence and attribution.

The engineer owns the main repository and integration. This task did not edit the
main checkout, publish, run Git, or run the game. The independently audited formal
v3 package is retained unchanged as rollback.

## Exact scope

Terrain IDs in ascending slot order 290–302:

`150, 156, 157, 158, 159, 160, 166, 168, 169, 170, 176, 177, 178`

All retain layer 3, scale 8, logical size 24×28, anchor (0,0), decoded size
192×224, and alpha 255 everywhere. Each HDA is exactly 172,060 bytes: `HDR1`, six
little-endian U32 values `[2010000 + ID, 8, 24, 28, 0, 0]`, then 172,032 straight
RGBA bytes. Slots belong to the manifest, not the HDA header. No geometry,
placement, palette, renderer, binder, gameplay or other asset is changed here.

Compared with exact connector-tone-v3:

- Only 176/177/178 change, exclusively in RGB rows 208–223 inclusive. These are
  zero-based logical rows 26–27, the last two logical backing rows.
- Changed HD pixels are 2,617 / 2,706 / 2,732 respectively, 8,055 total. Every
  one of the 16 permitted rows has changes; the operation does not change every
  pixel in those rows. Each changed tile's inclusive bounds are (0,208)–(191,223).
- Maximum absolute per-channel RGB delta is exactly 28 on each changed tile.
  All changes darken or preserve channels, and alpha remains byte-exact.
- The other 10 committed PNGs and HDAs are byte-for-byte unchanged from v3:
  150/156/157/158/159/160/166/168/169/170. Every pixel outside the three finite
  fringe regions is exact to v3, including the accepted connector-tone changes.

The companion actor changes are outside this terrain package. Full actor frames,
actor fringe source strips, and actor runtime payloads are not included. The one
small v3 actor-adjacent tone strip is retained as an existing generated-only input.

## Generated-only deterministic source chain

1. Read the 13 canonical generated authored crops in `source/generated-crops/`.
   Their original atlas crop registration, opacity normalization and source hashes
   remain byte-exact in `selected-crops.json`, `authored-crop-provenance.json`, and
   the preserved v3 records. No full authored master is needed or included.
2. Reassemble nine crops into the original 576×672 foundation:

       156 157 158
       166 150 168
       176 177 178

   Freshly compile the unmodified v3 `match_exposed_connector.cpp` and use the
   canonical 576×16 generated-only `actor-adjacent-strip16.png`. Decode its actual
   pixels; virtual-canvas metadata is irrelevant. This recreates the six accepted
   connector overrides, bounded to assembled rows 440–455 and RGB delta 20.
   Verify all 13 intermediate v3 decoded RGBA and HDA hashes against the frozen
   v3 contract before beginning v4. These v3 pixels are reconstructed, never
   substituted from selected output files.
3. Freshly compile the original `apply_fringe_strip.cpp` and apply it separately
   to v3 terrain 176/177/178 using the three canonical 192×16 generated fringe
   PNGs. The helper uses generated luminance ratios, tapered attenuation, and a
   per-channel delta cap of 28. It preserves alpha and all other rows.
4. Encode the selected PNGs and freshly construct all 13 HDA payloads. Compare
   exact decoded RGBA and exact HDA bytes with the committed selected outputs.
   Independently audit the v3-to-v4 finite pixel differences and alpha contract.

Image generation is not claimed reproducible from prompts. Deterministic
reproduction begins with the included generated crops and strips. The new strips
were independently checked against their private generated registered source;
`source/fringe-source-provenance.json` records that check. The original upstream
`fringe-provenance.json` is preserved unchanged as provenance metadata: its
references to full masters, actor strips and other upstream files do not mean
those files are distributed or required. The upstream six-tile audit is represented
by its hash and terrain-only excerpt. No actor result is claimed by this package.

## Standalone rebuild and audit

Requirements: Python 3 with Pillow, a C++17 compiler available as `c++`, and Bash
for the wrapper. No game assets/data, main checkout, image-generation service,
NumPy, ImageMagick or network is needed.

    bash rebuild-selected.sh "/absolute/new output directory"

Or:

    python3 source/rebuild_selected.py --output-root "/absolute/new output directory"

The output directory must not exist and must be outside this immutable package.
The builder verifies the complete inventory when present, all canonical source
hashes, both frozen stage contracts, selected manifest, source geometry, exact
intermediate v3 results, and exact final RGBA/HDA. It checks the package was not
modified. The compiled helpers and raw intermediate pixels are only written into
the new output's disposable `work/` directory.

The 13 committed selected PNG file hashes are verified separately. Different PNG
encoders may produce different file bytes with identical decoded RGBA. Seven
unchanged authored crops are copied byte-exact; six tiles containing the accepted
v3 connector changes are freshly encoded, including the three v4 fringe tiles.
In the tested environment 10/13 rebuilt PNG files match committed encoding bytes;
all 13 decoded RGBA and HDA files match exactly. This encoding count is distinct
from the 10 committed outputs that are unchanged between v3 and v4.

Seven untouched authored PNGs use RGB encoding. Their decoded RGBA is fully opaque.
The engineer reports that repository `assets/hd/source` canonical copies were
normalized to RGBA by adding opaque alpha, as required by the repository source
contract. This package retains the original authored PNG file bytes unchanged.
Repository PNG encoding identity is therefore not a requirement: decoded RGBA
and HDA identity are the exact compatibility guarantees. This is an integration
note supplied by the engineer, not a repository mutation made by this package.

Independent read-only finite-region audit:

    python3 source/verify_scope.py
    python3 source/verify_scope.py --rebuild-root "/absolute/rebuilt output directory"

This audit freshly reconstructs the verified v3 baseline in a temporary directory
and then compares the chosen selected/rebuilt target against it. The main builder
already has a verified baseline and passes it directly to the same audit.

## Provenance, topology and acceptance

The exact prior README, ownership statement, manifest, inventory, source contract,
and historical rebuild scripts are retained under `source/upstream-v3/`. Prior
verification records are retained under `verification/upstream-v3/`. These are
historical evidence of the v3 package, not standalone entry points in their new
locations and not v4 runtime acceptance. The live v4 entry points are above.
There is no duplicate v3 output raster or HDA set.

Prior static coverage is 64 cells in nine motif placements: one 5×2, two 3×2,
two 3×3, three 2×2, and one 12-cell cross with 4×4 bounds. Nine describes
placements, not nine distinct dimensional classes. The recorded 2088–2609 window
observed only 150/156/157/158/166/168/176/177/178; cross-center IDs 159/160/169/170
were static completion. This does not establish all-13 runtime coverage.

Preserve the paired actor rows 279/281/283, 245/169/207, 273/275/277, row offsets
0/−1/+1, actor anchor (6,7), and terrain anchor (0,0). Link0 component deaths are
independent: the struck actor disappears and exposes persistent broken terrain,
while the other pieces remain. Do not flatten the assembly or convert it to group
removal. The engineer's actual replay and component-death evidence are summarized as
bounded private-survival plus controlled independent removals in
`verification/runtime-acceptance.json`. The packager reviewed the supplied scope
audit but did not run the game. No runtime captures or private fixture are included.

## Distribution boundary

There are 17 generated-only source PNGs: 13 authored terrain crops, the retained
small generated actor-tone strip, and three tiny generated terrain fringe strips.
There are 13 selected PNGs and 13 selected HDAs. Only these positive-listed raster
classes are included. The package excludes original game rasters, references,
masks, data and map arrays; full generated masters; full actor frames; runtime
screenshots or videos; private/prebuilt executables; and archives.

`handoff-inventory.json` records every other file's byte count and SHA-256, excluding
itself to avoid self-hashing. Fresh standalone and relocated-path rebuilding,
finite scope, upstream identity, and package boundaries are recorded under
`verification/`. `OWNERSHIP.md` states source attribution without claiming rights
in third-party game assets or determining AI-output copyrightability.
