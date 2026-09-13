# M6 i-MedRAG / M7 TC-RAG 接入验收

按用户2026-09-13命名：**M6 = i-MedRAG（`imedrag`），M7 = TC-RAG（`tcrag`）**。下列结果沿用已有运行制品，仅补充比较编号。

当前状态：两方法实现、19项自动测试、各24条真实开发运行、熵后端对照、终态恢复和离线审计已完成。i-MedRAG为19有效/5无效，TC-RAG为9有效/15无效；输出格式及开放诊断评分兼容仍有未解决项，不能称全部验收通过。正式全量评测未启动。新增方法只有`imedrag`、`tcrag`；M20/MedCounterFact、M22/MedRGB、M23/BioRAB是现有数据集编号。

## 实现与冻结条件

i-MedRAG保留4轮追问、每轮请求3个查询、逐查询真实检索及作答、按原序写入QA历史、最终分析与官方格式化调用。TC保留真实工具、活动栈、回退、Summary替换、全分布熵、最早第5步接受及8步上限。入口已注册在现有项目。

| 条件 | M6 i-MedRAG | M7 TC-RAG |
|---|---|---|
| Backbone | meta-llama/Llama-3.1-8B-Instruct | Qwen/Qwen3-8B，thinking关闭 |
| 执行配置 | [imedrag_runtime_v4.json](<configs/imedrag_runtime_v4.json>) | [tcrag_runtime_v4.json](<configs/tcrag_runtime_v4.json>) |
| 方法默认 | 4轮，每轮请求3查询 | max_loop=8，topK=4，sigma=1.2 |
| 生成 | BF16，temperature=.7，top_p=1，top_k=0，seed42 | 同左；YaRN4/original32768 |
| 上下文/合批 | 窗口131072，合批32000 padded tokens，4工作线程 | 同左 |
| 阶段生成上限 | query/parse/QA=1024；final/format=2048 | action=2048 |
| 检索 | 完整MedCorp四库，BM25每库32，MedCPT重排top8，追加上下文30000 tokens | 同左 |

仅使用GPU1/2空余显存，既有任务继续运行。模型/分词器/索引身份见[resources.json](<configs/resources.json>)，依赖见[environment.json](<configs/environment.json>)、[requirements.lock.txt](<configs/requirements.lock.txt>)。逐组件固定论文、官方SHA、许可证、补丁及差异见[method_fidelity.md](<method_fidelity.md>)。名称为统一框架适配，不是两论文原表格分数复现。

## 自动测试与数据审计

19项自动测试全部通过（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/tests_final_syntax.log`）：跨轮QA依赖及并发顺序；安全查询解析；TC工具/回退/总结/接受边界/耗尽；FP32熵数值和位置；样本隔离、gold哨兵、证据差异及缓存；中断收据恢复、终态恢复与配置漂移拒绝；原生格式和失败分母；复用成本不重复计费。synthetic响应仅存在于tests。

冻结现有v5：6104单元、13000入选判断、13905唯一输入、15616原生评分记录、34753行target→input展开映射。[input_lock.json](<data/input_lock.json>)、input_manifest.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_manifest.jsonl`）、source_target_input_mapping.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/source_target_input_mapping.jsonl`）保留原记录及输入哈希。没有重新抽样或改变evaluation_labels。现有契约审计[通过](<reports/v5_existing_contract_audit.json>)，模型/索引及必需输入长度检查[通过](<reports/environment_check.json>)。

开发包为MedQA validation前12条、MedEinst training排除正式病例/完整输入后的前12条。来源记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_provenance.jsonl`）、[病例重叠审计](<data/dev_overlap_audit.json>)、[题干重叠审计](<reports/dev_question_overlap.json>)可重放：24条与13905正式输入规范化题干精确重叠为0，不声称排除了所有语义近重复。没有正式题模型暴露或阈值校准。

两个真实后端均通过同模型、同token序列的`output_scores`对照：熵最大绝对误差0；收集熵与不收集熵时生成token相同，阈值判断相同。证据：[Llama](<runs/imedrag_dev_v4/backend_reference.json>)、[Qwen](<runs/tcrag_dev/backend_reference.json>)。每次对照另计2个真实请求，无额外重放打分前向；不声称跨硬件/引擎逐bit一致。

## M6 i-MedRAG真实运行

最终目录：[runs/imedrag_dev_accepted](<runs/imedrag_dev_accepted>)。24/24终态，19有效、5无效、0失败、0待运行、0未知ID、0重复；有效率79.17%。96个追问轮次，实际279个查询及279个RAG答案，单题查询6–15个，未编造凑数。521个逻辑LLM请求，1093381输入token、169363生成token、279次检索；输出截断、无命中、传输重试和预算耗尽均为0。

