**当前：M6/M7均暂停；M7保存1646条。用户已授权三卡切换到新M4，见 ../results_v5_m4_structured/README.md。**

**2026-09-13 08:03：用户暂停M6；GPU1/2/3全部运行M7。当前入口：[formal_balanced/README.md](<formal_balanced/README.md>)。M6结果和缓存保留，勿自动恢复。**

# v5 M6 / M7 正式输入小批量试跑（2026-09-13）

**06:57更新：当前活动全量为 [按阶段和长度合批的接续](<formal_balanced/README.md>)；formal、formal_fast均已停止，勿重启。**

**2026-09-13 06:37更新：活动全量已切换至 [提高并发后的接续](<formal_fast/README.md>)，旧formal队列已停止，勿重启。**

**最新状态：用户已授权全量，2026-09-13约05:46启动。运行入口和实时状态见 [formal/README.md](<formal/README.md>)。以下为先行小批量的历史记录。**

用户授权评测新 v5 的原始 M6 i-MedRAG、M7 TC-RAG，先运行一部分检查兼容性与效率，允许使用当前三张空闲卡。本目录先执行每方法12个输入的诊断试跑；全量每方法13,905输入，共27,810次方法评测，尚未启动全量队列。

沿用 [前次实现与运行记录](<../../m6_m7_implementation/PAPER_REPRODUCTION_RECORD.md>)。本地 `code/` 和 `tests/` 是启动时源码副本。没有新增 CF、WM、adapter 等模块。保留已记录的统一框架适配：M6 Llama-3.1-8B；M7 Qwen3-8B、关闭thinking；完整MedCorp BM25+MedCPT；M22固定证据加外部检索。此处的“原始”指基线方法，不表示复现原论文的全部模型和工具设置。

## 样本与预算

从冻结 v5 输入按可见文本字符数排序，各11个来源选长度中位输入，另加全库最长输入，共12条；不读取答案或此前模型预测来选择。`data/pilot_manifest.jsonl` 记录来源、格式、选择原因。包含全部五种答案格式，最长输入来自M20，共260,199可见字符。字符长度只用于选样，实际token长度由模型收据记录。该样本用于诊断，不能代表全库准确率。

M6保留4轮，每轮请求3条追问，标准22次LLM调用/输入、12次检索/输入（实际查询数与格式修复另计）；M7保留最多8步、topK=4、sigma=1.2、完整分布熵。阶段token预算、检索预算及提示均沿用前次runtime_v4配置。全量标准M6约305,910次LLM调用和166,860次检索，M7最多111,240次动作生成，实际调用与重试据收据统计。

仅把模型从前次共享环境下的两卡分层部署改为单卡完整副本，每进程4个输入线程、32,000 padded token合批预算。GPU1/2各承担6条M6，GPU3承担12条M7。GPU0保留其他用户进程。单个合法长请求不截短以迎合合批预算。

前次开发吞吐为M6约7.25、M7约30.95输入/小时（共享GPU），不能直接外推本轮三张空闲卡和长输入。首轮预计至少数十分钟；全量时间待实测。配置参与既有请求种子计算，设备配置变化会改变请求种子；不把本轮与旧运行视为逐token相同的对照。复用已有精确查询检索缓存，未复用开发集答案。

## 执行与状态

tmux socket：`v5-m6-m7`。会话：`pilot-m6-gpu1`、`pilot-m6-gpu2`、`pilot-m7-gpu3`。每个模型执行了同后端熵参考检查，结果在对应 `runs/*/backend_reference.json`。日志与退出状态在 `logs/`，逐请求、事件、终态和配置在 `runs/`。

```bash
cd /home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7
python3 status.py
tmux -L v5-m6-m7 list-sessions
```

实际启动命令（运行中不要重复启动）：

```bash
bash launch_pilot.sh 1 imedrag data/pilot_m6_gpu1.jsonl pilot_m6_gpu1
bash launch_pilot.sh 2 imedrag data/pilot_m6_gpu2.jsonl pilot_m6_gpu2
bash launch_pilot.sh 3 tcrag data/pilot_inputs.jsonl pilot_m7_gpu3
```

全部预定输入必须有ok/invalid/failed终态，失败与无效不从分母删除。既有脚本保留请求与终态恢复；同一run的配置及源代码不可在运行中更改。原生评分继续使用 `evaluation_labels` 与既有canonical映射。小样本不会作为全量R1–R5结果发布。

## 试跑发现的上游行为遗漏与修复

M7原试跑已完成12/12：1有效、11无效、0运行失败，冷运行404.71秒。9条缺动作标签，1条空Thought，2条八步耗尽。核对锁定上游 `upstream/TC-RAG/model/TCRAG.py::process_no_regular_output` 发现：上游将没有任何动作关键词的输出加上 `Final Answer:`，作为提议继续经过步数和熵检查；旧适配直接失败，遗漏这段行为。

独立副本 `tc_upstream_fix/` 补回该处理。保留原始响应计算熵，sigma=1.2和topK=4不变；保留本包支持的Plan/Summary，不照搬上游把所有 `query` 全局替换为 `input` 的字符串处理，因为那会破坏已适配的DOC_RAG参数。14项方法测试通过，覆盖早停拒绝、高熵拒绝、低熵接受及无效答案格式。复用77份请求收据（其中60次LLM请求），追加10次LLM请求后12/12完成：9有效、3无效、0运行失败。50.19秒是追加计算时间，不是完整方法吞吐。实际轨迹审计通过70次模型身份与活动栈检查、57次熵重算、33次接受边界检查。两条八步耗尽和一条空Thought仍记无效。

M7诊断原生评分已完成，12输入映射19条评分记录，见 `diagnostics/M7/scores/`。“有效”不等于答对；该样本不能外推全量准确率。

M6核对锁定上游 `upstream/MedRAG/src/medrag.py::i_medrag_answer` 发现两项额外限制：旧适配要求抽取模型的查询字符串逐字匹配原文，并将任一查询解析失败轮次升级为整题invalid；上游直接使用抽取列表，解析失败时跳过该轮，仍可返回最终答案。独立副本 `m6_upstream_fix/` 移除这两项门槛，保留JSON/类型检查、真实检索与QA失败记录。14项方法测试通过，包括改写/换序列表按上游消费、解析失败轮次保留记录且不否定合法最终答案。硬件或检索/QA失败仍记failed。

M6修复验证由 `m6_upstream_fix/continue.sh` 在原分片结束后接续。同题对比新旧查询列表，从首个发生变化的轮次起重算QA及后续依赖，之前请求原样复用；选择不依赖gold或正确性。缓存来源在每个run的 `cache_provenance.json`。原试跑及其源代码不修改。

`watch_pilot.sh` 在原始三个分片结束后生成 `pilot_summary.json` 和 `pilot_details.jsonl`。`watch_fixed.sh` 等待M6修复分片完成轨迹审计，再运行 `finalize_fixed.py`，生成 `fixed_pilot_summary.json`、`RESULTS.md` 与 `diagnostics/M6/`、`diagnostics/M7/` 原生评分。tmux会话 `pilot-m6-fix-gpu1/2` 和 `fixed-report` 承担接续及汇总；不要重复启动。
