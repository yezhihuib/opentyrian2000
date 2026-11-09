# HD player ship during native invulnerability

This separate development candidate keeps the five existing HD Talon poses
visible during the original ship's translucent invulnerability period in
ASTEROID2. It reuses the normal candidate's exact public images and native
silhouette. It adds no blink, glow, palette change, new artwork or game behavior.

The original normal-only public preset stays unchanged. Explicitly opt in:

```sh
python3 scripts/build_level2_family.py --jobs 4
python3 scripts/launch_level2_family.py --data /path/to/original-game-data \
  --hd --public-candidates --player-invulnerable --check-only
```

`--player-invulnerable` requires both `--hd` and `--public-candidates`. Omit it
to retain the existing behavior. Inherited `PLAYER_SHIP_FAMILY_*` settings are
removed before the plan is built. Check-only never starts the game or creates
a profile. POSIX launching remains a separate `--launch` action; this does not
update the frozen Windows package or qualify Windows runtime behavior.

## Rendering and native state

The additional control is `PLAYER_SHIP_FAMILY_INVULNERABLE_ENABLE=1`, alongside
the existing player and parent-family gates. It grants no independent scene
admission. All existing ship-record, source-bank, palette, player, intact-state,
frame, geometry and position checks remain. Shadow-body calls are still excluded.

The native pose hook records the original counter before the game decrements
it. Body and completion checks require exactly that counter minus one. Thus the
last invulnerability tick, 1 to 0, still draws the native blended ship and cannot
be mistaken for a normal opaque pose. The next normal pose uses full coverage.
The renderer never changes the counter, player movement, damage, collisions,
input, RNG or the native drawing operation.

The existing sprite blitter already supplies the actual source index, bank,
tile and origin immediately after each native write. The restored adapter
validates those fields, the ordered destination address, and the native blended
index before the central writer updates its expected buffer. A one-callback
token is then consumed by the ship's HD write. Generic blend or shadow writers
cannot manufacture this token. The central writer still requires its physical
store receipt; incomplete or altered contributions invalidate the family frame.

For a valid blend callback, each authored alpha uses `(alpha + 1) / 2`, matching
the existing Talon HD convention. Transparent subpixels preserve the underlay.
Only original native callback cells are owned; native holes stay untouched.
The five material files, affine turning samples and normal path are unchanged.
The implementation is adapted from the repository's archived player-family
blend adapter, with a new independent opt-in and explicit token cleanup.

## Verification and limits

The focused test uses the real native blend blitter with a synthetic RLE bank,
the real production pose/body/token/pixel routines, and the five unchanged
public HDA payloads. The bank is reconstructed from frozen archived callback
records, not authentic original game data. Scene/source/palette admission and
the surrounding compositor are explicitly modeled; this is not gameplay.
All five poses pass both 2-to-1 and 1-to-0 counter transitions: 2,372 native
blend writes preserve the entire 64,000-byte native output. HD pixels match an
independent half-alpha calculation, with holes and outside cells untouched.
Fourteen malformed provenance/token cases, duplicate and incomplete draws fail
closed. Opt-in removal invalidates an admitted blended receipt. These sampled
materials have transparent/opaque alpha only; partial authored alpha is not
claimed as covered by the material run.

The focused tests pass with strict C99 warnings and with UBSan.
Existing normal-path, public-launcher and family-package checks pass. The central
writer checks all 121 modeled family transitions. Canonical production source
and runtime source-binding checks pass, and the full 112-unit Linux development
build succeeds. An independent source review found no introduced actionable
defects in the implementation, but does not certify visible game output.

The initial checkpoint above had no original game data. A later
[original-input scene check](PLAYER-SHIP-ORIGINAL-SCENE.md) now verifies actual
ASTEROID2 admission, native movement/firing and software-rendered output at
2×/4×, including all five translucent poses and the final 1-to-0 tick.
It uses a diagnostic scene bootstrap and sampled keyboard input, not ordinary
menu navigation or physical input. Pause/return-to-title, accelerated GPU output,
Windows and a complete level remain unverified. Earlier material previews remain
offline renderings, not game screenshots.

```sh
python3 -m unittest discover -s tests -p 'test_player_ship*.py' -v
python3 -m unittest discover -s tests -p test_public_candidates.py -v
python3 -m unittest discover -s tests -p test_level2_family_release.py -v
python3 scripts/check_family_writer_interleave.py
```
