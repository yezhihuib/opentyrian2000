# 素材调试与 15 秒片段索引（首个可运行版本）

在现有本地高清原型上使用；不下载游戏数据，不自动构建，不修改素材 ID 或关卡逻辑。蓝机械 v4 仍是冻结的整合进度，本交付验证调试入口，不代表蓝 v4 全部视觉状态已验收。

## 直接进入与暂停操作

在 PowerShell 中进入 `opentyrian2000-dev`：

```powershell
.\prototype\start-asset-debug.ps1 -Preset blue
```

从原始初始化开始确定性快进到 tick890，显示目标帧并暂停。Space/P 暂停或继续，N/句点推进一个 tick，R 用新进程重新初始化、快进并重新读取外部素材，Esc 退出。重播期间窗口标题和关卡 HUD 明确标记 ASSET DEBUG；R 需要这个启动脚本，直接运行 exe 时 R 返回退出码75。

`-Preset turret` 进入 tick232；`-Preset type10` 进入 tick150，使用原素材，高清整合仍排队。也可 `-Preset custom -Tick 1044`，或 `-Preset custom -Event 129` 按原始1基事件序号进入事件执行后的首帧；Tick 和 Event 不能同时指定。`-Talon13` 显式启用已验收13姿态，默认5帧。启动脚本无构建/下载动作。

H/D 对预设中的活动原敌人注入原 Pulse155 射击，走原碰撞、健康和联动死亡路径；此时日志及标题标记 SHOT FIXTURE/ARTIFICIAL。自然路线索引不包含这些注入，不能把注入录像当作自然玩法验收。

## 片段 ↔ 素材查询、定位、替换

```powershell
$debugPython = 'C:\Program Files\Python311\python.exe'
& $debugPython .\prototype\asset-index.py list
& $debugPython .\prototype\asset-index.py list --segment 1
& $debugPython .\prototype\asset-index.py find --sheet newsh2.shp --id 85
& $debugPython .\prototype\asset-index.py play --segment 1
& $debugPython .\prototype\asset-index.py play --sheet newsh2.shp --id 85
```

段号从0开始。段1从 tick522 进入；素材 `enemy:newsh2.shp:85` 出现在段1和2，素材定位进入首次引用 tick876。可同时 `--segment 2 --sheet newsh2.shp --id 85` 定位该段内首次引用 tick1044。按 P 继续即可越过15秒分界；分段是查询窗口，没有15秒播放硬停。默认安全上限6000 tick，原路线自然结束会更早停止；`--until` 可指定60..6000，并必须大于目标 tick。`--no-launch` 只打印可执行启动命令。

```powershell
& $debugPython .\prototype\asset-index.py replace --sheet newsh2.shp --id 85 --hda 'C:\path\approved-enemy-newsh2-85-8.hda' --assets 'C:\path\existing-pack'
& $debugPython .\prototype\asset-index.py list --segment 1 --assets 'C:\path\existing-pack'
& $debugPython .\prototype\asset-index.py play --sheet newsh2.shp --id 85 --assets 'C:\path\existing-pack'
```

replace 仅替换已有绑定的外部 HDA，核对原ID、密度、尺寸、anchor和RGBA长度；拒绝不匹配文件。已有目标保存在素材包的 `.asset-debug-backups`。播放同一目标或 R 重新加载。同sheet+ID歧义时加 `--category enemy`；未绑定的type10等仍需后续代码整合。查询状态说明“文件可用”，不承诺每种遮挡/效果都高清化。实际替换测试只修改独立测试包，已接受素材包保持原字节。

## 时间口径与覆盖截止

索引时间是**配置逻辑时间**：每 tick 记录原引擎的 `frameCountMax * delayPeriod`，其中 `delayPeriod = delaySpeed * ((12.0f / 14318180.0f) * 1000.0f)` 毫秒，保留C float舍入。本次记录每 tick 都是 frameCountMax=2、delaySpeed=0x4300，实际时长约 **28.750022888 ms**。tick0从0开始；tick t 的 start 是前 t 个 tick 的和，end 包含 tick t；段号按 `floor(start_ms / 15000)` 生成，定位直接使用记录的整数 tick，绝不从墙钟秒数反推。

