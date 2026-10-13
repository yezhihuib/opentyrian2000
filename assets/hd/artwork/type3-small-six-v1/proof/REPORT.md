# Type3 six small sprites: read-only source receipt

Pinned clean checkout: `2efdc890217330e75a873252ca96b576495b23b9`. Original Tyrian2000 data was decoded directly. This audit performed no repository edit, game execution, new capture, generated art or publication.

## Exact art input

- Bank1, `newsh2.shp`, IDs **171,190,209,228,247,266**. Each is a single **12×14** sprite with **anchor0,0**, one original draw call, `sprite_offset0`. It is not a24×28 composite and has no quadrants. At8×, output is96×112; HDR1 IDs are1010000+sourceID, dimensions12×14, density8, anchor0,0, names `enemy-newsh2-{ID}-8.hda`.
- Runtime top-left is `(enemy.ex + tempMapXOfs, enemy.ey)`. For the scheduled first-level sky lane, `tempMapXOfs=mapX2Ofs`. Do not subtract6,7 or add center padding.
- Transparent originals: `original-reference/original-{ID}.png`; inspection enlargements: `original-{ID}-8x.png`; all six contacts: `six-original-native2x.png`, `native4x.png`, `native8x.png` (full contact prefix is `six-original-`). Exact per-frame alpha PNGs are alongside them.
- All six decoded RGBA files were independently checked with the native x/y row-advance decoder against the linear extraction, and source palette5 was checked against `palette.dat`.
- Original opacity is the RLE write mask, not a palette-zero heuristic. All written pixels are opaque, with no palette-zero writes here. The opaque dark outline is index1, RGB12/12/12. Color body is warm brown/ochre/cream ramp16–31. Detailed counts/RGB values/hashes are in `art-input-contract.json`.
- There are **three unique alpha shapes**, applied to six frames. ID171:98 opaque pixels,bbox[1,0,12,14]; ID228:74,bbox[3,0,10,14]; IDs190/209/247/266:82 each and identical alpha,bbox[2,0,11,14]. Bboxes use exclusive right/bottom edges. Preserve each frame’s binary mask with nearest8× expansion.
- Visual inspection shows a rigid tapered mechanical/spindle-like body: broad head/shoulders, narrow downward point, opaque dark outline, warm moving highlight and varying profile width. This visual description is not a new mechanic. Preserve the six original matching views, with no synthetic angles, bending or extra appendages.
- **Original RGB is audit/reference only. It must not enter the generated-source or distributable art package.**

## Exact selector and reuse

`animate=1`, `ani=12`, `enemycycle=0` initially. The source increments before selection and wraps to1 after12:

`171,171,190,190,209,209,228,228,247,247,266,266`

This is a12-update loop, not independent real-time animation. Each unique frame occupies two horizontally eligible update steps. Animation advances when `-29 < ex+tempMapXOfs <300`, including while the actor is too high to draw; the small sprite draws only when `ey>-13`. Thus the first visible frame need not be171. Keep source state/timing and never synthesize new rotations.

All **1,701 loaded enemy records**, including the second bank, were decoded. Only **records3 and16** directly reference these bank1 bases; no other record’s24×28 quadrants overlap any of the six source tiles. Record16 shares all six art frames, animation, size and lifecycle forms. Its only table differences from3 are rawarmor12 vs2, xaccel0 vs92, and startx150 vs130. It is absent from the first-level scheduled/drop/launch closure. A bank+frame binding naturally affects16 elsewhere; that context is not tested here.

The only source table launcher targeting3/16 is **boss record53→type3**, frequency90. Its scheduled spawn is event5356, source-predicted tick6709; actual launches depend on survival, positioning, firing/launch overrides and slots. Keep it with the later whole boss family; no boss acceptance is claimed. No record’s default death drop points to3/16.

## Damage, filters, removal, drops and weapons

- Type3 rawarmor2; actual armor is difficulty-scaled. `explosiontype0` yields `enemyground=true`, `explonum0`, despite sky-lane placement. This flag matters for tint/ice, not art size.
- `dgr=dani=dlevel=0`: no damage/wreck sprite or separate damage animation. Nonlethal hits keep the same current frame and may apply the engine’s filter. Ice can set40 ticks and filter0x09. Original indexed expression is `filter | (source_index &15)`; existing RGBA enemy filtering maps brightness through the palette ramp and retains alpha. Do not replace it with baked art or alter timing.
- Normal lethal destruction frees the enemy and uses generic small explosiontype1, `newsh6:122..133`; hit effecttype0 uses146..152. These are separate, already mapped families. No shadow call exists for this enemy path.
- Movement removal after updates occurs if ex<-80/ex>340 or ey<-112/ey>190. Generic frame999 also removes actors, but this table contains no999.
- No turret (`tur=0,0,0`), initial fire (`freq=0,0,0`), own launch or default drop. Value5 is kill cash, not its own pickup sprite. First-level scheduled instances have link0; no level event33/45 assigns drops to link0. Type16 likewise has no own turret/drop/launch.
- Scheduled type3 movement uses horizontal pursuit xaccel92 and positive y-acceleration every8 updates. Event positions overwrite the randomized initial x with left20/right250 relative to map origin; event creation sets y=-28. Preserve original RNG consumption and movement even though the randomized x is overwritten.

