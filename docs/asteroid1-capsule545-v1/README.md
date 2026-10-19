# ASTEROID1 scheduled capsule enemy

This bounded checkpoint adds the single upright silver-grey capsule with a red
lower tip, original record 545, under the separate normal-data Episode 1 physical
level 1 ASTEROID1 opt-in. It is one static 24×28 design.

Use --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1 through ordinary campaign
progression. The option does not select or play a level. The optional catalog now
contains 35 images, 42 source records and 15 independently preflighted families.
All prior 34 optional PNG/HDR1 pairs and both 629-entry default catalogs are
unchanged. Other second-stage artwork remains outside this checkpoint.

## Original identity and presentation

The complete 77-byte record 545 is pinned independently: bank 8/newshd.shp, size 1,
ani 1, animate 0, base 77, original armor 5 and value 10. Its source has no turret,
launch, drop, damage-image alternative, rotation or animated pose. Ordered tiles
77, 78, 96, 97 occupy 255 logical cells. The occupied bounding box is [6, 3, 13, 25]
in xywh coordinates, or [6, 3, 19, 28] with exclusive right/bottom edges. The last
occupied row is 27; bottom-edge clipping is covered explicitly.

All 13 scheduled appearances are original event 10 actors in pool 75–99, links
1–9, curLoc 4080–7160. Event 19 changes the original down, left and right movement;
the capsule remains upright throughout. Later event 20/event 27 assignments with
reused links remain authoritative. No applicable normal-campaign event 33 gives
these actors a drop. Explosiontype 5 retains the original enemyground=false
simulation detail even though event 10 is called Ground Enemy2. Renderer code
does not alter events, movement, position, armor, destruction, RNG or INDEX8.

The built-in image generator authored one transparent smooth-edged silver-grey
metal master and deep red lower tip. The converter aligns it once and clips alpha
inward to the exact original occupied cells; no pixel staircase is used as the
new design geometry. The transparent master, exact prompt and final density 8
PNG are in assets/hd/artwork/asteroid1-capsule545-v1. Native small display is the
primary visual review. Density 8 is internal asset resolution, distinct from
native 2x and 4x display scales. Original game data remains external.

## Guard and fallback boundaries

The private loader requires role 1080077, density 8, logical 24×28, zero anchors,
exact file size and exact RGBA fingerprint. Missing, corrupt, foreign-role or
unsupported-density art falls back independently to the original capsule.
The other 14 families do not depend on this image. Warm resource failure is
sticky until renderer reset. Every accepted call checks the current loaded
bank bytes against the renderer-owned immutable bank snapshot and checks the
complete serialized source record independently. A dependency failure after an
accepted quadrant rejects the whole HD frame.

Each call checks the live slot, record type/pointer, loaded bank 8, full static
animation and 20-entry graphic sequence, size, availability, positive current
armor, filter, pool 75–99, links 1–9, drop 0, zero turret/launch/damage-image fields,
context consistency and original draw origin. Positive armor is unrestricted to
preserve difficulty and damage. Motion fields are unrestricted; context must
match live state, including zero motion. The four ordered original quadrant
calls 0/1/19/20 and all original clipping are retained. Existing physical-level,
ordinary-mode, lease and INDEX8 surface gates remain in force.

## Finite validation

See validation.json for the precise optimized/sanitized source tests, catalog,
strict build, independent review and assisted actual-engine receipts. Compiler
address space is limited to 1 GiB and runtime RSS to 512 MiB. LeakSanitizer is
disabled. Catalog-only verification uses an explicitly supplied historical
asset root; no private historical path is part of public runtime configuration.
The converter is checked for exact reproducibility.

Assisted original-event windows are explicitly distinguished from natural
campaign progression. No actor is injected, revived or healed. Original event
bytes and selector RNG state must remain unchanged. Native 2x and 4x paired
baseline/candidate runs compare original gameplay, RNG, INDEX8, actor/call and
event traces, plus prior accepted HD command order. Missing/corrupt/flag-off
pairs check exact classic fallback captures and commands.

The extracted production unit suite passes optimized and ASan/UBSan, including
all 77 cold and 77 warm serialized-byte mutations, both pool boundaries, all
255 positive armor values, every link, zero/down/left/right and unrestricted
later motion, six partial clipping origins with three filters, sticky frame
rejection, 16 malformed/missing fixtures and bidirectional independence from
all 14 existing families. The shared snapshot suite passes 717 checks across
15 families and 42 dependencies in both modes. The preceding fork284 suite
passes optimized regression. Strict production compilation has zero warnings.
Catalog verification accepts 1258 default entries and 35 optional entries.
Independent code review has no blocking findings and reproduces PNG/HDR1 exactly.

Eight enabled pairs cover four assisted original-event windows at native 2x
and 4x: curLoc 4080–4220, 5600–5740, 6712–6852 (70 ticks each), and 7160–7320
(90 ticks). Together they witness all 13 original scheduled instances at both
scales, including each later link's left/down/right/down transitions. Per scale,
2058 new and 282 prior accepted HD commands and 430 complete four-quadrant
actor-frame witnesses are observed. All 14 original traces, original actor/call
and event traces, and prior HD command subsequence are exact. Every frame has
zero coverage mismatch and zero rejection. Captured differences stay entirely
inside original occupied source cells.

Three additional first-column pairs cover missing 77, corrupt 77 and flag-off
physical level 1. Missing/corrupt art accepts zero new calls and preserves all
70 prior calls; complete frames.tsv and native PNG bytes match baseline. Flag-off
accepts zero HD calls and keeps frames, commands and captures exact. Runtime
fallback is directly witnessed for the first column; later regimes have enabled
paired engine evidence and source/unit fallback evidence.

Selectors preserve all 5772 active eventRec memory bytes by direct memcmp, raw
FNV b839e2440d1b5eff, serialized-field FNV 01d73c470a9401b1, and RNG fingerprint
8005e0d4ef40f5b1. Only original setup events are replayed before the selected
original spawn ordinal. Native 2x screenshots at first-column tick 20 were
parent-reviewed before commit; later ticks 30/60 and native 4x captures were
inspected separately. Captures are unresized 640×400 and 1280×800 renderer
readbacks. The tested render object matches strict production exactly. Peak
sampled runtime RSS is 94.3 MB. No original data or runtime captures are committed.

This is not natural-campaign, whole-level, Windows, fullscreen/GPU, performance
or LeakSanitizer acceptance. No external push or Windows package is included.

Rebuild: prototype/build-asteroid1-capsule545-art.py --data ORIGINAL --out OUTPUT

Tests: tests/test_asteroid1_capsule545_assets.py --data ORIGINAL --out OUTPUT
--sanitize. Add explicit --sdl-include paths if pkg-config is unavailable.
