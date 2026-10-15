# Live-only turret fallback cohorts

The display ledger's four-piece turret grouping now requires a live matching
record for every member: newsh2 IDs 77, 79, 115 and 117 at their existing exact
24-pixel / 28-pixel offsets. The only production edit is the sibling predicate
in `complete_turret_group()`: `regions[j].live&&`.

## Reproduced lifecycle defect

A synthetic same-frame sequence exercises the actual production registration,
draw, original-write callback, command-end and restoration functions:

1. Draw all four members at (40,30), (64,30), (40,58) and (64,58).
2. A local palette-blend fallback restores their complete 48×56 group and marks
   its four ledger entries dead.
3. Draw a separate 4×4 HD object in one missing member's old area, then redraw
   only a subset of the turret members. Registration appends new live entries;
   it deliberately retains the old dead entries.
4. A later blend touches one of those new members.

Before the fix, dead siblings complete the old group. With one member redrawn,
the later fallback restores 48×56 and removes 688 HD logical blocks: the 672
blocks of the live member plus the unrelated object's 16 blocks. After the fix,
the fallback restores just the touched 24×28 live member, removes 672 blocks,
and preserves the unrelated HD object. The same isolation holds for all 14
nonempty incomplete redraw subsets and all four possible anchor positions.

All four live members still restore as the same 48×56 group. Fully redrawing a
previously restored group works even with retained dead duplicates and reversed
registration order. All-dead records remain inert. The known-blend option,
strict overlap rule, wrong-bank/style/identity/adjacency rejection, dead-record
counting and per-frame reset are unchanged.

## Historical contract and limits

Grouping and the promise that previously restored records are inert were
introduced together in commit `082f591ccc5e88f2f7d22f920c369a0ded381bcc`.
The existing region-budget test explicitly covers restore followed by redraw
at the same position, with a new live entry and the old dead entry still counted
(`prototype/fixtures/test-hd-region-budget.c`).

This is a supported ledger lifecycle regression. No natural ordinary-game
occurrence of this exact sequence has been established. An actor's enemy
quadrants are consecutive NORMAL calls, enemy pools are processed once per
tick, and the ledger resets each frame. A natural occurrence would need a
later distinct matching draw in the same frame. The test does not demonstrate
a cross-frame problem or establish a visible gameplay frequency.

## Checks

From the repository root, use fresh external output paths:

```sh
python3 prototype/test-turret-region-lifecycle.py \
  --sanitize --out /tmp/turret-lifecycle-units
python3 prototype/test-turret-region-scope.py \
  --out /tmp/turret-lifecycle-scope.json
```

The first test extracts the production functions into a bounded C99 harness.
It needs no SDL, original game data, generated artwork or engine build. It
uses padded indexed/RGBA pitches and tests native densities 2, 4 and 8. The
optional `--source` and `--expect-stale` arguments support an explicit diagnostic
run of the old implementation; normal fixed expectations reject that old source.
Synthetic assets are opaque and the harness supplies indexed writes, so this
does not claim original RLE decoding or natural engine execution coverage.

The second test reverses exactly the added sibling-live predicate and requires
all 153 production source files to match checkpoint
`884b9acc5e015cd964a6afe3cc7c4e95cfd2c485` byte-for-byte. It also verifies all
6,722 tracked assets' bytes and executable modes, and rejects six deliberate
source mutations. Gameplay, original indexed blitters, Plasma admission/blend
handling, cloud compatibility/fallback and every other production byte remain
unchanged.

The existing Plasma unit and scope tests explicitly project out only this
independent predicate for their historical source-preservation guards. Their
compiled tests still use the actual current helper. Historical reports and
older frozen fixture sources are retained unchanged.

See [validation](VALIDATION.md) for results and remaining acceptance limits.
