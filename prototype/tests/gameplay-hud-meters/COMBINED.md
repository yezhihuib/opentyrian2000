# Combined HUF1/HUM2 source checkpoint

Base: `280e100a7204c907709a04f4186ec3b72d5542f2`, including the independently
reviewed HUF1 cache fix and published right4 mechanical checkpoint a50d257.
This is a new isolated source-only worktree. It does not change the HUF worktree,
main, artwork, resources, or asset manifests. Actual game rendering is a later gate.

## Integration boundary

The original HUM2 recovery-tests and feature changes are applied on this base.
The two production merge decisions preserve both additive sides:

- indicator cache retention uses all63 component bits and keeps `font_owned()`;
- shutdown calls both `hud_meters_shutdown()` and `font_shutdown()`.

All other HUF code and its source writers are unchanged. The combined oracle
requires byte-exact equality to280e100 for the HUF module/header/private renderer,
fonthand.c, sprite.c and mainint.c. Original tyrian2.c/varz.c changes remain only
the eight HUM2 observer calls. HUF has its own ledger/generation; HUM2 continues to
share HUC1's disjoint six-bit component ledger. No new production architecture,
owner arrays, resource format or authoring is introduced by the combined patch.

Shared renderer harnesses link both modules. The HUF source-extraction helper list
adds `layer3_mechanical_slot`, already required by the selected base. The older
finite geometry oracle retains its original hashes for the message writer and
unsafe glyph blitter: a test-only adapter removes only exact, counted HUF observer
strings and their two wrapped early returns. HUF's real-writer suite separately
exercises those observers. Other source tokens cannot silently drift.

## Finite combined proof

Run from repository root, with and without `--sanitize`:

```
python3 prototype/tests/gameplay-hud-meters/test_combined_hud.py
python3 prototype/tests/gameplay-hud-font/test_loader.py
python3 prototype/tests/gameplay-hud-font/test_renderer.py
```

The combined test constructs only deterministic synthetic resources. Both atlas
source guards refer to the same synthetic indexed PIC. No original asset bytes or
new art are created. Actual renderer, font/glyph/message writers and fade/cache
functions are source-extracted without changing their bodies.

- Active HUF with HUM2 absent is compared against exact280e100. Whole canvas,
  indexed surfaces, current/saved output, HD/cloud/live-green provenance, HUF
  hidden RGB and ownership, component ownership, textErase, cache flags and
  fingerprint are digested across ordinary frames, message replacement/expiry,
  modal/recreation and black/white restoration at densities4/8. Both digests are
  `3cdc524d668c3c80`.
- Simultaneous HUF/HUM performs32 whole-output and saved-output counterfactuals:
  densities4/8 × black/white × four fade/restore phases × either-family removal.
  Removing one family exactly matches the actual other-family-only run, retaining
  its current/saved generation. Removing the final family clears last-owner cache
  eligibility in both orders.
- Modal/recreation retains independent leases/history. An indexed generator
  mismatch affects its field; a full real write recovers it while HUF survives.
  Isolated saved-generation corruption in either family rejects presentation;
  valid ordinary frames recover without revoking the other family's lease.

Existing HUM2 and prior HUD suites remain required. The original no-HUM2/static-HUD
check against56efa261 also remains; its digest is `9d25d32b65aad19f`.

All evidence here is source/synthetic coverage. Linux compilation and disabled
syntax are checked separately. Windows project completeness is not a Windows
build. ASan/UBSan use `detect_leaks=0` because this executor's tracing environment
does not support LeakSanitizer; explicit bounded allocation/descriptor tests remain.
No actual game process, capture, publication or asset installation is performed.
