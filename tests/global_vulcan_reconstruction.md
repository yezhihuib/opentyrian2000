# Vulcan2 focused reconstruction tests

Current production Vulcan owner, real allocator, original primitive/pixel/root/fade functions with bounded SDL and unrelated-family shims. Original three weapon-table variants, shapes and palette travel only in memory over stdin. This is not native engine proof.

Covers all 11 complete records and used multipositions in all three variants, 1P/2P and 4x/8x; birth role/slot generations/born-on versus born-off; all 80 record and 82 port bytes; two exact RGBA resources and original head/shadow placement; cold/warm role/source/operator/palette/resource failure; source/cache/lease/fade/reset and transferred RGB contributor retirement. Native tests separately exercise actual input, HUD glyph transfer and integrated rendering.

The shared public front-dispatch wrappers and real Pulse helper implementation are compiled alongside Vulcan. Pulse tables are not loaded, so no claim is made of full enabled Pulse native rendering here. Born-on failed initializer/table claims remain classic-only across root disable/re-enable; born-off disabled-root draws return to the old route, and true allocation/reset revokes both. Actual mixed-family native runs are separately required.

Moving births exercise the real allocator for all three variants, 11 records, both players and every used lane at horizontal deltas -17, -5, -2, 0, 2, 5 and 17, checking exact del-98 clamp and admitted role. A wrong initial XM within the numerical clamp range is rejected, rather than accepting a broad velocity range.

Token-scoped geometry must be witnessed: missing/wrong-token geometry, wrong X/Y origin and wrong mouse-X proof all reject birth. Synthetic helpers explicitly supply the same geometry hook as the real allocator.
