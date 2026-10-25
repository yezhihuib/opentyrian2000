# Rear golden transport batching

## Scope

This is a tests-only optimization based on `111f3b4c6ae65f93865681d6d7223390c3f69443`.
Its logical base has the same tree as public commit
`01e0069a3b53be5463a99895d90c474c574cb72e`
(`539fe6bec5d98bd3047cbe728f0cdc86127a2622`).
Production compiler/validator scripts, drivers, art, runtime mappings, payloads,
and original source-projection ledgers are unchanged. It introduces no user-facing
skip flag, persistent worker, output cache, or cross-projection reuse.

`_ProjectionProofContext._check_tools` now owns one short-lived Node process per
Rear check, instead of six. The transport is lazy: the original P7 checker must
finish all Python assertions before Rear39 begins, then Rear1, Rear281 and both
independent Rear Lobes masters. Each original JS driver still renders its own
inputs, in a fresh VM context, with its original temporary working directory.
Original Python parsing, composition, Pillow/canonical-PNG encoding and complete
SVG/PNG/RGBA golden assertions remain active.

Both fresh dependency snapshots remain before/after every reuse and final check.
The new helper source, module origin, driver, environment and family order are
bound into that closure. Lobes' plural `GOLDEN_MASTERS` and `GOLDEN_SVG_HASHES`
are now explicitly included in the renderer profile as well.

## Bounds and failure semantics

- One fresh process per check, maximum six jobs; normal EOF/exit-zero required on success; killed/reaped on failure.
- Existing 128MiB Node heap, per-request 30s and aggregate 180s deadlines.
- Nonblocking stdin/stdout/stderr transport, bounded encoded frames and decoded
  outputs; strict envelope/base64/duplicate-field validation.
- Successful shutdown drains both pipes to EOF under a bounded deadline, rejects
  any trailing stdout/stderr and requires worker exit code zero. A final valid
  response alone is not enough.
- No fallback to serial when transport/order/callable/executable binding fails.
- Earlier Python failures cannot be masked by a later renderer failure because
  later jobs are not submitted until the earlier checker succeeds.
- Original production `check_tool()` functions provide the serial test oracle.

This bridge supports the existing fixed drivers; it is not a general subprocess
replacement or isolation sandbox. Native Sharp state is shared within one check,
while every driver retains its `cache(false)` / `concurrency(1)` reset. Independent
probes verified a prior job's VM global and deliberately changed Sharp cache/
concurrency settings do not alter the six accepted outputs. That is a bounded
state-equivalence claim, not arbitrary native-state isolation.

Successful raw driver outputs are byte-exact. Failure stderr stack formatting can
differ between standalone Node and the VM; parent-visible rejection type/message
and request ordering were checked, not exact failure-stack byte equality.
Existing sequential-filesystem snapshot/TOCTOU limitations remain unchanged.

## Controlled complete-projection comparison

A paired run executed the complete `project_p9_inventory` with the original
serial tool-check order and with batching. Timing excludes input scans.

| Measure | Serial | Batched |
| --- | ---: | ---: |
| Time | 108.760822 s | 76.604753 s |
| Node process launches | 498 | 133 |
| Full dependency snapshots | 330 | 330 |
| Output entries | 7225 | 7225 |

Observed reduction: **29.5659%** for this complete projection, not a claim about
the entire historical test suite. Both outputs are equal as Python objects and
have SHA-256:
`45ad4ff592f22934c23a4014708ad90fbc01518471144ea47aaef5f820dd583f`.

Before/after each phase and between phases, all 8843 measurement-candidate tracked files'
content/mode fingerprint remained:
`120ffb90e61abdaf83d5a3df3d9c3b863e4a7090ef0654bd0d1a33eab81b361f`.
This fingerprint precedes the documentation-only recording of these results.
All eleven family dependency snapshots, including selected external tool/package
profiles, also remained equal. A preceding pair produced the same output/counts
but experienced a tool-transport interruption, so only the quiet run above is
used for the timing comparison.

## Regression coverage

Focused differential cases cover all five Rear families, both Lobes masters,
SVG/PNG/RGBA hashes, Node/Sharp profile drift, unavailable paths, renderer errors,
malformed/oversize output, async hangs with kill/reap, first-error order, independent
processes across checks, unsupported callable/order, and restoration.

Finite real-file fixtures cover missing bytes/tampering/mode/module-origin drift
for all five families, first-derivation mutation, reuse/final boundary mutation,
and post-render mutation before the second snapshot. Helper origin/live-profile
changes are also rejected. No original assertion is removed or weakened.

Final combined regression result: **36 tests PASS, 447.607s**, comprising all
13 new focused tests and all 23 existing context tests, with no skips or failures.
The complete execution/source/profile fingerprint was unchanged afterward.

Reproduce from the repository tests directory:
```sh
python -m unittest -v test_rear_golden_batch test_single_projection_proof_context
```
## Withdrawn predecessor and lifecycle correction

Checkpoint `86c113506ab6e0dad5466acc70b8e13f4c9ef3e7` is not a qualified
performance release. An external probe showed its worker could flush the sixth
valid frame, exit with code 7, and still be accepted. Its in-progress historical
run was stopped after four completed tests and archived as withdrawn, not passed.

The corrected success path closes stdin, drains both output pipes to EOF within
the remaining bounded deadline, and requires exit code zero. Regression probes
cover delayed nonzero exit, trailing stdout/stderr, EOF hangs, and normal exit
zero. Independent review additionally checked closed pipes with a still-live
worker and verified every process was reaped and every stream closed. The full
36-test cohort and controlled pair above were rerun on this correction.

## Final historical qualification

The corrected checkpoint `9ddd753fc218a9bfb96ca2adbddcf195612943da` passed the **complete original 54-test
historical cohort in 11903.526s** (runner 11913.867920s), exit code zero, with no
skips or failures. Test names/order and all original assertions are unchanged.
This is additional to the 36-test focused/context run above; the withdrawn
predecessor's partial run is not counted.

All 7189 execution inputs retained identical content and mode before/after:
`428420cba299a7c70fc20aa84cfc86d5eaeb322fa89afcb93d35831c6b21f8eb`.
The full 8843-file repository fingerprint and all eleven selected
external dependency/profile closures also remained identical throughout the run's
before/after checks. Production compiler/validator scripts, assets, mappings and
original source-projection/test oracles remain unchanged from the base.

This report is the only post-qualification repository change. No production or
tested helper/test code was edited after the successful run. Historical-suite
wall time is reported as observed, not as a controlled speedup against a separate
older run; the controlled performance claim remains the paired 29.5659% result.

For context only, the earlier non-batched historical run took 14404.459s; this
run's 11903.526s is approximately 17.36% lower observed wall time. Those runs
had different conditions and were not a controlled performance experiment.
Do not substitute that comparison for the controlled single-projection result.
