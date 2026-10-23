# NEWSHF Phase A — selected art, source only

> Latest selected artwork policy: [168 V4 finite soft-alpha revision](newshf168-v4-soft-alpha/README.md). The previous binary-alpha revision and its receipts remain historical, not overwritten.

> Current art/pose revision: [corrected physical selection](newshf-fine-v2-corrected-poses/README.md). Earlier unchanged-art/pose claims below describe historical integration only; the first-two167/168 artwork assignments were subsequently found mislabeled and corrected.

> Historical phase receipt. The separately opt-in actual compositor is now
> documented in [NEWSHF HD compositor](newshf-hd-compositor.md); the original
> limits and results below describe this earlier phase, not its successor.

This bounded freeze adds **nine editable PNGs**, not a runtime asset pack. It
selects the existing AI-generated **v1 bbox-fit** candidates for records 163,
167 and 168, following delegated art selection and deterministic Python
postprocessing. It does **not** claim exact original silhouettes, original
internal feature registration, or runtime acceptance.

## Authority and reuse

`authoring-inputs/enemies/newshf-phase-a/manifest.json` is a **local, bounded
source contract**, not an entry in any global asset registry. Each NEWSHF base
identity has exactly one editable PNG shared across levels. This means nine
independent poses, **not one image reused for all poses**, and not per-level
copies. Record 824 and other potential aliases are outside this contract: no
additional eligibility is implied.

| Record | egraphic / enemycycle pose order | PNG canvas | Logical size / anchor |
|---|---|---|---|
| 163 | 125, 123, 127 | 192 × 224 RGBA | 24 × 28 / (6, 7) |
| 167 | 3, 1, 5 | 192 × 224 RGBA | 24 × 28 / (6, 7) |
| 168 | 55, 17, 93 | 192 × 224 RGBA | 24 × 28 / (6, 7) |

Density is 8, giving canvas registration point (48, 56). This is the entity
origin, not a visual centroid. Original esize=1 assembly uses source offsets
0, 1, 19, 20. **Logical bank selector 10 resolves to `newshf.shp`; it is not
static `spriteSheet10`.** All three records have ani=1 and animate=0: their
three egraphic entries are selected through enemycycle, **not an automatic
three-frame animation**. No timer or animation sequence is introduced here.

The source identity/geometry is independently fixed in the validator: original
bank SHA-256 and size (33,543 bytes), original item-table SHA-256, and exact
77-byte record offsets/hashes. Original files were read privately to verify
these pins. No original game binaries or reference images are committed.
The default check validates the pinned contract, **not absent original bytes**;
`--game-data` additionally verifies those bytes when supplied privately.

## Art provenance and edits

The nine selected PNGs are direct byte copies of existing normalized artist
candidates, not newly regenerated artwork. `provenance.json` records AI raw
candidate SHA-256, original normalization-script SHA-256, crop/resize/paste
parameters, transforms and selected PNG SHA-256. These script/input hashes
identify the private normalization inputs; those inputs and scripts are not
bundled, so this is a verifiable output freeze, not a self-contained regeneration
kit. No private absolute paths, original reference pixels, or old logs are
included.

Normalization cleared alpha <128 to transparent black, retained RGB with alpha
255, split occupied column runs, cropped whole figures, and used Pillow NEAREST
axis scaling to fit the original bounding envelope on the fixed canvas. It
contains slight nonuniform scaling. No row warp or original-mask clipping was
used. Envelope alignment does not prove silhouette equality. The gray v1
candidate was selected instead of the inferior-envelope v2 alternatives; green
v1 bbox-fit was retained for both records. All nine selected poses were visually
inspected as candidate art, not in-game acceptance.

`art_sha256` and corresponding provenance output hashes are **mutable revision
pins**: an intentional art edit updates both and regenerates `report.json`.
They do not redefine the immutable bank/base/record/geometry identity. Changing
that identity requires a separately reviewed contract change, not an art edit.
The selected-art report is deterministic and has no timestamp or machine path.
It is a checked-in receipt, **not a runtime output or second editable master**.

## Read-only validation

Requires Python 3 and Pillow (no game installation for the default check):

```sh
python scripts/check_newshf_phase_a.py
python -m unittest discover -s tests -p test_newshf_phase_a.py -v
# Optional: point to privately supplied original game data (never copied).
python scripts/check_newshf_phase_a.py --game-data "$PRIVATE_GAME_DATA"
```

The validator writes only JSON to stdout, never into the source directory or
production paths. To intentionally refresh the checked-in receipt after an
approved art edit:

```sh
python scripts/check_newshf_phase_a.py > authoring-inputs/enemies/newshf-phase-a/report.json
```

Checks reject missing/duplicate/extra PNGs, noncanonical paths and symlinks,
source aliases, reordered/missing identities, duplicate JSON keys, malformed
metadata, changed source pins or geometry, changed unpinned art bytes,
duplicate decoded pose pixels even with different PNG encodings, non-RGBA or
wrong-size images, animated PNGs, nonbinary alpha, hidden transparent RGB and
provenance/hash drift. Tests copy only this tiny source bundle, never the game
or a full repository. They compare the saved report, exercise rejection paths,
and verify a deliberate RGB-only art edit can be repinned without changing
source identity. Focused tests are not whole-repository/runtime certification.

## Explicit exclusions

No HDA production output, assets/hd manifest entry, package inclusion,
compatibility/global registry update, renderer integration, gameplay/level/data
change, animation change, new ordinary/opt-in eligibility, game launch,
installation or publication. Any future runtime integration is a separate phase
requiring explicit scope and runtime validation. Existing fallback behavior is
untouched.
