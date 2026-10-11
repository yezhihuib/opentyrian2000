# Physical rotor enemy types5/11: finite validation

## Identity and production change

Original newsh2 enemy types5/11 use eight24×28 composite phases:229,231,233,235,237,239,241,243. Type11 reverses that order. Each consists of the original12×14 quadrant calls at base,+1,+19,+20, with composite anchor6,7. Both loaded records have ani8 and no separate damage graphics or firing weapons. This is a physical metallic enemy body; homing/movement behavior is not an energy classification.

Only the exact odd-base mapping in the existing role101 enemy path and asset capacity change. Slots210–217 are used;201–209 remain reserved for the separately reviewed ground family. Bank identity, original quartet clipping/draw order, hit-palette filter, gameplay, collision and RNG are unchanged. A missing composite falls back for all four of its quadrants without freezing or substituting animation. Numeric229 in player/shield banks remains unrelated.

Eight generated PNGs and their HDR1 overlays extend the two current default packs to213/217 files. Existing packs/resources are untouched. Total manifest:18 packs,2666 HDR entries,225 unique formal PNGs. Shared arc geometry uses fixed lighting and eight calculated rotations; fixed generated core and per-phase placement are retained. The original237 gap-widening is intentionally not copied, to preserve rigid geometry. `prototype/build-rotor-art.py` rebuilds all eight PNG/RGBA bytes exactly with Blender4.3.2/Pillow and no game data.

## Actual runtime checks

- Natural original type5 wave: replay through929, presentation from600, at native4×/2×.5,474 role101 quadrant attempts across all eight phases are HD; zero coverage/classic errors. This counts offscreen/partially clipped draw attempts, unlike the earlier5,308 intersecting-material index references. Last family draw is912; final RGB913–929 exactly matches original baseline, proving clean disappearance.
- State, collisions, player/enemy projectiles, effects, poses and enemy logs remain byte-identical against original-art replay. Production executable at608–615 has exact RGB/state versus the reviewed private fixture.
- Missing235 actual8-frame replay:28 HD quadrants and four original fallbacks. All-eight-missing replay:32 original fallbacks and original baseline RGB/state exact.
- Native4×/2× eight-phase contact608–615 and120 consecutive real2× frames608–727 reviewed independently. Video input is direct SDL readback; every lossless-decoded frame hash and corresponding noncapture RGB/state audit matches. No synthetic scrolling/tweening. MP4 is a lossy viewing copy.
- A private diagnostic substitutes loaded type11 for requested type5 and sets its existing filter byte before original JE_drawEnemy/blit calls. Native4×/2× captures confirm243→229 reverse phases and filters00/70/80/09, all32 quadrants HD, no seams or old-art flashes. State/indexed logs exactly match the same diagnostic using original art. This is a synthetic trigger, not a naturally encountered type11 wave. Diagnostic hooks and captures are outside Git.
- Real cloud desktop window: native4× paused608, resumed through616, exit0. Native Windows/GPU/fullscreen/physical2K and whole-level performance are not claimed.

## Focused regression

`python prototype/fixtures/test-rotor-enemy.py --sanitize` extracts the production functions and tests synthetic HDR files. ASan/UBSan:101,573,120 pixel comparisons,1,016 successful quadrant calls,105 rejected source/part guards. Covers quartet-vs-full-composite equality, forward/reverse order, densities4/8 and8→4 source fallback, clipping/alpha/seams, four filters, source-bank isolation, malformed header/anchor/length, one-frame absence, classic/missing/invalid flags and cloud provenance. LeakSanitizer is disabled under ptrace; address/undefined checks are active.

Cloud-shadow and green-head-layer ASan tests still pass, including1,935,360 ordered-layer comparisons;12 strict fixture-preparation checks pass. Incremental production build passes with preexisting misleading-indentation warnings. No CI status jobs exist in this branch. Do not extrapolate this finite segment to unrelated enemy families or later-level overrides.
