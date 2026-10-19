OpenTyrian2000 HD runtime copy

This copy contains one active gameplay pack, the complete startup/title/settings/
load/selector/shop font pack, and the current optional shop metal/Talon/Pulse/
generator/shield resources. The twelve shop HDAs are installed in the startup directory
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

Optional Data text: in Data, press F6 to choose English or Simplified Chinese.
Only Data titles and stories change. Scroll with arrows, PageUp/PageDown,
Home/End or the mouse wheel. The language choice is saved in your profile.
The launchers pass the packaged Data resource directory explicitly.
Chinese font attribution and OFL license are included under licenses/.

Optional Data frame: Data lists and stories have a separately optional HD static
bronze background, including the oval portrait surround. All 18 portraits remain
native; list cubes, English text and cursor remain live. The launchers pass
--data-frame-assets with the package-relative assets/data-frame-v1 directory.
An absent or invalid DFM1 resource keeps the native background independently of
the optional Chinese resources. Help/other menus remain outside its scope.
Artwork/source provenance and the precise art-license status are under licenses/.
This package does not include original Tyrian game-data archives or native
portrait PNGs. Existing generated runtime directories/ZIPs are not refreshed by
a source-manifest update; build a new verified runtime copy to include the frame.

Optional Data HD portraits
---------------------------
Both launchers pass --data-portrait-assets with the package-relative
assets/data-portrait-v1 directory. All18 approved identities retain native size/anchor, including tall FACE15;
noPortrait remains intentionally absent. Missing/corrupt/source-mismatched
resources preserve the native portrait independently of optional frame/text.
The original game data remains external. See licenses/DATA-PORTRAIT-PROVENANCE.txt
and licenses/LICENSE-Data-Portrait.txt for provenance and rights status.
