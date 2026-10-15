# Bounded validation

Baseline: d98556a7798d79980c785b5a25ba67566697bdb0. Results below cover this
finite batch and do not imply broader runtime qualification.

## Changed files

Production:

- src/render_mirror.c
- src/render_mirror.h
- src/sprite.c

Tests and documentation:

- prototype/test-plasma-projectile-blend.c
- prototype/test-plasma-projectile-blend.py
- prototype/test-plasma-projectile-scope.py
- docs/option-plasma-projectile-blend-v1/README.md
- docs/option-plasma-projectile-blend-v1/VALIDATION.md

An exact inverse removes only the new display functions/declarations and the
single raw-blitter admission/callback change. All153 production source files then
match baseline bytes. Seven forbidden scope mutations are rejected. All6,722
asset files retain identical raw bytes and Git modes, using unfiltered Git blob
hashes. No art, HDA, resource inventory, source dimensions or pack modes changed.

## Focused no-engine tests

Both optimized and AddressSanitizer/UndefinedBehaviorSanitizer builds pass the
same exact-production extraction suite:

| Check | Per build |
| --- | ---: |
| Raw original draws / original calls | 2,234 / 2,234 |
| Observed source-pixel callbacks | 2,814,635 |
| Source identity/coverage mutations | 168 |
| Admission/context guard cases | 408 |
| Per-piece edge/linear-wrap cases | 336 |
| Ordered, overlapping and repeated composition draws | 1,728 |
| Independent palette-formula cases | 28,672 |
| Direct pixel-guard cases | 15 |

The harness extracts unchanged production helpers, the exact candidate raw
blitter and its baseline version. It compares original indexed buffer bytes,
source/write order and callback count after one original blit per call. It tests
all three Normal/Christmas source identities, current decoded values and
coverage, cold/warm same-address reloads, declaration and bytecode mutations,
non-target sources, draw bounds, supported densities4/8, actual palette5,
monotone palette variants and nonmonotone fallback. Owner0, owner1 and owner2,
mixed blocks, repeated calls and all three-piece order permutations are covered.
Original malformed RLE is tested at the HD admission guard only; the legacy raw
blitter is not run on malformed streams.

This path has no HDA/resource lookup, so there are no new projectile resources
to mutate. No-HD and mixed ownership controls exercise classic/rejected-underlay
behavior. The unchanged production-art Plasma body regression also passes in
optimized and sanitizer builds:4,028 cases,100 resource variants and1,440
animation phases per build. No test-only art is installed as a game asset.
LeakSanitizer is disabled for executor compatibility; ASan and UBSan are enabled.
Unrelated font/effect collaborators use explicit isolated-test stubs.

Commands, with original data installed separately and fresh output paths outside
this checkout:

    python3 prototype/test-plasma-projectile-blend.py --data /path/to/tyrian2000 --out /path/outside/checkout/plasma-units
    python3 prototype/test-plasma-projectile-scope.py --out /path/outside/checkout/plasma-scope.json
    python3 prototype/test-plasma-body-binding.py --data /path/to/tyrian2000 --out /path/outside/checkout/plasma-body-regression --production-art

## Builds

Both baseline and candidate full Linux production builds pass:72 translation
units, optimized -O2, linked, -Werror. The pre-existing misleading-indentation
warning is suppressed consistently in both builds. Both disabled-renderer
sprite.c/render_mirror.c compile checks pass. Both private observer builds link
73 translation units. Observer patches invert with zero fuzz to all153 frozen
production source files after removing the two private helper files.

## Actual original-engine witness

Exactly four Linux SDL dummy/software processes completed in one attempt:
Normal physical9 and Hard physical15, baseline/candidate,320 real logic ticks
each. All exit0. The four original time(NULL) seeds match; none is overridden.
Complete frozen sources, binaries, original game data, dependencies, helper
sources and physical pack pins are unchanged before/after execution.

Both variants use the SAME HD-enabled manual mode, density8, and byte-identical
565-file/560-HDA selected packs. Baseline already contains every prior published
HD upgrade. Entire pre-projectile PNGs through captured tick100 are byte-identical;
captured post-projectile ticks160/190/220/319 are identical again. The broad
cloud/bullet/pickup differences during active shots are a consequence of the old
restore_classic_rect closure over overlapping connected HD regions. They do not
represent newly added art or a classic-versus-HD configuration comparison.
This explanation is established by the frozen-source mechanism and same-run
controls; direct per-restore rectangle/count logs were not captured.

Every process uses original menus and first-shop RIGHT Plasma9 selection:
10000 cash,9500 cost, original Done,500 cash,left0/right9. Default Space is held;
six one-tick default Right-secondary LeftAlt presses occur at100/108/116/124/132/140,
followed by the empty seventh at148. No equipment, money, player position,
protection, animation, timing, RNG or refill state is supplied or altered.

Both paired cases have exact equality on all320 original indexed game/display
surfaces, palettes, player/enemy/shot/particle/global state hashes, RNG
fingerprints, and original menu/input/body/shot/emission/raw-write/collision
traces. Six requests naturally succeed, producing18 independent records, six
each of raw60023/60024/60025. There are312 ordered raw draws per case. Dimensions,
radii, source/background/result bytes and original draw counts remain exact.
The seventh empty press creates no request. Ammo ends0 and refill timer95/396;
the later actual refill is outside this window.

Per candidate difficulty:

- 312 raw draws and391,968 directly observed original pixel writes
- 276 fully-inside pieces with eligible pixel observations
- 36 edge-crossing pieces with fallback pixel observations
- No zero-write draw, so every draw's actual path is directly witnessed
- 361,386 eligible source writes,15,804,032 actual HD owner1 subpixels and
  7,324,672 classic owner0 subpixels
- Zero independently recomputed RGB, owner or expected-index mismatches

Owner2 does not occur naturally in these runs; its coverage is unit-only. An
optional begin-return event was absent because of a private logger's whitespace
match. Complete ordered per-pixel compatible flags were captured and bound to
every original raw draw instead. The first analysis assertion failure and its
corrected analysis are retained; there was no engine rerun, production change,
state edit or screenshot repair.

## Native-scale visual review and limits

92 untouched actual640×400 native2× SDL PNGs pass every chunk CRC, including
IEND. Private comparison sheets paste the same full screenshot pixels side by
side without scaling, recoloring or repair; labels are outside image pixels.
Normal/Hard tick103, repeated emissions at111, and edge behavior at140 were
inspected locally. Warm original Plasma shape and order remain recognizable;
HD clouds, terrain and ship detail no longer cascade to classic pixels after
eligible pieces. Hard's original NIGHT presentation remains in place.

The original projectile art deliberately remains pixelated at native2×. This
change improves background retention and blend compatibility; it does not redraw
or smooth the source art. Edge-crossing pieces retain their previous fallback
and can still restore connected regions to classic pixels. The continuous
true-color operator is the documented approximation, not exact palette-index
inversion or ordinary alpha-over.

This is bounded first-level local single-player RIGHT-weapon88 qualification.
No actual left/dual purchase, weapon1088 firing, later refill, actual Christmas
run, native4× runtime, whole-level/campaign, Windows, physical GPU or performance
qualification is claimed. No screenshot or original game-data upload is part of
this batch.
