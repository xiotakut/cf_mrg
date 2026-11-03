# E5：冻结后的32家族R5确认面板

仅R5，32固定新执行家族，来源M10/M14/M17/M22/M23为8/8/8/4/4。每骨干112原生端点、64非reference判断、32单元和64保持配对。材料此前已收集/资格审查；有界暴露核对未发现选定家族曾执行，不宣称从未见过来源或BioNLI文章级独立。

## 主指标：32单元内非reference平均，再单元等权（%）

| 配置 | C0 | B | Gen | RulePrompt |
|---|---:|---:|---:|---:|
| M4 | 65.4167 | 70.2083 | 70.2083 | 70.2083 |
| M5 | 70.6250 | 75.0000 | 73.9583 | 75.0000 |

RulePrompt−C0为+4.7917pp（95%区间[−10.4167,+20.4167]）、+4.375pp（[−5,+14.5833]）；小样本点估计为正，两区间均跨0。[主表](analysis/primary_unit_mean.csv)、[单元分数](analysis/unit_scores.csv)、[4000次配对家族区间](analysis/unit_contrasts.csv)、[图](analysis/r5_confirmation.pdf)。

另报[112全部端点](analysis/all_endpoints.csv)、[64非reference判断](analysis/nonreference_judgments.csv)、[64保持配对](analysis/pair_summary.csv)、[修复/损害](analysis/endpoint_repairs_harms.csv)和[文档识别](analysis/document_summary.csv)。M4全部112端点B/RulePrompt为82正确，C0为83；不能用主指标掩盖该差别。没有相关变化新控制，不是A1–A4或跨功能独立确认。

[选择核验](analysis/selection_identity.json)：RulePrompt与B最终选择224/224相同，但完整字典仅209/224相同；每次仍完整复制实际选中的候选。解释外，M4 n0101还有errors字段不同。M22的文档识别精确匹配不代表临床语义正确。

## 计算与配置

1,479实际请求：M4 741、M5 738；C0 224、F 807、Gen 224、RulePrompt224。其中1,415生成、64单token NLI取分。共输入6,360,011、输出316,555 tokens；新C0/F在两个聚合臂间共享，逻辑归属成本不可相加。[物理账本](call_ledger.jsonl)、[物理费用](analysis/physical_costs.csv)、[归属费用](analysis/attributed_costs.csv)。

原始length终止66中64是正常单token取分；真正生成额度停止仅M4 C0和Gen各1，[分解](analysis/stop_reason_breakdown.csv)。112端点不可用为M4 C0 1/Gen1、M5 C0 1，其余0；全部保留分母。

复用保存上下文，0新检索。冻结方法/生成解析与运行层差别详见[runtime_equivalence_scope.json](runtime_equivalence_scope.json)，不是历史GPU逐位复现。模型均已释放。完整采样源hash及准备记录保留，不追加提示搜索。
