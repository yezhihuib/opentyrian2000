# Independent pre-game font review

Reviewed 2026-10-13 UTC. Source/core and the frozen collection fixture pass. Native visual acceptance remains a separate gate.

## Identity and result

- Base: `317bf551db59df9c4e3754d2072446c7313ab1f4`
- Candidate: `bf301cb37d0fe619f1ca7bf90c23f8e3580874e7`
- Candidate core SHA-256: `a7324959d2a89f6f1858c3592d55f11c526b6ba3bc46367ee61cf879f8f8022e`
- Result: PASS for the scoped source/core boundary. The candidate was clean before and after independent checks. No game process was launched, no production source was edited, and nothing was published by this review.

## Independently rerun checks

The dependency environment was sourced from the existing recovery environment. Original data remained external/read-only. The accepted `startup-title-settings-v1` resources were unchanged.

1. `git -c core.whitespace=cr-at-eol diff 317bf551db59df9c4e3754d2072446c7313ab1f4 --check`: passed. The explicit setting respects the pre-existing CRLF palette source.
2. `python3 tests/test_pregame_font_integration.py`: passed. Eleven prior files reverse exactly to published base bytes, 33 unrelated mutations reject, 7,344 prior files and 691,873,108 asset bytes remain unchanged.
3. `python3 tests/test_selector_font_integration.py`: passed with the finite pre-game projection preserving earlier assertions.
4. `ASAN_OPTIONS=detect_leaks=0 bash tests/run_pregame_font_tests.sh --sanitize "$TYRIAN_DATA" assets/hd/packs/startup-title-settings-v1`: passed, 78 states and 9,327,126 checks. The source fixture checks zero live owned allocations independently. LeakSanitizer is excluded because this executor's traced setup fails its own exit handling; this is not a LeakSanitizer pass.

Measured core records: static 745,352 bytes; peak owned payload/output 5,881,856 bytes; shared sampler static 32,832 bytes. These are bounded source/core records, not a native process RSS or performance measurement.

Implementer-provided existing Settings/Load/selector core, manual/Data source-unit and default network build results were inspected in the candidate's documentation; they were not all independently repeated here.

## Source findings

- Admission is limited to contexts 0/1 and excludes two-player, arcade, network, SuperTyrian, super-arcade, timed battle, and constant-play modes. Selection and row bounds are explicit.
- The raw PIC1 restore and runtime palette 0 have their own fingerprints. Accepted SFN1 palette-7 provenance remains unchanged. Acquisition accepts a full PIC1 current palette or the all-black Help-return state; arbitrary palettes reject.
- Header/rows/help use bounded loaded source strings, with exact original row, selection and help-index maps. Cash remains the source decimal value.
- Font replay preserves per-glyph destination-dark then unsafe-face order, original selected brightness toggles, indexed halving and unsafe OR/overflow semantics. Tiny DARKEN face/shadow coordinates include both original shifts.
- Authenticated cubes, bars, ship/equipment and sidekick writes retain original ordering and their indexed result. All observed later writes erase authored support, including same-index writes. Unknown writers or incomplete primitive sequences fail classic.
- Original rendering, menu actions, input, sound dispatch, items, cash and save operations reverse byte-exactly to base after removing only reviewed observer additions. No item/purchase screen is admitted.
- Idle/cursor work does not append commands. Cursor erase checks restore the exact validated frame. F1's original outgoing ten-step fade is retained before release, and fresh PIC1 acquisition handles Help return. Other actions end the lease first.
- Output uses unchanged `selector_font_output`; there is no added output-size whitelist. Title, Settings, Load and selector implementations remain exact. Inactive pre-game teardown does not release their shared sampler. MSVC inventory includes the new source/header once; Windows build/runtime remain unverified.

Early review findings about timed-battle admission, palette acquisition, inactive shared-sampler release, and old test-runner links were corrected before this freeze.

## Native matrix review

The seven-process / 40-capture plan is acceptable in scope: exact published-base pairs, isolated fresh profiles, 2x/4x/odd geometry, missing-tiny fallback, a finite seven-key route ending root 0:4, and no item activation. Normal backup writes must remain confined to those synthetic profiles.

The following collection conditions were checked against the frozen fixture in the addendum below:

- Review the frozen private controller, read-only telemetry, manifest and negative size/extent tests against each exact ELF. Use the successful mapped same-process reader, never old symbol addresses or the failed cross-process revision.
- Startup capture suppression must be mandatory in the new wrapper to keep the total at 40. The original shared route defaults must remain equivalent.
- Strengthen live gates with the same cached natural presentation's context/selection/palette/cash/items, and fail immediately on unexpected post-root state. An unrelated newer observation cannot validate an earlier capture.
- Review the independent oracle built from actual bounded strings, original assets and call order. The old selector whole-string shadow oracle cannot substitute for the new per-glyph and overdraw contract.
- Retain exact output geometry/sampler state and endpoint screenshots; no odd-output or endpoint substitution.
- Obtain the parent's serialized runtime-slot release. Collection review does not itself release that slot.

