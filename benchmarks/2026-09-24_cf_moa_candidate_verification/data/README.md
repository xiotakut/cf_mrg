# 候选验证效果实验：公开数据与trace元数据

这是2026-09-24已完成实验的发布投影，不是新增模型实验。本次导出0模型调用、0原生评分、0旧head回放。全部40个面板×骨干×实验臂结果保留历史121／自然52完整分母。

- `quality_summary.json`：40组完整结果，含原生ALL/类别单元、辅助检测、候选池覆盖与选择率、修复/误伤、母题/来源/格式分层及逐配对/区间。旧普通重答三seed全部保留。
- `cost_summary.json`：每个方法继承一次已付B/F成本，另列追加计算；不能跨臂累加继承成本来声称本轮物理花费。
- `per_input_status.jsonl` / `.csv`：3460行完整逐输入状态；`native_scoring_metadata.jsonl`：4180条原生评分映射。只保留现成评分与状态，不包含答案正文或gold。
- `model_call_metadata.jsonl`：780次真实score调用的请求哈希、实际engine/sampling参数、完成状态、A/B logprobs、token与耗时。实际消息、检索原文、渲染prompt、原始返回与token序列不公开；哈希不等于这些原内容已发布。采样token-ID列表仅保留哈希。
- `candidate_selection_metadata.jsonl`：190条执行输出（176候选选择、14 NLI原F直返），全候选键、两次交换编码分数、选中索引、原响应哈希与成本。选中完整原生对象保存在服务器私有trace，不在此文件中。
- `prior_initialization_failures.jsonl`：原GPU0批32次初始化失败，0成功计算/0token；473.925秒初始化墙时见`decision.json`。8条旧smoke回退没有改名成新验证成功。
- `prior_semantic_review_metadata.jsonl`：31个旧修复/误伤独立组、93个三seed结果与非互斥原因类别；原文引文留私有记录，不是医学独立复判。
- `fixed_smoke_counterexample_metadata.jsonl`：4个事先固定smoke反例的短机制摘要与分数；26条原文位置已在私有trace核验。其成本属于本次780调用，不额外累加；反例不代替完整面板估计。
- `decision.json`：两臂暂不默认采用的结论；`analysis_receipt_metadata.json`：已完成评分的来源、数量和完整终态。
- `engine_interface_normalization.json`：发布核对发现780条请求的包装`output_kind=0`在实际vLLM入口统一变为`2`。本地`vllm/entrypoints/llm.py:1350`明确在engine提交前设置`FINAL_ONLY`，`sampling_params.py:113`定义0为CUMULATIVE、2为FINAL_ONLY；这是仅返回最终结果的接口模式，其余实际采样字段逐项一致。没有将整个sampling对象声称为逐字段完全一致，原历史验收收据不改写。
- `source_manifest.json`：准确来源文件SHA/字节数、投影字段、公开制品SHA；`verification_receipt.json`：导出一致性收据。

**public metadata != full trace。** 当前题面、选项文本、模型真实messages、检索上下文、理由、原始输出、完整原生响应、gold及SQLite仍在服务器。公开文件足以复核计数、费用、状态与已保存指标，不足以独立重做医学语义评分。固定公共提示源码由上层`source_snapshot/`提供，不因数据隐藏病例全文而删掉公共提示。

两臂新增780次真实取分，5,504,408输入token、780输出token；未重跑旧F或补造早停票。旧初始化失败与新成功批次分列。默认旧B不变；带理由臂开发有增益，但自然M5原生单元均分及自然保持配对仍有退步，不能称稳定泛化。

从本数据目录运行独立公开一致性验证：`python3 verify_public_data.py`；或从发布包根目录运行`python3 data/verify_public_data.py --data-dir data`。只需Python标准库，不读取私有目录、不运行模型或grader。
