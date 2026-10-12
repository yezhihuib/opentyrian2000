# Finite world-material tests: two-part packaging

These standalone tests do not start the game, capture images, load artwork by default, or use private absolute input paths. They require a C compiler, Python3 and SDL2 development declarations. Production uses the existing project FNV helper; `fnv_reference.c` extracts that helper only for standalone testing.

## Run

```
python3 /path/to/tests/run_tests.py --src /path/to/src --output /tmp/new-ground101-tests
```

The output directory must be fresh. Set `PKG_CONFIG_PATH` for a custom SDL2 prefix and `CC` to select the compiler. Assertions must remain enabled.

The default run uses synthetic data only: 9,847,539 scalar assertions, 458,752 independently calculated footer-weight combinations, 49,152,000 full-canvas scalar/fast samples, 65,536 composition/alpha cases and 27 split-loader cases.

## Validate an approved pack

```
python3 /path/to/tests/run_tests.py --src /path/to/src --output /tmp/new-ground101-pack-tests --approved-pack /path/to/selected-pack
```

The pack must contain:

- `ground101-world-material.g101.0`: exactly 8,388,608 bytes, including the original 764-byte header/inventory.
- `ground101-world-material.g101.1`: exactly 7,998,204 bytes, with no added part header.

The harness validates both exact lengths before reconstructing the logical 16,386,812-byte stream. It adds eight cases, for 35 total: successful reconstruction, corruption in either/both parts, mixed approved/synthetic parts and incomplete approved packs. Success also tests 26 finite actor states and invalid-context reset. The runtime still allocates only one 16,386,048-byte payload after structural validation; no reconstructed-file buffer or temporary file is used by the runtime.

`--approved-bundle /path/to/original.g101` remains available as a mutually exclusive alternative for a retained private combined oracle. It is not required by the published pack. Optional `--rejected-bundle /path/to/unapproved.g101` adds one structured-but-unapproved identity test, bringing the complete suite to 36 cases. The tests never modify input packs.

## Coverage

`check_loader.py` constructs missing either/both parts, truncated either/both parts, swapped parts, extra bytes in either/both parts, malformed magic/version/count/dimensions/density/size/inventory, duplicate inventory and rejected synthetic identity. A legacy unsplit file alone must not activate the feature. Structural failures allocate no payload. Valid-layout corruption reaches at most one bounded allocation, then disables coherently. The C validator checks that disabled loads expose no material records, Layer1 context or eligible actor. Selected-pack fallback is retained. No default material trace files are allowed.

`validate_portable.c` also mutates fixed compiled-layout counts, spans, duplicates, slots and footer offsets to prove checks do not rely on the checksum. FNV64 detects accidental corruption; it is not authentication. External SHA256 receipts identify the approved logical stream and physical parts.

## Sanitizers

```
ASAN_OPTIONS=detect_leaks=0 python3 /path/to/tests/run_tests.py --src /path/to/src --output /tmp/new-ground101-sanitized --sanitize --approved-pack /path/to/selected-pack
```

Use `detect_leaks=0` only when LeakSanitizer is unsupported under the execution environment's tracing restrictions; ASan and UBSan remain active. The suite also compiles the opt-in trace module. Standalone tests do not replace full normal/RENDER_MIRROR_DISABLED builds or actual no-capture state and whole-frame RGBA-audit equivalence.
