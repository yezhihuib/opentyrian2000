# type10 金属 v9：有限接入

type10认可金属v9八帧有限接入通过。

仅使用指定Library文件libfile_0fcf8533b0ec819185581ea79ad35cec第9版的冻结八PNG。原newsh2.shp 191/193/195/197/199/201/203/205，24×28逻辑、192×224RGBA、anchor6/7。原引擎每逻辑tick换帧、8tick循环，未使用预览GIF80ms、未建模/重绘/换成试验A/B。
新增仅八资源槽，沿已有逐象限RGBA/原filter路径；源码与原健康、碰撞、动画、随机数、事件和绘制顺序保持。正常包35 HDA、debug包39 HDA；旧包字节保留，两个入口增加-BeforeType10回退，-BeforeFoundation、-Talon5和默认2D13仍保持。

有限验证：9种生产案例，104帧实际SDL1280×800，48项完整RGBA/滤色body核验，2项缺195原不透明像素和透明背景核验；两个完整八tick循环；4种只读观测案例与生产原生窗口/状态逐字节匹配。原Pulse155在151扣血3→2，152原filter208，153恢复；致死目标退出，原爆炸保留至173。缺195仅该角度的原足迹变化，其他七角及邻近高清区域16帧完全一致；HUD、重复present、classic、底座、蓝受击短片段与既有证据核对。
范围：episode1 physical-level9 seed0x5eed有界快进，非全关卡/所有效果、手动自然玩法、实测FPS、Windows合成器或物理2K。后续完全清爆炸未新增验证。邻接170..177、炮塔232..235及蓝890..893为有限检查，未覆盖任意相邻对象。小图为96×112原生4x裁切，视频完整游戏区域1280×800未缩放，15fps剪辑含停留。

独立回退：git apply --reverse --check <type10-v9-only.patch完整路径>，通过后git apply --reverse <同路径>，再prototype/build-game.ps1。也可两个启动入口先用-BeforeType10恢复底座包。补丁仅四文件，已经在独立临时树正反向字节核验；生产未执行回退。
前置checkpoint：原项目checkpoints/before-type10-v9-after-foundation；通过：checkpoints/type10-v9-technical-passed。不要复制更早完整renderer覆盖已有修复。包不含EXE/HDA/游戏数据。
源码路径：当前repo/src/render_mirror.c和prototype/asset-index.py、start-actual-preview.ps1、start-asset-debug.ps1。
索引：tyrian-e1-level9-index-type10-v9.json，沿用已有227素材/三个15秒查询窗，保留原观测来源，新增binding_refresh记录当前exe/源码及八绑定；没有冒充重新采集1053tick。find/play --sheet newsh2.shp --id 191；start-asset-debug.ps1 -Preset type10直达150。15秒不是播放硬停。

底座独立通过checkpoint和交付先已完成。旧2D13默认、蓝v4静态、玩家与敌人滤色修复、底座绑定、109/107/120暂停家族均保留。清理异常的原因/去向仍未核实，沿此前有限只读报告；本轮未删除、回收、清空或push/PR。
