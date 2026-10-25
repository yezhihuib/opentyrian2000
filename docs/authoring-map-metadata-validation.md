# Authoring navigation metadata correction

This bounded correction is based on private checkpoint
`4cb0586a7bbf79d6eba1fc73557079324cd6d692` (2026-10-25). It changes only
navigation descriptions and rejection of identical consumer declarations, not
master artwork, recipes, generated outputs, runtime packaging or gameplay.

## Ownership correction

- Front Multi retains eight independent PNG inputs. It no longer advertises
  the unrelated Lobes JSON masters.
- Rear P7 retains canonical SVG294 and its mirrored295 outputs at d4/d8.
  The accidentally duplicated Lobes note and two duplicate C consumer claims
  are removed. Normal/shadow declarations each remain once per contract.
- Rear39, Rear1 and P7 no longer describe newer independent Rear families as
  frozen. See `current-rear-source-ownership.md`: 46 current editable outputs
  from six masters, plus two protected historical182/183 outputs. Those two
  historical outputs do not follow current Front163/164 edits.
- Lobes retains its two independent JSON203/43 masters, four outputs per
  master. Neither source is substituted for the other.
- The validator rejects duplicate **complete dictionaries**, regardless of
  dictionary insertion order. It does not deduplicate by path: different
  evidence, role and scope claims remain meaningful, including the NEWSHF
  `destination` schema.

## Verification boundary

Strict before/after maps retain 35 families, 244 contract rows and 210 indexed
source-input paths. Exactly 26 rows change explanatory notes; four P7 rows also
lose two identical consumer declarations each. After normalizing only those
allowed fields, the complete maps are equal, including all source/editable
inputs, identities, roles, densities, selections, recipes, derived outputs,
rebuild commands and the shared-input index. The true consumer set is unchanged.
The map still describes declared contracts, not exhaustive level coverage.

All 8,841 other baseline tracked files were independently compared by SHA256
and mode with the frozen checkpoint: no difference. This includes all PNG/HDA
assets, authoring inputs, C/runtime code, historical oracles and the prior
performance proof implementation. Source inventory verification remains 274;
runtime manifest remains 1,029 files and registry remains 120 entries.

Reproducible focused command:

```sh
python3 -B -m unittest discover -s tests -p test_shared_asset_authoring_map.py -v
```

The suite covers strict real-map construction, Front/P7/Lobes ownership,
all-current consumer uniqueness, exact-dictionary negative cases, preservation
of same-path distinct evidence/role/scope, frozen NEWSHF 168, strict missing and
corrupt Orb inputs, deterministic CLI and absence of tracked-tree writes.
Additional strict CLI checks cover P7 identity 1310294 and unknown identity
99999999 (exit 1, diagnostic only, no JSON output).

The five current Rear integration `test_current_preview_and_master_map` cases
exercise current preview count 232 and their historical-family boundaries.
The unchanged older Mint27/Missile integration files expect historical preview
counts 183/186 and are not run as current-tree tests; their live map contracts
remain strictly loaded in the aggregate map suite and unchanged in the full
before/after comparison.

No full 54 historical projection rerun or native rendering run is claimed for
this metadata-only change. The map is a leaf navigation tool, not imported by
runtime or projection proof modules; its existing CLI and map-facing integration
callers are the applicable surface. The preceding performance checkpoint's
full 54 evidence remains separate, intact and does not stand in for these tests.

## Recorded result

- Authoring-map suite: **23 PASS**, 77.745 seconds.
- Current Rear map/preview integration: **5 PASS** (P7,39,1,281,Lobes).
- Before/after exact metadata-only comparison, valid/invalid CLI checks,
  unchanged-file byte/mode inventory and `git diff --check`: **PASS**.
- Independent review also verified actual map deltas and full-dictionary
  consumer validation. No runtime behavior or visual change is claimed.

An initial development test run failed two newly written note-count assertions
because they omitted the two existing generic workflow disclaimers. The tests
were corrected to preserve those disclaimers; the final 23-test run above is
against the unchanged production patch and corrected tests.
