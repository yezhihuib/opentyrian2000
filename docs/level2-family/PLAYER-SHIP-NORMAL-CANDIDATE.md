# Five-pose normal player ship candidate

`--hd --public-candidates` now selects normal Talon player-body materials for
poses229/231/233/235/237. Plain `--hd` does not enable them. The launcher clears
inherited `PLAYER_SHIP_FAMILY_` controls and supplies the existing family enable
and asset-root controls only for the public preset. There is no new CLI option for the normal path. A separate, explicit
[`--player-invulnerable` candidate](PLAYER-SHIP-INVULNERABLE-CANDIDATE.md)
can additionally keep HD art during native invulnerability translucency. The
normal-only behavior described here remains the default public preset.

The five unchanged files are `assets/hd/current-compat/talon/ship-{pose}-8.hda`.
All are 172,060 bytes, HDR1 24x28 at density8 with anchor5,7. Their payload
hashes match the public archived player-ship specifications. The launcher checks
every file's exact size and SHA-256; the runtime validates HDR1 fields and pinned
payload identity. No image is generated or edited.

## Narrow normal-only integration

The source is selectively adapted from
`experimental/late-level/sources/03c5968bda89ae17/player_ship_family_mirror.inc`,
its header and native table, with the existing pose/body integration locations
cross-checked in the archived renderer. The current renderer's unrelated
families and global player-ship fallback path remain intact.

Only living intact player1 ship-record1 with original base233, the exact pinned
spriteSheet9 source, matching palette, ordinary ASTEROID2 and an existing valid
family frame can contribute. Body x24..264/y0..156 and unchanged session,
generation, frame, bank and player position are required. The adapter grants
no independent display lease and does not change equipment, movement, RNG,
pose selection, shadows or native drawing.

The real `render_mirror_player_pose` hook records the selected native pose.
The existing player-body call then emits the real four native tiles and its
existing entity-end callback. The adapter checks the exact sparse native store
sequence, with217/242/266/239/222 stores for the five poses and four-part receipt
completion. End and output guards reject incomplete or changed dependencies.

**Invulnerable poses are rejected at pose time, not merely at body time.**
The engine decrements the invulnerability counter between pose and body,
including1→0. The candidate requires both recorded and current counts to be0,
so that transition cannot accidentally enter the normal path. BLEND and SHADOW
body calls return to their previous path without consuming the recorded normal
pose. The archived invulnerability blend-token callback and half-alpha writer
are deliberately not integrated. This batch does not qualify invulnerable art.

Neutral233 samples the unchanged source directly. Turning poses use the
archive's existing bounded affine texture-coordinate sampling, not new native
coordinates or coverage. Out-of-range samples are transparent. All authored
alpha is blended into the current canvas only at verified native callbacks;
transparent subpixels retain RGB but have native ownership, while no-callback
holes stay untouched. Normal/blend retirement and validated shadow ownership
use the current central writer, before other family handlers can return early.

## Evidence limits

The five public files and archive pins were independently matched. Original
game data was not available for a fresh source-bank/RLE audit in this cloud
batch; runtime source and palette pins remain fail-closed checks.

The production-function extraction test exercises the five real HDA files,
pose/current/body selection, affine sampling, sparse pixel/end contracts and
ownership retirement with explicitly documented dependency stubs:1,186 native
callbacks and22,286 alpha0 subpixels. These five materials have no partial-alpha
subpixels in this test; no blended-invulnerability result is claimed. The
1→0 invulnerability transition is explicitly rejected. The existing
central writer test now covers81 pairwise family transitions; acquisition in
that test remains modeled. Launcher tests check preset-only selection,
inherited-control clearing and corrupted-file rejection.

These are offline implementation/material checks. They do not establish real
player motion, actual scene admission, final visible pixels, GUI, cache/fade
behavior or ordinary gameplay acceptance. In particular, turns may need visual
review even when their arithmetic and source bounds are correct. The game has
not been run by this batch and the entire level remains unqualified.
