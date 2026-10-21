# SmallExplosion12 focused production observer tests

Run `python3 tests/global_small_explosion_reconstruction.py --data <original-data-directory> --receipt <outside-checkout-path> --sanitize`.

Snapshots current production Talon and ordinary small-explosion includes, registry, allocator, pixel, root and fade entrypoints. Original shapes and palette remain in process memory and child stdin only. Source parsing, RGBA blending and indexed writes are independently calculated in a bounded SDL structure shim.

Covers all twelve source frames 122–133 at internal 4×/8×, normal/blend, actual allocator type 1 only, delta Y 0/−2/3 with native background drift, unchanged birth coordinates, signed-16-bit initialization and movement, exact per-phase RGBA and support, position and TTL provenance, cold/warm rejects, slot reuse and pool exhaustion, source and resource faults, final mapping, cache/geometry/alias leases, partial/equal/repeated writes, Talon ownership transfer and integer fade. Types 0, 2–10, 12, 14, 35, 53, 98 and 198 are negative identities. Other families are explicit disabled stubs here; native tests must establish actual caller and integrated family/HUD behavior.

Observed-fault restoration tests retire owner bits, observe source/palette/mode/layout failure through an invalid slot, restore inputs and require sticky Finish rejection. Further tests cover a distinct valid slot with wrong native flags, bank, style, target or coordinates. `--negative-control` removes only this preflight from a temporary build and requires the sticky-fault assertion to catch it.

This suite is not a real SDL game run, full campaign, Windows, GPU or acoustic test. The separate source projection proves observer-only original source changes, not runtime behavior.
