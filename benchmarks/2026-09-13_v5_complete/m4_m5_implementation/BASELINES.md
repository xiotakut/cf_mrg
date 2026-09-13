# MedRAG：M4（Llama 3.1）与 M5（Qwen3）

> 2026-09-11 V5 更新：用户要求 M4 与 M5 设置一致，仅保留 Llama 模型。当前 V5 使用 [独立评测配置](<../execution/results_v5_m0_m2_m4_m5/configs/m4.json>)（完整 MedCorp、BM25/MedCPT、top8、temperature0.7），不等待 RRF。下文及本安装目录 configs/m4.json 保留原始安装配置与索引任务的历史含义，不作为 V5 的生效配置。

> 2026-09-12 历史核对：已补写 [M4 / M5 完整安装报告](<M4_M5_INSTALLATION_REPORT.md>)，包含原始执行命令、修改清单及验证证据。后续 V5 的 M4、M5 已各完成 13,905 个输入，见 [正式结果](<../execution/results_v5_m0_m2_m4_m5/RESULTS.md>)。旧 RRF 的 Wikipedia MedCPT 索引已完成，Contriever、SPECTER 及准备启动脚本已停止，部分文件保留。

论文写作统一使用 [M4 / M5 安装、调整与论文实施记录](<M4_M5_INSTALLATION_REPORT.md>)。2026-09-13 已补充逐项调整台账、原生提示与评分细节、中英文方法草稿；后续相关工作继续记录在同一文档。

