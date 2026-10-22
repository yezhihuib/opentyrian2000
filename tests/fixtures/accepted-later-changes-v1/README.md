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
`current-source-inventory.json` also requires the exact current `.c`, `.h` and
`.inc` path/hash map under `src`; build outputs are not source inputs.

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
and asset inventories must match the accepted publication. Existing runtime
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
