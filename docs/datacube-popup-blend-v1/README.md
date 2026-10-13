# Data pickup blend compatibility

Baseline: `93008cc051b4b00c512dc9f8599849f6db1132e3`.

## Source cause

The original full-game Data pickup record 513 has value 1 and explosion type
52. `JE_playerCollide` increments `cubeMax`, queues the original sounds, removes
the pickup and calls the original `JE_setupExplosion`. It does not draw a text
message, load a picture, change the palette, or reset the manual-HD lease.

Type 52 stores sprite 265 with TTL 14. The fixed-position original draw loop
therefore draws `newsh6.shp` sprite 266 fourteen times. All 85 opaque pixels of
this original Data glyph use palette ramp `0x70`.

The renderer already lists 266 as a recognized fixed value effect, but its
value-glyph predicate previously accepted only the blue/gray `0x80` and `0x90`
ramps. Data therefore entered `restore_classic_rect`. That function closes over
overlapping earlier HD regions, so one glyph can restore a large connected
background and ship to classic pixels without revoking the manual-HD lease or
rejecting the frame.

## Bounded change

`recognized_contact_effect` additionally accepts only `(index == 266 &&
hue == 0x70)`. The existing original-sheet, supported-Talon, known-blend,
monotone-ramp and exact original indexed-write checks remain in place. It uses
the same existing continuous blend as other supported original effect glyphs.
No art, game-state update, timing, pickup behavior, input, palette, resolution
setting or lease lifecycle is changed.

The related first-level source audit found that cash records 391–395 retain
their previous blue/gray glyph handling. Rear-powerup 534 uses fixed glyph 145
on ramp `0x70`, which was already explicitly accepted. No other glyph admission
is added.

## Verification

- Release Linux build succeeds.
- `prototype/test-datacube-blend.py` builds the real baseline and candidate
  renderers with the original indexed sprite decoder and actual local game
  data. It uses an explicitly synthetic connected HD underlay and supported
  ship ownership; it does not launch the game or claim natural collection.
- At both source densities 4 and 8, all 14 Data draws restore 64,000 logical
  pixels in the baseline fixture and zero in the candidate. Final composition
  loses scene HD in the baseline and retains it in the candidate. Indexed
  pixels are byte-identical to an independent call of the original decoder.
- Missing Talon, wrong sprite sheet, disabled known blend and a nonmonotone
  live palette change preserve the original fallback. The palette change still
  rejects final HD output. Edge placements are also checked.
- Exhaustive comparison of 102,400 `(index, hue)` combinations admits exactly
  one new pair: `(266, 0x70)`.
- The existing 69 manual-HD parser, lease, scope, fade, fallback and banking
  cases pass. Their source-preservation gate projects only the exact bounded
  Data predicate edit before comparing the unchanged render helpers.

Reproduce after a normal `make` build, using your own original game data:

```
python3 prototype/test-datacube-blend.py --data /path/to/tyrian2000 --out /tmp/data-blend-new
python3 prototype/test-manual-hd.py --out /tmp/manual-hd-new
```

## Paired gameplay-path diagnostic

The reviewed baseline and candidate each entered Full Game / Episode 1 /
Normal through the original menus in Linux SDL's dummy-video/software renderer.
Both observed the original Data513 drop, then cube count 0→1 at logic tick 732.
The baseline restored 13,306 logical-pixel blocks at pickup, peaking at 14,208
on tick 737. Restoration occurred on ticks 732–745 and cleared on 746. The
candidate restored zero blocks throughout that interval. Palette, manual-HD
lease and some scene-HD ownership remained intact in both runs, without frame
rejection. The reproduced defect was a transient, partial classic restoration.

This was an explicitly artificial-combat fixture. After ordinary Space fire
reduced the real carrier5/link16 to armor2, each private binary made one guarded
call to the original `player_shot_create(...155...)` at tick 718. Its spawn
arguments were deliberately selected relative to the carrier, rather than the
player's firing position. Damage2 and subsequent shot movement remained
original, with no post-creation shot-field edits or direct entity/health writes.
Original collision, death, drop and collection code remained unchanged. Earlier
queued projectiles were present, so the final hit is not attributed uniquely to
the diagnostic projectile. Menus and movement used SDL key events.

Post-render observations show fixed sprite265 at (232,94), TTL13 through TTL1
on ticks 732–744, with transparent blending enabled. Sprite266 and the final
tick-745 draw are inferred from the unchanged sprite+1/decrement loop; they were
not recorded by a draw-callback instrument. The six retained 640×400 PNGs were
verified RGBA-identical to their BMP readbacks; both pickup images were reviewed.

See `runtime-result.json` for compact independently checked results and exact
source, executable and evidence pins. Raw evidence and private fixture sources
are retained separately; no game data, captures or diagnostic hook are added to
the production tree. Adaptive input and differing effect/RNG state mean this
pair is not whole-frame parity evidence. Indexed parity is established by the
separate deterministic unit test above. This result does not establish a
permanent whole-scene reset on Windows, and no Windows runtime or package was
validated by this diagnostic.
