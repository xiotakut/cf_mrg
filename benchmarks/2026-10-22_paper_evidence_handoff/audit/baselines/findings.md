> 轻量阅读副本：下文“本包”、原路径和历史核查状态按完整交接包的范围理解。本轻量目录真正交付哪些文件，以根目录 `EVIDENCE_INDEX.csv` 和 `SELECTION_AND_VALIDATION.json` 为准；缺少的层不能视为已经取得。

# 七系统基线证据审计（2026-10-22）

2026-10-23重建说明：原交接包因data3空间不足被用户删除，本文件从原会话保存的创建内容与修正恢复，以下2026-10-22数量、字节数和整理过程属于历史记录。当前data4重建的执行、计数与验证见`../rebuild/baselines_heads/rebuild_status.json`；压缩容器的时间戳/字节数可以不同，源身份与解码内容重新核验。旧导出器失败证据见`../rebuild/baselines_heads/historical_export_failures.json`；本次没有重演已经修正的错误，也没有新模型调用或评分。

此文件记录服务器实物审计，不以论文、底稿或旧总结作为完成证明。只读取既存文件、核对ID/哈希、汇总保存的`correct`；没有启动模型、评分器或生成新预测。当前GitHub逐文件差异由主审计合并。本文件的原路径是溯源标识，交付情况必须查总`FILE_MANIFEST.csv`，不能把服务器路径当作已交付。

## 可直接支持的结果

`coverage_and_reaggregation.json`与`recomputed_category_scores.csv`记录7×6＝42个数值核对。每系统保存的15,616条评分`record_id`均唯一，并全部能连接共用`evaluation.jsonl`；13,905个预测`item_id`零缺失、零重键，并全部连接共用`items.jsonl`。42格从已保存`correct`重汇总，均与最终七方法`category_comparison.csv`完整精度相差小于1e-10，论文两位小数一致。这支持**既存评分规则下已暴露v5范围的描述性比较**，不独立担保评分规则正确或模型输出医学正确。

- 评分：每方法6,818条`role=reference`不纳入主均值；8,798条非参考映射先在单元内均值，再对6,104唯一单元等权。类别使用`evaluation_labels`，允许重叠。R1/R2/R3/R4/R5分母＝2,866/79/733/13/3,600。不能把13,905输入、15,616映射或13,000选定judgments作为ALL分母，也不能加总类别分母。
- 不可用输出：保留原评分中的`invalid`及`correct=false`，没有删掉无效记录；未对答案再解析或重新判定。原生评分无效映射M0/M2/M3/M4/M5/M6/M7分别2,784/3,135/3,456/2,871/3,858/3,156/3,023（分母各15,616，包含参考）。这不等于推理进程失败数，也不等于协议JSON无效数。
- 最终ALL百分比：M0 48.10，M2 48.81，M3 51.61，M4结构修复版48.20，M5 47.35，M6 MedGENIE 48.02，M7 typed第二版49.43。完整精度见CSV，当前核查未发现这42格实质冲突。
- 汇总规则依据是实际保存的`code/analyze_v5.py`中排除reference、按`(unit_id,category,method)`分桶的代码；本次独立脚本不调用它或其评分依赖。`scripts/baselines/reaggregate_scores.py`通过总manifest支持离开服务器只用交接包重汇总。

## 实际运行与版本边界

主结果路径：

| 系统 | 实际预测 | 实际评分 | 版本可核实范围 |
|---|---|---|---|
| M0 | `Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/M0/predictions.jsonl`＋`cache/reused.jsonl` | 同包`scored.jsonl`筛`method=M0` | 保存提示/采样/原答；生成与评分运行时完整代码版本未核实 |
| M2 | 同包`M2/predictions.jsonl`＋`cache/reused.jsonl` | 同包`scored.jsonl`筛`method=M2` | runtime config记录baseline_source `1e01b3a`，并不能独立证明全部运行时本地修改；运行时版本未核实 |
| M3 | `.../2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/m3_predictions.jsonl` | 同包`scored.jsonl` | config保存上游commit `423f031cc0ffca679a047c885be999b9604100a9`；不能代替本地runner实际哈希；运行时版本未核实 |
| M4 | `.../2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/M4/predictions.jsonl` | 同包`scores/scored.jsonl` | 实际输出标记`implementation=structured_fix_20260913`、gpu-ready配置和实际messages/schema保留；未找到覆盖全部运行依赖的运行时哈希 |
| M5 | 09-11共用包`M5/predictions.jsonl` | 共用`scored.jsonl`筛`method=M5` | 原输出协议，不与新M4误写为只换模型；运行时版本未核实 |
| M6 | `.../2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/reports/predictions.jsonl` | 同包`scores/scored.jsonl` | 109份`runs/chunk_*/resolved_config.json`；每个code_hash匹配当前文件或该run代码快照，全部13,905结果config/input hash匹配；评分器运行时哈希未核实 |
| M7 | 同根`m7_typed_v5_full/reports/predictions.jsonl` | 同包`scores/scored.jsonl` | 109份resolved_config，全部code_hash匹配当前相应代码；13,905结果config/input hash匹配；评分器运行时哈希未核实 |

