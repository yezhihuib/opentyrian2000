# SHOP: published boundaries, not missing private Git prerequisites

The five original tests are preserved byte-for-byte as `*.historical.txt`.
Their SHA-256 values, fixture hashes, and the product parent Git blob are pinned
in `provenance.json`; the helper pins that receipt itself. These are historical
specifications, not disabled discovery modules. All five replacement modules
contain counted, live unittest checks, plus separate mutation controls. Each also
retains a counted `test_original_private_tree_proof`: it reports
`HISTORICAL_PROOF_UNAVAILABLE` as a failure until its exact private commit is
restored, then executes the byte-exact original script with its original
`__file__`/ROOT. Thus passing current contracts does not turn missing historical
proofs into an all-green suite.

## What can and cannot be proved

The old private commits `8218c1f`, `ac64ee7d`, `d97783b0`, `1685561b`, and
`8ffe93fa` are not available in a public clean clone. We do **not** manufacture
these commits, claim their complete trees were recovered, or equate their
opaque identities with a later published commit. The old requirement that the
entire *current* tree remain an intermediate SHOP-only tree was also invalid
once subsequently accepted features were published.

Instead, the following independent public stages anchor enduring contracts:

| Contract | Published stage | Retained original evidence |
| --- | --- | --- |
| Frame | `eba21695b298` | PMF1 constants, provenance, exact exporter output, owner list, current replay/mask guards and Windows inventory |
| Front | `fedc541cc6b6` | Original accepted pregame SHA-256 `50587fdd...`; all original resource/header pins |
| Generator | `1037b40b9a08` | Original accepted pregame SHA-256 `0c8aa83c...`; original resource/header/script pins |
| Menu font | `fedc541cc6b6` | All original menu resource/header pins; original menu accepted SHA equals front's original-parent SHA; front's independently published source matches its original accepted SHA; bounded SMR1/menu-run lease guards |
| Product font | `311de82e` → `eba21695b298` | Original annotation-only rule, exact 22 observer-call counts, no removed menu lines or state-changing expressions, current bounded tail/replay guards |

**Menu limitation:** the menu-only intermediate source bytes with SHA-256
`e6f5cfbe...` (and earlier Talon source `a9ddc4e1...`) have not been recovered.
The metadata chain is evidence of the recorded transition, **not proof those
intermediate bytes were reproduced**. Its live contract is checked at the
next independently published, originally pinned front stage; no claim of a
menu-only private-tree proof is made. Likewise the product public parent is
identified by its own commit/blob/hash, not relabelled as `8ffe93fa`.

## Current proof is mandatory

`current-inventory.json` enumerates every source and asset path and its exact
SHA-256 at public commit `775b6b77163723c6cae727bafce1d53746a5bd60`, plus
explicit build/exporter/original-pin files. It was read from that Git commit,
not from an unchecked working tree. Added, removed, changed, or symlinked
resources fail. This captures the subsequent accepted publication, not a
wildcard exemption for future changes.

Each stage JSON records the **full** original published blob ID and SHA-256,
current published SHA-256, and finite non-overlapping inverse replacements.
The helper verifies the full live current hash **before** reversing any span,
then checks every span, the reconstructed full SHA-256, and its Git blob ID.
It never substitutes an old fixture for unverified current code. All code
introduced after the old stage is therefore guarded too. Tests mutate each
inverse span at start/middle/end, preserved bytes, append new logic, truncate
source and alter replay guards; these must reject before projection.

The original assets and original JSON source-delta pins are unchanged. The
current front and generator source projections still match their original
accepted hashes rather than newly substituted expectations. Generator's
later test runner is projected to its original pinned published bytes.

The original `SF_EVENTS=40000` assertion is retained on the reconstructed
frame/product stage. The live published Pulse path uses `SF_EVENTS=65536`;
its exact value, `sf.event_count==SF_EVENTS` rejection, and 16 MiB cap are
checked separately. This is an explicit accepted pool expansion, not a
relaxed bound or deletion of the historical check.

## Updating

A future production change intentionally fails this frozen boundary. Review
its exact public commit, finite source changes, resource identity/format and
behavioral tests before extending the accepted-current inventory and inverse
spans. Never regenerate against an unreviewed working tree to make a failure
go away. Preserve original stage hashes, original source-delta pins, and
negative controls. No Git history, network, screenshots, game data banks or
private object stores are needed to execute these tests in a clean clone.

Run from the repository root:

```
PYTHONPATH=tests python -m unittest test_shop_frame_integration \
  test_shop_front_boundary test_shop_generator_boundary \
  test_shop_menu_font_boundary test_shop_product_font_integration \
  test_shop_published_boundaries
```

Historical readiness (nonzero status when any exact parent is unavailable):

```
python tests/shop_published_boundary.py --readiness
python tests/shop_published_boundary.py --historical menu_font_boundary
```

At repair time all five private parent objects above are unavailable. Targeted
discovery therefore reports **12 current-contract PASS, 5 historical-proof
FAIL (unavailable)**, not five fully recovered historical proofs. Once parents
are restored, original tree comparisons may still expose the historically
stale whole-current-tree assumptions; replay deliberately does not mask them.
