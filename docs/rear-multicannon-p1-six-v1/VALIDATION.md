# Rear Multi-Cannon P1 six-head pilot

Baseline: `22661ddfca21c6a81e3ec2af0670c24ea4ceed92`.

Integration status: **PASS: bounded source, artwork and native runtime qualification**. The immutable artwork
package records its earlier R2 art-stage decision; this document records the
integration decision and its limits.

## Bounded scope

This adds six static, full-canvas 12×14 heads to actual player-one rear
Multi-Cannon 10 power-one emissions on episode-one Normal (physical level 9) and
Hard (physical level 15). Mode one record 254 alternates 39/1; mode two record 265
cycles 281/282/301/300. There is no new animation. Role 131 owns twelve exact
density-4/density-8 resources in the two current default packs. Rollback packs are
unchanged.

The six source IDs are not a generic sprite whitelist. They are reused by higher
rear powers, NortShip Spreader, linked weapons, Mega Pulse and Rear Mega Pulse
chain children, and charge-related children. A lease at the actual main-weapon
call site and an 80-slot renderer-only birth sidecar identify the qualifying
emission. Every successful slot allocation replaces that slot's sidecar, including
nonqualifying reuse. Slot 80 is excluded. The original player-shot structure is
unchanged.

Birth identity remains stable across subsequent weapon mode/power selection:
existing P1 shots retain their identity, and old higher-power shots cannot become
P1 shots. The legitimate last draw after the original availability decrement is
retained. Observed source, table, scope or immutable-shot mismatch permanently
revokes that birth until genuine slot reuse. A temporary off-screen view or
missing optional resource does not create or promote an identity.

Unsupported contexts retain the existing renderer: network, two-player, linked,
Galaga, Christmas, demo/record, action/arcade/super/timed/bonus modes, shop
simulation, alternate source banks, other weapons and higher-power births. The
finite horizontal view does not reinterpret the original horizontal-wrap route.
Vertical clipping remains in the existing compositor.

## Source and resource guards

The current canonical 32,060-byte normal bank pointer and size are checked before
bounded decoding. Both decoded indices and coverage are stamped at birth and at
draw. Records 254/265 are serialized in original loader order, with explicit
little-endian words and all signed and unused byte fields. Hashes are published;
original decoded sprite arrays and original weapon payloads are not.

Before cold or warm resource use, the adapter checks the immutable emission,
source/table identity, dimensions, anchors, role, key, exact density, payload
pointer and full RGBA hash. Six-by-two cache slots are separate from generic
assets. The selected root and density remain fixed for the renderer session.
There is no cross-density fallback or disk hot reload. Public manual-HD startup
selects density 8; the density-4 route is separately qualified as a diagnostic
renderer selection, not an additional public startup mode. A failed cold attempt
stays classic for that session; replacing a previously cached valid file takes
effect only after restart.

The new view checks typed pixel/scratch alignment and overflow-safe disjoint
INDEX8/canvas byte ranges. Exact and partial aliases, address wrap and misalignment
fail closed; legitimate padded pitch and exactly adjacent ranges remain valid.
These defensive checks were completed before the final runtime source freeze.

Only the new role uses a finite exact-length regular-file loader. Linux tests
verify prompt rejection of FIFO, directory and device targets. Symlinks to
regular files are permitted. This is not a guarantee against every stalled
filesystem, and Windows runtime behavior has not been qualified.

## Artwork

Three independently authored vector silhouettes extend the accepted front-Multi
continuous yellow/orange/red luminous style. IDs 1 and 39 retain their distinct
geometry. Canonical 281 produces the other three diagonal heads through exact
whole-canvas RGBA permutations. Empty margins and anchor 0,0 are preserved.

R2 retains every R1 straight-RGB byte and supported sample. A 0.30-logical-pixel
inward coverage ramp softens the edge without enlarging the footprint or blurring
the core. Integrated coverage is 92.55–94.89% of R1; the tested heat-focus core
retains identical fully opaque RGBA. No night treatment is baked into the art.
Both density outputs are independently rasterized from vectors, with no native
1× intermediate or density-8-to-4 downsampling.

All six standalone SVGs, authoring scripts, twelve PNG/RGBA payloads, version
contracts and reproducible proofs are included. Independently scan-converted
reflections can differ at antialiased boundaries; the recorded canonical
whole-canvas-permutation output is authoritative. No original reference images,
game backgrounds, private captures or extracted game data are included.

