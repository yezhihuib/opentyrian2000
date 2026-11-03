# Tank194 body reuse

This finite renderer reuses four existing type15 HDR1 files without changing any
artwork bytes or resource identity:

| Native body pose | Existing material | HDR1 identity | SHA256 |
| --- | --- | --- | --- |
| 91 | enemy-newsh2-41-8.hda | 1010041 | 8d2f73e32e39be13e440ba8639f471ca1877dc476ac03b5ee60771741c2f515f |
| 93 | enemy-newsh2-131-8.hda | 1010131 | 7590d16a0c2378bca3d2ffb66c0279ede2c73ffcbc61383e83d582cdd03ad904 |
| 51 | enemy-newsh2-39-8.hda | 1010039 | faa362385a6b7f67e7926df162d9b5df4df41aa492709562841e410fd77e2d6d |
| 55 | enemy-newsh2-43-8.hda | 1010043 | 5874d9c67472bb9afa8e6be64480d33b0502ad4c035f8c985bb77ef7cfa00d66 |

The four global content aliases are complete, byte-identical copies of those
canonical files. The legacy global registry remains 120 resources in 14 families.
Original gameplay consumers 39/41/43/131 and the separate Tank147 muzzle path remain
unchanged. No original game data is included or needed to reproduce the aliases
and generated pins. Optional original-data fingerprint verification requires
the caller's own files and does not copy them into outputs.

## Finite runtime scope

Admission is limited to the actual loaded bank20, canonical actor194, native
poses 91/93/51/55 and their original four quadrants at tile offsets 0,1,19,20. It uses
the ordinary global density8 lane with NEWSHF disabled. NEWSHF-enabled builds,
legacy/selected packs, other actors, sources, poses and unsupported conditions
retain the existing path. Source, record, palette, slot-generation, resource,
ownership and dependency checks must all hold. This is an independent body
owner, not a new projectile membership bit or a widened rotor rule.

The91/93 pair and51/55 pair have independent readiness. Missing or invalid
unused39/43 materials do not disable91/93. Once a pair contributes, its source,
palette and material dependencies remain required. Frame13 stays excluded.

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

The explicit authority for the332-source/four-alias epoch is
`current-tank-energy-body194-extra-poses-v1`, selected through
`python scripts/build_current_tank_shell.py check --authority current-tank-energy-body194-extra-poses-v1`.
This authoring check requires the full declared producer inputs. It validates
all332 source bytes and all four aliases, restores only the exact extra-pose
core delta, and reuses the earlier strict source/runtime projection. The actual
current332 source receipt stays current throughout the projection.

`current-tank-energy-body194-v1` retains its exact331-source/two-alias authority
and rejects this newer epoch. Historical mode and `current-tank-energy-v3`
remain separate. No failed check selects another mode automatically. Every
selected-art, payload, registry, build-input and unrelated-asset check remains.

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
