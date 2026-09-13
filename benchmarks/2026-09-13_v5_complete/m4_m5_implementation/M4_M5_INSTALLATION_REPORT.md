# M4 / M5 MedRAG 安装、调整与论文实施记录

首次整理：2026-09-12；论文实施记录补充：2026-09-13。索引与进程状态核对点仍为 2026-09-12 19:01，Asia/Shanghai；9 月 13 日复核源码、配置和已有评分产物。下文时间均为北京时间；原始会话与部分 `build.json` 使用 UTC，已换算。

本文作为 **M4 / M5 后续论文写作的统一实施文档**：记录做过的工作、调整前后、原因、生效范围和证据。后续相关修改继续追加到本文，保留原实验版本及其结果对应关系。

| 写作或复核需求 | 本文位置 |
|---|---|
| 实际安装过程、命令与产物 | 第 2–9 节 |
| 正式 V5 的方法参数与结果 | 第 10 节，优先使用运行目录的 `M4/config.json`、`M5/config.json` |
| 逐项调整前后、原因及影响 | 第 13 节 |
| 方法章节草稿、原生任务接口与评分细节 | 第 14 节 |
| 实验边界与记录维护 | 第 11、15 节 |

## 1. 报告范围与结论

此前已经写了 [BASELINES.md](<BASELINES.md>)，记录安装环境、论文参数、运行方法和当时的验证状态；完整的执行过程、遇到的问题、编号更新及后续配置变化尚未汇总成一份报告。本报告补齐这些内容。

整理时回看了 9 月 10 日安装会话的实际工具命令和返回结果，对照代码差异、配置、安装日志、索引完成记录及四份真实模型输出；同时查阅 9 月 11 日 V5 评测会话和结果目录，补充安装交付后的使用情况。第 3–9 节主要记录本安装会话实际完成的工作，第 10 节记录后续 V5 会话的工作，第 13–15 节提供逐项调整和论文写作材料。9 月 12–13 日的文档整理只读取既有运行证据并更新文档，没有重新推理、构建索引或操作运行进程。

| 编号 | 固定含义 | 输出中的机器名称 |
|---|---|---|
| **M4** | MedRAG + Llama-3.1-8B-Instruct | `medrag_llama31` |
| **M5** | MedRAG + Qwen3-8B | `medrag_qwen3` |

实际交付包括：独立 Python 环境、上游源码与本地适配、模型与语料接入、补齐 StatPearls、两套配置、JSONL 推理入口、检索准备脚本、回归检查、真实 GPU 冒烟结果及使用说明。

**版本变化是理解这次工作的关键：**9 月 10 日的独立安装中，M4 按 MedRGAG 对 MedRAG 的专门描述配置为 RRF-4，M5 按 MA-RAG 的 SR-RAG 描述配置为 BM25 + MedCPT。9 月 11 日，用户明确要求“m4重新配置成和m5一致，除了llama”，后续 V5 因此统一了两者的检索、语料和采样参数。

截至核对时，**V5 的 M4、M5 已各完成 13,905 个输入并完成评分审计**。历史 M4 的完整 Wikipedia RRF-4 索引仍不齐全；它已不再是 V5 的依赖。两种状态分别有独立证据，不能用 V5 完成来证明历史 RRF-4 完成。

## 2. 实际执行时间线

| 时间 | 实际操作或完成事件 | 证据 |
|---|---|---|
| 09-10 12:03–12:06 | 检查工作目录、上级说明、GPU、磁盘、Python、已有模型和语料；拉取 MedRAG，阅读论文与两个现有项目 | 原始安装会话；上游 Git 记录 |
| 09-10 12:04:30 | 执行 `git clone https://github.com/gzxiong/MedRAG.git .` | 原始安装会话 |
| 09-10 12:06–12:11 | 创建 `.venv`，安装固定版本依赖；安装日志记录解析 82 个包 | `.cache/install.log` |
| 09-10 12:08–12:14 | 接入已有三库语料，下载新的 StatPearls 压缩包 | `.cache/statpearls-download.log` |
| 09-10 12:13–12:14 | Llama、Qwen 分别用提供的片段完成真实 GPU 推理 | `runs/smoke_llama31.jsonl`、`runs/smoke_qwen3.jsonl` |
| 09-10 12:15 | 解包、运行上游 StatPearls chunker、建立 BM25 索引 | 两份 StatPearls 处理日志 |
| 09-10 12:17–12:18 | Qwen 完成四库 BM25 → MedCPT → top-8 → 生成 | `runs/smoke_qwen3_full_medcorp.jsonl` |
| 09-10 12:18；12:23 | 先启动三个稠密编码任务；随后保存已完成分片，重启为带后续检查的统一准备脚本 | 原始会话；`.cache/prepare-processes.json` |
| 09-10 12:20–12:22 | 完成仓库级 Git LFS 安装；预取并验证 MedCPT Query Encoder | apt 下载日志；`.cache/medcpt-query.log` |
| 09-10 12:25 / 12:28 / 12:30 | Textbooks 的 MedCPT / SPECTER / Contriever 索引分别完成 | 各索引 `build.json` |
| 09-10 12:30–12:33 | Llama 在 Textbooks 上完成真实 RRF-4 冒烟；提交安装说明，Wikipedia 构建继续 | `runs/smoke_llama31_rrf4_textbooks.jsonl`；原始会话 |
| 09-10 22:08–22:18 | 按用户要求编号为 M4 / M5，更新配置、入口、已有记录和工作区指南 | 原始安装会话 |
| 09-11 04:45–04:47 | 用户要求 M4 与 M5 设置相同，仅保留 Llama backbone；V5 建立独立生效配置 | V5 会话；`m4_configuration_change.json` |
| 09-11 06:12:52 / 14:53:13 | V5 的 M5 / M4 各完成 6 个原生任务与长输入冒烟，随后复用这些输出 | `M5/smoke_complete.json`、`M4/smoke_complete.json` |
| 09-11 12:02:11 | Wikipedia 的 MedCPT 稠密索引完成 | 对应 `build.json` |
| 09-11 中午 | V5 会话停止已无评测用途的 Contriever、SPECTER 及旧准备启动脚本；保留已有文件 | V5 `supervision.md` |
| 09-11 12:42 前 | V5 补齐 PubMed 的 1,166 个行偏移文件并验证正文一致 | `pubmed_offset_validation.json` |
| 09-11 20:43:04 | M5 正式剩余 13,899 个输入完成，加 6 个冒烟共 13,905 个 | `M5/complete.json` 与覆盖验证 |
| 09-11 22:48:47；22:49:43 | M4 全部分片合并完成；四方法总评分与审计完成 | `M4/complete.json`、`analysis_finished_at.txt` |
| 09-12 | 回看上述历史，核对实际产物，补写本报告并更新文档入口 | 本报告 |
| 09-13 | 按论文写作要求，复核源码差异与评分接口，补充逐项调整台账、方法描述和后续维护规则 | 本文第 13–15 节 |

## 3. 当时如何确定两个 baseline 的配置

用户最初给出了 `gzxiong/MedRAG`，并提到两篇 SOTA，但没有在该消息中列出论文名称。当时根据工作区已经存在的 MedRGAG 和 MA-RAG 项目，将它们作为对应论文进行核对，并将这个判断写入安装说明。

