# Verified runtime content catalog

The optional packaging audit groups **entire verified files** by SHA256 and byte
length. HDA headers, anchors and pixel payloads all participate. Equal images
with different headers are not the same content. This identity does not confer
any rendering role, source, lifetime or resource-failure authority.

```sh
python3 scripts/package_runtime.py --content-catalog /outside/repository/catalog.json
python3 scripts/package_runtime.py --check-content-catalog /outside/repository/catalog.json
```

These flags use the same manifest, source roots, source map, optional executable
and platform options as normal packaging. An incomplete or mismatched selection
cannot produce or pass a catalog. Snapshot checks compare schema, logical paths,
source identities, groups, all whole-file fingerprints and summary totals.
The snapshot never supplies the package file selection or authorizes new paths.

Export is deterministic across source-root locations and manifest row order.
It omits resolved absolute source paths, timestamps and local source-map values.
The output must be a new external file, cannot overlap another requested
input/output, and is never overwritten. Checked snapshots must be regular files
without symlink components, at most 16 MiB, and cannot contain duplicate JSON
keys. JSON whitespace/key order are immaterial, but numeric types and all values
must match the deterministic projection.

For a guarded build, combine `--check-content-catalog` with the ordinary
`--build --output /new/runtime` options. Any drift is rejected before runtime
output creation. Catalog export occurs only after a successful preflight/build.
A snapshot is a local audit artifact, not a runtime file or installation format.

## Storage remains unchanged

All existing logical paths remain separate ordinary files. There are no aliases,
symlinks, hardlinks, deletions, changed loader paths, or shared failure domains.
Default preflight reports, package metadata, payload bytes and archive entries
are unchanged. The catalog reports `duplicate_bytes` as potential repeated
uncompressed bytes and always reports `bytes_saved_by_this_tool: 0`.

At the accepted Pulse-art revision `1fcdc947`, the asset-only Linux selection
contains 1,006 logical paths and 885 unique whole-file contents: 121 duplicate
pairs, totaling 12,695,988 repeated bytes. This is **not** actual reclaimed disk
space, guaranteed ZIP savings, or permission to remove any file. Adding an
explicit executable changes the selection and therefore the catalog.

Tests: `python3 tests/test_runtime_content_catalog.py` and
`python3 tests/test_runtime_packaging.py`. Existing rendering and source bindings
are not rewritten by this tooling-only change.
