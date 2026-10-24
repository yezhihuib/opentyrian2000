# Current NEWSHF163/167 authoring

## Scope

The two canonical editable files are:

- `authoring-inputs/newshf-current/master-163.png` (2011 × 782)
- `authoring-inputs/newshf-current/master-167.png` (2012 × 782)

Each source contains three separately authored physical poses. Editing one source
rebuilds its three declared consumers in every level using those existing roles.
This does not synthesize a tilt from a front view, change gameplay coordinates,
change enemy animation, or grant additional renderer eligibility.

Bootstrap reconstructs all six selected PNG files and HDR1 transports byte for
byte. The fixed recipe preserves the previously approved binary-alpha 163/167
processing: threshold 128 before and after RGBA Lanczos resize, clear transparent
RGB, paste without a mask onto 192 × 224. Logical size 24 × 28, density 8 and anchor
(6,7) are unchanged. This batch changes the editing workflow, not visual design.

The runtime remains 1029 files with the same destinations. Nine NEWSHF resources
remain in the existing `newshf-optin` group, default off. Only six transport source
paths migrate. The global registry remains 120 resources. C integration changes
one include from the frozen header to a new generated header with the same
bootstrap resource declarations.

## Physical identity, not guessed left/right

| Master | Source columns in order | Existing roles |
|---|---|---|
|163|base125, base123, base127|2100000,2100001,2100002|
|167|base3, base1, base5|2100003,2100004,2100005|

Historical 167 filename labels are not direction authority. Names and recipe use
physical base IDs and source columns, not velocity-sign guesses. No claim is made
that these columns are automatically cycled animation frames.

## NEWSHF168 remains frozen

The approved V4 poses 55/17/93, roles 2100006–2100008, retain their original soft
alpha PNGs, HDA files, runtime rows and `SOFT168_POLICY` hashes. They are not editable
through this two-master workflow. No V2/V3 pixels, alpha threshold, mirroring,
new tilt geometry or pin replacement is introduced for 168.

The entire legacy nine-pose source bundle, provenance, generated resources and
`src/newshf_hd_assets.h` remain unchanged and independently pass the original
validator. Historical masters under `docs/` are frozen evidence, not competing
editable sources. Only the two new canonical files are edited going forward.

## Stage / apply / check

After editing one or both canonical masters, create an external candidate JSON by
copying `assets/hd/authoring/newshf-current.json`, changing schema to
`opentyrian-current-newshf-candidate-v1`, removing `resources`, giving a version,
and updating the SHA256 of the edited master(s). Retain exact fixed master paths,
identities, ordering and recipe. The recipe is declarative data, never executed;
its complete geometry/alpha policy must match the bounded compiler constant.

From the repository:

```text
python3 scripts/build_current_newshf.py stage --selection /outside/candidate.json --stage /outside/new-stage
python3 scripts/build_current_newshf.py apply --stage /outside/new-stage
python3 scripts/build_current_newshf.py check
python3 scripts/check_newshf_phase_a.py
python3 scripts/build_newshf_hd.py check
```

Stage writes only a new directory outside the repository. Apply re-derives the
plan, validates all dependency fingerprints and staged bytes, and rejects stale,
modified or aliased input. Handled write failures roll back; this is not a
crash-safe multi-file transaction across process failure or power loss. No
cross-call cache hides edits. `check` is read-only and checks exact derived PNG,
HDA, full resource mapping/header, production source binding and formal manifest.

Do not edit generated PNGs, HDA files, headers or runtime manifests directly.
Do not alter frozen historical selection hashes to accept current edits.

## Validation boundaries

Focused tests prove bootstrap byte equality, exact three-role propagation for
each master, unchanged 168, fixed geometry and malformed/tampered/path rejection.
Transaction tests with mocked aggregate derivation prove handled rollback and
stale/staged-byte checks, not production integration alone. Separate runtime
tests run actual master edits through full stage/apply/check and verify every
file in 1029-member exports. Linux/Windows asset-layout exports do not mean a
Windows game was executed. Independent native/build results are recorded
separately; no natural campaign or physical GPU acceptance is inferred.

## Reproduce the native compositor lane

```text
python3 tests/current_newshf_native_validation.py --original-data /private/original-data --sysroot /local/sdl-sysroot --out /outside/native-output
```

The adapter SHA-pins the historical driver, preserves its C harness, validates
all nine current rows, and switches only the three fixture enumerations to those
validated current paths. Optional `--source-root` selects an explicit checkout.
Original game data is required locally and is never included in this repository.
The exact validation boundaries and negative controls are recorded in
`current-newshf-native-validation.json`. The older standalone identity driver's
stale preflight is reported there as not executed, not silently called a pass.
