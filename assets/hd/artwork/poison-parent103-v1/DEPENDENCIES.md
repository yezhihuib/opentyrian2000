# Poison Bomb parent103: dependency and reuse evidence

## Finite binding

Only player spriteSheet8 frame103 / asset key80103. Density8, logical12×14, anchor(0,0). The normal draw call already uses shotX+1, shotY; do not compensate for this twice. Source frame103 has no animation. Only one new HDA is supplied.

Original reference was decoded from the owner's local legal tyrian.shp and palette block5. Indexed source SHA256 including mask:221fea96631c3c61b5b65298dd8c0436588a323ca1558eb93773b95e2e8fa78b. Source opaque area96 logical pixels, bounds[2,1,11,13],68 brown-family and28 green-family pixels. These observations set identity/placement; the artwork was repainted rather than tracing pixel geometry.

## Actual firing and collision chain

Port33, front mode1, power1..11 selects shot636..646 in each of e1–3, e4 and e5. Each active pattern has sg103, del255, weapani0, attack171, trail255. Thus103 remains static before impact, has no parent trail, and attack171 yields chain71 with nominal parent damage1. Vertical acceleration advances it upward under the existing motion code.

On an actual enemy collision, tyrian2.c resets shotMultiPos[SHOT_MISC], invokes player_shot_create(0, SHOT_MISC, impactX, impactY, ...,71, playerNum), and releases the parent. This is not a time-based visual morph. Do not fake child emission or modify collision/RNG to make the preview easier.

Shot71 has multi8/max8, del8, sg214, weapani3, attack1 and no further chain. It emits the eight existing patterns. Each surviving child cycles214→215→216→217, then repeats while lifetime remains. All8 pattern offsets/velocities are preserved by the game. The child has trail type12. Explosion type12 has base76/TTL7; increment-before-draw plus the draw's+1 selects explosion-bank78..84. These are a different bank from player spriteSheet8:78..84.

Accepted child214–217 and green trail78–84 assets/bindings remain byte-identical. Their current source/HDA hashes are in dependency-bindings.json. Existing green-head shadow and smoke ordering behavior must remain unchanged. Parent103 remains on ordinary physical-object shadow behavior.

## Reuse across upgrades

All33 normal configurations (11 powers ×3 table groups) share the same parent and descendant identities. Powers change quantity, spread, offsets, cadence and pattern sequence, not parent artwork or animation. Powers1/6/11 correspond to weapon records636/641/646 and emit1/3/5 parents per call. Power7 uses2-at-a-time across4 pattern positions, another behavior-only difference.

No sidekick or supplemental player2 path in the audited normal scope adds a103 use. The loaded tables also contain byte-identical unused record aliases1636..1646; these are not evidence of another normally acquired weapon or an additional image identity.

Episode4/5 parent records differ from e1–3 only in shipblastfilter240→16 within the audited shot records. The shot71 records are identical across all3 tables. Do not overwrite that original per-episode filter distinction. Supported normal acquisition comes from the super-arcade SAWeapon table for Stealth Ship and Dragon, not a claim that port33 is sold in the first level shop.

## Runtime trial required

After root's offline art acceptance and current island integration priority, the sole main-repository writer should use the already-existing legal-loadout fixture with front-port33 and powers1/6/11 at Integer2x/4x. Powers1/6/11 cover the same artwork with increasingly crowded emissions; they are representative visual cases, not proof that every power was played.

At least one real parent collision must observe parent103→shot71→all214..217→all explosion78..84. Require normal and shadow/origin evidence, child/trail phase evidence, classic/HD/missing/invalid fallback, unchanged state/RNG/collision hashes, and no new temporal pop or occlusion regression. A missing-parent-only pack should leave accepted descendants intact and fall back103 alone. Runtime observation is still required; source-table identity reuse does not imply collision footage passed.

## Source references

Audited matrices and exact decoded pattern evidence are kept locally outside Git in player-weapon-audit/player-upgrade-matrix.json and poison-parent103-v1/dependency-evidence.json. Code reviewed read-only against b1c7d776d071d21949c55d644c192c6ec33efe1b: src/shots.c parent motion/draw and attack-chain setup; src/tyrian2.c:1504–1509 collision transition and1962–1989 explosion phase update; src/varz.c:47–58 acquisition table and876–970 explosion mapping; src/render_mirror.c:394–415 current player registry/anchors. Original binary game data and decoded reference pixels must not be copied into the artwork package or repository.
