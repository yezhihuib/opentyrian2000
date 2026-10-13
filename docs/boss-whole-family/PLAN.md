# Bounded whole-boss integration plan

Status: read-only planning and external receipts only. No game was run, no production/art file was edited, and nothing was published by this task. Implementation and runtime gates await parent review.

## Verified baseline and art

- Main checkout: `opentyrian-recovery-20261013-0122`, clean at `5629b3dda05b2aa77af3c624841320d05c0f7130`, tree `38bb894192f1f763784df9e43c54543e161d51e3`.
- Type3 recovery candidate `3ad430ed7ddafe47b26ad5e1f101f7dd17abed36` has the same tree. Slots 416–421 are occupied by its six small frames. Its fresh ordinary-type3 acceptance does not yet prove boss53 launch context.
- Frozen art is `tyrian-background-redraw/formal-boss-whole-family-v1`, not a directory ending `.43`. Fresh checks passed every input hash, all 43 output PNG/RGBA/HDA hashes, HDR1 identities/geometry, original source-mask hashes and nearest-neighbor 8× alpha.
- Forty nonempty 24×28 components, density8, anchor6,7, namespace102, key1020000+base. Three transparent audit assets238/278/282 are intentional no-ops.
- `clarification-receipt.json` preserves two prose corrections without editing frozen inputs: failed launch allocation can still activate center animation; 128/280 share image payload/PNG, while HDA ID headers correctly differ.
- Gameplay files `tyrian2.c`, `mainint.c`, `varz.c`, `entity_draw.c` are unchanged from source-audit baseline b2a6e4a. Type3 changed only the relevant renderer route among these files.

## Small production change

Use the existing `render_mirror_enemy_tile` full-composite/per-quadrant route. Do not flatten the boss or refactor the engine. Preserve each indexed original call exactly once and its order. A 24×28 asset supplies four ordered 12×14 slices, parts0/1/19/20, with original draw positions and clipping.

Reserve slots422–461 in this exact ascending-base order:

`1,3,5,7,10,12,14,16,18,39,41,43,45,48,50,54,56,86,88,90,92,94,124,126,128,130,132,162,164,168,170,200,202,206,208,240,242,244,246,280`.

The body-only Asset array becomes462 entries. Keep separate128 and280 logical slots/headers despite equal pixel payloads. Do not allocate slots for238/278/282: return false to the original empty RLE call, without suppressing it or counting it as missing artwork.

Recognize only bank2/role102, original source record46–65 and size1 using the existing `G101EnemyContext`. The source-record frame map is the audit's 20-component table. Never recognize a numeric base alone: record1 reuses every center base, and raw empty cells overlap entry470/473. Do not gate on `score_item`, `damaged`, static animation or independent motion: all have legitimate boss states. Do not introduce link, armor, animation or position writes. Absence is owned by original actor availability, not a new invisible-HD state.

Add one body-family preflight, selected-pack/density8 only, using the existing exact-payload integrity pattern. Before the first replacement validate all40 nonempty members, including damaged frames not yet visible. Any missing, corrupt, mismatched or allocation-failed member disables the complete body family for that Asset-cache lifetime. No partial body, mixed density, procedural substitute or 4× fallback. This readiness flag must not disable accepted type3, other body families, orbs, effects, terrain or HUD.

Retain original physical-row behavior: a quadrant may use HD only on the supported indexed320×200/pitch320/8-bit layout with x0..308 and y−13..199. Out-of-row, wholly offscreen, unsupported layout and extreme coordinates remain classic before subtraction/scaling. This is per-quadrant geometric fallback; whole-family resource readiness is separate. Keep original actor x/y gates and exact source alpha; do not replace RLE wrapping with rectangular clipping.

Use existing `enemy_filter_rgba` and original filter arguments/reset timing. No shadow route, new tint assets, collision-mask changes, anchor shifts or rotation. Keep world-material overlays ineligible for this body.

