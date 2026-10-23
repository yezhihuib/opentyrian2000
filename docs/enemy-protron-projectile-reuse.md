# P09 bounded enemy Protron reuse

Base `4810555b37ab12247690f383160e6bff433f41c6`.
Default-off, probe-only `ENEMY_REUSE_HD_PROTOTYPE=1`; no normal-game enablement.

## Exact native scope

Only E3 physical1 CAMANIS, normal data, original palette and source banks:

| Actor | Turret | Weapon | Frequency | Native selection | First original event |
|---|---|---|---|---|---|
| 133 | 1 | 141 | 40 | base226, animation2; first draw227 then226 | ordinal37/time210 |
| 129 | 1 | 134 | 28 | static shot positions244,227,227; max3/multi3 | ordinal150/time960 |

Both actors use NEWSH7/logicalbank3. The original preceding bank event loads
[3,6,15,8]. Event ordinals are one-based. Full77-byte actor records,80-byte
weapons, full actor bank and projectile bank, palette, allocation generation,
slot, selected shot position and native animation witnesses remain mandatory.
Native141 animation is observed before/after the original update, not rewritten.
Static134 is not treated as a three-frame animation. The raw base must equal the
authenticated native shot, not merely one of the numbers226/227.
Records134/216/218/224/225 and weapons135/37/38 remain classic even when227 matches.

## Source and finite resource contract

Existing226/244 reuse canonical approved bytes.225,226,244 and their master are
unchanged. The only new authoring source is
`assets/hd/enemy-protron-p09-v1/source227.png`, derived strictly from the approved
244 middle cell of the existing master. `recipe.json` separates selected artwork
from `identity.json`'s immutable native identity. The builder verifies both files,
master SHA, crop, Lanczos resize, registration, PNG and RGBA hashes.

No mask clipping, threshold, painting, new AI artwork or copied full sheet.
All2552 partial-alpha pixels, including2 nonzero subpixels outside the original
45-cell source mask, are deliberately retained. The original mask/index pins
identify the native source only; they are not an art stencil.

Material role147 was unused after baseline enum/private146 inspection. Only
private `enemy-protron-p09-227-8.hda`, HDR1 identity1470227, is added. No ordinary
`bullet-227-8.hda`, generic role8 eligibility or player/shadow registry entry.
Rendering retains private enemy role146 and its lease; it cannot invoke player
green-head/smoke logic. P09's three dependencies preflight atomically, independently
of oldP02/P04 six and P05 green three. Missing227 cannot disable either old family.
Cache/root changes, bank reloads, slot reuse, palette/surface changes, stale native
witnesses, unsupported modes, foreign owners and bare writes retain fail-closed
frame/cache/fade behavior. No gameplay, RNG or indexed framebuffer writes added.

Package count1024→1025, one private destination only. Current source count262→263
adds only the generated payload header. A finite four-source exact inverse runs
before P05's unchanged historical inverse; all prior ledger bytes stay fixed.
Current authoring workflows carry the finite P09 input closure when rebuilding
isolated packages; this is not permission to add unrelated consumers.

## Evidence and limits

See `enemy-protron-reuse-validation.json` for final build, native, source, package
and original-event observations. Static original source proof is independently
recorded in `enemy-protron-source-proof.json`; it is not a runtime claim.
Native test fixtures call actual production allocation/firing/renderer and copy
verbatim native update loops; controlled placements/timers are explicitly not
original-event gameplay observations. Full-game runs are reported separately.
No GitHub publication, laptop installation, private original binaries, Windows/GPU
certification or normal-game activation is included.

### Actual observation outcome

The original-event strong-input pairs reached37 and150. The unchanged opt-in
binary logged168 and390 role146 candidates respectively, including227→226 and
244, but **zero accepted HD draws**. Paired state/RNG/INDEX8 fields were equal.
Stationary inputs reached37, then died at481 before150; that nonappearance is
separate from the demo-mode rejection of candidates already observed.

A separate logging-only diagnostic (not an acceptance binary) established exact
actor/weapon/source/witness proofs and isolated the sole false scope conjunct:
`play_demo == true`. Existing `game_probe` startup unconditionally enables that
flag to run its controlled input loop. P09 correctly retains the old `!play_demo`
guard; no state override or new control mechanism was added to manufacture an
accepted frame. Existing supported probe/debug startup arguments provide no
non-demo variant. Thus full-game HD visual acceptance remains open, despite the
native production harness passing; neither animation order nor source mapping
failed in these original-event observations.
