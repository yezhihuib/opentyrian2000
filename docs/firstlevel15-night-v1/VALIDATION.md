# Hard first level night validation inventory

Evidence snapshot: 2026-10-14. This inventory summarizes completed reviews of
the frozen normal-data night candidate and the final combined-source offline
rerun. Runtime evidence belongs to the frozen night-only candidate; no combined
game run or publication is claimed.

## Completed source and unit review

- Exact inverse review checked 148 production files. Changes are limited to
  `src/render_mirror.c`, `src/render_mirror.h` and presentation annotations/calls
  in `src/tyrian2.c`. Original indexed loops, gameplay/events and physical-9
  crop behavior remain exact. No artwork changes are required.
- Independent mathematical checks passed in optimized and sanitized builds:
  16,777,216 channel triples and 111,919,104 source-index/geometry cases per
  configuration. These establish the approved anchored residual rule, including
  nonlit unchanged-index cases and exact geometrically lit identity.
- Independent real-module units passed in both configurations: 439,744 index
  cases, 23,040 RGBA cases, 81,920,000 composed subpixels, 32 accepted frames and
  50 rejection cases per configuration. They exercise the complete renderer,
  six real HUD/font modules and original font bytecode at densities 4 and 8.
- Covered behavior includes classic-owned destination colors, local cash
  fallback, HUD boundaries, invalid scope/palette/layout/index/ownership,
  unexpected scene-font ownership, caches, multistep fades, saved-output
  restoration and repeated/skipped presentation. The disabled production
  caller also compiled.

These are offline tests, with no game runs. ASan and UBSan were enabled;
LeakSanitizer was disabled. Synthetic compositor inputs do not qualify every
scene-asset loader or artistic contour. The full historical test aggregate was
not rerun.

## Completed unprotected opening witness

One ordinary-menu Full Game → Episode 1 → Hard attempt ran with normal data,
unmodified original health/damage behavior, native 640×400 output and density-8
assets under Linux SDL dummy/software. It stopped after the input witness:
24 loop entries, 23 finishes, 9.083 seconds total and 3.231 seconds live. These
times describe this instrumented run and are not a performance benchmark.

- Five native captures: selected Hard menu, last ordinary output, first night
  cone, right response and left response.
- The frozen live observer reported zero original-index mismatches across
  23 finishes × 48,576 scene cells = 1,117,248 observed cells.
- Four retained source/destination/palette pairs independently reproduced
  194,304 scene cells with zero original-loop mismatches. The remaining
  19 finishes rely on the reviewed live observer, not retained-byte recomputation.
- Each retained gameplay capture compared 256,000 native readback pixels to
  its stored composed output with zero mismatches. All four cash samples matched
  the original lit palette result. This is output-to-readback proof; the run
  did not retain the pre-transfer authored canvas/ownership needed to re-prove
  Option 1 per subpixel. That proof is supplied by the offline units.
- All 23 before/after-composition state/RNG fingerprint pairs matched. This
  proves equality of sampled state around composition, not raw whole-engine
  snapshot equality or a paired baseline/candidate gameplay trajectory.
- PIC3 granted the lease before the first tick. The original event enabled
  night on tick 1; the first night output was tick 2. All 22 night finishes
  used the original player-relative light coordinates. Right and left input
  moved the player and cone; queued input was consumed and keys were released.
- Visual review accepted this limited opening: the original sharp cone and
  compressed terrain/cloud contrast were visible, HUD and cash were legible,
  and no glaring retained full-bright rim appeared. The final ship remained
  visible but low-contrast in shadow. This is not aesthetic acceptance of every
  enemy, projectile or pickup.

Two derived review images were inspected. Every classic pane is an indexed
reconstruction from the candidate run, not baseline gameplay. The larger
diagnostic is derived from stored output and is not native 4× runtime evidence.

## Completed protected mid-level/Boss diagnostic

