# Native portable level-2 preview launcher

This is a new launcher for the direct `--level2-preview=asteroid2-v1` engine path.
It is not the earlier frozen, timed, scripted asset-debug preview. Historical
`scripts/preview_level2_frozen.py` and its tests remain unchanged.

## User flow

1. Extract the complete verified ZIP into a **fresh empty writable local folder
   outside the original Tyrian2000 data directory**. Do not overlay an existing
   installation or another extracted bundle. Chinese characters and spaces are supported
   by the launcher's Unicode Windows calls. Prefer a short location such as
   `C:\Games\Level2`; an overlong session or asset path fails before copying.
2. Double-click `Start-Level2-Preview.exe`. If Windows displays a security warning,
   the launcher does not dismiss it, change policy or remove download markers.
3. Choose the folder containing your existing original Tyrian2000 data. The
   launcher validates the exact named original assets and their hashes. It does
   not search the disk, download game data, sign in, copy a whole installation,
   import old settings or import saves.
4. A new `sessions/<UTC>-<128-bit-random>/` directory is created beside the
   launcher. The game starts there, windowed at 4x. Each subsequent actual launch
   creates a different session. Old sessions remain untouched.
5. Use the engine's real keyboard controls: arrows to move, Space to fire,
   Enter for the rear weapon mode, and Escape for the native menu/quit flow.
   There are no scripted inputs, debug playback ticks or automatic kills.
6. Exit normally. The session, generated settings, saves, `launcher.log`,
   `stdout.log` and `stderr.log` are retained. The launcher waits for normal exit.

Optional arguments:

- `--data=C:\Games\Tyrian2000` supplies an absolute local original-data folder.
  Quote the entire argument when the folder contains spaces.
- `--scale=2` selects a smaller window. `--scale=4` explicitly selects the default.
- `--check-only --data=C:\Games\Tyrian2000` verifies the compiled contract,
  package payload and original assets without creating any directory or log and
  without launching any child. It exits 0 on success or 2 on validation failure.
  Output goes to an inherited console/output handle when one exists. Check-only
  does not display a folder picker or a blocking message box. Redirect output
  when invoking the GUI-subsystem executable from a command shell.
- `--help` describes the options. Unknown or repeated data/scale options fail.

A game that starts and then exits unsuccessfully is reported with launcher exit
code 3. Preparation/launch failures return 2. Cancelling the data-folder chooser
returns 0 without creating a session.

## Compiled manifest contract

The parent packager owns the generated header and final payload inventory.
`tools/level2_preview_launcher_policy.h` supplies these types before including it:

```c
typedef struct {
    const wchar_t *path;
    const char *sha256;
    unsigned long long size;
} PreviewFile;
typedef struct { const wchar_t *name, *value; } PreviewEnv;
```

The generated header defines:

- `PREVIEW_GAME_EXE L"bin/opentyrian-level2.exe"`.
- `PREVIEW_BUNDLE_ID L"..."`, the release/payload identity.
- `PREVIEW_SOURCE_COMMIT L"..."`, the reviewed source commit. This is optional but
  strongly recommended; build receipts must identify all uncommitted source
  content hashes as well as the base revision.
- `preview_payload[]` and `PREVIEW_PAYLOAD_COUNT`: exact relative paths, lowercase
  SHA-256 strings and positive byte counts. Runtime locations are the game EXE,
  `bin/SDL2.dll`, `bin/SDL2_net.dll` and files below `assets/hd/`.
- `preview_original[]` and `PREVIEW_ORIGINAL_COUNT`: flat original asset filenames,
  expected SHA-256 strings and sizes. No original asset bytes are embedded.
- `preview_env[]` and `PREVIEW_ENV_COUNT`: all **53** reviewed name/value pairs,
  exactly once, from the current public-candidate HD/fallback/static-HUD plan.
  The launcher explicitly rejects the obsolete 23-control set, inherited debug
  settings, changed path values and private candidates.

See `tools/level2_preview_launcher_manifest.h.example` for syntax. It is
intentionally incomplete and is not a distributable manifest. The policy checks
case-insensitive duplicates, file/ancestor collisions, absolute and traversal
paths, NTFS alternate-stream syntax, backslashes, Windows device names, trailing
dots/spaces and non-ASCII manifest paths. The selected package and data **root**
folders may contain Unicode and spaces; only the child-relative asset names are
restricted to ASCII to work with the native engine's narrow file APIs.

Original extensions are restricted to `.dat`, `.lvl`, `.hdt`, `.cdt`, `.snd`,
`.mus`, `.pic`, `.shp`, and `.anm`. The minimum core inventory is `tyrian1.lvl`,
`tyrian.hdt`, `tyrian.cdt`, `tyrian.snd`, `voices.snd`, `music.mus`, and `palette.dat`.
The final packager must include all further original assets needed by the actual
normal level session. Merely satisfying the minimum is not a full gameplay test.

