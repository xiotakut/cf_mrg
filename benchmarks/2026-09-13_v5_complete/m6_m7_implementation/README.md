# M6 i-MedRAG / M7 TC-RAG 比较方法接入

本目录是 `xiotakut/cf_mrg` 的服务器运行包。按用户2026-09-13命名，**M6 = i-MedRAG，M7 = TC-RAG**。入口已注册至既有 `cf_medrgag_validation_pack/scripts/run_iterative_baselines.py`，执行标识仍为 `imedrag`、`tcrag`。复用现有完整 MedCorp、BM25＋MedCPT 检索实现、冻结 v5 输入与原生评分器；新增同权重 Transformers 生成后端以提供 TC-RAG 所需的完整分布熵。

| 论文/比较编号 | 方法 | 命令与结果中的执行标识 |
|---|---|---|
| M6 | i-MedRAG | `imedrag` |
| M7 | TC-RAG | `tcrag` |

后续论文与比较表统一使用上述编号；既有配置、命令、run目录和预测保留原执行标识，编号调整不改变实验身份或缓存。

TC-RAG 按用户指定使用 **Qwen3-8B，关闭 thinking**；i-MedRAG 使用当前 M4 的 **Llama-3.1-8B-Instruct**。比较各自同 backbone 的 M5/M4 时仍需披露生成引擎和阶段预算差异。论文的7个QA benchmark是方法来源设置，本包继续使用服务器已确认的 R1–R5 v5。

实现依据和补丁见 [method_fidelity.md](<method_fidelity.md>)，输入、证据权限和评分规则见 [evidence_protocol.md](<evidence_protocol.md>)。实际完成情况、成本及限制以 [acceptance_report.md](<acceptance_report.md>) 为准。

后续论文写作从 [PAPER_REPRODUCTION_RECORD.md](<PAPER_REPRODUCTION_RECORD.md>) 开始：其中记录实际完成的工作、逐项适配、全部试跑与修复顺序、最终配置来源、缓存复验、新增计算量及结论边界。

## 文件

| 文件 | 用途 |
|---|---|
| `code/methods.py` | 两方法注册与真实控制流 |
| `code/backend.py` | 相同权重生成、完整分布熵、独立请求合批、复用检索器 |
| `code/runtime.py`、`code/run.py` | 请求缓存、原子尝试收据、轨迹、恢复、完整分母 |
| `code/prepare.py`、`code/check.py` | 冻结既有输入和显式展开映射、资源和长度检查 |
| `code/score.py`、`code/report.py`、`code/cost.py` | 离线原生评分、轨迹审计、实际成本估算 |
| `configs/*runtime_v4.json` | 实际共享GPU执行配置；保留较早配置和pilot |
| `data/input_manifest.jsonl`、`source_target_input_mapping.jsonl` | 13905输入及source→unit→target→input映射 |
| `data/dev_inputs.jsonl` | 24条固定独立训练/开发输入，gold另存 |
| `runs/*/items/*/{requests,attempts,events}` | 完整prompt、输出、真实检索材料、逐步活动记忆 |
| `runs/*/{resolved_config,predictions,progress,complete}` | 每次运行的配置、正式终态与覆盖记录 |

大段数据、轨迹、上游checkout和模型不纳入代码发布包；在服务器保留可恢复路径及哈希。`data/input_lock.json` 保留原输入、候选/抽样协议、入选映射和评分资源的固定引用。13,000判断不等于LLM调用数；正式范围每方法为6,104单元、13,905唯一输入、15,616原生评分记录。

## 环境与准备

以下使用已经安装并实际运行的环境，无需再安装另一套依赖。`configs/environment.json` 与 `configs/requirements.lock.txt` 记录现有版本。准备脚本使用已有包含pyarrow的环境；模型生成使用MedRAG基线环境。固定模型权重和tokenizer身份见 `configs/resources.json`。

```bash
cd /home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc
BASELINE_PY=/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python
PREP_PY=/home/data3/txy/MedRGAG/.venv/bin/python

"$PREP_PY" code/prepare.py
"$BASELINE_PY" code/check.py
"$BASELINE_PY" -m unittest discover -s tests -v
bash -n run.sh
```

