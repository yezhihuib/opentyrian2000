# Portable historical test baselines

These fixtures replace historical object *reads*, not historical assertions.
The provenance labels in existing ledgers remain unchanged. Source projection,
finite inverse, partial inverse, protected-scope inventory and runtime record
checks still compare against the original frozen before-image.

## Supported checkout

Use a full public Git clone. A source ZIP or shallow/partial clone may lack pinned
public blobs or subtrees and fails clearly; the provider never fetches, resolves
HEAD as a replacement, chooses an ancestor, or rebases an expected value. No
private commits or parent graph are needed. The separate current Guided tests
also require their exact runtime prerequisite content tree to be published;
this change does **not** claim that pending prerequisite is already public.

## Frozen data

`tests/fixtures/portable-history-v1` has exactly 32 files / 4,120,570 bytes:
26 deduplicated original preimage blobs (4,040,385 bytes), five complete scope
inventory descriptors (26,907 bytes), and a 53,278-byte manifest. Manifest SHA256:
`2f10a46d70cb5fed377373f22f484b1c27f2a9cb1a969eab765cbf08407c9b02`.

The manifest declares 155 exact preimage queries across eight private baseline
labels. Another 62 distinct needed blobs are already public and are read by
immutable blob ID with size/SHA256/Git-blob-ID verification, not from the working
copy. The ninth label (5109) aliases its exact already-public content tree
`196d7181daa7ee55a99e5056aad59ff6bf44261d`; it is not a nearest-ancestor fallback.
There are no private commit objects, full private history, or original game data
in this fixture. Narrow `-text` attributes preserve every fixture byte under
Windows autocrlf; this is an encoding safeguard, not a Windows execution claim.

Five descriptor inventories reconstruct complete original protected scopes.
Public subtrees are immutable inputs; explicit differences and private ledger
rows are bound by original subtree IDs and an expanded-inventory SHA256. Tree
hashes are recomputed without writing objects. Missing/extra files, symlink
fixture directories, corrupt bytes and unknown query paths fail closed.
A Provider is an immutable manifest snapshot validated at construction (the
module caches one per checkout); it is not a live manifest watcher. Private
preimages and descriptors are read and checked on use, and candidate working
files are freshly inspected on every comparison. Blob storage files are data
containers: original path modes are pinned in the manifest/inventory, not
inferred from the containers' filesystem permission bits.

Candidate differences retain tracked-file mode/content/removal checks and
unignored untracked additions. Git's actual ignore rules exclude incidental
untracked `__pycache__`; ignored *tracked* files still count. There is no broad
suffix exemption. Symlinked candidate parent directories fail closed before any
outside descendant can be read. Git clean filtering is respected for changed tracked text
(including autocrlf), and `core.filemode` follows the repository's Git semantics.

## Scope and verification

The twelve audited entrypoints are current Protron authoring/source projection,
proof dedup binding, controlled probe binding, Protron reuse binding/authoring,
reuse observe binding, compositor guards, 168 V4 selection, normal observer
surface binding, and green/reuse source tests. Two use the shared adapted helper
and require no direct edits. The proof diagnostics helper uses the same immutable
public-tree read. Its old native paired instrumentation is not claimed as run;
a source-only validation can enumerate the pinned baseline `src` tree and check
every byte read independently.

Run the focused new test with:

```
python -m unittest discover -s tests -p test_portable_history_baselines.py -v
```

An optional `PORTABLE_HISTORY_PUBLIC_GIT_DIR` points at a separately verified
public-only object database to prove all eight private commit and root-tree
objects are absent while all 155 queries and five inventories work. This option
never imports objects. Integration validation must copy candidate files, not
checkout a private ancestor into that database. Existing source/runtime negative
assertions remain in their original test modules. The three provenance-only
labels and ten unrelated legacy standalone scripts are deliberately untouched.