上表省略前缀均为`/home/data3/txy`。`runtime_versions.json`逐分片给出记录SHA、当前匹配、快照匹配、输入文件匹配；它是绑定证据。不能把本次SHA或当前Git HEAD反推成早期运行的代码版本。M6/M7生成哈希被绑定，并不意味着其未列入哈希表的全部外部依赖、语料或评分器也已逐字验证。

M0保存新输出5,028＋复用8,877；M2新7,218＋复用6,687；M3合并文件13,905，其中`reused_from`明确标记3,690，新增10,215。M4/M5最终文件均13,905；M6/M7最终文件各13,905，保存`reused_stage_requests`总计0。M6保存`costs.llm_requests`之和83,430；M7为89,341，此为既存收据计数，不是本次调用。M6的6次/题表示5背景＋1答案的逻辑生成输出，实际backend_generate_calls总计27,810（2批/题）；M7 backend_generate_calls=89,341、retrieval_requests=27,578。M6的27,810个requests文件和M7的116,919个含检索requests文件不能直接当相同口径的模型调用数。不能把恢复分片、缓存回调、文件复制和旧试跑另计作新正式输入。

### 特别需要避免的原始记录误称

M3全部13,905行`raw_response`的`output_kind`是`native_scorer_serialization_of_final_vote`。这是最终投票答案供原生评分的序列化，**不是模型原始响应**。真正模型文本、8候选/多轮消息、查询与检索保存在每行`source_run`＋`raw_candidates`所指`cache/items/<item_id>/`。本次导出选取每个最终item的实际源目录，包括复用v3目录、`runtime_invalid`、`vote_tie`和`invalid_answer`，没有按成功筛选。M3最终状态complete=13,564、vote_tie=135、runtime_invalid=18、invalid_answer=188。

M6/M7预测文件是终态与成本收据，完整实际messages/raw文本来自`requests`。M6生成背景也在收据中，不是外部检索；M7收据包括LLM与retrieval请求。`score/*.jsonl`是评分元数据，不能代替上述原始响应/提示/检索材料。

## 额外主动发现的历史、失败和未采用运行

`history_inventory.json`是从实际预测/配置/状态扫描得到的34条历史逻辑记录；加7条最终运行共41条registry记录。不是所有目录都应算作独立实验；其中old_formal将formal→formal_fast→formal_balanced视为同一恢复链。

- 旧M4完整13,905输出与两个100输入format/structured pilot存在，最终采用的结构修复版另列。原生parser和输出协议改变属于实现变更，不能只把差异归因于Llama/Qwen骨干。旧RRF 100输入计划实际`plan.json`明确`inference_started=false`、`status=blocked_missing_retrieval_indexes`，因此可标“仅计划未执行”；这不是由文件缺失推断。
- 历史M6 i-MedRAG仍保留：dev 24条、dev_accepted 24条、dev_final 24条、v1 1条、v3 1条failed、v4 24条。`imedrag_dev_v2`没有合并预测终态，但实际`items/*/requests`和`events`存在，必须标“部分执行，缺终态”，不能标未执行。`superseded_development_pilot.json`及代码快照仍在。
- `optimization_vllm/runs/m6_vllm_128/predictions.jsonl`有128条**全部failed**，原错误`RuntimeError: vLLM engine failed`；后来`m6_vllm_128_mem70`保存128终态（102 ok/26 invalid）。这是失败→恢复记录，不是两个成功128输入实验，不得只报告后者。
- MedGENIE dev_v1/dev_v2各24条；v1背景提示把completion示例置于单user消息后出现示例重答，v2改变聊天轮映射（决策记录见`docs/baselines/medgenie.md`“首次试跑完成与提示适配修复”；实际两版snapshots/predictions保存）。format_smoke_v2 3条含1 invalid，multifix版3条ok；完整试跑384条（371 ok/13 invalid），再到最终13905。开发/格式试跑同最终来源重合，不能当独立确认。
- TC-RAG typed与recovery-only同384输入试跑均有完整终态。typed 366 ok/18 invalid；recovery-only 269 ok/115 invalid。实际`reports/paired_comparison.json`、`native_validity_rows.jsonl`、输入和配置保留。typed作为当前方法的选择记录见`docs/baselines/tcrag.md#record-0171`；这个选择参考开发/同题结果，不是独立测试选择。
- `m7_recovery_only_fresh/runs/gpu2`初始化失败、没有终态；`reports/gpu2_launch_failure.json`和日志记录KV-cache OOM，原128输入在`runs/gpu2_retry`下物理GPU0完成。文件名gpu2不能当实际GPU证明；不把失败初始目录解释为整个组没做。
- 原i-MedRAG正式链`formal_balanced`有40新终态＋状态记录明确12复用＝52/13905；原M7最终暂停checkpoint有1,646条（1,026 ok/620 invalid；12复用），不混入typed新全量。旧`logs/status.json`只到1,633，是较早轮询，不覆盖后来的1,646 checkpoint。
- `m6_current`、`m7_current`是符号链接，不是独立实验。当前前者指MedGENIE full，后者指typed 384 pilot方法入口；论文主结果应指显式full目录，不能按“current”名推定full证据。
- 历史M1是初始检索控制，不是独立MedRAG。现有原生全量M0/M1/M2、R1–R4、v3 M2与v3 M3历史文件保留在registry；它们是旧数据版本/当前复用来源，不增加当前v5独立验证样本。

