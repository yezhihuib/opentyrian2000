# SHOP current acceptance — fresh 2026-10-26 baseline

This is a **new, bounded current acceptance**, not a reconstructed historical
acceptance. The user authorized restarting after the five private parents were
lost. The production baseline is public commit
`f58647e7ff74e2276a1413b3675e651f1232bb41`. No production source, asset, original
pin, original historical specification, or archival test is changed here.

## Result

Both complete fresh Linux gates (plain and positive-core/typography UBSan) pass.
Static: **14/14**. Native core: **121 states / 13,145,152 checks**. Current
RFR3 typography: **126 states / 16,252 checks**. All **3 native semantic mutants**
are rejected by their expected assertions. **50 actual SDL-render captures**
pass the bounded pixel comparisons, with identical plain/UBSan-run capture bytes.
See [runtime evidence, inputs and limitations](runtime/README.md). This is a
current bounded SHOP result, not historical recovery or a full-game pass.

## Two distinct commands and meanings

Fast current source/resource gate (no private Git objects or game data):

```sh
PYTHONPATH=tests python3 -m unittest -v test_shop_current_acceptance
```

The current runtime gate is `tests/run_shop_current_acceptance.sh`; see its usage
and the runtime evidence below. A static-only pass is **not** a runtime pass.
Full current acceptance requires the static gate, native positive tests, native
negative controls, and bounded real SDL-render evidence. Missing dependencies
are blockers, not skips or successes.

Historical audit (expected nonzero while the five objects remain unavailable):

```sh
python3 tests/shop_published_boundary.py --readiness
PYTHONPATH=tests python3 -m unittest \
  test_shop_frame_integration test_shop_front_boundary \
  test_shop_generator_boundary test_shop_menu_font_boundary \
  test_shop_product_font_integration test_shop_published_boundaries
```

These commands and modules remain unchanged. Blanket test discovery therefore
still includes historical failures. This document makes **no all-repository
all-green claim**. `historical-unavailable.json` records every exact missing ID;
`archival-suite.log` records the fresh 17-test run: 6 pass, 11 fail. Of those
11, five are `HISTORICAL_PROOF_UNAVAILABLE`; five reject the obsolete 775b global
source/asset inventory; one rejects the later `sprite.c` frame projection.
Those six stale-contract failures are not six newly observed runtime bugs.

## What was reviewed rather than blindly re-pinned

The new inventory is read with `git ls-tree`/`git cat-file` from the exact public
commit, not regenerated from an unchecked working tree. Its 6,404 paths cover
274 source files, 6,124 assets and six explicit build/original-pin/exporter
files. Its SHA-256 is hard-coded in the new helper. Every byte, pathname and
regular-file requirement is checked, including additions and deletions. This
is identity evidence for this baseline, **not proof that every unrelated public
feature is correct**.

The old published-stage receipts and all five `*.historical.txt` specifications
remain byte-exact, validated through their original provenance receipt.
Front/generator/menu/product projections still match their existing original
accepted/public hashes; no expectation was weakened. Product's original
annotation-only 22-call diff is retained, with no removed menu lines and no
state-changing expressions.

The two frame owners that changed since public `775b6b...` were retrieved from
that real public Git commit and compared with `f58647e...`. The exact patch is
`public-owner-delta.patch`:

- `src/sprite.c`: nine added lines only. One identity-header include and two
  bank-change notifications, at load/free. Enemy-reuse calls are prototype-
  gated. The newshf notification is a no-op without its feature macros; enabled
  implementation only invalidates matching enemy-bank identity state.
  No original sprite rasterization/draw/input/purchase/RNG line was removed.
- `visualc/opentyrian.vcxproj`: two additions only, the corresponding C and
  header inventory entries. Current C inventory is exact and duplicate-free.
  This is **not Windows compilation or runtime evidence**.

The current helper removes exactly these finite additions (checking occurrence
counts and complete current hash first), then requires the unchanged old public
projection/hash/blob proof. Mutations of these additions, appended logic and
truncation are rejected. The rest of the original frame-protected owner list
continues through the unmodified public projection.

## Original-to-current invariant map

| Area | Original invariant retained | Current independent verification |
|---|---|---|
| Frame | PMF1 dimensions/fields/payload IDs/reserved bytes; source and mask provenance; exact exporter; protected owners | Byte-identical fresh export; finite reviewed owner delta; current replay rejection, one-way metal blocking, 16 MiB cap and 65,536-event bound |
| Front | Exact accepted resource/header pins and source boundary | Original accepted source SHA still reproduced from guarded live bytes; native ordered sprite/underlay/occlusion checks |
| Generator | Exact accepted resource/header/script pins and source boundary | Original accepted source SHA still reproduced; native ordering, placement and fallback checks |
| Menu | Exact original menu assets and bounded seven-run SMR1 lease at its recorded public stage | Current code deliberately migrated to shared RFR3; generation invalidation, fixed-slot bounds, exact text, output placement and family retirement checked separately; current reconstruction native harness, not obsolete SMR1 structure access |
| Product | 22 observer-only calls, preserved original menu lines, bounded update tail/cash/footer, replay | Original public diff plus live static-count merge/event/replay guards and native update/retirement cases |

