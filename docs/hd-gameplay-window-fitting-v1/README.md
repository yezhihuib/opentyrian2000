# Smooth fitting for the development HD gameplay renderer

The 112-unit `opentyrian2000-family` development build now uses linear sampling
when its final HD gameplay texture is fitted to a fractional logical-pixel
output size. This reduces the uneven fine edges produced by nearest-neighbor
fitting in freely resized or letterboxed windows. The paused gameplay snapshot
uses the same rule, so pausing does not change the background's sampling.

Integer logical output sizes keep the established nearest path, including
640x400 (2x), 1280x800 (4x), and stretched integer-axis output. This is final
texture sampling only, not a change to authored pixels, INDEX8 drawing,
collision, gameplay speed, input, RNG, assets, or the classic scaler. It does
not claim area-filtered downsampling or new art detail.

## Scope and fallback

- The existing development build/launch entry points select this code. No new
  CLI flag or environment variable is needed. HD owner admission is unchanged.
- The rule accounts for SDL renderer scale as well as the destination size.
  It matches SDL's float multiplication and software renderer integer extents.
- Each presentation selects its mode again, including after a window resize.
  Renderer scale, viewport, clip and texture blend mode are not changed.
- If linear filtering is rejected, the texture falls back to nearest. A failure
  of nearest setup is returned to the existing presenter fallback.
- The canonical 86-unit source tree, all assets/runtime manifests and the frozen
  Windows launch/build chain are byte-for-byte unchanged. This feature is only
  in the development overlay. It is not an update to the frozen Windows build.

Build the development executable using the existing workflow:

```sh
python3 scripts/build_level2_family.py --jobs 4
```

See [the development rebuild instructions](../level2-family/REBUILD.md) for SDL
setup and external original-data requirements. This change does not launch the
game or install anything on the user's computer.

## Bounded verification

```sh
python3 -m unittest discover -s tests -p test_hd_gameplay_scaling.py -v
SANITIZER_FLAGS='-fsanitize=undefined -fno-sanitize-recover=all' \
  tests/run_hd_gameplay_scaling_tests.sh
```

The real SDL software-renderer test uses synthetic opaque HD patterns at source
4x and 8x. Twenty-six output cases cover twelve unchanged integer outputs and
fourteen fractional outputs. New output is compared pixel-for-pixel with the
expected nearest/linear reference; differences remain inside the destination.
Additional checks cover repeated size changes, renderer scale, clip/viewport
preservation, the 2/3 float-rounding case, software truncation at scale 1.001,
invalid arguments, and injected linear/nearest setup failures. The helper itself
is compiled with C99, pedantic warnings and `-Werror`.

Focused plain/UBSan tests, the four counted integration tests, eight development
package tests, runtime source-binding tests and a complete 112-unit Linux build
pass. Current canonical source and runtime metadata verification also pass.
The synthetic patterns are **not game screenshots**. No original game data was
available in this cloud workspace, so real gameplay, motion-quality judgment,
accelerated GPU output and Windows runtime remain unverified. Linear sampling
is expected to soften edges; its visual preference should be checked in a later
user-observed game run rather than inferred from these synthetic tests.
