# Low grass / sand: nine-tile v3 source package

Selected art is frozen for runtime validation. This package does not claim that
the grass has yet been visibly accepted in actual play.

## Finite binding

Layer 1, shapesZ IDs **66, 67, 69, 76, 78, 79, 80, 89, 90**, in that order,
use reserved slots **312–320**. Proposed combined asset capacity is 321 and
terrain pointer registry capacity is 162. Bind only these nine original source
identities through the existing NORMAL terrain path. Main integration belongs
to the engineering owner; this package contains no renderer change.

Every tile is 192×224 RGBA, density 8, logical 24×28, anchor (0,0), fully opaque.
HDA is `HDR1` plus six little-endian u32 values
`[2010000 + source_id, 8, 24, 28, 0, 0]` followed by exact straight RGBA bytes.
`contract.json` records each PNG file hash, decoded RGBA hash, HDA hash and slot.

Accepted sand47 is a frozen generated input, not an extra replacement entry.
Accepted sand/path49 and50, the other backgrounds, clouds and entities are not
changed. Forest IDs 211,212,213,215,221,223,231,232,233,234 are explicitly excluded.

## Generated source ownership and deterministic reconstruction

Only authored/generated PNGs, deterministic registration code, prompts and
metadata are included. No original game binary, original pixel crop, map image,
game screenshot or raw original map array is included. Original references and
full native-size context boards remain in the private art workspace.

Three imagegen revisions are retained through canonical registered generated
sources. Their original full-image hashes and registration sizes are recorded
in `provenance.json`; those full generated masters also remain in the workspace.

1. `generated-family-v1.png`: coherent low, dark-green vegetation on sand.
   `register_vegetation.cpp` extracts the authored green support, uses a small
   closing/feather operation, maps vegetation onto the original five-stop green
   ramp, and restores exact frozen generated sand47 outside it.
2. `generated-interior-v2.png`: coherent short-blade groups and light/middle/dark
   patches that remain legible at native 2×. `register_interior.cpp` changes only
   interior green material, holds the prior silhouette/sand and four HD pixels
   at tile borders, and recenters green intensity rather than globally brightening.
3. `generated-fringe-v3.png`: a small, naturally irregular width correction for
   the six-tile isolated motif. `register_footprint.cpp` adds only new generated
   grass fringe. All prior v2 grass pixels and four-HD-pixel tile-facing borders
   remain byte-identical. IDs66/67/69 remain wholly identical to v2.

The final motif's green area is 99.7% of the original, versus 83.1% before the
fringe correction. Its central 95% width is 28.625 logical pixels versus 29.375
original. The centroid differs by −0.20 x / −0.06 y logical pixels. These are
visual-green diagnostics, not an assertion of identical original pixel geometry.

Run from any directory, with Python3, Pillow and a C++17 compiler:

```
python3 /path/to/package/rebuild.py --output-dir /new/empty/build
```

The rebuild requires no game files, repository checkout, network, imagegen call
or environment-specific path. It validates owned source files, compiles three
small registration helpers, and verifies all nine decoded RGBA and complete HDA
hashes before writing. PNG encoder bytes may vary; selected package PNG file
hashes are verified separately. No generative rerun is used for reproducibility.

## Offline review and limitations

The map census has 2,172 placements across these IDs. Independent review covered
all 26 non69 placements and all 110 distinct 3×3 contexts for69, totaling136
native2× comparisons. All five shared79 placements and frozen47/49/50 contacts
pass without a visible join or topology blocker. Soft69 tile-periodic mottling
remains perceptible, but no hard grid seam was found.

The worst later interface is original forest232's grass skirt against69 near
map[155,5]: the unchanged source skirt is coarser and slightly brighter. This is
a documented mixed-resolution transition with no crack or shifted boundary.
No forest artwork was generated in this batch.

The 75–90-second source trace only shows33 calls of80 at3099–3131, with at most
44 entering logical sand pixels, partly overlapped by later layers. Those calls
are not grass-visibility evidence. Root approved matched no-injection/no-control
private-survival logs through3599 to verify the complete six-tile motif's
registration and final visibility, followed by at most120 native2× frames at
3480–3599 if it is exposed. Predicted full entry3516 is provisional until logged.

Runtime validation and publication are separate pending gates at this freeze.
The production baseline is 7c7aee388e384840915bd2532bbcc038c3d5047e.

## Rollback

Unintegrated v1 and v2 candidates are retained in the art workspace. Existing
production assets are untouched. Removing the nine finite mappings or omitting
their HDA files must retain the original indexed fallback, verified by engineering.
