# Finite Talon invulnerability blend compatibility

This display-only path prevents the normal single-player Talon's temporary
invulnerability transparency from restoring entire underlying ASTEROID1 HD
regions to classic pixels. The original ship remains visible and translucent;
its source artwork, indexed blitter, invulnerability countdown, physics,
collision, events and RNG are unchanged. No asset/catalog changes are included.

## Admission and lifetime

The new helper is separate from explosion/shield source admission. It accepts
only normal bank9 (33484 bytes), Talon base233 and five original poses229/231/
233/235/237. Each pose's four original tiles are authenticated through20 finite
semantic pins over168 color cells and168 coverage cells. Only hue0x10 is
accepted. Every callback checks its current decoded source and coverage, not
cached trust. Mutated sources, wrong sheets, Christmas, multiplayer/linked/
Galaga modes, other ships and incompatible inputs retain the previous fallback.

A display pose records the single player's invulnerable Talon identity, position
and current logic tick. Only a matching ENTITY_BLEND/QUAD draw can obtain the
lease; each tile must match the expected quadrant index and origin. Entity end
revokes the draw lease; a new pose/reset revokes the recorded pose. An identical
matching draw can reacquire the lease in the same tick: this is draw-scoped
role validation, not one-shot callsite authentication. The current original
call graph has only the intended match. Existing level/layout/palette/owner,
font/suppression and exact post-indexed-write guards remain authoritative.

## Verified scope

- Strict renderer build with warnings as errors.
- Optimized and ASan/UBSan extracted-production tests each pass3,265,773 checks
  with the explicit ship-sheet option enabled. These include all5 Talon poses,
  all20 quadrants, densities4/8, classic/HD/mixed ownership, per-cell source
  mutations, coverage mutation, stale ticks, mismatched roles/origins/layouts,
  negative callback fallback and the existing116 warm plus22 shield sources.
- Native2×/4× paired original-event opening,120 ticks, seed0x5eed, stationary
  no-fire Talon:22 gameplay/draw trace files match at each scale, including
  state/RNG/INDEX8 hashes, collisions, projectiles, poses and event clock.
- Per scale,15 region restores become0;26,600 Talon RGBA writes include324 over
  HD. Coverage and restoration mismatches remain0. Captures85/87/98 change only
  inside the old fallback regions; the translucent ship remains visible and
  underlying rock detail is preserved. Tick103 is byte-identical after
  invulnerability ends, retaining the independently verified cyan-shield fix.
- Flag-off, entirely missing optional pack and corrupt-header pack controls
  at2×/4× retain exact traces and byte-identical captures. No Talon write in
  those resource controls is over HD.
- Assisted warm-contact regression at original-event location3940, seed1,
  ordinary front-port1/power11 fire at x74,80 ticks per scale:70,660 warm RGBA
  writes per run, exact traces and captures. Talon writes there touch classic
  ownership only and do not alter output.

The paired runtime set contains20 runs,2,240 total logic ticks,266 exact
trace-file comparisons and56 captures. Independent read-only source/evidence
review found no blocking correctness issue; the lease limitation above is
explicitly retained. All5 poses have extracted coverage; native captures
exercise the straight pose, not all banking/movement/clipping combinations.

## Reproduction and limitations

```
python tests/run_asteroid_effect_blend_tests.py --repo . \
  --source-sheet /path/to/original/newsh6.shp \
  --ship-sheet /path/to/original/tyrian.shp --output /path/to/test-output
```

The ship-sheet option is optional for legacy warm/shield-only checks. Talon
acceptance requires `talon_source_tests: true` in the resulting receipt.
The original data is read only and never copied into deliverables.

Runtime evidence uses headless SDL dummy/software rendering. The warm window
is assisted and omits prefix spawns; neither it nor the controlled opening
certifies a natural campaign, Windows/GPU, desktop window or whole level.
Native side clipping and all banking movement combinations remain unverified.
Unsupported ships, modes, sources and other effects remain conservative.
LeakSanitizer is disabled for executor compatibility; ASan/UBSan are enabled.
No screenshots, decoded original data, executables or external QA scripts are
committed. This change is local-only, with no further GitHub publication.
