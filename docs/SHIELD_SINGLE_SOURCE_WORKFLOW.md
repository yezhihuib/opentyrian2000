# Shield-hit authoring: one selected source per phase

The `shield` profile covers 22 existing player shield-hit resources: NEWSH6
indices 229–237, 248–250, 252–256, 267–269, 272 and 275 (identity 1060000 +
index). It does not include the unrelated SHOP shield material or HUD shield bar.
The five authenticated native-empty phases 251, 270, 271, 273 and 274 have no
resource and cannot be added through a selector.

`assets/hd/authoring/shield-current.json` selects the exact approved source PNGs.
This initial migration changes neither pixels nor gameplay. Every source is
single-frame 96×112 straight RGBA, logical 12×14 at density 8, anchor 0,0.
Phase268 must remain fully transparent; the builder rejects any nonzero alpha.
Its original tile is not empty. Phases267/268/269 retain distinct semantic IDs,
regardless of equal original source fingerprints or selected pixel bytes.

## Updating a selected version

Create new source files without overwriting historical artwork. Copy the selector
into an external draft and update its version, source paths and SHA-256 hashes.
Do not directly edit the installed selector: installed families are drift-checked.

```sh
python scripts/build_current_art.py --family shield stage \
  --selection /tmp/shield-draft.json --stage /tmp/shield-review
# Review plan.json and staged files.
python scripts/build_current_art.py --family shield apply --stage /tmp/shield-review
python scripts/build_current_art.py --family shield check
```

Stage must be outside the repository. Apply checks source authority, all selected
families, old hashes, staged bytes and temporary-file collisions before writing.
It uses per-file atomic replacement, not a crash-safe multi-file transaction.
After interruption, inspect the state and restage explicitly.

The shared builder updates the global content and generated registry pins,
`packaging/current-shield-compatibility.json`, and current legacy outputs at
`assets/hd/current-compat/shield/explosion-newsh6-<index>-8.hda`, together with
the current runtime manifest/source binding. The legacy package destination stays
`assets/gameplay/explosion-newsh6-<index>-8.hda`. Both paths consume the selected
pixels. There are no separate legacy Shield payload macros to update.

Historical packs, historical manifests and old global content remain untouched.
Source-bank fingerprints, birth/lifetime/role authority, phase order, empty-phase
semantics, original drawing and damage/audio behavior are not editable here.
Terrain/cloud migration and changing appearance are outside this batch.

`tests/test_current_shield_authoring.py` uses isolated diagnostic assets to prove
all22 propagation and rejection cases, including transparent268. These are not
production art edits or native gameplay acceptance. Native paired and package
verification are separate evidence; Linux software output does not imply Windows,
GPU, full-campaign or subjective audio acceptance.
