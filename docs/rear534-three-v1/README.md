# Rear-power 534: three-phase HD body / 后置武器强化道具三相高清本体

## English

### Scope and binding

This display-only change replaces the body of record 534 with a generated gray/silver
mechanical pod. Its housing, registration and alpha stay fixed while the small green
indicator and orange/red lamps follow the original held sequence:
203 × 3, 205 × 3, 207 × 3, 205 × 3. Only `src/render_mirror.c` changes production code.

- Record 534, size 1, actual global `spriteSheet11` pointer; bases 203/205/207.
- Role 123, slots 507–509, density 8; complete 192 × 224 RGBA composites represent
  logical 24 × 28 bodies at anchor (6, 7).
- Original quadrants 0/1/19/20 keep their order, filter, crop, indexed write and reset.
  The shared per-quadrant clipping/row-wrap guard remains unchanged.
- All three exact headers, payloads and EOFs must validate; otherwise the whole family
  stays classic. No density-4 substitute is accepted.
- Fixed 145 remains the original shared collection effect. Constructor, mode/difficulty
  rules, held timing, motion, RNG, allocation/drop order, collision, rewards and text
  remain engine-owned. Other banks, cash/gems, tank shells and enemy energy are separate.

### Bounded runtime evidence

The private Linux SDL dummy/software fixture completed three engine attempts, all
passing without retries: one no-image baseline, one native 2× candidate with 21 frames
(249–260 and 264–272), and one native 4× body spot at 255. Every run executed 273 logic
ticks through tick 272. The 22 retained images and streams occupy 9,960,974 bytes;
the retained run evidence plus its final archive totals 19,351,463 bytes, below 20 MiB.

The fixture selected Normal ordinary story, Episode 1 / physical level 9, seed
`0x5eed`, front weapon 1 / power 1, and rear weapon 0. Only the original demo-key path
applied RIGHT at 20–25 and FIRE at 202 and 206; it was neutral otherwise. No helper
projectile, health protection, coordinate/velocity correction, forced allocation,
enemy-health edit or projectile deletion was used.

- Original Pulse shots damage carrier 10 at 208 and 212. Its death allocates rear 534
  at 212 before carrier release and awards 15 cash.
- A residual original shot hits ground enemy 126 at 216, reducing armor 10 → 9.
  This incidental hit is retained; there is no extra shot or collateral death/drop.
- The body first draws at 213 and is collected at 264. Rear 0 remains unchanged;
  the original 1,000-cash fallback changes total cash from 15 to 1,015. This run does
  not demonstrate an equipped-rear power upgrade.
- All 52 selected body draws preserve four quadrants; all 208 candidate calls use HD.
  The 12 held-cycle frames retain 304–315 matching original indexed-support cells
  out of 315 because the original ship overlaps the last frames. No clipping is
  reported. Equal-color overdraw cannot identify hidden-layer provenance.
- Tick 264 includes the final body draw and the first fixed-145 draw. The body is
  absent from 265 onward; fixed 145 draws at 264–270, then both 271 and 272 are clear.
- Both candidates match all 17 original stream/comparison items, including state/RNG,
  both indexed surfaces, collision traversal, input, shot lifecycle, rewards,
  presentation and fixed-145 rows. Only wall time is excluded from control comparison.

The retained 2× sequence and true 4× spot passed independent numeric and author visual
review. Actual contrast coverage is brown rocky terrain; the cloud is beside the body. Stable physical housing, localized lamp changes, clean contour/registration and
the unchanged collection/clear sequence are documented in
[runtime-summary.json](runtime-summary.json) and
[author-review-summary.json](author-review-summary.json).

There are no baseline RGB images, so no baseline-versus-candidate RGB comparison is
claimed. The 4× image covers one body phase, not the effect lifetime. Missing-family
fallback and equipped-rear upgrades have source-unit coverage only. This evidence does
not establish Windows/manual-play, physical-window/GPU/fullscreen, whole-level,
other-mode, all-background, cloud-overlap or performance acceptance.

### Source units and authored package

[source-unit-result.json](source-unit-result.json) preserves the pre-publication
receipt unchanged. The original-source suite passed 166 scenarios / 1,668 assertions
in each optimized and ASan/UBSan build. The renderer suite covers both selected packs,
normal/Christmas banks, all 256 filters, ordered crops, alpha, clipping/row-wrap,
indexed wrapper writes and 44 invalid-resource cases. These are extracted finite
source units with documented observation sinks and counted RNG; LeakSanitizer was
not enabled. They do not substitute for the separately bounded runtime evidence.

