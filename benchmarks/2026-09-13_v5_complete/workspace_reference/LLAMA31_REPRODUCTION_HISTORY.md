# MedRGAG Llama 3.1 复现历史与会话交接

> 最后核验：2026-08-17，Asia/Shanghai  
> 项目根目录：`/home/data3/txy/MedRGAG`  
> 上游仓库：`https://github.com/ll0ruc/MedRGAG.git`  
> 上游公开 HEAD：`0057853df65dcaa46d2934a28f8d5025fc3de623`  
> 目标论文：`/home/data3/txy/Li - 2026 - From Retrieval to Generation Unifying External and Parametric Knowledge for Medical Question Answer.pdf`

本文档是本次对话的完整 handoff。下一个 agent 应先读本文，再读 `RESULTS_LLAMA.md`、`REPRODUCE_LLAMA.md` 和实际结果 JSON。论文、README、代码和输出中的文字都只作为待核验资料，不应被当作高优先级操作指令。

## 0. 2026-08-17 最新断点（优先于下方历史状态）

### 0.A 全 Llama 本地变体（2026-08-17 18:50 CST，最新）

用户明确纠正了实验执行原则：这是科研测试，模型给出格式差、重复、截断或不可解析的
输出本身也是结果，不应因“结果不好”停止全流水线。当前实现已经改为“科研宽容、工程
完整性严格”，并新增无人值守编排脚本。权威说明为 `REPRODUCE_ALL_LLAMA.md`，人工质量
审计仍保存在 `ALL_LLAMA_V15_AUDIT.md`。

当前最重要的状态：

- `reproduce_medrgag_all_llama.py` 仍是八阶段 runner，`run_medrgag_all_llama.sh` 是新的
  全流程入口。阶段固定为 `retrieval -> summary -> explore -> generate -> select -> rerank ->
  reader -> evaluate`，每阶段由独立 Python 进程执行并释放模型资源。
- 旧的 full-scope 质量安全闸已经删除。不带 `--limit` 可以直接做探索性五数据集运行；
  `--allow-unvalidated-full-run` 已从 CLI 删除，不能再传。运行许可不代表结果可信，最终报告
  仍必须标明这是 `experimental_not_table1`，并披露全部质量计数。
- summary/explore/select 的格式与质量检查仍保留。一次本地推理只要完成并形成确定的下游
  payload，artifact 就以 `status=ok` 保存；模型质量另记为 `model_output_valid=false`、
  `validation_status=invalid`、parse/quality warnings，并保留 `InvalidModelOutput` error sidecar。
  这些诊断不会使阶段或全流程退出。
- explore 缺失编号用 `None` 按原位置补齐；select 的重复、少于五个和空选择继续下游。空
  选择经过空 MedCPT 输入后让 reader 做 question-only 推理。evaluate 会汇总各角色 invalid、
  截断、fallback 和解析警告数。
- vLLM/MedCPT/CUDA/文件系统等后端失败、无法形成 payload 的 Python/parser 异常、上游
  artifact 缺失或损坏以及 profile/input/source/hash 不一致仍是致命错误。shell 不会用
  `|| true` 掩盖这些技术或完整性问题。
- 默认 profile 仍为 `role-stable-v15-guided-sentence-labels`，所有本地角色仍用同一
  Llama-3.1-8B checkpoint；这不是论文 Table 1 或 Figure 3(b) 原样复现。MedQA10 人工审核
  仍是 acceptable=30、suboptimal=13、blocking=7，且不是 held-out；现在这些是必须披露的
  解释限制，而不是停止科研运行的 hard cap。

旧 run 的冻结状态：

- `all-llama-five-dataset-full-v1` 在旧严格语义下完成 retrieval 7,663、summary 38,315、
  explore 7,663、generate 38,315 和全部 7,663 次 select 推理；select 当时为 7,596 `ok` +
  67 `invalid`，旧安全门随后退出，所以没有 rerank/reader/evaluate/metrics。
- 为实现宽容语义，runner/backend 和空输入处理源码已经变化，而 manifest 锁定源码 SHA。
  因此 `all-llama-five-dataset-full-v1`、`all-llama-smoke1-v19` 及更早 smoke 都只能作为历史
  证据，**不能在当前源码下使用同一 run-id 续跑**。不得篡改旧 manifest/records。
- 下一次五数据集正式实验必须使用新 run-id；建议
  `all-llama-five-dataset-lenient-v1`。截至本断点，该新 run 尚未启动。
- `released-code-intent/table1-full-v1` 的 7,663 条 retrieval donor 仍完整，可以由新 run
  验证后导入；不要重建 BM25/MedCPT retrieval。

无人值守命令（先 dry-run，再 start）：

```bash
cd /home/data3/txy/MedRGAG

# 零副作用：只打印八阶段命令，不创建 log、lock 或 artifact
./run_medrgag_all_llama.sh \
  --run-id all-llama-five-dataset-lenient-v1 \
  --retrieval-source-run \
  /home/data3/txy/MedRGAG/outputs_reproduced/llama3.1/medrgag/released-code-intent/table1-full-v1 \
  --dry-run

# nohup 后台执行完整八阶段
./run_medrgag_all_llama.sh start \
  --run-id all-llama-five-dataset-lenient-v1 \
  --retrieval-source-run \
  /home/data3/txy/MedRGAG/outputs_reproduced/llama3.1/medrgag/released-code-intent/table1-full-v1

# 一次性状态摘要 + 最后20行日志
./run_medrgag_all_llama.sh status \
  --run-id all-llama-five-dataset-lenient-v1

# 持续 tail 日志；Ctrl+C 只结束查看，不结束后台任务
./run_medrgag_all_llama.sh attach \
  --run-id all-llama-five-dataset-lenient-v1
```

脚本自动传 `--retry-pending-local`、用 `flock` 防同 run 并发，并写入
`runtime_logs/all-llama-<run-id>.state` 和 `.log`。技术故障修复后，可用相同锁定参数和
run-id 重启，必要时加 `--from-stage <stage>`；若源码或 manifest 参数变化则必须换新 run-id。

此前 assistant 对旧 tmux run 的周期轮询从未驱动下载、推理或阶段切换；旧 shell 循环本来
就是自动运行的。轮询只用于读取并转述状态，因而消耗了聊天 token。新脚本启动后不需要
assistant 常驻监督，用户可按需执行 `status` 或 `attach`。

当前自动测试为 35/35 通过，新增覆盖：科研宽容 invalid 可完成且可 resume、空 completion
作为模型结果保留、技术失败仍致命、空选择到 question-only reader、缺失 knowledge 位置
补齐、dry-run 零副作用、阶段范围，以及八阶段 shell 成功/真实非零错误停止。恢复时先读
`REPRODUCE_ALL_LLAMA.md`，确认新 run-id 不存在，再执行上面的 dry-run/start；不要恢复旧
`medrgag-allllama-full-v1` dead pane。

### 0.0 新服务器迁移与正在运行的正式流程

- 2026-08-16 项目从旧服务器复制到了新服务器；内容保持不变，但运行根目录从
  `/home/txy` 迁移为 `/home/data3/txy`。`.env`、`.env.example`、运行脚本和默认配置中的
  实际运行路径均已迁移；历史 manifests/Direct 输出中的旧绝对路径保留为 provenance，
  不参与本次正式 run。
- `.env` 仍为 mode `0600`，API key 未输出或改写；既有只读模型元数据请求已经验证
  `gpt-4o-mini-2024-07-18` 鉴权。2026-08-16 21:59 的首个真实 Summary smoke 请求已到达
  官方 API，但账户对全部请求返回 `429 credit_balance_exhausted`；因此尚无成功生成响应或
  usage，充值前禁止自动重试。
- Wikipedia 固定 revision `d76b9ad82135e352235d17e75921c49b68fd07b2` 已于
  2026-08-16 20:44:15 CST 下载完成：648/648 repo files、646/646 JSONL chunks、
  45,680,297,111 bytes；文件名连续、无空分片、无 `.incomplete`，下载命令退出 0，
  Xet 日志 0 WARN/0 ERROR。
- Wikipedia Lucene index 已完成：`JsonCollection + DefaultLuceneDocumentGenerator +
  16 threads`，29,913,202/29,913,202 documents，耗时 00:03:09；索引
  4,423,120,476 bytes、314 files、`segments_1`。Textbooks index 仍为 125,847 documents。
- 六类正式资源（Llama、MedCPT、两个 corpus、两个 Lucene index）已逐文件 SHA-256
  指纹并写入 `resource_manifests/resources.lock.json`；随后 `doctor --strict` 深度复核通过。