`SF_EVENTS=40000` remains true for the historical projected stages; current
`SF_EVENTS=65536` and `SF_CAP=16*1024*1024` are explicit public expansions, not
silently relaxed assertions. Current menu family resources are part of the new
exact inventory; the retired SMR1 loader is not falsely described as current.

Negative controls include real identity-validator rejection for mutated asset
bytes, new/deleted paths, changed finite owner deltas, more than 100 guarded
projection mutations, and source-structural guard removal without a hash gate.
Native semantic mutation evidence is recorded separately; string checks alone
are not claimed to prove runtime behavior.

## Limits and maintenance

Lost private commits and unrecovered intermediate menu-only bytes remain
unavailable. No new object is given an old identity. Current acceptance does
not prove the former intermediate whole-tree deltas, historical private
ancestry, Windows/GPU/fullscreen behavior, every gameplay route, or unrelated
public features. No new artwork was generated and nothing was published.

For future source/resource changes, review the finite public diff and rerun
positive, mutation and render checks before changing the new inventory. Never
update the receipt solely to make a hash failure green. Do not modify archived
specifications or describe a current pass as historical recovery.

## Runtime boundary (read before interpreting captures)

The native fixture executes current `pregame_font.c`, sprite/font code,
`common_menu_runs.c` and the SDL dummy/software presenter against restored game
banks. It does not execute the whole game loop. Its inherited
`render_mirror_pixel`/`render_mirror_rect` adapters dispatch to pregame, selector,
load and settings owners and track indexed writes; `render_mirror_text_glyph_*`,
`render_mirror_unsupported`, `title_layers_pixel`, `asset_debug_effect`, and pause
hooks are fixture stubs. Therefore captures are actual current SHOP renderer
outputs, **not whole-game observer-chain or gameplay integration acceptance**.

The legacy `run_pregame_font_tests.sh` and SMR1 `run_shop_menu_font_tests.sh`
runners are not the new canonical current gate: they predate shared RFR3/globals
and are retained unmodified as historical test infrastructure. The fresh adapter
links the current owner and loader explicitly. No passing old receipt is reused
as a current run.

The first native negative-control attempt revealed that deleting the idle-tail
`static_count` boundary survived the inherited 121-state core. This is a test
coverage gap, not evidence of a current production fault. The final adapter
adds a direct immutable-tail assertion; the initial result must remain in the
runtime audit alongside its rerun. Occlusion and alpha-order mutants were
already rejected by native pixel assertions. No failed mutant is counted as a
successful rejection merely because compilation failed.

The product contact sheet uses synthetic callback grammar: its repeated
Pulse-Cannon/Multi-Cannon rows and long test prices are deliberate fixtures,
not restored category-specific real shop inventory. Root-family captures show
finite fonts → metal → Talon → front → generator → shared-menu increments.
`--ubsan` instruments positive core and typography runs only; capture and
semantic-mutant binaries are plain native builds, explicitly labelled as such.

## Reproduce the complete current gate

Requirements: Linux C99 compiler (`cc` or `CC`), Python 3 with Pillow, Bash,
`realpath`, and SDL2 development headers/library (`pkg-config sdl2`). Supply
original game data, including the Tyrian item/sprite banks used by the fixtures.
Game data and SDL binaries are external inputs, not distributed by this patch.
If SDL2 lives in a separate sysroot, set `SDL_CFLAGS` and `SDL_LIBS`; set
`LD_LIBRARY_PATH` for its runtime library location when needed. The public repo
already supplies the unchanged SFN1/PMF1/sprite/RFR3/NFR1 resources.

```sh
# Use new, external output directories; no unrelated contents are deleted.
bash tests/run_shop_current_acceptance.sh /absolute/original-data /tmp/shop-current-plain
bash tests/run_shop_current_acceptance.sh --ubsan /absolute/original-data /tmp/shop-current-ubsan
```

Both commands run the 14 static checks, current core, current reconstructed
menu/product typography, three expected native assertion failures, and
capture/inspection. The plain gate and `--ubsan` gate are each fail-closed:
compile errors, missing data, an unexpectedly surviving mutant, malformed
staging or failed capture comparisons produce nonzero status. The UBSan switch
covers positive core/typography only; mutant/capture builds are plain in both
commands. A surviving mutant is never converted to a pass by catching its
failure outside the gate. Compiler/toolchain flags and exact input hashes for
the recorded runs are in the runtime receipt.
