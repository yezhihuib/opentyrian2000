# Shared effect authoring: one selected source, all active consumers

Three independent semantic profiles cover the already-approved artwork:

| Profile | Identities | Count |
| --- | --- | --- |
| `hitflare` | 1060146–1060152 | 7 |
| `white_smoke` | 1060135–1060141 | 7 |
| `small_explosion` | 1060122–1060133 | 12 |

This is editing convenience, not byte deduplication or new artwork. The installed
selectors are `assets/hd/authoring/<profile>-current.json`. Their initial PNGs are
exactly the approved global registry provenance sources. Each fixed identity
retains its original role, source bank, geometry, density and anchor.

## Select a new version

Create new normalized RGBA PNG source files inside the repository (96×112,
logical 12×14, density 8, anchor 0,0). Make an **external draft copy** of the
selector with a version label and each selected PNG's path and SHA-256. Do not
edit an installed selector first: all installed profiles are drift-checked.

For each profile, independently:

```sh
python scripts/build_current_art.py --family hitflare stage \
  --selection /tmp/hitflare-draft.json --stage /tmp/hitflare-review
# Inspect plan.json and staged outputs before applying.
python scripts/build_current_art.py --family hitflare apply --stage /tmp/hitflare-review
python scripts/build_current_art.py --family hitflare check
```

Use `white_smoke` or `small_explosion` instead for those profiles. Stage must be a
new directory outside the repository. Source bytes, authority, build inputs,
expected old hashes, staged bytes and temporary destinations are validated before
the first write. Apply uses per-file atomic replacement; it is **not a crash-safe
multi-file transaction**. After interruption, inspect state and restage explicitly.

The common builder synchronizes global content, registry/provenance and generated
global payload pins, the installed selector, current compatibility mapping and
`assets/hd/current-compat/<profile>/explosion-newsh6-<slot>-8.hda`, then regenerates
the current runtime manifest and source binding. Thus global and legacy runtime
consumers use the same selected pixels. These effects have no separate legacy
payload constants: no effect macros or runtime C changes are needed.

Historical packs, the historical runtime manifest and old global content are
never rewritten or deleted. Equal pixels still retain separate semantic IDs and
HDA headers. Terrain/cloud work and new runtime scene eligibility are out of scope.

The isolated synthetic fixtures in `tests/test_current_effects_authoring.py`
exercise every one of the 26 outputs, history preservation, cross-family checks,
wrong hashes/identities/paths, stage tampering and write preflight. They are not
production artwork. Authoring checks prove consistent generated consumers, not
native gameplay acceptance; native/package regressions are separate evidence.
