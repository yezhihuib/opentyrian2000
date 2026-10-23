# P05: bounded enemy green projectile reuse

Base: `47e7d062e0fc4a449a36f1d1f47e53c42f65c66d` (clean NEWSHF168 V4).
This remains **default-off, probe-only**, under `ENEMY_REUSE_HD_PROTOTYPE=1`.
It is not normal-game/global HD activation. All existing artwork remains byte-identical.

## Exact identity

Only original E2 physical level2 GYGES, enemy record379, turret1, weapon153.
Record379: offset193198/77 bytes, FNV `ad8714656b44632b`.
Weapon153: offset33428/80 bytes, FNV `0e1d756bd4135441`.
Actor bank18/NEWSHN:41201 bytes, FNV `c0c6df910c61dc88`.
Projectile bank8:32060 bytes, FNV `2b63027f74aaa21e`.
Weapon max8/multi2 has base214 in every position, animation length3.
The engine increments before drawing: birth214/phase0 → draw215 →216 →214.
No gameplay, RNG, scheduling, coordinate, or original animation writes are added.

The existing allocation generation, actor/weapon/full-bank proofs and one-use
admission witness remain required. New before/after observers enclose the original
native animation block; only its exact phase successor authenticates a draw.
Manual frame jumps, stale generations, repeated admission and intervening unrelated
indexed writes cannot borrow a pending witness. Pauses do not fabricate updates.

## Resource and ownership policy

Approved source PNGs and HDAs214/215/216 stay in their original single locations;
`docs/enemy-green-reuse-source-pins.json` records the independently checked pins.
Existing `CURRENT_GREEN_*` macros remain the current-authoring authority.
Geometry remains12×14, density8, anchor(0,0); all fractional alpha and pixels outside
classic support are retained, not cropped or repainted.

Private draw role146 reuses the loader/operator, **not** player role8 identity or
`get_asset`. It must not append green heads or allocate player green/smoke leases.
P05's three resources preflight atomically and independently of the original six
P02/P04 resources. Missing P05 resources cannot disable valid P02/P04 contributions.
The shared root epoch, relevant contributed-family payloads, source bank, native
slot generation, palette, indexed surfaces and cache proofs still fail closed.
Unsupported filters/modes/layouts and fades remain coherent classic fallback.

## Limits and evidence

See `enemy-green-reuse-validation.json` for final execution receipts.
Final native matrix:105 setups /115,075,282 assertions; prior six-frame matrix310 cases /79,076 assertions. Four targeted mutation controls are caught.
Normal interleave RGB uses the full viewport; BLEND checks independently identified
enemy-alpha overlap samples rather than every background pixel.
The native harness uses actual production renderer/allocation/wrappers, controlled
fire scheduling and verbatim extracted native update blocks. It is not equivalent
to observing the target encounter in a complete live game.
Original GYGES observation and its reached/not-reached result are recorded separately.
The preceding P02/P04 stage likewise has no positive target-HD live-game witness.

Not included: TORM enemy749/weapon110, frame217, P09/missing227, new artwork,
player-green policy changes, normal-game activation, uploads or laptop installation.
Source inventory remains262; runtime destination count remains1024. The new exact
five-file inverse restores the clean V4 source bytes before every older authority
check; neither NEWSHF168 alpha policy nor historical artwork guards are relaxed.
