# Private Charge Cannon renderer gate

This gate is prepared against production source `85cdb5dd31f97f8bf10dd564027cd26ff24c4891`.
It is a private runtime trial, not publication or visual acceptance. Art is frozen by
`candidate-manifest.json` SHA256 `e66f9b47a48233164b9f9537440d620f90b9c3de63998d1da4f09c5659df60be`.
No game data or art is included in this source patch.

## Finite binding

The only runtime-source change is six diff lines in `src/render_mirror.c`:
- Asset array capacity330 becomes333.
- Only bank8 / ENTITY_TILE / IDs252–254 select slots330–332.
- All use existing anchor0,0, logical12×14 and normal loader/header validation.
- Those shadow calls return to the original indexed path before asset lookup.

Bank9 launcher bodies, shop/HUD, gameplay, charging, damage, velocity, collision,
RNG, existing assets and renderer filters are unchanged. Shot record103 is not
bank8 sprite103. Separate explosion-bank252–254 shield entries retain their own
cache slots. Loaded but unreferenced records793/1793 can reuse these globally
bound indices; their animation and acquisition remain outside this runtime gate.

## Final log-only matrix

26 real-game runs ×90 ticks =2,340 renderer frames. All passed. No captures were
created. The accepted pack is referenced by individual symlinks, with only three
frozen candidate HDAs added. Per-file invalid tests contain new private files with
anchor1 rather than modifying source art. Every verbose blend log is consumed
through the existing FIFO proof helper; full indexed/per-tick hashes are retained.

- E1 physical9, E4 physical3, E5 physical1: unchanged/candidate at native Integer2×,
  actual HD8 heads on both mounts, complete emission/draw attribution and exact
  indexed state/RNG/collision/particle parity.
- E1 native Integer4× unchanged/candidate: actual1280×800 SDL renderer output,
  identical logical compositor RGB to native2×. Native2× is640×400.
- Deterministic repeat: complete TSVs and streamed blend proofs match exactly.
- Whole-family missing: complete output equals unchanged baseline.
- Each missing identity and each invalid-anchor identity: only that head falls
  back; all its live frames are full-frame RGBA-exact to baseline, and the other
  two heads still use HD. No accidental neighboring identity or cache alias.
- Classic, global missing, global invalid, and absent4-density-file fallback:
  complete baseline/candidate observations match exactly. Render density4 is a
  fallback test; it is distinct from native Integer4× with density8 art.

E1 and E5 each draw28/34/42 normal heads for252/253/254, plus104 original indexed
shadows. E4 level3 draws28/32/20 normal heads plus80 indexed shadows and has four
matched natural hits at ticks39/67/70/82. This is deterministic collision/effect
state parity, not a visual hit-effect acceptance claim.

E4 physical9 has a pre-existing whole-frame `smoothie-surface-routing` /
`water_filter` fallback. Both binaries remain exactly equivalent, with zero HD
heads on that route. Its nonzero coverage diagnostics are retained and qualified;
they are not treated as successful HD coverage. The supported original physical3
route supplies the actual E4 table/HD-head proof. No filters were bypassed.

The unchanged renderer's scene-draw observer is inactive in some fallback modes,
so cross-mode comparisons use gameplay/shot logs plus exact indexed state, original
blend-column hashes and effect semantic fields. Same-mode baseline/candidate full
fallback comparisons remain byte-exact. Renderer HD-ownership counters may differ
when new artwork draws; restored/indexed RGB mismatches stay zero on accepted HD
routes. These logical proofs do not evaluate visible aliasing, wisps, edge softness
or readability. Native2×/4× visual review is still required separately.

## Reproduce

Build an isolated source-only unchanged85cdb5d baseline, then the candidate, using
the normal Makefile and available SDL2/SDL2_net environment. Do not copy the art
pack into either source tree. From the candidate source directory:

```sh
python prototype/test-charge-render.py \
  --exe /path/to/candidate/opentyrian2000 \
  --baseline-exe /path/to/unchanged85cdb5d/opentyrian2000 \
  --data /path/to/legal/tyrian2000 \
  --assets /path/to/accepted/runtime/pack \
  --candidate-pack /path/to/current/runtime/pack \
  --manifest /path/to/charge-cannon-family-v1/candidate-manifest.json \
  --out /new/output/directory
```

The base `--assets` argument may reference the current public pack: the runner
filters out the three Charge filenames before constructing baseline symlinks.
`--candidate-pack` supplies those three files and verifies their frozen hashes;
omit it only when the manifest-relative runtime/ files are present. No private
pack directory or prebuilt executable is required: build the two source revisions.

The explicit `--resume` option only reuses completed cases whose command, zero-exit
receipt, executable hash and pack symlinks match. It rechecks all retained proof.
Each run stores `command.json`; `summary.json` retains full per-log hashes. The
compact receipt is `CHARGE_CANNON_RENDERER_GATE.json`.

Actual binder boundary/cache tests include the production C implementation:

```sh
cc -std=c99 -O0 -ffunction-sections -fdata-sections -DTARGET_UNIX -DWITH_NETWORK \
  -Isrc $(pkg-config sdl2 SDL2_net --cflags) prototype/test-charge-binding.c \
  -Wl,--gc-sections -o /tmp/charge-binding-test
/tmp/charge-binding-test /path/to/output/packs/full
```

This verifies capacity333, slots330–332, wrong bank/layout, neighboring/out-of-range
IDs, reverse-order cache loads, separate explosion IDs and existing guided slot329.
It also passed AddressSanitizer/UndefinedBehaviorSanitizer; LeakSanitizer was
unavailable under the execution runtime's ptrace and was disabled for that pass.
Strict C syntax, Python compilation and diff checks passed. No main checkout was
edited or push performed by this task.
