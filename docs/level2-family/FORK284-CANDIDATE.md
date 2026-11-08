# Optional Fork284 sparse candidate

This experimental build can reuse the existing public
`assets/hd/packs/asteroid1-ten-v1/enemy-newshd-121-8.hda` for four exact
record-284 origins (one-based eventLoc 12–15). It is **off by default**:

```sh
python3 scripts/launch_level2_family.py --data /your/game-data --check-only --hd --fork284
```

`--check-only` never starts a game. Actual execution additionally needs
`--launch`; this candidate has not been scene-qualified. The launcher requires
`--hd`, removes inherited `FORK284_*` settings, verifies the additional public
asset's exact byte count and SHA-256, and sets only `FORK284_ENABLE=1` and its
fixed repository asset directory. The original 52-file/24-terrain manifest and
all other optional switches remain unchanged. The extra asset is not counted
among those 52 files.

## Rendering and provenance limits

The native renderer still performs its original indexed writes. The optional
sidecar requires ordinary episode 1, physical level 2, mainLevel 6 ASTEROID2,
original D/Z map and initial offsets, and a complete 731-event stream hash at
level load. It then witnesses the original case-7/pool-50 allocation, constructor,
event commit, source bank, record, palette, normal actor state and four-part
native callback order. Unsupported/clipped states stay native; incomplete or
changed contributing contracts reject the shared HD frame. No event, RNG,
collision, native sprite, palette or gameplay state is rewritten.

Unlike the opaque families, only the 270 actual native-written cells receive
HD ownership. Within each cell the art's alpha blends over the **current** HD
underlay. Alpha-zero subpixels retain that underlay, and native holes are never
filled or restored from a rectangular crop. A normal/blended later writer
retires ownership before any other family's early-return path. Valid native
shadows darken retained HD pixels; malformed order or effects fail closed.

Allocation generations, bank-change/retirement hooks and frame reset prevent
slot reuse from inheriting a prior draw. Per-write checks validate cheap live
configuration/identity only; full asset/bank hashes and actor contracts are
checked at tile and final-output boundaries, avoiding whole-bank hashes for
every pixel. Support snapshots are diagnostic only and cannot grant a display
lease.

## Verification and remaining work

`tests/test_fork284_family.py` exercises default-off launch planning, inherited
control removal, asset corruption, exact event admission and one-time
consumption, sparse alpha compositing, native holes, normal/blend retirement,
shadow receipts, partial/order failure, and hook placement. Its C harnesses
execute extracted production functions with explicit stubs; they are **not** a
running-game test. The separate [offline preflight](FORK284-PREFLIGHT.md) remains
read-only.

Actual scene appearance, draw-order interactions across whole gameplay,
performance, sound and save/load are still unverified. No new terrain coverage
is claimed. Keep this option separate until visible scene validation succeeds.