这些命令已在本机验证。`prepare.py` 验证并复用冻结数据，不重新抽样；若文件内容发生变化会报错。资源初次锁定命令 `"$BASELINE_PY" code/prepare.py --resources` 也已执行，但日常运行直接使用已锁定配置。`run.sh` 配置Java21、离线权重加载及可扩展显存分配器；CUDA设备通过调用环境明确指定。

## 开发验收和恢复

```bash
CUDA_VISIBLE_DEVICES=1,2 bash run.sh imedrag \
  --config configs/imedrag_runtime_v4.json \
  --inputs data/dev_inputs.jsonl --run-dir runs/imedrag_dev_accepted --workers 4

CUDA_VISIBLE_DEVICES=1,2 bash run.sh tcrag \
  --config configs/tcrag_runtime_v4.json \
  --inputs data/dev_inputs.jsonl --run-dir runs/tcrag_dev \
  --verify-backend --workers 4

```

i-MedRAG最终验收目录为`runs/imedrag_dev_accepted`。其全部521次模型请求和279次检索来自实际模型运行的原始收据；最后一步仅重放并转换官方单引号示例的输出语法，没有新模型调用。递归`cache_provenance.json`连接到原始完整运行`runs/imedrag_dev_v4`，中间失败结果与源码快照均保留。吞吐和成本使用真实生成收据及原始完整运行时间，不能用1.6秒缓存重放时间估算正式运行。Llama熵后端对照证据位于原始运行的`backend_reference.json`。

TC阈值保持官方代码默认1.2。本轮仅执行两种方法各24条训练/开发输入；按用户最新要求撤下额外正式题盲测及阈值校准。早先准备的输入映射保留为既有benchmark接口核对记录，未触发正式模型评测。

`bash acceptance.sh`已在两方法完成后实际执行：验证终态恢复、重算离线报告和成本，不启动正式清单。

恢复时原样重复同一个命令：成功终态不会重新推理，中间成功请求从收据恢复；参数或源码改变则拒绝继续写入同一run。失败终态保留在正式分母内。要复验工程修复，使用新配置/运行目录并保留原失败记录。

```bash
"$BASELINE_PY" code/run.py imedrag --audit-only \
  --inputs data/dev_inputs.jsonl --run-dir runs/imedrag_dev_accepted
"$BASELINE_PY" code/report.py --inputs data/dev_inputs.jsonl \
  --run-dir runs/imedrag_dev_accepted
"$BASELINE_PY" code/score.py --split dev --run-dir runs/imedrag_dev_accepted
```

离线评分必须在全部预定输入有终态后进行，失败/无效不删分母。`report.py` 不读取gold。TC-RAG以相同方式审计/评分 `runs/tcrag_dev`。

## 正式运行

本轮不启动整套正式评测。下列为已接入入口的完整范围命令；全量GPU执行尚未验证，实际开发运行、离线准备和预检查证据见验收报告。执行前需结合成本报告确认正式预算。

```bash
CUDA_VISIBLE_DEVICES=1,2 bash run.sh imedrag \
  --config configs/imedrag_runtime_v4.json \
  --inputs data/inputs.jsonl --run-dir runs/formal_imedrag_v4 --workers 4

CUDA_VISIBLE_DEVICES=1,2 bash run.sh tcrag \
  --config configs/tcrag_runtime_v4.json \
  --inputs data/inputs.jsonl --run-dir runs/formal_tcrag --workers 4

"$BASELINE_PY" code/score.py --split formal --run-dir runs/formal_imedrag_v4
"$BASELINE_PY" code/score.py --split formal --run-dir runs/formal_tcrag
```

两个模型顺序运行以适配当前GPU余量。正式恢复使用相同命令，不更改目录内resolved配置。全量完成判定为所有13905输入均有ok/invalid/failed终态，pending=0、未知ID=0、重复正式结果=0；运行有效率与准确率分别报告。
