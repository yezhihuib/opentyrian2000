# Shared artwork and family integration

This is an engineering inventory, not a complete level-2 acceptance package.
Existing art, an adapter, and verified runtime coverage are different facts.

Run the read-only inventory with:

```sh
python3 scripts/audit_level2_shared_assets.py
python3 scripts/audit_level2_shared_assets.py --require-complete
```

The second command intentionally exits nonzero. The inventory does not claim
that all assets in a general-purpose pack are reachable in ASTEROID2. A complete
required-ID list still needs original level events, actual loadout/equipment,
death/damage states and full native draw observations. The JSON preserves every
selected resource's exact identity, filename, resource verification state and
family integration status. Missing files, LFS pointers and corrupt resources are
not counted as artwork present. Present artwork is not counted as HD rendering.

## Verified static inventory

The selected existing preview pack and two tank-shell resources contain 338
SHA-256-verified shared resources:

- Five player Talon poses: bank9 IDs 229/231/233/235/237, with the existing
  intact-player adapter. Invulnerability is separately opt-in. The independent
  player fallback still accepts normal bodies only. The eight intermediate
  Talon banking resources have no family adapter.
- Two enemy tank-shell resources: bank8 IDs 146/147, resource identities
  1220146/1220147. Only witnessed tank194 weapon2/3 lifetimes are admitted by
  the existing family adapter. This is not all enemy projectile coverage.
- 124 projectile/option resources, 48 pickup/value resources and 151 effect
  resources in the selected legacy pack are not wired into the family path.
  These are *available candidates*, not a list of required ASTEROID2 draws.

`render_mirror_entity()` and `get_asset()` explicitly decline family mode.
Those guards must not be removed to make the inventory look complete: legacy
leases do not prove family canvas ownership or current-frame writer order.

## Dynamic HUD adapter

`--hd --static-hud --dynamic-hud` adds independent family rendering of existing
HUC labels/shield, HUM2 front/rear/generator/armor meters, HUL top lens/paired
mode assembly, and HUF fixed MODE/SHIELD/ARMOR words. It does **not** add the
dynamic glyph font, score, message text or arbitrary option icons by itself.
The separate `--hud-font` option now adds witnessed persistent level/message
glyphs; see [the font contract](PERSISTENT-HUD-FONT-CANDIDATE.md). Scene score,
timer and WARNING still need their ordered scene-underlay adapter. No artwork
is generated or upscaled to fill those gaps.

`family_dynamic_hud_mirror.inc` captures only the genuine pristine PIC3 grant
already admitted by the static family adapter. Each existing loader retains
its own exact source/resource/palette checks. The original semantic callbacks
are forwarded without changing their native indexed writes:

- Paired mode draws need the exact decoded OPTION18/19 source and completed
  native event; the entire 27x8 assembly must still match before painting.
- Shield draws need an actual draw stamp and all 522 channel pixels, including
  capacity markers and black. Wipes revoke the stamp.
- Meters retain the loader's per-field write-begin/write-end history. A changed
  field retires independently; merely restoring plausible pixels cannot renew
  it without a fresh original writer event.
- Fixed words require each complete source group; labels use exact captured
  cell indices. Unowned cells remain native.

The adapter never enables legacy shared HUD, actor admission or a scene lease.
It paints only through the existing static adapter's accepted-scene and
independent native-frame fallback paths, including the post-texture-lock source
checks. Every paint recomputes field eligibility. Source/layout/scope changes,
reset or disabling the feature revoke capture. Missing/corrupt resources are
optional and do not change native game state. Dynamic font/modal/fade coverage
is not claimed.

## Verification

```sh
python3 -m unittest discover -s tests -p test_level2_shared_assets_audit.py
python3 tests/test_family_static_hud.py --data /path/to/original-data
python3 tests/test_family_static_hud.py --data /path/to/original-data --dynamic --sanitize
```

The original static oracle passes 13,570,686 assertions across valid, missing
and corrupt resources. The dynamic ASan/UBSan oracle passes 20,482,832 assertions
across the same cases. It exercises all front/rear levels, both generator
endpoints, armor/shield levels 0..28, both paired modes, independent late-field
retirement, wrong-surface callbacks, palette changes, suspension, scope/config
revocation and native fallback. Original data travels on stdin and is never
saved as a repository fixture. This oracle uses real material loaders and the
production family adapter with controlled unrelated scene admission; a native
gameplay run is separately required and must not be inferred from these counts.

### Bounded native verification

The integrated 112-unit engine compiled successfully. A fresh 4x native
ASTEROID2 session completed 240 frames, keyboard-event movement/firing,
spawn-invulnerability expiry and native Esc/Quit. Every sampled static,
dynamic and remaining-native HUD pixel matched its expected RGB on every
frame. The final frame had 33,616 dynamically authored HUD output pixels.
These counts are observations, not fixed-seed acceptance totals.

A separate deterministic 2x before/after sequence had 355 visible Presents,
zero whole-scene classic Presents and zero HD/classic switches. All six native
state/collision/projectile/emission/result/hit streams matched the untouched
baseline byte-for-byte. Actual captured frames were inspected for label,
gauge and fixed-word placement; unresolved pixel text and unintegrated actors
remain clearly visible. Neither test certifies full-level art coverage,
physical keyboard input, Windows/GPU rendering or performance.

See DYNAMIC-HUD-VALIDATION.json for bounded results and the independently
reproduced pre-existing production-receipt mismatch. Original data and raw
captures remain outside the repository.
