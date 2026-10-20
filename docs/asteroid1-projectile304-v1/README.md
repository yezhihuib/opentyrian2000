# ASTEROID1 shared enemy projectile304

One optional static projectile image replaces only the authenticated surviving
enemy-shot rendering role for source304 in normal Episode1 physical level1.
This is a shared-source visual role, not turret273-only ownership. There is no
emitter lineage, weapon state, movement, collision, timing or RNG modification.
The original indexed blit still executes exactly once.

The optional catalog now has79 images in24 finite families:55 body source-record
dependencies plus this independently authenticated projectile source. The prior
78 payloads and two629-entry default packs are unchanged. The historical273
body checkpoint's classic304 proof remains accurate for that earlier commit;
this separate checkpoint adds its enemy-role visual replacement.

## Source and exclusions

The source is the32,060-byte player-shot subbank inside normal TYRIAN.SHP,
loaded as spriteSheet8. SHA256 is
`9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68`,
FNV1a64`2b63027f74aaa21e`. This is NOT enemy NEWSHD logical bank8.
Selector304 occupies the bank's final28 RLE bytes and decodes to13 opaque
cells in a12x14 tile, bbox x4..8/y5..9. Full bank bytes and live bank identity,
not merely these13 pixels, establish the source.

Christmas304 has identical pixels but comes from a different32,404-byte bank;
Christmas and spriteSheet12 are excluded. Christmas spriteSheet12 has identical
content in a separate allocation, not a pointer alias. Normal spriteSheet12's
304 is empty. Ship bank9/304 is unrelated and excluded.

Original HDT users include weapons121,142,144,624 and their1000-offset duplicates.
Enemy records143/144/273 share this source; only the five record273 actors are
scheduled in physical level1. Other levels are outside admission. Player
special8 SandStorm uses weapon624 and source304; its heads and shadows remain
classic. Episodes4/5 player weapon121 uses encoded7304; that player-only decode
is not broadened. No different active enemy animation base reaches304 in the
three original item tables. Admission authenticates source+role, not these
weapons or emitter records.

## Art and presentation boundary

Imagegen refines the original orange/yellow diamond, without new animation,
external glow, shadow, rotation, extra particles or a larger footprint. The
retained master and prompt are registered to96x112 density8. Alpha is exactly
opaque in the13 original logical cells and zero elsewhere; transparent RGB is
zero. Coordinates and anchor0/0 remain original. No procedurally authored art
or recoloring is introduced.

Private material140 and role1400304 use one independently pinned optional
resource. Exact source bytes, normal-level scope, explicit enemy-only wrapper,
INDEX8 surface/layout, clipping and presentation guards all remain required.
Generic/player routes cannot borrow its private draw lease. A failed resource
or unknown source falls back to classic; integrity loss after an accepted
family draw rejects the frame rather than mixing an untrusted composition.
Live source bytes are checked every callback; cached RGBA/resource integrity
is checked once per logic tick, not against arbitrary same-tick memory changes.
The disk resource is an immutable cache for the selected-root epoch; replacing
it on disk requires renderer cache shutdown before it is reloaded.

## Verification boundaries

Portable receipts, production-extracted tests and actual original-engine paired
2x/4x evidence are recorded in validation.json. Native runs retain body273 HD
on both sides. Comparisons preserve original state/RNG/INDEX8, firing, collision,
damage, allocation and previous HD commands. Changed pixels must remain within
authentic304 opaque cells, including overlap, post-emitter-death shots and
collision disappearance. Off/missing/corrupt controls must be baseline-exact.

Native tests use disclosed assisted original-event windows and headless SDL
software readback, not natural-campaign, whole-level, interactive desktop,
Windows or GPU certification. Optimized and ASan/UBSan tests do not imply
LeakSanitizer coverage when it is disabled. No GitHub publication is part of
this local checkpoint.

### Final native and extracted observations

Sixteen paired native cases pass:10 positive and6 off/missing/corrupt controls,
1,800 paired logical ticks and168 paired native captures. All five original273
actors appear; other shared source users143/144 are not scheduled here and are
not native-certified. Positive cases emit72 five-shot volleys/360 projectiles,
with5,572 accepted HD304 draws. There are24 unchanged positive-case collision
witnesses and56 surviving draws whose emission is traced to the actor that
actually died. A broader time-after-death count is not used as lineage proof.

All105,040 changed native subpixels remain inside the13 original occupied cells,
including5,162 changed logical cells overlapping decoded opaque body canvases.
All six controls are baseline-exact; all original state/RNG/INDEX8, body commands,
fire and collision traces remain equal. Native origins span x54..275/y6..190;
six captured draws partially cross the184-row gameplay viewport. Negative-y
and horizontal-wrap surface limits are extracted-test coverage only.

Optimized and ASan/UBSan each pass32,060 cold plus32,060 warm source-byte
mutations,22 malformed-resource fixtures over three frames, full compositor
coverage with10 clipping origins, exact-once original indexed blit, generic
player lookup/private-lease exclusions and640 original shot-loop comparisons.
Catalog verification covers1,258 default and79 optional HDR1/PNG entries,
77 metadata exclusions and234 resource corruptions. Warm/shield/Talon regression
passes3,265,773 checks per optimized/sanitized run with original ship-sheet
source tests enabled. LeakSanitizer is explicitly disabled.

All four earlier body-family compatibility suites also pass optimized and
ASan/UBSan:272/275/276/273 retain68/108/114/180 negative fixtures per mode.
The273 suite retains7,040 animation comparisons,120 allocation cases,25 damage
cases and complete weapon-byte checks; its current304 fallback assertion is
explicitly for an invalid source, not the newly admitted authenticated role.
