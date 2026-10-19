# Retired HD resource checkpoints

The current checkout keeps both complete `head-v1` gameplay packs and the complete
nine-file `startup-title-settings-v1` pack. Their accepted runtime files are
unchanged. Nineteen superseded runtime directories were retired: sixteen gameplay
checkpoints and three startup subsets. This removes 2,249 files / 210,038,896 logical
bytes from a source snapshot before the small reference edits. It does not remove
Git history or promise the same reduction in a full clone's download size.

All canonical artwork, PNG recipes, source exports, licenses and original game
files remain. Some historical gameplay HDA files differ from current art, so they
must not be treated as interchangeable copies. Historical reports under `docs/`
and frozen source-package evidence describe their original checkpoint; paths in
those reports may require reconstruction or Git recovery.

## Current verification and use

`python3 prototype/build-hd-assets.py` verifies current installed resources and
canonical sources. `--output /absolute/path/to/a/new-directory` rebuilds the two
current gameplay packs and complete current startup pack outside the source tree.
The active inventory is `assets/hd/manifest.json` → `packs`; old gameplay recipes
are retained unchanged in `retired_packs` and are excluded from normal verification.

The eight `-Before...` switches on each PowerShell preview/debug launcher now stop
with a clear retirement message. Run without a `-Before...` switch for the current
pack. Current startup instructions use
`--startup-assets=assets/hd/packs/startup-title-settings-v1`, which includes the
manufacturer cards, layered title, title menu font and settings fonts together.

## Historical acceptance scripts

Some older source-preservation scripts intentionally pin a complete manifest,
asset tree, or source tree at a named feature checkpoint. Examples include the
cash/gem preservation suites and rear P5/P9 additive-asset acceptance scripts.
Later accepted features already change those finite baselines. Run such scripts
in a worktree of the historical commit named by that script or its acceptance
report. Restoring the pre-cleanup pack directories alone does not restore an
older whole-tree baseline. Their original pins and cases remain unchanged.
Current verification is the aggregate current-resource/source rebuild, focused
retirement/startup/fixture mutation tests, and current runtime packaging checks;
this change does not claim that every historical acceptance script passes on the
latest combined tree.

## Reconstruct a historical gameplay fixture

Choose a name from `retired_packs` and a new directory outside the checkout:

```sh
python3 prototype/rebuild_retired_hd_pack.py \
  packed-blue-four-foundation-type10-death-effects-white-smoke-v1-test \
  --output /absolute/path/to/new-historical-fixture
```

The helper verifies each canonical PNG's fingerprint, RGBA dimensions, HDR1 header
and reconstructed resource hash before creating output. It never needs an installed
old pack and refuses to overwrite an existing directory. Frozen effects fixtures
retain their exact checkpoint names and may request this external reconstruction
through `prepare-effects.py --assets-output`.

## Recover the original tracked directories

The last complete pre-cleanup tree is commit
[`1037b40b9a0878783978a1bf3e3f39a4d4aefc14`](https://github.com/yezhihuib/opentyrian2000/tree/1037b40b9a0878783978a1bf3e3f39a4d4aefc14/assets/hd/packs).
An isolated historical worktree preserves the old launch scripts and tests too:

```sh
git worktree add --detach ../opentyrian-before-pack-cleanup \
  1037b40b9a0878783978a1bf3e3f39a4d4aefc14
```

To restore only a chosen old directory into an otherwise clean checkout, use
`git restore --source=1037b40b9a0878783978a1bf3e3f39a4d4aefc14 -- assets/hd/packs/NAME`.
That creates ordinary working-tree changes; it does not rewrite history. No force
push, history filtering, garbage collection or deletion of local validation data
is part of this cleanup.
