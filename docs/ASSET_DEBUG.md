# 素材调试与 15 秒片段索引（首个可运行版本）

## 当前资源包与历史检查点

当前预览和调试入口分别保留自己的 `head-v1` 默认包。`-BeforeGreenHead`、
`-BeforeGreenV2`、`-BeforeGreenTrail`、`-BeforeShield`、`-BeforeWhiteSmoke`、
`-BeforeLargeGround`、`-BeforeImpact` 与 `-BeforeLargeAir` 对应的 16 个旧阶段目录
已退役；脚本会在创建运行目录或启动程序前提示退役，不会静默改用新包。
普通调试请省略这些参数。历史对照请先按[恢复与外部重建说明](RETIRED_HD_PACKS.md)
恢复准确的旧包，再通过 `-Assets` 指向独立目录。更早的外部 `runtime-hd-assets`
选择器只有在对应本地输入存在时才可使用。

下文的首版默认帧数、文件数量、冻结回退点与验收记录均为历史检查点说明；
其有限输入、时间与验收边界仍按原记录保留，不能作为当前默认资源数量的声明。

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

Default debug and preview launches materialize external current pack views before starting: all 142 mapped current gameplay resources (including Pulse, HUD and NEWSH2 base267) replace their frozen counterparts; the other 499 files stay unchanged. Python 3 + Pillow are required; explicit asset overrides and historical selectors keep their selected inputs. No new global/HUD routing flags are added. See [current-view workflow and validation limits](CRAFT267_SINGLE_SOURCE_WORKFLOW.md#current-preview-and-manual-entrypoints).

## 跨平台 Python 片段入口与外部数据路径

`asset-index.py play` 现在直接使用当前 Python 解释器调用
`prototype/start-asset-debug.py`，不再要求 `powershell.exe`。这是片段索引所需的
`custom + tick` 子集，不替代 PowerShell 入口的 preset/event/reference/index-only
等功能；原 PowerShell 入口保持不变。

```sh
python prototype/asset-index.py play --segment 1 --exe "/path with spaces/opentyrian" --assets "/path/current-debug-pack" --data "/path/original-tyrian2000" --headless --running --capture --capture-start 522 --capture-count 4 --window-only --until 526
python prototype/run-controlled.py --exe "/path/opentyrian" --assets "/path/current-debug-pack" --data "/path/original-tyrian2000" --modes classic,8 --ticks 600
python prototype/asset-index.py build --run "/path/observed-run" --output "/path/index.json" --assets "/path/current-debug-pack" --data "/path/original-tyrian2000"
```

Windows PowerShell 使用 `python` 或 `& 'C:\path to\python.exe'` 调用上述 Python
脚本，并把示例路径换成本机路径。实际进程以参数数组执行，不经过 shell。
`play --no-launch` 仅打印启动命令（Windows 为 PowerShell 格式，其他平台为
POSIX shell 格式），不会生成资源包或启动游戏；显式路径仍会预校验。

默认 EXE 仍为仓库内 `opentyrian-x64-Release.exe`，默认原版数据仍为仓库父目录
`runtime-data/tyrian2000`。Linux 构建请显式传 `--exe`。`play` 省略 `--assets` 时
仍使用现有构建器生成当前 debug view；显式指定可复用已有外部包。
`--data` 必须是存在的目录并含 `tyrian1.lvl` 文件（与引擎的数据目录探测一致），
这不是完整游戏数据的完整性认证，后续缺少文件仍由引擎报告。
索引 `build --data` 从同一个显式目录读取来源哈希；必须指向采样时实际使用的数据。

新 Python 调试入口每次运行创建独立目录、日志和 `asset-debug-run.json`，在非
Windows 平台同时隔离 HOME/XDG_CONFIG_HOME 并放置相应配置，避免使用真实用户
存档；Windows 保留 cwd 配置。退出码 75 触发新进程重播，每次重新读取素材；
默认最多重播 20 次，独立入口可用 `--max-replays 0..1000` 调整，耗尽时明确报错并
返回 75。其他退出码原样返回。`run-controlled.py` 本批仅补齐数据路径校验与传递，
其原有输出命名/复用规则不变，不等同于新入口的完整隔离实现。

验证边界：聚焦测试使用 mock 进程检查参数、路径含空格/Unicode、错误路径、
捕获参数、配置隔离、元数据及重播退出码；不以这些测试宣称 Windows 实机游戏
或视觉验收通过。

另完成一次 Linux 实际游戏冒烟：使用现有 C 可执行程序、原版数据和当前 debug
view，显式传入三个路径，dummy/software 模式下到达 tick232，正常结束于236个
逻辑 tick（退出0），输出232–235共4张 SDL窗口 BMP及运行元数据。此结果验证新
Python入口衔接，不是 Windows 实机验收，也不代表新素材视觉质量验收。
