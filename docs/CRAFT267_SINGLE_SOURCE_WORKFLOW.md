# NEWSH2 base267 current authoring

This finite legacy workflow maintains **only HDA1010267**. The current selection
uses the approved two-legged red π-mark design, copied byte-for-byte to
`authoring-inputs/enemy-267-approved-20261022/enemy-newsh2-267-master-v1-normalized-candidate-v2.png`.
It is the sole current PNG input; no normalization or redraw is performed here.

The PNG SHA256 is
`b396b4e2e54b213077eb77958e1accbc44ee90540f4301a3a313779291177b7e`.
Its exact straight RGBA8 payload, prefixed by fixed HDR1 values
`[1010267,8,24,28,6,7]`, produces 172060 bytes with SHA256
`2fe7c6cf46127f00e3229c84f8eab53487b2dbe0930423a1ea36731795db3f84`.
There is no resizing, premultiplication or alpha/color conversion.

The historical bootstrap PNG, `assets/hd/source/enemy-newsh2-267-8-60d4dcf1f760.png`,
retains SHA256 `1bace298e65167bcc51f3db30c9faab807593ae6c56aa43a74579c7f7fa47487`;
its old HDA retains SHA256 `60d4dcf1f76046c7d8e9f1f56495fce5affc4d919294334173d4a232430487a9`
in both frozen packs. Tests prove those fixed historical bytes separately from
current selected PNG/HDA equivalence. All inputs are repository-local: no private
Git history or additional historical image fixture is required.

## Source and generated consumers

`assets/hd/authoring/craft267-current.json` selects one 192×224 single-frame PNG.
`scripts/build_current_craft267.py` generates these four declared files:

- the installed selection;
- `assets/hd/current-compat/craft267/enemy-newsh2-267-8.hda`, the canonical HDA;
- `packaging/current-craft267-compatibility.json`;
- `packaging/runtime-assets-v1.json`, selecting that canonical HDA for the existing
  `assets/gameplay/enemy-newsh2-267-8.hda` destination.

The runtime remains 1006 logical files. In the old-pixel bootstrap, only that one
runtime row's source and revision change. Production C, its source binding and
the 120-entry global registry stay byte-exact. No new runtime payload pin exists.
The runtime manifest and shared global-header writers explicitly emit UTF-8 LF
on Windows and Unix so the public builders remain reproducible across hosts;
the generated production header's existing bytes remain unchanged.

Place a new approved PNG at a new repository-relative path. Copy the installed
selection to an **external draft**, updating its source path, SHA256 and version.
Do not overwrite the installed selection or historical PNG before applying.

```sh
python scripts/build_current_craft267.py stage --selection /external/draft.json --stage /external/new-stage
# Inspect new-stage/plan.json and new-stage/files/ before applying.
python scripts/build_current_craft267.py apply --stage /external/new-stage
python scripts/build_current_craft267.py check
python scripts/package_runtime.py
```

Stage does not change the repository. The plan binds proposed sources, exact old
outputs and the exact current tool/package/build inputs listed in the plan. Apply
re-derives all outputs and validates every old hash, staged byte, input fingerprint
and temporary-path collision before its first write. Bad JSON, extra/duplicate/
missing identities, wrong roles, geometry fields, RGB/APNG/16-bit PNG, CRC errors,
truncation, trailing data and unsafe source paths are rejected. Generated HDA
geometry and length are checked independently of its recomputed SHA.

Handled write errors trigger restoration of all previous bytes and removal of
newly created outputs/directories. Every individual replacement is atomic.
This is **not power-loss or process-termination recovery**: retain the stage and
inspect/restage after an interrupted process. A rollback failure is reported as
incomplete, never as success. There is no concurrent-writer guarantee.

## Current preview and manual entrypoints

The two old default pack directories and `assets/hd/manifest.json` remain frozen
historical inputs. Their complete 641-file trees are authenticated by digest
`6e40d0b6ad5868fecc00dd3a36b8144ae2e68d7ca166209328af6e0de1e3aa93`.
This includes the 636 HDA entries and five other files in each pack.
`prototype/build-hd-assets.py` remains the historical catalog verifier/reproducer;
it does not replace current authoring or update a current deployment.

Generate a new external current pack view with:

```sh
python scripts/build_current_craft267.py view --kind preview --output /external/new-preview
python scripts/build_current_craft267.py view --kind debug --output /external/new-debug
```

Each view preflights the frozen base and selected craft267 and six sidekick
PNGs against their canonical HDAs; copies all files; substitutes exactly those
seven body transports; verifies every written byte; then publishes the complete
view by a directory rename. No existing directory is
overwritten. All other members, including base269/271 and every density4 file,
are byte-exact copies. The view consumes the canonical HDA directly, not a second
authoring image or independent regeneration recipe.

Default `start-manual-hd.ps1`, `start-actual-preview.ps1`, `start-asset-debug.ps1`
and `asset-index.py build` create a fresh view beneath the repository parent's
`current-craft267-packs/` before using assets. They require Python 3 + Pillow.
The PowerShell helper is `prototype/current-craft267-pack.ps1`. Asset-index play
uses the updated debug launcher. Explicit asset overrides and existing historical
stage selectors keep their requested historical inputs; retired selectors still
fail before dependency checks. No game or profile is launched by authoring/view
commands. Views are ordinary external copies and may be retained for audit.

