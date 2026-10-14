# Enemy tank-shell pair

Two frozen generated PNGs, enemy bank 8 IDs 146/147 only: role 122, slots 505/506,
keys 1220146/1220147. Each is 96×112 RGBA at density 8, logical 12×14, anchor (0,0).
146 stays down and 147 down-right, regardless of actor facing or velocity.
Enemy records 15/194/195 share weapons 2/3/6/7; player and independent newsh6
explosion146/147 paths remain unchanged. Runtime coverage of 194/195 is not claimed.

Both members must validate together. Missing, malformed, changed or density 4-only
shell resources decline the pair. The startup cache is independent of other families.
Approved fractional-alpha edges are preserved, including samples beyond the old
binary support; the two canonical PNGs and all HDR1 pixels are unchanged.

## Reproduce the shipped resources

From the repository root with Python3 and Pillow:

    python3 prototype/build-enemy-tank-shell-pair-art.py
    python3 prototype/test-enemy-tank-shell-pair.py --source-only

The builder verifies every inventory member, both selected pack registrations,
and exact HDR1 reconstruction in memory. Add --out DIR to write only the two
wrappers to a new external directory. It does not recreate or resample artwork.
The canonical PNGs in source/ are the complete required inputs for that operation.

Finite extracted-production ASan/UBSan units require separate original game data:

    python3 prototype/test-enemy-tank-shell-pair.py --out RESULT_DIR \
      --original-data TYRIAN_DATA_DIR

RESULT_DIR must be new and outside the repository. Original data and SDL build
dependencies are not supplied. The complete source inverse requires baseline Git
object 916b7aa. The unit command does not launch the game or take native captures.

proof/ contains publication-safe technical derivatives, not original reference
pixels or a copy of the private art package. See proof/frozen-README.md for the
bounded reproducibility contract, and [validation](../../../../docs/enemy-tank-shell-pair-v1/VALIDATION.md)
for runtime evidence, failed-attempt accounting and limits.
