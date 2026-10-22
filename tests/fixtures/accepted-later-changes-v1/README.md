# Accepted later changes, not rebased historical expectations

These immutable test-only ledgers describe already published changes between
named historical public stages and `775b6b77163723c6cae727bafce1d53746a5bd60`.
The helper pins the ledger bytes. The older test SHA256 values, inventory counts
and digests are unchanged. Tests do not need a private Git object database.

| Ledger | Historical stage | Subsequent original oracle |
|---|---|---|
| data-source | `56d03bdd` | Existing four cursor inverses, then original DATA frame/portrait source hashes |
| rear-p1-source | `76689b78` | Original observer inverses and all 156 original source hashes |
| storm-source | `22661ddf` | Original STORM observer inverses and all 153 original source hashes |
| p9-assets | `82c0d3ec` | Original P9/P7/P5/P4 exact inverses and original asset inventory digests |

Each source entry includes its historical commit, old/current SHA256 and exact
line-oriented inverse hunks. These are derived from `git show <stage>:<path>`
and `git show 775b6b77:<path>`, not from a guessed historical reconstruction.
The inverse requires the **whole current blob** before applying any hunk and
checks the whole historical result afterwards. The DATA cursor and original
feature inverse operations remain separate and retain their original hashes.
`current-source-inventory.json` records two distinct layers: the 249 historical
`.c`, `.h` and `.inc` paths/hashes from `775b6b77`, and the one generated sidekick
build/package header introduced by `0ded81a9`. The 250-entry map is not a claim
that the new header existed at 775. Its initial hash is retained as provenance;
current acceptance derives that one header from the proof described below.
All 249 historical source hashes and all 250 paths remain exact.

P9's finite ledger records every changed, added and retired asset path with its
old/current SHA256 and Git mode. It first requires the exact current inventory
digest, then reconstructs the old path/hash map. It does **not** claim retired
files are still physically present. No wildcard path or directory exemption is
used. Unchanged historical content remains checked by each original inventory
digest. Catalog inverse operations require the complete current canonical hash;
the exact historical catalog fixture restores member order for the original
byte-level catalog SHA256 checks. Already historical P9/no-P9 catalogs are
accepted only at their exact historical canonical digests.

## Enduring current checks

Historical proof is not a replacement for current proof. Current whole-source
and asset inventories must satisfy their exact current checks. Existing runtime
role, pixel, payload, transform, reconstruction, and corruption checks continue
to run. The old generic-function interval check now ends at the actual matching
function brace, not at an unrelated later function. The accepted global-family
head/shadow branch and the rear branch are separately required to perform one
indexed write and return; textual call counts no longer incorrectly equate
mutually exclusive branches with double execution. STORM still precedes the
now-expanded shared-family early guard.

`test_accepted_later_changes.py` deliberately changes bytes within inverse
hunks, outside hunks, reverts accepted source, changes catalogs, adds/deletes
source or asset paths, reverts/changes asset hashes and changes asset modes.
All must fail. Eight script oracles have explicit one-case subprocess discovery
adapters, preserving failure isolation and executing their actual bodies; none
is merely imported and counted as zero tests.

Future legitimate changes require a reviewed ledger update with provenance and
negative controls, not replacing historical expected hashes or widening an
exception. Fixtures contain only this repository's source/catalog metadata and
hashes, no proprietary original game banks.

## Six-body current extension

The asset ledger keeps its original 3,259 edits and whole-inventory digest
`3f819ca1f9ac2b9ef4de53cfe4fb948bc0d347bd0f1f7b539dbb7bfd2915ae34`.
Its separately named `verified_current_outputs` contains exactly seven paths:
the sidekick selection JSON and six current compatibility HDA files. The listed
initial SHA256 values and review commit `0ded81a9` are provenance, not a permanent
pin on editable artwork. No prefix or arbitrary new hash is accepted.

Before removing those seven paths from the historical inventory, the helper
reads the fixed six identities in order, validates each selected PNG hash and
96x112 RGBA geometry, derives each complete HDR1 transport from those pixels,
and requires exact HDA, mapping, selection version and generated header bytes.
It verifies all 252 production source paths/hashes (the 250 code/header entries
plus the two explicitly pinned dr_mp3 license/provenance files), and the six corresponding
runtime rows, unique 1,006 destinations and binding row/digest. This is Python
build/package consistency only; production C does not include the new header.
The source inventory permits only that header's freshly derived value. Hand
edits, stale generated outputs, missing paths and unknown paths still fail.

Historical PNGs remain evidence. A future candidate can be saved separately
inside the repository, selected explicitly and rebuilt through the existing
CLI. The positive test uses a test-owned candidate outside `assets`, preserving
all historical PNG bytes; no production paths are moved. A new file under
`assets`, or an in-place edit to an old PNG, needs its own reviewed historical
ledger extension and is not silently admitted by this seven-path projection.
The test runs actual CLI stage/apply/check, verifies both inventory projections
after regeneration, restores the isolated fixture and verifies both again.

Asset modes come from the current Git index (`ls-files --stage -z`), not Windows
execute-bit guesses. POSIX also requires working-file modes to agree. Stage-1,
duplicate, symlink/submodule modes and untracked asset files are rejected.
Content hashes always come from actual file bytes. The mode inventory is read
fresh, needs no historical Git objects, does not change filesystem permissions
and does not cache an acceptance verdict. Tests separately cover the eight
existing executable scripts, index-mode changes, additions/deletions, arbitrary
content hashes, ledger corruption and independent current-chain tampering.

## NEWSH2 base267 current extension

Exactly two additional current asset paths (selection and canonical HDA) are
accepted only after deriving fixed HDA1010267 from its selected 192x224 RGBA8
PNG and checking mapping and its unique current runtime row. Together with the
six-body chain this admits exactly nine generated asset paths. The craft267
README change has a separately pinned complete-blob and one-hunk inverse before
the unchanged original inventory digest and all 3,259 historical asset edits.
No craft267 C header or source-inventory exception is added; source scope stays
252. Candidate PNGs under assets still need their own reviewed finite extension.
