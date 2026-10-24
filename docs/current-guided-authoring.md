# Current Guided: four independently editable static identities

Edit the four straight-RGBA PNG masters in `authoring-inputs/guided-current/`.
These are **four separate static identities**, not animation frames or mirrored
variants. No new design is introduced by this migration.

| Master | Source pixels | Fixed crop | Resize | Canvas position | Identity |
| --- | --- | --- | --- | --- | --- |
| `master-19.png` | 1160×1355 | 74,180,1086,1173 | 82×82 | 7,15 | 80019 |
| `master-171.png` | 1160×1355 | 160,260,1001,1098 | 82×82 | 7,15 | 80171 |
| `master-20.png` | 1060×1484 | 99,151,956,1352 | 46×62 | 29,29 | 80020 |
| `master-21.png` | 938×1677 | 130,116,811,1589 | 44×76 | 30,22 | 80021 |

The recipe is fixed, non-executable data: crop, Pillow Lanczos resize, then paste
without a mask into a transparent 96×112 canvas. Density 8, logical 12×14,
anchor (0,0), straight alpha, original source eligibility and gameplay remain
unchanged. No new alpha threshold or original-art mask is applied. Editing one
master changes only its own identity. Identity 22 is outside this family.

`assets/hd/artwork/guided-bomb-family-v1/`, its original exporter and historical
packs remain frozen. Do not edit them or the generated current PNG/HDA files.
The four bootstrap PNG hashes equal the original candidate manifest; the HDA
files are byte-identical to the existing historical pack resources.

## Edit, stage, apply

After editing one or more masters, prepare a candidate from the installed
selection (run in the existing checkout):

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
s = json.loads(Path('assets/hd/authoring/guided-current.json').read_text())
s.pop('resources')
s['schema'] = 'opentyrian-current-guided-candidate-v1'
s['version'] = 'guided-edit-1'
for r in s['masters']:
    r['source_sha256'] = hashlib.sha256(Path(r['source_png']).read_bytes()).hexdigest()
Path('../guided-candidate.json').write_text(json.dumps(s, indent=2)+'\n')
PY
python3 scripts/build_current_guided.py stage --selection ../guided-candidate.json --stage ../guided-stage-1
python3 scripts/build_current_guided.py apply --stage ../guided-stage-1
python3 scripts/build_current_guided.py check
```

Stage must be a new directory outside the checkout. Stage does not change the
checkout. Apply rederives the full finite output set and verifies the complete
input fingerprint, staged plan and bytes before writing. It rejects stale
masters, tools, plans, path escapes and symlinks. Handled write errors roll back;
this is **not** a process-crash/power-loss transaction and does not undo the
user's prior master edits. Keep those edits in version control.

An unapplied master correctly blocks unrelated current workflows until applied
or restored. Rebuild the executable after applying 20/21 edits: only their
already-existing enemy P04 payload pins are compiled in the new generated
header. Player slots 326–329 keep their original loader semantics; this change
adds no player payload-hash restriction.

## Current preview and runtime consumers

```sh
python3 scripts/build_current_craft267.py view --kind preview --output ../guided-preview-1
python3 scripts/shared_asset_authoring_map.py --id 80020 --format json
```

The current preview overlay has 182 entries (four Guided replacements of old
preview destinations, not four additional file names). The runtime package
still has **1029 destinations**: only the sources and revision labels of the
four existing Guided rows migrate to current authoring. The 120-entry global
registry does not change. Original resources retain their bytes.

The package's current Guided reference requires all four canonical, rederived
transports and their selected input closure. Missing, stale, tampered or forged
current inputs are rejected. Explicit historical/custom manifests without
current Guided references retain their existing generic semantics.

Player and eligible enemy reuse consume the same derived 20/21 transport pixels.
The existing P02/P04 atomic family remains Sonic 105/106/124/125 plus Guided
20/21. Role 146, original source stamps, weapon/level conditions and the enemy
renderer’s default-off status do not change. 19/171 are player-only in this map.
Packaging does not enable the renderer or establish natural visibility.

Synthetic edits validate dependency propagation, not artistic approval. Build,
unit/native harness, original-event playback and human Windows/GPU visual
acceptance are separate evidence; see the accompanying validation receipt for
what was actually run in this batch.