The current views compose exactly craft267 plus the six bodies managed by
public `build_current_sidekick_body.py`. Both builders carry the other mapping
in their isolated rebuild closures. Each family keeps its existing canonical
HDA authority; other independent historical pack families remain unchanged.
No unpublished sidekick or renderer source was read or used.

## Identity and acceptance limits

Current C proves dynamic shape id1 → NEWSH2 role101, slot243 → base267; slot244
and245 are independent base269/271. `newsh2.shp` is the bank filename. The complete
24×28 image supplies cells267/268/286/287 in order0/1/19/20, anchor(6,7).
Historical records identify enemy17/24/25 with base267/269/271 respectively;
this candidate does not re-enumerate original game records/events and does not
claim enemy17 is the exclusive user. Existing bank/base eligibility is unchanged.

No coordinates, filters, quadrant order, eligibility, cache, INDEX8 writes or
gameplay change. The existing 8→4→classic fallback remains the same source code.
PNG-to-HDA transport equivalence and byte-exact production C are verified; the
approved design intentionally changes pixels. No fresh renderer/native/GPU/
full-game acceptance is claimed by the authoring checks.
The stale historical craft fixture is not presented as a new passing oracle.

Run `python -X utf8 tests/test_current_craft267_authoring.py` for bounded synthetic
propagation, both preview views, runtime copy fingerprints, cross-authoring
closure compatibility, malformed input/stale-plan rejection and injected failures
at every replacement boundary. The package copy test explicitly mocks out
`Path.chmod` because this task forbids permission changes; it verifies actual
copying/hashes but does not certify filesystem permission setup. Actual symlink/
junction creation is explicitly skipped and **unverified**. No link or permission
operation is attempted. No original game data is included or needed.

The earlier Windows sandbox refused an actual test-fixture `os.replace` of its
installed selection with WinError5 (access denied). That operation did not execute;
it has not been retried using another tool or directory. Consequently the actual
synthetic apply/package-copy, installed-state coexistence and filesystem rollback
tests were not accepted in that Windows run. Set `CRAFT267_READ_ONLY_TESTS=1` to
skip those five tests and run the unaffected bounded checks. This variable is not a
zero-I/O mode: other tests still create fixtures or stages. For strictly read-only
review, select audited methods explicitly; do not run either full authoring suite
or the historical projection Generation classes. `MemoryRollbackTests` separately
checks all four replacement failure boundaries, restoration and new-directory
cleanup on a fully in-memory filesystem: this is algorithm evidence only, not OS
rename, durability or permission acceptance. The exact denial and remaining
acceptance gaps are retained in the external delivery receipt.

## Historical daf49548 integration candidate evidence

This candidate merges the frozen e556698 review fragment onto public
`daf49548dfe351c3775b536b778d1a0c0db4b36b`. Five overlapping paths preserve
both changes: the newer two-file render correction and its exact historical
inverse, current source authority, and the craft267 authoring extension.
Production C, the 252-file source binding and all six approved sidekick sources
remain byte-exact relative to daf49548. In that bootstrap, only the existing 267
runtime row's source path and revision change; all 1006 destinations remain
unchanged. The subsequent approved-art installation changes only that same row's
payload fingerprints, keeping its canonical source path and revision.
The historical asset projection verifies nine current generated paths plus the
finite README inverse, retaining the original 3259 historical asset edits.

Evidence at the initial frozen review was limited to static merge/compile checks,
whitelisted pure-memory and read-only checks, canonical PNG/HDA proofs,
read-only seven-overlay plans and runtime reconstruction with its output
captured in memory. These are not stage/apply, filesystem rollback, actual
preview publication, package-copy, renderer/native or full-game acceptance.
At that review stage, no actual authoring apply/replace, permissions or link
creation was attempted.
The separate delivery receipt records exact executed test counts and hashes.

The earlier 73f ordinary-user run (five passes, one explicit junction skip)
is evidence for that frozen revision only. The original Windows replacement
and clone refusals remain historical blockers; this cloud candidate does not
retry those operations or reuse their old acceptance evidence. Subsequent
authorized cloud real-I/O acceptance is recorded separately in
`ACCEPTANCE_RECEIPT.json`, SHA256
`3f65708bff4fb42f9b0850af56d25bc714df582d23c61745fdeade87de086ecf`.
Its A/B revision-dependency bridge and directly executed V3 C checks remain
historical foundation evidence, not a claim that every phase reran on the new art.

## Approved-art cloud installation (2026-10-22)

The approved PNG above was installed through the public stage/apply/check CLI,
with an independently decoded RGBA comparison against the full canonical HDA.
Both actual preview views contain 641 files: seven independently verified current
overlays (267 plus six unchanged approved sidekicks), and 634 byte-exact frozen
members. An actual runtime copy contains all 1006 independently rehashed
destinations; `Path.chmod` was mocked, so permission setup is not certified.
Strict current PNG/HDA/mapping/runtime proofs and the finite historical inverse
pass without changing the original 3259-edit ledger or historical digest.

Among production asset inputs/outputs, only 267's selected source and its four
declared outputs change. The test split
preserves fixed old-PNG/old-pack assertions and adds an independent current-PNG
RGBA oracle; no historical assertion or negative case is removed. Production C,
all 252 source bindings, 269/271, six sidekick inputs/transports and historical
packs remain unchanged. Windows, native/GPU/game rendering, the full suite,
permission/link operations and crash/concurrent-writer durability were not run.
The previous foundation rollback/family-closure evidence is retained; those
fault-injection scenarios are not represented as newly rerun for this installation.
