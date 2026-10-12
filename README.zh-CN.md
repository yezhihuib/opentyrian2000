[English](README.md) | [简体中文](README.zh-CN.md)

# OpenTyrian2000 高清视觉分支

本分支基于 OpenTyrian2000 / OpenTyrian，逐步重绘高清视觉，保留原玩法、
逻辑坐标、碰撞、关卡数据、事件和随机数流程。
[原上游 README](README.md#upstream-readme-preserved) 完整保留。

## 当前范围与限制

- 已接入部分船机、敌人、武器/特效、分层地形、云和世界材质。有限的单人
  HUD 改造包括框架、武器标签、护盾条、模式指示和右下角连接结构。
- 高清目前通过受控预览/素材调试入口启用。普通无相关参数启动仍走原版显示。
- 未覆盖、缺失或不兼容的资源按各功能规则回退；暂停、帮助、选项仍用原版界面。
- 已验收的是文档列明的有限 Linux 场景，包括原生 2×/4× 检查；不代表全游戏、
  全关卡、GPU/全屏或性能认证。最新修改尚未完成 Windows 运行验收。
- 固定 MODE/SHIELD/ARMOR 文字、有限范围的游戏内小字体及火力、能量、粗分组装甲条已接入；
  启动画面与 Logo 的重绘属于后续计划。

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

最后一条命令是普通原版显示启动。高清使用独立的
[有限预览入口](prototype/start-actual-preview.ps1)或
[素材调试入口](prototype/start-asset-debug.ps1)，需按说明准备外部数据和依赖。
这些是受控重播工具，尚非完整战役的手动操作高清发行版。参见
[调试操作](docs/ASSET_DEBUG.md)与
[有限场景启动示例](docs/FIRST30_HD_COVERAGE.md#later-windows-acceptance)。

Windows 使用[构建脚本](prototype/build-game.ps1)，环境与验收边界见
[Windows 说明](docs/WINDOWS_HANDOFF.md)。提供这些入口不代表最新版本已经通过
Windows 构建或运行验收。

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
