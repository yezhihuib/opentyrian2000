# Native ASTEROID2 playable preview

The explicit `--level2-preview=asteroid2-v1` engine option enters one local,
normal single-player ASTEROID2 session. It is separate from the historical
`562e8fc` frozen Windows diagnostic preview. That older package and
`scripts/preview_level2_frozen.py` are unchanged.

## Entry and session boundary

The normal CLI previously had no direct-level route. The new option calls the
ordinary Episode 1 and default-player initialization, then selects script
section 6. The existing loader must resolve Episode 1 / level file 2 / ASTEROID2.
No alternate map, actor constructor, event script, scripted player input or
asset-debug/probe mode is used. Normal difficulty and the default Talon/Pulse
loadout are selected. Automatic Christmas mode is disabled for this original
non-seasonal data contract.

This is a freely quit session, not a fixed-tick playback. Normal movement,
firing, collisions, animation, damage, spawn invulnerability, RNG and native
life/game-over handling are untouched. No first-death shortcut is added. When
the original engine reaches its level-termination boundary, normal scene and
sprite cleanup runs, then the process exits before score/shop/retry/next-level
flows. Native Esc → Quit also reaches that boundary. Closing the window uses
the existing window-close behavior.

Default keyboard controls are arrows to move and Space to fire. P pauses.
Escape opens the normal in-game menu; select Quit to end the preview. Enter
changes rear fire mode; Ctrl and Alt operate sidekicks when equipped. This
preview explicitly selects keyboard input. It does not qualify mouse/gamepad
control. There is no level-completion guarantee or imported campaign progress.

The option rejects render/asset-debug/enemy-reuse diagnostic options, other
direct-HD modes, network play, demo recording, constant/death/loot cheats and
explicit Christmas mode before reading game data or a profile. Wrong or duplicate
versioned option values are rejected. With the option absent the normal startup
and campaign lifecycle remain unchanged.

## Profile and artwork contract

Use the dedicated portable launcher with a newly created profile per launch.
Do not point this preview at an existing user's profile or copy saves into it.
The engine's normal backup/config writes belong only to that disposable profile.
The native switch itself is a session selector, not a profile-isolation tool.
Original game data remains external, private and unchanged.

To enable the currently reviewed artwork, the launcher retains the existing
explicit preset and controls:

```
--hd --public-candidates --terrain-fallback --player-fallback --tank-fallback --static-hud
```

These are launcher options, not additional engine options. They do not follow
implicitly from `--level2-preview=asteroid2-v1`. All existing asset/source,
identity, lifetime, event, geometry, ownership and presentation guards remain
unchanged. No new art, pose, event or approval is admitted by the session option.
The static border uses the current HUD resource; text and gauges stay native.

Coverage is incomplete. Only approved, currently proven assets display in HD.
Uncovered actors, clipped or filtered states, invulnerable player presentation
and rejected scene conditions can still use native graphics. This is not a
promise of complete level-2 HD coverage or zero flicker everywhere. Existing
bounded terrain/player/tank/HUD receipts must not be enlarged into full-level,
physical-input, Windows/GPU, audio or performance qualification.

## Focused verification

```
python3 -m unittest discover -s tests -p 'test_native_level2_preview.py'
python3 scripts/build_level2_family.py --jobs 8
python3 tests/check_native_level2_preview.py --data /private/original-data \
  --out /private/fresh-native-entry-2x --scale 2 --frames 540
```

The focused unit suite checks explicit opt-in, native initialization, unchanged
historical preview, both native session boundaries, invalid/duplicate versions
and conflicts before profile/data access. CLI checks need a current built
binary (`NATIVE_PREVIEW_BINARY` can select it).

The scene checker links the hash-verified, unmodified 112 native build objects
with a test-only observer. It does not replace startup or gameplay units and
uses the actual new command-line route. Test-only SDL events exercise arrows,
Space and Esc → Quit through the ordinary SDL event pump. Read-only observations
check movement, shots, expiring native spawn invulnerability, actual family,
terrain, player and tank presentation, and authored/static versus native/dynamic
HUD pixels. All output stays outside the repository. These generated input
events are software-path evidence, not a claim of physical keyboard testing,
and the observer is never included in a delivery executable.

### Cloud-native checkpoint

The combined source digest for the native-entry verification is
`57bfa1082112d19690b082084fbfbd8f9f8ef1ca54b229579a59e7344759ca50`.
The unchanged 112-unit native executable has SHA256
`f0eebe21dc909ec2e4fada0dd76f4c1da005fb2a58a31488b3b3a042fde6fcb3`.
At 4x, the actual direct-entry SDL-event run completed 240 frames and exited
through the native Esc/Quit menu and session boundary. It recorded 211 full
family, 6 independent terrain, 6 independent player and 3 independent tank
Presents. Static HUD and native dynamic HUD readback had zero pixel mismatches
in every frame. At 2x, a separate 540-frame run also completed native Esc/Quit
and recorded 433 full-family, 84 independent terrain, 82 independent player and
79 independent tank Presents, with zero static/dynamic HUD pixel mismatches in
all 540 frames. Both runs exercised arrow movement, Space firing and expiration
of normal spawn invulnerability. Original data was unchanged. The seven focused
native-preview tests and five existing terrain/player/tank/static-HUD launcher
tests pass.

The first 2x attempt reached frame 503 before the checker's initial 180-second
wall limit. A fresh complete rerun passed with a 600-second test-only limit.
The delivered native mode has no tick or wall-clock timeout. These runs are not
performance measurements.

These counts come from ordinary time-seeded runs and are not fixed-seed scene
oracle totals. The pre-existing deterministic A/B receipts remain separate.
Neither the checker nor these counts qualify physical controls or Windows/GPU.