安装目录就是本仓库；上游为 [gzxiong/MedRAG](https://github.com/gzxiong/MedRAG)，
基于 commit `7599a728a28789fd601728c08d313b1148051f41`。
独立 Python 3.10 环境在 `.venv`，完整依赖版本见 `requirements-baseline.lock.txt`。
模型权重通过 `models/` 的软链接复用本机已有文件。

本次依据工作区已有项目，将两篇 SOTA 理解为
[MedRGAG（WWW 2026）](https://arxiv.org/html/2510.18297v1)
和 [MA-RAG（ICML 2026）](https://arxiv.org/html/2603.03292v1)。

接续当前 R1–R5 benchmark 的 M0–M3，按 Llama、Qwen 的顺序编号为 **M4、M5**。
配置与输出的 `method_id` 分别为 `M4`、`M5`；`method` 分别为
`medrag_llama31`、`medrag_qwen3`，用于与已有记录关联。

| 编号 | 配置 | Backbone | 检索 | 最终文档数 | 解码 |
|---|---|---|---|---|---|
| **M4** | `configs/m4.json` | Llama-3.1-8B-Instruct，BF16 | Textbooks + Wikipedia；BM25、Contriever、SPECTER、MedCPT 经 RRF-4 融合 | 5 | temperature=0.2 |
| **M5** | `configs/m5.json` | Qwen3-8B，BF16 | 完整 MedCorp 四语料；每库 BM25 top-32，MedCPT Cross-Encoder 重排 | 8 | temperature=0.7，enable_thinking=false |

两者均保留上游 MedRAG 的单轮检索、CoT/JSON 答案提示和 question-only 检索。
M5 对应 MA-RAG 论文中的 **SR-RAG**；不含多轮 agent、候选投票或训练模块。

## 安装阶段验证与后续状态

- 依赖检查及导入通过：PyTorch 2.6.0/CUDA 12.4、Transformers 4.51.3、Pyserini 1.0.0。
- Java 21 复用 `/home/data3/txy/.cache/jdk/temurin21`；Git LFS 3.0.2 安装在本环境，并仅对本仓库初始化。
- 两个真实 8B 模型均通过 GPU 推理检查，给定片段均回答 A。
  原始输出在 `runs/smoke_llama31.jsonl` 和 `runs/smoke_qwen3.jsonl`。
- Qwen 的 **完整 MedCorp → BM25 → MedCPT → 8 篇文档 → 生成** 已通过，
  记录在 `runs/smoke_qwen3_full_medcorp.jsonl`。
- StatPearls 从 NCBI 重新下载并成功解包，上游 chunker 处理 9,648 个 XML，
  生成 9,646 个非空分片；BM25 索引包含 **372,148** 篇片段，索引错误为 0。
  本仓库使用该新副本；另外三个语料复用本机已有 chunk、BM25 索引及行偏移。
- Textbooks 的三个稠密索引均已完成，每个含 **125,847** 个 768 维 FP32 向量。
  Llama 的真实 **BM25 + 三路稠密检索 → RRF-4 → top-5 → 生成** 已在 Textbooks 上通过，
  输出为 `runs/smoke_llama31_rrf4_textbooks.jsonl`；这是明确覆盖语料的流程检查。
- 三个 Wikipedia 稠密索引于 2026-09-10 启动构建；MedCPT 在 09-11 完成，含
  **29,913,202** 个向量。后续 V5 改用统一的 BM25/MedCPT 设置后，Contriever、SPECTER
  和旧准备启动脚本已停止，分别保留 287/646、250/646 个 embedding 分片。
  `.cache/prepare-processes.json` 和 `.cache/prepare-{contriever,specter,medcpt}.log` 是历史记录。
  三路未全部完成，因此完整 Textbooks + Wikipedia RRF-4 冒烟未执行，
  `.cache/rrf4-complete.txt` 不存在。以下 `--check` 检查本目录的独立历史配置；
  M4 缺资源时退出码为 1，不代表后续 V5 M4 未完成。

```bash
./run_baseline.sh --variant m4 --check
./run_baseline.sh --variant m5 --check
.venv/bin/python test_baselines.py
```

## 使用

每行一个 JSON 对象：`id`、`question`、`options`（选项标签到文本的字典）。
入口支持 `--variant m4` / `m5`（也接受大写 `M4` / `M5`）；
此前的 `llama31` / `qwen3` 命令仍映射到同一配置，供已启动的准备任务使用。
需要复用外部检索时，可额外提供 `snippets`（含 `id/title/content` 的数组）；
此时跳过实时检索，输出明确标为 `provided_snippets`。
输入示例见 `examples/retrieval_smoke.jsonl` 与 `examples/smoke.jsonl`。

```bash
# 指定空闲 GPU；输出必须是新文件。
CUDA_VISIBLE_DEVICES=1 ./run_baseline.sh --variant m4 \
  --input examples/smoke.jsonl --output runs/my_m4_smoke.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant m5 \
  --input examples/retrieval_smoke.jsonl --output runs/my_m5_retrieval_smoke.jsonl

# 稠密索引齐备后，Llama 可同样使用不带 snippets 的输入。
CUDA_VISIBLE_DEVICES=1 ./run_baseline.sh --variant m4 \
  --input questions.jsonl --output runs/my_m4_predictions.jsonl
```

输出包含最终响应、实际检索片段和分数、完整模型消息、原始生成文本、
重编码得到的输入/输出 token 数、逐题耗时，以及实际使用的配置。
检索上下文保留上游 `context_length` 裁剪规则，并记录 `context_truncated_tokens`；
完整提示加输出预算超限时直接报错。
`--limit N` 可限定题数；`--model PATH`、`--corpus NAME` 的覆盖会写入结果。
GPU 编号由调用者选择。现有 R1–R5 benchmark 包仍使用它自己的输入接口和原生评分；
本入口服务原始多选 QA，含 `fixed_evidence` 的记录需要后续任务适配。

## 索引准备与安装复现

安装当日探测上游预计算向量的 SharePoint 链接，返回 HTTP 403。
本地构建沿用上游编码与 FAISS Flat 索引，不将近似索引或 BM25 替代项冒充 RRF-4。
构建先处理 Textbooks，再处理 Wikipedia；完成的 `.npy` 分片会被复用。
单个 Wikipedia 索引约 92 GB，三路向量加最终索引合计约 550 GB，构建耗时取决于 GPU。
每个完成的索引都有 `build.json`，记录向量数、精度、耗时和完成时间。
当前 V5 不依赖这些稠密索引。以下仅用于恢复历史 M4 的 RRF-4；有同一 encoder
任务运行时不重复启动：

```bash
# 一次恢复全部三路，完成后自动检查完整 Llama 检索链。
MEDRAG_GPU_A=1 MEDRAG_GPU_B=2 ./prepare_rrf4.sh

# 或单独恢复某一路：
export HF_HOME="$PWD/.cache/huggingface"
export TMPDIR="$PWD/.cache/tmp"
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=8 .venv/bin/python -u prepare_rrf4.py --encoder contriever
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=8 .venv/bin/python -u prepare_rrf4.py --encoder specter
CUDA_VISIBLE_DEVICES=2 OMP_NUM_THREADS=8 .venv/bin/python -u prepare_rrf4.py --encoder medcpt
```

重新创建 Python 环境可使用系统 Python 3.10 和 `requirements-baseline.lock.txt`。
本机 uv 的 Snap 启动器存在目录权限问题；可直接运行
`/snap/astral-uv/current/bin/uv venv --python /usr/bin/python3 .venv`，再运行
`UV_CACHE_DIR="$PWD/.cache/uv" TMPDIR="$PWD/.cache/tmp" /snap/astral-uv/current/bin/uv pip install --python .venv/bin/python -r requirements-baseline.lock.txt`。

## 与论文完全复现的边界

- [MedRGAG 附录 A](https://arxiv.org/html/2510.18297v1#A1) 同时写有通用 BM25/MedCPT 设置和
  MedRAG 专用四检索器/RRF 设置；附录 C 的概述又提到 MedCorp。
  此处采用附录 A 的两语料及专门针对 MedRAG 的 RRF-4，最终 top-5。
  作者未发布该 baseline 的逐题检索缓存，不能据此声称精确复现表 1。
- [MA-RAG 附录 D.2](https://arxiv.org/html/2603.03292v1#A4.SS2) 明确规定四语料、32/库与最终 8 篇。
  temperature=0.7、非 thinking、2048 输出预算取自作者公开代码 `utils.py::inference` 的 solver 默认值；
  论文未单列 SR-RAG 的全部解码参数和完整提示词，此处使用上游 MedRAG 提示词。
- 两个配置的 seed=42、top_p=1、禁用 top-k 采样筛选、2048 输出上限是明确记录的运行设置。
  Llama 使用 131,072 总上下文；Qwen 使用 32,768，未启用 YaRN。
  生成采用 Transformers；论文 MedRGAG 使用 vLLM。相同 seed 不保证跨引擎逐 token 一致。
- StatPearls 为 2026-09-10 下载的当前快照，片段数不同于原论文的旧快照。
  本目录的四份冒烟结果证明所列安装流程可运行。后续 V5 正式评测已完成，使用的配置、
  原生任务适配和实际结果见 [完整安装报告](<M4_M5_INSTALLATION_REPORT.md>)；它不是论文原表准确率复现。
