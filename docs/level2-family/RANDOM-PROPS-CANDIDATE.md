# Eight-record random props candidate

The existing `--hd --public-candidates` preset now selects the bounded random
props adapter for records135/136,260/261,263/265,266/268. Plain `--hd` keeps it off, and
inherited `RANDOM_PROPS_` variables are cleared. No new CLI option, asset, random
number draw or gameplay write is introduced. Records137/262/264/267
remain unsupported; matching a similar image is not sufficient for admission.

## Reused material and identity

Four existing files in `assets/hd/packs/asteroid1-ten-v1` are used:
`enemy-newshd-{5,43,85,123}-8.hda`. Each is 172,060 bytes, HDR1 24x28 at density8.
All four RGBA hashes match the archived adapter's pins. The public launcher
verifies their exact size and SHA-256 in addition to all existing checks; the
runtime checks HDR1 fields and payload identity. Asset bytes are unchanged.

The adapter/header/native tables are selected from the public source archive
`experimental/late-level/sources/03c5968bda89ae17/`, and integrated with the
current family rather than replacing existing source files. The only change
inside the archived adapter is renaming its private `rp_load` helper and call
to `rp_material_load`, avoiding a collision with the existing redvent loader.
The redvent implementation is unchanged. The later cloud audit independently checked the original bank, random table,
record stamps and ordered callback sequences; see the extension audit below.
Palette identity remains guarded at runtime.

Ordinary E1 physical-level2 ASTEROID2, mapD/shapeZ, the exact 33-entry random
enemy table and the parent family controls are required. Begin/commit surround
only the engine's existing random `JE_newEnemy(0,tempW,0)` after its RNG choices.
Allocation and initialization bind each actual pool0–24 object to record,
source bank, token, epoch and generation. Shape checks bind each allowed pair
to its particular base and speed. Failed allocations close calls; unrelated
slot reuse, bank replacement, death and scope loss revoke the existing witness.

## Four-block native transaction

A body must be fully supported at x24..264/y0..156. No top, side or bottom
clipping is added. Native parts0/1/19/20 must arrive in that order, for one slot
and body origin, with exact sparse callback counts. The four total counts are
355/345/461/433. A pre-tile check runs before every family's dispatch, preventing
another tile from silently interleaving with a pending four-block body.
Missing blocks, missing writes, duplicate bodies, foreign callbacks and altered
identity fail closed. Existing display admission is unchanged: random props
can only contribute inside an already authorized family frame.

Each actual native callback validates destination and expected index and blends
the real HDA alpha into the current HD underlay. An alpha0 subpixel retains RGB
but acquires ownership; a native hole has no callback and remains untouched.
Index0 would be a native write, not an implicit hole, although the three pinned
callback tables contain no zero-index entries. Other sparse owners retire
before any family pixel handler can return early. Generic normal/blend writes
retire random-prop ownership; validated shadows retain ownership and record a
shadow receipt. Pure snapshots use `rp_finish`; actual finish/Present uses the
faulting guard. Existing observer instrumentation is retained, not a new lease.

## Bounded checks

`tests/test_random_props_family.py` compiles extracted production birth/witness,
`rp_dependencies/finish`, `rp_before_tile/geometry/tile/pixel/end`, retirement,
shadow and alpha-blend functions. It checks six births, excluded sibling
records, allocation/token/reuse rejection, all three real materials across
1,161 native callbacks, 12,417 alpha0 and 61,336 partial-alpha subpixels, pending
transaction isolation, block order, incomplete bodies and missing writes.
Scope, shape, source/palette/resource readiness and canvas preparation are
explicit stubs. Event/RNG/constructor execution, original-bank RLE, Present
and normal gameplay are not executed by this test.

The existing central writer test now covers64 family-to-family transitions
with normal/blend/shadow/hole behavior; its acquisition adapters remain modeled.
Launcher tests cover preset-only selection, inherited-control removal and
changed-asset rejection. These are offline candidate checks, not actual scene,
final-pixel or GUI acceptance. The complete second level remains unqualified.

## Original-data extension audit

The cloud audit independently decoded the actual physical-level2 random table,
all eight selected 77-byte records, and all four ordered RLE callback sequences.
Records266/268 use base123 at native downward speeds4/6. Siblings137/262/264/267
are absent from this level’s random table and remain rejected. The new material
is existing artwork, not a new generation or source upscale. All nonzero alpha
remains inside actual native writes. No source identity or clipping guard changed.

Run `ORIGINAL_GAME_DATA=/private/data python3 -m unittest discover -s tests -p
 test_random_props_source.py` (join the command onto one line). The original-data
audit skips when no private data directory is provided; artifact checks still run.
The extracted runtime test now covers8 births,4 materials,1594 ordered writes,
alpha/underlay, holes, writer ordering and native retirement. This does not
qualify complete-level gameplay or make the remaining artwork gaps complete.
