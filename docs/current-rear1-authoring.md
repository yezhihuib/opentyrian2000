# Current Rear1 shared authoring

One independent right-facing data-only geometry master produces eight existing
role-131 transports: raw 1, 2, 3 and 77 at densities 4 and 8. It is **not** a
mirror of the independent Rear39 master. This migration changes authoring and
asset selection, not game coordinates, weapon records, source guards, normal
or shadow eligibility, anchors, or runtime resource count.

## Edit once

Editable source: `authoring-inputs/rear1-current/master-1.json`.
The fixed recipe and selection live beside it and in
`assets/hd/authoring/rear1-current.json`. Change bounded path / heat / gradient
parameters, update the selected master SHA256, use candidate schema
`opentyrian-current-rear1-candidate-v1`, and omit generated `resources`.

```
python scripts/build_current_rear1.py stage --selection /outside/candidate.json --stage /outside/new-stage
python scripts/build_current_rear1.py apply --stage /outside/new-stage
python scripts/build_current_rear1.py check
```

Stage rederives the finite output plan. Apply rederives again, checks all input
fingerprints and staged bytes, then uses handled-error rollback. This is not a
crash-safe, power-loss-safe, or concurrent-writer transaction.

## Exact compatibility geometry

- 1: independent semantic right geometry; 34 generated SVG path occurrences
  come from one editable path, not 34 separate manual edits.
- 2: original shifted `(0,-2)` plus full-canvas vertical flip shifted `(0,+2)`.
- 3: vertical flip `(-2,-5)`, vertical flip `(0,-1)`, original `(-2,+5)`.
  Retain accepted tail clipping: baseline 26 samples / alpha sum 2646 at d4;
  82 samples / alpha sum 11628 at d8. Do not recenter or enlarge the canvas.
- 77: clockwise quarter turn over the full canvas, then `(-2,+2)` translation.
  Only transparent pixels may be clipped. Output remains 12×14 logical pixels.
- Composed supports must be disjoint before clipping; 2 and 77 forbid occupied
  clipping. Transparent RGB is zero. d4 and d8 are rendered independently.

Bootstrap PNG, RGBA and HDR1 HDA bytes equal the frozen approved assets. Sharp
and Node use the existing exact P7/39 renderer profile and SVG/pixel goldens.
The accepted 77 encoder additionally binds Pillow 12.3.0, its linked zlib 1.3.1,
and Python zlib 1.3.2; PNG compression level 9, optimize false. No version bypass
or automatic golden repin is provided. The unchanged historical P1 strict
builder's older Node requirement remains unchanged; this explicit current
profile is separately verified by exact output equality.

## Shared consumers and isolation

There remain 1029 runtime rows and 120 registry resources; eight existing rows
change source/revision only. Current preview overlays increase from 196 to 204.
The source/header inventory remains byte-identical at bootstrap.

One shared payload header composes Rear1's eight pins with Rear39's six and
P7's four. Rear1 occupies flat cells 2/3, 14/15, 28/29 and 16/17. All production
loads derive and validate the other families' complete assets, including their
mapping and HDA bytes. Builders validate opposite-family assets without
mistaking the edited candidate's stale header for an unrelated-family failure.
The remaining 30 frozen Rear transports and all Front transports are untouched.
Sharing runtime records with historical Front-like Rear182/183 does not create
an artwork dependency on current Front163/164.

## Validation scope

The new authoring tests cover exact goldens, real path edits, finite grammar,
profile faults, fixed recipes, path restrictions, support overlap/clipping,
stale plans and handled replacement failures. Integration tests check exact
bootstrap inventory, isolated runtime selection, preview/master mapping and
packaging rejection paths. The portable transaction harness performs actual
three-family edits, actual second-replacement rollback and asset-only Linux /
Windows export checks. Consult completed validation receipts for run status.

Native tests use actual HDA/payload pins with synthetic source-bank and weapon
records plus observer draw/shadow-lease hooks. They are not final compositor
pixel validation, original-data admission, full campaign playthrough, or
Windows/GPU execution. Existing Linux build evidence can be inherited only
while the full 278-input closure remains identical; no new builds are implied.
