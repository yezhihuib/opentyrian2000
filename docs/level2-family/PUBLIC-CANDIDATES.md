# One public-only experimental combination

To check the completed public candidates together without launching:

```sh
python scripts/launch_level2_family.py \
  --data /path/to/original-game-data \
  --binary /path/to/opentyrian2000-family \
  --hd --public-candidates --check-only
```

Both explicit `--hd` and `--public-candidates` are required. Ordinary invocation
remains classic; `--hd` alone retains its existing baseline. The plan does not
create a profile, change the current directory, send input or start a game.
Existing binary availability and asset hashes are checked, but binary provenance
and original game-data validity are not certified by this command.

The preset includes the eight already-integrated public expansions: later
lamps, later embers, later triples, Fork284, normal Turret273, normal Linked338,
linked props287/288 and late282/285. It also includes the bounded normal270 body
candidate described in [its scope note](NORMAL270-CANDIDATE.md). Existing eight
fine-grained flags remain compatible for narrowing/debugging. There is no ninth
individual270 command-line flag.

Private redvent is incompatible with the public preset. Missing283 artwork,
compound309–312, tall structures, level1-only columns276, projectile art and
unimplemented enemy/damage states are not enabled. Inherited renderer-control
environment variables are cleaned before constructing the selected configuration.
Every selected asset must pass its existing identity check; missing/corrupt
assets stop plan creation rather than silently reducing the combination.

Actual launching is a separate user-controlled action using `--launch`, supported
by this launcher only on POSIX. Windows profile isolation is not implemented.
Do not use this preset to bypass display permissions or permission failures.
No game was launched during this change. A successful check-only result is not
actual scene/gameplay qualification. Default remains off because combined
visual overlap, frame timing and complete playthrough are still unverified.

## Offline combination checks

`tests/test_public_candidates.py` verifies the explicit parent gate, default
behavior, public-only boundary, all selected family settings, environment cleanup,
corrupt-asset rejection and absence of planner side effects.
`scripts/check_family_writer_interleave.py` compiles a small no-SDL harness using
the real central writer dispatch and real sparse-retirement functions. It tests
ordered family interleaving and generic normal/blend/shadow handling. Ownership
acquisition is modeled by narrow test adapters, not real enemy gameplay; each
family's native-pixel/alpha routines have separate tests.

## Explicit lamp boundary candidates

The standard launcher can now select the existing boundary adapters independently:

```sh
python scripts/launch_level2_family.py --data /path/to/game-data \
  --binary /path/to/opentyrian2000-family --hd --lamp-top-clip --check-only
```

Add `--lamp-bottom-clip` only when intentionally testing the unqualified bottom
candidate. Both flags may be combined; neither enables the parent HD family or
additional later origins. They reuse the manifest-verified lamp materials.
`--public-candidates` alone does not enable either boundary flag. Inherited
boundary variables are discarded, so a prior shell session cannot enable them.
The printed plan records each selection separately. Use a binary built from
`c8622ce` or later; the planner cannot certify executable provenance.

These flags expose existing renderer coverage, not newly qualified artwork.
Top has one bounded final-visible sample, not full gameplay acceptance. Bottom
has offline contract/build evidence only. No game starts without `--launch`;
POSIX launch support and Windows limitations above remain unchanged.

## Later longface groups

The public preset additionally requests `LONGFACE573_LATER230240_ENABLE=1`,
which reuses the same eight verified longface materials for two narrowly pinned
later groups. `--hd` alone still admits only the first group; inherited longface
controls are discarded. No new CLI flag or asset is added. See the
[longface candidate and evidence limits](LONGFACE573-DAMAGED-CANDIDATE.md).

## Random smallrocks

The preset also requests the [smallrocks candidate](SMALLROCKS-CANDIDATE.md),
using four separately size/SHA-256-verified existing public images for exact
witnessed random births317–324. Plain `--hd` keeps this adapter off and inherited
`SMALLROCKS_` variables are cleared. No new CLI option or asset was added.
Its sparse native writes and alpha/ownership contracts have offline evidence;
actual scenes and gameplay remain unverified.

## Six-record random props

The preset selects the [random props candidate](RANDOM-PROPS-CANDIDATE.md) for
records135/136,260/261,263/265 using three separately size/SHA-256-verified
existing images. Plain `--hd` does not enable it and inherited `RANDOM_PROPS_`
controls are removed. Four-block native transactions and alpha/ownership have
offline checks; actual scenes remain unverified. Sibling137/262/264 and base123
are not admitted. No new CLI option or material was added.

## Normal player ship

The preset selects a [five-pose normal player-ship candidate](PLAYER-SHIP-NORMAL-CANDIDATE.md)
using five separately size/SHA-256-verified Talon images. Plain `--hd` keeps it
off; inherited `PLAYER_SHIP_FAMILY_` controls are cleared. Invulnerable poses
and blend/shadow body calls are not admitted by this candidate. No new CLI
option or material is added; actual scenes and gameplay remain unverified.

The public preset also selects the bounded [tank194 initial encounter](TANK194-CANDIDATE.md):
eleven births6/25/26/36/37/76/77/78/89/90/91, eight existing poses, whole-body-only, and a strict stop
before event149. It excludes simultaneous global asset rendering. No later tank
births or real-scene acceptance are implied.
