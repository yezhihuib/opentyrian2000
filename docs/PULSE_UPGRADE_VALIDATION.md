# Pulse-Cannon upgrade heads

Accepted four generated player-only bank8 heads58/60/62/165, static12×14,
8× density, anchor(0,0), slots321–324. Existing59 and its anchor(-1,0) are
byte-identical. Production changes are capacity325 and four finite bank8 TILE
bindings. Enemy112/113, green effects and all329 prior debug assets are unchanged.

## Actual game validation

Starting loadout front port1 at powers1/2/6/11 was selected through the debug
fixture. Original weapon tables, emissions, simulation, collisions and shadows
ran normally; no survival or injected weapon/target records were used.

-40 cases,4,800 renderer frames: powers1/2/6/11 × integer2×/4× ×
 classic/local/missing/invalid/prior-baseline. Each case replayed ticks0–209.
-10 original state/emission/draw/material logs byte-exact across all modes and
 scales, including every original head/shadow command. Power1 prior59 RGB exact.
-Missing and invalid packs have zero HD calls and zero classic-pixel mismatch;
 their same-density RGB hashes match. Cross-density raw hashes are not compared.
-240 consecutive actual native2× frames90–149 reviewed,60 per power; native4×
 tick100 checks for powers2/6/11. Warm cores and soft shoulders remain readable,
 without clipped side shoulders, box edges, unstable shape or color pops.
-Observed heads: power1=59; power2=60; power6=58+165; power11=59+62.
-Original shadow behavior is preserved; dark shadows can remain conspicuous on
 bright clouds. This batch does not revise shadow art or blending.

ASan/UBSan oracle:18,801,646 assertions,3,225,600 pixel comparisons; all11
mutation controls rejected. Missing individual/all assets, invalid headers,
fractional alpha, pitch/clipping/ownership, density fallback, normal/shadow and
other-bank/enemy exclusions are covered. Existing green regressions also pass.
The final production source passes the same source-scope oracle; no private
FIFO readback hook is included.

## Reproduction

`python prototype/build-hd-assets.py` verifies18 packs,2898 HDA entries and341
canonical PNGs. Default preview/debug counts are329/333.
`python prototype/build-pulse-art.py --output /new/outside-repository/path`
recreates all four PNG/HDA files byte-exact from generated masters.
See `prototype/fixtures/README-pulse-upgrade.md` for the portable oracle.
The frozen artwork manifest records offline gate status; this document records
subsequent actual runtime acceptance.

This completes the selected Pulse-Cannon head family, not the full weapon
arsenal, every upgrade acquisition flow, full-game QA or Windows acceptance of
these new assets. Gray island rim/interior repair remains a separate pending
art revision. No original game files, screenshots or private capture hooks are
included in this commit.