## Exact lifecycle to preserve

- Initial body: twenty independent sky actors, five columns/four rows120×112. Draw order is actual ascending allocated pool slots, not a hard-coded record sequence. Spawn allocation order is63,64,65,61,62;59,60,56,57,58;54,55,51,52,53;49,50,46,47,48.
- Main link142:46–55,58,63. Left42:56,57,61,62. Right141:59,60,64,65. Original events translate the two lower groups independently beginning event6000; no new art is needed.
- Center53 has source-triggered bases1,3,5,7,39,41,43,45. Eligible draw advances to8 then waits; a later firing or launch-attempt trigger can wrap through1. Pool-full launch attempts still activate animation. Threshold fixes base1.
- Records52/54 initially show50/54 with `edamaged=true`; the threshold toggles false, transient cycle2 advances directly to table index3, showing202/206. The zero table entry is never a visible intermediate pose. Original turret59 becomes active; do not impose a three-frame/reverse loop.
- Projectile side lethality preserves same-link dlevel−1 components as avail2 wrecks, removes61/65, and uses original empty238/278/282 plus nonempty240/244/246. Main threshold may affect live or already-wrecked sides; preserve the exact toggles, unsigned dlevel comparison and availability differences.
- Nonlethal ship contact can cross armor40 without invoking the projectile threshold. Lethal contact removes linked actors outright, resets links, and produces no side-wreck exception, score or cube award. Main projectile lethality clears142,42,141, including existing wrecks.
- Up to72 pre-threshold visual combinations use this same finite image set; the21 source contact panels are representative, not exhaustive runtime evidence. Do not add final-death artwork.
- All default drops are0; projectile death of53 increments cubeMax directly, and48 contributes scaled cash. Do not reinterpret old event45/link42 as a current boss drop. Never clear61/65's recycled scoreitem field or require it false for rendering.

## Dependencies and scope boundaries

1. Type3 six-frame body is now bound. Boss launch still needs actual allocation/parent/child timing proof: same25-slot sky pool, at most five free slots after full assembly, post-movement parent origin, small-child y−7, and ascending-slot update ordering. Record16 reuse remains the accepted existing route; do not broaden this integration.
2. Weapon127 and newly activated59 use accepted112/113 enemy orbs. Preserve those bytes/bindings.
3. Weapon81 is a separate unclosed family: bank8 static bases1,58,77,163,164,182,183, logical12×14, anchor0,0. Reserve future slots462–468, but do not consume them in the body patch. Seven enemy-only bindings and approved shot art are required for projectile closure. The existing player-role58 resource is not an enemy binding. Its first burst can be observed as classic while body work proceeds; label it explicitly. A future narrow enemy-shot hook must preserve the original indexed call and never modify the player-shot mapping. Decide whether to reuse identical approved58 pixels or introduce a distinct enemy resource only during that separate review.
4. Required115 effect resources are already present. Preserve generic hit, ground-large, air-large and repeated-small routines and their capacity/order. Source/unit coverage is not a claim that all115 IDs were exposed in one actual explosion.
5. Fixed value effect newsh6:185 remains a separate generic stale-scoreitem edge. Do not call this body batch all-mode pickup closure.
6. Bossbar event79/link142 and `draw_boss_bar` stay byte-identical. Its minimum active armor, hit color/decay, y7 primitive bars, level-timer placement and removal remain indexed original UI. Existing HUD ownership must not cover the bar. No health values or game-state changes belong in this patch.

## Source/unit gates before any game launch

