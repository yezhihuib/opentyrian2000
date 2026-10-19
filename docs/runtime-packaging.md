# Separate runtime and development packages

`scripts/package_runtime.py` makes a new,
allowlisted runtime copy outside the source root; it has no network, deletion,
Git, overwrite, or source-move actions. A dry run is the default.

## Current selection and closure

`packaging/runtime-assets-v1.json` pins 694 selected files and 127,732,786 bytes,
excluding an optional executable and generated inventory/status metadata:

- One active manual gameplay pack: all 637 files, 95,176,717 bytes. Its four- and
  eight-density files and tested fallback resources are retained.
- Complete startup/title/settings pack: nine files, 17,780,592 bytes, with all
  shared UI font atlases, manufacturer cards and title layers.
- All twelve current optional shop HDAs: 2,329,034 bytes, flattened into that
  same startup directory, including the accepted generator and shield material.
- Three optional Data resources: 3,876,511 bytes. The Chinese text covers
  all 149 entries, its derived atlas contains 1,905 glyphs, and gold EXIT
  uses the accepted compact shop-font resource in both languages.
- One independently optional Data static frame: 4,096,128 bytes.
- Eighteen independently optional source-authenticated Data portraits:
  4,420,800 bytes, with exact native geometry and per-face fallback.
- Eleven license/provenance notices and three launcher/readme files:
  53,004 bytes.

This is an explicit snapshot, not a claim of a theoretically minimal asset set.
The complete selected gameplay directory is retained rather than stripping
untested fallback files. The preview/debug default pack copies have identical
contents at the public baseline; only one is included here.

The public baseline is `fedc541cc6b6e93f7748a85e6c40318b6ca9f5a8`.
The generator is a local-only addition from
`55d418de4f914d4694eb7f074458207b1cf6a2d2`; packaging does not publish it.
The shield material and integration are locally accepted source with no commit
assigned yet. Adding them does not advance the pinned public baseline.
Source paths, destination paths, sizes, Git-blob SHA1 and available SHA256 are
explicit in the allowlist. The public tree was complete (`truncated=false`), and
all selected local inputs are checked against pinned sizes and content hashes.
The copied inventory records SHA256 for every output resource.

## Optional dynamic shop shield

Exactly one resource is selected from `assets/shop-shield-v1`:
`shop-shield-option26-v1.hda` is copied to
`assets/startup/shop-shield-option26-v1.hda`. Its 72,992 bytes contain a 128-byte
`PSS1` header followed by separate alpha8 and Q4 tone planes for the accepted
396×92 material. The live shield draw's original hue/value and current palette
provide its equipment-dependent color; fixed-RGBA previews are not runtime
inputs. The existing public assets and license rows retain their original pins.

Only the `.hda` enters the runtime allowlist. Inspection PNGs, raw plane binaries,
authoring recipes, metadata and previews remain development inputs. The shield
is independently optional: an absent or rejected material retains the original
shield without disabling the other accepted shop resources.

## What stays in development

Original image-generation outputs, editable PNGs, font TTF source, exported asset
JSON, retained preview/debug packs, historical rebuild recipes, source, tests,
build objects and Git history do not enter the runtime copy. The classification
is recorded in `packaging/runtime-selection-v1.json`. The separate source-checkout
cleanup retires 16 superseded gameplay pack directories and three duplicate
startup subsets; their canonical sources, recipes and Git history remain intact.
See [retired packs and recovery](RETIRED_HD_PACKS.md). The packaging tool itself
never moves, deletes or deduplicates source files.

Font license and provenance notices still ship with their derived runtime atlas.
The compiled decoder's license and provenance notices are retained too.

## Dry run and build

From the source checkout:

```sh
python3 scripts/package_runtime.py --report /absolute/new-preflight.json
python3 scripts/package_runtime.py --build \
  --executable /absolute/path/to/opentyrian2000 \
  --output /absolute/new-runtime \
  --zip /absolute/new-runtime.zip \
  --report /absolute/new-build-report.json
```

Without `--executable`, this intentionally produces an assets-and-launchers copy;
its status states that the binary is absent. `--platform windows` names a supplied
matching executable `opentyrian2000.exe`. The tool never builds or downloads a
binary or its dependencies. An optional `--asset-root` can provide another
repository-layout root. For an explicitly approved local cache, `--source-map`
accepts a JSON mapping from selected repository-relative paths to existing local
regular files. Every mapped file is verified against the same allowlist; it
cannot silently replace a resource with a different version.

A complete input selection is required before any output directory is created.
Builds refuse unsafe paths, linked inputs, duplicate destinations, mismatches,
existing output paths, or output within a source root. The payload cap is
512 MiB, the directory-plus-archive budget is 1 GiB, and at least 4 GiB must remain
free. Copying is streaming. On interruption, a new partial directory remains
marked `INCOMPLETE`; the tool never deletes it or overwrites it on a rerun.
A completed directory has `COPY-VERIFIED.txt`, `RUNTIME-INVENTORY.json`, and
`RUNTIME-STATUS.json`. ZIP entries have stable ordering, timestamps, modes and
compression. Equal verified inputs produce the same ZIP bytes in the tested
Python/zlib environment; cross-version compressor identity is not promised.

To refresh the pinned selection after a separately reviewed asset change, supply
a complete recursive-tree metadata file for the pinned baseline:

