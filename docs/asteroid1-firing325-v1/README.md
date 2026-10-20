# ASTEROID1 firing-lamp installation

This local checkpoint adds NEWSHS record 325 as one coherent three-image family
under the existing normal-data Episode 1 physical level 1 ASTEROID1 opt-in. Use
`--asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1` during ordinary campaign
progression. The option does not select or play a level. The bounded optional
catalog now contains 41 images, 17 independent families and 45 source records.
All prior 38 PNG/HDR1 pairs and both 629-entry default catalogs remain unchanged.

## Original source and firing

The complete 77-byte record is pinned to FNV1a64 `521b35b127dbdc53`. NEWSHS is
logical bank 23, 46,566 bytes, pinned to `f22ec1295ced5d11`. It owns a separate
renderer-private immutable snapshot. Existing NEWSHD remains 42,012 bytes with
its original pin/cache. Correctly bound NEWSHS can occupy any of the four
loaded bank slots; ordinary spriteSheet8 and equal numeric bases in another
bank cannot qualify. Every eligible call compares all current source bytes,
including cold corrupt input, reload, rebind and same-address reuse.

Nineteen original event 6 allocations in pool 25–49 occur at curLoc 3716, 3800,
3884, 5284, 5368, 5704, 5732, 6460, 7216 and 7244. Event placement and the original
JE_makeEnemy RNG call remain intact. Each actor uses four original quadrant
calls, offsets 0/1/19/20. Link 0 destruction, armor, value, ice, scrolling,
allocation failure, culling and per-row clipping remain original engine work.
No actor requires a neighbor. No actor, projectile or gameplay field is added.

The original eight entries are 277, 277, 277, 125, 125, 277, 277, 11. Initial entry 1
holds with active 2. Only successful ordinary shot allocation activates the
sequence. The engine draws before firing and pre-increments while active 1;
entry 8 returns to active 2 and holds until a later successful shot. The next
eligible draw wraps 8→1. Full shot pools do not activate the hold; another shot
during an active sequence does not restart it. Ice skips firing but does not
stop an active body sequence. No timing, loop, interpolation or new pulse stage
is introduced. Weapon 145 retains ordinary spriteSheet8 frames 112/113.

## Artwork and runtime boundary

The built-in image generator authored a smooth 2D gray-metal master and dim,
bright and unlit indicator states. The deterministic converter uses one common
opaque housing and samples generated indicator artwork only within the
original logical 7×4 region at x9..15/y2..5. All 672 occupied source cells remain
opaque, including gray rails, supports and the dark right-side recess. State
differences outside that region are zero. Masters, provenance and final PNGs
are retained; no procedural geometry or recoloring replaces the generated art.
Internal density 8 is distinct from native 2×/4× game display size.

Private NEWSHS resource filenames and roles are explicit: bases 11/125/277 use
roles 1080011/1080125/1080277, logical 24×28, density 8 and zero anchors. All three
must pass exact header, length and payload checks before any is used. Missing
or corrupt one disables this family coherently. Selected-root failures remain
sticky until shutdown/reset; the other 16 families remain independent. A source
or resource integrity failure after a successful quadrant rejects that whole
HD frame. Renderer shutdown revokes both source snapshots independently.

Live guards preserve full source/record/context identity, original pool,
availability, positive current armor, zero link/drop/launch/damage-alternate
fields, complete 20-entry graphics array, exact turret/frequency and animation
fields, nine legitimate active/cycle combinations, zero intrinsic motion,
reversal 100, enemyground=false, explonum 12 and exact quadrant origin. Current
armor/value, ice and shot countdowns are intentionally unconstrained.

## Validation and limits

See validation.json for the final optimized/sanitized, two-bank snapshot,
preceding paired-family regression, catalog, independent review, strict build
and actual-engine evidence summary. Unit tests use original serialized record
and weapon data and extracted production draw/fire code and MT RNG. They
compare complete actor/shot/countdown/multiposition/sound/RNG state while also
requiring actual HD admission for every eligible integrated fire callback.

Actual-engine baseline/candidate windows are explicitly ASSISTED. Original
setup/spawn events are replayed in order; raw eventRec bytes and selector RNG
remain unchanged. Prefix actors are omitted. No actor or projectile is
injected, healed or resurrected. Native 2×/4× windows cover all 19 original
occurrences, the side-clipped x 282 cases, both late x 234 cases, all three body
states, both held endpoints and original ordinary shots. This is finite
original-event evidence, not natural campaign progression or a whole-level
clear. Missing/corrupt-member and flag-off pairs verify classic fallback.

Original game data, temporary harnesses, binaries and captures remain external.
No Windows build or external publication is included. LeakSanitizer is disabled;
AddressSanitizer and UndefinedBehaviorSanitizer are exercised. Compiler address
space is bounded to 1 GiB and runtime RSS to 512 MiB. Catalog-only validation uses
an explicitly supplied historical asset root without rebuilding artwork;
that local validation path is never a public runtime setting.
