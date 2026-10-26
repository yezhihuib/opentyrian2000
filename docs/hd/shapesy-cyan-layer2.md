# Static ShapesY cyan cloud quartet — candidate integration

One generated 48×56 master supplies four 24×28 tiles: 111, 112, 121, 122.
This is normal background layer2 terrain, not smoke particles or animation.
Only palette5, neutral normal rendering at internal density8 may qualify.
True internal4, blended/color-filtered rendering, other cloud families, shore,
water and existing layer1 platform zero-black semantics remain unchanged.

The editable raw generated input, prompt and registration recipe are under
`authoring-inputs/shapesy-cyan/`. The native binary alpha mask contains no
original index or RGB data. Rebuild needs neither game data nor Git history.
The recipe yields the accepted canonical master SHA256
`69ba9e3a0b6c22ce7885d2d5443ee367eb83a71f2cb1fdffabdaee3bdce88e63`.
It is divided without resampling, and exact inverse assembly is checked.
Original 521 nonzero source cells contain every generated pixel; 519 cells
have visible generated pixels, with boundary cells (37,14) and (37,19)
deliberately fully inward. All transparent pixels have RGBA0.

Stage and apply to a separate new directory:

```
python3 scripts/build_current_shapesy_cyan.py --root . stage --selection assets/hd/authoring/shapesy-cyan.json --destination <new-external-stage-dir>
python3 scripts/build_current_shapesy_cyan.py --root . apply --destination <external-stage-dir>
```

The stage receipt binds every fixed input and output preimage. Apply derives
outputs again and rejects a modified or stale plan before writes. Handled
write failures roll back; process or power loss is not transactional.

Runtime transports use independent role203 and four-resource closure.
No old ShapesY platform or aircraft art bytes are changed. Source/palette FNV
pins detect drift, not adversarial cryptographic tampering. Source SHA256
pins and authoring input hashes are retained in the registration recipe.
No claim of user-specific visual approval, complete campaign support, or
public release is made by this candidate document.
