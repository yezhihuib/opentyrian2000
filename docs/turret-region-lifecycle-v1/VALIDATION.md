# Validation

Baseline: `884b9acc5e015cd964a6afe3cc7c4e95cfd2c485`.

## Focused lifecycle units

Both historical and fixed production function bodies were exercised with
AddressSanitizer and UndefinedBehaviorSanitizer at densities 2, 4 and 8:

- Historical source with explicit stale-sibling expectations: PASS, 7,418,524
  checks. All 14 incomplete redraw subsets restore the stale 48×56 rectangle
  and remove a separately registered live 4×4 HD object.
- Historical source with normal fixed expectations: expected failure at the
  first partial-redraw rectangle assertion; executable exit 3. This confirms
  the regression rejects the original defect.
- Candidate source with normal fixed expectations: PASS, 2,592,388 checks
  in each of an optimized and an ASan/UBSan build.
  All 14 incomplete subsets restore the touched 24×28 rectangle, preserve the
  unrelated live object and other nonoverlapping redrawn members, and restore
  exactly 672 HD logical blocks.
- Full-live and all-four-redrawn controls retain the complete 48×56 closure
  and 2,688 restored HD blocks. All-dead controls remain inert. All 15 nonempty
  live-state masks, four anchors, reversed redraw registration, dead duplicate
  records, wrong bank/style/index/adjacency and known-blend-off are covered.
- Indexed and RGBA row padding stays untouched. Restored rectangles are checked
  against the current indexed palette color and ownership/provenance clearing.

The fixture uses real extracted production bodies for registration, drawing,
suppressed original-write callbacks, command-end and fallback. Font/material
features are stubbed out, synthetic opaque indexed writes replace an original
RLE decoder, and no engine main is launched.

## Production scope

PASS: exact one-predicate inverse across all 153 production files, with all
6,722 tracked asset bytes and modes unchanged. Six negative scope controls
reject removal of the live predicate, changed turret identity/overlap, broadened
Plasma admission, indexed blend arithmetic and gameplay-source changes.

The existing combined and vertical Plasma source inverses also pass after the
explicit independent live-predicate projection: all 153 production files and
6,722 assets checked; all seven Plasma negative scope mutations rejected.

## Existing Plasma units

The full existing original-art Plasma suite also passes in optimized and
ASan/UBSan builds: 64,367,833 checks, 10,046 raw draws and 8,888,387 pixel
callbacks per build. Original indexed writes and full RGBA/ownership oracles
remain exact across the existing vertical clipping, palette, ownership, order
and source-guard matrices. The suite includes both normal and Christmas source
records; no game process is launched.

## Builds

The full optimized Linux engine compiled and linked successfully in an isolated
copy: 72 translation units, C99, `-O2 -pedantic -Wall -Wextra -Werror`, with the
existing warning suppressions `-Wno-misleading-indentation`,
`-Wno-format-truncation`, and `-Wno-missing-field-initializers`.

Renderer-disabled `sprite.c` and `render_mirror.c` also compile successfully with
those strict flags and `-DRENDER_MIRROR_DISABLED`. This is a two-unit disabled
renderer check, not a full classic-engine runtime acceptance.

## Qualification

This batch has no new art, original-data edits or game launches. The demonstrated
defect and fix are same-frame synthetic ledger lifecycle behavior. A natural
ordinary-game occurrence, Windows runtime/device behavior, GPU/fullscreen and
performance improvement have not been established.
