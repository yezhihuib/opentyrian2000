# Current public reader / rendering boundary checks

No original game data, graphics window, OS screenshot, game simulation or Windows
acceptance. Run from any checkout location; outputs must stay outside the checkout.

```
python tests/run_current_public_loader.py --repo "$PWD" --out /absolute/new/loader
python tests/run_render_boundary_tests.py --mode all --case-group all --receipt /absolute/existing-parent/boundary.json
```

On a traced execution host where LeakSanitizer explicitly reports unsupported ptrace,
append `--no-leak-check` to either command. This disables only leak checking, not ASan
or UBSan. Receipts disclose this. Otherwise leak checking stays enabled by default.

Loader: actual current `shared_asset_load_stdio` and `shared_asset_load_fd`, with
current global registry. Each row reads public content from `assets/hd/global-assets-v1`.
Real resources must load in both readers; missing, wrong identity, truncated, trailing
byte and corrupted payload fixture files must be refused. Inputs remain untouched;
mutations are isolated in the new output directory. Logs identify each row and case,
exit code and before/after source/art SHA. No historic Git object is required.
The PPM preview is a single decoded public sprite over gray, not rendered gameplay.
Passing only covers the120 current registry inputs, not all1163 ordinary package files,
source-bank/palette admission, full-scene ownership, or compositor presentation.

Boundary: current production cache/compositor/indexed blitter functions are extracted
unchanged; synthetic sprites and a structural SDL shim test cache invalidation,
clip/coverage edges and integer extremes at4x/8x. Other feature owners are explicitly
disabled in the test fixture, including newer Tank194/Projectile91/NEWSHF/SHAPESY
hooks. Their behavior is not tested by these stubs. Both optimized and sanitizer
builds must pass; fixture adaptation is not a runtime fix or full-scene acceptance.
