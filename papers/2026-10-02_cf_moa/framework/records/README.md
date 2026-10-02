# CF / MedRAG论文实验工作区

2026-10-03 五类 benchmark 与五 agent 主线框架完成：[中文逻辑链及证据选择](paper/outline.md) · [原生 LaTeX 框架](paper/latex/framework.tex) · [框架 PDF](paper/latex/framework.pdf)。以数据收集、五类功能体系、v5构建、七系统诊断、五head及CF-MoA为主线；主表七基线＋两配置采用B，全量收益10.09/12.01pp。已核验两份全过程汇报和数据沿革。当前28页完整稿是上一轮版本，新框架尚未展开为新全文；[本轮记录](paper/writing_record.md#taxonomy-benchmark-five-agents-20261003)。

2026-10-03 论文范围修订已完成：[28 页 LaTeX 论文](paper/latex/main.pdf)恢复七配置完整 v5 基线、七系统 R1–R3 加头结果，再单列 M4/M5 六臂 CF-MoA，共 11 表/6 图/24 引用。42 基线指标与 21 组优化前后结果经原评分核验，独立内容审阅与异目录编译通过；[全流程审计与写作记录](paper/writing_record.md#seven-system-scope-correction-20261003)。已更新私有 GitHub，最终提交 `bb5a017`，350 包文件远端核验通过；[发布记录](workspace.md#seven-system-paper-github-20261003)。下方 10-02 页数与制品数量是上一版快照。

2026-10-02 LaTeX 修订：[权威 `.tex` 主稿](paper/latex/main.tex)与[21 页 LaTeX 编译 PDF](paper/latex/main.pdf)已完成并更新到私有 GitHub 论文目录；提供可上传 Overleaf 的工程 ZIP。20 引文、8 表/54 行、4 公式、5 图与异目录编译核验通过；[写作记录](paper/writing_record.md)。早期 Markdown/Typst/Word 为冻结历史。

2026-10-02：[论文材料已上传新目录](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa)，`xiotakut/cf_mrg` 已设为 **private**，需授权访问。LaTeX 修订后的论文目录共 312 文件；[最新发布验收](workspace.md#cf-moa-paper-latex-github-20261002)。下方历史公开访问描述按当时状态理解。

2026-10-02：[CF-MoA 通用英文会议论文初稿已完成](paper/writing_record.md)：[英文 PDF](../Documents/Codex/2026-10-02/cf_moa_paper/manuscript.pdf)、[中文框架](paper/outline.md)、5组图、8组表及复现脚本。20条文献核验、原始记录重汇总与独立事实/写作审阅通过；0新增模型/评分。以09-28全量收尾为主证据，已暴露开发、C3双骨干方向不同与独立确认未执行继续如实保留。

2026-09-28：[完整v5透明收尾已完成](research/cf_moa.md#transparent-closeout-20260928)：零新增推理/评分，全部六臂、11来源、5输入格式、36家族区间及每方法费用/覆盖、五表已实际交付。C3−B ALL区间M4为[−2.5287,−1.0819]pp、M5[+0.3039,+1.5562]pp；默认B保持，C3研究扩展保留。未删题、未改标签或算法；确认/独立F复本及自然M5 C0四旧缺项明确未执行/延后。 [GitHub完整交付](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-28_cf_moa_transparent_closeout/README.md)已发布，提交`2d56c71`，73文件与8个raw入口核验通过。

2026-09-26，已将[完整报告第16章全量补充](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-26_cf_moa_rcv_full_v5/docs/research/cf_moa_experiment_report.md#rcv-full-v5-results-20260926)与[运行过程、源码/配置/逐题trace及成本索引](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-26_cf_moa_rcv_full_v5/RUN_AND_DELIVERY.md)上传GitHub，提交`d857934`。两骨干各13905输入、六臂评分齐全；C3相对B原生ALL −1.8108/+0.9273点。269文件远端逐字核验、7个匿名入口通过；本次0模型/评分、不操作GPU。全量家族区间、每方法费用/最终五表及冻结后确认仍未完成，旧默认B保持。

最新状态：2026-09-24（Asia/Shanghai）。`/home/data3/txy`整个目录是实验工作区，本文是长期文档的统一入口。

2026-09-26，[CF-MoA RCV收口新计划执行中](research/cf_moa.md#rcv-completion-20260924)：M4/M5完整13905输入及C0–C5原生评分均完成，M5自动收尾于15:19完成。主C3相对B的ALL差为M4−1.8108点、M5＋0.9273点，正确输入分别−275/＋89，两骨干方向不一致，默认B不变。18:44检查已无本任务模型/评分进程，GPU1/2/3原脚本占位、GPU0空闲，本轮未操作进程。全量配对区间/最终成本报告、自然M5 C0四旧缺项、共同冻结与确认仍待完成。

2026-09-25 01:02，RCV[执行中第16章](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-25_cf_moa_rcv_completion_in_progress/docs/research/cf_moa_experiment_report.md#rcv-completion-in-progress)、[开发五表与交付包](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-25_cf_moa_rcv_completion_in_progress/README.md)已发布，提交`10b699b`，163远端文件及5个raw入口核验；全v5继续运行、确认未完成。[发布记录](workspace.md#cf-moa-rcv-progress-github-20260925)。

2026-09-24，已发布[候选验证新计划完整报告第15章](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/docs/research/cf_moa_experiment_report.md#candidate-verification-execution)和[运行过程与代码/配置/逐题trace/成本交付](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/RUN_AND_DELIVERY.md)，提交`854f00b`，81远端文件逐字验收、4关键raw入口无认证可读；前述历史包与用户计划保持。本次仅发布，0新模型/评分；[发布记录](workspace.md#cf-moa-candidate-verification-github-20260924)。

2026-09-24，[CF-MoA候选验证效果实验完成](research/cf_moa.md#candidate-verify-results-20260924)：GPU2/3完成780次真实取分，无理由臂历史121正确87/83、自然52正确33/27；带理由臂88/87、35/28（旧B87/82、35/26）。带理由有开发选择增益，但自然M5原生均分及保持配对仍有退步，暂不默认采用。95旧trace、31组原文审阅、缓存控制、完整评分/费用/反例及交付索引齐备；旧失败保留，默认B与旧head不改。两引擎已关闭、两卡恢复各60GiB占位，一般自动队列保持停止。

2026-09-24，[CF-MoA v4定向源码与95触发组合诊断](research/cf_moa.md#v4-trigger-diagnosis-20260924)已完成：旧池78/95含正确键、35组未选中；三seed已有285次重答新增正确键覆盖0、35修复/40误伤。[源码与分析阅读入口已补发GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_v4_diagnosis/README.md)，提交`28ea62f`，完整样本另存私有包。未证实退步由映射/消息丢失代码错误引起；默认B与F关闭保持，0新模型/评分/回放。

2026-09-24，[CF-MoA版本4完整报告第14章](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_minimal_v4/docs/research/cf_moa_experiment_report.md#minimal-head-reuse-v4)及[运行过程/交付索引](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_minimal_v4/RUN_AND_DELIVERY.md)已上传GitHub，提交`3786653`，49文件远端逐字验收，前3版保持。公开代码/配置快照、1384状态、231调用元数据与完整成本；本次0新模型/评分。[发布记录](workspace.md#cf-moa-minimal-v4-github-20260924)。

2026-09-23，[最简复用计划完整完成](research/cf_moa.md#minimal-head-reuse-20260923)：等价旧B五操作包装及F开关交付；旧121三seed小幅增益，自然52两骨干三seed均退步，默认保持等价B、F普通重答不采用。231新调用、247新触发映射评分，完整分母/成本/错误记录保持；GPU0/1不重占、2/3恢复占位。[本地完整报告](research/cf_moa_experiment_report.md)第14章。

2026-09-23，按用户要求释放GPU0/1自有占位，GPU2/3继续保留；[版本3完整进展与细节](research/cf_moa_experiment_report.md)已[上传GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-23_cf_moa_effect_first_v3/docs/research/cf_moa_experiment_report.md)，提交`31069fc`，22远端文件逐字验收通过。保留原全过程并补齐四轮效果优先实验、诊断读出缺口、失败与成本；0本次新模型/评分。[发布/释放记录](workspace.md#cf-moa-effect-first-v3-github-20260923)。

2026-09-23，[第四轮目标条件绑定](research/cf_moa.md#effect-first-cycle4-20260923)完成并未采用：主臂18/34、15/34，低于B23/19；普通20/14、去理由20/15。330真实生成和一次原生评分齐备，M4一题三臂截断保留；发现诊断自由字符串未落实目录键读出，需另版修正。GPU四卡占位已恢复/保持，独立评估未启动。

2026-09-23，[第三轮效果优先开发](research/cf_moa.md#effect-first-cycle3-20260923)已完整结束：B23/19，新主臂及同证据普通重答21/17，无新增证据19/15（各34），未采用。268生成＋123正式检索及评分/比较齐备；GPU0按原profile成功运行后自动补占，当前GPU0/1/2/3均已由原脚本占位。修正仅调度的60GiB额外floor，未改模型；详见[资源交接](workspace.md#gpu-reservation-handoff-20260923)。独立评估未启动。

2026-09-23，[效果优先新计划](../cf_moa/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)[第二轮GPU开发](research/cf_moa.md#effect-first-cycle2-20260923)全部完成：A1为19/34、23/34，A3比较2/8、3/8，A5合成32题30/31，均未建立超越强旧及同预算控制的增量。822新调用，GPU2/3已释放，旧结果保持；A1直接读出离线诊断亦未形成新可用方法，独立评估未启动。

2026-09-23，CF-MoA[版本2完整过程报告](research/cf_moa_experiment_report.md#incremental-revision-v2)已[上传GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-23_cf_moa_incremental_v2/docs/research/cf_moa_experiment_report.md)，提交`a7a97da`，23个远端文件逐字验收；保留上一版快照。新增修订计划后的新B接口、A2兼容、A1_delta/A3负结果、错误与成本，24/80条公开状态可核验。本次只发布，0新模型/评分；[发布记录](workspace.md#cf-moa-incremental-v2-github-20260923)。

2026-09-23，[CF-MoA修订后执行](research/cf_moa.md#incremental-revision-execution-20260923)完成新B确定性封装、前置审阅与A2兼容；A1_delta 6/6不可用、不扩展。A3完整8题受控开发已结束：M4关键4/8未超原题重评分4/8，M5关键3/8低于B/重评分4/8，保留负结果、继续旧目录核。本轮254真实调用全部结束，GPU2/3释放；A5新版及共同冻结/独立评估未完成。

2026-09-23，用户[修订CF-MoA核心计划](../cf_moa/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)已登记：以固定强旧答案B为基准，转向目标化A1_delta与局部修改裁决；保留旧有效组件和全部负结果。A2 parser兼容、紧凑同工具合同另版和独立集暴露审计方向已明确，先做现有修复/误伤trace归因，均未在本次执行；不重算互补矩阵、不直接进入独立评测。GPU0/2/3可用授权已记录，本次0新模型，见[修订主记录](research/cf_moa.md#baseline-delta-plan-revision-20260923)。以下已发布报告和旧阻断段落保留历史状态。

2026-09-23，按用户要求整理[CF-MoA完整执行过程报告](research/cf_moa_experiment_report.md)：集中说明阶段完成情况、A1/A5及聚合全部主要失败链、修复方案、成本、GPU/CPU执行问题与尚未完成的冻结评估；已[发布到GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-23_cf_moa_process/docs/research/cf_moa_experiment_report.md)并核验远端字节，提交`3c43afa`；来源记录见[主记录](research/cf_moa.md#cf-moa-process-report-20260923)，发布验收见[工作区记录](workspace.md#cf-moa-process-github-20260923)。该文是独立过程回顾，后续研究仍续写`cf_moa.md`，不恢复暂停实验。

2026-09-23，[含A1聚合完整开发结果](research/cf_moa.md#saved-a1-complete-development-20260923)为79/121、74/121，低于强旧87/82，保留负结果、不采用；原生评分、三核心逐题比较与完整成本已保存。默认聚合此前75/73也未采用；[固定3draw](research/cf_moa.md#fixed3-complete-development-20260923)完整评分84/74，同池top1为72/57（不可用16/44）。两项GPU作业与[完整激活/证据使用汇总](research/cf_moa.md#saved-a1-complete-evidence-use-20260923)均已结束；[开发交付索引](research/cf_moa.md#development-delivery-index-20260923)已绑定31份证据；原专家不重跑，A3编辑、同工具控制和独立范围待决，[目标已标为阻塞](research/cf_moa.md#goal-blocked-handoff-20260923)，尚未共同冻结。

2026-09-23，[先证据后原生答案v4终态](research/cf_moa.md#aggregation-evidence-first-terminal-20260923)：固定16成功保留；扩展M4 d00021原生解释重复40次并2048截断，首错停止、M5扩展未启动。完整242分母31完成/1失败/210未提交，共32新聚合687218/14586token，0专家重生成；真实入口/停止/成本核验通过，GPU2已释放。保留负结果，不重试/拼接/评分/采用。A1来源重绑定仅CPU完成，不放行多专家模型。

2026-09-23，[多专家缓存CPU入口与有限补查验收](research/cf_moa.md#multiexpert-request-preflight-20260923)已完成：242题原控制器首轮、484实际请求/3766个grammar及原parser正负fixture，独立39835项核验通过。补查另完成7固定输入/13场景/19槽及1409项独审，19条聚合均为合成响应，4个正向场景追加旧F后形成新audit并关门；初次compact空格fixture失败与unknown=1原记账保留。A1不可用提议不填补、不删分母，费用仅历史复用，0新模型/评分；不据此宣称协作收益或放行推理。[现有证据清单](research/cf_moa.md#freeze-evidence-inventory-20260923)补齐强旧/top-1绑定，整体仍未冻结，独立评测未开启。

2026-09-23，[简洁解释独立聚合候选](research/cf_moa.md#native-explanation-stability-20260923)双骨干smoke各6/6通过，扩展在M4 d00051重复解释截断后首错停止；完整242分母58完成/1失败/183未提交，59新聚合952561/23872 token，旧专家0重生成，GPU2已释放。[旧参考采样真实CPU回放](research/cf_moa.md#sampling-reference-replay-20260923)及5109项终检完成：M5 121完成，M4 63/1原截断/57未提交，0新模型。默认仍单专家，[实验A1缓存](research/cf_moa.md#multiexpert-cache-feasibility-20260923)仅CPU准备，A1/A5未采用、A3编辑暂停；尚无完整新方法开发成绩或协作增量。

2026-09-23，按最新请求[重放既定离线互补分析](research/cf_moa.md#complementarity-replay-20260923)：两骨干各121输入，13个结果制品与此前完成版逐字节一致，111个源及旧制品未变。强旧正确87/82、含未采用A1的离线上界90/86，仍不构成协作增量或采用证据。0新模型、0原生重评分，A3编辑模型继续暂停。

2026-09-23，[RU约束独立decoder](research/cf_moa.md#reason-codes-crossfield-decoder-20260923)：原逻辑v2 prompt/schema/parser保持，81项测试、484实际tokenizer请求/1210fixture及3894项独立CPU核验通过。两骨干固定GPU smoke各5/5，531项实际入口核验通过；10新聚合319573/5516token，0专家重生成。外部扩展守卫补齐并通过29项非评分回归，剩余116×2在GPU3首题M4 d00002重复解释并截断，1失败/231未提交，首错停止并释放；原10题保持，不评分失败批次。当前v2资源参考另已重绑定，[553旧采样映射](research/cf_moa.md#sampling-import-ledger-20260923)及10项回归/2566项核验完成，但durable导入未实现、旧失败与live门保持；A1/A5未采用、A2 parser待决、A3编辑暂停，尚无协作增量或独立评测。

2026-09-23，[原因码聚合v2](research/cf_moa.md#aggregation-reason-codes-v2-20260923)：129＋15项测试、484实际tokenizer请求/1210fixture通过；固定GPU2 smoke为3完成/1语义无效/6未提交，M4 d00018的RU与无冲突矛盾，669token完整JSON仍不可评分。4新聚合59040/1978token，首错停、引擎自动释放；独立live222及CPU3894项核验通过。新方法未过扩展门，前三旧聚合失败及原专家保持。另完成[完整分母与核心对照成本准备](research/cf_moa.md#control-resource-alignment-20260923)：839共享旧调用去重，同工具与双骨干采样仍不完整；新预算计划只准备、不执行，共同冻结和独立评测未开始。

2026-09-23，[紧凑聚合候选与纯top-1控制](research/cf_moa.md#aggregation-compact-decoder-20260922)：137项测试及484请求/726原parser fixture全开发实际tokenizer预检通过。固定GPU2 smoke为M4 5完成、M5 3完成/1截断/1未提交；9新聚合215955/7989token，首错停且GPU释放，M5仅完成53/58决策，未过扩展门，三个失败批次均保留。纯top-1另完成242输入/839旧回调及未改原生评分、0新模型：M4/M5正确87/82、与强旧汇总相同；完整保留原提议及partial身份。默认范围仍每题单专家，没有协作增量结论。A2 parser待处理、A3编辑暂停，共同冻结与独立评测未开始。

2026-09-22，[CF-MoA原型](research/cf_moa.md#a2-control-parser-difference-20260922)：A1 r5及A5不采用，真实旧F两骨干各121输入、合725请求完成。同工具r2两骨干停止结果保留。原A2/A3/A4不重跑；新增A2同事实控制2次smoke，M4通过，M5因新增严格parser包装与历史原生行为不同而停止，完整诊断及成本已存，扩展待用户处理决定。四项固定CPU对照已完成离线评分，原A2覆盖内各8/9，主要增益来自补全有效支持；小范围限制与成本见[机制对照记录](research/cf_moa.md#a2-fixed-cpu-controls-20260922)。A3默认关闭编辑臂的[四项准备缺陷](research/cf_moa.md#a3-edit-readiness-20260922)已完成[无模型限定修复](research/cf_moa.md#a3-edit-repair-20260922)：79项合并测试、242条默认输出回放、16条真实tokenizer CPU预检通过；原A3保持，编辑臂真实模型仍暂停。另完成[A3固定控制CPU准备](research/cf_moa.md#a3-fixed-control-preparation-20260922)：37项测试、726控制行及80条唯一score请求tokenizer检查通过，0新推理/评分。授权的[离线互补分析](research/cf_moa.md#complementarity-analysis-20260922)已完成：各121输入，强旧87/82、含未采用A1的离线上界90/86；A1在两旧控制联合之外仅新增2/1题，独立计数/成本/家族不确定性核对通过，0新模型。[A3配对执行器和冻结校验](research/cf_moa.md#a3-paired-execution-20260922)已完成CPU验收：64项测试、242输入流程与224实际tokenizer/grammar预检通过，当前未冻结。[Router与证据聚合CPU准备](research/cf_moa.md#router-aggregation-cpu-20260922)另完成67项测试、242输入/484真实tokenizer与grammar预检；默认三模式在当前范围均为同一单专家，未建立协作收益。后续[缓存衔接与固定聚合smoke](research/cf_moa.md#cached-prefix-aggregation-20260922)：242输入缓存流程通过；1次M4聚合真实调用出现跨字段合同无效，首错停、其余9输入未提交，旧专家0新生成。聚合候选未通过，失败完整保留。随后[显式解码候选与评分桥](research/cf_moa.md#aggregation-decoder-contract-20260922)完成125项合并测试/20实际tokenizer预检；新GPU2 smoke为3完成/1截断/6未提交，4新聚合调用59448/3820token，首错停且GPU自动释放。当前无本任务模型作业，A2 parser待处理、A3编辑暂停，独立评测未开启。

2026-09-20，按新增两个会话，将[实验全过程报告](research/support_update_experiment_report.md)扩展至R1–R5：原78阶段保留，新增R4 30阶段、R5 40阶段，共148节。补齐临床与结构失败、来源适配、生理模型冻结验证，以及R5旧F交付后的监督研发、负结果、两次平台中断和最终保存。R4为受限生理分支完成，R5论文方法目标仍未完成；CAD五头仅计划。本次只读核验与编写，0新模型调用/训练/积分。沿用[GitHub正文](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-16_support_update_method/docs/research/support_update_experiment_report.md)，发布核验见[工作区记录](workspace.md#support-update-r45-github-20260920)。

2026-09-18，按用户要求完成独立的[R1–R3实验全过程报告](research/support_update_experiment_report.md)：按实际R2→R3→R1顺序，以78个过程小节还原最初观察、分析、候选方案、每轮配置与中间结果、失败恢复、用户反馈、采用与放弃、冻结验证和后续回归，另述09-16交叉审计。它与前一份论文式论证稿分别承担过程回顾和方法论证；后续实验仍在各方向主记录续写。本次0新模型调用，正式结果与既有head保持。已同步[GitHub正文](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-16_support_update_method/docs/research/support_update_experiment_report.md)，提交与核验见[发布记录](workspace.md#support-update-process-github-20260918)。

2026-09-18，[R5面向论文方法的持续研发](research/r5_invariance_head.md#r5-task-supervised-results)：任务条件均值／映射差分及标量控制已完成两骨干训练、共同冻结、旧J/T评分及独立核验；均值头R5双正确31/40、36/40，强控11/16、13/16，但固定H变P诊断强控仅1/32、1/32，未采用、不进入D。此前支持审查、原句选择、旧开发训练、实体重呈现、范围隔离、裸P/H及DRiFt的失败／负结果均保留。迁移诊断及一次固定半径门／长度门回退均未通过条件、不采用；CAD来源与583族全审已完成，保留train246/dev134，新五头方案仅计划、尚无模型执行。按用户要求完成[含两次平台中断的对话与研究保存](research/r5_invariance_head.md#r5-conversation-preservation)，当前不推进新实验。128新母题＋8强控原生输入已就绪、NLI子集资格复核完成，仍0确认推理；旧组合保留作对照，持续目标未完成。

2026-09-18，[R5组合head已交付并完成验证](research/r5_invariance_head.md#r5-final-delivery)：NLI两路径×两映射等权，其他支持题型完整五票/三票早停。共1,312输入、5,032缓存回调通过，另24次真实回调通过；208 R5单元（开发与验证合计）双正确由历史60.19/59.17%升65.90/66.47%。新16组相对匹配单答两骨干各升6.25点，新8变答控制3/8、5/8→5/8、6/8。采用为原生分类决策研究版本，解释和文档纠错仍有限制。[论文定位审查](research/r5_invariance_head.md#r5-paper-method-assessment)支持作为受限组件，独立核心创新及统一跨类方法尚未建立。累计10,151新调用，全部运行结束，原停止过早及负结果保留，正式v5保持。

2026-09-17，[R4来源方法继续研究与最终验证](research/r4_consequence_head.md#r4-physiology-validation)完成：采用“给定生理模型与完整状态的局部干预后果head”作为受限医学R4分支。冻结后24profile/288题，两骨干head二元、联合数值和完整动作均288/288，同工具full联合数值270/222、动作263/213。1728新调用及1728实际入口回放完成，累计9930新生成/7085缓存回调；GPU0/1已释放。[代码与适用合同](research/r4_consequence_head.md#r4-physiology-method)可复现。原HIV失败、形式结果和正式v5保持，开放临床R4与跨模型泛化仍未验证。

2026-09-17后续，[R4第二轮已完成](research/r4_consequence_head.md#r4-binding-factorial)：患者绑定×后果/极性提示四臂共400次新生成、400请求回放及全部解释审核完成，GPU1两任务与分析均退出0。原13题redo/scope/outcome/组合为M4 7/5/6/8、M5 5/4/7/6，原答案均7，组合未采用。仅scope在明确规则24端由20/21升21/24，保留有限组件证据；患者污染、干预传播及极性问题未解决。诊断仅3个虚构基础世界，不是独立临床评测；正式v5与既有head保持。

2026-09-17，[R4后果推导head首轮已完成](research/r4_consequence_head.md)：指定三会话可读正文、R1/R2/R3主记录与运行失败附件全文复盘后，实现一次原骨干调用的后果/极性提示头。104新调用、52请求回放完成；原13题M4原答/普通重答/head为7/7/8，M5为7/4/4，反问诊断未改善，首版未采用、不扩七方法。作者解释的[来源核查](data/construction.md#r4-author-reference-audit)发现多种机制问题但未改gold。GPU0/1及分析全部结束，代码、负结果和阅读边界均已保存，正式v5保持。

2026-09-16，[R1–R3支持更新与候选重决策论证稿](research/support_update_method.md)完成：依据用户指定三会话的可读正文、三方向完整主记录及运行/失败文档，串联类别低分、错误机制、失败取舍、方法设计与实验依据，并参考三篇医学/反事实RAG论文的论证组织。该文承担跨方向论文叙述，原始实验历史仍在各自主记录续写；阅读范围与证据清单附于正文。本次0新模型调用，既有head及正式v5不变。已按用户要求[上传GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-16_support_update_method/docs/research/support_update_method.md)，范围与提交见[发布记录](workspace.md#support-update-github-20260916)。

2026-09-16，按用户纠正的对象完成[R2论文方法审查](research/r2_support_head.md#r2-paper-method-assessment)与[R3论文方法审查](research/r3_candidate_comparison.md#r3-paper-method-assessment)，R1仍由另一任务负责。R2支持有限问句范围/三值重算组件，固定事实范围消融两骨干24→48/48，补获最终版本局部强执行对照；总分与保留侧、独立临床缺口分开解释。R3公开目录重决策的七方法开发收益保留，但95.05%诊断修复起点是原评分无效，且CUPCase18记录上完整校正未优于单次/未校正，不能概括为稳定CF推理增强。本次为原始制品核验和CPU重算，0新模型调用；默认head与正式v5保持。

2026-09-16，[R1/R2交叉审计](research/optimization.md#r1-cross-head-evidence-audit)完成：R1 20062条与R2 553条当前入口缓存回放、正式基线和相关汇总一致，0新模型调用。R1开发收益保留且评分/组件贡献分开；[R2审计](research/r2_support_head.md#r2-cross-head-evidence-audit)补明130条修复均来自有效初答，但同覆盖常数None总分更高，保留侧与独立验证必须分别解释。另一会话的R1定向开发继续按下文主记录更新。

2026-09-16晚[R1定向开发270次新调用已完成](research/optimization.md#r1-postvalidation-refinement)，GPU与分析结束。旧facts＋限定问句组合使33端21→28、25→33；新facts两骨干及七方法真实R2回归均退步，未采用。广域删UNKNOWN暴露相互作用支持缺项；无目录单名诊断47例canonical4→27、20→22，进一步确认输出/评分归因。旧47/33全部作为已暴露开发，既有默认head与正式v5保持。

2026-09-16后续，[R1冻结后验证与归因对照全部完成](research/optimization.md#r1-frozen-validation-complete)：1660次新调用、630缓存回调，GPU及分析均结束。ASCENT47的冻结head与单次目录同为38/39题正确，原生自由答的目录未映射不能当医学错误；规则33端程序21/25优于同facts模型执行6/17，但独立临床病例缺口仍在。关系201普通重答→目标提示M4 102→118、M5 120→122，单种子增量在M4获得信号、M5未确认。结论支持有限组件，尚未建立泛用R1；全部失败、负结果与暴露沿革保留，既有R2/R3及正式v5保持。

2026-09-16，[R1主候选及完整回放](research/optimization.md#r1-core-head-delivery)已完成：全2866七方法原正确861/898/766/798/819/858/901，head为1329/1323/1260/1225/1367/1317/1331；旧R3复用和本轮新增贡献分别报告。独立入口20062输入、75264缓存回调一致。单选全202扩展未采用；[关系201问句族与成本收尾](research/optimization.md#r1-relation-extension-complete)也已完成，无旧答目标提示M4/M5为100→123、112→132，额外删除检索无一致增量，尚未加入完整七方法主候选。本轮47434次已记录新调用，全部本任务GPU与分析结束。原模型、实际输入、冻结评分及失败/中断证据保留，正式v5未改；结果属于已暴露开发。

当前v5的 **M0、M2、M3、新M4、M5、M6 MedGENIE和M7完整第二版均已完成**，每方法覆盖13,905个输入。最新比较见[v5评测主记录](/home/data3/txy/docs/evaluation/v5.md#current-seven-methods)。旧i-MedRAG和旧M7队列保留暂停状态。R2独立head实现及本轮938次新生成已完成，当前保留为开发候选：原79题均反复参与调优，尚无独立临床泛化验证；未发现最终推理直接查测试答案或训练病例标签的逻辑，详见[R2测试集复用核查](/home/data3/txy/docs/research/r2_support_head.md#r2-test-reuse-audit)。所选短提示正向事实提取＋问句范围＋三值支持重算通过553条结果/385条请求回放；原79题M0/M2/M3/M4/M5/M6/M7为29/23/43/39/46/38/37题正确（原7/6/27/23/33/15/23），来自两原骨干事实生成与七方法离线组合，M7保留题仍有退步。Llama范围探针40→48/48、Qwen48/48属于有限规则开发证据。所选版本、政策/常数控制、成本与失败见[当前R2交付](/home/data3/txy/docs/research/r2_support_head.md#r2-head-delivery)，正式v5未改。

v5有6,104个唯一比较单元、13,000个选中判断、每方法15,616条原生评分映射，类别可重叠。成员选择使用`evaluation_labels`，`labels`保留原分类语义。v3、v4及历史结果继续保留。已暴露v5可继续用作优化开发，方法价值由冻结后的独立评测判断，见[开发与泛化的共同标准](/home/data3/txy/docs/research/optimization.md#development-generalization-boundary)。

R3本轮寻找与交付目标已完成：原模型目录重决策头在七方法上取得共同提升，作为主要开发结果保留，见[最终交付与证据范围](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-head-delivery)。额外NLI及三批新来源验证均已收尾，当前无本任务GPU作业；更广泛的CF泛化尚未证明。此前最近训练病例标签直返头仍撤回核心方法候选定位，保留为有监督检索对照。其诊断开发124/128、确认535/552的实测结果保留，局限见[自我反驳与取舍](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-head-self-review)。全部阶段记录、负结果和接口继续保存在R3主记录，正式v5未改；下文历史进展按各阶段当时状态理解。

2026-09-15，R3[实际证据暂隐与原病例审计](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-process-restart)、多数门控及[三候选似然校正](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-likelihood-scout)未形成跨骨干净增益。[七方法同40题目录与重呈现对照](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-catalog-transfer)及[固定v1完整128题扩展](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-patient-selection-v1)均完成：M4/M5原30/24、同资源名称控制53/62、v1为59/64。重呈现增量较小、宏平均无两骨干一致改善，仅保留开发候选；编号/额外身份提示未选用。没有检索训练答案；本批GPU任务已结束，独立泛化范围仍待确定，R3目标未完成。

同日后续已取得CUPCase和ASCENT作为[新验证候选来源](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-generalization-source-selection)，完成ASCENT原生输入及病例分组检查。R3资格、跨来源重合和多诊断评分仍待处理；没有把新来源普通诊断题直接当作R3，也没有新增泛化分数。

R3后续[去历史/去资料及统一系统指令对照](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-context-selection)未采用。[目录分布与六排列校正](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-catalog-distribution)完成M4/M5各128题后，[七方法同40题比较](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-calibrated-transfer)又完成1,290新调用：新头M0/M2/M3/M4/M5/M6/M7为19/21/12/21/24/16/19，旧v1为18/22/10/21/19/19/20，不能统一替换或称差距已缩小。[对应40组参考端对照](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-paired-control-probe)也完成560新调用：M4/M5两端均正确分别从旧v1的15/17升至19/19，对匹配未校正多数票为17/18→19/19；M4有一对修复涉及旧v1输出截断，全部比较仍属同批暴露病例。GPU任务全部结束；ASCENT完成[仅train的目录兼容计数](/home/data3/txy/docs/data/construction.md#r3-ascent-qualification)，资格与原生评分继续准备，无独立泛化分数，R3目标未完成。

[患者与背景分布对比](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-patient-contrast)已完成960新调用：M4/M5同40组的变体正确16/21、两端均对15/17，均低于现有校正头；均匀背景控制和160端点接口回放也已完成。本版本未采用，GPU任务全部结束，原候选保持，R3目标继续进行。

[四候选双向比较与等调用列表控制](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-pairwise-comparison)已完成1,920新调用。M4/M5两两比较19/21，列表19/20，均低于现有校正头21/24；覆盖内错题多数存在双向一致选错，未采用，全部GPU任务结束。后续[原文观察块选择](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-evidence-selection)也完成776新调用：区分性臂M4/M5为19/24，一般臂18/24，现有校正21/24；M4的1题表面增量来自无效选择回退。未采用，两原骨干接口回放通过，全部GPU任务已结束，仍无独立泛化分数。

[独立逐候选核验](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-pointwise-verification)完成1,280新调用：M4/M5主要诊断核验19/20，相容性18/17，现有校正21/24（均同40题）。收紧核验目标有局部增量，整体未达采用条件；接口回放通过，GPU任务全部结束，后续检查候选知识供给。

[同池医学资料分配](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-candidate-knowledge-allocation)也完成1,280新调用：M4/M5原资料列表18/20、总体相关性新资料10/18、候选均分新资料7/16（各40题），两个策略均未采用。接口回放通过，全部本批GPU任务结束。正文核查发现学习目标、通用诊断介绍占据部分高排位资料，资料均分没有保证实际鉴别知识；内容与查询修正尚待新实验，R3目标未完成。

## 从哪里开始、往哪里记录

最新完成：[NLI对照与补跑](research/r3_candidate_comparison.md#r3-fact-nli)未采用；[第三批冻结验证](research/r3_candidate_comparison.md#r3-cupcase-validation)384次成功新评分、72次缓存回调完成。head和字符归一对照两骨干均6/6；三批累计18记录，Llama/Qwen校正15/16、字符归一15/14、未校正16/17，尚无稳定校正增量。64组资格、53组未建立比较及5组参考问题归[构建记录](data/construction.md#r3-cupcase-validation-qualification)。全部失败、恢复和负结果保留，本轮GPU及分析均结束，七方法主要开发成果及正式v5不变。

此前完成：[事实字段说明、约束解码与R2式接口迁移](research/r3_candidate_comparison.md#r3-fact-scope-factorial)两轮144新调用。显式字段有局部改善，但关闭约束不改判断内容；24探针三值/句ID迁移M4/M5为15/18，显式控制17/15，未形成双骨干提升，停止扩大该版。M4显存失败已恢复，全部GPU和分析结束；新NLI文献的流程线索及不适用假设已记录，现有校正候选及正式v5不变，R3目标继续活动。

此前完成：[原模型事实提取与训练统计知识比较](research/r3_candidate_comparison.md#r3-empirical-feature-head)3092新调用、12800缓存回调。M4/M5统计臂12/15、修正模型综合21/18，现有校正21/24（各40题），不采用。观察到事实主体/否定误读，以及训练生成器的结构零频率惩罚CF保留背景；完整失败、调度恢复和引用修正均已保存。本批GPU与分析结束，R3目标继续活动。

最新完成：[疾病名称绑定与逐候选关系接口](research/r3_candidate_comparison.md#r3-bound-evidence-relations)6,410新调用、13,300缓存回调。names模型综合M4/M5为19/18，single为18/22（各40题），低于现有校正21/24；顺序敏感与无事实标题误判仍存在，均不采用。四个模型任务与分析已结束；原队列保留初次M4初始化失败，恢复队列退出0，健康M5未重跑。R3目标仍在进行。

最新完成：[局部关系输入及代码映射对照](research/r3_candidate_comparison.md#r3-local-evidence-relations)共1,474新调用、3,428缓存回调。局部输入降低标题误判但没有跨骨干诊断收益；交换任意代码使M4的28/40个固定观察关系表改变，关系绑定仍需修正。本批GPU3两队列和分析均退出0，尚未采用新头，R3目标继续活动。

最新完成：[逐观察关系判断与显式汇总](research/r3_candidate_comparison.md#r3-evidence-relations)1,394新调用与3,428缓存回调，两个新臂未优于现有校正头。发现无患者事实的标题也被判为诊断支持；关系范围约束及计数假设需继续研究。运行参数冲突已恢复并保留失败证据，本批GPU和分析全部结束，仍是开发结果，R3目标未完成。

最新完成：[下一批CUPCase64组资格审核](data/construction.md#r3-cupcase-expansion-qualification)固定8个新记录，[冻结流程扩展](research/r3_candidate_comparison.md#r3-cupcase-expansion)512新评分和96次缓存回调完成，GPU2/3队列及分析退出0。Llama/Qwen校正head分别5/8、6/8，字符归一对照6/8、5/8，单次判断5/8、8/8，未校正6/8、7/8；校正两骨干均比未校正少对1题，不支持稳定泛化收益。原四例与本批分别报告，保留Qwen亚型翻转及Llama平票退步证据；不按本批成绩拼接骨干策略，R3目标未完成。

最新适配：[CUPCase统一格式对照](research/r3_candidate_comparison.md#r3-cupcase-option-style)再完成24新评分＋8同请求复用，原两开发例Qwen表面head增量消失。冻结后剩余28例[审核完成](data/construction.md#r3-cupcase-frozen-qualification)：纳入4个自然诊断更新记录、23例未建立原生候选比较、1例源标签错误。[四记录评测](research/r3_candidate_comparison.md#r3-cupcase-frozen-subset)256新评分与48次缓存回调完成：两原骨干head均4/4、字符归一对照均3/4，但只修复同一个病例；单次选择也4/4，Llama总似然4/4、Qwen无患者先验3/4。初步新来源成绩不能证明投票/校正增量、七方法或CF配对泛化，R3目标继续活动；本批GPU与分析全部退出0。

最新完成：[七方法完整比较及733题独立包回放](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-calibrated-all-methods)，18,714新评分，另486个同请求复用；本批GPU及自动分析进程全部退出0。完整733题原正确131/181/63/223/185/157/212，head为338/340/238/386/443/305/349。独立包28,630次缓存回调通过；680诊断题方法差距由25.0扩大到30.3个百分点，投票/校正并非跨方法一致改善，平均概率事后控制亦未采用。正式v5不变，仍无独立泛化新成绩。CUPCase16例结构审核与暴露归[构建记录](/home/data3/txy/docs/data/construction.md#r3-ascent-qualification)。

此前完成：[M4/M5冻结头扩展](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-calibrated-expansion)6624次新评分。全部680诊断题原答案203/160、单次目录339/382、未校正多数票359/402、校正359/410；校正对552扩展部分为−2/+5，宏平均改善而方法差距未缩小。接口及旧开发预测复核通过，该批GPU任务结束。

此前完成：[通用鉴别条件先生成](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-general-criteria)777次新调用，M4/M5同40题names_only为17/21、case_visible为16/23，现有校正21/24；未采用。Qwen两次知识输出截断及实际回退已记录，1752次缓存接口回调通过，相关GPU任务结束。

此前[反向病例似然](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-channel-likelihood)640次新评分，M4/M5同40题channel为1/11、同资源direct为20/18，现有校正21/24；两骨干均未达采用条件。1600次缓存接口回调及逐行分数分解完成，无新独立泛化分数。

此前[分项判断汇总](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-option-aggregation)72新调用未采用；[冻结R2规则接口向R3用药题迁移](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-frozen-rule-transfer)40新调用形成子分支开发候选。七方法原10题正确1/3/4/3/2/1/3，head后10/10/8/10/10/10/8；3题与R2开发重合，其余7题各方法均7/7，仍属已暴露同来源范围。只有两原骨干的新事实/控制调用，七方法结果为原答案离线组合。接口回放及同事实执行对照完成；一般诊断、单选及独立泛化仍未解决。

此前[原生选项列表延迟呈现](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-delayed-options)180新调用及纯接口回放均完成。M4/M5原答案9/8、延迟选项7/8（各18题），没有跨骨干收益；事后双路径一致门控10/7也未采用。全部本批GPU任务结束，失败和过程实例保留。

此前完成：[医学资料效用筛选](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-knowledge-utility)3,840新评分，M4/M5主题筛选18/22、临床事实筛选18/21（各40题），均未优于现有校正21/24，未采用。已知学习目标段落大幅减少，接口回放通过，本批GPU任务全部结束。[原生选项R3分支](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-native-option-scope)的范围与AMQA原文复核已用于上述延迟选项试验；该分支不替代诊断分支与泛化任务。

记录范围、续写归属、新建/拆分文档及目录扩展的规则统一维护在
[根AGENTS的范围与归属标准](/home/data3/txy/AGENTS.md#documentation-scope)和
[新建与扩展标准](/home/data3/txy/AGENTS.md#documentation-growth)。新增内容先判断研究对象、
问题、阶段和版本，再选下表中的主记录；初次迁移的22份主文档不是扩展上限，R2、R3现已按独立研究主题拆出。

先读与本次工作相关的主文档最新状态和章节，再实施并及时续写。方法实现、配置变化、成功、失败、负结果、暂停、结果和证据都是交付的一部分。日期写在文档内部，不因新日期、任务或重试新建总结。同一事实只有一个主记录，其他位置写摘要并链接。

| 内容 | 主文档 | 负责的内容 |
|---|---|---|
| 英文会议论文 | [LaTeX 主稿](paper/latex/main.tex) · [编译 PDF](paper/latex/main.pdf) | 直接维护 .tex：七基线、七系统 R1–R3 head 与后期双配置完整 v5；旧稿冻结，负结果与证据边界保留 |
| 论文框架与证据 | [outline.md](paper/outline.md) · [LaTeX框架](paper/latex/framework.tex) | 数据收集、五类体系、benchmark、七系统诊断与五agent CF-MoA完整逻辑及证据选择 |
| 论文写作与交付 | [writing_record.md](paper/writing_record.md) | 写作 skill 选择、版本、引用/事实审查、制图与导出验证；不复制实验运行历史 |
| 工作区与文档管理 | [workspace.md](/home/data3/txy/docs/workspace.md) | 实际路径、共享环境与接口、发布、历史合并及目录决策 |
| 数据来源 | [sources.md](/home/data3/txy/docs/data/sources.md) | 来源编号、获取状态、任务与本地资源 |
| 分类规则 | [classification.md](/home/data3/txy/docs/data/classification.md) | R1–R5定义、实例、边界与规则修订 |
| 数据构建 | [construction.md](/home/data3/txy/docs/data/construction.md) | 收集审核、资格、抽样、v2→v5沿革及历史数据暴露 |
| 直接回答与初始检索 | [direct_retrieval.md](/home/data3/txy/docs/baselines/direct_retrieval.md) | M0/M1方法、运行与复用 |
| MedRGAG | [medrgag.md](/home/data3/txy/docs/baselines/medrgag.md) | M2完整all-Llama流程与适配 |
| MA-RAG | [marag.md](/home/data3/txy/docs/baselines/marag.md) | M3原生流程、接口、失败与性能调整 |
| MedRAG | [medrag.md](/home/data3/txy/docs/baselines/medrag.md) | M4/M5接入、历史RRF、v5配置及结构输出修复 |
| i-MedRAG | [imedrag.md](/home/data3/txy/docs/baselines/imedrag.md) | 历史M6，多轮追问、formatter、成本和暂停 |
| MedGENIE | [medgenie.md](/home/data3/txy/docs/baselines/medgenie.md) | 当前M6，替代决策、适配、试跑和全量 |
| TC-RAG | [tcrag.md](/home/data3/txy/docs/baselines/tcrag.md) | M7状态/熵/控制流程、修复、消融与正式运行 |
| 统一协议 | [protocol.md](/home/data3/txy/docs/evaluation/protocol.md) | 输入与证据权限、评分、分母、复用及比较规则 |
| v5比较 | [v5.md](/home/data3/txy/docs/evaluation/v5.md) | 跨方法进度、版本选择、正式结果表图与结论 |
| 优化研究总览 | [optimization.md](/home/data3/txy/docs/research/optimization.md) | 文献取舍、跨类误差诊断、其他head构建经验与尚未独立成篇的探索 |
| CF-MoA系统原型 | [cf_moa.md](/home/data3/txy/docs/research/cf_moa.md) | 旧版本锁定、统一合同、五专家互补、路由聚合、资源匹配对照及冻结评测；已有单head历史继续在各自主记录 |
| CF-MoA全过程报告 | [cf_moa_experiment_report.md](/home/data3/txy/docs/research/cf_moa_experiment_report.md) | 用户要求的截至09-23过程回顾：全阶段完成表、问题与错误、处理方案、负结果、成本和未完成范围；不替代持续主记录 |
| R1–R3方法论证稿 | [support_update_method.md](/home/data3/txy/docs/research/support_update_method.md) | 面向论文写作的跨方向逻辑：类别表现、原因证据、失败取舍、支持重算与候选重决策、组件归因及研究主张；运行历史链接原主记录 |
| R1–R5实验全过程报告 | [support_update_experiment_report.md](/home/data3/txy/docs/research/support_update_experiment_report.md) | 截至09-18保存的跨方向回顾：148阶段的观察、决策、配置、失败恢复、优化与阶段交付；R4受限完成、R5论文目标未完成；不另建持续运行日志 |
| R2支持重算head | [r2_support_head.md](/home/data3/txy/docs/research/r2_support_head.md) | [执行指南与七方法验证范围](/home/data3/txy/docs/research/r2_support_head.md#r2-execution-guide)、独立接口、版本与成功路径、全部失败/未采用试验、跨方法结果和复现证据 |
| R3候选比较与独立head | [r3_candidate_comparison.md](/home/data3/txy/docs/research/r3_candidate_comparison.md) | 独立接口、证据审计/查询、公开目录约束、历史病例记忆、开发与确认结果、来源控制、反例及负结果 |
| R4后果推导head | [r4_consequence_head.md](/home/data3/txy/docs/research/r4_consequence_head.md) | 历史与失败复盘、原临床负结果、结构/形式/生物与来源适配、生理模型局部干预及冻结后验证 |
| R5目标保持head | [r5_invariance_head.md](/home/data3/txy/docs/research/r5_invariance_head.md) | 历史失败复盘、具体目标保持、旧组合F交付、后续监督研发负结果、平台中断及未完成交接 |

方法文件采用稳定名称，编号按实验版本解释：M1是MedRGAG初始检索对照，不是独立MedRAG；M6于2026-09-14改为MedGENIE，旧i-MedRAG结果不改名。M4/M5目前同时存在骨干和输出协议差异，跨方法差值不能都归因于算法。

## 历史研究与结果

| 历史方向 | 主记录 |
|---|---|
| 早期Direct、Table 1、all-Llama v15复现 | [medrgag_reproduction.md](/home/data3/txy/docs/archive/medrgag_reproduction.md) |
| 原始WM代理、盲审与停止结论 | [wm_medrgag.md](/home/data3/txy/docs/archive/wm_medrgag.md) |
| CF-WM Gate、无效oracle、修正版负结果 | [cf_wm.md](/home/data3/txy/docs/archive/cf_wm.md) |
| DeltaRev、DeltaRank、CFShift、CF-KADS-MoE、RiskRoute | [cf_method_trials.md](/home/data3/txy/docs/archive/cf_method_trials.md) |
| CF-Residual Adapter、MA-RAG迁移与消融 | [cf_residual_adapter.md](/home/data3/txy/docs/archive/cf_residual_adapter.md) |
| 原生来源筛选、M2全量和M0/M1/M2比较 | [native_baseline_screening.md](/home/data3/txy/docs/archive/native_baseline_screening.md) |
| 早期R1–R4、旧rubric、v2/v3评测 | [r1_r5_early_evaluation.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md) |

## 文档和运行证据的位置

长期过程与分析主记录统一在`/home/data3/txy/docs/`。`Documents/Codex/日期/`保留代码、数据、运行包、配置、日志、预测、评分、图表及冻结报告；运行包README可以维护本包命令和制品导航，并链接对应主记录。不要在那里再建立承担持续研究叙述的新主文档。

`MedRGAG/`、`MA-RAG/`、`MedRAG-upstream/`、`models/`及既有CF代码目录继续在原位置。可复现命令使用各记录明确的原工作目录，不能在docs目录直接执行其中相对路径命令。

2026-09-14初次迁移建立22份主文档并迁入实际历史正文，章节带来源和证据链接。旧过程文档作为归档或跳转入口，原始制品与Git发布快照保留。详情及完整原文备份见[2026-09-14迁移记录](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)。
