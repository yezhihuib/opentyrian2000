# Archived finite effects fixtures

These source overrides are exact snapshots of already tested private binaries, not production code. prepare-effects.py only copies the existing source/build files and applies hashed snapshots; it does not build or run. This newly exported preparation command was not executed after the stop request. The source snapshots and their hashes were checked while packaging.

White/green call original loaded weapons at a fixed tick; they do not overwrite per-shot TTL, motion, collision or RNG. Shield is a read-only observer of original natural bursts. Match the documented family pack and environment. Their original Windows runs and complete reports remain in existing Library evidence. Original game data, SDL SDKs, DLLs/EXEs and screenshots are intentionally excluded from Git.

Windows preparation: `python prototype/fixtures/prepare-effects.py --family green-trail --output ../green-fixture` (choose a new sibling directory so the existing project-deps remains reachable). Build with `../green-fixture/prototype/build-game.ps1`. On Linux, use the copied Makefile and installed SDL dependencies. See docs/WINDOWS_HANDOFF.md for the exact green run arguments and remaining WIP scope.
