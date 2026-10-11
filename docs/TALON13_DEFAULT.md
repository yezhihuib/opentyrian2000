# 旧2D Talon13默认

按用户最新选择，已认可的2D/浅代理13角自机现为普通高清启动默认。
`prototype/start-actual-preview.ps1` 无需 `-Talon13`，选择含已核验foundation的`packed-talon13-foundation-v1-test`；
debug及索引播放也默认13角。`-Talon5` / `--render-talon-bank=5` 用于5帧兼容对照。
旧 `-Talon13` 参数仍接受。classic、缺中间帧和缺素材沿用已有回退。

本批只改渲染默认布尔值与启动入口；控制器、暂停/复活挂钩、碰撞、RNG不变。
七组196-tick有限回放核对当前默认、显式13、重复present、5帧、缺扩展、classic。
默认和显式13/重复present的16帧实际1280×800窗口逐像素一致；重复不推进角度。
暂停/复活复用先前通过的有界证据，未在本批重跑整套大用例；没有全关卡/人工/FPS验收声明。

报告：`talon-2d-restored-evidence/approved-2d13-default-validation.json`。
独立补丁：`talon-2d-restored-evidence/approved-2d13-default-only.patch`。
回退节点：`checkpoints/before-approved-2d13-default`；新节点：`approved-2d13-default-technical-passed`。

实体Talon v9停用归档，蓝2D v4保持静态，type10按队列使用已认可金属v9八PNG。既有玩家受击、敌人非致命
色滤修复和15秒素材索引保留。type10批准模型仅做兼容几何交接，没有新绘制或渲染。

本轮清理仅只读盘点。已有`run-controlled.py`永久BMP清理实现未在本批执行；普通preview
不再自动传`--png-captures`。删除或回收站处理须另获精确批次确认。
