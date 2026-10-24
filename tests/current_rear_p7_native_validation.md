# Current Rear P7 finite native validation

The reusable runner uses these adjacent files under `tests/`:

- `current_rear_p7_native_validation.py`
- `current_rear_p7_observer_shims.h`
- `current_rear_p7_cache_checks.c`

Run with Python3 and a POSIX C compiler with ASan/UBSan support:

```sh
python tests/current_rear_p7_native_validation.py --source-root . --out /tmp/rear-p7-native-bootstrap
```

The output directory must not exist. No pre-existing fixture or absolute workspace path is needed. Generated synthetic fixture data takes approximately400MB; retain `receipt.json` and top-level logs before cleaning the disposable output. No original game data, network access, SDL or Windows session is required.

For edited-authoring validation, independently stage/apply a real canonical SVG change in an isolated repository copy first, then invoke the same runner with that copy as `--source-root` and a fresh `--out`. Authoring transaction checks are intentionally not simulated by this runner. The historical full runners remain SHA-pinned and unchanged. Any future edits to these four pinned historical scripts/C harnesses must trigger explicit adapter review, not silent hash updating.

The historical runner fails unchanged on public525 and current source because it lacks16 unrelated Green/Front/global/shop observer declarations. The external shim supplies neutral behavior only for those hooks; no Rear hook is stubbed, and no historical test is removed. Original failure equivalence is recorded in the independent validation receipt. Global unhandled responses are -1; begin observer handles are0; other observers discard arguments. This fixture does not test those unrelated routes.

The runner first runs all historical synthetic adapter and shadow cases with the shim, then regenerates malformed resource variants from all48 actual HDA files and uses production current payload pins. Both real-payload shadow preparation and extra current P7 cache tests run plain and ASan/UBSan. The current4 HDA override their historical same-name counterparts; other44 retain frozen transport bytes. Extra tests cover all selected P7–P11mode2 records271..275,294/295,d4/d8; exact loaded file bytes; cold/warm caching and restart; Hard normal versus shadow gates; birth reset.

**Limits:** original bank and weapon records remain generated synthetic controls with fixture source/record pins. Normal draw callback is an observer. Shadow coverage and lease preparation are actual production code, but no final compositor pixel output is measured. No original-data admission, campaign, Windows, GPU or visual acceptance claim. The independent one-off crossgeneration pin/HDA rejection checks are separate evidence and are not claimed as part of this portable invocation.
