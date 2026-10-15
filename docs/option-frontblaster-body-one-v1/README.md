# MicroSol FrontBlaster body: finite QUAD renderer batch

Baseline:d755b79c890d140e294a683664259d6833a3ca6f,
tree481455fc0deaf7cf93a7fdf3521b3d4e8618e9ad.

## Production boundary

Exactly one static24x28 body is admitted from the existing option20/style2/
charge0/base83 bank10 QUAD draw site, at its original sidekick.x-6,y origin.
Role128/slot540 is separate from the other body and projectile families.
Options22/26 share base83 but do not enter this binding. Original pre-draw
animation wrapping, attachment, launch/return, firing and draw gating/order
remain unchanged.

The dedicated wrapper prepares one ordered normal asset, always executes the
original indexed blit_sprite2x2 exactly once, then ends the mirror entity. That
original composite retains all four blit_sprite2 calls in83/84/102/103 order.
There is no new body shadow. Existing weapon727 shots121/122 are untouched.

Every cold or warm lookup first verifies current spriteSheet10 pointer and size,
boundedly decodes all four tiles into zeroed672-index and672-coverage buffers,
and checks the complete24x28 identity. Identical normal and Christmas sources
are both eligible only while that guard passes. Existing scene-level eligibility
is unchanged, including normal15 Christmas exclusion. Malformed/changed source,
wrong scope, missing/malformed resource or incompatible surfaces stays classic.
The existing ordered compositor and independent8-to4 fallback are unchanged.
Full-quad horizontal row-wrap is conservatively excluded from HD; original
indexed writes keep their exact edge behavior.

## Frozen resources

One already-generated and reviewed master is imported with the fixed crop,
resample and registration in the artwork contract. No repaint, recolor, shift,
threshold or source-mask compositing is used. The complete192x224 density8
canvas has anchor0,0. The accepted offline tradeoff is about90% original
alpha-weighted area and a0.31-logical-pixel higher centroid.

Each default pack grows548 to549 listed resources and559 to560 physical files,
with555 HDA and five auxiliaries. Every prior physical byte, including six
unlisted HDA, and every rollback pack is preserved. Run
python3 prototype/build-frontblaster-body-art.py for exact reconstruction and
pack preservation. Original game data, extracted pixels and runtime evidence
are private external test inputs and are never bundled in this repository.

## Qualification

The published baseline and final candidate each completed320 original first-level
ticks in Normal9 and Hard15 from an actual right-side first-shop purchase8000,
with leftNone/right20 and cash10000 to2000. Original indexed surfaces, palettes,
explicit player/enemy/shot/particle/global state, RNG, attachment state and
original input/draw/pose/firing traces match exactly within each paired case.
Both source executables retain the same untouched natural time(NULL) seed.

Each run retains320 complete original QUADs,1280 ordered indexed tile calls and
90240 original writes. Ordinary LeftAlt detaches at110, requests return at140,
and naturally reattaches at170. There are54 weapon727 requests and108 emitted
shots,54 each of121/122. No equipment, cash, position, protection, attachment,
firing, time or RNG override is used. Natural pickups after purchase are kept.

All80 actual640x400 renderer-readback PNGs have valid chunk CRCs, including
IEND. All34 gameplay screenshot pairs differ only inside the complete original
24x28 body canvas; shop pairs match exactly. Actual tick100 attached and175/190
reattached scenes include ten original occupied body/Talon overlap pixels with
invulnerability zero. Normal and Hard launched full screens and exact old/new
attached/launched/returning/reattached comparisons have been visually accepted. Runtime data and screenshots stay private.

Hard has319 actual NIGHT ticks and one ordinary-output tick. This forward body
stays wholly in the lit cone on the natural path, with282 lit source support
cells; no transition/dark body coverage is claimed. No Christmas actual-engine
run, whole-level/campaign survival, Windows/GPU or performance qualification is
claimed. Christmas current-source cold/warm reloads are covered by focused units.

Optimized and ASan/UBSan units pass source mutations, all-quadrant coverage-only
changes, same-address normal/Christmas reloads, invalid resources, independent
8-to4 fallback, duplicate/overlap and exact original edge/row-wrap behavior.
All153 production source files inverse byte-exactly to the baseline after the
finite five-file addition is removed; twelve forbidden mutations are rejected.
All72 translation units link; the disabled renderer boundary compiles and the
Windows project source inventory is valid. See verification.json for precise
bounded evidence and limits.
