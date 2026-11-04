# Private terrain23 registration

This is a finite private candidate, not a complete runtime package or a public distribution clearance. It retains accepted ground10, cliff12 and corner366 only. The stable23 runtime logic is unchanged except that its native-plane/palette capture helper is removed from the normal source tree. Tile380 is the accepted calibratedv2 material, not a rejected later experiment.

## What is bound

- The actual338 files under `src`, five existing build inputs, and two historical validation receipts.
- Exact byte projection to the public335 TOPCLIP source ancestry. Projection is an in-memory proof only. The current receipt and manifest remain bound to the actual338 source digest.
- Exactly1162 manifest rows:1138 unchanged old nonbinding rows, one refreshed current binding row, and23 new gameplay rows under `assets/hd/current-terrain23/`.
- All23 new HDA files, including complete bytes, HDR1 identities/dimensions/anchors, payload FNV/SHA and alpha/mask contracts.

The338 count is not the whole repository. Scripts, tests, proofs, authoring inputs and assets are outside `src` and are separately inventoried. Existing old tank authoring modes are not extended to this source epoch. In the default packager/rebuild, the verified projected epoch is used only to retain the old eight tank aliases. Their existing validators and all other old package validators remain enabled.

## Finite verification

Run from the source root with Python3. The following command does not build the game, render frames, fetch data or write the source tree:

```
python3 -B -c "import sys,json; from pathlib import Path; sys.path.insert(0,'scripts'); import current_terrain23_source_bridge as b; r=Path('.'); print(json.dumps(b.validate_runtime_rows(r,json.loads((r/'packaging/runtime-assets-v1.json').read_text()),required=True),sort_keys=True))"
```

The result explicitly reports `full_package_acceptance: false` and `old_payloads_revalidated: false`. A PASS applies only to the stated source/metadata/23-payload scope.

To rebuild a separate finite registration manifest from the exact public TOPCLIP1139 manifest, supply its regular local file explicitly. The output and optional report must be new files outside this source tree and must have existing nonsymlink parent directories:

```
python3 -B scripts/build_terrain23_registration.py \
  --root . \
  --base-manifest /path/to/exact-topclip-runtime-assets-v1.json \
  --output /separate/existing/directory/terrain23-runtime.json \
  --report /separate/existing/directory/terrain23-finite-report.json
```

The pinned base SHA256 is `87ee42de76ec64b1e96754e82ea3c0c41129e0cb27ff4c30cc724afac06c4ea4`. This builder preserves its old rows but does not claim to read the missing old payloads. Re-running with an existing output rejects instead of overwriting it. This is separate from `rebuild_recovered_runtime_manifest.py`, which still requires the full historical resources and original validators.

Targeted registration tests are in `tests/test_terrain23_registration.py`. Authoring instructions/tests are separate and require caller-owned matching original game data. Never substitute the registration result for an authoring or runtime test.

## Default packaging remains incomplete

Use the ordinary default commands to expose real missing inputs:

```
python3 -B scripts/package_runtime.py --source-root .
python3 -B scripts/rebuild_recovered_runtime_manifest.py --root . --output /new/external/manifest.json
```

The sparse candidate lacks1117 old manifest row sources. The default package/rebuild therefore remains unaccepted and may stop on the first missing public verification dependency, historical metadata or payload. No import stub, fallback receipt, skipped validator, or copied historical PASS is acceptable. Public verification modules restored from the fixed public tree are unchanged dependencies, not new terrain implementation or restored original game data.

The new source-root includes/proof themselves are terrain markers, including abnormal symlinks. Replacing the manifest and receipt with their old335/1139 versions cannot downgrade the actual338 root into the old validation path. Invalid or incomplete terrain state fails closed.

## Runtime and content limitations

There is no new gameplay/RNG/physics/animation change. Capture-free game compilation and bounded CPU/actual-SDL comparisons are separate evidence, not consequences of registration success. The normal tree must not emit game-index, final-index or palette capture files. No original game `data` is bundled.

The new bounded scene runs use `--render-assets=source/assets/hd/current-terrain23`, the canonical23-only resource root, not a materialized1162-row full package. They do not qualify mixing these terrains with every old HD actor, other levels or palettes, ordinary manual play, or a full campaign. Registration at the normal default destination does not establish those runtime guarantees.

The unchanged cliff loader contains12×84=1008 reconstructible original-derived silhouette bytes, not merely hashes. Final HDA preserves original silhouette/color structure, calibration and source-color locks. The authoring audit counts36781 mandatory original-color lock pixels; the other pixels are not thereby proven wholly independent. Generated raw inputs used original references. Any future publication must explicitly review these derivatives and masks. This candidate does not remove them, conceal them, or establish redistribution permission.