- 正式无 API retrieval 已于 2026-08-16 21:50:55 CST 完成，run 为
  `released-code-intent/table1-full-v1`：五数据集共 7,663/7,663 records、5/5
  `complete.json`、0 errors。每题均保存双 BM25 top-32 的 64 candidates 和 MedCPT top-5；
  retrieval 产物约 1.6 GiB。
- 独立 smoke run `table1-smoke10-v1` 的 MedQA retrieval 已完成 10/10。其 Summary 阶段按
  既定设计提交 50 个逻辑任务（10题×5文档），50/50 均返回
  `429 insufficient_quota / credit_balance_exhausted`：现有 50 个 records 全为 `pending`、
  50 个 RateLimitError error records、0 response_id、0 usage、无 complete marker。失败证据保留在
  `outputs_reproduced/llama3.1/medrgag/released-code-intent/table1-smoke10-v1/`；不要把它误认为
  成功 smoke，也不要在充值前传 `--retry-api-records`。
- smoke 最新日志路径记录在 `runtime_logs/current-smoke10-log.path`。充值后优先新建干净的
  smoke run-id，而不是覆盖失败 run；先审计 Summary 的 response_id、resolved_model、usage、
  finish_reason 和 errors，再运行 Explore/Generate/Select/Rerank/Reader/Evaluate。未经成功 smoke，
  不得启动正式 run 的 53,641 个 GPT 辅助请求。

恢复时先执行：

```bash
cd /home/data3/txy/MedRGAG
tmux list-sessions
tmux capture-pane -p -S -80 -t medrgag-post:pipeline
find outputs_reproduced/llama3.1/medrgag/released-code-intent/table1-full-v1/artifacts \
  -path '*/retrieval/records/*.json' -type f | wc -l
```

若 `medrgag-post:pipeline` 已正常退出，检查 `pane_dead_status=0`、五个
`retrieval/complete.json` 和 7,663 records；若意外退出，先读日志，不要删除现有 records，
修复外部原因后用相同 profile/run-id 重跑 retrieval 即可续跑。

用户当前目标已经从 Direct Response 明确切换为：复现 Table 1 的
`Llama3.1-8B reader + MedRGAG` 行。下方早期段落中“尚未安装/下载/实现”的描述是历史记录；
与本节冲突时，以本节和实际文件状态为准。

### 0.1 本轮已经实现

- 新建私密 `.env`（mode `0600`、已被 `.gitignore` 忽略）。2026-08-15 14:44 后诊断为
  `OPENAI_API_KEY` 已非空；16:04 又通过官方 `GET /v1/models/gpt-4o-mini-2024-07-18`
  元数据请求验证鉴权和该 snapshot 权限成功。只记录状态，不记录值或哈希；随后 API
  summary smoke 已发出请求但全部因余额不足失败，详见上方 0.0，未产生成功 usage。
- 新建 `.env.example`；默认 GPT 固定为 `gpt-4o-mini-2024-07-18`，temperature 1.2，
  OpenAI SDK retries=2、并发=16。仅填 key 不会产生调用，API stage 还要求
  `--allow-paid-api`。
- 新建 `src/config.py`。配置优先级为 process env > 显式 `--env-file` > 默认值；不再把
  dotenv 内容污染到全局环境；manifest 永不写入 key。
- 新建 `src/medrgag_prompts.py`：恢复初始提交历史 pyc 中完整 summary/explore ICL
  prompt，并冻结 13 个 prompt SHA-256；同时提供 Appendix D 规范化 profile。
- 新建 `src/medrgag_logic.py`：独立实现两种 option formatter、2/3 点 explore、固定 5 个
  generation slots、selection parser、reader prompt、作者/严格答案解析。
- 新建 `src/medrgag_artifacts.py`：per-item 原子落盘、flock、profile/input/upstream hash 链、
  completion marker、pending/invalid API 恢复保护。
- 新建 `src/medrgag_retrieval.py`：双语料 BM25、MedCPT rerank、Lucene 无 raw field 时的
  JSONL byte-offset 回读，避免上游每个 hit 整文件读取。
- 新建 `src/resource_fingerprints.py`：对 Llama、MedCPT、corpus、Lucene index 做流式
  SHA-256、原子 manifest、symlink/路径逃逸拒绝和变更验证。
- 新建 `prepare_medrgag.py`：doctor、无 sudo Java 21 安装、固定 revision 下载、Lucene
  建索引、完整性校验和资源指纹锁。
- 新建 `reproduce_medrgag_llama31.py`：八阶段正式 runner：
  `retrieval → summary → explore → generate → select → rerank → reader → evaluate`。
- 新建 `REPRODUCE_MEDRGAG.md` 和 `requirements-medrgag.txt`。
- 测试现为 18 项，包含单题八阶段 mock E2E、第二遍零新增调用、API failure 正确归属、
  pending 显式重试、付费 attempt 历史保留、资源指纹、配置/secret 和所有纯逻辑；全部通过。
- runner 已把 generator/reader batch size 锁进 profile，并逐 invocation 记录实际 batch；run 只锁
  稳定的 semantic resource lock，不会因审计时间戳变化而误伤 resume。
- `doctor --strict` 现在会核验 Java 21、实际 Lucene document count、资源锁结构、每个 manifest
  和全部锁定文件 bytes，而不是只检查文件是否存在。
- 正式 run manifest 记录 Python/依赖、PyTorch CUDA build、GPU UUID/型号/显存、驱动和
  `CUDA_VISIBLE_DEVICES`；这类执行环境改变时同一 run-id 会拒绝续跑。
- API record 显式重试前会把旧 pending/invalid 及 usage/raw response 按内容哈希归档到
  `attempts/`；error 同样保留历史，避免成功重试抹掉真实费用证据。
- 新增并启动 `continue_medrgag_no_api.sh 49165`：它等待当前 Wikipedia 下载 PID 后，自动
  复验 snapshot、建双索引、fingerprint、strict doctor，并运行五数据集完整 retrieval。
  脚本没有任何 OpenAI stage；恢复时检查该进程/日志，勿并行启动第二份索引。
- 新增 `monitor_medrgag_download.py`：只读显示完整 chunks/bytes、目标文件滚动有效速度、
  下载进程写盘活动、本次进程平均速度、ETA 以及 downloader/continuation PID。默认 5 秒刷新、
  120 秒滚动窗口；`Ctrl+C` 只退出监控。

### 0.2 已准备的环境与资源

- `.venv`：Python 3.10.12、torch 2.6.0、vLLM 0.8.5、transformers 4.53.2、
  openai 1.86.0、Pyserini 1.0.0；`pip check` 通过。
- Java：用户态 `/home/data3/txy/.local/medrgag-jdk-21`，OpenJDK 21.0.11；Ubuntu deb
  SHA-256 `1dda0b40056186afebe068a9ce3cec23416ec2b42418f576b53fa1a59616d777`。
  Debian 包的 25 个 `/etc/java-21-openjdk` 绝对 symlink 已物化为自包含文件；Java
  security 初始化和 Pyserini 均已验证。
- Textbooks：固定 commit `9c72838920a1323ffa867467d3f7aa7b36b0f994`，20 个 repo
  文件、18 个 chunks、211,564,327 bytes，下载完成。
- Textbooks Lucene：公开代码相同的 `JsonCollection + DefaultLuceneDocumentGenerator +
  16 threads` 命令建成；`segments_2`，125,847 documents，0 errors。真实检索确认索引
  不存 raw，offset fallback 工作正常。
- offset 测试生成了 3 个 Textbooks `line_offsets/*.u64le`，约 420 KiB；它们是正式检索
  本来也会生成的派生缓存，保留。资源 snapshot 统计和 fingerprint 明确排除 index/
  line_offsets。
- Wikipedia：固定 commit `d76b9ad82135e352235d17e75921c49b68fd07b2`，目标 648
  repo files、646 chunks、45,680,297,111 bytes、29,913,202 documents。2026-08-15 15:15
  已完成至少 22/646 chunks；16:13 时已到 89/646、13.70/45.68 GB（30.00%）。当前用 Xet、
  外层单 worker 续传；本次进程平均写盘约 2.4 MB/s，期间有自动重试的 TLS EOF。
  未完成前不能建正式 index。
- MedCPT：固定 commit `71caf65d4927987813984f54c284405a13fcca49`，已完整下载 10 files /
  438,938,843 bytes；权重 437,998,062 bytes 的 SHA-256 已重算为
  `61d5ccd48869e03500544525fc231641d7daa9ba267b202c82724750038dc1e0`，与公开 LFS 一致。
  真实 H20 smoke 已验证单对/4 对 score、排序、shape 与显存释放。
