# ASTEROID1 linked NEWSHP gold platform

This checkpoint adds the complete eight-image, five-record NEWSHP installation
338–342, including its persistent post-lethal wreck. It uses the existing
normal-data Episode 1 physical level 1 ASTEROID1 opt-in:
`--asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1`. This option does not select
or play a level. The finite optional catalog now contains 53 images, 19
independent families and 51 source-record dependencies. All preceding 45 PNG/HDR1
pairs and both 629-entry default catalogs remain unchanged.

## Original source and independent actors

Logical bank 20 is NEWSHP, 46,204 bytes with full-file FNV1a64
`e2413e3aeab4d908`. It has its own immutable renderer-private snapshot and every
callback compares all current bytes. NEWSHD retains its separate 42,012-byte
snapshot and NEWSHS its separate 46,566-byte snapshot. A valid binding can occupy
any loaded slot; the live actor must point at that actual logical-20 slot object.
Ordinary spriteSheet8, unloaded clones, foreign banks, mutation, same-address
reuse and stale bindings do not qualify. The physical-1 gate remains mandatory
because physical 2 also uses this source family.

The canonical field-order 77-byte source stamps are:

- 338: `cbad2cf90f5c58cf`
- 339: `2ddda4009b77985a`
- 340: `cf24bb2935688c70`
- 341: `1dbea2914b901887`
- 342: `68faea6f9286755d`

Every image depends on all five records, even if a component is absent. The
original cap event 6 and platform event 12 occur at curLoc 3968, 5256 and 6488,
with links 23, 29 and 33. Event 12 calls the original allocator separately for
339/340/341/342. Each successful original constructor consumes one x-position
RNG draw before event placement. Five successful actors consume five draws;
allocation failures, first-free pool slots 25–49 and holes remain authoritative.
No merged game object or neighbor-admission requirement is introduced.

The normalized 48×84 assembly places cap 338 at (0,0), upper-left 341 at (0,28),
upper-right 342 at (24,28), lower-left 339 at (0,56), lower-right 340 at (24,56).
The top-right 24×28 cell stays empty. Each component clips, scrolls and culls
independently through the original ordered quadrants 0/1/19/20. The cap is above
the platform's left half. Map-relative placement and draw ordering are unchanged.

## Original animation and linked destruction

The exact twelve-entry live cap sequence is:
115,115,115,117,117,117,119,119,119,117,117,117.
These are lower, middle, upper, middle gold-tier lighting states. Original
horizontal eligibility controls the pre-increment from constructor cycle 0 to 1
and wrap 12→1. Vertical offscreen state and ice do not pause it. There is no extra
pulse, timer or interpolation. The four supports remain static with their exact
full graphics arrays, including inactive stored tail values.

Source explosiontype 25 means enemyground=false and explonum 12. Current positive
armor, difficulty-scaled cap value, legitimate ice and inactive countdowns are
not frozen to source defaults. Nonlethal damage only changes the struck armor.
An ordinary lethal player shot to any existing same-link component runs the
original ascending-slot linked damage path: supports become availability 1;
an existing cap becomes availability 2, damaged=true, static image 121, retaining
its original graphics tail and other unmodified state. Original effects, cash,
kill counters, sound, explosions and RNG remain in charge. No absent cap or
culled actor is recreated. The availability 2 wreck remains drawable, scrollable
and eligible for the original homing-target predicate, although ordinary
player-shot collision tests only availability 0. Source 25 excludes the ship-ram
damage path. No drop, launch, firing or extra damage image is invented.

## Artwork and material identity

The built-in image generator authored one smooth 2D gold/grey installation
master, two aligned cap-lighting edits and one dark broken-cap edit with red
detail. The platform is normalized once and sliced into four original component
boundaries, so adjacent seams remain coherent. All four generated masters,
provenance, eight PNGs and a deterministic conversion recipe are retained.

