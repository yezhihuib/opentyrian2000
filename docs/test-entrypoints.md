# Counted CLI test entrypoints

Eight historical CLI oracles now also expose one counted `unittest` case each.
Importing a module does not parse the test runner's arguments, compile code, or
run an oracle. Its `load_tests` adapter invokes the original command in a fresh
subprocess and verifies exit status, nonempty output, and the oracle's receipt
(including positive checks/mutation counts where a JSON receipt is produced).
A main guard by itself is not a successful test: discovery must count and run
these cases. Their historical assertions are retained; fixing invocation does
not make an obsolete historical projection pass.

## Inputs and dependencies

Run the suite from the repository root, with the same Python used for Pillow:

```sh
export TYRIAN_TEST_DATA=/path/to/tyrian2000
python -m unittest discover -s tests -v
```

The four P10/P11 authentic-input checks require an explicitly supplied directory
containing `tyrian.hdt` and `tyrian.shp`. They validate the actual data fingerprints,
not merely file presence. No original game data is downloaded, generated, saved
or bundled by this adapter. Missing or invalid input is an explicit test error,
not a silent skip or a synthetic stand-in. Existing direct CLI invocation still
accepts the data directory as its sole positional argument.

The reconstructed menu loader requires a C compiler and SDL2 development headers.
Normal installed headers use `pkg-config --cflags sdl2`, respecting standard
`PKG_CONFIG_PATH` and `PKG_CONFIG_SYSROOT_DIR`. For an explicitly relocated Linux
package sysroot, use:

```sh
export TYRIAN_TEST_SDL2_SYSROOT=/path/to/extracted/sysroot
```

That directory must contain one `usr/lib[/<triplet>]/pkgconfig/sdl2.pc` (or
`usr/share/pkgconfig/sdl2.pc`). The helper sets pkg-config's sysroot and library
search directory for this invocation only. A unique Debian-style multiarch
`SDL2/_real_SDL_config.h` include directory is added when present. No global
system configuration is changed. Missing or ambiguous dependencies fail clearly;
they do not result in a passing/skipped native oracle. Pillow RAQM is also needed
by the existing independent raster oracle; its failure remains visible.

Each oracle receives a fresh temporary output location. Its subprocess output
and traceback are included in a failing unittest result. There is no tolerance
for a nonzero exit, empty output, absent receipt or a bare forged PASS receipt.

## SHOP boundary

The shield boundary continues to check its exact 72,992-byte material and all
existing schema/payload pins. The current SHOP group is checked against an
explicit set of 15 distinct destinations, including the three separately
approved static quads. Obsolete whole-package totals from an earlier release
are replaced by exact reconstruction of the complete current runtime manifest
from its finite approved inventories, rather than relaxed counts or arbitrary
new expected hashes.

This change only repairs invocation/dependency and package-boundary tests. It
does not repair missing historical Git objects or stale historical inverse
projections, and does not change game code, assets or rendering.
