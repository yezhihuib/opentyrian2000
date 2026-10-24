# Current art: edit once, rebuild every declared consumer

The purpose is maintenance, not merely deduplication: choose one source version
per semantic resource, and do not search each level or SHOP to replace copies.

## Supported scope

- Pulse: five independent IDs 80058/59/60/62/165.
- Vulcan: two independent IDs 80067/70, including the existing legacy head/shadow
  eligibility table. The original INDEX8 source-bank pins remain immutable.
- `cash25`, `cash50`, `cash75`: six body frames and one fixed value popup each.
- `gem100`, `gem250`: five body states and one fixed value popup each.
  These five families cover 33 independent IDs, not 33 interchangeable copies.
- Green energy: four bank8 heads and seven NEWSH6 trails; see
  [Green single-source workflow](GREEN_SINGLE_SOURCE_WORKFLOW.md).
- Talon13 and Rotor8: fixed 192×224 sources, logical 24×28 at density 8; see
  [large-sprite workflow](LARGE_SPRITE_SINGLE_SOURCE_WORKFLOW.md).
- HUD was outside the original cash/gem batch; its separate current workflow
  uses `scripts/build_current_hud.py`. Existing effect and Shield profiles also
  use the shared builder.

Each family has `assets/hd/authoring/<family>-current.json`. Each identity selects
one PNG with its SHA256. Separate identities, source banks, roles and anchors stay
separate even if their pixels happen to match. Approved original PNGs are not edited
by the builder. A new version should be placed at a new source path, then selected in an external draft JSON passed to `--selection`. Do not directly
edit the installed `*-current.json`: it authenticates the current state until apply.

## Commands

```sh
python scripts/build_current_art.py --family vulcan check
python scripts/build_current_art.py --family vulcan stage --selection /path/to/selection.json --stage /path/outside/repo/new-stage
# Inspect plan.json and staged files, then:
python scripts/build_current_art.py --family vulcan apply --stage /path/outside/repo/new-stage
python scripts/build_current_art.py --family vulcan check
python scripts/build_current_art.py --family pulse check
```

`build_current_pulse.py` and `build_current_vulcan.py` are convenience wrappers over
one validated implementation. The selected family emits content-addressed HDA,
global registry/header, its current legacy compatibility files/mapping, generated
legacy payload pins, and exact current package/source-binding inventories.
Every other supported family's selected source and provenance must remain consistent.

Current global battle and SHOP consumers use the global identities; current legacy
package consumers use `assets/hd/current-compat/<family>/`. The generated
`src/current_art_payload_pins.h` covers Vulcan, cash/gem and Green head RGBA art only, never INDEX8 source identity.
Changing pixels requires rebuilding the executable so its generated pins agree.
Explicitly choosing an old development pack still chooses historical art.

## Safety and acceptance

Stage is non-mutating and must be outside the repository. Apply re-derives the
plan and validates selected source hashes, immutable role/source/build policy,
all expected old hashes, staged bytes and temporary-path collisions **before**
writing. Paths reject traversal and symlink components. Writes are individually
atomic; this is not a crash-safe multi-file transaction. On interruption, inspect
and restage rather than assuming the batch completed.

No historical pack or accepted source PNG is overwritten or deleted. PNG decoding
must be single-frame straight RGBA, exactly the trusted per-profile dimensions
(96×112, or 192×224 for Talon/ Rotor), with fixed original HDA geometry;
there is no resize, palette conversion or re-interpretation of resource roles.
`check` detects missing/stale declared generated consumers. Package assembly also
requires exact compatibility/global equality. Source-binding inventory is not
visual acceptance: a genuinely new design still needs visual/native verification.

The cash/gem extension preserves approved pixels byte-for-byte. It changes only
legacy RGBA payload constants to equal generated macros, not source-bank stamps,
records, anchors, reward amounts or animation. In particular, the 16-step gem
cycle and record 509's 250 reward with fixed100 display remain unchanged. Body and
popup identities remain independent even when source PNG bytes match.

For example, copy `assets/hd/authoring/cash25-current.json` to an external draft,
select newly approved source paths/hashes there, and use the commands above with
`--family cash25`. Repeat for a different family only if that family's art changes;
no level-by-level or package-by-package replacement is necessary. Do not edit the
generated compatibility HDA or C payload pins by hand.

