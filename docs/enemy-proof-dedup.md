# Single-proof enemy identity validation deduplication

Baseline: `5109ebbd3f8a5c58075d6358e82e2e4459ac5460` (P09).

Only the adjacent generation/live pair in `enemy_reuse_proof` is combined.
`enemy_reuse_identity_live_generation` freshly validates generation, emitter
bank, record/weapon pins and actor/shot lifetime on every call. It requires a
nonzero generation equal to the expected value before evaluating the unchanged
live fields. The expected value is never a trusted validation token. Public
`enemy_reuse_identity_generation` and `enemy_reuse_identity_live` still perform
complete independent validation. Disabled builds conservatively return false.

The private live-fields helper has only two callers, both immediately following
successful fresh generation validation. The traversed identity helpers read
state/bytes and local temporaries without callbacks, writes or reentry. This
relies on the existing single-threaded simulation/render ownership, not a new
concurrent mutation guarantee. No memo or result survives a call.

Witness consumption, before/after-animation checks, post-draw generation,
allocation/retirement, source/resource families, owner transfers, finish and
Present checks remain separate. NEWSHF, assets, demo gates and gameplay are
unchanged. No proof-local bank memo, across-shot sharing, cross-proof/frame/draw
cache or release-performance claim is included.

## Reproduce the bounded evidence

The diagnostic driver snapshots the exact baseline from Git and the candidate,
instruments only temporary copies at actual hash execution sites, and reuses
the existing native P09 input/compilation driver:

```sh
python tests/enemy_proof_dedup_diagnostics.py \
  --original-data /verified/tyrian2000 --sysroot /sdl/sysroot \
  --base-build /verified/native-build --assets /verified/p09-assets \
  --out /diagnostic-output
python -m unittest discover -s tests -p 'test_enemy_proof_dedup_*.py' -v
```

Counters reset immediately before a direct successful proof after natural
fixture firing/drawing: record133 has one shot; record129 has three sibling
shots (244,227,227). Spawn, animation, admission, post-draw and Present costs
are excluded from this particular counter region. Repeated proof and independent
public calls are measured separately; failure counters include the actual
short-circuit prefix. Native inputs are pinned and passed on stdin rather than
persisted. These are controlled native harnesses, not original-event gameplay
acceptance or FPS measurements.

Mutation tests cover emitter-bank in-place changes between proofs, before a
next draw, at finish and before Present. A pure failed proof is observational;
full revocation is verified through the renderer boundary. Restore cannot
resurrect rejected HD output. After draw rejection followed by restore, existing
renderer behavior may queue a wholly classic upscale (`ready` true), so the test
checks every queued output pixel against the classic oracle and requires both HD
cache flags false rather than incorrectly requiring no classic output. If a failed
begin-draw retires the shot, finish stays unready; stale backing pixels are not
a queued frame and Present must still reject the output.

Exact newest-first inverse bindings preserve every older ledger and reject
whole or partially reverted source mutations. Source inventory remains 263;
runtime inventory remains 1025 and only its current-production binding row
changes. No asset bytes or destinations change.

## Measured hash work (one successful proof)

| Domain | One shot: old → new calls / bytes | Three siblings: old → new calls / bytes |
|---|---|---|
| Emitter bank | 2 / 88,158 → 1 / 44,079 | 6 / 264,474 → 3 / 132,237 |
| Enemy record | 2 / 154 → 1 / 77 | 6 / 462 → 3 / 231 |
| Weapon record | 2 / 160 → 1 / 80 | 6 / 480 → 3 / 240 |
| Shot bank | 1 / 32,060 (unchanged) | 1 / 32,060 (unchanged) |
| RGBA | 3 / 129,024 (unchanged) | 3 / 129,024 (unchanged) |
| Palette | 1 / 768 (unchanged) | 1 / 768 (unchanged) |

Both builds execute one proof and respectively one/three used-slot visits.
Repeating the proof reproduces the same complete hash work, not a cache hit.
Independent generation and live calls each still scan the 44,079-byte emitter
bank plus 77-byte record and 80-byte weapon, on every invocation. Mutated-bank
proofs stop after the first actual emitter hash in both builds.

## Limits

The inherited original-event HD acceptance gap remains: probe startup runs in
demo mode while this feature deliberately rejects demo rendering. This change
does not broaden that gate. Windows, GPU/fullscreen, full-game visual acceptance,
release timing and FPS are not tested or claimed. See the accompanying bounded
validation receipt for actual counts and regression outcomes.
