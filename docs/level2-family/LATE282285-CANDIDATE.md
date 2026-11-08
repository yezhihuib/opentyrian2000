# Late282/285 body candidate (default off)

`--hd --late282285` enables only the eight original episode1 physical-level2
(ASTEROID2) body origins below. The launcher verifies six existing public HDA
files and otherwise strips inherited `LATE_ACTORS_` controls. No game is launched
by preparing a plan. Canonical sources and the52-file default manifest stay unchanged.

| Record | Events (one-based) | Native type/pool | Times |
|---|---|---|---|
|285|291,296,301,312|15 /0–24|2500,2540,2580,2700|
|282|319,320,325,326|7 /50–74|2740,2740,2800,2800|

The six NEWSHD images are79/81/83 and157/159/161. Their bytes and source-bank8
identity match the existing physical-level2 `late_actor` implementation pins.
HDA role143 for285 is an artwork identifier, not a different native sprite bank.
Record283 is deliberately excluded: its115 image is unavailable, its four
origins cannot be admitted, and its authored extra-coverage arrays are removed.
Stable historical pin-table indices remain for traceability, but unsupported
image3 is never loaded, selected or drawn. There is no projectile art admission.

Each actor remains independently allocated. Failed native allocation consumes
only that origin. Original case7 background3 coordinate branches and y-speed
adjustment are preserved; native case15 coordinates remain authoritative.
282 uses its original six-cycle firing animation and285 its eight-cycle sequence.
Only successful original shot allocation that changes animation gate2 to1 emits
the resume observation. Full projectile pools, cooldowns, aim, weapon damage,
randomness, movement, linked death and actor health remain native gameplay.

The initial731-event stream is fully pinned. Independent before/after hooks
observe actual native case12 and case33 row mutations, without replaying events
or generating RNG. Unsupported rows/states fail closed. Native slot reuse,
offscreen disposal, direct/linked death, damage transformation, full event clear,
pool0-only clear and event replacement retire witnesses.

Six images have no authored non-native extra coverage. Their alpha blends only
on authenticated original native-write cells. Holes retain the current underlay.
Sparse owner retirement runs for every integrated family before early return;
shadows retain ownership, later normal/blended writers retire it. Per-pixel
checks are cheap identity/configuration checks; expensive source/art hashes
remain at tile/output boundaries.

## Qualification boundary

The staged tests cover launcher gates/assets, eight independent admissions,
excluded283, both firing/resumption cycles, native alpha/hole ownership and hook
ordering. They are isolated observer harnesses, not gameplay simulation. The final focused/regression aggregate passes56 tests; the complete112-unit
production build also links successfully. These checks follow an independently
read-back private code checkpoint. Actual
scene, projectile appearance, clipping transitions and runtime performance are
not qualified. No graphics permission workaround or game launch was performed.
