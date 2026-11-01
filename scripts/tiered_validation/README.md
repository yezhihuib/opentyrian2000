# 分层验证：daily 默认，full 显式

这是可移入仓库 `scripts/tiered_validation/` 的工具代码，不包含私有工作区路径、已批准 profile、旧 PASS 或发布操作。仅依赖 Python 标准库；实际测试沿用项目原来的冻结 full 协议与运行环境。

## 约定

- **daily**：使用本批独立审查过的精确选择清单；新资源方法全部保留；失去哪些旧故障/历史投影覆盖，必须逐项写明。
- **full**：显式运行本批完整原始测试计划和原始公共 phase；不删改原方法，不借用以前结果。
- 未知 profile、变化的源/真实依赖、未批准 hash、缺失资源、实际失败：**停止**。不自动补跑四小时 full、不把失败变 skip、不自动降级。
- 下一批只需要准备并审查新 profile，并非每次必须重新执行全套。准备 full plan 是收集/绑定，不等于执行 full tests。
- 当前执行适配要求可独立批准的 **clean candidate checkout**（可为私有候选 commit，不要求先发布）。工作树/index、实际依赖、脚本和方法来源仍由原协议逐段校验。未提交改动不能冒充已批准候选。
- 当前 `current-state-once/v1` 是本项目专用合同：production binding + 当前默认 runtime manifest 干跑 + 已批准全树字节/模式/成员与 HD catalog + 三个原 SHOP 静态方法。不是视觉/真实 UI 验收，也不声称重证历史 inverse/P9/SHOP 全量故障枚举。

## 每批流程

1. 用原有准备流程为本批生成新的完整部署 profile、bundle、938 或本批实际全套 methods/provenance、原始 full protocol。**不要先运行 full**。独立审核当前树、真正 producer/shared-renderer 依赖、pins 与来源。不要把上一批 profile 改个路径便冒称恢复完成。
2. 复制 `selection-policy.template.json` 到本批私有材料目录。填写准确 required/deferred segment 名称（不支持通配符/自动影响分析）、每项省略的风险/恢复触发条件、全部新资源 test IDs，以及独立批准的 source binding。三个 SHOP 方法 source SHA 必须来自已审查的原方法源码。
3. 展开精确 IDs，生成不可执行的 DRAFT：

   ```sh
   "$VALIDATION_PYTHON" scripts/tiered_validation/prepare_profile.py \
     --full-plan "$FULL_PROTOCOL/plan.json" \
     --explicit-policy "$BATCH_POLICY" --out "$PROFILE_DRAFT"
   ```

   此步骤只按显式 segment 列表展开 IDs；**不推断影响、不批准、不运行测试**。独立审查实际依赖和 exact partition 后，审核人将独立副本的 `impact_review.status` 设为 `REVIEWED_EXPLICIT_SELECTION`，冻结 canonical JSON SHA。哈希仅用于本地完整性，不是对同权限修改者的认证签名。
4. 准备新的 mode-bound 协议（路径必须全新）：

   ```sh
   "$VALIDATION_PYTHON" scripts/tiered_validation/build_tiered_protocol.py \
     --full-protocol "$FULL_PROTOCOL" --approved-full-manifest "$FULL_SHA" \
     --profile "$REVIEWED_PROFILE" --approved-selection "$PROFILE_SHA" \
     --observed-binding "$INDEPENDENT_OBSERVED_BINDING_JSON" \
     --out "$DAILY_PROTOCOL" --mode batch
   ```

   每个新协议都包含原 full plan、准确选中/延期 IDs、phase replacement 合同和真实 source/tool 身份。先做 source/tool input_check 与收集预飞，再独立审查新协议 SHA。适配器不会自动启动 tests。
5. 用该 profile 绑定的 Python 环境运行日常验收（`daily` 为默认）：

   ```sh
   "$VALIDATION_PYTHON" scripts/tiered_validation/run_validation.py \
     --protocol "$DAILY_PROTOCOL" --approved-manifest-sha "$DAILY_SHA" \
     --campaign "$DAILY_PROTOCOL/qualification-01"
   ```

   campaign 必须是协议目录下全新目录；CLI 不自动恢复、不覆盖旧失败。原 controller 保留 250 MiB 最低剩余、64 MiB 增量预算、来源/工具/模式/pins 头尾校验、atomic completion chain 和失败规则。中断恢复须另行检查原有协议记录，不自动处理。

## 显式 full

对同一独立审查的批 profile，步骤 4 使用 `--mode full` 和另一个全新输出目录。运行时必须显式：

```sh
"$VALIDATION_PYTHON" scripts/tiered_validation/run_validation.py --mode full \
  --protocol "$FULL_MODE_PROTOCOL" --approved-manifest-sha "$FULL_MODE_SHA" \
  --campaign "$FULL_MODE_PROTOCOL/qualification-01"
```

full 使用完整原计划与四个原 phase；不会运行 daily 专用替代 phase。原 full 工具与原证据不覆盖。模式/hash 不匹配时停止，不帮用户偷偷切模式。

## 报告计数

分开报告 `selected_count`（原方法）、`additional_count`（新增静态方法）、`total_executed_method_count`、`deferred_count`、替换/保留的 phase。例如本次候选是 769 原方法 + 3 附加 = 772，另 169 原方法延期；这不是“938 全套通过”。完整方法分区只对原938计算；新加3项不冒充原方法。

`tests` 原 controller 字段仍表示原选中方法数；附加项在 `tier_selection` 和 composite receipt 有独立 IDs、成功记录、source SHA。不要只读 `tests` 字段就漏报附加项，也不要把 daily PASS 改名为 full PASS。

## 工具自测

```sh
cd scripts/tiered_validation
python -m unittest test_toolkit -v
```

这些可移植自测覆盖 profile 展开不自动批准、明确分区/full、未知输入停止、模式/新目录拒绝；不是实际项目验收。仓库迁入前应另行审查具体 delta，运行当前已批准批 profile 后保留完整证据；迁入工具代码本身也是新的 source input，需要新的 profile，不能复用旧 qualification 的源码身份。
