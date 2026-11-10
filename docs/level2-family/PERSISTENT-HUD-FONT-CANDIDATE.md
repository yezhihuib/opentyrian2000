# Source-witnessed level and message glyphs

`--hd --static-hud --hud-font` opts into the existing HUF1 artwork for the
persistent level label and bottom message. It is independent of `--dynamic-hud`
and is not added to the public preset. The launcher verifies the 163,952-byte
`gameplay-hud-font-v1.hda`, SHA-256
`3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e`.

This is **not all gameplay text**. Score, timer and WARNING are drawn on the
shifted scene source and need a separate witnessed HD underlay path. They remain
native. Pause/modal text is not added by this adapter.

## Authority and ownership

`family_hud_font_mirror.inc` is independent of the legacy font scene/canvas
state. It owns only `[268,118,320,126)` (level label) and
`[20,190,244,198)` (message), after actual original semantic calls. Neither box
intersects the playfield or dynamic gauge material regions.

- The real pristine PIC3 grant initializes HUF1. All 127 font source records,
  dimensions, encoded bytes and ASCII mapping remain checked by the existing
  source-pinned HUF1 loader. Changed counts, null data and malformed glyphs fail
  before reading their payloads.
- A finite text plan must match every original glyph's position, ID, hue and
  brightness, including `~` toggles. Every physical native store must then match
  the expected cell, value and order. Missing, extra, wrong-value, wrong-surface
  and out-of-footprint callbacks reject that run.
- Native glyph opacity and authored alpha jointly define the finite ownership
  mask. The captured pre-text native underlay is restored only within those
  cells, then existing HUF1 coverage is blended in original command order using
  the established native hue/brightness role. No new shadow is invented.
- Message replacement requires the genuine OPTION36 erase event. Its exact
  228x9, 2052-byte source is pinned to FNV64 `029ec9ec39f694b1`; the complete
  final erase rectangle must match before a new underlay is captured.
- Any later write to an owned run's rectangle, including a same-value write or
  rectangle fill, retires it. A final whole-region comparison also catches
  missed/unobserved changes. Restoring old-looking pixels does not restore
  ownership. A fresh known message erase/draw can create a new transaction.
- Frame start clears prepared output, interrupted glyph transactions fail,
  and suspension prevents composition. Reset, source replacement, scope change
  and disabling the option revoke capture. No old surface is dereferenced after
  its identity changes.

The static family presenter recomputes glyph readiness before painting and
after locking its independent fallback texture. Missing/corrupt font art keeps
native text; it does not disable valid static borders or dynamic material HUD.
The observer sampling API is read-only and grants no presentation permission.

## Verification

```sh
python3 -m unittest discover -s tests -p test_family_hud_font_launcher.py
python3 tests/test_family_hud_font.py --data /path/to/original-data --sanitize
python3 tests/test_family_static_hud.py --data /path/to/original-data --sanitize
python3 tests/test_family_static_hud.py --data /path/to/original-data --dynamic --sanitize
```

The persistent-font original-input oracle passes 2,722,955 assertions under
ASan/UBSan across valid, missing and corrupt resources. It compares exact
ordered alpha/color samples, exercises real SDL software presentation at 2x and
4x, changed/replaced text, real erase restoration, source/palette changes,
same-value writes, bad glyph order, missing/extra stores, null source data,
bad table counts, suspension, scope/config revocation and surface replacement.
World/out-of-HUD callbacks take a pointer/coordinate-only fast rejection path;
active wrong-surface glyph writes still reject, and source mutations skipped by
that fast path are rejected by the full pre-presentation source check.
Original game data stays outside the repository and enters the oracle on stdin.
The existing static and dynamic HUD sanitizer oracles remain unchanged in
their accepted output. Native gameplay verification is separate from these
isolated source/adapter tests.

## Bounded native checkpoint

The accompanying `PERSISTENT-HUD-FONT-VALIDATION.json` records the completed
checkpoint. A fresh 112-unit build and 240 native gameplay frames at 2x passed
with both font and dynamic HUD enabled. Actual SDL Present readback had zero
font, dynamic HUD, static HUD or native HUD mismatches throughout the run;
font ownership contributed, and ordinary SDL movement/fire and Esc → Quit
completed. Original data hashes were unchanged. The test wrapper did not
modify native source units or native game state directly.

The isolated source/adapter oracle also compares real SDL software output at
2x and 4x. Native 4x was **not run**: concurrent terrain changes made the build
receipt stale, and the verifier rejected it before launch. No screenshot was
saved in the completed native run, so visual screenshot inspection is not
claimed. The combined follow-up should rebuild and run the native checker at
both scales with `--hud-font --dynamic-hud --capture-frame 80`.

All 48 launcher tests passed (one skipped). The broader shared-asset suite has
an unrelated Guided derived-PNG recipe failure. Its inputs, generator, mapping
and test match HEAD; a clean-checkout baseline reproduction was not performed.
This bounded checkpoint is not physical-input, Windows/GPU, full-level, or
complete-HD qualification. The font option remains explicit and separate from
the public preset.
