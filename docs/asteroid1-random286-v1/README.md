# ASTEROID1 continuous random-rock jewel pulse

This bounded checkpoint adds original record286 to the existing separate
normal-data Episode1 physical-level1 ASTEROID1 presentation opt-in. It is one
fixed-geometry rock with four color/light states and twelve original animation
slots. It completes the artwork identities in the21-entry original random table;
it does not complete the second stage, its other enemies, terrain or weapons.

Use --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1 through ordinary campaign
progression. The option does not select or play a level. Physical2, other levels
and incompatible modes remain classic. The optional catalog now has33 images,
40 source records and13 independently preflighted families. Both default packs
retain629 entries, and all prior29 optional PNG/HDA pairs remain byte-identical.

## Original identity and behavior

The original77-byte record286 pins size1, enemy bank8/newshd.shp, ani12, animate1,
no turret, launch, drop or damaged-image state, original value50 and base armor8.
It is the only bank8 record using bases229/231/233/235. The original sequence is:

229,231,231,233,233,235,235,233,233,231,231,229

Animation advances continuously in the original enemy draw loop and wraps after
slot12. It is not rotation and is not fire-triggered. Original repetitions and
all timing remain authoritative. The original random table selects this record
at weight1/21; no direct physical1 scripted spawn was found. Original y-speed2
and xaccel93 homing steer its live x-speed within−4..4. The renderer never
changes steering, RNG, armor, animation, event, spawn or indexed-buffer writes.

All four original states have433 opaque logical cells in one24×28 footprint.
Only65 center cells differ: neutral/off, small deep-blue jewel, larger saturated
blue with local reflected rock light, then pale electric-blue and stronger
reflected light. Every source alpha byte and exterior color remains fixed.

## Artwork and binding

A single built-in imagegen neutral slate-rock master supplies smooth painted
geological planes and a recessed mineral socket. Global footprint alignment and
inward alpha coverage preserve the original exterior. The builder derives only
continuous center RGB/light fields within the exact65-cell source-change bound.
Their inward feathering avoids enlarging a low-resolution pulse staircase. All
four final states have identical alpha and exterior RGBA bytes, so no geometry
or wobble is introduced. The prompt, master and source-bound PNG files live in
assets/hd/artwork/asteroid1-random286-v1. Original game data stays external.

Four density8 HDA resources preflight atomically, independently of all prior
families. Missing, corrupt, wrong-role, foreign-base or unsupported-density art
keeps the whole new family classic. Warm payload failure is sticky until reset.
Current source bytes are checked through the immutable private bank snapshot on
every accepted call; full serialized record286 is pinned independently. A
source/dependency failure after an accepted quadrant rejects that HD frame.

Every candidate quadrant additionally validates physical1 scope, current sky
pool0–24, exact live actor type/record/source pointer, link0/drop0, complete
20-entry source sequence, current12-slot phase/base, original animation/motion
fields, positive dynamic armor, INDEX8 surface, coordinates and original
parts0/1/19/20. Original clipping, filter, blitter and ordered calls still run.

## Bounded verification

See validation.json for finite receipts and exclusions. Tests cover all12 slots
and48 quadrants, all77 serialized record-byte mutations,2 warm record mutations,
current-bank reload/rebind/role/address reuse, live steering−4..4, scope and
surface/format guards, isolated four-state positive and22 loader negatives.
Optimized and ASan/UBSan runs use compiler1GiB/runtime512MiB limits, with
LeakSanitizer disabled. The shared snapshot regression covers625 checks across
13 families and40 record dependencies. Catalog-only validation checks1258
default resources and33 optional resources with an explicitly supplied historical
asset root; no historical path is part of the public runtime configuration.

Five actual-engine baseline/candidate pairs pass: native2x140ticks, native4x
110ticks, missing231, corrupt233 and flag-off eligible physical1. All14 original
gameplay/RNG/INDEX8 traces, detailed live pulse-actor traces and prior command
subsequences are byte-exact in every pair, with zero coverage mismatches or
rejected frames. Native2x accepts258 original pulse quadrants and four full-body
12-slot/48-quadrant loops; native4x accepts138 quadrants and two full loops.
Missing/corrupt dependencies accept no pulse quadrant while preserving5464 prior
HD calls. Flag-off accepts no HD calls. The three fallback/flagoff frames.tsv
files match baseline exactly. Slot1 ticks122–133 is the explicit complete live
12-step/48-quadrant witness, including original steering and repeated states.

Actual-engine pairs use explicit diagnostic seed1, original random spawning,
normal physical1 and stationary no-fire input. They are separate evidence from
source harnesses. Native screenshots are cropped SDL renderer readbacks without
resizing; internal density8 is not native2x. No BMP files, original resources or
runtime screenshots are included in the repository. This is not natural campaign,
full-level, Windows, fullscreen/GPU, performance or LeakSanitizer acceptance.
No GitHub publication or Windows package is part of this checkpoint. The final
strict production recompile is byte-identical to the tested candidate object and
has no warnings. Independent review found no blocking issue and rebuilt all
four PNG/HDA pairs byte-identically. Source and actual native2x four-state art
were parent-reviewed. New output plus Git stays below50MB, all new PNG copies
below10MiB, and free disk above5GB; final local-commit accounting is separate.

Rebuild: prototype/build-asteroid1-random286-art.py --data ORIGINAL --out OUTPUT

Tests: tests/test_asteroid1_random286_assets.py --data ORIGINAL --out OUTPUT
--sanitize. Add explicit --sdl-include paths if pkg-config is unavailable.
