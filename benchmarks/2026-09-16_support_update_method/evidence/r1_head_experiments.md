# R1错因诊断与方法试验

2026-09-16启动。主记录：[optimization.md](../docs/research/optimization.md#r1-head-experiments)。本包只承载代码、输入请求、原始输出、评分、运行状态和证据导航。既有调查：r1_head_investigation（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/README.md`）。

分支：`diagnosis/`（MedEinst）、`rules/`（MedPIC）、`mcq/`（AMQA/Cultural/CPV）、`relations/`（MedCounterFact）。先实读原始错题定位机制，再做固定试跑与扩展；原模型、原评分和分母保持。2026-09-16全部本批模型运行、评分和汇总完成。诊断/规则主候选的七方法完整结果和独立入口回放通过；单选完整扩展未采用，关系201问句族作为两骨干范围内研究结果单独报告。最终取舍与成本见[主记录收尾](../docs/research/optimization.md#r1-relation-extension-complete)。

## 当前制品导航

- `candidate/README.md`：独立R1开发头的调用方式、公共资源和适用范围；完整2866×7回放已经通过。
- `diagnosis/`：新增1100＋历史680诊断、七方法、四个决策对照；最终汇总为`all_methods_1780/summary.json`。
- `rules/RESULTS.md`：已完成的96题冻结规则迁移、同事实执行对照和真实反例。
- `mcq/pilot/`、`mcq/fresh/`：已完成的24题两轮有限提示对照；`mcq/fresh_full/`为固定简单重答的全202扩展。
- `relations/pilot_summary.json`、`context_summary.json`：已完成的64题两轮关系对照；`context_extension_summary.json`为已完成的预选137问句族扩展，M4中断后仅补未保存部分；`context_all201_summary.json`为最终合并。
- `aggregate_r1.py`、`replay_candidate.py`：已生成2866×7主候选评分并逐字回放独立入口；结果见core_r1_summary.json和candidate_replay.json。
- `relations/combine_context.py`：两骨干201问句族合并，含R5重合项、旧/新review分层；没有替换全788分数。
- `summarize_costs.py`、`cost_summary.json`：全部已排定试验完成，47434次已记录新调用的成本/复用/耗时；未知的中断在途成本另记。

研究过程、采用/未采用理由和新的分组解释只在主记录持续维护。本包的运行失败证据不覆盖或删除，健康模型作业保持。
