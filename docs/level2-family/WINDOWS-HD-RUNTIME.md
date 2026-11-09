# Isolated Windows public HD trial

Experimental, not scene-qualified. Use a new run directory, never an existing classic
profile or installation. Python 3.11 and the separately verified AMD64 build/SDL DLLs
are required. No game executable or original game data is included in the art package.

The package must contain `tools/windows_hd_runtime.py`, `windows_classic_runtime.py`,
`launch_level2_family.py`, `HD-ASSET-PINS.json`, and the original relative `assets/`
layout. Keep package provenance/license notices. Art is not collectively claimed GPL.
The fixed set is 103 public art files (18,496,240 bytes) plus baseline MANIFEST metadata. Private redvent
and unsupported candidates are not enabled. This includes the current bounded
longface normal/damaged, five normal player poses, smallrocks, random props,
tank194 and its two bounded shell materials when the public preset is explicitly selected.

Use `python tools/windows_hd_runtime.py prepare` with the same required binary,
DLL, build/STAGE receipt paths and independently verified SHA256 values as the classic
launcher, plus `--output NEW_ABSOLUTE_ROOT --data ORIGINAL_DATA --assets PACKAGE_ROOT
--hd`. Add `--public-candidates` only to explicitly choose the public extension preset.
Default is check-only. Add `--prepare` to copy verified inputs to the new root.
Preserve the returned RUNTIME.json SHA256 independently.

Use `python NEW_ROOT/tools/windows_hd_runtime.py run --root NEW_ROOT
--trust-sha256 VERIFIED_RUNTIME_DIGEST --hd` to verify without starting.
Repeat `--public-candidates` if it was chosen at preparation. Only with a person present
and ready to observe, add `--launch --observer-present`. Do not schedule unattended
launches or claim this flag proves visual acceptance. The game uses normal input and
natural exit, with no timeout, replay, level jump, or synthetic input.

Windows copies preserve source alternate streams, including Zone.Identifier. Any OS
approval is handled normally, never removed. Copied tools and resources are rehashed;
EXE/DLL identity and build chain are rechecked. Unknown extra files, altered resources,
symlinks/reparse paths, existing outputs and modified environment configuration fail
closed. Child environment removes inherited HD/test/SDL dummy controls. Only selected
family values are supplied; all family absolute paths point into the new root and
relative terrain layout is preserved. Original game data is read-only and external.

This is one first-launch profile. Saves and launch receipts stay in the new root and
prevent accidental repeated launch under the first-launch policy. Do not delete these
files to bypass that protection. Existing classic roots and their original scripts
remain untouched. Normal270 still has its bounded events244/245 pre1960 candidate
window; the public preset is not a promise of full-scene replacement or game validation.


## Resource closure repair

The older 81-file delivery list omitted 20 files required by the newer public
preset: eight tank images, five player poses, three random props and four
smallrocks. Its baseline MANIFEST checksum was also stale. These caused verified
preparation/checks to fail; they do not establish what a previous Windows run
actually displayed. The fixed list retains all original81 byte pins, adds only
those20 existing public assets, and pins the current baseline metadata.

An offline regression prepares from a package containing only these declared
resources, removes that source package, and runs the copied check-only CLI with
all public controls. It also rejects deletion of a newly required image. This
uses synthetic PE fixtures on the cloud host: no Windows executable or game is
run and no screenshot/scene acceptance is claimed. Build staging remains source
only; it is not a substitute for this verified resource preparation.

The current pinned set additionally includes shell146/147, keeping the public
projectile candidate resource-complete. This does not qualify a Windows binary
or an actual gameplay frame; the previous101-file package is not this version.