| 段号 | tick（含两端） | 配置逻辑时间范围 | 覆盖 |
| --- | --- | --- | --- |
| 0 | 0..521 | 0..15.007512 秒 | 首窗口 |
| 1 | 522..1043 | 15.007512..30.015024 秒 | 第二窗口 |
| 2 | 1044..1052 | 30.015024..30.273774 秒 | 仅最后约0.258750秒 |

离散 tick 可能跨过窗口边界，属于其 start 所在窗口。tick890 的 start≈25.587520秒、end≈25.616270秒。实测顺序测试到该帧约54.316433墙钟秒，快进约0.769559秒，省约53.546874秒；这是同机测试的启动/等待/渲染/记录成本，**不是54秒的关卡逻辑时间或实测FPS**。短视频按12fps编辑播放，暂停停留及字幕也不能用于定位段号。

固定配置：episode1、TYRIAN 原始关卡数据 physical-level9（不是菜单中的“第9关”），种子0x5eed，船1、前武器1、power1，现有 enemy-hit 输入（静止、不发射，原自然敌人/子弹）。当前采集自然演示在 next_tick1053 停止，覆盖截止30.273774逻辑秒，**不是全关卡通关**。共227个带类别+sheet+ID命名空间的素材、174855次原绘制引用。记录矩形与原视野相交的引用，后续遮挡可能盖住它；不含菜单/字体/程序化粒子。其他输入、难度、种子或后续关卡未被本索引覆盖。

## 重新采集与保存隔离

```powershell
.\prototype\start-asset-debug.ps1 -Preset custom -IndexOnly -Until 1100 -Headless
# 使用输出中 ASSET DEBUG run 的实际目录：
& $debugPython .\prototype\asset-index.py build --run 'C:\path\controlled-runs\asset-debug-实际目录' --output '..\asset-debug-evidence\tyrian-e1-level9-index.json'
```

当前 build 明确只支持上述固定路线；不会将其他物理关卡冒充此索引。保存源/执行文件/数据/轨迹哈希、seed/input和覆盖信息；依赖是已有运行数据及外部包。

每次调试建立独立工作目录并禁用调试模式的配置、存档及高分写入。已检查暂停/重入/射击及最终3个入口：opentyrian.cfg字节不变、未创建tyrian.cfg/sav；外部既有保存文件未变化。普通启动无调试参数，进入原启动界面并正常关闭，正常写配置仍在隔离测试目录工作；另有420 tick普通13姿态原型回归，逻辑/RNG/RGBA及控制器记录与此前验收完全一致。未宣称完整手工游玩、战役存档读写或Windows合成器/物理2K测试。

## 源码与独立回退

交付包含完整原型源码补丁（基线 `aad5aca01af139c0b089237c38ef765f7a84355d`）、仅本次调试改动的 `opentyrian-asset-debug-only.patch`、冻结蓝v4的旧源码补丁与哈希、操作说明/索引/验证/视频。补丁正向和反向都在临时目录验证原始字节；没有向GitHub推送或创建PR。包中不含可执行文件、HDA或游戏数据。

在与当前交付源字节一致且没有后续编辑的副本中，仅回退本次调试：

```powershell
git apply --reverse --check 'C:\path\opentyrian-asset-debug-only.patch'
git apply --reverse 'C:\path\opentyrian-asset-debug-only.patch'
```

如check失败，保留现场差异并核对，不强行覆盖。冻结的本地完整回退点是 `checkpoints/blue-four-v4-before-asset-debug`。源文件更改后需用已有工具链执行 `.\prototype\build-game.ps1`；正常启动脚本、默认15素材/5船帧、固定flare145和已验收Talon13控制器均保留。

