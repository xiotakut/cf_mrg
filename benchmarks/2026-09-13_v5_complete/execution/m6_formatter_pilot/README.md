# M6 最终格式整理修复试验（2026-09-13）

试验结论：优先使用显式字段的确定性兼容解析，不直接采用重新生成的formatter。新formatter即使结构合法，也可能改写已有推理的答案。正式M6已在其他工作区按用户指令暂停，本试验未恢复全量；GPU1–3的M7未操作。

## 样本和方法

冻结 `formal_balanced/runs/imedrag_*/items/*/result.json` 当时全部40个正式完成终态，没有按成败挑选：30协议有效、10无效；20单选、10诊断、7robustness、3关系题，无多选集合题。样本、完整formatter调用前的消息、原始输出、配置、seed和来源路径见 inputs.jsonl。早期完成样本不是全库代表性样本，不能将其有效率外推。

两种生成试验均复用原final reasoning及此前完整消息，只替换最后一条user格式请求：

- prompt：要求合法JSON，明确类型、保留原答案，提供JSON Schema描述。
- structured：相同提示另加xgrammar的Hugging Face LogitsProcessor，仅约束formatter阶段。

使用原 HFBackend、Transformers 4.51.3、同一Llama-3.1-8B-Instruct权重、BF16、SDPA、温度0.7、top_p1、top_k0、2048-token预算；每请求保留原seed，批次按输入长度排序、每批8条，与历史批次不同。query/parse/qa/final阶段没有重跑。约束只来自可见选项、类型和文档ID，不加入金标或canonical诊断标签。模型处理输出不能保证语义等价，因此额外比较原先协议有效的30条答案值，并抽查原final reasoning。

## 确定性兼容方案

[normalize.py](<normalize.py>)仅从已有formatter输出提取显式答案对象：

1. 接受标题/代码围栏中的JSON或Python字典字面量；使用JSON解码或 `ast.literal_eval`，不执行代码。
2. 将单引号、尾逗号、字符串换行等语法差异序列化成合法JSON；拒绝冲突答案对象及重复键，不从自由 prose 猜选项。
3. 对诊断，只去除唯一 `diagnosis` 字段的对象包装或其JSON字符串包装，保留内部诊断文本，不添加别名或修正诊断。
4. robustness答案对象缺errors时，仅搬入已有唯一 `## Errors` 节的显式数组，不补造空数组或医学纠正。
5. 转换后仍调用原 `valid_answer` 和原生评分器；缺失、含糊、非法值或结构继续无效。

literal.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/literal.jsonl`）与原始结果分开保存。该路径新增LLM调用为0。[检查脚本](<check_literal.py>)及[收据](<literal_validation.json>)验证40条答案值在仅去除显式诊断包装后不变，原对象已有errors逐字段不变；冲突与非法输入负例保留。原先有效的30条中，5条答案字符串从 `{"diagnosis":"..."}` 包装变成同一诊断标签，其余答案值不变，不能将这5条误报为换诊断。

[集成补丁](<methods.integration.patch>)只替换M6的最终formatter输出转换，不改M7共用的final_json。应用时需要同时放入normalize.py；该补丁是供新版本运行包使用的候选，**未写入活动共享代码，也未替换正式预测或评分**。已有配置/代码收据需按新版本记录，不能把此转换作为无记录的正式结果修补。原方法代码快照为 methods_source_snapshot.py。

## 证据与限制

[comparison.json](<comparison.json>)和逐题评分（本地制品：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/scored.jsonl`）汇总所有版本；原基线是历史输出，未以当前批次重新生成。有效率指M6运行协议，包含errors验证；原生有效率另外检查诊断映射等，和M4的format_invalid不完全同义。结构约束并不保证答案正确、忠于原推理或不截断。

对同题s200003，原final明确选择A，原formatter也是A，新提示formatter输出B；s011683原final明确给出Pulmonary Embolism，新提示formatter输出Pneumothorax。这些是拒绝把生成版直接视作“仅修格式”的实际依据，不是根据金标选择答案。确定性方案沿用已生成formatter的答案，不能修复它在更早阶段已经产生的语义偏移。

本批已用于方案开发，不是独立验证集，也没有覆盖真实多选集合输入。推荐方案仅建立了这些40条的兼容性与值保留证据；还需在独立样本及后续新结果上验证。正式论文必须将此处理标注为额外的确定性输出适配，并保留原始分数。

## 追加的不重叠样本检查

方案确定后，使用与40条开发输入不重叠的12条原试跑结果运行同一兼容代码，没有修改规则：协议有效11/12→12/12，原生有效11/12→11/12；12条答案值在仅去除显式包装后保持一致。样本涵盖single/multi/diagnosis/relation/robustness_single，包括开发样本缺少的真实多选格式。见 [holdout_validation.json](<holdout_validation.json>)、原始及转换输出（本地制品：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/holdout.jsonl`）、[检查脚本](<check_holdout.py>)。这些是历史上已观察过的试跑样本，虽然与本次开发集合不重叠，也不称为完全盲测或全库代表性测试。

因此确定性方案在两批共52条输出上协议有效52/52（原41/52），原生有效43/52（原35/52）；不需要新增模型请求。这是当前样本证据，不保证后续输出均可转换。未命中诊断标签继续无效，没有增加同义词表。

## 最终生成对照与推荐

两种生成对照均已完成40/40，新增80次formatter请求；没有重跑上游推理。以下计数针对同一40条开发输入：

| 方案 | 协议有效 | 原生有效 | 原生正确 |
|---|---:|---:|---:|
| 原formatter | 30 | 24 | 18 |
| 新提示词formatter | 39 | 32 | 13 |
| 新提示词＋结构约束formatter | 39 | 32 | 13 |
| 确定性兼容解析 | 40 | 32 | 22 |

原本协议有效30条中，提示词版21条答案字段变化，约束版22条变化；包括诊断字符串包装变化，也包括真实选项和诊断变化，不能将变化全部视为语义变化，但已观察到明确改选。确定性版的5条变化全部为诊断包装去除，验证后内部诊断文本相同。

生成版剩余无效均为s118747：提示词版无法提取无冲突答案，结构版触发invalid_document_ids；schema保证JSON和可见ID枚举，但不保证文档ID无重复。两者均正常stop，无运行失败。这说明JSON结构合法还不足以满足全部协议，更不能保证回答忠于已有final reasoning。**不推荐将本次两种生成版直接部署。** 推荐使用已验证的确定性兼容转换，并在新版本中单独记录其评分影响。

GPU0保护程序最终exit_code=0、yield_reason=null；09:44核查GPU0恢复9863 MiB、0%利用率，只保留原有其他用户进程。GPU1–3继续运行M7。原始预测、原评分、活动源码和暂停的M6队列未修改。

## 本轮格式修复的统一交接

[实施总记录](<../EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>)第10–13节汇总M4/M6诊断、候选方案、逐文件调整、复核命令和论文表述；明确区分正式结果、独立试验及尚未应用的补丁。
