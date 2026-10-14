# Rear534 three-phase generated art source package

Native2x pilot visually approved and unchanged art frozen on2026-10-14. Three new generated body resources only. One imagegen master, exact prompt, portable deterministic rebuild, source hashes/geometry, generated-only proofs, and three PNG/HDA outputs. Original RGB/index grids, original reference contacts, palette bytes, compressed records, proprietary source data, retained terrain and private workspace paths are excluded.

## Rebuild

Run: python3 rebuild.py /new/output/path

Requires Python3, Pillow, NumPy and SciPy. Output directory must not exist. Only the packaged generated master is an image input. Inventory verifies all packaged source/proof inputs; each reconstructed output must match its frozen hash, RGBA, alpha and resource metadata. No game installation is required.

## Resource contract

Role123; slots507,508,509; bases203,205,207; keys1230203,1230205,1230207. Each resource is192x224 RGBA, density8, logical24x28, anchor(6,7). HDA is HDR1 plus six little-endian uint32[key,8,24,28,6,7], then172032 RGBA bytes and EOF:172060 bytes total. Preserve original quarter order0,1,19,20.

## Appearance and alpha

Fixed silver/gray physical housing, red/orange lower and side lamps, small green upper indicator. Only localized generated lamp colors and their immediate reflections change at levels0.30/0.64/1.00. Neutral steel and all alpha/geometry remain byte-identical across phases. Exact original held sequence203x3,205x3,207x3,205x3 remains engine-owned. No new rotation, interpolation or light outside the object.

Source occupied extent[1,7,24,24) remains unchanged. Source315 cells versus pilot alpha-weighted300.5548,−4.5858%; nonzero support313.4844 cell equivalents. Centroid shift−0.0116x,−0.0590y logicalpixels. The generated smooth contour is not clipped to the source staircase mask. Differences are documented rather than corrected by whole-object shrinking, rematting or artificially increasing opacity. Interior alpha is predominantly high fractional values, not uniformly255; exact histogram is in inventory.

Native2x/4x previews are center-nearest samples of canonical8x, with sample coordinates floor((target+0.5)*8/scale). Integer source-over is(background*(255-alpha)+foreground*alpha+127)//255. No direct master-to-display Lanczos is substituted. Generated-only held-order proofs use actual sprite display dimensions48x56 and96x112.

## Scope and limitations

Art freeze is not runtime/gameplay acceptance. Integrator preserves record534 qualification, bank pointer/base/size/part checks, ordered filtered quadrant draws, original indexed writes, fail-closed fallback, phase timing, allocation/state/RNG, physics and collection reward. Fixed145 collection effect remains unchanged; Data513 is outside this family. No game run, repository edit or runtime proof is contained in this package.