## 有证据支持的方法事实与取舍

1. 正式七配置来自六方法家族。M4/M5同MedRAG家族且本次有输出协议差异；主表是配置比较，不是七个纯算法隔离实验。
2. M2实际配置`m2_runtime/config.json`保留初始5文档、3知识点、5生成文档、10 KADS候选、最终5文档，使用all-Llama。其stage JSONL和prompt_ref连接阶段；是否当时与GitHub上全部源文件逐字相同仍未核实。
3. M3实际`config.json`：Qwen3-8B，8候选，最多4轮，solver temperature0.7/max_tokens2048/thinkingfalse；query temperature0/max_tokens8192/thinkingtrue；唯一最高投票获胜、平票无效；分歧触发检索，MedCorp3（pubmed/textbooks/wikipedia），BM25 total_k32、MedCPT top_k2。保存的缓存可核对实际消息，方法名不能代替这些事实。
4. M4结构修复的gpu-ready配置明确`explicit output contract + visible-input JSON Schema/xgrammar`，复用旧M4实际检索证据、prediction_reuse=0、生成2048、温度0.7、seed42。M5保留原始输出协议，二者差值不能归因于单一骨干因素。
5. M6实际resolved_config：`method_version=medgenie-llama31-v5-v2`，Llama3.1-8B generator和reader，3个option-focused＋2个option-free，有选项时分支；无选项5个free，生成0.9/frequency_penalty1.95/512，reader greedy/2048；upstream_commit `6ccff62c19e0a51447263e487efac4521f49259a`，本地接口适配保留。它不是原论文PMC-LLaMA权重的数值复现。改换M6身份是替代决策，历史i-MedRAG不改名。
6. M7实际resolved_config与methods：Qwen3-8B、关闭thinking，8步、topK4、sigma1.2，FP32全词表熵，typed控制/预算提醒/确定性已接受答案表示转换。选择typed而非仅异常恢复有同384题试跑记录，组合增益不能反推各反馈独立因果贡献。
7. 评分实现保存固定canonical诊断匹配与结构映射；未映射诊断被原记录计错。该评分可能包含医学错误、同义词、粒度/多诊断差异，当前只核对保存分数，不能未经复判把“unmapped”全部解释成格式错误或全部医学错误。

## 独立性和限定

v5中部分输入参与格式开发、参数/方法选择及早期运行。M6/M7`reports/exposure_strata.json`是已有暴露记录的排除分层，文件本身注明不是独立构造的untouched test；这不建立独立确认。七基线本身的当前结果可报告，不能用“outside_recorded_prior_runs”推导无暴露的独立验证。CF-MoA共同冻结/独立F复本等结论由相应主审计单独核对，本子审计不据基线结果推定执行。

## 文件交付、导出和未核实范围

`evidence/exports/baselines`的导出目标是保留实际prompt、模型原始文本和必要检索正文，覆盖所有所选v5样本及已保存状态。为了体积，原始token ID/logprob/逐token entropy向量不进入派生导出；剔除键和次数详见`export_manifest.json`。这些原向量文件属于**仅索引，尚未交付完整原文件**，需要按源路径和SHA取得服务器原件。M6/M7完整events/attempts也不自动等于request导出；方法决策可查保存的源代码/终态与关键历史日志，完整逐步state-stack/技术重试重放仍需原events/attempts。

原始请求文件的交付表示为保留字段的JSON导出，源SHA指原文件字节；转换只进行JSON读取、长字符串内容寻址与明确token向量删除，没有修改实际消息/模型文本/已存评分。各保留JSON值已在导出时解码相等验证。不要声称剔除向量后的导出可恢复原文件每个字节。最终文件数量、完成状态和映射以`export_manifest.json`、`source_exports.json.gz`及总manifest为准。