- 本地 Llama 模型仍在
  `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`；11 个运行必需文件、
  16,069,722,717 bytes 的内容指纹已试算为
  `efdc003f6b9bc148f3a542653cf6c54ceecc679d49e7560a15e79a5a4d07db6a`。
- 尚未生成 `resource_manifests/resources.lock.json`，因为 Wikipedia/MedCPT/第二个索引未完成。
- 尚未调用任何付费 OpenAI API，也尚未运行完整 MedRGAG retrieval/prediction。即使 key 已填，
  API stage 仍必须显式传 `--allow-paid-api`。

### 0.3 当前后台进程（恢复时先用 `ps`/doctor 重新核对）

当前只保留一个可续传下载（PID 会变化，恢复时以 `ps` 为准）：

```text
MEDRGAG_HF_DISABLE_XET=0 MEDRGAG_HF_DOWNLOAD_WORKERS=1 \
  .venv/bin/python prepare_medrgag.py download --resource wikipedia
```

Hugging Face 经本机 `127.0.0.1:7890` 代理。常规 HTTP 实测约 0.54 MB/s，当前受控 Xet
单 worker 约 2.8 MB/s；完整文件会原子落盘并由固定 revision/LFS SHA 校验。进程停止后可
安全重复相同命令续传。不要把“chunk 文件数量够”当成完成，
`inspect_resource` 现在还要求 repo file count 和总 bytes 精确相等。

当前 downloader PID 49165 和 continuation PID 50510 都仍挂在 Codex/VS Code PTY，未忽略
SIGHUP，不能视为可靠的跨 SSH 断线后台任务。若为了更换 SSH 反向代理而断线，必须先停止
continuation（否则它会在 30 秒内用旧代理重启 downloader），再向 downloader 发 SIGINT。
完整 chunks 和 `.cache/huggingface` metadata 会保留；当前单个 `.incomplete` 可能重下，绝不
删除 `.incomplete`、`.metadata` 或 `.lock`。

监控命令：

```bash
cd /home/data3/txy/MedRGAG
.venv/bin/python monitor_medrgag_download.py
```

安全暂停顺序（执行时先重新核对 PID/PGID，以下是本断点的 PID）：

```bash
ps -o pid,ppid,pgid,sid,stat,cmd -p 49165,50510
kill -TERM -- -50510   # 先停 continuation 整个进程组
while kill -0 50510 2>/dev/null; do sleep 1; done
kill -INT -- -49165    # 再温和暂停 downloader
```

若 downloader 在 60 秒后仍未退出，可再发一次 INT，最后才用 TERM；不要用 KILL。重连并确认
新代理可用后，在 `tmux new -s medrgag-wiki` 内重复固定 revision 下载命令；用 `Ctrl+B`、`D`
detach。不要同时再启动旧 continuation，先让下载命令明确退出 0，再恢复后续阶段。

### 0.4 资源完成后的下一步

```bash
cd /home/data3/txy/MedRGAG

# 1. 若 Wikipedia 下载进程已停止或失败，续传（.env 已固定 Xet + 1 worker）：
.venv/bin/python prepare_medrgag.py download --resource wikipedia

# 2. 建 Wikipedia index；Textbooks 命令会只验证现有 index：
.venv/bin/python prepare_medrgag.py index --corpus all

# 3. 深度锁定所有实际文件，再做 strict doctor：
.venv/bin/python prepare_medrgag.py fingerprint
.venv/bin/python prepare_medrgag.py doctor --strict

# 4. retrieval 不依赖 API，可先跑全量：
.venv/bin/python reproduce_medrgag_llama31.py \
  --profile released-code-intent --run-id table1-full-v1 --stage retrieval

# 5. key 已被检测为非空；仍须用户明确同意付费调用后，先严格按
#    REPRODUCE_MEDRGAG.md 做独立 10 题 smoke，审查 usage/费用/parse warnings，
#    再决定是否继续 full-v1 的付费阶段。
```

### 0.5 profile 与不能消歧的事实

- `released-code-intent` 是默认主结果：历史 pyc prompt、代码 reader temp=0.1、two-point
  分支按 2 点正确解析、最终 MedCPT rerank 开启。它修复公开代码显然损坏的接线和 `None`
  第三知识点行为，不是“所有 bug 的 byte-exact 执行”。
- `paper-faithful` 实际是 Appendix-D approximation：reader temp=0.2、全数据集 3+2、最终
  rerank 关闭；question-only prompt/seed 等借用代码，动态 ICL 规则缺失。
- 论文和 GitHub 没有给作者实际 corpus/index/model hashes、BM25 显式 k1/b、GPT seed、
  generator seed、完整 ICL 规则，因此最终只能称为透明工程复现，不能承诺逐位复得 71.43。
- 截至 2026-08-15，OpenAI 官方模型页仍列出 `gpt-4o-mini-2024-07-18` snapshot 和
  Chat Completions 支持；正式运行仍取决于用户账号权限与 rate limits。

---

## 以下第 1 节起是此前会话的历史快照

以下内容按用户要求保留全部目标演变、早期计划和当时结论，其中出现的“当前”“尚未安装”
等措辞描述的是较早断点。恢复工作时只以第 0 节和实际文件/进程状态为准。

## 1. 一句话断点

已经完成并验证了 Table 1 中 Llama3.1-8B **Direct Response** 的两套全量独立推理；尚未运行 Llama3.1-8B **MedRGAG** 全流水线。完整 MedRGAG 当前停在以下断点：

1. 论文方法、Table 1 数值、GitHub 全历史和外部公开资源均已审计。
2. 已确认语料 chunks、MedCPT、Llama 模型和 GPT 日期快照并非完全缺失。
3. 五个数据集的 retrieval snippets 和预建 Lucene 索引确实没有发布，需要重建。
4. 当前公开 HEAD 不能直接运行 MedRGAG，必须做一套可审计的修复版 runner。
5. 论文与代码存在数个无法自行唯一消歧的实验配置冲突。
6. 本机尚未安装检索环境、未下载语料和 MedCPT，也没有 OpenAI API 凭据。

因此当前可以做“透明、可审计的独立工程复现”，但不能诚实承诺逐项精确复得论文宏平均 `71.43%`。

## 2. 本次对话中的目标演变

按发生顺序：

1. 对话最初有问候和一个与项目无关、要求不联网回答时点事实的问题；该请求随后被新的论文复现请求替代，没有产生项目文件或结论。
2. 用户提供论文 PDF，要求“复现该文章的 llama3 部分”。
3. 对论文方法、Table 1、附录提示、数据集划分和环境设置进行了全文提取。
4. 对当前机器、上游 GitHub 仓库、公开输出、模型和依赖进行了只读盘点。
5. 发现完整 MedRGAG 不能直接运行后，先实现并实际运行了公开材料足以独立完成的 Direct Response 行。
6. 用户追问是否只复现了 Direct Response；结论是：是，完成的确实只是 Direct Response，而不是 MedRGAG。
7. 用户继续确认 retrieval snippets、Textbooks/Wikipedia BM25/Lucene 索引和 MedCPT rerank 是否缺失。
8. 用户最终把目标明确为 Table 1 的 `Llama3.1-8B reader + MedRGAG` 行，并要求在声称缺少前先检查论文和 GitHub。
9. 随后检查了 PDF 全文、GitHub 当前分支/全部提交历史、已删除的历史字节码、外链 Hugging Face/ModelScope 资源和 OpenAI 官方模型文档。
10. 当前请求是把上述所有工作、结论和恢复计划固化到本文档。

## 3. 当前完成状态

### 3.1 已完成

- [x] 阅读论文全部 12 页并提取 Llama3.1 相关实验设置。
- [x] 提取 Table 1 的 Llama3.1-8B reader 全部 9 个方法结果。
- [x] 明确 MedRGAG 的 Llama 主结果不是全 Llama 流水线。
- [x] 核对五个数据集的 split、题数和指标。
- [x] 克隆并固定公开仓库 HEAD。
- [x] 审计 GitHub 唯一公开分支、全部 6 次提交、无 tag/release 的事实。
- [x] 审计发布的 benchmark、Qwen predictions 和 MedQA 中间缓存。
- [x] 盘点本机 GPU、内存、磁盘、Python 和缺失依赖。
- [x] 下载完整的本地 Llama-3.1-8B-Instruct 权重。
- [x] 创建最小 Direct Response 虚拟环境。
- [x] 创建可审计的 Direct Response runner。
- [x] 做单题 smoke test。
- [x] 全量运行 7,663 题的 `released-code` profile。
- [x] 全量运行 7,663 题的 `paper-appendix` 敏感性 profile。
- [x] 同时计算作者宽松解析口径和严格解析诊断口径。
- [x] 对结果 ID、题数、分数和宏平均做独立复算。
- [x] 核实外部 Textbooks/Wikipedia、MedCPT、Llama 和 GPT snapshot 的公开状态。
- [x] 列出公开 MedRGAG 代码的直接崩溃点、路径错误和不确定语义。

