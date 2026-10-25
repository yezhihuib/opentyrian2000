# Current Rear281 finite native validation

Run separately from the historical regression aggregate on Linux/POSIX with `cc` and its address/undefined sanitizers:

```sh
python tests/current_rear281_native_variants.py . /tmp/rear281-variants
python tests/current_rear281_native_validation.py --source-root . --out /tmp/rear281-bootstrap
python tests/current_rear281_native_validation.py --source-root . --out /tmp/rear281-edited --fixture /tmp/rear281-bootstrap/actual --overlay /tmp/rear281-variants/rear281-edit --pin-header /tmp/rear281-variants/rear281-edit/current_rear_multi_payload_pins.h
python tests/current_rear281_native_validation.py --source-root . --out /tmp/rear281-wrong --fixture /tmp/rear281-bootstrap/actual --overlay /tmp/rear281-variants/rear281-edit --wrong-pins rear281
```

Use a workspace-local temporary directory when `/tmp` has limited capacity. Output directories must not already exist. An existing fixture may be reused only when every recorded source and extracted artifact hash matches. The source renderer must satisfy the current four-family profiles/goldens; no renderer mismatch bypass exists here.

The variants script changes actual canonical geometry, not only final payload bytes. It produces the successive Rear281-only, Rear281+Rear1, +Rear39 and all-four (+P7) variants, changing exactly20/28/34/38 HDA resources and matching pin cells. Candidate source files, exact edit operations, HDA hashes and combined pin headers are retained. The bootstrap comparison uses all48 actual HDA resources. Normal and shadow preparation checks include all56 Rear281 record/phase consumers at both densities, plus17 Rear1,10 Rear39 and10 P7 consumers.

Each valid configuration runs the unchanged historical shadow harness and the extra actual-file/cache/birth checks under plain C and ASan/UBSan. Cross-generation negative runs use `--wrong-pins rear281`, `rear1`, `rear39` or `p7`, selecting only the intentionally mismatched family. The separate existing observer shim provides finite unrelated missing hooks without weakening any Rear checks. No old test body is deleted.

Scope: real HDA loader bytes and current payload pins, but synthetic source bank and weapon records. Ordinary draw is an observer and shadow checks cover preparation, pointer leases and birth epochs, not final compositor pixels. This does not establish original-data admission, actual weapon firing, campaign playback, Windows execution or GPU behavior. Reusing an earlier hash-verified synthetic fixture is not a fresh execution of the old synthetic fixture builder; receipts distinguish fixture reuse from new actual-payload native runs.
