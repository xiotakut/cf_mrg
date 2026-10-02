# MedGENIE（当前M6）

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。MedGENIE v2 Llama-3.1-8B/v5适配已完成384输入试跑及13,905输入全新全量生成。全量运行失败0；格式有效96.49%、原生有效77.32%、ALL准确率48.02%。5份背景＋1次greedy reader；保留失败试跑和来源论文适配差异。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [2026-09-14：从 MedRGAG 基线筛选 M6 替代候选](#record-0229)
- [2026-09-14：MedGENIE 四来源复现（进行中）](#record-0230)
- [2026-09-14：新版M6 MedGENIE独立384题试跑](#record-0231)
- [2026-09-14：M6 MedGENIE v2全量v5](#record-0232)
- [README.md](#record-0396)
- [RESULTS.md](#record-0397)
- [README.md](#record-0398)
- [RESULTS.md](#record-0399)

<a id="record-0229"></a>

## 2026-09-14：从 MedRGAG 基线筛选 M6 替代候选

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第539行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2026-09-14：从 MedRGAG 基线筛选 M6 替代候选

用户要求在MedRGAG中寻找替代方法。核对论文附录A/C及本地src/main.py：候选包括GenRead、MedGENIE、GRG、CGAP；本地MedRGAG代码未发现这些独立基线执行器，不能声称直接切换现有开关即可使用。优先候选为MedGENIE的ICL reader路线：面向医学的选项相关/无选项多视角生成背景，再读取回答，有[作者公开实现](https://github.com/disi-unibo-nlp/medgenie)及[ACL2024论文](https://aclanthology.org/2024.acl-long.533/)，可与现有检索方法形成生成增强对照。作者同时提供FiD训练路线；优先评估无需新训练的ICL路线。原方法针对选择题，v5无选项诊断及证据错误定位如何适配尚需验证，不能预设97%以上有效或具体加速倍数。

备选CGAP：MedRGAG附录采用5份上下文及投票，免外部语料但投票仍需要多份答案，且开放式诊断的投票适配需定义。GenRead在MedRGAG中使用训练数据构造5个ICL簇，准备成本高于最简零样本变体；GRG在该文设置生成10个候选再重排top3，不优先用于本次降低成本的目标。这些是基于公开流程的筛选判断，尚未接入或试跑，未改变M6编号/正式配置。MedRGAG论文来源：https://arxiv.org/html/2510.18297v1 。

<a id="record-0230"></a>

## 2026-09-14：MedGENIE 四来源复现（进行中）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第546行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2026-09-14：MedGENIE 四来源复现（进行中）

用户要求参照原论文、原论文链接代码、MedRGAG描述及其代码（若有）。已下载ACL2024原论文与官方checkout `6ccff62c19e0a51447263e487efac4521f49259a`，证据在 `upstream/papers/` 和 `upstream/medgenie/`。原论文附录A明确3份option-focused＋2份option-free、两示例生成prompt、temperature=.9、frequency_penalty=1.95、512 tokens；ICL reader greedy。本轮保留这些参数及官方Llama3 reader示例，生成器和reader沿用现有Llama3.1-8B（MedRGAG的generator及reader之一），全题型接口适配另行记录；不是PMC-LLaMA原权重的表格分数复现。MedRGAG附录A统一generator温度1.2/256 tokens、zero-shot及reader温度.2，与原方法不同；没有直接套用其未单独披露的MedGENIE细节。匿名仓库API返回Cloudflare验证页；发现本地origin为 `ll0ruc/MedRGAG`，继续检查公开checkout。本地源码搜索未找到MedGENIE执行器；也检查了gzxiong/MedRAG以覆盖名称歧义。

环境尝试：系统没有`pdftotext`，改用网页PDF文本读取，没有为此安装依赖。复现运行将使用既有vLLM环境、空闲单卡，先24条固定开发题；未启动13905条全量。

启动记录：`CUDA_VISIBLE_DEVICES=1 VLLM_USE_V1=0 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True /home/data3/txy/MedRGAG/.venv/bin/python -u code/run_medgenie.py --inputs data/dev_inputs.jsonl --run-dir runs/medgenie_dev_v1 --workers 12`。日志 `logs/medgenie_dev_v1.log`。3+2分支、选项隔离、完整固定证据、5份背景合入reader、6次模型调用/零检索及缓存复验已通过 `tests/test_medgenie.py`；CPU流程检查不当作真实模型结果。公开MedRGAG已clone到 `upstream/MedRGAG`，提交 `0057853df65dcaa46d2934a28f8d5025fc3de623`，在其Python/Markdown源码未搜到MedGENIE；这解除了匿名站不可访问对本轮代码核查的阻碍。


###### 四来源核对与本轮配置取舍

| 来源 | 已核查证据 | 对实现的作用 |
|---|---|---|
| [MedGENIE原论文（ACL2024）](https://aclanthology.org/2024.acl-long.533.pdf) | §3.1–3.2、附录A、B.3、C、K | 3份option-focused＋2份option-free；两条背景生成示例；先生成后读取；无外部检索；512 tokens、temperature=.9、frequency penalty=1.95；reader greedy |
| 原文脚注链接的代码 | 原文第1页脚注URL `https://github.com/unibo-nlp/medgenie` 实测404；现存[作者官方仓库](https://github.com/disi-unibo-nlp/medgenie/tree/6ccff62c19e0a51447263e487efac4521f49259a)的README标注相同论文、方法、作者引用和模型 | 使用其 `context_generation/prompt/pmc-llama-13b-awq-template{,-no-options}.txt`；`generate_contexts.py`/`src/utils.py`核对输入与并行采样；`utils/preprocess.py`先focused后free拼接；`icl_reader/benchmark.py`及Llama3模板核对greedy和一示例reader |
| [MedRGAG论文v1](https://arxiv.org/html/2510.18297v1) | §4.2、附录A/C | 明确MedGENIE为option-focused＋option-free；提供Llama3.1 generator/reader实验条件；共享generator参数与原法不同，不能替代原方法的细节 |
| [MedRGAG公开代码](https://github.com/ll0ruc/MedRGAG/tree/0057853df65dcaa46d2934a28f8d5025fc3de623) | 本地已有origin及本轮重新clone相同SHA；检查 `main.py`、`src/`、README和文件列表 | 未找到MedGENIE独立执行器/配置；不能声称调用了作者MedRGAG中的MedGENIE实现。额外在已有 `gzxiong/MedRAG` checkout搜索也未找到该方法 |

实现入口：`code/run_medgenie.py`；方法：`code/medgenie.py`；配置：`configs/medgenie.json`；后端：`code/medgenie_backend.py`，从已验证的 `optimization_vllm/code/vllm_backend.py`复用，增加逐阶段temperature/frequency penalty传递，不改变旧M6/M7后端。复用既有Session请求收据、重试/恢复和run_item、audit与原生score.py；无需安装新依赖。

实际身份为 **MedGENIE-Llama-3.1-8B，v5适配版**，候选替代M6。原i-MedRAG执行标识、目录和历史结果保留。本次没有修改五/六方法正式汇总，也没有把MedGENIE预测覆盖为i-MedRAG。

| 项目 | 原论文/官方实现 | 本轮实际值与理由 |
|---|---|---|
| Generator | PMC-LLaMA-13B，4bit AWQ | Llama-3.1-8B-Instruct，BF16；沿用M6比较模型，亦为MedRGAG generator |
| 背景生成prompt | 两条固定医疗示例＋问题，带/不带全部候选选项；不是逐个选项各生成一次 | 固定示例原文直接读取；将完整prompt放进Llama3.1 user消息，用其原生chat template；保留题目原有证据 |
| 背景数量/采样 | 3＋2；.9、1.95、512；`n`多样本 | 完全保留数量、采样参数和上限；同批提交五个请求，独立seed，focused→free顺序固定 |
| Reader | 主文Llama2/Zephyr两示例；后来Llama3模板和实验为一示例；greedy；代码max_tokens=50 | 采用官方Llama3 MedQA一示例的完整问题和背景；其示例答案包装为JSON；当前模型为Llama3.1；greedy；输出上限2048以支持纠错列表 |
| Seed | 原文reader state=0 | 项目seed42＋已有请求级独立seed机制；不会声称与作者逐token一致 |
| Native任务接口 | 医疗单选，字母答案 | 沿用single、multi、diagnosis、relation、robustness_single和原生选项键；仅改reader任务/格式说明，不追加formatter/投票/重排/兜底答案 |
| 无选项任务 | 原论文未评测 | 5份option-free独立背景；不生成伪选项。relation若输入自带options则照原始3＋2 |
| 上下文 | 官方reader会按窗口跳过放不下的背景 | 131072窗口，题干和固定证据完整保留，五份背景全部交给reader；超窗报错，不能静默截短 |
| 生成输出清理 | PMC原脚本清除Context标签及Answer后的续写 | 本轮只strip外围空白；Llama聊天输出不套用PMC模型专用清理，收据保留原输出 |

局限性：这次复现方法并在既有v5接口验收，不复现ACL原始模型/数据集表格分数，也不是已经确认的MedRGAG baseline精确配置。两来源差异已逐项披露；MedRGAG没有公开该baseline执行器。开放题5份free和统一MedQA reader示例属于本地适配。开发集小样本只能验证接口及描述性准确率，不能证明全量效果或对i-MedRAG的配对加速。

示例重叠检查：原始两条生成示例及一条reader示例的规范化题干，在24条开发输入、13905条正式输入均没有包含匹配，见 `reports/medgenie_demo_overlap.json`。此检查不读取gold，不代表语义近重复已完全排除。


###### 首次试跑完成与提示适配修复（v1→v2）

v1已完成24/24，接口JSON有效24/24；144次模型输出（120背景＋24答案），37951输出tokens、198872输入tokens，纯推理29.98秒，含加载61.88秒，39次输出达到长度上限，零检索、零重试。原生评分15/24有效，MedQA 8/12正确，MedEinst 2/12正确（9个诊断字符串不在既有canonical表）。首次运行和原生评分保留在 `runs/medgenie_dev_v1`，没有修改评分规则。原样重启确认全部终态复用，无新模型加载/生成。

轨迹抽查发现首版把PMC的两段completion示例整体放进一个Llama user消息，会导致模型回答示例题，例如真实肺癌病人问题下重答BPH/维生素B12。这是backbone聊天模板适配错误，不能仅以JSON全有效宣告复现成功。修复为将官方两个Question→Context示例分别映射为user→assistant轮，再将真实题作为最后一个user轮，并用简短system明确生成最终题的背景。官方示例题和背景正文不改，3＋2数量及采样不改；不是根据gold调整答案。

v2计划仍用同24条开发题重新生成，输出 `runs/medgenie_dev_v2`，日志 `logs/medgenie_dev_v2.log`；源码及配置各run自动保存，v1不覆盖。

接口覆盖补充：固定24题仅含single和diagnosis。另从已有v5公开输入中按题干＋证据字符长度最短、同长度取原始顺序，分别选multi、relation、robustness_single各1条保存 `data/medgenie_format_smoke.jsonl`。这3条是正式来源的接口抽查，不属于24题开发集、不计入其准确率，选择过程不读gold。单独输出 `runs/medgenie_format_smoke_v2`，用于确认各原生输出类型及纠错列表能真实生成。


###### v2 开发验收结果（已完成）

`runs/medgenie_dev_v2/complete.json`：24题全部终态、接口合法24/24、failed=invalid=pending=0；H20物理GPU1，workers=12；纯推理32.72秒，含模型加载63.19秒。144次真实模型输出＝120份背景＋24个答案，44807输出tokens、209386输入tokens，55份背景达到512-token上限，零reader长度截断、零检索、零重试。耗时为实际端到端推理段wall time，不能用终态重放时间估算吞吐。相同命令再次执行只复用终态，未新增生成。

| 固定开发来源 | 分母 | JSON接口有效 | 原生评分有效 | 原生正确 |
|---|---:|---:|---:|---:|
| MedQA_dev | 12 | 12 | 12 | 11（91.67%） |
| MedEinst_train | 12 | 12 | 0 | 0 |
| 合计 | 24 | 24 | 12（50%） | 11（45.83%） |

诊断原始输出包括 `Viral Pharyngitis/Tonsillitis`、`Conjunctivitis`、`Acute Coronary Syndrome (ACS)`、`Pertussis (Whooping Cough)` 等。当前原生评分使用既有固定canonical精确匹配，这12条字符串均未映射成功；这同时可能包含错误诊断、粒度差异、同义词/附注和多诊断文本，不能仅凭该结果认定全部只是格式错误，也不能擅自将其算作正确。原样保存预测，不根据gold补答案或修改评分器。**开发运行完成不等于全题型准确率已验收；诊断兼容性/效果仍是限制，未启动全量正式评测。**

示例主题直接字符串检查（`cost_summary.json`）：包含BPH/B12等示例词的背景由v1 66/120降为v2 1/120。抽查v2背景已围绕最后的真实题；剩余一条位于神经症状/营养缺乏题，提及维生素本身相关。该数字仅用来辅助定位示例重答，不是背景正确率或完整语义相关性指标。保留两版全部轨迹，可复核具体错误和修复。

验证证据：`tests/test_medgenie.py`、各run的 `resolved_config.json`/`code_snapshot`/`items/*/{requests,attempts,events,result.json}`，`scores/{summary,source_task_scores}.json`及 `cost_summary.json`。补充的3条其他题型接口检查仍单独运行，结果随后记录。


###### 补充题型检查与多选序列化修复

首次3条接口检查全部完成，15.16秒推理、45.93秒含加载，共18次模型输出；relation、robustness_single合法，多选返回 `{"answer":"A"}` 被数组合同判invalid（2/3合法）。原始结果在 `runs/medgenie_format_smoke_v2`。修复仅在multi任务、answer是单个合法原生key时，将该值包装为单元素数组；不拆解逗号字符串、不推断缺失选项、不改其他任务，也不新增模型调用。原模型响应以 `model_raw_response` 和事件保留。已加回归断言验证合法单项转换、非法/多项字符串拒绝、原数组不变及single不变。

这属于确定性序列化，不改MedGENIE背景/reader流程、prompt、阶段seed或采样，因此算法配置仍为 `medgenie-llama31-v5-v2`；每run代码快照和冻结code_hashes区分序列化修复版本。追加新目录 `runs/medgenie_format_smoke_v2_multifix` 实际复验3题，保留修复前失败。24题single/diagnosis不走新分支，其原生评分继续引用已完成 `medgenie_dev_v2`，不浪费重复推理。


###### 本轮完成状态

多选确定性序列化修复后，`runs/medgenie_format_smoke_v2_multifix` 已完成3/3合法、0失败、0待处理，推理 15.23 秒、含加载 46.19 秒。三条模型原始答案与修复前逐字一致：True；只将多选的字符串 `"A"` 包装为 `["A"]`。本轮追加18次真实模型输出（不是缓存重放），完整成本见该run的 `cost_summary.json`。这是输出合同验证，不是这些题的准确率/事实纠错质量验收。

交付：方法、独立运行入口、配置、来源checkout、回归检查、24题开发预测与原生评分、3题格式抽查及修复前后轨迹均已落盘；运行进程正常退出。当前代码增加的是MedGENIE执行标识，旧i-MedRAG和TC-RAG的源码、预测、汇总保持原身份。正式全量尚未运行。复现和评分命令见本包README；算法/模型与原论文、MedRGAG的差异按上表披露，不能写成作者原始表格分数复现。

<a id="record-0231"></a>

## 2026-09-14：新版M6 MedGENIE独立384题试跑

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第628行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2026-09-14：新版M6 MedGENIE独立384题试跑

{"method": "M6 MedGENIE", "version": "medgenie-llama31-v5-v2+native_multi_singleton_v1", "planned": 384, "gpus": [0, 1, 3], "workers_per_gpu": 32, "source": "/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc", "selection": "Exact previously frozen M7 fresh384 inputs, no reselection based on outputs", "prior_medgenie_smoke_overlap": [], "reused_predictions": 0, "created_at": 1789347199.1114962}

范围为固定输入子集，类别评分仅覆盖子集中的原生任务，不能视作完整v5单元准确率；共享此前M7试跑输入用于描述性比较。GPU2已有其他训练任务，本轮不使用。源码/配置/官方示例冻结在独立包内；复用既有runner、评分器，不修改模型方法。启动、监督、成本、逐题原生评分和报告保存在该包。


###### 384题完成结果、有效率与成本（2026-09-14）

全部384条新生成，分片GPU0/1/3各128；旧预测和阶段复用均0，运行失败/请求重试/缺失/重复均0。含启动墙钟319.44秒（5分19秒）；三卡累计纯推理729.61秒（12.16 GPU分钟），按推理段为1894.72输入/GPU小时。GPU0/3先完成，GPU1处理自身较长分片至全部结束；未中断或迁移题目。所有模型进程正常退出，GPU2其他训练始终保留。配置和run代码快照沿用已修复MedGENIE v2，无本轮方法更改。

| 口径，均以384唯一输入为分母 | 新M6 MedGENIE | 同题M7完整typed版试跑 |
|---|---:|---:|
| 协议有效 | 371（96.61%） | 366（95.31%） |
| 原v5格式有效 | 366（95.31%） | 366（95.31%） |
| 原生评分有效 | 287（74.74%） | 290（75.52%） |

诊断105题中21原生有效（20%），79未映射、5歧义；single182/188、multi6/6、relation20/20、robustness58/65原生有效。有效率不等于准确率；没有根据gold修正输出、放宽诊断映射或剔除无效题。协议拒绝的13条在既定native入口按空答案评分，其malformed_json原因不能解读为13条原始输出均是JSON语法错误。原始协议无效原因另列于结果JSON。

2304次真实生成＝1920背景＋384reader；5,319,409输入tokens、668,506输出tokens，零检索、零额外评分forward。609份背景到512-token上限、1个reader到2048-token上限，均保留。384个输入/配置身份、384个实际五背景顺序和reader拼接、2304个实际模型/prompt/token预算检查全部通过；确定性多选序列化触发1次，保留model_raw_response。原始请求、尝试、事件、代码及实际配置均可追溯。

离线原生评分保留本子集覆盖的412条映射，不将共享输入的多评分映射折成一条。子集内单元平均准确率ALL52.78%（234单元）、R1 30.14%（73）、R2 0%（4）、R3 10.53%（19）、R4 0%（1）、R5 67.35%（170）。这些只包含384输入触达的原生任务，不保证单元内任务完整，尤其R2/R4极小，不能当全量v5结论或与完整六方法柱状图直接合并。无全量新推理启动。

运行确认新版可在当前三卡完成该规模评测，格式有效率与同题M7一致，原生有效少3题；诊断映射、鲁棒性输出及一条reader截断仍限制结果。旧i-MedRAG128题34分29秒和本次输入/方法均不同，不报告成对加速倍数。当前方法身份为MedGENIE-Llama3.1-v5适配版，原论文/MedRGAG配置差异沿用上文披露。

证据入口：[试跑结果](/home/data3/txy/docs/baselines/medgenie.md#record-0397)、[最终机器可读指标与审计](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/reports/final_results.json)、[逐题原生评分](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/scores/scored.jsonl)、[GPU与进度监督](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/reports/supervision.jsonl)、[冻结输入计划](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/reports/plan.json)。预运行回归检查与输入三分片覆盖检查通过；最终审计和评分脚本为`code/finish_pilot.py`，只离线读取预测，不调用模型。

<a id="record-0232"></a>

## 2026-09-14：M6 MedGENIE v2全量v5

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第657行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2026-09-14：M6 MedGENIE v2全量v5

用户在384题验收后明确要求全量运行、中途尽量表格汇报。冻结此前验收方法、后端、runtime、提示及配置，全部13905输入重新生成，保留旧试跑独立。GPU0/1/3，70%显存预留、max_num_seqs128、每卡32线程；109个128题动态分片，最后81题；打乱seed20260918。GPU2现有训练不动。常驻引擎复用已验证M4/M7队列，MedGENIE resolve配置函数提取以支持分片冻结/恢复；方法无修改。

预启动已验证13905唯一输入全覆盖、109分片无重复领取/归属恢复、MedGENIE背景/多选序列化/预算/缓存回归检查、冻结配置一致恢复且拒绝改workers；方法/后端/runtime/配置与384试跑逐字一致。磁盘可用2.2TB。五分钟进度、协议/格式/原生有效率、失败、重试、截断及GPU0–3保存到 reports/；全量完成后对15616映射作原生评分、6104单位和13000判断范围核对、全部生成轨迹检查，更新七方法分类图。所有无效保留分母。

执行：`bash launch_gpu.sh 0`、`1`、`3`，tmux socket `m6-medgenie-v5-full`；运行包/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full。

09:04 GPU0/1/3常驻worker已启动，PIDs2271490/2271494/2271498。首批完成且三卡进入连续生成。独立监督进程每300秒保存快照；完成13905题及109分片后依次执行`code/finish.py`原生评分/轨迹检查和`code/full_report.py`七方法图/成本/试跑以外分层。CPU评分使用HF环境，绘图使用已有matplotlib的vLLM环境，避免此前M7的绘图库环境问题。

09:21进度达到1391/13905（10%），协议98.13%、格式97.12%、原生78.29%，运行失败/重试/阶段复用均0。GPU0/1/3持续生成，监督原始记录持续写入；本时点有效率只针对已完成输入，不代表全量结果。

09:45进度3566/13905（25.65%），协议97.42%、格式96.47%、原生77.76%，0失败/重试/阶段复用。26个分片完整，3个执行中；GPU2原训练占用约09:42自然释放，本轮继续既定GPU0/1/3三卡。五分钟表格与更短进度检查均保留到supervision.jsonl。

10:26全量过半：7117/13905（51.18%），54/109完整分片，协议97.47%、格式96.45%、原生77.53%，运行失败/重试/阶段复用0。用户09:59要求仅每五分钟汇报一次，此后取消逐分钟对话进度，继续五分钟表格及异常时即时通知；原始监督文件持续。推理方法、预算与三卡并发未改。

11:07完成10660/13905（76.66%），82个完整分片；协议97.46%、格式96.45%、原生77.41%，运行失败/重试/阶段复用均0。剩余3245题，三卡仍按启动配置运行。


###### MedGENIE全量完成、最终评分与成本（2026-09-14 11:48）

新版M6 MedGENIE v2全量13,905输入和15,616原生评分映射完成；全部新生成，0运行失败/重试/阶段复用，109分片、83,430次真实生成轨迹检查通过。协议97.45%、格式96.49%、原生有效77.32%，ALL原生准确率48.02%。推理含初始化2小时41分46秒，GPU0/1/3本轮模型已正常退出。

| 指标 | 结果 |
|---|---:|
| 协议有效 | 13550/13,905（97.45%） |
| v5格式有效 | 13417/13,905（96.49%） |
| 原生评分有效 | 10751/13,905（77.32%） |

输入唯一覆盖、缺失/重复/未知ID检查通过；15616评分映射全部保留（6818 reference＋8798 non-reference），6104唯一单元、13000入选判断范围核对通过。类别归属采用evaluation_labels，类别内先对单元非reference任务取均值再等权平均；ALL独立去重。所有无效保留分母。

| 类别 | 单元数 | 单元平均原生准确率 |
|---|---:|---:|
| ALL | 6104 | 48.02% |
| R1 | 2866 | 29.94% |
| R2 | 79 | 18.99% |
| R3 | 733 | 21.42% |
| R4 | 13 | 61.54% |
| R5 | 3600 | 65.15% |

ALL聚类bootstrap 95%区间46.50%–49.53%；R4仅13单元，61.54%不能作为稳定优势结论。七方法图沿用纵轴0–100和各方法不同颜色的分组柱状图；M6为MedGENIE，旧i-MedRAG不混入。其他M0/M2/M3/修复M4/M5和完整第二版M7全量结果保持不变。

协议无效355：missing_or_conflicting_answer171、invalid_option_key147、invalid_document_ids31、invalid_errors6。原生额外133诊断歧义造成格式有效降至13417，再有2666诊断未映射造成原生有效10751。原生3154无效均保留；其中malformed_json355是协议拒绝后置空入口结果，不能当作原始JSON语法错误355次。诊断原生有效760/3560（21.35%）；单选6355/6489（97.93%），鲁棒单选2480/2700（91.85%），multi167/167和relation989/989有效。未根据gold修正输出或改变canonical评分器。

成本：83,430次生成＝69,525背景＋13,905reader；208,381,653输入tokens、24,439,800输出tokens；零检索、零额外评分forward，零请求失败/重试。22,487背景达到512-token上限、70个reader达到2048-token上限，保留预算和原始输出。推理墙钟9706.276秒，三卡分片累计28864.367秒（8.02 GPU小时），1734.25输入/GPU小时。每卡加载约35.25秒；墙钟含加载，分片累计不含加载和分片间排队。GPU0共享其他用户任务；GPU2其他任务曾自然释放后重新占用，本轮始终仅使用0/1/3。完成后本轮worker均退出。

审计：13905输入/配置身份、13905份五背景视角/拼接与reader顺序、83430个实际prompt/模型/token预算全部通过；确定性多选序列化触发73次，原始model_raw_response保留。启动前MedGENIE回归、队列归属恢复/109分片唯一覆盖、配置恢复与改workers拒绝检查通过；复用的轨迹审计器也离线重核384试跑的2304次真实生成，无新增推理。此次全量没有运行故障、重启、OOM或中途算法修改。

历史MedGENIE正式接口抽查3题及384试跑之外13518题：协议97.44%、格式96.48%、原生77.33%。本轮重新生成的同384题为375协议/372格式/294原生有效，与独立试跑371/366/287存在差异。已核对384条背景生成prompt、采样和seed完全一致；该比较是新运行的描述性结果，不把它当缓存重放或逐token等价。动态合批下的具体差异来源未另作隔离实验。M7此前已运行全部v5，这一排除分层不声称全新独立测试集。

已生成PNG/PDF/SVG七方法图、完整精度CSV、原生逐条/来源/类别/配对评分及逐题有效率。用户指定只每五分钟对话汇报后已按要求调整，原始监督记录保留。

证据：[完整结果与图](/home/data3/txy/docs/baselines/medgenie.md#record-0399)、[最终成本与审计](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/final_results.json)、[原生评分](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/scores/scored.jsonl)、[试跑之外分层](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/exposure_strata.json)、[同384题轨迹对照](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/pilot_full_trajectory_comparison.json)、[监督记录](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/supervision.jsonl)。

<a id="record-0396"></a>

## README.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/README.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh`。

### 新M6 MedGENIE v2：384题独立试跑

2026-09-14按用户要求试跑。使用此前M7固定384题，GPU0/1/3各128题、32线程、70%显存预留。原实现、参数、示例已冻结；运行前test_medgenie通过，零旧预测复用。

运行：`bash launch.sh GPU编号`。相同命令可恢复；不可改变已启动配置。进度入口`reports/status.json`，历史`reports/supervision.jsonl`，全部完成后`RESULTS.md`。

完整方法和失败修复记录：[主记录](/home/data3/txy/docs/baselines/medgenie.md#record-0231)。旧i-MedRAG结果保持其原身份，不与MedGENIE合并。

<a id="record-0397"></a>

## RESULTS.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/RESULTS.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh`。

### 新M6 MedGENIE v2：384题试跑结果

固定使用此前M7的384题，全部新生成，旧预测及LLM阶段复用0。模型Llama-3.1-8B-Instruct；5份生成背景＋1次greedy reader，无检索、无CF/WM或Schema约束。

GPU0/1/3，每卡128题、32题目线程、128并行序列、显存预留70%。含启动墙钟5.32分钟；纯推理累计12.16 GPU分钟。

| 指标（分母384） | 新M6 | 同题M7完整typed版 |
|---|---:|---:|
| 协议有效 | 371/384（96.61%） | 366/384（95.31%） |
| 格式有效 | 366/384（95.31%） | 366/384（95.31%） |
| 原生有效 | 287/384（74.74%） | 290/384（75.52%） |

协议有效表示方法输出满足合同；格式有效与既有M0–M5的原生解析口径对齐；原生有效还要求诊断等可映射。有效率不是准确率。

| 题型 | N | 协议有效 | 格式有效 | 原生有效 |
|---|---:|---:|---:|---:|
| diagnosis | 105 | 100.00% | 95.24% | 20.00% |
| multi | 6 | 100.00% | 100.00% | 100.00% |
| relation | 20 | 100.00% | 100.00% | 100.00% |
| robustness_single | 65 | 89.23% | 89.23% | 89.23% |
| single | 188 | 96.81% | 96.81% | 96.81% |

协议无效原因：{"missing_or_conflicting_answer": 5, "invalid_document_ids": 1, "invalid_option_key": 7}；另有79条诊断未映射、5条诊断歧义。协议拒绝的输出按既定评分入口置空，因此native中的malformed_json计数不能解释为全部原始JSON语法错误。

运行失败0；请求重试0；真实模型生成2304次，零检索。背景长度截断609/1920，reader截断1/384；原预算和无效分母均保留。

| 类别 | 部分覆盖单元数 | 子集任务的单元平均准确率 |
|---|---:|---:|
| ALL | 234 | 52.78% |
| R1 | 73 | 30.14% |
| R2 | 4 | 0.00% |
| R3 | 19 | 10.53% |
| R4 | 1 | 0.00% |
| R5 | 170 | 67.35% |

上述类别仅评分384题覆盖的任务，不保证单元内所有任务或R1–R5完整覆盖，不能与全量v5类别分数直接比较。MedGENIE沿用原法3＋2背景（无选项题5份free），模型和开放题接口为本地适配；本次未改方法，也未运行13905题全量。

[配置与成本、无效原因、轨迹审计](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/reports/final_results.json) · [逐题原生评分](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/scores/scored.jsonl) · [进度与GPU历史](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/reports/supervision.jsonl) · [冻结计划](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_fresh/reports/plan.json)

<a id="record-0398"></a>

## README.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/README.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full`。

### M6 MedGENIE v2：v5全量运行

2026-09-14按用户要求全新生成13905输入；旧预测复用0。GPU0/1/3，每卡常驻引擎，32题目线程/128生成序列/70%显存预留，109个动态128题分片。方法沿用384题试跑冻结版，不改变生成流程及采样。

运行`bash launch_gpu.sh GPU编号`；相同命令从已完成题目和阶段恢复。`reports/status.json`为最近监督，`reports/supervision.jsonl`为历史；完成后`RESULTS.md`及`scores/`。

主记录：[MedGENIE全量](/home/data3/txy/docs/baselines/medgenie.md#record-0232)。

<a id="record-0399"></a>

## RESULTS.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/RESULTS.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full`。

### M6 MedGENIE v2：v5全量结果

全部13,905输入新生成，旧预测和阶段复用0；完整保留15,616条原生评分映射。Llama-3.1-8B-Instruct、5份背景＋1次greedy reader；本轮沿用试跑版方法和预算。

| 有效率（分母13,905） | 数量 | 比例 |
|---|---:|---:|
| 协议有效 | 13550 | 97.45% |
| 格式有效 | 13417 | 96.49% |
| 原生有效 | 10751 | 77.32% |

有效率不是准确率。格式有效率沿用既有v5解析口径；原生有效率还要求诊断等映射成功。协议拒绝结果在native入口置空，原生malformed_json计数不能当作原始输出JSON语法错误数。

| 类别 | 单元数 | 单元平均原生准确率 |
|---|---:|---:|
| ALL | 6104 | 48.02% |
| R1 | 2866 | 29.94% |
| R2 | 79 | 18.99% |
| R3 | 733 | 21.42% |
| R4 | 13 | 61.54% |
| R5 | 3600 | 65.15% |

运行失败0，请求重试0；背景截断22487次，reader截断70次。全部无效/失败保留分母。

MedGENIE的模型和v5开放题接口为本地适配，原论文/MedRGAG差异见主记录；不声称复现作者原模型的表格分数。R1–R5可重叠，ALL按6104唯一单元计算，R4仅13单元。

[详细成本、题型有效率和审计](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/final_results.json) · [原生逐题评分](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/scores/scored.jsonl) · [监督历史](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/supervision.jsonl)

含初始化推理墙钟 **2小时41分46秒（161.77分钟）**；累计分片耗时8.02 GPU小时；1734.25题/GPU小时。

![方法分组柱状图](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/v5_grouped_methods.png)

七方法比较见 reports/category_comparison.csv；开发/试跑以外的有效率见 reports/exposure_strata.json。

[方法、适配、历史失败与全量记录](/home/data3/txy/docs/baselines/medgenie.md#record-0232) · [完整精度七方法CSV](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/category_comparison.csv) · [PDF图](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/v5_grouped_methods.pdf) · [SVG图](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/v5_grouped_methods.svg)

诊断原生有效760/3560（21.35%）；主要限制仍为诊断映射及部分鲁棒性输出。成本为83,430次生成、208,381,653输入tokens和24,439,800输出tokens，零检索。

## 2026-09-14：R2优化研究的离线反馈

优化研究回读全量MedGENIE的167道MedPIC输出，并发现选项集合覆盖不足及三道既有定性案例中的生成背景文字退化。指标、原始背景证据、限制和待验证原因统一记录于[R2研究主记录](/home/data3/txy/docs/research/r2_support_head.md#r2-seven-method-diagnosis)。本次仅分析既有结果，未调整MedGENIE正式版本或原评分；背景采样参数与reader示例的因果影响仍待受控验证。