### 3.2 尚未完成

- [ ] 没有运行任何一个数据集的完整 Llama MedRGAG 流水线。
- [ ] 没有下载 Textbooks/Wikipedia corpus 到本机。
- [ ] 没有建立两个 Lucene/BM25 索引。
- [ ] 没有下载/固定本地 MedCPT-Cross-Encoder。
- [ ] 没有生成五个数据集的 retrieval snippets。
- [ ] 没有调用 GPT-4o-mini 生成缺失的 summary/explore/selection。
- [ ] 没有生成其余四个数据集的 Llama background documents。
- [ ] 没有生成 Llama MedRGAG reader predictions。
- [ ] 没有运行 Table 1 的 Vanilla RAG、MedRAG、i-MedRAG、GENREAD、MedGENIE、GRG、CGAP。
- [ ] 没有联系作者解决论文—代码冲突。
- [ ] 本次新增脚本、报告和本文档尚未提交到 Git。

## 4. 论文目标和方法定义

### 4.1 Table 1：Llama3.1-8B reader 区块

| Method | MedQA-US | MedMCQA | MMLU-Med | PubMedQA* | BioASQ-Y/N | 宏平均 |
|---|---:|---:|---:|---:|---:|---:|
| Direct Response | 67.48 | 58.45 | 75.48 | 55.40 | 76.38 | 66.64 |
| Vanilla RAG | 67.24 | 58.38 | 75.85 | 50.20 | 73.30 | 64.99 |
| MedRAG | 68.42 | 59.32 | 76.95 | 52.00 | 75.24 | 66.39 |
| i-MedRAG | 70.62 | 60.63 | 77.31 | 53.80 | 76.74 | 67.82 |
| GENREAD | 70.07 | 60.89 | 78.15 | 54.60 | 78.32 | 68.41 |
| MedGENIE | 68.81 | 60.24 | 78.24 | 56.60 | 80.26 | 68.83 |
| GRG | 68.97 | 60.89 | 76.77 | 57.00 | 82.36 | 69.20 |
| CGAP | 71.64 | 60.60 | 78.60 | 58.20 | 79.94 | 69.80 |
| **MedRGAG** | **74.63** | **61.77** | **80.90** | **57.80** | **82.04** | **71.43** |

目标 MedRGAG 行对应的整数正确数是：

| 数据集 | 正确数/总数 |
|---|---:|
| MedQA-US | 950 / 1,273 |
| MedMCQA | 2,584 / 4,183 |
| MMLU-Med | 881 / 1,089 |
| PubMedQA* | 289 / 500 |
| BioASQ-Y/N | 507 / 618 |

宏平均是五个百分比的未加权算术平均，不是按总题数加权。

### 4.2 目标流水线

```text
question + 按 key 排序的 options
  ├─ Textbooks BM25 top-32
  └─ Wikipedia BM25 top-32
            │
            └─ 合并 64 篇 → MedCPT rerank → retrieved top-5
                                      │
                                      ├─ GPT-4o-mini：逐篇 summary（5 次/题）
                                      ├─ GPT-4o-mini：explore 缺失知识（1 次/题）
                                      └─ Llama-3.1-8B：生成 5 篇补充文档
                                                              │
retrieved 5 + generated 5 ────────────────────────────────────┘
            │
            └─ GPT-4o-mini KADS selection：选最多/目标 5 篇
                                      │
                                      └─ MedCPT 再排序
                                                │
                                                └─ Llama-3.1-8B reader CoT/JSON
                                                          │
                                                          └─ locate_answer → accuracy
```

目标模型组合：

- generator：LLaMA-3.1-8B-Instruct，zero-shot。
- reader：LLaMA-3.1-8B-Instruct。
- summarizer、explorer、integrator/selector：GPT-4o-mini。
- sparse retriever：Pyserini/Lucene BM25。
- reranker：`ncbi/MedCPT-Cross-Encoder`。

### 4.3 数据集

| 仓库 key | 论文名称 | 使用划分 | 题数 | 论文 Avg.L | 选项数/说明 |
|---|---|---|---:|---:|---|
| `medqa` | MedQA-US | English test | 1,273 | 177 | 4 |
| `medmcqa` | MedMCQA | dev | 4,183 | 26 | 4；官方 test label 不公开 |
| `mmlu` | MMLU-Med | test | 1,089 | 63 | 6 个医学子领域 |
| `pubmedqa` | PubMedQA* | 官方 500 test | 500 | 24 | 3；移除原始 contexts |
| `bioasq` | BioASQ-Y/N | 2019–2023 Task B gold test | 618 | 17 | Yes/No |

`benchmark.json` 实际还包含不属于当前 Table 1 五数据集目标的 `medxpertqa` 2,450 题，因此文件总计 10,113 题；当前目标五集共 7,663 题。Direct Response runner 只处理这五个目标 key。文件 SHA-256：

```text
0ab94ad8a680028fe3eaea2bcee448045209b1b3291aa8acb5773117839f8daa
```

### 4.4 论文明确给出的设置

- 每个语料 BM25 top-32，合计 64，再由 MedCPT 取 top-5。
- Textbooks 约 125.8K chunks；Wikipedia 约 29.9M chunks。
- KGCC 论文描述为识别 3 个缺失知识点，每点生成 1 篇，再直接根据问题生成 2 篇，共 5 篇。
- 5 retrieved + 5 generated 交给 KADS，最终给 reader 最多/目标 5 篇。
- generator temperature `1.2`，最多 `256 tokens`。
- explorer temperature `1.2`。
- reader temperature 在论文 Appendix A 写为 `0.2`。
- 原论文环境：Python 3.10、PyTorch 2.6、vLLM、3×NVIDIA A40（论文写每张 45GB）。
- 论文 Appendix D 给出 summary、explore、generation、selection 和 answer prompt 的规范化文本。

代码还提供了更多运行设置：

- generator：`temperature=1.2, top_p=0.9, top_k=50, max_tokens=256, presence_penalty=1.0`，无 seed；batch 64；TP=2。
- reader：`temperature=0.1, seed=42, max_tokens=512`；batch 128；TP=2。
- system message：`You are a helpful assistant.`
- GPT snapshot：`gpt-4o-mini-2024-07-18`；temperature 1.2；16 个线程；未设置 seed/max_tokens/top_p。

### 4.5 Figure 3 的辅助发现

这些不是当前最终目标，但本轮已从 PDF 矢量柱高恢复，reader 均为 Qwen2.5-7B，适合后续 sanity check：

- 不同 generator，MedQA/MedMCQA/MMLU：
  - Llama3.1-8B：`75.57 / 62.13 / 81.63`
  - Qwen2.5-14B：`76.33 / 63.76 / 84.85`
  - GPT-4o-mini：`78.16 / 67.10 / 86.32`
- 不同 auxiliary model，MedQA/MedMCQA/MMLU：
  - GPT-4o-mini：`75.57 / 62.13 / 81.63`
  - Qwen2.5-14B：`70.91 / 61.06 / 78.33`
  - Llama3.1-8B：`69.91 / 59.79 / 77.96`

这些数值是从 PDF 图形恢复的两位小数，不应当成作者发布的机器可读表格。

### 4.6 其他 baseline 的附录线索

这次没有运行这些 baseline，但论文附录给出的实现线索已记录，便于以后扩展整个 Llama 区块：

- 原则上共享 corpus、retriever、generator 和最终 top-5 设置。
- MedRAG 按原设使用 4 个 retrievers 和 reciprocal-rank fusion。
- GENREAD 从 training data 每题取 top-1，构造 5 个 ICL clusters 并生成 pseudo-context。
- CGAP 生成 5 个 contexts 并 majority vote。
- GRG 生成 10 个 candidates，再由 MedCPT 选 top-3。
- i-MedRAG 的迭代次数等关键设置没有披露。
- 论文只报告单次 accuracy，没有重复运行、方差/置信区间或显著性检验，也没有完整声明无效 JSON 的处理规则。

## 5. 本次新增文件与 Git 状态

### 5.1 当前 Git 状态

- branch：`master`，与 `origin/master` 同为 `0057853...`。
- 上游 tracked 文件没有任何修改。
- 没有 staged changes，没有本地 commit。
- 创建本文前存在 6 个 untracked 文件；本文
  `LLAMA31_REPRODUCTION_HISTORY.md` 创建后为第 7 个。
