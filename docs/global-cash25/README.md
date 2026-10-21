# Global Cash25 body and fixed value

This eighth shared-resource family reuses seven byte-identical approved 8×
resources: bank11 body tiles 7–12 and fixed newsh6 tile 185. No new artwork,
source animation, gameplay, collision, reward, input, RNG or sound logic changes.
The family has independent resource/source/lifetime proof, not a level allowlist.

## Native identity

- The actual `JE_makeEnemy` call must initialize a free global enemy slot from
  the exact serialized 77-byte record 391 and ordinary bank21 selector, which
  binds the global spriteSheet11. Three original table datasets have the same pin.
- The original animation-step hook records each six-phase transition before the
  vertical visibility gate. A coin born above the screen can therefore enter at
  a later phase without loosening phase checks. Native event/drop placement and
  movement remain unchanged; the draw still proves actual coordinates and slot.
- A body needs availability2, scoreitem, size0, exact animation/egr and source
  record, original value captured at initialization, no damage/filter, and part0.
  Wrong role, duplicate calls, reallocation, missing animation and observed death
  cannot revive a previous generation. Unsupported filtered calls stay classic.
- Fixed value185 requires the real original type36 allocator, sprite184, ttl8,
  fixed position, no following and deltaY0. It proves all eight ordered draws.
  Moving185, other amount types and raw sprite IDs cannot borrow the owner.
  The popup has an independent lifetime; legitimate pickup/body retirement does
  not invalidate an already-authenticated contribution in the current frame.

## Display and fallback

All seven resources must pass exact header/payload validation. Both source
banks and the record/palette are checked on warm calls and final/cached output.
The original indexed draws always execute. Body pixels use normal authored
alpha. Fixed value NORMAL uses authored alpha; BLEND preserves the existing
hue-overwrite/value-average analogue, not RGB half-opacity. Authored alpha is
coverage only. The 8× resources are sampled for 2×/4× final output, unchanged.

The owner participates in every existing global family's ordered ownership
transfer, native writes, final-surface writes, cache and fade handling. Observed
invalidation remains sticky even after pixels move to another owner and source
bytes/flags are restored. Missing/corrupt/wrong-context cases fall back to the
classic indexed result; enabling global resources never falls through to the
old unscoped cache for the selected body/value range.

## Verification

- `tests/test_global_cash25_registry.py` pins the seven exact approved resources,
  eighth family and native type36 table entry.
- `scripts/verify_cash25_source_identity.py` verifies original source bytes in
  memory only, including both banks, 18 palette indices and three record tables.
- `tests/global_cash25_identity.py` exercises the production identity helper and
  current production struct definitions with ASan/UBSan.
- `tests/global_cash25_reconstruction.py` runs the production renderer with an
  SDL shim, independent indexed/RGB oracle, malformed resources, source/role
  mutation, lifetime/transfer/cache/fade tests and observed-invalidation negative
  control. It is not native gameplay evidence.
- `tests/global_cash25_integration.py` proves unchanged original source after
  removing only display hooks. Independent review also checks transfer changes.
- Separate external native paired runs verify controlled native births followed
  by unchanged movement/collision, cash and popup transition in TYRIAN and MINES,
  normal/blend and 2×/4×, including missing/corrupt/reference fallback. Final
  body and popup visibility are checked separately at actual traced draw frames;
  pickup timing differs by scene (MINES31, TYRIAN43 in the bounded fixtures), so
  a shared hardcoded screenshot frame is not accepted as popup evidence.

Evidence is a bounded Linux SDL software/dummy run, not a full natural campaign,
Windows/GPU benchmark, acoustic test or proof of arbitrary enemy records. HUD
coexistence does not by itself prove a direct RGB contribution transfer to fonts.
Original commercial game data and test binaries are not distributed here.
