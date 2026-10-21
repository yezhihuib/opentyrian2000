# Pulse5 focused reconstruction tests

The harness includes current production Pulse/Talon/Shield owners, actual player_shot_create, and original primitive/pixel/root/fade functions. SDL, diagnostic hooks and unrelated families are bounded shims. Actual engine integration is tested separately. Original source shapes, palette and three complete weapon-table variants arrive on stdin and are never persisted.

Coverage includes all 11 records, every used multiposition, 1P/2P, 4x/8x; original allocator power/bounds/capacity exits and zero-graphic slot reuse; born-on/off envelopes and post-birth equipment changes; complete 80-byte weapon and 82-byte port mutations, runtime name terminator; all five RGBA payloads, native-position anchor metadata and indexed-palette shadow analogue; source/role/operator/geometry negatives cold/warm; resource corruption; observed exact indexed write transactions; ordering and equal-index writes; source/lease/palette/table invalidation with zero remaining owner pixels after another RGB consumer; fade, reset and next-frame restoration.

All images retain their original positions and authored bytes. Resource59's -1 header anchor is validated metadata, not a translation of the native head/shadow rectangle. HUD copied-contribution behavior is modeled here only as removed owner bits; native tests must exercise actual glyph composition.

Regression shims for the preexisting Talon/Shield/HUD suites disable Pulse only, leaving their prior assertions intact. Those isolated suites are not proof of enabled cross-family integration.
