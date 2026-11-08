# Optional normal Turret273 body

This independent default-off candidate reuses nine public NEWSHD images
(169, 193, 195, 197, 199, 201, 203, 205, 207) for the two original ASTEROID2
record-273 origins, one-based eventLoc **476 and 477**. Both occur at time 4612,
x 90/210. The complete original 731-event stream is pinned at level load.

```sh
python3 scripts/launch_level2_family.py --data /your/game-data --check-only --hd --turret273
```

The plan does not start the game. Actual execution additionally needs `--launch`.
The launcher removes inherited `TURRET273_*` controls and verifies the nine
extra assets' byte counts and SHA-256. The original 52-file/24-terrain manifest
stays unchanged; these nine extra files are reported separately. Fork, lamps,
embers, triples and private red vents remain separate options.

## Supported animation, not projectile support

Normal 273 has a 20-cycle sequence using nine unique body images. Its native
contract is `ani=20`, `animax=0`, `aniwhenfire=0`, `aniactive=1`: it continuously
loops, including across normal firing. It does **not** use record-270's
pause-at-frame-six / shot-resumption state. This candidate observes each native
cycle update immediately before drawing and rejects duplicate, skipped,
out-of-range or altered animation states. It does not rewrite the animation.

No projectile304 integration, weapon replacement, damage state, arbitrary
spawn, gameplay change or broad map reuse is included. Exact event, constructor,
allocation-generation, source-bank, record, normal-state and palette witnesses
are required; unsupported or clipped cases retain native rendering. Changes to
a contributing contract reject the shared HD frame rather than presenting a
partial replacement.

All nine pinned images are opaque, with 672 native cells and zero authored
native-hole extras. The code uses those exact four-part native callback streams;
unused generic extra-support arrays and projectile dependencies were removed.
Both turret and Fork ownership retire before every family's early-return pixel
writer. Valid shadows keep and darken HD pixels; later normal/blended writes
retire them. Per-native-write checks are cheap identity/configuration checks;
full bank/art validation remains at tile and output boundaries.

## Verification limits

Focused tests cover explicit launch planning and Fork combination, changed
assets, all nine native callback streams, normal/blend retirement, shadow
receipts, malformed callback order, continuous 20-cycle observation and invalid
animation retirement. C harnesses execute extracted production functions with
explicit stubs; they do not emulate the full game or prove visible frame output.

Actual scene appearance, whole-game draw ordering, firing appearance, sound,
performance and save/load remain unverified. This candidate is not enabled by
default and does not increase terrain coverage.
