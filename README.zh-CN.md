[English](README.md) | [简体中文](README.zh-CN.md)

# OpenTyrian2000 高清视觉分支

本分支基于 OpenTyrian2000 / OpenTyrian，逐步重绘高清视觉，保留原玩法、
逻辑坐标、碰撞、关卡数据、事件和随机数流程。
[原上游 README](README.md#upstream-readme-preserved) 完整保留。

## 当前范围与限制

- 已接入部分船机、敌人、武器/特效、分层地形、云和世界材质。有限的单人
  HUD 改造包括框架、武器标签、护盾条、模式指示和右下角连接结构。
- 手动游戏高清通过显式参数启用，仅限本地单人第一章的首关（物理关卡编号 9）；其他关卡保持原版。
  受控预览/素材调试仍是独立入口；厂商画面与分层标题使用下文的显式启动入口。
  普通无相关参数启动仍走原版显示。
- 未覆盖、缺失或不兼容的资源按各功能规则回退；暂停、帮助、选项仍用原版界面。
- 已验收的是文档列明的有限 Linux 场景，包括原生 2×/4× 检查；不代表全游戏、
  全关卡、GPU/全屏或性能认证。最新修改尚未完成 Windows 运行验收。
- 固定 MODE/SHIELD/ARMOR 文字、有限范围的游戏内小字体及火力、能量、粗分组装甲条已接入；
  厂商 PIC10/PIC12 可通过独立参数启用；另一个组合包增加 PIC4 背景与两张标题标志，
  标题中的版本、菜单、高亮及光标仍由原版绘制。标题已通过 8 个有限场景、13 次实际引擎运行，
  加一次合并后的逐帧一致性回归，覆盖原生 2×/4×、光标、返回标题与真实空闲交接。厂商画面已通过实际引擎在
  SDL dummy/software 下的原生 2×/4× 输出检查，实体窗口/GPU 验收仍须另行进行。

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
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --manual-hd-assets=/absolute/path/to/repo/assets/hd/packs/packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test
```

该参数仅启用 8 倍源素材、既有混合处理与 Talon 的 13 姿态显示。按键、随机种子、
生命值、受伤、死亡、重新开始、存档及关卡推进仍由原版控制；没有自动开火、自动移动、
强制装备或运行时限。适用范围仅为本地单人第一章 TYRIAN 首关（物理关卡编号 9，
不是菜单中的第九关）。标题演示、双人/Galaga 模式和其他关卡使用原版显示。
缺失或不兼容的资源按原有规则回退；暂停、帮助、设置及离开关卡/返回菜单的渐变可使用原版显示。

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
已有内容但没有专用标记的目录会被拒绝，避免覆盖个人存档。无需 Python 或诊断包装器；
原版数据及 Windows 依赖仍需另行提供。

这是有限的首关手动模式，不是完整战役高清认证。Windows 实机/设备运行验收须与源码、
构建检查分开报告。[有限验收与待验证项](docs/MANUAL_HD_ACCEPTANCE.md)记录具体源码/单元/构建结果
及四次无实体窗口的合成 SDL 事件引擎运行。[有限预览入口](prototype/start-actual-preview.ps1)与
[素材调试入口](prototype/start-asset-debug.ps1)仍为受控重播工具，详见[调试操作](docs/ASSET_DEBUG.md)。

### 可选厂商启动画面

Release/NDEBUG 构建可在原有本地启动流程中使用两张已审阅的厂商画面：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-manufacturer-v1
```

请从仓库根目录运行，或把素材路径改为绝对路径。这个双图目录只替换 PIC10（XSIV GAMES）
与 PIC12（ECLIPSE）；标题、菜单及之后的手动游戏保持各自原有显示，除非另行显式启用高清。
某一张资源缺失、损坏或不兼容时，只让该张回退到原版；原淡入淡出与输入跳过代码保持不变。
不能与联网、render-test 或 asset-debug 模式组合使用，程序会拒绝这些组合。
不加该参数时，普通启动保持原版。Debug 构建的原启动流程本就跳过厂商画面，因此会拒绝该参数。

[启动画面契约与检查](docs/STARTUP_MANUFACTURER.md)记录已通过的源码/单元检查及 12 次
有限实际引擎运行：原生尺寸 2×/4×、原淡入淡出、队列按键/持续鼠标按下跳过、
缺失资源逐张回退和原版标题衔接。运行使用 SDL dummy/software；实体桌面/GPU、全屏、
实体手柄和 Windows 运行仍未验收。带观测开销的录像/计时不证明原速或帧率。
该参数不代表手动游戏已支持高清。

### 可选分层标题

独立组合包保留两张厂商画面，并加入 PIC4 背景、独立移动的 Tyrian 与 2000™ 标志：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-v1
```

保留原 29 个位置、分开的画面/UI 淡入淡出、版本、菜单高亮与光标写入。
缺失资源逐层回退；所有权或源状态异常时，整次标题显示回退原版。原双图目录不变。
[标题契约与检查](docs/STARTUP_TITLE.md)记录已通过的 8 个场景、13 次实际引擎运行：
原生 2×/4×、各层独立缺失回退、键盘/鼠标菜单与光标擦除、帮助界面及返回静止标题、
淡入期间输入、真实 30 秒空闲后的演示交接。另一次无新增媒体的合并回归中，
142 次呈现的原始状态和输出全部一致。使用 SDL dummy/software，计时包含观测开销。
标题显式 CPU 常驻存储峰值为 12,075,752 字节，另有标称 4,096,000 字节 SDL 纹理。
实体 GPU/全屏、Windows、实体手柄及演示游戏过程仍未验收；游戏内高清选择方式不变。

Windows 使用[构建脚本](prototype/build-game.ps1)，环境与验收边界见
[Windows 说明](docs/WINDOWS_HANDOFF.md)。提供这些入口不代表最新版本已经通过
Windows 构建或运行验收。

### 可选标题菜单字体试验

独立的六文件包在现有厂商与分层标题素材上增加已审阅的中号字体 V3.1：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-menu-v1
```

原生2×仅对菜单字形做覆盖率整合，原生4×保留清晰的标准字形；其他输出尺寸使用
原版菜单文字，标题美术继续保留。仅主标题的七行菜单使用新字形。原始索引绘制、
字宽、居中、点击区域、输入、调色板
渐变及光标仍由原版代码决定。字体资源缺失或不兼容时，整个菜单恢复原版文字，
有效的标题美术仍然保留。版本文字、设置/读档界面与游戏内 HUF1 均不变。
原五文件标题包及默认素材选择不变。[协议与当前检查](docs/TITLE_MENU_FONT.md)区分
已通过的源码/合成测试与仍待进行的实际引擎视觉和交互验收。

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

九文件兼容包保留已发布的六个厂商、标题与主菜单资源，并增加设置菜单的大号、
中号及小号字体：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

仅在精确原生最近邻 2×/4× 下增强 Setup、Graphics、Sound 及其选项列表。
PIC2 背景、音量条、光标、索引文字、字宽、输入与保存设置仍保持原样。SFN1 文件
缺失或不兼容时，整个设置菜单使用原版字体，有效标题资源仍可使用；滤镜和比例
拉伸输出同样回退。已有资源包及默认选择不变。
[协议与有限验收](docs/settings-font-v1/ACCEPTANCE.txt)包含 SDL dummy/software 下
实际引擎的配对操作、渐变与生命周期检查，以及源码、消毒器和作者静态画面审阅。
未声明实体 GPU/显示器或 Windows 运行验收。可用以下命令重建完全相同的九文件包：
`python3 prototype/settings_font_bundle.py --output /absolute/new/directory`。

同一 `startup-title-settings-v1` 资源包现也支持有限范围的读档界面字体，遇到不支持的存档名或缩放方式时整帧回退至原版；详见[读档字体使用说明](docs/load-font-v1/USAGE.txt)。

同一 `startup-title-settings-v1` 包现也覆盖人数/模式、章节、难度（含原版解锁行）
及限时战斗选择。这四个界面的字体按实际输出与视口映射，已通过原生 2×/4× 和
1365×767 非整数尺寸的软件渲染有限检查。主标题、设置和读档的既有尺寸限制不变。
同一资源包现也增强普通单人模式下的游戏前主选单及 Upgrade Ship 分类页文字；
物品购买页面和原版飞船、背景美术保持不变。继续使用相同 `--startup-assets`
目录及既有大号/中号 SFN1 文件，无需新美术。
[选择界面范围、光标回退与验收边界](docs/selector-font-v1/NATIVE-ACCEPTANCE.txt)。
