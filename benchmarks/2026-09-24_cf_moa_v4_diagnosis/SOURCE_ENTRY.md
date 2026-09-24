# v4 F触发路径：源码阅读入口

本公开包发布已导出的现有源码、冻结版本和来源差异；没有模型调用、回放或原生评分，也没有修改默认方法。持续研究结论由[诊断报告](DIAGNOSTIC_REPORT.md)承载。逐文件真实来源、SHA、当前文件SHA和差异位置见`source_manifest.json`；源码观察见`source_findings.json`。当前范围73份文件（含来源plan、差异与一次性导出脚本），约0.96MB。

## 先读这些位置

|层|包内路径（相对`source/v4_reanswer/`）|入口|
|---|---|---|
|真实新增推理|`cf_moa/evaluation/minimal_f_runner.py`|固定plan、输入和物理请求绑定；调用已有`execute`|
|实验分支|`cf_moa/evaluation/effect_first_runner.py`|`execute`的`a5_reanswer`分支调用`a5_premise.run(control=True)`|
|分歧与替换|`cf_moa/agents/a5_premise.py`|`competition`、`request`、`parse_key`、`run_proposal`、`run`|
|旧F适配器|`cf_moa/agents/a5_robust_readout.py`|`run_legacy`，不是历史负候选`run_views`|
|采用F算法|`Documents/Codex/2026-09-18/r5_head/delivery/r5_head.py`|`optimize`、`decide_paths`、`catalog_aggregate`、`aggregate`；仅标准库依赖|
|旧B能力与完整输出|`cf_moa/controller/strong_legacy.py`、`baseline_native.py`|`select`与`wrap`|
|模型请求和解析|`cf_moa/tools/adapters.py`、`native_backend.py`、`vllm_backend.py`|`ModelSession`、`native_json`、`messages_with_instruction`、`prepare`、`interpret`、`generate_batch`|
|profile与来源|`cf_moa/tools/adopted.py`、`configs/native_sources.json`、`readout_m4.json`、`readout_m5.json`|`profile(method,'readout')`；逐字段原样复制|
|离线评分|`cf_moa/evaluation/native_scoring.py`、`score_run.py`、`paired_metrics.py`|原生`norm/parse/score`按AST载入；不进入推理|

原生grader、normalizer，以及本轮`score_and_compare.py`/旧`score_development.py`放在`source/offline_evaluation_only/`。评分器只读取保存答案与离线评测对象；没有把gold拼入模型请求。逐题实际schema/messages/prompt以服务器私有样本JSON为准；本公开包不含这些正文。95组均为F支持格式，不执行diagnosis评分分支；诊断canonical全量表仅记原路径/hash，不随包复制。导出准备期一度自动复制该文件和未用import依赖，随后40个新复制副本已排除；未将它们用于样本分析或推理，原文件不变。

## 三个来源阶段必须分开

- `source/historical_F_acquisition/`：历史121旧F实际采集时的文件，按其`f_complete/m4/plan.json`锁定。旧`a5_robust_readout.py`与当前不同，已优先保留旧版本；静态对比确认`run_legacy`相同，差异在另一候选`run_views`。原采集backend/adapter也保留原SHA版本。
- `source/cycle1_seed42/`：121 seed42在旧cycle1真实运行的三份源码。其`effect_first_runner.py`为`090d9d…`，不能用后来`229f64…`文件冒充；`source/diffs/cycle1_seed42/`给出完整差异。`a5_reanswer`调用分支和`a5_premise.py`本身未变。
- `source/v4_reanswer/`：v4新增seed43/44和自然52三seed所绑定的源码；优先复制其`seeds/code_snapshot/`或其他逐字匹配的已保存文件。当前文件与锁定SHA相同才作为等价来源。只附实际F调用及必要基础helper；未执行的A1知识审计、A3编辑、single-agent等import文件名列在manifest，不打包其整条实现链。

`source/provenance/`保留小型实际plan/收据；`source/diffs/`保留六份已发生版本差异。默认系统外层与配置虽再次随链路提供，主要补充是此前缺失的被调模块。

## 源码可直接确认的行为

1. 旧F的NLI分支显式重复当前问题，并定义positive为整个hypothesis受premise支持，negative为未完整支持。每路径两个A/B语义映射先各自softmax映射回native键，再平均四个分布，最终完整响应的键由schema固定。不是四份独立生成答案投票。
2. 非NLI分支生成完整原生响应，最多五次；某键得三票即早停，平票按最早样本；完整返回被选中的原始响应。未生成的第四/第五次不是缺失样本，不补跑。
3. 触发仅看旧F已有语义键是否至少两种；NLI看四个映射赢家，普通看实际生成键。它不估计新重答净收益，也不按gold筛题。
4. 普通重答保留全部原始messages，追加完整当前题、检索上下文和`model_input`。该`control=True`指令不附竞争答案、票数或当前F答案；也没有重新追加旧F特有的NLI `RULE`与`CURRENT_QUESTION`定位包装。原始上下文是否已充分包含该语义定义，应结合实际样本判断。这是可见提示差异，尚不是因果性代码错误。
5. 触发后读出新native键，直接替换F的键和解释；不并入旧F投票/分布，也无第二裁决。旧辅助字段（包括需要时的`errors`）保持原值。这是事前输出合同，但跨字段医学一致性仍需样本核查。
6. 解析允许完整answer-first键后可选reason不完整，键本身不可读才作一次预定格式修复。本轮已发表的231新增请求无修复，不能把允许路径当本轮实际发生的失败。

## 环境与来源限制

`source/template_metadata/`仅复制两模型的当前`tokenizer_config.json`、special-token/model小配置，未复制权重或tokenizer词表。旧日志保存了真实渲染prompt；历史没有为每个模板文件存运行前SHA，因而当前模板文件不冒称运行前冻结版。M4为Llama-3.1-8B-Instruct，M5为Qwen3-8B；M5设置`enable_thinking=false`与YARN上下文参数，完整profile保留。两个readout均0.7/2048，而本轮普通重答显式0.7/512，NLI旧F分析/完整输出为0/2048；各自身份不可混写。

外部运行依赖为Python 3.10、vLLM、PyTorch、Transformers/tokenizers、msgspec、xgrammar、jsonschema；numpy/scipy属于旧评分脚本环境（实际原生parse/score仅提取指定函数）。后台优先插入`adopted.EXTRA_SITE`再从主venv补齐依赖。当前包元数据可见vLLM0.8.5、PyTorch2.6.0、xgrammar0.1.18、msgspec0.21.1、jsonschema4.26.0；EXTRA_SITE为Transformers4.51.3/tokenizers0.21.4，主venv另有5.16.1/0.23.1。此为当前安装记录，不补造每轮实际import版本证明。

冻结hash覆盖并不完整；`source_manifest.json`明确逐文件区分run-hash-bound、未完整锁定辅助依赖、当前模板元数据及本次导出工具。这是定向源码证据包，不是完整可移植软件发行或全仓库正确性认证。无凭证、模型权重、检索索引和无关缓存。

公开范围补充：原B来源收据包含一条通用选项文字的历史parser失败片段，保留其真实身份；本包不含完整病例请求响应。详见[源码发布审阅](verification/source_publication_review.json)。另附[三个导出与分析脚本](analysis_code/README.md)，不计入上述73份运行调用链文件。
