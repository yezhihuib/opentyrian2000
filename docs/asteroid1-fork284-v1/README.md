# ASTEROID1 scheduled fork craft

This bounded checkpoint adds the static record 284 fork-shaped mechanical craft
under the separate normal-data Episode 1 physical-level 1 ASTEROID1 opt-in. It is
one 24×28 image, not an animation, random rock, turret or launch family.

Use --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1 through ordinary campaign
progression. The option does not select or play a level. The optional catalog now
contains 34 images, 41 source records and 14 independently preflighted families.
All prior 33 optional PNG/HDA pairs and both 629-entry default catalogs are
unchanged. Other second-stage artwork remains outside this checkpoint.

## Original identity and presentation

The complete 77-byte record 284 is pinned independently: bank 8/newshd.shp, size 1,
ani 1, animate 0, base 121, original base armor 6 and value 25. Its source contains no
turret, launch, drop, damage-image alternative or animated pose. It alone uses
base 121 in this bank. The four original tiles are 121, 122, 140, 141, with 270 opaque
logical cells and bounding box [3, 0, 19, 26] in a 24×28 footprint.

There are 42 scheduled instances at curLoc 3130–4750: 38 event 10 actors in the
original pool 75–99, links 1–19, and 4 event 6 actors in pool 25–49, link 0. This record
is absent from the original random table. Event 20/event 27 alter original motion,
acceleration and reversal state. Event 33 can give surviving link 1 actors drop 512.
These events remain authoritative. No renderer code changes position, speed,
events, armor, destruction, RNG, timers or the original INDEX8 blitter.

The built-in image generator authored one smooth-edged grey metal master with a
small red-orange visor, keeping the original upright fork silhouette and open
central gap. The converter performs one global alignment and inward alpha
clipping to original occupied cells. It does not invent an animated state or
redraw with code. The transparent master, exact prompt and final density 8 PNG
are in assets/hd/artwork/asteroid1-fork284-v1. Native small display was the primary
visual review; enlarged detail was supplementary. Original game data stays
external.

## Guard and fallback boundaries

The private one-image HDR1 loader requires role 1080121, density 8, logical 24×28,
zero anchors, exact size and exact RGBA fingerprint. Missing, corrupt,
foreign-role or unsupported-density art falls back independently to the original
craft. Other families do not depend on this image. Warm payload failure is
sticky until renderer reset. Current loaded bank bytes are checked on every
accepted call against the renderer-owned immutable snapshot; the complete
serialized source record is checked separately. A dependency failure after an
accepted quadrant rejects the whole HD frame.

Each call checks the live actor slot, type, source-record pointer, loaded bank,
static pose and full 20-entry sequence, size, availability, positive armor,
filter, pool/link/drop conditions, zero turret/launch/damage-image fields and
context consistency. Both scheduled pools are accepted, and original motion
fields remain unrestricted. Draw origins must match the live actor and original
quadrants 0/1/19/20. Existing physical-level, mode, lease, INDEX8 surface, clipping
and filter gates remain in force. There is no random-sky-only restriction.

## Bounded checks

See validation.json for exact finite receipts and limitations. The extracted
production harness covers all 77 cold and 77 warm serialized-byte mutations,
16 ordered quadrant calls at pool boundaries 25/49/75/99, source role/rebinding/
reload/address reuse, live static identity, link/drop cases, event-driven and
field-range motion, surface/lease/scope guards, two isolated positive cases and
16 loader negatives. Optimized and ASan/UBSan pass; compiler address space is
limited to 1 GiB and runtime RSS to 512 MiB, with LeakSanitizer disabled. The shared
snapshot suite passes 671 checks across 14 families and 41 record dependencies in
both modes. The preceding record 286 family regression also passes.

Catalog-only verification accepts 1258 default entries and 34 optional entries
using an explicitly supplied historical asset root. Default counts stay 629/629;
no private historical path is part of the public runtime configuration. The
converter independently reproduces the final PNG/HDR1 bytes exactly. Strict
production compilation passes without warnings. Independent code review found
no blocking issue; actual-engine acceptance is recorded separately below.

## Assisted actual-engine validation

Five baseline/candidate pairs pass for 145 ticks each: native 2x, native 4x,
missing base 121, corrupt base 121 and flag-off eligible physical level 1. Each
pair preserves all 14 gameplay/RNG/INDEX8 traces, detailed original actor/call
arguments and event traces, and the prior accepted HD command subsequence.
Both display scales accept 3724 fork quadrant calls and 378 prior HD calls,
with 785 complete four-quadrant actor-frame witnesses covering both pools.
Coverage mismatches and rejected frames are zero. Missing/corrupt art accepts
zero fork calls while preserving all 378 prior calls; frames.tsv and both native
captures are byte-identical to baseline. Flag-off accepts zero HD calls and its
frames, draw commands and captures remain identical.

This is explicitly assisted late-window QA. An unchanged stationary diagnostic
ends at tick 167 / curLoc 336 after player death, before the first fork spawn.
The external selector replays original setup events 1, 2, 3, 4 and 21, omits the
remaining prefix through event 152, then starts original event 153 at curLoc 3130.
EventRec bytes and the selector's RNG fingerprint are unchanged. The unmodified
original dispatcher and enemy initializer create every witnessed actor; no actor
is injected, revived or healed. The 145-tick window reaches curLoc 3420 and
witnesses 22 scheduled instances across slots 25–28 and 75–86. It does not cover
all 42 scheduled instances. Representative complete calls are tick 9 / slot 75
and tick 112 / slot 25. Later event 33/drop 512 remains source/unit evidence.

Native 2x screenshots at ticks 30 and 120 were parent-reviewed before commit;
4x captures are 1280×800 renderer readbacks and were inspected separately.
Captures are not resized, and internal density 8 is distinct from display scale.
The original HUD remains unchanged in this isolated asteroid opt-in. No BMP,
original data or runtime captures are added to the repository. The tested
candidate render object matches the final strict production object exactly.
Runtime peak RSS is below 96 MB. This is not natural-campaign, full-level,
Windows, fullscreen/GPU, performance or LeakSanitizer acceptance. No external
push or Windows package is part of this checkpoint.

Rebuild: prototype/build-asteroid1-fork284-art.py --data ORIGINAL --out OUTPUT

Tests: tests/test_asteroid1_fork284_assets.py --data ORIGINAL --out OUTPUT
--sanitize. Add explicit --sdl-include paths if pkg-config is unavailable.