Package-only licenses, source/build receipts and documentation need not be
copied into sessions. Extra unlisted package files are not selected or copied by the launcher.
Windows resolves bootstrap static imports before launcher code starts, so this is
not a claim that arbitrary extra DLLs placed beside the bootstrap are harmless.
Extract only the externally verified ZIP into a fresh empty directory. Only
named original files are opened; arbitrary old profiles are not
scanned. Missing assets or different original-data editions fail validation
rather than being silently accepted.

## Build

Use a Windows x64 MinGW-w64 toolchain with Windows BCrypt support. The runtime
requires neither Python nor PowerShell, and the launcher imports only Windows
system libraries. No non-system compiler runtime DLL is needed.

```sh
x86_64-w64-mingw32-gcc \
  -std=c11 -O2 -Wall -Wextra -Werror -municode -mwindows -static-libgcc \
  -Wl,--no-insert-timestamp \
  -DPREVIEW_MANIFEST_HEADER='"/absolute/path/generated_manifest.h"' \
  tools/level2_preview_launcher.c -o Start-Level2-Preview.exe \
  -lbcrypt -lshell32 -lole32
```

The generated header is compiled into the bootstrap. It is not loaded from an
editable sidecar at runtime. Finalize all payload bytes before compiling it and
record the source/header/compiler/binary hashes in the bundle receipt. Audit PE
machine type, PE32+ optional header and imports for the **final** bootstrap, game,
and DLLs. The packager must separately provide an external SHA-256 for the final
ZIP.

## Runtime safety and isolation

- Package identity comes from `GetModuleFileNameW`, never the caller's working
  directory. The bootstrap and each input/parent are inspected as disk files or
  directories using `FILE_FLAG_OPEN_REPARSE_POINT`. Reparse points and symlinks
  fail. Directory handles remain open without delete sharing to prevent ancestor
  replacement; pinned file handles also deny write/delete sharing while checked,
  copied and used by the child.
- Paths use Unicode Win32 APIs and extended local-drive syntax. Both selected
  drive roots and resolved volume roots are checked with `GetDriveTypeW`; remote
  shares, mapped network drives and unknown drive types fail. UNC/network and
  device input roots are intentionally rejected. Package/data identities come
  from their locked directory handles using `GetFinalPathNameByHandleW` with
  `FILE_NAME_NORMALIZED | VOLUME_NAME_GUID`, not lexical drive-letter paths.
  Normalized volume-GUID ancestors are locked too, and matching file IDs plus a
  second final-path query verify that the identities did not change. All later
  file operations and the new session use these resolved volume paths, avoiding
  changes to a SUBST/drive alias after validation. Process creation has a separate
  ordinary DOS long-path projection: the locked handle is queried with
  `FILE_NAME_NORMALIZED | VOLUME_NAME_DOS`, its verbatim prefix is removed, and
  its drive's `QueryDosDeviceW` target must equal the canonical volume target.
  The projected directory is reopened, locked and checked against the same
  physical identity. A projection that cannot map directly to a real local
  drive fails closed. The projection and physical identity are checked again
  immediately before `CreateProcessW`. No verbatim or volume-GUID path is passed
  as the process executable or current directory. The child profile/temp paths
  likewise use the verified ordinary DOS projection.
  Before any session directory is created, a length check accounts for the
  fixed 49-character session name and every child-relative payload/data path.
  They must remain below `MAX_PATH` (260 UTF-16 code units, including room for
  the terminator). The actual session projection is checked again before any
  payload copy. This is intentionally conservative for the native engine's
  ordinary relative file APIs; move the extracted bundle closer to the drive
  root if the check fails. Overlap checks therefore compare
  physical long-name identities, including 8.3 and SUBST aliases, with ordinal
  Unicode-insensitive comparisons. Failure to obtain a local identity fails
  closed before creating output. The ordinary folder picker is limited
  by the shell's supported folder paths; an explicit `--data=` path is available.
- BCrypt computes SHA-256 over every pinned package file and required original
  asset before a session exists. Copies are hashed again. A missing, changed or
  unreadable input stops the launch. The original data cannot contain the session
  tree or lie inside it. No output is written into the original-data tree.
- `CopyFileW(..., TRUE)` refuses replacement and preserves alternate streams.
  When `Zone.Identifier` is present, its copied bytes and size are checked for
  equality. Failure to preserve it stops launch. There is no deletion/unblocking
  call, execution-policy change, SmartScreen interaction or security-warning
  approval. Use a local NTFS folder for reliable alternate-stream preservation.
- The output directory uses UTC and 128 random bits from BCrypt and must be newly
  created. Collisions are retried with a new identity, never adopted. Failed and
  previous sessions are retained, not cleaned up or resumed.
