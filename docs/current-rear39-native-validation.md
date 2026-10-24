# Rear39 independent finite native validation — PASS

Baseline: frozen local P7 parent `019c92a1547726807eacf93673983e91cd2ca7a6`; source root `current-rear39-authoring-worktree`. No source-root writes, production code edits, eligibility changes, uploads, or user-computer commands were made.

## Verified scope

- Every production `src/` file, including current combined header and frozen source/bank/record pins, was byte-exact to the parent. SHA inventory: `source-and-payload-scope.json`.
- Independently generated real JSON path edit `11 5.25` → `10.9 5.25`: exactly six real HDA changed (39/40/41 × d4/d8); all four P7 files remained unchanged.
- Additional real P7 SVG path edit `Q8.9 1 9 1` → `Q8.8 1 8.9 1`: all four P7 files changed. Both-family variant changed exactly ten of the 48 installed HDA files.
- Production combined pin header changed only Rear39 cells 0/1,12/13,26/27, then additionally P7 cells34–37. All other supported and unsupported pin cells remained frozen.
- The additional native cache helper exercises exactly ten Rear39 record/phase consumers and ten P7 consumers, each at d4/d8. Rear39 consumers match the separate actual `phase_ok` audit (528 queries): raw39 records254/255/261/272/274, raw40 records256/275, raw41 records258/259/262.

## Completed runs

All seven configurations compiled and ran plain plus ASan/UBSan successfully:

| Configuration | Full actual-payload shadow checks per mode | Additional byte/cache/birth checks per mode |
|---|---:|---:|
| Bootstrap | 1,470,254 | 1,081,564 |
| True edited Rear39 | 1,470,254 | 1,081,564 |
| True edited Rear39 + P7 | 1,470,254 | 1,081,564 |
| Edited Rear39 HDA / old header | Not valid configuration | 564 rejection checks |
| Old Rear39 HDA / edited header | Not valid configuration | 564 rejection checks |
| Both-edited HDA / Rear39-only header | Not valid configuration | 564 P7 rejection checks |
| Rear39-only HDA / both-edited header | Not valid configuration | 564 P7 rejection checks |

The first generation also executed unchanged historical synthetic adapter plain/sanitized:17,080,056 checks each; pending-art controls983 and1,123 each; synthetic shadow1,470,254 each. Actual HDA negative fixtures are regenerated from actual bytes, rather than using the old synthetic payloads.

Extra helper compares every loaded RGBA byte to the selected HDA disk bytes, verifies exact role131 identity, cold versus warm file opens and cache behavior, fail-closed cold invalidation after backing-byte changes, successful reload only after reset, valid Hard normal versus rejected Hard shadow, d4 shadow rejection versus d8 lease preparation, shared alpha pointer and birth/reset invalidation. Original shadow suite covers all22 roles,103 phases,80 slots and96 negative families. Frozen helper includes remain unchanged. A forged fixture-source hash was rejected before reuse.

## Honest limitations

Bank data and weapon records are synthetic. Normal draw is a test observer; shadow checks preparation, current/birth lease and actual alpha resources, not compositor pixels. No actual gameplay firing, original-data admission, Windows/GPU execution or campaign playthrough is established. Sixteen pre-existing unrelated observer hooks are neutralized only through the inherited external finite shim. No Rear observer, eligibility/source/record pin, or production branch was stubbed or widened.

## Reproduction and diagnostics

Reusable runner, helper and minimal-source variant derivation are in `runner/`; usage is in its README. `native-summary-receipt.json` binds all seven result receipts, actual48-HDA hashes, source/runner/helper hashes and log hashes. Original fixture generation is retained under `bootstrap/`; successful actual baseline is `bootstrap-fixed/`.

One initial external runner compile failed because a local variable named `src` was overwritten by an HDA path while building malformed fixtures. Renaming it `source_copy` fixed the runner; both plain and sanitized actual suites were rerun successfully. That diagnostic and fixture-only receipt remain preserved and are not represented as an actual PASS. One initial variant derivation passed integers instead of the API-required16-digit hexadecimal pins; fixed to exact strings before all tested variants, with initial diagnostic inputs retained separately.

Footprint about604 MiB, predominantly one synthetic historical fixture tree. Subsequent runs reused hash-verified fixture code/bank/records; no full-repository duplicate clone was created.