Propagation tests use synthetic PNG fixtures only; they never modify the user's
approved art. Runtime/native acceptance records are separate.

## Legacy-only authoring extension

The enemy tank-shell pair (1220146/1220147) has a separate
[`build_current_tank_shell.py` workflow](TANK_SHELL_SINGLE_SOURCE_WORKFLOW.md).
It generates exactly two existing legacy consumers and payload-only pins, without
adding global registry identities. Thus coverage is 120 global resources plus two
legacy resources and the independent HUD workflow, not 122 global resources.

## Additional legacy enemy-energy family

Seven enemy-energy resources have an independent single-source workflow in
[ENEMY_ENERGY_SINGLE_SOURCE_WORKFLOW.md](ENEMY_ENERGY_SINGLE_SOURCE_WORKFLOW.md).
They remain outside the 120-entry global registry and preserve original mask
support, static directions and Christmas rejection. Together with tank shells,
there are now nine explicitly maintained legacy-only authoring resources.

## Marlo and Plasma body family

The six existing bank9 bodies have an independent workflow in
[SIDEKICK_BODY_SINGLE_SOURCE_WORKFLOW.md](SIDEKICK_BODY_SINGLE_SOURCE_WORKFLOW.md).
It preserves the approved Marlo single frame and Plasma five-frame bytes,
identities and runtime qualifications. Its generated body header is read only
by Python build/package consistency checks; production C does not include it
or gain runtime payload enforcement. Coverage stays at 120
global entries, six HUD classes and 15 independent legacy-only resources.

NEWSH2 base267 uses the bounded [craft267 workflow](CRAFT267_SINGLE_SOURCE_WORKFLOW.md). Current body pack views combine that canonical HDA with the six selected sidekick transports.

## Charge body single-master extension

Charge is a separate nine-state subfamily of the shared sidekick builder. One
normalized master plus a data-only recipe generates every state; derived PNGs
are not independent editable inputs. See [workflow and strict candidate/current
boundaries](CHARGE_BODY_SINGLE_MASTER_WORKFLOW.md). Existing family defaults and
historical exports retain their prior meanings.

## Front Multi8 independent current sources

The eight existing role8 resources121/122/163/164/201/202/279/280 use the bounded
[Front Multi8 workflow](FRONT_MULTI_EIGHT_SOURCE_WORKFLOW.md): eight independent
96×112 sources, eight current transports and payload-only shadow pins. Current
runtime remains1015 destinations; complete views are650 files with169 current
overlays and481 frozen members. Historical rear182/183 still depend on frozen
front163/164, not the mutable current selection. No gameplay coverage expands.

## Read-only authoring map

Run `python3 scripts/shared_asset_authoring_map.py --id 80112 --format json`
(omit `--id` for all supported contracts, omit `--format json` for readable text).
The index is generated on stdout from strict current selections/loaders, not a
second hand-maintained resource list. It gives editable inputs, recipes, derived
outputs, declared consumers and existing rebuild commands; shared source paths
group contracts without merging role/density or recipes. Material IDs differ
from sprite numbers; HUD accepts names such as `hud:font`. Unknown IDs fail.

Charge has one input/nine outputs; Plasma projectile one input/six density-role
contracts; Orb has two independent inputs/four ordinary-or-masked contracts.
NEWSHF163/167 now have two canonical authored three-pose masters under
`authoring-inputs/newshf-current/`, producing six current normalized PNGs and
transports through `build_current_newshf.py stage/apply/check`. These are physical
bank/base slots, not inferred left/right directions or automatic animation.
The original nine-pose selection and its old compiler remain frozen; all three
168 V4 poses still use the exact approved soft-alpha policy and are not editable
through this new workflow. The nine runtime destinations, opt-in group and
default-off renderer eligibility are unchanged. P05 adds a finite role146
consumer of three existing Green sources, not new masters. Frozen P09/player244
share a master but reject edits under their historical hashes; they are not a
current edit/apply loop. Front's historical rear182/183 remain outside current
propagation. No level usage is inferred. The map writes no index or artwork and
fails on missing/stale selected inputs or contracts. Rebuild commands are
instructions only, never executed by the map. Current edits still require the
existing candidate/stage/review/apply workflow and full family checks.
