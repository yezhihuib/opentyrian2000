# Terrain completion resource candidates

38 8x HDR1 tiles and byte-equivalent PNG previews, built from the seven generated
masters. IDs, source geometry hashes, build versions and resource hashes are in
MANIFEST.json. Native data is caller-owned and not included.

NEIGHBOR-AUDIT.json validates complete candidate payloads and source alpha, then
reports stored-map neighbor measurements. It is not gameplay or seam acceptance.
The producer does not enable runtime integration. Any opt-in adapter is a
separate candidate with separate validation.

See `docs/level2-family/TERRAIN-COMPLETION-CANDIDATE.md` for the full receipt,
known visual differences and reproducible regression commands.
