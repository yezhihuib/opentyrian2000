# Low grass / sand9: bounded acceptance

Base: `7c7aee388e384840915bd2532bbcc038c3d5047e`.

Adds only Layer1 shapesZ **66/67/69/76/78/79/80/89/90**, slots312–320,
through the existing NORMAL terrain path. Each is opaque24×28, anchor0,0,
density8. The source family closes nine related sand/low-vegetation designs;
forest211/212/213/215/221/223/231/232/233/234 is excluded. Accepted47/49/50
and all320 previous default-debug resources are byte-identical.

The selected generated v3 restores the six-tile patch's green area to99.7% of
the original visual-green support, with centroid difference about0.2logicalpx.
Dark low grass follows the original palette. Fine blades merge into compact
texture at native2×; this is not tall grass or a claim of individually visible blades.

## Runtime evidence

Matching baseline/candidate replay from0 through3599 uses the original level,
scroll, RNG and draw order, with **private survival only**, no weapon or hit
injection. All3,600 original state/clock/pose records,595,200 material rows,
57 collisions and3,778 enemy-projectile rows match exactly. Original gameplay
source is unchanged; the private survival/probe/capture hooks are not committed.

The first complete48×84 source canvas is registered at tick3516, x212/236,
y0/28/56, layout90/89,78/76,80/79. Earlier ticks3483–3498 expose all1,161
original green-support pixels despite clipping6–11 top rows of the surrounding
sand canvas. The accepted native2× stream covers3480–3599, including clear
vegetation and subsequent natural Layer3/enemy occlusion. All120 frames match
direct SDL readback and noncapture RGB/state, and two independent visual reviews
passed. The stream ends covered/active, not a clear-tail or whole-level test.

A matching native4× log run preserves original state and drawing. Missing all
nine files gives22 deterministic TSVs and final RGB byte-exact to baseline
(excluding wall-clock timing). Processor4 preserves indexed/state/material/
blend writes, uses NORMAL for the new Layer1 family, leaves cloud BLEND on the
original path, and reports no coverage/restoration errors. HD ownership counts
naturally differ from the unbound baseline.

Only the six-tile motif has clear dynamic grass acceptance. Other members and
all136 deduplicated neighbor contexts have static source/native-size review;
partially entering mainland and later original forest/enemies do not imply
complete runtime acceptance of those areas. Unrelated original newsh2
159/161/163/165/167 in the tail are deliberately outside this batch.

## Reproduction and limits

`python prototype/build-hd-assets.py` verifies18 packs,2,890 HDA entries and337
active canonical PNGs; preview/debug defaults contain325/329 assets.
`python prototype/build-grass-sand-art.py --output NEW_EXTERNAL_DIRECTORY`
reconstructs exact nine RGBA/HDA resources without original game data. The
frozen generated source package documents all revisions and standalone guards.

See [WINDOW75_90_VALIDATION.md](WINDOW75_90_VALIDATION.md) for the separate
log-only mapping closure. No full522-frame75–90 visual pass, ordinary-survival
claim, whole-game completion, Windows acceptance or CI result is implied.
