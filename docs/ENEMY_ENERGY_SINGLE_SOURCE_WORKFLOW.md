# Enemy energy seven: single-source legacy authoring

This maintains seven existing legacy enemy-shot resources, in fixed slot order
1110077, 1110058, 1110182, 1110163, 1110001, 1110183, 1110164. It adds no global
registry identities. Global coverage stays 120, plus six HUD resources and the
separate two tank-shell legacy resources. Terrain and clouds remain paused.

Selected sources: `assets/hd/authoring/enemy-energy-current.json`, initially the
approved `assets/hd/artwork/enemy-energy-seven-v1/output/` PNGs. Historical art,
masks, inventory, HDA packs and proofs remain immutable. Bootstrap pixels are
unchanged. Each source must be a single 96×112 RGBA PNG, density 8, logical 12×14,
anchor (0,0), with its fixed direction. Nonzero alpha may not extend beyond that
identity's original bank8 RLE support. Seven fixed original mask paths/SHA256
and decoded support bitsets are trusted policy, not selection fields. The builder
rejects out-of-support alpha rather than clipping or silently editing the image.

## Workflow

Create an approved new PNG at a new repository path, then edit an external copy
of the selected manifest with its path, SHA256 and revision. Do not replace the
installed selection before applying.

1. `python scripts/build_current_enemy_energy.py stage --selection /external/draft.json --stage /external/new-stage`
2. Inspect `plan.json`, including every expected old/new output hash.
3. `python scripts/build_current_enemy_energy.py apply --stage /external/new-stage`
4. `python scripts/build_current_enemy_energy.py check`
5. Rebuild executable/package and visually verify genuinely changed art.

Generated consumers: seven `assets/hd/current-compat/enemy-energy/` HDA files,
`src/current_enemy_energy_payload_pins.h`, the current compatibility mapping,
production source binding and runtime manifest. The package still uses the
same seven `assets/gameplay/enemy-energy-{id}-8.hda` names. Running a historical
pack explicitly still uses its historical artwork.

Stage does not mutate the repository. Apply re-derives outputs and checks source,
old output and staged hashes, path containment, fixed authority, and temporary
collisions. Individual writes are atomic, not a crash-safe multi-file transaction;
inspect and restage after interruption. Never hand-edit generated HDA or headers.
Global, HUD, tank-shell and energy workflows retain each other's current outputs.

## Runtime boundary

Enemy 58 is not player Pulse 58 or an older enemy orb. Existing enemy records
6/7/26/27/28/29/53 and 790 share enemy58 through their original weapons; record53
and episode4/5 record790 also use the other six. Episode4/5 extra shot39 remains
classic. No new role, source-bank, palette or consumer qualification is added.
The same seven-or-classic startup cache remains; Christmas rejects energy
before even a warm cache can admit it. Order, directions, alpha compositor,
movement, collisions and indexed simulation are untouched.

New synthetic workflow tests are `tests/test_current_enemy_energy_authoring.py`.
Historical inverse-source prototype checks remain unchanged. Independent runtime
and native evidence is separate from generated source binding: controlled Linux
fixtures do not prove natural campaign, Windows/GPU or every level coverage.
