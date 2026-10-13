# Weapon81 original-source audit

## Finding and finite scope

The first-level boss weapon81 uses exactly **seven static directional energy bolts**, in firing order **77, 58, 182, 163, 1, 183, 164**, from **spriteSheet8 / tyrian.shp chunk7 (zero-based)**. This is a seven-way shot pattern, not a seven-frame animation. All seven original frames were decoded and visually inspected. Their hot yellow/orange heads and dark red, tapering tails support an **energy** classification; no solid mechanical casing is present. There is no green palette color in this set.

Recommended art work is exactly seven separate, registered energy shapes with the original colors and headings. Keep each source canvas **12×14** and top-left **anchor(0,0)**. An 8× master would be96×112 per shape; a separately required4× asset would be48×56. Preserve soft energy-color falloff and inward edge antialiasing; retain zero coverage outside the original support. The original mask is binary, so fractional HD edge alpha would be an authored treatment, not recovered source alpha. Do not turn the dark red tail into a hard physical outline, add a green tint, create extra animation frames, or add a left-pointing39/other directional family members.

Recommended declared binding scope is **one seven-ID enemy-role family**, including the shared enemy uses below, while preserving every player path. The shared-use audit finds this visually/source compatible without adding weapon-provenance state: each shared use draws the exact same original ID with the same colors, coverage, canvas, anchor, and no pixel rotation/filter. Preserve the original orientation even where its heading differs from travel. Do not replace generic bank8 assets: these IDs are also shared with player shots, and **ID58 already has a player pulse asset**. This is deliberately broader than first-level-boss-only coverage. No renderer change was made in this audit.

## Direction, geometry and timing

Coordinates use screen axes(+x right,+y down). Bboxes are half-open source-pixel bounds.

| Position | Sprite | Heading | Boss turret3 velocity | Covered bbox | Covered pixels |
|---|---:|---|---|---|---:|
|1|77|down|(0,10)|(4,3)–(8,14)|37|
|2|58|up|(0,-10)|(4,0)–(8,11)|37|
|3|182|down-left|(-7,7)|(0,3)–(11,14)|43|
|4|163|up-left|(-7,-7)|(0,0)–(11,11)|43|
|5|1|right|(10,0)|(1,4)–(12,8)|37|
|6|183|down-right|(7,7)|(1,3)–(12,14)|43|
|7|164|up-right|(7,-7)|(1,0)–(12,11)|43|

- HDT weapon81: multi=7,max=7,weapani=0; no runtime rotation, animation, homing or acceleration. All seven spawn offsets are(0,0), damage1,duration255. The eighth array slot contains unused data and is excluded.
- The emitter is original enemy record53, turret3; turrets=[127,0,81], initial frequencies=[60,0,0]. Turret3 converts source velocities to(-sy,-sx). Creation advances positions1…7 and emits all seven before moving to turret1. Source: src/tyrian2.c:378–513.
- First-level event6025(index907) enables turret3 at frequency5; event6075 disables it. Further on/off intervals begin6275,6400,6900,7640,7830. Event8000 leaves frequency40. Every exact override is in source-contract.json. The event6025 dispatch is observed at retained tick7378.
- At tick7378, all seven spawn at(182,32), then first draw at that origin plus the velocities above. All retained logs show animate=animax=0. Classic drawing uses the exact top-left shot coordinates with no center compensation or shadow.
- Enemy simulation updates motion before drawing and removes shots at lifetime/collision/screen limits. Preserve those, the original layer order and the RLE blitter's linear-address clipping behavior. Source: src/tyrian2.c:1815–1910; src/sprite.c:539–575.

## Palette and transparency

- Source palette is palette.dat entry5 (zero-based). Expand each6-bit channel using(v<<2)|(v>>4). The full palette exactly matches all four retained classic7378 BMP palettes.
- Cardinals use indices113–124. Diagonals use115–123,125 plus one dark-brown index18 pixel each. RGB18=(44,24,4), RGB113=(56,0,0), RGB124=(251,203,48), RGB125=(255,231,60). Full per-frame histograms and colors are saved.
- RLE skips are transparent; every literal is opaque. No covered palette0 pixels occur. Original alpha values are only0/255; glow softness is expressed in the color ramp. No blending/additive/filter operation is used by the original enemy-shot draw path. shipblastfilter=208 is not applied by that path and is not a recolor instruction.
- Native2×/4× contacts use exact nearest-neighbor source pixels, with dark and light backgrounds, to expose the complete support and tail. They are deterministic source reconstructions, not game captures or generated art.

