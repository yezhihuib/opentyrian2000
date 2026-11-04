# Tank194 body reuse

This finite renderer reuses seven existing type15 HDR1 files without changing any
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

The seven global content aliases are complete, byte-identical copies of those
canonical files. The legacy global registry remains 120 resources in 14 families.
Original gameplay consumers 39/41/43/45/93/129/131 and the separate Tank147 muzzle path remain
unchanged. No original game data is included or needed to reproduce the aliases
and generated pins. Optional original-data fingerprint verification requires
the caller's own files and does not copy them into outputs.

## Finite runtime scope

Admission is limited to the actual loaded bank20, canonical actor194, native
poses 91/93/51/55/15/17/89 and their original four quadrants at tile offsets 0,1,19,20. It uses
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
already within the original18-color gate. Frame13 stays excluded.

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

The explicit authority for the334-source/seven-alias epoch is
`current-tank-energy-body194-pose89-v1`, selected through
`python scripts/build_current_tank_shell.py check --authority current-tank-energy-body194-pose89-v1`.
This check requires the full declared producer inputs. It validates all334 source
bytes and all seven aliases, restores only the exact89 core delta, and reuses the
earlier strict source/runtime projections. The actual current334 source receipt
stays current throughout the projection.

The earlier modes remain exact: `current-tank-energy-body194-v1` for331 sources,
`current-tank-energy-body194-extra-poses-v1` for332 sources, and
`current-tank-energy-body194-poses15-17-v1` for333 sources. All reject this newer
epoch. Historical mode and `current-tank-energy-v3` remain separate. No failed
check selects another mode automatically. Every selected-art, payload, registry,
build-input and unrelated-asset check remains.

This change was prepared on the unpublished15/17 dependency tree
`aaa41373f96ec70a57dbc314a30264c2a669f78d`, not a new public commit. Publishing
this delta alone must not bypass approval of that dependency. Tests use genuine
frozen331/332/333 input trees for compatibility positives, without constructing
substitute receipts.

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
