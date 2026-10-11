# 已绑定敌人的非致死色滤修复

基于 `before-enemy-nonlethal-filter` 冻结的蓝 v4、调试索引、玩家受击和旧 Talon13 源码。只改 `render_mirror.c` 的高清敌人滤色绘制；原引擎的受击、健康、link、死亡、冰冻、无敌和滤色清除代码不改。四个认可蓝 v4 文件与原27文件包字节不变；type10没有新增高清素材或绑定。

## 原问题与修复

旧的非零 enemy filter 分支恢复整块24×28原图矩形。该恢复会闭合到重叠的其他高清矩形；下方123/125受击时，tick892最终四部件区域的高清覆盖降到0，上方已经画出的85/87也被覆盖。绘制日志中的 mirrored1不能证明最终仍保留高清。

现在按原四象限调用，把 filter 作用于高清素材RGB，再按原顺序、原alpha合成。映射沿当前调色板连续插值，整数亮度端点遵守原 `filter | (source_index & 15)`，包括filter低位的OR语义；不对背景合成结果整体染色，不把高清素材量化成原像素图。filter完全来自当前原绘制调用，没有新计时器。原索引绘制继续照常执行。

缺失或未绑定的对象继续用原索引精灵的实际不透明像素绘制。未识别混合效果的局部恢复护栏保留，没有全面禁用回退。

## 有限验证

- 同一原始初始化、事件与输入：episode1、物理数据关卡9、seed0x5eed、静止不发射。蓝机器人属于索引段1，目标tick890；type10属于段0，tick150。
- 蓝四对象分别非致死和致死；另测四种单文件缺失、重复呈现和type10原素材的无伤/非致死/致死。受击为明确标注的原Pulse155调试射击夹具，原碰撞处理执行。
- 非致死在891碰撞damage1；892原filter208；893恢复，连续观察至913。原目标单独扣血、同link滤色传播、两对原link死亡规则保持。四个命中位置与原绘制时序、原游戏状态和RNG均对照修复前。
- 1648个逐象限完整矩形alpha合成核对，240个四部件整体绘制与最终合成核对；最终核对包括后续原绘制和既有已识别RGBA爆炸。401项整组原生输出/完整窗口与HUD核对。四种缺失各有原滤色不透明像素对照。
- 下方受击的旧tick892高清子像素为0；修复后131840。上方受击的旧值32090；修复后131840。原样保留的后续爆炸/精灵写入会遮挡部分子像素，不能把整个矩形都算作高清对象。
- 实际生产程序的24个原生帧与只读观测程序逐像素相等。重复Present不改变游戏、滤色恢复、RGBA或旧13角控制时序。
- 旧Talon13的420 tick游戏、RGBA审计、视觉控制与原混合写入一致。现有970..999片段的14次未知效果恢复调用与修复前一致。
- 取生产函数原文编译验证12240个整数OR端点、65280个连续 ramp/alpha样本。索引重建仍为1053 tick、227个带命名空间素材、174855条原绘制引用、三个索引窗口；不是整关/全路径素材索引。

实际显示证据为已显示SDL1280×800窗口的Nearest、beforePresent读回。视频完整保留每个观察tick，含明确剪辑停留；不是实测FPS、Windows合成器/物理2K、手动游玩或全关卡/全效果验收。

## 独立回退与复现

`enemy-filter-only-keep-blue-debug-talon.patch` 只改该renderer，正向和反向源字节核对已通过。撤回它保留蓝v4、调试、旧Talon13和玩家受击修复：

```powershell
git apply --reverse --check 'C:\path\enemy-filter-only-keep-blue-debug-talon.patch'
git apply --reverse 'C:\path\enemy-filter-only-keep-blue-debug-talon.patch'
.\prototype\build-game.ps1
```

当前程序没有执行回退。完整源补丁基于aad5aca，另有独立技术检查点与本次前置冻结；不要复制更早的整份C覆盖调试成果。交付包不含exe、HDA或游戏数据，不推送GitHub。

使用本次更新来源的索引，或已交付索引的相同素材/段定位。15秒只是索引窗口，播放可继续跨窗口：

```powershell
python .\prototype\asset-index.py play --index 'C:\path\tyrian-e1-level9-index-filter-fix.json' --sheet newsh2.shp --id 85 --segment 1 --until 950
.\prototype\start-asset-debug.ps1 -Preset blue -Capture -Until 914
.\prototype\start-asset-debug.ps1 -Preset type10 -Capture -Until 174
```

暂停后可用控制队列 `hit 75` / `destroy 75` / `resume`，或按H/D选择预设目标；所有人工射击都有日志与窗口标识。type10仍为原素材。Talon实体v9的认可13角交付已到齐，作为下一个独立资源接入批次；本次没有混入。未认可的新蓝机器人候选不替换v4；底座与type10高清仍在后续队列。
