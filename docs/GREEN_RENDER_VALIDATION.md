# Green projectile and smoke integration

Status: final parent visual review passed on native4×/2× actual-engine contacts,2026-10-11. Complete214–217 diffuse energy head cycle, v2 smoke and scoped brightness interpolation and head-over-green-smoke compositing are selected. Native Windows and full-level acceptance remain pending.

## Verified mapping correction

The original green heads are spriteSheet8 IDs **214–217**, a four-frame pulse, not a static214 sprite. Reading the legal Tyrian2000 data at the correct 80-byte weapon-record stride gives both weapon71 and1071 `weapani=3`, eight `del=8` values, eight base214 values and trail12. Thus `shotAniMax=weapani+1=4`. Actual weapon71 material logs show214,215,216,217 on ticks90–93, repeating94–97. The prior static214 handoff/preflight mapping was incorrect. The diagnostic fixture calls the original weapon creation function; no animation, TTL, physics, collision or RNG override was added.

All four frames are12×14 logical,8× RGBA,anchor0,0. The normal draw remains shotX+1,shotY. Separate shadows stay on the original indexed path at the original shotY+shadowYDist. Original source frame occupancy is(0,1)–(11,12) for all four. See `assets/hd/green-head-mapping.json`; original game data/reference PNGs remain outside Git.

## Smoke cause and bounded fix

Green v2 art remains unchanged for newsh6 IDs78–84. The original HD blend averages authored source peak with the underlying destination peak, preserves source RGB ratios, then applies authored alpha for coverage. Point-sampled indexed scenery therefore imprints logical8×8 brightness blocks even into opaque smoke. A different texture alone does not remove that cause.

Only mapped HD green78–84 in the original blend path now use bilinear interpolation of the indexed scenery's **brightness term**. Before each draw, a14×16 logical center-sample snapshot records the12×14 tile and one-pixel halo. This avoids scan-order feedback from the current smoke writing into the live canvas. Existing HD destinations keep their exact original operator. HD-owned or outside neighbor taps use the current destination value, so adjacent HD objects are not blurred into scenery. Source hue, source alpha, blend switch, classic fallback, all other effect families and the background outside smoke remain unchanged. No full-frame blur or global opacity change.

The earlier unapplied live-canvas patch under `prototype/experiments/green-background` is historical WIP, not the selected implementation.

## Earlier interpolation and art-stage checks (before foreground-head layering)

- C99/Linux build with the existing SDL toolchain passed. Existing misleading-indentation warnings remain; no new compiler warning in the green helpers.
- The actual helpers, extracted from current production source, passed346,480 independent bilinear-oracle, clipped-edge, neighboring-HD and immutable-snapshot checks at densities4/8 under ASan/UBSan. Leak checking is disabled under this environment's ptrace.
- Original point versus smoothing:116 identical state/collision/indexed-output ticks;64 original spawns and448 smoke draws, all7 IDs and original TTL. Actual4× window captures cover90–115. Every RGB difference is confined to a currently drawn green tile. Last smoke draw103; zero differences104–115.
- Across448 actual command snapshots,1,174,022 existing-HD pixels exactly match the unchanged peak-average equation;2,974,528 transparent pixels are untouched.
- Actual processor1 nonblend point/smoothing windows and state logs are identical. Classic, missing81, missing head, repeat presentation and real2× window runs preserve logical/collision/RNG logs, with zero coverage/restoration mismatch. Missing81 produces384 HD smoke draws and64 original fallbacks; classic produces no HD draws.
- Current renderer versus pre-change production in the natural blue/shield window:220 ticks, byte-identical state, indexed output, RGB audit, collision and draw traces.
- Genuine dot-cloud desktop window reached the paused green scene at tick90; keyboard resume completed116 ticks and exited0. Desktop screenshot retained outside Git. This is Linux graphical verification, not native Windows acceptance.

The initial head214-only proof exposed the missing215–217 coverage and was superseded. Final complete-cycle checks:

