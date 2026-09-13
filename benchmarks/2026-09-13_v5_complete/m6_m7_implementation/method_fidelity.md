# M6 i-MedRAG / M7 TC-RAG 方法忠实性记录

用户2026-09-13指定比较编号：**M6 = i-MedRAG（`imedrag`），M7 = TC-RAG（`tcrag`）**。执行标识及已冻结制品不变；编号是本项目命名，不是原论文命名。

名称：**统一实验框架下的适配实现**。本包延续服务器的 dated-run-pack 结构，复用现有 MedRAG 检索实现、v5 物化输入和原生评分器。不是原论文表格分数复现。2026-09-12 核对；本文件在真实验收前建立，运行证据另见 acceptance_report.md。

## 固定来源

| 方法 | 原论文 | 官方代码 checkout | 许可证 |
|---|---|---|---|
| i-MedRAG | [2408.00727v3，2024-10-11](https://arxiv.org/html/2408.00727v3)，§3.2–3.3、Algorithm 1 | [gzxiong/MedRAG@7599a728a28789fd601728c08d313b1148051f41](https://github.com/gzxiong/MedRAG/tree/7599a728a28789fd601728c08d313b1148051f41) | LICENSE 为 NCBI US Government Work 公有领域声明，不是 MIT；GitHub API 标记 NOASSERTION |
| TC-RAG | [2408.09199v3，2026-09-03](https://arxiv.org/html/2408.09199v3)，§5、Appendix 8.6 Algorithm 1 | [Artessay/TC-RAG@dd8f32f90832eeb452680cfdb02ca604988648d0](https://github.com/Artessay/TC-RAG/tree/dd8f32f90832eeb452680cfdb02ca604988648d0) | checkout 未发现 LICENSE；API license=null。参考源码独立实现，不替上游声明许可证 |

原始 URL 与 GitHub API resolved URL 在 reports/source_resolution.json。论文里 i-MedRAG 链接作者的新用户名 Teddy-XiongGZ；本次 API 返回 gzxiong/MedRAG。两个 checkout 位于 upstream/，不包含模型权重。

## 逐组件对应

| 组件 | 论文/上游函数 | 本地函数与保留行为 |
|---|---|---|
| i-MedRAG 追问 | §3.3；src/medrag.py::i_medrag_answer，src/template.py | code/methods.py::imedrag；原题及已有 QA → 分析和追问；轮间串行 |
| 独立检索和追问作答 | Algorithm 1 行 8–11；medrag_answer | imedrag；每个真实追问单独 retrieval → RAG answer；同轮并发，按查询序号写回 |
| 追问解析 | i_medrag_answer 内 LLM 提取调用 | parse_queries；保留同 backbone 的提取调用并记成本；JSONDecoder 替代正则+eval，禁止改写/新增查询 |
| 历史和最终答案 | Algorithm 1 行 14；i_medrag_answer | imedrag；最终使用原题+完整 QA 历史，额外保留同模型格式化调用 |
| TC 工具和栈 | §5.1，TCRAG.py::whitebox_pop_react_executor | tcrag；Thought、Plan、真实 Tool_Observation 入栈；模型生成的 Observation 不执行、不进入活动上下文 |
| 回退和状态 | §5.2，pop_message/backtrack_now_state | tcrag；栈顶 pop，恢复该条入栈前状态；工具及实际 Observation 作为一条复合栈项 |
| Summary | §5.1、Algorithm 1 行 29–31 | tcrag；栈顶替换为模型总结；移除内容仅在审计轨迹保留 |
| cuct | Generator.py::generate_all::compute_entropy；system_score.py::calculate_cuct_from_entropy | code/backend.py::entropy_from_scores；code/methods.py::state_signal；生成时计算全词表逐 token 熵并求和 |
| 结论/终止 | whitebox_pop_react_executor | tcrag；零基 actions_taken >= topK 且 state < sigma 接受；否则转 Thought；max_loop 终止，返回真实栈顶同时保留 budget_exhausted |

## 默认值及差异（不可混作论文原参数）

- i-MedRAG **4 轮、请求 3 个追问/轮**：官方函数和 README 默认。上游不保证实际正好 3 个；本地保存请求数、实际数、解析和执行情况，不合成补齐。
- i-MedRAG 保留上游的 LLM 提取步骤。安全解析允许 JSON 空白和代码块；非 ASCII 定界引号等语法错误最多一次纯格式修复，原始输出和修复都入日志。提取后的查询必须能在模型原查询段定位：仅规范化无意义水平空白、换行、Markdown 加粗和查询编号/标题，词句与顺序保持一致；拒绝改写、拆分及合并。相同响应回放覆盖这些语法等价情况。失败轮次记录后继续，历史只加入成功 QA。
- 最终格式化保留上游 `Output the answer in JSON: {'answer': your_answer (A/B/C/D)}` 提示，仅按原生选项和答案类型替换括号说明。实测模型跟随示例生成单引号字典，现有评分器要求严格JSON；`final_json` 用标准库 `ast.literal_eval` 读取完整字典字面量并序列化为JSON，最多一次，拒绝冲突/重复字段或非字面量。此操作不使用 `eval`，不改变答案大小写或内容，不增加LLM调用。原始响应及转换事件保留；TC仅在结论已通过熵检查后使用同一语法转换，预算耗尽不转换成合法结论。
- 上游在 4 轮外允许额外 3 次自由循环，甚至继续追问。本包固定 4 个追问轮次，接一次最终分析和一次格式化；这是明确的终止适配，不声称调用数完全等同任意上游轨迹。满额正常为 **22 次 LLM 请求 + 12 次检索**，语法修复和传输重试另计。
- TC **max_loop=8、topK=4、sigma=1.2、初值100000**：固定官方执行器。最早第 5 次生成接受，sigma 比较严格小于。论文 v3 Appendix 8.7.6 另写 uct=20 / cppl=10、temperature=.6、500 tokens；本包不默默把这些与代码默认混用，不按正式测试分数调阈值。
- 过早Final Answer若带有Thought前缀，会按上游保留该前缀后转为Thought；达到topK后沿用上游的Final Answer片段处理。固定响应测试核对下一轮实际看到的内容及阈值边界。
- TC 官方代码没有独立 Summary 分支；其 Backtrack 文字要求总结，但实现会 pop 后追加反馈，不等价于 Summary 替换。Plan 和 Summary 均来自论文§5.1/Algorithm 1，本地补齐明确动作分支。Backtrack按论文恢复 popped Thought 的前一状态，并修复上游跨题 state_value_list 未清空问题；反馈只入审计，不重新塞回栈导致反复弹反馈。
- 论文Algorithm 1会把低于sigma的Thought状态钳制到sigma，配合while条件避免过早结束；官方执行器没有该钳制，只在Final Answer分支检查阈值。本地沿用后者，保存真实未钳制熵，普通Thought不会结束循环。Summary替换Thought时恢复下面栈项的状态快照，是本项目保持活动记忆/状态一致的记录约定；论文Summary伪代码没有明确写出这项状态恢复。状态数值不写入模型prompt，接受结论时重新计算当前生成的熵，因此这项快照约定不增加接受条件或模型调用。
- TC 默认 token 范围保留官方 `update_status_value` 的精确 token 字符串匹配：剔除全部特殊 ID 后，循环 `range(len(tokens)-3)`，首次 `Thought` 后偏移2，或 `Final` 后下一 token 精确为 `Answer` 时偏移3；扫描失败从0开始，边界失败取全部。**不 strip token 的前导空格**，因此某 tokenizer 的 ` Answer` 不匹配。每次保存 start、selected_positions、匹配状态、真实 token 文本；这是上游口径，不能写成完美截取 Final Answer 正文。
- 分数取 Transformers 生成处理器和采样变换之后、抽样之前的完整词表分布；自然对数，`-sum(p*log(p+1e-10))`，FP32，token 级再求和。特殊 token 分布不从词表重归一化，只排除生成位置。无 top-k logprob 近似、单 token NLL、口头自信度或更小评分模型。
- 生成时熵收集器不修改分数；与同后端 `generate(output_scores=True)` 对照测试。选 cuct 后不计算 attention、其他指标及完整词表导出；日志仅需逐 token 熵。主路径没有额外打分前向。
- 上游依赖锁为 Transformers 4.44.0 / torch2.4.0。本包4.51.3 / torch2.6.0支持Qwen3。已核对4.44.0的 [生成器](https://github.com/huggingface/transformers/blob/v4.44.0/src/transformers/generation/utils.py) 保存的是处理器和warper之后的scores；其 [Qwen2](https://github.com/huggingface/transformers/blob/v4.44.0/src/transformers/models/qwen2/modeling_qwen2.py)（Qwen1.5架构路径）及 [Llama](https://github.com/huggingface/transformers/blob/v4.44.0/src/transformers/models/llama/modeling_llama.py) forward将logits转换为FP32。本包FP32熵公式与此口径一致；未声称不同模型/引擎的分布或阈值判断逐bit相同。
- 工具统一为真实 DOC_RAG → 既有完整 MedCorp 四库 BM25 每库32 + MedCPT top8；不引入上游外部 web/KG/NER 的异构模型。语言改为英文，动作语义按论文；不使用 CF 专项提示。此工具集合迁移属于统一框架适配，不能称上游完整工具系统。
- i-MedRAG 使用当前 M4 的 Llama-3.1-8B-Instruct；TC-RAG 按用户明确指令使用当前 M5 的 Qwen3-8B，`enable_thinking=false`，YaRN factor4 / original32768。BF16、temperature=.7/top_p=1/top_k=0、seed42、131072 上下文和追加检索预算30000沿用当前 v5 M4/M5。查询/解析/QA/TC动作/最终/格式化各阶段 token 上限单独冻结。不同 backbone 的两个新方法不能作为只改变算法的直接因果对照；与旧 M0/M2 的64-token预测和不同生成引擎也不构成全部条件受控的比较。
- 同一轮 QA 并发提交、按查询序号写回，各条 QA 单独保存成功收据；不同输入可共享张量批次，各输入的上下文与随机数流独立。经过共享GPU环境下的实际OOM，执行配置v4将合批上限改为32000 padded tokens（单个合法长请求保留完整输入），使用可扩展显存分配器，并将Llama层分为12/20、Qwen分为14/22，4个输入工作线程。方法轮数、检索条数、输入和生成预算均未减少。小模型回放验证单独/合批的 token 序列一致；BF16 在不同硬件或张量形状下仍可能有数值差异，未声称跨引擎逐 bit 一致。早期pilot及失败记录保留。请求缓存、尝试记录和最终结果均采用原子写入，运行配置改变须新目录。
- 按用户最新范围要求，本轮保留TC官方默认sigma=1.2，不执行阈值校准或正式题盲测。早先登记的有限校准计划未执行；无据此产生的阈值或预测。
- 任务允许的固定证据保留于原问题，检索也按冻结证据权限执行；最终原题自带证据不等于直接合并迭代检索文档。M22 沿用 v5 六档材料，额外检索访问需清晰命名及单独报告，不能冒充原生静态证据协议。

## 验证证据

19项自动测试、两方法各24条真实开发运行、两个实际模型的熵参考对照以及终态恢复已完成，证据汇总于[acceptance_report.md](<acceptance_report.md>)。全部实际prompt/QA历史/活动栈/状态接受边界已通过离线审计。输出格式与开放诊断评分兼容问题、其他来源及长输入的真实验收仍保留为未完成项。
