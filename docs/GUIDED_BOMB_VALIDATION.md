# Guided physical heads and shared warm fragments

## Accepted finite scope

Player bank8 IDs19/171/20/21 bind to slots326–329, respectively. Each is a
static12×14 sprite at8× density, anchor(0,0).19/171 retain solid blue-metal
casings and warm centers;20 is a short luminous oval and21 a rounded light bar.
The four replacements also apply to their existing shared uses. ID22 remains
unmapped; no complete Widget or arsenal acceptance is implied.

Only two production renderer hunks change: the asset registry326→330 and this
four-ID player TILE lookup. Original indexed drawing, shotX+1/shotY origin,
conditional shadows, physics, collisions, RNG, weapon tables, firing patterns,
TTL, filters and child creation remain unchanged. The65,536-region budget is
unchanged. All334 previous debug-pack assets are byte-identical.
Current totals:18 packs,2,908 HDA entries,346 canonical PNGs; preview334/debug338.

## Source closure and actual runtime

Read-only original table analysis checks99 guided configurations across the
three episode-table groups. Ports28/29/31 have static parents and child
records12/13/14/16/28. e1–3 use20; e4/e5 can use20 and21 simultaneously.
Parent blast filters208/80 and child112 are original hit-effect controls,
not replacement projectile RGB tints. No22 dependency was invented.
Port31's front test is a supported super-arcade configuration, not a normal
shop-acquisition demonstration.

Six matched600-tick replays render3,060 frames: e1 rear28/P6, rear29/P6/P7/P11,
front31/P6, and e4 rear29/P11 (physical level3). All19 original TSVs are
byte-exact, including state/RNG, collisions, emissions, results and effects.
11,653,906 indexed blend rows and every per-tick original-column hash match.
The fixture uses original deterministic firing and real collisions, without
survival changes, injected weapon records or scripted hits.

A separate e1 front40/P6 Widget case renders330 frames per side. All19 logs
and266,050 indexed blend rows match; only mapped20/21 normal/shadow calls
change.22 was absent in this case and remains source/unit-only coverage.
Six fallback cases render780 frames: each missing identity plus global missing
and invalid packs. Original prefixes match; missing identities use the whole
original sprite, peers remain HD, and global missing/invalid RGB is exact.
Two production-binary smoke cases add240 frames with exact candidate prefixes.

New raw blend TSVs are streamed into whole-stream and per-tick hashes rather
than retained. The producer was checked against a2,756,263-row regular-file
fixture; all six retained baseline streams were independently rehashed.
Candidate raw rows cannot be replayed after consumption. Other original logs,
proofs and source hashes remain available. No private readback hook is committed.

## Visual acceptance and limits

Every frame of four60-frame native2× sequences was inspected in chronological
order: MicroP6 ticks240–299, HeavyP11 ticks120–179, episode4 mixed20/21 ticks150–209,
and WidgetP6 white-cloud context360–419. Three native4× stills at250/130/170
also pass. All captured frames match actual SDL readback hashes and matched
full-run RGB/state references. Physical bodies remain solid; warm shoulders
read as luminous edges on clouds without opaque boxes, black fringes or
shape jumps. Root and independent artist accepted the final rounded forms.
This is ordered-frame inspection, not a separate real-time playback claim.

Episode4 surroundings and the old grainy red explosion/trail art are outside
this batch. Other shared missile/sidekick/special users have source closure,
not full runtime visual acceptance. Continuous4×, Windows, full-game and
all-weapon acceptance remain pending. SDL software readback is the current
native-output evidence; no new desktop-window interaction is claimed.

## Reproduction

- `python prototype/build-hd-assets.py`
- `python prototype/build-guided-bomb-art.py --output NEW_EXTERNAL_DIRECTORY`
- See `prototype/fixtures/README-guided-bomb-family.md` for the independent
  ASan/UBSan pixel, source, ownership and negative-control oracle.
- See `docs/PLAYER_WEAPON_PREVIEW.md` for legal loadout selectors. Example:
  `--render-front-port=0 --render-rear-port=28 --render-rear-power=6 --render-rear-mode=1`.
  Use the same episode/level/tick/preset on both sides; keep original game data
  outside the repository. No original decoded records or private captures ship.

The frozen art package's earlier pending-runtime wording is its freeze-time
status; this integration report records the completed gates. Exact machine
receipts and their hashes are in `GUIDED_BOMB_VALIDATION.json`.
