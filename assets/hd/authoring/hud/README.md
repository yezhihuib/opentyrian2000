# 当前 HUD：一处选择，同时生成所有当前使用位置

唯一入口是 `current.json`。它按语义指定六组素材，不按关卡复制：

| 键 | 编辑来源 | 固定不变的内容 |
|---|---|---|
| static | corner-v2 4× PNG | 原图身份、64000 字节所有权遮罩、透明度、尺寸 |
| meters | selected-rgb.json + 已固定的 materials.py 配方 | 原始角色、索引、几何、944 行结构及 lookup |
| font | tiny-coverage-atlas-4x.png 的 alpha 通道 | 字体来源、度量、字形位置、边距 |
| components | FRONT/GUN/REAR 标签和 14 个护盾色带 PNG | 原始角色、排列、尺寸、不透明约束 |
| indicators | 顶部镜片和两种模式装配 PNG | 状态角色、来源、尺寸、不透明约束 |
| fixed_text | MODE / SHIELD / ARMOR 字形 PNG | 字形来源、顺序、尺寸、不透明约束 |

初始选择精确重放已经接受的六个 HDA；没有改变字体、美术或游戏行为。
相同字节不代表相同语义，故 GUN 前后标签、ARMOR 中两个 R 仍有明确角色。
不要修改历史包或历史证明；保存新的来源版本，再修改入口中的路径及 SHA256。
这里只允许现有 PNG 无损解码和现有仪表配方重放，不自动生成/重新绘制图像。

环境依赖沿用 `assets/hd/artwork/gameplay-hud-meters-v2/requirements.txt` 中的
Pillow / NumPy 固定版本；本配方不安装依赖或访问网络。

```sh
python scripts/build_current_hud.py stage --selection assets/hd/authoring/hud/current.json --stage ../hud-stage-new
# 检查 ../hud-stage-new/plan.json；stage 不修改仓库
python scripts/build_current_hud.py apply --stage ../hud-stage-new
python scripts/build_current_hud.py check
```

六个 `assets/hd/shared-ui-v1/*.hda` 是生成输出，不是编辑入口。
`packaging/current-hud-compatibility.json` 把每个输出同时指定给运行包的
`assets/shared-ui/<文件>` 和 `assets/gameplay/<文件>`。因此只改一处来源，
正常共享路径和兼容回退路径一起更新。历史关卡包中的副本保留但不再是当前打包输入。
生成器同步更新仪表美术校验值、生产源绑定及运行包清单。

`check` 检查所有当前输出是否缺失/过期；它不是美术批准或运行时验收。
`apply` 会重算来源与计划、检查所有旧哈希和临时路径，再逐文件原子替换；
它不是跨文件的崩溃安全事务。中断后检查并重新 stage，不复用旧计划。
新字体或改变仪表 lookup 的编辑超出本配方范围，会明确拒绝而不是偷偷改结构。
