# Four-ID Pulse upgrade oracle

This is a bounded source/binder/compositor test, not an in-game visual approval.
It compiles unchanged helpers extracted from the supplied `src/render_mirror.c`;
it does not start the game, SDL, a capture, or a renderer-disable build.

## Run

Requirements: Python3, Pillow, a C99 compiler supporting AddressSanitizer and
UndefinedBehaviorSanitizer. No network is used. From the repository root:

```sh
python prototype/fixtures/test-pulse-upgrade.py \
  --source . \
  --art /path/to/rebuilt-pulse-output \
  --assets /path/to/pulse-upgrade-review-pack \
  --baseline-assets /path/to/pinned-b595707-debug-pack \
  --sanitize --mutations --report /path/to/pulse-upgrade-result.json
```

Temporary synthetic files and executable inputs are retained and their path is
reported. The checker never writes source or authored artwork. Leak detection
alone is off because the executor's ptrace sandbox does not support it; address
and undefined-behavior instrumentation remain enabled.

## Frozen inputs and source scope

`pulse-upgrade-contract.json` records the107 source/header hashes from
`b595707d04a90ff0833f8751975d36a398c5606b`, all329 baseline HDA hashes, and the
approved candidate-manifest hash. The candidate pack must have333 HDA files,
with every original file identical and exactly four additions. The complete
PNG, master, HDA header and actual RGBA payload are validated for each addition.

The only permitted renderer differences are capacity321→325 and bank8 TILE
IDs58/60/62/165→slots321–324. Reversing those two changes must recreate the
baseline renderer bytes exactly. ID59 stays slot5, anchor(-1,0); the four new
IDs use(0,0). Every other source file must match baseline except the explicitly
pinned private FIFO readback version of `asset_debug.c`, which is permitted for
private testing only and is not included in the renderer patch.

Exact source comparison also establishes unchanged original indexed blitters,
entity wrapper calls, weapon tables, game state, timing, movement, collision,
RNG, and enemy-shot gate. It does not replace gameplay testing.

## Executed oracle

- Six bank identities × three layouts × IDs0–599, independently expected slots,
  roles, dimensions and anchors; no alias to the four new slots.
- Actual HDA loads and byte-for-byte RGBA; positive old59 and214–217 controls.
- Every header word, invalid magic, short payload, trailing byte, missing all,
  missing each independently, explicit missing/invalid/1x gates,8→4 fallback.
- Exact per-channel independent normal-alpha and shadow math using actual art
  plus synthetic alpha0/1/17/63/127/128/191/254/255, at output2x/4x/8x.
- Original palette-ramp shadow treatment on indexed-owned pixels; authored
  alpha half-darkening on HD-owned pixels; untouched transparent destinations.
- Normal and clipped placement, padded surface pitch, ownership and green-layer
  invalidation, actual entrypoint routing, unchanged59 shadow/green exceptions.
- Bank8 ID83 remains unbound; newsh6 ID83 retains its existing slot180.
- Enemy-shot negative sweep for all banks/IDs and positive actual112/113 controls;
  the Pulse IDs cannot gain an enemy-shot binding.

The finite lookup sweep uses the actual `game_probe_invalid` flag only to
inspect initialized slot metadata without repeatedly reading every old asset.
All load, entrypoint and pixel tests run with valid assets and the real renderer
branches. No production helper is edited for testing. Only the external trace
callback and unsupported-reason recorder are minimal harness shims.

Eleven mutations must fail: undersized capacity, omitted bindings, wrong ID,
wrong bank, wrong layout, wrong slots, changed anchor, expanded enemy gate,
opaque-alpha replacement, wrong shadow alpha, and expanded green-head scope.

Current approved alpha is preserved exactly:58 and62 peak at253,165 at254;
only60 contains fully opaque255 texels. The test does not impose a false opaque
core requirement. Visual acceptance and in-game visibility remain separate.

The baseline pack must be exported from commit b595707, before these four
additions. The current default debug pack is the candidate333-file pack.
Recreate the artwork output with prototype/build-pulse-art.py first.