- `.venv/` 和 `outputs_reproduced/` 已由新 `.gitignore` 忽略。

### 5.2 新增文件

| 文件 | 用途 | 创建本文前 SHA-256 |
|---|---|---|
| `.gitignore` | 忽略 venv、复现输出和 Python cache | `d348d3fb5fafaab8ada45de8654f0783a062f1a90b8f0921a83c11d54b3392c0` |
| `requirements-reader.txt` | Direct Response 最小固定环境 | `985a9c5c7c946aedc0fb55c778cf082c99268b96746e00b62fd89b757a25911d` |
| `reproduce_llama31.py` | Direct Response 可审计 runner | `cf87287822ceea9b91cbfe5f8984ab4ae92d35c6c2f66dc3f2c13a252d4198a6` |
| `validate_release.py` | 校验发布产物和本地复现结果 | `7a8ad9ed6e0bb38a3c6e4eae1823b014a44a7e6095f7e70eac6df75828ea8298` |
| `REPRODUCE_LLAMA.md` | 使用命令、论文目标表和早期边界说明 | `29138e667283004d1ed281a6672995c74b31cab9f5f01f503cf071a1d4346363` |
| `RESULTS_LLAMA.md` | 两套 Direct Response 结果报告 | `bf197cc95ead5ffcd5a8d0033b650e52772a0c03ed5a066d86261689d5a9ee77` |
| `LLAMA31_REPRODUCTION_HISTORY.md` | 历史断点与会话交接文档 | 不在文件内嵌入自指 hash；恢复时可对该文件运行 `sha256sum` |

注意：如果这些文件在恢复前已经变化，应以 `git status`、文件内容和结果 JSON 为准，不要盲信上述 hash。

## 6. Direct Response 已完成工作

### 6.1 环境和模型

虚拟环境：`/home/data3/txy/MedRGAG/.venv`

已确认版本：

```text
Python          3.10.12
torch           2.6.0+cu124
vLLM            0.8.5
transformers    4.53.2
numpy           1.26.4
```

本地完整模型：

```text
/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct
```

- 约 15GB。
- 包含 4 个 safetensors shards、tokenizer 和 config。
- 每个正式结果 JSON 的 `model_artifact` 内记录了权重、tokenizer 和 config 的大小与 SHA-256。
- `/home/data3/txy/models/NousResearch-Meta-Llama-3.1-8B-Instruct` 只有配置/说明文件，没有权重，不能用于离线运行。

关键模型 hash：

```text
model-00001-of-00004.safetensors  2b1879f356aed350030bb40eb45ad362c89d9891096f79a3ab323d3ba5607668
model-00002-of-00004.safetensors  09d433f650646834a83c580877bd60c6d1f88f7755305c12576b5c7058f9af15
model-00003-of-00004.safetensors  fc1cdddd6bfa91128d6e94ee73d0ce62bfcdb7af29e978ddcab30c66ae9ea7fa
model-00004-of-00004.safetensors  92ecfe1a2414458b4821ac8c13cf8cb70aed66b5eea8dc5ad9eeb4ff309d6d7b
tokenizer.json                    79e3e522635f3171300913bb421464a87de6222182a0570b9b2ccba2a964b2b4
tokenizer_config.json             177c7b61e616fecb84c17ce0591acb92c6c4d60e9ac5ababfb940ff23bbcd424
```

### 6.2 Runner 的重要语义

`reproduce_llama31.py` 只实现 Direct Response，不是完整 MedRGAG。

- `released-code`：使用发布仓库 `rag_template` 的字节级文本，包括两个有 tokenizer 影响的行尾空格；temperature 0.1。
- `paper-appendix`：使用 Appendix D 的规范化转录 reader prompt；temperature 0.2。
- 两者均使用 seed 42、max tokens 512、batch 128、TP=2。
- 未人为限制 `max_model_len`，与发布代码一致，模型原生 context length 为 131,072。
- 题目格式是 question 加按原 options key 顺序输出的 `A: ...` 等选项。
- 使用模型自身 chat template 和 system prompt。
- 所有 prompts 分 batch 128 提交给 vLLM。
- 输出同时保存：原始模型文本、作者解析结果、严格解析结果、解析规则和运行 manifest。
- 运行前会一次性检查所有目标输出碰撞，避免 smoke/full 共用目录污染结果。
- 对本地模型记录 tokenizer/config hash；正式运行还记录全部权重 hash。

Prompt/hash：

```text
released-code user template SHA-256  a7396cd113729de20fbce77e50bf4f3b39b17312454f4013f30399aaa833eb3d
paper-appendix user template SHA-256 5373fdb17149fb94467ead80d4361e239e4c16236834df92c434e1afab5b3e86
tokenizer chat template SHA-256       e10ca381b1ccc5cf9db52e371f3b6651576caee0a630b452e2816b2d404d4b65
```

### 6.3 已执行的运行

1. 单题 MedQA smoke test成功：

   ```text
   outputs_reproduced/smoke/released-code/released-code/
   ```

2. 7,663 题 `released-code` 全量运行：

   ```text
   outputs_reproduced/llama3.1/direct/released-code/
   elapsed_seconds = 510.9268934726715
   ```

3. 7,663 题 `paper-appendix` 全量敏感性运行：

   ```text
   outputs_reproduced/llama3.1/direct/paper-appendix/
   elapsed_seconds = 558.1838757991791
   ```

两次正式运行均使用 2×H20、tensor parallel size 2。

### 6.4 Direct Response 结果

| 数据集 | released-code 作者口径 | released-code 严格口径 | 论文 Direct | paper-appendix 作者口径 | paper-appendix 严格口径 |
|---|---:|---:|---:|---:|---:|
| MedQA-US | 64.65 | 62.84 | 67.48 | 46.82 | 32.52 |
| MedMCQA | 58.36 | 56.83 | 58.45 | 50.90 | 40.64 |
| MMLU-Med | 74.10 | 72.54 | 75.48 | 55.56 | 47.47 |
| PubMedQA* | 54.40 | 54.00 | 55.40 | 53.60 | 33.80 |
| BioASQ-Y/N | 75.40 | 73.14 | 76.38 | 70.87 | 63.75 |
| 宏平均 | **65.38** | **63.87** | **66.64** | **55.55** | **43.64** |

`released-code` 相对论文宏平均低 `1.2550` 个百分点；`paper-appendix` 只是敏感性实验，不能当作论文主结果复现。

### 6.5 解析器审计

论文/发布代码口径使用 `src/evaluate_utils.py::locate_answer`：

- 宽松正则会从非严格 JSON 或后续说明中抽取 A-D。
- 解析失败时默认返回 `A`。
- 为与论文可比，主分数保留此口径。

额外实现了严格解析作为诊断：

- JSON 成功时，`answer_choice` 必须是该题合法的单一选项。
- fallback 只接受明确且完整的 quoted `answer_choice` 字段。
- 不给格式错误输出默认赋 A。

`released-code` 的 7,663 条输出中：

- 422 条无法严格解析。
- 319 条归一化后仍接近/达到 512-token 上限。
- 311 条缺失或未完成 `answer_choice`，强烈提示输出被截断。
- 36 条是较短的拒答或“无法核验”。
- 作者解析器仍给 422 条全部分配了选项并计对 123 条。
- 另有 9 条 strict 和 author 在可提取答案上不同；作者正则可能先命中解释中的 `: A/B/C/D`。

因此：`65.38%` 是与发布代码同口径的主复现值；`63.87%` 是格式稳健性诊断，不应替换主表口径。

### 6.6 已完成的完整性验证

2026-08-15 再次运行：

```bash
cd /home/data3/txy/MedRGAG
python3 validate_release.py
```

结果：退出码 0，并确认：

- 五个 benchmark 的题数正确。
- 两套 Direct Response 各有完整的 7,663 个唯一 ID。
- ID 与 `benchmark.json` 一一对应，无缺失、重复或中途失败。
- 所有保存指标与独立复算一致。
- 发布的五套 Qwen2.5 MedRGAG predictions 与论文对应分数一致。
- 五个 retrieval 文件均缺失。

注意：validator 把 retrieval 缺失打印为 `BLOCKED` 状态，但当前不会因此返回非零；退出码 0 只表示 benchmark、发布预测和已有 Direct Response 结果的可验证完整性通过。

## 7. 发布仓库及公共资源审计

### 7.1 GitHub 全历史

公开仓库在核查时：

