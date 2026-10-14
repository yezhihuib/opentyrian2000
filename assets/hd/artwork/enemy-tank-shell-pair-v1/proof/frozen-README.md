# Frozen artwork provenance summary

This is a derivative summary of the private art-only freeze dated 2026-10-13.
The two canonical generated PNGs are shipped in ../source/ and unchanged.
Full original reference pixels, generated masters, prompts, rejected variants,
terrain-composite previews and the historical reconstruction script stay separate.
This package does not claim those omitted inputs can be reconstructed from hashes.

Both PNGs are 96×112 straight-alpha RGBA, density 8 over 12×14 with anchor (0,0).
146 stays down;147 stays down-right. Only the accepted two designs are present.
Their smooth authored alpha extends beyond the old binary support at some samples;
no original-alpha clipping or source-mask equivalence is claimed. Aggregate
canonical8 support and centroid measurements are in frozen-art-contract.json.

The repository's prototype/build-enemy-tank-shell-pair-art.py validates the frozen
PNG/RGBA hashes and reconstructs both exact HDR1 wrappers in memory. Optional
--out DIR writes only those wrappers to a new directory. It does not regenerate
or resample the artwork. The existing renderer uses integer straight-alpha blend
and nearest output sampling:8 → 2 selects 2, 6, 10,…;8 → 4 selects 1, 3, 5,… .

Historical direct-master Lanczos pilots differ from renderer-nearest previews.
Terrain-composite approval is art evidence, not current game output. The bounded
actual-frame result is documented separately in docs/enemy-tank-shell-pair-v1.
