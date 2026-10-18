# Secret-route collectible orbs 823/843

One analytic orange-gold globe replaces only collectible objects 823 and 843 from
original enemy bank 20 (`newshp.shp`). The complete 24×28 artwork has a dark rim,
upper-left bright core, fine curved internal light and layered lower-right arcs.
Bases 85/131/233 share exactly the same contour and curves; only their warm-ramp
luminance changes by 0/+2/+5. The original engine retains its eight-tick sequence
85,85,131,131,233,233,131,131. No clock, RNG, bitmap, halo or new dependency is
introduced. Three palette-keyed 8× RGBA caches occupy 504 KiB, plus 68 palette bytes.

## Narrow scope and source

Admission requires type 823/843, size 1, availability 2, score_item and no damage;
base 85/131/233; part 0/1/19/20; filter 0–255; and the current selected bank 20 pointer
and size. Other same-frame objects 577/591/593/688/690 remain on their old path.
The source must be exactly 46204 bytes with whole-sheet FNV64
`e2413e3aeab4d908`, rechecked before every call including warm art cache hits.
The verified original SHA256 is
`4bd9a72339e30440c172e385f258c8895b516ff84026a9a6b5a65ada4cf0ab90`.
No game art/data is redistributed. Both original records have armor 0, dani 0,
size 1 and nonzero score value, so these collectible-state gates match creation.

The existing original four ordered 12×14 calls and source offsets are unchanged.
Only the matching quadrant is composited; original INDEX8 writes execute exactly
once through unchanged blit_enemy and original normal/filter blitters. Existing
ownership, alpha, filters, restoration and later occlusion are reused. Tile
coordinates x 0–308, y −13–199 admit normal clipping; physical-row wrapping outside
those bounds stays classic. Density 8, valid/nonaliased INDEX8/ARGB8888 surfaces
and all ownership resources are required. Missing/invalid assets, reference mode,
Christmas data, unsupported contexts and bad resources fall back. No generic
bank 20/tile asset binding or gameplay, drop, collision or unlock change exists.

## Reproduce

```sh
make -j2 WITH_NETWORK=false LDLIBS=-lz
python3 tests/run_secret_exit_orb_tests.py
python3 tests/run_secret_exit_orb_tests.py \
  --data-dir /path/to/original/tyrian2000 --output /tmp/secret-orb-review
python3 tests/run_data_pickup_glyph_tests.py --data-dir /path/to/original/tyrian2000
python3 tests/run_fixed_pickup_flash_tests.py --data-dir /path/to/original/tyrian2000
```

SDL_CFLAGS/SDL_LIBS can select installed or restored headers/runtime. The source
SHA is verified before the optional private-data adapter run. Each process has a
512 MiB address-space limit, 32 MiB output-file limit and 60 CPU-second limit; the
runner requires 4 GiB free disk. The compiler alone was allowed a 1 GiB virtual
limit after the existing large HQ scaler unit exceeded 512 MiB; the interrupted
full rebuild resumed successfully without changing that source. The fixture
extracts the actual production scope,
admission, compositor, pixel ledger, normal/filter blitters and blit_enemy. Its
dispatch stops before unchanged generic paths and therefore is not a full-game
integration test.

## Verification and limits

- Plain and UBSan art tests pass: finite IDs, identical phase alpha/geometry,
  monotone luminance, bounded circle, deterministic cache and palette recoloring.
- Plain and UBSan actual-blitter/compositor fixtures pass 230 cases / 636487 checks
  each, with 135 original blits: all 3 bases × 4 parts × 2 objects, normal/filter,
  held-twice cycle, exact INDEX8 and full-canvas RGBA oracle, edge clipping,
  row-wrap fallback, excluded objects, warm source mutations, resource guards,
  original-support ownership, prior HD/cloud underlay, unchanged-index fallback,
  restoration and later normal occlusion.
- DATA regression passes 82 cases / 929272 checks per plain/UBSan suite; flash145
  passes 86 cases / 634234 checks per suite. Previous artwork and weapon paths are
  unchanged. The old unrelated rear source-projection fixture is excluded.
- Whole-sheet hash microcheck: 2000 calls at approximately 68 µs/call, 0.272 ms per
  four-part orb on this machine in the plain fixture; UBSan approximately 88 µs.
  This measures the source pin alone, not full game performance.
- Three-frame native 48×56 art and native 640×400 original/candidate studies were
  visually reviewed. The adapter also renders before/after through SDL's actual
  software nearest presenter at 640×400 over synthetic scenery.
- These are native-size composited previews, not natural hidden-route captures.
  Natural 823/843 attachment, carrier death, spawn, collection and bonus-level
  selection remain unverified. Palette fades, pending green-head overlaps and
  whole-game performance are not runtime-tested. Reviewed production ownership
  logic handles transparent original support; the fixture does not run finish.
- Full production rebuild and link passed with -Werror and suppressions for existing
  misleading-indentation/format-truncation/missing-field warnings.
  A first -Werror attempt without misleading-indentation suppression failed on
  existing compact code; that source was left unchanged.

This bounded local change does not establish whole-level coverage. No remote
push, upload or publication is part of this work.

### Bounded ordinary-game attempt

On 2026-10-18, private candidate `976ce2f4` and baseline `ebf909c` snapshots
attempted the natural 843 route using genuine SDL menu, shop and flight inputs.
Both stopped at player death at tick 751 / curLoc 752, before the route's
curLoc 4515 unlock. No orb attachment, birth, draw, source admission or collection
occurred. All three natural phases remain unverified; route 823 was not attempted.
All 752 paired observed original-state/RNG/INDEX8 rows and input/event streams
matched. Two direct indexed-surface byte witnesses and the initial native
640×400 frame were identical. Both builds exited normally. This is regression
evidence for the untriggered route only, not a successful orb runtime witness.
The finite unsuccessful attempt was retained and was not repeatedly retried.
