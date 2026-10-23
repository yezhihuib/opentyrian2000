# Front Multi8: eight independent current sources

This bounded workflow shares **one editable source per existing resource**, not
one source for all eight. It copies the already-approved normalized PNGs
byte-for-byte at bootstrap; it generates no new artwork and does not resample,
merge phases, edit SVGs, introduce densities or extend gameplay coverage.

## Fixed resource boundary

| Source PNG / HDA basename | Identity | Existing shadow slot |
| --- | --- | --- |
| bullet-121-8 | 80121 | 524 |
| bullet-122-8 | 80122 | 525 |
| bullet-163-8 | 80163 | 526 |
| bullet-164-8 | 80164 | 527 |
| bullet-201-8 | 80201 | 528 |
| bullet-202-8 | 80202 | 529 |
| bullet-279-8 | 80279 | 530 |
| bullet-280-8 | 80280 | 531 |

All eight are existing role8, density8 HDR1 resources: logical12×14,
anchor(0,0), from complete **96×112 straight RGBA8 PNGs**. The eight initial
editable files live under `authoring-inputs/front-multi-current/` and exactly
match `assets/hd/artwork/player-front-multi-eight-v1/output/`.

The original approved inventory, normalized output PNGs, default packs,
catalogs, contracts and acceptance fixtures stay frozen. In particular,
historical rear derivatives1310182/1310183 retain their frozen front163/164
inputs. Editing current front163/164 must not silently change those rear assets.

## Edit, stage, inspect, apply

Installed selection: `assets/hd/authoring/front-multi-current.json`.
Copy that JSON outside the repository, retain all eight ordered identities,
change the version and update only the edited source's path/hash. Each record
has exactly `identity`, `source_png` and lowercase `source_sha256`; the complete
selection has exactly `schema`, `version` and `resources`.

The schema is `opentyrian-current-front-multi-authoring-v1`. Sources must be
regular, independent `authoring-inputs/…/*.png` paths. In-place source edits
are supported by proposing the new hash in the external selection; until
apply, the installed selection is intentionally stale. Generated Charge/Plasma
pieces, their aliases, hardlinks, symlinks, reparse points, traversal, wrong PNG encoding,
animations, trailing bytes, duplicate JSON keys and nonfinite numbers fail.
The accepted normalized PNG dialect is IHDR, optional PLTE/pHYs, contiguous
IDAT and IEND only; export without other metadata. Chunk order, CRC, palette
length, physical-density metadata and the exact bounded zlib stream are checked.

```sh
python -B scripts/build_current_front_multi.py stage \
  --selection /absolute/path/front-multi-draft.json \
  --stage /absolute/path/new-front-multi-stage
# Inspect plan.json, request.json and files/ before applying.
python -B scripts/build_current_front_multi.py apply \
  --stage /absolute/path/new-front-multi-stage
python -B scripts/build_current_front_multi.py check
python -B scripts/verify_current_production.py
python -B scripts/package_runtime.py
```

Stage does not mutate the repository. Apply rereads the request and sources,
rederives all outputs, checks the complete finite dependency fingerprints,
old output hashes, staged bytes and all output/temporary paths before writes.
Handled replacement failures roll back; this is **not a crash-safe multi-file
transaction**. After interruption inspect the state and explicitly restage.
A changed apply makes its old stage stale. A byte-identical no-op can repeat,
but never grants permission to overwrite later work.

The finite outputs are the installed selection, eight HDAs in
`assets/hd/current-compat/front-multi/`, compatibility mapping, dedicated
payload-only C header, current source binding and runtime manifest. Apply never
rewrites the eight selected PNGs. Current source/tool closure includes Plasma,
Charge and Mint/Front and is carried by every existing authoring builder;
there is no recursive artwork/provenance input glob.

**Rebuild the executable after changing a Front Multi source.** Generated
`src/hd_front_multi_current.h` pins the eight existing shadow payload checks.
An old binary correctly rejects new payloads; packaging never compiles or
silently swaps binaries.

## Current views and packaging

```sh
python -B scripts/build_current_craft267.py view --kind preview \
  --output /absolute/path/new-preview
python -B scripts/build_current_craft267.py view --kind debug \
  --output /absolute/path/new-debug
python -B scripts/package_runtime.py --build \
  --output /absolute/path/new-runtime
```

Each complete view remains **650 files:169 current overlays and481 unchanged
frozen members**. Runtime remains **1015 destinations**, global registry remains
**120 resources**, and exact current C inventory is **254 files**. Bootstrap
preserves every gameplay payload byte; only these eight runtime source/revision
pairs and the current production-binding row migrate. The family uses exactly
eight rows in default/current packages. Historical/custom packages with no
current Front Multi reference retain standalone semantics, without depending
on this authoring module or its current inputs.

Production C changes are only one include and eight existing shadow-table
payload literal substitutions. Existing legacy scene coverage remains E1
physical9 or qualified15, including ASTEROID1 exclusions; this is not all-level
coverage. No eligibility, source-stamp, geometry, selected-density loading,
cache, blend, indexed-write, fallback or draw-order changes are authorized.
A separately pinned inverse projects the narrow source extraction before old
historical oracles; no historical acceptance fixture is rebased.

## Verification boundary

`tests/test_current_front_multi_authoring.py` exercises eight independent edit
isolations, source/mapping/header tamper rejection, strict schema/PNG/path
handling, stale plans/tool inputs/staged bytes, preflight and handled rollback,
both complete views, exact8 package closure and standalone historical packages,
frozen rear derivatives, and composition with existing authoring families.
`FRONT_MULTI_REAL_COPY_OUTPUT` selects a new external directory for the guarded
real CLI package copy in the propagation test. Native compile and controlled
shadow harnesses are separate from Windows, GPU, full-campaign or new-art
acceptance.
