# Marlo and Plasma bodies: six-source legacy authoring

This workflow maintains the six existing approved bank9 body resources below.
It adds zero global registry identities: global coverage remains 120, with six
HUD classes and 15 independent legacy resources (two tank shells, seven enemy
energy shots and these six bodies). Terrain and clouds remain paused.

| Role / option | Bank9 indices in fixed selection order | Identities | Geometry |
| --- | --- | --- | --- |
| Marlo role126 / option30 / style4 / charge0 | 152 | 1260152 | density8, logical12x14, anchor(0,0) |
| Plasma Storm role129 / option9 / style0 / charge0 | 224,243,262,281,300 | 1290224,1290243,1290262,1290281,1290300 | density8, logical12x14, anchor(0,0) |

Selection: `assets/hd/authoring/sidekick-body-current.json`. Each source is one
96x112 straight RGBA PNG. The initial selection uses the original approved
`assets/hd/source/option-{marlo,plasma}-bank9-*-8-*.png` files. Bootstrap HDA
bytes match their historical approved pack exactly. No historical PNG, HDA,
manifest, artwork proof or pack is overwritten. The parent task's new image
sample is outside this workflow's initial selection.

## Workflow and generated outputs

After separate approval of new artwork, place the PNG at a new repository path
and edit an external copy of the selection with that path, its SHA256 and a
version. Keep all six identities in the fixed order. Do not edit geometry or
replace the installed selection before applying.

```powershell
python scripts/build_current_sidekick_body.py stage --selection ..\draft.json --stage ..\new-sidekick-stage
# Inspect plan.json and files/ before applying.
python scripts/build_current_sidekick_body.py apply --stage ..\new-sidekick-stage
python scripts/build_current_sidekick_body.py check
python scripts/verify_current_production.py
```

Stage must be new and outside the repository. Omitting `--selection` stages the
installed selection. Stage performs no repository writes. Apply re-derives the
plan, validates every expected old hash and staged byte, and preflights output
paths and temporary collisions before its first write. Traversal, symlink and
Windows junction/reparse components are rejected. Writes are individually
atomic, not a crash-safe multi-file transaction; inspect and restage after an
interruption.

Outputs are exactly the selection, six HDA files in
`assets/hd/current-compat/sidekick-body/`,
`packaging/current-sidekick-body-compatibility.json`,
`src/current_sidekick_body_payload_pins.h`, the current production binding and
the current runtime manifest. Package destinations remain
`assets/gameplay/option-marlo-bank9-152-8.hda` and
`assets/gameplay/option-plasma-bank9-{224,243,262,281,300}-8.hda`.
The runtime destination set stays at 1006. Other authoring workflows include
this mapping in their derivation closure so their updates retain these bodies.

The generated header provides **build/package consistency checks only**.
`scripts/current_sidekick_body_compatibility.py` recomputes the payload values
and compares the generated text in Python. Production C does not include this
header or enforce its payload values: the existing Marlo and Plasma loaders
gain no runtime payload pin, rejection or fallback condition. Raw-bank
qualification, source guards and fallback remain in the existing production
logic. Merely listing this header in the complete source binding does not make
it a production C dependency. The complete source inventory includes all
252 files, including this new header; removing its binding, even with a
recomputed aggregate digest, fails verification.

## Runtime boundary and validation

At the sidekick-only foundation `6ada526fa11c633e3ae02facb5f498bbfdacd1d9`,
all 251 pre-existing source files remained byte-exact to baseline
`775b6b77163723c6cae727bafce1d53746a5bd60` and the integration base
`f8bf77f2f7219fcc63bebb6cc644c3ab83211e3e`. Original source-bank fingerprints,
Marlo bank9 decoding, five-frame Plasma phase selection, 4x/8x/classic fallback,
ammo, collisions, positions and RNG remain unchanged. The identities remain
distinct even when artwork might look alike. Do not infer another role's HD
eligibility from this authoring mapping.

The later [reviewed render-boundary integration](RENDER_BOUNDARY_INTEGRATION.md)
changes exactly `src/render_mirror.c` and `src/global_talon_mirror.inc` relative
to that foundation. Its current package source binding records those actual
bytes; the sidekick foundation and older receipts retain their original scope.
Those rendering corrections are not a claim that current source still equals
775, and they do not add sidekick runtime payload enforcement or change the
six selected body resources.

`tests/test_current_sidekick_body_authoring.py` uses synthetic PNG fixtures to
exercise each source independently, exact propagation and isolation, unchanged
historical packs, composition with global/HUD/tank/energy workflows, stale plans,
tampered or missing staged bytes, wrong identities/order/geometry, invalid PNG
size/mode/hash/data, path escapes and simulated Windows reparse attributes.
The actual Windows junction test is an explicit opt-in with
`OPENTYRIAN_TEST_NTFS_JUNCTIONS=1` when `mklink /J` is permitted. In this local
environment link creation returned `Access is denied`; no permission setting
was changed or alternate link target tried. That actual filesystem test remains
unverified here and is not replaced by a claim of native junction coverage.
Packaging tests
also check actual source-binding membership and deterministic manifest output.
The two manifest/header text generators write explicit UTF-8 LF bytes so native
Windows newline translation cannot change their frozen outputs.

These authoring tests and a Windows Release build do not establish new artwork's
visual acceptance. Campaign animation, compositor/GPU and natural gameplay
verification remain separate. Historical package acceptance evidence is not
relabelled as acceptance of this local candidate.

## Review provenance and integration scope

The parent task reported independent review of frozen commit
`b4d3575e69a74b5ce1f3de7f6907f93d32e1dc2a` (tree
`ce64ec74f5d37d043094ae90e93da174f0e32786`), based on 775: authoring 14 PASS /
1 junction SKIP, four packaging tests, 1007-file preflight, CLI stage/apply/check,
120/1006/252 inventories, unchanged old 251 source files and six HDA payloads,
plus SDL guard/wrapper qualification and four negative controls. Its production
MSVC `/showIncludes` run had zero references to the new header. This is evidence
for that frozen version's stated scope, not a new runtime payload-pin hookup.

This integration starts at f8, retaining the 79-file public test/documentation
repair and all four performance files. It reruns affected authoring and cache
tests and records its own candidate receipts. Neither the earlier review nor
these targeted reruns establish that this integration passed the complete long
test suite, GPU/compositor or natural campaign acceptance. New artwork remains
outside this old-pixel integration.
