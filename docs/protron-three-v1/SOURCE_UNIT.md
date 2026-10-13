# Isolated Protron source/unit proof

Status: PASS in `run-3/result.json` with ASan and UBSan enabled. LeakSanitizer is disabled for the ptrace-based executor. This is a source/unit result, not a gameplay, screenshot, visual-quality, or native-presentation result.

## Final results

Each candidate default pack (preview and debug) passes:

- 28,848 finite bank/layout/ID cases in normal and Christmas modes
- 29 metadata/cache checks, including reverse load order and Christmas rejection before cold and warmed cache access
- 1,032 indexed/RGBA transactions: 665 HD accepted and 367 indexed fallbacks
- 13,867,232 affected-subpixel comparisons and 50 complete frame comparisons
- 54 guards and 12 real compositor blend rejection/local-restoration cases
- 589,824 straight-alpha operator comparisons, including alpha 0, 1, 17, 63, 127, 128, 191, 254, and 255

The pinned baseline also passes the same bounded suite against both current packs. It has no Protron mapping and therefore keeps those transactions indexed. The report includes both runs, compiler flags, source/function hashes, input hashes, and fixture variants.

All 142 production `.c`, `.h`, and `.inc` files are checked against commit `e54ebee1884c3131153f806ab65ab12989639e10`. Removing exactly four approved renderer fragments (xmas include, capacity, three-ID mapping, indexed-shadow exception) gives byte-identical pinned source. No other production source is changed.

## Coverage

The proof reuses the compact regular-missile finite enumeration and enemy-energy/Pulse compositor approach. Production loader, selectors, entity/scene wrappers, original RLE blits, compositor, pixel hook, local restoration, and reset functions are extracted unchanged from each supplied source tree.

Actual frozen HDA pixels are checked for all three Protron heads. The proof covers normal and reversed cache order, neighbors, wrong bank/layout, cold and warmed Christmas rejection, all missing-member combinations requested (each member separately and all three), every HDR1 field, short header, truncated payload, trailing bytes, valid 4x files, malformed 8x with valid 4x fallback, and indexed fallback at density 4 with the current 8x-only packs.

Pixel cases include transparent preservation, original indexed writes, original indexed shadows, mixed prior ownership, ordered overlapping heads, horizontal/vertical clipping, indexed pitches 320 and 328, and padded RGBA rows. Actual alternate Christmas244 indexed pixels are used. Prior player metadata and Pulse58/Missile31 rendering are checked. Explicit enemy-hook/wrapper negatives and direct indexed calls remain original. All enemy/shop/Christmas caller files are byte-identical to the pinned baseline.

## Reuse

The Python runner accepts all inputs as CLI paths and creates a fresh output directory outside the supplied candidate, baseline, and artwork trees. The two harness files can be copied together without the generated run directories.

```sh
python3 test-protron-binding.py \
  --candidate /path/to/candidate \
  --baseline /path/to/pinned-baseline-repository \
  --art /path/to/formal-player-protron-three-v1 \
  --original-data /path/to/tyrian.shp \
  --xmas-data /path/to/tyrianc.shp \
  --source-packet /path/to/PROTRON_SOURCE_PACKET.json \
  --out /path/to/fresh-external-output
```

The baseline must be a Git checkout at the pinned commit. The candidate need not be a Git checkout. The approved candidate source and HDA inventory are verified before compilation. Compiler and run stdout/stderr are retained per source tree and pack.

## Boundaries

- No game binary was started; no gameplay capture or upload/publication occurred.
- No production source, wrapper, loader, compositor, game data, or artwork was edited by this test task.
- Font notification/pixel integration is stubbed. Material-specific routes fail if entered. The test does not claim coverage for those separate systems.
- The global unsupported callback records the rejection reason. Its caller, the actual unchanged generic compositor, is tested, but full-frame rejection recovery is not simulated.
- Blend cases exercise the actual compositor rejection and unchanged local-restoration function; they do not claim successful generic-bullet HD blending.
- Original-data fixtures (`bank.bin`, `xmas-bank.bin`, `reference.bin`) are private generated test inputs. Keep generated run folders external to source/distribution packages; distribute only the two harness files and this README unless separate permission covers the inputs.
- `run-1` records a harness compile error corrected before execution; `run-2` is the first passing suite. `run-3` is the final expanded, passing result.
