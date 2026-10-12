# Late six-piece source family, artwork v1

Reviewed generated artwork for newsh2.shp bases 1, 3, 5, 7, 9, 11 (enemy types 23, 22, 21, 18, 19, 20 respectively). Each is a 24×28 logical composite, anchor (6,7), canonical density 8. The two source triplets are distinct: no mirrored mask or recentered sprite is used.

The approved steel/red palette and refined cylindrical forms were generated as two continuous assemblies. Whole-triplet registration then applies the exact original six RLE support masks, clears RGB under transparent pixels and splits at 24-pixel boundaries. Central pieces 3 and 9 are each reused unchanged. Four source layouts contain 7/9/8/9 actors on links 7/8/9/10; they are separate outward-moving rows, not one six-part object.

## Reproduce

Use Python 3 and Pillow 12.3.0, then run `python3 rebuild.py --output /absolute/new/external/directory` from any location. The output parent must exist. The output must be absent and outside this source package; relative, existing, nested and symlink paths are rejected. The builder needs only its generated master, prompt identity, technical binary masks and expected hashes. It does not read canonical output files or original game assets.

The builder verifies all inputs before output, reconstructs each PNG and HDR1 byte-exactly, validates original opacity support, and proves split/rejoin equality for both triplets. HDR1 stores key 1010000+base, density8, width24, height28, anchor6,7 followed by 192×224 straight RGBA (172060 bytes total). No runtime mapping or code is included.

## Provenance and scope

Built-in image generation used `sources/prompt.txt` and the original two-triplet layout reference; the reference is not included. The immutable generated master is retained in `sources/`. The original source file identity and decoded opacity/index hashes are recorded in `proof/source-contract.json`. Only technical binary masks are included from original pixels. Original indexed/RGB assets, comparison screenshots and private machine paths are excluded.

Root approved all four assembled native2× comparisons on 2026-10-12; the artist also checked native4×. The source-only package does not establish actual exposure, timing or combat behavior. The original source has one static frame per record, no alternate damage/wreck shape, and original procedural hit/ice filters and linked explosions. Later layers can occlude the rows. Source projection shows natural camera limits for the outer caps; do not claim every pixel or quadrant is naturally visible.

Preserve existing movement, armor, original filter arithmetic, links, score awards, lifecycle, layer order and fallback. An independent bounded runtime trial is required before publication.
