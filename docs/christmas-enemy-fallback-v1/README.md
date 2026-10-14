# Christmas enemy-shot fallback

The production diff and JSON receipts in this directory describe the historical
isolated Christmas checkpoint. They are preserved unchanged. The current tree
also includes the separately reviewed normal-data Hard+ night extension; its
[combined-source validation](../firstlevel15-night-v1/VALIDATION.md) records the
coexistence rerun and exact inverse of both deltas. Do not treat the isolated
receipts below as a combined-tree run.

## Reviewed isolated change

Four added lines in `render_mirror_enemy_shot` decline the nine existing normal-art
replacements when the real `xmas` mode flag is set and the call uses bank 8:

- Energy namespace 111: IDs 77,58,182,163,1,183,164
- Enemy orbs 112/113: HDA namespace 8, diagnostic trace role 108

The guard runs before family checks, asset loading and warmed-cache acceptance.
Shell 146/147 (namespace 122) remain eligible because their original compressed RLE,
decoded indices and coverage are byte-identical in normal and Christmas data.
The existing wrapper still executes the original indexed draw exactly once.

The isolated production diff is [production.diff](production.diff). Removing those
four lines from that checkpoint reproduces public baseline tree
`2a60deb74b1a677e3d3cd6c5ea0c251e8ac54028` exactly across all 148 production
files. Assets, loaders, compositors, palettes, player bindings and gameplay are
unchanged. Manual HD eligibility remains local single-player Episode 1 / physical level 9;
this checkpoint does not admit physical level 15.

## Mode and original-source proof

Startup selects `tyrianc.shp` when `xmas` is true, otherwise `tyrian.shp`.
The tests pin both complete external inputs and their bank 8 slices. They separately
exercise the real pairings and deliberately mismatched flag/bank controls.
This is a mode guard, not a source-content hash check: loading Christmas bytes
under a false mode flag is an artificial fixture that retains normal-mode admission.

[Source proof](source-proof.json) contains only hashes and equality metadata.
All nine affected compressed/decoded sources differ. IDs 77/58/1 also change
coverage; the other six retain coverage but change indexed colors. Shell 146/147
are identical, including their 63/60-byte compressed streams.

## Reproducible, bounded tests

The current harness additionally verifies both approved deltas through
`test-normal15-source.py`, includes the night scope dependency, and checks normal
Hard+ admission versus Christmas and special-mode exclusion. It still compiles
the same three finite Christmas units. Counts below and the linked JSON are the
historical isolated run; current combined results are linked above.

The public Python/C harness requires separately supplied, matching original game
data. It does not bundle or download original data. Only two bank 8 slices and 26
named existing HDA resources are materialized in a fresh external test directory;
no full pack or original-data fixture is added to the repository.

```sh
python3 prototype/test-christmas-enemy-fallback.py --source-only
python3 prototype/test-christmas-enemy-fallback.py \
  --normal-data /path/to/original/tyrian.shp \
  --xmas-data /path/to/original/tyrianc.shp \
  --out /path/to/fresh/external/unit-output
```

Requirements: Python 3, a C99 compiler, local Git objects for the pinned baseline tree,
and ASan/UBSan support. Tree-addressed reads do not depend on a private commit alias.
The final matrix compiles three standalone units:
baseline `-O2`, candidate `-O2`, and candidate ASan+UBSan. None launches the game.
The default preview/debug resources used by the tests are verified identical.

Each final executable passes 1,156 original-wrapper transactions and 2,216 direct
negative-guard checks. Baseline admits all nine real-Christmas changed IDs with
both cold and warm caches; each candidate observes zero. Candidate transactions
include 702 accepted and 454 fallback draws. See [validation.json](validation.json).

Covered:

- Real normal and Christmas modes, cold and normal-warmed resources
- Separate mismatched flag/bank controls and normal→Christmas→normal transitions
- No new file reads or asset-cache mutation on nine-ID Christmas rejection
- Continued HD admission for 146/147, including real Christmas sources
- Player head/shared-ID admission isolation and the existing player 58 shadow path
- Wrong bank/ID, inactive/rejected/missing/invalid/no-pack and density guards
- Existing energy/shell surface, clipping and unsupported-coordinate rejection
- Ordered original indexed writes and full indexed-buffer/guard-byte equality
- Original source-bank immutability and unchanged manual level 9 eligibility

## Limits and retained failures

These are focused extracted-source units, not full-engine or visual acceptance.
The loader, admission hooks, wrappers and original RLE blitters are production
extractions. The HD compositor and pixel notification hook are observing stubs;
RGB composition and visual shadow correctness are not measured. Player 58 is the
only executed player-shadow route. Other player-shadow/compositor preservation is
established by the exact production inverse. Diagnostic `decode_tile` code is
extracted but its synthetic-asset path is not exercised.

One normal Linux production build (`make -j2`, exit 0) passed using the retained
verified dependency prefix, without dependency installation or fetching. Five
misleading-indentation warnings refer to unchanged lines; there were no errors.
No gameplay process, native 2×/4× capture, Windows/GPU check, fetch or publication
occurred for this fix. The first sanitizer attempt failed
because LeakSanitizer cannot run under this executor's tracing environment.
The successful final run disables leak detection while keeping ASan and UBSan
active. Six local development harness iterations produced 18 standalone unit compilations
and executions; the final three pass. Private original-data fixture bytes and
intermediate execution directories are excluded from this public packet.