阅读范围包括 [MedRAG 原论文](https://aclanthology.org/2024.findings-acl.372/)、[MedRGAG 附录 A](https://arxiv.org/html/2510.18297v1#A1)、[MA-RAG 附录 D.2](https://arxiv.org/html/2603.03292v1#A4.SS2)，以及本机两个作者仓库中的检索、reader 和 `utils.py::inference` 实现。Qwen 的接口适配还参考了 [Qwen3-8B 模型说明](https://huggingface.co/Qwen/Qwen3-8B)。

MedRAG 原始工具支持多种语料与检索器。因此，“安装同一个 MedRAG”本身不能确定具体语料、检索器、top-k 和温度。最初写入本仓库的配置如下：

| 参数 | 9 月 10 日 M4 | 9 月 10 日 M5 |
|---|---|---|
| 配置文件（编号后） | [configs/m4.json](<configs/m4.json>) | [configs/m5.json](<configs/m5.json>) |
| 模型 | Llama-3.1-8B-Instruct | Qwen3-8B |
| 生成权重精度 / 引擎 | BF16 / Transformers | BF16 / Transformers |
| 语料 | Textbooks + Wikipedia | MedCorp：PubMed、Textbooks、StatPearls、Wikipedia |
| 检索 | BM25、Contriever、SPECTER、MedCPT，RRF-4 融合 | 每库 BM25 top-32，MedCPT Cross-Encoder 重排 |
| 最终片段数 | 5 | 8 |
| RRF 参数 | `rrf_k=100` | 配置保留该公共字段，重排链不使用它 |
| 温度 | 0.2 | 0.7 |
| 采样 | `do_sample=true`，`top_p=1`，`top_k=0` | 同左 |
| seed / 最大新增 token | 42 / 2,048 | 42 / 2,048 |
| 总上下文上限 | 131,072 | 32,768 |
| 检索上下文裁剪上限 | 128,000 | 30,000 |
| Chat template | 本地 Llama 模板 | 本地 Qwen 模板，`enable_thinking=false` |

M4 的取法依据 MedRGAG 附录 A 中专门描述 MedRAG 的四检索器/RRF 段落，以及该附录的两语料、top-5 和温度设置。该论文同时存在通用 BM25/MedCPT 说明，附录 C 概述还提到 MedCorp；当时已经记录这些表述之间的歧义，没有把所选解释写成唯一确定的逐项复现配置。

M5 对应 MA-RAG 的单轮 **SR-RAG**：四库、每库 32 条候选、重排后 8 条。温度 0.7、非 thinking 与 2,048 输出预算取自作者公开代码的 solver 默认值；SR-RAG 的完整独立提示及全部解码参数没有单列公开，因此使用上游 MedRAG 的 CoT / JSON 答案模板。其余运行参数由配置明确记录。

## 4. 环境安装与模型接入

### 4.1 上游与目录

安装根目录：

```text
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag
```

上游为 [gzxiong/MedRAG](https://github.com/gzxiong/MedRAG)，本地基于提交 `7599a728a28789fd601728c08d313b1148051f41`，提交日期为 2025-05-07。安装采用克隆源码并直接运行本地模块的方式。

### 4.2 初始环境问题及处理

| 实际发现 | 实际处理 |
|---|---|
| `python` 命令不存在，系统 `python3` 为 3.10.12 | 使用 `/usr/bin/python3` 创建项目 `.venv` |
| `uv` 的 Snap 启动器遇到目录权限问题 | 使用实际二进制 `/snap/astral-uv/current/bin/uv`，版本 0.12.6 |
| 既有 MedRGAG 环境存在 Transformers 5.16.1 与 vLLM 0.8.5 不兼容等依赖混杂 | 为本次安装建立独立环境并固定依赖 |
| 根分区仅约 7 GB 空闲，数据盘约 2.6 TB 空闲 | 将虚拟环境、uv 缓存、临时文件、下载和新索引放在本项目所在数据盘 |
| 系统默认 Java 8，与采用的 Pyserini / Lucene 环境不匹配 | 复用 `/home/data3/txy/.cache/jdk/temurin21`，在运行脚本设置 `JAVA_HOME` |
| 系统缺 Git LFS | 下载 Ubuntu 的 git-lfs 包，在 `.cache/git-lfs` 解包，链接到 `.venv/bin`，只对本仓库初始化 |
| 本机 4 张 H20 中 GPU 0 / 3 当时有其他任务 | 安装阶段在 GPU 1 / 2 做推理与编码；GPU 选择通过环境变量传入 |

安装使用的直接依赖见 [requirements-baseline.txt](<requirements-baseline.txt>)，完整冻结版本见 [requirements-baseline.lock.txt](<requirements-baseline.lock.txt>)：

| 包 | 固定版本 | 用途 |
|---|---|---|
| torch | 2.6.0 | GPU 推理；安装结果 CUDA 12.4 |
| transformers | 4.51.3 | Llama / Qwen3 模型和模板接口 |
| accelerate | 1.10.1 | 模型设备分配 |
| sentence-transformers | 3.4.1 | 上游稠密编码路径 |
| faiss-cpu | 1.12.0 | CPU 上的 Flat 向量索引与搜索 |
| numpy | 1.26.4 | 向量及排序 |
| python-liquid | 1.10.2 | 上游提示模板 |
| openai | 1.86.0 | 上游模块依赖 |
| pyserini | 1.0.0 | BM25；兼容本机已有 Lucene 9.9 索引 |
| tiktoken | 0.6.0 | 上游 tokenizer 依赖 |
| tqdm | 4.67.1 | 进度记录 |

安装日志记录解析、安装 82 个包。之后执行了 `uv pip check`、核心模块导入及 CUDA 可用性检查，结果通过。

### 4.3 权重从哪里来

LLM 和 Cross-Encoder 使用本机已有完整权重，通过以下链接接入：

| 项目路径 | 实际目标 | 观察到的文件 |
|---|---|---|
| `models/Llama-3.1-8B-Instruct` | `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct` | 4 个 safetensors 分片 |
| `models/Qwen3-8B` | `/home/data3/txy/models/Qwen3-8B` | 5 个 safetensors 分片 |
| `models/MedCPT-Cross-Encoder` | `/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder` | 本地 PyTorch 权重及 tokenizer |

当时还检查了本机 NousResearch 的 Llama 目录，但它缺少完整权重，最终选择上述完整目录。Contriever、SPECTER、MedCPT Article / Query Encoder 通过 Hugging Face 接口加载，缓存位于 `.cache/huggingface`。Query Encoder 另做了一次 CPU 编码检查，输出形状为 `(1, 768)`，记录在 .cache/medcpt-query.log（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/medcpt-query.log`）。

### 4.4 安装命令记录

以下为历史主命令整理，工作目录为安装根目录。它们说明当时怎样完成安装；已有目录和结果文件现在已经存在。

```bash
git clone https://github.com/gzxiong/MedRAG.git .
mkdir -p .cache/tmp
/snap/astral-uv/current/bin/uv venv --python /usr/bin/python3 .venv
TMPDIR="$PWD/.cache/tmp" UV_CACHE_DIR="$PWD/.cache/uv" \
  /snap/astral-uv/current/bin/uv pip install --python .venv/bin/python \
  -r requirements-baseline.txt > .cache/install.log 2>&1
/snap/astral-uv/current/bin/uv pip check --python .venv/bin/python
/snap/astral-uv/current/bin/uv pip freeze --python .venv/bin/python \
  > requirements-baseline.lock.txt
```

Git LFS 的实际安装流程是先在 `.cache/downloads` 执行 `apt download git-lfs`，随后：

```bash
dpkg-deb -x .cache/downloads/git-lfs_3.0.2-1ubuntu0.3_amd64.deb .cache/git-lfs
ln -s "$PWD/.cache/git-lfs/usr/bin/git-lfs" .venv/bin/git-lfs
PATH="$PWD/.venv/bin:$PATH" git lfs install --local
.venv/bin/git-lfs version
```

## 5. 语料接入与 StatPearls 重建

### 5.1 复用已有三库

对 Textbooks、Wikipedia、PubMed，分别在 `corpus/<name>/` 下建立本地目录，并将已有的 `chunk`、`index/bm25` 及存在的 `line_offsets` 链接到 `/home/data3/txy/MedRGAG/corpus/<name>/`。

这样，已有语料与 BM25 直接可用，新建稠密索引则落在本安装目录自己的 `corpus/<name>/index/<encoder>/`。当时 PubMed 没有可复用的行偏移；其本地偏移是在后续 V5 会话中补齐的。

### 5.2 为什么重新准备 StatPearls

旧 MedRGAG 目录中的 StatPearls 是未完成的 aria2 下载，无法作为完整第四库使用。因此下载 NCBI 的新副本到本项目，保留旧目录原状。

下载地址为 [NCBI StatPearls 压缩包](https://ftp.ncbi.nlm.nih.gov/pub/litarch/3d/12/statpearls_NBK430685.tar.gz)，本次下载发生于 2026-09-10。关键命令为：

```bash
aria2c --continue=true --max-connection-per-server=4 --split=4 \
  --max-tries=3 --retry-wait=5 --connect-timeout=15 --timeout=30 \
  --summary-interval=30 --console-log-level=warn --download-result=full \
  --file-allocation=none --dir="$PWD/corpus/statpearls" \
  --out=statpearls_NBK430685.tar.gz \
  'https://ftp.ncbi.nlm.nih.gov/pub/litarch/3d/12/statpearls_NBK430685.tar.gz' \
  > .cache/statpearls-download.log 2>&1

tar -xzf corpus/statpearls/statpearls_NBK430685.tar.gz -C corpus/statpearls
.venv/bin/python src/data/statpearls.py > .cache/statpearls-chunk.log 2>&1

JAVA_HOME=/home/data3/txy/.cache/jdk/temurin21 \
PATH="/home/data3/txy/.cache/jdk/temurin21/bin:$PWD/.venv/bin:$PATH" \
  .venv/bin/python -m pyserini.index.lucene \
  --collection JsonCollection --input corpus/statpearls/chunk \
  --index corpus/statpearls/index/bm25 \
  --generator DefaultLuceneDocumentGenerator --threads 8 \
  > .cache/statpearls-index.log 2>&1
```

使用了上游 [src/data/statpearls.py](<src/data/statpearls.py>)，该文件没有本地修改。实际结果为：

- 压缩包 **1,901,131,797 字节**，aria2 记录下载成功，平均速度约 5.3 MiB/s。
- chunker 处理 **9,648 个 XML**，生成 **9,646 个非空 JSONL 分片**。
- BM25 索引含 **372,148 条片段**；`unindexable/empty/skipped/errors` 均为 0，索引阶段日志耗时约 3 秒。

证据：下载日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/statpearls-download.log`）、分片日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/statpearls-chunk.log`）、BM25 日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/statpearls-index.log`）。

## 6. 对 MedRAG 实际改了什么

### 6.1 模型生成接口：`src/medrag.py`

保留上游单轮 MedRAG 答案流程与提示模板，在 [src/medrag.py](<src/medrag.py>) 做了以下适配：

1. 将 `utils/template/config` 改为包内相对导入；模板文件通过源码位置定位，使项目入口能够稳定导入。
2. 支持注入检索器，延迟初始化检索资源。输入已带 `snippets` 时，可以独立验证 reader。
3. 增加 `generation_kwargs`、`chat_template_kwargs`、`max_length`、`context_length`，让实际运行参数由配置传入。
4. 补充 Qwen 模型识别，从模型配置读取上下文能力；通过 chat template 参数关闭 Qwen3 thinking。
5. 将实际 tokenizer 交给 Transformers pipeline，沿用上游已有的 BF16 设置，改为读取模型自己的 EOS 配置。BF16 本身不是本次新增的精度改造。
6. 对已经套好 chat template 的字符串设置 `add_special_tokens=False`，避免 Llama 重复加入 BOS；设置 `return_full_text=False`，直接记录生成部分。
7. 使用明确的 `max_new_tokens=2048`；避免同时传入冲突的 `max_length`。完整提示加输出预算超过模型上限时直接报错。
8. 保留上游对检索上下文的裁剪，并新增 `context_truncated_tokens`；记录 messages、原始生成文本、重编码得到的 prompt / completion token 数。

`enable_thinking=false` 控制 Qwen 的 thinking 模式；上游模板本身仍要求解释并给出答案，这两者在报告中分别记录。

### 6.2 单轮 BM25 + MedCPT：`src/baselines.py`

新增 [src/baselines.py](<src/baselines.py>)，主要实现：

```text
question
  → 四个语料各取 BM25 top-32（k1=0.9，b=0.4）
  → 合并最多 128 个候选，按作者实现的 BM25 分数顺序排列
  → 将 [question, document.content] 交给 MedCPT Cross-Encoder
  → 按重排 logits 降序选择 top-8
  → MedRAG 模板 + Llama 或 Qwen 生成
```

Cross-Encoder 输入最大 512 token，按模型 tokenizer 截断。该链使用 Cross-Encoder 重排；它与 RRF-4 中用于稠密检索的 MedCPT Query / Article Encoder 是不同用途的模型。

同文件提供 `missing_resources` 和 `make_retriever`，普通运行前检查所需语料与索引是否存在，缺资源时报告路径。`--check` 是资源存在性检查，真实链路通过独立冒烟验证。

### 6.3 语料与稠密索引辅助：`src/utils.py`

在 [src/utils.py](<src/utils.py>) 中新增两组语料别名 `TextbooksWikipedia` 和 `MedCorp3`；本次独立 M5 实际使用完整 `MedCorp`。

修改 `Retriever.idx2txt`，优先利用已有 `.u64le` 行偏移定位正文，避免每条命中都重读整个 JSONL 分片；没有偏移时保留原读取路径。

对编码分片和最终 FAISS 文件采用临时文件写完再替换的方式，配合跳过已完成 `.npy`，支持长时间构建中断后的分片复用。

历史 M4 的 RRF-4 保留上游检索和融合逻辑：每个检索器在每个库召回 `max(2*k, 100)` 条，当前 k=5 时为 100；同检索器跨库按其分数排序，然后按 `1/(rrf_k+rank)` 融合，最终取 5 条。Contriever / MedCPT 使用内积，SPECTER 使用 L2；索引为 FAISS Flat，`HNSW=False`。

### 6.4 新增运行与记录入口

| 文件 | 实际用途 |
|---|---|
| [run_baseline.py](<run_baseline.py>) | 读取原始多选 QA JSONL，选择配置，调用检索和 reader，逐条保存结果 |
| [run_baseline.sh](<run_baseline.sh>) | 固定项目 Python、JDK、缓存和线程环境 |
| [prepare_rrf4.py](<prepare_rrf4.py>) | 按 encoder 依次构建 Textbooks、Wikipedia 的缺失稠密索引 |
| [prepare_rrf4.sh](<prepare_rrf4.sh>) | 管理三路编码进程，全部成功后触发完整历史 M4 检查与冒烟 |
| [test_baselines.py](<test_baselines.py>) | 使用真实本地 tokenizer 和模拟生成器验证接口行为 |
| examples/smoke.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/examples/smoke.jsonl`） | 带明确提供的片段，用于 reader 冒烟 |
| examples/retrieval_smoke.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/examples/retrieval_smoke.jsonl`） | 不带片段，用于真实检索链冒烟 |
| .gitignore（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.gitignore`） | 排除虚拟环境、模型、语料、缓存、索引与运行输出等大文件 |

独立入口输入为 `id/question/options`，可选 `snippets`；支持 `--limit`、`--model`、`--corpus`、`--db-dir`。输出文件必须是新文件，逐题写入并刷新，包含实际配置、检索模式、文档、分数、响应、生成记录和耗时。每题设置 seed 42，显式覆盖语料或模型时写入结果。

9 月 10 日检查已有 benchmark 输入后，发现它包含必须保留的 `fixed_evidence`。因此独立多选入口对非空 `fixed_evidence` 明确报错，等待原生任务适配；这一接口扩展随后在 V5 的独立 runner 中完成。

## 7. RRF-4 索引为什么重建，最终完成了多少

### 7.1 下载问题与本地构建

安装当日探测上游预计算向量的 SharePoint 链接，HEAD 和 GET 均遇到 HTTP 403。也查阅了官方 Hugging Face MedRAG 数据集列表，未找到可直接替代的官方向量资源，于是转为本地编码。

构建调用上游 `embed` / `construct_index`，batch size 128；Contriever 使用 mean pooling，SPECTER、MedCPT 使用 CLS pooling；保存 768 维 FP32 向量并构建精确 Flat 索引。Wikipedia 有 646 个语料分片、约 2,991 万条片段，单路向量约 92 GB；三路向量连同最终索引预计约 550 GB。这解释了最初 M4 比仅需已有 BM25 和 Cross-Encoder 的 M5 多出大量准备工作。

09-10 12:18 先分别启动三个 encoder；12:23 停止自己的原 worker，保留已完成分片，再由统一脚本恢复，以增加“全部完成后检查并冒烟”的步骤。记录的 supervisor PID 为 1327922，三个 worker 为 1327925 / 1327926 / 1327927：Contriever、SPECTER 在 GPU 1，MedCPT 在 GPU 2。

记录入口：[.cache/prepare-processes.json](<.cache/prepare-processes.json>)、总日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-rrf4.log`）、Contriever 日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-contriever.log`）、SPECTER 日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-specter.log`）、MedCPT 日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/prepare-medcpt.log`）。这里的 PID 是历史记录；本次核对时这些进程已经不存在。

### 7.2 核对到的真实状态

| 语料 / Encoder | 完成的 embedding 分片 | 最终索引 | 向量数 / 完成时间 |
|---|---:|---|---|
| Textbooks / Contriever | 18 / 18 | 已完成 | 125,847；09-10 12:30:39 |
| Textbooks / SPECTER | 18 / 18 | 已完成 | 125,847；09-10 12:28:20 |
| Textbooks / MedCPT | 18 / 18 | 已完成 | 125,847；09-10 12:25:19 |
| Wikipedia / Contriever | 287 / 646 | 未生成 | 后续已停止；保留约 53.45 GB 分片 |
| Wikipedia / SPECTER | 250 / 646 | 未生成 | 后续已停止；保留约 49.23 GB 分片 |
| Wikipedia / MedCPT | 646 / 646 | 已完成 | 29,913,202；09-11 12:02:11 |

完成信息来自各 `build.json`，未完成计数来自实际 `.npy` 文件。Textbooks 三路 `seconds` 分别约为 428 / 289 / 108 秒，是恢复后该次构建段的计时，不代表包括首次编码在内的完整总耗时；Wikipedia MedCPT 记录为约 85,012 秒。

09-11 V5 会话确认统一配置不再使用这些稠密索引后，停止了 Contriever、SPECTER 和旧 supervisor；MedCPT 已提前正常完成。已生成目录约 271 GiB，按该会话记录保留，没有删除。

因此，`.cache/rrf4-complete.txt` 没有生成，完整 Textbooks + Wikipedia 的历史 M4 自动冒烟没有执行。**历史 M4 通过的是 Textbooks 范围内的完整四检索器检查。**

## 8. 安装阶段实际做过哪些验证

### 8.1 依赖与接口检查

安装会话执行并通过了：依赖一致性与模块导入检查、CUDA 检查、`bash -n`、`git diff --check`，以及 [test_baselines.py](<test_baselines.py>)。回归检查覆盖：

- 真实 Llama 模板只包含一个 BOS；Qwen 非 thinking 模板按预期生成。
- 提供片段时不初始化不需要的检索器；pipeline 仅返回生成部分。
- 2,048 输出预算传递正确，不与 `max_length` 冲突；提示超限能够报错。
- 检索上下文裁剪量有记录。
- RRF 合并保留四个检索器的贡献；行偏移准确读取指定记录。

还单独验证了带 `fixed_evidence` 的输入被独立多选入口拒绝，退出码为 2，且不产生结果文件。编号更新后又验证了六种别名解析一致，以及旧结果仅新增编号字段。

上述接口回归使用真实 tokenizer 和模拟生成器；下面四项使用真实 8B 权重完成 GPU 推理。

### 8.2 四份真实冒烟输出

四项均使用同一道面神经多选题；前两项使用人为提供、明确标注的示例片段，后两项实际执行检索。

| 输出文件 | 验证范围 | 片段数 | Prompt / Completion token | 逐题耗时 | 输出答案字段 |
|---|---|---:|---:|---:|---|
| smoke_llama31.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_llama31.jsonl`） | M4 reader，提供片段 | 1 | 308 / 141 | 3.54 s | A |
| smoke_qwen3.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_qwen3.jsonl`） | M5 reader，提供片段 | 1 | 290 / 117 | 4.08 s | A |
| smoke_qwen3_full_medcorp.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_qwen3_full_medcorp.jsonl`） | M5，完整四库 BM25 + MedCPT | 8 | 1,708 / 234 | 13.87 s | A |
| smoke_llama31_rrf4_textbooks.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/runs/smoke_llama31_rrf4_textbooks.jsonl`） | M4，显式 `--corpus Textbooks` 的 RRF-4 | 5 | 1,256 / 235 | 10.27 s | A |

逐题耗时来自 runner 在模型与检索器初始化之后的计时，不能当作包含下载、加载权重和建索引的端到端启动耗时。token 数为安装入口对文本重编码后的计数。最后一份输出明确记录 `context_truncated_tokens=0`；前三份生成于该记录字段加入之前。

当时验证了 M5 的返回数为 8、重排分数降序、语料为完整 MedCorp；验证了 Textbooks M4 的 RRF-4、top-5 和零裁剪。回答保留原始形式：Llama 输出曾出现 `Dict{...}` 前缀或 Markdown 代码围栏，因此这些冒烟验证的是模型与流程可运行、答案字段为 A，不构成严格 JSON 输出率或正式准确率评测。

历史推理主命令如下；`llama31/qwen3` 当时尚未改成 M 编号，现在仍保留为对应别名：

```bash
CUDA_VISIBLE_DEVICES=1 ./run_baseline.sh --variant llama31 \
  --input examples/smoke.jsonl --output runs/smoke_llama31.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant qwen3 \
  --input examples/smoke.jsonl --output runs/smoke_qwen3.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant qwen3 \
  --input examples/retrieval_smoke.jsonl --output runs/smoke_qwen3_full_medcorp.jsonl
CUDA_VISIBLE_DEVICES=2 ./run_baseline.sh --variant llama31 --corpus Textbooks \
  --input examples/retrieval_smoke.jsonl --output runs/smoke_llama31_rrf4_textbooks.jsonl
```

## 9. M4 / M5 编号更新具体改了哪些文件

用户要求按顺序取 M 版本时，现有 benchmark 已使用 M0–M3，因此接续为 M4（Llama）、M5（Qwen）。09-10 晚间实际完成：

1. `configs/llama31.json` → `configs/m4.json`，`configs/qwen3.json` → `configs/m5.json`，增加 `method_id`，保留原机器名称。
2. 运行入口接受 `m4/M4/llama31` 和 `m5/M5/qwen3`，分别加载同一套配置；输出同时保存 `method_id` 与 `method`。
3. 四份已有 smoke JSONL 和两份资源检查 JSON 补充编号；对修改前后内容进行比较，其他配置、提示、检索、响应和耗时保持一致。保留原文件名。
4. 更新 README、BASELINES、回归检查路径及工作区指南中的编号对应关系。
5. 更新未来准备脚本使用的命令和 smoke 文件前缀；当时有 Bash 脚本运行，因此通过替换脚本文件保留旧进程已打开的版本，同时保留旧参数别名。
6. 检查六个别名输出一致、记录内外编号一致、脚本语法和 diff 格式通过；该次编号操作没有重跑推理。

## 10. 后续 V5 怎样使用这套安装

这部分依据另外一次 V5 评测会话的配置、runner、监督日志和完成记录整理。完整评测包位于：

```text
/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5
```

### 10.1 M4 配置更改及实际生效值

09-11 04:45 的用户指令要求 M4 与 M5 设置一致、仅保留 Llama。更改前后配置保存在 [m4_configuration_change.json](<../execution/results_v5_m0_m2_m4_m5/m4_configuration_change.json>)。该文件记录更改时旧配置下 V5 的 M4 / M5 预测数均为 0。

| 参数 | V5 M4 | V5 M5 |
|---|---|---|
| Backbone | Llama-3.1-8B-Instruct | Qwen3-8B |
| 语料 / 检索 / 最终 k | 完整四库 MedCorp；每库 BM25 32；MedCPT 重排 8 | 同左 |
| 引擎 / 生成精度 | vLLM 0.8.5 / BF16 | 同左 |
| 温度 / top-p / seed | 0.7 / 1 / 42 | 同左 |
| 输出预算 | 2,048 token | 同左 |
| 检索上下文裁剪 | 30,000 个本模型 token | 同左 |
| 实际总上下文 | 131,072 | 131,072，YaRN factor 4，原始长度 32,768 |
| 模型模板适配 | Llama 原生模板 | Qwen 模板，非 thinking |
| 原生任务接口 | 共用 `code/run_medrag.py::messages` | 同左 |

**复核 V5 应读取保存的实际运行配置：**[M4/config.json](<../execution/results_v5_m0_m2_m4_m5/M4/config.json>)、[M5/config.json](<../execution/results_v5_m0_m2_m4_m5/M5/config.json>)。V5 `configs/m5.json` 仍保留基础值 32,768，`load_config()` 在运行时扩展为 131,072 并加入 YaRN；保存于 `M5/config.json` 的才是此次运行实际值。

本安装目录的 `configs/m4.json` 保留 9 月 10 日的历史 RRF-4 配置；运行本目录 `run_baseline.sh --variant m4` 仍会选中它。V5 使用自己的配置与 runner。

### 10.2 原生 benchmark 适配与运行环境

V5 [code/run_medrag.py](<../execution/results_v5_m0_m2_m4_m5/code/run_medrag.py>) 复用这里的 `make_retriever` 和上游 MedRAG 模板，增加原生单选、多选集合、诊断、关系标签及 robustness 错误文档列表的输出约定。

检索查询仍只取 `question`；完整 `fixed_evidence` 放入 reader 可见输入。追加检索内容按 30,000 token 裁剪，必需证据保留，完整提示加输出预算超限即报错。输出经过明确字段映射后交给原生评分器，无效输出按协议算错。

该 runner 使用已有 MedRGAG Python 环境提供 vLLM，同时优先导入本 MedRAG `.venv` 中的兼容依赖；独立安装的锁文件中没有新增 vLLM。正式生成使用 batch 16、prefix caching；在 vLLM 中 `top_k=-1` 表示不做 top-k 采样筛选，对应独立 Transformers 配置中的 `top_k=0`。

长输入核对发现 Qwen 原生输入最长达到 69,721 token，超过独立安装的 32K 设置，因此加入 YaRN 4 倍扩展。配置文件和输出中保留了这一原因。

### 10.3 后续性能处理与调度

V5 中补齐了 PubMed 1,166 个 `.u64le` 行偏移文件，共 191,189,608 字节。一次 32 条命中正文的前后比较完全一致，读取耗时从约 4.326 秒降至 0.00151 秒，见 [pubmed_offset_validation.json](<../execution/results_v5_m0_m2_m4_m5/pubmed_offset_validation.json>)。这是正文读取环节的测量，不代表整个检索或推理链的加速倍数。

M5 在 GPU 2 接续 M0 队列运行；M4 后续按用户授权使用 GPU 0，并逐步增加 GPU 1 / 2。M4 先保留 5,830 条结果，再将剩余 8,075 条按完整 batch 分成两路；随后汇总为 9,062 条，剩余 4,843 条分成三路。GPU 0 出现其他进程时，自己的守护逻辑让出 GPU，未完成部分最终在 GPU 1 续跑。分片及提示覆盖检查通过后合并，历史文件保留。

上述调度改变记录在 V5 [supervision.md](<../execution/results_v5_m0_m2_m4_m5/supervision.md>)，没有改变生成设置或遗漏输入。显存份额随调度调整；这不应混同为算法配置变化。

### 10.4 已完成的正式验证与结果

两者分别做了 6 个覆盖原生格式及长输入的真实冒烟，并把这些预测纳入正式结果复用。最终每个方法有 13,905 条预测和对应提示记录；完整评分共覆盖 6,104 个比较单元、13,000 个选中判断，每方法 15,616 条评分映射。

| 已有正式记录 | M4 | M5 |
|---|---:|---:|
| 完整输入 / 最终生成调用 | 13,905 | 13,905 |
| ALL 单元平均原生任务正确率 | 29.76% | 47.35% |
| Prompt token 总数 | 48,325,826 | 49,856,833 |
| Completion token 总数 | 5,821,549 | 3,685,268 |

分数为本地 V5 的单元等权指标，ALL 对单元去重；不能直接解释成 13,905 道题的简单正确率，也不是论文原表结果。token 总数来自 vLLM 实际 token ID 记录的审计。

[validation.json](<../execution/results_v5_m0_m2_m4_m5/validation.json>) 显示 `status=complete`、M4 / M5 缺失预测均为 0、全部方法重复预测为 0；[artifact_audit.json](<../execution/results_v5_m0_m2_m4_m5/artifact_audit.json>) 为 `passed`，缺失提示记录为 0。分类分数、指标定义与评测限制见 [RESULTS.md](<../execution/results_v5_m0_m2_m4_m5/RESULTS.md>) 及同目录 README。

## 11. 复现边界与保留事项

1. **论文配置有明确解释边界。**初始 M4 对 MedRGAG 文中不完全一致的说明作了有记录的选择；M5 的部分 SR-RAG 解码细节取自作者 solver 默认值。没有作者逐题 baseline 检索缓存可核对，不能宣称精确复现论文表格。
2. **当前 V5 与初始独立安装不同。**V5 M4 已统一为 BM25 + MedCPT；M5 加入 YaRN；两者改用 vLLM 和原生任务适配。它们的配置及结果应按各自运行目录解释。
3. **历史完整 RRF-4 仍未完成。**Wikipedia 的 Contriever、SPECTER 仅保留部分分片，完整自动冒烟没有成功标记。当前 V5 不依赖这些索引。
4. **语料快照不同。**StatPearls 使用 2026-09-10 下载的新副本，372,148 条片段不同于原论文约 301.2k 的旧快照；其他三库复用本机已有数据。
5. **验证粒度不同。**四份安装冒烟证明所列流程可运行；正式评测使用 V5 原生协议。Transformers 与 vLLM、不同 tokenizer 和上下文设置，即使 seed 相同也不保证逐 token 一致。原始响应及无效输出应按各阶段实际评分规则解释。
6. **安装文件以本机资源为基础。**模型与大部分语料是软链接，Java 也是既有本机目录；只复制源码不能得到完整运行资源。缓存、模型、语料和结果受 `.gitignore` 排除，但在本机保留。报告整理时本地修改尚未形成新的 Git 提交。
7. **调整效果的证据范围。**本报告对应的正式 V5 结果来自 seed 42 的已记录运行，没有针对 RRF → BM25/MedCPT、引擎切换或 YaRN 分别开展控制其他条件的消融。M4 与 M5 采用共同的检索与采样协议，但 tokenizer、chat template、权重及 Qwen 上下文扩展不同；30,000 token 裁剪按各自 tokenizer 计数，可见文本边界不保证相同。
8. **推理与统计口径。**正式生成默认每输入产生一个输出，不含候选集成或投票；不同输入可按相同 question 复用检索缓存，因此最终生成调用数不等于独立检索次数。采样输出和单次正文读取计时不能推出逐 token 确定性或端到端加速结论。
9. **评分覆盖范围。**输出按第 14.3 节解析；开放诊断按冻结标签的归一化精确匹配处理，未额外进行医学同义表达判分。Robustness 的错误文档识别有独立评分，纠正文本的语义质量未评分；这些边界也适用于第 14.4 节的论文草稿。

## 12. 证据与文件入口

| 要核对的内容 | 入口 |
|---|---|
| 原始安装、验证、编号操作的会话记录 | 2026-09-10 安装会话（本地制品：`/home/data3/txy/.codex/sessions/2026/09/10/rollout-2026-09-10T12-03-45-01a0897c-63e4-7803-b918-7910e00692e7.jsonl`） |
| 后续 V5 用户配置变更指令 | 2026-09-11 V5 会话（本地制品：`/home/data3/txy/.codex/sessions/2026/09/11/rollout-2026-09-11T03-51-50-01a08ce0-63a0-7a82-880c-a3d561dde361.jsonl`） |
| 独立安装的日常使用与历史参数 | [BASELINES.md](<BASELINES.md>) |
| 依赖安装结果 | .cache/install.log（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/install.log`）、[requirements-baseline.lock.txt](<requirements-baseline.lock.txt>) |
| Textbooks 三路完成记录 | Contriever（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/textbooks/index/facebook/contriever/build.json`）、SPECTER（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/textbooks/index/allenai/specter/build.json`）、MedCPT（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/textbooks/index/ncbi/MedCPT-Article-Encoder/build.json`） |
| Wikipedia 已完成的 MedCPT 索引 | build.json（本地制品：`/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/corpus/wikipedia/index/ncbi/MedCPT-Article-Encoder/build.json`） |
| V5 完整方法、数据和运行协议 | [V5 README](<../execution/results_v5_m0_m2_m4_m5/README.md>) |
| 工作区目录和后续任务入口 | [MEDRGAG_WORKSPACE_GUIDE.md](<../workspace_reference/MEDRGAG_WORKSPACE_GUIDE.md>) |

本报告中的完成状态优先采用实际结果、配置和完成标记；较早的工作区摘要中“仍在构建”“尚无正式 benchmark”等语句属于历史快照，已经在本安装说明中补充了后续状态。

## 13. 逐项调整台账：调整前、调整后、原因与影响

本节将第 3–10 节的执行记录转换为论文实施台账。“调整前”分别标明上游代码、初始安装或后续 V5 流程，避免将已有能力计作本地新增工作。表内日期为实施日期；2026-09-13 仅补充记录。

### 13.1 方法与实验协议

本表涉及的证据集中在本仓库 [初始 M4](<configs/m4.json>)、[初始 M5](<configs/m5.json>)、[检索实现](<src/baselines.py>)，以及 V5 [配置变更记录](<../execution/results_v5_m0_m2_m4_m5/m4_configuration_change.json>)、[原生任务 runner](<../execution/results_v5_m0_m2_m4_m5/code/run_medrag.py>)。

| 日期 / 工作 | 调整前 → 实际调整后 | 原因、影响与最终生效范围 |
|---|---|---|
| 09-10 模型选择 | 上游可选多种 reader → 配置两个本地 8B instruct reader：Llama-3.1 和 Qwen3 | 为两种 backbone 建立 benchmark baseline；生成权重采用 BF16。模型选择属于实验设置 |
| 09-10 初始 M4 | 上游通用检索工具 → Textbooks + Wikipedia、RRF-4、top-5、温度 0.2 | 依据当时对 MedRGAG baseline 段落的解释；这是历史安装配置，正式 V5 已更改 |
| 09-10 初始 M5 | 上游单检索器 / RRF 组合 → 新增四库 BM25 32/库 + MedCPT 重排 top-8 | 实现 MA-RAG 单轮 SR-RAG 对应的检索流程；同一实现随后供 V5 M4/M5 共用 |
| 09-10 候选重排细节 | 新检索链尚不存在 → BM25 `k1=0.9,b=0.4`；合并至多 128 条；`[question,content]` 输入 Cross-Encoder，最大 512 token | 将召回、候选排序、重排输入和长度规则写成明确实现。重排正文不拼入标题；reader 展示片段时包含标题 |
| 09-10 采样设置 | 上游本地生成分支显式 `do_sample=False` → 配置化采样；seed 42、top-p 1、无 top-k 筛选、输出上限 2,048 | 支持所选 baseline 的温度；采样设置会影响回答。初始 M4/M5 温度不同，V5 均为 0.7 |
| 09-10 Qwen 模板 | 上游缺少 Qwen 专门分支和 thinking 参数传递 → 识别 Qwen 配置并传入 `enable_thinking=false` | 使 Qwen3 在选定模式下运行；上游模板仍要求解释与答案，非 thinking 不等于只输出选项 |
| 09-10 语料快照 | 旧 StatPearls 下载未完成 → 下载新副本、上游切分、BM25 入库 372,148 条 | 补齐第四库；会改变相对于旧论文快照的可检索内容。其余三库复用已有资源 |
| 09-10 独立输入边界 | 原始多选题入口未承接 benchmark 必需证据 → 对非空 `fixed_evidence` 报错 | 防止把必需证据遗漏后当成已适配 benchmark；该阶段只交付原始多选 QA 入口 |
| 09-11 M4 协议统一 | 历史 RRF-4 / 两库 / top-5 / 0.2 → 四库 BM25+MedCPT / top-8 / 0.7；检索上下文 128,000 → 30,000 token | 按用户明确指令统一 M4/M5 设置。变更记录显示当时旧设置下 V5 两方法预测数均为 0 |
| 09-11 原生任务适配 | 原始 MCQ 模板 → 共享任务格式适配，支持多选、诊断、关系标签、robustness；保留完整给定证据 | 使相同 baseline 可回答 V5 原生任务。增加的是任务接口约定，模板不再与上游原始 MCQ 提示逐字相同 |
| 09-11 Qwen 长上下文 | 独立安装最大 32,768 → V5 运行时 131,072，YaRN factor 4，原始长度 32,768 | 已观察到最长原生输入 69,721 token；扩展用于保留长证据。这是模型特定的实验适配 |
| 09-11 生成引擎 | 安装冒烟使用 Transformers → V5 使用 vLLM 0.8.5，正式 batch 16、prefix caching | 支持完整评测吞吐；token 计数改为实际生成 token ID。采样协议保留，但不同引擎输出可能不同 |
| 09-11 评分接口 | MedRAG 字段 `answer_choice` → 确定性提取并映射到已有 scorer 的 `answer` | 使原生评分器接收同一语义字段；解析规则详见第 14.3 节，原始响应仍保留 |

以下内容沿用既有方法：单轮检索和单次最终生成、question-only 查询、MedRAG 文档与问题模板的主体结构、RRF 编码及融合公式、StatPearls 上游 chunker。V5 使用冻结模型做推理，未引入训练、微调、候选投票、查询改写、多轮 agent 或 M2 的生成文档阶段。

### 13.2 源码兼容、运行和资源处理

源码证据见 [reader 改动](<src/medrag.py>)、[语料与索引改动](<src/utils.py>)、[独立运行入口](<run_baseline.py>)；后续操作见 V5 [监督记录](<../execution/results_v5_m0_m2_m4_m5/supervision.md>)。

| 日期 / 工作 | 调整前 → 实际调整后 | 目的与证据边界 |
|---|---|---|
| 09-10 环境安装 | 既有依赖混杂、`python` 不存在、uv 启动器失败 → 系统 Python 3.10 独立 venv、固定依赖、直接 uv 二进制 | 完成可运行安装；82 个包的安装日志和版本锁保留 |
| 09-10 Java / LFS | Java 8、缺 Git LFS → 运行脚本使用现成 JDK 21，git-lfs 本地解包并按仓库初始化 | 满足现有 BM25 索引兼容性及资源工具依赖；不改变检索公式 |
| 09-10 目录与复用 | 根盘空间不足、资源分散 → 数据盘缓存和索引目录，模型与既有三库软链接 | 完整权重与正文直接复用；本机依赖路径在第 4–5 节列出 |
| 09-10 导入与模板路径 | `sys.path.append('src')`、依赖当前目录的模板路径 → 包内相对导入、按源码位置定位模板 | 让项目入口可稳定导入；未重写模板文本 |
| 09-10 检索初始化 | reader 构造即加载检索资源 → 可注入检索器、需要时再初始化 | 提供片段的 smoke 可以单独检查模型接口；正常实时查询仍调用所选检索流程 |
| 09-10 tokenizer / 输出提取 | pipeline 未显式传入对应 tokenizer，生成后按 prompt 字符数截取 → 传入 tokenizer，`add_special_tokens=False`、`return_full_text=False` | 修正重复 BOS 风险及生成结果提取路径；真实模板回归和 GPU smoke 已验证。该变化可能影响实际模型输入 |
| 09-10 结束与长度规则 | 分支中手写 EOS、总长生成和输入自动截断 → 模型 EOS、明确新增 token 预算、总长超限报错 | 让模型结束条件与输出预算明确；检索上下文仍按规定裁剪并记录裁剪量 |
| 09-10 正文读取 | 每条命中都读取并切分整个 JSONL 文件 → 有 `.u64le` 时按偏移读取目标行，无偏移时沿用旧路径 | 优化 IO；回归检查验证目标行定位。未修改 BM25、RRF 或重排排序公式 |
| 09-10 稠密资源获取 | 官方向量链接返回 403 → 按上游 encoder 本地生成 FP32 向量和 Flat 索引 | 为初始 M4 补资源；完整 Wikipedia RRF 最终未完成，状态见第 7 节 |
| 09-10 分片保存与恢复 | 直接写最终 `.npy` / FAISS 文件 → 写完临时文件再替换，保留并复用已完成分片 | 支持长构建恢复；编码、pooling 和索引距离度量沿用上游 |
| 09-10 准备任务管理 | 三个独立 worker → 保留分片后由 supervisor 管理，并设置全部成功后的检查与 smoke | 这是一次实际执行的停启调整；后续整体成功标记未产生 |
| 09-11 停止旧索引 | V5 已不依赖 RRF，旧任务仍占资源 → 停止 Contriever、SPECTER 与 supervisor，保留文件 | 释放运行资源；MedCPT 此前已完成，V5 检索链不加载这些稠密索引 |
| 09-11 PubMed 行偏移 | PubMed 缺少偏移表 → 补齐 1,166 个偏移文件 | 一组 32 条命中正文前后完全一致；单次正文读取计时改善已记录，不等同于端到端速度提升 |
| 09-11 GPU 与续跑 | M4 单路 → 按已提交完整 batch 分成两路、再三路；外部进程出现时让出 GPU 0 并续跑 | 处理资源可用性；保留生成参数、已完成样本和提示，最终覆盖与重复项检查通过 |

### 13.3 记录、验证和交付

| 日期 / 工作 | 实际完成内容 | 留下的证据或产物 |
|---|---|---|
| 09-10 可复用入口 | 创建配置、shell 环境入口、JSONL 输入输出、资源检查、模型与语料覆盖参数；禁止覆盖已有输出 | 第 6.4 节文件表；覆盖参数写入实际结果 |
| 09-10 运行记录 | 保存原始生成、messages、片段与分数、配置、逐题耗时、token 统计，随后补充裁剪统计 | 四份 smoke 输出及运行代码；前三份早期输出不含后来新增的裁剪字段 |
| 09-10 验证 | 环境导入与依赖检查、实际 tokenizer 回归、四次 GPU smoke、必需证据入口检查 | 第 8 节；每项验证范围及其未覆盖范围都有明确说明 |
| 09-10 编号 | 配置和入口改为 M4/M5，保留旧别名；已有结果仅补编号字段，更新文档与测试引用 | 第 9 节；没有为编号变更重新生成答案 |
| 09-11 评测留存 | 原生格式 smoke 复用、按 question 缓存检索、保存实际配置、原始 prompts、预测和 token ID 计数 | V5 `M4/`、`M5/` 及其分片目录 |
| 09-11 覆盖和评分 | 合并分片、检查所有输入和提示齐备、执行原生评分和成本审计、导出表格与图 | 第 10.4 节；`validation.json=complete`、`artifact_audit.json=passed` |
| 09-12 文档追溯 | 浏览原始会话和日志，形成完整安装报告，更新 README、BASELINES、工作区指南的报告入口和旧索引状态 | 本文第 1–12 节 |
| 09-13 论文实施记录 | 复核 diff、运行快照和解析器，补充前后对照、论文方法草稿及维护记录 | 本文第 13–15 节；本次只修改文档 |

## 14. 论文方法与实现细节写作材料

### 14.1 正式结果对应的实验版本

本文论文草稿对应 **2026-09-11 已完成的 V5 M4/M5**，参数依据第 10.1 节保存的实际配置。算法来源引用 [MedRAG](https://aclanthology.org/2024.findings-acl.372/)，单轮检索设置来源引用 [MA-RAG 附录 D.2](https://arxiv.org/html/2603.03292v1#A4.SS2)；其本地默认参数和原生任务扩展按本报告披露。[MedRGAG 附录 A](https://arxiv.org/html/2510.18297v1#A1) 对应初始 M4 配置选择的历史来源。

BF16 指 LLM 生成权重精度。`BM25MedCPT` 对 Cross-Encoder 的加载未显式指定 BF16；历史稠密向量为 FP32。三者的精度记录分别对应不同组件。

### 14.2 查询、证据、提示和答案约定

| 环节 | V5 代码实际执行的规则 |
|---|---|
| 模型输入字段 | `item_id/question/options/fixed_evidence/answer_format/max_tokens` 为已材料化输入字段；其中 M4/M5 使用统一 2,048 生成预算，并非直接使用逐项 `max_tokens` |
| 检索查询 | 仅使用 `item['question']`；另存于 `options`、`fixed_evidence` 的内容不追加到检索查询。相同 question 在所在运行目录中复用检索缓存 |
| 候选与重排 | 四库各 BM25 top-32，合并后以 `[question,doc.content]` 做 MedCPT 重排，输入对最大 512 token，返回 top-8 |
| Reader 上下文 | 按重排顺序组织 `Document [j] (Title: title) content`；用当前 reader tokenizer 编码并保留前 30,000 token，再解码为文本 |
| 必需证据 | 将完整 `fixed_evidence` 依序附到 reader 问题中；与可裁剪的追加检索上下文分开处理 |
| 提示结构 | MedRAG system message + 文档、问题、选项组成的 user message；选项按 key 排序展示；再使用相应模型 chat template |
| 原生格式扩展 | 对非原始单选格式以及特殊选项 key，修改答案类型要求；robustness 另要求错误文档 ID 与纠正文本 |
| 生成 | 每个输入返回一个最终样本；温度 0.7、top-p 1、seed 42、最大新增 2,048 token；Qwen 非 thinking；不添加多候选选择阶段 |
| 长度校验 | 完整 chat prompt 的 token 数 + 2,048 必须不超过 131,072；超限报错，检索上下文裁剪量独立保存 |

Gold、分类理由和评分映射保存在评测侧，不进入上述 reader 消息。具体字段映射与输入准备由 V5 评测包负责；其冻结数据规模及分类规则引用 V5 原有文档。

| `answer_format` | `answer_choice` 的提示约定 |
|---|---|
| `single` | 一个原生选项 key 字符串 |
| `multi` | 一个包含一个或多个原生选项 key 的 JSON 数组 |
| `diagnosis` | 一个简洁的最可能诊断标签 |
| `relation` | `higher`、`lower`、`no difference`、`uncertainty` 中的一个 |
| `robustness_single` | 一个原生选项 key；另提供 `errors` 数组，各项含 `document_id` 和 `correction` |

这部分由同一个 `messages()` 函数对 M4/M5 应用。模型 tokenizer 与 chat template 各自保留，故共享的是输入组织和任务约定。

### 14.3 输出解析与评分：需要准确记录的细节

V5 [analyze_v5.py::objects](<../execution/results_v5_m0_m2_m4_m5/code/analyze_v5.py>) 在原始响应中扫描可解析的 JSON 对象，选取包含 `answer_choice` 的对象。若多个对象中的答案字段值一致，使用第一个对象；若不存在此类对象或答案字段相互冲突，则不产生有效映射。代码围栏、解释文字、`Dict` 外层前缀本身不会使其中可解析的对象失效。

提取成功后，将字段值映射为 `{"answer": value}`，交给既有 [原生 scorer](<../../../cf_medrgag_validation_pack/scripts/analyze_cf_baseline_screening.py>)。该过程是固定解析及字段转换；没有调用模型修复答案或根据 gold 选择相互冲突的输出。

- 单选要求合法原生选项 key；多选要求非空、合法、无重复的 key 数组，主正确性按完整集合匹配。
- 关系标签按已有归一化规则匹配四种合法值；诊断按冻结 canonical labels 做归一化精确匹配。
- 无法映射、非法类型或不合法答案按原有 scorer 判为无效并计错；原始响应保留供追溯。
- Robustness 主问沿用单选评分，`errors` 的文档 ID 集合另做识别评分；`correction` 文本保存，但 `correction_semantic_score` 为 `None`。

主表先对同一比较单元、同一类别中的非 reference 原生评分记录求均值，再对该类别的单元等权平均；ALL 对单元去重。参考端另用于配对与不变性指标。因此第 10.4 节的 29.76% / 47.35% 是 V5 单元平均原生任务正确率。

### 14.4 可用于方法章节的文字草稿

**中文方法描述：**

我们基于 MedRAG 实现两个单轮医学检索增强生成基线，分别以 Llama-3.1-8B-Instruct 和 Qwen3-8B 作为回答模型，记为 M4 和 M5。两者采用统一的检索协议：以问题文本为查询，分别从 PubMed、Textbooks、StatPearls 和 Wikipedia 的 BM25 索引召回 32 个片段，使用 MedCPT Cross-Encoder 对合并候选进行重排，并将前 8 个片段提供给回答模型。BM25 参数为 k1=0.9、b=0.4，Cross-Encoder 的问题—正文输入对最大长度为 512 token。我们沿用 MedRAG 提示结构，并为 benchmark 的原生答案类型添加共享格式约定。题目给定的必需证据完整保留，追加检索上下文按相应模型的 tokenizer 限制为 30,000 token。正式评测通过 vLLM 0.8.5 使用 BF16 生成，温度为 0.7，top-p 为 1，随机种子为 42，最大新增输出为 2,048 token，每输入产生一个最终回答。M5 使用 Qwen 非 thinking 模式，并采用 factor 4 的 YaRN 将总上下文从 32,768 扩展至 131,072 token；M4 使用原生 131,072 上下文。可解析答案通过固定字段映射进入统一原生评分器，无效答案计错。

**English implementation draft:**

We implemented two single-round medical RAG baselines using MedRAG, with Llama-3.1-8B-Instruct (M4) and Qwen3-8B (M5) as readers. Both used question-only BM25 retrieval from PubMed, Textbooks, StatPearls, and Wikipedia, retrieving 32 snippets per corpus with k1=0.9 and b=0.4. We reranked the pooled candidates with the MedCPT Cross-Encoder using question–content pairs of at most 512 tokens and supplied the top eight snippets to the reader. We retained the MedRAG prompt structure and added shared output contracts for the benchmark's native tasks. Mandatory evidence was preserved in full, while additional retrieved context was limited to 30,000 tokens under each reader's tokenizer. Generation used vLLM 0.8.5, BF16 reader weights, temperature 0.7, top-p 1, seed 42, and a maximum of 2,048 new tokens, producing one response per input. M5 used non-thinking mode and YaRN scaling with factor 4 to extend its context from 32,768 to 131,072 tokens; M4 used its native 131,072-token context. Answers were extracted by a fixed JSON-field parser and evaluated with the native scorers; invalid answers were counted as incorrect.

**语料与结果口径补充句：**

StatPearls 使用 2026-09-10 下载并通过上游 chunker 处理的副本，共 372,148 条片段；其余三库复用本地已有 MedRAG 语料。M4/M5 分别完成 13,905 个独立输入，结果按 6,104 个比较单元等权汇总。上述设置对应本地 V5 适配后的基线评测；具体复现边界与组件差异见第 11 节。

### 14.5 写论文时的信息来源索引

| 论文部分 | 本文与实际证据 |
|---|---|
| Baseline 定义与算法来源 | 第 3、10.1、14.1 节；MedRAG / MA-RAG 论文与实际运行配置 |
| Implementation details / 超参数 | 第 4、10.1、13.1、14.2 节；依赖锁、`src/baselines.py`、V5 runner |
| 与原始方法的实现差异 | 第 13 节；源码 diff、`m4_configuration_change.json`、保存的运行配置 |
| 数据与语料快照 | 第 5、10 节；StatPearls 日志、V5 数据说明和材料化输入 |
| 提示与答案格式附录 | 第 14.2–14.3 节；`src/template.py`、V5 `messages()`、各方法的 `prompts.jsonl.gz` |
| 结果与评分 | 第 10.4、14.3 节；V5 `RESULTS.md`、`category_scores.csv`、`validation.json` |
| 成本与效率 | 第 8.2、10.3–10.4 节；原始计时、token 审计、PubMed 单次读取比较 |
| 局限与可复现性 | 第 11 节；原始配置歧义、快照差异、引擎与上下文适配、未完成历史索引 |

## 15. 后续记录约定与文档更新历史

按用户要求，M4/M5 后续涉及代码、模型、语料、提示、解码、评分、运行资源或验证的工作，都在本文追加记录。每项记录写明实施日期、调整前后、原因、生效配置与运行目录、实际执行命令或源码位置、验证结果，以及已完成 / 已停止 / 未执行状态。只讨论的方案与实际执行的操作分别标明。

方法设置发生变化时保留原配置及原结果的对应关系，在第 13 节追加变更，在第 10 节说明新结果所属版本；方法章节草稿随生效协议更新。运行进度采用带日期的记录，已有完成记录与产物作为历史证据保留。来自其他会话的实施记录标明来源，本文整理动作与原实验实施动作分别记载。

| 文档更新日期 | 已完成的文档工作 | 本次实验状态变化 |
|---|---|---|
| 2026-09-10 | 新增 BASELINES 安装说明、运行命令和当时的验证状态；完成 M4/M5 编号与文档同步 | 对应安装、冒烟、索引启动及编号的原始执行记录 |
| 2026-09-12 | 从历史会话、日志和产物补写本文第 1–12 节；同步 README、BASELINES、工作区指南 | 文档整理；更新历史状态表述，没有新实验 |
| 2026-09-13 | 将本文作为统一论文实施记录；补充逐项调整、原生评分细节、中英文方法草稿和维护约定；明确 BF16 沿用上游 | 文档整理；正式 V5 配置和已有结果保持原值，没有新实验 |

### 保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）

用户明确要求保存M7并让GPU1/2/3全力运行刚更新的M4，额外监督有效率。M7已13:45暂停，1646/13905（1634新＋12复用），1026有效/620无效/0失败、11完整分片；已核对单题terminal数量与独立保存点一致。保存点：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/；原阶段缓存保留，m7_pause.json记录暂停。M6仍52条暂停，不自动恢复两方法。

新活动包：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/README.md。全新生成13905条，复用原M4完整历史检索消息，加入已试验的明确输出契约与逐题JSON Schema/xgrammar。代码和修改后的全量输入独立保存，旧M4不覆盖。Llama3.1-8B、BF16、温度0.7、top_p1、seed42、2048输出及131072上下文不变。每卡vLLM常驻实例、.90显存、128并行序列、16384 prefill token、prefix cache/chunked prefill，109个锁保护动态分片。tmux v5-m4-structured；GPU0未动。

队列与有效率监控2项针对性检查通过；监控复现已有100题98格式有效/84原生有效/99Schema有效/1截断。监控分别报告格式/原生/Schema有效率、截断和题型原因，并单列100条方案选择输入之外的有效率；全部无效保留分母。原v5的3个共享输入存在不同gold映射，最终评分保留全部映射；去重有效率与gold无关。全量完成后自动合并并调用原生分析器，生成scores/、validity.json、complete.json、RESULTS.md。五分钟报告继续针对新M4。

### 新M4结构约束修复全量完成（2026-09-13 15:04）

[最终结果](<../completion/results_v5_m4_structured/RESULTS.md>)：13,905唯一输入全部新生成，109/109分片完成，15,616原生评分映射、6,104单元、13,000入选判断完整，缺失/重复/运行失败均为0。GPU1/2/3生成墙钟含加载71.86分钟，完成后自动释放；GPU0未动。

同一13,905输入，格式有效率61.41%→99.09%，原生有效率43.92%→79.42%；严格Schema有效99.46%，原生监控与完整评分器去重一致。单元平均准确率原M4→修复M4：R1 21.53→27.84、R2 6.33→29.11、R3 14.32→30.42、R4 23.08→53.85、R5 39.63→65.28、ALL 29.76→48.20（%）。所有无效保留分母。原生无效2,861：未映射诊断2,735、诊断歧义50、原生解析malformed_json 76；严格JSON无效75，长度截断73，口径分别记录。诊断原生有效率仍仅21.32%。

方案选择100输入之外的13,805输入格式/原生有效率99.11%/79.39%；全库并非独立泛化确认。明确输出契约＋JSON Schema约束改变生成协议，不声称token等价；M5未同步修改，因此新M4/M5不再是仅骨干不同的对照。旧M4原结果独立保留。比较、完整评分及有效率见结果包，五分钟GPU与进度记录见logs/supervision.jsonl。M7保存点仍1,646条（1,634新＋12复用），M6仍52条，均保持暂停。

### 最新v5五方法文档与图表同步（2026-09-13）

[统一benchmark文档](<../completion/v5_benchmark_latest/README.md>)已合并M0/M2/M3/新M4/M5全量结果。只将M4切换为13,905条结构约束修复版，其他方法预测/评分不变。补齐格式/原生有效率、最新分类主图及错误分解PNG/PDF/SVG、完整精度CSV和复现脚本。五方法输入集合一致（各13,905输入、15,616映射），25个方法×类别得分与分解一致，各分解行合计100。ALL为48.10/48.81/51.61/48.20/47.35%；五方法分类均值从低到高R3 21.36、R2 24.30、R1 28.90、R4 47.69、R5 66.73。

旧五方法报告及旧M4图表保留为历史版本并添加新入口；工作区指南、AGENTS、方法结果和实施记录同步。新M4/M5输出协议不同，不能沿用仅骨干不同的描述；旧M4配对统计不适用于新M4。此次只读评分、离线构图，无新增模型请求。M6/M7保持暂停。