## All current source use sites and static reuse

The audit decoded all1,638 weapon rows and1,701 loaded enemy rows in each of the three data-table sources: tyrian.hdt(episodes1–3), tyrian4.lvl and tyrian5.lvl. `static-reuse.json` records every matching position, raw sprite ID, possible player/enemy animation range, enemy turret reference and weapon-port/option/special table reference. This is static address reuse, not proof of every possible gameplay occurrence.

- Weapon81 direct enemy users: HDT record53/turret3; episode4 and5 record790/turret3. Record790 starts with zero frequencies; this audit does not prove its event activation. Weapon81 has no direct port/option/special table reference.
- Episode4/5 weapon81 is an **eight-way** variation: the seven positions retain the exact HDT velocities/IDs, then position8 uses leftward39 at(-10,0). The declared seven-ID family leaves39 classic. This is a known partial visual replacement of that later eight-way pattern, not a missing first-level frame.
- Other original enemy paths sharing these IDs: HDT weapon78→records6/turret3 and7/turret2; weapon125→records26/28/turret1; weapon126→records27/29/turret1. These share58. Episodes4/5 retain the125/126 references. Zero initial frequency does not establish nonuse because event31 can enable fire.
- Static weapon rows with a potentially overlapping bank8 address:124 in HDT and112 each in episode4/5. Counts include loaded1000-series rows and potential animation addresses; detailed lists are in the JSON. Enemy251–255 are special operations, not ordinary weapon emitters, and are excluded as enemy users.
- All seven are additionally present in `linkMultiGr` (src/shots.c:117–141): linked rear-player port IDs10,27,32 select them by direction. Caller: src/mainint.c:4156. The larger16-direction player family is outside the proposed seven-image scope.
- Direct player table overlap includes Pulse-Cannon, Multi-Cannon, Hyper Pulse, NortShip Super Pulse and NortShip Spreader. Generic gameplay/player preview drawing: src/shots.c:95–107 and274–313. Full names/mode/power references are in the JSON.
- Bank8 runtime drawing sites were searched across src: enemy shots(src/tyrian2.c:1897–1905); ordinary and shadow player shots(src/shots.c:274–313); player preview(src/shots.c:95–107). xmas.c uses different indices225/226. Bank allocation/loading is src/sprite.c:827–857.
- Current published source binds only enemy112/113 through draw_enemy_shot_sprite2(src/tyrian2.c:1902–1905; src/entity_draw.c:41–53; src/render_mirror.c:1466–1477). All seven weapon81 shapes are classic/unbound. Player58 is separately selected as a pulse in render_mirror.c:1173–1177 and the default pack contains bullet-58-8.hda. None of the other six has a default-pack bullet asset.

### Exact shared enemy closure and compatibility

`shared-enemy-closure.json` lists each ID × table × enemy record × turret × source position, including velocity, acceleration, tracking, spawn offset, initial frequency, animation offset and unchanged pixel-transform semantics.

| ID(s) | Data / emitter | Velocity | Artwork heading / compatibility |
|---|---|---|---|
|77,182,163,1,183,164|HDT weapon81,record53,slot3; episode4/5 weapon81,record790,slot3|As seven-way table above|Only this weapon uses these six IDs through an actual enemy turret. Same static source shapes.|
|58|Same weapon81 users,position2|(0,-10)|Up-facing source matches up travel.|
|58|HDT weapon78,record6,slot3,position1|(-8,0)|Up-facing source already travels left. Retain its source orientation.|
|58|HDT weapon78,record7,slot2,position1|(8,0)|Up-facing source already travels right. Retain its source orientation.|
|58|All three tables: weapon125,records26/28,slot1|(0,6)|Up-facing source already travels down; spawn offset(-8,0).|
|58|All three tables: weapon126,records27/29,slot1|(0,6)|Up-facing source already travels down; spawn offset(8,0).|

