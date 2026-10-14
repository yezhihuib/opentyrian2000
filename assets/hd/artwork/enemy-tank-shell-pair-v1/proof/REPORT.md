# Enemy tank-shell source summary

This is a publication-safe derivative of the earlier source audit. Original
pixel/index/mask grids and palette RGB tables are omitted. The adjacent JSON
summaries retain source hashes, dimensions, support bounds, route and event facts.
The original audit stays separate; its hashes are recorded in each derivative.

Bank8 IDs 146/147 are two static shell designs on 12×14 canvases with anchor (0,0).
146 points down and 147 down-right. Actor facing, changed velocity and Repulsor
never imply rotation, mirroring or alternate art. “Mauve/steel physical shell”
is an art interpretation, not a material or lore field in the original data.

Enemy records 15/194/195 reuse the IDs through weapons 2/3/6/7. First-level original
events enable the observed tank 15 weapons 2/3. The runtime evidence covers that
emitter only;194/195 and 6/7 remain source-level closure. Generic player weapon
reachability is not universally excluded, so role 122 is strictly enemy-only.
Independent newsh6 explosion IDs 146/147 retain their existing role 106 binding.

Source and mode summaries are historical source evidence, not runtime receipts.
Current bounded checks, actual visibility and limitations are documented in
[the release report](../../../../../docs/enemy-tank-shell-pair-v1/VALIDATION.md).
