# Current Rear lobes native validation

This opt-in Linux/POSIX suite exercises production loading of the actual 48 Rear HDA payloads and current shared payload pins. It preserves original source/record guards, uses the unchanged historical synthetic bank and weapon-record fixture, a normal-draw observer, and production shadow preparation/lease checks. It does not verify original game-data admission, final compositor pixels, actual weapon firing, Windows/GPU execution, or a campaign.

Two independent multi-lobe masters, 203 and 43, are tested separately: each changes four density/direction outputs; together they change eight. The full edited five-family variant changes exactly 46 outputs. Historical 182/183 d8 payloads and the two unsupported d4 zero pins remain unchanged.

Run the portable runner with `--source-root ROOT --out NEW_DIRECTORY`. To reuse a prior synthetic fixture, supply `--fixture PRIOR_RUN/actual`: its source-file hashes and every recorded fixture-artifact hash must match before reuse. Reuse does not count as a fresh historical adapter execution. The wrapper adds only the finite pre-existing unrelated observer shims; no Rear observer is stubbed.

Run `current_rear_lobes_native_variants.py ROOT NEW_VARIANTS_DIRECTORY` to create independent actual master-geometry edits. Feed a variant to the runner using `--overlay VARIANT --pin-header VARIANT/current_rear_multi_payload_pins.h`. The derivation script records original source bindings and altered control points. It preserves separate input roots for each independent candidate, rather than rewriting authoritative repository inputs.

For a deliberate old/new mismatch, use `--wrong-pins lobes203`, `lobes43`, `rear281`, `rear1`, `rear39`, or `p7`. Correctly paired real resources are checked byte-for-byte, cached open counts, warm/cold backing-file behavior, normal versus shadow eligibility, and retained-birth invalidation. Every run compiles and executes plain and AddressSanitizer/UndefinedBehaviorSanitizer harnesses. These checks are finite behavioral assertions, not exhaustive process or concurrency guarantees.

The copied fixture and result directories are private validation artifacts. They are not part of the public asset package. Keep adequate free space and retain source bindings, logs and receipts before cleaning reproducible copies.
