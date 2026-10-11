# Four remaining plateau edges

Generated shapesz layer1 IDs96,97,98,108 complete the missing top/left/concave edges of the accepted nine-tile plateau. Each is24×28 logical,192×224 RGBA at8×, anchor0,0, alpha255. Accepted nine ground tiles,101, props, clouds and road candidates are unchanged.

Only the four authored target-cell crops are formal source inputs. The complete generated scene also contained unchanged game-derived context, so that full scene, original references and screenshots are excluded. The exact prompt, crop registration and source hash are retained. `source/generated-crops` contains generated target artwork only.

`prototype/build-plateau-art.py --output NEW_EXTERNAL_DIRECTORY` invokes the C++17/Pillow reproducer, verifies ten frozen accepted neighbor hashes, applies deterministic harmonic RGB registration in a32-HD-pixel inward band, and checks all four PNG/RGBA/HDA hashes. Original game data is not needed. Interior pixels beyond the band and all alpha bytes remain unchanged.

Forty of48 actual canonical neighbor types receive explicit registration. Eight external original road/prop/context transitions are reviewed visually. Some frozen neighbors already disagree by up to11RGB, so a new shared edge cannot equal them all simultaneously; no universal byte-identical seam claim is made. See docs/PLATEAU_FOUR_VALIDATION.md for actual finite coverage and limits.
