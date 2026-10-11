# Current scoped release (2026-10-11)

The manifest is authoritative:18 packs,2786 HDA entries,285 formal PNGs, defaults273/277. Latest additions are the [plateau edge correction](PLATEAU_FOUR_VALIDATION.md) [static installation](INSTALLATION_VALIDATION.md), [physical terrain underlay](UNDERLAY_VALIDATION.md), and the [complete road family](ROAD_NINE_VALIDATION.md). The final [terrain111/114 batch](TERRAIN_HOLES_VALIDATION.md) closes the [audited first-30-second milestone](FIRST30_HD_COVERAGE.md):222 nonempty HD identities plus5 intentional empty shield identities out of227 observed.

The next bounded private-survival segment now also includes the [three static physical craft](CRAFT_THREE_VALIDATION.md). It now also includes [terrain113 and the six-tile stone foundation](TERRAIN_NEXT_SEVEN_VALIDATION.md), verified with the same clearly labeled private-survival replay. The [complete intact/remnant stone entity family](STONE_TWELVE_VALIDATION.md) now retains both original linked outcomes, with a separately labeled later clipped-state diagnostic.

The [complete purple formation family](PURPLE_FOUR_VALIDATION.md) closes the base127 dependency with four independently drawn designs and original linked/drop behavior. Its tail/reuse checks are bounded private-survival diagnostics.

## Historical green release update (2026-10-11)

See [GREEN_RENDER_VALIDATION.md](GREEN_RENDER_VALIDATION.md) for the selected complete214–217 head pulse, green-only brightness interpolation, finite cloud visual/technical checks and Windows acceptance commands. At that green checkpoint:18 packs,2620 HDA entries,201 formal PNGs; defaults190/194. Existing rollback packs and accepted families are byte-preserved. The text below records earlier release stages and their then-current scope.

# HD release stages

Current handoff adds reviewed white smoke/shield and explicitly WIP green v1/v2. Current source/pack/default status, limits and Windows commands are in [WINDOWS_HANDOFF.md](WINDOWS_HANDOFF.md); reviewed scopes are in [EFFECTS_ACCEPTANCE.md](EFFECTS_ACCEPTANCE.md). The following is the earlier d1dcfbed resource baseline, retained as historical validation context; its counts and unbound-family statement describe that earlier stage.

# Accepted local HD release

The independent RGBA renderer, Talon13 default/5-frame compatibility, static blue2Dv4, transparency/hit/enemy filters, turretv7, foundation321/322/331/332, type10v9 and the accepted finite death families are committed with runtime resources. Original game simulation, RNG, collision, events and indexed drawing remain the reference.

`assets/hd/manifest.json` records exact sourcePNG, HDR1 key/density/logical size/anchor and all runtime SHA256. Final preview/debug packs have150/154 entries. Eight packs retain three recent resource rollback stages47/51,95/99,102/106. They are byte-identical copies of the passed local packs. The154 PNG inputs are lossless RGBA dumps of accepted resources, not captured game images or newly painted art.

Build on the existing Windows environment with `prototype/build-game.ps1`. Verify all resources with `python prototype/build-hd-assets.py`; rebuild identical packs with `--output NEW_DIRECTORY`. Existing SDL SDKs in sibling `project-deps` and original game data in sibling `runtime-data/tyrian2000` are prerequisites, excluded from Git along with executable/DLL build outputs.

The two start scripts use repository packs by default. `-BeforeLargeGround`, `-BeforeImpact`, `-BeforeLargeAir` choose the three repository resource rollback stages. Earlier rollback selectors still use preserved local legacy packs. Explicit `-Assets` on the debug launcher remains available. `prototype/asset-index.py` uses the committed index retaining the original1053tick trace and three15-second windows; only the pack path was migrated. Recorded source/data/executable hashes describe that original observation, not a newly replayed trace.

Finite technical passes: small type1v2 IDs122..133 frozen; large-air48 IDs3..14/22..33/41..52/60..71; impact IDs146..152 seven ticks; large-ground48 IDs192..203/154..165/211..222/173..184. Original offsets, TTL, repeats, drift, clipping and blending remain in game code.12-frame wholeRGBA reassembly, native2x/4x, missing single piece, classic, repeat/RNG and stable end windows passed. The original right-edge contact in ground art is retained.

Existing air/impact fixtures naturally contain ground, so36/19RGB-different ticks after ground integration exactly match ground draw ticks; non-ground ticks agree. Protected resource bytes/calls, indexed operations and RNG match. Full RGB on ground-present ticks was not compared pixel-for-pixel with the old unbound rendering. Arbitrary screen edges, full-level acceptance, physical FPS and other display resolutions remain untested.

No smoke, green trails, shields, cash, table-only effects or paused terrain109/107/120 are newly bound in this release. Those future active effects require their own finite integration and visual acceptance before another commit. No push/PR was performed. Separate pre/post checkpoints and full evidence/media/rollback ZIPs remain outside the repository.

Retained untracked files: historical standalone prototype importers, render demos, exploratory maps and verification scripts whose exact current variants are not necessary to this accepted runtime. They are preserved, not blanket-added or deleted. Temporary screenshots/HTML, run logs, EXEs/DLLs/objects, local SDK props, videos and rollback archives remain excluded; original third-party game data is not committed. Exact file inventory is saved in the local git-release/pre-commit-audit.json and final commit report.
