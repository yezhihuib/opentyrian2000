Poison Bomb parent103: one finite HD player-projectile sprite.

Root visually approved the registered original-versus-HD actual4x/2x comparison on2026-10-12 for a runtime trial. In-game visual acceptance remains pending. This is the physical brown/bronze canister with a narrower green central chamber, not another energy orb.

Scope is exactly spriteSheet8:103, logical12x14, anchor(0,0), density8, exported96x112 straight RGBA. Runtime header is HDR1+[80103,8,12,14,0,0]. No new animation, weapon table, gameplay behavior, or accepted green214–217 / explosion78–84 artwork is changed. The engine's existing(-1,0) anchor exception for59 does not apply to103.

The original tile's occupied bounds are[2,1,11,13]. Generated export alpha>16 and alpha>128 bounds are[16,8,88,104], matching that placement at8x. Only boundary antialiasing extends just outside these bounds. Parent103 is an opaque physical object with smooth material shading, while its accepted collision children are translucent energy.

Built-in image_gen produced the artwork. The first pass was too golden; a targeted second pass muted the metal toward source brown/khaki and made the enclosed green chamber readable. Both prompts are retained; only the selected second-pass master is in the source package.

Reproduce with: python export_final.py
Requires Pillow. The export uses a recorded whole-sprite crop[156,74,1084,1288], resize74x98 with Lanczos, placement(15,7) into96x112. No procedural repaint, recolor, alpha remask, pixel tracing, component warping, or synthesized frames. The crop retains the physical boundary antialiasing while dropping low-alpha generated specks well outside the registered object.

Source comparison reference images and decoded original-data evidence remain outside all distributable packages and outside the main repository. The exporter itself has no original-game-data dependency. Optional source comparison generation occurs only if its locally decoded reference exists. Packages contain generated artwork, reproducible exporter, prompts, metrics, technical dependency notes and generated-only review images.

Before acceptance, use the existing legal-loadout fixture after island-repair priority: front-port33, representative powers1/6/11, real collision that creates shot71, all parent/child/trail identities observed, Integer2x and4x, classic/HD/missing/invalid, full state/RNG/collision parity, parent origin/shadow/occlusion check, and unchanged accepted green rendering. Actual gameplay screenshots were not run or captured by the artist.
