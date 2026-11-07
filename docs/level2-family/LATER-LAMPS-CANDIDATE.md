# Optional later 16 lamp origins

This small batch reuses the **four existing, hash-verified lamp images** (newshs
229/231/233/235). It does not generate or replace art, change the 52-file asset
manifest, or enable any other late-level family. It ports the bounded later-lamp
logic already preserved in the public source-only `experimental/late-level`
package into the separately built `level2-family` candidate.

## Default and explicit option

The original seven admitted origins keep their existing switches and behavior.
The 16 appended origins remain **off by default**. To inspect an explicitly
selected plan without starting the game:

```sh
python3 scripts/launch_level2_family.py --data /path/to/game-data \
  --hd --later-lamps --check-only
```

`--later-lamps` requires `--hd`, adds only
`LAMP272_LATER_SIXTEEN_ENABLE=1`, and does not select the private red-vent pair.
Omitting it removes an inherited later16 request. Use the level2-family binary;
the ordinary canonical build and the source-only late-level package are unchanged.

## Exact scope

The target remains episode 1, **physical level 2 ASTEROID2**, main script section
6, map D/shapes Z, ordinary non-demo/non-probe play. This is a branch after TYRIAN,
not a universally mandatory second campaign stage. Unsupported modes retain
native fallback. The parent family and the lamp's existing source, palette,
actor lifetime, ordered native callback and geometry guards remain in force.

The additional zero-based event indexes are:

`267,268,481,482,483,484,486,487,488,489,572,573,586,587,604,605`.

Index **485 is not a lamp**; it creates record 269 and is deliberately excluded.
The range reaches event time 6208, but this is data coverage, not a claim of
having played through that point. Original eventLoc conversion remains 1-based
to zero-based. Compact origin ordinals 0–22, never raw event indexes, own the
consumed-once bits; failed allocation still consumes an origin. Renderer or
bank resets do not re-arm those bits. Only a real level load may do so.

The complete 731-event native stream must match FNV64 `0xa6df39659b2d348d` at
native level load, before events legitimately mutate their own fields. Each
selected event is also checked at its existing runtime admission points.
Changes of mode, scene, root or lifetime cannot expand an existing lease. No
actor, event, palette, RNG, movement, drop or combat field is written by this
extension.

## Evidence and limits

An offline audit of the matching original `tyrian1.lvl` confirmed all 23 origins,
including all 16 additions, field for field. These are exactly the 23 case-6,
record-272 rows in ASTEROID2. No original event table is published here.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_lamp272_later16.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_level2_family_release.py -v
```

Tests compile the actual selected predicates and origin table, cover flag/scope
combinations, exact append-only membership, bit bounds and explicit launcher
selection. A private isolated C check accepts the real full stream and rejects
an unrelated-row mutation, wrong count and a copied table at the wrong pointer.
These are **not real-scene validation**. Later positioning, occlusion, blend,
clipping, normal play, sound, save/load and performance remain unverified. This
candidate must not be described as an accepted whole-level visual release.
