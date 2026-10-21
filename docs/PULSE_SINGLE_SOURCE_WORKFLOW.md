# Pulse: one selected art version, all current consumers

The maintenance unit is a **semantic resource ID**, not a duplicate byte group.
This pilot covers exactly 80058, 80059, 80060, 80062 and 80165. It does not
change weapon tables, original source banks, palettes, eligibility or gameplay.

## One maintenance entry

`assets/hd/authoring/pulse-current.json` selects one immutable, normalized
96 × 112 straight-RGBA PNG per ID. The initial selection is the approved
`pulse-family-v2-simple/exports/` version. Keep previous art versions unchanged;
put an intentional new version in a new directory and select its PNG path and
SHA256 in an external draft copy of this selection. Keep the installed current
selection untouched until apply installs the proposal atomically per file. Normalizing a new image is a separate artistic decision. This tool
only encodes the selected pixels without resampling, recoloring or alpha edits.
Anchor 59 stays (-1, 0); other anchors stay (0, 0).

```
cp assets/hd/authoring/pulse-current.json /tmp/pulse-proposal.json
# Edit /tmp/pulse-proposal.json to select the new PNG paths and SHA256 values.
python scripts/build_current_pulse.py stage --selection /tmp/pulse-proposal.json --stage /tmp/pulse-next
# Review /tmp/pulse-next/plan.json: exact destinations and expected old/new hashes.
python scripts/build_current_pulse.py apply --stage /tmp/pulse-next
python scripts/build_current_pulse.py check
```

For an art change, supply the external reviewed proposal with `stage --selection`.
Default stage is only a rebuild of the already installed current selection.
The chosen selection is installed with the other outputs by `apply`. A stage
must be a new directory outside the repository, with no symlink parents. Apply re-derives the plan from current source inputs,
checks old destination hashes and staged bytes before the first write, and
rejects stale/tampered plans. It does not delete old content-addressed files.
Apply uses atomic replacement per file, not a multi-file filesystem transaction;
a process or disk failure can leave a partially applied set. Run `check` before
packaging, and restage deliberately after inspecting any such interruption.

## Automatically synchronized current consumers

1. Five exact HDR1 blobs and their content-addressed global paths.
2. Five global registry art rows; every family/source/role definition is retained.
3. `src/global_asset_registry.h`, used by battle and SHOP.
4. `assets/hd/current-compat/pulse/bullet-*-8.hda`, byte-identical to the global
   resources, and `packaging/current-pulse-compatibility.json`.
5. The five existing `assets/gameplay/bullet-*-8.hda` **runtime package destinations**
   now obtain content from that current compatibility overlay. The selected old
   development pack remains an immutable historical input, verified against the
   original baseline before these current outputs override its five rows.
6. The package registry fingerprint, exact current production binding and runtime
   asset inventory. A binding is a source hash inventory, not a new test approval.

The normal battle and SHOP paths already share the same global IDs. The
compatibility change keeps manual legacy mode in the **built current package**
on the selected art too. Manually pointing development debug commands at a
historical pack intentionally selects historical art; those archives are not
rewritten. No 4× HDR1 variant was shipped for these five resources, so none is
invented. Output scaling and legacy eligibility remain unchanged.

## Check and acceptance

`check` regenerates expected outputs without changing the repository. A missing
or stale declared output fails; a source hash mismatch fails. Packaging separately
requires the compatibility mapping and checks exact equality with global bytes.
The historical baseline and frozen acceptance records are never rewritten. Immutable
approved-base policy hashes reject changes to family/source authority, unrelated registry resources, fixed geometry, gameplay source and build inputs.
The shared builder separately validates each other supported family against its selection. Only
the five art payloads/provenance and declared generated consumers can change.

A new art version still requires visual/native acceptance: this builder establishes
propagation and integrity, not whether a design is aesthetically approved or a
new role can use it. Frozen art-revision tests remain historical acceptance and
must not be weakened into blanket approval for arbitrary future artwork.

Vulcan now uses the same generic builder; see `CURRENT_ART_SINGLE_SOURCE_WORKFLOW.md`.
Coins/gems and shared HUD authoring remain separate future work.
It is not a disk-space optimization: current compatible paths remain ordinary
independent files, preserving separate missing/corruption behavior.
