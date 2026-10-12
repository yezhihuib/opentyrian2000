# Synthetic plateau-cap oracle

Run against the explicitly selected production source directory and a fresh
output directory:

```sh
python3 prototype/tests/plateau-cap/run_tests.py --src src --output /tmp/cap-test-new
python3 prototype/tests/plateau-cap/run_tests.py --src src --output /tmp/cap-test-asan-new --sanitize
```

Only `world_material.c`, `world_material_fast.c`, and the synthetic C test are
compiled. No SDL dependency or game invocation is needed. The runner refuses to
reuse an output directory. `CC` may select a different C compiler; the linker
must support GNU-compatible `--wrap` allocation traps.

`--sanitize` enables AddressSanitizer and UndefinedBehaviorSanitizer. The
separate LeakSanitizer checker is off by default because ptrace-based sandboxes
cannot run it; allocation traps still run. On an unsandboxed host,
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1` opts into that additional checker.

The suite checks:

- An independent 64-bit integer blend oracle for every accepted-channel,
  cap-channel, and weight combination, independently covering all RGB channels
- Every accepted alpha byte against every weight, exact full-weight RGB identity,
  and preservation of accepted alpha even when the cap atlas is transparent
- Full-canvas scalar/fast equality across twelve transforms, with distinct
  synthetic lower and cap atlases, negative origins, wrapping, and extreme world
  coordinates; separate extreme 64-bit scalar screen-coordinate tests
- Byte-exact accepted fallback for zero weight, transparent source, invalid
  context, missing cap atlas, wrong atlas metadata/density, and fast canvas bounds
- Invalidation after failed prepare, recovery on the next valid frame, unchanged
  lower-material selection, and read-only reuse of bounded existing lookup tables
- Clipped and shuffled actor quadrants, buffer canaries, terrain row rollover,
  and the existing one-logical-pixel actor phase
- No allocation by the tested production paths, using link-time allocation traps

This suite does not load, validate, generate, or approve any asset pack or media.

## Loader, source package and renderer wiring

With the approved lower pack and generated cap sidecar available, run:

```sh
python3 prototype/tests/plateau-cap/check_loader.py --src src --lower-pack PACK --selected-pack PACK --cap-bundle FILE.pcap --output /tmp/cap-loader-new
python3 prototype/tests/plateau-cap/test_renderer.py --src src --output /tmp/cap-wiring-new
python3 prototype/tests/plateau-cap/test_package.py --src src --package PACKAGE --selected-pack PACK --second-pack OTHER_PACK --bundle FILE.pcap --output /tmp/cap-package-new
```

The loader harness requires SDL2 development declarations through pkg-config,
but it neither links SDL nor starts the game. Use PKG_CONFIG_PATH when needed.
`check_loader.py` and `test_renderer.py` also support `--sanitize`; use
`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` in ptrace-restricted environments.
The package test requires Pillow and does not mutate its inputs.

The40 loader cases cover missing/truncated/oversized files, all header fields,
duplicate/reordered identities, corruption in atlas/mask/base data, missing lower
dependency, and each of13 selected-source mismatches. Every case compares all
pixels of all61 lower records byte-for-byte before/after cap handling. The valid
case checks559,104 authored pixels against the independent cap formula,
including lower/footer protection and both zero guards. Structural and payload
mutation tests also bypass checksum dependence to test the actual invariants.

The16 extracted renderer scenarios check that no cap load precedes the lower
family's61 selected-source checks and valid Layer1 preflight. Cap-only failure
leaves lower selection active. NORMAL/Layer1/density/surface/context gates,
finite IDs, callback bank/ID/dimensions/anchors and actor/general exclusion are
checked. Source assertions additionally retain lower-to-cap-to-filter ordering
and the original clipped screen-coordinate calculation.

Package checks require the frozen inventory before any author rebuild invocation
and independently assert selected HDA identity, lower disjointness and semantic
rim geometry. They include absent/modified inventory, modified bindings/art,
each selected HDA, corrupted lower parts and forbidden output locations. They
can verify that both compatible selected packs reproduce the same sidecar.