- All64 normal head draws use HD art,16 draws per ID214–217. All64 shadows use the original indexed path. Every draw matches original shotX+1,shotY and original shadow delta10 in this fixture.
- Complete4×,2×,point baseline,classic,missing216 and repeat runs all finish116 ticks with exact original state/collision/indexed logs and zero RNG/coverage/restoration errors. Missing216 yields48 HD draws plus16 original fallbacks; classic yields0 HD head draws.
- Final8-tick point/smooth window comparison remains confined to green tiles.1,222,368 existing-HD overlap pixels match the original equation;1,575,296 transparent pixels are unchanged. Final clear104–115 RGB audits exactly match the prior full-capture clear proof.
- Final genuine cloud desktop scene paused at92 with the complete-cycle art, resumed by keyboard, exited0 at116. Native contacts show a coherent smooth pulse; dense overlaps retain volumetric puff texture and are not a flat glow.
-18 stage packs /2620 exact HDR entries /201 formal PNG sources verified and independently rebuilt. Defaults contain190 preview /194 debug entries. Four formal head PNGs regenerate byte-for-byte from the selected generated atlas with one shared transform. See `prototype/build-green-head-art.py` and `assets/hd/artwork/green-head-energy-v4/identity.json`. Rejected art and original game reference images are excluded.

## Reproduction

1. Optionally reproduce head art into a new directory: `python prototype/build-green-head-art.py --output ../green-art-check`. Verify assets: `python prototype/build-hd-assets.py`.
2. Run strict fixture/hash tests: `python prototype/fixtures/test-prepare-effects.py`.
3. Run helper oracle: `python prototype/fixtures/test-green-background.py --sanitize` (GCC/Clang sanitizer support required; omit flag for plain C99).
4. Prepare a fresh sibling fixture: `python prototype/fixtures/prepare-green-review.py --output ../green-review`.
5. Build the fixture with its Makefile on Linux or `prototype/build-game.ps1` on Windows. Supply legal original data separately.
6. In a fresh run/config directory set `OT_FX_FIXTURE=1`, `OT_FX_PROBE=1`. Use4x or2x Integer scaling. Run with `--data=<legal-data> --no-sound --no-joystick --no-xmas --asset-debug=custom --asset-debug-tick=90 --asset-debug-running --render-ticks=116 --render-assets=<manifest-default-debug-pack> --render-test=local --asset-debug-explosion-log --asset-debug-capture --asset-debug-window-only --asset-debug-capture-start=90 --asset-debug-capture-count=26`.
7. The private-only `OT_GREEN_POINT_BASELINE=1` selects the original point brightness for the paired run. It does not exist in production. Preserve decoded-pixel-verified PNG versions of captures. `verify-green-review.py --baseline <point-run> --candidate <smooth-run> --assets <pack>` checks state, scope and HD overlap equations with Pillow/NumPy.

Windows launchers use the new complete-head stage by default. `-BeforeGreenHead` selects the unchanged prior green-v2 asset pack; `-BeforeGreenV2` and earlier rollback stages remain available. Asset rollback alone does not roll back the renderer; use the prior Git commit to reproduce the old point operator exactly.

## Limits

Acceptance is finite-scene only. No native Windows/GPU/fullscreen/controller/audio, arbitrary map/palette, full-level stability or physical FPS acceptance is implied. Original game media, captures, executables, SDKs and credentials are not Git artifacts. Keep bounded captures: warn at5GB, stop before10GB, retain at least4GiB free; no automatic permanent cleanup of user evidence.

## Superseded plasma art review

The glossy sphere was rejected as stylistically inconsistent with the smoke. The superseded v3 art had a direction-neutral green energy core, broad folds and a softer perimeter, with no glass-like point highlight or baked directional tail. Both four-frame cycles remain engine-driven; all four share one calibrated atlas transform. Renderer source is byte-identical to the tested sphere-stage implementation. No extra stage packs were added: the two unpublished head stages were replaced, with the sphere retained in local rollback Git history.

Bounded final plasma runs: native4× captures90–97, native2× captures90–93, missing216 and repeat runs all finish116 ticks. Each complete run has64 HD normal heads (16 per ID) and64 original indexed shadows, exact shot origins and original state/collision/RNG. Missing216 yields48 HD heads plus16 original fallbacks. Clear104–115 RGB hashes exactly match the retained full-cycle clear proof. The extensive point/nonblend/overlap matrix above validates the unchanged renderer before this art-only replacement; it is not presented as a second full matrix using plasma art. Actual native contacts and the8-tick loop passed parent visual review. Dense overlapping trail puffs remain textured.

