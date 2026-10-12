# Circuit/deck10: generated-only frozen art v1

Status: root-approved offline material and canonical map contexts; actual-game candidate review remains pending. No production source or renderer edits in this package.

## Exact scope

Layer3 shapesZ IDs181/182/184/185/192/193/194/195/201/202, sorted order maps to proposed asset slots349–358. Each output is192×224 RGBA, density8, logical24×28, anchor0,0, fullyopaque. HDA header is HDR1 plus six little-endian uint32 values:2010000+sourceID,8,24,28,0,0. Source191 is unplaced reference-only and is excluded.

The art preserves intentional orthogonal circuit routing.201 remains the distinct vertical repeat;181 the horizontal design;182 is an E/W/S tee;192 a four-way cross;193 is a N/W/S tee with a closed right rock rim and short internal branches;185 and194 are W/S and N/E elbows. Deliberate mechanical repeats are retained.

## Rebuild

Requires Python3+Pillow, ImageMagick convert, and a C++17 compiler. Run:

    python3 rebuild.py /path/to/NEW-output-directory

The output directory must not already exist. No original game data, main checkout, or external art package is required. Inputs are hash-checked against inventory.json. Resize/crop and semantic-mask compositing reproduce exact decodedRGBA and HDA bytes for all10. PNG encoder metadata may vary; canonical selectedPNG file hashes are separately recorded.

## Authored sources and protected interfaces

sources/generated-approved-pilot-v2.png is the selected imagegen tonal revision of the initial coherent first-spur rendering. Its generated predecessor has SHA256 c55e67bcd339afb6bc5d2a587cd7acfa0706ed2dc1ba41c6642e45dd74066d8b; its prompt is retained, but that unselected predecessor is not a rebuild dependency. sources/generated-remaining-five.png finishes the other five source-specific connectors against actual-neighbor reference contexts. Prompt text is retained. Original game raster guides and screenshots are excluded.

sources/frozen-approved-gray132.png is previously accepted generated gray-island artwork, used only inside each new circuit tile's stone margin. Whole external gray18 and purple6 tiles remain unchanged. Current accepted variants share the relevant facing9/10output-pixel border bands with132; this does not authorize replacing their entire tiles. Technical semantic masks represent clean metal domains rather than a color-threshold classification of old pixel shading.

The C++ port fit uses the already selected generated181/201 profiles within8output pixels, one logical pixel, of active openings. Two facing pixels use full authority; the remaining six taper inward. Only active opening RGB changes. The original pilot interiors beyond this narrow interface band are unchanged; alpha remains255. No blur or global palette rescale is applied.

## Static coverage and limitations

Whole-map closure is197placements,96cardinal+156diagonal pair types,1244directional occurrences. All28actual connecting metal pair types,187occurrences, have zero RGB mismatch on their active faces. All10 alpha and protected margin checks pass. Independent visual review covers all10 source routes and five actual-map offline contexts. Source191 remains excluded; other original debris161/162/171/172 intentionally remains original where visible in references.

Canonical sources have actual material sightings through private-survival tick4960. Existing normal4320 proof exposes the first spur with181/184/195/201/202; this source evidence is not yet runtime acceptance of the new art. Integrator should test native2×/4×4320, bounded all10 visibility, current foreground order/state parity and finite missing/invalid fallback before publication. No hidden layers are needed for this motif.