## Evidence limits

The core's real cube/authored overlap uses a longer bounded synthetic source string. Its explicit same-index occlusion case is a private primitive fixture at authored support; it is not evidence that natural native cube artwork produced a same-index overlap. Native capture/oracle evidence must identify its actual coverage.

No native visual, physical input, native auditory, hardware/DPI, Windows/MSVC runtime, fullscreen, performance or resize-during-fade claim follows from this review.

## Collection-safety addendum, 19:27 UTC

PASS for the private collection fixture at `/workspace/scratch/f67dd347fa0a/pregame-native-acceptance-bf301cb-20261013`:

- `frozen/identities.json` SHA-256: `c9e5909a44e5d2349b0af76d9c29869df3b1e95ea90b005b6a6862670eac5f30`
- `frozen/pregame-private.diff` SHA-256: `3ab713cfb0930b69164d2c13bf6dc2debb70e13e706d13d6010e3639fa58a02e`
- Baseline ELF SHA-256: `f2436b62f7c2d1405a4de9281dc980cca432dad8a85df89d41814676373f22d8`
- Candidate ELF SHA-256: `6ec5b6eada924cf99ec2a68ed7c5a16873277ceed8545a8ad3e43fe4115be838`

Independently passed eight pre-game route tests, six unchanged shared-route tests, fifteen transport static tests including all added object-width negative cases, the standalone mapped-reader boundary tests, and all seven preflight-only invocations. Every entry of the final identities file was checked, and the remaining pure collector/constants dependencies match their frozen successful originals. The identities/diff hashes stayed unchanged across these checks. No game was launched.

The new transport only reads authenticated source-owned objects, caches menu/equipment/text alongside natural pre-Present pixels, and queries the existing texture sampler. No production callbacks, gameplay writes, pixel injection, pointer replacement or alternative rendering path were added. The successful mapped reader and input/capture contract are retained.

Controller review findings were corrected before this freeze: mandatory startup capture suppression; transition-only selection admission; retained root/category and unused selection/menu-choice checks; live/cached frame agreement; compatible newer natural presentations without a scheduling-coincidence requirement; cached pixel-validity checks; explicit transport mode verification; named equipment decoding; separate rendered-pixel hashes; and frozen original/startup/manual input identities.

This clears collection safety for the exact seven serial processes and forty captures, subject to the parent's runtime-slot release. Offline independent image reconstruction, source/palette/state pair comparisons, missing-tiny equality and direct visual review still gate final acceptance and publication. Do not treat a completed collection as those proofs.

## R4 startup failure and bounded repair, 19:34 UTC

R1/R2/R3 collection subsequently passed according to their retained receipts. R4 stopped with zero captures before any selector or pre-game presentation. Independent retained-log inspection found the reused startup gate accepted title sample59/frame109 while the target palette hash was `d3ca5814ae4cd625` and the actual palette was still `791beab0ab51c840`, despite the stack hint reporting `in_fade=0`. The Return event occurred at5535ms and released at5660ms; the full title palette was first observed at6207ms. The original title's logo animation and partial fades explain this state. Its later `service_SDL_events(true)` clears pre-menu new input, and its original30-second idle branch entered demo.1. The first recorded `demo=1` was36376ms, followed by the controller's normal quit. This is an initial readiness race, with no acquisition of the new pre-game lease. See `R4-startup-diagnosis.json` for exact retained receipts and file hashes.

The smallest private repair passes review: it marks pre-A observations unready until they agree with a complete same-frame natural presentation with valid indexed/RGB data and a full current palette equal to target colors. An existing true fade hint remains restrictive. The shared route, transport, production code, keys and deadlines are unchanged. Exactly one `R4_retry` alias copies the original1280×800/four-capture configuration into a fresh directory.

- Revised identities SHA-256: `ab6270863594116f74db912d7251a0bab71f5cc8fb3374b2c2f18bb0e17e0056`
- Repair diff SHA-256: `7ed58084836976723c168c337186714c668a7f59615e4cb79f6dd76ca4486d81`
- Independently rerun: ten pure route tests including the original gate withholding Return through a partial palette; R4_retry preflight; all revised identity hashes.
- Failed-R4 result, transport log, stdout/stderr and execution log remain byte-exact to the independent diagnostic hashes. Earlier passing captures are retained.

Collection safety is cleared for that single same-case retry after parent runtime-slot release. This is not permission for broader retries, longer deadlines, additional capture cases or publication. Native visual acceptance remains pending.

## Final native numeric and visual receipt, 19:44 UTC

**PASS for the bounded pre-game text-only candidate.** Production and unit source remain unchanged at `bf301cb37d0fe619f1ca7bf90c23f8e3580874e7`; only the worker's new acceptance documentation was untracked at final status check. Seven intended cases completed in eight starts, retaining the failed R4 with zero captures and one reviewed R4_retry. There are exactly forty retained captures. This reviewer launched no games or new captures.