## V4 diffuse energy art, before the layer correction

The user requested removal of a perceptible spherical shell. The final v4 head uses a cohesive luminous core and diffuse halo, without a hard circular rim. Geometry, four original IDs, timing, source8× density, anchor0,0, all original draw origins, separate indexed shadows and the renderer are unchanged. All four frames use one shared atlas-grid formula; generated PNGs rebuild byte-for-byte. Existing two head stages were replaced, not multiplied.

Final bounded runs at4×/2×, repeat presentation and missing216 finish116 ticks with64 normal draws,64 original shadows,16 normal draws per ID, exact original gameplay/collision/indexed/RNG logs and zero coverage/restoration mismatch. Complete runs have64 HD heads; missing216 has48 HD plus16 original fallbacks. Final clear104–115 RGB hashes match the retained full-cycle clear evidence.

Native final-window contacts/cycles show no hard rim or phase/reset jump. A separate private read-only first-head capture before the trail overlays it confirms a readable luminous core at point4×/2×. This pre-trail diagnostic is explicitly not a final-gameplay screenshot, and its temporary hook is not included in production or this repository. The unchanged final windows are shown alongside it. **Dense original foreground smoke obscures much of the core**; this is a documented draw-order/readability limit, not a claim that all gameplay readability is solved. No trail alpha, draw-order, physics or animation change was made to conceal that overlap.

## Selected head-over-green-smoke presentation

The user then requested keeping the luminous core above its smoke instead of enlarging it. The same v4 art and geometry are retained. Successful HD normal heads214–217 record a bounded ordered display layer and the exact head-free RGB/ownership underneath each covered subpixel. Only green78–84 smoke updates that underlay, using its original NORMAL or BLEND operator; the overlapping heads are recomposed once in original order. This avoids accumulating alpha or brightness. Green interpolation samples head-free scenery/ownership. Suppressed original smoke coverage advances saved ownership even at authored alpha-zero edges.

Every unrelated HD/ indexed/brightness/shadow/restoration write bakes and invalidates protection at its actual affected pixels. There is no frame-end foreground redraw, so unrelated later foreground/UI is not lifted behind the heads. Conservative invalidation may leave a head behind smoke after another effect has touched that pixel. Classic, missing-head and missing-smoke paths retain their original fallback. No original indexed draw, shadow, gameplay, position, collision, TTL or RNG change is made.

Final bounded layer checks:
- Actual native4× ticks90–97 and2×90–93 expose the bright cores with a diffuse edge; both pulse cycles and reset remain coherent.
- Complete4×/2×, missing216 and repeat runs finish116 ticks with64 normal heads,64 original shadows,16 draws per ID, exact original state/collision/indexed/RNG and zero coverage/restoration errors. Missing216 yields48 HD and16 original heads. Clear104–115 RGB hashes match retained full-capture evidence.
- Classic, missing81 and original processor1 nonblend runs also finish116 ticks with matching respective baseline logic and no coverage errors.
- Actual production helpers pass1,935,360 independent ordered-compositing pixel comparisons at densities2/4/8 under ASan/UBSan. Coverage includes multiple overlapping heads, alpha-zero/partial edges, mixed densities, clipping, foreground invalidation, indexed/brightness writes, classic restoration, suppressed ownership and restart indices. Four deliberate mutation checks detect double composition, incorrect replay start, missing foreground invalidation and missing smoke-owner stamps.
- The original background oracle still passes346,480 checks. Asset verification and all8 strict fixture-hash portability tests pass.
- A genuine cloud desktop window is inspected paused at92 and resumed by keyboard to116, exit0. Dense smoke remains volumetric/mottled; arbitrary full-level/native Windows/GPU acceptance is still pending.

Run the new focused test with `python prototype/fixtures/test-green-head-layer.py --sanitize`. The paired-window verifier excludes head footprints from its old visible-destination blend oracle; those pixels use the separately verified head-free-underlay composition. Historical numeric overlap counts above describe the earlier interpolation stage, not unchanged final head pixels.