Independent numerical and visual review accepted five selected windows from one
protected original-event progression. It completed 7,429 loop entries/finishes;
entry 7,430 was deliberately blocked. Six native 640×400 captures include Hard
selection plus five gameplay samples; two comparison sheets derive from those
same samples and exact same-run indexed reconstructions.

- Mid-level samples show shell 146 near the upper edge and then both 146/147
  with their turrets. The earlier parent tank bodies are top-clipped, so this
  is not a whole-body or all-eight-heading witness.
- The full-boss sample contains all 20 original records 46–65 and 80 matching
  quadrant draws, entirely within the scene crop below the bar.
- The energy sample shows the weapon-81 burst. Seven IDs appear in retained
  draw receipts, but this is not an all-seven-directions visibility claim.
- The final successful child launch matches original event 1146, parent
  record 53/link 142 and child type 3. The child is discernible over the core,
  not an isolated silhouette. This is a re-enabled launch, not the first one.
- All 360 sampled original-index oracles have zero mismatch and unchanged
  immediately bracketed composition state/RNG fingerprints. Transit is
  unsampled; no claim is made for every tick's canonical state.
- Five retained pairs independently reproduce 242,880 scene cells and match
  1,280,000 native capture pixels with zero mismatches. Capture equality is
  output-retention proof, not a second independent authored-RGB compositor.
- In every retained sample, 74 cash foreground cells and 110 neighboring
  shadow cells match the exact destination palette. HUD structure and meters
  remain legible with zero reported boundary/residue/rejection counters.
  Retained boss bars are wholly lit; dark-region bar appearance is untested.
- Visual review found no obvious full-bright residual contour rim in these
  samples. Some dark actors/projectiles remain low contrast, so universal
  visibility is not established.

Protection applies to an already-alive player on ticks 100–7,429 (7,330 entries).
It can alter blended player drawing, collision response and downstream
trajectory/RNG. This is a protected renderer diagnostic, not natural Hard
survival, ordinary player-style coverage, unchanged gameplay progression or
full completion. The terminal exit code 94 is the reviewed five-second
blocked-entry cleanup after a successful witness, not a normal game exit.
Instrumented durations (934.180 seconds at success, 939.243 seconds at outer
exit, 928.341 seconds live) are not a performance benchmark.

## Final combined-source offline rerun

The current production source is exactly the approved three-file night change
plus the independent four-line Christmas enemy-ID guard. Both source drivers
check the same exact inverse across all 148 production files against public
baseline tree `2a60deb74b1a677e3d3cd6c5ea0c251e8ac54028`. Removing only the
Christmas guard reproduces the frozen night renderer SHA below; reversing
the night change then recovers the public baseline byte-for-byte. Every
production byte outside the two approved deltas and all assets are unchanged.
See [exact source proof](source-proof.json) and [production diff](production.diff).

- The final night optimized and ASan/UBSan units each pass 16,777,216 channel
  triples, 439,744 index cases, 23,040 RGBA cases, 81,920,000 composed subpixels,
  32 accepted frames and 50 rejections, with unchanged historical counts.
- The Christmas baseline optimized, combined optimized and combined sanitized
  units each pass 1,156 original-wrapper transactions and 2,216 negative-guard
  checks. The baseline admits nine real-Christmas changed IDs with cold/warm
  caches; the combined candidate admits zero. Candidate draws remain
  702 accepted / 454 fallback. Scope assertions now include the exact night
  dependency: normal-data ordinary Hard+ is eligible on physical 15, while
  Christmas and excluded modes are rejected; physical 9 is unchanged.
- A normal full production rebuild and a separate `RENDER_MIRROR_DISABLED`
  compile of `src/tyrian2.c` pass. The latter is caller compile coverage, not
  a full disabled link. Normal build warnings are pre-existing indentation
  warnings in unchanged statements.
- ASan/UBSan remain enabled; LeakSanitizer is disabled. No new game run,
  artwork, full-source snapshot, full resource-pack copy or test framework
  was added. Historical isolated Christmas JSON/diff receipts are retained
  unchanged and are not relabeled as combined evidence.

