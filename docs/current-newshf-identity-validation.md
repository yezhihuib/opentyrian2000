# Current NEWSHF identity validation

This is a test-only adapter for the public `4f7e60b` source. It does not alter
production code, gameplay eligibility, artwork, the old identity driver, or the
old native C harness.

## Why a current adapter is needed

The frozen `tests/newshf_identity_validation.py` requires the identity frame hook
to be the first statement of `render_mirror_begin`. The current renderer first
rejects a requested but inactive enemy observation session, resets HUD state and
returns. Accepted normal/observation entries then invoke the identity frame hook
before the global NEWSHF tick hook. The frozen driver's old preflight consequently
fails before compilation. Its result remains a historical preflight failure, not
a passed test.

The new adapter pins both historical driver and C harness SHA256 values and the
entire current extracted `render_mirror_begin` function. It replaces only the
obsolete first-statement assertion with an explicit exact prefix, single-hook and
ordering check. A source change fails closed and requires a new reviewed contract;
the adapter does not discover a newer baseline or silently strip arbitrary code.
The only other driver substitution selects the explicit source root.

## Commands

From the repository root, with the separately supplied original game data:

```sh
python3 tests/current_newshf_identity_validation.py --original-data /path/to/original-data --out /path/to/identity-results
python3 tests/current_newshf_identity_validation.py --original-data /path/to/original-data --out /path/to/identity-negative-results --negative-control
PYTHONPATH=tests:scripts python3 -m unittest discover -s tests -p test_current_newshf_identity_validation.py -v
```

An optional `--source-root /path/to/checkout` selects another checkout containing
the same pinned driver/harness and current entry function. Original game bytes
are verified and passed to the native child on stdin; they are not copied into
this deliverable. C compiler support for ASan and UBSan is required. The original
harness intentionally disables LeakSanitizer in the container; no claim of leak
checking is made.

## Verified coverage and boundaries

- The unchanged native identity harness passed 24,594 assertions over nine poses,
  using the production identity include, structs, decoder and `JE_makeEnemy`,
  with bounded SDL/RNG shims. It checks identity lifetime, bank/record/palette
  changes, actor/indexed-pixel preservation and allocation equivalence.
- The unchanged feature-off checks compile and execute default, flag-zero and
  mirror-disabled modes. The native identity run uses ASan and UBSan.
- Removing the original whole-bank hash guard in a temporary include triggers
  the original expected mutation assertion. The driver classifies that specific
  failure as a successful sensitivity control, not a passing normal execution.
- Six Python tests include a separate native **extracted entry-prefix** matrix:
  default/flag-zero/flag-one builds, each with all four requested/active states.
  This verifies accepted entries execute frame then next hook, while the enabled
  requested-but-inactive path resets and returns without invoking either hook.
- Four isolated native mutants (missing frame hook, frame after next hook, lost
  rejection return, frame before rejection) trigger specific lifecycle check
  failures. Static contract tests also reject altered/duplicated hook or changed
  rejection condition and accept restoration in the same process.

The prefix harness uses stub observation predicates and counters: it does **not**
validate full session activation, downstream rendering or a complete frame. The
identity harness is not HD compositor proof, natural-level playback, player
shadow, Windows execution, physical GPU validation or full-game acceptance.
Previously published compositor results are separate evidence, not rerun here.
