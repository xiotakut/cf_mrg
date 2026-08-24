# Gate A 公开数据执行结果

执行日期：2026-08-23
规范运行：`private_data/gate-a-public-20260823-seed13-v3`
机器可读报告：`results/gate_a_report.public-seed13.json`
最终决定：`stop_before_inference`

## 结果

已用固定 revision 的真实公开源完成当前计划的 Gate A。最终冻结 6,577 条 inference 和 6,577 条 gold；数据适配、目标计数、哈希、pair/control 结构与固定证据策略通过，但公开材料不足以执行计划要求的正式推理实验。因此按 `PROJECT_PLAN.md` 的 Gate 顺序停止，没有运行 M0–M13，也没有调用模型、GPU 或推理 API。

| 数据集 | 固定 revision | 原始数据 | 最终 pilot |
|---|---|---:|---:|
| MedPIC | `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983` | 467 行 | 467 行 |
| CLIR | `e7e1733b74819bbefa2a1b5bf653a0d1e00fbb9a` | 3,000 行 | t6–t10 各 100，共 500 行 |
| MedEinst | `354f4b527e764a8f2bebea8f71be55e0a6966402` | 10,766 行 | 500 pairs / 1,000 行 |
| MedCounterFact | `f35b98063b51a63e677829b6d173029d98dd3b1e` | 1,012 行 | 200 pairs / 400 行；四类各 50 |
| ReMedQA | `3abb4b47a5859c7b46c0a1872a58c82e2e3029e3` | 5,036 行 | 300 IDs / 1,200 行 |
| CPV | `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5` | 12,310 行 | 300 case IDs / 3,010 行 |

CPV 的 300 个控制单元均使用实际 `case_text` 人口学变体，其中 298 组含 10 行、2 组含 15 行。CLIR 只有 t6/t8 共 200 行具备可安全使用的公开观测；t7/t9/t10 共 300 行没有可用的历史观测。

## Gate 决定

20 项检查中 15 项通过，5 项阻断：

1. MedCounterFact 仓库和 ReMedQA dataset card 没有明确 license。
2. MedPIC 公开 467 行没有计划所需的官方 89 linked-pair map。
3. CLIR 有 300/500 行缺少可用的 repository observations。
4. CLIR 500/500 行都没有计划要求的 Full-TS。
5. CLIR 公开源没有官方 causal-edit pair map。

因此当前结果是数据/接口边界的 `stop_before_inference`，不是模型效果上的 NO-GO，也没有用此前的 Luna 代理实验替代本计划。

## 冻结哈希

| 产物 | SHA-256 |
|---|---|
| `configs/gate_a_sources.json` | `1389258e6248a862d88e7f8894ba96e2bf80e72916425f5d9ca8d313e3740bc5` |
| `gate_a_manifest.json` | `a34ae77072a73f275d7ec28cfbccd1e5534142d2ab506ab84e0950c10fe7cf9c` |
| `pilot.inference.jsonl` | `307d7d88cdad367a7e4e5f2beb0741247c3fb68a7b359c252c1fd46777b32e96` |
| `pilot.gold.jsonl` | `c53231e2e12b169c6abc8295e50a0cff32719112c214a34b85e8828e9cfbf25e` |
| `gate_a_report.json` | `c4f2851a5d33c1882bc85d6054f1b7adf1c1d176e0eea41332bcfbc20a7733df` |

## 执行与验收

- `result_audit`：数据源、revision、许可与真实结果数值检查。
- `code_test_audit`：数据准备、adapter、pilot 冻结与测试。
- `provenance_audit`：独立 Gate-A 审计器。
- 主 Agent：真实集成运行、结果复算与最终 Gate 决定。

最终测试：`python3 -m unittest discover -s tests -v`，4/4 通过；`py_compile` 通过。
