# Current Rear Multi P7 shared authoring

## One editable source, four existing outputs

Edit only `authoring-inputs/rear-p7-current/master-294.svg`. It is the approved P7 mode-2 twin diagonal master, copied byte-for-byte from the frozen `player-rear-multicannon-p7-mode2-twins-v1` package. The current layer produces raw 294 and 295 at densities 4 and 8 (role 131, identities 1310294/1310295). Each density is rendered independently from the vector; 295 is an exact full-canvas horizontal RGBA flip of 294, not a separately editable SVG or resized density. Logical geometry remains 12×14 and anchor `(0,0)`.

The other 44 Rear transports and every Front resource are outside this edit family. In particular, this is not shared with Front raw 163/164. Frozen artwork, original source pins, record pins and historical evidence stay unchanged. The old diagnostic `rear-multi-295.svg` is not a current input.

## Fixed renderer contract

`scripts/current_rear_p7_compatibility.py` uses a fixed subprocess argument vector and a non-executable JSON recipe. The installed Linux Node executable must report **v24.22.1**, and Sharp **0.35.5** plus its entire dependency-version dictionary must match. A fixed approved vector golden independently verifies all four PNG/RGBA outputs on each derivation. The frozen P7 builder recorded Node v24.19.0 but did not enforce it; the current compiler explicitly pins the actual verified environment instead of pretending these versions are identical.

SVG input is bounded to 64 KiB, strict UTF-8, 256 nodes, nesting depth 16, attribute values 8192 characters, and finite numeric magnitudes at most 10000. Only the finite vector/gradient grammar is accepted; declarations, entities, processing instructions, external references, images, scripts and CSS are rejected. The canvas/viewBox are fixed. The renderer receives input over stdin with no inherited Node options, a private working directory, a 30-second timeout and a 128 MiB **V8 heap** setting. The latter is not a total native-memory limit. Captured output size is checked after process completion, not a live disk quota. There is no fallback rasterizer, automatic tool installation or network fetch.

Straight RGBA is retained; RGB is explicitly zeroed where alpha is zero, matching the approved recipe. PNG compression level is 9 with adaptive filtering and palette disabled. No image resampling, recentering or eligibility change occurs. The embedded golden is immutable compiler validation data, not a second editable semantic master.

## Stage / review / apply

1. Edit the canonical SVG, preserving the fixed geometry and accepted vector grammar.
2. Copy `assets/hd/authoring/rear-p7-current.json` to an external candidate JSON. Set `schema` to `opentyrian-current-rear-p7-candidate-v1`, remove `resources`, update `masters[0].source_sha256` to the SHA256 of the edited SVG, and choose a version label. Keep the recipe path/hash and master selector/path unchanged.
3. Run `python3 scripts/build_current_rear_p7.py stage --selection /absolute/candidate.json --stage /absolute/new-stage`.
4. Review its plan and four derived PNGs. Run `python3 scripts/build_current_rear_p7.py apply --stage /absolute/new-stage`.
5. Run `python3 scripts/build_current_rear_p7.py check` and the relevant package/renderer tests.

Stage does not mutate the repository. Apply regenerates and verifies the complete finite plan, current fingerprints and staged bytes before writing. Handled write errors restore the old bytes. This is not process-crash/power-loss atomicity or a concurrent-writer lock; use one writer and restage after any input change. Synthetic test edits are propagation evidence, not approval of new artwork.

## Runtime consumers remain unchanged

The four existing `assets/gameplay/rear-multicannon-p1-bank8-{294,295}-{4,8}.hda` destinations now read the current transports. The formal runtime still has 1029 rows; global registry still has 120 identities. Shared previews have 190 overlays. The finite current input closure is 11 paths plus the compatibility mapping.

`src/current_rear_multi_payload_pins.h` precedes the frozen Rear pins header. It overrides the same 25×2 payload table while only allowing the four 294/295 cells to change. All other cells remain frozen, including unsupported d4 182/183 zeros. The `#ifndef REAR_P1_RGBA_PINS` guard preserves the existing synthetic fixture mechanism. It does not bypass the ordinary production gates.

