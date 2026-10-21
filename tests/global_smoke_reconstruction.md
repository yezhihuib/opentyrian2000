# WhiteSmoke7 focused production observer tests

Run `python3 tests/global_smoke_reconstruction.py --data <original-data-directory> --receipt <outside-checkout-path> --sanitize`.

Snapshots current production Talon and white-smoke includes, registry, allocator, pixel, root and fade entrypoints. Original shapes and palette remain in process memory and child stdin only. Source parsing, RGBA blending and indexed writes are independently calculated in a bounded SDL structure shim.

Covers all seven source frames 135–141 at internal 4×/8×, normal/blend, actual allocator types 6/98/198, delta Y 0/−2/3 with native background drift, type-6-only x+2/y+12, signed-16-bit initialization, exact per-phase RGBA and support, position and TTL provenance, cold/warm rejects, slot reuse and pool exhaustion, source and resource faults, final mapping, cache/geometry/alias leases, partial/equal/repeated writes, Talon ownership transfer and integer fade. Other families are explicit disabled stubs here; native tests must establish actual caller and integrated family/HUD behavior.

This suite is not a real SDL game run, full campaign, Windows, GPU or acoustic test.

Observed-fault restoration checks deliberately retire all owner bits, observe source, palette, mode or layout failure even through an invalid/non-smoke slot, restore inputs, and require sticky Finish rejection. Additional checks cover a second valid slot with wrong native role, bank, style, target or coordinates. `--negative-control` removes only the preflight from a temporary build; successful detection requires the specific sticky-fault assertion to fail. A separate movement edge uses `explodeMove=65535` and delta Y 1 to establish native two-step signed-16-bit narrowing.
