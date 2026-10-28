# Shared NEWSHF aircraft 169: three-pose finite extension

This development candidate adds original enemy record **169**, not the existing dual-missile family whose sprite base is 169 (records 2/500). It is one shared family, with no per-level asset copies or changes to gameplay coordinates, events, movement, collision, health, or pose timing.

- Logical source bank: 10 (`newshf.shp`). Native cycle bases: 79, 77, 115; 24×28 quartet, anchor (6,7), component offsets 0/1/19/20. Cycle 1 is straight; cycles 2/3 retain their original banking graphics without introducing animation.
- Resource IDs: 2100037–2100039; phases 37–39; profile 20. Resource count 40 and group mask `UINT64_C(0xe000000000)` fit the existing 64-bit dependency witness. Bounds reject unknown phases before indexing or shifting.
- Exact original 77-byte `tyrian.hdt` record at offset 177028 is pinned by SHA-256 `1e189a8f99ab90040bb5967779232f54db4bf8bf1bb732cbfb94a21ad845be43`; runtime uses its independently reproduced FNV witness. No original record or source-color pixels are published.
- Native occupancy masks are immutable and contain 260/238/238 occupied cells in the cycle order above. Transparent source cells remain RGBA zero; partial alpha or cleared occupied cells retain the existing typed-underlay requirements.
- Independent resource loading, source identity, palette checks, resource mutation detection, owner/borrow transfers, reset, cached contribution and row-wrap classic fallback retain the previous contracts. The only production changes are the two finite render/identity descriptors and two new headers.
- Existing 166/165/164 and older art remains byte-exact. Prior proof ledgers and native harnesses remain immutable; bounded adapters preserve their exact preimages and adjust only declared finite boundaries.

## Episode and evidence scope

The historical original-data audit records 18 direct spawns across E1 level 8 (5), E1 level 12 (3), E3 level 10 (6), and E5 level 4 (4). This is reuse evidence, not proof of a captured natural HD encounter. Admission pins only the original E1–3 record identity; no alternate E4/E5 identity or scene architecture is introduced. Render eligibility follows exact source/identity evidence, never an episode or level whitelist.

New naturally visible and controlled evidence must remain separately labeled. All three actual authored poses, gameplay differentials, inherited native matrices, ownership/borrow checks and E5 classic fallback equality require candidate-specific evidence. No inherited receipt qualifies new assets.

## Development and qualification

Use `test_current_aircraft169_newshf_authoring` during art iteration and verify the actual generated bundle with `current_aircraft169_newshf_compatibility.load`. Candidate integration uses the existing finite source/runtime projection, package/catalog checks and native adapters. `aircraft169_smoke.py` is explicitly not a release substitute.

`run_aircraft169_qualification.py` adds new family checks while retaining all 17 original166 selectors and its SHOP mutation targets. The original166 qualification driver remains unchanged. Do not run multi-hour release acceptance until the parent freezes the coherent candidate. Every later byte change invalidates the associated evidence. Linux cloud checks do not establish Windows or full-campaign acceptance.
