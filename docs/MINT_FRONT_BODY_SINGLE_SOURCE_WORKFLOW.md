# Mint and FrontBlaster: four independent current body sources

This is an authoring/package migration of **already approved pixels**, not new
artwork or new renderer eligibility. It starts at public commit
`845641e5af248cfb0b69f5a2c57ffdc8f22833b1`. The original approval contracts,
normalized PNGs, historical HDA packs, manifests, tests and qualification records
remain unchanged. Historical reports retain their original scope.

## Fixed boundary

| Body | Current identities | Independent source canvases | Existing renderer scope |
| --- | --- | --- | --- |
| Mint | 1270112, 1270131, 1270150 | **Three** 96×112 RGBA PNGs | bank9 frames112/131/150; option16/style3/charge0 |
| FrontBlaster | 1280083 | **One** 192×224 RGBA PNG | bank10 complete QUAD83/84/102/103; option20/style2/charge0 |

Every HDA is density8, anchor(0,0); Mint logical geometry is12×14 and Front24×28.
Mint's three independently approved phase shells are not generated from one
master. Front's four original tiles remain one complete source canvas, never
four separately editable pieces. Shared base83 does **not** authorize Front
options22/26. No production source/header, source-bank qualification, animation,
attachment, geometry, clipping, draw order, fallback, firing or gameplay changes
are made. Existing six-body Marlo/Plasma and single-master Charge APIs remain
separate and unchanged.

## Edit one source, update every current consumer

Selection: `assets/hd/authoring/mint-front-body-current.json`.
Bootstrap inputs: `authoring-inputs/mint-front-body-current/*.png`, copied
byte-for-byte from the approved normalized artwork outputs. No re-encoding,
crop, resample, recolor or new artwork generation is involved in bootstrap.
`tests/fixtures/mint-front-body-bootstrap-v1.json` records those frozen source,
RGBA and HDA hashes independently of future installed selections.

After separately approving a future artwork change, edit the relevant PNG or
place its replacement at another regular `authoring-inputs/…/*.png` path. Make
an **external draft** of the selection, updating that source's SHA256 and the
version. Keep all four identities in fixed order and four distinct source
paths. Charge's nine generated PNG outputs cannot be selected as editable
Mint/Front sources. Do not manually replace the installed selection or any derived output.
Changing one source never derives or rewrites the other three images.

```sh
python3 scripts/build_current_sidekick_body.py --family mint-front-body stage \
  --selection ../mint-front-draft.json --stage ../mint-front-stage
# Review plan.json, request.json and files/ before applying.
python3 scripts/build_current_sidekick_body.py --family mint-front-body apply \
  --stage ../mint-front-stage
python3 scripts/build_current_sidekick_body.py --family mint-front-body check
python3 scripts/verify_current_production.py
```

Omitting `--selection` stages the installed selection. A stage must be a new
external directory. Stage is non-mutating. Apply re-derives the request and
validates input/tool fingerprints, old output hashes and every staged byte
before the first write. Duplicate/non-finite/oversize JSON, unexpected fields,
wrong identities/order, aliased source paths, non-RGBA8/wrong-size/animated or
malformed PNGs, path traversal, symlinks/reparse points, and temporary output
collisions fail closed. Handled write failures roll back the batch through the
shared replacement helper; this is **not** a crash-safe multi-file transaction.
After an interrupted process, inspect outputs and explicitly restage.

The exact seven generated files are:

- the installed selection;
- four HDA files under `assets/hd/current-compat/mint-front-body/`;
- `packaging/current-mint-front-body-compatibility.json`;
- `packaging/runtime-assets-v1.json`.

No payload-pin header or production binding is generated. Current package
validation re-decodes all four selected PNGs and matches complete HDA bytes,
strict compatibility rows, and current runtime references. A current manifest
cannot mix partial or historical Mint/Front consumers. Explicit historical
manifests without current-family paths/revisions keep their generic old
packaging semantics and never acquire new runtime authority.

## Views, counts and composition

```sh
python3 scripts/build_current_craft267.py view --kind preview --output ../current-preview
python3 scripts/build_current_craft267.py view --kind debug --output ../current-debug
python3 scripts/package_runtime.py
# A separate new runtime copy, only when wanted:
python3 scripts/package_runtime.py --build --output ../current-runtime
```

The existing current preview/debug composer overlays all four bodies. Each view
still contains650 files (641 immutable base files plus the existing9 Charge
additions). Current overlays increase151→155; untouched base members decrease
499→495. The runtime retains1015 destinations, the global registry120 entries,
and the production source binding252 files. Four runtime `source_path` and
`revision` pairs change at bootstrap; all resource payloads stay byte-exact.
The historical `closure.gameplay_files` field remains the pinned base's637;
it is not reinterpreted as a freshly computed total.

Every other current authoring builder carries the finite Mint/Front source
closure and compatibility mapping into temporary rebuilds. Staged plans bind
these inputs so a later source/tool change cannot silently reuse stale stages.
Cross-family tests cover global art, HUD, tanks, energy, six Marlo/Plasma bodies,
craft267 and the independently derived Charge family.

## Evidence scope

`tests/test_current_mint_front_body_authoring.py` checks each source independently,
HDA/runtime isolation, both materialized views, package copies, schema/path/PNG
rejection, stale source/tool/staged data, rollback and cross-family composition.
`tests/accepted_later_changes.py` independently proves exactly the five new
asset paths (one selection plus four HDA) before projecting them out of older
fixed asset inventories; no historical ledger or pack digest is rebased.

These are authoring/packaging checks, not fresh visual acceptance. Original
approvals remain in [Mint](option-mint-body-three-v1/README.md) and
[FrontBlaster](option-frontblaster-body-one-v1/README.md). This migration makes
no Windows, GPU, full-game, campaign or performance claim. Validation logs and
receipts for this change are retained outside the repository.
