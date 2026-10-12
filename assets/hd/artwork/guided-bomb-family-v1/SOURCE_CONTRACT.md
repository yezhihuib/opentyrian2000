# Guided-bomb source and runtime contract

Read-only original source verification is against `3f05b84b6b63141f9f7ce3bc3b7e9399ccbb4b8e`. Independent engineering audit corroborates the complete99 guided port/power/table configurations against all4,914 decoded original weapon records. Local original pixels were inspected for every one of the four identities before generation.

## Static identities

- Port28 Guided Micro Bombs: shots576–586 use bank8:171.
- Port29 Heavy Guided Bombs: shots587–597 use bank8:19.
- Port31 Guided Bombs: shots609–619 use bank8:19.
- Every parent is static, `weapani=0`, active TTL255; homing and trail98 are gameplay metadata. Parents use blastfilter208 in episodes1–3 and80 in episodes4/5. These filters affect enemy-hit effects, not projectile RGB.
- Real collisions create shots12,13,14,16 or28. These are static TTL4/8 child projectiles with trail1 and blastfilter112. Episodes1–3 use20 only; episodes4/5 mix20 and21 in simultaneous pattern positions. Damage0 slots are still visible.
- Frame22 is not reachable from any of these99 configurations and is not a next animation frame. It belongs to the separate higher-power Widget Beam family.
- Ordinary bank8 draw uses logicalX+1/logicalY, a12×14 tile and anchor(0,0). Original conditional shadow uses the same sprite and original position/guards. No frame59-specific offset applies.

## Existing dependencies remain unchanged

Parent trail98 is white smoke, newsh6 frames135–141. Child trail1 uses newsh6 frames122–133. These explosion-bank identities are distinct from bank8:20/21 and are not replaced by this candidate package. Never infer bank or animation from matching/adjacent numeric identifiers.

## Shared-use boundary

Binding a player bank/index necessarily also affects other player users.171 is used by linked rear ports21/37, Seeker Bombs and a superbomb descendant.20/21 are reused by missile ports17/20/21, Widget Beam port40, rear charge/link paths, several sidekicks and specials. This package preserves their common static source identity. Runtime acceptance should be explicitly limited to observed guided cases and relevant unchanged-art regressions, not claim complete acceptance of all shared users.

## Engineering anchors

`src/shots.c` static animation, movement, trail, spawn offset, bank8 draws and conditional shadow; `src/tyrian2.c` collision chain reset/spawn; `src/episodes.c` table groups and original loaded records; `src/render_mirror.c` player bank key, logical size and anchor; `src/varz.c` trail definitions and special users. Full independently rederived closure evidence remains in the separate runtime source audit, not bundled with these generated art assets.

## Candidate integration and verification

Proposed renderer cache slots supplied by the engineer are19→326,171→327,20→328,21→329. They are suggestions only; the key in the HDR1 file remains80000+sprite index and the actual production binder is owned by the engineer.

After root offline visual approval: use finite natural collisions for legal-loadout guided Micro28 P6, Heavy29 P11, and the actual episode4 Heavy29 P11 table to observe20/21 together. Log-only discovery also found Heavy29 P6/P7 exercise child16/13. Runtime review must distinguish what was observed from static closure. Check Integer2x/4x, classic/HD/missing-art/invalid-art behavior, original state/RNG/collision parity, colors, origin, smoke/child overlap, shadows and foreground occlusion. Do not expand to an unrestricted capture sweep or replace unaffected assets.