Final pins independently checked:

- Oracle `verify_pregame_captures.py`: `7d7dd29b18c6e3d8fdcd77c4ee4312fc58d21fe17631514c04e31b72142ca112`
- Oracle pure tests: `39b9851eae118768a598659c2b51d65dd80add70c281424c1a3e1e279f92b192`
- Collection identities: `ab6270863594116f74db912d7251a0bab71f5cc8fb3374b2c2f18bb0e17e0056`
- Native evidence inventory: `ef49bca33bec566128db69fe63d7d1c464a141a653e222a1a4762924b54274a5` (all 306 entries verified for bytes and SHA-256).

The oracle was source-reviewed and rerun independently, including all seven cases, three baseline/candidate pairs, missing-tiny fallback and five pure tests. It reconstructs original PIC1, original sprite/font banks, encrypted source text and serialized item data, plus the already accepted SFN1 alpha/role data. It does not import production pregame-font code or use captured production command/event buffers. Original per-glyph shadow then unsafe-face order, tiny double +1 shifts, selected brightness, bars, cube sprites and ship/equipment ordering match the unchanged source operations. Source-loaded text is checked against independently decoded original strings, rather than accepted from capture telemetry.

All 2,560,000 indexed pixels and all 22,711,640 complete RGB pixels match exactly. This includes backgrounds, ship/equipment, cubes, bars and odd-output black sidebars; there are no tolerance thresholds, ignored pixels or region exclusions. All RGB changes between matching baseline/candidate captures lie within original/authored font support (zero outside). Actual odd output is 1365×767 with a 1022×767 scene at x=171. The independent classic raster/nearest expansion qualifies the SDL software 16.16 sampling phase before the enhanced underlay uses it.

The earlier separable-footprint result is retained and rejected, not hidden. This reviewer reproduced its 49 one-channel-level disagreements on odd C, then separately evaluated every disagreement by scalar row-major footprint accumulation: all 49 exactly match the retained native image. That order agrees with the unchanged approved sampler's C double accumulation and floor(value+0.5) contract. No production fix or relaxed comparison was used.

Additional independent checks (`verify_final_evidence.py`, `final-evidence-receipt.json`, `final-inventory-check.json`, `final-native-event-receipt.json`):

- All 200 capture artifacts have the recorded sizes/hashes; BMP and PNG decoded RGB are identical.
- Every captured colors/current palette is the full original PIC1 palette0, including exact packed RGB layout and untouched zero initial-palette buffer. SFN1 provenance is not substituted as the runtime palette.
- Baseline/candidate original source/state/palette/indexed sequences agree after only collapsing repeated idle states; every naturally observed per-selection RGB hash is stable.
- Every successful run has exactly the expected twelve synthetic keydowns and matched keyups, all SDL_PushEvent receipts return 1, and non-key event receipts are only focus gain and final quit. The seven post-root actions never activate a purchasing category or gameplay.
- Cash stays 10000 and equipment stays byte/field-identical; current, last and old equipment dictionaries agree with their raw source fields. Only the synthetic profile's expected opentyrian.cfg exists in profile/home/cwd; no save file was produced.
- Both idle holds meet the original ≥1 second/≥8 new-frame bounds. C/H, C/F, E/G and retained idle images are byte-identical wherever present, confirming clean category return/re-entry and stable selection restoration.
- Missing only settings-font-tiny-v1.hda makes all four R7 images/indices/palettes byte-identical to baseline R1. Every remaining startup file hashes identically to its original; all three preceding selector settled indexed/palette/RGB signatures remain equal to candidate R2.
- The original failed-R4 result, transport/stdout/stderr and execution log still match the independently recorded failure hashes.

Direct retained-still inspection: R2 C/D/E/H (2× root, category, selected Done and root return); R4_retry D/E (true 4× category/Done); R6 C/E (odd root/category); R7 D (classic missing-tiny fallback). Text is legible, correctly highlighted, positioned and shadowed; no clipping, stale selection remnants or disturbed non-font artwork was visible. Image identity checks independently cover the other retained returns/idle captures.

Qualification: this is native Linux source execution with synthetic SDL input and software/dummy output, not physical keyboard, hardware GPU/DPI, auditory, fullscreen or Windows runtime evidence. No purchase was made. Natural strings in this matrix do not overlap cube artwork, so positive same-index authored-overdraw coverage remains the explicitly synthetic core/oracle fixture. F1 fades/reacquisition remain source/core-test coverage, not a newly claimed native route. Existing title/settings/load/selector regression conclusions remain those established by the unchanged-source projection and previous suites; this matrix does not expand the admitted font scope beyond ordinary single-player root/category text.

The source, numeric and direct visual gates pass for this scope. Publication remains the parent's separate decision.
