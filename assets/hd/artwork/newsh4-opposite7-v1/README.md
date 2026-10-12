# Opposite brown strip: frozen seven-piece art

Root approved the offline pilot after native 2× review on 2026-10-12; the art author inspected its native 2× and 4× comparisons. This package preserves its exact seven images. Actual moving, hit, ice, link2 removal and source-count gates remain separate; left/link1 QA does not establish right/link2 correctness.

## Exact scope

Enemy records73–79 use bank2/newsh4.shp bases231/233/235/267/269/271/273. Each complete composite is24×28 logical pixels, with anchor(6,7), density8 and quadrant offsets0/1/19/20. Seven ascending bases form one horizontal168×28 assembly. Every original piece was inspected independently. The source differs from the other family mirrored at1,028RGBA cells, including51 silhouette cells; the approved other-family master was only a material reference.

Opacity is the exact original RLE support, repeated8×. The per-piece support counts are110/201/229/263/295/425/504, totaling2,027. Every opaque original entry is nonzero. Quadrant231 itself is empty and232 owns only2 cells; the full base231 composite remains valid through its lower quadrants. Preserve its composite route rather than treating a blank first quadrant as a missing object. All six piece joins retain their original support rows and the269→271 asymmetry. Fully transparent output texels are RGBA0.

## Rebuild and integration

Use Python3 and Pillow12.3.0, then `python3 rebuild.py --output /absolute/new/external/output`. The parent directory must exist. The builder rejects existing, relative, symlinked or in-package output paths and validates source hashes before writing. Its only raster inputs are sources/generated-whole.png and masks/alpha-assembly-logical.png. Canonical PNG/HDR1 files and original game RGB are not read as build inputs.

The generated master is registered by its visible alpha (>16/255) bounding box[122,196,2050,507) into[16,8,1344,208) within the unchanged1344×224 assembly canvas. This corrects imagegen placement drift without per-piece recentering. Generated straight RGBA is composited over technical dark-brown matte(12,8,0), assigned the exact original support, zeroed outside that support, then partitioned into seven192×224 images. Rejoining the seven pieces is byte-exact to the single assembly. Intermediate drafts remain preserved separately.

The seven output/enemy-newsh4-{base}-8.hda resources are HDR1: magic plus six little-endian u32 values(key=1020000+base,density8,width24,height28,anchor6,7), followed by172,032 row-major RGBA bytes. Each file is172,060 bytes. Namespace102 belongs to newsh4; identical IDs in other banks are unrelated. Do not mutate global original sprite quadrants. A finite renderer/manifest binding and original source guards are the integrator’s responsibility.

## Behavior and evidence limits

The source baseline is349b3ca. Three original groups use link2, with left-then-right acceleration opposite link1. Static artwork still moves. Ice does not freeze that movement. Armor50 has original difficulty scaling; original ground-hit/ice filtering, linked removal, record79 reward1000 and ground explosions remain authoritative. No alternate hurt/wreck image is selected.

First retained rectangle references begin5568 for six bases and5574 for273; its right quadrants appear5578. First-group references end5617. These are retained source/draw evidence, not proof of final exposure; later layer3 can occlude the strip. The5640 screenshot of the other orientation is not a right-family proof. The metadata audit checked all1,701 episode1–3 HDT records and found no other bank2 users of these28 quadrants. Episode4/5 custom tables and other routes remain outside that audit.

This package contains generated art, prompts, a technical binary support mask, source metadata and compact offline/rebuild proof. It excludes original-reference RGB/indices, comparison screenshots, private machine paths, caches and old actual-QA claims. The exact source audit was normalized only by removing the workspace prefix; its original digest is recorded in contract.json. Its historical “binding missing” fact applies to349b3ca, not later integrations. No game execution, capture, code edit or publication is performed by this art package.
