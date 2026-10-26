# Fresh Linux SHOP runtime evidence (2026-10-26)

These are fresh checks of the current public `f58647e7ff74e2276a1413b3675e651f1232bb41`
production source/assets, not recovered historical acceptance or historical screenshots.
The five original private-tree proofs remain unavailable. No production file was
changed to make these tests pass.

## Reproduce

Use original authenticated Tyrian data and SDL2 development headers/library.
In a normal SDL2 installation, pkg-config supplies flags. A private relocated
sysroot can instead use `SDL_CFLAGS`, `SDL_LIBS`, and `LD_LIBRARY_PATH`.

```sh
bash tests/run_shop_current_acceptance.sh ORIGINAL_DATA_DIR /absolute/external/plain
bash tests/run_shop_current_acceptance.sh --ubsan ORIGINAL_DATA_DIR /absolute/external/ubsan
# Optional separate rerun of either stage after preparation. Export flags in
# this shell first (the bash runner cannot export back to its parent shell):
export SDL_CFLAGS="${SDL_CFLAGS:-$(pkg-config --cflags sdl2)}"
export SDL_LIBS="${SDL_LIBS:-$(pkg-config --libs sdl2)}"
python3 tests/shop_current_runtime_mutations.py ORIGINAL_DATA_DIR /absolute/external/plain
python3 tests/shop_current_capture.py ORIGINAL_DATA_DIR /absolute/external/plain
# Additional independent shared-loader/raster oracle, with normal pkg-config or
# TYRIAN_TEST_SDL2_SYSROOT pointing to the relocated sysroot:
python3 tests/test_reconstructed_menu_runs.py /absolute/external/shared-loader
```

The full runner requires the static current gate, native positive tests, all three
expected semantic mutation failures, and SDL capture comparisons. A compile error
is not a killed mutant. Unexpected leftover resources, symlinks and nonregular
staged files are rejected rather than silently reused or removed. Missing SDL/data
is a failure, never a skip. Builds are capped at 1 GiB; runtime at 512 MiB.
Mutant and capture compiler/runtime subprocesses additionally have 180-second
limits. `--ubsan` instruments **positive core and typography only**; the mutation
and capture stages deliberately build plain code, and are not claimed sanitized.

## Positive and negative meaning

- Core: 121 states / **13,145,152** checks; exact indexed/write replay, independent
  continuous-alpha oracle, ordered hull → generator → front, full 4×4 same-index
  occlusion, frame/sprite fallback, malformed resources, sibling independence,
  product bounded updates and fixed command/event budgets. Static bytes 915,624;
  tracked peak-owned bytes 7,909,204. These memory figures are harness-accounted
  allocations, not OS peak RSS.
- Current typography: 126 states / **16,252** checks; real shared RFR3 loader,
  authenticated name/numeric admission, retained command retirement, original
  reference cold/warm behavior and generation/family isolation. Retained bytes
  12,272,367 (<16 MiB), shared all-family bytes 3,324,879, numeric 46,398.
- Additional shared-loader/raster oracle: 1,009 whole-string cases, 5,297,472
  independent alpha pixels, 16 invalid canonical strings and 2,631 mutated-resource
  negatives. See `shared-loader-receipt.json` (separate from full runner).
- Mutants: 3-row instead of 4-row classic occlusion must fail the explicit cleared
  sample assertion; sprite overwrite instead of alpha accumulation must fail the
  independent compositor oracle; crossing the retained-static command boundary
  must fail `sf.count==2&&sf.event_count==2`. The driver requires each exact
  expected assertion, not just an arbitrary failure.

The initial existing core **did not reject** the retained-static boundary mutant.
That useful gap is preserved in `initial-mutation-results.json` and
`initial-idle-static-merge.log`. The new adapter adds five focused assertions:
a subsequent idle write creates a new command/event and leaves both retained
command and event byte-identical. Only test code changed. The original legacy
runner also failed to link newer current dependencies; its failure is preserved
as `legacy-runner-link-failure.log`, not relabelled as a test pass.

## Actual SDL render comparisons

The versioned capture harness calls current `pregame_font_present` through a real
SDL software renderer, captures 50 BMPs, and uses independent image comparisons:
6 root variants (fonts, metal, hull, front, generator, current RFR3 menu) ×
3 dimensions (640×400, 1280×800, 913×599) × classic/HD, plus 7 product-category
synthetic grammar pairs. Six root INDEX8 buffers and every classic RGB pair are
identical. Front-only and generator-only HD changes must stay inside their
original rectangles (fractional output allows a 2-pixel sampler margin).

At 640×400, the measured front bbox is `(122,96)-(188,164)` and generator bbox
`(124,168)-(186,236)`; at 1280×800 they are `(244,192)-(376,328)` and
`(248,336)-(372,472)`. This implies unchanged right-menu pixels for these two
resource additions. JSON capture inventories bind the exact saved BMP bytes;
hashes alone are not the acceptance oracle.

The root and product contact sheets were visually inspected: additions are
aligned, text remains legible, and no unexpected rectangle spill was observed.
Product captures intentionally reuse synthetic Pulse/Multi labels under each
category heading: **they are grammar fixtures, not real inventories or actual
purchases**. Product category scopes/fallback are exercised, not all live game
navigation states. The snapshots do not approve a new art design.

## Integration limits

Production pregame presenter, sprite blitters, sampler and shared menu loader
are compiled directly, not inverse-projected or replaced by old fixtures. The
existing test fixture supplies data/globals and an explicit render-mirror test
adapter; `title_layers_*`, `asset_debug_effect`, glyph mirror callbacks and pause
callbacks are inactive/stubbed. Thus this is not a test of the full production
observer integration, actual game-loop navigation, purchases, input, RNG,
Windows, GPU presentation, or exhaustive equipment inventories. No older private
SDL navigation route was recovered, and no such claim is made.

Raw BMPs remain outside the repository; see the adjacent evidence manifest for
exact external locations and file hashes. Only bounded logs, JSON receipts and
contact sheets are retained here.
