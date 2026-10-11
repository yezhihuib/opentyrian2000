# Archived finite effects fixtures

These source overrides are exact snapshots of already tested private binaries, not production code. prepare-effects.py only copies the existing source/build files and applies hashed snapshots; it does not build or run. This newly exported preparation command was not executed after the stop request. The source snapshots and their hashes were checked while packaging.

White/green call original loaded weapons at a fixed tick; they do not overwrite per-shot TTL, motion, collision or RNG. Shield is a read-only observer of original natural bursts. Match the documented family pack and environment. Their original Windows runs and complete reports remain in existing Library evidence. Original game data, SDL SDKs, DLLs/EXEs and screenshots are intentionally excluded from Git.

Windows preparation: `python prototype/fixtures/prepare-effects.py --family green-trail --output ../green-fixture` (choose a new sibling directory so the existing project-deps remains reachable). Build with `../green-fixture/prototype/build-game.ps1`. On Linux, use the copied Makefile and installed SDL dependencies. See docs/WINDOWS_HANDOFF.md for the exact green run arguments and remaining WIP scope.

## Current green integration review

`python prototype/fixtures/prepare-green-review.py --output ../green-review` prepares the archived original weapon71 injection/read-only observers with the current production renderer. It additionally logs every normal/shadow head214–217 draw. Set `OT_FX_FIXTURE=1` and `OT_FX_PROBE=1`; `OT_GREEN_POINT_BASELINE=1` selects original point brightness in this private fixture only. The production renderer has no such environment switch. Use the manifest's current default debug pack.

`python prototype/fixtures/test-prepare-effects.py` tests strict hash compatibility including cross-platform line endings. `python prototype/fixtures/test-green-background.py --sanitize` tests the actual extracted renderer helpers against an independent bilinear oracle (C99 compiler; optional GCC/Clang sanitizers).

The original weapon71/1071 heads are a four-frame214–217 cycle: loaded weapani=3, delays8, base214, so shotAniMax=4. The earlier static214 handoff was incorrect. Do not alter animation, shot positions, timing or shadows to fit one authored frame.

Formal head regeneration: `python prototype/build-green-head-art.py --output ../green-art-check`. Same-scale point/smooth review: `python prototype/fixtures/verify-green-review.py --baseline <point-run> --candidate <smooth-run> --assets <current-pack>`. The verifier uses lossless PNG conversions of the actual captures.

Green foreground-head layer oracle: `python prototype/fixtures/test-green-head-layer.py --sanitize` checks the extracted current renderer at2×/4×/8×, including overlapping alpha, foreground invalidation, restoration and suppressed ownership.

Cloud-floor shadow oracle: `python prototype/fixtures/test-cloud-shadow.py --sanitize` verifies only tagged cloud pixels, original palette transition/floor, zero-denominator handling, provenance invalidation and unchanged green head replay. Current review preparation restores the production layer2 binding; archived preparations remove only that reviewed line and still require the old source hash.

Physical rotor enemy mapping/filter coverage: `python prototype/fixtures/test-rotor-enemy.py --sanitize --output NEW_EXTERNAL_DIRECTORY`. The test reads current production functions, creates synthetic assets in a temporary directory, and writes reports outside the checkout. See `docs/ROTOR_ENEMY_VALIDATION.md` for actual scene, missing-frame and private reverse/hit diagnostic results.

Finite ground binder: `python prototype/fixtures/test-ground-binder.py --sanitize --output NEW_EXTERNAL_DIRECTORY`. Tests the current layer/bank/ID whitelist, nine slots, capacity, missing/invalid assets, existing ground/cloud paths and fallback trace preservation. Runtime scope is documented in `docs/GROUND_NINE_VALIDATION.md`.
