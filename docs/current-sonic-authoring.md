# Current Sonic quadrants: two editable masters

Edit only `authoring-inputs/sonic-current/master-105.png` or `master-124.png`.
They are independent approved images, not vertical flips of one image.

- Master 105 is straight RGBA, 1254×1254. Fixed Lanczos resize to 96×96,
  pasted at (0,16) on a 96×112 transparent canvas, produces identity 80105.
  Its exact full-canvas horizontal mirror produces 80106.
- Master 124 is straight RGBA, 1310×1201. Fixed Lanczos resize to 96×88,
  pasted at (0,0), produces 80124. Its horizontal mirror produces 80125.
- Density 8, logical size 12×14 and anchor (0,0) stay fixed. No original mask,
  alpha threshold, recolor, crop or additional shape deformation is applied.
- Editing 105 updates only 105/106; editing 124 updates only 124/125. Current
  player heads, their alpha shadows and the eligible default-off enemy reuse
  path consume the same derived payload pins. Roles, source stamps, cache slots
  563–566, enemy eligibility and gameplay do not change.

The previous `assets/hd/artwork/player-sonic-quadrants-v1/` directory and old
packs remain frozen historical reproducibility evidence. Do not edit them or
manually edit generated PNG/HDA, payload pins or compatibility metadata.

## Stage and apply

After editing either master, prepare a candidate from the current selection:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
s = json.loads(Path('assets/hd/authoring/sonic-current.json').read_text())
s.pop('resources')
s['schema'] = 'opentyrian-current-sonic-candidate-v1'
s['version'] = 'sonic-edit-1'
for r in s['masters']:
    r['source_sha256'] = hashlib.sha256(Path(r['source_png']).read_bytes()).hexdigest()
Path('../sonic-candidate.json').write_text(json.dumps(s, indent=2)+'\n')
PY
python3 scripts/build_current_sonic.py stage --selection ../sonic-candidate.json --stage ../sonic-stage-1
python3 scripts/build_current_sonic.py apply --stage ../sonic-stage-1
python3 scripts/build_current_sonic.py check
```

Stage must be a new directory outside the checkout. It does not alter the
checkout. Apply rederives all outputs, binds current inputs/tools, rejects stale
or modified plans/bytes and rolls back handled write failures. It is not a
power-loss/process-crash transaction and does not undo a manual master edit.
After apply, rebuild the executable: player-shadow and enemy payload pins are
compiled into it. Export a fresh current preview as below; mixing an old binary
with edited assets correctly fails closed.

Keep source edits in version control. An edited but unapplied master correctly
blocks unrelated current workflows until it is applied or restored.

## Preview and packaging boundary

Use the existing current preview/debug view, not the frozen pack itself:

```sh
python3 scripts/build_current_craft267.py view --kind preview --output ../sonic-preview-1
python3 scripts/shared_asset_authoring_map.py --id 80106 --format json
```

The current overlay contains 178 resources. The formal runtime package now
includes the four current Sonic HDA resources in its `gameplay` group, increasing
its explicit destination count from 1025 to 1029. The 120-entry global registry
is unchanged. The finite P02/P04 atomic family has all six required resources
(105/106/124/125 plus the existing 20/21) in that formal package.

After a master edit, stage/apply regenerates the runtime manifest with the new
pair's transport hashes. Export a new runtime with `scripts/package_runtime.py`
and rebuild the executable for its new payload pins. The default/current
package path requires the complete, rederived quartet; missing, stale or forged
current Sonic inputs are rejected. Explicit historical/custom manifests without
current Sonic references retain their original generic semantics.

Packaging these resources does not enable the default-off enemy renderer or
change gameplay. See [runtime closure](current-sonic-runtime-package.md) for the
exact package change and verification scope.

Bootstrap output is byte-identical to the previously approved four PNG/HDA
files. Synthetic edit tests establish propagation and renderer compatibility,
not visual approval of future edits. Native tests, assisted original-event
captures and natural campaign/Windows/GPU acceptance are separate evidence.

The accompanying validation JSON is the frozen Sonic migration receipt, whose
1025-destination package boundary predates the later four-resource addition. Its
Front fixture failures describe the public baseline at that stage. A subsequent
test-only repair updates the exact inverse order and complete fixture inputs;
the integrated Front boundary suite passes 11 tests, including six rejected
shadow mutants, and the separate frontend-history support suite passes seven.
That repair changes no production code, source-authority helper or historical
ledger. It does not replace the Sonic native or artwork validation above.
