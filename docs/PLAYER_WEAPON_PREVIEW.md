# Bounded player-weapon preview fixture

This is opt-in QA plumbing, not new HD artwork. Without a render/asset-debug probe,
these hooks only return and the original shot logic and inputs are unchanged.
The fixture changes only the requested debug starting loadout. It does not patch
weapon tables, spawn artificial targets, refill generator energy, or replace the shot functions.

## Selectors

All selectors require `--render-test=MODE` or `--asset-debug=PRESET`:

- `--render-front-port=ID`, `--render-rear-port=ID`: named item-table ports 0–47,
  excluding internal port 16. Zero disables that bay; its power and mode must be 1.
- `--render-front-power=1..11`, `--render-rear-power=1..11`.
- `--render-rear-mode=1..2`: additionally checked against the loaded port's `opnum`.
- `--render-no-capture`: disables automatic probe exports and explicit asset-debug
  window captures; TSV observation remains enabled.

Defaults remain front 1/power 1, rear 0/power 1/mode 1. Values are decimal digits
only. Malformed values, internal/test ports, and unsupported table combinations
exit 2. Validation happens against the actual selected episode table, after
`asset_debug_level`. `weapon-loadout.tsv` records that episode/level, resolved shot
records, complete initial player hash, and RNG fingerprint.

This is a direct named-table selector, not a shop/acquisition validator: it permits
examining a named port in either bay when its firing table is valid. Do not call an
arbitrary selection a normally obtainable loadout. Sidekick selection/charge input,
player-2 linking, special-weapon acquisition, and a full arsenal sweep are separate
work. Existing default items and gameplay firing/input code are untouched.

For Pulse-Cannon use front port 1 at powers 1, 2, 6, and 11. These resolve to records
155, 156, 160, and 165 and collectively draw spriteSheet8 identities
59, 60, 58, 165, and 62 through the real game. For example, in an isolated working
and config directory, use the built executable with:

```
--data=/path/to/legal/tyrian2000 --no-sound --no-joystick --no-xmas
--render-test=8 --render-ticks=120 --render-assets=/path/to/accepted/pack
--render-front-port=1 --render-front-power=6 --render-no-capture
```

Use `--render-scene=v1` to fire when combining this with asset-debug (whose default
scene does not fire). Use `--asset-debug-reference` when testing HD composition:
index-only fast-forward bypasses the renderer and cannot prove HD equivalence.

## Read-only observations

- `player-shot-requests.tsv`: every call to `player_shot_create`, including main,
  rear, sidekick, linked, special and collision-child callers. `call` joins the logs.
- `player-shot-results.tsv`: complete/bounds/power/capacity result and exact number
  of initialized emission slots, including partial creation before pool exhaustion.
- `player-shot-emissions.tsv`: every initialized slot in the original multi-shot
  loop, including pattern ordinal, initial encoded sprite, velocity/acceleration,
  TTL, animation span, damage, chain, trail, and aim. It is a creation-time snapshot;
  later linked-direction/spray changes are visible in state and actual draws.
- `player-shot-draws.tsv`: every head/shadow command in `player_shot_move_and_draw`,
  including the final lifetime frame, with slot, player, original encoded frame,
  resolved bank/index, actual coordinates/style, and size. This does not include
  a separate trail/explosion draw or the non-sprite reserved Zinglon collision slot.
- `draw-commands.tsv`: all spriteSheet8 and spriteSheet12 entity draws plus the
  direct OPTION_SHAPES blended draw. The old `fire-events.tsv` remains compatible
  but its final-slot-only rows are no longer the emission coverage source.

Bank 8/12 indices are 1-based sprite2 identities. Bank 5 denotes `OPTION_SHAPES`
(variable-size, zero-based index), not spriteSheet5. Styles are normal=0, blend=1,
shadow=2; OPTION_SHAPES has layout=-1 in the generic command log. The material log
also distinguishes bank12 and visible OPTION_SHAPES; asset-index normalizes them
to `tyrian.shp#spriteSheet12` and `tyrian.shp#OPTION_SHAPES`. A draw command is observation
of the original call, not proof that the sprite is visible or has accepted HD art.

## Reproduce validation

Build normally with the available SDL2/SDL2_net pkg-config environment. Keep legal
data, baseline binary, and test output outside the checkout. Run:

```
python prototype/test-weapon-preview.py --exe /path/to/new/opentyrian2000 \
  --baseline-exe /path/to/7a5c62f/opentyrian2000 \
  --data /path/to/legal/tyrian2000 --assets /path/to/accepted/8-density/pack \
  --out /new/output/directory
```

The runner refuses to reuse an existing output directory, uses identical isolated
Integer2x configs, and requires the actual renderer to execute. It compares exact
per-tick state/RNG/indexed pixels, collisions, and emissions/draws for equal selected
loadouts, plus pre-change/no-selector state. It covers all five Pulse identities,
bank12 animation, both rear modes, natural Poison Bomb and OPTION_SHAPES collision
children, all three item-table groups, malformed/unsupported selections, and
capture suppression. No BMP/PNG/video capture is produced. HD density 8 is the
positive path; `render-test=4` intentionally tests missing 4-density-file fallback
with an 8-density-only pack. Render density is not the display's Integer2x scale.

The exact bounded results are in `PLAYER_WEAPON_PREVIEW_VALIDATION.json`. No claim
is made that the unmapped Pulse upgrade artwork has passed visual review.

Validation on the frozen fixture passed 64 bounded cases: 43 real-game runs and
21 invalid-input rejections, 7,200 actual renderer frames, and zero media bytes.
The default pre-change/current classic and HD8 paths match exactly. The final
coverage check reconciles 76,178 candidate head/shadow commands, including 37,650
shadows, and observes natural OPTION_SHAPES and Poison Bomb collision children.
The new code also passed strict C syntax checks and independent read-only review.
