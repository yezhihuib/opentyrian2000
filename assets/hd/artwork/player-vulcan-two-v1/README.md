# Frozen normal front Vulcan two-head art

Two newly authored code-native luminous ballistic effects for normal bank8 IDs67 and70. The source SVGs use continuous Bézier contours and vertical red/orange/yellow gradients. No original raster, pixel mask, traced staircase, external image, metal casing, smoke, exhaust, halo or animation is an authoring input.

The finite pair was visually approved at native2× on 2026-10-14 before freeze. ID67 is the single tracer for ordinary front Vulcan7 P1–6; ID70 retains two bright streak cores for P7–11. The complete authored pixels remain exactly those approved at that gate. Native1×/2×/4×/8× apparent bounding boxes preserve67=[4,0,7,11] and70=[3,0,8,11], scaled appropriately. Antialiased fringes can touch after tiny-scale sampling, but the two luminous cores remain distinct. The bright-core test uses alpha≥128 and G≥100, with 8-connected components.

## Asset contract

- Role8 ENTITY_TILE; bank8 heads67/70; normal source only
- Logical12×14, anchor(0,0), density8, authored96×112 straight RGBA
- Filenames bullet-67-8.png/.hda and bullet-70-8.png/.hda
- HDR1 header: magic plus6 little-endian uint32 fields: [80067 or80070,8,12,14,0,0]
- Each HDA is43,036 bytes; payload43,008 bytes
- Renderer slots522/523, capacity524; pending rear507–509 and Data510–521 are reserved separately. Slots are not HDA header fields.

Later authorized integration must guard !xmas before cache lookup and retain the original indexed shadow path. This art also affects shared normal player identities: Single Shot Option1, Satellite Marlo30 and Dragonwing/rear Vulcan15 charges0–1. It does not complete rear15 ordinary or later charge/linked heads. Enemy original blits, shop simulation and shop icons are separate and must stay unchanged. Ordinary shot phases are not an art animation. Christmas originals are ice-blue and must retain their original pixels.

## Standalone rebuild

Requires Node.js and the existing sharp0.35.4/librsvg2.62.91 environment. Run:

    node rebuild.cjs /absolute/path/to/new-output-directory

The output directory must not already exist. The script pins every source input and verifies generated PNG, straight RGBA and HDA hashes against inventory.json. It consults only this package. It does not read a game repository, original artwork, a source mask or the earlier pilot.

The formal package contains only newly authored SVG, generated output, code and metadata. Original comparison contacts and original RGB remain outside this package. Local art/source acceptance is not gameplay or runtime verification. No engine, production asset pack or GitHub change is included.
