# Private Layer3 gray binder review

## Result

The two-file private candidate passes the independent binder/integration and
pixel/ownership oracles plus all ten requested prior regression suites. No
remaining functional blocker was found in the scoped binder. The initial
missing `render_mirror_bind_terrain(3, ...)` loader call was reported and fixed
by the candidate owner before the final tests.

Reviewed immutable base: `d351fe256e82216baa5281be552399ea1a276cca`.

Final source SHA-256:

- `src/render_mirror.c`: `537224e51daca151b1f66e59d113aba65b5c5cce18281cb996589d49b245ce6b`
- `src/tyrian2.c`: `d5c23bd88b27a8a1ef7572880e5f3f184424684d1ef22d9fadda114e61ce493a`

Every other `src/` file is byte-identical to the immutable base. The renderer
diff is limited to the finite family, capacities, layer guard, row selection
and missing-art skip. The only `tyrian2.c` change is the single layer3 loader
hook. Generic blend, shadow, filter and indexed-write code is unchanged.

## New independent tests

- `test-layer3-gray-binder.py/.c`: **301,188,958 assertions**, ASan/UBSan.
  Exact 18 IDs and slots 272–289; exhaustive bank/layer/ID guards; pointer
  identity even with byte-identical data or shared IDs on other layers;
  slots 269–271 untouched; all 38 malformed-header/payload cases; malformed
  member isolation; missing-all/each, null, disabled and 4x fallback; map reset;
  77 simultaneous terrain assets; 252 ordered full/partial 12-tile rows.
- `test-layer3-gray-alpha.py/.c`: **287,886,969 assertions**, ASan/UBSan.
  Executes the actual row, RGBA compositor, original NORMAL indexed blitter
  and per-pixel callback. All 18 gray IDs at 2x/4x/8x; binary/fractional alpha;
  clipped rows; exact RGBA, ownership metadata and indexed writes;
  missing/invalid/null classic fallback. Non-NORMAL styles cannot draw or
  restore the scene.
- `test-layer3-gray-mutations.py`: **9/9 deliberate faults rejected**.
  Wrong layer, bank, slot and whitelist; omitted shadow guard; missing-art
  trace; removed map reset; off-by-one capacity guard; removed real-loader
  hookup. Only temporary extracted snippets are mutated.

The new binder oracle executes the original `tyrian2.c` loading loop and
checks the audited map lookup directly against hash-verified `tyrian1.lvl`
bytes. Shape-blank metadata is read from hash-verified `shapesz.dat`. Source
art pixels are neither generated nor changed by this test.

## Registry scope

The reviewed level9 map requires **78 source pointers**: 45 layer1 pointers
(44 distinct IDs, because ID351 occupies two different source slots),
15 layer2 cloud pointers, and 18 layer3 gray pointers. This fits capacity140.

The original loop bounds can theoretically register 213 eligible aliased
slots on a different map. A synthetic original-loader test exercises that
case: the first140 records are preserved, and every later unregistered
pointer follows classic fallback. Capacity140 is therefore verified for the
reviewed map and for safe overflow, not claimed to cover every possible map.

The source topology oracle also checks the original NORMAL layer3 row path,
15-column stride, and existing `background3over` call positions.

## Prior regressions

All passed with ASan/UBSan:

- Ground binder: 6,107 checks
- Terrain holes binder: 10,777,700 assertions
- Terrain next-seven binder: 449,259,220 assertions
- Terrain holes alpha: 16,920,800 assertions
- Terrain next-seven alpha: 94,059,984 assertions
- Enemy orb: 46,024,704 pixel comparisons; 108 wrappers, 18 clipped helpers,
  783 scope guards; disabled-build check passes
- Rotor enemy: 101,573,120 pixel comparisons; 1,016 successful quadrant calls,
  105 rejected-source/part guards
- Green background: 346,480 checks
- Cloud shadow and green head, each: 1,935,360 pixel comparisons,
  28,290 overlapping-head checks, 38,120 later-start-index checks,
  31,749 transparent-preservation checks

The three legacy binder harnesses received test-only helper extraction,
capacity and independent literal layer3-whitelist updates. Their previous
asset/pixel checks remain. The rotor harness emits four pre-existing unused
helper/variable warnings; other reviewed runs have no compiler warnings.
LeakSanitizer is disabled under ptrace; address and undefined-behavior checks
are enabled.

## Run

From the private snapshot, source the existing official SDK environment:

```sh
. ../opentyrian-cloud-runtime/env.sh
python prototype/fixtures/test-layer3-gray-binder.py --sanitize \
  --report prototype/fixtures/layer3-gray-results/binder.json
python prototype/fixtures/test-layer3-gray-alpha.py \
  --report prototype/fixtures/layer3-gray-results/alpha.json
python prototype/fixtures/test-layer3-gray-mutations.py \
  --binder-report prototype/fixtures/layer3-gray-results/binder.json \
  --report prototype/fixtures/layer3-gray-results/mutations.json
```

Use `--source`, `--topology`, and `--data` on the binder test when directories
are arranged differently. Temporary synthetic test inputs are retained.

Detailed JSON reports and regression logs are in `layer3-gray-results/`.
This is a private source/test review, not a gameplay, authored-art or visual
acceptance result. No game run, capture, authored-art modification, deletion
of project files, or main-checkout edit was performed.
