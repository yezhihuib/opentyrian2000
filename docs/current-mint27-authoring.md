# Current Mint27 single-master authoring

Mint27 is the existing player/sidekick projectile identity `80027`, density 8,
logical size 12×14, anchor (0,0), source slot 535. It is **not** the bank-9 Mint
sidekick body. This workflow changes the editable source and its generated
transport, not weapon eligibility, shot logic, collision, source sprite hash,
shadow blend or default rendering flags.

## Edit once

The canonical editable source is `authoring-inputs/mint27-current/master-27.png`.
It is the selected 1312×1199 straight RGBA generated revision-3 master, copied
without repainting. The fixed recipe crops `[339,139,966,1041]`, resizes to 40×72
with Pillow LANCZOS, then alpha-composites at (32,32) onto a transparent 96×112
canvas. The alpha-composite operation is intentional: it exactly reproduces the
selected original recipe, including its transparent RGB semantics. There is no
alpha threshold, recolor, silhouette mask or inferred animation.

The initial generated PNG, RGBA payload and HDA are byte-for-byte identical to
`assets/hd/artwork/player-mint27-one-v1/output/`. The old artwork, contract,
reproducer and historical test evidence are not edited or repinned.

After editing the canonical master, prepare a candidate JSON with schema
`opentyrian-current-mint27-candidate-v1`, a descriptive version, the single
selector 27 master entry and its actual SHA256, and the unchanged recipe entry
and SHA256. Use the installed `assets/hd/authoring/mint27-current.json` as the
shape, remove `resources`, and change only its schema/version/master SHA.

Run from the repository (stage path must be outside it and new):

```sh
python scripts/build_current_mint27.py stage --selection /outside/candidate.json --stage /outside/mint27-stage
python scripts/build_current_mint27.py apply --stage /outside/mint27-stage
python scripts/build_current_mint27.py check
```

Stage does not modify the repository. Apply rederives the exact finite outputs,
checks the staged plan and all captured input fingerprints, and rolls back
handled write failures. This is not a power-loss or process-crash atomicity
claim. A stale plan must be restaged; do not edit staged bytes or disable checks.

## Runtime contract

The one existing destination remains `assets/gameplay/bullet-27-8.hda`; only its
source becomes `assets/hd/current-compat/mint27/bullet-27-8.hda`. The formal
runtime still has 1029 rows and the global registry still has 120 resources.
Player and sidekick eligibility still use the original source hash
`0xd25ba01692cfa4b7` and slot 535. The existing shadow table's payload value is
now generated as `CURRENT_MINT27_80027_D8_PAYLOAD_FNV` in
`src/current_mint27_payload_pins.h`; bootstrap remains `0xe75bfc31a0616e75`.
No new payload gate is added to the player path.

`shared_asset_authoring_map.py` presents the actual canonical master and recipe.
Other builders include the finite Mint27 closure so edits in one family do not
silently stale another family's scratch rebuild. Packaging revalidates the
current master-derived HDA and requires exactly the current Mint27 row, rejecting
missing, extra marked or stale current rows. Explicit historical manifests that
contain no current Mint27 contract retain their prior generic semantics.

## Verification boundaries

Synthetic edit tests establish source propagation and runtime packaging, not
approval of a new artistic appearance. Linux/Windows *asset-layout* exports do
not constitute Windows executable tests. Native renderer receipts describe
only their executed harness paths, not natural campaign or physical-GPU QA.
Historical receipts remain historical; new finite inverse tests undo only this
reviewed include/payload-macro extraction and one runtime-source migration,
without rewriting old source pins or admitting unrelated differences.
