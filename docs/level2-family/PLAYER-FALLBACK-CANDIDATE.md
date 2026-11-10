# Independent normal player fallback candidate

`BUILDING313_PLAYER_FALLBACK_ENABLE=1` is a separate default-off experimental
control. It also requires the terrain fallback and existing player-ship family
controls. Successful full-family presentation remains preferred. This candidate
can retain only the normal, living, intact player 1 Talon in the five original
poses 229/231/233/235/237 while an unrelated actor rejects that full scene.
Invulnerability and blended body acquisition remain unsupported, including the
original 1-to-0 invulnerability transition. It is not full actor continuity.

## Independent current-frame proof

The original pose, body and entity-end callbacks still execute when legacy ship
admission returns 0. The new observer uses those exact calls without changing
admission results or native execution. It independently binds the original
player/ship, pose, coordinates, frame/session/generation, bank 9 pointer/size/hash,
palette and scope. A separate pinned HDA cache avoids the rejected legacy ship
transaction. Unchanged materials and affine texture sampling match the existing
five-pose adapter.

Immediately before the genuine normal body draw, a 192×224 ARGB patch captures
only the current pre-body underlay: surviving independently captured terrain, or
the palette-expanded native index tracked by the complete writer ledger. No
rejected actor canvas, saved-under rectangle from another frame or historical
ship is copied. The original native body still draws its four tiles.

The new callback runs inside the independent terrain writer, after its single
physical-store pairing and before native-index/terrain retirement. Only the
exact ordered 217/242/266/239/222 native writes acquire local ownership. Missing,
extra, reordered or wrong-value callbacks reject the ship. Authored transparent
subpixels preserve the captured underlay within those cells; native holes never
acquire ship ownership. Any subsequent normal, blend or shadow write retires the
whole affected logical cell, including a same-value write. No replacement shadow
or blend operator is inferred.

A completed ship still needs the original independent terrain/source/resource,
complete writer, native framebuffer and output-crop proofs. The patch and sparse
mask are sealed at finish. After texture lock and the terrain transaction's full
second validation, the ship's identity, source/art payload, mask and patch are
rechecked before any ship composition. Failure leaves the terrain/native result
untouched. Valid surviving cells are copied only into the cropped playfield.
Existing HUD/border composition remains separate.

All ship failures are local and irreversible for that frame. Shared terrain or
writer failures revoke the ship too. Reset, frame change, successful full-scene
presentation and teardown discard the unused transaction; presentation is
single-use. No native state, collision, pose, RNG, equipment, drawing order or
legacy acceptance counter is changed.

## Read-only evidence

`render_mirror_player_fallback_status()` reports independent current-frame state
and cumulative counters. `presenting` is true only during the actual independent
SDL Present/readback interval, not merely when a candidate has been prepared.
`render_mirror_player_fallback_sample()` is available only during that interval
and rechecks current proofs. It returns a 672-byte relative 24×28 logical ownership
mask and 43,008 ARGB values in a 192×224 patch anchored at status.x/y. Unowned samples
have no authority. This receipt can test displayed pixels and constrain an
on/off difference mask; it is not an independent artwork oracle.

## Checks and limits

The dedicated player-fallback fixture exercises the real adapter, independent
terrain transaction, native writer and SDL software renderer with sanitizer
checks. Its source/scope substitutions are stated explicitly in the test. The
existing ship-material and terrain tests remain separate evidence. A successful
build or fixture does not establish original-data gameplay, actual-frame visible
coverage, physical input, GPU/Windows, performance or full-level acceptance.
This initial subset also requires at least one surviving terrain cell. A ship
alone does not grant independent presentation. Keep this candidate opt-in until
the corresponding bounded native scene checks and their limitations have been
reviewed.

## Bounded native validation

