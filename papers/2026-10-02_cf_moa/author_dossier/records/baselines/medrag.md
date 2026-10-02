# MedRAG基线（M4/M5）

最新状态：2026-09-22（Asia/Shanghai）。M4/M5正式v5结果保持不变；当前M4采用全量结构化输出修复版，M5保留原已完成版本，因此两者仍同时存在骨干和输出协议差异。09-22对修复配置做了4题live smoke：4/4执行、4/4 inline JSON有效、4/4原生数值格式有效，但引擎一致性字段`engine.sampling.output_kind`从旧值0变为新值2，运行状态标为`failed`，不产生新的正式准确率结论；证据见[运行目录](/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_live_check/m4/status.json)。早期M4 RRF安装配置与正式v5 BM25＋MedCPT配置分别保留。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [当前 M4 格式修复独立试跑（2026-09-13 09:17）](#record-0070)
- [新M4结构约束修复全量完成（2026-09-13 15:04）](#record-0077)
- [3.2 M4 与 M5 对齐：确实改变过实验配置](#record-0094)
- [4.1 M5 / M4：补齐 PubMed 行偏移文件](#record-0098)
- [5.2 M4 调度历史](#record-0105)
- [10. M4 / M5 输出有效率专项核查（2026-09-13）](#record-0115)
- [10.1 同骨干 M0/M2 对照：不能归因于 Llama 本身](#record-0116)
- [10.3 回查 M4 输入调整是否导致格式失败（2026-09-13）](#record-0118)
- [10.4 用户要求旧配置试跑：资源预检与样本准备](#record-0119)
- [11. 当前 M4 输出格式修复试验（2026-09-13）](#record-0120)
- [两个候选版本](#record-0121)
- [执行与评分](#record-0122)
- [最终结果](#record-0123)
- [约束版原始制品](#record-0124)
- [保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）](#record-0138)
- [新M4结构约束修复全量完成（2026-09-13 15:04）](#record-0141)
- [M4_M5_INSTALLATION_REPORT.md](#record-0254)
- [README.md](#record-0388)
- [README.md](#record-0394)
- [RESULTS.md](#record-0395)
- [2026-09-22 M4修复版四题live smoke](#record-20260922-m4-live-smoke)

<a id="record-20260922-m4-live-smoke"></a>

## 2026-09-22：M4修复版四题live smoke

为核对新修复配置在GPU0上的当前可运行性，执行了独立的4题 `a4_live_check`，未纳入正式v5结果。运行目录为[`a4_live_check/m4`](/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_live_check/m4)，4/4请求执行，4/4 inline JSON有效，4/4原生数值格式有效；但一致性校验在每条请求都发现`engine.sampling.output_kind`由旧值0变为新值2，因此`status.json`为`failed`。这表示本次输出格式可以解析，但当前引擎参数/回读字段与保存的旧参考不一致，不能据此更新正式准确率，也不能把这4题当作独立验证集。运行结束后GPU0进程已退出，监控脚本也按用户要求停止。

<a id="record-0070"></a>

## 当前 M4 格式修复独立试跑（2026-09-13 09:17）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2216行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 当前 M4 格式修复独立试跑（2026-09-13 09:17）

[试验记录](/home/data3/txy/docs/baselines/medrag.md#record-0120)：100条同题、固定历史检索证据，原格式有效65/100；加强提示92/100；再加xgrammar JSON Schema为98/100（1截断、1含糊诊断），原生有效53→76→84。新增200条试验预测独立保存，原正式输出不变。GPU0试跑模型已释放，M6/M7未操作。尚未启动全量重测；同一试验样本已用于方案选择，不能当独立确认集。

<a id="record-0077"></a>

## 新M4结构约束修复全量完成（2026-09-13 15:04）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2252行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 新M4结构约束修复全量完成（2026-09-13 15:04）

[最终结果](/home/data3/txy/docs/baselines/medrag.md#record-0395)：13,905唯一输入全部新生成，109/109分片完成，15,616原生评分映射、6,104单元、13,000入选判断完整，缺失/重复/运行失败均为0。GPU1/2/3生成墙钟含加载71.86分钟，完成后自动释放；GPU0未动。

同一13,905输入，格式有效率61.41%→99.09%，原生有效率43.92%→79.42%；严格Schema有效99.46%，原生监控与完整评分器去重一致。单元平均准确率原M4→修复M4：R1 21.53→27.84、R2 6.33→29.11、R3 14.32→30.42、R4 23.08→53.85、R5 39.63→65.28、ALL 29.76→48.20（%）。所有无效保留分母。原生无效2,861：未映射诊断2,735、诊断歧义50、原生解析malformed_json 76；严格JSON无效75，长度截断73，口径分别记录。诊断原生有效率仍仅21.32%。

方案选择100输入之外的13,805输入格式/原生有效率99.11%/79.39%；全库并非独立泛化确认。明确输出契约＋JSON Schema约束改变生成协议，不声称token等价；M5未同步修改，因此新M4/M5不再是仅骨干不同的对照。旧M4原结果独立保留。比较、完整评分及有效率见结果包，五分钟GPU与进度记录见logs/supervision.jsonl。M7保存点仍1,646条（1,634新＋12复用），M6仍52条，均保持暂停。

<a id="record-0094"></a>

## 3.2 M4 与 M5 对齐：确实改变过实验配置

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第82行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 3.2 M4 与 M5 对齐：确实改变过实验配置

用户要求 M4 与 M5 使用相同检索与生成设置、保留不同回答模型。调整发生在此次 M4/M5 正式结果产生之前；变更记录中两者已有预测数均为 0，未把两种 M4 配置的输出混入最终表。

| 设置 | 原 M4 配置 | 本次最终 M4 配置 |
|---|---|---|
| 检索器 | RRF-4 | BM25 + MedCPT 重排 |
| 语料 | TextbooksWikipedia | MedCorp 四语料 |
| 最终检索片段数 | 5 | 8 |
| temperature | 0.2 | 0.7 |
| 追加检索上下文预算 | 128,000 | 30,000 个模型 token |
| 回答模型 | Llama-3.1-8B-Instruct | 保留 |

证据：[完整前后配置](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_configuration_change.json)、[M4 配置](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/configs/m4.json)、[M5 配置](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/configs/m5.json)。配置中保留的 `rrf_k` 字段不能用来证明实际采用了 RRF；实际路径为 BM25+MedCPT。

两者本次均为 question-only 检索的单轮流程、四库每库 BM25 top-32、MedCPT 重排 top-8、temperature=0.7、top_p=1、seed=42、输出最多 2,048 token，保留 CoT/JSON 模板并适配原生任务格式。M5 使用 Qwen3-8B、关闭 thinking；M4 使用 Llama-3.1-8B-Instruct。模型各自的 tokenizer/chat template 不相同。

**论文必须把这项变化写成所采用的基线设置，而不是宣称原 RRF-4 方法仅做了性能优化。** M4/M5 与 M0/M2/M3 的语料、调用次数及预算并非完全一致，不能把所有分数差异仅归因于算法结构。

<a id="record-0098"></a>

## 4.1 M5 / M4：补齐 PubMed 行偏移文件

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第132行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 4.1 M5 / M4：补齐 PubMed 行偏移文件

定位到 PubMed 命中正文读取缺少旁路行偏移文件，导致每条命中可能重新读完整 JSONL 分片。复用已有 `CorpusDocumentResolver` 生成器和 MedRAG 已支持的按偏移读取分支，为全部 1,166 个 PubMed 分片补齐约 182 MiB（191,189,608 字节）偏移文件。

这不是重建语义向量索引，也不是更换检索器。检索策略、正文、文档顺序和采样参数保持。M5 运行中可直接使用，未为此重启；M4 使用相同语料目录与运行代码，随后自动继承。

| 检查 | 实测结果 | 证据 |
|---|---|---|
| 同一组 32 条 PubMed 正文读取 | 4.3263 秒 → 0.001511 秒；正文完全一致 | [读取验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/pubmed_offset_validation.json) |
| 全部偏移有效性 | 1,166 分片、23,898,701 行，每个字节偏移验证通过 | [全量验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/pubmed_offsets_full_validation.json) |
| 历史 16 个样本输入等价 | 5 种原生格式，prompt、token IDs、记录 token 数一致，采样设置不变 | [输入等价验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m5_input_equivalence_validation.json) |
| 16 题排除检索后的准备时间 | 总计 0.143389 秒 | [准备时间剖析](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m5_prompt_preparation_profile.json) |

最后一项进一步拆成：上下文与消息构造 0.068479 秒、chat template 0.019154 秒、tokenization/长度检查 0.055755 秒。此前对话中的“每题检索约 5.7–6.5 秒、一批准备输入约 90–100 秒”，其“一批准备”口径包含检索循环，不能解释为纯提示拼装需要 90–100 秒。

会话观察到修复后每题检索约 2–3 秒、16 题批准备约 42 秒。这些是共享机器运行观察，不是严格控制的端到端 A/B 实验。32 条读取样本的巨大加速比只适用于该文档读取子步骤，不得写成整个 M5/M4 同倍提速。完整偏移验证证明定位正确，也不等于对所有题目都执行了优化前后生成对照。

适用范围：同样的语料布局与读取路径可用于其他 benchmark，不依赖当前题目内容。M2 已使用较快的 Textbooks/Wikipedia 读取路径；M3 使用另一套内存字典检索服务，不能直接套用这项每题优化。

<a id="record-0105"></a>

## 5.2 M4 调度历史

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第199行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 5.2 M4 调度历史

先在 GPU0 受保护借用，保留 6 个正式输入冒烟结果。原批提交到 5,824 条后迁移，合计 5,830 个已完成结果保留，剩余 8,075 条按完整 16 题批切成 4,043 / 4,032，在 GPU0/1 并行。随后两 worker 各提交 1,616 条，合并核对到 9,062 个唯一结果，剩余 4,843 条切为 1,616 / 1,616 / 1,611，在 GPU0/1/2 并行。

M4 使用 `flock` 防止旧队列重复启动；合并核对预测和 prompt 覆盖，保留切换前文件。运行 batch=16；初始读取模型份额 .55，GPU0 受保护运行与并行阶段 .50（.45 的 KV 容量不足以支持 131,072 上下文）。没有因调度改变 temperature、输出预算或检索设置。证据：[运行说明](/home/data3/txy/docs/evaluation/v5.md#record-0391)、[并行协调器](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/run_m4_parallel.py)。

<a id="record-0115"></a>

## 10. M4 / M5 输出有效率专项核查（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第335行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 10. M4 / M5 输出有效率专项核查（2026-09-13）

针对 M4 有效率偏低的问题，对已有完整预测与评分记录做了全量只读诊断，未重跑推理、修复输出或修改正式评分。可复核的[诊断脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/audit_output_validity.py)与[统计 JSON](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/output_validity_audit.json)已保存。脚本使用 AST 提取冻结分析代码中的 `objects` 函数，避免导入推理依赖；宽松 JSON 解码仅作原因定位。

以下均以每方法 15,616 条评分映射（包括 reference）为分母，不能与 13,905 个独立请求混用。“接口有效”在这里明确指评分字段 `not format_invalid`，不是 HTTP/API 请求成功率；“原生评分有效”指 `not invalid`。

| 指标 / 无效原因 | M4 | M5 |
|---|---:|---:|
| 格式/接口有效 | 9,621（61.61%） | 14,523（93.00%） |
| 原生评分有效 | 7,189（46.04%） | 11,758（75.29%） |
| JSON/answer_choice 对象提取失败 | 3,699 | 27 |
| 选项键无效 | 2,195 | 959 |
| 诊断未匹配固定 canonical labels | 2,432 | 2,765 |
| 多个/含糊诊断 | 98 | 90 |
| 多选集合无效 | 3 | 17 |

如果“接口”仅指能提取严格 JSON 的 `answer_choice` 对象，则独立输入口径为 M4 10,741/13,905、M5 13,881/13,905；这是另一指标，不应与上述格式有效率共用名称。

M4 JSON 提取失败的 3,699 条映射中，2,987 条在 `JSONDecoder(strict=False)` 下可找到答案字段，支持字符串中未转义换行等控制字符是主要格式问题之一；M5 对应 26 条。该诊断不保证宽松读取出的答案满足原生格式或回答正确，也不是建议直接替换正式评分器。其余失败不能统一归因为同一种语法问题。

M4 选项键失败中，2,168 条以合法选项键开头但附带正文或其他字符，如输入 `s021424` 输出 `"answer_choice": "A. Proceed with liver biopsy"`，原生规则只接受 `"A"`；M5 对应 917 条。这里只统计前缀形态，不声称附带正文一定与选项语义一致。诊断未映射则不是 JSON 失败，例如 `s004434` 的 M4 返回 `Pharyngitis (Throat Infection)`，未命中冻结标签。M5 同类未映射数量甚至更多，因此 M4/M5 的有效率差距主要来自格式失败，而非额外诊断映射惩罚。

两者共享 MedRAG 提示词构造、检索与采样参数，但骨干分别为 Llama-3.1-8B-Instruct 和 Qwen3-8B，tokenizer/chat template 不同，Qwen 关闭 thinking 并有其上下文扩展设置。本次实际输出显示 Llama 在该提示词下更常违反 JSON 与纯选项键要求；这不是对所有任务或提示词的普遍模型能力结论。共享系统提示词使用 `Dict{... Str{A/B/C/...}}` 这样的格式描述，普通单选没有另加明确的“只输出键，不附正文”约束，也未启用 constrained decoding。由此存在提示词契约不够明确、对不同模型适配效果不一的问题，应作为实验局限披露，不能仅以“模型较弱”解释。

输出长度不是主要原因：13,905 个独立请求中 M4 仅 29 条以 `length` 结束，M5 为 1 条。现有证据不支持把数千条格式无效归因于显存扩容或输出截断。严格解析器按既定 JSON/选项要求工作，但这种评测同时测量了格式遵循，不能将最终低分全部归因于医学推理。

如后续比较格式稳健性，应另立统一、预先冻结的双模型提示词或解析规范，并保留当前原始结果；不能只为 M4 放宽标准后混入原主表。本次未实施此类实验。

<a id="record-0116"></a>

## 10.1 同骨干 M0/M2 对照：不能归因于 Llama 本身

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第363行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 10.1 同骨干 M0/M2 对照：不能归因于 Llama 本身

用户进一步指出 M0/M2 同样使用 Llama，却没有 M4 的严重格式问题。核查确认 M4 的模型目录经 `readlink -f` 解析与 M0/M2 均为 `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`。全量评分记录的[同骨干对比](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/llama_output_comparison.json)如下，分母仍为 15,616 条映射：

| 方法 | 格式有效率 | 原生有效率 | malformed_json |
|---|---:|---:|---:|
| M0 | 97.43% | 82.17% | 157 |
| M2 | 96.64% | 79.92% | 169 |
| M4 | 61.61% | 46.04% | 3,699 |
| M5 | 93.00% | 75.29% | 27 |

关键差别是最终回答协议。M0/M2 普通任务使用明确的原生格式说明，例如 `The answer must be exactly one option key string, e.g. {"answer":"A"}.`，要求 JSON-only，普通任务最终回答预算 64 tokens、temperature=0。M2 的多阶段推理在最终 reader 之前完成，不能因为它有内部推理就认为其最终 JSON 与 M4 同样复杂。robustness 任务另外允许 errors 数组和 2,048 tokens。

M4 使用 MedRAG 提示词，要求在同一个 JSON 中先写长 `step_by_step_thinking` 再写 `answer_choice`，temperature=0.7、预算 2,048 tokens；普通单选的纯键约束也较弱。长解释字符串内的换行或引号必须转义，否则即使最终答案存在也无法通过严格 JSON 解码。以上是代码中已确认的差异；温度、解释字段、检索上下文各自导致多少差异，尚无受控消融，不能给出独立因果贡献。

具体同题 `s021424`：M0 与 M2 均返回 `{"answer": "A"}`，M4 返回包含长解释的 JSON，答案字段为 `"A. Proceed with liver biopsy"`，M5 返回长解释和纯键 `"A"`。这直接说明同一题上的一部分差异发生在答案表达格式，而不是是否选出 A。本例不代表全量答案语义均正确。

因此更准确的结论是：**当前 M4 的提示词、生成配置与严格评分接口组合存在明显的格式适配问题；不能将其概括为 Llama 不会输出 JSON，也不能将 M4 的低分直接归因于骨干模型较弱。** 这次任务适配与启动检查未充分评估格式失败率，是评测实现上的局限。需要统一输出协议的独立实验才能进一步区分方法能力与接口损失；本次仅诊断并补充记录，没有改写主结果。

<a id="record-0118"></a>

## 10.3 回查 M4 输入调整是否导致格式失败（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第392行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 10.3 回查 M4 输入调整是否导致格式失败（2026-09-13）

回查 `m4_configuration_change.json`、`supervision.md`、原生提示验证脚本以及安装目录 Git diff，区分三件事：

- 正式输出开始前将 M4 对齐 M5：RRF-4/TextbooksWikipedia/k=5/temperature=0.2/检索上下文上限128000，改为 BM25+MedCPT/MedCorp/k=8/temperature=0.7/上限30000。该变更确实改变输入证据及采样条件，不能断言与格式失败无关。变更审计记录当时旧 M4/M5 预测数均为0，没有同批题目的旧配置对照结果来定位因果。
- 原生任务适配：扩展多选、诊断、关系、特殊选项键和 robustness；普通 A–N 单选保留上游 system。长 `step_by_step_thinking` JSON 是上游模板已有要求，并非此次适配从 M0/M2 的短 JSON 改造而来。当前 `src/template.py` 相对本地 Git HEAD 无差异。
- PubMed 行偏移加速：正文读取实现的工程变化。历史16条 M5 样本验证 prompt 文本、token IDs、采样参数相同；M4共享读取机制。该证据支持这次读取加速未改变这些验证样本的输入，但不是对前两项方法修改的等价性证明。

进一步全量检查归档 M4 普通 A–N 单选输入：3,034个独立 prompt 的 system 均与上游模板完全一致。对应4,012条评分映射仍有1,441条格式无效（35.92%），其中1,370条为 malformed_json。详见[输入历史专项审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_input_history_audit.json)。因此严重格式失败并不局限于新增原生任务适配；不能把它全归因于改写了特殊题型输入。该分组没有控制检索内容或温度，也不证明那些变量没有影响。

先前 `medrag_prompt_validation.json=passed` 实际检查的是输入保留、选项可见、长度和普通单选 system 一致；没有执行生成或证明全量输出格式稳定。应纠正“提示验证通过就代表回答协议充分验证”的解读。本次仅回查与记录，没有改动推理或评分。

<a id="record-0119"></a>

## 10.4 用户要求旧配置试跑：资源预检与样本准备

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第406行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 10.4 用户要求旧配置试跑：资源预检与样本准备

2026-09-13执行旧安装入口 `run_baseline.sh --variant m4 --check`，退出码1，`retrieval_ready=false`：Wikipedia Contriever/SPECTER 均缺 `faiss.index` 和 `metadatas.jsonl`。这是先前停止的大型构建资源，不是模型运行失败。已准备[100条同题对照计划](/home/data3/txy/docs/baselines/medrag.md#record-0119)，每种原生格式随机20条，不按原有输出成败筛选；seed=20260913，旧配置保存在 [old_config.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/old_m4_pilot/old_config.json)。仅用Textbooks不能代表旧两语料配置。未启动生成或恢复索引构建，不能提供旧配置有效率。需要先明确完整旧配置的索引恢复，还是单独做 temperature=0.2 的对照；二者不能混称。

<a id="record-0120"></a>

## 11. 当前 M4 输出格式修复试验（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第412行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 11. 当前 M4 输出格式修复试验（2026-09-13）

用户授权的两版100题试验详情合并如下；“未启动全量”指试验结束时。后续全量结构修复已完成，见第16节及[新M4结果](/home/data3/txy/docs/baselines/medrag.md#record-0395)。

2026-09-13。固定100个独立输入，每种原生格式随机20条，seed=20260913；样本在本次生成前固定，不按原答案有效性或正确性筛选。直接复用每题正式 M4 的完整 archived messages（包括真实检索证据），没有重新检索、换语料或降低温度。

<a id="record-0121"></a>

## 两个候选版本

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第418行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 两个候选版本

1. 本目录：在原 system/user 消息末尾添加明确输出契约，包括合法双引号 JSON、字符串转义、单选纯键、多选真实数组、诊断字符串，并提供仅作语法示意的例子。保留 step_by_step_thinking 字段。
2. [约束解码版本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot)：使用相同新提示，加上逐题 JSON Schema；约束合法选项键、多选非空无重复子集和关系标签。诊断为自由字符串，不传入 canonical labels 或金标。robustness 保留 errors 对象数组，限定可见文档 ID；不保证纠正内容正确或 ID 不重复。

骨干 Llama-3.1-8B-Instruct、BF16、temperature=0.7、top_p=1、seed=42、max_tokens=2048、max_model_len=131072、batch16。约束版本使用已安装 vLLM 0.8.5 的 xgrammar；这会改变允许采样的 token，是显式方法实现调整，不声称与原输出语义或 token 等价。多选集合按原可见选项顺序排列，与原生评分的集合语义一致。

<a id="record-0122"></a>

## 执行与评分

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第425行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 执行与评分

启动首次遇到共享 Python 环境 Transformers tokenizer 接口不兼容，未生成预测；随后恢复原 run_medrag.py 使用的 MedRAG Transformers 路径优先级，启动成功。错误日志保留。GPU0 借用采用既有 guard，外部进程恢复或空闲显存低于25 GiB时只停止自己的进程组；未操作 GPU1–3 的 M6/M7。

[运行器](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/m4_format_pilot.py)、[schema](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/m4_output_schema.py)、[评分器](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/report_m4_format_pilot.py)。100个schema在生成前均经xgrammar编译检查。评分复用冻结 objects 和原生 score，没有宽松解码或答案修复。原生有效率仍会因诊断未匹配而降低。

原始对照是这100题已保存的正式 M4 输出，没有用相同批次重新生成原提示对照；随机采样及批次差异未完全控制。五题型等权抽样不能直接估计全库有效率，正确率变化也不是全库准确率增益或显著性结论。本试验没有自动重跑全量，也没有改变M5。

详细计数见两个目录的 comparison.json 与 scored.jsonl；原始生成、扩展后的输入、配置、时间和退出记录全部保留。

<a id="record-0123"></a>

## 最终结果

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第435行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 最终结果

两版均完成100条独立输入，无漏题或重复；原正式对照100条保持原样。以下是该分层样本的计数/百分比，不是全库加权指标。

| 指标 | 同题原 M4 | 加强提示词 | 加强提示词 + JSON Schema |
|---|---:|---:|---:|
| 可提取严格 JSON 答案对象 | 74/100 | 93/100 | 99/100 |
| 原生评分器的格式有效 | 65/100 | 92/100 | 98/100 |
| 原生有效（包括诊断映射要求） | 53/100 | 76/100 | 84/100 |
| 原生回答正确 | 36/100 | 42/100 | 49/100 |

约束版99条正常停止输出均通过完整 `json.loads` 和逐题 JSON Schema 验证。多选题 `s001295` 达到2048 token预算，解释字符串被截断，保留为 malformed_json；另一条 ambiguous_diagnosis 是答案表达含糊。14条 unmapped_diagnosis 也继续按原规则计分。没有为这些样本重试、增加输出预算或改写答案。

[真实输出与错误形态验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/check_m4_format_pilot.py)还确认选项正文、嵌套诊断对象、重复多选键会被schema拒绝；[验证收据](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/schema_validation.json)保留截断失败。引擎适配阶段另有两次启动尝试没有生成预测：第一次请求后端与引擎auto不匹配；第二次本机V1后端不接受no-fallback选项。最终显式使用引擎和请求一致的xgrammar，相关日志均保留。未升级或修改共享依赖。

两个试跑guard最终exit_code=0、yield_reason=null。09:17后核查GPU0恢复为原有9863 MiB、0%利用率，仅保留其他用户进程。GPU1–3继续运行M6/M7。本次新增200条预测，均位于独立试验目录，正式M4的13,905条预测未覆盖。

结论：本试验支持采用明确输出契约与结构约束来缓解当前M4的接口损失，但仍需保留截断及语义无效。该100题已经用于方案选择，不能充当独立的后续确认集；正式部署前宜用新样本确认，方法比较应对M4/M5采用一致的输出策略。此次没有启动全量重测。

<a id="record-0124"></a>

## 约束版原始制品

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第454行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 约束版原始制品

- [对照计数](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/comparison.json)
- [逐题评分](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/scored.jsonl)
- [原始输出](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/predictions.jsonl)
- [有效配置](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/config.json)
- [完整修改后输入](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/inputs.jsonl)
- [结构验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/schema_validation.json)
- [GPU0保护退出记录](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/guard_result.json)

提示词版的[对照计数](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_pilot/comparison.json)、[逐题评分](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_pilot/scored.jsonl)同样保留。

<a id="record-0138"></a>

## 保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第627行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）

用户明确要求保存M7并让GPU1/2/3全力运行刚更新的M4，额外监督有效率。M7已13:45暂停，1646/13905（1634新＋12复用），1026有效/620无效/0失败、11完整分片；已核对单题terminal数量与独立保存点一致。保存点：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/；原阶段缓存保留，m7_pause.json记录暂停。M6仍52条暂停，不自动恢复两方法。

新活动包：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/README.md。全新生成13905条，复用原M4完整历史检索消息，加入已试验的明确输出契约与逐题JSON Schema/xgrammar。代码和修改后的全量输入独立保存，旧M4不覆盖。Llama3.1-8B、BF16、温度0.7、top_p1、seed42、2048输出及131072上下文不变。每卡vLLM常驻实例、.90显存、128并行序列、16384 prefill token、prefix cache/chunked prefill，109个锁保护动态分片。tmux v5-m4-structured；GPU0未动。

队列与有效率监控2项针对性检查通过；监控复现已有100题98格式有效/84原生有效/99Schema有效/1截断。监控分别报告格式/原生/Schema有效率、截断和题型原因，并单列100条方案选择输入之外的有效率；全部无效保留分母。原v5的3个共享输入存在不同gold映射，最终评分保留全部映射；去重有效率与gold无关。全量完成后自动合并并调用原生分析器，生成scores/、validity.json、complete.json、RESULTS.md。五分钟报告继续针对新M4。

<a id="record-0141"></a>

## 新M4结构约束修复全量完成（2026-09-13 15:04）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第664行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

正文与[已合入记录](#record-0077)相同，统一在该处维护。

<a id="record-0254"></a>

## M4_M5_INSTALLATION_REPORT.md

来源：[Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/M4_M5_INSTALLATION_REPORT.md](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/M4_M5_INSTALLATION_REPORT.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag`。

### M4 / M5 MedRAG 安装、调整与论文实施记录

**最新衔接（2026-09-13）：新M4结构约束修复已完成13,905输入，当前M4/M5的输出协议也不同。本文第10、14节保留原M4阶段配置及Methods草稿；最新对照与论文输出协议应读取[正式评测主记录](/home/data3/txy/docs/evaluation/v5.md#record-0084)及[最新五方法结果](/home/data3/txy/docs/evaluation/v5.md#record-0410)。**

首次整理：2026-09-12；论文实施记录补充：2026-09-13。索引与进程状态核对点仍为 2026-09-12 19:01，Asia/Shanghai；9 月 13 日复核源码、配置和已有评分产物。下文时间均为北京时间；原始会话与部分 `build.json` 使用 UTC，已换算。

本文作为 **M4 / M5 安装与接入阶段的统一实施文档**：记录做过的工作、调整前后、原因、生效范围和证据。后续相关修改继续追加到本文，保留原实验版本及其结果对应关系。

| 写作或复核需求 | 本文位置 |
|---|---|
| 实际安装过程、命令与产物 | 第 2–9 节 |
| 正式 V5 的方法参数与结果 | 第 10 节，优先使用运行目录的 `M4/config.json`、`M5/config.json` |
| 逐项调整前后、原因及影响 | 第 13 节 |
| 方法章节草稿、原生任务接口与评分细节 | 第 14 节 |
| 实验边界与记录维护 | 第 11、15 节 |

#### 1. 报告范围与结论

原 BASELINES.md 的安装与使用说明已合入本文，独立入口见[第16节](/home/data3/txy/docs/baselines/medrag.md#record-0254)；本文统一保存安装过程、失败处理、编号及配置演进。

整理时回看了 9 月 10 日安装会话的实际工具命令和返回结果，对照代码差异、配置、安装日志、索引完成记录及四份真实模型输出；同时查阅 9 月 11 日 V5 评测会话和结果目录，补充安装交付后的使用情况。第 3–9 节主要记录本安装会话实际完成的工作，第 10 节记录后续 V5 会话的工作，第 13–15 节提供逐项调整和论文写作材料。9 月 12–13 日的文档整理只读取既有运行证据并更新文档，没有重新推理、构建索引或操作运行进程。

| 编号 | 固定含义 | 输出中的机器名称 |
|---|---|---|
| **M4** | MedRAG + Llama-3.1-8B-Instruct | `medrag_llama31` |
| **M5** | MedRAG + Qwen3-8B | `medrag_qwen3` |

实际交付包括：独立 Python 环境、上游源码与本地适配、模型与语料接入、补齐 StatPearls、两套配置、JSONL 推理入口、检索准备脚本、回归检查、真实 GPU 冒烟结果及使用说明。

**版本变化是理解这次工作的关键：**9 月 10 日的独立安装中，M4 按 MedRGAG 对 MedRAG 的专门描述配置为 RRF-4，M5 按 MA-RAG 的 SR-RAG 描述配置为 BM25 + MedCPT。9 月 11 日，用户明确要求“m4重新配置成和m5一致，除了llama”，后续 V5 因此统一了两者的检索、语料和采样参数。

截至核对时，**V5 的 M4、M5 已各完成 13,905 个输入并完成评分审计**。历史 M4 的完整 Wikipedia RRF-4 索引仍不齐全；它已不再是 V5 的依赖。两种状态分别有独立证据，不能用 V5 完成来证明历史 RRF-4 完成。

#### 2. 实际执行时间线

| 时间 | 实际操作或完成事件 | 证据 |
|---|---|---|
| 09-10 12:03–12:06 | 检查工作目录、上级说明、GPU、磁盘、Python、已有模型和语料；拉取 MedRAG，阅读论文与两个现有项目 | 原始安装会话；上游 Git 记录 |
| 09-10 12:04:30 | 执行 `git clone https://github.com/gzxiong/MedRAG.git .` | 原始安装会话 |
| 09-10 12:06–12:11 | 创建 `.venv`，安装固定版本依赖；安装日志记录解析 82 个包 | `.cache/install.log` |
| 09-10 12:08–12:14 | 接入已有三库语料，下载新的 StatPearls 压缩包 | `.cache/statpearls-download.log` |
| 09-10 12:13–12:14 | Llama、Qwen 分别用提供的片段完成真实 GPU 推理 | `runs/smoke_llama31.jsonl`、`runs/smoke_qwen3.jsonl` |
| 09-10 12:15 | 解包、运行上游 StatPearls chunker、建立 BM25 索引 | 两份 StatPearls 处理日志 |
| 09-10 12:17–12:18 | Qwen 完成四库 BM25 → MedCPT → top-8 → 生成 | `runs/smoke_qwen3_full_medcorp.jsonl` |
| 09-10 12:18；12:23 | 先启动三个稠密编码任务；随后保存已完成分片，重启为带后续检查的统一准备脚本 | 原始会话；`.cache/prepare-processes.json` |
| 09-10 12:20–12:22 | 完成仓库级 Git LFS 安装；预取并验证 MedCPT Query Encoder | apt 下载日志；`.cache/medcpt-query.log` |
| 09-10 12:25 / 12:28 / 12:30 | Textbooks 的 MedCPT / SPECTER / Contriever 索引分别完成 | 各索引 `build.json` |
| 09-10 12:30–12:33 | Llama 在 Textbooks 上完成真实 RRF-4 冒烟；提交安装说明，Wikipedia 构建继续 | `runs/smoke_llama31_rrf4_textbooks.jsonl`；原始会话 |
| 09-10 22:08–22:18 | 按用户要求编号为 M4 / M5，更新配置、入口、已有记录和工作区指南 | 原始安装会话 |
| 09-11 04:45–04:47 | 用户要求 M4 与 M5 设置相同，仅保留 Llama backbone；V5 建立独立生效配置 | V5 会话；`m4_configuration_change.json` |
| 09-11 06:12:52 / 14:53:13 | V5 的 M5 / M4 各完成 6 个原生任务与长输入冒烟，随后复用这些输出 | `M5/smoke_complete.json`、`M4/smoke_complete.json` |
| 09-11 12:02:11 | Wikipedia 的 MedCPT 稠密索引完成 | 对应 `build.json` |
| 09-11 中午 | V5 会话停止已无评测用途的 Contriever、SPECTER 及旧准备启动脚本；保留已有文件 | V5 `supervision.md` |
| 09-11 12:42 前 | V5 补齐 PubMed 的 1,166 个行偏移文件并验证正文一致 | `pubmed_offset_validation.json` |
| 09-11 20:43:04 | M5 正式剩余 13,899 个输入完成，加 6 个冒烟共 13,905 个 | `M5/complete.json` 与覆盖验证 |
| 09-11 22:48:47；22:49:43 | M4 全部分片合并完成；四方法总评分与审计完成 | `M4/complete.json`、`analysis_finished_at.txt` |
| 09-12 | 回看上述历史，核对实际产物，补写本报告并更新文档入口 | 本报告 |
| 09-13 | 按论文写作要求，复核源码差异与评分接口，补充逐项调整台账、方法描述和后续维护规则 | 本文第 13–15 节 |

#### 3. 当时如何确定两个 baseline 的配置

用户最初给出了 `gzxiong/MedRAG`，并提到两篇 SOTA，但没有在该消息中列出论文名称。当时根据工作区已经存在的 MedRGAG 和 MA-RAG 项目，将它们作为对应论文进行核对，并将这个判断写入安装说明。

阅读范围包括 [MedRAG 原论文](https://aclanthology.org/2024.findings-acl.372/)、[MedRGAG 附录 A](https://arxiv.org/html/2510.18297v1#A1)、[MA-RAG 附录 D.2](https://arxiv.org/html/2603.03292v1#A4.SS2)，以及本机两个作者仓库中的检索、reader 和 `utils.py::inference` 实现。Qwen 的接口适配还参考了 [Qwen3-8B 模型说明](https://huggingface.co/Qwen/Qwen3-8B)。

MedRAG 原始工具支持多种语料与检索器。因此，“安装同一个 MedRAG”本身不能确定具体语料、检索器、top-k 和温度。最初写入本仓库的配置如下：

| 参数 | 9 月 10 日 M4 | 9 月 10 日 M5 |
|---|---|---|
| 配置文件（编号后） | [configs/m4.json](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/configs/m4.json) | [configs/m5.json](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/configs/m5.json) |
| 模型 | Llama-3.1-8B-Instruct | Qwen3-8B |
| 生成权重精度 / 引擎 | BF16 / Transformers | BF16 / Transformers |
| 语料 | Textbooks + Wikipedia | MedCorp：PubMed、Textbooks、StatPearls、Wikipedia |
| 检索 | BM25、Contriever、SPECTER、MedCPT，RRF-4 融合 | 每库 BM25 top-32，MedCPT Cross-Encoder 重排 |
| 最终片段数 | 5 | 8 |
| RRF 参数 | `rrf_k=100` | 配置保留该公共字段，重排链不使用它 |
| 温度 | 0.2 | 0.7 |
| 采样 | `do_sample=true`，`top_p=1`，`top_k=0` | 同左 |
| seed / 最大新增 token | 42 / 2,048 | 42 / 2,048 |
| 总上下文上限 | 131,072 | 32,768 |
| 检索上下文裁剪上限 | 128,000 | 30,000 |
| Chat template | 本地 Llama 模板 | 本地 Qwen 模板，`enable_thinking=false` |

M4 的取法依据 MedRGAG 附录 A 中专门描述 MedRAG 的四检索器/RRF 段落，以及该附录的两语料、top-5 和温度设置。该论文同时存在通用 BM25/MedCPT 说明，附录 C 概述还提到 MedCorp；当时已经记录这些表述之间的歧义，没有把所选解释写成唯一确定的逐项复现配置。

M5 对应 MA-RAG 的单轮 **SR-RAG**：四库、每库 32 条候选、重排后 8 条。温度 0.7、非 thinking 与 2,048 输出预算取自作者公开代码的 solver 默认值；SR-RAG 的完整独立提示及全部解码参数没有单列公开，因此使用上游 MedRAG 的 CoT / JSON 答案模板。其余运行参数由配置明确记录。

#### 4. 环境安装与模型接入

##### 4.1 上游与目录

安装根目录：

```text
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag
```

上游为 [gzxiong/MedRAG](https://github.com/gzxiong/MedRAG)，本地基于提交 `7599a728a28789fd601728c08d313b1148051f41`，提交日期为 2025-05-07。安装采用克隆源码并直接运行本地模块的方式。

##### 4.2 初始环境问题及处理

| 实际发现 | 实际处理 |
|---|---|
| `python` 命令不存在，系统 `python3` 为 3.10.12 | 使用 `/usr/bin/python3` 创建项目 `.venv` |
| `uv` 的 Snap 启动器遇到目录权限问题 | 使用实际二进制 `/snap/astral-uv/current/bin/uv`，版本 0.12.6 |
| 既有 MedRGAG 环境存在 Transformers 5.16.1 与 vLLM 0.8.5 不兼容等依赖混杂 | 为本次安装建立独立环境并固定依赖 |
| 根分区仅约 7 GB 空闲，数据盘约 2.6 TB 空闲 | 将虚拟环境、uv 缓存、临时文件、下载和新索引放在本项目所在数据盘 |
| 系统默认 Java 8，与采用的 Pyserini / Lucene 环境不匹配 | 复用 `/home/data3/txy/.cache/jdk/temurin21`，在运行脚本设置 `JAVA_HOME` |
| 系统缺 Git LFS | 下载 Ubuntu 的 git-lfs 包，在 `.cache/git-lfs` 解包，链接到 `.venv/bin`，只对本仓库初始化 |
| 本机 4 张 H20 中 GPU 0 / 3 当时有其他任务 | 安装阶段在 GPU 1 / 2 做推理与编码；GPU 选择通过环境变量传入 |

安装使用的直接依赖见 [requirements-baseline.txt](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/requirements-baseline.txt)，完整冻结版本见 [requirements-baseline.lock.txt](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/requirements-baseline.lock.txt)：

| 包 | 固定版本 | 用途 |
|---|---|---|
| torch | 2.6.0 | GPU 推理；安装结果 CUDA 12.4 |
| transformers | 4.51.3 | Llama / Qwen3 模型和模板接口 |
| accelerate | 1.10.1 | 模型设备分配 |
| sentence-transformers | 3.4.1 | 上游稠密编码路径 |
| faiss-cpu | 1.12.0 | CPU 上的 Flat 向量索引与搜索 |
| numpy | 1.26.4 | 向量及排序 |
| python-liquid | 1.10.2 | 上游提示模板 |
| openai | 1.86.0 | 上游模块依赖 |
| pyserini | 1.0.0 | BM25；兼容本机已有 Lucene 9.9 索引 |
| tiktoken | 0.6.0 | 上游 tokenizer 依赖 |
| tqdm | 4.67.1 | 进度记录 |

安装日志记录解析、安装 82 个包。之后执行了 `uv pip check`、核心模块导入及 CUDA 可用性检查，结果通过。

##### 4.3 权重从哪里来

LLM 和 Cross-Encoder 使用本机已有完整权重，通过以下链接接入：

| 项目路径 | 实际目标 | 观察到的文件 |
|---|---|---|
| `models/Llama-3.1-8B-Instruct` | `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct` | 4 个 safetensors 分片 |
| `models/Qwen3-8B` | `/home/data3/txy/models/Qwen3-8B` | 5 个 safetensors 分片 |
| `models/MedCPT-Cross-Encoder` | `/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder` | 本地 PyTorch 权重及 tokenizer |

当时还检查了本机 NousResearch 的 Llama 目录，但它缺少完整权重，最终选择上述完整目录。Contriever、SPECTER、MedCPT Article / Query Encoder 通过 Hugging Face 接口加载，缓存位于 `.cache/huggingface`。Query Encoder 另做了一次 CPU 编码检查，输出形状为 `(1, 768)`，记录在 [.cache/medcpt-query.log](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/medcpt-query.log)。

##### 4.4 安装命令记录

以下为历史主命令整理，工作目录为安装根目录。它们说明当时怎样完成安装；已有目录和结果文件现在已经存在。

```bash
git clone https://github.com/gzxiong/MedRAG.git .
mkdir -p .cache/tmp
/snap/astral-uv/current/bin/uv venv --python /usr/bin/python3 .venv
TMPDIR="$PWD/.cache/tmp" UV_CACHE_DIR="$PWD/.cache/uv" \
  /snap/astral-uv/current/bin/uv pip install --python .venv/bin/python \
  -r requirements-baseline.txt > .cache/install.log 2>&1
/snap/astral-uv/current/bin/uv pip check --python .venv/bin/python
/snap/astral-uv/current/bin/uv pip freeze --python .venv/bin/python \
  > requirements-baseline.lock.txt
```

Git LFS 的实际安装流程是先在 `.cache/downloads` 执行 `apt download git-lfs`，随后：

```bash
dpkg-deb -x .cache/downloads/git-lfs_3.0.2-1ubuntu0.3_amd64.deb .cache/git-lfs
ln -s "$PWD/.cache/git-lfs/usr/bin/git-lfs" .venv/bin/git-lfs
PATH="$PWD/.venv/bin:$PATH" git lfs install --local
.venv/bin/git-lfs version
```

#### 5. 语料接入与 StatPearls 重建

##### 5.1 复用已有三库

对 Textbooks、Wikipedia、PubMed，分别在 `corpus/<name>/` 下建立本地目录，并将已有的 `chunk`、`index/bm25` 及存在的 `line_offsets` 链接到 `/home/data3/txy/MedRGAG/corpus/<name>/`。

这样，已有语料与 BM25 直接可用，新建稠密索引则落在本安装目录自己的 `corpus/<name>/index/<encoder>/`。当时 PubMed 没有可复用的行偏移；其本地偏移是在后续 V5 会话中补齐的。

##### 5.2 为什么重新准备 StatPearls

旧 MedRGAG 目录中的 StatPearls 是未完成的 aria2 下载，无法作为完整第四库使用。因此下载 NCBI 的新副本到本项目，保留旧目录原状。

下载地址为 [NCBI StatPearls 压缩包](https://ftp.ncbi.nlm.nih.gov/pub/litarch/3d/12/statpearls_NBK430685.tar.gz)，本次下载发生于 2026-09-10。关键命令为：

```bash
aria2c --continue=true --max-connection-per-server=4 --split=4 \
  --max-tries=3 --retry-wait=5 --connect-timeout=15 --timeout=30 \
  --summary-interval=30 --console-log-level=warn --download-result=full \
  --file-allocation=none --dir="$PWD/corpus/statpearls" \
  --out=statpearls_NBK430685.tar.gz \
  'https://ftp.ncbi.nlm.nih.gov/pub/litarch/3d/12/statpearls_NBK430685.tar.gz' \
  > .cache/statpearls-download.log 2>&1

tar -xzf corpus/statpearls/statpearls_NBK430685.tar.gz -C corpus/statpearls
.venv/bin/python src/data/statpearls.py > .cache/statpearls-chunk.log 2>&1

JAVA_HOME=/home/data3/txy/.cache/jdk/temurin21 \
PATH="/home/data3/txy/.cache/jdk/temurin21/bin:$PWD/.venv/bin:$PATH" \
  .venv/bin/python -m pyserini.index.lucene \
  --collection JsonCollection --input corpus/statpearls/chunk \
  --index corpus/statpearls/index/bm25 \
  --generator DefaultLuceneDocumentGenerator --threads 8 \
  > .cache/statpearls-index.log 2>&1
```

使用了上游 [src/data/statpearls.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/src/data/statpearls.py)，该文件没有本地修改。实际结果为：

- 压缩包 **1,901,131,797 字节**，aria2 记录下载成功，平均速度约 5.3 MiB/s。
- chunker 处理 **9,648 个 XML**，生成 **9,646 个非空 JSONL 分片**。
- BM25 索引含 **372,148 条片段**；`unindexable/empty/skipped/errors` 均为 0，索引阶段日志耗时约 3 秒。

证据：[下载日志](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/statpearls-download.log)、[分片日志](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/statpearls-chunk.log)、[BM25 日志](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/statpearls-index.log)。

#### 6. 对 MedRAG 实际改了什么

##### 6.1 模型生成接口：`src/medrag.py`

保留上游单轮 MedRAG 答案流程与提示模板，在 [src/medrag.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/src/medrag.py) 做了以下适配：

1. 将 `utils/template/config` 改为包内相对导入；模板文件通过源码位置定位，使项目入口能够稳定导入。
2. 支持注入检索器，延迟初始化检索资源。输入已带 `snippets` 时，可以独立验证 reader。
3. 增加 `generation_kwargs`、`chat_template_kwargs`、`max_length`、`context_length`，让实际运行参数由配置传入。
4. 补充 Qwen 模型识别，从模型配置读取上下文能力；通过 chat template 参数关闭 Qwen3 thinking。
5. 将实际 tokenizer 交给 Transformers pipeline，沿用上游已有的 BF16 设置，改为读取模型自己的 EOS 配置。BF16 本身不是本次新增的精度改造。
6. 对已经套好 chat template 的字符串设置 `add_special_tokens=False`，避免 Llama 重复加入 BOS；设置 `return_full_text=False`，直接记录生成部分。
7. 使用明确的 `max_new_tokens=2048`；避免同时传入冲突的 `max_length`。完整提示加输出预算超过模型上限时直接报错。
8. 保留上游对检索上下文的裁剪，并新增 `context_truncated_tokens`；记录 messages、原始生成文本、重编码得到的 prompt / completion token 数。

`enable_thinking=false` 控制 Qwen 的 thinking 模式；上游模板本身仍要求解释并给出答案，这两者在报告中分别记录。

##### 6.2 单轮 BM25 + MedCPT：`src/baselines.py`

新增 [src/baselines.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/src/baselines.py)，主要实现：

```text
question
  → 四个语料各取 BM25 top-32（k1=0.9，b=0.4）
  → 合并最多 128 个候选，按作者实现的 BM25 分数顺序排列
  → 将 [question, document.content] 交给 MedCPT Cross-Encoder
  → 按重排 logits 降序选择 top-8
  → MedRAG 模板 + Llama 或 Qwen 生成
```

Cross-Encoder 输入最大 512 token，按模型 tokenizer 截断。该链使用 Cross-Encoder 重排；它与 RRF-4 中用于稠密检索的 MedCPT Query / Article Encoder 是不同用途的模型。

同文件提供 `missing_resources` 和 `make_retriever`，普通运行前检查所需语料与索引是否存在，缺资源时报告路径。`--check` 是资源存在性检查，真实链路通过独立冒烟验证。

##### 6.3 语料与稠密索引辅助：`src/utils.py`

在 [src/utils.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/src/utils.py) 中新增两组语料别名 `TextbooksWikipedia` 和 `MedCorp3`；本次独立 M5 实际使用完整 `MedCorp`。

修改 `Retriever.idx2txt`，优先利用已有 `.u64le` 行偏移定位正文，避免每条命中都重读整个 JSONL 分片；没有偏移时保留原读取路径。

对编码分片和最终 FAISS 文件采用临时文件写完再替换的方式，配合跳过已完成 `.npy`，支持长时间构建中断后的分片复用。

历史 M4 的 RRF-4 保留上游检索和融合逻辑：每个检索器在每个库召回 `max(2*k, 100)` 条，当前 k=5 时为 100；同检索器跨库按其分数排序，然后按 `1/(rrf_k+rank)` 融合，最终取 5 条。Contriever / MedCPT 使用内积，SPECTER 使用 L2；索引为 FAISS Flat，`HNSW=False`。

##### 6.4 新增运行与记录入口

| 文件 | 实际用途 |
|---|---|
| [run_baseline.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/run_baseline.py) | 读取原始多选 QA JSONL，选择配置，调用检索和 reader，逐条保存结果 |
| [run_baseline.sh](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/run_baseline.sh) | 固定项目 Python、JDK、缓存和线程环境 |
| [prepare_rrf4.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/prepare_rrf4.py) | 按 encoder 依次构建 Textbooks、Wikipedia 的缺失稠密索引 |
| [prepare_rrf4.sh](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/prepare_rrf4.sh) | 管理三路编码进程，全部成功后触发完整历史 M4 检查与冒烟 |
| [test_baselines.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/test_baselines.py) | 使用真实本地 tokenizer 和模拟生成器验证接口行为 |
| [examples/smoke.jsonl](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/examples/smoke.jsonl) | 带明确提供的片段，用于 reader 冒烟 |
| [examples/retrieval_smoke.jsonl](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/examples/retrieval_smoke.jsonl) | 不带片段，用于真实检索链冒烟 |
| [.gitignore](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.gitignore) | 排除虚拟环境、模型、语料、缓存、索引与运行输出等大文件 |

独立入口输入为 `id/question/options`，可选 `snippets`；支持 `--limit`、`--model`、`--corpus`、`--db-dir`。输出文件必须是新文件，逐题写入并刷新，包含实际配置、检索模式、文档、分数、响应、生成记录和耗时。每题设置 seed 42，显式覆盖语料或模型时写入结果。

9 月 10 日检查已有 benchmark 输入后，发现它包含必须保留的 `fixed_evidence`。因此独立多选入口对非空 `fixed_evidence` 明确报错，等待原生任务适配；这一接口扩展随后在 V5 的独立 runner 中完成。

#### 7. RRF-4 索引为什么重建，最终完成了多少

##### 7.1 下载问题与本地构建

安装当日探测上游预计算向量的 SharePoint 链接，HEAD 和 GET 均遇到 HTTP 403。也查阅了官方 Hugging Face MedRAG 数据集列表，未找到可直接替代的官方向量资源，于是转为本地编码。

构建调用上游 `embed` / `construct_index`，batch size 128；Contriever 使用 mean pooling，SPECTER、MedCPT 使用 CLS pooling；保存 768 维 FP32 向量并构建精确 Flat 索引。Wikipedia 有 646 个语料分片、约 2,991 万条片段，单路向量约 92 GB；三路向量连同最终索引预计约 550 GB。这解释了最初 M4 比仅需已有 BM25 和 Cross-Encoder 的 M5 多出大量准备工作。

09-10 12:18 先分别启动三个 encoder；12:23 停止自己的原 worker，保留已完成分片，再由统一脚本恢复，以增加“全部完成后检查并冒烟”的步骤。记录的 supervisor PID 为 1327922，三个 worker 为 1327925 / 1327926 / 1327927：Contriever、SPECTER 在 GPU 1，MedCPT 在 GPU 2。

记录入口：[.cache/prepare-processes.json](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-processes.json)、[总日志](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-rrf4.log)、[Contriever 日志](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-contriever.log)、[SPECTER 日志](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-specter.log)、[MedCPT 日志](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-medcpt.log)。这里的 PID 是历史记录；本次核对时这些进程已经不存在。

##### 7.2 核对到的真实状态

| 语料 / Encoder | 完成的 embedding 分片 | 最终索引 | 向量数 / 完成时间 |
|---|---:|---|---|
| Textbooks / Contriever | 18 / 18 | 已完成 | 125,847；09-10 12:30:39 |
| Textbooks / SPECTER | 18 / 18 | 已完成 | 125,847；09-10 12:28:20 |
| Textbooks / MedCPT | 18 / 18 | 已完成 | 125,847；09-10 12:25:19 |
| Wikipedia / Contriever | 287 / 646 | 未生成 | 后续已停止；保留约 53.45 GB 分片 |
| Wikipedia / SPECTER | 250 / 646 | 未生成 | 后续已停止；保留约 49.23 GB 分片 |
| Wikipedia / MedCPT | 646 / 646 | 已完成 | 29,913,202；09-11 12:02:11 |

完成信息来自各 `build.json`，未完成计数来自实际 `.npy` 文件。Textbooks 三路 `seconds` 分别约为 428 / 289 / 108 秒，是恢复后该次构建段的计时，不代表包括首次编码在内的完整总耗时；Wikipedia MedCPT 记录为约 85,012 秒。

09-11 V5 会话确认统一配置不再使用这些稠密索引后，停止了 Contriever、SPECTER 和旧 supervisor；MedCPT 已提前正常完成。已生成目录约 271 GiB，按该会话记录保留，没有删除。

因此，`.cache/rrf4-complete.txt` 没有生成，完整 Textbooks + Wikipedia 的历史 M4 自动冒烟没有执行。**历史 M4 通过的是 Textbooks 范围内的完整四检索器检查。**

#### 8. 安装阶段实际做过哪些验证

##### 8.1 依赖与接口检查

安装会话执行并通过了：依赖一致性与模块导入检查、CUDA 检查、`bash -n`、`git diff --check`，以及 [test_baselines.py](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/test_baselines.py)。回归检查覆盖：

- 真实 Llama 模板只包含一个 BOS；Qwen 非 thinking 模板按预期生成。
- 提供片段时不初始化不需要的检索器；pipeline 仅返回生成部分。
- 2,048 输出预算传递正确，不与 `max_length` 冲突；提示超限能够报错。
- 检索上下文裁剪量有记录。
- RRF 合并保留四个检索器的贡献；行偏移准确读取指定记录。

还单独验证了带 `fixed_evidence` 的输入被独立多选入口拒绝，退出码为 2，且不产生结果文件。编号更新后又验证了六种别名解析一致，以及旧结果仅新增编号字段。

上述接口回归使用真实 tokenizer 和模拟生成器；下面四项使用真实 8B 权重完成 GPU 推理。

##### 8.2 四份真实冒烟输出

四项均使用同一道面神经多选题；前两项使用人为提供、明确标注的示例片段，后两项实际执行检索。

| 输出文件 | 验证范围 | 片段数 | Prompt / Completion token | 逐题耗时 | 输出答案字段 |
|---|---|---:|---:|---:|---|
| [smoke_llama31.jsonl](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_llama31.jsonl) | M4 reader，提供片段 | 1 | 308 / 141 | 3.54 s | A |
| [smoke_qwen3.jsonl](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_qwen3.jsonl) | M5 reader，提供片段 | 1 | 290 / 117 | 4.08 s | A |
| [smoke_qwen3_full_medcorp.jsonl](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_qwen3_full_medcorp.jsonl) | M5，完整四库 BM25 + MedCPT | 8 | 1,708 / 234 | 13.87 s | A |
| [smoke_llama31_rrf4_textbooks.jsonl](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_llama31_rrf4_textbooks.jsonl) | M4，显式 `--corpus Textbooks` 的 RRF-4 | 5 | 1,256 / 235 | 10.27 s | A |

逐题耗时来自 runner 在模型与检索器初始化之后的计时，不能当作包含下载、加载权重和建索引的端到端启动耗时。token 数为安装入口对文本重编码后的计数。最后一份输出明确记录 `context_truncated_tokens=0`；前三份生成于该记录字段加入之前。

当时验证了 M5 的返回数为 8、重排分数降序、语料为完整 MedCorp；验证了 Textbooks M4 的 RRF-4、top-5 和零裁剪。回答保留原始形式：Llama 输出曾出现 `Dict{...}` 前缀或 Markdown 代码围栏，因此这些冒烟验证的是模型与流程可运行、答案字段为 A，不构成严格 JSON 输出率或正式准确率评测。

历史推理主命令如下；`llama31/qwen3` 当时尚未改成 M 编号，现在仍保留为对应别名：

```bash
CUDA_VISIBLE_DEVICES=1 ./run_baseline.sh --variant llama31 \
  --input examples/smoke.jsonl --output runs/smoke_llama31.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant qwen3 \
  --input examples/smoke.jsonl --output runs/smoke_qwen3.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant qwen3 \
  --input examples/retrieval_smoke.jsonl --output runs/smoke_qwen3_full_medcorp.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant llama31 --corpus Textbooks \
  --input examples/retrieval_smoke.jsonl --output runs/smoke_llama31_rrf4_textbooks.jsonl
```

#### 9. M4 / M5 编号更新具体改了哪些文件

用户要求按顺序取 M 版本时，现有 benchmark 已使用 M0–M3，因此接续为 M4（Llama）、M5（Qwen）。09-10 晚间实际完成：

1. `configs/llama31.json` → `configs/m4.json`，`configs/qwen3.json` → `configs/m5.json`，增加 `method_id`，保留原机器名称。
2. 运行入口接受 `m4/M4/llama31` 和 `m5/M5/qwen3`，分别加载同一套配置；输出同时保存 `method_id` 与 `method`。
3. 四份已有 smoke JSONL 和两份资源检查 JSON 补充编号；对修改前后内容进行比较，其他配置、提示、检索、响应和耗时保持一致。保留原文件名。
4. 更新 README、BASELINES、回归检查路径及工作区指南中的编号对应关系。
5. 更新未来准备脚本使用的命令和 smoke 文件前缀；当时有 Bash 脚本运行，因此通过替换脚本文件保留旧进程已打开的版本，同时保留旧参数别名。
6. 检查六个别名输出一致、记录内外编号一致、脚本语法和 diff 格式通过；该次编号操作没有重跑推理。

#### 10. 后续 V5 怎样使用这套安装

这部分依据另外一次 V5 评测会话的配置、runner、监督日志和完成记录整理。完整评测包位于：

```text
/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5
```

##### 10.1 M4 配置更改及实际生效值

09-11 04:45 的用户指令要求 M4 与 M5 设置一致、仅保留 Llama。更改前后配置保存在 [m4_configuration_change.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_configuration_change.json)。该文件记录更改时旧配置下 V5 的 M4 / M5 预测数均为 0。

| 参数 | V5 M4 | V5 M5 |
|---|---|---|
| Backbone | Llama-3.1-8B-Instruct | Qwen3-8B |
| 语料 / 检索 / 最终 k | 完整四库 MedCorp；每库 BM25 32；MedCPT 重排 8 | 同左 |
| 引擎 / 生成精度 | vLLM 0.8.5 / BF16 | 同左 |
| 温度 / top-p / seed | 0.7 / 1 / 42 | 同左 |
| 输出预算 | 2,048 token | 同左 |
| 检索上下文裁剪 | 30,000 个本模型 token | 同左 |
| 实际总上下文 | 131,072 | 131,072，YaRN factor 4，原始长度 32,768 |
| 模型模板适配 | Llama 原生模板 | Qwen 模板，非 thinking |
| 原生任务接口 | 共用 `code/run_medrag.py::messages` | 同左 |

**复核 V5 应读取保存的实际运行配置：**[M4/config.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/M4/config.json)、[M5/config.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/M5/config.json)。V5 `configs/m5.json` 仍保留基础值 32,768，`load_config()` 在运行时扩展为 131,072 并加入 YaRN；保存于 `M5/config.json` 的才是此次运行实际值。

本安装目录的 `configs/m4.json` 保留 9 月 10 日的历史 RRF-4 配置；运行本目录 `run_baseline.sh --variant m4` 仍会选中它。V5 使用自己的配置与 runner。

##### 10.2 原生 benchmark 适配与运行环境

V5 [code/run_medrag.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/run_medrag.py) 复用这里的 `make_retriever` 和上游 MedRAG 模板，增加原生单选、多选集合、诊断、关系标签及 robustness 错误文档列表的输出约定。

检索查询仍只取 `question`；完整 `fixed_evidence` 放入 reader 可见输入。追加检索内容按 30,000 token 裁剪，必需证据保留，完整提示加输出预算超限即报错。输出经过明确字段映射后交给原生评分器，无效输出按协议算错。

该 runner 使用已有 MedRGAG Python 环境提供 vLLM，同时优先导入本 MedRAG `.venv` 中的兼容依赖；独立安装的锁文件中没有新增 vLLM。正式生成使用 batch 16、prefix caching；在 vLLM 中 `top_k=-1` 表示不做 top-k 采样筛选，对应独立 Transformers 配置中的 `top_k=0`。

长输入核对发现 Qwen 原生输入最长达到 69,721 token，超过独立安装的 32K 设置，因此加入 YaRN 4 倍扩展。配置文件和输出中保留了这一原因。

##### 10.3 后续性能处理与调度

V5 中补齐了 PubMed 1,166 个 `.u64le` 行偏移文件，共 191,189,608 字节。一次 32 条命中正文的前后比较完全一致，读取耗时从约 4.326 秒降至 0.00151 秒，见 [pubmed_offset_validation.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/pubmed_offset_validation.json)。这是正文读取环节的测量，不代表整个检索或推理链的加速倍数。

M5 在 GPU 2 接续 M0 队列运行；M4 后续按用户授权使用 GPU 0，并逐步增加 GPU 1 / 2。M4 先保留 5,830 条结果，再将剩余 8,075 条按完整 batch 分成两路；随后汇总为 9,062 条，剩余 4,843 条分成三路。GPU 0 出现其他进程时，自己的守护逻辑让出 GPU，未完成部分最终在 GPU 1 续跑。分片及提示覆盖检查通过后合并，历史文件保留。

上述调度改变记录在 V5 [supervision.md](/home/data3/txy/docs/evaluation/v5.md#record-0393)，没有改变生成设置或遗漏输入。显存份额随调度调整；这不应混同为算法配置变化。

##### 10.4 已完成的正式验证与结果

两者分别做了 6 个覆盖原生格式及长输入的真实冒烟，并把这些预测纳入正式结果复用。最终每个方法有 13,905 条预测和对应提示记录；完整评分共覆盖 6,104 个比较单元、13,000 个选中判断，每方法 15,616 条评分映射。

| 已有正式记录 | M4 | M5 |
|---|---:|---:|
| 完整输入 / 最终生成调用 | 13,905 | 13,905 |
| ALL 单元平均原生任务正确率 | 29.76% | 47.35% |
| Prompt token 总数 | 48,325,826 | 49,856,833 |
| Completion token 总数 | 5,821,549 | 3,685,268 |

分数为本地 V5 的单元等权指标，ALL 对单元去重；不能直接解释成 13,905 道题的简单正确率，也不是论文原表结果。token 总数来自 vLLM 实际 token ID 记录的审计。

[validation.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/validation.json) 显示 `status=complete`、M4 / M5 缺失预测均为 0、全部方法重复预测为 0；[artifact_audit.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/artifact_audit.json) 为 `passed`，缺失提示记录为 0。分类分数、指标定义与评测限制见 [RESULTS.md](/home/data3/txy/docs/evaluation/v5.md#record-0392) 及同目录 README。

#### 11. 复现边界与保留事项

1. **论文配置有明确解释边界。**初始 M4 对 MedRGAG 文中不完全一致的说明作了有记录的选择；M5 的部分 SR-RAG 解码细节取自作者 solver 默认值。没有作者逐题 baseline 检索缓存可核对，不能宣称精确复现论文表格。
2. **当前 V5 与初始独立安装不同。**V5 M4 已统一为 BM25 + MedCPT；M5 加入 YaRN；两者改用 vLLM 和原生任务适配。它们的配置及结果应按各自运行目录解释。
3. **历史完整 RRF-4 仍未完成。**Wikipedia 的 Contriever、SPECTER 仅保留部分分片，完整自动冒烟没有成功标记。当前 V5 不依赖这些索引。
4. **语料快照不同。**StatPearls 使用 2026-09-10 下载的新副本，372,148 条片段不同于原论文约 301.2k 的旧快照；其他三库复用本机已有数据。
5. **验证粒度不同。**四份安装冒烟证明所列流程可运行；正式评测使用 V5 原生协议。Transformers 与 vLLM、不同 tokenizer 和上下文设置，即使 seed 相同也不保证逐 token 一致。原始响应及无效输出应按各阶段实际评分规则解释。
6. **安装文件以本机资源为基础。**模型与大部分语料是软链接，Java 也是既有本机目录；只复制源码不能得到完整运行资源。缓存、模型、语料和结果受 `.gitignore` 排除，但在本机保留。报告整理时本地修改尚未形成新的 Git 提交。
7. **调整效果的证据范围。**本报告对应的正式 V5 结果来自 seed 42 的已记录运行，没有针对 RRF → BM25/MedCPT、引擎切换或 YaRN 分别开展控制其他条件的消融。M4 与 M5 采用共同的检索与采样协议，但 tokenizer、chat template、权重及 Qwen 上下文扩展不同；30,000 token 裁剪按各自 tokenizer 计数，可见文本边界不保证相同。
8. **推理与统计口径。**正式生成默认每输入产生一个输出，不含候选集成或投票；不同输入可按相同 question 复用检索缓存，因此最终生成调用数不等于独立检索次数。采样输出和单次正文读取计时不能推出逐 token 确定性或端到端加速结论。
9. **评分覆盖范围。**输出按第 14.3 节解析；开放诊断按冻结标签的归一化精确匹配处理，未额外进行医学同义表达判分。Robustness 的错误文档识别有独立评分，纠正文本的语义质量未评分；这些边界也适用于第 14.4 节的论文草稿。

#### 12. 证据与文件入口

| 要核对的内容 | 入口 |
|---|---|
| 原始安装、验证、编号操作的会话记录 | [2026-09-10 安装会话](/home/data3/txy/.codex/sessions/2026/09/10/rollout-2026-09-10T12-03-45-01a0897c-63e4-7803-b918-7910e00692e7.jsonl) |
| 后续 V5 用户配置变更指令 | [2026-09-11 V5 会话](/home/data3/txy/.codex/sessions/2026/09/11/rollout-2026-09-11T03-51-50-01a08ce0-63a0-7a82-880c-a3d561dde361.jsonl) |
| 独立安装的日常使用与历史参数 | [BASELINES.md](/home/data3/txy/docs/baselines/medrag.md#record-0254) |
| 依赖安装结果 | [.cache/install.log](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/install.log)、[requirements-baseline.lock.txt](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/requirements-baseline.lock.txt) |
| Textbooks 三路完成记录 | [Contriever](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/textbooks/index/facebook/contriever/build.json)、[SPECTER](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/textbooks/index/allenai/specter/build.json)、[MedCPT](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/textbooks/index/ncbi/MedCPT-Article-Encoder/build.json) |
| Wikipedia 已完成的 MedCPT 索引 | [build.json](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/wikipedia/index/ncbi/MedCPT-Article-Encoder/build.json) |
| V5 完整方法、数据和运行协议 | [V5 README](/home/data3/txy/docs/evaluation/v5.md#record-0391) |
| 工作区目录和后续任务入口 | [MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/docs/workspace.md#record-0001) |

本报告中的完成状态优先采用实际结果、配置和完成标记；较早的工作区摘要中“仍在构建”“尚无正式 benchmark”等语句属于历史快照，已经在本安装说明中补充了后续状态。

#### 13. 逐项调整台账：调整前、调整后、原因与影响

本节将第 3–10 节的执行记录转换为论文实施台账。“调整前”分别标明上游代码、初始安装或后续 V5 流程，避免将已有能力计作本地新增工作。表内日期为实施日期；2026-09-13 仅补充记录。

##### 13.1 方法与实验协议

本表涉及的证据集中在本仓库 [初始 M4](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/configs/m4.json)、[初始 M5](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/configs/m5.json)、[检索实现](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/src/baselines.py)，以及 V5 [配置变更记录](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_configuration_change.json)、[原生任务 runner](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/run_medrag.py)。

| 日期 / 工作 | 调整前 → 实际调整后 | 原因、影响与最终生效范围 |
|---|---|---|
| 09-10 模型选择 | 上游可选多种 reader → 配置两个本地 8B instruct reader：Llama-3.1 和 Qwen3 | 为两种 backbone 建立 benchmark baseline；生成权重采用 BF16。模型选择属于实验设置 |
| 09-10 初始 M4 | 上游通用检索工具 → Textbooks + Wikipedia、RRF-4、top-5、温度 0.2 | 依据当时对 MedRGAG baseline 段落的解释；这是历史安装配置，正式 V5 已更改 |
| 09-10 初始 M5 | 上游单检索器 / RRF 组合 → 新增四库 BM25 32/库 + MedCPT 重排 top-8 | 实现 MA-RAG 单轮 SR-RAG 对应的检索流程；同一实现随后供 V5 M4/M5 共用 |
| 09-10 候选重排细节 | 新检索链尚不存在 → BM25 `k1=0.9,b=0.4`；合并至多 128 条；`[question,content]` 输入 Cross-Encoder，最大 512 token | 将召回、候选排序、重排输入和长度规则写成明确实现。重排正文不拼入标题；reader 展示片段时包含标题 |
| 09-10 采样设置 | 上游本地生成分支显式 `do_sample=False` → 配置化采样；seed 42、top-p 1、无 top-k 筛选、输出上限 2,048 | 支持所选 baseline 的温度；采样设置会影响回答。初始 M4/M5 温度不同，V5 均为 0.7 |
| 09-10 Qwen 模板 | 上游缺少 Qwen 专门分支和 thinking 参数传递 → 识别 Qwen 配置并传入 `enable_thinking=false` | 使 Qwen3 在选定模式下运行；上游模板仍要求解释与答案，非 thinking 不等于只输出选项 |
| 09-10 语料快照 | 旧 StatPearls 下载未完成 → 下载新副本、上游切分、BM25 入库 372,148 条 | 补齐第四库；会改变相对于旧论文快照的可检索内容。其余三库复用已有资源 |
| 09-10 独立输入边界 | 原始多选题入口未承接 benchmark 必需证据 → 对非空 `fixed_evidence` 报错 | 防止把必需证据遗漏后当成已适配 benchmark；该阶段只交付原始多选 QA 入口 |
| 09-11 M4 协议统一 | 历史 RRF-4 / 两库 / top-5 / 0.2 → 四库 BM25+MedCPT / top-8 / 0.7；检索上下文 128,000 → 30,000 token | 按用户明确指令统一 M4/M5 设置。变更记录显示当时旧设置下 V5 两方法预测数均为 0 |
| 09-11 原生任务适配 | 原始 MCQ 模板 → 共享任务格式适配，支持多选、诊断、关系标签、robustness；保留完整给定证据 | 使相同 baseline 可回答 V5 原生任务。增加的是任务接口约定，模板不再与上游原始 MCQ 提示逐字相同 |
| 09-11 Qwen 长上下文 | 独立安装最大 32,768 → V5 运行时 131,072，YaRN factor 4，原始长度 32,768 | 已观察到最长原生输入 69,721 token；扩展用于保留长证据。这是模型特定的实验适配 |
| 09-11 生成引擎 | 安装冒烟使用 Transformers → V5 使用 vLLM 0.8.5，正式 batch 16、prefix caching | 支持完整评测吞吐；token 计数改为实际生成 token ID。采样协议保留，但不同引擎输出可能不同 |
| 09-11 评分接口 | MedRAG 字段 `answer_choice` → 确定性提取并映射到已有 scorer 的 `answer` | 使原生评分器接收同一语义字段；解析规则详见第 14.3 节，原始响应仍保留 |

以下内容沿用既有方法：单轮检索和单次最终生成、question-only 查询、MedRAG 文档与问题模板的主体结构、RRF 编码及融合公式、StatPearls 上游 chunker。V5 使用冻结模型做推理，未引入训练、微调、候选投票、查询改写、多轮 agent 或 M2 的生成文档阶段。

##### 13.2 源码兼容、运行和资源处理

源码证据见 [reader 改动](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/src/medrag.py)、[语料与索引改动](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/src/utils.py)、[独立运行入口](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/run_baseline.py)；后续操作见 V5 [监督记录](/home/data3/txy/docs/evaluation/v5.md#record-0393)。

| 日期 / 工作 | 调整前 → 实际调整后 | 目的与证据边界 |
|---|---|---|
| 09-10 环境安装 | 既有依赖混杂、`python` 不存在、uv 启动器失败 → 系统 Python 3.10 独立 venv、固定依赖、直接 uv 二进制 | 完成可运行安装；82 个包的安装日志和版本锁保留 |
| 09-10 Java / LFS | Java 8、缺 Git LFS → 运行脚本使用现成 JDK 21，git-lfs 本地解包并按仓库初始化 | 满足现有 BM25 索引兼容性及资源工具依赖；不改变检索公式 |
| 09-10 目录与复用 | 根盘空间不足、资源分散 → 数据盘缓存和索引目录，模型与既有三库软链接 | 完整权重与正文直接复用；本机依赖路径在第 4–5 节列出 |
| 09-10 导入与模板路径 | `sys.path.append('src')`、依赖当前目录的模板路径 → 包内相对导入、按源码位置定位模板 | 让项目入口可稳定导入；未重写模板文本 |
| 09-10 检索初始化 | reader 构造即加载检索资源 → 可注入检索器、需要时再初始化 | 提供片段的 smoke 可以单独检查模型接口；正常实时查询仍调用所选检索流程 |
| 09-10 tokenizer / 输出提取 | pipeline 未显式传入对应 tokenizer，生成后按 prompt 字符数截取 → 传入 tokenizer，`add_special_tokens=False`、`return_full_text=False` | 修正重复 BOS 风险及生成结果提取路径；真实模板回归和 GPU smoke 已验证。该变化可能影响实际模型输入 |
| 09-10 结束与长度规则 | 分支中手写 EOS、总长生成和输入自动截断 → 模型 EOS、明确新增 token 预算、总长超限报错 | 让模型结束条件与输出预算明确；检索上下文仍按规定裁剪并记录裁剪量 |
| 09-10 正文读取 | 每条命中都读取并切分整个 JSONL 文件 → 有 `.u64le` 时按偏移读取目标行，无偏移时沿用旧路径 | 优化 IO；回归检查验证目标行定位。未修改 BM25、RRF 或重排排序公式 |
| 09-10 稠密资源获取 | 官方向量链接返回 403 → 按上游 encoder 本地生成 FP32 向量和 Flat 索引 | 为初始 M4 补资源；完整 Wikipedia RRF 最终未完成，状态见第 7 节 |
| 09-10 分片保存与恢复 | 直接写最终 `.npy` / FAISS 文件 → 写完临时文件再替换，保留并复用已完成分片 | 支持长构建恢复；编码、pooling 和索引距离度量沿用上游 |
| 09-10 准备任务管理 | 三个独立 worker → 保留分片后由 supervisor 管理，并设置全部成功后的检查与 smoke | 这是一次实际执行的停启调整；后续整体成功标记未产生 |
| 09-11 停止旧索引 | V5 已不依赖 RRF，旧任务仍占资源 → 停止 Contriever、SPECTER 与 supervisor，保留文件 | 释放运行资源；MedCPT 此前已完成，V5 检索链不加载这些稠密索引 |
| 09-11 PubMed 行偏移 | PubMed 缺少偏移表 → 补齐 1,166 个偏移文件 | 一组 32 条命中正文前后完全一致；单次正文读取计时改善已记录，不等同于端到端速度提升 |
| 09-11 GPU 与续跑 | M4 单路 → 按已提交完整 batch 分成两路、再三路；外部进程出现时让出 GPU 0 并续跑 | 处理资源可用性；保留生成参数、已完成样本和提示，最终覆盖与重复项检查通过 |

##### 13.3 记录、验证和交付

| 日期 / 工作 | 实际完成内容 | 留下的证据或产物 |
|---|---|---|
| 09-10 可复用入口 | 创建配置、shell 环境入口、JSONL 输入输出、资源检查、模型与语料覆盖参数；禁止覆盖已有输出 | 第 6.4 节文件表；覆盖参数写入实际结果 |
| 09-10 运行记录 | 保存原始生成、messages、片段与分数、配置、逐题耗时、token 统计，随后补充裁剪统计 | 四份 smoke 输出及运行代码；前三份早期输出不含后来新增的裁剪字段 |
| 09-10 验证 | 环境导入与依赖检查、实际 tokenizer 回归、四次 GPU smoke、必需证据入口检查 | 第 8 节；每项验证范围及其未覆盖范围都有明确说明 |
| 09-10 编号 | 配置和入口改为 M4/M5，保留旧别名；已有结果仅补编号字段，更新文档与测试引用 | 第 9 节；没有为编号变更重新生成答案 |
| 09-11 评测留存 | 原生格式 smoke 复用、按 question 缓存检索、保存实际配置、原始 prompts、预测和 token ID 计数 | V5 `M4/`、`M5/` 及其分片目录 |
| 09-11 覆盖和评分 | 合并分片、检查所有输入和提示齐备、执行原生评分和成本审计、导出表格与图 | 第 10.4 节；`validation.json=complete`、`artifact_audit.json=passed` |
| 09-12 文档追溯 | 浏览原始会话和日志，形成完整安装报告，更新 README、BASELINES、工作区指南的报告入口和旧索引状态 | 本文第 1–12 节 |
| 09-13 论文实施记录 | 复核 diff、运行快照和解析器，补充前后对照、论文方法草稿及维护记录 | 本文第 13–15 节；本次只修改文档 |

#### 14. 论文方法与实现细节写作材料

##### 14.1 正式结果对应的实验版本

本文论文草稿对应 **2026-09-11 已完成的 V5 M4/M5**，参数依据第 10.1 节保存的实际配置。算法来源引用 [MedRAG](https://aclanthology.org/2024.findings-acl.372/)，单轮检索设置来源引用 [MA-RAG 附录 D.2](https://arxiv.org/html/2603.03292v1#A4.SS2)；其本地默认参数和原生任务扩展按本报告披露。[MedRGAG 附录 A](https://arxiv.org/html/2510.18297v1#A1) 对应初始 M4 配置选择的历史来源。

BF16 指 LLM 生成权重精度。`BM25MedCPT` 对 Cross-Encoder 的加载未显式指定 BF16；历史稠密向量为 FP32。三者的精度记录分别对应不同组件。

##### 14.2 查询、证据、提示和答案约定

| 环节 | V5 代码实际执行的规则 |
|---|---|
| 模型输入字段 | `item_id/question/options/fixed_evidence/answer_format/max_tokens` 为已材料化输入字段；其中 M4/M5 使用统一 2,048 生成预算，并非直接使用逐项 `max_tokens` |
| 检索查询 | 仅使用 `item['question']`；另存于 `options`、`fixed_evidence` 的内容不追加到检索查询。相同 question 在所在运行目录中复用检索缓存 |
| 候选与重排 | 四库各 BM25 top-32，合并后以 `[question,doc.content]` 做 MedCPT 重排，输入对最大 512 token，返回 top-8 |
| Reader 上下文 | 按重排顺序组织 `Document [j] (Title: title) content`；用当前 reader tokenizer 编码并保留前 30,000 token，再解码为文本 |
| 必需证据 | 将完整 `fixed_evidence` 依序附到 reader 问题中；与可裁剪的追加检索上下文分开处理 |
| 提示结构 | MedRAG system message + 文档、问题、选项组成的 user message；选项按 key 排序展示；再使用相应模型 chat template |
| 原生格式扩展 | 对非原始单选格式以及特殊选项 key，修改答案类型要求；robustness 另要求错误文档 ID 与纠正文本 |
| 生成 | 每个输入返回一个最终样本；温度 0.7、top-p 1、seed 42、最大新增 2,048 token；Qwen 非 thinking；不添加多候选选择阶段 |
| 长度校验 | 完整 chat prompt 的 token 数 + 2,048 必须不超过 131,072；超限报错，检索上下文裁剪量独立保存 |

Gold、分类理由和评分映射保存在评测侧，不进入上述 reader 消息。具体字段映射与输入准备由 V5 评测包负责；其冻结数据规模及分类规则引用 V5 原有文档。

| `answer_format` | `answer_choice` 的提示约定 |
|---|---|
| `single` | 一个原生选项 key 字符串 |
| `multi` | 一个包含一个或多个原生选项 key 的 JSON 数组 |
| `diagnosis` | 一个简洁的最可能诊断标签 |
| `relation` | `higher`、`lower`、`no difference`、`uncertainty` 中的一个 |
| `robustness_single` | 一个原生选项 key；另提供 `errors` 数组，各项含 `document_id` 和 `correction` |

这部分由同一个 `messages()` 函数对 M4/M5 应用。模型 tokenizer 与 chat template 各自保留，故共享的是输入组织和任务约定。

##### 14.3 输出解析与评分：需要准确记录的细节

V5 [analyze_v5.py::objects](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/analyze_v5.py) 在原始响应中扫描可解析的 JSON 对象，选取包含 `answer_choice` 的对象。若多个对象中的答案字段值一致，使用第一个对象；若不存在此类对象或答案字段相互冲突，则不产生有效映射。代码围栏、解释文字、`Dict` 外层前缀本身不会使其中可解析的对象失效。

提取成功后，将字段值映射为 `{"answer": value}`，交给既有 [原生 scorer](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/analyze_cf_baseline_screening.py)。该过程是固定解析及字段转换；没有调用模型修复答案或根据 gold 选择相互冲突的输出。

- 单选要求合法原生选项 key；多选要求非空、合法、无重复的 key 数组，主正确性按完整集合匹配。
- 关系标签按已有归一化规则匹配四种合法值；诊断按冻结 canonical labels 做归一化精确匹配。
- 无法映射、非法类型或不合法答案按原有 scorer 判为无效并计错；原始响应保留供追溯。
- Robustness 主问沿用单选评分，`errors` 的文档 ID 集合另做识别评分；`correction` 文本保存，但 `correction_semantic_score` 为 `None`。

主表先对同一比较单元、同一类别中的非 reference 原生评分记录求均值，再对该类别的单元等权平均；ALL 对单元去重。参考端另用于配对与不变性指标。因此第 10.4 节的 29.76% / 47.35% 是 V5 单元平均原生任务正确率。

##### 14.4 可用于方法章节的文字草稿

**中文方法描述：**

我们基于 MedRAG 实现两个单轮医学检索增强生成基线，分别以 Llama-3.1-8B-Instruct 和 Qwen3-8B 作为回答模型，记为 M4 和 M5。两者采用统一的检索协议：以问题文本为查询，分别从 PubMed、Textbooks、StatPearls 和 Wikipedia 的 BM25 索引召回 32 个片段，使用 MedCPT Cross-Encoder 对合并候选进行重排，并将前 8 个片段提供给回答模型。BM25 参数为 k1=0.9、b=0.4，Cross-Encoder 的问题—正文输入对最大长度为 512 token。我们沿用 MedRAG 提示结构，并为 benchmark 的原生答案类型添加共享格式约定。题目给定的必需证据完整保留，追加检索上下文按相应模型的 tokenizer 限制为 30,000 token。正式评测通过 vLLM 0.8.5 使用 BF16 生成，温度为 0.7，top-p 为 1，随机种子为 42，最大新增输出为 2,048 token，每输入产生一个最终回答。M5 使用 Qwen 非 thinking 模式，并采用 factor 4 的 YaRN 将总上下文从 32,768 扩展至 131,072 token；M4 使用原生 131,072 上下文。可解析答案通过固定字段映射进入统一原生评分器，无效答案计错。

**English implementation draft:**

We implemented two single-round medical RAG baselines using MedRAG, with Llama-3.1-8B-Instruct (M4) and Qwen3-8B (M5) as readers. Both used question-only BM25 retrieval from PubMed, Textbooks, StatPearls, and Wikipedia, retrieving 32 snippets per corpus with k1=0.9 and b=0.4. We reranked the pooled candidates with the MedCPT Cross-Encoder using question–content pairs of at most 512 tokens and supplied the top eight snippets to the reader. We retained the MedRAG prompt structure and added shared output contracts for the benchmark's native tasks. Mandatory evidence was preserved in full, while additional retrieved context was limited to 30,000 tokens under each reader's tokenizer. Generation used vLLM 0.8.5, BF16 reader weights, temperature 0.7, top-p 1, seed 42, and a maximum of 2,048 new tokens, producing one response per input. M5 used non-thinking mode and YaRN scaling with factor 4 to extend its context from 32,768 to 131,072 tokens; M4 used its native 131,072-token context. Answers were extracted by a fixed JSON-field parser and evaluated with the native scorers; invalid answers were counted as incorrect.

**语料与结果口径补充句：**

StatPearls 使用 2026-09-10 下载并通过上游 chunker 处理的副本，共 372,148 条片段；其余三库复用本地已有 MedRAG 语料。M4/M5 分别完成 13,905 个独立输入，结果按 6,104 个比较单元等权汇总。上述设置对应本地 V5 适配后的基线评测；具体复现边界与组件差异见第 11 节。

##### 14.5 写论文时的信息来源索引

| 论文部分 | 本文与实际证据 |
|---|---|
| Baseline 定义与算法来源 | 第 3、10.1、14.1 节；MedRAG / MA-RAG 论文与实际运行配置 |
| Implementation details / 超参数 | 第 4、10.1、13.1、14.2 节；依赖锁、`src/baselines.py`、V5 runner |
| 与原始方法的实现差异 | 第 13 节；源码 diff、`m4_configuration_change.json`、保存的运行配置 |
| 数据与语料快照 | 第 5、10 节；StatPearls 日志、V5 数据说明和材料化输入 |
| 提示与答案格式附录 | 第 14.2–14.3 节；`src/template.py`、V5 `messages()`、各方法的 `prompts.jsonl.gz` |
| 结果与评分 | 第 10.4、14.3 节；V5 `RESULTS.md`、`category_scores.csv`、`validation.json` |
| 成本与效率 | 第 8.2、10.3–10.4 节；原始计时、token 审计、PubMed 单次读取比较 |
| 局限与可复现性 | 第 11 节；原始配置歧义、快照差异、引擎与上下文适配、未完成历史索引 |

#### 15. 后续记录约定与文档更新历史

按用户要求，M4/M5安装环境、独立入口及历史RRF配置相关工作在本文追加；正式v5配置、输出修复、调度和评分更新在[评测实施记录](/home/data3/txy/docs/evaluation/v5.md#record-0084)追加，跨阶段只保留摘要链接。每项记录写明实施日期、调整前后、原因、生效配置与运行目录、实际执行命令或源码位置、验证结果，以及已完成 / 已停止 / 未执行状态。只讨论的方案与实际执行的操作分别标明。

方法设置发生变化时保留原配置及原结果的对应关系，在第 13 节追加变更，在第 10 节说明新结果所属版本；方法章节草稿随生效协议更新。运行进度采用带日期的记录，已有完成记录与产物作为历史证据保留。来自其他会话的实施记录标明来源，本文整理动作与原实验实施动作分别记载。

| 文档更新日期 | 已完成的文档工作 | 本次实验状态变化 |
|---|---|---|
| 2026-09-10 | 新增 BASELINES 安装说明、运行命令和当时的验证状态；完成 M4/M5 编号与文档同步 | 对应安装、冒烟、索引启动及编号的原始执行记录 |
| 2026-09-12 | 从历史会话、日志和产物补写本文第 1–12 节；同步 README、BASELINES、工作区指南 | 文档整理；更新历史状态表述，没有新实验 |
| 2026-09-13 | 将本文作为统一论文实施记录；补充逐项调整、原生评分细节、中英文方法草稿和维护约定；明确 BF16 沿用上游 | 文档整理；正式 V5 配置和已有结果保持原值，没有新实验 |

##### 2026-09-13 文档合并及后续归属

原 BASELINES.md 的配置、语料和冒烟摘要与本文第3–11节重复，其独立运行接口及恢复命令合入第16节。原文中的新M4运行、完成和图表更新段落已由[评测实施记录](/home/data3/txy/docs/evaluation/v5.md#record-0084)第14–16节完整维护，本文只保留衔接入口。安装环境、独立入口和历史RRF设置继续在本文更新；正式v5运行及输出修复在评测主记录更新。



#### 16. 独立安装入口与历史RRF恢复命令

合并自 BASELINES.md（2026-09-13）。这里的 `configs/m4.json` 是安装阶段RRF-4配置，不能替代正式v5的独立配置。以下命令以本安装目录为工作目录，输出须使用新文件；原检查 `--variant m4 --check` 因Wikipedia索引不齐退出1，M5资源检查可通过，这与已完成的v5是不同范围。

原v5的生效配置入口保留为 [v5 configs/m4.json](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/configs/m4.json)，运行时覆盖值见第10节的保存配置；后续结构修复版另见正式评测主记录。

```bash
./run_baseline.sh --variant m4 --check
./run_baseline.sh --variant m5 --check
.venv/bin/python test_baselines.py
```

##### 16.1 JSONL接口与运行

每行一个 JSON 对象：`id`、`question`、`options`（选项标签到文本的字典）。
入口支持 `--variant m4` / `m5`（也接受大写 `M4` / `M5`）；
此前的 `llama31` / `qwen3` 命令仍映射到同一配置，供已启动的准备任务使用。
需要复用外部检索时，可额外提供 `snippets`（含 `id/title/content` 的数组）；
此时跳过实时检索，输出明确标为 `provided_snippets`。
输入示例见 `examples/retrieval_smoke.jsonl` 与 `examples/smoke.jsonl`。

```bash
# 指定空闲 GPU；输出必须是新文件。
CUDA_VISIBLE_DEVICES=1 ./run_baseline.sh --variant m4 \
  --input examples/smoke.jsonl --output runs/my_m4_smoke.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant m5 \
  --input examples/retrieval_smoke.jsonl --output runs/my_m5_retrieval_smoke.jsonl

# 稠密索引齐备后，Llama 可同样使用不带 snippets 的输入。
CUDA_VISIBLE_DEVICES=1 ./run_baseline.sh --variant m4 \
  --input questions.jsonl --output runs/my_m4_predictions.jsonl
```

输出包含最终响应、实际检索片段和分数、完整模型消息、原始生成文本、
重编码得到的输入/输出 token 数、逐题耗时，以及实际使用的配置。
检索上下文保留上游 `context_length` 裁剪规则，并记录 `context_truncated_tokens`；
完整提示加输出预算超限时直接报错。
`--limit N` 可限定题数；`--model PATH`、`--corpus NAME` 的覆盖会写入结果。
GPU 编号由调用者选择。现有 R1–R5 benchmark 包仍使用它自己的输入接口和原生评分；
本入口服务原始多选 QA，含 `fixed_evidence` 的记录需要后续任务适配。

##### 16.2 历史索引恢复与环境重建

安装当日探测上游预计算向量的 SharePoint 链接，返回 HTTP 403。
本地构建沿用上游编码与 FAISS Flat 索引，不将近似索引或 BM25 替代项冒充 RRF-4。
构建先处理 Textbooks，再处理 Wikipedia；完成的 `.npy` 分片会被复用。
单个 Wikipedia 索引约 92 GB，三路向量加最终索引合计约 550 GB，构建耗时取决于 GPU。
每个完成的索引都有 `build.json`，记录向量数、精度、耗时和完成时间。
当前 V5 不依赖这些稠密索引。以下仅用于恢复历史 M4 的 RRF-4；有同一 encoder
任务运行时不重复启动：

```bash
# 一次恢复全部三路，完成后自动检查完整 Llama 检索链。
MEDRAG_GPU_A=1 MEDRAG_GPU_B=2 ./prepare_rrf4.sh

# 或单独恢复某一路：
export HF_HOME="$PWD/.cache/huggingface"
export TMPDIR="$PWD/.cache/tmp"
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=8 .venv/bin/python -u prepare_rrf4.py --encoder contriever
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=8 .venv/bin/python -u prepare_rrf4.py --encoder specter
CUDA_VISIBLE_DEVICES=2 OMP_NUM_THREADS=8 .venv/bin/python -u prepare_rrf4.py --encoder medcpt
```

重新创建 Python 环境可使用系统 Python 3.10 和 `requirements-baseline.lock.txt`。
本机 uv 的 Snap 启动器存在目录权限问题；可直接运行
`/snap/astral-uv/current/bin/uv venv --python /usr/bin/python3 .venv`，再运行
`UV_CACHE_DIR="$PWD/.cache/uv" TMPDIR="$PWD/.cache/tmp" /snap/astral-uv/current/bin/uv pip install --python .venv/bin/python -r requirements-baseline.lock.txt`。

<a id="record-0388"></a>

## README.md

来源：[Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/README.md](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag`。

### MedRAG Toolkit

本机 **M4：MedRAG-Llama-3.1-8B** / **M5：MedRAG-Qwen3-8B** 的安装、论文配置、验证结果和运行命令见 [BASELINES.md](/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/BASELINES.md)。

安装流程、逐项调整前后与原因、验证证据、V5 生效配置及中英文论文方法草稿，统一维护在 [M4 / M5 安装、调整与论文实施记录](/home/data3/txy/docs/baselines/medrag.md#record-0254)。后续相关工作继续追加到这份文档。

`MedRAG` a systematic toolkit for Retrieval-Augmented Generation (RAG) on medical question answering (QA). `MedRAG` is used to implement various RAG systems for the benchmark study on our [`MIRAGE`](https://github.com/Teddy-XiongGZ/MIRAGE) (Medical Information Retrieval-Augmented Generation Evaluation).

[![Paper](https://img.shields.io/badge/paper-available-brightgreen)](https://aclanthology.org/2024.findings-acl.372/)
[![Homepage](https://img.shields.io/badge/homepage-available-blue)](https://teddy-xionggz.github.io/benchmark-medical-rag/)
[![Corpus](https://img.shields.io/badge/corpus-available-yellow)](https://huggingface.co/MedRAG)

#### News
- (02/20/2025) [`RAG-Gym`](https://rag-gym.github.io/) is released! RAG-Gym is a unified framework for optimizing agentic RAG with process supervision, applicable to both general and medical QA tasks.
- (10/10/2024) Multiple updates!
- - We have changed the output format of open-source LLMs to make it similar to closed-source ones like GPT-4. Input tokens will no longer be included in the model output.
- - We updated our `transformers` version in requirements.txt to ensure [compatibility](/home/data3/txy/docs/baselines/medrag.md#record-0388) with new LLMs, such as Llama 3.1 and 3.2.
- - Information retrieval in MedRAG can be accelerated by setting `corpus_cache=True` when initializing a `MedRAG` object.
- - Information retrieval for dense retrievers can be further accelerated by setting `HNSW=True` when initializing a `MedRAG` object for the first time (i.e., the faiss index hasn't been built).
- - Pre-computed embeddings of `Contriever`/`MedCPT`/`SPECTER` on `PubMed`/`Textbooks`/`Wikipedia` will be now be automatically downloaded when initializing a `MedRAG` object for the first time. No need to embed them on your machine! (We do not provide the embeddings of `StatPearls` due to frequent updates by the article [source](https://ftp.ncbi.nlm.nih.gov/pub/litarch/3d/12/))
- - The implementation of [`i-MedRAG` ](https://arxiv.org/abs/2408.00727) (to appear in PSB 2025) has been included. You can easily run it by setting `rag=True` and `follow_up=True` when initializing a `MedRAG` object. Demo code can be found in [Usage](/home/data3/txy/docs/baselines/medrag.md#record-0388).
- (06/19/2024) Add supports for openai>=1.0.0. MedRAG now allows pre-determined snippets/snippet ids as input.
- (05/16/2024) Our [paper](https://aclanthology.org/2024.findings-acl.372/) has been accepted by ACL 2024 Findings!
- (04/26/2024) Add supports for `Google/gemini-1.0-pro` and `meta-llama/Meta-Llama-3-70B-Instruct`.
- (02/26/2024) The code has been updated. It supports all corpora and retrievers introduced in our paper now.

#### Table of Contents

- [Introduction](/home/data3/txy/docs/baselines/medrag.md#record-0388)
- - [Corpus](/home/data3/txy/docs/baselines/medrag.md#record-0388)
- - [Retriever](/home/data3/txy/docs/baselines/medrag.md#record-0388)
- - [LLM](/home/data3/txy/docs/baselines/medrag.md#record-0388)
- [Requirements](/home/data3/txy/docs/baselines/medrag.md#record-0388)
- [Usage](/home/data3/txy/docs/baselines/medrag.md#record-0388)
- [Compatibility](/home/data3/txy/docs/baselines/medrag.md#record-0388)
- [Citation](/home/data3/txy/docs/baselines/medrag.md#record-0388)

#### Introduction

The following figure shows that MedRAG consists of three major components: Corpora, Retrievers, and LLMs.

<img src="figs/MedRAG.png" alt="Alt text" width="375"/>

##### Corpus

For corpora used in MedRAG, we collect raw data from four different sources, including the commonly used [PubMed](https://pubmed.ncbi.nlm.nih.gov/) for all biomedical abstracts, [StatPearls](https://www.statpearls.com/) for clinical decision support, medical [Textbooks](https://github.com/jind11/MedQA) for domain-specific knowledge, and [Wikipedia](https://huggingface.co/datasets/wikipedia) for general knowledge. We also provide a MedCorp corpus by combining all four corpora, facilitating cross-source retrieval. Each corpus is chunked into short snippets.

| **Corpus**  | **#Doc.** | **#Snippets** | **Avg. L** | **Domain** |
|-------------|-----------|---------------|------------|------------|
| PubMed      | 23.9M     | 23.9M         | 296        | Biomed.    |
| StatPearls  | 9.3k      | 301.2k        | 119        | Clinics    |
| Textbooks   | 18        | 125.8k        | 182        | Medicine   |
| Wikipedia   | 6.5M      | 29.9M         | 162        | General    |
| MedCorp     | 30.4M     | 54.2M         | 221        | Mixed      |

(\#Doc.: numbers of raw documents; \#Snippets: numbers of snippets (chunks); Avg. L: average length of snippets.)

##### Retriever

For the retrieval algorithms, we only select some representative ones in MedRAG, including a lexical retriever ([BM25](https://github.com/castorini/pyserini)), a general-domain semantic retriever ([Contriever](https://huggingface.co/facebook/contriever)), a scientific-domain retriever ([SPECTER](https://huggingface.co/allenai/specter)), and a biomedical-domain retriever ([MedCPT](https://huggingface.co/ncbi/MedCPT-Query-Encoder)).

| **Retriever** | **Type**   | **Size** | **Metric** | **Domain**   |
|---------------|------------|----------|------------|--------------|
| BM25          | Lexical    | --       | BM25       | General      |
| Contriever    | Semantic   | 110M     | IP         | General      |
| SPECTER       | Semantic   | 110M     | L2         | Scientific   |
| MedCPT        | Semantic   | 109M     | IP         | Biomed.      |

(IP: inner product; L2: L2 norm)

##### LLM

We select several frequently used LLMs in MedRAG, including the commercial [GPT-3.5](https://platform.openai.com/) and [GPT-4](https://oai.azure.com/), the open-source [Mixtral](https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1) and [Llama2](https://huggingface.co/meta-llama/Llama-2-70b-chat-hf), and the biomedical domain-specific [MEDITRON](https://huggingface.co/epfl-llm/meditron-70b) and [PMC-LLaMA](https://huggingface.co/axiong/PMC_LLaMA_13B).
Temperatures are set to 0 for deterministic outputs.

| **LLM**      | **Size** | **Context** | **Open** | **Domain** |
|--------------|----------|-------------|----------|------------|
| GPT-4        | N/A      | 32,768      | No       | General    |
| GPT-3.5      | N/A      | 16,384      | No       | General    |
| Mixtral      | 8×7B     | 32,768      | Yes      | General    |
| Llama2       | 70B      | 4,096       | Yes      | General    |
| MEDITRON     | 70B      | 4,096       | Yes      | Biomed.    |
| PMC-LLaMA    | 13B      | 2,048       | Yes      | Biomed.    |

(Context: context length of the LLM; Open: Open-source.)

#### Requirements

- First, install PyTorch suitable for your system's CUDA version by following the [official instructions](https://pytorch.org/get-started/locally/) (2.1.1+cu121 in our case).
- - New LLMs such as Llama 3.1 and Llama 3.2 were tested with '2.4.1+cu124' on our machine.

- Then, install the remaining requirements using: `pip install -r requirements.txt`,

- For GPT-3.5/GPT-4, an OpenAI API key is needed. Replace the placeholder with your key in `src/config.py`.

- `Git-lfs` is required to download and load corpora for the first time.

- `Java` is requried for using BM25.

#### Usage

Example medical qusetion from [MMLU](https://github.com/hendrycks/test)
```python
from src.medrag import MedRAG

question = "A lesion causing compression of the facial nerve at the stylomastoid foramen will cause ipsilateral"
options = {
    "A": "paralysis of the facial muscles.",
    "B": "paralysis of the facial muscles and loss of taste.",
    "C": "paralysis of the facial muscles, loss of taste and lacrimation.",
    "D": "paralysis of the facial muscles, loss of taste, lacrimation and decreased salivation."
}
```
###### CoT
```python
cot = MedRAG(llm_name="OpenAI/gpt-3.5-turbo-16k", rag=False)
answer, _, _ = cot.answer(question=question, options=options)
print(f"Final answer in json with rationale: {answer}")
# {
#   "step_by_step_thinking": "Compression of the facial nerve at the stylomastoid foramen will affect the function of the facial nerve. The facial nerve is responsible for innervating the muscles of facial expression, including those involved in smiling, frowning, and closing the eyes. It also carries taste sensation from the anterior two-thirds of the tongue. Additionally, the facial nerve controls tear production (lacrimation) and salivation. Therefore, compression of the facial nerve at the stylomastoid foramen will cause paralysis of the facial muscles (A), loss of taste (B), lacrimation (C), and decreased salivation (D).", 
#   "answer_choice": "D"
# }
```

###### MedRAG
```python
medrag = MedRAG(llm_name="OpenAI/gpt-3.5-turbo-16k", rag=True, retriever_name="MedCPT", corpus_name="Textbooks")
answer, snippets, scores = medrag.answer(question=question, options=options, k=32) # scores are given by the retrieval system
print(f"Final answer in json with rationale: {answer}")
# {
#   "step_by_step_thinking": "A lesion causing compression of the facial nerve at the stylomastoid foramen will result in paralysis of the facial muscles. Loss of taste, lacrimation, and decreased salivation are not specifically mentioned in relation to a lesion at the stylomastoid foramen.", 
#   "answer_choice": "A"
# }

### MedRAG with pre-determined snippets
snippets = [{'id': 'InternalMed_Harrison_30037', 'title': 'InternalMed_Harrison', 'content': 'On side of lesion Horizontal and vertical nystagmus, vertigo, nausea, vomiting, oscillopsia: Vestibular nerve or nucleus Facial paralysis: Seventh nerve Paralysis of conjugate gaze to side of lesion: Center for conjugate lateral gaze Deafness, tinnitus: Auditory nerve or cochlear nucleus Ataxia: Middle cerebellar peduncle and cerebellar hemisphere Impaired sensation over face: Descending tract and nucleus fifth nerve On side opposite lesion Impaired pain and thermal sense over one-half the body (may include face): Spinothalamic tract Although atheromatous disease rarely narrows the second and third segments of the vertebral artery, this region is subject to dissection, fibromuscular dysplasia, and, rarely, encroachment by osteophytic spurs within the vertebral foramina.', 'contents': 'InternalMed_Harrison. On side of lesion Horizontal and vertical nystagmus, vertigo, nausea, vomiting, oscillopsia: Vestibular nerve or nucleus Facial paralysis: Seventh nerve Paralysis of conjugate gaze to side of lesion: Center for conjugate lateral gaze Deafness, tinnitus: Auditory nerve or cochlear nucleus Ataxia: Middle cerebellar peduncle and cerebellar hemisphere Impaired sensation over face: Descending tract and nucleus fifth nerve On side opposite lesion Impaired pain and thermal sense over one-half the body (may include face): Spinothalamic tract Although atheromatous disease rarely narrows the second and third segments of the vertebral artery, this region is subject to dissection, fibromuscular dysplasia, and, rarely, encroachment by osteophytic spurs within the vertebral foramina.'}]
answer, _, _ = medrag.answer(question=question, options=options, snippets=snippets)

### MedRAG with pre-determined snippet ids
snippets_ids = [{"id": s["id"]} for s in snippets]
answer, snippets, _ = medrag.answer(question=question, options=options, snippets_ids=snippets_ids)
```

###### MedRAG with the corpus cached in memory (for fast information retrieval)
```python
medrag = MedRAG(llm_name="OpenAI/gpt-3.5-turbo-16k", rag=True, retriever_name="MedCPT", corpus_name="Textbooks", corpus_cache=True)
answer, snippets, scores = medrag.answer(question=question, options=options, k=32) # scores are given by the retrieval system
print(f"Final answer in json with rationale: {answer}")
# {
#   "step_by_step_thinking": "A lesion causing compression of the facial nerve at the stylomastoid foramen will result in paralysis of the facial muscles. Loss of taste, lacrimation, and decreased salivation are not specifically mentioned in relation to a lesion at the stylomastoid foramen.", 
#   "answer_choice": "A"
# }
```

###### i-MedRAG (MedRAG with follow-up queries)
```python
medrag = MedRAG(llm_name="OpenAI/gpt-3.5-turbo-16k", rag=True, follow_up=True, retriever_name="MedCPT", corpus_name="Textbooks", corpus_cache=True)
answer, history = medrag.answer(question=question, options=options, k=32, n_rounds=4, n_queries=3)
print(f"Final answer in json: {answer}") # {'answer': 'A'}
print(f"Raw answer with analysis: {history[-3]}")
# {
#   'role': 'assistant', 
#   'content': '## Analysis:\nBased on the previous information provided, a lesion causing compression of the facial nerve at the stylomastoid foramen can result in an ipsilateral loss of motor function of the whole side of the face. This can lead to an unusual appearance and complications with chewing food. Lacrimation and taste may not be affected if the lesion remains distal to the greater petrosal and chorda tympani branches that originate deep in the temporal bone. However, decreased salivation can occur if the lesion affects the parasympathetic fibers that innervate the salivary glands.\n\n## Answer:\nThe correct answer is A. paralysis of the facial muscles.'
# }
print(f"Follow-up queries generated: {[item.split('Answer: ')[0].strip() for item in history[-4]['content'].split('Query: ')[1:]]}")
# [
#   'What are the functions of the facial nerve?', 
#   'What is the anatomical location and function of the stylomastoid foramen?', 
#   'What are the possible effects of a lesion causing compression of the facial nerve at the stylomastoid foramen?', 
#   'What are the specific branches of the facial nerve that control taste sensation and lacrimation?', 
#   'How does a lesion at the stylomastoid foramen affect salivation?', 
#   'Are there any other possible effects of a lesion causing compression of the facial nerve at the stylomastoid foramen?', 
#   'What are the effects of a lesion causing compression of the facial nerve at the stylomastoid foramen on salivation?', 
#   'Can a lesion at the stylomastoid foramen affect lacrimation and taste if it remains distal to the greater petrosal and chorda tympani branches?', 
#   'Are there any other possible effects of a lesion causing compression of the facial nerve at the stylomastoid foramen?', 
#   'What is the specific effect of a lesion causing compression of the facial nerve at the stylomastoid foramen on lacrimation?', 
#   'How does a lesion at the stylomastoid foramen affect taste sensation?', 
#   'Can a lesion at the stylomastoid foramen result in decreased salivation?'
# ]
```

#### Compatibility
We've [tested](https://teddy-xionggz.github.io/MIRAGE/) the following LLMs on our MedRAG toolkit:
- OpenAI/gpt-4
- OpenAI/gpt-3.5-turbo
- Google/gemini-1.0-pro
- meta-llama/Meta-Llama-3-70B-Instruct
- meta-llama/Llama-2-70b-chat-hf
- mistralai/Mixtral-8x7B-Instruct-v0.1
- epfl-llm/meditron-70b
- axiong/PMC_LLaMA_13B

Other LLMs that can run but are not comprehensively evaluated by MedRAG:
- OpenAI/gpt-4o
- OpenAI/gpt-4o-mini
- meta-llama/Meta-Llama-3-8B-Instruct
- meta-llama/Meta-Llama-3.1-8B-Instruct
- meta-llama/Meta-Llama-3.1-70B-Instruct
- meta-llama/Llama-3.2-1B-Instruct
- meta-llama/Llama-3.2-3B-Instruct

#### Citation
For the use of `MedRAG`, please consider citing
```bibtex
@inproceedings{xiong-etal-2024-benchmarking,
    title = "Benchmarking Retrieval-Augmented Generation for Medicine",
    author = "Xiong, Guangzhi  and
      Jin, Qiao  and
      Lu, Zhiyong  and
      Zhang, Aidong",
    editor = "Ku, Lun-Wei  and
      Martins, Andre  and
      Srikumar, Vivek",
    booktitle = "Findings of the Association for Computational Linguistics ACL 2024",
    month = aug,
    year = "2024",
    address = "Bangkok, Thailand and virtual meeting",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.findings-acl.372",
    pages = "6233--6251",
    abstract = "While large language models (LLMs) have achieved state-of-the-art performance on a wide range of medical question answering (QA) tasks, they still face challenges with hallucinations and outdated knowledge. Retrieval-augmented generation (RAG) is a promising solution and has been widely adopted. However, a RAG system can involve multiple flexible components, and there is a lack of best practices regarding the optimal RAG setting for various medical purposes. To systematically evaluate such systems, we propose the Medical Information Retrieval-Augmented Generation Evaluation (MIRAGE), a first-of-its-kind benchmark including 7,663 questions from five medical QA datasets. Using MIRAGE, we conducted large-scale experiments with over 1.8 trillion prompt tokens on 41 combinations of different corpora, retrievers, and backbone LLMs through the MedRAG toolkit introduced in this work. Overall, MedRAG improves the accuracy of six different LLMs by up to 18{\%} over chain-of-thought prompting, elevating the performance of GPT-3.5 and Mixtral to GPT-4-level. Our results show that the combination of various medical corpora and retrievers achieves the best performance. In addition, we discovered a log-linear scaling property and the {``}lost-in-the-middle{''} effects in medical RAG. We believe our comprehensive evaluations can serve as practical guidelines for implementing RAG systems for medicine.",
}
```

For the use of `i-MedRAG`, please consider citing
```bibtex
@inproceedings{xiong2024improving,
  title={Improving retrieval-augmented generation in medicine with iterative follow-up questions},
  author={Xiong, Guangzhi and Jin, Qiao and Wang, Xiao and Zhang, Minjia and Lu, Zhiyong and Zhang, Aidong},
  booktitle={Biocomputing 2025: Proceedings of the Pacific Symposium},
  pages={199--214},
  year={2024},
  organization={World Scientific}
}
```

<a id="record-0394"></a>

## README.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/README.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured`。

### 新 M4：v5 全量结构约束修复重测

[最新M0/M2/M3/新M4/M5 v5完整对照](/home/data3/txy/docs/evaluation/v5.md#record-0410)（2026-09-13）。

**已完成：2026-09-13 15:04:49，13,905/13,905全部新生成并完成原生评分。格式有效99.09%、原生有效79.42%、整体单元平均准确率48.20%。GPU1/2/3已释放；M6/M7保持暂停。详见[最终结果](/home/data3/txy/docs/baselines/medrag.md#record-0395)。**

2026-09-13 13:52启动，用户明确授权保存M7后改用GPU1/2/3全力运行新M4，并额外监督有效率。M7已暂停，M6保持暂停。GPU0不使用。

#### 范围与修复

13,905个唯一输入全部新生成，不复用旧M4或100条试跑预测。沿用冻结v5的6,104单元、13,000入选判断和15,616原生评分映射，使用evaluation_labels。已按seed20260913打散为109个不重叠分片，每片128条，末片81条。

修复源：2026-09-11工作区 `results_v5_m0_m2_m4_m5/code/m4_format_pilot.py` 的明确输出契约，以及 `m4_output_schema.py` 的逐题可见输入JSON Schema。源代码已复制到本包code/。原M4每题完整archived messages和检索证据复用，并在原system/user末尾追加同一输出契约。所有13,905输入的retrieval_question与冻结question相等，required evidence完整保留；未重新检索或更换证据。修改后的消息、schema、原生可见item及上下文截断元数据保存在inputs/。

Llama-3.1-8B-Instruct、BF16、temperature0.7、top_p1、top_k=-1、seed42、输出2048 tokens、总上下文131072。约束解码使用已安装vLLM0.8.5/xgrammar。约束会改变允许采样的token，是明确记录的方法实现修复，不宣称与原输出等价。没有添加CF/WM/adapter模块，没有修改M5。

#### 三卡执行

每卡一个常驻vLLM实例，gpu_memory_utilization=.90，max_num_seqs=128，max_num_batched_tokens=16384，prefix cache和chunked prefill启用。与M7静态HF批处理不同，本运行使用vLLM调度。初次模型加载后每卡约84.2GiB整卡显存占用。GPU1/2/3共用带文件锁的分片队列，完成后自动领取下一片，不重复生成。每个分片预测原子保存；分片切换不重新加载模型。

`config.json`保存所有参数；`plan.json`保存范围、队列和100条方案选择样本ID。原始M4正式目录及M7结果保持独立。耗时等待首批正式分片测量，不用M7或试跑耗时推断完成承诺。

#### 有效率监督与最终评分

每五分钟记录logs/status.json、logs/supervision.jsonl，并在对话中报告当前完成/新增/剩余、GPU0–3显存和利用率、格式有效率及原生有效率。监控按完成的唯一输入去重，所有无效和截断输出保留分母；额外记录严格JSON/Schema有效率、截断数、原因与题型分布。

格式有效与原生有效沿用既定评分器；原生有效还要求诊断进入冻结canonical映射，不等于回答正确。Schema约束结构，不能保证语义正确或避免2048token截断。100条原试跑用于方案选择，包含在全库中；`outside_selection_pilot_inputs`另列其余输入的有效率，不把该口径称为完全独立来源病例确认集。

队列不重复领取/恢复检查，以及监控对已有100条修复结果的核对通过：98格式有效、84原生有效、99Schema有效、1截断。原v5有3个共享输入对应不同gold映射，监控只去重统计与gold无关的有效性；最终评分保留所有15,616映射，不去掉冲突或修改标签。

全部分片完成后，finish.py验证13,905输入零缺失/重复，合并到M4/predictions.jsonl，调用复制的原analyze_v5.py做全部R1–R5原生评分、来源、任务和R5配对分析。最终写scores/、validity.json、complete.json和RESULTS.md。未出现complete.json表示未完成。

#### 操作

```bash
cd /home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured
/home/data3/txy/MedRGAG/.venv/bin/python code/status.py
tmux -L v5-m4-structured list-sessions
```

tmux会话gpu1/gpu2/gpu3/monitor；启动命令`bash launch_gpu.sh 1`（或2/3）仅用于该卡进程退出后的恢复，勿重复启动健康进程。运行错误会保留job.error并停止该卡，先检查日志。恢复error前需记录并修正原因，将对应job置回queued；已完整保存的预测不重做。

#### M7 保存点

M7在13:45暂停于1,646/13,905条（1,634正式新结果＋12复用），1,026有效、620无效、0运行失败，11个完整分片。独立汇总保存于`../results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/`；逐题terminal文件与汇总数量一致。原runs/阶段请求、事件和未完成输入缓存保留，`m7_pause.json`记录原队列状态及所属进程。M6保持52条暂停。两者均不自动恢复。

<a id="record-0395"></a>

## RESULTS.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/RESULTS.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured`。

### 新 M4 v5 全量结果

[最新M0/M2/M3/新M4/M5 v5完整对照](/home/data3/txy/docs/evaluation/v5.md#record-0410)（2026-09-13）。

2026-09-13 15:04:49 完成全部生成与原生评分。13,905个唯一输入全部新生成，109/109分片完成；15,616条评分映射、6,104单元、13,000入选判断覆盖完整，缺失/重复/运行失败均为0。三卡生成墙钟时间（含模型加载）71.86分钟。

| 指标（唯一输入口径） | 原 M4 | 修复 M4 |
|---|---:|---:|
| 格式有效率 | 61.41% | 99.09% |
| 原生评分有效率 | 43.92% | 79.42% |

修复M4严格JSON/Schema有效率为99.46%（13,830/13,905）。格式有效13,779条，原生有效11,044条。监控有效数与完整评分器去重后逐项一致。

| 类别 | 单元数 | 原 M4 单元平均准确率 | 修复 M4 | 提升（百分点） |
|---|---:|---:|---:|---:|
| R1 | 2866 | 21.53% | 27.84% | +6.32 |
| R2 | 79 | 6.33% | 29.11% | +22.78 |
| R3 | 733 | 14.32% | 30.42% | +16.10 |
| R4 | 13 | 23.08% | 53.85% | +30.77 |
| R5 | 3600 | 39.63% | 65.28% | +25.65 |
| ALL | 6104 | 29.76% | 48.20% | +18.44 |

ALL按6,104唯一单元计算，不把重叠R1–R5类别相加；R5保留全部原生任务与配对统计。

#### 有效率与失败监督

| 输入题型 | 数量 | 格式有效率 | 原生有效率 |
|---|---:|---:|---:|
| single | 6489 | 99.89% | 99.89% |
| diagnosis | 3560 | 98.15% | 21.32% |
| multi | 167 | 97.60% | 97.60% |
| relation | 989 | 99.09% | 99.09% |
| robustness_single | 2700 | 98.52% | 98.52% |

原生无效共2,861条：诊断未映射2,735、诊断歧义50、原生解析malformed_json 76。严格JSON无效75条、长度截断73条；原生解析与严格JSON检查是不同口径。全部无效保留分母，没有按结果挑选重跑。

100条既有方案选择输入之外的13,805条：格式有效率99.11%，原生有效率79.39%，Schema有效率99.47%。该100条也全部重新生成，没有复用预测。

#### 设置与限制

修复为已试验的明确输出契约＋逐输入JSON Schema/xgrammar；Llama3.1-8B-Instruct、BF16、temperature0.7、top_p1、seed42、2048输出预算、131072上下文及原完整检索证据固定。每卡一个常驻vLLM，128并行序列，.90显存配置；稳定运行各约87.2GiB。GPU1/2/3完成后自动释放，GPU0未操作。没有新增CF/WM/adapter模块。

约束解码改变允许采样的token，属于方法实现修复，不声称与原输出等价；M5未同步改变，修复后的M4/M5不能再表述为仅骨干不同的对照。相同v5用于发现问题和选择修复方案，因此不能将本次全库结果称为独立泛化确认。有效率不是正确率；诊断未映射不能直接认定为医学错误或按正确补分。

#### 结果与暂停点

- [完整原生评分校验](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/scores/validation.json)、[分类评分](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/scores/category_scores.csv)、[有效率](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/validity.json)、[新旧M4对比](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/comparison_original_m4.json)。
- 来源与任务分数、R5配对分析见scores/；逐题预测见M4/predictions.jsonl，修改后的输入见inputs/，五分钟记录见logs/supervision.jsonl。
- M7保持暂停于1,646条（1,634新＋12复用）；[保存点](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/summary.json)及原阶段缓存保留。M6保持52条暂停，两者不自动恢复。
