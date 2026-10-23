# Enemy orb112/113: current two-contract authoring

Each identity now has **one current editable RGBA8 PNG**:

- `authoring-inputs/enemy-orb-current/orb-112.png`
- `authoring-inputs/enemy-orb-current/orb-113.png`

`assets/hd/authoring/enemy-orb-current.json` binds their exact hashes. The two
masters are independent; editing 112 never changes 113. Both remain 96×112.
Each master derives **both** contracts without resizing:

| Contract | IDs | Geometry | Current destination |
| --- | --- | --- | --- |
| Ordinary role8 | 80112, 80113 | full RGBA soft edge | `bullet-{112,113}-8.hda` |
| Opt-in ASTEROID1 role142 | 1420112, 1420113 | RGBA preserved within fixed 45-cell mask, zero outside | `enemy-orb112113-{112,113}-8.hda` |

Both use logical 12×14, density8 and anchor(0,0). The mask was derived from the
already-public approved opt-in PNGs and compared exactly to the authenticated
original-bank decoder. Its fixed 168-bit policy is compiled into the compatibility
script, not editable art. Builds require no original game data. Every occupied
mask cell must retain nonzero alpha somewhere. The initial four HDA files are
byte-identical to the frozen approved outputs. Original data is never copied.

## Edit, stage, apply, check

Edit a master, update its SHA256 in a separate candidate JSON with schema
`opentyrian-current-enemy-orb-candidate-v1`, and retain exactly `schema`, `version`,
and the two ordered `masters` records (`selector`, `source_png`, `source_sha256`).
The master paths are fixed as above; there are no retained-file fallbacks.

```sh
python scripts/build_current_enemy_orb.py stage --selection /external/candidate.json --stage /external/new-orb-stage
python scripts/build_current_enemy_orb.py apply --stage /external/new-orb-stage
python scripts/build_current_enemy_orb.py check
python scripts/build_current_craft267.py view --kind enemy-orb-contracts --output /external/new-orb-transports
python tests/test_current_enemy_orb_authoring.py
```

Stage writes only a new external stage directory. Apply re-derives all four
outputs, verifies the complete plan, input hashes, and staged bytes before any
write, then rolls back handled write failures. This is not crash/power-loss
atomicity. Source changes after staging require explicit restaging. Unrelated
source authority, global header and legacy payload pins are checked before
rebinding the current source inventory. The ordinary renderer has no existing
orb payload pins; only the two existing role142 constants were extracted into
`src/current_enemy_orb_payload_pins.h`, initially with exactly the same values.
No role, density, registration, renderer-mode eligibility or gameplay changed.

Default packaging still includes only the ordinary pair. Existing preview/debug
views overlay the current ordinary pair. `enemy-orb-contracts` explicitly exports
all four current transports to a separate directory; it does **not** enable
ASTEROID1 or modify a historical pack. Explicit current package selections that
include role142 must include its complete pair plus the ordinary pair, all from
the same current selection. No global registry entries are added.

The original approved PNGs, selected manifest, retained PNGs, packs, artwork
inventories and historical receipts remain frozen. The old commands below still
reproduce the fixed approved revision, not current edits. Current authoring
checks are build/package consistency, not fresh visual/native/Windows/full-game
acceptance.

## Historical fixed-approved-revision binding (unchanged)

This is **固定批准版本共源绑定**, not a current-art selector or automatic
publication of arbitrary new artwork. Both routes now select the same approved
PNGs through `assets/hd/artwork/enemy-orb112-113-v1/selected-manifest.json`:

- 112: `assets/hd/source/bullet-112-8-22e2be2903bc.png`, SHA256
  `c28da6740c5827bab6e2ab44faf0e5218fb8f033af7c6bc500d80167cf47405b`;
- 113: `assets/hd/source/bullet-113-8-185ae48dcc14.png`, SHA256
  `49a4ef3fe0c25cb5cabe153a83d4cf72fc204c45872af83178521d33a902d412`.

The ordinary reproducer already reads this selection. The ASTEROID1 compiler
now validates both entries, unique integer selectors, source paths without link
components, source hashes and geometry **before creating any output**. Missing,
corrupt or differently approved sources fail; it never falls back to retained
copies. Source changes plus a recomputed manifest hash are not new approval:
the fixed compiler pins still reject them.

## Two intentional output contracts

Both retain logical size12×14, density8 and anchor(0,0). Ordinary role8 outputs
80112/80113 keep the complete soft edge. Separate ASTEROID1 role142 outputs
1420112/1420113 preserve RGBA within the original45-cell support and zero RGBA
outside it. The two HDA pairs are not interchangeable or duplicate outputs.
The original-bank decoder and all production C/runtime pins remain unchanged.

The runtime manifest still contains1006 files, including the ordinary two and
excluding these two opt-in outputs. These orbs are not in the120-entry global
registry. No pack, selected manifest, PNG, HDA, production source, runtime
mapping or historical acceptance receipt is changed by this binding.

## Reproduce and verify

Use directories outside the checkout; fresh directories are recommended for
separate evidence. The ASTEROID1 compiler also retains its existing external
directory behavior: rebuild its named outputs without deleting unrelated files.
Source preflight failure leaves an existing output directory unchanged.
No command installs a new selection:

```sh
python prototype/build-enemy-orb-art.py --output /external/new-normal-orbs
python prototype/build-asteroid1-orb112113-art.py --data ORIGINAL_DATA --out /external/new-asteroid-orbs
python tests/test_enemy_orb_shared_source.py
python tests/test_asteroid1_orb112113_art.py --data ORIGINAL_DATA --out /external/new-original-data-check
```

Original game data remains external and is needed only by the second and fourth
commands. The data-free unit test derives a mask from the **approved public
opt-in output** to verify deterministic RGBA/PNG/HDA equivalence. Its synthetic
CLI test does not authenticate the original bank or RLE. It is not new native,
visual, Windows or full-game acceptance. Link rejection has a mocked unit check,
not an operating-system symlink/junction acceptance claim.

The compiler preserves the legacy `art-inventory.json` schema and values when
built with the authenticated original bank. Its `retained_source_sha256` is the
historical byte pin, not a claim that the retained file was read. A separate
`source-binding.json` in that **explicit external output directory only** records the
actual selected-manifest hash, source paths and fixed hashes used by this build.
Historical `retained-source-*.png`, `art-inventory.json`, `provenance.json`, packs,
catalogs and acceptance records remain untouched evidence; do not update them
to manufacture a new history. Retained copies are no longer editable inputs or
build dependencies. A future art revision still requires a separately designed
approval/pin/publication workflow for both contracts; this change adds none.
