# Separate runtime and development packages

`scripts/package_runtime.py` makes a new,
allowlisted runtime copy outside the source root; it has no network, deletion,
Git, overwrite, or source-move actions. A dry run is the default.

## Current selection and closure

`packaging/runtime-assets-v1.json` pins 665 selected files and 115,250,568 bytes,
excluding an optional executable and generated inventory/status metadata:

- One active manual gameplay pack: all 637 files, 95,176,717 bytes. Its four- and
  eight-density files are retained, including fallback resources. Split
  `ground101` transport parts, forest material and its coupled-original policy,
  plateau cap material, and all seven gameplay HUD sidecars are present.
- Complete startup/title/settings pack: nine files, 17,780,592 bytes. This includes
  all three settings-font atlases shared by settings/load/selector/pregame UI,
  the separate title-menu font, two manufacturer cards, and three title layers.
- All eleven current optional shop HDAs: 2,256,042 bytes, including the locally
  accepted generator. These are flattened into that same startup directory;
  `params.c` connects `--startup-assets` to all six startup/UI font consumers.
- Five license/provenance notices and three launcher/readme files: 37,217 bytes.

This is an explicit snapshot, not a claim of a theoretically minimal asset set.
The complete selected gameplay directory is retained rather than stripping
untested fallback files. The preview/debug default pack copies have identical
contents at the public baseline; only one is included here.

The public baseline is `fedc541cc6b6e93f7748a85e6c40318b6ca9f5a8`.
The generator is a local-only addition from
`55d418de4f914d4694eb7f074458207b1cf6a2d2`; packaging does not publish it.
Source paths, destination paths, sizes, Git-blob SHA1 and available SHA256 are
explicit in the allowlist. The public tree was complete (`truncated=false`), and
all selected local inputs are checked against pinned sizes and content hashes.
The copied inventory records SHA256 for every output resource.

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

## Measured local copy (2026-10-19 UTC)

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
