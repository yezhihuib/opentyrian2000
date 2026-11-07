# Optional later five ember origins

This source-only extension reuses the four public ember images (newshd
267/269/271/273) and the six exact origins preserved in
`experimental/late-level/sources/03c5968bda89ae17/ember269_family_mirror.inc`.
It adds no art, changes no 52-file manifest entries, and enables no other
late-level family. It is a candidate, not an accepted whole-level visual release.

## Default and explicit option

The original event 157 keeps its existing `EMBER269_FAMILY_CANVAS_ENABLE`
switch. The five additional origins are **off by default**:

```sh
python3 scripts/launch_level2_family.py --data /path/to/game-data \
  --hd --later-embers --check-only
```

`--later-embers` requires `--hd` and adds only `EMBER269_LATER_FIVE_ENABLE=1`.
Without this option the launcher strips inherited requests. Later lamps and the
private red-vent pair remain separately selected options. Only the separately
built level2-family candidate changes, not the canonical build or late-level
archive. Existing four images, palette and source hashes remain unchanged.

## Scope and lifetime

The target is episode 1, physical level 2 ASTEROID2, main script section 6,
map D/shapes Z, ordinary non-demo/non-probe play. This is a branch after TYRIAN,
not the mandatory second stage of every campaign route.

| Zero-based event index | Time | X | Group |
| --- | --- | --- | --- |
| 157 | 1252 | 114 | Original |
| 349 | 3128 | 114 | Later |
| 351 | 3128 | 186 | Later |
| 479 | 4668 | 42 | Later |
| 480 | 4668 | 66 | Later |
| 485 | 4668 | 258 | Later |

Every row is case 6, record 269, with remaining event fields zero. The complete
731-event stream must match FNV64 `0xa6df39659b2d348d` at the actual native level
load, before native events mutate themselves. Runtime admission checks the
selected row again. A six-byte consumed array is indexed by bounded origin
ordinals, never raw event indexes. Allocation failure consumes the origin;
renderer/bank reset cannot re-arm it. Only a real level load clears consumption.
Modes 2 (original), 4 (later), and 6 (both) are pinned at load. A changed mode,
root, scene or epoch cannot expand an existing lease. Existing exact actor,
source, palette, ordered writer and geometry guards remain. No gameplay fields
are written.

## Verification and limits

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_ember269_later5.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_level2_family_release.py -v
```

The isolated C harness compiles the actual origin table, mode, selected-row and
scope predicates, plus actual event-begin admission with scope/log/fault stubs.
It checks consumed-once behavior after failed allocation and disabled origins,
and exercises independent flags, scope exclusions, ordinal
bounds, bad rows/streams and launcher defaults. `harness()` also emits a program
accepting an optional raw 731 × 11-byte event file as its first argument, to test
the real full stream, all six rows, unrelated-row corruption, wrong count and
wrong-pointer rejection without publishing original data. This optional check
passed against the privately held real stream; no original event table is
included in this source batch.

No game was run for this extension. Later positioning, clipping, occlusion,
blend behavior, normal play, sound, save/load and performance remain unverified.
