# Six-tile dark ground foundation for the bounded level9 scene

Selected terrain IDs341/342/343 above351/352/353 form a72×56 logical ground footprint beneath the six-part gray stone assembly. This package contains generated-only source and finite replacement assets, not the overlying object. The charcoal center, subdued gray fragments, warm brown perimeter and full opacity are preserved. A first draft was too bright and raised; the selected second imagegen revision restores low embedded fragments rather than substituting a new standing assembly.

## Finite integration

Reference checkpoint: `51d4bc4af5ab63c1357e11911c8013e8e028e68b`. Slots341=247,342=248,343=249,351=250,352=251,353=252. Preserve separately reserved craft243–245 and terrain113=246. These six require asset capacity at least253. If113 is installed first, terrain registry116→122. This is an asset/binder update; no renderer, map, event, physics, palette, shadow or entity-canvas change is included.

Each file is172060 bytes: `HDR1`, then six little-endian U32 values `[2010000+ID,8,24,28,0,0]`, followed by192×224 straightRGBA. Every alpha byte is255. Original near-black ground is opaque; it is not treated as a transparent cutout. Missing or malformed resources retain original fallback.

## Complete local family and seams

The physical level map has one complete3×2 instance at top-left(row243,col10), plus an intentional right-map-edge2×2 instance at(row223,col12). The map ends at column13, so that second instance has no rightmost343/353 column. No invented tiles extend it beyond the map. All ten placements were audited, comprising19 canonical cardinal pair types/27 unique actual edges, plus43 all-eight-neighbor types/57 actual edges. External cardinal neighbors are the already accepted101/110. Numerically nearby344/354 are empty, and361–363 do not appear in this map.

A native C++ harmonic correction is confined to32 HD pixels inward from each new tile border. Only these six images change. New-to-new facing edges are exact. Frozen101/110 constraints have intrinsic differences, leaving a maximum6 RGB residual at a few texels; those accepted neighbors remain byte-frozen. Complete and map-edge native2× and4× composites were visually approved. This is full static closure for this level, not runtime coverage of every placement or all game levels.

## Generated source and standalone reproduction

The built-in imagegen masters were generated and revised in an exact5×4 original-map neighborhood, then registered with native ImageMagick Lanczos to960×896. The selected central3×2 region is `[192,224,768,672]`; six literal192×224 crops are included under source/generated-crops. Full masters contain contextual reference imagery and remain private, with their hashes and exact crop geometry recorded in source/crop-provenance.json. Included crop RGB is newly generated artwork, not original indexed-game raster colors.

The standalone rebuild includes only numerical RGB perimeter constraints from accepted HD101/110, not full neighboring raster assets. It needs Python3 with Pillow and a C++17 compiler; no original game data, repository checkout or base-pack path is required:

    bash rebuild-selected.sh /absolute/new-output-directory

All six selected RGBA payloads and HDA files reproduce exactly. Committed PNG file hashes are separately verified; the current rebuild also reproduces all six PNG bytes exactly. Encoding changes across Pillow versions do not substitute for the required decoded-RGBA and HDA checks. Geometry, complete opacity and exact source hashes are verified.

## Overlay, removal and evidence limits

The original entity is newshE bases1/3/5 above39/41/43, types516–521, event1308/link29. Actual original logs at1372 place terrain at x212/236/260,y0/28 and the corresponding entities at y1/29. The object therefore remains exactly one logical pixel below the terrain origin. The exposed top strip and hidden ground are retained; no object canvas is enlarged.

A separately verified private original-hit diagnostic applies1 damage at1401, then lethal19 damage at1403. All six linked components are absent from1404, while every ground tile remains drawn through1463. No alternate wreck art is present in those loaded records. An original-data offline overlay/removal contact confirms the selected foundation reads as low ground after the unchanged object disappears. Actual runtime candidate/reveal and scale tests are being performed separately by the engineer and are not claimed as completed in this art-source package.

The requested next window is ticks1044–1565. Earlier natural-end weapon71 fixtures supply ordinary overlap only through1052. The current51d no-weapon-injection replay is still an explicitly modified private survival diagnostic; its78,368 selected material rows match the earlier identity trace. The full ground group is on-screen1372–1500. Cloud commands appear1400, bounding boxes enter1401, and actual nonzero cloud pixels begin1404. Cloud opacity and accepted assets remain unchanged, and can obscure later foundation views. Neither private survival nor artificial original-hit evidence is an untouched ordinary playthrough.

## Exclusions and rollback

Original source data, palette/index arrays, reference PNGs, original entity exports, runtime captures, videos, executables and private survival/hit hooks are excluded. Only the finite generated art/source package is intended for integration. All prior art and the superseded first draft remain preserved outside this package. No claim is made that the next15-second segment or six-part entity art is fully finished by this ground-only batch.

## Repository layout

Use `python prototype/build-next-terrain-art.py --output <new-external-directory>` from the repository. Formal PNGs are stored once under `assets/hd/source`; the wrapper verifies their hashes and supplies temporary copies in the standalone package layout before rebuilding. This preserves the original committed-PNG hash check without duplicating formal PNGs in Git. No original game data is required.