- 只有 `master` 一个公开分支。
- 没有 tag、release 或隐藏在其他公开 branch 的运行代码。
- 全部历史只有 6 个提交。
- 源码从初始提交后基本没有实质修复；后续主要是 README 修改和删除误提交的 pyc。
- 全历史没有 retrieval outputs、Lucene indexes、Llama predictions 或完整 run manifest。

关键提交：

```text
0057853  Update README.md                  当前 HEAD
047e2ef  Update README.md
bbe9d18  Delete template.cpython-311.pyc
452e260  Delete evaluate_utils pyc
78857d4  Create README.md
8434041  first commit
```

### 7.2 发布数据和输出

上游原始 `outputs/` 包含：

- 五个数据集的 Qwen2.5 MedRGAG predictions。
- Qwen prediction 只含题目、选项、gold、模型答案和模型输出，不含 reader 最终 documents。
- 发布的 Qwen2.5 MedRGAG 五项分数经独立校验为 `75.57 / 62.13 / 81.63 / 51.60 / 84.79`；这是作者产物验证，不是本机重新推理。
- 只有 MedQA 带 1,273 题的四类生成阶段缓存：
  - `outputs/medqa/docs/generate/snippets.json`
  - `outputs/medqa/docs/generate/snippets_inter_summary.json`
  - `outputs/medqa/docs/generate/snippets_inter_explore.json`
  - `outputs/medqa/docs/generate/snippets_final_select.json`
- 其余四个数据集没有 summary/explore/generated/selection 缓存。
- 五个数据集都没有 `docs/retrieval/snippets.json`。
- 没有任何 Llama prediction。

MedQA 的 KADS selection 统计：

- 1,242 题选 5 篇。
- 26 题选 4 篇。
- 4 题选 3 篇。
- 1 题选 2 篇。
- 920/1,273 题至少引用一个 retrieval passage（索引 0–4）。

因为对应 retrieval 文本缺失，现有 MedQA 缓存也无法单独恢复完整 reader 输入。若重建的检索与作者当时不逐项一致，不应把这些缓存混进声称“严格复现”的运行。

### 7.3 公开但没有固化 revision 的资源

下列内容在论文 GitHub 仓库内不是实体文件，但有明确公开来源：

| 资源 | 公开位置 | 2026-08-14 审计结论 |
|---|---|---|
| Textbooks chunks | `https://huggingface.co/datasets/MedRAG/textbooks` | 125,847；当前 HEAD `9c728389...`；内容提交早于实验 |
| Wikipedia chunks | `https://huggingface.co/datasets/MedRAG/wikipedia` | 29,913,202；当前 HEAD `d76b9ad8...`；内容提交早于实验 |
| MedCPT reranker | `https://huggingface.co/ncbi/MedCPT-Cross-Encoder` | 当前 HEAD `71caf65d...`；模型内容自 2023 年后稳定 |
| Llama model | `https://www.modelscope.cn/models/LLM-Research/Meta-Llama-3.1-8B-Instruct` | 当前 HEAD `359efdbb...`；权重早于实验且后续主要是说明变化 |
| GPT auxiliary | OpenAI API | 代码固定 `gpt-4o-mini-2024-07-18`；官方文档核查时仍列出该 snapshot |

结论要分两层表述：

- **工程层面**：这些资源都能取得，不应再说“语料、MedCPT、Llama 或 GPT snapshot 完全没有提供”。
- **严格 provenance 层面**：论文/仓库没有记录不可变 revision、checksum 和完整 run manifest，仍无法证明当前公开 HEAD 与作者运行时逐字节相同。

## 8. retrieval snippets：确认缺失但可以重建

经 `validate_release.py`、`git log --all` 和公开 branch/tag 检查，以下文件在所有公开历史中都不存在：

```text
outputs/medqa/docs/retrieval/snippets.json
outputs/medmcqa/docs/retrieval/snippets.json
outputs/mmlu/docs/retrieval/snippets.json
outputs/pubmedqa/docs/retrieval/snippets.json
outputs/bioasq/docs/retrieval/snippets.json
```

预建 Lucene 索引也没有发布。不过 `src/utils.py` 已提供基本下载和建索引逻辑：

1. 从 Hugging Face 下载 Textbooks 和 Wikipedia chunks。
2. 用 `pyserini.index.lucene`、`JsonCollection`、`DefaultLuceneDocumentGenerator`、16 threads 建索引。
3. 每个语料独立搜索 top-32。
4. `src/medrgag.py` 把 question 和排序后的 options 拼成 query。
5. 合并 64 篇后用 MedCPT query-document cross encoder 打分。
6. 保留 top-5 retrieved snippets。

BM25 `k1/b`、analyzer 和额外 preprocessing 没有显式设置，代码继承 Pyserini/Lucene 默认行为；`requirements.txt` 固定 `pyserini==1.0.0`。所以这是可重建的运行产物，不是语料本身不可恢复，但应保存新索引、工具版本、命令、revision 和 checksum。

## 9. 当前公开 MedRGAG 代码不能直接运行的原因

以下均已在当前 HEAD 逐行确认；实现修复时必须逐项记录，不应静默修改后声称“原仓库原样运行”。

1. `src/medrgag.py:22` 导入不存在且全历史从未提供的 `src/config.py`；该 import 看起来未使用。
2. `src/medrgag.py:25-31` 的 Llama、Qwen、MedCPT 等路径全是 `****` 占位符。
3. `main.py:46` 使用未定义变量 `llm_name`。
4. `src/llm_by_gpt.py:238-255` 忽略 `Function_LLM` 的 `mode` 参数，读取不存在的全局 `args.mode/args.data_path`。
5. 当前 `src/template.py` 的 summary/explore prompt 含 `{example}`，调用方 format 时没有传 `example`，会触发 `KeyError`。
6. MedMCQA/BioASQ 分支引用当前源码未定义/未 import 的 `knowledge_explore_template_two_know`。
7. 即使恢复 two-point prompt，`extract_knowledge_str` 仍固定提取 3 个知识点，可能给 2-point 输出追加字符串 `"None"`。
8. `main.py:92` 把 explore 的整条 dict 作为 `explore_contents`，generator 却按整数索引读取 list，必然结构错误；应明确取其中 `explore_snippets`。
9. selection 阶段读取 `snippets_gen_gpt.json`，主程序实际生成/写入的是 `snippets.json`。
10. reader 在 `src/medrgag.py:231` 使用不存在的 `self.tokenizer`；构造函数实际定义的是 `self.reader_tokenizer`。
11. GPT 阶段硬编码 `./outputs`，与 `main.py --results_dir` 接线不一致。
12. 16 线程共享 JSONL writer，没有锁、原子写、断点续跑或逐题幂等保护；文件每次以 `w` 打开。
13. selection parser 可产生空列表、不足 5、重复或非法索引，并用 `%10` 静默纠错；下游没有严格校验。
14. KADS selection 后，`main.py:131` 又调用 MedCPT 对选中项排序；论文没有明确描述这次最终重排，是否保留必须写入 profile。
15. README 激活了错误环境名 `automir`，并把 Transformers 版本误写为不存在的 `44.53.2`；`requirements.txt` 中才是 `4.53.2`。

这些问题属于可修工程 bug；但因为发布仓库没有作者实际使用的 patch，部分修复会涉及对作者意图的推断。

## 10. Git 历史中可恢复但当前源码损坏的 prompt

不能再简单声称 ICL 示例或 two-knowledge prompt “GitHub 完全没提供”。

初始提交 `8434041` 曾误提交：

```text
src/__pycache__/template.cpython-311.pyc
```

该文件后来在 `bbe9d18` 删除，但仍能从 Git object 恢复。对其字符串常量检查确认含有：

- 完整的 summary 固定 ICL 示例。
- 完整的 3-point explorer 固定 ICL 示例。
- 2-point、1-point、up-to-5 knowledge prompt 变体。
- question-only generation prompt 和其他模板。

只读恢复示例命令：

```bash
git show 8434041:src/__pycache__/template.cpython-311.pyc > /tmp/medrgag-template.cpython-311.pyc
strings /tmp/medrgag-template.cpython-311.pyc
```

真正仍缺失的是：论文正文声称 summarizer 的 ICL demonstrations 从 training corpus 检索，但没有说明检索算法、示例数、格式或是否逐题变化。历史 pyc 更像固定示例。Table 1 到底使用“固定示例”还是“动态检索示例”无法从公开材料唯一判断。

## 11. 论文—代码及公开材料内部冲突

这些冲突是精确复现的核心不确定性：

