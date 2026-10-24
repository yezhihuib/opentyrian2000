# Current Rear39 shared authoring

One editable **data-only** `authoring-inputs/rear39-current/master-39.json`
controls six role 131 transports: raw 39, 40 and 41, independently at d4/d8.
It contains one cubic/line path, bounded heat-field numbers and ordered color
stops. The fixed compiler generates all 34 identical coverage/color path uses.
Do not edit the six derived PNG/HDA files, the generated shared payload header,
or any frozen P1/P3/P5 source package. Raw 1 is independently authored, not a
mirror of 39. Current P7's independent SVG controls only raw 294/295.

The fixed recipe preserves the original 12×14 canvas, anchor (0,0), role,
identities and densities. Raw40 copies whole-canvas flipY at (0,-4) then original
at (0,+4). Occupied cropping and overlap are forbidden. Raw41 copies original
(+2,-3), original (0,+1), then full-canvas flipY (+2,+3), preserving accepted tail
cropping rather than re-centering. All supports must be disjoint even outside
the canvas. Both stage plans and `check` report clipped sample/alpha counts.
There is no resampling, blend, RGB normalization, halo or density fallback.

## Edit and apply

Edit the canonical JSON, copy `assets/hd/authoring/rear39-current.json` into an
external candidate file, change its schema to
`opentyrian-current-rear39-candidate-v1`, remove `resources`, update
`masters[0].source_sha256` to the edited JSON's SHA256, and set a version label.
Keep the fixed recipe path/hash and selector 39 unchanged.

```
python scripts/build_current_rear39.py stage --selection /external/candidate.json --stage /external/new-stage
python scripts/build_current_rear39.py apply --stage /external/new-stage
python scripts/build_current_rear39.py check
python scripts/build_current_rear_p7.py check
```

Stage is read-only. Apply independently re-derives every planned output and
requires current dependency fingerprints, plan and staged bytes to match.
Handled write failures restore pre-apply file bytes and remove temporary files;
this is not crash/power-loss atomicity or concurrent-writer locking.
Both families generate the same single payload table from two independently
validated complete source/PNG/HDA/mapping closures. Ten cells are mutable across
the two families; the remaining 38 supported cells and two unsupported zero
cells are frozen. The old header banner is retained byte-for-byte for bootstrap
build equivalence; this documented joint composer is its current authority. Public loads require the exact complete header. During a
candidate authoring transaction the opposite family's assets are fully checked,
then the entire header is recomposed; it never uses the old header as a baseline.

## Reproducibility and limits

The current compiler requires Node **24.22.1**, Linux x64, Sharp **0.35.5** and
its complete recorded native dependency profile. Every generation first checks
the unchanged canonical SVG SHA and all six PNG/RGBA golden hashes. Bootstrap
HDA bytes are exactly the accepted public 525de2b outputs. Future renderer
admission requires a separate explicit golden-verification change.

The frozen P1 strict builder still requires Node 24.19.0 and therefore fails on
this installed Node. It was not bypassed or repinned; the new current compiler
is a separate explicitly admitted compatibility layer, not a claimed successful
old rebuild. Input JSON is strict UTF-8, rejects duplicate keys/nonfinite values,
and admits only bounded closed data fields. It cannot supply SVG, code, URLs,
external resources or transforms. Renderer argv/environment are fixed and
bounded by timeout, JS heap limit and post-execution output-size checks; those
limits are not a native-memory or filesystem quota.

No source-bank pins, record hashes, routes, eligibility, shadows, 80-slot leases,
Front assets or current P7 art change. The 25×2 table order is unchanged; source
index 41 is 15 while payload row 41 is 13. Current source count stays 274; runtime
export count stays 1029 and global registry stays 120. The exact 10 record/phase
consumers are independently enumerated in the validation evidence.

Portable transaction validation:
```
python tests/current_rear39_transaction_validation.py --source-root . --out /external/new-proof
```
It performs true JSON and reciprocal P7 SVG edits, actual second-write rollback,
full stage/apply/check, cross-family corruption rejection and byte-identical
Linux/Windows **asset-only** exports. Native probes and build-input equivalence
have narrower documented scopes; none proves Windows execution, compositor
pixels, original-data admission or a naturally played campaign.

## Final frozen validation

Checkpoint `00bdc8cc90ec001229ef3227c2c400fa69ac77cc` passed all 54
historical boundary tests in 5508.042 seconds. All 7,064 execution input files
were byte-identical before and after; final receipt/documentation changes do
not change those tested inputs. Final P7 and Rear39 integration suites passed
9 and 10 cases respectively. See the companion validation JSON receipts for
focused tests, true edit/rollback/export proofs, native limits and transitive
build-input evidence.
