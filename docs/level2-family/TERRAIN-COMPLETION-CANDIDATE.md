# ASTEROID2 remaining terrain: 38-resource candidate

This is an artwork/resource checkpoint, **not complete HD gameplay acceptance**.
The initial exact-name inventory lacked 38 nonblank SHAPESZ identities. This
batch supplies one 8x HDA and a matching RGBA PNG for each. Together with the
existing 24 terrain resources, all 62 nonblank layer-1 identities now have
resource candidates. Blank shape 1 and NULL upper layers require no art.
This does not fill enemy, effect, HUD or other outstanding coverage gaps.

## Contents and provenance

- Seven image-generated RGB masters and their authoring prompts:
  `assets/hd/artwork/level2-terrain-completion-v1/`.
- 38 HDR1 resources, 38 PNG previews, manifest and numerical neighbor audit:
  `assets/hd/packs/level2-terrain-completion-v1/`.
- Producer: `scripts/build_level2_terrain_completion.py`.
- Independent resource/adjacency checker: `scripts/audit_level2_terrain_completion.py`.
- Regression suite: `tests/test_level2_terrain_completion.py`.

The producer pins each master and the caller-owned SHAPESZ file. It resizes
an entire family master once, then cuts the 192x224 outputs at common exact
boundaries. No independent per-tile resize, native RGB border copy, palette
copy, or recolored source sprite is used. Alpha is exact 8x nearest expansion
of the original 24x28 zero/nonzero mask; transparent RGB is zero. This derived
geometry is disclosed, not represented as wholly independent art. Alpha
identity does not prove that every painted internal contour matches the source.

Master dimensions, source and output SHA-256 values, family layouts, transparent
cell counts and library versions are recorded in MANIFEST.json. RGB masters
are unchanged from generation and have no PNG metadata chunks exposed by Pillow.
The authoring prompts refer to private reference images; those images are not
included. No original DAT/LVL data, palette, raw reference map, source screenshot,
or private filesystem path belongs in this batch. The audit publishes derived
adjacency counts and measurements, not map cell arrays.

## Layout and numerical evidence

The pinned 4,200-cell ground map confirms complete coherent assemblies:
bronze-pit 2 occurrences, broken-pit 6, cross-pit 9, bronze-column 3, and
twin-shafts 1. Every occurrence of each member is contained in its complete
assembly. Fixtures and architecture are independent tile contact sheets, not
claims that their 4x2 authoring layouts occur together in the map.

All 38 candidate HDA headers, full payload hashes, PNG equivalence, source
hashes and exact alpha coverage pass. The numerical audit finds all nonblank
resources and measures 361 distinct directed joins over 3,447 stored map
adjacencies involving this batch. Eleven adjacencies with blank shape 1 are
explicitly excluded from RGB measurements. Map edges have no neighbor.

There are 42 reusable-edge constraints with different unchanged neighboring
RGB targets, considering only samples opaque in every target. This means
pixel-identical joins to every old neighbor cannot be assumed. It does not
prove that these joins look bad. Conversely, low edge differences cannot prove
visual continuity. The largest mean RGB jump is 79.2656 for 420→419 downward;
307→340 right is 75.122 and 317→340 right is 74.503. These values include
intentional lighting and structural boundaries and are not pass/fail thresholds.

## Actual image review and limitations

Reviewed actual pixels of all seven generated masters, the private original
38-tile reference contact sheet and architecture reference, and eight private
offline 4x4 map patches around IDs 299, 306, 319, 318, 423, 339, 410 and 416.
Those patches combine the new candidate art with existing terrain23/24 art;
they are not runtime captures and were not added to the repository.

The pits/shafts read as coherent assemblies, and the bronze, recessed black,
muted red and grey masonry vocabulary is consistent across the new masters.
The new smooth masonry nevertheless differs visibly in texture scale and
brightness from older ground neighbors. Some wall lighting changes are strong.
This review therefore does **not** qualify every outer seam, every repetition,
scrolling motion, occlusion, or scene composition. No undocumented master edits
were made. Regeneration or targeted re-authoring should follow scene-level review
if these material transitions are unacceptable, with new pins and a new receipt.

This resource manifest intentionally records `runtime_integrated: false`: the
producer does not activate or qualify an adapter. Any separate opt-in runtime
adapter must provide its own source, ownership, lifecycle and parity evidence.
Neither such integration nor a short replay retroactively turns this art review
into complete-level visual acceptance. `all_neighbor_joins_verified` and
`visual_scene_review_complete` remain false.

## Reproduction and regression receipt

Use a fresh output directory outside the private data/master directories:

```sh
python scripts/build_level2_terrain_completion.py --data "$TYRIAN_DATA" --output /tmp/terrain-rebuild
python scripts/audit_level2_terrain_completion.py --data "$TYRIAN_DATA" --pack /tmp/terrain-rebuild --output /tmp/terrain-audit.json
python -m unittest discover -s tests -p test_level2_terrain_completion.py -v
TYRIAN_DATA=/path/to/tyrian2000 python -m unittest discover -s tests -p test_level2_terrain_completion.py -v
```

Verification on 2026-11-10: **11 tests passed**, including the pinned private-data
integration test. Two fresh builds reproduce every shipped HDA/PNG and manifest
byte-for-byte in the recorded Pillow/numpy environment; the audit reproduces the
committed JSON. Synthetic checks cover invalid/truncated shapes, wrong hashes
and sizes, symlinks, overlapping/existing output, empty/ragged/duplicate layouts,
invalid tile identities, wrong array geometry/dtype, exact shared crop boundaries,
zeroed hidden RGB and join directions. Pinned corruption tests reject changed
payloads, wrong alpha even after refreshing its outer hash, altered HDA identity
headers and changed PNGs. Without TYRIAN_DATA, ten synthetic tests pass and the
one pinned replay test explicitly skips. This suite is not a native runtime test.

Build versions are recorded rather than installed or silently changed. A different
Pillow encoder/resampler version may produce different bytes and will fail the
committed replay comparison; investigate rather than replacing the pins casually.