| 项目 | 论文/附录 | 当前代码或历史证据 | 影响 |
|---|---|---|---|
| reader temperature | 0.2 | 0.1，seed 42 | 直接改变采样和准确率 |
| missing knowledge 数量 | 所有题 3 个，再 question-only 2 篇 | 代码意图对 MedMCQA/BioASQ 使用 2 个 | 改变生成文档组成 |
| generation 长度 | Appendix A：最多 256 tokens | prompt：不超过 256 words；代码 max_tokens=256 | 截断边界不一致 |
| summarizer ICL | 从 training corpus 检索 demonstrations | 历史 pyc 中是固定示例 | prompt 输入无法唯一还原 |
| KADS 数量 | 通常描述 top-5 | prompt/缓存允许 up to 5 | reader context 数量可变 |
| KADS 后顺序 | 论文没有明确二次重排 | 代码再用 MedCPT 排序选中项 | reader 文档顺序不同 |
| prompt 字面量 | Appendix D 规范化文本 | 公开 executable-style template 不同 | Direct Response 已证明影响很大 |
| GPT sampling | temperature 1.2 | 无 seed/max_tokens/top_p；16 threads | 中间产物不可逐次恢复 |
| Llama generator sampling | temperature 1.2 | 无 seed | 四个数据集无缓存，随机结果不可恢复 |

没有作者的实际 run manifest、修复后源码或中间输出时，不应任意选择更高分设置再称为一次统一实验。

## 12. 真正缺失、可重建和已提供的最终分类

### 12.1 已提供或可高置信恢复，不应列为完全缺失

- 五个 benchmark 和 gold labels。
- Textbooks/Wikipedia corpus 内容和准确 chunk 数量。
- 基本 Pyserini Lucene index builder 逻辑。
- BM25 每源 top-32、MedCPT top-5 流程。
- `ncbi/MedCPT-Cross-Encoder` 模型身份和 pair scoring 实现。
- Llama-3.1-8B-Instruct 模型身份。
- GPT snapshot `gpt-4o-mini-2024-07-18`。
- generator、reader 的大部分 SamplingParams。
- question-only generation prompt。
- Appendix D prompts。
- 固定 summary/explore ICL 示例和 two-point 模板，可从历史 pyc 恢复。
- 依赖的大部分版本，尤其 `torch==2.6.0`、`vllm==0.8.5`、`transformers==4.53.2`、`pyserini==1.0.0`。

### 12.2 仓库没有附带，但可以自己生成

- 两个 Lucene indexes。
- 五个数据集的 BM25/MedCPT retrieval outputs。
- GPT summary/explore/selection 中间产物。
- Llama generated documents。
- Llama MedRGAG predictions。
- 完整评测报告。

### 12.3 从公开材料确实无法唯一恢复

- 作者实际用于 Table 1 的可执行代码/config patch。
- reader temperature 冲突的最终选择。
- MedMCQA/BioASQ 使用 2 还是 3 个 missing points。
- 固定 ICL 还是动态 training-corpus retrieval ICL，以及后者的算法。
- stochastic generator/GPT 的随机种子和作者当次输出。
- 作者的索引 checksum、retrieval outputs 和 run manifest。
- Llama、MedCPT、corpus 的作者运行时不可变 revision/hash。
- 作者实际 API endpoint/proxy 和服务侧请求行为。

## 13. 当前机器环境快照

2026-08-15 核验：

### 13.1 硬件

```text
GPU             4 × NVIDIA H20
每卡显存        97,871 MiB，核验时约 97,367 MiB free
互联            NV18
Driver          570.195.03
CUDA            12.8
Compute cap.    9.0
RAM             367 GiB，总可用约 362 GiB
CPU             32 vCPU
Swap            0
根盘可用        约 563 GiB
/home/data 可用 约 364 GiB
OS              Ubuntu 22.04.5 LTS，Linux 5.15
```

硬件足以运行 Llama-3.1-8B BF16、MedCPT 和检索；正式 Direct Response 已在 2×H20 上完成。

### 13.2 软件和缺失项

- 系统 Python：3.10.12。
- `.venv`：约 7.7GB，Direct Response 依赖已安装。
- `.venv` 的 `pip check` 当前无损坏依赖。
- `.venv` 当前没有完整 MedRGAG 所需的 `faiss-gpu==1.7.2`、`deepspeed==0.17.4`、`python-liquid==1.10.2`、`sentence-transformers==5.0.0`、`pyserini==1.0.0`、`datasets==3.6.0` 和 `scikit-learn`。
- 仓库要求 `tiktoken==0.9.0`，当前 `.venv` 是 `0.13.0`，完整运行前要决定是否严格降级。
- 系统没有 `java`/`javac`，`JAVA_HOME` 未设置。
- 没有 `git-lfs`。
- Docker CLI 虽存在，但当前用户没有 daemon 权限。
- 没有 conda/mamba/uv；`venv` 可用。
- 本机没有 Textbooks/Wikipedia corpus、Lucene index 或 MedCPT 本地模型。

### 13.3 缓存和凭据陷阱

当前环境：

```text
HF_HOME=/home/data/hf_cache
TRANSFORMERS_CACHE=/home/data/hf_cache/transformers
```

这些目录对当前用户不可写。下载新资源前应显式改为可写目录，例如：

```bash
export HF_HOME=/home/data3/txy/.cache/huggingface_medrgag
export HF_HUB_CACHE="$HF_HOME/hub"
unset TRANSFORMERS_CACHE
```

当前均未设置：

```text
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_API_BASE
AZURE_OPENAI_API_KEY
HF_TOKEN
HUGGING_FACE_HUB_TOKEN
```

不要把 API key 写入源码、本文档、shell history 或 Git。应通过受控环境变量/secret manager 提供。

## 14. 全量 MedRGAG 的工作量估算

设总题数 `N=7,663`，按发布代码意图：

| 阶段 | 调用/打分量 |
|---|---:|
| BM25 search | `2N = 15,326` 次搜索 |
| 首轮 MedCPT | `64N = 490,432` 个 query-document pairs |
| 最终 MedCPT | 通常 `5N = 38,315` pairs |
| GPT summary | `5N = 38,315` 次 |
| GPT explore | `N = 7,663` 次 |
| GPT selection | `N = 7,663` 次 |
| GPT 合计 | **53,641 次** |
| Llama generator | `5N = 38,315` 次 |
| Llama reader | `N = 7,663` 次 |
| Llama 合计 | **45,978 次** |
| 所有 LLM 请求 | **99,619 次** |

两轮 MedCPT 合计通常约 `490,432 + 38,315 = 528,747` 个 pairs。

GPT 调用按数据集：

```text
MedQA       8,911
MedMCQA    29,281
MMLU        7,623
PubMedQA    3,500
BioASQ      4,326
```

这要求在开始前确认 API 预算、组织 rate limits、缓存/断点恢复策略和用户授权。不要因为已有 MedQA 缓存就默认可跳过该数据：缓存没有 retrieval provenance。

## 15. 两种可执行复现 profile

如果作者没有补充，建议明确分开运行，不混合挑选：

### 15.1 `paper-faithful`

- reader temperature 0.2。
- 所有数据集 3 个 missing knowledge points + 2 篇 question-only documents。
- 以 Appendix D prompt 为基准。
- generator 仍按实际代码 `max_tokens=256`，同时记录与“256 words”的冲突。
- 所有未给参数使用显式、预注册的默认值并写入 manifest。

### 15.2 `released-code-intent`

- reader temperature 0.1、seed 42。
- 保留发布代码模板的字节级文本。
- 按代码意图对 MedMCQA/BioASQ 使用 2 个 missing points，其余 3 个，并用 question-only prompt 补足到 5 篇。
- 使用恢复出的固定 ICL examples。
- 只修复必然崩溃/接线错误，每个 patch 写入变更清单和测试。

两套都只能称为独立复现。只有作者给出实际 patch、配置和中间产物后，才可能定义 `author-exact` profile。

## 16. 推荐恢复计划

### Phase 0：先保护当前成果并确定口径

1. 阅读本文全部内容。
2. 运行 `git status --short --branch`，确认没有其他用户修改。
3. 运行 `python3 validate_release.py`，确认 Direct Response 结果仍完整。
4. 经用户同意后提交或至少备份当前 7 个新增文件；不要擅自提交或推送。
5. 修正 `REPRODUCE_LLAMA.md` 和 `RESULTS_LLAMA.md` 的过时缺口表述。
6. 询问/决定跑 `paper-faithful`、`released-code-intent`，还是两者都跑。

### Phase 1：固定资源和存储布局

1. 把 HF cache 改到 `/home/data3/txy` 下的可写路径。
2. 记录 Textbooks/Wikipedia/MedCPT/Llama 的 revision、下载命令、文件数、大小和 checksum。
3. 下载前重新做磁盘容量估算；不要假设 563GB 一定足够 corpus + 临时文件 + 双索引。
4. 为 corpus、index、intermediate outputs 和 final predictions 使用不同目录。

