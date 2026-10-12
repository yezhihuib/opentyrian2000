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
- `--render-left-sidekick=0|3`, `--render-right-sidekick=0|3`: independently select
  no sidekick or the named Charge Cannon from the selected episode table.
- `--render-sidekick-input=charge-stages`: fixed 90-tick stationary input described
  below; no configurable press/release timing.
- `--render-no-capture`: disables automatic probe exports and explicit asset-debug
  window captures; TSV observation remains enabled.

Defaults remain front 1/power 1, rear 0/power 1/mode 1, both sidekicks 0. Values are decimal digits
only. Malformed values, internal/test ports, and unsupported table combinations
exit 2. Validation happens against the actual selected episode table, after
`asset_debug_level`. `weapon-loadout.tsv` records that episode/level, resolved shot
records, complete initial player hash, and RNG fingerprint.

This is a direct named-table selector, not a shop/acquisition validator: it permits
examining a named port in either bay when its firing table is valid. Do not call an
arbitrary selection a normally obtainable loadout. Charge Cannon is legal in both
shop slots across all episodes, but this preview is not a campaign purchase
demonstration. Other sidekick selection, player-2 linking, special-weapon acquisition,
and a full arsenal sweep remain separate work. Existing default items and gameplay firing/input code are untouched.

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

## Charge Cannon: fixed, original-input proof

The optional `charge-stages` preset lasts exactly 90 ticks. It requires existing
front/rear selectors both set to 0 and at least one sidekick set to 3. It rejects
any explicit `--render-ticks`, even 90, rather than allowing an incomplete or
extended schedule. Both named sidekick selectors accept decimal digits only and
only values 0 and 3; omitted mounts stay 0. These options all require a render or
asset-debug probe. The named input preset overrides the ordinary probe input.

The preset keeps normal fire off and presses each selected mount's dedicated
button for one tick at 2, 24 and 66, releasing it at every other tick. Original
JE_drawOptions initialization and the gameplay loop own charge, the 20-tick passive
charge counter, cooldown, energy consumption, firing and charge reset. The fixture
only selects items and inputs; it never writes those runtime values or item tables.

Example, with the external accepted pack and legal data:

```
--data=/path/to/legal/tyrian2000 --no-sound --no-joystick --no-xmas
--asset-debug=custom --asset-debug-index-only --asset-debug-reference
--render-test=classic --render-assets=/path/to/accepted/pack
--render-scene-assets=off --render-front-port=0 --render-rear-port=0
--render-left-sidekick=3 --render-right-sidekick=3
--render-sidekick-input=charge-stages --render-no-capture
```

`sidekick-loadout.tsv` records the resolved episode, physical level, item, mount,
maximum charge, power-cost port and base shot. It is separate from the unchanged
legacy weapon-loadout schema. `sidekick-states.tsv` logs a read-only snapshot per
mount at input and tick-end: position, player position, charge/counter, cooldown,
buttons and shared power. Both files are only enabled by the new selectors/preset.
Input-phase sidekick coordinates can still be the prior tick's coordinates; compare
actual shot request origins with the end-phase row. The original first-tick clamp
moves player y=180 to160 after sampling the mouse target; this is not an injected
fixture motion. From tick1 onward the stationary firing origins are left(86,160),
right(116,160), exactly player-target x-14 and x+16.

The existing request/result/emission/draw logs prove each mount fires:
- charge0: shot101, bank8 identity252, damage2, velocity(0,-12), repeat6
- charge1: shot102, bank8 identity253, damage5, velocity(0,-10), repeat10
- charge2: shot103, bank8 identity254, damage10, velocity(0,-8), repeat16

These are separate static heads, each with animation span1, TTL255, no acceleration,
trail or collision child. Shot record103 is unrelated to bank8 sprite103 (Poison
Bomb). The nine bank9 launcher-body identities and shop/HUD icons retain original
rendering; this adds no art or sprite mapping. Latent loaded records793/1793 use
252–260 and271–279, but have no direct supported named-item reference in the audited
tables. Their animation and any future reuse remain out of scope.

Run the narrow regression with a separately built unchanged9dbb8036 baseline:

```
python prototype/test-charge-preview.py --exe /path/to/candidate/opentyrian2000 \
  --baseline-exe /path/to/unchanged9dbb8036/opentyrian2000 \
  --data /path/to/legal/tyrian2000 --assets /path/to/accepted/pack \
  --out /new/output/directory
```

The runner uses the existing streamed blend-proof implementation, now also included
as prototype/stream-blend-proof.py. Each verbose blend log is a FIFO: full raw and
original-indexed per-tick hashes are retained, not its raw rows. Other bounded TSVs
retain complete observations. It requires real renderer frames, uses isolated
Integer2x configs, and produces no captures. Checks include exact default classic
and HD8 baseline equality, explicit-zero equivalence, passive charging without
sidekick button presses, each mount independently, both mounts in episodes1/4/5,
classic/HD8 equal gameplay, deterministic repeat, input/loadout/tick rejection,
and exact request-to-emission-to-draw reconciliation.

The episode1 90-tick route contains no natural enemy collision. Other selected
episodes can contain natural collisions, which remain in the unchanged collision
log and are compared exactly between classic/HD8 runs. This fixture certifies
charging, origins, firing and projectile behavior, not natural-hit tint/effect
coverage, launcher art, Dragonwing, latent animations or full-game acceptance. No
targets are injected to manufacture hit coverage.

Recorded acceptance: 16 bounded game runs, 38 invalid-input rejections, 1,620 real
renderer frames, zero capture bytes. Default HD8 has 1,170 actual HD draws in both
unchanged/current builds. The nine selected-mount runs additionally passed the
strengthened final read-only verifier. Independent review repeated those checks
and the default exact comparisons, and rejected an extra unrelated-slot draw
mutation. See CHARGE_CANNON_PREVIEW_VALIDATION.json for hashes and case receipts.
