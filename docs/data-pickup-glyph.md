# Fixed DATA collection lettering

## Scope

The original fixed collection effect (`explosion_data[52]`, sprite 265 + 1)
gets a small code-native vector replacement. It retains the diagonal D/A/T/A
positions, thin dark rim and the current original gold/orange palette ramp.
The bounded 12×14, 8× RGBA cache is 43,008 bytes. There are no new art files,
external font dependencies, sprite-derived pixel matrices or bundled game data.

Admission requires fixed position, no player following, deltaY 0, sprite 265,
and TTL 1–14. The draw-call lease is consumed before early returns and cleared
at frame begin/entity end. The selected explosion sheet's decoded indices and
coverage must match FNV64 `d958f72b804b9ee8` on every draw, including warm calls.
Only TILE NORMAL/BLEND on the existing safe indexed game surface at density 8
is supported. Existing manual-HD scope is unchanged. Missing, invalid,
alternate-source and reference modes retain their fallback decisions.
There is no global sprite-266 binding.

The established ordered compositor handles alpha, hue/value blend, ownership,
restoration and occlusion. The original indexed blit still executes once.
Original coordinates, palette, TTL decrement, explosion pool and gameplay/RNG
code are unchanged. The original loop still draws a valid effect at the same
coordinates for TTL 14 through 1, with its existing offscreen cull.

## Reproduce

Build with SDL2 development headers/runtime available:

```sh
make -j2 WITH_NETWORK=false LDLIBS=-lz
python3 tests/run_data_pickup_glyph_tests.py
```

For actual source-pin, indexed blitter, compositor and native SDL fixtures,
point the test at a local original Tyrian 2000 data directory containing
`newsh6.shp` (17,810 bytes) and `palette.dat`. Choose a new output directory:

```sh
export TYRIAN_DATA=/path/to/original/tyrian2000
python3 tests/run_data_pickup_glyph_tests.py \
  --data-dir "$TYRIAN_DATA" --output /tmp/data-glyph-review
```

When SDL2 is available without pkg-config, set `SDL_CFLAGS` to the existing
include flags and `SDL_LIBS` to its existing library flags or runtime path.
The adapter needs SDL 2.0.12+ for the production nearest-neighbor scale mode.
The runner extracts current production functions rather than maintaining a
second compositor. The entity extraction stops after the DATA lease branch;
it does not claim coverage of the unrelated generic dispatch below it.

## Verified and bounded gaps

- Full production `make -j2` passed with `-Werror`; the Makefile's `src/*.c`
  wildcard includes the module. The production executable links both glyph
  functions and `render_mirror_data_value_begin`.
- Plain and UBSan vector tests passed: eligibility limits, deterministic
  cache, irrelevant-palette stability and relevant-palette recoloring.
- Plain and UBSan original-blitter/compositor suites each passed 82 cases and
  929,272 checks: NORMAL and BLEND for every TTL 14–1, exact INDEX8 and ordered
  RGBA reference, prior HD backgrounds, restoration/normal occlusion, clipping,
  surface/bank/layout/style/scope guards, lease consumption and same-address
  source mutations. The shared fixed-effect fixture also checks one indexed blit
  per wrapper call, cloud-ledger preservation and DATA/flash context separation.
  Actual wrapper fallback cases retain exact classic pixels.
- Native 640×400 before/after BMPs use the actual SDL software nearest presenter
  over explicitly synthetic scenery. They are not gameplay screenshots.
- The unmodified production executable started with original data and manual
  HD assets, stayed alive for five seconds, and exited normally when stopped.
  It used SDL's dummy/software backend, no scripted input and no DATA injection.
  A fresh isolated config used defaults. This only checks startup liveness.

Each test process is capped at 512 MiB address space, 32 MiB per output file
and 60 CPU seconds; the runner requires at least 4 GiB free disk. UBSan was
used within this limit; ASan's large virtual-address reservation was not used.

### Bounded natural gameplay verification

On 2026-10-18, candidate `c35fa7ee` was paired against baseline `e3a3944`,
without the later flash145 changes. Private diagnostic snapshots used seed
`0x5eed`, genuine SDL menus and flight inputs, and a real shop Pulse-Cannon
power-4 purchase. Gameplay, drops and admission were not injected or changed.
Episode 1 / Normal / physical level 9 naturally collected DATA513 at tick 729,
curLoc 730. All fourteen draws of 266 at fixed (232,72), TTL 14 through 1, admitted
the candidate BLEND/TILE path. All 747 observed original-state, RNG and INDEX8
hash rows matched; both indexed surfaces were directly byte-identical for all
fourteen collection ticks (28 buffer pairs). Native 640×400 frames at TTL 14/7/1
differed only inside the 24×28 DATA area. An earlier stock-power attempt died at
tick 767 without collecting; that result was retained.

This verifies one deterministic route, not the full game. Live palette fades,
performance benchmarks and pending green-head overlap remain unverified. The independent
RGBA oracle reuses the authored glyph pixels; geometry is supported by visual
review rather than a separate golden-art oracle. The known unrelated legacy
source-projection fixture was left unchanged and was not part of this suite.