- The only generated config is fresh `opentyrian.cfg` with windowed 4x (or 2x)
  and integer scaling. Configs/saves from the original folder and earlier sessions
  are never copied. `TARGET_WIN32` saves to `.`; the explicitly supplied child CWD
  is the new session root. The game executable and DLLs are below its `bin/`.
- The child receives `--data=data --level2-preview=asteroid2-v1 --no-xmas
  --no-joystick`. Audio is not disabled. There are no debug, probe, capture,
  headless, benchmark or scripted-input options.
- The environment is rebuilt, not filtered from inherited arbitrary values:
  Windows APIs provide `SystemRoot`, `WINDIR`, `SystemDrive` and a `PATH` containing
  only the Windows system directory. `TEMP`/`TMP` use the new `tmp/`, and
  `USERPROFILE`/`APPDATA`/`LOCALAPPDATA` use the new `profile/`. The exact 53 reviewed
  relative HD controls are then added. Inherited old HD, asset-debug, game-probe,
  SDL/audio/video driver, home-directory and PATH overrides are absent. No parent
  or global environment is changed.
- `CreateProcessW` receives the explicit verified EXE, Unicode environment and
  new CWD. `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` permits only the child's stdout,
  stderr and read-only NUL stdin handles. Other handles are non-inheritable.
  A process-local DLL-search setting excludes the caller's unrelated CWD; it
  does not alter user/system policy. There is no shell invocation. The child is
  waited on indefinitely and is never
  killed, sent fake input or terminated on a timer.
- `launcher.log` records release/source identity, every runtime/original digest,
  selected scale, exact command, HD controls and the final child exit code.
  Logs are local to each session. They are not uploaded automatically.

The integrity boundary is the **untampered bootstrap plus externally verified
ZIP**. Embedded payload hashes catch altered/mismatched payload files; they do
not prove a modified bootstrap is trustworthy. This is ordinary same-user
application isolation, not a sandbox against a malicious administrator or other
process controlling that user's account. The launcher does not request elevation
or alter filesystem ACLs, antivirus, firewall, SmartScreen or system policy.

## Validation and remaining acceptance

Run the focused executable host-policy and source-contract tests:

```sh
python -m unittest discover -s tests -p test_level2_preview_launcher.py -v
```

Set `LEVEL2_MINGW_CC` and `LEVEL2_MINGW_OBJDUMP` to the toolchain binaries to enable
the actual strict Windows x64 cross-link/OS-import test. Without them that gate is
explicitly skipped. The full test fixture uses a valid compiled manifest so the
link test cannot optimize away the normal launch and folder-picker paths.

Host policy tests and PE audits do **not** establish Windows runtime, physical
GPU, real keyboard, sound, focus, menu or flicker correctness. The cloud Wine
runtime available during initial development failed its own initialization; no
launcher Windows runtime pass is claimed on that basis.

Before distribution acceptance on an authorized Windows test machine:

1. Run check-only from an unrelated CWD with Chinese/spaced package/data paths.
   Compare directory inventories before/after; no new session/log is permitted.
2. Verify failure on a modified EXE/DLL/HD file, missing or changed original
   asset, symlink/junction in any selected ancestry, and source/output overlap.
   Use disposable **fixture** folders to test a bundle located inside data while
   selecting data through an existing 8.3 short alias and through a SUBST alias;
   both must fail before any sessions directory is created. A source data folder
   physically inside a prior session must likewise fail under either alias.
   Do not change system 8.3 settings to run this test; if aliases are unavailable,
   record that case as not run. Test an already-authorized disposable mapped
   network drive: its data/package paths must be rejected before payload reads
   or output creation. Do not create a new network mapping without permission.
   Test a benign separated local SUBST case: it may use a verified physical
   ordinary-drive projection or fail closed, but must never pass a verbatim CWD.
   Test the projected ordinary DOS executable/CWD, path lengths immediately below
   and at the rejection boundary, and original folders with non-ASCII case
   variants. Overlong paths must fail before creating the sessions container.
   Original bytes and existing saves/configs must remain unchanged. These are
   native Win32 acceptance cases, not results established by host policy tests.
3. On NTFS, attach a benign `Zone.Identifier` to a fixture input and confirm an
   exact copied stream. Do not remove existing download markers to conduct tests.
4. Use a harmless instrumented **test build** in a separately pinned test bundle
   to check CWD, Unicode environment, absence of inherited debug/SDL/PATH values,
   log handles, and that unrelated inheritable handles are not inherited.
5. Launch twice, checking distinct retained sessions and fresh settings each time.
   Run default 4x and explicit 2x. Cancel the chooser and verify no output.
6. Test the actual game interactively: real keyboard controls, audio, Escape menu,
   normal quit and both supported scales. Confirm the current HD tank/player/HUD
   assets and assess flicker on the actual Windows/GPU surface. Keep this result
   separate from compilation/host-test success.