## Reproduction

Run the public checks from the repository root:

    python tests/run_rear_multi_p1_core_tests.py
    python tests/run_rear_multi_p1_adapter_tests.py
    python tests/test_rear_multi_p1_source_inverse.py
    python prototype/build-rear-multicannon-p1-art.py
    python prototype/build-hd-assets.py --output /absolute/new-pack-directory

The ordinary aggregate verifier/rebuilder uses Python/Pillow. For a fresh
source-vector rebuild, install the exact recorded Node/Sharp toolchain and run:

    python prototype/build-rear-multicannon-p1-art.py --vector-output /absolute/new-vector-directory

Existing output directories are rejected. The current exact toolchain is Node
v24.19.0, Sharp 0.35.5, Linux x64, with every native renderer dependency recorded
in the artwork package. Both fresh and relocated vector rebuilds are byte-exact.

## Actual runtime results

The final source/art freeze passed 16 paired cases, 32 fresh processes and 4,080
logic ticks. Fourteen pairs retain unmodified public manual-HD startup at density
8. Two additional Normal/Hard native-2× pairs use separately pinned, reversible
presentation-only startup selection at density 4. These diagnostics qualify all
six density-4 payloads through the actual renderer without creating a new public
startup mode or altering gameplay state.

Natural menu purchase, original `time(NULL)` seeds, inputs and gameplay remain
authoritative. Original per-tick state, RNG, INDEX8 buffers, palettes, allocation,
movement, collision, original head/shadow blits and their order match within every
pair. Each natural P2 control genuinely emits all six same IDs forty times with
zero new-role admission. Removing or corrupting only the twelve new resources
falls back to baseline-exact native output.

Actual 640×400 and 1280×800 SDL software-renderer readbacks verify support-contained
changes and fractional alpha against the ordered underlay. The unchanged Hard
night filter is independently reconstructed over the full gameplay viewport.
Ship overlap at tick 80 and lower/HUD clipping at tick 88 preserve order. Mode
1→2→1 and stop-fire clear to baseline-exact frames at ticks 150 and 179. Separate
actual repeated/skipped SDL Present cases preserve state, RNG and admission.

All final observations are fresh. Post-completion hard-link deduplication of
identical immutable bytes is storage-only, not observation reuse. The superseded
pre-layout-guard qualification is retained separately and does not establish the
final-source result. Six private observer inverses restore exact original source;
those observers, data, captures and binaries are excluded from the repository.

See `RUNTIME.json` for case-level counts, source/art pins, build details, hashes
and explicit limits. Broader mixed-use, power-lifetime and cache mutation coverage
is supplied by separate core/adapter tests rather than a claim of native coverage
for every excluded game mode.

## Qualification record

- Strict C99 core and independent provenance tests pass plain and ASan/UBSan;
  the independent provenance suite executes 4,452 checks per build.
- The public actual-adapter suite passes 21,313 checks and 192 malformed-resource
  cases per build, plain and ASan/UBSan. The separate independent synthetic suite
  passes 21,733 checks per build. These exercise the real adapter, bounded decoder,
  wrapper and loader, with an observer replacing only the pixel sink.
- An additional private-data check passes 15,197 checks per build with authentic
  source bank/records and final production pins. No original data enters the
  public tests or artwork.
- All 156 baseline source files are restored exactly by removing the enumerated
  renderer-only hooks. The generic asset route, original shadow draws and Hard
  night filter remain unchanged.
- All prior artwork, source PNGs and runtime resources remain exact; only the
  asset catalog is extended. The aggregate rebuild verifies both
  default packs at 589 resources each, plus every other existing pack/sidecar.
- Fresh normal builds pass with the existing documented diagnostic suppressions.
  Mirror-disabled builds retain precisely the same 15 inherited unused warnings;
  no new warnings occur. Disabled strict builds use explicitly enumerated
  inherited-warning suppressions.

ASan/UBSan uses `detect_leaks=0` because LeakSanitizer cannot run under this
environment's ptrace setup. This is not leak-check coverage. The synthetic sink
does not establish final display pixels; actual native runtime evidence is a
separate required gate. No Windows/GPU/full-campaign claim is made.
