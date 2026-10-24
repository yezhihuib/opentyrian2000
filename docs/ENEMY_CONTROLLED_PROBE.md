# Controlled original-event enemy projectile validation

This restores compatibility with the **existing** segmented asset-debug interface.
It is assisted deterministic original-event replay, **not natural playthrough**.
No level data, gameplay events, collisions, damage, RNG, coordinates, assets,
life count, or tick clock implementation changed.

## Existing interface (not newly invented)

- `--asset-debug=custom --asset-debug-episode=N --asset-debug-level=N` selects
  the original episode and physical level.
- `--asset-debug-event=N` or `--asset-debug-tick=N` replays from that level's
  beginning, executing every original tick without pacing until the target.
  There is no saved-state seek or direct clock jump.
- The target frame is shown and paused. `--asset-debug-control=FILE` reads
  newline-delimited `pause`, `step`, `resume`, `toggle`, `reload`, and `quit`.
  The existing P/Space, N/period, R and Escape keyboard controls also work.
- `--asset-debug-capture --asset-debug-capture-start=N
  --asset-debug-capture-count=4 --asset-debug-window-only` captures actual SDL
  renderer readback. Tick counts remain bounded by `--render-ticks=60..6000`.

## Explicit new renderer permission

Only builds with `ENEMY_REUSE_HD_PROTOTYPE=1` (and without
`RENDER_MIRROR_DISABLED`) accept:

```
--render-enemy-reuse-session=original-events-v1
```

It defaults off; old probe commands and ordinary demos are not silently granted
this permission. The private session is minted only after fixed-seed probe
initialization and the existing original-level/loadout setup. It permits only
E1 physical 2/5, E2 physical 2, and E3 physical 1; identity checks still bind the
finite original actor/weapon families, pinned source/resources, generations,
animation, palette, ownership and fallback.

Only existing `v1` or `enemy-hit` input and default loadout or the previously
used strong loadout (front36/rear37, both power11, rear mode1) are permitted.
Configuration, asset root, episode/level and session generation are locked.
Pause/step/resume preserve permission; hit/destroy, reload, quit, completion,
mode/level/configuration changes revoke it. Artificial hit/destroy cases are
negative controls only, never acceptance evidence.

The original game switches `VGAScreen` from `game_screen` to `VGAScreenSeg`
before output. The explicit session now proves that specific output transition:
both captured surface objects, pixel stores, formats and INDEX8 layouts remain
locked. Draw-time still requires the original game owner; output permission
cannot authorize a later draw or resurrect a revoked cached presentation.
The separate normal-game observer is unchanged. Its real-event output alias
path remains unverified and may have the same pre-existing limitation.

## Reproduce the verified P09 segments

Use the opt-in binary, original Tyrian 2000 data and the existing validated
12-member reuse asset directory (no new asset files). Create a control file
containing `resume` and a newline, and run in a fresh output/config directory:

```sh
opentyrian2000 --data="$ORIGINAL_DATA" \
  --asset-debug=custom --asset-debug-episode=3 --asset-debug-level=1 \
  --asset-debug-event=37 --asset-debug-control="$CONTROL_FILE" \
  --render-test=8 --render-assets="$REUSE_ASSETS" --render-ticks=280 \
  --render-scene=v1 --render-front-port=36 --render-front-power=11 \
  --render-rear-port=37 --render-rear-power=11 --render-rear-mode=1 \
  --asset-debug-capture --asset-debug-capture-start=239 \
  --asset-debug-capture-count=4 --asset-debug-window-only \
  --render-enemy-reuse-session=original-events-v1
```

For event150 use `--asset-debug-event=150 --render-ticks=1800` and
`--asset-debug-capture-start=979`. Removing only the final permission flag is
one negative control. Compare old-opt-in/no-flag, new-opt-in/no-flag and
new-opt-in/explicit-flag with the same initial seed/configuration/input.

Local raw evidence lives under `enemy-controlled-probe-validation` beside this
worktree; the concise checked-in validation summary distinguishes real events,
unit fixtures, negative controls and remaining reachability gaps. No Windows,
GPU, full-campaign or natural-playthrough certification is claimed.
