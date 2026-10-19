# ASTEROID1 optional four-piece event12 rock

This is a second bounded artwork family, not second-stage completion. Original
events, actor positions, animation, collision, damage, links and destruction
remain authoritative. No original game data is shipped here.

## Compatible opt-in

Use the existing separate asteroid mode and historical runtime directory:

```
./opentyrian2000 --data=/path/to/original/tyrian2000 --no-xmas \
  --asteroid-hd-assets=/path/to/repo/assets/hd/packs/asteroid1-ten-v1
```

The directory contains the original unchanged ten files plus four optional
regular HDA files. There are no symlinks or duplicated ten-piece payloads.
The ten and four families preflight independently. An old ten-only pack still
draws the accepted ten-piece rock and leaves these four-piece rocks classic.
Any absent/corrupt four-member dependency keeps the entire four-piece rock
classic. There is no density4 fallback or implicit lookup outside the chosen
directory. The default/manual-HD registry and its 629 assets are unchanged.

The existing Episode1 Normal physical1 PIC3 scope and incompatible-mode guards
are unchanged. This option does not select or skip a level. Other physical
levels, title demos, Christmas data, multiplayer, linked/Galaga, arcade/action,
SuperTyrian, timed, bonus, network and recording modes remain excluded.

## Original family and authoring

Physical1 ASTEROID1 event19 at curLoc80 is the first of 33 original event12
spawns using base record440. The original event12 handler creates four actors:

| Position | Record | newshd base | Logical size |
|---|---|---|---|
| lower left | 440 | 45 | 24x28 |
| lower right | 441 | 47 | 24x28 |
| upper left | 442 | 7 | 24x28 |
| upper right | 443 | 9 | 24x28 |

Their exact offsets assemble a 48x56 rock. All four records have ani1,
animate0, size1, armor16 and bank8; there are no alternate or damage poses.
These are components, not rotation frames. Bank8 resolves to enemy bankD
newshd.shp, distinct from player spriteSheet8 and overlapping sprite numbers.

The imagegen reconstruction matches the accepted ten-piece neutral grey,
cratered matte stone. Broad shapes are prioritized at actual2x game size. One
continuous master is globally aligned and inward-smoothed within original
logical support, then split into the original actor rectangles. Every authored
nonzero subpixel stays inside original alpha support. No interior split edge
is independently softened. Original indexed blitters always execute.

The dedicated four-family binding checks current loaded enemy-bank identity,
the full original bank bytes and all four serialized77-byte records on every
draw. Each draw also checks actor type/size/base, static pose, source surface,
geometry and mode. Four pinned density8/zero-anchor resources preflight as one
dependency. Their private warm payloads are verified before each display frame;
a dependency failure after a successful draw rejects the whole HD frame.

## Validation

See validation.json for exact final receipts. Tests use only explicit source,
art and named external data inputs. They do not read the private projection.
The source harness is separate from actual-engine acceptance. Finite native
captures are controlled fixed-seed original-event diagnostics, not natural
campaign progression, a full level clear, Windows/GPU/fullscreen or performance
acceptance. The existing ten artwork/source bytes and prior first-level state
are preserved. No GitHub push or Windows package is part of this batch.

Rebuild with prototype/build-asteroid1-four-art.py --data ORIGINAL --out OUT.
Run tests/test_asteroid1_four_assets.py --data ORIGINAL --out OUT --sanitize;
supply SDL include directories if pkg-config is unavailable.
