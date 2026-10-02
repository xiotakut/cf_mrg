# 医学反事实数据来源

2026-09-18 19:55补充：[CAD作者RP/RH来源核验](#r5-cad-premise-supervision-source)完成固定版本下载及许可边界核对，作为非医学的辅助前提监督候选；仅来源审核，未训练或提取特征。

最新状态：2026-09-18（Asia/Shanghai）。已取得[R5监督研究的BioNLI作者balanced原件](#r5-bionli-supervision-source)，用于资格与训练可行性核查，尚无新训练成绩。R4新增[形式因果及临床后果来源核查](#r4-structural-sources)，取得不等于资格通过或已有新验证成绩。[R1冻结验证来源核查](#r1-validation-source-availability)已完成：ASCENT用于有限目录验证；MedPIC全467已暴露，外部候选尚未提供兼容独立用药集。[R1六来源论文/公开代码复核](#r1-source-code-review)已完成，新增快照用于方法调查，未替换冻结数据。R3后续来源核对已取得CUPCase测试文件与ASCENT公开train/test，见[新增来源](#r3-additional-sources)；尚未纳入正式v5，验证范围与结论按各研究主记录区分。来源目录覆盖早期CF数据以及医学CF收集阶段的26个候选来源和两个控制资源，新增研究来源另列。获取状态按记录日期区分；来源编号、任务和本地文件位置以各阶段已保存制品为准。

2026-09-14补充：R3研究已取得固定上游版本的[M01公开训练文件](#medeinst-train-r3)，用于新增病例记忆候选的资格核对，未改变v5评测来源。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [R5前提监督：CAD作者RP/RH原件及许可](#r5-cad-premise-supervision-source)

- [R5监督：BioNLI作者balanced原件](#r5-bionli-supervision-source)

- [R4结构执行：形式因果与临床后果来源](#r4-structural-sources)

- [R1冻结验证的来源可用性](#r1-validation-source-availability)

- [R1六来源论文与代码当前发布状态](#r1-source-code-review)
- [MedEinst公开训练文件：R3记忆研究](#medeinst-train-r3)

- [Source collection and five-label annotation archive (2026-09-08)](#record-0021)
- [发布范围与原始来源.md](#record-0344)
- [医学CF资源清单.md](#record-0350)
- [DATASET_MATRIX.md](#record-0352)
- [r1_r5_benchmark_sources_20260910.md](#record-0354)

<a id="r1-source-code-review"></a>

## 2026-09-16：R1六来源论文与代码当前发布状态

为R1接续调查取得MedEinst最新ACL论文/实际GitHub树、MedPIC官方HF树和数据卡、AMQA v1/FairMedQA v2论文及公开复制资源、CPV正式NAACL PDF与固定commit完整代码、Cultural论文/推理代码、MedCounterFact论文/发布树，并追溯上游MedEvidence实际汇总代码。地址、版本和本地文件集中见[来源快照索引](/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/sources/README.md)，失败后取得的过程见该索引及各acquisition日志；没有新取数进入正式v5。

现发布物的具体边界：MedEinst官方仓库仍标ECR Coming Soon；MedPIC HF只有三个文件，无完整规则/修复代码；CPV公开的是构造、提示和评测，没有对应微调训练流程/训练样本；MedCounterFact当前仓库为数据/格式说明，不能把其上游MedEvidence实现冒称原方法完整代码。AMQA与FairMedQA为同arXiv号不同版本，不能登记成独立来源。方法细节、版本差异与R1取舍唯一正文在[优化研究记录](../research/optimization.md#r1-head-investigation)。

<a id="medeinst-train-r3"></a>

## MedEinst公开训练文件：R3记忆研究

2026-09-14。从作者[固定revision的数据目录](https://huggingface.co/datasets/zhui711/MedEinst/tree/354f4b527e764a8f2bebea8f71be55e0a6966402)取得train.jsonl，保存在[r3_memory_source/train.jsonl](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r3_memory_source/train.jsonl)，23,136,893字节，下载约1.96秒。来源URL、revision、状态与归属见[acquisition.json](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r3_memory_source/acquisition.json)。沿用CC-BY-4.0，保留MedEinst作者及DDXPlus来源归属；这次仅下载和资格处理，没有修改上游原始内容。

文件实读为21,218行、10,609病例对、46个疾病标签；这些是当前固定公开文件的数量，不能直接抄用论文描述的10,689对/49疾病。该文件与既有test属于相同上游revision。训练/测试重叠与可用病例的完整审计归[数据构建记录](construction.md#r3-memory-qualification)，新增方法及控制归[R3主记录](../research/r3_candidate_comparison.md)。历史其他方法曾使用本地MedEinst train作开发，其用途与本次新增记忆研究区分保存。

<a id="r3-source-followup"></a>

## 2026-09-15：R3后续来源可用性

重新核对[HelpMum-Personal/MamaBench数据卡](https://huggingface.co/datasets/HelpMum-Personal/MamaBench)，仍要求登录并接受联系人分享条件，病例未取得，未提交访问申请。作者公开的217对/434病例为零样本评测范围；搜索到的[nmrenyi/mamabench](https://huggingface.co/datasets/nmrenyi/mamabench)是另一个MAMAI多来源QA汇编，不能按同名代替该反事实来源。前者获取状态与既有M03记录相同。

为评估R3可否使用公开疾病知识而非训练答案检索，阅读[DDXPlus官方README](https://github.com/mila-iqia/ddxplus/blob/main/README.md)及其疾病/证据元数据说明。官方英文来源为[Figshare 22687585](https://figshare.com/articles/dataset/DDXPlus_Dataset_English_/22687585)。本机请求其`https://api.figshare.com/v2/articles/22687585`得到403 HTML，首次直接解析JSON因此报JSONDecodeError，复查确认HTTP状态；web工具也未取得该API内容。当前未下载release_conditions/release_evidences或患者数据，未修改运行中试验输入，不将此记作知识库已取得。疾病关联与候选机制取舍归[R3主记录](../research/r3_candidate_comparison.md#r3-process-restart)。

**公开镜像取得知识元数据。** 官方Figshare网页后续同样返回403；转读公开的[aai530-group6/ddxplus镜像](https://huggingface.co/datasets/aai530-group6/ddxplus)，仅下载固定revision `2ad986acc1ec62fb4a94171acc43f4fdd5bfde53`的`release_conditions.json`（49疾病，21,029字节，0.34秒）及`release_evidences.json`（223证据，120,263字节，0.42秒）。原件和URL、许可、耗时保存在[r3_ddxplus_knowledge](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r3_ddxplus_knowledge/acquisition.json)。镜像卡声明CC-BY-4.0，归属仍为DDXPlus；尚不能与访问失败的官方文件逐字比较。没有下载镜像train/test/validate患者或诊断标签行，也没有把新知识加入正在运行的审计试验。字段结构与官方README相符：疾病名、ICD10、症状/既往史关联，以及证据问题、类型、取值含义；疾病关联不等于必要条件、临床概率或完整排除规则。

另为后续独立验证检查[CFDX作者仓库README](https://github.com/FAIRHealth/clinical-counterfactual-reasoning)：公开树和README提供方法代码，运行说明要求调用方提供病例CSV/JSON；本次所读页面未找到固定病例评测包的下载入口。没有把方法代码仓库当作已取得的新验证数据，也没有取得新的病例。

<a id="r3-additional-sources"></a>

### 新增研究来源：CUPCase与ASCENT

2026-09-15，为冻结R3候选准备未参与其提示选择的病例资源；取得数据不等于已经完成资格审核或泛化评测。制品根目录为[r3_generalization_sources](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r3_generalization_sources)。两来源不改现有26来源编号和正式v5。

**CUPCase。** 从[作者数据集](https://huggingface.co/datasets/ofir408/CupCase)固定revision `157a85b1a0fa6d0e25e5209a1cdaf41cf1ff8753`下载`test.parquet`（8,424,692字节，0.95秒）及数据卡。实读3,562行，字段为病例叙述、正确诊断和三个干扰诊断；作者[AAAI论文](https://ojs.aaai.org/index.php/AAAI/article/view/35050)及[代码](https://github.com/nadavlab/CUPCase)已定位。数据卡声明Apache-2.0，无访问门槛；URL和耗时见[cupcase/acquisition.json](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r3_generalization_sources/cupcase/acquisition.json)。只检查了schema/数量，网页预览暴露首病例片段，尚未按候选成绩选样。它是病例诊断来源，原发布不提供反事实配对；不能把全体直接标为R3。

**ASCENT。** 阅读[原论文](https://proceedings.mlr.press/v333/choi26a.html)并从[作者仓库](https://github.com/naver-ai/ascent)固定commit `89091716698d6a2fa78b81d8380e7fec57e73fa5`取得`data/ascent/`、推理/评分说明与代码，共16文件、5,306,396字节；Apache-2.0，记录见[ascent/acquisition.json](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r3_generalization_sources/ascent/acquisition.json)。Arrow实读train 2,773行、test 305行；包含逐步病例上下文、当前目标、步骤和原生提示。只展示train前两行作接口理解，未展示test逐题文本/答案或运行模型。当前未下载`ascent_w_reason`，不能记作两种任务均已取得。

ASCENT输入允许既往步骤的医生印象/理由及当前新发现，当前目标和未来步骤不属于推理输入；原生答案可含多个疾病或相关系统。其MedQA-USMLE血缘可能与本项目其他来源重合，须在独立评测声明前核对；资格、暴露及接口选择归[data/construction.md](construction.md)，方法取舍归[R3主记录](../research/r3_candidate_comparison.md#r3-generalization-source-selection)。

**获取失败与处理。** ASCENT PDF的web打开因`application/octet-stream`失败，直接HTTP取得8,817,381字节；本机无`pdftotext`且原环境无PDF读取库，在制品内`pdf_reader/`单独安装pypdf 5.9.0后提取23页正文，未改共享环境。pip显示既有sentence-transformers/transformers版本冲突警告，未处理与本次PDF读取无关的环境问题。仓库获取首试使用不存在的裸`python`命令，改为既有venv解释器；随后tree响应SHA等于commit SHA、与commit内tree SHA不同，事先断言失败，保留两个原始API响应，下载采用单独取得的commit SHA，未靠该断言宣称文件一致性。上述失败均发生在模型运行之前。

**未采用的其他来源。** [counterfactual-diagnosis](https://github.com/babylonhealth/counterfactual-diagnosis)公开的是随机网络与去除临床概念名称的重现实验资源，不能直接充当文本诊断头的病例评测；[clinical-reasoning-benchmark-v0.2](https://huggingface.co/datasets/ClarusC64/clinical-reasoning-benchmark-v0.2)主要目标为稳定性/轨迹/干预判断，与当前诊断接口不同，未下载病例。仅检查[MedCaseReasoning](https://huggingface.co/datasets/zou-lab/MedCaseReasoning)元数据（revision `469a5365bc534b5b2b9cfbc52b2ef2a10f43a339`），未下载病例；其开放答案和评审需求尚未解决，不把来源目录存在当成已有可评分验证集。DDXPlus镜像患者train/test/validate仍未下载。

### DDXPlus训练统计资源取得（2026-09-15后续）

为[R3事实提取与统计知识比较](../research/r3_candidate_comparison.md#r3-empirical-feature-head)，从同一公开镜像固定revision `2ad986acc1ec62fb4a94171acc43f4fdd5bfde53`取得`train.csv`，670584506字节，下载53.85秒。此前“患者train/test/validate均未下载”是当时状态；本次仅新增train，test和validate仍未获取。来源URL、CC-BY-4.0许可归属、字节数和耗时见[train_acquisition.json](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r3_ddxplus_knowledge/train_acquisition.json)，实际命令为同目录`acquire_train.py`。官方Figshare内容仍未逐字核对，保留镜像来源限制。

该文件是新增带标签监督资源，不能归为无监督通用知识；当前仅开始按PATHOLOGY和EVIDENCES汇总疾病—二值特征计数，不建病例答案检索索引、不采用DIFFERENTIAL_DIAGNOSIS列。DDXPlus与MedEinst同上游生成器，尚未据本次获取证明病例隔离或临床泛化。统计转换和实验结论由R3主记录维护。

<a id="record-0021"></a>

## Source collection and five-label annotation archive (2026-09-08)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第863行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Source collection and five-label annotation archive (2026-09-08)

The source annotation collection, from which the current v3 subset derives, is
[`medical_cf_collection/README.md`](/home/data3/txy/docs/data/construction.md#record-0321),
indexed under `$CF_BENCHMARKS/2026-09-08_medical_cf_five_labels/`.
Published to [the independent GitHub folder](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-08_medical_cf_five_labels)
on `origin/main` at `cfe8246e4c759abf914867d2c92e1e016f007c84`.
The public archive contains 55,991 annotation records, the 28,243-unit reviewed
analysis set, 80,910 target annotations, audit/correction receipts and offline
prediction regrouping; native `original_records` and raw model responses stay
on the server. Necessary evidence quotations and official download locators
are retained. Its 9 gzip files and all exported ID/field correspondences passed
`scripts/verify_github_results.py`; this is package consistency, not a new
medical semantic audit. Text R5 is 20,318/25,746 (78.92%); AMQA, MedRGB and
MedPerturb supply 56.40% of text R5. See the archived R5 composition report.
The [publication receipt](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/reports/github_publication.json)
records the verified remote commit and scope; the
[package validation](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/reports/github_package_validation.json)
records the 79-file release checks. The
[counting and R5 explanation](/home/data3/txy/docs/data/construction.md#record-0348)
defines comparison units, source roots and missing-image metadata, and explains
why source-size sampling has not balanced the five labels.
It uses the user's medical-only five labels: R1 新增支持, R2 撤销支持,
R3 重新比较, R4 推导后果, R5 保持判断, at the question/comparison or
specific subjudgment level. Labels may overlap; uncertain records remain.

Independent audit on 2026-09-08 is now in
[`audit_20260908/README.md`](/home/data3/txy/docs/data/construction.md#record-0322).
All 26 candidate sources and 2 cited medical controls have primary sources;
all 55,991 collected and 28,243 selected records reproduce independently
downloaded official originals. The initial 187-judgment audit found 92
confirmed classification problems. Follow-up corrections now update 172
judgments in 130 units, including same-rule siblings; 11 original references
are explicitly excluded from scoring. Native questions, gold and frozen
IDs are unchanged. See `audit_20260908/corrections/README.md` for current
results. `scripts/finalize_review.py` reapplies the three stable correction
files; `scripts/audit_collection.py` checks provenance and independent
post-correction review. The initial audit remains historical evidence.

The user clarified quantity: collect all acquired target subsets below 1,000,
and reduce very large sources around 5,000–10,000. The adopted implementation
also keeps 1,000–4,999 in full and takes 2,500 comparison units from pools of
5,000 or more; these defaults do not equalize sources or functional labels.
Keep complete raw files and normalized data.
The earlier 358-unit pilot was too small and is archived under `pilot_358/`.
It is no longer the current collection scope.

All 26 resources have acquisition records; 15 contribute collected data
(14 text sources and one missing-image multimodal source), while the specified
CF inputs of 11 candidates remain unacquired. The complete normalized archive
has 55,991 records: 53,494 text comparison records (including 97 flagged
non-CF/no-op records) and 2,497 MedMKEB edit metadata records with missing
images. The analysis subset has 25,746 text comparisons plus those 2,497
multimodal metadata records kept separately. The frozen 28,243 IDs and their
order now all have first-pass review decisions. Of the 25,746 text units,
21,695 have at least one classified target; 4,051 have reviewed reasons for
no label (2,129 insufficient evidence, 1,901 source problems, 21 outside the
five relations). Of the labelled text units, 1,127 still have unresolved
child targets. Text R1/R2/R3/R4/R5 counts are 2,030/88/389/53/20,318 and overlap.
The 2,497 missing-image metadata groups remain separate; all have partial
child coverage. Nonselected 27,748 archive rows retain preliminary status.
`review_method` distinguishes semantic item review, semantic group review,
and structural verification; all retain `clinical_review=false`. Current
child decisions are in `judgments`; old `target_annotations` and rule fields
are archived in `pre_review_annotation`. No expert agreement study was run.

All 25,280 old unique inputs and all 75,840 M0/M1/M2 predictions are
accounted for in `reports/旧库全部输入索引.jsonl`. The complete collection
links 17,949 comparisons to old predictions (7,341 in the analysis subset).
All 82,131 original evaluation-record/method rows were regrouped offline
using the original native parser and gold; zero new model calls or changed
inputs. References, GF, no-ops and historical sensitivity inputs remain
explicitly identified. The earlier full-test metrics remain authoritative.

Reuse the five original raw caches rather than downloading again. Newly
acquired fixed data include LabTest, HIV, MedPerturb, AMQA, DiversityMedQA,
EquityMedQA, MedRGB, BioRAB, MedCF and MedMKEB metadata. MedRGB is counted as
3,680 question groups preserving 36,800 document slots; MedCF retains all
splits but analysis uses all 798 actual test edits plus four unchanged test
records as references. Source roots, repeated variants and patients differ.
MamaBench access, CLIR official CF pairs, ECG MCo, and other documented
fixed-data gaps remain unresolved; GenMedicalEval's one public example is
separate and does not imply acquisition of its declared 12,000 entries.

Read `分析子集_逐题标注.csv`, `分析子集.jsonl`, `全部比较单元.jsonl`,
`医学CF资源清单.md`, `分类与抽样说明.md`, and `reports/` in the package.
Re-export the frozen annotations sequentially with `scripts/finalize_review.py`,
`scripts/reclassify_full_predictions.py` (the existing MedRGAG venv), and
`scripts/verify_full_collection.py`. The preliminary assembler is guarded
against overwriting reviewed data. `parts/*/build_full.py` expands cached
releases. Read `reports/分类审阅报告.md`, `分析子集_具体判断.csv`, and
`分析子集_未能定类.csv` for current decisions and limitations. Old pilot
scripts and pilot review reports are historical only. Complete-scope saved
prediction grouping includes preliminary nonselected annotations; use
analysis_subset for this reviewed cohort, retaining native task metrics.

<a id="record-0344"></a>

## 发布范围与原始来源.md

来源：[Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/reports/发布范围与原始来源.md](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/reports/发布范围与原始来源.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/reports`。

日期：2026-09-08。拟发布目录：`benchmarks/2026-09-08_medical_cf_five_labels`。本次发布标注、统计和审计结果，未打包`original_records`原始题库镜像。标注依据仍包含必要的原题引文，个别引文较长；已审核引文不截断或改写。现有`benchmarks/README.md`作为此前归档范围参考，不作为禁止发布任何原句的条款。

当前成果包含26项真实医学资源候选，其中15项已取得本次使用的数据：14项文本来源及1项缺图的多模态编辑元数据。服务器全库55,991个归一化单元，冻结分析子集28,243个；这些是本地收录规模，不代表GitHub附带相同数量的完整原始题。原题、比较组和必要参照仍应分别计数。出处审核证明资源及所选原件真实，不能据此保证原作者每个答案都正确。最新分类、更正记录及评分禁用标记应随结果一起发布。

服务器已取得来源的许可与输入状态如下。数量取最终主表；发布表保留对应标注、已审核依据引文和官方出处，不另附完整原始题库镜像。

|来源|全库单元|分析单元|原作者许可声明/核查入口|输入状态|
|---|---:|---:|---|---|
|M01 MedEinst|5,383|2,500|[CC-BY-4.0](https://huggingface.co/datasets/zhui711/MedEinst)|已取得所选文本|
|M02 MedPIC-Bench|183|183|[CC-BY-4.0](https://huggingface.co/datasets/TIM0927/MedPIC-Bench)|已取得所选文本|
|M05 临床检验因果推理评测|33|33|[MIT](https://github.com/balubhasuran/LLM_Causality_LabTest/blob/main/LICENSE)|已取得所选文本|
|M06 HIV治疗因果情景研究|20|20|[CC-BY-4.0 article and associated supplement](https://api.crossref.org/works/10.1038/s41746-026-02771-7)|已取得所选文本|
|M10 CPV-MedQA|10,225|2,500|[MIT](https://huggingface.co/datasets/kenza-ily/medqa-cpv)|已取得所选文本|
|M11 Counterfactual Cultural Cues|1,349|1,349|[未声明明确数据许可](https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs)|已取得所选文本|
|M12 FairMedQA/AMQA|4,806|4,806|[未声明明确数据许可](https://github.com/XY-Showing/AMQA)|已取得所选文本|
|M14 DiversityMedQA|6,296|2,500|[未声明明确数据许可](https://huggingface.co/datasets/Rajat1212/DiversityMedQA)|缺原生选项/答案|
|M16 EquityMedQA|323|323|[CC-BY-4.0 article and Supplementary Data 1](https://www.nature.com/articles/s41591-024-03258-2)|已取得所选文本|
|M17 MedPerturb|3,759|3,745|[CC-BY-4.0](https://huggingface.co/datasets/abinitha/MedPerturb)|已取得所选文本|
|M20 MedCounterFact|809|809|[未声明明确数据许可](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence)|已取得所选文本|
|M22 MedRGB|3,680|3,680|[CC-BY-4.0](https://huggingface.co/datasets/ngotrnghia1811/MedRGB)|已取得所选文本|
|M23 BioRAB|12,615|2,500|[未声明明确数据许可](https://drive.google.com/drive/folders/19d_pl89iD8I3-KDkqT1EuNr1Mg0zuW-5)|已取得所选文本|
|M24 MedCF|4,013|798|[未声明明确数据许可](https://github.com/quqxui/MedLaSA)|已取得所选文本|
|M25 MedMKEB|2,497|2,497|[未声明明确数据许可](https://github.com/pkusixspace/MedMKEB)|仅编辑元数据；缺图|

CC BY来源需保留作者、原始出处、许可链接，并说明本项目只增加分类及结构化整理；MedEinst还需保留DDXPlus归属。M05仓库的MIT通知应随相关材料保留；M10数据卡也声明MIT，保留该扩展及MedQA原题出处。M06的许可依据是出版社提交的Crossref记录，本次出版社正文入口读取失败；实际问题出自已核验的官方补充PDF。M16出版社明确将问题/评级工作簿作为Supplementary Data 1公开，并给出CC BY 4.0，当前所选原件为论文官方arXiv附件。[M05许可](https://github.com/balubhasuran/LLM_Causality_LabTest/blob/main/LICENSE)、[M06出版社元数据](https://api.crossref.org/works/10.1038/s41746-026-02771-7)、[M16正文及数据说明](https://www.nature.com/articles/s41591-024-03258-2)。

M11、M12、M14、M20、M23、M24、M25的作者入口公开，但所检发布中未找到明确数据许可。这不能写成作者明示禁止再分发，也不能把本项目许可套给第三方材料。旧M11目录字段中的“no text redistribution”未找到作者条款依据，不作为作者禁令。本次发布本项目结果、已审核依据引文和官方定位信息，不将缺LICENSE解释为额外禁令。

结果发布与原任务复现需要分开理解。GitHub主表保留改动说明、五标签、具体判断、依据、原任务定义、质量/评分状态及官方文件定位；不另打包`original_records`原始题库镜像和历史模型答案。已审核的依据引文原样保留，不截断或改写。其中个别引文较长，例如M12复核引用两端问题、M23引用NLI上下文。因此准确的范围是“未打包原始题库镜像，保留必要的原题引文”，不能声称发布目录完全不含原始句子。

重新运行原任务之前，需要从配套JSON里的官方固定版本地址下载原件，再按题目ID、行号和原任务结构还原下列依赖。本次结果目录本身不是可独立运行的完整benchmark：

- **共享原题与清洁对照。** 服务器`parts/evidence_other/full_root_records.jsonl`共11,751条：M12 801、M14 1,707、M22 3,680、M23 5,563。这些记录不随结果目录作为原题库发布。还原M22时必须取得清洁`signal_documents`、`sub_qa_pairs`；还原M23时必须取得匹配的clean输入。`DOC_n`不能猜成清洁文档数组下标。
- **MedPIC的284条GF。** 服务器文件为`parts/clinical_existing/raw/medpic_gf_references.jsonl`；这些参照需从官方467条原件恢复，不在183条CF计数里，也没有足以任意猜配对的正式映射。
- **M06的PDF和转录对应。** 20条已取得CF来自官方补充PDF。原Scenario ID、页定位、转录方法和准确PDF下载入口需保留；复现时恢复`M06_cf_transcription.json`对应的题目与作者expected answer/explanation，不能包装为本项目新生成的问题。
- **原任务信息。** MedEinst的开放诊断配对、M12原题/中性题/固定变体及选项、M16两端问题与理想答案差异评级、M20两套证据、M24/M25编辑目标与locality都依赖原文件。M14原件没有完整选项/gold，M25原件没有随包图像；重新下载这些文件也不能自动消除已知缺口。
- **跨机器可用性。** 发布定位至少包括资源ID、官方URL、固定版本、行/题ID、来源根ID及对应解析规则；本机绝对路径只能作为本地历史记录，不能是唯一的数据入口。当前核查没有声称已经验证一键下载及还原全部原任务。

以下11项仅发布资源目录、科学范围与官方访问入口，不计为已取得输入：

|来源|当前缺口|
|---|---|
|M03 MamaBench|gated病例未取得|
|M04 肿瘤临床CF评测|未定位原病例发布包|
|M07 CLIR-Bench|指定CF编辑对未发布于所检树|
|M08 ECG-Expert-QA|MCo固定文件未定位；MC不能替代|
|M09 GenMedicalEval|仅栏目文档示例，未取得声明的12000条|
|M13 MedEqualQA|所检作者仓库未发布题库|
|M15 CLIMB|未取得固定诊断CF病例对|
|M18 DeVisE|仅生成代码，受限MIMIC病例未取得|
|M19 MedFuzz|未取得完整固定攻击输入release|
|M21 MediEval|受限患者上下文/知识源未取得|
|M26 COLLECT|受限图像包未取得|

实际访问限制集中在尚未取得的资源。MamaBench要求登录并接受访问条件，且作者将其定位为保留的零样本评测集；DeVisE和MediEval使用需相应权限的MIMIC数据，后者还需UMLS。代码公开不等于受限病例已经公开。当前发布不含这些未取得病例，也不需要为它们补造原题。[MamaBench数据卡](https://huggingface.co/datasets/HelpMum-Personal/MamaBench)、[DeVisE访问说明](https://github.com/camztag/DeVisE)、[MediEval访问说明](https://github.com/ZhanQu945/MediEval)、[MIMIC-IV-Note](https://physionet.org/content/mimic-iv-note/2.2/)。

COLLECT有明确的额外限制：Borealis v1.3标为CC BY-NC-ND 4.0，图像ZIP为restricted；访问条款要求相关研究用途、原样使用和署名，禁止修改、增强及分发变换后的版本，原文包括“redistributing transformed versions, are not permitted.”。当前仅保留候选说明和官方申请入口，不上传未取得图像或制作替代图像。这是针对受控/改写数据的实际条款，不应夸大为所有未改动非商业副本一概被禁止。[COLLECT官方条款API](https://borealisdata.ca/api/datasets/:persistentId/?persistentId=doi:10.5683/SP3/KXYCNY)。

此外，核查过程中缓存的医学资料网页不是benchmark输入。尤其`M06_efavirenz_medlineplus.html`含ASHP药物资料，其页面注明商业复制需要授权；发布结果保留相关医学引用即可，无需把整张网页缓存镜像带入GitHub。原作者历史模型输出和与本次CF无关的普通子任务同样无需随结果重复发布。[该药物资料及版权通知](https://medlineplus.gov/druginfo/meds/a699004.html)。

本核查未打包、未修改主库、未执行Git提交或推送。许可未声明项仍按未声明登记；M06本轮许可复查采用出版社元数据，M16的figshare API本轮返回403但原件已由官方arXiv附件完成审核。逐源状态、固定版本、公开原件URL和依赖记录在`source_release_notes.json`。

<a id="record-0350"></a>

## 医学CF资源清单.md

来源：[Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/医学CF资源清单.md](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/医学CF资源清单.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection`。

### 医学CF资源清单：完整库与分析子集

2026-09-08。所有已选28,243个单元完成首轮审阅；有标签指至少一个具体目标成立，不是临床专家验收。26项是资源目录，表中0表示目标数据尚未取得，不表示其科学范围被排除。

|编号|资源|完整比较记录|分析已审|有标签|无标签|
|---|---|---:|---:|---:|---:|
|M01|MedEinst|5,383|2,500|843|1,657|
|M02|MedPIC-Bench|183|183|167|16|
|M03|MamaBench|0|0|0|0|
|M04|肿瘤临床CF评测|0|0|0|0|
|M05|临床检验因果推理评测|33|33|30|3|
|M06|HIV治疗因果情景研究|20|20|13|7|
|M07|CLIR-Bench|0|0|0|0|
|M08|ECG-Expert-QA|0|0|0|0|
|M09|GenMedicalEval|0|0|0|0|
|M10|CPV-MedQA|10,225|2,500|1,111|1,389|
|M11|Counterfactual Cultural Cues|1,349|1,349|1,174|175|
|M12|FairMedQA/AMQA|4,806|4,806|4,298|508|
|M13|MedEqualQA|0|0|0|0|
|M14|DiversityMedQA|6,296|2,500|2,378|122|
|M15|CLIMB|0|0|0|0|
|M16|EquityMedQA|323|323|302|21|
|M17|MedPerturb|3,759|3,745|3,615|130|
|M18|DeVisE|0|0|0|0|
|M19|MedFuzz|0|0|0|0|
|M20|MedCounterFact|809|809|788|21|
|M21|MediEval|0|0|0|0|
|M22|MedRGB|3,680|3,680|3,680|0|
|M23|BioRAB|12,615|2,500|2,499|1|
|M24|MedCF|4,013|798|797|1|
|M25|MedMKEB|2,497|2,497|2,497|0|
|M26|COLLECT|0|0|0|0|

标签分布与审阅方法见[分类审阅报告](/home/data3/txy/docs/data/construction.md#record-0342)；M25缺图元数据单列，不计文本数量。

#### 已取得范围与限制

- **M01 MedEinst**：完整保留5,383官方对；83对未见临床文字变化，保留问题构造标志并从分析池剔除。分析按原trap诊断分层取2,500。 [原始入口](https://huggingface.co/datasets/zhui711/MedEinst)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/clinical_existing/acquisition.json)。
- **M02 MedPIC-Bench**：183 CF全收；284 GF保留原文件与旧输入索引，不猜配对。 [原始入口](https://huggingface.co/datasets/TIM0927/MedPIC-Bench)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/clinical_existing/acquisition.json)。
- **M03 MamaBench**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://huggingface.co/datasets/HelpMum-Personal/MamaBench)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M04 肿瘤临床CF评测**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://arxiv.org/html/2605.30590v1)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M05 临床检验因果推理评测**：33 CF全收；第一99题块的66道非CF题作原序列参照，第二模型评价块不重复算题。 [原始入口](https://github.com/balubhasuran/LLM_Causality_LabTest)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M06 HIV治疗因果情景研究**：20道CF附录情景全收；参考答案可靠性逐项标记。 [原始入口](https://www.nature.com/articles/s41746-026-02771-7)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M07 CLIR-Bench**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://huggingface.co/datasets/winall/CLIR-Bench)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M08 ECG-Expert-QA**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/Zaozzz/ECG-Expert-QA)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M09 GenMedicalEval**：仅已发布文档示例另存；目录声称的12,000不能计作已取得数据。 [原始入口](https://github.com/MediaBrain-SJTU/GenMedicalEval)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M10 CPV-MedQA**：12,310发布变体中2,085文字与原题相同，10,225实际变化完整收录；分析取2,500。1,202原题根单列。 [原始入口](https://huggingface.co/datasets/kenza-ily/medqa-cpv)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/existing_other/acquisition.json)。
- **M11 Counterfactual Cultural Cues**：1,350发布变体中1条无变化另存；1,349实际变化全部分析，150原题根。 [原始入口](https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/existing_other/acquisition.json)。
- **M12 FairMedQA/AMQA**：801根×6固定攻击=4,806比较，全收；中性和原题作为参照；已按实际新增临床线索、原题目标及明确的实施条件裁决。 [原始入口](https://github.com/XY-Showing/AMQA)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M13 MedEqualQA**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://aclanthology.org/2025.sciprodllm-1.4/)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M14 DiversityMedQA**：6,380候选变体中84无变化；6,296完整归档，分析2,500。保留author_train/author_test、缺选项与性别矛盾。 [原始入口](https://aclanthology.org/2024.nlp4pi-1.29/)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M15 CLIMB**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/uscnlp-lime/climb)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M16 EquityMedQA**：323对全收：123 CC-Manual＋200 CC-LLM，关联145个问题。逐项保留相同/不同理想答案评定，不整包R5。 [原始入口](https://www.nature.com/articles/s41591-024-03258-2)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M17 MedPerturb**：3,759发布变体与1,884基线全收；14文字无变化另作对照，3,745实际变化全部分析。VISIT/MANAGE分别判断。 [原始入口](https://huggingface.co/datasets/abinitha/MedPerturb)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M18 DeVisE**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/camztag/DeVisE)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/new_clinical/acquisition.json)。
- **M19 MedFuzz**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://arxiv.org/html/2406.06573v2)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M20 MedCounterFact**：已复用完整809个替换比较及203个原始证据根，809条全收全审；保留假设证据与现实合理性的区别。 [原始入口](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/existing_other/acquisition.json)。
- **M21 MediEval**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/ZhanQu945/MediEval)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M22 MedRGB**：3,680原问CF组全收，组内36,800 DOC位置完整保留；36,601完整、199缺字段。3,480个options元数据占位另存，不计CF。 [原始入口](https://arxiv.org/html/2411.09213)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M23 BioRAB**：两强度12,616发布记录中1个输入未变，12,615完整归档；实际11,125种可见配对、5,563个不同目标。分析取2,500，重复不当独立病例。 [原始入口](https://arxiv.org/html/2405.08151v3)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M24 MedCF**：4,028编辑根各split全保留：15个新旧值相同另存，4,013实际编辑；分析取test798实际编辑，另保留4个test未改值记录。 [原始入口](https://github.com/quqxui/MedLaSA)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M25 MedMKEB**：2,497 eval编辑元数据全收、全部缺图，单列多模态，不加入文本题量；train/attack原文件留存但不充评测数。 [原始入口](https://arxiv.org/html/2508.05083v1)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。
- **M26 COLLECT**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://doi.org/10.5683/SP3/KXYCNY)；[取得记录](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/parts/evidence_other/acquisition.json)。

来源详情中的旧selected_units/labeled_units是归档试点历史字段；当前完整/分析规模以本表、资源目录.json的full_counts/analysis_selection和reports/collection_counts.json为准。各来源full_counts.json提供发布行、实际变体、参照与重复规模。

<a id="record-0352"></a>

## DATASET_MATRIX.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/datasets/DATASET_MATRIX.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/datasets/DATASET_MATRIX.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/datasets`。

### Public Dataset Matrix

| Dataset | Public resource | Core capability | Compatibility with MedRGAG | World-model value | Primary limitation |
|---|---|---|---|---|---|
| MedPIC-Bench | `TIM0927/MedPIC-Bench` | rule activation/deactivation under patient changes | Very high | L1 applicability/precondition | medication safety only; weak next-state rollout |
| CLIR-Bench | `winall/CLIR-Bench` | irregular temporal evidence, intervention response, forecast, next action, causal edits | Medium; requires time-series adapter | Highest for `(s,a)->s'` | derived ICU QA; viewer currently has schema error |
| MedEinst | `zhui711/MedEinst` | diagnosis flip after minimal discriminative-evidence change | High for textual input | state-update generalization | diagnosis, not action transition |
| MedCounterFact | `KaijieMo-kj/Counterfactual-Medical-Evidence` | conflict between supplied evidence, priors and safety | High for KGCC/KADS stress test | evidence-world consistency | not a patient transition benchmark |
| ReMedQA | `disi-unibo-nlp/ReMedQA` | MCQ/open/format perturbation robustness | Very high | negative control | not causal counterfactual |
| CPV / MedEqualQA / FairMedQA | public GitHub/HF releases | demographic counterfactual invariance/bias | High | negative control | answers usually should not change |
| CLADDER | `causalNLP/cladder` | formal SCM counterfactual reasoning | Low end-to-end; high module-level | causal sanity test | non-medical synthetic text |
| CP-Env | `SPIRAL-MED/CP_ENV` | dynamic clinical pathways and tool use | Low; requires agent wrapper | optional L3 pathway test | expensive; not paired static QA |

#### Recommended core suite

##### Minimal publishable diagnosis suite

- MedPIC-Bench
- MedEinst
- MedCounterFact
- ReMedQA or CPV control

##### Strong world-model suite

- MedPIC-Bench
- CLIR-Bench IR + forecasting + decision + official counterfactual edits
- MedEinst
- MedCounterFact
- ReMedQA/CPV controls
- CLADDER module sanity

#### Adaptation principles

1. Do not flatten all datasets into identical single-choice MCQ if that destroys the official task.
2. A unified internal schema may coexist with dataset-specific output parsers.
3. Pair members are independent at inference and grouped only for metrics.
4. Distinguish answer-changing counterfactuals from answer-invariant perturbations.
5. Distinguish in-world evidence faithfulness from real-world clinical safety.
6. Distinguish observed intervention response from normative guideline recommendation.

<a id="record-0354"></a>

## r1_r5_benchmark_sources_20260910.md

来源：[Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/r1_r5_benchmark_sources_20260910.md](/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/r1_r5_benchmark_sources_20260910.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md`。

**当前 R1–R5 benchmark 的来源、筛选过程与排除原因**

核对日期：2026-09-10。对象是本地冻结的 `v3_20260909_exclusive_text_auto_cpv`，不是对各作者网站最新版本的重新检索。统计依据为当前 units/coverage、2026-09-08 已修正分类表、来源取得与抽样记录，以及相关历史对话。本次没有模型推理、重新判类、改题或改分。

**结论：当前是从 8 个来源构建的项目评测子集，不能称为 8 个完整官方 benchmark 的全量测试。** 共 3,105 个互斥评测单元、4,872 个独立模型输入。单元可以是原题与变体的比较或题内反事实任务；参照输入不重复计入单元数，单元也不是独立患者数。

**当前来源与类别**

| 来源 | R1 新增支持 | R2 撤销支持 | R3 重新比较 | R4 推导后果 | R5 保持判断 | 合计 |
|---|---:|---:|---:|---:|---:|---:|
| MedEinst | 569 | 0 | 274 | 0 | 0 | 843 |
| MedPIC-Bench | 85 | 75 | 7 | 0 | 0 | 167 |
| HIV ART causal scenarios | 0 | 0 | 0 | 13 | 0 | 13 |
| CPV-MedQA | 1 | 0 | 0 | 0 | 1,090 | 1,091 |
| Counterfactual Cultural Cues | 67 | 0 | 0 | 0 | 0 | 67 |
| FairMedQA/AMQA | 91 | 0 | 43 | 0 | 0 | 134 |
| DiversityMedQA | 0 | 2 | 0 | 0 | 0 | 2 |
| MedCounterFact | 788 | 0 | 0 | 0 | 0 | 788 |
| 合计 | 1,601 | 77 | 324 | 13 | 1,090 | 3,105 |

以上直接按当前 `units.jsonl.labels` 计数，与 [source_summary.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/benchmark_r1_r5_text_auto_cpv_v3_exclusive_20260909/source_summary.csv) 一致。v3 将重合单元分配给其已有类别中题量较少的一类，调整了 328 个单元、消除 331 次重复归属，**未删除任何 v2 单元**。原标签继续保留；这一步不依据模型得分。

**为什么这 8 个来源没有完整纳入**

下表“发布/取得范围”指冻结取得记录对应的原数据范围；比较、原题、文件行和附录场景分别表述，不能混作同一种分母。

| 来源 | 发布/取得范围 → 冻结审阅 → 当前 | 具体原因 |
|---|---|---|
| MedEinst | 5,383 官方病例对 → 2,500 审阅 → 843 | 83 对没有可见临床文字变化，不进抽样池；从其余 5,300 对按原诊断分层抽取 2,500。审阅后 1,119 个证据不足、538 个源构造问题，843 个有标签单元全部纳入。 |
| MedPIC-Bench | 467 题，其中 183 CF、284 GF → 183 CF 全审 → 167 | 本项目目标是 CF；GF 是事实题，原文件保留，不因缺少官方映射自行拼成题对。183 个 CF 中 12 个分类证据不足、4 个源构造问题。 |
| HIV ART causal scenarios | 取得附录 60 个表格场景中的全部 20 个 CF 场景 → 20 全审 → 13 | 5 个缺少可支持分类的关系依据、2 个干预条件不明确。这是已取得附录的 CF 子集，不能称为整篇研究的完整数据集。 |
| CPV-MedQA | 12,310 发布变体 → 10,225 有文字变化 → 2,500 审阅 → 1,091 | 2,085 个无变化变体不计有效 CF；大来源抽取 2,500。审阅后 1,289 个源构造问题、100 个证据不足，余下 1 个 R1 和 1,110 个 R5；再排除 20 个图像依赖 R5，最终为 1+1,090。 |
| Counterfactual Cultural Cues | 1,350 变体 → 1,349 实际变化全审 → 67 | 1 个无变化变体另存；173 个证据不足、2 个不属于五类；1,107 个已标注 R5 暂不纳入，仅保留 67 个 R1。 |
| FairMedQA/AMQA | 801 原题 × 6 固定攻击 = 4,806 比较 → 全审 → 134 | 508 个分类证据不足；4,164 个 R5 暂不纳入；剩余 134 个 R1/R3 单元全部纳入。原题/中性题作为参照保存。 |
| DiversityMedQA | 6,380 候选变体 → 6,296 实际变化 → 2,500 审阅 → 2 | 84 个无变化变体另存；大来源抽取 2,500。120 个证据不足、1 个源构造问题、1 个不属于五类；2,376 个 R5 暂不纳入，只留下 2 个 R2。 |
| MedCounterFact | 809 替换比较 → 全审 → 788 | 21 个因替换将不同治疗臂合并成同名等比较构造问题而无可用标签。其余 788 个全部纳入 R1；其中原本也带 R5 的 703 个仅关闭本版 R5 归属，题目并未再被删除。 |

“证据不足”“源构造问题”是既有分类审阅的裁决，不是本次重新作出的临床判断，也不表示对来源整体质量的判定。例如 MedEinst 的患者事实被改成尚未回答的问句，不能把问句当作新事实；CPV 部分变体添加了与原文身份表述冲突的称谓。逐单元依据仍在 [分类表](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/分析子集_逐题标注.csv) 和 [未能定类清单](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/分析子集_未能定类.csv)。已修正分类的计数优先于各分组较早的 review_summary。

**已收集但当前整个来源未进入的 7 项**

| 来源 | 已收集/审阅范围 | 当前未纳入的实际原因 |
|---|---|---|
| LabTest / LLM_Causality_LabTest | 33 个 CF，30 个有标签 | 需要基于回答内容的人工或 LLM rubric 评分；当前限定固定规则评分，因此 30 个已分类 R4 全部排除。 |
| EquityMedQA | 323 对，302 个有标签 | 当前不用此来源的裁判评分任务。R1–R4 候选中的 125 个因此排除；另 177 个仅 R5 单元本就不在 CPV-only 范围，21 个在分类阶段未获得标签。 |
| MedPerturb | 3,759 发布变体；3,745 个实际变化全审，3,615 个有标签 | 已分类单元均仅 R5；当前 R5 限定 CPV-MedQA。 |
| MedRGB | 3,680 题组全审，全部有 R5；保留 36,800 个文档位置 | 当前 R5 限定 CPV-MedQA；不是因题目已被判为无效。 |
| BioRAB | 12,615 个有效比较归档，抽取 2,500，2,499 个有标签 | 当前 R5 限定 CPV-MedQA；1 个在分类阶段证据不足。 |
| MedCF | 4,013 个实际编辑归档；按原 split 审阅全部 798 个有效 test 编辑，797 个有 R5 | 当前 R5 限定 CPV-MedQA；其余 split 和未改值参照仍归档。 |
| MedMKEB | 2,497 个 eval 编辑元数据 | 全部缺少任务必需图像，当前纯文本评测不能完整执行。R1–R4 候选范围内涉及 86 个，其余仅 R5 元数据也未进入当前范围。 |

这 7 项及其他未入选记录仍保存在旧库和归档中。“未进入当前评测”不等于从磁盘删除。

**排除数量的口径**

v3 的 [coverage.jsonl](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/benchmark_r1_r5_text_auto_cpv_v3_exclusive_20260909/coverage.jsonl) / [excluded_units.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/benchmark_r1_r5_text_auto_cpv_v3_exclusive_20260909/excluded_units.csv) 只覆盖“R1–R4 候选 + CPV R5 候选”：

| 候选处理 | 单元数 |
|---|---:|
| 纳入当前 v3 | 3,105 |
| 排除裁判评分：LabTest 30 + EquityMedQA 125 | 155 |
| 排除图像依赖：MedMKEB 86 + CPV 20 | 106 |
| 本版候选合计 | 3,366 |

所以 **155 + 106 不是从完整来源库到 v3 的全部减少量**。它不含更早的无变化处理、大来源抽样、无标签记录和暂缓的其他 R5。

若从已冻结审阅的 28,243 个单元做一次互斥对账，按“未获标签 → MedMKEB 缺图 → 两个裁判来源 → CPV 缺图 → 其他仅 R5 暂缓 → 纳入”的顺序归因，结果如下。这个表为了对账采用来源级优先归因，和上一张候选范围表的分母不同。

| 从完整已审范围归因 | 单元数 |
|---|---:|
| 未获得任何 R 标签：2,129 证据不足 + 1,901 源问题 + 21 不适用 | 4,051 |
| MedMKEB 缺图元数据 | 2,497 |
| LabTest / EquityMedQA 的全部已分类单元 | 332 |
| CPV 已分类但图像依赖 | 20 |
| 其他来源仅 R5 的已分类单元暂缓（不再重复计算上述两类裁判来源和 MedMKEB） | 18,238 |
| 当前纳入 | 3,105 |
| 合计 | 28,243 |

**更早未取得目标数据的 11 项**

以下是 2026-09-08 冻结取得/审核记录的状态，不能据此宣称今天作者仍未发布。这些属于“未取得目标数据”，不是“先纳入后删除”。

| 来源 | 当时记录的取得缺口 |
|---|---|
| MamaBench | gated 病例未取得。 |
| 肿瘤临床 CF 评测 | 未定位固定原病例发布包。 |
| CLIR-Bench | 所检官方文件树未取得指定 CF 编辑对；普通题不能替代。 |
| ECG-Expert-QA | 未定位 MCo 固定文件；MC 题不能代替目标 MCo 任务。 |
| GenMedicalEval | 只有栏目文档示例，未取得声明的完整题库。 |
| MedEqualQA | 所检作者仓库未取得题库。 |
| CLIMB | 未取得固定诊断 CF 病例对。 |
| DeVisE | 取得生成代码，但未取得受限 MIMIC 固定病例。 |
| MedFuzz | 仅论文示例，未取得完整固定攻击输入 release。 |
| MediEval | 受限患者上下文/知识源尚未取得。 |
| COLLECT | 受限图像包未取得。 |

原记录见 [医学 CF 资源清单](/home/data3/txy/docs/data/sources.md#record-0350) 和 [source_release_notes.json](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/reports/source_release_notes.json)。26 个候选中有 15 个已取得来源，当前 8 个有评测单元；各来源结构化计数另见 [26 来源对照 CSV](/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/r1_r5_source_scope_20260910.csv)。

**能够据实写入实验设置的筛选理由**

**2,500 的决策来源：2026-09-10 核对原始对话后的补充**

用户在 2026-09-08 08:09 的初始请求中允许“大量单一类别”的内容适量取一部分以平衡来源；08:49 又明确说：“少量的指的是1000以下的全收录，大量指的是10000～5000条这种的benchmark可以适量收录少一些。”因此存在适量缩减的授权，但用户没有指定 2,500，也没有指定“满 5,000 即取 2,500”的规则。

2,500 出自助手 08:49:26 的回复，是助手将上述宽泛要求落实成的实施参数。当前文档中的“按用户补充要求执行”不能被读成用户要求了这一具体数值。记录见 [初始请求](/home/data3/txy/.codex/sessions/2026/09/08/rollout-2026-09-08T08-09-56-01a07e59-984e-7580-a306-3d6c68815e99.jsonl:9)、[数量澄清](/home/data3/txy/.codex/sessions/2026/09/08/rollout-2026-09-08T08-09-56-01a07e59-984e-7580-a306-3d6c68815e99.jsonl:612)、[助手设定 2,500](/home/data3/txy/.codex/sessions/2026/09/08/rollout-2026-09-08T08-09-56-01a07e59-984e-7580-a306-3d6c68815e99.jsonl:619)。

现有方案没有给出事先预算测算、目标估计精度/统计功效或样本量稳定性证据来支持“恰好 2,500”。规模控制是实施动机，不能充当样本量已经充分的论证。4,806 条全留而 5,300 条取 2,500 的阈值存在不连续，未实现统一来源上限，更未实现 R 类均衡。2,500 还是分类前的审阅数，后续分类筛选后可能只剩 843 或 2 条，不能当作最终每来源评测样本量。

助手当时还曾承诺“平衡抽样只作为额外分析子集”（[原回复](/home/data3/txy/.codex/sessions/2026/09/08/rollout-2026-09-08T08-09-56-01a07e59-984e-7580-a306-3d6c68815e99.jsonl:538)）；后续当前 v3 继承了这个审阅子集。因此应明确交代这一范围沿用，不能将其表述为用户最初明确规定的正式测试规模。

若继续使用当前结果，应据实称为采用实施性规模限制的探索子集，公开母集、抽样规则和筛选过程，承认 2,500 未经样本量充分性验证。事后补做的分布或结果稳定性分析可以增强现有证据，但不能倒写成最初选择 2,500 的原因。若要主张更完整的来源覆盖，需要先对未抽中记录补齐同标准分类与合格性审阅，再建立独立的新评测版本，复用匹配的已有预测；这不是本次答疑已执行的工作。


大来源使用的是历史规模控制规则：有效比较池小于 5,000 的来源原则上全取，达到 5,000 时分层抽取 2,500；种子为 20260908。MedEinst 按原诊断，CPV 按发布属性组合，其他来源按子任务等分层，并优先覆盖不同原题根。MedCF 另遵守其原 test 划分。该规则不使用项目 R 标签或模型正确性抽样，但确实改变了来源分布，不能称为总体随机代表样本或类别均衡设计。规则见 [分类与抽样说明](/home/data3/txy/docs/data/construction.md#record-0349) 及 [抽样实现](/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/scripts/assemble_full.py:45)。

R5 限定一个来源的直接依据是历史对话中的明确范围调整：2026-09-09 15:48:55（Asia/Shanghai）提出“只收入一个 benchmark，来让数字控制在 2000 以内”；15:56:56 确认推荐的 CPV 方案并要求保留老版。当时选择 CPV 的理由是合格子集 1,090 单元、672 个病例根，可自动判分，且相近题量下比另一候选覆盖更多病例根；其已有预测也可复用。**这属于规模与范围控制，不是其他 R5 benchmark 不合格的证据。** 记录位置：[历史请求](/home/data3/txy/.codex/sessions/2026/09/08/rollout-2026-09-08T14-14-37-01a07fa7-7c43-7132-a803-f6934516590b.jsonl:3006)、[方案](/home/data3/txy/.codex/sessions/2026/09/08/rollout-2026-09-08T14-14-37-01a07fa7-7c43-7132-a803-f6934516590b.jsonl:3053)、[确认](/home/data3/txy/.codex/sessions/2026/09/08/rollout-2026-09-08T14-14-37-01a07fa7-7c43-7132-a803-f6934516590b.jsonl:3060)。

推荐的论文表述：

> 我们从八个公开医学评测来源构建了一个包含 3,105 个评测单元的 R1–R5 功能分类子集。评测沿用冻结来源版本的原任务、输入与参考答案，仅纳入支持当前功能分类、输入完整且能够按固定规则评分的文本任务。大型来源按预定分层规则形成审阅子集；审阅后证据不足、构造无效或不符合五类定义的记录不进入该分类评测。为控制评测规模，R5 仅使用 CPV-MedQA 的全部 1,090 个合格冻结子集单元。重合单元按预定类别规模规则互斥分配。该评测衡量所构建子集上的表现，不代表八个原始 benchmark 的完整测试结果。

**解释结果时的实质限制**

R4 仅 13 个 HIV ART 附录场景，评分是与作者预期答案的一致性；R5 仅 CPV 患者属性变体。因此当前数据不足以支持广泛 R4/R5 来源泛化。分类是项目代理审阅及修正结果，未完成临床专家一致性验证。不同来源保留不同原生评分规则，跨来源总分是项目按单元汇总指标。同一原题的多个变体有关联，CPV、Cultural Cues、AMQA 等还存在 MedQA 血缘，8 个来源不代表 8 个完全独立患者总体。

此前 2026-09-07 的五来源全发布集 M0/M1/M2 结果仍在 [完整实验报告](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0299)，与当前 v3 子集是两个范围。当前 M0–M3 完成的是上述 3,105 单元；不能用早先全发布集的名称为当前四方法表标注覆盖范围。


<a id="r1-validation-source-availability"></a>

## 2026-09-16：R1冻结验证来源可用性

沿用已取得的[ASCENT作者仓库](https://github.com/naver-ai/ascent)固定commit `89091716698d6a2fa78b81d8380e7fec57e73fa5` train/test Arrow，位置`Documents/Codex/2026-09-14/new-chat/r3_generalization_sources/ascent/data/ascent/`；原生任务要求依据全部已有阶段及最后Findings给出boxed诊断，作者评分为GPT‑4.1五次语义/粒度判别，不能把本项目目录准确率称其完整官方指标。资格、病例重合与暴露归[构建主记录](construction.md#r1-frozen-validation-qualification)。CUPCase四选一在当前冻结R1头不激活诊断分支，故本轮不通过改题型将其充作新目录验证。

MedPIC官方revision `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983`仍是467病例，三个文件最后修改2026-07-30，本轮没有新发布病例可取得。历史逐例使用情况不在此重复，见上述构建记录。

取得[RxSafeBench作者仓库](https://github.com/CAS-SIAT-XinHai/RxSafeBench)commit `a25f9a1f173cf034b678c60f051901e86fbbbbb2`的Contradiction/Interaction文件，共2443情景（1063＋1380；538＋696 indication groups）。原生为选择最合适药物的单选任务，当前71规则头需要多选avoid或dose-reduction任务，所以可直接激活0条；不改问题及gold冒充冻结验证。MedGUIDE的癌症决策树不在现规则范围，MedGuideX未取得可核实的对应CF原始发布病例，旧状态/答案协议也未建立兼容。本轮有界来源核对结束，结论是尚无取得且原生兼容的独立用药病例集；这不是证明所有外部资源都不存在。版本、下载及核对证据见[rules/README](../../Documents/Codex/2026-09-16/r1_head_validation/rules/README.md)和[source_qualification.json](../../Documents/Codex/2026-09-16/r1_head_validation/rules/source_qualification.json)。


<a id="r4-structural-sources"></a>

## 2026-09-17 R4结构执行：形式因果与临床后果来源

本次为[R4持续开发](../research/r4_consequence_head.md#r4-structural-execution)寻找有明确机制与可追溯答案的材料，不改变正式v5。原件和逐来源读取边界见[方法来源附件](../../Documents/Codex/2026-09-17/r4_structural_head/causal_method_scout.md)与[临床来源附件](../../Documents/Codex/2026-09-17/r4_structural_head/clinical_source_scout.md)。来源论文/官方代码可用性与数据的医学资格分别判断。

| 来源 | 实际取得/核读 | 当前用途与边界 |
|---|---|---|
| [CLadder](https://github.com/causalNLP/cladder) | 官方主zip、模型元数据、MIT许可及确定性查询/机制代码快照；balanced10112中det-counterfactual1422 | 可作明示布尔结构的形式诊断；不是临床验证，资格和暴露见[构建记录](construction.md#r4-structural-source-qualification) |
| [Executable Counterfactuals](https://huggingface.co/datasets/Raidriar-Dai/executable-counterfactuals) | 9个公开配置可访问，读code/math首例与字段；官方GitHub main仅README | 隐状态及多解参考；未取全数据、未适配，外部执行将改变作者纯LLM协议 |
| [LabTest](https://github.com/balubhasuran/LLM_Causality_LabTest) | commit `6d0fbd1bc42cf604258f0fde4317a542d0b9090f` 的42150字节XLSX及48850字节生成脚本 | 99问题两LLM重复成198行，33反事实；四名医师Yes/No评价的是保存的LLM答案，不是问题答案。本工作区此前已暴露30 R4，不能作为新精确gold |
| [CLIR-Bench](https://huggingface.co/datasets/winall/CLIR-Bench) | revision `e7e1733b74819bbefa2a1b5bf653a0d1e00fbb9a` 仓库树11×600文件、论文定义，未下载任务正文 | intervention-response描述已发生干预；counterfactual-evidence-edit不提供改变治疗后的未知临床结局。本次是任务不匹配，不只是未下载 |
| [IHDP-post](https://github.com/Aurora-Brooks/Spiked-CFR-Benchmarks) | commit `8355e5461fd1293bbb6daed3c23a71f32f7c4a45` 的1231784字节/747行CSV；全文读unit0 | 半合成治疗效应结果＋LLM文本，首行将数值写成−0.53kg体重/−0.34cm头围，字面物理不成立；未追溯生成原因、未悄悄修复。非可直接零样本临床QA真值 |
| [simglucose](https://github.com/jxx123/simglucose) | commit `a6f6777586c860457a2a1e6cce6d0bd3fd33d1cc` 的13状态ODE、30虚拟患者参数、环境/餐食文件、MIT许可 | 医学生理模型条件下的后果方向候选，同日后续已完成adult#001单profile CPU冒烟；10成人/10青少年/10儿童，不把多时点计成新患者。开源实现有[PLOS ONE使用证据](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0274608)，不等于本数据或该版本获FDA批准 |

simglucose源代码说明胰岛素输入U/min、餐食克数按事件输入；`observation.Gsub`是皮下葡萄糖而非血浆葡萄糖。公开参数释义自称推测性社区说明，不能替代实际方程。匹配干预血糖[2026预印本](https://arxiv.org/html/2605.00645v1)的paired数据仍称接收后发布，匿名代码检索失败；未声称已取得，也不把论文100成人队列等同这30公共参数。是否采用数值机制还需确定与当前布尔头的边界、对两臂同等充分的输入及模拟真值核验。

原件统一在`Documents/Codex/2026-09-17/r4_structural_head/sources/cladder/`及`source_scout/`；未取得资源、访问失败和仅元数据核读均保留在附件，不能据一次失败声称来源不存在。初次取得阶段为0新模拟、0该来源LLM预测；后续取得和运行状态如下，方法开发另记。

<a id="r4-physiology-source"></a>

**同日后续：simglucose作者实现可运行。** 复用上述固定commit的patient实现和参数原件，补取同版本`patient/base.py`及包初始化文件，连同MIT许可保存于`r4_structural_head/physiology_probe/author/`，取得记录为该包`patient_support_acquisition.json`。仅adult#001的作者完整初态/辅助记忆下配对轨迹完成CPU验证；数值、单位与运行边界只在[R4主记录](../research/r4_consequence_head.md#r4-physiology-probe)维护，6开发/24保留及仅1profile实际暴露见[构建记录](construction.md#r4-physiology-development-split)。

相关[From Prediction to Practice，arXiv:2605.00645v1](https://arxiv.org/html/2605.00645v1)已读§3.3、Appendix B及Availability，原HTML和[阅读附件](../../Documents/Codex/2026-09-17/r4_structural_head/physiology_probe/papers/paper_reading.md)留存。原文固定subject、seed、历史与未来餐，仅改变未来胰岛素；本地借鉴配对思想，不是其100成人、15天默认MPC流程复现。匿名代码链接取得失败和配对数据待接收后发布分别保留，不能一并写成代码未发布，也未声称取得作者配对数据。当前来源用途为模型条件后果开发，不是新的真实患者临床gold。


**同日有界补查：发表的细胞命运布尔机制。** 为判断是否能在不扩成数值生理工具的前提下检验当前布尔head，取得[PhysiBoSS Boolean models](https://github.com/PhysiBoSS/boolean-models)的`fb904c0fa0dacec92799cb7c1e683d3b1ed79b4f` TNF模型、配置及BSD-3许可。已读模型/配置全文及[Calzone等2010原论文](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000702)相关模型部分。该发布物含反馈和随机异步速率，不能原样送无环布尔执行器，也不能称真实患者标签。若以后采用有限同步时间展开，必须声明新条件及两臂同等可见状态；当前未模拟、未建题、未生成gold。取得与实际读取边界见[源附件](../../Documents/Codex/2026-09-17/r4_structural_head/sources/cell_fate/README.md)。GitHub网页取得失败后API/raw成功，不把失败伪装不存在。

2026-09-17补充：已取得PhysiBoSS固定commit `fb904c0fa0dacec92799cb7c1e683d3b1ed79b4f`下TNF、AGS胃癌、generic前列腺三个网络原bnd/cfg、BSD3许可及三篇原论文官方XML（前列腺另PDF）。TNF复用既有下载；无新GPU/LLM调用。取得记录、真实网络版本与论文差异见[冻结来源审核](../../Documents/Codex/2026-09-17/r4_structural_head/biological_source_qualification.md)，文件在该包`sources/biological_models/`。正式任务仍为R4机制探索，未新增临床gold或正式v5来源。

<a id="hiv-full-data-20260917"></a>

## HIV ART完整机器表与作者代码取得（2026-09-17）

本次由论文Data/Code Availability定位作者[OSF egtyw](https://osf.io/egtyw/)，公开API取得60行dataset.csv与CODE.zip；dataset_extra.csv仅定位未下载。原机器表包含20关联、20干预、20反事实及六专家评分。20个CF按query_idx与旧附录转录核对，NFKC和空白归一化后题面20/20、作者答案20/20一致，新增CF为0。更早“完整研究题库未取得”是当时获取状态，现已补足60题原表；不改旧冻结收集数量及v5范围。

原件、公开清单、取得记录及对应关系在`Documents/Codex/2026-09-17/r4_structural_head/method_revision/clinical_sources/`，详见[方法核读附件](../../Documents/Codex/2026-09-17/r4_structural_head/method_revision/clinical_methods.md)。公开代码已静态核读目标Llama/no-PDF和带PDF路径，未执行；凭据样式字串仅在本地归档副本脱敏，记录保留。专家评分对参考资格的含义见[建设记录](construction.md#hiv-expert-ratings-20260917)，方法采用见[R4主记录](../research/r4_consequence_head.md#r4-source-method-revision)。


<a id="r5-bionli-supervision-source"></a>

## R5监督研究：BioNLI作者balanced原件（2026-09-18）

由[作者官方仓库](https://github.com/StonyBrookNLP/BioNLI)定位[balanced公开文件夹](https://drive.google.com/drive/folders/1-zNfaoDdszvu8cTCRqx9s1EWM2qZ0wcI)，已取得train_balanced.csv、dev_balanced.csv和当日实际公开列出的test.csv原始字节。仓库README的“test需联系作者”与当前公开目录状态有差异，按真实取得状态记录；未发送邮件或联系第三方。full文件夹跳转登录，未取得，论文表内full规模不记为本地已获取。官方BioNLI README明示CC BY 4.0；这不自动改变此前BioRAB派生包的许可核查状态。

原件与作者仓库说明保存`Documents/Codex/2026-09-18/r5_head/mechanism_research/bionli_author_sources/`，作者代码版本`1aa25c4abfa4b5d05a3102c85f4949cdaf97277a`；训练原件9,686,555 bytes、SHA256 `41a144a904c3080a1683425b7dccee9815b17cf8a6a317b397bab9abbee64ca0`。取得URL、各文件哈希及可复跑身份清点见[bionli_supervision_inventory.json](../../Documents/Codex/2026-09-18/r5_head/mechanism_research/bionli_supervision_inventory.json)。test原件仅提取文章身份/前提作排重，未用其假设或标签作方法选择。实际行数、作者dev交集及可训练范围由[构建主记录](construction.md#r5-bionli-supervision-construction)维护，训练方法归[R5研究主记录](../research/r5_invariance_head.md)。


<a id="r5-cad-premise-supervision-source"></a>

## R5辅助前提监督：CAD作者RP/RH来源及许可（2026-09-18）

为检查固定假设H而实质改变前提P的监督缺口，取得[Kaushik、Hovy、Lipton，ICLR 2020](https://arxiv.org/pdf/1909.12434v2)作者[公开仓库](https://github.com/acmi-lab/counterfactually-augmented-data)，固定commit `6f232a1d2a11462a30ce08fb4825b734ab30828e`，GitHub提交时间2021-04-26T17:51:49Z。19:41取得original与revised_premise的train/dev/test六个原始TSV；19:48另取得revised_hypothesis的train/dev两个TSV，未取得RH test正文。README、LICENSE、commit与完整文件树API原件一并保留。网页目录首次抓取技术失败后公开API/raw成功，不涉及登录、受限数据或模型下载。

论文§3明确RP由人工保持H、改P以对应另外两个NLI类，RH反向保持P、改H；改写后另由三名标注者验证，一致时采纳其裁决，不一致时作者复核。这建立了人工反事实来源身份，**不保证每条发布记录都正确**；本次实核发现相同P/H带不同gold等问题，详见[资格主记录](construction.md#r5-cad-premise-supervision-qualification)。来源为SNLI日常图像描述句的英文NLI，不是医学病例，不是本工作区R5保持评测，不能直接充当医学R5泛化验证。

固定原件实数如下；original[i]、RP[2i:2i+2]及RH相同位置的结构关联、实际问题和二类映射由构建记录维护。

| 作者划分 | original | RP | RH本次实际取得 |
|---|---:|---:|---:|
| train | 1,666 | 3,332 | 3,332 |
| dev | 200 | 400 | 400 |
| test | 400 | 800 | 未取正文，仅固定树中存在 |

[固定commit的LICENSE](https://github.com/acmi-lab/counterfactually-augmented-data/blob/6f232a1d2a11462a30ce08fb4825b734ab30828e/LICENSE)为Apache-2.0；但[SNLI官方来源页](https://nlp.stanford.edu/projects/snli/)明确SNLI为CC BY-SA 4.0，且包含同为Attribution-ShareAlike来源的Flickr30k描述。记录应同时保留CAD、SNLI及上游归属，不能把仓库顶层Apache声明解释为已替代所有派生文本的上游条件。本次确认公开研究使用来源可取得，未作统一再许可或发布衍生文本的决定。

全部原件在`Documents/Codex/2026-09-18/r5_head/mechanism_research/premise_supervision_source/`；[取得清单](../../Documents/Codex/2026-09-18/r5_head/mechanism_research/premise_supervision_source/download_manifest.json)及[补充清单](../../Documents/Codex/2026-09-18/r5_head/mechanism_research/premise_supervision_source/supplement_download_manifest.json)保存每个文件URL、字节和SHA256，后者另含论文v2 PDF与SNLI官方网页快照。论文实际核读范围为摘要、引言有关NLI部分、§3 NLI收集及审核、Table 4、§5 NLI结果与Tables 7–9，未声称全文逐页读完。使用CAD扩增及RP/RH对照是已发表方法；新机制研究不得将它重新命名为原创算法。具体因果增量检验与方法选择由[R5研究主记录](../research/r5_invariance_head.md)维护，本次0模型调用、0特征提取、0训练。
