# NEWSHF 169 shared dual-missile artwork

The editable source is `single-master.png`, a 96 x 224 RGBA bitmap representing
one 12 x 28 original missile at density 8. The builder copies the same bitmap
twice without reflection, giving one 192 x 224 RGBA resource for the two distinct
native records 2 and 500. Editing one source updates both halves and both records.

`native-mask.png` is immutable original support, not an editable image. Smooth
alpha is preserved inside that mask; all nonzero alpha outside it is rejected.
Transparent RGB is normalized by alpha composition. The game canvas, bank,
quartet, anchor, original white-smoke effects and gameplay behavior are unchanged.

`raw/` preserves the original built-in image_gen output, exact prompt and original
registration script as provenance. That script records the draft workspace layout;
the current build entry point does not depend on its old paths. `registration.json`
records the reviewed crop/scale/placement used to prepare the editable master.
Subsequent explicitly selected master edits use the fixed native support contract.

Generated raw image: exec-d9446def-54b2-4862-ab95-9cebc4b2b457.png, 2026-10-26,
using built-in image_gen with transparent background. Parent-reviewed candidate,
not independent user visual acceptance. Runtime qualification is reported separately.

Build through `scripts/build_current_dualmissile_newshf.py` stage/apply. A stage is
non-mutating and apply rederives all outputs, checks source hashes and staged bytes,
then uses the shared rollback-capable finite replacement helper. Handled errors roll
back; process or power loss is not transactional. No original game files are needed
to rebuild selected art. Runtime density 8 only; density 4 retains classic fallback.
