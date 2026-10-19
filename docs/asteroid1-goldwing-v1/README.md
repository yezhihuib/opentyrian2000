# ASTEROID1 optional record282 gold-wing actor

This third bounded family extends the existing separate asteroid opt-in. It is
one gold mechanical flying actor with three jewel-color states, not a rotating
rock and not completion of the second stage. The previous14 static rock assets
remain byte-identical. The global manual-HD manifest remains629 assets.

Use the existing historical directory and option:

```
./opentyrian2000 --data=/path/to/original/tyrian2000 --no-xmas \
  --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1
```

This option does not select a level. All existing physical1, normal-data campaign
and incompatible-mode guards remain unchanged. Normal-data does not restrict
difficulty: original difficulty-scaled armor and shot timing remain dynamic.
The finite actual-engine proof below uses Normal difficulty.

## Source identity and timing

Original record282 is size1, bank8, ani6, animate2, turret59/frequency50, armor3,
y-speed2. Bank8 here means enemy bankD newshd.shp, never player spriteSheet8.
Its six source positions are79,81,83,81,81,79. All three images have identical
458-pixel alpha support and identical exterior RGB. Precisely12 pixels in the
lower center jewel change dark blue to blue to cyan. There is no geometric
rotation or wobble. Animate2 initializes/rests on position1 or6 and pulses only
when the original gun or launch code activates it. Engine-selected positions,
repetitions, idle periods and all shot state remain authoritative.

Physical1 has four direct Sky Enemy event15 spawns at curLoc30,500,1000,1400,
x30,230,30,230, all link40 in sky slots0–24. Each following event33 sets the
original death drop535. Arcade-only event45 alternatives603/611/612/616 remain
excluded by the existing mode guards. Records531 and689 reuse these graphics;
they are explicitly outside this family. Physical2 also uses record282, but its
level, pool and link identity remain excluded.

The original weapon59 projectile moves at the same vertical speed as the actor
and can occlude the jewel after firing. Native acceptance preserves this red
projectile overlay. It must not be removed to make authored pulse colors visible.

## Artwork and binding

One built-in imagegen master provides the smooth2D satin-brass shell, pale-gold
structural ribs and recessed blue lens. A second imagegen pass removes the first
pass's blocky pixel grid. The builder aligns the whole master once, applies
inward-only original alpha support, and derives three source-bound jewel RGB
variants. Every exterior RGBA byte and all alpha bytes are identical across
poses. Inward contour coverage leaves456 of458 original logical blocks with
nonzero HD alpha; the remaining tiny tip blocks retain classic rendering. Only the source12-pixel jewel region can differ. No original art or game
data is copied into the repository.

The three regular density8 HDA files preflight as one dependency independently
of the previous10 and4 families. A ten-only or fourteen-only pack remains
compatible. Missing/corrupt/wrong-role/unsupported-density resources keep the
whole new actor classic. There is no implicit lookup or density4 fallback.
Warm payload corruption is sticky until cache reset; source or dependency
failure after an accepted quadrant rejects the whole HD frame.

Binding verifies the current loaded full bank bytes and full serialized77-byte
record282. Each original quadrant additionally validates live pool slot, exact
record pointer/type, link40, drop535, complete20-entry source sequence, original
fire-animation phase/base, gun and movement fields, source pointer, coordinate
origin, INDEX8 surface and original part0/1/19/20. Armor and shot timers are not
rewritten. Every original indexed blitter, clipping gate, filter and ordered
quadrant still executes.

## Bounded validation

See validation.json. Source-harness tests and finite actual-engine captures are
separate evidence. The latter use an external selection/export-only physical1
probe, original events, fixed seed0x5eed, stationary no-fire input, native2x
software-rendered output. A pre-final4x diagnostic is retained separately and
does not replace final-source acceptance. They do not prove natural campaign progression, a
level clear, Windows/GPU/fullscreen operation or performance acceptance.
Native screenshots are visible-*.png; display-*.png is the internal density8
surface and must not be described as native2x output. No GitHub push or Windows
package is part of this batch. Only explicitly named inputs are read.

Rebuild: prototype/build-asteroid1-goldwing-art.py --data ORIGINAL --out OUTPUT.
Tests: tests/test_asteroid1_goldwing_assets.py --data ORIGINAL --out OUTPUT
--sanitize. Add --sdl-include directories when pkg-config is unavailable.
