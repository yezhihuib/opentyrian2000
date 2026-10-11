# Purple installation: portable effect regressions

These CPU-only fixtures execute extracted production functions. They do not run the game or create artwork. The combined renderer has312 asset slots,153 terrain registrations, the finite layer3 gray18/purple13 families, and59 independent enemy bindings.

## Inputs

Python3, a C99 compiler, AddressSanitizer, and UndefinedBehaviorSanitizer are required. Pillow is needed for optional ZIP or canonical PNG verification. LeakSanitizer is disabled under ptrace; address and undefined-behavior checks remain enabled.

Source defaults resolve from each fixture's repository root. Existing `--source` arguments can select another checkout. Asset tests default to the repository's accepted blue-four/head-v1 pack and accept `--assets` overrides.

The gray loader fixture requires original game data via `--data` or `TYRIAN_DATA_DIR`. It validates both data-file hashes and derives the level9 lookup tables directly from the original level header, enemy count, and event count. `--topology` is optional independent JSON verification; no separate map audit is required for normal use.

The installation entity fixture uses the repository's `assets/hd/artwork/purple-installation32-41-v2/selected-manifest.json` when present to verify each HDA hash/header and canonical source PNG hash/payload. Its `original-alpha-contract.json` is also checked when present. Independent sparse-alpha coordinates are embedded and always enforced, even without external metadata. `--art-manifest`, `--alpha-contract`, and optional `--runtime-zip` provide explicit overrides. Reports disclose which optional inputs were checked.

## Run the prior suites

From the repository root, with `TYRIAN_DATA_DIR` set to a licensed original-data directory:

```sh
REPORT_DIR=$(mktemp -d)
export PYTHONDONTWRITEBYTECODE=1
python prototype/fixtures/test-layer3-gray-binder.py --sanitize --report "$REPORT_DIR/gray-binder.json"
python prototype/fixtures/test-layer3-gray-alpha.py --report "$REPORT_DIR/gray-alpha.json"
python prototype/fixtures/test-layer3-gray-mutations.py --binder-report "$REPORT_DIR/gray-binder.json" --report "$REPORT_DIR/gray-mutations.json"
python prototype/fixtures/test-turret40.py --sanitize --output "$REPORT_DIR/turret40"
python prototype/fixtures/test-cloud-shadow.py --sanitize
python prototype/fixtures/test-green-background.py --sanitize
python prototype/fixtures/test-green-head-layer.py --sanitize
python prototype/fixtures/test-enemy-orb.py --sanitize --output "$REPORT_DIR/enemy-orb"
python prototype/fixtures/test-ground-binder.py --sanitize --output "$REPORT_DIR/ground"
python prototype/fixtures/test-plateau-binder.py --sanitize --report "$REPORT_DIR/plateau.json"
python prototype/fixtures/test-underlay-binder.py --sanitize --report "$REPORT_DIR/underlay.json"
python prototype/fixtures/test-road-binder.py --sanitize --report "$REPORT_DIR/road.json"
python prototype/fixtures/test-terrain-holes-binder.py --sanitize --report "$REPORT_DIR/holes-binder.json"
python prototype/fixtures/test-terrain-holes-alpha.py --report "$REPORT_DIR/holes-alpha.json"
python prototype/fixtures/test-terrain-next-seven-binder.py --sanitize --report "$REPORT_DIR/next-seven-binder.json"
python prototype/fixtures/test-terrain-next-seven-alpha.py --report "$REPORT_DIR/next-seven-alpha.json"
```

Terrain inventory checks accept exactly the established77 IDs or the reviewed90-ID extension. The original59 layer1/layer2 payload, pixel, hole, clipping, and residency checks remain unchanged.

The turret fixture retains all three turret artwork checks, exact nine-step phase selection, and terrain153/entity153 cache isolation. Its finite prior-binding list includes the nine installation bases; all59 bindings and wrong-bank negatives are checked. Its synthetic RLE bank has320 entries because base283+part20 requires sprite303. The optional turret `--clean-source` audit permits only the exact three turret and nine installation lookup additions, each required exactly once. Removing those twelve terms must leave a byte-exact match to the older renderer; wrapper/blitter and unrelated-helper comparisons stay exact.

## Run the installation entity suite

```sh
python prototype/fixtures/test-installation9.py --sanitize --output "$REPORT_DIR/installation9"
python prototype/fixtures/test-installation9.py --sanitize --actual-only --output "$REPORT_DIR/installation9-actual"
```

The full suite checks all9 bases, four quadrants, all24 draw orders, all256 filters, clipping, partial quadrants, malformed/missing/null inputs, wrong banks,59 simultaneous bindings, and terrain169/entity169 cache isolation in both orders. At density4, the full9-by24-by256 product compares RGBA and ownership after every quadrant. Native8 and inherited4-to-8 paths retain full coverage of their representative orders and filters. The original wrapper oracle requires exact indexed output, one original blit, one end call, and an unchanged enemy record.

`--actual-only` runs the existing actual-art oracle for all nine components, three filters, clipped placements, and all15 nonempty quadrant subsets. It does not replace the generic suite. Both modes verify the selected sparse-alpha contract and available canonical PNG/HDA evidence.

Temporary synthetic inputs are retained. Tests that need a generated file to become absent rename it out of the load path. Results and retained-work paths belong in external reports, not committed evidence. The no-state-mutation assertion concerns the exercised wrapper and its enemy record; these fixtures do not establish whole-runtime gameplay or visual acceptance.

## Current finite grass/sand compatibility

With the nine Layer1 grass/sand slots, current capacities are321 assets and162
registrations. The fixtures retain their previous guards and pixel expectations;
only extraction lists, strict capacities and finite accepted inventories change.
Terrain inventories accept only the exact77/90/99 reviewed-ID sets. See
README-grass-sand-tests.md for current7c7 source and artifact baselines.
