# Ordinary production Windows HD, separate from family candidates

This workflow restores the public ordinary opening/title/menu/TYRIAN asset path. It
requires a new **86-unit canonical ordinary executable**, not the existing112-unit
family executable. Native compilation and user-observed visual checks are separate
acceptance steps; this package is not a claim of GPU/full-campaign qualification.

## Single download handoff
Source stage:339 exact source inputs (including two license/provenance files), three
shared-menu generated headers, RC/icon, bound validation, standalone MSVC project,
and `build_ordinary_windows.ps1`. No old user.props or CopyPropsTemplates are used.
SDK10.0.26100.0/MSVC14.44.35207/v143 and existing SDL2/SDL2_net x64 dependencies are
required. Run the build script check-only first, then explicit `-Build` in a fresh
stage. It emits an ordinary-production86 STAGE/BUILD chain and AMD64 EXE SHA.
No family overlay, diagnostic enable macros, or forced candidate options are added.

Resources: exact1163 runtime-assets-v1 rows,166516707 bytes, at `destination` paths.
Keep all original metadata, license and provenance notices. Bundled original
start-hd.ps1/.sh are retained for provenance, **not invoked** by the safe launcher.
No EXE, SDL DLL, original game data, saves, private assets or optional music are
included in the handoff ZIP. Art is not blanket licensed as GPL.

Tools directory: `windows_ordinary_runtime.py`, `windows_classic_runtime.py`,
`runtime-assets-v1.json`, `ordinary-initial.cfg`. The first-launch root copies only
these required tools (the config template becomes opentyrian.cfg), resources, the
separately trusted EXE+DLLs and their receipts:1172 exact immutable files.

## Prepare/check; don't launch unattended
`python tools/windows_ordinary_runtime.py prepare` takes the same explicit binary,
DLL and STAGE/BUILD paths plus SHA256 values as the classic workflow, and additionally
`--output NEW_ABSOLUTE_ROOT --data EXTERNAL_ORIGINAL_DATA --assets PACKAGE_ROOT --hd`.
It rejects family112 builds and `--public-candidates`. Default is check-only. Add
`--prepare` only to create the new directory. Preserve the returned receipt digest
independently. No prior profile or source package is overwritten.

`python NEW_ROOT/tools/windows_ordinary_runtime.py run --root NEW_ROOT
--trust-sha256 VERIFIED_RUNTIME_DIGEST --hd` verifies without launching. When a person
is present, `--launch --observer-present` starts normally and waits for natural exit.
Choose New Game and Episode1 normally. No jump, replay, synthetic input or timeout.

Windows CopyFileW preserves ADS/Zone.Identifier. Existing OS approvals are handled
normally. Exact hashes, paths, AMD64 roles, build flavor and source binding are
rechecked; new root cwd isolates Windows '.' saves. External original data is not
copied or modified. All inherited family/probe and SDL dummy overrides are removed
from child environment only. Startup/common-menu/manual/global/HUD/Data text/frame/
portrait CLI paths point to the new immutable assets. Fresh config is windowed4x
Integer scaling. It is not copied from an existing profile. First launch only: logs
and saves thereafter deliberately block reusing the first-launch receipt. Do not
remove those files to bypass checks. Existing classic/family roots stay untouched.

The default first-play window is 1280x800 (4x), not640x400 (2x). This restores the
previous display sampling size; it does not widen any renderer admission or promise
full-scene HD. Existing prepared profiles/receipts are not modified.
