[English](README.md) | [简体中文](README.zh-CN.md)

# OpenTyrian2000 高清视觉分支

本分支基于 OpenTyrian2000 / OpenTyrian，逐步重绘高清视觉，保留原玩法、
逻辑坐标、碰撞、关卡数据、事件和随机数流程。
[原上游 README](README.md#upstream-readme-preserved) 完整保留。

## 当前范围与限制

- 已接入部分船机、敌人、武器/特效、分层地形、云和世界材质。有限的单人
  HUD 改造包括框架、武器标签、护盾条、模式指示和右下角连接结构。
- 手动游戏高清通过显式参数启用，适用于本地单人第一章。保留原有物理关卡 9 支持，
  新增普通数据、普通 Full Game 中 Hard+ 首关变体（物理关卡 15）。其他关卡和排除模式
  沿用既有显示方式。受控预览/素材调试仍是独立入口；厂商画面与分层标题使用下文的
  显式启动入口。普通无相关参数启动仍走原版显示。
- 未覆盖、缺失或不兼容的资源按各功能规则回退；暂停、帮助、选项仍用原版界面。
- 已验收的是文档列明的有限 Linux 场景，包括原生 2×/4× 检查；不代表全游戏、
  全关卡、GPU/全屏或性能认证。最新修改尚未完成 Windows 运行验收。
- 固定 MODE/SHIELD/ARMOR 文字、有限范围的游戏内小字体及火力、能量、粗分组装甲条已接入；
  同一个完整启动资源包包含厂商 PIC10/PIC12、PIC4 背景、两张标题标志，以及下文说明的
  主菜单、设置、读档、选择与游戏前菜单字体。标题已通过 8 个有限场景、13 次实际引擎运行，
  加一次合并后的逐帧一致性回归，覆盖原生 2×/4×、光标、返回标题与真实空闲交接。厂商画面已通过实际引擎在
  SDL dummy/software 下的原生 2×/4× 输出检查，实体窗口/GPU 验收仍须另行进行。

- 敌方坦克弹146/147已通过有限原生2×/4×与成对回退检查；共5次进程启动，
  包含保留的1次夹具失败及修正后的替代运行。具体范围见[验证记录](docs/enemy-tank-shell-pair-v1/VALIDATION.md)。

- 普通模式玩家 Vulcan 弹头 67/70 已完成 P1/P7 原生 2× 成对检查：4 次运行，
  每次 90 个逻辑 tick；全部 11 档火力另由源码单元测试覆盖，原始索引行为保持一致。
  数值及作者审阅在此范围内通过，具体见[验证记录](docs/player-vulcan-two-v1/README.md)。
  后续[有限平滑阴影修复](docs/player-vulcan-shadow-v1/README.md)也已通过两次新的
  P1/P7 各 90 tick 对照检查，复用原有实际截图；该次修复仅改变这两种普通玩家弹头的阴影，
  负横坐标可能跨行的调用仍保留经典回退。

- 后置强化道具 534 已接入三相高清本体，共用的固定 145 拾取特效保持原版。
  有限原版按键检查共 3 次运行、22 张原生 2×/4× 图，实际奖励为空后武器的现金回退。
  具体范围见[验证记录](docs/rear534-three-v1/README.md)。

- Data 方块（记录 513）增加十二个原创本体明暗阶段，资源异常时整组回退原版。
  有限原版按键流程、原生 2× 画面及四张原生 4× 本体抽查已通过数值检查与作者审阅。
  具体见 [Data 方块范围与验证](docs/data513-twelve-v1/README.md)。

- 组合源码共存检查已合入后置道具 534、Data 513、Vulcan 弹头 67/70 及平滑阴影，
  标准美术资源保持不变。四个独立的有限 Linux 场景通过检查：新增 69 张原生 2× 图
  和 12 张 INDEX8 图与各组保留的最终候选完全一致；状态及轨迹除墙钟计时外也完全一致。
  此检查验证各组共同安装后的独立场景，不涵盖同场同时出现、完整关卡或 Windows 验收。
  具体见[组合检查范围与验证](docs/qualified-family-coexistence-v1/README.md)。

- Protron 为普通玩家 ID 225/244/226 使用三个独立创作的阴影覆盖资源，
  既有弹头字节及原始索引写入保持不变。内部保留原有完整阴影强度，
  仅轮廓边缘采用部分覆盖。新的 P1/P6/P11 基线/候选成对检查通过数值及有限作者审阅：
  共 6 次 Linux SDL dummy/software 运行，每次 90 tick，保留 36 张原生 2× 图
  和 36 张 INDEX8 图。原始状态、RNG 和索引对照完全一致；重叠的半透明弹头像素
  可因底层阴影变化而改变。见[范围与验证记录](docs/player-protron-shadow-three-v1/README.md)。

- 普通前置 Multi（武器端口 2）新增八个原创玩家弹头。P2/P4/P7/P11 原生 2×
  基线/候选成对检查已通过数值及作者审阅：共 8 次运行，每次 90 个逻辑 tick，
  保留 48 张原生图和 48 张
  INDEX8 图。八个新 ID 均在固定截图窗口中有可见见证，部分单帧存在裁切。
  后续平滑阴影扩展复用这八个既有弹头的 alpha：新增 P2/P4/P7/P11 各 90 tick
  运行，与保留的仅弹头候选组成 24 对原生 2× 画面；原始状态、RNG 及 INDEX8
  对照完全一致，数值与作者画面审阅在此有限范围内通过。该次 Multi 扩展保持
  既有 58/59、敌方及 Protron 的运算不变，但重叠的半透明像素可因底层阴影变化而改变；
  全部火力档、圣诞模式及其他共用路径仍是独立的源码/单元覆盖。
  具体见[范围与验证记录](docs/player-front-multi-eight-v1/README.md)。

- 普通数据 Hard+ 首关夜间高清保留原版索引光锥，对非亮区原创细节使用有界、
  以调色板为锚点的偏差收缩，现金文字局部保留原版。源码/单元测试及一次未添加保护的
  Hard 开场检查通过：23 次完成帧、5 张实际 640×400 图、4 组独立复核的索引/调色板数据。
  另一次受保护中段/Boss 诊断已通过五个选定窗口，运行至 7,429 tick，抽查 360 次索引核对。
  这是有限渲染验收，不代表自然 Hard 生存、完整通关或 Windows 验收。
  详见[范围与验证](docs/firstlevel15-night-v1/README.zh-CN.md)。

- 圣诞模式中，九个与普通数据不同的敌方弹体 ID 保留原版素材，146/147 坦克弹仍可高清显示。
  此独立回退通过源码/单元检查，与普通数据的夜间扩展分别验收。
  详见[范围与历史记录](docs/christmas-enemy-fallback-v1/README.md)。

## 构建与体验

需另行准备原版 Tyrian 2000 数据，仓库不包含这些数据；请放在仓库之外。
获取说明见[原上游 README](README.md#upstream-readme-preserved)。

Linux 构建需要 C 编译器、make、pkg-config、SDL2 和 SDL2_net；素材校验还需要
Python 3 与 Pillow。构建入口为 [Makefile](Makefile)：

```sh
make
python3 prototype/build-hd-assets.py
./opentyrian2000 --data=/absolute/path/to/tyrian2000
```

最后一条命令是普通原版显示启动。

### 手动首关高清

正常进入标题菜单，手动选择 New Game / 第一章：

```sh
python scripts/build_current_craft267.py view --kind preview --output /absolute/path/to/new-current-preview
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --manual-hd-assets=/absolute/path/to/new-current-preview
```

该参数启用 8 倍源素材、既有混合处理与 Talon 的 13 姿态显示。按键、随机种子、
生命值、受伤、死亡、重新开始、存档及关卡推进仍由原版控制；没有自动开火、自动移动、
强制装备或运行时限。适用范围为本地单人第一章：原有物理关卡 9，以及普通数据、
普通 Full Game 中原版 Hard+ 难度选中的物理关卡 15。这些是首关内部变体编号，
不是菜单关卡序号。标题演示、双人/Galaga 模式和其他关卡使用原版显示。
缺失或不兼容的资源按原有规则回退；暂停、帮助、设置及离开关卡/返回菜单的渐变
可使用原版显示。

现有手动验收报告记录的是先前的物理关卡 9 检查点；新增路径另见
[Hard+ 夜间范围与验证](docs/firstlevel15-night-v1/README.zh-CN.md)。Windows 验收仍待完成。

不能与任何 `--render-*` / `--asset-debug*` 参数、联网、record、constant、death 或 loot
模式混用（包含旧式参数），程序会拒绝这些组合。Release/NDEBUG 构建可独立追加
`--startup-assets=/absolute/path/to/repo/assets/hd/packs/startup-title-settings-v1`
启用厂商/标题/设置/读取界面的素材。素材路径不通过 `--data` 查找。

Windows 使用独立的[手动启动脚本](prototype/start-manual-hd.ps1)：

```powershell
& .\prototype\start-manual-hd.ps1 -DataDirectory 'C:\Games\Tyrian 2000'
```

脚本从自身仓库位置定位 EXE 和已审阅的游戏素材包，使用
`%LOCALAPPDATA%\OpenTyrian2000-HD\manual-first-level` 下持久的独立配置/存档目录。
仅在配置不存在时创建窗口化 2x/Integer 设置，之后保留用户设置和存档。
`-InitialScale 4x` 仅对新配置生效；已有配置请通过游戏内设置修改。可使用绝对路径
覆盖 `-Executable`、`-AssetsDirectory`、`-StartupAssetsDirectory`、`-ProfileDirectory`。
已有内容但没有专用标记的目录会被拒绝，避免覆盖个人存档。默认 current pack 视图生成需要 Python 3 和 Pillow，详见
[NEWSH2 base267 单源入口](docs/CRAFT267_SINGLE_SOURCE_WORKFLOW.md)；
原版数据及 Windows 依赖仍需另行提供。

这是有限的首关手动模式，不是完整战役高清认证。Windows 实机/设备运行验收须与源码、
构建检查分开报告。[先前有限验收与待验证项](docs/MANUAL_HD_ACCEPTANCE.md)记录物理关卡 9 的源码/单元/构建检查点
及当时四次无实体窗口的合成 SDL 事件引擎运行。[有限预览入口](prototype/start-actual-preview.ps1)与
[素材调试入口](prototype/start-asset-debug.ps1)仍为受控重播工具，详见[调试操作](docs/ASSET_DEBUG.md)。

### 独立的 ASTEROID1 小行星开关

`--asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1` 仅替换普通数据版第一章
物理关卡 1（ASTEROID1，战役段落 5）的十五组有限素材：十块拼接灰色陨石、两组四块拼接陨石、
记录 135–137、260–262、263–265、266–268、317–324 各自共享的八种静态陨石，以及记录 282 的金色外壳与三态宝石脉冲，以及记录 286 的固定岩体与四态连续宝石脉冲，以及记录 284 的静态叉形金属飞行器，以及记录 545 的银灰色红底尖静态胶囊敌机。其余画面保持原版。
仍通过普通菜单和战役流程进入，不会自动选关或代玩。它不能与已有手动高清开关、
渲染诊断开关同时使用；物理关卡 2 和排除模式仍保持原版。
见[十块拼接范围](docs/asteroid1-ten-v1/README.md)和[新增两组静态随机陨石与有限验收](docs/asteroid1-random43-85-v1/README.md)。另见[大、小静态随机陨石与有限验收](docs/asteroid1-random123-95-v1/README.md)。另见[三种小型静态随机陨石与有限验收](docs/asteroid1-random114-133-152-v1/README.md)。另见[连续随机陨石宝石脉冲与有限验收](docs/asteroid1-random286-v1/README.md)。另见[定时叉形金属飞行器与有限验收](docs/asteroid1-fork284-v1/README.md)。另见[定时胶囊敌机与有限验收](docs/asteroid1-capsule545-v1/README.md)。这些只是十五组有限的第二关素材，
不代表第二关全部完成或通过 Windows 实机验收。

### 可选外部 MP3 音乐

添加 `--music-dir`，即可用自己的 MP3 替换指定曲目：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --music-dir=/absolute/path/to/my-music
```

文件名须使用小写 `track01.mp3` 至 `track41.mp3`；例如 `track18.mp3` 对应
**Tyrian, The Level**。文件缺失、被拒绝或超出限制时，该曲目单独回退到原版 FM。
不加参数时，原版音乐路径及首次选曲行为保持不变。仍须提供完整原版数据，
包括 `music.mus`，用于原有时间线、渐变与回退。

Windows 手动启动脚本支持已有目录的绝对路径，也支持路径中的空格和中文：

```powershell
& .\prototype\start-manual-hd.ps1 -DataDirectory 'C:\Games\Tyrian 2000' `
  -MusicDirectory 'C:\Music\我的配乐'
```

MP3 在播放前完整解码，立体声混合为现有的单声道输出，并转换到声卡实际采样率。
原曲结束、循环标志和音量渐变仍由原版控制，MP3 文件末尾另行循环。
每个输入文件最多 32 MiB、时长最多 10 分钟；最终 PCM 最多 64 MiB，受跟踪的
临时分配总量最多 256 MiB。不保证所有 MP3 都能无缝循环。个人音乐须保留在
仓库和公开包之外。完整曲目表、控制规则、限制与验收边界见
[外部音乐说明](docs/EXTERNAL_MUSIC.md)。

### 可选厂商启动画面

Release/NDEBUG 构建可在原有本地启动流程中使用两张已审阅的厂商画面：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

请从仓库根目录运行，或把素材路径改为绝对路径。当前保留的完整资源包包含 PIC10（XSIV GAMES）
与 PIC12（ECLIPSE）、分层标题和下文说明的界面字体；该参数本身不启用游戏内高清。
某一张资源缺失、损坏或不兼容时，只让该张回退到原版；原淡入淡出与输入跳过代码保持不变。
不能与联网、render-test 或 asset-debug 模式组合使用，程序会拒绝这些组合。
不加该参数时，普通启动保持原版。Debug 构建的原启动流程本就跳过厂商画面，因此会拒绝该参数。

[历史启动画面契约与检查](docs/STARTUP_MANUFACTURER.md)记录已通过的源码/单元检查及 12 次
有限实际引擎运行：原生尺寸 2×/4×、原淡入淡出、队列按键/持续鼠标按下跳过、
缺失资源逐张回退和原版标题衔接。运行使用 SDL dummy/software；实体桌面/GPU、全屏、
实体手柄和 Windows 运行仍未验收。带观测开销的录像/计时不证明原速或帧率。
该参数不代表手动游戏已支持高清。

### 可选分层标题

同一完整启动资源包包含两张厂商画面、PIC4 背景、独立移动的 Tyrian 与 2000™ 标志：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

保留原 29 个位置、分开的画面/UI 淡入淡出、版本、菜单高亮与光标写入。
缺失资源逐层回退；所有权或源状态异常时，整次标题显示回退原版。旧的子集目录已退役，
历史恢复与重建方法见[资源包退役说明](docs/RETIRED_HD_PACKS.md)。
[历史标题契约与检查](docs/STARTUP_TITLE.md)记录已通过的 8 个场景、13 次实际引擎运行：
原生 2×/4×、各层独立缺失回退、键盘/鼠标菜单与光标擦除、帮助界面及返回静止标题、
淡入期间输入、真实 30 秒空闲后的演示交接。另一次无新增媒体的合并回归中，
142 次呈现的原始状态和输出全部一致。使用 SDL dummy/software，计时包含观测开销。
标题显式 CPU 常驻存储峰值为 12,075,752 字节，另有标称 4,096,000 字节 SDL 纹理。
实体 GPU/全屏、Windows、实体手柄及演示游戏过程仍未验收；游戏内高清选择方式不变。

Windows 使用[构建脚本](prototype/build-game.ps1)，环境与验收边界见
[Windows 说明](docs/WINDOWS_HANDOFF.md)。提供这些入口不代表最新版本已经通过
Windows 构建或运行验收。

### 可选标题菜单字体试验

同一个九文件完整资源包在厂商与分层标题素材之外，包含已审阅的中号字体 V3.1 及设置/读档字体：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

原生 2×/4× 保留已验收的精确输出。其他有效输出尺寸仅对字体做覆盖率缩小和
预乘颜色/透明度的线性放大，标题美术仍使用原有采样。新字形仅用于主标题的七行菜单。
原颜色、索引文字、字宽、居中、点击区域、输入、调色板渐变及光标仍由原版决定。
字体资源缺失或不兼容时，整个菜单恢复原版文字，有效的标题美术仍保留。版本文字、
游戏内 HUF1 各自独立；设置/读档字体使用下文说明的同一完整包。不加参数时仍采用原版启动。
参见[历史协议与验收](docs/TITLE_MENU_FONT.md)及[当前输出适配检查与限制](docs/TITLE_MENU_FONT_PORTABILITY.md)，
后者包含实际 1920×1200 和非整数尺寸/留边的软件渲染检查。

## 资源与验证

[资源清单](assets/hd/manifest.json)记录当前默认素材包和哈希；旧报告中的数量
只对应当时的检查点。具体范围与回退规则见
[地形/电路甲板](docs/CIRCUIT10.md)、[森林材质](docs/FOREST13_WORLD_CANOPY.md)、
[HUD 框架](docs/GAMEPLAY_HUD_V5.md)、
[标签/护盾/模式指示](docs/GAMEPLAY_HUD_COMPONENTS_INDICATORS.md)及
[右下角 V2](docs/GAMEPLAY_HUD_CORNER_V2.md)及
[固定绿字](docs/GAMEPLAY_HUD_FIXED_TEXT.md)及
[游戏内小字体](docs/GAMEPLAY_HUD_DYNAMIC_FONT.md)及
[其他仪表](docs/GAMEPLAY_HUD_METERS.md)。

原上游介绍、数据说明、键位、联网说明及项目链接均保留在
[英文版的上游部分](README.md#upstream-readme-preserved)。
[许可证 COPYING](COPYING)与原有署名保持不变。

### 可选设置菜单字体

当前保留的九文件完整启动包包含六个厂商、标题与主菜单资源，以及设置菜单的大号、
中号及小号字体：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

增强范围仅为 Setup、Graphics、Sound 及其选项列表。原生最近邻 2×/4× 保留
已验收的合成路径；其他有效输出尺寸（含滤镜和比例适配）使用仅处理字体的新路径。
原颜色、PIC2 背景、音量条、光标、索引文字、字宽、输入与保存设置仍由原版决定。
SFN1 文件缺失或不兼容时，整个设置菜单使用原版字体，有效标题资源仍可使用。
不加参数时仍采用原版启动。参见[当前输出适配、回退与验证](docs/SETTINGS_LOAD_FONT_PORTABILITY.md)。
[协议与有限验收](docs/settings-font-v1/ACCEPTANCE.txt)包含 SDL dummy/software 下
实际引擎的配对操作、渐变与生命周期检查，以及源码、消毒器和作者静态画面审阅。
未声明实体 GPU/显示器或 Windows 运行验收。可用以下命令重建完全相同的九文件包：
`python3 prototype/settings_font_bundle.py --output /absolute/new/directory`。

同一 `startup-title-settings-v1` 资源包支持有限范围的读档界面字体，并使用相同的
输出适配路径。不支持的存档名、源数据或资源仍触发整帧原版回退。
[输出适配说明](docs/SETTINGS_LOAD_FONT_PORTABILITY.md)更新了[历史读档使用说明](docs/load-font-v1/USAGE.txt)中的尺寸限制。

同一 `startup-title-settings-v1` 包现也覆盖人数/模式、章节、难度（含原版解锁行）
及限时战斗选择。这四个界面的字体按实际输出与视口映射，已通过原生 2×/4× 和
1365×767 非整数尺寸的软件渲染有限检查。主标题、设置和读档的输出适配见上文。
同一资源包现也增强普通单人模式下的游戏前主选单及 Upgrade Ship 分类页文字；
物品购买页面和原版飞船、背景美术保持不变。继续使用相同 `--startup-assets`
目录及既有大号/中号 SFN1 文件，无需新美术。
[选择界面范围、光标回退与验收边界](docs/selector-font-v1/NATIVE-ACCEPTANCE.txt)。
