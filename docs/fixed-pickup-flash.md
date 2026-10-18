# Fixed pickup flash145

A small analytic orange/red ember replaces only the original fixed type-0
collection flash. It keeps the 12×14 tile, center near (6, 7.5), warm 0x70
palette ramp and seven unchanged draws. Its soft irregular contour and narrow
orange core are distinct from accepted moving146–152. One palette-keyed 8× RGBA
cache uses 43,008 bytes; there is no new bitmap, animation, clock or RNG.

Admission requires fixed position, no following, deltaY 0, sprite 144 and TTL1–7.
The consumed-once draw context clears before early returns and at frame/entity
boundaries. The selected explosion sheet must match decoded indices+coverage
FNV64 `7560c3259e9e9462` on every draw, including warm calls. Only TILE
NORMAL/BLEND on the existing safe INDEX8 game surface and density8 ARGB canvas
is admitted (2560×1600 canvas at density8 only). Missing/invalid resources, alternate banks, reference mode and
unsupported contexts retain their existing fallback. There is no global145
asset binding; moving146–152 and fixed DATA266 remain separate.

The existing ordered compositor provides hue/value blending, alpha, ownership,
restoration and occlusion. The original indexed blitter executes exactly once.
Coordinates, explosion pool, culling, palette, TTL decrement, gameplay and RNG
are unchanged. Original type0 pickup callers533/534/535/800/801 are unchanged.

## Reproduce

With SDL2 development headers/runtime available:

```sh
make -j2 WITH_NETWORK=false LDLIBS=-lz
python3 tests/run_fixed_pickup_flash_tests.py
python3 tests/run_fixed_pickup_flash_tests.py \
  --data-dir /path/to/original/tyrian2000 --output /tmp/fixed-flash-review
python3 tests/run_data_pickup_glyph_tests.py \
  --data-dir /path/to/original/tyrian2000 --output /tmp/data-regression
```

`SDL_CFLAGS` / `SDL_LIBS` can select existing SDL headers/runtime when
pkg-config is unavailable. Original data is read locally and never bundled.
The flash runner reuses the small DATA fixture with explicit effect constants;
actual production admission, compositor, original blitters and wrapper are
extracted unchanged. Generic entity dispatch after the fixed branches is not
part of the extracted fixture. Each process is capped at 512MiB address space,
32MiB per output file and 60 CPU seconds; the runner requires 4GiB free disk.

## Evidence and gaps

- Full production build with `-Werror` and disabled-mirror `tyrian2.c` syntax
  check passed. The new functions are linked into the production executable.
- Plain and UBSan unit tests: all context/TTL boundaries, bounded warm geometry,
  deterministic cache and palette recoloring.
- Plain and UBSan original-blitter/compositor fixtures: every TTL 7–1 in both
  styles (86 cases / 634,234 checks per suite), exact INDEX8 plus ordered RGBA
  reference, one indexed blit per wrapper call, prior HD/cloud ownership,
  restoration/occlusion, clipping, resource and
  layout guards, source mutations and consumed leases.
- DATA unit and actual-blitter/compositor regressions rerun with its original
  fourteen TTLs (82 cases / 929,272 checks per suite). The shared fixture also
  checks146–152 mappings are unchanged.
- Native 640×400 before/after BMPs come from the actual SDL software nearest
  presenter over synthetic scenery. These are not natural gameplay captures.
- Production startup with original data and manual HD assets stayed alive for
  five seconds, then exited normally after tester SIGTERM. No input or effect
  injection was used. This only checks startup liveness.

### Bounded natural gameplay verification

On 2026-10-18, candidate `e68737e8` was paired against baseline `c35fa7ee`
through genuine SDL menus, a real shop power upgrade and ordinary flight/fire
inputs in Episode 1 / Normal / physical level 9. The link 1 carrier died to shots
at tick 212 and naturally spawned 534. Its pickup at tick 221 produced the fixed
sprite 144 effect at (138,104), TTL 7 through 1 on ticks221–227. All seven draws
admitted the candidate 145 path. Both runs exited normally after 232 ticks;
all 232 observed original-state/RNG/INDEX8 rows and input/event streams matched.
Both indexed surfaces were byte-identical across all seven collection ticks
(14 buffer pairs). Pre-pickup native 640×400 frames were identical. Each of the
seven effect frames differed by 104 pixels solely within half-open native bounds
[234,218,246,228]. A simultaneous large explosion partly obscures the ember,
so this establishes visible contribution, not an unobscured contour witness.
The first attempt collided with the carrier and missed its drop; it is retained.

Only this bounded route is verified, not full-game parity. Live palette fades,
pending green-head overlap and performance remain unverified. The RGBA oracle reuses authored ember pixels; geometry requires
visual review. The intentionally old unrelated rear source-projection fixture is
unchanged and excluded. No remote push, upload or publication is part of this work.
