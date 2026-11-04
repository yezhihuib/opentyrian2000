# Tank194 body reuse

This finite renderer reuses eight existing type15 HDR1 files without changing any
artwork bytes or resource identity:

| Native body pose | Existing material | HDR1 identity | SHA256 |
| --- | --- | --- | --- |
| 91 | enemy-newsh2-41-8.hda | 1010041 | 8d2f73e32e39be13e440ba8639f471ca1877dc476ac03b5ee60771741c2f515f |
| 93 | enemy-newsh2-131-8.hda | 1010131 | 7590d16a0c2378bca3d2ffb66c0279ede2c73ffcbc61383e83d582cdd03ad904 |
| 51 | enemy-newsh2-39-8.hda | 1010039 | faa362385a6b7f67e7926df162d9b5df4df41aa492709562841e410fd77e2d6d |
| 55 | enemy-newsh2-43-8.hda | 1010043 | 5874d9c67472bb9afa8e6be64480d33b0502ad4c035f8c985bb77ef7cfa00d66 |
| 15 | enemy-newsh2-45-8.hda | 1010045 | 3a20918ae6fffb966c9fc857a04a9b75a5554c961e622f6f7851db2d871f8af5 |
| 17 | enemy-newsh2-93-8.hda | 1010093 | c816a59f906bbf63af3707d7b183c7be8c39136613f60c0a9f8b4423d2622164 |
| 89 | enemy-newsh2-129-8.hda | 1010129 | 0369d6e3fdbe602f8e5caa51fa3834a434a1abd28c267674d4b7aa98005e3e56 |
| 13 (deliberate adaptation) | enemy-newsh2-91-8.hda | 1010091 | e2c3aaa833db864ae73b4cd611305043ddcefd89dda19d22a1b1d5d577b2c29f |

The eight global content aliases are complete, byte-identical copies of those
canonical files. The legacy global registry remains 120 resources in 14 families.
Original gameplay consumers 39/41/43/45/91/93/129/131 and the separate Tank147 muzzle path remain
unchanged. No original game data is included or needed to reproduce the aliases
and generated pins. Optional original-data fingerprint verification requires
the caller's own files and does not copy them into outputs.

## Finite runtime scope

Admission is limited to the actual loaded bank20, canonical actor194, native
poses 91/93/51/55/15/17/89/13 and their original four quadrants at tile offsets 0,1,19,20. It uses
the ordinary global density8 lane with NEWSHF disabled. NEWSHF-enabled builds,
legacy/selected packs, other actors, sources, poses and unsupported conditions
retain the existing path. Source, record, palette, slot-generation, resource,
ownership and dependency checks must all hold. This is an independent body
owner, not a new projectile membership bit or a widened rotor rule.

The91/93,51/55 and15/17 pairs have independent readiness. Missing or invalid
unused materials do not disable other pairs. Once a pair contributes, its source,
palette and material dependencies remain required. The15/17 pair independently
checks indices16/116 in addition to the original18 colors; it does not require
index10 or the51/55 pair to have loaded. Pose89 has one independently ready
resource, not a synthetic two-resource pair. Its16 used palette indices are
already within the original18-color gate. Pose13 is an independent single
material adaptation, requiring116=860400 beyond original18 even if the older
extra groups never load. Its native source is not identical to donor bank1/91:7
covered cells are added,2 removed and3 have changed indices. Its actual native13
tiles and142-cell coverage are independently pinned. The unchanged HD91 RGBA is
blended over the actual native13/HD union; native INDEX8 is not substituted.

Each reused HDR1 has logical size 24×28 and anchor 6,7. The caller's quadrant
top-left is already adjusted from the actor reference by that anchor. Therefore
the full composite origin is `quad_top_left - part_offset`, with quadrant
offsets (0,0),(12,0),(0,14),(12,14). The anchor must not be subtracted again.

The original indexed draw and gameplay behavior remain in place. HD admission
or later validation failures fall back conservatively. Supported natural SHADOW
writes first validate every sample of the density8 cell, then darken body RGB
once and update classic samples through the resulting palette index. Other
transformations, mixed ownership, interrupted quartets or invalid dependencies
are not generalized into new supported cases.

## Reproduction and authoring