检查范围：用`rg --files`对`/home/data3/txy/Documents/Codex`、`MedRGAG`、`MA-RAG`、`MedRAG-upstream`盘点（默认遵循rg忽略规则，排除权重/二进制/Parquet/PDF/图像/ZIP/TAR等扩展）得914,332路径；再对09-11/09-12/09-13实际基线目录和08-23历史CF结果目录做定向读取，读取各`docs/baselines/`记录寻找版本/取舍线索。本审计没有逐字审阅所有914,332文件；未找到均仅指上述相关目录和文件模式，不能声称全服务器不存在。模型权重、全语料索引及所有早期普通医学QA轨迹未复制，也未由本审计单独检验。

## 本次交接整理的最终导出与工具修正（不属于实验）

已导出308,953个源文件中的757,363条范围内记录，原文件总大小14,871,307,725字节（某些来源JSONL按v5样本范围导出，不表示全文件所有样本均复制）。最终`records.jsonl.zst`98,308,274字节、`text_blobs.jsonl.zst`349,634,691字节，合447,942,965字节。源索引保存原路径、原SHA、原字节数、包含/范围外记录数；不能把本次源文件计数当独立运行数、样本数或模型调用数。

本次整理保留三项工具过程：首次gzip导出达到440MiB护栏后暂停在完整源文件边界，SHA字符串引用改整数引用节省109,093,574字节后续写；对M5 prompts使用Python `splitlines()`误把16条含Unicode行分隔符的JSON值拆开，独立逐LF读取确认原13,905条均合法后改只按LF分隔；M2子调用`key=sXXXXXX::...`的范围过滤补正，补入139,190条已保存prompt，原key/stage/source_line保持。它们是本次导出器问题，不是原实验失败，不能改写原日志。全部过程见`export_progress.log`、`compact_progress.log`、`subcall_prompt_correction.log`。

两流gzip→zstd转换验证解压字节SHA一致后才删除本次派生gzip；没有删除服务器原件。保留JSON值在初导和补导时逐条解码相等。`decoder_tests.json`另对M6实际request、M3旧v3原候选记录、M4实际messages/schema抽查解码与原件保留字段相同。全流结构、blob哈希、源记录数及凭证样式扫描结果见`export_validation.json`；其结果应与主包最终哈希验证一起阅读。

最后在`HANDOFF_ONLY=1`下禁止读取原服务器路径，经总`FILE_MANIFEST.csv`只读包内已交付评分文件，再次重汇总42个独立单元格全部一致。证据：`portable_reaggregation_bundle_only.json`；命令为`HANDOFF_ONLY=1 python3 scripts/baselines/reaggregate_scores.py audit/baselines/portable_reaggregation_bundle_only.json`。此验证证明这些表格数值的材料已实际进入包内，不只是服务器索引；仍没有运行评分器。

2026-10-22补充：对34条历史记录继续读取resolved_config，26条含运行时代码哈希；64次配置引用（共享运行包可能跨registry行重复）全部找到匹配代码现件或快照。详见`history_runtime_versions.json`。此检查没有将全部历史预测逐条绑定到config_hash，亦未核实历史评分器运行时版本。

## 2026-10-23 data4重建验收

原包因data3空间不足被用户删除。本次从保存会话恢复导出器及最终修正，读取原始证据并在data4重建。原始导出耗时约1188秒，补齐子调用、压缩、全流验证、来源绑定和解码抽查合计约738秒；无新模型调用、预测、评分或原件修改。旧失败过程保留为历史证据，没有重演已修复的错误。

完成308,953个源文件、757,363条记录、2,721,976个文本块及13,714,636次块引用的全流验证，七系统分别覆盖13,905个样本ID。两条完整解码字节流的SHA-256均与旧包保存收据完全一致，见`../rebuild/baselines_heads/historical_stream_comparison.json`。最终文本容器339,132,689字节、记录容器98,308,274字节，总437,440,963字节；这更新上文旧记录中的重压前体积。全流凭证样式匹配计数为0。

`source_method_bindings.json.gz`按每条记录实际method字段生成308,953项来源绑定，保留M0+M2联合标记并列出组件方法。实际解码器对M6、M3、M4、M0、M2共5例验证保留JSON值与原件一致；M0和M2均成功查询M0+M2共用记录。42个基线单元格已在HANDOFF_ONLY=1下从包内评分重汇总通过，34条历史运行中的64次配置代码引用全部匹配。

候选文件最终3,043项：按原会话中的追加动作补回68项历史i-MedRAG开发证据，并保留先后两版选择造成的2项v3通用prediction原件。相应恢复依据见`../rebuild/baselines_heads/partial_imedrag_candidate_correction.json`和`legacy_v3_candidate_correction.json`，未按目标计数添加无依据文件。最终验证收据与责任范围统一列于`../rebuild/baselines_heads/rebuild_status.json`。
