# Windows handoff to dot

Latest cloud milestone and current Windows acceptance command: [FIRST30_HD_COVERAGE.md](FIRST30_HD_COVERAGE.md). The remainder below is historical, including its old counts and WIP claims.

This is the historical eaebe318 handoff. Current cloud integration and corrected214–217 mapping are documented in [GREEN_RENDER_VALIDATION.md](GREEN_RENDER_VALIDATION.md). Use `prepare-green-review.py` for the current renderer; `prepare-effects.py` intentionally reproduces the archived historical fixture.

The laptop stops mainline development after publishing this handoff. Dot owns the remaining green projectile/smoke work in the complete cloud checkout. Future laptop work requires a supplied commit for Windows acceptance or an explicitly independent task. No new A/B/test was run after the stop instruction.

Current production uses green trail v2 (IDs78–84) with ORIGINAL point sampling, peak-value blend,12×14logical size,8x RGBA andanchor0,0. No extra+22offset. v1 remains unchanged; `-BeforeGreenV2` selects it, and `-BeforeGreenTrail` selects the pre-green shield stage. Renderer SHA256 fc53fad690a361ac2c3316bacc8258f1ed16f72054c9955776334939b1912a1f; last production Windows EXE SHA256 d2913de9a7beaa0f18179ec12f702f62e70c91616232a10c3255a711f3f387a0. EXE is a local build output, not a Git artifact.

White and shield are parent visually accepted within docs/EFFECTS_ACCEPTANCE.md limits. Green v1 and v2 are WIP: v1 has the original finite normal/nonblend/missing81/classic/repeat/real2x/clear checks; v2 has art-only actual normal/nonblend/real2x26frames each,64 spawns / 448 draws, original gameplay/input/collision/RNG/indexed logs unchanged, all RGB differences inside current smoke footprints,103 last draw and104–115clear. V2 missing81/classic/repeat were not rerun. Parent green visual acceptance, other weapons/maps/palettes/full-level/FPS remain unverified.

At tick90call0 the pre-smoke canvas is exact8xexpanded indexed RGB (HDowner 0). The unchanged HSV-value average carries its brightness blocks into even opaque smoke pixels. Source8x RGBA loads correctly. Actual processor1 has a different underlying image too, so the original diagnostic additionally labels a same-input nonblend FORMULA REPLAY; it is not called a native screenshot.

The interpolation B candidate in prototype/experiments/green-background is UNAPPLIED WIP: source patch and a private halo observer were prepared; private Windows build succeeded. No B runtime/A/B/visual result exists. B would interpolate only original-background peak under mapped green78–84whenowner 0, leave existing HD/background alpha and original hue/valueaverage unchanged. Do not treat it as selected or passed.

Projectile spriteSheet8/214 is still unmapped. CORRECTION: Original weapons71 and1071 use base214 but loaded weapani3, hence the four-frame214–217 pulse; the earlier static214 claim was incorrect. Geometry is12×14logical,anchor0,0, draw shotX+1,shotY and separate original shadow. Screenshot alone cannot distinguish71from1071. Dot has original-frame/mapping evidence and is creating replacement art. Nothing new was bound for214.

Tracked formal resources are197 PNG sources and2236 exact HDR entries in16 stage packs; current debug/preview counts190/186. Main engine/build/launcher/index files are tracked. Original data at siblingruntime-data/tyrian2000, local SDL SDKs at siblingproject-deps, EXE/DLL/PDB/build products, run captures/videos and rollback ZIPs remain external. Exact tested private fixture source overrides and hashes are tracked; the newly exported preparation command was not executed during handoff. HISTORICAL_PROTOTYPE_AUDIT.jsonlists64retained untracked files individually, their hashes/dependencies and reasons. No active tracked build/runtime dependency on those64was found. Their old local evidence dependencies are not advertised as portable. The prior screenshot/recycle discrepancy remains unverified; nothing was deleted or placed into recycle.