Rear uses its dedicated role-131, 80-slot record/birth/lifetime path, not the generic player or sidekick loader. Normal and existing shadow consumers use the same payload authority; `rear_multi_p11_shadow.inc` already covers all 22 P1–P11 records. Source/record checks, density support, slot lease, normal/shadow eligibility and blend code are unchanged. Source inventory gains one generated header (274 files); the historical helper verifies an exact one-include inverse before projecting to the previous source binding.

## Evidence scope

Focused authoring tests cover exact public bootstrap PNG/HDA hashes, four-output edit propagation, full RGBA flip, transparent-RGB canonicalization, fixed non-P7 pin cells, malformed/encoded SVG rejection, strict tool/golden failure, stale/tampered transaction rejection and handled rollback. Integration tests cover exact source inverse, unchanged other Rear/Front resources, runtime/package closure, preview mapping and other builder dependencies.

Linux asset export or native wrapper tests are not Windows execution, physical-GPU acceptance or natural campaign/weapon-fire coverage. Further build/native/history results belong in their separately verified receipts; no public upload is part of this local implementation.

Completed local receipts:

- `current-rear-p7-validation.json`: 11 focused tests and current builder check.
- `current-rear-p7-transaction-validation.json`: a real isolated SVG edit bound 526 inputs, regenerated 13 outputs, passed stage/apply/check and a real second-write failure rollback. Both Linux and Windows asset-layout exports verified all 1029 rows. Exactly the four P7 payload destinations and source-binding document differed from the bootstrap; the other 1024 runtime entries were byte-identical. These exports contain no game executable and do not establish runtime readiness.
- `current-rear-p7-build-validation.json`: six fresh Linux builds, comparing the public baseline and current candidate in opt-in, default-off and mirror-disabled modes. All 86 object pairs per mode (258 total) and all three executable pairs match byte-for-byte. Build input and private sysroot inventories were stable; this is compile/link evidence only.
- `current-rear-p7-independent-review.json`: independent final compiler review, strict UTF-8/16/32 declaration and finite-number rejection, golden/mirror/payload-table checks.
- `current-rear-p7-history-review.json`: independent exact 274→273 source inverse, five projection tests, fixture macro precedence and unchanged gates/pins review.
- `current-rear-p7-native-validation.json`: independent bootstrap and real-edited 48-HDA tests with actual production payload pins, including cold/warm loader and normal/shadow lease checks. Original bank/record controls remain synthetic and normal draw is an observer, not compositor pixels. The reusable `tests/current_rear_p7_native_validation.py` runner keeps frozen historical harnesses unchanged and provides an explicit neutral shim for their 16 missing unrelated observer hooks.

### Final validation revision distinction

The full historical aggregate passed **54/54** in 3990.659 seconds with an unchanged 6909-file input snapshot. Its compiler was the pre-symbolic-token-guard revision (`01013d64…`), not the final revision. A later two-line parser guard rejects literal NaN/Inf/Infinity values case-insensitively; it changes only invalid-input admission. The final revision (`c09a317d…`) passed 12 focused tests, seven added token probes, independent mixed-case/Unicode probes, exact golden checks, 14 integration/projection tests, bootstrap check, and real edited stage/apply/check. All 13 edited outputs remained byte-identical to the previously native-tested edit. This is not a claim that the full historical aggregate was rerun after that guard. See `current-rear-p7-post-token-review.json` and `current-rear-p7-post-token-validation.json`.
- `current-rear-p7-portable-native-validation.json`: the installed reusable runner was executed again from the final worktree and passed all synthetic adapter/shadow and real-48-HDA shadow/cache lanes, including ASan/UBSan. This remains synthetic bank/record controls with real loader/payload pins, not compositor pixel acceptance.
