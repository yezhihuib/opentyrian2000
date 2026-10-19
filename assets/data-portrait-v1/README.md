# Source-authenticated HD Data portraits

All18 parent-approved newly painted portraits retain their exact original native
geometry and canonical4x size. Intentionally absent portraits stay absent.
FACE7's approved v3 PNG and DPR1 remain byte-identical to the accepted pilot.
This directory retains only selected approved PNGs, exact packed resources,
full source identities, generation prompts and separate rights notices. Original
game data, native-reference images and generated masters remain external.

Rebuild: `python3 scripts/export_data_portrait.py` (Python/Pillow).
Runtime: `--data-portrait-assets=/absolute/path/to/assets/data-portrait-v1`.
The18 `face00-v1.hda` through `face17-v1.hda` files plus the two notices are the
runtime selection. Missing/corrupt entries fall back individually.
See `docs/data-portrait-hd.md` for bounded authentication, alpha and ownership.
