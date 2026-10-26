# Addendum: linked NEWSHF natural-run density correction

**This corrects the earlier natural 4× coverage claim; it does not rewrite its
historical receipts.** All six prior `linked171-game-qa/runs/{4,8}x-*` runs
actually used internal **density8**, including those labeled `4x`. Their
[original RGB audit logs](evidence/linked-density-correction-20261026/original-rgb-audits/4x-present.tsv)
record `density=8`; the [preserved commands](evidence/linked-density-correction-20261026/original-runs.json)
put `--global-assets` after `--render-test=4`.

The frozen parser processes options in order. `--global-assets` and
`--hud-assets` set density8. An explicit render mode must follow **all** such
options; the new reproduction driver places it last. No C/parser semantics,
production assets, old logs, or original validation documents were changed.

The former nominal4 captures were therefore additional 8× evidence, **not**
4× evidence. Their rendering/state checks still apply to effective8. The native
C harness's direct density4 tests remain valid. `--render-original-reference`
sets an independent boolean: prior reference cases remain **reference8**, not
non-reference cases. We have not newly run a reference4 case.

## Corrective evidence

A new bounded pair used the same qualified executable
`b2685e56936f042c7daf2c678de0bf26d95fb4bb3bc875937660596f57e3b1d2`,
the same immutable linked art, and the same original E1 physical-level12 route.
The final `--render-test=4` explicitly overrides earlier asset-implied density.
Both runs' actual RGB audits show **75 density4 rows, ticks106–180**.

- [Initial corrective run receipt](evidence/linked-density-correction-20261026/corrected-first/run-receipt.json)
- [Same-tick native-mask and state verification](evidence/linked-density-correction-20261026/corrected-first/visual-state-receipt.json)
- [Input byte hashes](evidence/linked-density-correction-20261026/corrected-first/input-before.json)
- [Actual present density log](evidence/linked-density-correction-20261026/corrected-first/present/rgb-audit.tsv)
- [Actual missing-art density log](evidence/linked-density-correction-20261026/corrected-first/missing/rgb-audit.tsv)

The pair has identical 181-row state/RNG (excluding output pixels), projectile,
collision, emission and presentation traces. Every Present preserves RNG.
All 875,253 changed **window** pixels are inside exact same-tick original
quartet masks. Natural bases are43/81/119/121: top/middle do not fire with the
bottom; base83 remains latent. Captures are native640×400 window output,
**not** 1280×800 or density4-sized raw renderer surfaces. The changed-pixel
count also equals the older density8 count, illustrating why count/filename
alone cannot prove internal density.

Natural4 acceptance is established by this new corrective run, not by the
old mislabeled runs. No Windows/GPU/full-campaign claim is added.

The final checked-in reproduction driver also completed a fresh full pair:
[receipt and capture hashes](evidence/linked-density-correction-20261026/final-driver/receipt.json),
[driver/test identity](evidence/linked-density-correction-20261026/final-driver/reproduction.json),
and actual [present](evidence/linked-density-correction-20261026/final-driver/present-rgb-audit.tsv) /
[missing](evidence/linked-density-correction-20261026/final-driver/missing-rgb-audit.tsv) density logs.
Seven focused regression tests passed.

## Canonical wrapper audit

The public7d wrappers do **not** contain this ordering bug:

| Entrypoint | Density control / finding |
| --- | --- |
| `prototype/run-controlled.py --modes 4` | Accepts4; emits `--render-assets`, which does not reset density. Does not emit global/hud-assets. |
| `prototype/start-asset-debug.py` | No internal-density option; debugger defaults8. Its `scaler4x` configuration controls window resolution only. |
| `prototype/asset-index.py play` | Delegates to that debugger; no internal-density option or global/hud-assets. |

[Audited file hashes](evidence/linked-density-correction-20261026/wrapper-audit.json)
are bound to public `7d94cf87740566e40c91043dcf2ebe2fb4e0e67b`.
No canonical-wrapper modification is justified by this incident.

## Reproduce without relying on intended labels

Pillow and NumPy are required. Supply the original game data, qualified binary,
and present/missing packs from the accepted setup; the missing pack must omit
only the six linked assets. The output directory must be new.

```sh
python prototype/verify-linked-newshf-density.py \
  --exe /absolute/qualified/opentyrian2000 \
  --data /absolute/original-data \
  --assets /absolute/pack \
  --missing-assets /absolute/pack-missing \
  --sdl-library-dir /absolute/sysroot/usr/lib/x86_64-linux-gnu \
  --density 4 --out /absolute/new-evidence-directory
python tests/test_linked_density_correction.py
```

The hardened driver checks actual RGB audit density/tick coverage, pack
equivalence, state/RNG/Present equality and all75 frame differences against
same-tick quadrant masks. Before running, it verifies four critical original
files (`tyrian1.lvl`, `newshf.shp`, `tyrian.hdt`, `palette.dat`) and the four
oracle mask PNGs (43/81/119/121) against fixed published SHA256 values. It
snapshots those eight files, itself, the executable and both packs before/after.
It reads only the four named original files, not unrelated user data. This is
**not an identity check of every game-data file**. Missing or mutated pinned
inputs, post-run input changes, and wrong/empty/mixed density evidence fail.
The level pin exists in the published original-data fixtures; bank/table/palette
pins match `check_newshf_phase_a.py` and `build_newshf_prototype_pins.py`; mask
pins match `current_linked_newshf_compatibility.py`.
It can also read-only verify an existing complete pair with
`--verify-existing --density 4 --out /absolute/evidence-directory`. That read-only
mode verifies recorded density, outputs, state and fixed oracle masks; it does
not retroactively establish the original-data identity of an arbitrary old run.
Original-data before/after qualification requires a fresh guarded run.
The default binary SHA guard deliberately binds this correction to the original
qualified binary; overriding it requires new evidence, not a historical claim.
The earlier corrective receipts above retain their original narrower input
scope (binary and packs); they are not retroactively rewritten to claim these
new checks. The hardened rerun is recorded separately below.

Compact receipts retain local paths for traceability; no original game files,
executables, or full BMP capture sets are embedded in this addendum.

## Hardened original-input qualification

A subsequent **fresh** full present/missing pair passed with the hardened
version of the driver: [new receipt](evidence/linked-density-correction-20261026/hardened-driver/receipt.json),
[1290 before/after input hashes](evidence/linked-density-correction-20261026/hardened-driver/input-before.json),
[validation and code identity](evidence/linked-density-correction-20261026/hardened-driver/validation.json),
and actual [present](evidence/linked-density-correction-20261026/hardened-driver/present-rgb-audit.tsv) /
[missing](evidence/linked-density-correction-20261026/hardened-driver/missing-rgb-audit.tsv) density4 logs.
Ten regression tests passed, including missing/mutated data, a widened native
mask, and post-run driver/input mutation or deletion. Its scope includes the
four named critical original files, not the complete original-data inventory.
The initial manifest and receipts remain immutable snapshots of the earlier
private correction commit; `manifest-v2.json` describes the hardened state.
