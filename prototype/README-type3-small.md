# Type3 six small sprites: source validation

Historical implementation predecessor: `e6fd18a8d53c31f90d15c0ac1bce9d0e927336ac`. Recovery predecessor: published `b2a6e4a1e924aed71630f9f63c0ba4648e920d6d`. This append is finite: bank 1 / newsh2, namespace 101, IDs 171/190/209/228/247/266, cache slots 416–421. Each member is a single 12×14 logical tile, density 8, anchor (0, 0), draw part 0 and a 96×112 authored image. It must not inherit the 24×28 composite dimensions, four-part routing or (6, 7) anchor of another family.

The immutable package lives at `assets/hd/artwork/type3-small-six-v1`. Its inventory SHA256 is `5012962c54ab3fd0b22cc8a2534fddee272704fa73447e267ffeb4938f787c33`; its art-input contract SHA256 is `9c8934790afb66ba2431be75ba68b20a22ad58b522c8db85661a849288cd8686`. Closure comprises exactly 31 files: 17 input files, the inventory, twelve PNG/HDA outputs and the rebuild receipt. Both prompts, generated master, recipe, technical masks and source proof documents remain byte-identical. Unknown files, empty directories, special files and symlinks are rejected.

Opaque logical counts in ID order are 98/82/82/74/82/82, totaling 500 cells. Six frame-specific binary alpha masks contain three distinct supports; nearest-neighbor 8× enlargement is exact. Every HDA is exactly 43,036 bytes: `HDR1`, six little-endian u32 values `(1010000+ID, 8, 12, 14, 0, 0)`, 43,008 RGBA bytes and EOF. SHA256 validates PNG encoding, full RGBA, HDA and canonical source identity. The manifest's FNV1a64 stamps are derived from that full frozen RGBA; they supplement the authoritative SHA256 provenance checks.

Preserve the transparent RGB bytes exactly. This selected source uses a technical matte, (8, 6, 2), beneath its alpha support. Replacing transparent RGB with zero, even while keeping the same visible alpha, changes the frozen artwork and must fail validation. Reproduction uses only the generated six-frame master and technical alpha masks; it does not sample original palette or indexed/RGB artwork.

Only the two established default packs receive these six 8× HDA files, plus their exact canonical PNG/index bindings. The validator rejects widened density, renamed key aliases, added pack members, changed default identities and mismatched metadata. Physical pack scanning also detects unindexed HDA aliases, including non-HDA filenames carrying these keys. Other families remain outside this validator's artwork scope.

## Recovery provenance

After the workspace reset, the builder, source guards and this README were restored byte-exact from the retained task transcript. Their recovered SHA256 values were respectively `ea30ac6ed5f6cb2c8a29f051a2b205a1f0d60e70e2ca88ac428ef18d66237028`, `466cd09e787efddce04fc2d04edc785926106b1c3e54268f716a4901e1611c0d` and `20863572e850e234eb6c988889c7a5f403bd084054a02a75f14a220e2bfa356d`. These are verified recovery identities, not claims that the prior files survived.

The recovered guard remains byte-identical. The builder then changes exactly one whole-file source-reader pin: `src/tyrian2.c` now has SHA256 `0a042621d599fdba15f89012c9bb1007327cd6f5df0e0a41865ea61c08856d02`, reflecting the published titleScreen-only menu hooks. The diff from the historical predecessor adds only those title-screen hooks; gameplay/event readers and `src/episodes.c` stay unchanged. The immutable frozen art and its historical proof are not rewritten. Fresh source and malformed-source receipts must be rerun on this recovery; historical passes alone do not establish readiness.

## Source-only commands

Choose a new absolute output directory whose parent already exists. It must be outside the repository and must not overlap the optional original-data directory. No source or original file is overwritten.

    python3 prototype/build-type3-small-art.py --output /tmp/type3-source-rebuild
    python3 prototype/build-type3-small-art.py --output /tmp/type3-original-rebuild --original-data /path/to/tyrian2000
    python3 prototype/test-type3-small-source-guards.py --out /tmp/type3-source-guards
    python3 prototype/test-type3-small-source-guards.py --out /tmp/type3-original-guards --original-data /path/to/tyrian2000

The wrapper validates the complete frozen import and all bindings before invoking the SHA-pinned recipe. It requires byte-exact reproduction of all thirteen frozen output files. Pillow 12.3.0 was used for this validation and is recorded in the frozen inventory; a different encoder/resampler cannot silently replace the approved bytes.

The malformed-source suite copies inputs to fresh external fixtures without hardlinks. It checks changed and missing forms of every frozen file, canonical PNG and both default pack files; every HDA header field, magic, truncation, trailing bytes, RGB under both alpha states, erased/grown/partial alpha; finite manifest scope, index aliases, duplicate JSON keys, unsafe paths, symlinks, special files, output guards and optional original-file identity. Each rejection must leave its requested output absent. It also rebuilds from an eight-file generated-only fixture (recipe, master and six masks) with no frozen outputs, proof records, palette or original game data available, then compares every output byte. Actual inputs and restored fixtures are fingerprinted at the end.

## Optional original evidence

`--original-data` reads only SHA-pinned `newsh2.shp`, `tyrian.hdt` and `tyrian1.lvl`. It independently decodes all six original RLE records, verifying record bytes, palette-index hashes and exact alpha support without using those RGB/index data as artwork inputs. The unchanged source readers are pinned too.

All 1,701 loaded enemy records are decoded. Only records 3 and 16 select or overlap these source tiles, including composite quadrants and direct damage selectors. Their complete lifecycle records match the frozen proof. Boss record 53 is the sole active table launcher of type3, at frequency 90. Record 803 stores the same launch selector but frequency 0, so it is dormant. No default death-drop record targets 3 or 16.

The first-level event table has 1,010 records. Scheduled type3 and boss53 events are checked against the frozen source proof. A conservative closure includes scheduled spawns, all four event-12 records, event-assigned drops/launches/replacements and active table launch/default-drop edges. Type16 is absent from that closure. This is source reachability, not evidence that any actor was actually visible or launched during a replay; predicted tick numbers are not revalidated by this script.

## Unchanged gameplay and remaining acceptance

The intended draw route uses the existing filtered asset drawing path and original scene accounting. All six resources are required before any member replaces its original tile. A resource failure disables only this family for its existing startup-selected cache lifetime. Geometry fallback is per call: a physical indexed 320×200 target with pitch 320, 8-bit / one-byte format and tile x in 0…308 is required to avoid changing the original RLE row-wrapping behavior. Partial top/bottom clipping remains distinct from resource readiness. No new timer, alternate damage frame, synthetic rotation or gameplay gate belongs in this source append.

Original animation holds each distinct image twice in a 12-step table and increments before selection on horizontally eligible updates, including updates above the visible area. Type3's ground flag permits original hit/ice palette filtering despite sky-lane placement. Its raw armor is 2, value 5 and own turret/launch/drop fields are zero. Original movement, RNG, lifecycle, collision and generic hit/death effects must stay untouched. The raw explosion type also makes body collision relevant outside private-survival setups.

The source receipt is `docs/TYPE3_SMALL_SOURCE_VALIDATION.json`. It claims zero game executions, zero captures and no native output. It does not establish production pixel composition, runtime fallback, animation/lifecycle acceptance, a native 2×/4× capture, body collision, type16's other-level context, later boss-spawn context, complete-level behavior, Windows/GPU behavior or publication. Those require separately authorized validation.