Windows future acceptance commands (not executed after stop):
```powershell
& .\prototype\build-game.ps1
& 'C:\Program Files\Python311\python.exe' .\prototype\build-hd-assets.py
& .\prototype\start-asset-debug.ps1 -Preset blue -Tick 194 -Until 275 -Running -Capture -CaptureStart 194 -CaptureCount 9 -WindowOnly -ExplosionLog
```
The last command checks the natural shield window using production code; it does not inject the green weapon. For the original71 green fixture:
```powershell
& 'C:\Program Files\Python311\python.exe' .\prototype\fixtures\prepare-effects.py --family green-trail --output ..\green-fixture
& ..\green-fixture\prototype\build-game.ps1
# Use a fresh run directory with the same4x/Integer config, and legal data separately.
$env:OT_FX_FIXTURE='1'; $env:OT_FX_PROBE='1'
# Run the prepared fixture EXE from that fresh directory with:
# --data=<legal-data> --no-sound --no-joystick --no-xmas --asset-debug=custom
# --asset-debug-tick=90 --asset-debug-running --render-ticks=116
# --render-assets=<repo>/assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-test
# --render-test=local --asset-debug-explosion-log --asset-debug-capture
# --asset-debug-window-only --asset-debug-capture-start=90 --asset-debug-capture-count=26
Remove-Item Env:OT_FX_FIXTURE,Env:OT_FX_PROBE -ErrorAction SilentlyContinue
```

Existing Library IDs only; do not duplicate archives:
- V1board libfile_86544cb18a9c819197c49706d4501dfe,12.2s video libfile_15485d572e008191bb6787c558cca06e,218KB evidence libfile_f84ec05cbf088191943b756ec8d40d27.
- Same-frame blend diagnostic libfile_6048d764b5388191a939b97c49a0dc2b.
- V2actual42crop board libfile_aaed7270a1d88191a85151cb90d30232,9.15s A/B video libfile_b4c105c9e4b08191b1077b50110de8b4.
-214full original frame libfile_e0e9749b6cd481918264d5e262222405; mapping ZIP libfile_03f143291a4481918b078086676dee40.

Local rollback checkpoints in the recorded task/checkpoints directory: before-white-smoke-v1-after-git-resources, before-shield-v1-after-white-smoke, before-green-trail-v1-after-shield, before-green-trail-v2-after-v1. They are not Git-required cloud dependencies. Original prior Talon/blue/filters/turret/foundation/type10/death approvals,5frame/classic/missing compatibility and paused109/107/120 remain preserved.


## Purple installation / Layer3 foundation batch

See [PURPLE_INSTALLATION_VALIDATION.md](PURPLE_INSTALLATION_VALIDATION.md) for exact identities, reproduction and bounded cloud acceptance. Adds13 persistent terrain tiles and9 independent components; final gray fringe correction is accepted. Current packs316/320, canonicalPNG328, totalHDA2872. Windows native2×/4× acceptance remains pending; use the existing local fixture commands and current manifest defaults.


## 60–75 second bounded closure and cloud64

See [WINDOW60_75_VALIDATION.md](WINDOW60_75_VALIDATION.md). The final522-frame private-survival window has103 visible material identities with zero mapping gaps. Cloud64 lower-edge brightness/contour is corrected with14 cloud peers unchanged; production code is unchanged. Current packs316/320 and all18pack verification pass. Windows acceptance remains pending.


## Low grass / sand9 and75–90 mapping closure

See [GRASS_SAND_VALIDATION.md](GRASS_SAND_VALIDATION.md) and [WINDOW75_90_VALIDATION.md](WINDOW75_90_VALIDATION.md). Nine finite Layer1 assets are added; defaults325/329,337 active canonical PNGs,2,890 HDA entries across18 packs. The120-frame private-survival grass tail is visually accepted. Final 522-frame native 2×75–90 visual review passed; original-state/mapping audit has zero gaps. Windows native acceptance remains pending. Verify with `python prototype/build-hd-assets.py`; rebuild generated grass with `python prototype/build-grass-sand-art.py --output NEW_EXTERNAL_DIRECTORY`.
