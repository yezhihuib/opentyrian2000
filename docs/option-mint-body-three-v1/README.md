# Mint-O-Ship body: finite renderer batch

Baseline:8b71966b59315b7ee67163e160925e0d60a0ae39,
tree967e74f99f07e31d3e5d631744de9d20756303dd.

## Production boundary

Exactly three normal body resources112/131/150 are admitted only from the
existing option16/style3/charge0 bank9 TILE draw site. Role127 and slots537–539
are separate from Marlo126/536, Talon9/109 and Mint's bank8 projectile27. There is
no generic bank9 binding. The late draw conditions, sidekick positions, original
sixteen-step animation phase and all charge/firing logic remain unchanged.

Each dedicated wrapper executes the original indexed `blit_sprite2` exactly
once, then ends the mirror entity. The source bank pointer and size must match
the current spriteSheet9. Before every cold or warm lookup, a bounded decode
zeros168 indices and168 coverage bytes and verifies the requested normal source
identity. Christmas sources are empty and retain the invisible classic fallback,
including normal→Christmas reload into reused memory. Changed source pixels or
coverage, malformed/missing art and unsupported surfaces fall back to classic.

The existing ordered normal compositor and independent8→4 asset-loader fallback
are reused without changes. HD conservatively declines horizontal wrapping and
out-of-range tiles; the original indexed writes retain their exact clipping and
row-wrap semantics. Original Talon shadows, invulnerability and later enemy-shot
ordering are untouched. The Mint body has no newly introduced shadow.

## Resources

Three frozen generated resources are appended to each of the two existing
default packs. Their manifests increase545→548; each physical directory keeps
all556 prior files, including six unlisted HDA and five auxiliaries, and reaches
559 files with554 HDA. Rollback packs are unchanged. Original game files and
private runtime captures are not included in this source/art package.

Run `python3 prototype/build-mint-body-art.py` for byte-exact reconstruction and
pack preservation. The dedicated binding and source-scope fixtures use external
original game data, never bundled source pixels.

## Qualification

Actual-game native2x review accepted all three phases in Normal and Hard,
including original stationary non-invulnerable Talon overlap and mixed NIGHT
shading. The frozen dark-core/small independent-shell tradeoffs remain accepted
and unmodified. The artwork contract preserves its earlier offline-freeze
provenance; `verification.json` records the subsequent bounded qualification.

The published-baseline source executable and candidate executable each ran160
actual first-level ticks in Normal and Hard with the same untouched natural
seed. Original indexed output, palette, player/enemy/shot/particle/global state,
RNG, positions and original menu/draw/pose/firing traces matched exactly. Each
candidate run admitted112 forty times,131 eighty times and150 forty times,
while retaining160 original body blits and15040 indexed writes. All sixteen
sampled gameplay image pairs changed only inside the20×26 native2x body bounds;
shop captures were identical. A separate same-binary missing-art fallback
control also passed and is not counted as this cross-source comparison.

The original first shop actually purchased left Mint for5000: the observed
sorted inventory was9/16/30/None; None selection5 moved to Mint selection3, then
original Done6 committed10000→5000 cash with rightNone. Each run naturally
requested and emitted weapon452 thirty-two times. During ticks100–159, the
stationary body and non-invulnerable Talon overlapped fourteen source-support
pixels. Normal sampled94 lit support cells; Hard sampled159 NIGHT ticks with
2 lit,39 transition and53 dark support cells, covering all three body phases.

Focused units pass optimized and ASan/UBSan checks, including source reload,
Christmas, valid coverage-only mutation, malformed/missing resources,
independent8→4 fallback, edges/row-wrap, duplicates/overlap and phase parity. All
153 production files inverse byte-exactly to the baseline;72 translation units
link and the disabled-renderer boundary compiles.

This batch makes no claim of a right/dual Mint purchase, contact collisions,
fully-dark-body coverage, whole-level survival, Windows/GPU testing or
performance measurement. Original game files and runtime screenshots remain
outside the repository.
