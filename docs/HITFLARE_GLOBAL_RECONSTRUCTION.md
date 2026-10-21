# Global Hitflare7 reconstruction

This batch moves the seven accepted hitflare frames to the independent `--global-assets` route. Original sprites, authored RGBA resources, game data, collision calculations and simulation remain unchanged. The default launcher and packaging manifest are not changed. No level, episode, map or legacy scene permission grants this family.

## Identity and allocation

Only the existing player-shot/enemy-hit and enemy-shot/player-hit branches open the dedicated collision envelope. They still call the original `JE_setupExplosion` exactly once with type 0, deltaY 0, nonfixed and nonfollowing flags. Unrelated generic type-0 calls, including sidekick animation, do not acquire identity. Fixed sprite 145 is not a Hitflare phase.

The real explosion allocator increments the independent slot generation on every selected free slot, before initialization. A witness is committed only for a matching current envelope, coordinates and the native initial sprite 144 / TTL 7. Every draw verifies the current allocation generation, unique simulation tick, ordered TTL 7 through 1 and post-increment source indices 146 through 152. An eligible rejected slot follows a classic-only tri-state path rather than reentering a warmed generic HD cache.

## Pixels and lifetime

The original bank, seven decoded source tiles, used palette colors and all seven authored resources are independently authenticated. Native normal/blend draws remain once-only and their writes are observed in order. Support is the union of native opaque source cells and authored alpha. Independent ownership records preserve overlap with Talon, Shield, Pulse and HUD without claiming their roles.

A contributor latch survives transfer of Hitflare RGB to later owners, including antialiased HUD glyphs. Its source, palette, output-layout and dependent-underlay proof is required through Finish, cache and fade. Invalidating a copied contribution conservatively declines the complete current Present; the next valid frame may reconstruct HD normally. Root changes and true lifetime resets clear slot witnesses and cached contribution state.

## Validation scope

The focused harness executes production Hitflare/Talon helpers and the actual explosion allocator with an independent indexed decoder and bounded SDL structures. Shield/Pulse and HUD typography are stubbed there; native combined tests are separate. Original shape and palette bytes stay in memory and are not included in the repository or delivery archive. Temporary corrupt fixtures contain only authored resources.

The complete production build and focused ASan/UBSan tests passed 200 cases / 10,736,703 assertions. Isolated regressions passed Pulse 551 / 9,575,682, Shield 354 / 15,046,787, Talon 365 / 421,050,144 and HUD 166,155,902 checks. These counters are not native gameplay proof.

A controlled post-HUD source mutation at frame 113 was measured after 1,047 Hitflare subpixels were copied into font underlay, including 724 actual glyph overlaps. The invalidated Present exactly equals pure classic output (zero differing pixels), and frame 114 exactly equals the clean global output after unconditional source restoration. Four 160-frame state/index/RNG/audio/fire/hit/fixture traces match. The final native matrix passed nine scenarios / 27 runs / 4,320 total frames (2,880 variant frames compared to their classic baselines). It covers both collision roles, normal/blend, single/two-player, Hard15 night, HUD overlap, generic wrong-role type 0 and fixed 145. All seven phases appeared in 168 accepted HD calls; 180 sampled isolated images remained within declared native/alpha support. Fourteen wrong-role and seven fixed-145 draws were rejected. The controlled player-hit fixture uses original collision handling; other cases also contain a naturally occurring player-shot hit. Equipment selection, deliberate collision placement and in-memory source mutations remain labelled test fixtures, not claims about complete natural encounters. Independent review accepted the exact 239-file frozen source/test candidate as `ACCEPT_HITFLARE_V2`, rerunning the 200-case sanitizer suite and independently checking the final state traces, support bounds and mutation pixel equalities. Ordinary hit and Hard15 overlap frames were visually inspected. Evidence and source/test freezes are held outside the repository under `recovery-validation-20261021/hitflare`, `hitflare-native` and the independent reviewer directory. No Windows, GPU, full campaign, natural encounter coverage or Vulcan readiness is asserted.