Every row has animax0, frame-offset0, no acceleration, no homing/tracking, normal literal-color drawing, canvas12×14 and anchor(0,0). Source enemy slots rotate velocity components only; they **never rotate/mirror pixels**. A seven-ID enemy family is consistent with these originals when it retains that behavior. Weapon78 also emits201/202, and later weapon81 emits39; these other IDs remain outside scope.

First-level relevance: records6/7 are directly spawned at event1000;28/29 at1568–1960;26/27 at2100–2330. All these original direct spawns are **fire-dormant in level1**: relevant initial turret frequency0, no later matching event31 sets the relevant slot positive, and the level has no event39 link reassignment. The script verifies all34 such direct spawn rows. These are real static reuse sites, not an assertion they visibly fire in the retained boss scene. Weapon81/record53 is the positively observed seven-shape firing case at7378.

Normal gameplay loads picture3 or6, both selecting palette5 (src/tyrian2.c:790;src/pcxmast.c;src/picload.c:92). Thus the ordinary shared enemy uses have the same source colors. Retain the existing gamma/fade/global-filter behavior and unsupported-mode fallback; this audit does not claim new coverage of postprocessing or other episodes.

## Retained tick7378 evidence, no new run

Exact absolute paths, SHA256 hashes, run-summary source revisions, and all tick7378 weapon81 creation/reference rows are in `retained-7378-references.json`.

- N2 baseline/candidate: ../boss-whole-family-inward-completion-prep-20261013/runs/n2-{baseline,candidate}-completion/actual-7378-native2x.png and classic-7378.bmp
- N4 baseline/candidate: ../boss-whole-family-inward-remaining-runner-r2-20261013/runs/n4-{baseline,candidate}/actual-7378-native4x.png and classic-7378.bmp
- Existing N2 certificate: ../boss-whole-family-inward-reuse-proof-20261013/completion-certificate.json, PASS_CANONICAL_N2_SPLIT_EVIDENCE; first-level weapon81 exposed-pixel counts in firing order=[141,148,160,172,144,155,172].
- Existing N4 certificate: ../boss-whole-family-inward-n4-proof-20261013/n4-oracle.json, PARTIAL_PAIR_PASS; corresponding counts=[566,592,644,688,575,616,688]. Every shape is positively exposed in both retained lanes. These are native output pixel counts, not source-mask areas. The certificates were read and hashed, not rerun or relabeled as full-matrix results.

## Reproduce and verify

From the workspace root:

```
python boss-weapon81-source-audit-20261013/audit.py \
  --repo opentyrian-recovery-20261013-0122 \
  --data recovery-dependencies-20261013/game-data/tyrian2000 \
  --workspace .
```

Requires Python3 and Pillow only. The script writes only this new audit directory. Two independent RLE cursor decodes must agree; all seven index/mask/RGBA hashes must also match the earlier independent boss source audit. It checks current repo clean at start/end and checks all four retained BMP palettes. No builds, game launches, captures, uploads or shared-repository edits are performed.

Pinned current source: e50fff31057ee08cca6c27bb7c56f4df06f28b5a.

Key SHA256 values:

- tyrian.shp:80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0
- bank8 chunk(offset350426,size32060):9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68
- tyrian.hdt:fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b
- palette.dat:f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0
- palette5 raw bytes:7b61340087527e9d7c5b6a4dc57e81c955c21bfd2a1f4a922842b7db857b72f4
- src/tyrian2.c:0a042621d599fdba15f89012c9bb1007327cd6f5df0e0a41865ea61c08856d02
- src/shots.c:ec0f326f407849037af1a0218a1bfed1f3f2a720301a053afd3a7d25c7391405

`source-contract.json` includes every inspected code/data hash plus encoded/index/mask/RGBA hashes for every sprite. `SHA256SUMS.json` covers audit outputs.

Limits: no new gameplay evidence, replacement artwork, behavior change, or full-level/cross-episode reachability proof. Color/material classification is based on all seven original images and their actual palette, not a game-data material tag. Existing runtime certificates use their recorded historical fixture revisions; this audit only establishes the current static source and retained reference correspondence.
