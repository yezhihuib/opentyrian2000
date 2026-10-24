# Bounded CURRENT Guided native validation

`current_guided_native_validation.py` accepts the existing production-object
native driver's required `--original-data`, `--sysroot`, `--base-build`,
`--assets`, and `--out` arguments, plus optional `--source-root` for an isolated
real authoring candidate. Use `--current-sonic-art` with current packs.

The adapter checks the exact SHA-256 of the reused driver before applying a
finite set of textual adaptations. It does not edit that driver or the frozen
`prototype/fixtures/test-guided-bomb-family.py` source-scope oracle. Current
Guided inputs must pass the production compatibility loader and be reproduced
from all four selected masters; only the P04 20/21 expected transport hashes
are replaced. Other families keep their existing authentication.

The C test links actual renderer/entity/sprite/identity/shots/game code and
loads the real original sprite bank privately. It runs the unchanged P09/P05
matrix, then the existing P04 matrix, followed by four Guided player identities:
ordinary and shadow wrappers, independent per-channel RGB oracle, original
INDEX8 equality, player-state/RNG stability, later indexed-write ownership,
cold-load missing/bad-magic/wrong-header/truncated-file fallback, unmapped 22,
and byte equality between player 20/21 and enemy role 146 loads. No player
payload-hash restriction is introduced: an authorized edited master remains a
valid player transport. Enemy payload corruption is rejected by the existing
P04 resource failure matrix.

Each independent player scenario explicitly clears only cache slots 326–329
before beginning. This is test setup representing a cold process, **not** a
claim that changing asset paths reloads the process-lifetime player cache.
Production functions and original indexed blits are not stubbed. Existing
native extraction includes exact projectile/explosion loops and deliberately
controlled fire scheduling; it is not natural campaign, Windows, or GPU QA.

Real edited-20 evidence must be made in a separate source copy using the
actual `build_current_guided.py stage`, `apply`, and `check` pipeline. The
fixture changes red by `(red+37)%256`, preserving green/blue/alpha, only for
master 20. Check that 19/171/21 transports remain byte-identical. It is a
synthetic compatibility fixture, not approval of new artwork.

The driver records compile logs, native stdout/stderr, exact source and
harness hashes, baseline object hashes, source stability across the run,
sanitisers, and original-data non-persistence. Original game data is read
only from the explicitly supplied private directory and transferred on stdin;
do not add it to source control. Run artifacts belong outside the repository.
