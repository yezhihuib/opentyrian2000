# Current Regular Missile authoring

## Scope

The existing bank 8 sprites 31, 32 and 33 are **three independent static upgrade designs**, not animation frames or variations generated from a common master. Their original source identity, role 8, slots 333/334/335, logical 12×14 geometry, density 8 and anchor `(0,0)` are unchanged. Sprite 33 retains its original one-logical-pixel-left placement. Existing Guided 20/21 and smoke/impact effects are not part of this edit family. Sprite 31's shared special-weapon reuse is not a claim of complete special-weapon gameplay coverage.

The approved original art package is frozen at `assets/hd/artwork/regular-missile-family-v1/`. Current editable copies live in `authoring-inputs/missile-current/master-31.png`, `master-32.png` and `master-33.png`. Editing one master updates only its corresponding current PNG/HDA. It does not revise the original source package, approved receipts, renderer source pins, or the global registry.

## Exact rendering recipe and tool requirement

The fixed recipe file records each approved whole-object crop, nonuniform Lanczos fit and paste placement on a transparent 96×112 canvas. The compiler implements a finite argument vector, not executable instructions supplied by JSON. It feeds a strictly checked single-frame RGBA8 PNG over `PNG:-` and receives `PNG32:-`; no source filename, shell command, URL or alternate coder is accepted.

The required existing tool is `/usr/bin/magick`, ImageMagick **7.1.1-43 Q16 x86_64 22550**. Both its precise version line and a fixed synthetic PNG golden profile must match on every derivation. No automatic install, download, alternative converter or Pillow approximation occurs. A missing tool, wrong profile, failed command, timeout or oversize result is an error. Subprocess environment overrides are not inherited; resource limits, a private scratch directory and a 30-second timeout are applied. Captured output is checked before it is consumed. This is a Linux authoring-tool contract, not a claim that arbitrary Windows or other ImageMagick builds produce the same bytes.

Source alpha and hidden RGB under alpha 0 are preserved by the original ImageMagick operation. There is no recoloring, alpha threshold, nearest-neighbor upscale, silhouette mask or recentering. In particular, the approved outputs contain nonzero RGB under zero alpha, and these bytes remain part of the HDA payload proof. Fixed crop bounds are intentional; edits should keep the object inside them rather than change the recipe.

## Workflow

1. Edit the appropriate current master without changing the fixed canvas dimensions or recipe.
2. Prepare a candidate JSON using schema `opentyrian-current-missile-candidate-v1`, the same three ordered master paths with their new SHA256 values, the unchanged recipe path/hash, and a new version label. Omit installed `resources` from the candidate.
3. Run `python3 scripts/build_current_missile.py stage --selection /absolute/candidate.json --stage /absolute/new-stage-directory`.
4. Review the plan and generated PNGs. Then run `python3 scripts/build_current_missile.py apply --stage /absolute/new-stage-directory`.
5. Run `python3 scripts/build_current_missile.py check` and the relevant runtime/package tests.

Stage does not modify the repository. Apply rederives the complete output and compares the exact request, current input fingerprints, plan and staged bytes before writing. It restores old files after handled write failures; this is not power-loss/process-crash atomicity. Use a new stage after changing inputs. Image-generation approval is separate from a synthetic validation edit.

## Consumers and unchanged runtime boundary

Current transports use the same three existing destinations `assets/gameplay/bullet-{31,32,33}-8.hda`; the formal runtime remains 1029 entries. Generated `src/current_missile_payload_pins.h` replaces only the three existing shadow payload literals. The generic ordinary-shot loader and its existing source behavior are unchanged; the dedicated shadow lease still uses its original source pins and eligibility checks. No new player/sidekick weapon-fire or gameplay eligibility is enabled.

The compatibility mapping, shared authoring map and other current builders carry the finite eleven-path selected/canonical closure plus its mapping. The three shared payload macros move with a real edit, preventing an updated ordinary projectile from retaining an obsolete shadow payload pin. Source binding reflects the extra generated header; historical tests use a verified finite inverse, not a changed historical baseline.

## Validation boundaries

Bootstrap current PNG, RGBA and HDA bytes must exactly reproduce the already-approved original images and existing formal runtime payloads. Tests cover independent master edits, malformed inputs, wrong tooling, stale/modified plans, package rows, handled rollback and unrelated resource invariants. The validation receipt records actual completed tests. Linux/Windows *asset export layouts* are not Windows game execution. Native wrapper tests are not natural campaign, actual weapon firing or physical-GPU visual acceptance.

### Recorded validation evidence

- `current-missile-build-validation.json`: six fresh Linux builds in three modes; all 258 object pairs per mode and all three linked executables exactly match public `0fde773717b714f6d5c02cb024b9265e28c25d38`.
- `current-missile-native-validation.json`: bootstrap and truly edited 31/32/33 lanes each pass 337 setups and 189,824,834 assertions, including the unchanged legacy matrix. The isolated wrong-shadow-pin negative control fails as expected. Final compiler derivation reproduces the native-tested payloads and complete source snapshot.
- `current-missile-independent-review.json`: independent compiler/closure review and focused 19 plus integration 8 test runs. A later comment-only clarification describes output size checking accurately; native final derivation records the final compiler hash.
- `current-missile-history-review.json`: independent finite source/runtime inverse review; all 273 current source files project exactly to the 272-file public baseline. Frozen ledger fixtures remain unchanged.
- `current-missile-history-focused-validation.json`: 121 distinct focused historical/consumer tests with exact log hashes and retained diagnostic outcomes, including clean corrected reruns. This focused receipt does not stand in for the separate full historical aggregate.
- `current-missile-history-validation.json`: full historical aggregate **54/54 PASS** in 3482.868 seconds, for **175 distinct historical methods** together with the focused suite. Before/after inventory covered 1162 files: imported aggregate/helper/compiler/source inputs stayed unchanged; the sole delta was the separately rerun Mint runtime test adaptation, not imported by this aggregate.