[Combined validation metadata](validation.json) records the final source/test
pins and results. The unchanged three-file night delta ties earlier runtime
evidence to this source, while the independent Christmas guard has separate
admission/indexed-write units. These checks are not a new combined gameplay run.

## Excluded coverage

No full-level clear, natural Hard survival, ordinary protected-run player style,
all-headings/all-projectiles coverage, pickup lifecycle, paired baseline gameplay,
native 4× runtime, physical GPU/input/audio, performance or Windows acceptance
is established by this night packet. The full historical aggregate is not rerun.

## Evidence identity

The public baseline is tree `2a60deb74b1a677e3d3cd6c5ea0c251e8ac54028`, published
at commit `06a935e9b6995b4d11e96e6e6d8385325c85f1e5`. SHA-256 pins below identify
the reviewed frozen content. They do not imply these raw receipts or original
game inputs are bundled, or qualify later source/test edits.

- Approved Option 1 contract: `1bc78605ace6739a8981db4bc382c7d044a9b7dc144e8109d60a419453e7bc6a`
- Source/unit review receipt: `31496347e2c1834f98017d287ba93bf6faa23cc3454ca8e8bf5d02c4d4039948`
- Actual opening review receipt: `a7eb6ab4e2700db93e52f5232301b95ba7345969967a51c0b484c3219fe49faf`
- Protected actual review receipt: `fa86076f2de415a25fe9ae7cc7beff3620ac3163a642c12bd709bed60a649201`
- Protected visual review: `d7042e1aedd955c371f863f8be95db0d984e2980fda4ba2b4ab8d957dcc14282`
- Protected independent numerical review: `eff24303f4d5d0a843ff266b4a5a548a5f1acd035d1507dd8bb94d5a34400c1a`
- Frozen night-only `src/render_mirror.c`: `7bcd99a433733794e3f384f3b485b60219a251adfad7bf1f7412f29abf5687e2`
- Combined `src/render_mirror.c`: `8c44901a23942dc09bf3b4c3bff462ec70dee4547d2eb6e7bd22382f8f7e96a3`
- `src/render_mirror.h`: `ffff0a989ec27ec710426dba1ae0ebaf0d8c027aca77721c5813aae7b86cd6fe`
- `src/tyrian2.c`: `33ad04c16c53861a956608f91dd2edd0c25d1d63e4921f1266abdba5f054ba48`

The three existing finite test files are `prototype/test-normal15-source.py`,
`prototype/test-normal15-night.py` and `prototype/test-normal15-night.c`.
Their baseline reads now use the public tree above, with no local-only commit
alias required. The source checker also supplies the Christmas driver's exact
combined inverse. Original game inputs remain external.

## Reproduction

Requirements: Python 3, C99 compiler, make, pkg-config, SDL2, SDL2_net, Git objects
for the public baseline tree, and ASan/UBSan support. Use matching separately
owned original game data. Choose fresh external output directories:

```sh
python3 prototype/test-normal15-source.py --out /path/to/external/source-proof.json
python3 prototype/test-normal15-night.py \
  --normal-data /path/to/original-data \
  --out /path/to/fresh/external/night-units
python3 prototype/test-christmas-enemy-fallback.py --source-only
python3 prototype/test-christmas-enemy-fallback.py \
  --normal-data /path/to/original-data/tyrian.shp \
  --xmas-data /path/to/original-data/tyrianc.shp \
  --out /path/to/fresh/external/christmas-units
make -B -j2 VCS_IDREV=false
cc -std=c99 -O2 -DRENDER_MIRROR_DISABLED -DTARGET_UNIX -DNDEBUG -DWITH_NETWORK \
  $(pkg-config --cflags sdl2 SDL2_net) -Isrc -c src/tyrian2.c \
  -o /path/to/external/tyrian2-disabled.o
```

These commands build/test offline and do not launch the game. The night driver
materializes only bounded palette/PIC3/font slices and six named HUD resources;
source hashes and exact inverse checks replace its former redundant full-source
snapshot. No original inputs, private captures or machine-specific execution
paths are distributed in this documentation.
