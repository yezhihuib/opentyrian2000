# First isolated Windows classic run

This is a separate, classic-only preparation/launch tool. The existing POSIX
launcher is unchanged. HD/public flags deliberately fail with an unsupported
message: missing optional art cannot block a classic run. Native menu/Data UI
fallback remains available; no optional HD art is bundled or claimed qualified.

Use `scripts/windows_classic_runtime.py prepare` with a new absolute output root,
absolute external original-data directory, trusted EXE/SDL2.dll/SDL2_net.dll paths
and their SHA256 values, and original STAGE.json/BUILD-WINDOWS.json paths with
independently verified SHA256 values. Use the full build receipt, not a summary
report. Default is check-only; `--prepare` creates the new profile. Consult `--help`
for exact required options. No compiler, dependency download or installation.

Preparation verifies successful AMD64 build identity and112-unit stage lineage,
EXE/DLL hashes and PE roles, and readable nonempty tyrian1.lvl/tyrian.hdt/
tyrian.cdt/tyrian.snd/voices.snd/music.mus/palette.dat. Their SHA256 values bind the
external data used later; this is not full game-data semantic validation.
Original data is never copied or written by this tool. Reject existing output,
source/data/build directory overlap, parent traversal, symlinks and Windows
reparse points. On Windows CopyFileW with fail-if-exists preserves alternate data
streams including Zone.Identifier for EXE/DLL/scripts/receipts. The tool never
unblocks files or strips download/security metadata. Any normal Windows security
approval remains necessary.

The new root contains bin/game+two DLLs, this tool under tools/, and trusted input
receipts under trust/. RUNTIME.json records hashes of every immutable file and
script. Preserve the returned runtime receipt SHA256 independently. No save or
configuration from an old installation is imported. No global environment or
current directory is changed. Missing/corrupt files stop preparation or launch;
a partial new root is not reused or automatically deleted.

Run the trusted copied tool with `run --root <absolute-root> --trust-sha256
<independently-preserved-runtime-digest>`. Default remains check-only. Only adding
`--launch` starts an ordinary child on Windows. The external digest is mandatory:
a marker's self-declared hashes cannot establish trust in an unfamiliar binary.
The active tool must match the pinned launcher bytes, and every copied input and
data hash is rechecked before launch. No unexpected files are accepted.

Child cwd is the isolated root, matching Windows native`.` save behavior. Absolute
`--data` points to the external original data. Child environment is built from a
short Windows OS allowlist; all mixed-case old HD/candidate controls, SDL dummy
video/audio/render overrides and untrusted PATH values are discarded. Parent
environment/cwd stay unchanged. Normal input and console handles are inherited;
there is no timeout, synthetic input, replay, forced level or graphics workaround.

This initial scope permits **one explicit first launch per newly prepared root**.
A second start is refused because launch logs/saves are now present. Saved files
remain untouched for inspection or later explicit profile-reuse support. Do not
delete logs to trick it into restarting or adopt arbitrary preexisting profiles.

Start/end JSON records store receipt identity, child PID when created, exit code
or honest start/wait failure. An interrupted wait may leave a child running and
is reported as such, not forcibly terminated. Exit0 is not visual/audio/gameplay
acceptance. Actual native testing must verify window, input, sound, clean exit
and isolated save writes. Runtime DLL resolution and optional dependencies still
require real Windows validation; this minimal package is not a portable installer.

## Verification boundary

The new classic-runtime tests use synthetic PE inputs and mocked process launch.
Six runtime cases plus30 adjacent stage/launcher/release cases pass. Native
preparation and launch-check also pass on the existing Windows machine: the
trusted EXE, two SDL DLLs, two receipts and launcher copy retain identical data
streams, and no old configuration/save or HD asset is imported. Actual game
startup and visual acceptance are recorded separately; preparation alone does
not qualify gameplay, audio, save/load or the experimental public combination.
