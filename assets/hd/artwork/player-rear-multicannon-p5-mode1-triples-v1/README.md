# Rear Multi-Cannon P5 mode1 fixed-canvas triples

This generated-only family adds only normal-bank triple heads3/41, densities4/8,
role131, for player1 rear10 power5 mode1, exact record258. Source, ordinary-call
and gameplay gates are separately enforced. Later powers and physical aliases
sharing these IDs receive no permission. Ordinary P5 acquisition is not
established; any runtime qualification must be explicitly diagnostic.

Independent technical art review passed with the explicitly accepted tail-clipping
deviation. Native4x outer red/orange tips end on mild blunt edges, clearest on
pale backgrounds. Native2x triple separation and direction remain clear, and
bright heads remain intact. This does not claim seamless taper or whole-lobe
brightness/alpha/RGB/luma preservation.

The exact already accepted R2 components are used at their authored densities:
- ID3: flipY(1)+(-2,-5), flipY(1)+(0,-1), 1+(-2,+5).
- ID41: 39+(+2,-3), 39+(0,+1), flipY(39)+(+2,+3).

A reflection covers the full12x14 canvas before integer logical translation.
The output stays on that12x14 canvas with anchor(0,0), and occupied logical
bounds[0,1,12,13]. Original component lobes are disjoint and reconstruct the
original geometry after each outer lobe clips one occupied tail cell. This
geometry was verified separately; original pixels, indices, coverage masks,
palettes, decoded game data, source offsets and reference captures are absent.
Generated smooth support is not a trace of the original indexed coverage mask.

Generated alpha supports are disjoint even before clipping. Every one of six
orders has identical retained bytes; no blend choice or roundoff is introduced.
Retained RGBA samples copy exactly from accepted components. There is no new
generation, resampling, interpolation, blur, recoloring, normalization, support
beyond the clipped component union, canvas expansion, or added margin. Only
retained plus discarded samples equal three full lobes; retained samples alone
do not conserve the full multiset or energy.

Authored clipping is exact and bounded:

|ID|Density|Lost samples|Lost alpha sum|Max lost alpha|Lost alpha %|Lost luma %|
|---|---:|---:|---:|---:|---:|---:|
|3|4|26|2646|231|0.750453|0.399072|
|3|8|82|11628|255|0.812253|0.436325|
|41|4|20|1926|215|0.580843|0.287289|
|41|8|64|8390|250|0.622350|0.312028|

Some discarded samples are fully opaque. Native sampled alpha loss can reach
0.964561%, and native luma proxy loss0.524773%. Numeric energy uses existing
encoded8-bit RGB multiplied by alpha; luma weights2126/7152/722. These are
reproducible proxies, not linear-light photometry or perceptual brightness
claims. Exact per-part, sample and native1x/2x/4x metrics are preserved in
output/component-manifest.json. Its preview-only status is a frozen historical
stage record; current package scope is in binding.json. Those offline sampling
checks do not establish gameplay qualification.

Rebuild using Python3 standard library only, into two fresh separate directories:

    python3 build.py --output NEW_ART_DIRECTORY --hda-output NEW_HDA_DIRECTORY

Default inputs are eight already published PNG/RGBA files in the sibling
player-rear-multicannon-p1-six-v1/output directory, IDs1/39, densities4/8.
Use --source for a relocated folder containing those eight files. No input
copies are bundled. The wrapper retains the reviewed build_components.py and
frozen-inputs.json byte-exact, validates all input and output pins before writing,
and reproduces all nine frozen output files. It uses temporary staging and does
not create cache files in artwork. Existing, overlapping, source-contained or
package-contained output destinations, changed inputs and corrupt output pins
are rejected. Fixed uncompressed DEFLATE and zero filters reproduce PNG bytes
without relying on image-library encoder versions.

HDR1 header is role131 key1310003/1310041, density4/8, logical12x14, anchor0,0.
Both existing default packs receive identical payloads using the historical
rear-multicannon-p1-bank8 filename prefix. Missing/invalid exact-density assets
fall back to indexed drawing. No other pack receives these resources. Existing
P1-P4, P5 mode2, generic, enemy and other resources remain byte-exact. Earlier
family scope descriptions stay byte-exact as historical records.

The cache-free reviewed-art checkpoint and sanitized art review are hash-pinned
in provenance.json. No bytecode or cache is included in this package.

file-manifest.json pins every package file except itself. The catalog is purely
additive: one family, four PNG source mappings and eight pack entries. Removing
those additions restores the baseline catalog bytes; all7093 old non-manifest
asset files are preserved. Catalog counts are3446 total pack entries,658 source
mappings,658 unique mapped PNG paths and654 unique mapped PNG hashes. The source
directory has724 PNGs and718 unique PNG hashes; pack entries reference617
unique source PNG paths and613 unique PNG hashes. Each default has605 entries.
Runtime, ordinary P5 acquisition, whole-campaign,
performance and Windows acceptance are not established by this asset package.
