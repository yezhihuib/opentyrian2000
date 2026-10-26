# NEWSHI shared large aircraft — accepted contour V2

The two original image-generation outputs, exact prompts, and original generation provenance are retained unchanged. No user screenshot is an authoring input. The private screenshot only identified the shoulder defect; it is neither packaged nor referenced by the executable recipe.

`registration-recipe.json` and `scripts/current_large_newshi_compatibility.py` deterministically register the original normal raw into one 96×84 native / 768×672 HD master. The V1 silhouette is constrained by immutable original-derived binary masks. Four local inward alpha mattes then reproduce the user-accepted V2 shoulder/nozzle edges. Retained RGB is unchanged; 452 pixels become fully transparent;344 of these require nonzero hidden RGB to be cleared. No visible texture repaint, global blur, or whole-plane shrink is used.

The seven normal crops are derived together from this master at native offsets 24,0; 48,0; 0,28; 24,28; 48,28; 72,28; 36,56. They reassemble byte-exactly. The damaged nose is registered from the one open-center raw; bases268/272 are deterministic piston offsets from270. Each state has its own immutable native alpha mask and original unchanged-cell constraint. The first five nose rows remain exact across all states. The master/crops under `derived/` are outputs, not independently editable inputs.

Accepted master PNG SHA256: `2ef027faa1cff76cc6a1269ba0943eac4de2ca4b77194348a297bbfacd5f9062`.

These are NEWSHI bank13 records302–308, not NEWSHF bank10. Ten HDR1 resources use IDs2100018–2100027, 24×28 native geometry, density8 and anchor6,7. Runtime parts remain independent entities, damage states, links, collision, positions and clocks. Nose projectile151 and its original timing are outside this art family.

Rebuild with `scripts/build_current_large_newshi.py --root . stage --selection assets/hd/authoring/newshi-large.json --destination <fresh-external-dir>`, then `apply --destination <same-dir>`. Stage/apply checks source closures and all derived bytes before writes, with handled-error rollback. It does not update production source bindings. `scripts/check_large_newshi_pins.py --game-data <original-data-dir>` independently verifies bank, records, all40 source tiles and all16 binary masks/differences without emitting original game data.

Art acceptance is not a claim of full campaign or Windows/GPU runtime qualification. See the separately produced bounded runtime reports for actual coverage.
