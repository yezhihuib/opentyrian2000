# ASTEROID2 artwork and integration audit

Audit baseline: `691c79b66c429363d7e34736c803c2ab6f259f9a`.
Target: Episode1, physical level file2, script section6, ASTEROID2, mapD/shapesZ.
This is a campaign branch after TYRIAN, not every route's second stage. The
ASTEROID1 production mode is physical file1/section5 and cannot qualify this
level merely because both reuse the same art directory.

This is an evidence-based backlog, not a complete-level acceptance receipt.
The existing52-file family manifest covers24 terrain files plus selected actors.
Present files, admitted rendering, full natural lifetimes and tested appearance
are different facts. Ordinary canonical builds do not include this overlay.

## Packaged terrain and building

- Terrain: shapesZ340,361–368,371–376,378,380–383,386–388,390. Exact52-file
  inventory: `assets/hd/level2-family-v1/MANIFEST.json`.
- Building313–316: three384×448 phase canvases. Native phase bases are
  [191,193,153,155], [195,197,157,159], [199,201,161,163].
- Optional terrain339/348 red vents: loader and registration script exist, but
  matching masters/HDA files are not in the public checkout. The provenance
  document explicitly says they stayed private. Do not count them as delivered.
- Independent terrain fallback preserves only proven, untouched terrain cells.
  Unsupported writers retire ownership; it does not replace missing terrain.
  See ACTUAL-INPUT-INVENTORY.md for the now-complete pinned event/map decode.

## Present and integrated, with guarded boundaries

Base IDs below are bank-local; overlapping numbers in another bank are not substitutes.

- Lamp272: NEWSHS229/231/233/235. Seven initial origins plus16 optional later
  origins. Top/bottom clipping has separate controls, not public-preset defaults.
- Ember269: NEWSHD267/269/271/273. Initial zero-based event157 plus349/351/479/480/485.
- Triple275: NEWSHS153/155/157/159/161/163. Initial zero-based event150 plus132 later
  origins in `triple275_later132_scope.inc`.
- Gray325: NEWSHS11/125/277 exist; existence does not qualify all three states.
  Controlled-window document retains unexplained whole-frame RGB differences.
- Longface573–576: normal NEWSHD155/165 and NEWSHP123/127; damaged NEWSHD163/167
  and NEWSHP125/129. Exact-origin/full-body/bounded top-entry guards remain.
- Fork284: NEWSHD121; one-based events12–15 only; clipping remains native.
- Turret273: NEWSHD169/193/195/197/199/201/203/205/207; events476/477, normal
 20-cycle body only. Projectile304 and damage are not admitted by this adapter.
- Linked338–342: NEWSHP115/117/119/229/231/267/269; events288/289/351/354, normal only.
- Props287/288: NEWSHD245/281/283; events183–186/286–287, with original independent
  native allocations and linked behavior.
- Late282/285: NEWSHD79/81/83 and157/159/161; events291/296/301/312 and319/320/325/326.
- Normal270: NEWSHD127/129/131, events244/245 only. The guard stops at curLoc1960
  or eventLoc260, so this is explicitly not full natural-lifetime coverage.
- Smallrocks317–324: NEWSHD95/114/133/152. Original random births only; fully
  visible12×14 tiles, no arbitrary matching-image admission.
- Random props135/136,260/261,263/265: NEWSHD5/43/85, fully visible24×28 bodies.
  This audit's extension adds records266/268 and existing NEWSHD123. Independent
  original data confirms these eight identities in the exact33-entry random table.
  Siblings137/262/264/267 are absent from that table and remain excluded.
- Tank194: public candidate admits18 listed births and eight poses, stops before
  event259. Tank fallback is independently guarded, not a grant for later births.
- Tank shells146/147: existing materials, only births tied to admitted tank witnesses.

See each family's candidate document and `experimental/level2-family/src` for
source/event/lifetime checks. The public preset adds optional families; plain
`--hd` does not imply all of them. Unsupported filters, clipping, damage, source
or scene conditions can still restore native presentation.

## Artwork absent from the checkout

Repository-wide named-HDA search and archived source pin tables identify:

- Record283: NEWSHD115. Four origins excluded by `late_actor_family_mirror.inc`.
- Compound309–312: NEWSHS39/41/43/45/47/49/77/79/81/83/85/87. Archived compound
  adapter exists; current normal270 deliberately excludes these12 images and
  events242/243. Pins: `experimental/late-level/sources/03c5968bda89ae17/compound309270_asset_pins.inc`.
- Tall326–331: NEWSHS13/15/89/91/51/53. Tall343–348: NEWSHP165/167/241/243/203/205.
  Six one-based events613–618 at time6264 create twelve bodies. Pins:
  `experimental/late-level/sources/03c5968bda89ae17/tall_structure_pins.inc`.
- Launcher271/child463: NEWSHD275/277/279/191. Parent events493–496 at4920.
  Archived family/lineage code exists, but its README explicitly does not accept
  launcher shared-body phase identity. Pins:
  `experimental/late-level/sources/9a69cfe175a0bbc0/launcher271_family_pins.inc`.
- Terrain shapesZ339/348, as described above.

These are missing matching packaged resources, not claims that archived
private artwork never existed. Source-only archives cannot be presented as a
complete runtime package, and their old pins must not be weakened to enable art.

## Existing artwork needing further integration

- NEWSHP121 damaged linked installation is present in asteroid1-ten-v1, but
  current linked338 explicitly never loads it.
- Projectile304 and orb112/113 have existing ASTEROID1 material/implementation
  receipts. Their physical1 admission is not level2 wiring or validation.
- NEWSHD123 already existed with authored PNG and original-source alignment.
  The bounded266/268 reuse in this change is tested without inventing births.
- Other common player/effect/HUD assets are outside this terrain/enemy inventory;
  the new explicit dynamic HUD adapter covers gauges/labels/fixed words; dynamic
  glyph text and generic projectile/effect/pickup integration remain separate gaps.

## Completion gate

Before claiming all assets are HD: decode every original map layer and all731
original events, expand compound/launch/damage/random descendants and every
reachable frame, reconcile each bank/base/state with actual resources, then
verify integration through natural lifetimes and boundary transitions. Keep
original gameplay, INDEX8, collision, movement, event order and RNG authoritative.
A successful manifest check or short opening replay cannot certify this gate.
