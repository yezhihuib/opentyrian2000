# Pregame typography on the published B/C parent

This is a source-equivalent integration of the accepted pregame candidate into published C `a35747a9b25a0e7a296165e802e0777a3aaee511` (tree `cc1f5da9feeea8d12407bd7e5a079981ef711d13`, parent B `f3bcc061d8a136e257e9c36d40629b4f948a1708`). The earlier source/native documentation remains an immutable record of its original `317bf55` baseline. This document qualifies the later integration separately.

## Exact coexistence

- All 148 production source files equal native-tested `c9232d59778c8689d85f9e87e8fee260b4c3187a` after reversing only C's eight type15 FNV constants and their adjacent comment. C's existing strict whole-source projection rejects 194 source mutations. There was no production conflict or other implementation edit.
- Every one of the 7,499 files in the published C tree is either byte-identical or recovered by the finite exact pregame reversal. All 703,167,400 asset bytes equal C. All accepted startup/title/settings font resources remain byte-identical to the native-tested candidate. Added source and asset paths are checked explicitly.
- The current parent qualification rejects 159 single-byte changes to approved B/C assets and 27 reversions to their old bytes. Both negative classes call the same validator used for the actual files. Historical selector/manual/Data tests first qualify current B/C files and only then project those finite files back to their original source, retaining their input, draw, fade, token and byte assertions.
- The pregame source projection has 51 mutation controls, including the two narrow bilingual README coverage corrections. Existing production edits and MSVC registration remain exactly the tested pregame additions; only regression qualifications advance to the published C parent.

## Completed checks

All commands run in the integrated worktree with locally owned original Tyrian2000 data and the unchanged `assets/hd/packs/startup-title-settings-v1` resources:

- Pregame source integration; strict coexistence; historical selector integration.
- Pregame core under ASan/UBSan: 78 states, 9,327,126 checks. Unchanged sampler under ASan/UBSan: 33 cases, 28,246,374 checks.
- Selector core: 203 states, 361,097,946 checks. Settings: 359 states, 339,687,940 checks. Load: 832 draws, 138,723,449 checks.
- B and C real-source binding units, both generated-source guard suites, and C preservation/manifest/resource assertions.
- Manual: 69 cases. Data: 20 cases in each of four baseline/candidate density combinations.
- Forced complete Linux builds: `make -B -j4 WITH_NETWORK=false`, followed by `make -B -j4`. Each rebuilt all 71 C translation units with the corresponding network define/link flags. Warnings remain the existing style warnings; there was no build failure. The first post-build digest command used the wrong executable basename, then was corrected before the default rebuild.
- MSVC project source inventory: all current source files are represented, with `pregame_font.c` and `.h` each registered exactly once. This host has no Windows compiler/runtime, so these results do not claim an actual Windows build or physical Windows presentation.

Use the commands in `SOURCE-CHECKPOINT.md` for the core suites. Additional checks are `python3 tests/test_pregame_coexistence.py`, `python3 prototype/test-type4-binding.py --out NEW_DIR`, `python3 prototype/test-type15-binding.py --out NEW_DIR`, `python3 prototype/test-type15-preservation.py --out NEW_REPORT.json`, and the corresponding `test-type4-source-guards.py` / `test-type15-source-guards.py` scripts with fresh `--out` directories. ASan/UBSan used `ASAN_OPTIONS=detect_leaks=0` for the previously documented executor limitation; core allocation accounting remains active.

## Retained native qualification

No new game was launched for this merge. The tested native production bytes and all pregame resources commute exactly with the separately accepted C change, so the original 40-frame proof remains evidence for the same pregame implementation. It retains its synthetic SDL/software/dummy execution, eight starts including the failed R4 admission, and synthetic same-index-overlap qualifications; it does not become a Windows hardware proof.

The original candidate and baseline ELF files plus both private transport libraries remain in the sealed native fixture directory with their original hashes. A local branch retains `c9232d5`; durable source/native archives are unchanged. Only the 13 old manual-pack HDA blobs changed by B/C were copied (2,236,780 bytes), with an explicit reconstruction manifest for the historical fixture inputs. The original native docs and receipts have not been rewritten.

`COEXISTENCE-RECEIPT.json` pins source/test files, finite projection results, resource hashes, forced-build receipts and all regression logs. Full local logs and retained input blobs reside in `pregame-coexistence-a35747a-20261013` alongside the worktree; no duplicate full artwork checkout was made.