```sh
python3 scripts/update_runtime_manifest.py --public-tree /absolute/tree.json
python3 -m unittest discover -s tests -p 'test_runtime_packaging.py' -v
```

The refresh tool only reads selected resource paths, notices and launchers. It
fails if the public pack inventory, existing published shop bytes, or current
shop-resource count changes. Update its pinned revision/counts only after
reviewing the new runtime closure. It never reads development test fixtures.

## Runtime dependencies and acceptance limits

Original Tyrian 2000 data, personal saves and optional user music remain external.
Linux requires compatible SDL2, SDL2_net and system libraries. Windows requires a
matching-architecture executable, SDL2.dll, SDL2_net.dll and their notices from
official distributions. These dependencies are described in the shipped README
and status report; absent DLLs are not represented as included.

Both launchers enable the packaged gameplay and complete startup/shop resources.
They preserve an existing marked dedicated manual-first-level profile and only
initialize windowed 2x/Integer settings when absent. Linux exports a dedicated
`XDG_CONFIG_HOME`; the engine uses its `opentyrian2000/` subdirectory for actual
config and saves instead of the regular user profile. Nonempty unmarked profiles
are refused. Launching remains ordinary local single-player play with the
project's existing first-level-9/15 HD scope and classic fallbacks.

Packaging unit tests cover missing/corrupt input refusal, safe path and symlink
handling, existing-output refusal, deterministic copy/ZIP output, loader-group
coverage, and a quoted-path/save-preserving Linux launcher witness. Hash/copy
verification is not whole-game acceptance, Windows execution, GPU/fullscreen,
performance or full-campaign certification.

## Earlier measured local copy (2026-10-19 UTC, before shield integration)

The directory and ZIP below are the earlier snapshot. They do not contain the
new shield material, and the updated allowlist does not rebuild or overwrite
either deliverable. A fresh copy requires a separately authorized packaging run.

Final corrected Linux copy: 666 selected payload files, 116,339,392 bytes including
its supplied executable. Inventory/status/completion metadata brings the generated
directory to 116,662,877 bytes (111.26 MiB). The ZIP is 42,983,612 bytes (40.99 MiB):

`1f1c10ba2a92c873f5edc391c3f952da8278b2c2d6566f5485cec766018fe7e5`

All selected directory payloads were checked again by size, SHA256 and pinned Git
blob SHA1; every selected ZIP member passed SHA256 and the full ZIP passed CRC.
Twelve packaging unit tests passed. A second full ZIP serialization to an
in-memory buffer reproduced the same 42,983,612-byte archive and SHA256 exactly;
no additional runtime directory or archive was created on disk. A bounded actual-engine Linux startup using
SDL dummy/software remained live for three seconds and exited cleanly after a
requested shutdown. The dedicated effective XDG config existed afterwards and a
separate ordinary-profile sentinel remained unchanged. The isolated first-run
profile initially lacked classic `tyrian.cfg`/`tyrian.sav`, producing the expected
first-run/default warnings; these were not asset-copy failures. No screenshots
were generated. No Windows runtime or PowerShell execution is claimed.

All gameplay asset bytes were reused from locally available, hash-matching
validation files. Only six missing startup resources (15,994,352 bytes) were
retrieved from the pinned public baseline. No full-project asset download was
needed. These measurements are a generated Linux runtime copy, not the previous
Windows source ZIP or a complete Windows release. That packaging run did not reduce, delete or rewrite the source project or public
repository. The later, separately reviewed obsolete-pack cleanup is documented in
[retired packs and recovery](RETIRED_HD_PACKS.md) and does not change this pinned
runtime selection.

## Optional Data-only Chinese

Two independent optional resources are copied under `assets/data-text-zh-CN-v1`: the complete bounded DCT translation and the subset DZF alpha atlas. Their OFL license and font provenance are copied under `licenses/`. The development catalog, merged JSON, source font, previews, and font manifest are excluded. Both launchers pass `--data-text-assets` with an absolute package-relative directory; changing to the dedicated save profile does not break resource loading. F6 in Data toggles English/Simplified Chinese, default English. See [Data text usage](data-text-chinese.md).

## Optional Data static frame

One independently optional resource, `assets/data-frame-v1/data-frame-v1.hda`,
is copied to the same relative path in the runtime. Its 4,096,128 bytes contain
a fixed 128-byte DFM1 header and a full 1280x800 straight-RGBA payload. Both
launchers pass the absolute package-relative `--data-frame-assets` directory.
Missing or rejected art preserves the native Data background independently of
valid optional Chinese text/font resources. The static-frame resource upgrades
the metal background and oval surround only; the separate source-authenticated
all18-face compositor is described in [Data portrait HD](data-portrait-hd.md).

The retained source-v3 PNG is 701,041 bytes and remains unchanged. The DFM1
exporter reuses accepted PMF1 samples only where exact original Data writes
leave PIC1 visible. Only exported candidate alpha outside an explicitly reviewed
two-logical-cell Chebyshev source-support bound is clipped; this rule is scoped
to DFM1, and PSP1 retains its separate one-cell bound. No existing art pack,
previous runtime directory, or ZIP is regenerated by this manifest update.

Only the HDA and its two provenance/license-status notices enter the runtime
allowlist. Artwork PNGs, prompts/JSON, exact source-layout mask, authoring scripts,
native game data, portrait PNGs, and font sources are excluded. The notices do
not assert a new redistribution grant for original game artwork. See the
[Data frame contract](data-frame-metal.md) and the retained license-status file.
