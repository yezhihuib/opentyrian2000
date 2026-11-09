# Original-input HD ship scene check

The separately selected invulnerability candidate now has bounded actual-engine
software-renderer evidence, beyond its earlier synthetic callback test. It keeps
the detailed five-pose ship during native translucency, including the last tick,
without changing the original ship or weapon coordinates. No production source,
material, public-preset default or Windows package changes in this checkpoint.

## Original inputs stay private

The archive linked by the upstream README was obtained directly from
<https://www.camanis.net/tyrian/tyrian2000.zip>. Its entries were inspected without
running bundled programs. The archive, extracted data, diagnostic profiles and
actual-game screenshots remain outside Git and public artifacts. These hashes
identify the tested inputs, not permission to redistribute the original data:

- ZIP: 5,051,363 bytes, SHA-256 `348bc76e73514e452279b8730cf217daf0f70a282f07b6b94af653d87e921667`.
- `newshd.shp`: 42,012 bytes, SHA-256 `08c7c81b4ed590609f97347b1a4ec60aba56925ecc7193a6718c34cb8d698adf`.
- `tyrian.shp`: SHA-256 `80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0`.
- Player bank9: 33,484 bytes, SHA-256 `6e783ccf58eb55a4fad82cd1fb600968e1397f297d30398ac935c7f81dfd9cff`, matching the existing production source pin.

The checkers never download or install data. Both require an explicitly supplied
input directory and a fresh output directory outside the checkout. The scene
checker also refuses overlap with its original-data directory. The private
output is created with mode 0700. No bundled DOS program is executed.

## Authentic callback check

```sh
python3 tests/check_player_ship_original_data.py \
  --data /private/tyrian2000 --out /private/fresh-ship-bank-check
```

Original RLE decoding independently matches all five ordered callback records
and tile boundaries: 217/242/266/239/222 writes for poses 229/231/233/235/237.
The real source-bank guard, native blend blitter, callback validation and HD
half-alpha writer pass 2,372 writes across the 2-to-1 and 1-to-0 transitions.
Native INDEX8 output stays exact. All affected subpixels, native holes and
outside cells are checked, alongside 14 malformed callback cases, replay,
incomplete draw, live opt-out and pointer/size/content source corruption.

This check still models the backdrop, player state, SDL surface, scope/palette
admission and central compositor bridge. Its neutral normal comparison writes
native records directly. It is not itself gameplay evidence. ASan+UBSan passed
with leak detection explicitly disabled because LeakSanitizer is unsupported in
this execution environment; no leak-check pass is claimed.

## Real engine and display check

Build the current optional family binary with the documented dependencies, then:

```sh
python3 scripts/build_level2_family.py --jobs 4
python3 tests/check_player_ship_scene.py --data /private/tyrian2000 \
  --out /private/fresh-ship-scene-2x --scale 2 --ticks 540
python3 tests/check_player_ship_scene.py --data /private/tyrian2000 \
  --out /private/fresh-ship-scene-4x --scale 4 --ticks 240
```

The diagnostic verifies source, generated-header and object hashes against the
current 112-unit family build, then recompiles four instrumented units plus one
observer. The instrumented executable is private and never replaces the normal
game binary. The original scene loader starts Episode 1 script section 6 / physical
level 2, ASTEROID2, with seed 0x5eed and the native default ship/loadout. Menus are
bypassed. Sampled keyboard input goes through native movement, pose selection,
firing, collision and damage code. It holds fire, turns both directions, and
moves vertically. No actor, shot, pose, immunity counter or weapon origin is
injected. Probe/debug mode and the renderer's eligibility guards are unchanged.

Each pair differs only in `--player-invulnerable`. Both otherwise use the same
public candidate settings. Fresh isolated profiles avoid personal saves. SDL's
dummy video driver and software renderer produce actual 640×400 or 1280×800
readbacks immediately before Present. This is not a GPU or physical-window test.

Final reproducible results:

- 2×: two 540-tick executions, 7,020 equal comparisons of selected native fields,
  state hashes, RNG and full INDEX8 surfaces; 13 actual capture pairs.
- 4×: two 240-tick executions, 3,120 equal comparisons; 10 actual capture pairs.
- Each enabled run accepts 81 translucent frames spanning all five banking poses.
  Native count 1 at tick 98 becomes 0 at tick 99, whose ship is still translucent;
  tick 100 is accepted opaque rendering.
- At sampled ticks 20/40/90/99, changed pixels stay entirely within the native
  ship envelope. Captured weapon and background pixels outside that envelope
  remain exact. Every other scheduled capture matches byte-for-byte, including
  ticks 100/101 and all later captured normal frames.
- The 2× run records 326 accepted ship frames in total; the 4× run records 205.
  Unsupported/fade/blend cases still fall back. This is not a claim that every
  frame or all second-level content is HD.
- Original input file hashes are unchanged after the pairs. Numerical results
  and visual inspection of turning/firing samples agree within this scope.

The comparator requires the exact scheduled capture set. Missing readback,
missing visual differences, differences outside the ship, changed native hashes,
a false transition or absent opaque follow-on fails the check. Its own synthetic
negative tests cover these failure modes; those tests are separate from the
original-input executions. Two earlier development pairs are retained privately
and are not additional independent gameplay qualification.

## Boundaries and next checks

These observations exercise the real scene compositor and original firing path,
but do not exhaust every possible sprite overlap or weapon. Unchanged native
coordinates and selected shot-state hashes are not a complete all-weapon
alignment certification. The existing 121-transition central-writer model still
provides separate normal/blend/shadow retirement coverage; it is not substituted
for actual collision or overlap evidence.

Ordinary menu entry, physical controls, pause/resume, save/load, return to title,
full-level completion, other ships/loadouts, accelerated GPU/fullscreen,
performance and Windows remain unqualified. Keep the feature separately opt-in.
