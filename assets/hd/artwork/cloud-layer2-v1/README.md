# Selected 15-tile HD cloud family

Generated-art handoff for the authorized OpenTyrian2000 HD branch. This folder contains no original game RGB tiles, game distribution files, full map images, screenshots or private capture executable. The original data remains external.

## Contract

- shapesz.dat, layer2 only; IDs41–45,51–55,61–65, one-based.
- Original cell24×28, anchor0,0; output192×224 RGBA, density8.
- HDR1 header: [2010000+ID,8,24,28,0,0].
- `selected-manifest.json` is the exact selected ID/header/hash/source inventory. Its `source_png` entries point to the committed formal PNG set. All15 HDA bytes match the independently tested cloud-v1 runtime package.
- Merge these15 HDA files into the existing selected preview/debug pack, preserving all other resource bytes. Do not replace the whole current pack with an older background-test base pack.

## Authorship and reproducibility

RGB authored with built-in imagegen; raw source `source/imagegen-atlas-v1.png`, prompt `prompts/imagegen-atlas-v1.txt`. ImageMagick registers tiles and reconstructs the original low-resolution opacity contours with soft continuous edges. Native GEGL creates a periodic common RGB boundary substrate; distinct cloud interiors are retained. A deterministic C++ pass reconciles97 compatible observed neighbor pairs over16HD pixels. Three incompatible original full-map pairs are intentionally not forced equal (43↓62,45↓54,45→54); no complete-level arbitrary-adjacency claim.

Requirements: ImageMagick7 `magick`, GEGL0.4 introspection available to `/usr/bin/python3`, Python3+Pillow, C++17 compiler. From the repository run `python prototype/build-cloud-art.py --output ../cloud-art-check --data <legal-Tyrian2000-directory>`. The wrapper copies this source into a new external directory, sets `TYRIAN_DATA_DIR`, and runs `rebuild-selected.sh`. The script reads only15 opacity masks from the external shapesz.dat, writes a private work-mask-reference folder, and deterministically regenerates the15 PNG/HDA files. Do not commit the work-mask-reference, temporary registered PNG/raw files, compiled helper, original data or test evidence images.

Fresh reconstruction already matched all15 tested HDA byte-for-byte and every decodedRGBA pixel. ImageMagick PNG date metadata may differ; the selected committed PNG file hashes remain separately checked. Generation itself is not deterministic; saved imagegen source is the rebuild starting point.

## Integration conditions

The production terrain binding adds the finite layer2 family and has a cloud-only MIRROR_BLEND guard. It does not modify public filtering or the blend operator. Highest-detail wild mode deliberately retains the original clouds; the guard was verified to preserve its full116tick output byte-for-byte versus baseline. Missing-all-cloud fallback matches existing runtime; missing54 falls back only54.

The accompanying reviewed HD-cloud shadow correction transfers the original palette before/after ratio only on still-cloud-owned pixels. It retains the original blue floor under stacked indexed shadows without changing other HD families. Full details and acceptance limits are in `docs/CLOUD_LAYER2_VALIDATION.md`.

## Proven coverage

Episode1 physical-level9, first522ticks (~15.0075 configured seconds), actual4×1280×800 and2×640×400 windows, repeat presentation. All15 cloudIDs drawn,22302/22302 HD cloud references, unchanged game state/RNG/collisions/indexed pixels and HUD, zero coverage/classicRGB audit mismatch. All77 observed first15-second cloud adjacency relations lie inside the compatible set. A120-frame3.45s actual-scroll clip is captured separately, not an offline animation or full-level acceptance.

Ground terrain is not upgraded by this batch. Windows/GPU/physical2K/full-level validation is not claimed. Rollback removes only these15 cloud bindings/resources and the scoped engineering cloud-shadow addition, preserving the previously accepted assets.

## Selected edge revision2

Only cloud55 changes after the user flagged its repeated straight notch at tick144. Saved imagegen source `source/imagegen-edge-context-v2.png` authors a freer alpha perimeter. `rebuild-selected.sh` reconstructs the15-tile base, then runs `source/apply_edge_revision.sh`; do not overwrite the corrected55 with its old reconstructed opacity mask. The localized registration preserves all four outer-edge RGBA rows and all97 compatible adjacency pairs. The other14 tiles, header/anchor, binder and shadow code remain unchanged.
