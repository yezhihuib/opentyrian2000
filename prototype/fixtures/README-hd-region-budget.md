# Finite HD region registry:65536 entries

The requested65536-entry presentation registry is a file-scope static array.
On the checked ABI each HdRegion is32 bytes:2,097,152 bytes total,2,088,960
bytes more than256 entries. The interim1024 array was32,768 bytes.
Only the macro/array declaration changes. The original >=sizeof guard, active
count, matching keys, restoration, composition and per-frame reset remain exact.

## Bounds from current source

Current ordinary frame control flow has a conservative1122 registration-call
bound even if no calls deduplicate. Its tighter present-behavior bound is822:

- Terrain:3 layers ×8 row calls ×12 tiles =288. backgrnd.c:161–260 has the
  i=-1..6 loops; render_mirror_terrain_row has tile=0..11. tyrian2.c:1296,
  1328–1342,1383–1403,1441,1892,2002 selects one pass per layer. Over-flags are
  not changed between these branches. JE_eventJump only updates event position.
- Enemies:100 slots (varz.h:115), four25-slot groups processed once each
  (tyrian2.c:1361–1362,1432,1449,1900,1910). At most four quadrant callbacks
  per enemy (tyrian2.c:238–249):400 raw calls. The current renderer normalizes
  part0/1/19/20 to exactly the same24×28 full origin, same bank/base/style.
  Calls are consecutive, NORMAL, and successful original pixel callbacks are
  suppressed; no restoration invalidates that record between quadrants.
  Therefore the present registry adds at most100 enemy records. The test also
  checks400 quadrant draws become100 regions. The1122 bound does not rely on it.
- Player projectiles:MAX_PWEAPON81 (shots.h:33); one indexed pass per slot
  (tyrian2.c:1454), at most NORMAL+SHADOW (shots.c:294–314):162. The special
  final slot does not need both; keeping it in the product is conservative.
- Enemy projectiles:ENEMY_SHOT_MAX60 (varz.h:46), one draw each
  (tyrian2.c:1793–1884):60. Only112/113 can actually acquire a region.
- Explosions:MAX_EXPLOSIONS200 (varz.h:50), one NORMAL or BLEND draw each
  (tyrian2.c:1962–1989):200. Repeating explosions and shot trails allocate
  this same pool; they do not create another rendering pass outside it.
- Player ships:two player movement calls maximum (mainint.c:4687–4700), at
  most six wrapper calls per ship (mainint.c:4162–4267):12. This deliberately
  includes non-HD/double-shadow possibilities. Ordinary supported Talon demand
  is smaller. Sidekick/indexed-only draws do not register additional HD assets.

Totals:288+400+162+60+200+12=1122 raw callbacks; with existing enemy quadrant
matching,288+100+162+60+200+12=822 records. These count clipped/transparent
calls too: registration precedes pixel clipping. Dead records remain counted,
so no capacity estimate subtracts records later restored to classic pixels.
The bounds describe current ordinary engine pools/control flow, not arbitrary
future injected diagnostic draw calls; the fail-closed guard still covers those.

## Integer, memory and performance audit

region_count and every region-loop index are unsigned int. They hold65536
without a16-bit wrap on the checked platform (the test symbol is4 bytes).
The array has static storage in BSS, not on a thread stack. No allocation size
is derived from the capacity, no frame routine copies/clears the whole table,
and every search/restoration loop ends at region_count. Reset sets the count
and other frame counters to zero; stale array records are ignored. Existing
one-record stack temporaries remain32 bytes. Green-head arrays and Uint16
head indices are independent, still limited to256, and are not enlarged.

Larger capacity therefore does not add65536-iteration work to ordinary frames.
Duplicate searches and some restoration paths retain their pre-existing
active-count/quadratic worst cases. This test intentionally seeds boundary
records in O(n) rather than performing65536 O(n) registrations.

## Portable sanitizer test

Run against a source tree that has the parent103 binding and either the exact
legacy declaration `static HdRegion regions[256];` or the exact production
65536-entry comment/macro/array block encoded in the script's CAPACITY constant.
For current production source, only that exact block is normalized in memory to
make the256-entry comparison; the candidate must have the exact expected65536
block. Other capacities (including1024) and altered production blocks are
rejected as source inputs. The1024 variant is constructed only for comparison.

The script creates only temporary extracted C harnesses and in-memory capacity
variants. It never edits that tree, starts the game, reads original game data or
records media:

```sh
python prototype/fixtures/test-hd-region-budget.py \
  --source /path/to/current-source \
  --report /path/to/region-budget-result.json
```

The report records the input source hash and capacity, the normalized256-entry
baseline hash, and the exact65536-entry candidate hash. For a current production
input, the input and candidate hashes must match.

ASan and UBSan test:
- Seed65,535 records;65,536th registration succeeds; duplicate at capacity
  deduplicates;65,537th distinct registration rejects with hd-region-capacity.
- Failure leaves region count, draw count, pixels and ownership unchanged;
  public entrypoints remain blocked until the next real render_mirror_begin.
- Reset clears counts, rejection, coverage and green/cloud ownership; disabled
  and fast-forward starts stay inactive; no out-of-bounds writes.
- All1122 conservative raw demands fit, and100 four-part enemies deduplicate.
- Actual green head/smoke replay plus physical alpha/shadow/indexed overwrite.
- Nonoverflow compositions at2x/4x/8x are byte-identical for256,1024 and65536.
- Negative controls:off-by-one guard, missing region reset, missing green reset,
  and reverting to the old capacity must fail. The guard mutation is caught by
  UBSan at region index65536.

Only the SDL allocation shell and external trace callback are test shims;
actual begin/reset, upscale, failure recorder, binder, draw, restore, green and
pixel functions are extracted unchanged. LeakSanitizer alone is disabled for
executor ptrace; address/undefined checks remain enabled.
