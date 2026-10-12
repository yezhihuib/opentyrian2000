# Forest13 finite loader and sampler checks

The production module is `src/forest13_material.c` and `.h`. Its only runtime dependencies are the existing `ground101_fast_context`, `g101_fast_select_cap`, and `game_probe_hash` interfaces. The generated production index is copied unchanged from the approved builder. No existing lower/cap implementation is edited.

## Run

From a repository containing the module and existing world-material sources:

```
python3 prototype/tests/forest13/run_tests.py \
  --src src --reference-src src --output /tmp/forest13-tests
```

The source-only suite needs a C99 compiler and Python 3 standard library. It copies the exact production module into an isolated build directory, supplies a small declaration-only `game_probe.h`, and builds the existing world-material implementations directly. SDL, game data, PNG decoders, and third-party Python modules are unnecessary. There is no game run or screenshot capture.

To include the frozen-art loader checks:

```
python3 prototype/tests/forest13/run_tests.py \
  --src src --reference-src src --output /tmp/forest13-frozen-tests \
  --frozen-bundle-dir /path/to/generated/bundle \
  --frozen-sources /path/to/frozen/runtime-overlay
```

The bundle directory must contain `forest13-world-material.fcan`, `forest13.policy`, and its matching generated `forest13_bundle_index.h`. The selected-source directory must contain the thirteen density8 HDA files. These inputs are read only. `--output` must be a fresh directory outside the source directories; omit it for an automatically created temporary directory.

Add `--sanitize` for AddressSanitizer and UndefinedBehaviorSanitizer. LeakSanitizer is separately opt-in with `--leak-check`: the provided host does not support its ptrace-based process inspection. The tests independently assert payload allocation and free counts. GCC or Clang and compatible sanitizer runtimes are required for this optional mode. No linker wrapping, SDL test stubs, or GNU-only C APIs are used by the tests.

## Coverage

- Valid exact declaration, absence with valid/missing/bad sidecars, every marker truncation and byte mutation, unsupported version, extra and oversized data.
- Empty/overlong directory, unreadable marker/payload, directory, FIFO, dangling link, link loop, and symlink declaration handling. POSIX-specific filesystem cases are conditional; permission tests explicitly report a skip when running as root or on a non-POSIX host.
- Injected marker read error, short header read, short payload read, and allocation failure. Test-only I/O/allocation function substitutions apply to the exact loader translation unit, never to production sources or the callback.
- Exact bundle length, each magic byte, finite version/count/dimensions/density/payload size, each record role/ID/offset, duplicate/reordered inventory, every mask, atlas RGB/alpha, and final payload byte.
- Each of the thirteen missing, RGB-mismatched, and nonopaque sources; all-or-nothing record availability; no allocation before lower readiness or structural validation; one bounded setup allocation; cached success/failure; current-context invalidation/recovery; invalid/forged records and out-of-range coordinates.
- Source-only deterministic canopy atlas, thirteen independent mask phases, 9,599,296 oracle-checked sampler pixels, all source alpha and mask weights, both atlas axes, negative/extreme world origins, clipping, scroll continuity, exact zero-weight bytes, accepted alpha preservation, and unchanged lower lookup tables. The scalar expected-value calculation is independent of production sampling/blending functions.
- Physical pack rename/move leaves valid behavior unchanged.

The full synthetic-plus-frozen run executes 484 loader cases. Without frozen inputs, the 242-case synthetic suite and full sampler oracle still run.

## Runtime contract and limits

`forest13_policy_check` is cached independently of lower material readiness. It returns true only for the exact supported marker; `forest13_declared` also stays true for present-invalid and inaccessible declarations. Unix `lstat` and Windows `GetFileAttributesA` conservatively reject declaration links/reparse points before reading, including dangling links. A truly absent marker opts out. Nonempty paths that cannot be inspected are conservative failures.

The first valid lower context permits the sole payload/source preparation attempt. All structural bounds are checked before allocating exactly 3,311,616 bytes. The complete header+payload FNV64 and every selected source FNV64 are checked, along with opaque atlas/source alpha. FNV detects accidental corruption; it is not authentication. Build-time audits establish approved mask geometry; runtime fingerprints pin those bytes.

The selected pack and its directory are immutable for the process lifetime, matching the existing HDA caches. Tests can explicitly reset private state under `FOREST13_MATERIAL_TEST`; production exports no reset. Sampler calls use the existing current-frame lookup context and allocate nothing. No new frame context, per-pixel modulo, or per-pixel geometric lookup is added.

The lookup callback owns exact role/index/slot, density8, 24x28, anchor0,0 and payload-length validation. The loader cannot recover those header fields from an RGBA pointer. Renderer binding/style/registry gates, actual eight-row lower preflight, and original indexed fallback are separate integration tests and are not claimed by this isolated suite.

Unix production flags were checked with the actual SDL headers and `-DTARGET_UNIX -std=iso9899:1999 -pedantic -Wall -Wextra -Werror`. The Windows branch was source-reviewed only; no Windows cross-compiler was available. File type is checked before reading; as with the existing immutable asset loader, this does not claim a defense against concurrent hostile filesystem replacement.
