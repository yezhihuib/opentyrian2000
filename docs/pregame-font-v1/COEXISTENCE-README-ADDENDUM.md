# Final bilingual README review addendum

2026-10-13 UTC. **PASS.** The tested coexistence checkpoint is `3cdd398497515e17d99dd21ac1b31c6b8bc964c8`. Its production, asset and MSVC bytes remain unchanged in the following documentation-only revision.

The two stale English/Chinese coverage sentences now accurately describe text-only support for the ordinary single-player pre-game root and Upgrade Ship category. They retain unchanged purchase pages and original ship/background artwork. No admission or runtime claim is expanded. The only test-data change adds exact before/after reversals for those README edits.

Frozen reviewed hashes:

- README.md: `5f1f8cf4f004c60d3c8110f74875c3ee7ca1d11e987239da92d72dfe869cd923`
- README.zh-CN.md: `c96b81734777e3e354661562976fc20e53e4e4541c44544452821fd047aab385`
- tests/pregame_font_source_projection.json: `349c3a45eed74155f30d1ceb1acf7d574935253a454da9add9088e44c697ef6a`

Independently rerun after freezing those bytes: pre-game source integration, coexistence, historical selector integration and C preservation all PASS. The final source check rejects 51 mutations across 17 exact projections; the 194 production, 159 asset-mutation and 27 old-art-reversion controls remain intact. Hashes stayed unchanged during all four checks. Evidence: the adjacent readme-*.json/log files and before/after hash lists.

The main independent review's forced Linux builds, exactly-once MSVC inventory, unchanged accepted resources and historical-native qualifications continue to apply. No new game or capture was run. Publication remains the sole integrator's decision.
