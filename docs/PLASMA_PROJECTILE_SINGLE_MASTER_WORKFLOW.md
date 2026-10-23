# Plasma Storm projectile: one current editable master

This workflow changes **one master**, then derives all six already-existing
Plasma Storm projectile transports. It is **not** the five independent bank9
Plasma sidekick **body** sources. No new art, game data or renderer coverage is
introduced by the bootstrap.

## Editable input and fixed derivation

- Installed selection: `assets/hd/authoring/plasma-projectile-current.json`.
- Initial editable master: `authoring-inputs/plasma-projectile-current/master.png`.
  It is byte-identical to the approved historical generated master, SHA256
  `de7d4bd38f70e4f19405c5349535f790729b469f1c4e7df9df1afaec186dccb4`.
- Input is one complete **1167×1347, straight RGBA8, nonanimated PNG**.
- `authoring-inputs/plasma-projectile-current/recipe.json` is data-only and must
  equal the fixed recipe in `scripts/current_plasma_projectile_compatibility.py`.
  It is not an executable hook or a place to change geometry/IDs.
- Fit the complete master to 520×600 with Pillow RGBA LANCZOS; crop density8
  pieces at logical y=0/24/52 with sizes 62×24, 65×28 and 62×23; derive each
  density4 piece separately by halving that density8 piece. Anchors remain 0,0.
- Resource IDs stay 1300022/1300023/1300024, densities4/8. The pieces are
  simultaneous parts of one projectile effect, **not animation alternatives**.

Only the master is editable artwork. The six PNGs in
`authoring-inputs/plasma-projectile-current/derived/` are generated outputs,
never independent selectable sources. The installed selection declares and
verifies every output hash and exact generated PNG bytes. Candidate selections
cannot supply generated resources or override the fixed recipe. Charge and
Mint/Front also reject these generated paths as independent artwork.

Bootstrap reproduction and the tests were run with **Pillow12.3.0**. Use that
version for byte-exact authoring; another Pillow implementation/version is not
qualified by this record. The compiled game does not need Python or Pillow.

## Stage, inspect, apply, check

Keep proposed artwork under a new regular `authoring-inputs/` path, for example
`authoring-inputs/plasma-projectile-edit/master.png`. No symlinks, junctions,
traversal, absolute paths, arbitrary scripts or generated-piece inputs are
accepted. The original historical master/contract/PNGs/packs stay unchanged.

Make a candidate JSON outside the repository, with exactly this structure
(replace the master path and its actual lowercase SHA256):

```json
{
  "schema": "opentyrian-current-plasma-projectile-candidate-v1",
  "version": "my-plasma-master-revision",
  "master": {
    "source_png": "authoring-inputs/plasma-projectile-edit/master.png",
    "source_sha256": "<actual master SHA256>"
  },
  "recipe": {
    "path": "authoring-inputs/plasma-projectile-current/recipe.json",
    "sha256": "<actual recipe SHA256>"
  }
}
```

From the repository root, choose a **new external** stage directory:

```sh
python -B scripts/build_current_plasma_projectile.py stage \
  --selection /absolute/path/candidate.json --stage /absolute/path/new-stage
# Inspect new-stage/plan.json, request.json, and files/ before applying.
python -B scripts/build_current_plasma_projectile.py apply \
  --stage /absolute/path/new-stage
python -B scripts/build_current_plasma_projectile.py check
python -B scripts/verify_current_production.py
python -B scripts/package_runtime.py
```

`stage` never changes repository outputs. `apply` rereads candidate inputs,
rederives every output, rejects stale/tampered plans or inputs, checks old hashes
and temporary paths, then uses the existing preflighted batch replacement with
rollback on handled failures. It is **not** a crash-safe multi-file transaction:
after process termination/power loss inspect the state and explicitly restage.
A stage that changed outputs becomes stale after apply; restage before later
changes. A byte-identical no-op can be repeated but is not permission to replace
later work.
A valid in-place master edit can be proposed using its new hash without first
replacing the installed selection; until apply, checks intentionally reject the
stale installed selection.

The finite generated outputs are the installed selection, six PNGs, six HDAs in
`assets/hd/current-compat/plasma-projectile/`, compatibility mapping, dedicated
payload-only C header, current production source binding, and runtime manifest.
The master and recipe themselves are never rewritten by apply. Other authoring
builders carry this finite nine-input closure and mapping, not an artwork-tree
glob, so later unrelated edits cannot silently restore old Plasma pieces.

**Rebuild the executable from the new current source after a master update.**
The existing renderer payload checks now use six generated constants in
`src/current_plasma_projectile_payload_pins.h`; an old binary still contains old
pins and will correctly reject changed payloads. Packaging never compiles or
silently substitutes a binary. This is the same build/package boundary as the
other generated runtime payload pins.

## Current views and package

```sh
python -B scripts/build_current_craft267.py view --kind preview \
  --output /absolute/path/new-preview
python -B scripts/build_current_craft267.py view --kind debug \
  --output /absolute/path/new-debug
python -B scripts/package_runtime.py --build --output /absolute/path/new-runtime
```

Both complete views remain **650 files**: **161 current overlays**, with **489
other frozen members** unchanged. Runtime remains **1015 destinations** and the
global registry remains **120 resources**. Bootstrap HDAs and PNGs match their
approved historical bytes exactly; only six gameplay runtime source/revision
pairs migrate, plus the independently updated current-production-binding row.
Historical/custom manifests without current Plasma references retain their
original semantics. Any current Plasma request must include all six fixed rows;
default current packaging cannot remove the entire family silently.

## Rendering and historical boundary

The only executable-source edit is one header include and substitution of the
six existing payload literals. The exact source inventory is now **253** files
(the dedicated generated header adds one), not an artificial preservation of252.
A separately pinned inverse ledger projects that two-hunk source change back
before older historical oracles run; no prior acceptance fixture is rebased.

Existing E1 Normal9/Hard15, normal-data/right-sidekick9 and weapon88
qualification stays exactly as before. No eligibility, emission, geometry,
selected-density loading, per-draw reopening, projection cache, indexed writes,
warm-ramp blend, per-piece fallback or excluded context changes. Sharing an
editable source does not authorize any additional level or weapon coverage.
The historical `closure.gameplay_files` number remains historical metadata.

## Verification and limits

`tests/test_current_plasma_projectile_authoring.py` covers literal bootstrap
geometry/hashes, strict PNG/recipe/path/schema rejection, generated-output
integrity, source isolation, full six-output mutation, both complete views,
package closure, stale plans and handled rollback, and coexistence with the
other authoring workflows including changed Charge and Mint/Front sources.
Set `PLASMA_PROJECTILE_REAL_COPY_OUTPUT` to a new external directory when running
the full propagation test for a real guarded CLI package copy. The portable
content-only path is not a filesystem/permission acceptance claim.

Current-source verification, controlled native harnesses and packaging are not
Windows, GPU, full-campaign or new-art acceptance. Frozen originals, contracts,
canonical historical PNGs, both historical packs and old acceptance records
remain the authority for their original scopes.
