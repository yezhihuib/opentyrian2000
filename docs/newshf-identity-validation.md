# NEWSHF identity-validation prototype (classic pixels unchanged)

> Historical phase receipt. The separately opt-in actual compositor is now
> documented in [NEWSHF HD compositor](newshf-hd-compositor.md); the original
> limits and results below describe this earlier phase, not its successor.

This is a **default-off diagnostic observer**, not NEWSHF HD integration. It
validates identities submitted by the real allocation/initialization/draw path.
It never loads an HDA, draws a pixel, grants a rendering role, suppresses an
indexed blit, changes animation, or changes gameplay/RNG. The existing nine
selected PNGs remain source-only candidates. No package destinations are added.

## Enable only for diagnostic builds

Compile with `-DNEWSHF_IDENTITY_VALIDATION=1` and the mirror code enabled.
Without the flag, with value `0`, or with `RENDER_MIRROR_DISABLED`, all observer
calls are compile-time no-ops. No environment variable or game option silently
enables it. Enabled diagnostics repeatedly hash the bank and records and are not
a performance-qualified gameplay mode. The observer's internal counters are available to the native harness
or a debugger; there is no new HUD, log stream, or user-facing acceptance claim.

The flag does not broaden `mirror_enabled`, manual/asteroid scope, generic bank
routing, or global asset eligibility. It does not install or publish anything.

## Exact bounded proof

- Logical enemy bank **10 / NEWSHF**, not static `spriteSheet10`.
- Records **163, 167, 168**, exact canonical 77-byte serialized record stamps.
- Pose order **125/123/127**, **3/1/5**, **55/17/93**, respectively.
- `ani=1`, `animate=0`: native pose selection is observed, never advanced.
- Ordered native quadrant offsets **0, 1, 19, 20**, logical 24×28 composite,
  anchor (6,7); the actor's native vertical visibility controls which quadrants
  are submitted. These are submission witnesses, not proof of clipped pixels.
- Exactly one currently loaded logical-bank slot; retain its slot-object,
  data-pointer, size, whole-bank stamp and bank-lifetime epoch from allocation
  through initialization and each observed tile. This rejects stale inherited
  `sprite2s`, duplicate logical IDs, alias objects and same-address reloads.
- Allocation generation and initialization witness, exact current actor record
  pointer and all twenty egraphic fields, static-animation/damage state, selected
  pose, position, filter and matching source quadrant stamp.
- Full palette5 equality is intentionally conservative; a different valid
  palette can decline validation. This is not evidence of actual E1 acceptance.

The generator verifies immutable original bank/table/palette SHA-256 pins before
producing the small header. Runtime checks use the existing FNV64 integrity
pattern, **not cryptographic authentication**. Only hashes/identity metadata are
stored; private original bytes are passed to tests over stdin and never bundled.

## Lifetime and failure behavior

A separate diagnostic frame tick runs before renderer admission early returns.
Every actor allocation retires the old slot role, even for unrelated records.
Normal death/despawn retires that actor locally; an unwitnessed actor cannot
repeatedly poison a newly allocated actor. Invalid family source/record proof,
mutated live identity, reordered or interrupted submitted quadrants revoke the
family's existing witnesses. Rejected actors remain ineligible until a fresh
allocation/initialization, without changing the underlying actors.

Both enemy-bank free and load callbacks revoke witnesses **before** the backing
bytes can change, even if an allocator later reuses the same address. Level/map
reset, resource-root change and shutdown also revoke witnesses. No saved pointer
is dereferenced to recover an old bank; only the currently bound object is read.

Counters `tiles` and `assemblies` are cumulative diagnostics. An assembly means
one complete **visible submitted subset**; prior counts are not rolled back on
later rejection. They are not a complete frame/family acceptance certificate.
There is no partial HD contribution to discard because this prototype draws none.

## Reproducible checks

```sh
python scripts/check_newshf_phase_a.py
python scripts/build_newshf_prototype_pins.py
python -m unittest discover -s tests -p test_newshf_prototype_pins.py -v
# Optional private original-byte verification; original files are never copied:
python scripts/build_newshf_prototype_pins.py --game-data "$PRIVATE_GAME_DATA"
python tests/newshf_identity_validation.py --original-data "$PRIVATE_GAME_DATA" --out "$PRIVATE_VALIDATION_OUT"
```

The native harness includes the actual observer, current production structs,
source decoder and extracted `JE_makeEnemy`. A temporary-only
`--negative-control` removes the whole-bank hash check and must be caught by the
bank-mutation test; it never edits production sources. Its scope is a bounded native harness, not a whole-game run. ASan/UBSan are
enabled; LeakSanitizer is disabled because it cannot run under this container's
ptrace environment.
Compile/link checks and default-off object comparison likewise do not establish
Windows/GPU, E1 event timing, gameplay acceptance, or successful HD composition.

## Deferred work

See [the compositor hook audit](newshf-compositor-hook-audit.md). A future HD
owner must prove all pixel/order/occlusion/output/cache/fade/coexistence paths,
whole-frame rollback after transferred ownership, and exact nine-resource
build/package bindings. Those hooks are deliberately **not partially installed**
here. Existing approved family pixels and all historical art remain unchanged.

## Local verification result

For this prototype, the native harness passed 24,594 assertions with ASan/UBSan,
including all nine poses and 180 extracted-allocation equivalence combinations.
Its temporary bank-hash-removal negative control was caught as expected.
Thirteen source-freeze tests and twelve pin tests passed. Seventeen focused
source-history/authority/package tests and four independent inverse/negative
checks passed. The current 257-file source binding, current-art check and
1,015-destination package dry-run passed; only package validation metadata changed.

Using the retained SDL sysroot, full native builds compiled and linked in three
modes: default-off, identity-on, and mirror-disabled with the identity flag. The
three changed translation-unit objects (`render_mirror`, `sprite`, `tyrian2`)
were byte-identical to the pre-prototype baseline when default-off, after stripping
debug information with identical optimization/compiler flags. This is stronger
than a source-only no-op check, but is not a game execution or platform-wide proof.
