# 蓝机械 v4：本批有限接入验收

结论：首组合正常显示、四个文件分别缺失回退、四个对象分别被原射击命中致死的有限场景通过。复用已冻结19个短场景记录并核验来源，另用当前生产程序和已交付索引复验950 tick；没有回写旧 checkpoint 的整份源码。

- 四对象为 newsh2.shp 的85/87/123/125，原类型13/14/8/9，槽25/26/75/76，各有独立资源与健康记录。
- 逻辑尺寸24×28、anchor6/7；上部偏移0/0和24/0，下部0/16和24/16，保留12像素逻辑重叠及原四象限顺序。
- 原上部link4、下部link3。逐个damage6命中会删除原联动的一对，另一对保留；没有人为改成四对象各自独立死亡。下部槽75/76在tick924被新link5对象复用，是原事件生成的新组。
- 232项RGBA源透明合成、148项单文件缺失原像素核验通过；原健康/碰撞/RNG/绘制及indexed blend顺序保持。19场景17840 tick，正常首组875..949、缺图883..899、明确射击夹具890..925。
- 原默认5帧和已验收13角各420 tick输出/控制记录保持。当前C除调试入口钩子外逐字节等于冻结蓝v4；再去掉四个绑定就逐字节等于此前受击/13角完成后的渲染器。
- 当前索引进入tick876后的36帧真实视野逐像素等于冻结完整蓝场景。保留当前exe、调试脚本、原素材、已验收Talon13、固定flare145和玩家受击修复；没有新增艺术图/模型。

## 最短使用

在现有本地repo内：

```powershell
$bluePython = 'C:\Program Files\Python311\python.exe'
& $bluePython .\prototype\asset-index.py find --sheet newsh2.shp --id 85
& $bluePython .\prototype\asset-index.py play --sheet newsh2.shp --id 85 --segment 1
# 更完整的四对象目标帧：
.\prototype\start-asset-debug.ps1 -Preset blue
```

默认使用本地27素材蓝v4测试包；正常旧启动脚本仍保持15素材/5船帧，未改默认。素材索引仍以配置逻辑时间分段，直接使用记录tick，15秒不是播放硬停。

## 范围与已知兼容路径

视频是原生SDL1280×800读回，未缩放的游戏区域，外加字幕；15fps剪辑，不代表墙钟时间、实测FPS、Windows合成器或物理2K。四个致死例使用明确标记的原Pulse155射击夹具，不是手工自然玩法录像。

**未宣称全效果高清**：原敌人的非致死受伤色滤仍走现有原图护栏。已观察tick892下部123/125的style3、mirrored0；玩家此前的受击/已知效果修复保留，敌人色滤高清兼容另行处理。后续第二波993..999与未绑定type10等相交时仍有既有局部原图恢复，超出本次首组合视觉通过范围。底座/type10整合继续排队。

## 独立回退

`blue-v4-bindings-only-keep-debug.patch` 只撤回19→15容量和四个蓝资源槽绑定，保留当前调试、受击和Talon13代码。已在临时目录验证正反向源字节完全一致，没有对当前repo执行回退。

```powershell
git apply --reverse --check 'C:\path\blue-v4-bindings-only-keep-debug.patch'
git apply --reverse 'C:\path\blue-v4-bindings-only-keep-debug.patch'
.\prototype\build-game.ps1
```

回退后使用已有 `packed-talon13-test` 外部包，并重新采集/核对索引来源；索引“文件可用”状态不能代替实际渲染验收。不要复制历史before-blue checkpoint的整份C来覆盖当前调试成果。完整源码补丁、单项回退、来源哈希和验证记录同包，不含exe/HDA/游戏数据，也没有推送或PR。


## 后续独立修复

上述色滤限制是蓝v4原交付的历史边界。之后的敌人色滤修复已独立冻结与交付，最终四部件合成复核见 [ENEMY_FILTER_VALIDATION.md](ENEMY_FILTER_VALIDATION.md)。原蓝v4检查点和交付文件保持不变。
