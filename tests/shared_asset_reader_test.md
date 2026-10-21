# Shared HDR1 reader differential gate

Run:

```sh
python3 tests/shared_asset_reader_test.py --out /tmp/shared-reader-review
```

The test compiles the actual shared header and fd adapter with ASan and UBSan.
Legacy reader IO fragments are extracted from immutable ancestor
`76757030842b19397353152c6ea326f95ef50c33` and compiled alongside them. It
compares acceptance, exact returned payload hashes, and IO/malloc call traces.
The original trusted registry/caller preconditions remain in production.

Coverage includes every current registered global asset and all eight SHOP
ship/Pulse/Vulcan resources, including Pulse's signed -1 anchor. Injected faults
include each header byte mutation, truncated header and payload, trailing bytes,
short/chunked/failed reads, open/stat/allocation/close failures, nonregular file
and incorrect file size. Global stdio EOF and ignored close behavior are preserved;
SHOP fd regular-file/size checks are retained, and only ship rejects close failure.

The reference header and payload code is extracted, not rewritten to use the new
helpers. The common parser grants no role, cache lease or rendering permission.
Existing native/composer tests separately establish role and frame behavior.

Limits: mock IO tests preserve API semantics, not OS permission behavior; caller
metadata is a checked trusted registry descriptor, not an arbitrary untrusted
pointer. LSan is disabled because this execution environment runs under ptrace;
ASan and UBSan remain enabled. The output receipt records the exact source hashes,
baseline hashes, compile command and sanitizer output. No original game data is
read or persisted by this test.
