# Opt-in static HD border

`--hd --static-hud` selects the existing approved HUD1 border independently of
the scene families. Plain `--hd` and `--public-candidates` remain unchanged.
The launcher removes inherited `BUILDING313_FAMILY_HUD_ENABLE` and sets it only
for this explicit option. It verifies the existing 4,160,064-byte resource at
`assets/hd/shared-ui-v1/gameplay-hud-v1.hda`, SHA-256
`98cd6cfefa02a9ae79b75a65e02dd2566d3dec1492552f20b042b3c61c19cd17`.
No new artwork, source data, gauge, font or save format is introduced.

```sh
python3 scripts/launch_level2_family.py --data /path/to/original-data \
  --hd --public-candidates --static-hud --check-only
```

The existing launcher remains check-only unless `--launch` is supplied. Its
separate profile rules are unchanged. This option is currently a POSIX family
launcher candidate; the frozen Windows package and its trust pins are unchanged.

## Independent source and presentation contract

Only the real single-player gameplay PIC3 hook can capture the border. It uses
the unchanged HUD1 parser, complete original PIC3 fingerprint, finite approved
mask, sprite/glyph/item compatibility checks, exact indexed surface identity and
source-used palette fingerprint. Current dynamic index values stay authoritative.
The conditional corner's entire 336-cell block falls back after any changed
message pixel. Text, mode lamps, icons and all gauge values still use native
rendering; this is not full HUD typography or meter integration.

The family scene still rejects shared-HUD activation. The new adapter never
sets `fc.ready`, changes actor/terrain scope, renews a failed witness, alters
scene counters or modifies indexed game pixels. For an accepted scene it writes
only outside the visible 264×184 playfield, then repeats those guards after the
texture lock. A late changed border cell is restored from current native pixels.

If the scene is rejected, a separate static-HUD presentation uses only the final
native indexed frame plus the approved border. This path has its own texture and
full final-index/palette witness. It never reads the rejected HD canvas. It checks
surface, geometry, renderer, texture, pitch, sampling and source identities again
after locking, consumes the pending frame and refuses repeated presentation.
Thus the border does not flicker when an unrelated scene family falls back.

Reset and generic picture transitions revoke the source lease. Modal suspension,
fade/reset and renderer recreation discard pending presentation. Eligible next
ordinary frames can resume a preserved source. Unsupported modes and palettes,
missing/corrupt resources, or replaced source storage use native rendering.
The classic modal and fade routes are unchanged; no HD-modal claim is made.

## Verification

The isolated original-input oracle compiles the current adapter, the production
HUD1 loader, extracted production compatibility/geometry checks and real SDL
software presentation. Original PIC3/font/option bytes arrive only on stdin.
It checks 13,570,686 assertions across valid, missing and corrupt-resource runs,
including 2×/4× native scaling, static ownership, gauges/messages, late writes,
corner retirement, palette/identity changes, suspension, repeated Present and
feature-off behavior. ASan and UBSan pass; LeakSanitizer is disabled.

```sh
python3 tests/test_family_static_hud.py --data /path/to/original-data --sanitize
python3 -m unittest discover -s tests -p 'test_family_static_hud_launcher.py'
```

An immutable 112-unit family build with source digest
`ea68053b9a8d7cf7bf3405aa5301b954670520836dcfbc9da323f896c5a1d98b`
was tested with real original-data ASTEROID2 native firing/movement:

- 2×: 540 ticks and 540 actual Presents, including 172 native-scene fallback
  frames. The border remained visible in every frame, with 27,412 authored
  displayed pixels per frame. All 7,020 native-state comparisons and every
  playfield readback hash matched border-off.
- 4×: 240 ticks and 240 actual Presents, including 35 native-scene fallback
  frames. The border remained visible in every frame, with 109,648 authored
  displayed pixels per frame. All 3,120 native-state comparisons and every
  playfield readback hash matched border-off.
- Both runs had zero authored-border mismatches and zero mismatches in native
  unowned HUD pixels. They produced 13 and 10 scheduled full-window captures.
  Original input hashes remained unchanged; runs used new isolated profiles.

```sh
python3 scripts/build_level2_family.py --jobs 4
python3 tests/check_family_static_hud_scene.py --data /path/to/original-data \
  --out /fresh/external/output --scale 2 --ticks 540
```

The native harness uses a deterministic scene bootstrap and sampled keys. It
does not enable asset-debug/probe or change render admission, damage, RNG,
actor births or weapon origins. Menus, physical controls, save/reload, sound,
GPU rendering, Windows and a complete level remain unverified. These isolated
results do not by themselves certify a later terrain integration. The final
combined source was separately rerun at 2×540 and 4×240 ticks with
`--terrain-fallback`; see [the checkpoint report](PREVIEW-CONTINUITY-CHECKPOINT.md)
for exact source pins, independent terrain counts and remaining limitations.
