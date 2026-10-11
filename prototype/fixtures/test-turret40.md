# Type40 finite turret binding oracle

Test-only coverage for the combined private renderer containing newsh2 bases
153, 155 and 157 in slots 269–271 and the separately reviewed gray Layer3 family
in slots 272–289. Asset capacity must be 290. Production source is only read.

Run from an isolated working directory with Python 3, Pillow and a C99 compiler:

```sh
python /path/to/prototype/fixtures/test-turret40.py \
  --source /path/to/private-fixture/src/render_mirror.c \
  --assets /path/to/private-review-pack \
  --runtime-zip /path/to/opentyrian-turret40-hd-v1-runtime.zip \
  --clean-source /path/to/clean-d351/src/render_mirror.c \
  --sanitize --output /path/to/new-external-results
```

The source argument must point to the combined private candidate; adjacent
`tyrian2.c` and `sprite.c` provide the original wrapper and indexed RLE blitters.
The optional clean-source check verifies that generic rendering helpers and the
original wrapper/blitters are unchanged and that the turret binder delta is
exactly the three explicit base-to-slot entries. The frozen runtime ZIP hash is
pinned. Omitting runtime-zip skips PNG transport verification but still tests the
supplied HDA bytes, opacity, unique designs and common body outside the 6×6 core.
The test creates all synthetic packs and compiled binaries in a temporary
directory, writes reports only to the output directory and never runs the game.

Coverage:
- Exact bank1 pointer identity and newsh2 role101, all three bases, slots,
  dimensions, anchors and four original part offsets 0/1/19/20.
- All 24 quadrant orders, all 256 filters at 8×, representative filters at 4×
  and 8× from 4× fallback, independent RGB/alpha oracle and canvas pitch guards.
- Original source-selected nine-step sequence
  153,155,157,157,155,155,155,153,153. The wrapper is checked at every one-based
  enemycycle index with all parts, filters and success/fallback outcomes.
- Every nonempty quadrant subset, overlap/repeated calls and clipping. Missing
  quadrants remain untouched rather than being synthesized or prefilled.
- Unknown bases, invalid parts including signed extremes, null/wrong surface,
  null/wrong/same-byte-different-pointer bank, wrong bank IDs and relocated bank
  registration. Flags, density1, absent path and unavailable art fall back.
- Missing-all, missing-each, only-one-present, all header words, magic, short,
  empty, truncated or trailing payloads, wrong role/prefix and independent 4×
  fallback. A missing design never poisons available siblings.
- All 50 accepted enemy bindings coexist without changing their cache slots.
  Turret153 and Layer3 terrain153 are loaded simultaneously with distinct role,
  anchor and RGBA caches and checked in both draw orders at the same position.
- Original indexed bytes, original blit exactly once, reset exactly once,
  clipping and no enemy-structure mutation, on both HD success and fallback.
- Pixel/ownership checks establish that mirror rendering never writes the
  original indexed surface. Original-wrapper checks use generated RLE bytes.

This is an extracted-function unit oracle. It does not establish live firing
trigger timing, shot lifecycle, collision, damage, destruction or runtime visual
acceptance. No original game pixels, generated art, gameplay edits or captures
are included. ASan and UBSan are enabled together; LeakSanitizer is disabled for
the instrumented execution environment and is not claimed as passing.
