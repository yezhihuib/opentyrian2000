# Shared HUD reconstruction oracle

This is a fresh targeted test of current renderer helper bodies, the current
font adapter include, and all six production HUD loaders. It does not inherit
historical PASS results and does not build moving menu or native caller sources.

Run from the repository root:

    python tests/shared_hud_reconstruction.py --data /path/to/original/tyrian2000 --sanitize --receipt /outside/repo/shared-hud-asan-ubsan.json

Omit `--sanitize` for the plain C run. `--assets` defaults to the frozen
`assets/hd/shared-ui-v1` directory. The runner snapshots the tested C source and
headers, records their SHA-256 values, and records whether those files remained
unchanged through completion. A receipt with changed inputs needs rerunning
before it can certify the current checkout.

The original PIC3, palette 5, tiny-font glyphs, and option sprites are decoded
read-only in Python memory and sent through a pipe to the executable. They are
never written to fixtures or receipts. Missing and corrupt resource cases use
throwaway directories, symlinks to frozen resources, and a synthetic corrupt
payload. No original data or frozen resource is modified.

Coverage includes:

- Six production loaders with their unmodified original-source pins.
- Independent shared root across levels 1–18 at 4x/8x; no scene, probe, or manual
  renderer activation; independent behavior alongside inactive legacy flags,
  rejected active legacy scenes, and genuinely accepted ORDINARY legacy scenes.
- Static HUD sampling against the actual final indexed surface, not a shifted
  scene canvas. Every owned static subpixel is compared with the production
  family sampler in the 36 level/density cases.
- Explicit ordinary/normal15-low-detail scene-font admission, full-run shifted
  final-index witness, full source-write witness, and exact INDEX8 layout.
  Unknown/night output, mismatched source/final indices, changed source format,
  and unrelated scene rejection remove scene font output but retain static HUD.
- Same-index writes on both scene and final indexed surfaces, with pixel/rect
  notifications before/after finish, during fades, and after a consumed Present.
  Multi-cell rectangles are checked against authored legacy underlay, including
  current/saved fade-cache restoration. Active legacy scene admission must
  not bypass the shared font run's exact final-index witness.
- Modal suspend/resume, reset, idempotent root assignment,
  root replacement/disable/overlong rejection, missing/corrupt family isolation,
  source identity/layout and glyph/palette/density mutation. HUD1 source-used
  palette index 108 is changed before begin and between begin/finish; index 255
  is checked separately to prevent an overly broad full-palette HUD1 guard.
- Disabled-stage and repeated-finish preservation of pending presentation,
  static and scene-font cached fades/restoration, repeated Present non-replay,
  and invalidated cached final indices.

Limitations: SDL allocation/presentation and unrelated scene/menu family
callbacks are narrow stubs. This is not a native engine, GPU, user-input,
playthrough, or full build test. ASan and UBSan are enabled together when
requested. LeakSanitizer is explicitly disabled because this execution
environment uses ptrace, which LeakSanitizer rejects. The sanitizer run must
therefore not be described as a leak check.