MedQA开发12条中11有效、1无效；MedEinst训练12条中8有效、4无效。5条无效中，3条最终格式无法无歧义读取，3条涉及追问提取失败，交集1条。没有其他方法补答。见[执行审计](<runs/imedrag_dev_accepted/execution_report.json>)、逐题终态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/predictions.jsonl`）。审计核对521次实际模型身份、96轮前后历史、279次真实检索/QA、24次最终QA上下文。

官方格式化提示的单引号示例导致严格JSON接口失败；最终仅增加确定性字典字面量→JSON转换，19条发生转换，全部原值保留。最终目录重放800份真实收据（521模型＋279检索），新模型和检索调用均为0。链式[缓存来源](<runs/imedrag_dev_accepted/cache_provenance.json>)连接原始完整运行及统一接口复验，所有24条执行相同规则，未按正确性筛选。较早pilot及中间无效预测、成本、源码快照全部保留。

现有评分器以完整12条来源分母计算：MedQA为11/12；MedEinst既定canonical评分为0/12。后者8条运行有效答案仍有6条嵌套结构字符串被旧解析器拒绝、1条未映射诊断、1条歧义诊断。不能据此声称医学语义准确率为0或开放诊断评分兼容性已通过。未基于gold新增同义词或改写答案。[离线评分](<runs/imedrag_dev_accepted/scores/summary.json>)分别记录运行有效率和评分有效率。

原始完整i运行耗时11914秒（3.31小时），共享GPU吞吐7.25输入/小时；单题延迟p50=1875秒、p95=2401秒，合批行数中位4、最大10。最终语法重放1.60秒仅是缓存时间。后续接口复验新增60＋24次模型调用及24次检索另列；失败pilot成本也保留，不混作最终逻辑请求数。

## M7 TC-RAG真实运行

运行目录[runs/tcrag_dev](<runs/tcrag_dev>)。24/24终态：9有效、15无效、0失败、0待运行、0未知ID、0重复；有效率37.50%。12条动作解析失败（9条缺动作标签、3条空Thought），3条达到8步上限。实际动作数平均6步、中位6步、范围3–8步；40次真实检索、3次自然Summary替换、0次自然Backtrack。Backtrack完整行为已由固定响应测试验证，未强制模型额外触发动作。

44次Final Answer提议中，17次因步数过早拒绝，18次因熵阈值拒绝，9次接受。全部97次状态计算的熵和中位数22.38、p95=60.04、范围0.0121–109.88；逐次值、选定token位置、栈前后和阈值均可重算。sigma固定1.2，没有校准。审计通过144次实际prompt/活动栈检查、97次熵重算、44次接受边界、3次Summary移除及状态恢复、3次耗尽不提升为答案检查。见[执行审计](<runs/tcrag_dev/execution_report.json>)、逐题终态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/predictions.jsonl`）。

MedQA 12条中3有效、6条动作解析失败、3条耗尽；MedEinst 12条中6有效、6条动作解析失败。按完整来源分母的旧评分器：MedQA为2/12，MedEinst canonical为0/12；后者6条运行有效答案全部未进入既定canonical映射，不等同于语义答错。完整[离线结果](<runs/tcrag_dev/scores/summary.json>)保留这些区别，未修改gold、映射、阈值或提示来提高分数。

实际144次模型请求、354715输入token、18918生成token；40次检索中34次访问后端、6次同查询缓存命中。输出截断、无命中和传输重试为0；预算耗尽率12.5%。全程2792秒（46.53分钟），吞吐30.95输入/小时，单题延迟p50=476秒、p95=787秒；合批行数中位3、最大4。这里的吞吐包含失败解析及早停输入，不是保证得到有效答案的吞吐，也不用于宣称TC-RAG一定更快。熵参考对照的2个请求另计。

## 正式规模和成本

每方法13905唯一输入。标准i-MedRAG恰好12个QA/题且无重试时为305910个LLM请求、166860次检索；实际查询数可能不同。TC至多111240个动作请求，最早全部第5步接受为69525个；重试另计。

[成本估算](<reports/formal_cost_estimate.json>)按实测请求和输入长度分层，并使用原始完整运行的wall/engine比例，没有再次除以并发数。当前i开发样本全部落在必需输入≤1024 tokens层；该层正式10508条按共享GPU条件投影约1398小时。1024–8192层3040条、>8192层357条没有实测开发样本，完整正式时长保持未估出，不能将已覆盖层当作整套预算。TC的≤1024 tokens层正式10466条、开发24条，投影约338小时；其1024–8192层3072条及>8192层367条未实测。两方法完整正式预算均保持未估出。此投影只代表当时共享GPU、两类短开发输入的执行尝试，不能外推空闲GPU或全部来源的有效完成成本。

## 命令与限制

[README](<README.md>)给出本机验证的环境检查、准备、测试、开发运行、原样恢复和离线评分命令。两方法完成后原命令恢复均已验证，无新增推理；`bash acceptance.sh`已实际执行，日志见acceptance_final_commands.log（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/acceptance_final_commands.log`），[完成标记](<reports/acceptance_execution_complete.json>)同时记录formal/blind/calibration均未启动。评分源码、来源路径及哈希已留存于[scoring_snapshot/sources.json](<reports/scoring_snapshot/sources.json>)。成本脚本已再次实际运行，包含v1/v2/v3全部旧pilot及格式修复来源链；无输出的中断请求只能记录已知时间/尝试，其未知token不作猜测。正式全量命令已接入，但**尚未执行全量GPU验证**；本轮未启动正式评测。

尚未完成：开发包暴露的输出格式和开放诊断评分兼容问题；全部正式来源结构、长输入及证据干预的真实模型覆盖；未观测长度层的可靠完整成本预算。其他格式和核心回退/总结动作已有固定响应测试，不能代替全部来源真实验收。M22继承v5固定受扰动材料＋外部检索，并非MedRGB原生静态证据协议。开放诊断存在上述评分兼容限制。两个backbone、旧64-token预测及生成引擎的可比性限制见[输入与评分协议](<evidence_protocol.md>)。