The reviewed 112-unit source digest is
`c9de64863f218497eb5e9b9b38ad457755f369e34d1decc2bb9519f08174d464`;
the Linux binary SHA-256 is
`c7a7276773e70e55fc57ba4bdb11c8df07243e480672fba559d1b1c04bcd3ebf`.
Tests use the original ASTEROID2 data, deterministic scene bootstrap and sampled
keys into original movement/firing code. Asset-debug and probe stay off. Each arm
uses a fresh private profile, public actor candidates, terrain fallback and static
border. Only this new player option differs between arms.

- At 2× over 540 ticks, actual HD player frames increase from 287 to 440:
  287 unchanged legacy ship frames plus 153 independent ship frames. Player
  HD/native switches decrease from 116 to 1. All five independent poses appear.
- At 4× over 240 ticks, HD player frames increase from 124 to 140:
  124 unchanged legacy frames plus 16 independent frames. Switches decrease
  from 25 to 1. Independent poses 233, 235 and 237 appear in this shorter sample.
- In both runs the sole remaining switch occurs at tick 100, after the original
  invulnerability countdown. Every sampled normal-player frame thereafter is HD.
  The original invulnerable and 1-to-0 frames stay on the existing path.
- All 10,140 native-state comparisons match on versus off, including player,
  enemy, projectile, particle, global, RNG and indexed-surface hashes. Full-family
  and terrain presentation counts, and legacy ship admission, remain identical.
- Actual independent player pixels match the sealed current-frame candidate,
  with zero mismatches. Every-frame hashes outside exact surviving native-write
  cells match the off run, including native holes, other actors and the border.
  Thirty scheduled full-window images additionally pass byte-level difference
  checks confined to those exact cells, not merely the ship rectangle.
- Default-off output is also compared with the preceding terrain/HUD checkpoint:
  all 10,140 native-state fields and all 23 common full-window captures match.
  Original input hashes remain unchanged. No existing user save is opened.

The actual-Present candidate comparison verifies integration, not artwork
independently. The separate combined real-include/native-blitter/writer/SDL
fixture checks 5,199,569 assertions under ASan/UBSan using real HDA files and an
independent archived callback oracle. Scope, original-bank and palette admission
are explicit fixture substitutions. Cold-cache missing/corrupt files, all five
poses, alpha/native holes, later writes, crop bounds, resets, single-use behavior
and post-lock changes are covered. Leak detection is disabled. A review-found
hook-test naming error was corrected and the counted test rerun.

```sh
python3 scripts/build_level2_family.py --jobs 4
python3 tests/check_player_fallback_scene.py \
  --data /path/to/original-data --out /fresh/private/output \
  --scale 2 --ticks 540
python3 -m unittest discover -s tests -p 'test_b313_player_fallback.py'
python3 scripts/launch_level2_family.py --data /path/to/original-data \
  --hd --public-candidates --terrain-fallback --static-hud \
  --player-fallback --check-only
```

The launcher requires explicit `--launch` to start a game. This is a normal-player
source candidate, not an update to the frozen Windows asset-debug preview.
Enemy HD/native transitions remain. It does not qualify physical input, menus,
save/reload, sound, complete levels, GPU/Windows or runtime performance.

## Why the player was a useful first local transaction

Read-only instrumentation of the previous 540-tick checkpoint reproduced all
state/status fields and captured images. Its 158 terrain-only frames comprised
61 native sprite-blend rejections, 26 building-event denials, 29 building-lifetime
denials, 9 small-rock final checks, 6 building identities invalidated by native
allocation, and 27 frames without building/terrain-continuity admission. Of the
last group, 15 were event-related, 10 allocation-related and 2 were unresolved.
These are first-failure categories, not permission to relax their guards.

All 98 completed-but-unaccepted player transactions still passed their own final
ship checks. Another 55 normal ship draws were never allowed to contribute after
earlier scene rejection. The independent transaction covers those 153 frames
without accepting the failed building, rock or blend candidate. Other actors
need their own equally bounded proofs before their fallback can be localized.