## Visibility: predictions are not observations

The first-level has30 explicit type3 event15 spawns:

- Wave1: event4190–4350, scalar predicted ticks6145–6225, left5/right5/left5.
- Wave2: event4695–4855, scalar predicted ticks6398–6478, same side sequence.

The scalar clock was previously matched to retained actual curLoc through5956. These later ticks remain **source predictions**. Source speed changes at event4020→tick6060 explain the later2-units/tick dispatch. Slot limits, actor death and actual play can prevent exposure.

This audit scanned all61 existing material streams found at scan start,50 distinct compressed hashes. All61 parsed; their latest recorded tick is5956. **No matching type3 bank-qualified material row exists in those retained streams.** The historical ordinary first30 index also has none. See `retained-material-scan.json`; duplicate run counts are never merged.

Parent requested a small retention add-on during a separately approved existing late-spike replay. The handoff supplied:

- bounded primary ticks6145–6249 inclusive (first wave plus24 updates)
- category `enemy`, sheet `newsh2.shp`, id in171/190/209/228/247/266; expected tile_id=id and12×14
- only if the first window yields nothing, optional second-wave6398–6502
- no extra replay/capture requested by this audit

Any resulting fresh evidence will be a separate receipt, not retroactively part of the61-file scan. Material rows prove ordered rectangle references, not final unoccluded RGB. First-level sky actors are drawn before layer3 (`background3over=1` from event3500), and later layers/projectiles/effects can occlude them. Existing scene-enemies/scene-hits are restricted to records121–124 and cannot prove type3 lifecycle. The current unmapped enemy callback returns before scene-draw logging, so absent callback rows are also not proof of absence.

## Smallest existing route versus composite route

`blit_enemy` already calls `render_mirror_enemy_tile` once for each small sprite, passes its exact bank, base, part0, filter and size context, then always executes the original indexed blit and ends suppression. Keep that call order intact.

Current `scene_asset` hardcodes24×28; the end of `render_mirror_enemy_tile` assumes anchor6,7 and a quadrant. **Adding these six IDs to that allowlist alone is incorrect**: small HDR1 files fail its size/anchor validation, while padding them to composite size creates a false region/anchor contract.

The smallest finite future integration is a six-ID, bank1/role101, part0, size0 branch within the existing callback, with12×14/anchor0,0 cache entries, using the existing `read_asset` and `draw_asset_filtered` with the original filter and no quadrant. Existing `get_asset(ENTITY_TILE)` and `render_mirror_enemy_shot` demonstrate12×14 storage/drawing; neither currently binds these dynamic banks, and generic entity dispatch does not carry enemy filters. No new general renderer, game-state hook, rotation algorithm or entity rewrite is needed. A coherent six-member preflight/fallback can follow the existing finite-family pattern. Cache slot numbers must be selected against the eventual integrated head, not frozen here.

All six are absent from every current manifest pack and have no finite enemy binding. Identical numeric IDs in shots, terrain, `newsh4` or other banks must remain separate. In particular, player guided-missile171 is bank8, not this bank1 family.

## Files and source pointers

- `art-input-contract.json`: precise six-frame authoring and source lifecycle contract
- `source-record-proof.json`: all1701-record reuse scan result, exact records,30 spawn events, related events, manifest absence and source hashes
- `retained-material-scan.json`: per-file historical evidence bounds and hashes
- `verification.json`: clean checkout, independent decode and no-run boundary
- extraction/audit scripts reproduce the receipt without executing the game

Key pinned source: `src/tyrian2.c:165–265` (draw/animation), `:306–330` (movement removal), `:1548–1760` (hit/death), `:4035–4170` (record initialization), `:4285–4360` (event creation), `:560–633` (launch), `:4833–4860/:4940–4965` (drop assignment). Renderer: `src/render_mirror.c:1119–1139` (HDR1 contract), `:1162–1195` (small storage), `:1270–1286` (filter), `:1457–1479` (small-shot versus composite), `:1590–1673` (enemy callback). `src/sprite.c:525–560/:679–711` is authoritative RLE/filtered indexed writing.
