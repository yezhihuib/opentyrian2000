# Archived finite effects fixtures

These source overrides are exact snapshots of already tested private binaries, not production code. By default, prepare-effects.py copies the existing source/build files and applies hashed snapshots. Optional --assets-output also reconstructs the required historical resource pack; neither mode compiles or runs a test binary. At the original export, the newly exported preparation command had not been executed after the then-current stop request. The source snapshots and their hashes were checked while packaging.

White/green call original loaded weapons at a fixed tick; they do not overwrite per-shot TTL, motion, collision or RNG. Shield is a read-only observer of original natural bursts. Match the documented family pack and environment. Their original Windows runs and complete reports remain in existing Library evidence. Original game data, SDL SDKs, DLLs/EXEs and screenshots are intentionally excluded from Git.

Windows preparation: `python prototype/fixtures/prepare-effects.py --family green-trail --output ../green-fixture` (choose a new sibling directory so the existing project-deps remains reachable). Build with `../green-fixture/prototype/build-game.ps1`. On Linux, use the copied Makefile and installed SDL dependencies. See docs/WINDOWS_HANDOFF.md for the exact green run arguments and remaining WIP scope.

## Rebuild retired archived resource packs

The `test_resource_pack` names in `effects/*/manifest.json` are frozen historical inputs. Their old installed directories have been retired. Their recipes remain under `retired_packs` in `assets/hd/manifest.json`, with canonical PNGs, original HDR1 headers and expected hashes retained. Do not substitute a current head-v1 or green-v2 pack: changed artwork would change these archived regression tests.

Prepare sources and reconstruct their exact historical pack in two separate new external directories:

```text
python prototype/fixtures/prepare-effects.py --family green-trail --output ../green-fixture --assets-output ABS_NEW_EXTERNAL_DIRECTORY
```

`--assets-output` must be absolute and outside the checkout, and must not overlap the source output. Preparation verifies source compatibility and frozen override hashes before reconstruction. It does not compile a binary, start a game, or install either output. Point the archived binary's normal resource-pack argument at the external pack directory; provide original legal game data separately.

A compatible historical production source base is also required. Preparation deliberately rejects any unreviewed drift from `same_other_production_src_sha256`; current production sources may have evolved beyond that archived base. Reconstructing retired assets does not relax these source pins. The standalone asset command below works independently of that source-compatibility gate.

To reconstruct assets without preparing sources, use the exact `test_resource_pack` value for the chosen family:

```text
python prototype/rebuild_retired_hd_pack.py packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v1-test --output ABS_NEW_EXTERNAL_DIRECTORY
```

The same command works with the white-smoke-v1 and shield-v1 manifests' pack names. Without `--assets-output`, source preparation prints the required historical pack name and standalone rebuild command. Existing source snapshots, source hashes, archived binary hashes and original validation limits remain unchanged. The tests in `test-prepare-effects.py` cover this optional reconstruction handoff and rejected output paths as well as source and override negative controls.

## Current green integration review

`python prototype/fixtures/prepare-green-review.py --output ../green-review` prepares the archived original weapon71 injection/read-only observers with the current production renderer. It additionally logs every normal/shadow head214–217 draw. Set `OT_FX_FIXTURE=1` and `OT_FX_PROBE=1`; `OT_GREEN_POINT_BASELINE=1` selects original point brightness in this private fixture only. The production renderer has no such environment switch. Use the manifest's current default debug pack.

`python prototype/fixtures/test-prepare-effects.py` tests strict hash compatibility including cross-platform line endings. `python prototype/fixtures/test-green-background.py --sanitize` tests the actual extracted renderer helpers against an independent bilinear oracle (C99 compiler; optional GCC/Clang sanitizers).

The original weapon71/1071 heads are a four-frame214–217 cycle: loaded weapani=3, delays8, base214, so shotAniMax=4. The earlier static214 handoff was incorrect. Do not alter animation, shot positions, timing or shadows to fit one authored frame.

Formal head regeneration: `python prototype/build-green-head-art.py --output ../green-art-check`. Same-scale point/smooth review: `python prototype/fixtures/verify-green-review.py --baseline <point-run> --candidate <smooth-run> --assets <current-pack>`. The verifier uses lossless PNG conversions of the actual captures.

Green foreground-head layer oracle: `python prototype/fixtures/test-green-head-layer.py --sanitize` checks the extracted current renderer at2×/4×/8×, including overlapping alpha, foreground invalidation, restoration and suppressed ownership.

Cloud-floor shadow oracle: `python prototype/fixtures/test-cloud-shadow.py --sanitize` verifies only tagged cloud pixels, original palette transition/floor, zero-denominator handling, provenance invalidation and unchanged green head replay. Current review preparation restores the production layer2 binding; archived preparations remove only that reviewed line and still require the old source hash.

Physical rotor enemy mapping/filter coverage: `python prototype/fixtures/test-rotor-enemy.py --sanitize --output NEW_EXTERNAL_DIRECTORY`. The test reads current production functions, creates synthetic assets in a temporary directory, and writes reports outside the checkout. See `docs/ROTOR_ENEMY_VALIDATION.md` for actual scene, missing-frame and private reverse/hit diagnostic results.

Finite ground binder: `python prototype/fixtures/test-ground-binder.py --sanitize --output NEW_EXTERNAL_DIRECTORY`. Tests the current layer/bank/ID whitelist, nine slots, capacity, missing/invalid assets, existing ground/cloud paths and fallback trace preservation. Runtime scope is documented in `docs/GROUND_NINE_VALIDATION.md`.

Enemy-only orb112/113: `python prototype/fixtures/test-enemy-orb.py --sanitize --output NEW_EXTERNAL_DIRECTORY`. Extracts the real wrapper, mirror helper and original RLE blitter to verify indexed parity, exactly-once blit/reset, finite source scope and ownership. See `docs/ENEMY_ORB_VALIDATION.md` for actual lifecycle and native evidence.

Remaining plateau edge binder: `python prototype/fixtures/test-plateau-binder.py --sanitize --report EXTERNAL_REPORT.json`. Covers only96/97/98/108 and existing finite mappings; see `docs/PLATEAU_FOUR_VALIDATION.md` for native, missing-all and highest-detail tests.

Finite bank9/newshE intact and remnant stone family: `python prototype/fixtures/test-stone-enemy.py --sanitize --source <renderer.c> --assets <candidate-pack> --runtime-zip <approved-generated-runtime.zip> --output <new-external-directory>`. Tests the twelve explicit bases and slots, all original quadrant offsets, role110 namespace isolation, loader failure per whole component, actual opaque PNG/HDA transport, independent RGB/filter oracle, six-component registration, source guards and all31 prior bank1 bindings. A separate extracted original `blit_enemy`/RLE test checks indexed parity and exactly-once original blit/reset. Original game pixels are not required. Frame-reset checks are unit-level; saved runtime logs are still required to establish actual removal and remnant transitions. The `0xD0` cases exercise compositor compatibility only: these explosiontype25 stone records do not receive the craft family's natural palette hit flash.

Purple ten-piece formation: `python prototype/fixtures/test-purple-formation.py --sanitize --output NEW_EXTERNAL_DIRECTORY`. Four static designs, all47 enemy bindings, source-role isolation, exact PNG/HDA transport and original wrapper parity; actual linked/drop diagnostics are documented in `docs/PURPLE_FOUR_VALIDATION.md`.
