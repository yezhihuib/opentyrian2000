# Enemy tank-shell pair: single-source legacy authoring

This adds two **legacy-only** authoring resources, 1220146 and 1220147, not two
new global registry entries. The registry remains 120 resources in 14 profiles;
HUD has its separate six-resource workflow. The paused terrain/cloud work is
unchanged. The previous coverage inventory's two `enemy-tank-shell` HDA files
are now maintained here; its other legacy filename groups remain outside scope.

The selected sources are in `assets/hd/authoring/tank-shell-current.json`.
Initially they point to the two approved PNGs in
`assets/hd/artwork/enemy-tank-shell-pair-v1/source/`. Those PNGs, their frozen
inventory, historical preview/debug HDA packs and proof files remain unchanged.
There is no resampling or pixel editing in the bootstrap.

## Edit once, synchronize current consumers

1. Place a newly approved PNG version in a new repository path. Copy the current
   selection to an external draft; edit its source paths, SHA256 and version.
   Do not overwrite the installed selection before applying the plan.
2. `python scripts/build_current_tank_shell.py stage --selection /external/draft.json --stage /external/new-stage`
3. Review `plan.json`. It names every generated file and expected old/new SHA256.
4. `python scripts/build_current_tank_shell.py apply --stage /external/new-stage`
5. `python scripts/build_current_tank_shell.py check`
6. Rebuild the executable and package; verify genuinely changed art visually.

The fixed geometry is single-frame 96×112 straight RGBA PNG, density 8, logical
12×14, anchor (0,0). Selection cannot change identity, size, rotation or anchor.
146 remains the fixed downward drawing and 147 the fixed down-right drawing;
neither rotates with velocity or turret angle.

Generated current consumers:
- `assets/hd/current-compat/tank-shell/enemy-tank-shell-{146,147}-8.hda`
- `src/current_tank_shell_payload_pins.h`, with the two payload-only FNV pins
- `packaging/current-tank-shell-compatibility.json`
- current production source binding and runtime manifest

The package still installs exactly the existing two names under
`assets/gameplay/`. The source selection and header are development inputs, not
additional runtime sprites. Current package generation never mutates historical
packs. Explicitly running an old historical pack still uses its historical art.

Enemy records 15/194/195 already share these resources through the existing enemy
shot role. Player shots and NEWSH6 explosion146/147 are different identities.
No source-bank proof, palette qualification, Christmas qualification, role,
render order, movement, collision or indexed simulation path changes. The runtime
still requires the complete pair, with startup-selected cache and classic fallback
if either payload is unsuitable. Choosing art does not authorize new consumers.

## Safety and verification boundary

Stage is non-mutating and outside the repository. Apply re-derives the plan and
checks source hashes, old outputs, staged bytes, authority and temporary-path
collisions before writing. Paths reject traversal and symlink components.
Individual replacements are atomic, but the whole operation is not a crash-safe
transaction; inspect and restage after interruption. Never hand-edit generated
HDA or pin headers. All global/HUD authoring operations preserve the shell pair,
and shell operations preserve global/HUD sources and current outputs.

`tests/test_current_tank_shell_authoring.py` uses synthetic diagnostic PNGs, not
edits to the approved art. Runtime/native evidence is separate from the source
binding. Linux controlled-fixture checks do not imply Windows/GPU or full campaign
coverage, and static record sharing must not be described as native execution.

Run the current scoped renderer checks with:

`python tests/run_current_tank_shell_renderer_tests.py --root . --out /external/new-renderer-test`

This compiles extracted production loader, role hook, wrapper and blend primitive
with ASan/UBSan. The compositor is a strict spy, not a substitute for native
visual testing. Historical prototype tests are retained unchanged.
