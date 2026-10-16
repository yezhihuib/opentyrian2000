# Plasma Storm9 art-only export

Generated-only reproducible master and three simultaneous pieces, not animation. Original logical geometry62x24/65x28/62x23, anchors0,0 and weapon offsets(-32,-24)/(-32,0)/(-32,28) are preserved.

Run `python3 rebuild.py --output /absolute/new-directory`. All density4/8 PNG/RGBA hashes are checked against contract.json. To wrap HDA, pass `--resource-ids ID22 ID23 ID24` using IDs chosen explicitly by the integrating renderer. HDA header uses HDR1 plus six little-endian uint32 values (resource ID, density, width, height, anchor x, anchor y); no namespace is guessed here.

Art-stage PASS only. This basis was provisionally accepted for isolated actual-runtime tests. Original indexed writes/collision/gameplay remain authoritative, and original warm hue/value blend behavior must not silently become generic alpha-over. Integration, original-source/palette/context guards, owner handling, missing/corrupt-art fallback, clipping, ordering and stale-residue need separate exact-production/runtime qualification.

This export contains the new generated master, exact prompt and deterministic recipe, not original pixels, decoded source indices, masks, palette, private captures or audit data.
