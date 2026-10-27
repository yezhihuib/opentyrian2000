# Shared NEWSHF scout 164: three-pose HD authoring

Three independently generated silver-grey, nose-down aircraft poses, registered to the original 24×28 support masks at 8× density (192×224 RGBA). Base 11 is straight; bases 9 and 13 are opposite banks. The body contains no projectile, engine flame, glow or cast shadow.

## Rebuild

Run `python3 rebuild.py` in this directory with Python, Pillow, NumPy and SciPy. The recipe uses each selected raw PNG and the corresponding 24×28 native mask. It crops the alpha >32 support extent, registers to the original support bounding box with Lanczos resampling, applies a conservative inward-rounded alpha mask, sets every native-zero cell to exact RGBA zero and removes disconnected alpha dust. It does not paint new artwork, mirror poses or synthesize banking from one master. All visible artwork originates in the recorded image-generation outputs.

`master-base11.png`, `master-base9.png` and `master-base13.png` are the production candidates. `preview-4x.png` and `preview-8x.png` show bases 9, 11, 13 left to right on a dark background. The generated alpha is preserved except for deterministic registration, inward support masking and disconnected-dust removal. Uncovered occupied native cells intentionally have alpha zero and require the already-qualified underlying-scene restoration path; this is not a native transparent-cell expansion.

The first banking generation had strongly diagonal wing spans that could not fit the source footprint without clipping. It was revised through a second independent image-generation edit to bring the wing tips closer to level. The selected v2 banking outputs use global registration; an experimental landmark warp was rejected and is not part of the recipe. Rejected trials remain private and are excluded from the publishable allowlist.

## Coverage limits

Natural source audit observed base 11 in E1 physical level 8; opposite-bank diagnostics must be explicitly controlled unless later natural evidence is obtained. This authoring package alone does not assert runtime qualification, Windows acceptance or full-campaign coverage.

Public provenance uses relative artifact names and hashes only. Private tool-return paths and generation transport traces are excluded.
