OpenTyrian2000 HD runtime copy

This copy contains one active gameplay pack, the complete startup/title/settings/
load/selector/shop font pack, and the current optional shop metal/Talon/Pulse/
generator resources. The eleven shop HDAs are installed in the startup directory
because --startup-assets is shared by all of these loaders. Filenames and asset
bytes are unchanged. The full source/artwork/older experiments remain in the source
project; this tool neither moves nor deletes them.

Start on Linux:
  ./start-hd.sh /absolute/path/to/your/tyrian2000
Start on Windows, using PowerShell:
  .\start-hd.ps1 -DataDirectory 'C:\Games\Tyrian 2000'

A prebuilt binary is included only when the packager was given --executable.
Original Tyrian 2000 game data is required separately and is never bundled here.
Your own optional music stays external. Missing original-data files can prevent
launch even when every HD resource in RUNTIME-INVENTORY.json has been verified.

Dependencies:
- Linux: compatible SDL2 and SDL2_net shared libraries plus standard C/math runtime.
- Windows: a matching architecture build, SDL2.dll and SDL2_net.dll from official
  SDL distributions, including their license notices. The packager does not fetch
  DLLs, guess their architecture, or claim that absent DLLs are bundled.
- Python/Pillow are development tools, not game-runtime requirements.

Launchers use a dedicated persistent manual-first-level profile and initialize a
windowed 2x/Integer config only when absent. Existing marked profiles, settings
and saves are retained. Nonempty unmarked profiles are refused. On Linux set
OPENTYRIAN_HD_PROFILE to override the dedicated XDG base; the actual Linux
config and saves live under its opentyrian2000/ subdirectory. On Windows
use -ProfileDirectory. Startup/shop HD is enabled by these launchers. Other launch
methods can opt out by omitting --startup-assets.

Scope: local single-player Episode 1, first physical-level-9/15 variants only;
this package does not turn the entire campaign into HD. Display fallbacks and the
existing bounded acceptance scope still apply. Linux copying/hashing acceptance is
separate from a complete Windows/device/runtime acceptance test.

COPY-VERIFIED.txt means every selected copied file passed size, SHA256 and pinned
Git-blob SHA1 verification. RUNTIME-STATUS.json lists external dependencies and
whether a binary was supplied. Neither file claims whole-game runtime acceptance.
RUNTIME-INVENTORY.json records every source/destination/hash. The layout, counts
and compression are packaging decisions; no resource decoder or gameplay changes
are made. Font and decoder notices are retained under licenses/.
