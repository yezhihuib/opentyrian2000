# Rebuilding the public second-level baseline

Start from a fresh checkout of `hd-render-prototype`. The restoration baseline
is commit `f7608ea06d0d896f018d28087f338bac2bfd53ff`. It contains the 52-asset,
24-terrain-member level-2 family package, plus a separate source-only late-level
candidate. It does **not** contain or restore later private development.

## Dependencies without a system install

Prefer your operating system's SDL2/SDL2_net development packages. If system
package installation is unavailable, the following optional helper uses pinned
release commits from the official SDL repositories and installs into a **fresh
user-owned directory outside this checkout**:

```sh
python3 scripts/build_local_sdl_dependencies.py --output ../opentyrian-sdl-deps
python3 scripts/build_local_sdl_dependencies.py --output ../opentyrian-sdl-deps --build --jobs 4
export PKG_CONFIG_PATH="$(cd ../opentyrian-sdl-deps/prefix/lib/pkgconfig && pwd)${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
export LD_LIBRARY_PATH="$(cd ../opentyrian-sdl-deps/prefix/lib && pwd)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
python3 scripts/build_level2_family.py --jobs 4
python3 experimental/late-level/build.py --jobs 4
```

Without `--build` the helper only prints its plan. An existing output directory
is rejected rather than reused. It requires Git, a working POSIX C/C++ toolchain,
make and the ordinary configure utilities; it does not install those tools or
OpenSSL development headers/libcrypto. It performs no root operation and changes
no system configuration. Logs and a success/failure receipt stay in its output.
The SDL backend set is detected on the build machine; a successful build does
not certify desktop, audio, GPU or display capabilities. Neither the helper nor
the game build scripts launch the game.

SDL is pinned to release 2.32.4 and SDL_net to 2.2.0. The script checks the exact
commit after cloning and refuses a moved tag. For SDL_net, it refreshes only the
modification times of the release's already-generated Autotools files, avoiding
unnecessary regeneration after a Git checkout. It changes none of their bytes.

## Fast baseline checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_level2_family_release.py -v
PYTHONDONTWRITEBYTECODE=1 python3 experimental/late-level/test_release.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_local_sdl_dependencies.py -v
```

These are package and isolated code checks, not game acceptance. Original game
data and a supported graphical session are still needed for gameplay. Preserve
the documented default-off and normal-only boundaries; do not activate a source
family whose matching art or configuration is missing.

## Checkpoints

Commit completed source batches and verify the commit on the remote. A local
commit, bundle, or archive is not independent storage. Keep unpublished assets
and intermediate work in a separately saved private archive; verify a readback
before removing the only local copy. Record the base commit and exact asset
hashes, and explicitly distinguish newly rebuilt material from recovered data.