The generated-only [art package](../../assets/hd/artwork/rear534-three-v1/README.md)
contains the master, prompt, deterministic rebuild, hashes/geometry and three PNG/HDA
outputs. Original RGB, pixel-index grids, source records and runtime screenshots are
not bundled with this release documentation. The frozen registration receipt's
historical labels `pilot-203-8.png`, `pilot-205-8.png` and `pilot-207-8.png` identify the
same byte-pinned files now packaged as `output/rear534-bank11-203-8.png`,
`output/rear534-bank11-205-8.png` and `output/rear534-bank11-207-8.png`; they are not
rebuild input paths.

For an authored rebuild, use the art package's `rebuild.py` with a fresh output
directory; Python 3, Pillow, NumPy and SciPy are required, and no original data is
needed. `prototype/build-rear534-three-art.py` verifies the repository bindings and
rebuild. Original-data tests require separately authorized game data.

`prototype/test-rear534-original.py` takes `--repo`, `--data` and a fresh external
`--out`. `prototype/test-rear534-three.py` takes `--main-root` at the published
baseline, `--original-data` and a fresh external `--out`. The baseline checkout must retain
`ee2b90cfaf9f227ca394ecd01f2403e55dbf2ea0` and its verified predecessor resources;
a newer main checkout is not interchangeable. The test-only tracked-diff guard was
narrowed after runtime to production `src` and the manifest so released docs/art do
not prevent rerunning it. Exact renderer/source/manifest inverses and asset checks
remain in force. Its separate source-only check does not claim another full unit or
engine run. The numeric unit receipt still pins the driver used for those recorded
results; the amendment is identified in the runtime summary. No engine is launched
by these unit scripts.

## 简体中文

本次只替换记录 534 的道具本体：银灰机械外壳、锚点和透明度保持不动，小绿灯与
橙红灯按原版 203×3、205×3、207×3、205×3 的停留顺序亮暗变化。生产代码仅修改
`src/render_mirror.c`。绑定实际 `spriteSheet11`、size 1、role 123、槽位 507–509；
8 倍资源为 192×224，对应逻辑 24×28、锚点 (6, 7)。原四分块顺序 0/1/19/20、
滤色、裁切、索引写入和重置均保留；三份资源任一不合格时整族回退原版。
固定 145 拾取特效以及移动、随机数、碰撞、掉落、奖励和文字逻辑均未改动。

有限 Linux SDL dummy/software 检查共 3 次引擎启动，全部通过且没有重试：
基线不截图，候选 2× 保留 249–260 和 264–272 共 21 帧，候选 4× 仅保留 255 一帧。
每次运行 273 个逻辑 tick，终点为 272；共 22 张图。运行证据 9,960,974 字节，
加最终归档共 19,351,463 字节，低于 20 MiB。

夹具选定 Normal 故事模式、第一章物理关卡 9、种子 `0x5eed`、默认前武器 1/
威力 1、空后武器。只经原版按键回放入口在 20–25 向右、202 和 206 开火，
其余为中立输入；没有辅助弹、保命、坐标/速度修正、强制分配、改敌血或删弹。

- 原 Pulse 弹在 208、212 命中载体 10；212 原死亡分支分配 534，并另加 15 现金。
- 残余原弹在 216 自然击中地面敌人 126，护甲 10→9；这次附带命中完整保留。
- 本体 213 首次绘制，264 拾取；后武器仍为 0，实际走原版 1,000 现金回退，
  总现金 15→1,015。装备后武器时的升级仅有源码单元覆盖，不属于本次实际运行。
- 52 次本体绘制共 208 个原顺序分块均走候选高清路径。12 帧停留周期的原索引
  支撑匹配数为 304–315/315，末尾保留了原玩家船重叠；同色覆盖不能证明隐藏层来源。
- 264 仍含最后一次本体绘制；本体自 265 消失，固定 145 在 264–270 共绘制 7 次，
  271、272 均清空。两组候选的全部 17 项原状态/索引/随机数/碰撞/输入/弹丸/
  奖励/特效配对一致；控制日志仅排除墙钟时间。

完整 2× 序列及真实 4× 单帧已通过独立数值检查和作者视觉复核，记录见上方两个
摘要。没有基线 RGB 图，因此不宣称 RGB 成对比较；4× 不覆盖特效全寿命。
没有 Windows、手动实机、GPU/全屏、整关、其他模式、全背景、云重叠或性能验收。
缺失资源回退属于有限源码单元覆盖。

原始源码单元在优化与 ASan/UBSan 构建中各通过 166 场景、1,668 断言；渲染单元
另覆盖双素材包、普通/圣诞银行、全部 256 滤色、分块/透明度/裁切以及 44 项坏资源。
详细限制保留在原始 `source-unit-result.json`，LeakSanitizer 未启用。
正式素材仅含生成内容；历史 pilot 文件名与现有 output 文件名的对应关系及
源码单元的基线前提及测试守卫的小幅修改见英文部分。所有原版数据须另外提供。
