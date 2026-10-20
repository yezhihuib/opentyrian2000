# ASTEROID1 four-state ember installation

This checkpoint adds NEWSHD record 269 as one coherent four-image family under
normal-data Episode 1 physical level 1 ASTEROID1 opt-in. Use
`--asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1` during ordinary campaign
progression. This option does not select or play a level. The finite optional
catalog contains 45 images, 18 independent families and 46 source records. All
prior 41 PNG/HDR1 pairs and both 629-entry default catalogs remain unchanged.

## Original identity and animation

Canonical 77-byte record 269 FNV1a64 is `587e8cbe02db82e2`. Logical bank 8 NEWSHD
contains 42,012 bytes, pinned to `913975450e0fc00d`. Each callback verifies the
current loaded bank binding, exact size and every byte against the existing
renderer-private immutable NEWSHD snapshot. NEWSHS keeps its own separate
46,566-byte snapshot. Numeric bases in another logical bank cannot qualify.
Physical 2 randomly reuses 269; the physical 1 gate remains mandatory.

Five independent original event 6 actors allocate through JE_makeEnemy in pool
25–49: ordinals 250/251 at curLoc 4220, 352/353 at 5676 and 373 at 6208. Map-relative
placement, allocation failure, scrolling, culling and ordered quadrant calls
0/1/19/20 remain original. Zero source startxc/startyc consumes no position RNG.
Record 269 has no firing, launch, drop or damage-image closure. Link 0 death only
destroys the struck actor. Positive remaining armor, value, ice and inactive
countdowns are not frozen to constructor values. Enemyground remains false,
explonum 2, despite event 6's Ground Enemy label.

The exact continuous sequence is:
267,267,269,269,271,271,273,273,271,271,269,269,267,267,267,267,267,267,267,267.
Constructor cycle 0 pre-increments to first callback 1. Cycle 20 wraps to 1 on the
next eligible draw. Original horizontal eligibility gates animation; vertical
offscreen state and ice do not pause the active sequence. Every repeated entry
keeps its original dwell. There is no added timer, interpolation or pulse.

## Artwork and renderer boundary

The built-in image generator authored one smooth copper/red 2D metal housing
and dark, dim-red, orange and yellow chamber states. Four generated masters,
provenance, PNGs and a deterministic converter are retained. One opaque shared
housing is used throughout; all state differences stay in the original logical
5×13 rectangle x 8..12 / y 6..18. All 672 original occupied cells remain opaque,
including the dark recess, rails and gray supports. No procedural recoloring or
code-drawn geometry replaces the generated raster art. Density 8 is internal
resolution, distinct from native 2×/4× game display size.

Private NEWSHD resources 267/269/271/273 have roles 1080267/1080269/1080271/1080273,
logical 24×28, density 8 and zero anchors. All four pass exact header, length and
payload pins before any replacement. Missing or corrupt one disables the whole
family. Selected-root failures stay sticky until renderer shutdown/reset. The
other 17 families stay independent. Dependency failure after an accepted 269
quadrant rejects the whole HD frame. All original per-quadrant filter and
side/top/bottom clipping behavior remains authoritative.

Live guards pin record/context/source identity, original pool and availability,
positive armor, zero link/drop, motion and acceleration, reversal 100, all 20 egr
entries, active 1 / cycle 1..20, exact selected base, no turrets/frequencies/launch/
damage alternate, explosion semantics and each original quadrant origin.
Dispatch is explicit type 269; raw bases never fall through another asset role.

## Validation and limits

See validation.json for final test/build/catalog/review and actual-engine
results. Optimized and ASan/UBSan suites verify 77 cold + 77 warm canonical byte
mutations, 64 malformed-art fixtures per mode, all 20 animation entries, repeated
dwell, constructor 0→callback 1 and 20→1 wrap. Extracted original constructor/draw
code and production MT RNG compare complete actor/shot/countdown/sound/RNG state
and require positive HD admissions. Boundary, filter, ice, all loaded slots,
source-bank independence and sticky/frame-local fallback cases are exercised.
All 46 source-record corruptions are checked across all 18 independent families.
Preceding 325 and 287/288 suites are rerun.

Actual-engine evidence is explicitly ASSISTED original-event windows at 4220,
5676 and 6208. Original setup/spawn events replay in order with raw eventRec and
selector RNG preserved; prefix actors are omitted. JE_makeEnemy remains intact.
No actors or projectiles are injected, healed or resurrected. Paired native 2×/
4× baseline/candidate windows cover all five ordinals, four bases, twenty cycles
and wrap, with original top/bottom clipping. These placements do not cross a
side viewport boundary; side-clipping evidence is the dedicated extracted
production-draw suite. This is finite original-event evidence, not a natural
campaign clear. Each missing/corrupt-member and flag-off pair checks fallback.
Some state-contact crops include the unchanged INSERT COIN overlay partly
occluding the surrounding scene. The separate all-five-events contact retains
clear native-scale housing comparisons; captures are not repainted.
The engine runs use headless SDL dummy video and a software renderer, with
unresized 640×400 and 1280×800 native readbacks. No desktop-window check is claimed.

Original game data, harnesses, captures and binaries stay external. No Windows
build or external publication is included. LeakSanitizer is disabled;
AddressSanitizer and UndefinedBehaviorSanitizer run. Compiler address space is
bounded to 1 GiB and runtime RSS to 512 MiB. Catalog-only validation uses an explicit
historical asset root without rebuilding; that root is not a public runtime
setting.
