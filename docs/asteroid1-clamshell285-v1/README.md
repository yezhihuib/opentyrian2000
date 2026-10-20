# ASTEROID1 record285 clamshell body

This finite body-only extension adds three distinct mechanical poses157/159/161 from enemy bank8/NEWSHD, using private material143. It does not add projectile91 or drop512 art, enable generic materials, change the defaults, or claim completion of the second stage.

## Original source and scheduling

Normal Episode1 physical level1 schedules record285 at event ordinals150/233/316, curLoc3000/4000/5000, x140/100/200. Event6 uses slots25–49; d3−2 cancels the constructor's ymove2 and link1 remains original. The immediately following event33 assigns drop512; arcade-only event45 alternatives are outside admitted normal-mode scope. The static record's zero drop field alone does not describe the scheduled actor.

The original eight-step firing-gated sequence is157,159,159,161,161,159,159,157. Successful original shot allocation controls activation; full-pool failure must retain original idle behavior. Weapon24 frequency40 emits the original single selector91, which continues through its original classic blitter. The guard authenticates the entire77-byte record,80-byte weapon and42,012-byte NEWSHD bank without writing gameplay state. Armor/difficulty-scaled reward, firing, animation, linked damage, collision, drops, explosions, coordinates and RNG remain engine-owned.

## Artwork and safety

Three built-in-imagegen poses share the same smooth dark-steel shell identity. They are actual opening/closing silhouette changes, not recolors. Original support counts are362/314/252 cells in24×28. Accepted masters are registered to their exact per-pose original bounding boxes on192×224 canvases, then masked inward to original support. Generated alpha is retained inside; all RGBA outside each original silhouette is zero. All original occupied cells are represented. The closed pose has no visible warm core. The first pixelated open-pose attempt was rejected rather than integrated.

Atomic preflight requires all three resources. Private per-call leases, source/record/weapon checks, original actor/pose/layout guards and unchanged indexed writes preserve fail-closed behavior. Missing/corrupt art affects this family only. Cached payloads are checked once per logic tick, not every callback; live source dependencies are checked on callbacks. No arbitrary same-tick cached-RGBA corruption claim. Disk replacement requires cache shutdown/new root epoch.

## Validation

Portable artwork rebuild: `tests/test_asteroid1_clamshell285_art.py --data ORIGINAL_DATA --out NEW_OUTPUT`.
Catalog identity/hash/malformed-input checks: `tests/test_hd_pack_catalog.py --out NEW_OUTPUT`.
Extracted-production and native2×/4× acceptance receipts are summarized in validation.json. ASan/UBSan runs disable LeakSanitizer and are not a full leak proof. Assisted original-event SDL software windows are not full natural-campaign or desktop-interaction certification.

Linked-death tests retain the original allocator ordering: three linked285 victims produce three512 drops, and later drops may occupy an already-freed victim slot with availability2. Therefore “killed actor slot remains availability1” is not a valid invariant. The extracted test compares complete classic/HD state and original rewards instead of changing the engine to satisfy that assumption.


Native acceptance completed30 paired scenarios/60 launches at2×/4×,3,440 paired trajectory ticks. All three genuine scheduled actors and original eight-step animation were observed. There were4,380 new HD body commands,74 original91 emissions,1,178 classic91 draws,16 body-hit events and4 lethal events;4 targeted shot91/player collisions were witnessed. All517,688 changed captured physical pixels stayed within exact original per-pose masks. Fourteen missing/corrupt/flag-off pairs and two prior270/112113 pairs retain identical output. Effects over body masks had no coverage, rejection or restoration mismatch. Native contacts retain original bullets and show the distinct shell closure, not a changed firing effect.

Final extracted guard passes optimized and ASan/UBSan:72 negative resource fixtures per mode,74,368 HD admissions,23,232 firing/INDEX8/RNG comparisons,72 allocation cases,8 damage/drop cases and255×256 RAM cases. It authenticates every original42,012 source-bank byte,77 record bytes and80 weapon bytes cold and warm. Catalog verification accepts87 optional and1,258 default HDR1 payloads; all84 prior optional asset and26 prior family metadata entries remain unchanged.

All seven prior extracted families272/275/276/273/304/112113/270 pass optimized and ASan/UBSan against the new private-role integration. Warm/shield/Talon blend regression also passes both modes with authenticated Talon source tests enabled. Final receipts retain exact production and harness hashes.
