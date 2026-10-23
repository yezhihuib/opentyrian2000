# Enemy orb112/113: fixed-approved-revision shared-source binding

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
