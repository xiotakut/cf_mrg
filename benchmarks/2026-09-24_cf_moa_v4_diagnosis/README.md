# CF-MoA v4 诊断补充：给规划／审阅模型的阅读入口

2026-09-24。这里补齐上一版缺少的真实被调用源码和95触发组合的离线选择分解，供另一个模型直接通过GitHub读取。**不是V5新计划；没有新模型调用、评分或旧head回放。默认B、F重答关闭保持。**

## 建议阅读顺序

1. [诊断报告](DIAGNOSTIC_REPORT.md)：范围、结果、三类结论、成本和不确定性。
2. [源码入口](SOURCE_ENTRY.md)：实际触发、消息、解析、替换和采用F；73份源码/配置/来源文件，6份版本diff。
3. [选择分解表](data/selection_decomposition.csv)、[逐seed记录](data/per_trigger_seed.csv)、[完整面板原结果](data/full_panel_existing_results.csv)：可核对35次修复、40次误伤与原分母。
4. [数据发布范围](data/README.md)和[来源清单](source_manifest.json)：区分原字节源码、元数据投影、运行时冻结证据和当前模板快照。

## 优先看的真实代码

|问题|入口|
|---|---|
|何时触发、真正问了什么、怎样替换旧F|[a5_premise.py](source/v4_reanswer/cf_moa/agents/a5_premise.py)|
|旧F适配器|[a5_robust_readout.py](source/v4_reanswer/cf_moa/agents/a5_robust_readout.py)|
|采用F的映射、归一化、投票与早停|[r5_head.py](source/v4_reanswer/Documents/Codex/2026-09-18/r5_head/delivery/r5_head.py)|
|能力优先级与完整B答案绑定|[strong_legacy.py](source/v4_reanswer/cf_moa/controller/strong_legacy.py)、[baseline_native.py](source/v4_reanswer/cf_moa/controller/baseline_native.py)|
|真实执行分支|[effect_first_runner.py](source/v4_reanswer/cf_moa/evaluation/effect_first_runner.py)|
|请求／解析与采用配置|[native_backend.py](source/v4_reanswer/cf_moa/tools/native_backend.py)、[adopted.py](source/v4_reanswer/cf_moa/tools/adopted.py)、[M4](source/v4_reanswer/cf_moa/configs/readout_m4.json)、[M5](source/v4_reanswer/cf_moa/configs/readout_m5.json)|
|两次运行版本变化|[六份diff](source/diffs)|

## 当前可以确定的结果

95触发“输入—骨干”组合中：旧F正确43；旧池有正确键但F选错35；旧池全部错误17。三seed的285份补充回答新增正确键覆盖为0；35修复、40误伤，其中39次改选旧池已有错误键。95是触发范围，285不是独立患者数，不能替代完整121/52分母。

已证实发生的是“新单答替换旧聚合”，尚未证实退步由映射或消息丢失代码错误导致。NLI专用语义包装与普通重答的差异、具体医学原因和替代选择的泛化仍待验证；不要把当前诊断写成已找到稳定涨分修复。

## 本公开包能看什么

实际代码、配置、diff、候选键／概率／票数、质量与成本元数据可在GitHub阅读。**完整病例、检索正文、messages及原始响应不在公开包。** 私有294文件附件的名称、大小和SHA见[报告](DIAGNOSTIC_REPORT.md#私有完整样本对应关系)；需要逐题医学语义复核时，由文件持有人把该附件直接交给模型，不能将本表格投影当成完整trace。

旧报告与结果保持：[v4第14章](../2026-09-24_cf_moa_minimal_v4/docs/research/cf_moa_experiment_report.md#minimal-head-reuse-v4)、[v4运行与交付](../2026-09-24_cf_moa_minimal_v4/RUN_AND_DELIVERY.md)。本目录仅补充阅读材料。
