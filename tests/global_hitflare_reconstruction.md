# Hitflare7 focused reconstruction tests

Run `python3 tests/global_hitflare_reconstruction.py --data <original-data-directory> --receipt <outside-checkout-path> --sanitize`.

Snapshots the production Talon and Hitflare includes, registry, root setter, actual explosion allocator and Hitflare helper, pixel observer and fade entrypoints. Original shape/palette files are verified in memory and passed only through stdin; no original bytes are saved. Only authored resource copies are corrupted in temporary fixtures.

Covers all seven phases at 4x/8x, normal/blend, both genuine caller-role envelopes; exact independently computed RGBA/support; wrong or unscoped births, fixed145, fresh allocation, last/exhausted slots without original-state changes, clipped bounds, slot reuse, replay/order, cold/warm source/palette/operator/mode negatives; every resource missing/corrupt/header/trailing; observed-write transactions, equal-index writes, final mapping, cache and surface leases, integer fade with alias/layout negatives, transferred contribution with no remaining owner bits and next-frame recovery.

Enabled Talon/Hitflare overlap tests cover both draw orders and transferred Hitflare source proof. Shared Shield and Pulse modules are explicit no-op stubs. SDL is a bounded structural shim, indexed emission uses an independent decoder, and this does not prove native caller contexts, HUD typography, real input/audio, Windows, GPU or whole campaign. Separate native tests establish those applicable game-engine observations.