All four cap images keep the original 346 occupied cells and identical alpha.
Live differences are confined to the original 279-index-cell union. The platform
preserves opaque floor, dark recesses and rails, including the single transparent
cell in 229 at (15,1) and 269 at (12,0). The intact assembly has 3032 occupied logical
cells. Internal density 8 is distinct from native 2×/4× display size. The conversion
does not procedurally redraw or recolor generated art.

NEWSHP uses the explicit renderer material namespace 135, independent of source
logical bank 20 and existing material 108. Bases 115/117/119/121/229/231/267/269 have
roles 1350115/1350117/1350119/1350121/1350229/1350231/1350267/1350269. This prevents
collisions with unrelated NEWSHD images sharing numeric bases. Headers, accepted
commands, scene probes, regions and finite catalog inventory all retain the new
identity. Generic read_asset rejects 135; only the eager eight-member family
preflight can provide these assets. Missing/corrupt any member disables this
family without disabling a valid peer. Selected-root failures stay sticky until
reset. A dependency failure after an accepted quadrant rejects the whole HD frame.

## Validation and limits

See validation.json for exact optimized, ASan/UBSan, prior-family regression,
catalog, strict production-build, independent-review and actual-engine results.
The aggregate source suite retains the exact 17 NEWSHD families/45 dependencies,
one NEWSHS family/one dependency, one NEWSHP family/five dependencies partition.
Catalog-only verification reads all 53 optional resources and both 629-entry
defaults through the explicit historical validation input without rebuilding
artwork. That validation input is not a public runtime path.

Optimized and ASan/UBSan each pass 385 cold plus 385 warm canonical-byte
mutations against all eight member callbacks, 22,038 positive production HD
admissions, all twelve cycles/eight images, 4,960 original animation comparisons,
108 original allocation cases, 90 shot-damage cases and 128 bad-art fixtures.
All four actor-binding slots, all 256 ice values and all 255 positive armor
values are exercised. Three-bank aggregate testing passes 6,435 checks per mode.
The preceding 269, 325 and 287/288 suites also pass both modes. A clean strict
build independently compiles all 81 production sources and links with no warnings.

Actual-engine validation passes 48 paired cases: 14 enabled/clean-wreck windows
and 34 missing-member/corrupt-member/flag-off fallbacks, across 96 runs and 8,120
logic ticks. The 21,036 new accepted commands preserve the previous 22,598
accepted-command subsequence. Gameplay, original callbacks, event records, actor,
RNG and INDEX8 traces match the baseline exactly. Fallback native pixels match
exactly. No accepted frame has an integrity or coverage rejection.

Actual-engine evidence uses explicitly ASSISTED original-event windows at all
three sites. Original setup/spawn events replay in order, with raw eventRec and
selector RNG recorded; prefix actors are omitted. The original JE_makeEnemy,
allocation and event 12 paths remain intact. No actor or projectile is injected,
healed or resurrected. Cap-lethal and support-lethal witnesses use ordinary
player movement/fire and the real original shot-damage path. These are finite
original-event windows, not a natural campaign-clear claim.

The selected original placements provide actual independent top/bottom entry
and exit clipping. They do not cross a side viewport edge in these windows;
side-boundary clipping is covered by the extracted original draw/renderer suite.
No actual-engine side-boundary witness is claimed. Early destruction frames can
be occluded by unchanged original explosions and ordinary projectile restoration;
separate fire-release/move-away continuations show the persistent smooth wreck
after those effects, without changing its gameplay state.

The paired runs use headless SDL dummy video and a software renderer, with native
640×400 and 1280×800 readbacks. No desktop-window check is claimed. Original data,
captures, test harnesses and binaries stay external. No Windows build or external
publication is included. LeakSanitizer is disabled; AddressSanitizer and
UndefinedBehaviorSanitizer run. Runtime RSS is bounded to 512 MiB and compiler
address space to 1 GiB. The free-disk reserve is at least 5 GB.
