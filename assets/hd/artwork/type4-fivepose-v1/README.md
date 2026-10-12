# Type4 compact craft five-pose family v1

Root approved the final v3 native2x pilot after original-source red-timing audit. Actual full-cycle review remains pending. This is the compact brown/gray craft, not the long brown newsh4 structure.

Five complete24x28 composites use newsh2 bases159/161/163/165/167, each consisting of original12x14 cells at offsets0,1,19,20. Each HD output is192x224, density8, anchor6,7. HDA header is HDR1 plus six little-endian uint32 fields1010000+base,8,24,28,6,7, followed by RGBA. Do not independently crop, recenter, or map one quadrant as an entire pose. Original call-order/clipping stays intact.

The exact20-step source cycle is159,159,161,161,163,163,165,165,167,167,165,165,163,163,161,161,159,159,159,159. All five sources were inspected and authored together. It is mechanical side extension/retraction with stable body orientation, not a five-angle rotation. No3D model used.

Rebuild with Python3+Pillow into a nonexistent directory:

python rebuild.py /absolute/new/output

Canonical Pillow12.3.0. Source master resized768x640 with Lanczos, crops pinned per entry. Generated antialiasing is composited over original dark-outline RGB12,12,12 before applying exact binary original RLE occupancy masks. This prevents hidden transparentRGB fringes becoming visible when opaque source support is restored. Explicit written palette0 remains occupied; RLE skips are transparent. Both source decoder and independent worker matched original RGBA for all5 poses.

Original RGB/game data is not needed to rebuild. Input hashes and exact decodedRGBA/HDA output hashes are enforced. Independent separate-directory rebuild and canonicalPNG comparison pass. PNG metadata may vary by encoder.

Red audit:159/161 have no red;163 has only tiny subdued dark-red tip slits, matching source timing.165/167 expose progressively larger areas. Selected generated red area is smaller than source; some subpixel peak channels exceed source, accepted by root at native scale. See proof/red-audit.json. V1 bright gold and V2 excessive red were rejected; only frozen v3 master is selected.

Lifecycle constraints: same-pose palette hurt tint, no separate hurt/shadow art, shared mapped ground-death effects unchanged. Default drop0 does not authorize removing arcade event45 assignments. Preserve original enemy state, damage, movement, cycle and drops. Existing exact source/proof/first-full-reference evidence is under proof; actual full-cycle normal-layer/private-survival comparison, hurt/fallback checks and author review remain required before publication. No Windows or full-level acceptance claim.
