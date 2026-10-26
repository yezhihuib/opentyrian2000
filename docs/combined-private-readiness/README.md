# Private combined launcher / SHOP / projectile91 readiness

This is a new private integration, not restoration of lost private history and
not a public/GitHub publication.

## Exact ancestry

- Public base: `f58647e7ff74e2276a1413b3675e651f1232bb41`.
- Qualified projectile91: `1fec095caebd17b6a87cd71eeed59f37d64ce996`.
- Local launcher cherry-pick: `1cfa129` of original private `7204f43387ccf3d1855bb9cd3b78c15dcb4a7d0b`.
- Local SHOP cherry-pick: `e00ae11` of original private `0ef62184d0ffa1a889bfb87e45ac9bd4483a2128`.
- The commit containing this document adds only the combined acceptance gate,
  its tests/receipt, canonical test invocation, and this evidence. Original
  launcher, SHOP, and projectile91 branches are retained unchanged.

## What the gate proves

The original 6,404-entry SHOP inventory and its SHA-256 pin remain unchanged.
The six new qualified paths have a separate immutable receipt:
`tests/fixtures/shop_current_acceptance/projectile91-qualified-extension.json`.
That receipt is pinned by SHA-256
`cd2b80009795e1b106bbc64eded7f104bcdc6b38ee44779070941ec7eefd750b`.

Before excluding any path, the gate verifies those six exact files and runs the
existing projectile91 master-to-derivative proof. The immutable selection also
pins the approved master bytes outside `assets/`. Two executable includes are
whole-file pinned; the generated header and three assets must be reproducible.
The checked-in 14-file / 59-hunk projectile91 inverse then verifies complete
current files and restores their authentic public-f586 hashes. Every original
inventory path/hash is still checked, including the six non-src/assets files.
Unaccounted source/assets, missing paths, symlinks, partial inverse application,
newlines, altered role/eligibility, and unrelated source changes fail closed.
Acceptance itself requires no Git subprocess or private Git objects.

**Editable generation is not acceptance.** The builder may coherently derive a
new approved master, but a new visual/native acceptance review must explicitly
freeze a new small qualified-extension receipt. Neither coherent artwork
replacement nor harmless receipt/selection whitespace inherits this snapshot's
acceptance. This is one centralized shared-material qualification, not per-level
copies or an automatic rebaseline of the old SHOP inventory.

Original frame/front/generator/menu/product historical proofs remain untouched;
the frame protected-source list does not intersect the projectile91 delta.
Unavailable historical Git-stage checks remain unavailable; no fabricated
parent or alternative expected historical hashes were introduced.

## Reproduce

From this checkout, with SDL development flags/libraries and original data:

```sh
PYTHONPATH=tests python3 -m unittest -v test_shop_current_acceptance test_shop_projectile91_compatibility
python3 -m unittest discover -s tests -p test_portable_launchers.py -v
python3 scripts/build_current_projectile91.py check
bash tests/run_shop_current_acceptance.sh /path/to/data /outside/repo/plain-output
bash tests/run_shop_current_acceptance.sh --ubsan /path/to/data /outside/repo/ubsan-output
```

The canonical runner now includes all 14 original fresh SHOP tests plus six new
compatibility tests. Tests use a complete private file copy for actual
mutation/missing/symlink/restore controls; accepted checkout bytes are not edited.
Native checks compile the live combined source, never source projected by Python.
The runtime harness uses synthetic SHOP fixtures and SDL's software presenter,
not game-loop navigation or historical recovery. Negative harnesses remain plain;
the `--ubsan` switch instruments the positive core/typography executable.

See the accompanying evidence and external final-chain/backup manifest for
terminal results. Prior long history-wide sweeps were deliberately stopped
incomplete, not passed. The bounded projectile91 full source inverse and frozen
P9 asset-inventory positives passed before this combined integration.
