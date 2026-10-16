# Rear Multi-Cannon P3 mode 1 two-lobe components

This integration packages source identities 2 and40 for the finite player 1 rear 10
power 3 mode 1 record 256 birth path. Both source and full weapon-record identities
are checked independently from the generated resource identity. See
`docs/rear-multicannon-p3-mode1-reuse-v1/VALIDATION.md` for qualification and limits.

The unchanged `components/` directory preserves the independently reviewed,
generated-only proposal snapshot. Its README describes the original preview
stage; `binding.json` describes this later production integration. All accepted
R2 component inputs remain in `../player-rear-multicannon-p1-six-v1`. No new
artwork generation or editing was performed. No original masks, palettes,
extracted sprites, game data or screenshots are included.

Logical canvas 12×14 and anchor (0,0) are unchanged. ID2 combines accepted ID1
translated by −2 rows and its whole-canvas flipY translated by +2. ID40 combines
flipY of accepted ID39 translated by −4 and unchanged ID39 translated by +4.
Supports do not overlap or clip. Both retain the transparent central strip
y∈[6,8), two distinct lobes, the full-density component alpha and RGB bytes.
Inherited accepted HD curves differ from the original pixel mask within the
same bounds. Native nearest reflection can change the sampled subpixel phase;
no brightness correction is applied. Density 4 and 8 are independently derived
from the matching accepted density, never downsampled from each other.

Rebuild the immutable proposals using Python3 standard library:

    python3 components/build_composites.py ../player-rear-multicannon-p1-six-v1 NEW_ART_OUTPUT

Rebuild the four HDR1 wrappers from their pinned RGBA payloads:

    python3 pack-hda.py NEW_HDA_OUTPUT

The established role 131 filename prefix is retained for loader compatibility.
Keys are 1310002 and 1310040. `binding-map.json` explicitly associates identities,
densities, keys and filenames; `binding.json` records all payload and pack hashes.
The existing six accepted head resources remain byte-for-byte unchanged.
