[English](README.md) | [简体中文](README.zh-CN.md)

# OpenTyrian2000 高清视觉分支

本分支基于 OpenTyrian2000 / OpenTyrian，逐步重绘高清视觉，保留原玩法、
逻辑坐标、碰撞、关卡数据、事件和随机数流程。
[原上游 README](README.md#upstream-readme-preserved) 完整保留。

## 当前范围与限制

- 已接入部分船机、敌人、武器/特效、分层地形、云和世界材质。有限的单人
  HUD 改造包括框架、武器标签、护盾条、模式指示和右下角连接结构。
- 游戏内高清通过受控预览/素材调试入口启用；厂商画面与分层标题使用下文的显式启动入口。
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

最后一条命令是普通原版显示启动。游戏内高清使用独立的
[有限预览入口](prototype/start-actual-preview.ps1)或
[素材调试入口](prototype/start-asset-debug.ps1)，需按说明准备外部数据和依赖。
这些是受控重播工具，尚非完整战役的手动操作高清发行版。参见
[调试操作](docs/ASSET_DEBUG.md)与
[有限场景启动示例](docs/FIRST30_HD_COVERAGE.md#later-windows-acceptance)。

### 可选厂商启动画面

Release/NDEBUG 构建可在原有本地启动流程中使用两张已审阅的厂商画面：

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-manufacturer-v1
```

请从仓库根目录运行，或把素材路径改为绝对路径。这个双图目录只替换 PIC10（XSIV GAMES）
与 PIC12（ECLIPSE）；标题、菜单及之后的手动游戏继续使用现有原版显示。
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