1. Freeze baseline commit/tree, selected pack, official data hashes, frozen art inventory, source contract and private observer/fixture source hashes. Revalidate clean production diff and prior families/HUD preservation.
2. Verify the40-slot bijection, every record/base/part mapping, all43 mask identities, all256 filter arguments, alias payload equality and distinct header identities. Check the center common structure and exact approved output hashes. Keep transparent files as audit material only.
3. Execute extracted production loader/route tests: all40×4 calls; initial and damaged frames; null/wrong context, record1, records45/66, wrong size/bank, invalid part; entry470/473 and all prior family coexistence. Confirm no raw-cell alias and no accidental ground material.
4. Exhaust each required-resource failure position: missing file, malformed header/size/truncation/trailing bytes, changed alpha/RGB payload and allocation failure; no HD body member may draw. Verify failure-cache lifetime, fresh cache recovery, selected-pack/density1/4/debug gates, and unaffected other families. Removing transparent audit files must not disable the body.
5. Adapt original-RLE differential and pixel tests for all43×4 cells, normal/filter writes, supported partial vertical clipping, physical x row-wrap boundaries, bad layouts and INT_MIN/MAX. Check original indexed writes and exact alpha independently of the HD route. Geometric fallback must remain local to each ordered call.
6. Test unmodified lifecycle branches with original decoded records: initial negative-dani, center pause/wrap, launch allocation success/failure, all three side conditions, threshold from intact/wreck/absent combinations, direct side/main projectile deaths, nonlethal/lethal body contact, stale-scoreitem preservation, value/cube rules and bossbar. These may be extracted-routine fixtures, but must not be presented as game captures or natural combat.
7. Review instrumentation before launch. Existing scene callbacks miss unbound boss/non-orb shots. Private observers must run at original actor draw, spawn/launch, enemy-shot creation/draw, damage/contact and effect-admission boundaries; they must not consume RNG or mutate source state. Record source weapon ID at creation, not infer it from shared sprite112/113. Confirm observer-on/off state/RNG equivalence.

## Minimal actual windows, chosen from source first

### N: one log-first no-fire census

First execute only a finite original-event replay0..7454 inclusive, retaining compact relevant logs from6625. Use the already-reviewed private player-survival convention, with exact disclosure. Do not inject enemies, damage, projectiles, events, gear or suppress original shot contacts. No captures/video on this discovery pass.

Source anchors, still predictions until actual logs confirm them:

-6653: first row;6681/6709/6737: subsequent rows.6753: continual damage/bossbar setup.
-6772..6824: first predicted fully in-bounds vertical body rectangle.6799..6806: candidate eight-state cycle;6802: candidate intact still.
-7353: lower-group split;7378: first weapon81 enable and launch disable;7428: weapon81 disable;7453: first return event. End7454, without extending to9453.

Retain per-tick full original state/RNG/input/indexed-frame hashes; actual slots, availability, type/link, armor/damaged/scoreitem, geometry, animation and firing/launch counters; ordered bank/base/part/filter draws; original alpha intersections; successful/failed allocations; source-weapon shot data; effect admissions; bossbar state. Distinguish attempted draws, alpha intersections and finally exposed RGB. Verify all20 allocations rather than assuming the source ordering succeeded.

If this finite census fails to expose a promised source state, stop and diagnose clock/mode/pool/visibility/observer coverage. Do not silently extend or start whole-level video.

After successful logs, freeze exact retained windows and the compact baseline/candidate matrix. Reuse that baseline census where possible. Capture only:

- One native2× contiguous eight-state center cycle with intact body, plus one held endpoint or trigger boundary if needed to prove pause/restart. Expected6799..6806 is a candidate, not a promised runtime result.
- One native2× split-claw/first-burst still chosen near7378 from actual exposure. Retain the burst's compact logs even if a sprite is clipped in that still.
- Native4× spot checks at the chosen intact and split stills. These are true4× presentation spots, not a complete4× lifecycle claim.
- Missing one late required body member, corrupt a different member, and unsupported density4: one matching intact still each versus its baseline. Use a late damage base, e.g.280, for missing-resource proof so a visually intact-only run still demonstrates complete-family preflight. All40 failure positions remain source/unit coverage.

### P and R: two separately scoped original-routine lifecycle trajectories

