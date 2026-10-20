# Open follow-up: shared palette-blend rollback over an HD body

Status: the later [authenticated warm/contact blend fix](../asteroid1-warm-contact-blend-v1/README.md)
resolves this witnessed rollback for its finite supported source subset. The
original NEWSHS272 family checkpoint left shared effects unchanged. The evidence
below and its JSON retain that pre-fix state; other unsupported shared effects
still use the conservative fallback.

## Minimal witnessed case

Existing actual-engine ASSISTED 3940 ordinary-fire window, tick 28, native 2x/4x:

- The remaining original link 0 actor in slot 26 is live, with armor 3, cycle 11,
  base 233, and no alternate damage state.
- All four material 136/base 233 quadrant commands are accepted at whole-body
  root (95,21). Each callback leaves actors/projectiles, RNG and INDEX8 unchanged.
- A later original MIRROR_BLEND pixel invokes restore_classic_rect on the live
  HD rectangle (95,21,24,28). The trace reports 590 replaced HD blocks and 672
  checked classic blocks, with no restored mismatch or whole-frame rejection.
- The candidate survivor therefore looks classic under the overlapping shared
  effects. Gameplay, ordinary partial/lethal processing and paired baseline
  state remain exact. This passing simulation proof does not fix the visuals.

## Cause and attribution boundary

The existing ASTEROID branch of render_mirror_sprite2_blend_pixel immediately
delegates to render_mirror_pixel with MIRROR_BLEND. A blend over owned HD pixels
uses the conservative complete-region classic restoration path. This early
delegation also bypasses blend_source_index attribution, so the existing restore
trace records source_index 0. The material 136 admission and 24x28 rollback are
proven; naming one exact explosion sprite would exceed the recorded evidence.
Nearby normal/shadow bank 8 player-shot 59/62 draws are separately recorded and
do not by their styles alone identify the blend that triggers the rollback.

## Regression evidence and next task boundary

tick28-shared-blend-regression.json retains the small exact derived command,
callback, hit, restore, effect, frame and paired-state rows. Full original-data
inputs, native captures and trace files remain external in the validation
runtime folder; the all-site/lethal contact shows this exact tick 28 case.

A separate fix should preserve legitimate HD body detail through correctly
ordered shared palette blending while retaining original effects, INDEX8,
gameplay/RNG and peer-family identities. Add precise effect attribution and a
targeted actual-engine regression before changing that shared path. Do not hide
the issue, suppress legitimate classic effects or weaken the current integrity
guards. No such fix is included in this family checkpoint.

## Subsequent scoped resolution

A separate unchanged-rendering diagnostic attributed the original trigger to
explosionSpriteSheet index151 at origin(93,42), source112, pixel(98,43). The
later fix authenticates current original warm/contact source indices and
coverage before applying the existing continuous palette-ramp operation to
authored HD subpixels. At native2x/4x tick28, the four136/base233 commands remain
accepted, original warm effects remain visible and the590-block rollback becomes
zero. Gameplay/RNG/INDEX8 and ordered command traces stay exact. See the linked
fix for negative tests, full evidence and the explicitly retained fallback scope.
