# Qualified-family coexistence checkpoint

The combined source at `b7f93d2e7546e3d07853b6b533a5b0b8992e27d6` passed
bounded source and runtime parity checks on 2026-10-14. It joins rear-power pickup
534, Data cube 513, and normal player Vulcan heads 67/70 with their smooth-shadow
follow-up. Canonical artwork, original gameplay and independent family checkpoints
remain unchanged. This is a tested local checkpoint; publication is a separate step.

## New runtime evidence

Four separate actual-engine witnesses ran under Linux with SDL dummy/software and
the combined code/resources installed. There were four process starts and no
automatic retries:

- Rear 534: 273 actual logic ticks, 21 new native 2× images.
- Data 513: 795 actual logic ticks, 36 new native 2× images.
- Vulcan P1: 90 ticks, 6 new native 2× images and 6 INDEX8 images.
- Vulcan P7: 90 ticks, 6 new native 2× images and 6 INDEX8 images.

All 69 native 640×400 captures match every decoded RGB and RGBA pixel, including
the HUD, against the retained final independent family candidates. All 12 INDEX8
files, palettes and indices match exactly. There are no masks or pixel exceptions.
State and trace comparisons also pass: 35, 36, 33 and 33 raw streams respectively,
plus the two Vulcan canonical blend proofs. Only `control.wall_ms` is excluded.
Where historical rear/Data admission streams no longer have raw files, comparisons
use their frozen original SHA-256 and count receipts rather than claiming a new
raw-to-raw comparison.

The retained references are the final rear/Data candidates and final smooth-shadow
P1/P7 candidates. Independent read-only numerical review confirmed all four results
and unchanged frozen inputs. The [machine-readable summary](runtime-summary.json)
pins each result, reference receipt, tested source and review. Earlier per-family
measurements and visual reviews retain their original scope.

## Source and resource coexistence

The source/manifest merge is an exact additive union over `ee2b90c`. Rear uses
slots 507–509, Data uses 510–521, and Vulcan uses 522–523; capacity is 524. Each
default pack contains 532 manifest entries and preserves its six existing extra
HDA files. The 17 added unique HDA resources total 2,666,972 bytes.

Combined extracted-source checks passed for rear/Data, the full unchanged shadow
suite, and the original gameplay units. A separate source-only mixed loading and
fallback suite passed 16 cases and 3,840 routing calls. This does not establish
simultaneous family exposure or overlapping rendering in gameplay.

## Historical receipts and portable metadata

The [rear](../rear534-three-v1/README.md),
[Data](../data513-twelve-v1/README.md),
[Vulcan head](../player-vulcan-two-v1/README.md), and
[smooth-shadow](../player-vulcan-shadow-v1/README.md) receipts remain separate.
Two inherited metadata exports now use portable directory labels: the relocated
Vulcan rebuild receipt and the Vulcan binding-unit compiler arguments. The two
public receipt references that hash the latter are repinned to its portable bytes.
Original and public SHA-256 values, plus the precise changed fields, are recorded
in `historical_evidence.public_metadata_normalization` in the summary. No measured
results, canonical art inventory, source or independent checkpoint were rewritten.

## Limits

These are four separate installed-coexistence witnesses. They do not show all
families exposed together, a cross-family overlap oracle, full-level or campaign
acceptance, Windows/manual play, physical-window/GPU/fullscreen behavior, or
performance. There is no new combined native 4× run or fractional-alpha runtime
oracle. No original game data or raw reference images are included in this report.
