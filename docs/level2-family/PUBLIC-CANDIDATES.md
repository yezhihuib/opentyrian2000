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
