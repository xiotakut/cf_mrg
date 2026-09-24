# 实际调用链与配置层次

本轮唯一新操作是选择已存在的完整旧F候选响应。旧Router与R1–R4、采用F保持；本目录的源码可审阅，但模型权重、私有输入和完整运行环境不随包发布。

1. `plan/runtime_plan.json`绑定95组样本路径/哈希、两骨干载入profile、固定smoke、预算、源码哈希及保护文件。模型权重路径为服务器本地路径，不是公开下载内容。
2. `source_snapshot/cf_moa/evaluation/candidate_verify_runner.py`从同一合法输入/旧F提议取候选，经`effect_first_runner.execute`进入`agents/a5_candidate_verify.py`。
3. `candidate_records`使用旧`trace.predictions/responses`，每个不同合法键取最早完整响应，全部键保留。`verifier_messages`保留完整合法题面/证据；两臂仅区别是否附不可信旧理由。没有票数、F赢家、gold或来源ID在线输入。
4. 每候选两次A/B语义交换调用既有`ModelSession.score`，逐映射归一再求语义概率均值，最大者胜出；程序返回其整份旧响应，不重生成或拼接辅助字段。NLI原F直返。
5. `source_snapshot/cf_moa/tools/native_backend.py`、`adapters.py`、`vllm_backend.py`与journal保存真实调用；取分路径依赖的旧采用代码见[已公开实际旧调用链](../2026-09-24_cf_moa_v4_diagnosis/SOURCE_ENTRY.md)。本包另收录六份保护源文件，逐字哈希确认未改。
6. 最终离线评分源码为[analysis_code/score_candidate_experiment.py](analysis_code/score_candidate_experiment.py)，复用原生评分与配对函数。其最后一次空NLI分母修复发生在冻结推理启动后，版本差异明确见[分析修订收据](evidence/analysis_revision_receipt.json)与[diff](evidence/analysis_fix_empty_nli/fix.diff)。启动快照内旧分析源码保留，不能混作最终分析版本。

**参数有两个层次。** runtime_plan里的原readout profile仍为temperature=0.7、max_tokens=2048等；这用于原模型/引擎配置，保留两骨干各自差异。实际本轮`ModelSession.score`按既有取分入口发送temperature=0、max_tokens=1、seed=42及A/B候选代码，这不是把旧F生成参数静默改为0。两模型均BF16，max_model_len=131072、num_gpu_blocks_override=16384；M5另有原YaRN与enable_thinking=false。实际每请求参数和接受状态见公开调用元数据，完整消息与engine输入IDs留私有SQL。

**运行时修复。** 原M4 32次初始化失败来自共享引擎启动故障没有立即升级，导致同一smoke重复尝试。新代码识别`Engine core initialization failed`并传播journal已标记的系统故障；只停受影响骨干，不改变普通单题错误继续/保留分母政策。20项针对回归与方法AST核对见[验收](evidence/runtime_test_receipt.json)、[原样diff](evidence/runtime_recovery.diff)。推理完成后终检全部190响应身份、780物理调用和两engine关闭见[终检](evidence/final_runtime_receipt.json)。

源码快照采用运行时字节。`source_snapshot/Documents/Codex/...`中的路径层次用于维持原来源可定位性，属于冻结launch/supervisor/分析源；`analysis_code/`是最终已执行分析修订。源码中的路径和公用提示是复现配置，不是实际患者messages。历史源依赖、当前源码与运行冻结版有差异时，以本包runtime_plan及对应快照为准。

发布核读另外确认实际返回模式：全部780条constructed `sampling.output_kind=0`，engine为2。本地vLLM `entrypoints/llm.py:1350`在添加请求前将其设为`RequestOutputKind.FINAL_ONLY`；公开元数据保留两值。取分解码参数一致不等于整个sampling对象逐字段相同；这是返回模式归一，无新模型/方法修改。
