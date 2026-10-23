# Charge Cannon: one editable body, nine derived states

The approved normalized **96×112 RGBA master** is
`authoring-inputs/charge-body-current/master.png`. Together with the data-only
`recipe.json` in that directory, it is the only current image/effect input.
The nine files under `derived/` are generated previews, **not nine editable
sources**. The original V2 image is provenance only and is not needed to build.
No original game PNG, index arrays, private data, fonts, NumPy or network access
is required. Python 3 and Pillow are required for authoring/preview/package
validation; the compiled runtime still consumes HDA files only.

The fixed, reviewed `scripts/current_charge_body_recipe.py` derives the three
phases × three charge levels. Production uses role 145, bank 9 sprites
258/259/260, 277/278/279, 296/297/298, density 8, logical 12×14, anchor (0,0).
Every HDA identity is `1450000 + sprite`; no global registry entry is added.
The original six Marlo/Plasma body workflow and its generated header are
unchanged. The default `build_current_sidekick_body.py` still means those six.

## Edit once, regenerate all nine

Edit only the master and/or recipe. Prefer a new versioned path under
`authoring-inputs/` to retain the previous editable input. If the master changed,
update the recipe's `master_sha256`. Create an external candidate JSON with
**exactly** these fields (fill in the two actual SHA256 values):

```json
{
  "schema": "opentyrian-current-charge-body-candidate-v1",
  "version": "my-reviewed-charge-version",
  "master": {
    "source_png": "authoring-inputs/charge-body-current/master.png",
    "source_sha256": "MASTER_SHA256"
  },
  "recipe": {
    "path": "authoring-inputs/charge-body-current/recipe.json",
    "sha256": "RECIPE_SHA256"
  }
}
```

A candidate must not contain `resources`, derived PNGs/hashes, generator paths
or arbitrary fields. Stage creates all nine PNGs, nine HDA files, the installed
selector, compatibility mapping and runtime manifest automatically. You never
need to type nine derived SHA values.

```sh
python scripts/build_current_sidekick_body.py --family charge-body stage \
  --selection /absolute/path/to/candidate.json --stage /absolute/path/to/new-stage
# Review plan.json and files/ before applying.
python scripts/build_current_sidekick_body.py --family charge-body apply \
  --stage /absolute/path/to/new-stage
python scripts/build_current_sidekick_body.py --family charge-body check
python scripts/build_current_craft267.py view --kind preview --output /absolute/path/to/new-preview
python scripts/build_current_craft267.py view --kind debug --output /absolute/path/to/new-debug
python scripts/package_runtime.py
```

Stage is non-mutating to the repository; its directory must be new and outside
it. Apply re-derives the request, checks source/tool fingerprints, every expected
old output and every staged byte before writing. It uses the existing atomic
replace/handled-error rollback helper; it is not a power-loss-safe transaction.
Inspect and explicitly restage after an interruption. Source changes, changed
fixed recipe code (even a comment), changed staged PNGs and stale plans fail.

The installed selector is
`assets/hd/authoring/charge-body-current.json`, using the separate
`opentyrian-current-charge-body-authoring-v1` schema with exactly nine ordered
`resources`. When staging that installed schema, checking, composing either
view or packaging Charge, validation recomputes all nine states from the master
and recipe and compares the decoded RGBA and HDA bytes. Hand-editing a derived
PNG and replacing its SHA does not make it an accepted input.

## Bounded integration

- Nine canonical HDA files live in `assets/hd/current-compat/charge-body/` and
  have destinations `assets/gameplay/option-charge-bank9-{sprite}-8.hda`.
- Current overlays are 151 (the existing 142 plus exactly 9 new names). Both
  views contain 650 files. Their frozen 641-file bases retain their original
  digest; the 499 non-overlay members remain byte-exact.
- The current runtime has 1015 logical files, including 646 gameplay files.
  Global resources remain 120; source bindings remain 252.
- All 19 existing authoring families carry the finite 12-path Charge input
  closure (selector, master, recipe, nine derived PNGs) plus its mapping. The
  fixed script modules are copied from `scripts/`, never selected by candidates.
- Legacy authoring plans additionally fingerprint just the new Charge
  dependencies: those 12 inputs, mapping, fixed recipe module, shared Charge
  compatibility module and shared sidekick builder. This is not a redesign of
  the pre-existing families' complete tool-fingerprint boundaries.
- Packaging requests containing any Charge consumer (including case variants)
  must contain exactly the nine canonical names and prove their derivation.
  Historical/custom manifests with no Charge keep their prior generic behavior.
  The old historical exporter and its 637-gameplay selection are unchanged.
- Current content accounting is 1015 logical / 889 unique contents. The original
 126 duplicate groups and 12911168 duplicate bytes are unchanged; this tooling
  neither aliases nor deduplicates physical files.

The fixed bootstrap is `tests/fixtures/charge-body-bootstrap-v1.json`.
Historical proofs use a separate exact five-C-file inverse and independently
remove only the new selector plus nine HDA assets before the old projection.
The prior P9 ledger, historical source inventory and render-boundary fixture
are not rewritten. Current production binding records the real current C
bytes rather than presenting the old source receipt as new acceptance.

Tests: `tests/test_current_charge_body_authoring.py` covers candidate/installed
schema separation, regenerated PNG/HDA guards, the single-master update through
both views and a 1015-file runtime copy, existing-family coexistence, stale
plans/tools, partial/case-variant package requests and malformed inputs.
By default, the isolated runtime-content test suppresses permission changes.
Set `CHARGE_REAL_COPY_OUTPUT` to a new external output directory to additionally
run the actual package CLI with real free-space and permission checks on that
same single-master update; a receipt is written next to the output. This real
copy is a synthetic authoring test, not an approved-art runtime release.
Renderer tests are separate in
`tests/run_charge_body_renderer_tests.py`. These bounded checks do not establish
Windows, GPU, full-campaign or natural gameplay acceptance.

The existing asset-index default build uses the 650-file current debug view. Its
small availability map recognizes only the exact nine Charge IDs in the
`player` / `tyrian.shp#spriteSheet9` combination; other sheets/categories do not
inherit that binding. The category remains generic. This records resource
availability, not runtime eligibility or a claim that a draw used HD. Default
`play --no-launch` retains the existing current-view launch route; no new menu
or game launch is added.
