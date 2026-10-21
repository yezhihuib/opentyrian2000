# Shield22 focused reconstruction tests

Run `python3 tests/global_shield_reconstruction.py --data <original-data-directory> --receipt <outside-checkout-path> --sanitize`.

The harness snapshots the current production global Talon and Shield includes, their registry, root-reset setter, original explosion allocation/helper, pixel observer and fade entrypoints. The snapshot is compiled separately with ASan and UBSan. Original `tyrian.shp`, `newsh6.shp` and `palette.dat` bytes are verified in memory and passed through stdin; they are never written as test fixtures. Only authored replacements are corrupted in temporary resource fixtures. The receipt hashes every source snapshot and verifies whether sources changed while the run was in flight.

## What is exercised

- All 27 semantic phases of the 9 actual shield parts, normal and blend at 4x/8x, 1P follow and 2P non-follow. The original allocator and bounded real helper are extracted, not replaced with a fake role grant.
- Exact per-pixel straight-alpha expected output and support masks against independently loaded artwork. This includes five empty source phases and the authored-transparent 268 resource, whose opaque source must not reappear.
- Birth arguments, source role, allocation generation, fresh/free-slot and same-tick initialization; replayed initialization, slot reuse and logical reset.
- Wrong index, TTL, ordering, repeated draw, slot geometry/operator, copied/wrong bank and source-size changes, original-reference/missing/invalid modes and palette changes, both before and after resource cache warm-up.
- Every one of the 27 source fingerprint mutations. Every one of the 22 authored resources is independently missing, payload-corrupt, header-corrupt and trailing-byte-corrupt. A Shield-only resource directory excludes unrelated-family resource dependencies.
- Exact original indexed writes are independently decoded/emitted and fed into the current production pixel observer. Missing, duplicate, off-bounds and wrong-operator observations fail closed. Equal-index normal writes retire ownership; shadow writes preserve supported ownership.
- Ordinary final composition and cache checks, final writes, source/canvas/output geometry mutation, aliasing/alignment guards.
- Actual enabled Talon and Shield in both draw orders, disjoint ownership transfer, exact composed output and cross-family source dependency rejection.
- Actual production fade entrypoints with other HUD state empty: valid integer palette step and pixel output, wrong saved-buffer layout/alias, source/output mutation and unexpected palette changes.

- Zero-final-owner contributor handoff: independent finish proof, repeated cache validation, source/palette/fault/root-disable and surface-lease invalidation before finish, after compose/before Present and during fade, followed by clean next-frame recovery. This models owner-bit transfer, not a real HUD glyph; it tests supported state invalidation, not arbitrary memory-tamper resistance.

## Limits

SDL allocation/layout is a bounded shim; this is not a native game run. The focused test does not call the whole `JE_playerDamage` branch or process player input/audio. The birth helper and allocator are actual source, while indexed sprite writes use an independent decoder rather than the complete native sprite blitter. The distinct native-pair suite must establish the actual damage branch, original state/RNG/sound/INDEX8 parity, real frame scheduling and visual positives. HUD font/scene modules are disabled in this focused harness, so HUD coexistence is covered by native tests, not inferred from these stubs. No Windows, GPU, full campaign or unrelated family acceptance is implied.
