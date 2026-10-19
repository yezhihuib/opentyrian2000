# ASTEROID1 optional frequent four-piece grey asteroid

This fourth bounded artwork family extends the separate asteroid opt-in. The
previous17 image identities (14 static rocks and three record282 jewel states)
remain byte-identical. The global manual-HD manifest remains629 assets. This
batch does not complete the second stage or add a Windows package.

## Compatible opt-in

```
./opentyrian2000 --data=/path/to/original/tyrian2000 --no-xmas \
  --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1
```

The historical runtime directory now contains21 regular HDA files across four
independently validated families. An older pack remains compatible: any missing,
corrupt, wrong-role or unsupported-density member keeps this whole new rock
classic, while the previous families remain eligible. No implicit lookup or
mixed-density fallback is used. The option does not select or skip a level.

Existing normal-data Episode1 physical1 (ASTEROID1, campaign section5) scope
and incompatible-mode guards remain unchanged. Physical2, title demos,
Christmas data, multiplayer, linked/Galaga, arcade/action, SuperTyrian, timed,
bonus, network and recording modes remain excluded. Normal-data is not a
restriction to Normal difficulty; the finite acceptance probe uses Normal.

## Exact source relationship

Physical1 has31 original event12 spawns using base record138, from curLoc100
through5070. These are four static actor components, never rotation poses:

| Position | Record | enemy newshd base | Logical size |
|---|---|---|---|
| lower left | 138 | 39 | 24x28 |
| lower right | 139 | 41 | 24x28 |
| upper left | 140 | 1 | 24x28 |
| upper right | 141 | 3 | 24x28 |

The event handler positions them at(0,0),(24,0),(0,-28),(24,-28), assembling one
48x56 rock. Each record has ani1, animate0, size1, armor10 and bank8. Here bank8
is the loaded enemy bankD newshd.shp, never player spriteSheet8 or an ordinary
numeric sprite binding. Original quadrant offsets are0,1,19,20. Source events
use several pools and links; the new binding does not invent one fixed pool or
link identity. Original events, movement, collision, filters, armor, damage,
linked destruction and all indexed draw calls remain authoritative.

One built-in imagegen master reconstructs the source asymmetric silhouette,
major crater layout and neutral grey matte stone. The established four-rock
master is only a material/style reference. Broad values and crater rims were
reviewed at actual2x game size. The exporter aligns the whole artwork globally,
applies inward-only original support, then slices original24x28 rectangles.
No interior component seam is independently softened; reconstructing the four
RGBA pieces reproduces the packaged whole master exactly. No original game
art or data is included in the repository.

The private independent cache preflights all four exact density8, zero-anchor
files before any new-family replacement. Every draw checks actor type/base,
size, static pose, surface geometry, original clipping eligibility, complete
loaded bank bytes and all four serialized77-byte records. Private immutable
payloads are checked before the first accepted call of each display frame,
not rescanned for every quadrant. Failures are sticky for that cache lifetime;
a dependency failure after an accepted quadrant rejects the whole HD frame.

## Bounded validation

See validation.json for exact receipts. Optimized and ASan/UBSan extracted-
production tests cover one complete valid family and19 invalid fixtures, all
four record pins, bank identity/address reuse, spriteSheet8 exclusion, mode
scope, warm corruption, sticky failure and16 original quadrant calls. The
previous ten, four and gold-wing test suites were rerun in both modes.

Finite actual-engine pairs compare the current source to commit646adfad63ae03929361139baa4fec4417147e1c
using an external selection/export-only physical1 probe, original events,
fixed seed0x5eed and stationary no-fire input. Both native2x640x400 and
native4x1280x800 output are checked. All14 gameplay/state/RNG/indexed-pixel
traces and classic captures remain byte-identical, with zero coverage mismatch
or rejected HD frames. A missing39 pack admits all17 previous identities while
keeping every new component classic. A flag-off physical9 pair remains exact.
Native screenshots are visible-*.png; display-*.png is the internal density8
canvas, not the native-size screenshot.

These diagnostics do not establish natural campaign progression, a full level
clear, Windows/GPU/fullscreen compatibility or performance acceptance. A
preflight-only24-tick request was rejected by the existing60-tick minimum;
the final flag-off pair uses60 ticks. LeakSanitizer is unavailable in this
executor; AddressSanitizer and UndefinedBehaviorSanitizer remain enabled.
No GitHub push or Windows package is part of this batch. Only named inputs
were read; no private projection or session archive was accessed.

Rebuild: prototype/build-asteroid1-common4-art.py --data ORIGINAL --out OUTPUT.
Tests: tests/test_asteroid1_common4_assets.py --data ORIGINAL --out OUTPUT
--sanitize. Add --sdl-include directories when pkg-config is unavailable.
