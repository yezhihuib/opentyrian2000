# Current regular Missile native validation

This finite adapter pins the existing full-production P09 Python driver and adds explicit ordinary/shadow checks for the existing bank-8 regular Missile identities 80031, 80032 and 80033. It does not replace original gameplay code, add a rendering eligibility rule, or rewrite the frozen legacy harness.

Use the same arguments as `enemy_protron_reuse_validation.py`, with `--source-root` selecting a complete current checkout. Supply the official original-data directory, an unchanged production baseline-build, SDL sysroot, and a current asset directory. Original game data is read and piped to the native harness; it is not copied into the deliverable.

The C harness runs the unchanged P09/P05 regression matrix first, then all three missiles through the actual player-shot sprite wrappers and dedicated shadow path. It compares classic INDEX8 writes, RNG and shot state, per-pixel RGBA blend, dedicated shadow palette/owner rounding, anchor/density/identity/slot geometry, later pixel occlusion, cold resource failures, malformed or changed transports, warm source/payload shadow rejection, mode and resource-root eligibility, and fade invalidation. Two wrapper slot values exercise the same shared generic wrapper, not actual sidekick firing attribution.

Regular Missile ordinary loading intentionally differs from Mint27: it does not have Mint27's extra per-call original-source gate. A warm ordinary asset is allowed to remain available after source-byte mutation, but its pinned shadow lease must be rejected. The test preserves and verifies this existing asymmetry instead of adding production restrictions to satisfy a copied negative case.

Bootstrap and a real candidate with independent color edits to each of the three canonical masters are tested. Stage/apply/check must regenerate exactly the three selected HDA payloads and the generated payload-header/binding metadata, preserving every old artwork file and other runtime payload. A separate isolated wrong-shadow-pin mutation must fail the positive shadow draw assertion, proving sensitivity to the new generated pin.

This is native wrapper/compositor evidence, not original-event gameplay, natural campaign, actual player-weapon/sidekick firing, Windows execution, or physical-GPU acceptance. The driver's sanitizers cover the renderer, modified production objects and harness; unchanged optimized baseline objects are reused only after byte checks.