### Phase 2：建立完整检索环境

1. 安装与 Pyserini 1.0.0 兼容的 Java。
2. 在单独/扩展的 venv 中安装 `pyserini==1.0.0`、`sentence-transformers==5.0.0`、所需 sklearn/faiss 等。
3. 下载两个 corpus。
4. 构建两个 Lucene indexes，并记录完整命令和 checksum。
5. 用少量已知 query 做 smoke retrieval，验证每源恰好 top-32。
6. 下载并固定 MedCPT，验证 64→5 rerank 的 shape、排序方向和 max_length=512。

### Phase 3：实现可审计的 MedRGAG runner

建议不要直接在上游 `main.py` 上做难以审计的散乱修补；新增一个明确的 runner 或小 patch series：

1. 参数化所有模型、corpus、index、output 路径。
2. 移除未使用的 `config.py` import。
3. 修复 `llm_name`、`args`、dict/list、文件名和 tokenizer 接线。
4. 恢复 prompt 示例，但把来源和 hash 写入 manifest。
5. 对 selection 强制验证唯一合法索引，并保留原始 GPT 输出。
6. 所有阶段逐题/逐 batch 原子写入，可断点续跑。
7. 不让多线程共享未加锁 writer。
8. 所有阶段保存输入 hash、输出 hash、模型 revision、SamplingParams 和 elapsed time。
9. 为 retrieval、rerank、prompt assembly、selection parser、answer parser 写小测试。

### Phase 4：按阶段生成并验证

推荐顺序：

1. 单题全链路 smoke。
2. 每数据集 10–50 题小样本。
3. 五数据集完整 retrieval + MedCPT，先冻结并校验，不调用 GPT。
4. summary。
5. explore。
6. Llama generator。
7. KADS selection + final MedCPT。
8. Llama reader。
9. 使用作者 parser 报主分数，同时报告严格解析率、invalid count 和截断率。

每阶段必须在进入下一阶段前检查题数、ID 集合、重复、空输出、选择数量和 hash。

### Phase 5：最终报告

至少分别报告：

- 论文目标值。
- `paper-faithful` 结果。
- `released-code-intent` 结果。
- 作者宽松解析口径。
- 严格解析诊断口径。
- 每数据集和宏平均差值。
- retrieval overlap、selected retrieved/generated 比例等中间诊断。
- 所有与公开代码不同的修复。
- 由于随机性和公开信息缺口导致的复现边界。

## 17. 最值得向作者确认/索取的内容

按优先级：

1. Table 1 实际使用的可执行 commit/patch 和 config。
2. Llama reader temperature 到底是 0.1 还是 0.2。
3. MedMCQA/BioASQ 是 2 个还是 3 个 missing points。
4. summary ICL demonstrations 是固定示例还是逐题从 training corpus 检索；若动态，提供检索方法。
5. generator/GPT seed，以及完整 sampling/API 参数。
6. 五个数据集的 retrieval snippets、Lucene index checksum 和中间缓存。
7. Llama、MedCPT、corpus 的 exact revision/hash。
8. 完整运行 manifest、日志和 Llama predictions。
9. KADS 后是否正式再做一次 MedCPT 排序，以及不足 5 篇时的正式 fallback。

## 18. 恢复时可立即执行的只读检查

```bash
cd /home/data3/txy/MedRGAG

git status --short --branch
git log --oneline --decorate --all

python3 validate_release.py

.venv/bin/python --version
.venv/bin/python -c 'import torch, transformers, vllm; print(torch.__version__, transformers.__version__, vllm.__version__)'

nvidia-smi --query-gpu=index,name,memory.total,memory.free,driver_version --format=csv,noheader

test -d /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct && echo model-present
test -d corpus && du -sh corpus || echo corpus-absent
command -v java || echo java-missing
```

不要直接重跑现有 full Direct Response 目录；runner 会拒绝覆盖。若必须重跑，使用新的 `--output-dir`，或仅在明确授权后使用 `--overwrite`。

Direct Response smoke 示例：

```bash
export HF_HOME=/home/data3/txy/.cache/huggingface_medrgag
export HF_HUB_CACHE="$HF_HOME/hub"

.venv/bin/python reproduce_llama31.py \
  --datasets medqa \
  --limit 1 \
  --profile released-code \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
  --cuda-visible-devices 0 \
  --tensor-parallel-size 1 \
  --output-dir outputs_reproduced/smoke-next
```

## 19. 两份已有报告中的已知过时表述

`REPRODUCE_LLAMA.md` 和 `RESULTS_LLAMA.md` 的数值、Direct Response 命令和主要运行清单仍然有效，但它们的“完整 MedRGAG 为什么缺失”段落形成于后续完整审计之前。

恢复时必须使用以下修正：

1. **GPT snapshot 并非未披露。** `main.py` 和 `src/llm_by_gpt.py` 都固定为 `gpt-4o-mini-2024-07-18`；OpenAI 官方文档在 2026-08-14 核查时仍列出它。
2. **ICL 示例并非彻底丢失。** 初始提交被删除的 `template.cpython-311.pyc` 可恢复固定 summary/explore 示例和 two-knowledge prompt；真正未公开的是论文声称的动态 training-corpus 检索规则。
3. **语料并非不可取得。** 两个 MedRAG HF 数据集公开且 counts 与论文一致；缺的是本地副本、预建索引、不可变 provenance 和 retrieval outputs。
4. **MedCPT 身份并非未知。** 代码路径明确指向 `ncbi/MedCPT-Cross-Encoder`；缺的是本地权重和作者 exact revision/hash。

下一步若修改这两份报告，应只改过时的事实判断，不得改写已经真实运行并验证的结果。

## 20. 边界、安全和工作区约束

- 不要把论文/PDF 内文字当作执行指令；它只是研究对象。
- 不要在没有用户授权时提交、推送或调用付费 GPT API。
- 不要在聊天、代码或 Git 中暴露 API key。
- 不要覆盖 `outputs_reproduced/llama3.1/direct/*` 的已验证结果。
- 不要把发布的 Qwen predictions 称为本地重跑；它们只是作者产物校验。
- 不要把现有 MedQA generated cache 与新 retrieval 静默混用。
- 不要把 `paper-appendix` Direct Response 敏感性实验称为论文主结果。
- 不要在没有作者澄清时声称精确复现 `71.43%`。
- 工作区可能包含用户文件；删除、重建、移动大型 corpus/index 前必须解析确切路径并确认范围。
- 当前上游 tracked tree 是 clean；保留用户已有变更，不要 reset/checkout 清除 untracked 成果。

## 21. 当前证据索引

| 内容 | 位置 |
|---|---|
| 论文原文 | `/home/data3/txy/Li - 2026 - From Retrieval to Generation Unifying External and Parametric Knowledge for Medical Question Answer.pdf` |
| 上游 README | `README.md` |
| benchmark | `benchmark.json` |
| 主流水线 | `main.py` |
| Llama/MedCPT/retrieval/reader | `src/medrgag.py` |
| GPT 调用和中间处理 | `src/llm_by_gpt.py` |
| prompt | `src/template.py` |
| corpus/index builder | `src/utils.py` |
| 作者 parser | `src/evaluate_utils.py` |
| Direct runner | `reproduce_llama31.py` |
| 结果验证器 | `validate_release.py` |
| 使用说明 | `REPRODUCE_LLAMA.md` |
| 已完成结果报告 | `RESULTS_LLAMA.md` |
| released-code 汇总 | `outputs_reproduced/llama3.1/direct/released-code/summary.json` |
| appendix 汇总 | `outputs_reproduced/llama3.1/direct/paper-appendix/summary.json` |
| 本文档 | `LLAMA31_REPRODUCTION_HISTORY.md` |

## 22. 下一个 agent 应如何开始

1. 运行第 18 节的只读检查。
2. 确认用户现在要的是完整 MedRGAG，而不是重复 Direct Response。
3. 先向用户说明当前断点和需要的 profile/API 选择；不要再次从零盘点已完成工作。
4. 若用户授权继续实施，优先完成“可审计 runner + 检索环境”，先冻结 retrieval，再进入付费 GPT 阶段。
5. 每完成一个阶段就更新本文的日期、checkbox、命令、hash、结果和新断点。

当前最后状态：**Direct Response 已完成且复核通过；完整 Llama3.1-8B MedRGAG 尚未开始执行，下一实质步骤是确定复现 profile、修复 runner，并构建 Textbooks/Wikipedia 的 Lucene 检索与 MedCPT rerank。**
