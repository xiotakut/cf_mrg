# i-MedRAG（历史M6）

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。旧M6 i-MedRAG保持原方法身份，历史全量队列暂停。本文保存多轮追问、逐问题RAG、跨轮QA历史、formatter失败、缓存复验、吞吐优化和替代前成本核查。当前M6已改为MedGENIE。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [M6 formatter修复试验（2026-09-13 09:44完成）](#record-0071)
- [10.2 M6 活动运行的格式问题抽查（2026-09-13 07:30 UTC+8）](#record-0117)
- [12. M6 formatter 有效率修复试验（2026-09-13）](#record-0125)
- [样本和方法](#record-0126)
- [确定性兼容方案](#record-0127)
- [证据与限制](#record-0128)
- [追加的不重叠样本检查](#record-0129)
- [最终生成对照与推荐](#record-0130)
- [3.1 i-MedRAG](#record-0180)
- [4.2 i-MedRAG缓存复验链](#record-0185)
- [v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）](#record-0209)
- [2026-09-14：MedRGAG 论文中的 i-MedRAG 成本与配置核查](#record-0228)
- [M6 i-MedRAG真实运行](#record-0382)

<a id="record-0071"></a>

## M6 formatter修复试验（2026-09-13 09:44完成）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2220行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M6 formatter修复试验（2026-09-13 09:44完成）

[实施、验证及候选补丁](/home/data3/txy/docs/baselines/imedrag.md#record-0125)。固定40条正式完成输出，两种仅重跑formatter的生成版均39/40协议有效，但出现实质改选，未采用。确定性兼容解析40/40有效，追加12条不重叠原试跑12/12有效；合计协议41/52→52/52，原生35/52→43/52。答案值在仅去除显式诊断包装后保持，既有errors不改写，无LLM补答或新增同义词。推荐转换代码和仅针对M6的集成补丁已准备，未写入活动方法代码或正式预测；M6保持既有暂停，未操作GPU1–3的M7。试验新增80次formatter请求，GPU0已释放自身模型。样本非全库代表性，也不声称100%普遍保证。

<a id="record-0117"></a>

## 10.2 M6 活动运行的格式问题抽查（2026-09-13 07:30 UTC+8）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第382行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 10.2 M6 活动运行的格式问题抽查（2026-09-13 07:30 UTC+8）

只读检查另一工作区 `results_v5_m6_m7/formal_balanced` 的已落盘终态，含12条复用试跑：45条完成、38条协议有效、7条无效、0条运行失败。保存[当时快照](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m6_validity_snapshot.json)，不代表全量最终有效率。M6 的运行协议还检查 robustness errors 等字段，不能直接等同于本节 M4 的 format_invalid 口径；本次未重算 M6 原生评分。

7条无效均到达 final_formatted：6条为 missing_or_conflicting_answer，1条 invalid_answer_type。可见案例包括单引号字典前附 `## Answer` / Analysis（s002285、s008154、s116746），以及返回 `{"answer":{"diagnosis":"..."}}` 而非诊断字符串（s006117）。这确认 M6 也存在最终答案格式损失，但不能据45条早期样本推断全库严重程度。

M6 与 M4 的机制不同：M6 先在自由文本 Analysis/Answer 中推理，再额外调用 formatter，提示原文使用 `Output the answer in JSON: {'answer': your_answer ...}`，其中单引号示例实际是 Python 字典语法，不是合法 JSON。现有 final_json 兼容函数仅对整个输出为字典（可包整段代码围栏）做 AST 安全转换；带标题/解释的单引号字典不能通过这条回退路径。这是已确认的提示示例与解析兼容范围不一致，不能归咎于 Llama 本身。M6 已有该兼容步骤及查询格式修复调用，输出处理并非与 M4 完全相同。

此次未改动 M6 活动代码、配置、队列或结果，也未中断进程。若修复，应先在保存的响应上验证无语义改写的解析兼容，并独立记录版本和影响，避免正在运行的结果无标记混入新评分规则。

<a id="record-0125"></a>

## 12. M6 formatter 有效率修复试验（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第468行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 12. M6 formatter 有效率修复试验（2026-09-13）

试验结论：优先使用显式字段的确定性兼容解析，不直接采用重新生成的formatter。新formatter即使结构合法，也可能改写已有推理的答案。正式M6已在其他工作区按用户指令暂停，本试验未恢复全量；GPU1–3的M7未操作。

<a id="record-0126"></a>

## 样本和方法

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第472行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 样本和方法

冻结 `formal_balanced/runs/imedrag_*/items/*/result.json` 当时全部40个正式完成终态，没有按成败挑选：30协议有效、10无效；20单选、10诊断、7robustness、3关系题，无多选集合题。样本、完整formatter调用前的消息、原始输出、配置、seed和来源路径见 inputs.jsonl。早期完成样本不是全库代表性样本，不能将其有效率外推。

两种生成试验均复用原final reasoning及此前完整消息，只替换最后一条user格式请求：

- prompt：要求合法JSON，明确类型、保留原答案，提供JSON Schema描述。
- structured：相同提示另加xgrammar的Hugging Face LogitsProcessor，仅约束formatter阶段。

使用原 HFBackend、Transformers 4.51.3、同一Llama-3.1-8B-Instruct权重、BF16、SDPA、温度0.7、top_p1、top_k0、2048-token预算；每请求保留原seed，批次按输入长度排序、每批8条，与历史批次不同。query/parse/qa/final阶段没有重跑。约束只来自可见选项、类型和文档ID，不加入金标或canonical诊断标签。模型处理输出不能保证语义等价，因此额外比较原先协议有效的30条答案值，并抽查原final reasoning。

<a id="record-0127"></a>

## 确定性兼容方案

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第483行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 确定性兼容方案

[normalize.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/normalize.py)仅从已有formatter输出提取显式答案对象：

1. 接受标题/代码围栏中的JSON或Python字典字面量；使用JSON解码或 `ast.literal_eval`，不执行代码。
2. 将单引号、尾逗号、字符串换行等语法差异序列化成合法JSON；拒绝冲突答案对象及重复键，不从自由 prose 猜选项。
3. 对诊断，只去除唯一 `diagnosis` 字段的对象包装或其JSON字符串包装，保留内部诊断文本，不添加别名或修正诊断。
4. robustness答案对象缺errors时，仅搬入已有唯一 `## Errors` 节的显式数组，不补造空数组或医学纠正。
5. 转换后仍调用原 `valid_answer` 和原生评分器；缺失、含糊、非法值或结构继续无效。

[literal.jsonl](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/literal.jsonl)与原始结果分开保存。该路径新增LLM调用为0。[检查脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/check_literal.py)及[收据](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/literal_validation.json)验证40条答案值在仅去除显式诊断包装后不变，原对象已有errors逐字段不变；冲突与非法输入负例保留。原先有效的30条中，5条答案字符串从 `{"diagnosis":"..."}` 包装变成同一诊断标签，其余答案值不变，不能将这5条误报为换诊断。

[集成补丁](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/methods.integration.patch)只替换M6的最终formatter输出转换，不改M7共用的final_json。应用时需要同时放入normalize.py；该补丁是供新版本运行包使用的候选，**未写入活动共享代码，也未替换正式预测或评分**。已有配置/代码收据需按新版本记录，不能把此转换作为无记录的正式结果修补。原方法代码快照为 methods_source_snapshot.py。

<a id="record-0128"></a>

## 证据与限制

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第497行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 证据与限制

[comparison.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/comparison.json)和[逐题评分](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/scored.jsonl)汇总所有版本；原基线是历史输出，未以当前批次重新生成。有效率指M6运行协议，包含errors验证；原生有效率另外检查诊断映射等，和M4的format_invalid不完全同义。结构约束并不保证答案正确、忠于原推理或不截断。

对同题s200003，原final明确选择A，原formatter也是A，新提示formatter输出B；s011683原final明确给出Pulmonary Embolism，新提示formatter输出Pneumothorax。这些是拒绝把生成版直接视作“仅修格式”的实际依据，不是根据金标选择答案。确定性方案沿用已生成formatter的答案，不能修复它在更早阶段已经产生的语义偏移。

本批已用于方案开发，不是独立验证集，也没有覆盖真实多选集合输入。推荐方案仅建立了这些40条的兼容性与值保留证据；还需在独立样本及后续新结果上验证。正式论文必须将此处理标注为额外的确定性输出适配，并保留原始分数。

<a id="record-0129"></a>

## 追加的不重叠样本检查

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第505行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 追加的不重叠样本检查

方案确定后，使用与40条开发输入不重叠的12条原试跑结果运行同一兼容代码，没有修改规则：协议有效11/12→12/12，原生有效11/12→11/12；12条答案值在仅去除显式包装后保持一致。样本涵盖single/multi/diagnosis/relation/robustness_single，包括开发样本缺少的真实多选格式。见 [holdout_validation.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/holdout_validation.json)、[原始及转换输出](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/holdout.jsonl)、[检查脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/check_holdout.py)。这些是历史上已观察过的试跑样本，虽然与本次开发集合不重叠，也不称为完全盲测或全库代表性测试。

因此确定性方案在两批共52条输出上协议有效52/52（原41/52），原生有效43/52（原35/52）；不需要新增模型请求。这是当前样本证据，不保证后续输出均可转换。未命中诊断标签继续无效，没有增加同义词表。

<a id="record-0130"></a>

## 最终生成对照与推荐

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第511行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 最终生成对照与推荐

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

上述GPU1–3仍运行M7是本试验完成时的历史状态。最新暂停状态与后端优化见[M6/M7主记录](/home/data3/txy/docs/workspace.md#record-0174)；本节的生成式formatter未采用、确定性候选未部署。

<a id="record-0180"></a>

## 3.1 i-MedRAG

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第75行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 3.1 i-MedRAG

真实执行顺序为：原题Q及成功QA历史H → 本轮追问生成 → 同模型提取追问 → 每个追问独立检索和作答 → 按查询序号写入H → 下一轮 → 基于Q与H生成最终分析 → 同模型格式化。最后的追加上下文是QA历史；各轮动态检索正文不会直接合并给最终reader。任务本来自带的合法固定证据仍属于原题。

| 调整 | 原行为 / 问题 | 最终处理及影响 |
|---|---|---|
| 安全查询解析 | 官方依赖特定空格正则和 `eval()` | 保留上游LLM提取调用，用JSONDecoder读明确JSON；保存提取prompt、原始输出、状态和成本 |
| 限定格式修复边界 | 提取模型可能重写、截取、合并或补造查询 | 逐条定位原查询段、完整边界及原顺序；拒绝语义重写/拆合；无效轮次有记录，成功QA才进入H |
| 支持实际Markdown形式 | 实测出现加粗、编号标题、`### Query 1`、`### 1.`、`1. ##`及关键词括注 | 仅处理这些语法包装和无意义空白；保留问题正文，保护1.5等小数和-3等负数；没有凑足3条查询 |
| 每条QA独立恢复 | 早期同轮 `call_many` 以一个批请求收据保存，不利于局部恢复 | 每条QA独立future/请求收据；后端可合批，写回仍按原查询序号；轮间保持依赖 |
| 固定终止 | 上游除4轮外还允许3次自由循环，可能继续追问 | 本项目固定4轮后一次最终分析及一次格式化；这是明确的终止适配 |
| 最终格式提示 | 初版通用格式提示；中间尝试明确flat JSON和小写选项，随后恢复官方形式 | 最终保留 `Output the answer in JSON: {'answer': your_answer (...)}`；只按原生选项/多选/关系/诊断/错误文档字段适配 |
| 单引号字典兼容 | 模型模仿官方提示中的单引号字典，严格JSON接口拒绝 | `final_json` 用标准库 `ast.literal_eval` 读取完整字典后 `json.dumps`；拒绝重复字段、非字面量及值变化；不改大小写、诊断内容或增加LLM调用 |
| 失败与分母 | 仅最终输出合法不足以证明追问流程完成 | 有未解决追问问题仍记invalid；检索/QA请求失败记failed；不使用其他方法或Direct补答案 |

标准恰好3条有效追问/轮时，4轮共12条QA，加上4次生成追问、4次提取、1次最终分析和1次格式化，共 **22次LLM请求、12次检索**。这不是实际请求数的硬上限；实际查询数、格式修复和传输重试分别统计。

<a id="record-0185"></a>

## 4.2 i-MedRAG缓存复验链

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第153行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 4.2 i-MedRAG缓存复验链

1. `imedrag_dev_v4` → `imedrag_dev`：复制716份未受影响的请求收据，排除所有最终格式化；查询语法修复涉及 `dev_medqa_009` 第3轮、`dev_medeinst_003` 第1轮、`dev_medeinst_006` 第3轮、`dev_medeinst_009` 第1轮（均为零基编号），重算受影响QA及依赖历史之后的阶段。新增60个LLM请求、24次检索。
2. `imedrag_dev` → `imedrag_dev_final`：复制776份收据；只新增24次最终格式化调用，恢复官方提示及原生答案类型说明。
3. `imedrag_dev_final` → `imedrag_dev_accepted`：复制全部800份真实收据，即521个模型请求及279个检索请求；统一重放24条，19条产生 `answer_syntax_repair` 事件，新增模型/检索调用均为0。

每层 [cache_provenance.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/cache_provenance.json) 指向来源和复用规则；辅助脚本为 [replay_format_prefix.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/replay_format_prefix.py)。早先734份收据的准备方案在追加两项实际语法问题后作废，当时尚未开始该复验的推理，保留于 [prefix_preparation_before_syntax_followup.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/prefix_preparation_before_syntax_followup.json)。最终按716份方案执行。没有按答案正确与否挑选输入或复用结果。

<a id="record-0209"></a>

## v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第338行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）

用户明确要求暂停 M6，继续 M7。当前活动包 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced` 未迁移。M6全部109分片标记paused，累计52/13905（40新＋12复用），41有效/11无效/0失败；预测与阶段缓存保留，操作记录m6_pause.json，不自动恢复。GPU1/2原M6已释放并领取M7分片002/003；GPU3原M7分片001未中断。M7三卡均32并发、96000合批token，其余方法/生成/检索设置不变。GPU0未动。tmux仍v5-m6-m7-balanced。

调整独立完成汇总：M7所有分片完成并审计后，自动写results/tcrag/complete.json、原生评分和RESULTS.md，不等待M6；根complete.json仍只用于两方法均完成。暂停队列不被领取和独立评分幂等性等3项针对性测试通过。五分钟进度与GPU0–3报告继续。

<a id="record-0228"></a>

## 2026-09-14：MedRGAG 论文中的 i-MedRAG 成本与配置核查

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第530行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2026-09-14：MedRGAG 论文中的 i-MedRAG 成本与配置核查

用户询问 MedRGAG 是否以当前 M6 速度完成基线。核对 [MedRGAG v1](https://arxiv.org/html/2510.18297v1) §4及附录A/C：论文报告三个reader上的i-MedRAG结果；明确采用vLLM批量推理，实验五数据集合计7,663题且均为选择题，通用检索说明为Textbook/Wikipedia及最终top-5。没有找到i-MedRAG专属轮数、每轮查询数、逐阶段输出上限或该基线总耗时/GPU小时，不能断言与本地4×3、完整MedCorp、top-8、13,905多题型输入等价。附录的256-token限制描述背景文档生成，不应直接套作i-MedRAG全部子QA预算。MedRGAG辅助模块使用GPT-4o-mini，也不能推断i-MedRAG追问全部使用该API。

本地MedRGAG/src和main.py未找到i-MedRAG执行实现；本地锁定的MedRAG上游src/medrag.py::i_medrag_answer默认n_rounds=4、n_queries=3。两者来源须区分：本地采用上游默认不证明MedRGAG论文使用相同配置。核对 [i-MedRAG原论文v3](https://arxiv.org/html/2408.00727v3) Limitations：作者明确承认查询数增加会线性增加成本，更多检索文档也增加时间成本，且最优超参数随模型/问题变化。

结论：论文报告了实验结果，但没有足够运行证据证明其以本地早期低效HF吞吐完成，也没有发现已披露的i-MedRAG特殊提速机制。我们已验证vLLM版M6为222.67题/GPU小时，若粗略线性投影13,905题约62.45 GPU小时、三卡约20.82小时；样本并非完整代表性且未计调度/长尾，因此不作完工承诺。此次只读代码与文献、更新既有记录，无推理或GPU操作。

<a id="record-0382"></a>

## M6 i-MedRAG真实运行

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md)，原文第33行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### M6 i-MedRAG真实运行

最终目录：[runs/imedrag_dev_accepted](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted)。24/24终态，19有效、5无效、0失败、0待运行、0未知ID、0重复；有效率79.17%。96个追问轮次，实际279个查询及279个RAG答案，单题查询6–15个，未编造凑数。521个逻辑LLM请求，1093381输入token、169363生成token、279次检索；输出截断、无命中、传输重试和预算耗尽均为0。

MedQA开发12条中11有效、1无效；MedEinst训练12条中8有效、4无效。5条无效中，3条最终格式无法无歧义读取，3条涉及追问提取失败，交集1条。没有其他方法补答。见[执行审计](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/execution_report.json)、[逐题终态](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/predictions.jsonl)。审计核对521次实际模型身份、96轮前后历史、279次真实检索/QA、24次最终QA上下文。

官方格式化提示的单引号示例导致严格JSON接口失败；最终仅增加确定性字典字面量→JSON转换，19条发生转换，全部原值保留。最终目录重放800份真实收据（521模型＋279检索），新模型和检索调用均为0。链式[缓存来源](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/cache_provenance.json)连接原始完整运行及统一接口复验，所有24条执行相同规则，未按正确性筛选。较早pilot及中间无效预测、成本、源码快照全部保留。

现有评分器以完整12条来源分母计算：MedQA为11/12；MedEinst既定canonical评分为0/12。后者8条运行有效答案仍有6条嵌套结构字符串被旧解析器拒绝、1条未映射诊断、1条歧义诊断。不能据此声称医学语义准确率为0或开放诊断评分兼容性已通过。未基于gold新增同义词或改写答案。[离线评分](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/scores/summary.json)分别记录运行有效率和评分有效率。

原始完整i运行耗时11914秒（3.31小时），共享GPU吞吐7.25输入/小时；单题延迟p50=1875秒、p95=2401秒，合批行数中位4、最大10。最终语法重放1.60秒仅是缓存时间。后续接口复验新增60＋24次模型调用及24次检索另列；失败pilot成本也保留，不混作最终逻辑请求数。
