# Current Protron: one editable master

Edit **`authoring-inputs/protron-current/master.png` only** (straight RGBA PNG,
2011×782). Do not edit the frozen historical master, generated PNG/HDA, pins,
coverage masks, runtime manifest, or old P09 evidence. This migration changes no
bootstrap pixels and adds no weapon, level, family, role, density, or player227
eligibility.

The fixed `recipe.json` declares three non-overlapping source cells:

| cell | crop xyxy | consumers |
|---|---|---|
|225|187,272,458,544|player225|
|244|651,38,1373,762|player244, eligible enemy244, private P09 enemy227|
|226|1498,234,1839,569|player226, eligible enemy226|

227 is resized directly from raw cell244, not from the masked player244 output.
Its straight soft alpha is preserved without thresholding. The three player
outputs retain the frozen original support-mask algorithm. Their separate
role125 source-coverage resources remain untouched. The historical artwork
folder and P09 builder are frozen reproducibility evidence, not editing entry
points.

After editing, create a candidate with the current master hash (run at repo root):

```sh
python - <<'PY'
import hashlib, json
from pathlib import Path
s=json.loads(Path('assets/hd/authoring/protron-current.json').read_text())
s.pop('resources')
s['schema']='opentyrian-current-protron-candidate-v1'
s['version']='protron-edit-1'
s['master']['source_sha256']=hashlib.sha256(Path(s['master']['source_png']).read_bytes()).hexdigest()
Path('../protron-candidate.json').write_text(json.dumps(s,indent=2)+'\n')
PY
python scripts/build_current_protron.py stage --selection ../protron-candidate.json --stage ../protron-stage-1
python scripts/build_current_protron.py apply --stage ../protron-stage-1
python scripts/build_current_protron.py check
```

Stage directories must be new and outside the checkout. Stage is read-only with
respect to the checkout. Apply rederives every output, checks the complete input
fingerprints and staged bytes, preflights paths, and rolls back handled write
failures. This rollback covers generated outputs only: it does not undo your
manual master edit. Keep a source backup or use version control to discard an
unwanted edit. It is **not a power-loss/process-crash transaction**. If inputs change
after staging, restage explicitly. During an unapplied edit, unrelated workflows
correctly reject the stale installed selection; apply Protron before continuing.

The four HDA destinations are unchanged; the registry remains 120 entries and
runtime package remains 1025 destinations. Only their source binding moves to
`assets/hd/current-compat/protron/`. The normal current-art preview includes the
three player outputs; private227 remains in the isolated P09 runtime route.
Historical validation receipts do not qualify future artwork. A new visual edit
still needs appropriate visual/runtime review; authoring checks establish
source-to-consumer consistency, not new gameplay/platform acceptance.