Both use actual source-spawned actors and original game damage/contact/explosion routines, paired baseline and candidate with identical private inputs. No direct writes to enemy armor, frames, links, availability, turret counters or effects. Pin target slots/coordinates and exact action ticks from the census before launch; guard unique original collision candidate, source armor, link, shot pool/capacity, original difficulty and RNG fingerprint. Artificial projectile/contact positioning must be disclosed as a fixture, not natural combat. If fixture authorization does not cover a proposed input override, pause for it.

P sequence: a small ordinary main hit and one99 ice shot if hit/ice actual coverage is claimed; allow original ice timer to expire; lethal projectile on left42 while core is intact; core nonlethal threshold to40; wait for original52/54 weapon59 firing; lethal projectile on right141; lethal projectile on core142. This covers pre-threshold left wreck, threshold applied to an existing wreck and a still-live right side, right same-link wreck, center locking, both newly active turrets and main linked removal of both wreck groups. Damage values come from the guarded live armor;99 is reserved for ice and250+ encodes another source behavior.

R sequence: reduce one right141 target to original contact damage, then perform one guarded lethal body contact to produce an absent side; reduce one core target to just above40, use a nonlethal body contact to cross40 without a graphic transition, then a small ordinary projectile to invoke the real threshold while left42 is still live and right141 absent; retain59 firing; reduce core to contact-lethal armor and use the original body collision branch to clear main142 plus remaining left42. Verify no ram score/cube award. Release private invulnerability only for the guarded contacts, maintain actual damageRate, and guard player health/contact uniqueness; never modify enemy state to fake these outcomes. At normal armor254 and contact rate2, core42→40 by contact is a suitable example; derive actual values rather than assuming normal difficulty.

This pair is deliberately asymmetric to minimize actual runs while exercising both threshold propagation paths and both projectile-wreck families. Left-side ram absence and every72-way composition remain original-routine unit/source coverage unless a separate mirrored R lane is explicitly added. The pair must not be called exhaustive combat validation.

Choose interventions within the earliest useful complete-body intervals, preferably after the natural cycle, rather than advancing the boss fight. Capture pre-impact, first changed presentation, one clear aftermath, filter/ice representative frames, first activated59 shot, final removal and the first target-effect-clear frame. Log full intermediate state even when no screenshot is retained. Movement remains source-owned.

Stop each lifecycle trajectory after linked removal plus its original effect descendants clear and two clear presentations. Source-derived hard diagnostic ceiling: final lethal impact+75 ticks. An eight-repeat big explosion requires at most3+7×7 ticks for the last big repeat, at most3+4 for its two-repeat child, and at most12 for its final small sprite, with conservative phase allowance. Threshold nine-repeat small sequences are shorter. Pool saturation can omit effects, so verify original admission results rather than force spawns. If the ceiling is exceeded, stop and report a fixture/observer discrepancy instead of extending the replay.

## Runtime comparison and exit gate

Compare baseline/candidate full original state, RNG, ordered references and indexed surfaces exactly, including all original enemy-shot contacts. Do not repeat the previous mistaken assumption that a private-survival run has zero collisions. Verify final exposed HD pixels with the ordered original draw/effect/layer/HUD oracle, including bossbar pixels; do not exclude inconvenient UI pixels. Source-clipped/occluded references are separately counted, never passed off as visible artwork.

The minimum actual scenario set is N, P and R, paired original/candidate as needed, with the small fallback/presentation spots above. It is not72 full fight runs. Exact lifecycle ticks and capture count are a post-census freeze gate, because source arithmetic alone cannot prove allocation/exposure. Body closure, launch-context closure, weapon81 closure and UI preservation must each have their own result. Full scene closure cannot pass while weapon81 stays unbound.

Exit only after finite source/unit gates, paired state/pixel evidence, fresh visual review, clean production diff and aggregate build/preservation checks. No whole-level clear, natural survival/combat, all-mode pickup, complete4× lifecycle, Windows runtime or GPU claim. Publication remains a later parent-owned decision.
