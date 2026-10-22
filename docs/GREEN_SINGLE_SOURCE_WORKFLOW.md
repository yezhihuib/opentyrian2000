# Green energy: one selected source per head or trail

The `green` authoring profile contains exactly four bank8 heads 214–217
(identities 80214–80217) and seven NEWSH6 trails 78–84 (1060078–1060084).
These eleven resources already have global identity; this migration makes their
selected sources authoritative for current legacy consumers too. No pixels change.

`assets/hd/authoring/green-current.json` selects the approved PNGs. Every source is
single-frame 96×112 straight RGBA, logical 12×14 at density8, anchor0,0. Head and
trail identities remain separate even when pixels match: matching pixels never
license another source bank, role, weapon or phase.

## Change one selected source, rebuild all current consumers

Save new approved artwork at a new source path, copy the installed selection to
an external draft, then change that row's path and SHA256 and the draft version.
Do not overwrite approved historical artwork or directly edit the installed
selector, which authenticates the currently installed version.

```sh
python scripts/build_current_art.py --family green stage \
  --selection /path/outside/repo/green-draft.json \
  --stage /path/outside/repo/new-green-review
# Inspect plan.json and staged files before applying.
python scripts/build_current_art.py --family green apply \
  --stage /path/outside/repo/new-green-review
python scripts/build_current_art.py --family green check
```

This emits the selected global HDA and registry/header pins, current compatibility
mapping, eleven legacy outputs under `assets/hd/current-compat/green/`, and exact
runtime/source-binding inventories. Legacy destinations remain
`assets/gameplay/bullet-214-8.hda` through `bullet-217-8.hda` and
`assets/gameplay/explosion-newsh6-78-8.hda` through `explosion-newsh6-84-8.hda`.
Four generated `CURRENT_GREEN_<identity>_RGBA` macros update existing head/shadow
payload eligibility; source fingerprints and slot/role pins are not generated.
Rebuild the executable and package after an art change so compiled pins agree.
There is no per-level copying and no separate trail payload constant to maintain.

Stage is non-mutating and must be outside the repository. Apply validates all
source, authority, old-output and staged hashes and temporary collisions before
writing. Replaces are atomic per file, not a crash-safe multi-file transaction;
after interruption inspect and restage. Other selected profiles and HUD must stay
consistent. Historical packs/manifests and old content-addressed blobs remain.

Head-over-smoke composition, background blending, shadows, original source-bank
and weapon-record guards, birth/lifetime/animation authority, draw order and all
gameplay remain unchanged. Explicit historical development packs still select
historical artwork. New visual designs require separate visual/native acceptance.

Independent synthetic tests exercise propagation and rejection without editing
approved art. Native Linux software and package checks are separate evidence, not
Windows/GPU/full-campaign or subjective visual acceptance.
