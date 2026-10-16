# Rear Multi-Cannon P5 mode2 twin composites

This generated-only package adds only twin heads277/278 at density4 and8 for
normal-bank player1 rear weapon10, power5, mode2, exact record269. Independent
offline art review passed. Diagnostic runtime qualification is recorded separately.
It does not claim a natural P5 purchase or actual-game PASS: ordinary starting
funds cannot buy P5. P5 mode1 remains classic, and Christmas artwork is excluded.
No full-campaign, performance or Windows qualification is claimed.

Each twin uses two exact accepted R2 components281 or282 on the unchanged
12×14 logical canvas with anchor(0,0). The upper copy at(0,0) is background;
the lower copy translated to(0,+4) is foreground. lower_over_upper is the
explicit reviewed HD assembly convention. The original normal-bank lobes are
disjoint, so their internal order is unobservable. upper_over_lower is only
numeric comparison evidence in overlap-analysis.json; it has no production
PNG, RGBA or HDR1 resource here.

Composition is exact rational Porter-Duff source-over in the existing encoded
RGB space. Alpha and straight RGB are independently half-up quantized once.
There is no new generation, resampling, filtering, blur, recoloring or alpha
normalization. Only five overlapping samples per target/density change;
nonoverlap RGBA is preserved exactly, support equals the translated union,
and no nonzero source samples are clipped. Full-density alpha sum falls22
at density4 and12 at density8 versus two copies. Stored RGB energy is not
exactly additive: overlap and 8-bit quantization produce the documented small
channel residues, including blue increases45/22. No compensation is applied.
Exact sample arithmetic, native nearest-sampling consequences and both
orders' numeric comparisons are in overlap-analysis.json. These are offline
calculations, not runtime qualification.

The only inputs are eight existing published PNG/RGBA files from
../player-rear-multicannon-p1-six-v1/output/rear-multi-{281,282}-{4,8}.*.
Their repository-relative paths and exact hashes are in inputs.json.
No input duplicates, original game data, decoded originals, masks, palette
or captures are included or required. provenance.json pins the published
baseline, reviewed export, selected outputs and independent art review.

Rebuild with Python3 standard library only into fresh separate destinations:

    python3 build.py --output NEW_ART_DIRECTORY --hda-output NEW_HDA_DIRECTORY

The default source is the sibling accepted R2 package's output directory.
Use --source to point to a relocated folder with only the eight pinned files.
Output PNG encoding uses fixed uncompressed DEFLATE blocks and zero filters,
matching the reviewed bytes independently of image-library encoder versions.
The builder validates all PNG/RGBA input pins and selected PNG/RGBA/HDR1
output pins before writing. Existing or overlapping output destinations and
modified input are rejected. The focused asset test independently recomputes
every pixel with rational arithmetic and verifies a fresh relocated rebuild.

HDR1 resources use role131, keys1310277/1310278, exact density4/8, logical12×14
and anchor(0,0). The historical loader prefix rear-multicannon-p1-bank8 is
retained. binding.json records both current default-pack copies and catalog
PNG mapping. Each twin needs exact-density source and call qualification;
missing/invalid resources retain indexed rendering. Existing183/182 remain
byte-exact density8-only and indexed at density4. Existing77, P1–P4, generic
resources and old catalog scope descriptions are unchanged.

file-manifest.json pins every file in this package except itself. The catalog
change is a pure addition of one family, four source mappings and eight pack
entries. The resulting catalog has654 HDA-key source mappings with654
unique mapped paths and650 unique mapped PNG byte hashes; the source directory
contains720 PNG files with714 unique PNG byte hashes. Pack entries reference
613 distinct source PNG paths with609 distinct PNG byte hashes. Removing the
new family and its mappings restores the baseline catalog byte-for-byte.
