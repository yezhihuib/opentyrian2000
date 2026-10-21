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
methods can opt out of these additions by omitting --startup-assets,
--common-menu-assets and --hud-assets as appropriate.

Legacy scene-pack scope: local single-player Episode 1, original physical-level-9/15
variants. The separately configured shared interface and verified player families
are source-identity based across compatible levels. This package does not turn
the entire campaign into HD. Display fallbacks and the
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
bronze background, including the oval portrait surround. With the separate
portrait root omitted, all 18 portraits remain native; list cubes, English text
and cursor remain live. The launchers pass
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

RECONSTRUCTED SHARED RUNTIME
The launchers additionally configure two independent resource roots:
  assets/shared-ui: shared gameplay HUD resources.
  assets/startup: natural menu runs and the original source-witness font files.
Shared resources are not authorized by episode or level. The older scene pack
retains its separate, existing renderer scope; it does not grant shared roles.

The reconstructed RFR3 complete-run resources are newly versioned and are not
claimed byte-identical to the lost RFR1/RFR2 files. They preserve the approved
fonts, natural advances and menu semantics. The OSIfont numeric NFR and recovered
shared HUD artwork retain their original verified bytes. Product source strings and game
economy remain original. Font licenses and corresponding OSIfont source archives
are under licenses/shared-menu. Runtime requires no external font renderer.

GLOBAL PLAYER AND EFFECT RUNTIME
The launchers now additionally pass --global-assets with assets/global.
That independent root contains the exact 49 approved HDA resources plus registry:
Talon (13 poses), Shield (22 resources, with 5 authenticated empty phases),
Pulse (5), Hitflare (7) and front Vulcan (2). No new artwork is introduced.
The renderer authenticates original source/role/palette/operator and lifetime;
no episode or level list grants a global identity. Unknown or invalid contexts
retain the original indexed renderer. The legacy scene pack remains separate.
Original simulation, damage, random state and audio queues are unchanged.

These launchers enable the global root by default without changing your existing
profile or scaler. PowerShell -GlobalAssetsDirectory can select an absolute
alternate root. To run classic/global-disabled controls, invoke the executable
without --global-assets; the old manual scene pack must also be omitted for a
fully classic control. Independent feature roots are not interchangeable.
A missing/corrupt global resource is a safe rendering fallback, not a successful
complete installation: the packager strictly refuses an incomplete copy.

GLOBAL-VALIDATION.json records the final production source fingerprints and
bounded per-family evidence. FRONTEND-VALIDATION.json is retained unchanged as
historical frontend acceptance, not evidence that later source is identical.
Package integration adds no gameplay logic. Windows project source coverage is
checked statically; this does not substitute for a Windows build or GPU test.

Consult RUNTIME-STATUS.json, FRONTEND-VALIDATION.json and GLOBAL-VALIDATION.json for
actual platform and verification scope. A successful copy is not proof of game
acceptance. No whole-campaign, Windows/GPU or frame-pacing validation is implied.