`scripts/build_tank194_body_registration.py` reproduces the aliases and pins
from the finite public proof and existing public inputs. Its generation mode
requires a new output directory outside the source tree; `--check` is read-only.
It does not encode or derive artwork. The explicit `--extra-poses` option
reproduces the additional39/43 aliases and supplemental pins; the default still
reproduces the original two aliases and old header byte-for-byte.

The explicit `--poses15-17` option reproduces the additional45/93 aliases and
third-pair pins. It is separate from `--extra-poses`; the default and earlier
option keep their original outputs.

The mutually exclusive `--pose89` option reproduces one additional129 alias and
single-pose pins. All earlier registration options retain their exact outputs.

The mutually exclusive `--pose13-adaptation` option reproduces one additional91
material alias and independently pinned native13 header. All earlier registration
options retain their exact outputs. This is deliberate visual adaptation, not an
exact native-source alias or newly generated art.

The explicit authority for the335-source/eight-material epoch is
`current-tank-energy-body194-pose13-adaptation-v1`, selected through
`python scripts/build_current_tank_shell.py check --authority current-tank-energy-body194-pose13-adaptation-v1`.
This check requires the full declared producer inputs. It validates all335 source
bytes and all eight aliases, restores only the exact13 core delta, and reuses the
earlier strict source/runtime projections. The actual current335 source receipt
stays current throughout the projection. Its exact material proof binds the
native13 composite/four tiles, donor91 composite and all12 differences.

The earlier modes remain exact: `current-tank-energy-body194-v1` for331 sources,
`current-tank-energy-body194-extra-poses-v1` for332 sources,
`current-tank-energy-body194-poses15-17-v1` for333 sources, and
`current-tank-energy-body194-pose89-v1` for334 sources. All reject this newer
epoch. Historical mode and `current-tank-energy-v3` remain separate. No failed
check selects another mode automatically. Every selected-art, payload, registry,
build-input and unrelated-asset check remains.

This change was prepared on the unpublished89 dependency tree
`2df416d4eac50d4e40f746dab2650ec21506957f`, not a new public commit. Publishing
this delta alone must not bypass approval of that dependency and its unpublished
15/17 predecessor. Tests use genuine frozen331/332/333/334 input trees for
compatibility positives, without constructing substitute receipts.

The registration receipt retains its historical `deferred_authoring` field.
That field describes the earlier registration-only stage, before the explicit
body194 authority was added. It is not a qualification result for the new mode,
and the pinned registration manifests are not rewritten to reinterpret it.

## Qualification limits

Focused source-projection, registration and current-root authoring tests cover
this finite change. Authoring unit tests spy on unrelated asset reads; they do
not prove the complete asset tree or a full producer/package run. Renderer
qualification is separate from metadata and authoring checks. No general enemy,
arbitrary-transform, full-campaign, GPU or Windows qualification is implied.

## Top-only clipping source epoch

`current-tank-energy-body194-topclip-v1` explicitly selects the new335-source
clipping epoch. It has the same1139 runtime rows and eight material aliases as
pose13 adaptation, but a different exact source digest. The previous pose13 mode
continues to accept only its own335 bytes. All earlier modes remain strict;
no failed check selects a fallback. The new source proof reverses only the body
core delta, then reuses all earlier authority checks with the actual current
receipt unchanged. No material, header, palette entry or artwork was added.

Only original complete four-quadrant calls can clip above the top. Physical row
safety and the prior native/alpha support side and bottom bounds are retained;
missing or interrupted quadrants still reject. RGB addresses are formed only
for visible rows, and native callback counts omit rows the original blitter
skips. Even a wholly invisible quadrant must complete its normal call/end.
Native INDEX8, collision, shots and gameplay are unchanged.

The bounded natural witness is an upward exit at ticks495/496, not entry from
the top. Old91 at origin(118,-15) then(118,-16) stayed HD for its visible support.
The retained pre-fix495 comparison changed4199 samples within4264 visible
support, with zero changes outside or in the central already-HD body. The next
frame changed3488 samples. These finite witnesses and targeted native tests do
not qualify every offscreen path, side/bottom clipping, incomplete quartets or
an entire level. This delta depends on unpublished pose13 tree
`766a2b09fc5bfcf83d6b3c4d6a4599f872fc4c17` and its predecessors; it is not
permission to publish those dependencies. Genuine prior335 fixtures are used
alongside earlier source epochs, without manufacturing historical receipts.
