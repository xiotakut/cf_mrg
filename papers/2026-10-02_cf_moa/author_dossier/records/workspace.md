# 工作区位置、公共运行接口与文档沿革

2026-10-03：五类benchmark与五agent CF-MoA新框架已上传原私有库，提交`80dcbcf`；10页原生LaTeX框架、三表两图、三条审计和原过程记录快照齐备；[发布验收](#cf-moa-framework-github-20261003)。上一轮完整稿保留。

2026-10-03 七系统论文修订已发布：[28 页原生 LaTeX 论文与复现包](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa)，11 表/6 图/24 引用，350 个包文件及根导航的远端内容核验通过。最终提交 `bb5a017`，仓库保持 **private**；[发布记录](#seven-system-paper-github-20261003)。

2026-10-02 LaTeX 更新：[原生 LaTeX 工程及真实编译 PDF](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa/latex)已推送，最终导航提交 `cac3fe4`；312 个包文件与根导航远端校验通过，仓库保持 **private**。[本次发布记录](#cf-moa-paper-latex-github-20261002)。

2026-10-02：[论文包 GitHub 发布及仓库私有化](#cf-moa-paper-github-private-20261002)已完成；[论文目录](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa)共 262 文件，提交 `7308479`，远端 263 个提交文件校验通过。`xiotakut/cf_mrg` 当前为 **private**；历史文档的公开访问记录仅代表当时状态。

<a id="cf-moa-incremental-v2-github-20260923"></a>

2026-09-23 15:00，CF-MoA版本2发布完成：应用户“汇总一个新版本上传到github”，在同一[本地过程报告](research/cf_moa_experiment_report.md#incremental-revision-v2)增加修订后执行章节，实验状态截止14:25；新[GitHub报告](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-23_cf_moa_incremental_v2/docs/research/cf_moa_experiment_report.md)与[发布包](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-23_cf_moa_incremental_v2)已推送`xiotakut/cf_mrg/main`，提交[a7a97da](https://github.com/xiotakut/cf_mrg/commit/a7a97da66cefc2e9a596655e5cd8869b33526fc7)。研究事实仍归[CF-MoA主记录](research/cf_moa.md#incremental-revision-execution-20260923)，本文只记录发布。旧09:41发布包17文件逐字保持，新包不会覆盖旧负结果、原121题指标或正式v5。

隔离工作区沿用`Documents/Codex/2026-09-23/cf_moa_github_publish`，新包`benchmarks/2026-09-23_cf_moa_incremental_v2/`共21文件，连同两级导航共23提交文件。报告1153行，新增B接口/A2兼容、A1_delta与A3真实检验、错误处理和实际费用；另含主记录快照、修订计划、19项文件来源绑定、20个数据源哈希、7份数据JSON摘要、24条A1臂状态与80条A3输入×方案状态、成本和独立就绪限制。患者全文、答案值/gold、模型完整响应、SQL和大型缓存不上传；完整实验源码/配置/trace在服务器，由交付索引定位。报告不是完整可移植推理环境或独立重现实验。

只读来源核验56项通过；独立报告和公开范围审阅通过。包内13份JSON、19项发布哈希、24/80状态行、45真实final/3零探针回退、254调用与token/墙钟费用、157处Markdown链接全部一致；独立公开checker另通过10个临时包测试（9项故障注入）。旧版checker仍通过242行状态/13来源/112链接。发布准备的只读错误（不可用python别名、错误摘要类型、查找不存在的状态文件）分别保留在审计/导出收据，未改实验。初次`git diff --cached --check`因两CSV的CRLF记录分隔符报尾部空白；只将公开CSV改LF，逐字段解析相等，更新导出哈希后重验通过；日志`initial_diff_check.log`保留。

正常推送后远端main及Git tree与本地提交一致；通过GitHub Git blob API base64逐个取得23文件，全部字节/SHA-256相等，工作区干净，15:00验收完成。未使用此前会改变字面转义的raw媒体响应作字节比较。此次0新模型、0原生重评分、不操作GPU进程；不改变后来14:44资源占位任务。完整证据见[发布收据](../Documents/Codex/2026-09-21/cf_moa/publication_v2_20260923/publication_receipt.json)和[构建目录](../Documents/Codex/2026-09-21/cf_moa/publication_v2_20260923/README.md)。

<a id="cf-moa-process-github-20260923"></a>

2026-09-23 CF-MoA完整过程报告发布完成：按用户明确要求，将[本地完整报告](research/cf_moa_experiment_report.md)、截至实验交接的持续主记录快照、原核心计划和精简结果/成本/逐题状态上传到既有`xiotakut/cf_mrg`的`main`，提交[3c43afa4029f1d4bce9d6cc8691f10ef980fdf16](https://github.com/xiotakut/cf_mrg/commit/3c43afa4029f1d4bce9d6cc8691f10ef980fdf16)。[GitHub报告](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-23_cf_moa_process/docs/research/cf_moa_experiment_report.md)共1022行，覆盖阶段A–E、采用配置、全部主要失败与修复链、负结果、GPU/CPU执行问题和未完成范围。正文事实及研究结论归报告与[CF-MoA主记录](research/cf_moa.md#cf-moa-process-report-20260923)，本文只记录发布。

隔离工作区为`Documents/Codex/2026-09-23/cf_moa_github_publish`，包路径`benchmarks/2026-09-23_cf_moa_process/`；19个提交文件包含17个包内文件和两级导航。13份来源绑定、242行逐题状态及三控制转移、保存的费用、112处包内链接与差异空白检查通过，403条未收录本地制品引用有索引。未上传完整敏感请求、模型正文、隐藏配对端或大型缓存；本次0新模型、0原生评分，暂停实验不恢复。

普通推送成功后，远端main与本地提交一致，发布工作区干净。首次raw媒体API核验时，返回正文将两处字面Unicode转义变形，正文短8字节；本地Git对象与工作副本一致。改用GitHub Git blob API的base64内容进行字节比较，正文155866字节、主记录快照415663字节、核心计划26940字节和来源清单7472字节均与本地发布副本逐字、SHA-256一致，未因读取差异修改报告内容。该发布核验错误、处理及最终哈希保存在[发布收据](../Documents/Codex/2026-09-21/cf_moa/publication_report_20260923/publication_receipt.json)。

<a id="support-update-r45-github-20260920"></a>

2026-09-20过程报告扩充与发布完成：按用户新增R4/R5两会话及此前“上传到github”的明确授权，将既有[全过程报告](research/support_update_experiment_report.md)扩展至R1–R5，推送到`xiotakut/cf_mrg`的`main`，提交[be65ca520a93afcf5dd3852a3e429b2e3a7c7475](https://github.com/xiotakut/cf_mrg/commit/be65ca520a93afcf5dd3852a3e429b2e3a7c7475)。[GitHub正文](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-16_support_update_method/docs/research/support_update_experiment_report.md)沿用原地址；新增R4 30节、R5 40节，合计148个方向过程小节，本地2580行、406989字节。原R1–R3与交叉审计的整段正文逐字保持，更新首尾、时间线、分母与阶段交付。R4为给定生理模型/完整状态的受限完成；R5旧F交付保留，后续论文方法目标未完成，CAD五头仅计划。论文式论证稿范围仍为R1–R3。

本次读完两会话可读正文、R4/R5主记录及相关过程失败文件，并独立核验时间线、状态与成本。读取范围、不可恢复字段、代理审阅与人类专家证据的区别见报告附录及新清单；没有声称逐字读过所有加密字段和巨型工具输出。13个提交文件包含更新报告、R4/R5主记录快照、阅读清单、源消息时间索引、状态/成本核验和导航；未上传原始会话JSONL、完整模型轨迹或大型运行缓存。已有R1–R3来源快照保留。

本地593处链接/锚点、发布包19份Markdown的692处内部链接/锚点通过，来源清单25项无重复且目标齐全、包内JSON均可解析，暂存差异空白检查通过。初次链接检查不识别既有`文件:行号`写法，补足检查器后通过，未改旧实验正文。发布转换将本轮涉及的64处已收录引用转为包内相对链接，510处未收录目标保留明确服务器路径并更新索引。推送后用既有`gh`认证读取远端正文415378字节及R4/R5快照135065/198215字节，三文件均与本地发布副本逐字、SHA-256一致；远端main与提交一致，隔离发布工作区干净。完整[发布验证收据](../Documents/Codex/2026-09-16/r1_r2_r3_method_synthesis/process_report_r45_publication.json)保存检查范围。本次0新模型调用、训练和生理积分，未推进R5旧计划或改变任何运行作业。

<a id="support-update-process-github-20260918"></a>

2026-09-18过程报告发布完成：沿用户此前“上传到github”的要求，将独立的[R1–R3实验全过程报告](research/support_update_experiment_report.md)发布到同一仓库`xiotakut/cf_mrg`的`main`，提交[15824b074b512dc7f375c6f3ca6e3db5b4b01205](https://github.com/xiotakut/cf_mrg/commit/15824b074b512dc7f375c6f3ca6e3db5b4b01205)。[GitHub正文](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-16_support_update_method/docs/research/support_update_experiment_report.md)包含78个过程小节，回顾09-14至09-16的R2→R3→R1实际探索，另述交叉审计。与前一份方法论证稿分别保留，新增相互入口、R2的33目录/10995新请求账本和本地核验收据，共9个提交文件；未更新09-16来源快照或上传原始会话、完整模型轨迹。正文引用中的246处未收录目标明确保留服务器路径并追加索引，41处已收录文档引用转换为相对链接。

本地报告373处链接/锚点核对通过；发布包16份Markdown共566处内部链接/锚点通过，78阶段数及R2账本去重加和通过，提交差异空白检查通过。两个CSV的旧CRLF导致初次差异检查提示行尾空白，统一LF后通过，索引数据保持；第一次未认证GitHub API请求返回404，随后用既有`gh`认证逐字读取267506字节正文，SHA-256与本地发布副本一致。远端main与提交一致，隔离发布工作区干净。[发布核验收据](/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_r3_method_synthesis/process_report_publication.json)保存验证范围；工作区仍为`Documents/Codex/2026-09-16/method_synthesis_github_publish`。本次0新模型调用，正式v5、现有head和其他任务不变。

<a id="support-update-github-20260916"></a>

2026-09-16发布补充：按用户“上传到github”的要求，将[支持更新与候选重决策主稿](research/support_update_method.md)及其直接依据发布到 `xiotakut/cf_mrg` 的 `main`，提交 [c791cc966d1d8da5173fce4599e96dbe56822773](https://github.com/xiotakut/cf_mrg/commit/c791cc966d1d8da5173fce4599e96dbe56822773)。[公开入口](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-16_support_update_method)包含15份来源文件（主稿、R1/R2/R3主记录、分类/协议/v5、关键分析与阅读清单），连同来源索引、发布说明及两级导航共20个提交文件。发布副本将链接改为仓库相对路径、主稿公式改为GitHub数学分隔符；533处未收录引用保留服务器路径并列入本地制品索引，原始会话、完整模型轨迹及大型数据未上传。434处包内链接及其锚点通过，新增导航与主稿的差异空白检查通过；推送后远端main与本地提交一致，GitHub API可读到59206字节的主稿，发布工作区干净。隔离工作区为 `/home/data3/txy/Documents/Codex/2026-09-16/method_synthesis_github_publish`，既有仓库未提交改动保留；本次0新模型调用，正式结果不变。

最新状态：2026-09-26（Asia/Shanghai）。GPU0的30GiB holder和GPU1的恢复占位均已按用户要求释放，当前GPU0/1无本账号占位。归属监控器PID2993679每5秒采样并每600秒追加报告。

**2026-09-24 13:09起持续监控与进程归属。** 旧候选验证包的四个generation在13:05统一写入STOP并保留原始证据；为满足本次持续监督，在独立状态目录重新启动GPU0–3的live watcher：GPU0主进程1510408（tmux会话`gpu-watch-gpu0-free50-20260924`），GPU1/2/3主进程分别1511721、1511769、1511809（对应`gpu-watch-gpu{1,2,3}-free50-20260924-live`）。只读归属监视器PID1511976运行于`gpu-owner-monitor-20260924`，由[归属监视器脚本](/home/data3/txy/.local/bin/gpu_owner_monitor.py)每5秒写入[status.json](/home/data3/txy/.local/state/gpu-owner-monitor-20260924/status.json)，每600秒追加[report.jsonl](/home/data3/txy/.local/state/gpu-owner-monitor-20260924/report.jsonl)，记录GPU利用率、显存、compute PID、Unix账户和命令行，并把`gpu_watch.py --gpu`识别为本账号holder。启动核验时GPU0/1/2/3空闲显存为29012/23695/6782/21894 MiB、利用率均100%，因此没有分配显存；监控本身不改变其他任务。GPU0 watcher此前候选目录已停止的原因未在该旧日志中说明，不能据此归因；本次未向任何非本账号进程发送信号。

**2026-09-24 13:23 GPU0/1各20GiB无限期占位。** 用户明确要求在GPU0和GPU1各占20GiB。第一次尝试使用`--min-free-gib 2`被脚本参数校验拒绝（该阈值必须严格大于2），没有启动holder或改变显存；随后改用`--min-free-gib 2.1 --gib 20 --hold-hours 0 --wait-hours 0`，分别在[GPU0状态目录](/home/data3/txy/.local/state/gpu0-hold20-20260924/)和[GPU1状态目录](/home/data3/txy/.local/state/gpu1-hold20-20260924/)启动独立tmux会话。GPU0 holder PID1519331、GPU1 holder PID1519512均记录`held`与`target_reached`，归属监视器确认各约20796MiB进程显存；随后实时剩余显存为GPU0 8211MiB、GPU1 2888MiB，均保留超过2GiB并无限期持有，需手动在对应状态目录写入`STOP`才释放。GPU2/3的原5秒阈值watch继续运行，未向任何外部任务发送信号。

**2026-09-24 13:36–13:37 GPU2/3占位保留量修正。** 原GPU2/3阈值watch分别自动占用约77.48/70.70GiB；随后外部进程显存变化使实时余量降至1725/1694MiB，低于至少2GiB约束。只对本账号的两个旧状态目录写入STOP，13:36:41/42分别记录`released`和`stopped`，未发送信号给外部任务。随后以新的[GPU2 safe60状态](/home/data3/txy/.local/state/gpu-watch-gpu2-free50-20260924-safe60/)和[GPU3 safe60状态](/home/data3/txy/.local/state/gpu-watch-gpu3-free50-20260924-safe60/)重启`--min-free-gib 50 --gib 60 --hold-hours 0 --wait-hours 0`；GPU2 holder PID1529160、GPU3 holder PID1529368均成功`held`。13:37:29实时余量为GPU0/1/2/3分别9841/2562/19627/12650MiB，四卡均保留超过2GiB；GPU0/1的20GiB holder未改变。

**2026-09-24 13:53–15:33候选恢复占位交接。** 上述safe60状态分别于13:53:44/48释放并停止，证据保留在各自`watch.log`。随后候选验证包的恢复目录[`recovery_gpu23/restored_holders/gpu2`](/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_candidate_verify_20260924/recovery_gpu23/restored_holders/gpu2/)和[`gpu3`](/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_candidate_verify_20260924/recovery_gpu23/restored_holders/gpu3/)分别启动PID1545527和1544348，配置为`--gib 60 --min-free-gib 50 --hold-hours 0`，截至15:33仍在运行。GPU1原live watcher另启动PID1570143（约55196MiB），与明确的20GiB holder并存。15:33直读快照为GPU0/1/2/3剩余12367/2064/8754/1904MiB、利用率100/100/100/100%；GPU3低于2GiB保留线，属于候选恢复holder和其他任务共同变化后的观测状态，未对其发信号或自动回收。

**2026-09-24 21:49–21:51 GPU0/1占位释放与监控恢复。** 用户要求释放GPU0/1的本账号占位；向`gpu0-hold20-20260924`、`gpu1-hold20-20260924`及两张卡的free50阈值watch状态目录写入`STOP`。四个holder/supervisor均记录21:49:32 `released`/`stopped`，GPU0/1随后不再有本账号`gpu_watch.py` compute进程；21:49直读显存为GPU0已用61716、空闲35652MiB，GPU1已用9981、空闲87387MiB。清理无子holder的GPU0 tmux进程时发现它与归属监控器共用同一tmux server，监控器被一并停止；未触碰任何计算任务，随即在21:50:55以原状态目录重启监控器，PID2993679，21:51快照确认GPU0/1 `holders=[]`。停止前后的日志和STOP文件均保留在上述状态目录，GPU2/3及其他账号进程未因本次释放操作发送信号。

**2026-09-24 22:35–22:37 GPU1 65GiB占位尝试。** 用户要求GPU1占65GiB。启动前GPU1仅空闲30404MiB，按脚本的共享卡策略实际只分配27.691GiB（holder PID4074364），未达到目标且外部显存变化后剩余约1.7GiB；该部分holder在22:36:41释放，失败与释放证据保留在[部分尝试状态](/home/data3/txy/.local/state/gpu1-hold65-20260924/watch.log)。随后启动[等待状态](/home/data3/txy/.local/state/gpu1-hold65-wait-20260924/)：`--gib 65 --min-free-gib 68 --hold-hours 0 --wait-hours 0`，每5秒检查，只有可用显存超过68GiB才申请，避免再次只占部分显存。截至22:36:56尚未满足阈值，`holders=[]`；该等待器持续运行，直到手动写入其`STOP`。

**2026-09-25 02:41 GPU资源快照。** GPU1等待器PID4075739仍在运行但未持有显存；GPU1空闲18806MiB，无法达到65GiB申请阈值。GPU3的独立M4 live恢复holder PID4159296占用61756MiB，状态目录为`cf_moa_rcv_completion_20260924/c0_missing_natural/m4_live/restored_holders/gpu3`；归属监控将其标为txy holder，但本轮未启动、停止或干预该进程。GPU1的txy PID4125547和GPU2的txy PID4097282分别是实际M4/M5 readout任务，不计入显存占位。

**2026-09-25 11:11 GPU0 30GiB占位。** 用户要求占用GPU0 30GiB；启动前空闲35574MiB，使用`--gib 30 --min-free-gib 2.1 --hold-hours 0`启动[GPU0状态](/home/data3/txy/.local/state/gpu0-hold30-20250925/)。holder PID624458记录`held`与`target_reached`，监控确认进程显存31036MiB，11:11:49剩余4532MiB；该holder无限期运行，需在状态目录写入`STOP`释放。其他GPU任务未受信号或停止。

**2026-09-26 12:06资源复核。** GPU0 holder PID624458仍占31036MiB，但wbc的VLLM PID3768541占66182MiB后，监控快照显示GPU0已用97241、空闲127MiB、利用率100%，因此原先的2GiB余量已被外部进程变化侵蚀；未向外部进程发信号。GPU1当前已用89811、空闲7557MiB，无占位；其65GiB等待器在2026-09-25 10:46:59停止，STOP内容记录为“Authorized GPU1/GPU3 unchanged M4 resource handoff.” GPU2的恢复watch supervisor PID3823439仍在，但当前无holder；GPU1/GPU3的txy实际M5 readout任务继续运行。

**2026-09-26 12:08 GPU0占位释放。** 用户要求释放GPU0的30GiB holder；向[GPU0状态目录](/home/data3/txy/.local/state/gpu0-hold30-20250925/)写入`STOP`后，holder PID624458于12:08:18记录`released`，监督进程于12:08:19记录`stopped`。12:08:34归属监控确认GPU0 `holders=[]`，已用66199、空闲31169MiB；仅wbc的VLLM等外部任务仍在运行，未向其发送信号。

**2026-09-26 18:48 GPU1恢复占位释放。** 用户要求释放GPU1占位；实际占位为候选运行目录[`readout_tail_gpu123_20260926/gpu1/restored_holders/gpu1`](/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/full_v5/readout_tail_gpu123_20260926/gpu1/restored_holders/gpu1/)，holder PID3894988，约60GiB。第一次按错误日期前缀尝试写STOP，未找到目录且未改变进程；随后按进程命令行中的真实路径写入STOP，18:48:00记录`released`、18:48:01记录`stopped`，18:48:06监控确认GPU1 `holders=[]`、已用33243、空闲64125MiB。GPU1的VLLM PID3988937未停止，GPU2/3占位未动。

<a id="gpu-watch-20260915"></a>

## 2026-09-15：GPU定期巡检与临时占位

用户要求查看当前显卡、每五或十分钟自动检查，有空闲时为后续实验占位。11:04实际快照：GPU0/1/2利用率100%，GPU3为85%；四卡均有其他用户进程（wbc、dpc），无整张空闲卡。未终止或更改这些进程。没有发现可用的squeue命令；既有M4 guard用于运行避让，不能直接作为临时占位工具。

实现：[gpu_watch.py](/home/data3/txy/.local/bin/gpu_watch.py)，使用标准库调用nvidia-smi，真正占位时由已有MedRGAG虚拟环境的PyTorch分配显存。采用默认方案：监控GPU0–3、间隔300秒、最多成功占一张、每张80 GiB、占到后保留7200秒自动释放，等待窗口24小时；占到并释放后不会循环重新抢占。用户可用`--max-cards`、`--interval`、`--gib`、`--wait-hours`、`--hold-hours`修改下一次启动配置。空闲要求：无compute进程、已用显存低于1 GiB、利用率不超过5%、空闲显存至少82 GiB。占位子进程导入torch后再次核实条件，再分配张量并等待，不持续执行计算。

状态和逐次日志存于`/home/data3/txy/.local/state/gpu-watch/`：`status.json`为最新快照，`watch.log`为追加事件日志，`GPU-*.json`为成功占位的时间、PID及计划释放时间；历史占位文件不单独代表仍在运行，应以status及实时nvidia-smi为准。后台tmux会话名`gpu-watch`。停止并释放：`touch /home/data3/txy/.local/state/gpu-watch/STOP`，主进程最多约5秒察觉（若正在nvidia-smi调用，需等待该调用结束或超时），结束自己启动的占位子进程。重启前清除STOP文件，并确认旧会话已结束；同状态目录有flock阻止重复监控实例。

启动命令：`tmux new-session -d -s gpu-watch 'exec python3 -u /home/data3/txy/.local/bin/gpu_watch.py >> /home/data3/txy/.local/state/gpu-watch/watch.log 2>&1'`。只读检查：`python3 /home/data3/txy/.local/bin/gpu_watch.py --check`。巡检无需模型请求，不会自动发送聊天消息。

验证：[CPU检查](/home/data3/txy/.local/bin/test_gpu_watch.py)覆盖忙卡跳过、显存/利用率阈值、最多领取一次、正常完成、停止时清理自己的子进程，以及占位计时释放调用；实际nvidia-smi只读检查成功，已确认现有torch 2.6.0+cu124可导入。当前卡全忙，未实测80 GiB真实分配；占位是否成功应以未来held事件为准。显存占位不是调度器独占预约，检查与分配也不是跨用户原子操作；分配失败会记录异常并在后续巡检重试。不会驱逐其他用户或自动启动任何benchmark。

启动时状态：2026-09-15 11:09:39 CST启动，tmux会话`gpu-watch`、主进程PID3336831，首次快照成功写入；四卡仍有compute进程，holders为空。首次后台快照GPU0/1/2/3利用率分别100/100/100/30%，空闲显存6153/15951/8647/35891 MiB。等待窗口原设至2026-09-16 11:09:39，若窗口末尾才占到卡，其两小时保留期仍从占位成功起计算。

**2026-09-16 13:39完成核查。** `watch.log`记录9月15日21:25:04启动GPU2占位子进程3889780，21:25:06出现held事件，实际分配80 GiB；23:25:06释放，23:25:08子进程exit_code=0，主进程记录stopped。GPU UUID为`GPU-15a39260-1d85-9f71-ce5d-cad20ec907ce`。首次真实占位及两小时自动释放已执行成功，补充了启动时尚未实测的部分。当前`status.json`为stopped、holders为空，tmux会话和巡检进程均已退出；这是达到“一次成功占位并释放”终止条件，不是崩溃。此次只读核查未重新启动占位或改变任何实验，GPU0/1/3上另有本账号R1实验在运行，其进度由R1主记录承接。

**2026-09-16 18:27再次启动。** 用户指定临时占住GPU1，同时汇报所有卡。工具增加最小参数`--only-gpu`：它只限制领取候选，四卡快照仍全部记录；原有默认行为不变，CPU模拟检查通过。启动前GPU1为0 MiB使用、0%利用率、无compute进程。tmux会话`gpu1-watch`、主进程1015382在18:27:20启动，子进程1015441于18:27:22成功持有GPU1的80 GiB（nvidia-smi实测82236 MiB进程显存），计划20:27:22自动释放；每300秒记录四卡，状态与日志位于`/home/data3/txy/.local/state/gpu1-watch-20260916/`。等待窗口设为两小时；本次卡已立即取得，因此以持有期限为准。停止并提前释放可创建该状态目录下的`STOP`文件；脚本不会操作其他用户进程。

**19:36续接。** 首轮持有进程在19:20:13收到终止并释放，19:20:14主进程写入stopped；当时尚未到20:27的计划释放时间，tmux会话随后也不存在。现有证据能确认安全释放，不能确认是谁或哪个外部操作结束了会话。用户要求继续占用后，19:36:36使用新状态目录`/home/data3/txy/.local/state/gpu1-watch-20260916-continued/`启动同配置；GPU1启动前仍为0 MiB、0%、无compute进程。子进程1058890于19:36:38成功持有80 GiB，实测82236 MiB，计划21:36:38自动释放；tmux会话仍为`gpu1-watch`，每300秒记录四卡。

**2026-09-18历史补证。** 编写R1–R3过程报告时核对了R1定向开发已保存的[资源交接收据](/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/resource_handoff.json)：R1会话在09-16 19:20:13向GPU1占位supervisor PID1015382发送SIGTERM，其退出清理释放holder PID1015441，19:20:14记录stopped，随后诊断队列PID1040377启动。因此上文巡检会话当时“未确认谁结束”的历史状态保留，但现存跨任务证据已明确该次释放来自R1实验资源交接；不能将占位启动本身也归给R1会话。此为旧事件归属补证，本轮没有发送进程信号或改变GPU作业。

**2026-09-17 16:40结束核查。** 续接日志记录GPU1占位进程1058890于9月16日21:36:38按计划释放，21:36:40子进程exit_code=0，主进程写入stopped；holders为空，tmux会话已退出。实时nvidia-smi显示GPU0和GPU1均为0 MiB、0%且无compute进程，GPU2/3仍由其他用户任务占用；`ps -u txy`未发现本账号GPU模型进程。本次只读核查未重启占位或实验。

**2026-09-17 16:42双卡占位。** 用户要求占住GPU0和GPU1三小时。启动前两卡均为0 MiB、0%、无compute进程；分别启动tmux会话`gpu0-hold`和`gpu1-hold`。GPU0子进程2050398、GPU1子进程2050399均于16:42:03成功持有80 GiB，nvidia-smi各实测82236 MiB，计划19:42:03自动释放。两个监控分别写入`/home/data3/txy/.local/state/gpu0-hold-20260917/`与`gpu1-hold-20260917/`，每300秒保留全部四卡快照；不会操作GPU2/3或其他用户进程。

**2026-09-21状态核查。** 两份日志显示GPU0/1占位均在9月17日16:54:37收到终止、释放显存并写入stopped，实际只持有约12分34秒，未达到计划的19:42:03；两者未记录holder_finished事件，当前tmux server也不存在。现有证据只能确认两个子进程同时安全释放，不能确认外部终止来源。9月21日21:34实时检查显示本账号没有GPU模型或占位进程，四卡当前均由其他用户任务使用。本次只读状态检查未重启占位或实验。



**2026-09-21空闲显存阈值占位。** 用户要求任意卡出现大于50 GiB空闲显存时自动占位。在既有`.local/bin/gpu_watch.py`增加可选`--min-free-gib`，新模式允许卡上已有进程或计算负载；未指定参数时仍保持原整卡空闲策略。父进程筛选、子进程导入torch后及CUDA初始化后复查，严格大于50 GiB才分配；分配量为当时空闲量减2 GiB、上限80 GiB（其他进程并发分配仍可能改变余量）。目标为同时取得两张卡；取得后默认无限期持有，只有手动停止监控或创建`STOP`文件才释放；每5秒巡检。CPU模拟测试通过，覆盖50 GiB边界、共享卡准入、动态分配量、单卡限制、定时释放和无限期持有路径；当前尚无满足阈值的实际分配验证。

21:42:06通过tmux会话`gpu-watch-free50`启动，命令：`python3 -u /home/data3/txy/.local/bin/gpu_watch.py --state-dir /home/data3/txy/.local/state/gpu-watch-free50-20260921 --min-free-gib 50 --gib 80 --hold-hours 3 --wait-hours 24 --interval 300 --max-cards 1`。日志和快照分别为该状态目录的`watch.log`与`status.json`。首次检查GPU0–3空闲量分别为24313、24397、27769、25387 MiB，均未触发，holders为空。创建该目录下`STOP`文件可停止监控并释放本脚本占位；后台只记录日志，不自动发送聊天消息。

**22:08缩短抢卡检查间隔。** 用户指出五分钟不适合及时抢卡。此前脚本持续驻留，但每次检查后等待300秒；沿用早期巡检间隔可能错过释放窗口，现拆分为`--interval 5 --log-interval 300`。每约5秒刷新`status.json`并判断领取，周期快照日志每300秒追加，领取、释放及错误事件立即写日志。确认旧进程1019789尚无占位子进程后将其正常终止，22:08:21在新tmux会话`gpu-watch-free50-fast`重启，共用上述状态目录及追加日志；保留原9月22日21:42左右的等待截止时间，持有3小时及单卡限制保持。CPU回归检查通过，实测状态时间由22:08:21刷新至22:08:27，四卡空闲量仍为24313/24397/27769/25387 MiB，holders为空。检查间隔之外仍有查询及torch启动耗时，不能保证抢得所有短暂空闲窗口。

**22:18两张卡目标。** 用户要求持续监督并定期汇报，直到抢到两张卡。脚本的完成条件调整为两张卡必须同时存在成功占位子进程；第一张若在第二张取得前释放，会继续作为候选重新领取，不把两个不重叠的历史占位误算为完成。`--wait-hours 0`表示无等待截止。确认原监控没有holder后正常切换为tmux会话`gpu-watch-free50-two`、主进程PID1039342，配置为`--max-cards 2 --interval 5 --log-interval 300 --hold-hours 3 --wait-hours 0`，其他阈值和动态占用量不变。CPU回归检查通过；22:18:35首次快照空闲显存仍为24313/24397/27769/25387 MiB，0/2张占位。聊天汇报按用户最新要求每5分钟读取实时状态；后台脚本本身不具备主动发送聊天消息的能力。

**2026-09-22无限期持有修正。** 用户要求抢到卡后一直持有到手动解除。脚本现将`--hold-hours 0`解释为无限期等待，仅在监控收到停止信号或状态目录出现`STOP`时释放；原有正数参数仍可用于历史定时占位。CPU回归测试通过，新增覆盖无限期持有分支；在实际取得两张卡前，不创建holder文件也不改变其他用户进程。旧监控于01:00:31安全停止且holders为空；第一次重启命令因扫描到自身命令行而以143退出，未影响GPU或其他任务。随后使用独立tmux会话`gpu-watch-free50-indef-20260922`于01:01:53重新启动，主进程PID1117626，配置为`--min-free-gib 50 --gib 80 --hold-hours 0 --wait-hours 0 --interval 5 --log-interval 300 --max-cards 2`。01:01:54快照显示四卡空闲显存24313/24397/27769/25387 MiB，均低于严格的大于50 GiB门槛，holders仍为0；进程、tmux会话及`NO_STOP`状态已核实。双卡监控将继续运行，直到达到两张同时持有或用户手动停止。

**2026-09-22停止与驱动查询超时修复。** 监控运行期间多次`nvidia-smi`查询超过15秒，旧实现会使查询子进程处于内核等待并拖住主循环；状态日志最后一次`poll_error`为11:12:13，期间没有生成holder，也没有成功领取任何卡。脚本随后改用带超时的`Popen`查询、非阻塞子进程回收和30秒暂停保护，`py_compile`及CPU回归测试均通过。用户要求停止后，11:23:25在该状态目录写入`STOP`；核查无`gpu_watch.py`、监控tmux或占位子进程，holders/claimed仍为空。停止后的实时查询显示GPU0由`cf_moa.evaluation.a4_live_check --method M4`进程（PID15929）使用15779 MiB、GPU1–3分别0 MiB已用且各97367 MiB空闲；compute-app列表仅含该M4进程。该停止动作只作用于本脚本及状态文件，没有终止M4或其他用户进程；后续重启前需清理`STOP`并重新核对旧进程。

**2026-09-22单卡无限期占位恢复。** 用户要求重新占住一张卡。为保留已停止双卡运行的历史证据，新建状态目录`/home/data3/txy/.local/state/gpu-watch-one-free50-20260922/`，通过tmux会话`gpu-watch-one-free50-20260922`启动`gpu_watch.py`，配置为`--min-free-gib 50 --gib 80 --hold-hours 0 --wait-hours 0 --interval 5 --log-interval 300 --max-cards 1`。第一次启动命令因日志重定向目标目录尚未创建，在Python启动前退出，没有产生进程或GPU变化；随后预创建目录并重启。12:10:24首次快照显示四卡均97367 MiB空闲，12:10:26 GPU0（UUID `GPU-8c712173-4c58-ee01-a68d-6db9853acdad`）由子进程34776成功分配80 GiB，12:10:29写入`target_reached`。实时核查显示GPU0使用82245 MiB、空闲15123 MiB，GPU1–3各0/97367 MiB，利用率均为0%；该占位只保持显存、不执行计算，需在该状态目录创建`STOP`或停止监控才释放。证据为该目录的`status.json`和`watch.log`。

**2026-09-22释放单卡占位。** 用户要求释放上述保留卡；13:18:09在`gpu-watch-one-free50-20260922`状态目录写入`STOP`，占位日志记录GPU0释放并写入`stopped`，holders为空。随后实时`nvidia-smi`显示GPU0–3均0 MiB已用、97367 MiB空闲、0%利用率，compute-app列表为空，相关监控进程与tmux会话均已退出。停止动作只作用于本次占位脚本，没有终止其他用户任务；`STOP`文件保留作为已停止标记，后续重新占位需另行启动并清理/更换状态。

**2026-09-23双卡占位。** 用户要求占住两张卡。新建状态目录`/home/data3/txy/.local/state/gpu-watch-two-free50-20260923/`，通过tmux会话`gpu-watch-two-free50-20260923`启动`gpu_watch.py`，配置为`--min-free-gib 50 --gib 80 --hold-hours 0 --wait-hours 0 --interval 5 --log-interval 300 --max-cards 2`。11:40:38首个快照显示GPU0/1空闲60077/55127 MiB、GPU2/3空闲97364 MiB；GPU3低于50 GiB门槛。11:40:41 GPU0（UUID `GPU-8c712173-4c58-ee01-a68d-6db9853acdad`）和GPU1（UUID `GPU-a7a94bce-88f6-79db-cfc5-116324f0d028`）分别成功分配56.668945/51.834961 GiB，因卡上已有其他任务而按余量动态分配，不终止原进程；11:40:43写入`target_reached`。实时核查GPU0/1各约95643 MiB已用、1725/1723 MiB空闲，GPU2/3各4/97364 MiB，利用率约17/22/0/0%；holders为2，将无限期保持，需在状态目录创建`STOP`或停止监控才释放。证据为该目录的`status.json`和`watch.log`。

**2026-09-23迁移到GPU2/3。** 用户指出应优先使用空闲卡，要求改占GPU2和GPU3。先在`gpu-watch-two-free50-20260923`写入`STOP`并等待原两个占位子进程释放；12:23:32状态为`stopped`、holders为空，GPU0/1原有任务未被终止。随后分别启动固定候选的tmux会话`gpu-watch-gpu2-free50-20260923`和`gpu-watch-gpu3-free50-20260923`，各使用`--only-gpu 2/3 --min-free-gib 50 --gib 80 --hold-hours 0 --wait-hours 0 --interval 5 --log-interval 300 --max-cards 1`。GPU2于12:24:02、GPU3于12:24:07各成功分配80 GiB并写入`target_reached`；实时核查GPU0/1为6/4955 MiB已用，GPU2/3均82245 MiB已用、15123 MiB空闲、0%利用率。两份状态目录分别保存各自的`status.json`、`watch.log`和holder文件；释放时需分别在两个目录创建`STOP`，不会操作GPU0/1的其他任务。

**2026-09-23再次占用GPU2/3。** 上一轮固定占位目录的`status.json`分别在13:45:15和13:54:55变为`stopped`，当时未发现监控进程或tmux会话，外部停止原因未确认；holders均为空，保留原日志。用户再次要求至少占用两张空闲卡后，14:44:29和14:44:36分别启动新tmux会话`gpu-watch-gpu2-free50-20260923-r2`、`gpu-watch-gpu3-free50-20260923-r2`及独立状态目录。GPU2于14:44:31、GPU3于14:44:38各成功分配80 GiB并写入`target_reached`；当前GPU0/1为37511/4955 MiB已用，GPU2/3均82245 MiB已用、15123 MiB空闲、0%利用率。两张卡将无限期持有，需分别在对应`-r2`状态目录创建`STOP`才释放。

本次`r2`状态目录为`/home/data3/txy/.local/state/gpu-watch-gpu2-free50-20260923-r2/`和`/home/data3/txy/.local/state/gpu-watch-gpu3-free50-20260923-r2/`；启动日志、实时快照和holder文件均已保存。两份监控使用`--only-gpu`分别固定GPU2与GPU3，避免共享模式按编号优先再次选择GPU0/1。

<a id="agents-actual-injection-evidence-20260914"></a>

## 2026-09-14：两个AGENTS的职责与实际注入证据

用户再次质疑两个同名文件哪个生效，以及过去是否只是建立文件而未被平台读取。本次直接检查本地任务rollout中的`response_item`，只读取user角色的AGENTS指令消息，不以工具cat输出或模型自述代替加载证据。

已核实的实际注入（Asia/Shanghai）：

- 本文档管理任务`01a09abb-0476-7a23-ac78-4fb7e2b9a4d9`，2026-09-14 11:22:58，对应rollout第268行，user消息以`# AGENTS.md instructions for /home/data3/txy`标识，含根文件标题及持续论文记录要求。
- 优化任务`01a09dd7-8667-7ab0-8a9e-7051b56031e7`，11:27:05，对应rollout第191行，同样收到上述指令，而不是仅有一次读取文件的工具输出。
- 同一优化任务12:26:25、第888行再次收到平台指令消息，明确写有`These AGENTS.md instructions replace ...`，包含“长期主记录统一在docs”的更新要求。这证明该具体旧任务本轮已收到根指令更新；不能笼统说旧任务一律不刷新，也不能推广成所有任务每次都会刷新。

原始证据文件为`.codex/sessions/2026/09/13/rollout-2026-09-13T20-25-42-01a09abb-0476-7a23-ac78-4fb7e2b9a4d9.jsonl`及`.codex/sessions/2026/09/14/rollout-2026-09-14T10-55-42-01a09dd7-8667-7ab0-8a9e-7051b56031e7.jsonl`。这里只登记事件位置，不把完整对话再次复制进文档。

根`/home/data3/txy/AGENTS.md`是唯一共同规则正文；`.codex/AGENTS.md`于12:24:23新增，只有约10行，承担全局读取入口，用于引导从txy内部独立Git根启动的任务读取共同规则。它晚于前两次注入，因此过去根文件确实加载与它无关。官方发现机制支持Codex home全局AGENTS，但本次没有另启新任务验证该薄入口的实际自动注入；已检查的优化任务消息不含该薄入口的标题。应区分“根规则实际已加载”和“全局入口已配置、跨Git根新启动效果尚未实测”。

结论：根AGENTS并非未生效的自建说明；两个文件的职责分别为规则正文与读取入口，不是两份竞争规则。已经加载也不意味着模型必然完全遵守，实际执行仍以文件修改及研究记录为证据。此前对优化任务的记录规范核对继续成立。本次只补充可核验的加载证据，不修改共同规则、Codex配置或实验进程。

<a id="optimization-thread-documentation-review-20260914"></a>

## 2026-09-14：截图中“优化方法”任务的记录规范核对

用户提供截图，要求核对任务是否遵循统一文档要求。已通过本地任务历史定位任务`01a09dd7-8667-7ab0-8a9e-7051b56031e7`，截图对应最终回复轮次`01a09df4-40af-79d0-a902-71f774d5e18e`，回复时间2026-09-14 12:22:57（Asia/Shanghai）。检查用户消息/最终回复、文件修改事件及相关读写命令；没有把历史任务中的实验授权当作本次执行指令。

结论：该任务按迁移时序切换了主记录，文档归属与实验留痕符合约定。11:03创建旧优化主记录时，尚未切换到docs；最后一次旧路径追加启动信息是12:08:18。旧文件于12:09:34改为迁移入口。任务12:11:36检查该入口和AGENTS，12:11:42读取更新后的AGENTS及docs主记录；12:13:48、12:16:15和12:22:30的新增分析、进展及最终结果均写入docs/research/optimization.md，12:22:30还更新docs/README.md。当前旧文件仅保留跳转和历史章节链接，没有迁移后的独立研究正文。本次没有找到该任务在切换后继续向旧主记录写研究内容的操作。

研究主记录保留首轮prepare失败及修复、提示复核负结果和不采用决定、七方法离线分析、四条件2,004次生成的配置/范围、分层结果、无效输出、token与时间成本、证据路径、限制及下一步。未把75道MedPIC R2诊断冒充完整79道R2或全v5优化成果。最新结果段落的本地证据链接已检查可定位。

截图中的脚本、launch.sh和运行包README继续放在Documents/Codex目录符合制品管理约定；运行包README明确链接docs主记录，主要承担配置、命令和证据导航。该实验仍属于同一优化方向，续写optimization.md合理，无需为本次四条件对照新建研究主文档。截图显示的是该任务切换前后累积修改，因此旧路径仍列在修改列表中不能单独作为违规证据。

核对入口：[研究主记录](/home/data3/txy/docs/research/optimization.md)、[旧入口](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/OPTIMIZATION_RESEARCH_RECORD.md)、[运行包README](/home/data3/txy/Documents/Codex/2026-09-14/new-chat/r2_backbone_retrieval/README.md)。截图之后12:28的用户范围澄清也已追加到新主记录；本次结论针对文档规范，不替代代码正确性和全部实验分数的独立验收。没有重新推理、评分、修改实验正文或联系其他任务。

<a id="agent-instructions-scope-20260914"></a>

## 2026-09-14：指令加载范围与文档扩展规则

用户要求确认AGENTS是否生效，并明确记录范围、归属、新建文档和新目录的标准。当前任务上下文已包含工作区AGENTS，本轮又直接读取了磁盘当前内容。实际文件是`/home/data3/txy/AGENTS.md`，没有单数`AGENT.md`。检查时工作区根、父目录、docs及实际Codex home中未发现AGENTS.override.md；配置未显式设置project_doc_max_bytes、备用文件名或项目根标记。不能由此推断每个其他任务的已加载快照。

官方说明Codex在每次run开始构建指令链：先读Codex home全局指令，再按项目根至当前目录发现项目指令；同目录优先override，默认合计上限32KiB。独立Git仓库的项目根可能阻断对上层txy根指令的自动发现；现有长任务也不能假定即时重载。[官方AGENTS加载说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

本地实际CODEX_HOME为`/home/data3/txy/.codex`；该目录原先无全局AGENTS/override。txy根没有.git，MedRGAG、MA-RAG、MedRAG-upstream及CF代码目录各有.git。因此新增[薄全局入口](/home/data3/txy/.codex/AGENTS.md)：只对当前目录位于txy及其子目录的任务，要求读取工作区根AGENTS；其他目录不施加本项目规则。没有修改模型、配置、会话或进程，没有批量向其他任务发消息，也没有声称已运行独立新任务验证加载。

[根AGENTS](/home/data3/txy/AGENTS.md#documentation-scope)新增内容：实质记录与重复问答的界限；按研究问题/方法身份/阶段/版本决定归属；数据、基线、协议、评测、研究、公共环境和归档的分工；同事实单处正文。新建要求存在真实独立边界和当前具体内容，同问题默认续写；新子目录要求多份不同职责的相关文档确实需要组织，新一级目录要求现有类别不能承接的实际职责。名称使用稳定内容，版本只在协议确有独立含义时进入文件名；新建/拆分/迁移同步登记总入口。运行证据包的新目录与长期主文档的新建分别判断，常规选择不增加审批步骤。

`docs/README.md`只链接这套共同规则，避免重复维护。现有22份文档不是数量上限。原Scope limits、成功/失败与负结果记录、证据保存要求均保留。本次验证只针对新增入口断链、根与全局指令合计长度可能触及默认加载上限，以及指令文件命名；未为文档规则启动模型或实验。 验证结果：根与全局指令合计16,307字节，小于默认32,768字节；新增范围/扩展锚点和导航链接均存在。

<a id="outside-docs-audit-20260914"></a>

## 2026-09-14：Documents/Codex之外的零散文档复查

用户询问其他位置是否仍有零散内容。本次扫描工作区根目录及代码目录中的Markdown、文本、RST、PDF、Notebook文件，并检查`.codex/attachments/`；另对MedRGAG、MA-RAG、MedRAG-upstream关闭Git忽略规则复查，未发现额外被忽略的同类记录。排除依赖环境、模型、语料缓存和工具插件文档。这里只核查文件归属，没有逐条重新审阅所有聊天消息或模型轨迹。

结果：根目录旧分类指南、v3工作记录、研究计划和工作区指南均已归入docs；MedRGAG中的六份本地复现/审计/结果说明也已合入，原件保留历史用途。本次没有发现这些位置还存在另一份尚未归入的独立实验主记录。MA-RAG、MedRGAG和MedRAG-upstream的上游README，以及五份依赖清单，继续属于各代码目录。

外部参考原件仍分散：根目录的MedRGAG论文PDF，以及`.codex/attachments/a3ab4721-70b7-4b9e-9f4b-937588b4d3f4/`中的研究报告和30项文献JSON。论文已在复现归档/工作区说明中登记；附件已在优化主记录中链接，其筛选判断已进入主记录，外部报告全文未复制为新的实验主文档。`.codex`中的原始任务历史仍是聊天证据，不属于22份主文档；此前关键词追溯不等于已经逐条提炼全部历史消息。

文件清单及归属见[复查清单](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/outside_docs_audit.csv)。本次只补记管理结论，没有搬移代码、参考材料或实验制品，没有新增主Markdown。


<a id="documentation-migration-20260914"></a>

## 2026-09-14：完整目录建立与历史正文迁入（已完成）

用户确认方案B并要求建立整套目录、复制已调查历史内容。本轮创建`/home/data3/txy/docs/`的22份主文档，覆盖数据、七份基线方法、评测、新研究以及七份历史归档。原始正文来自158份现存研究文档及1份从Git找回的历史报告，共417个来源段落/文档块按归属合入；相同完整块合并13处。上游代码说明、可执行prompt、原始数据内README和发布镜像保留在原位置，不将其计入研究主文档。

跨主题的原工作区指南、v3记录、v5变更记录和M6/M7复现记录按章节分别归位；每段只分配一个主位置。单一主题原文保留完整主体，成功、失败、错误修正、暂停、未采用方案和不同版本的结果均保留。内容导航列出来源章节；Markdown相对链接转为可定位的绝对路径，已迁移记录之间链接到新主文档的对应段落。代码块中的命令和配置保留原语义与原工作目录。

本次额外纳入迁移时更新：MedGENIE全量已完成，七方法正式比较在[v5主表](/home/data3/txy/docs/evaluation/v5.md#current-seven-methods)；R2首轮开发试验已完成且未采用，随后新骨干×检索受控实验已启动，均在[优化研究记录](/home/data3/txy/docs/research/optimization.md)。切换前发现原优化记录被其他任务更新，先合入新增段落及最新状态，再修改入口；没有覆盖该任务新增记录。

### 原文备份与章节去向

- [迁移前原文备份](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/source_documents_before_migration.tar.gz)：159个原文件，包括158份研究文档和AGENTS；按工作区相对路径保存，未用哈希取代正文。
- [来源章节→新主文档清单](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/section_mapping.csv)：源路径、起始行、字符范围、归属文档、段落锚点；417行记录。
- [历史链接去向](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/link_targets.json)：原文及章节锚点到新正文的对应。
- [CF-WM Git b714735恢复原文](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/cf_wm_results_b714735.md)：保留曾被DeltaRev覆盖的修正版报告。
- [入口切换前新增原文](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/cutover_source_updates.tar.gz)：保存并行任务新补的优化记录，章节清单同步更新至此版。

根AGENTS已指定docs为唯一长期记录目录，删除过时的逐运行Project documentation摘要。根旧指南、分类指南、v3工作记录、旧研究计划及近期持续过程文档改为入口；其他已合入历史文档标明归档，运行包README与冻结结果保留内容及证据用途。此前10个跳转入口同步指向新主记录，避免仍引导在日期目录续写。

### 维护方式

每份主文档顶部维护带日期的最新状态；按阶段在正文续写目标、实际尝试、配置、结果、证据、决策与下一步。一个阶段内不因新任务、日期、修复或重试新开文档；独立新方向才在docs下建主记录并登记总入口。方法细节归baselines，跨方法比较归evaluation，原始日志和冻结报告留运行包。历史内的旧续写要求由当前AGENTS及docs/README的归属取代。

### 验证与限制

已核对159个来源版本的417个片段完整覆盖源正文，目标段落均存在，未发现漏段或重复分配；13个完全相同的正文块改为单处内容加引用。检查新文档及根入口的2,215处本地链接，目标路径和迁移锚点均可定位，代码围栏闭合。两处原历史局部AGENTS.md/agent.md路径已不存在，5条带行号引用改指现存归档合同或实验结果，并保留旧名称说明。验证结果见[validation.json](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/validation.json)。

13份持续过程文档改为含原章节入口的跳转，其余原文按用途保留；此前10个合并入口以及另外2个现有导航同步直达新主记录。原始发布快照保留原字节，不将其改成活动记录。切换前的优化记录新增内容已保存到补充备份并合入；之后各任务应直接在docs主文档续写。

本次仅整理文档和导航，没有推理、重新评分、改动实验数据或操作实验进程。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [MEDRGAG_WORKSPACE_GUIDE.md](#record-0001)
- [论文实验记录入口与续写归属](#record-0002)
- [2026-09-13 历史对话追溯与正文合并](#record-0003)
- [2026-09-14 稳定文档目录方案（初版比较；随后选定B，尚未迁移）](#record-0004)
- [2026-09-14 方案B：历史调查与具体目录归属](#record-0005)
- [2. Data flow](#record-0023)
- [3. Top-level directory map](#record-0024)
- [6. GitHub handoff](#record-0034)
- [7. Model inputs](#record-0035)
- [8. Fast start for a new conversation](#record-0036)
- [12. MA-RAG environment and execution contract](#record-0046)
- [12.1 Actual main configuration](#record-0047)
- [12.2 Service layout used](#record-0048)
- [17. Takeover checklist for another agent](#record-0059)
- [v5 实施与复现总记录（2026-09-13）](#record-0063)
- [v5 M6/M7 正式输入小批量试跑与上游兼容性修复（2026-09-13）](#record-0064)
- [v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）](#record-0065)
- [v5 M6/M7 提高并发后接续（2026-09-13 06:37）](#record-0066)
- [v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）](#record-0067)
- [M4/M6修复实施文档汇总（2026-09-13）](#record-0074)
- [最新v5五方法文档与图表同步（2026-09-13）](#record-0078)
- [近期文档与 GitHub 首页发布完成（2026-09-13）](#record-0079)
- [M6/M7与新M4吞吐差异诊断（2026-09-13）](#record-0080)
- [M6/M7 vLLM 优化验证（2026-09-13 20:00，完成）](#record-0081)
- [3. 方法设置：哪些属于实验定义](#record-0092)
- [3.3 上下文与推理后端](#record-0095)
- [4. 工程调整与性能证据](#record-0097)
- [4.5 未采用的提速方案与参考来源](#record-0102)
- [7. 修改与证据的文件索引](#record-0110)
- [17. 近期记录归档与 GitHub README 更新（2026-09-13）](#record-0143)
- [17.1 本轮实际完成的工作](#record-0144)
- [17.2 发布范围、验证及提交](#record-0145)
- [17.3 对实验与论文的影响](#record-0146)
- [PAPER_REPRODUCTION_RECORD.md](#record-0174)
- [1. 实际完成的工作及代码位置](#record-0175)
- [2. 固定来源与最终配置](#record-0176)
- [2.1 方法依据](#record-0177)
- [2.2 最终执行参数及来源](#record-0178)
- [3. 对方法具体做了什么调整](#record-0179)
- [4. 实际试跑、修复和复验顺序](#record-0183)
- [4.1 并发、随机数和显存修复的具体变化](#record-0184)
- [4.3 曾准备但未执行的工作](#record-0186)
- [6. 验证证据和最终真实开发结果](#record-0192)
- [6.1 自动测试与轨迹审计](#record-0193)
- [6.2 最终终态及方法运行量](#record-0194)
- [6.3 按来源的完整分母评分](#record-0195)
- [7. 已发生的计算成本及正式成本估算](#record-0196)
- [7.1 开发累计新增计算](#record-0197)
- [7.2 正式规模及尚不能估出的部分](#record-0198)
- [8. 可用于论文的表述及局限性](#record-0199)
- [8.1 Methods草稿](#record-0200)
- [8.2 实现验证草稿](#record-0201)
- [8.3 当前证据的局限](#record-0202)
- [9. 制品导航及记录维护](#record-0203)
- [本次试跑发现的上游行为遗漏（2026-09-13）](#record-0205)
- [10. M6/M7与新M4吞吐差异诊断（合并原独立分析）](#record-0213)
- [实测对照](#record-0214)
- [1. 方法本身需要多少工作](#record-0215)
- [2. 主要执行瓶颈：静态批次等待最长输出](#record-0216)
- [3. 等待池很大，实际批次仍小](#record-0217)
- [4. M7的熵采集和采样循环有额外开销](#record-0218)
- [建议的实施顺序](#record-0220)
- [实现](#record-0222)
- [验证设计与证据](#record-0223)
- [完成结果](#record-0224)
- [执行与复核](#record-0225)
- [解释边界](#record-0226)
- [method_fidelity.md](#record-0374)
- [固定来源](#record-0375)
- [逐组件对应](#record-0376)
- [默认值及差异（不可混作论文原参数）](#record-0377)
- [验证证据](#record-0378)
- [acceptance_report.md](#record-0379)
- [实现与冻结条件](#record-0380)
- [自动测试与数据审计](#record-0381)
- [正式规模和成本](#record-0384)
- [命令与限制](#record-0385)
- [README.md](#record-0387)

<a id="record-0001"></a>

## MEDRGAG_WORKSPACE_GUIDE.md

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

### MedRGAG Workspace Guide

Updated: 2026-09-14 (Asia/Shanghai; documentation layout survey)

This is the MedRGAG orientation and historical handoff document. Use it to
locate the relevant source, interface, result, and handoff without
rediscovering the workspace or rerunning an experiment.
Inspect additional files only when the user's requested change actually
touches them.

For paper methods and a dated record of completed work and concrete changes,
read [the consolidated work log](/home/data3/txy/docs/data/construction.md#record-0351)
([GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_process_history/README.md)),
expanded on 2026-09-13. It distinguishes collection, semantic labels,
qualification, sampling and model runs; documents the 704-unit AMQA review
overlay and 172-judgment audit corrections; and connects the 09-08 archive to
v2/v3/v4/v5 without mixing their counts. This update only consolidated existing
artifacts and documentation. Follow each run pack's final report for model
completion; a dated dataset README can predate its subsequent completed run.

<a id="record-0002"></a>

## 论文实验记录入口与续写归属

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第23行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 论文实验记录入口与续写归属

维护约定：2026-09-13。每次论文相关实质工作都按 [AGENTS.md](/home/data3/txy/AGENTS.md)
的持续记录要求落盘。先按下表选择已有主记录；同阶段同方向的新对话继续更新
该文档。跨阶段记录中的重叠内容作为衔接摘要保留，后续细节只在所属主记录更新。

| 阶段 / 方向 | 优先续写的主记录 | 范围边界 |
|---|---|---|
| 早期来源收集、首轮分类与审核、v2/v3 数据沿革 | [工作过程与调整记录](/home/data3/txy/docs/data/construction.md#record-0351) | 后续 v4/v5 只保留衔接摘要；相关构建细节续写下一项 |
| v4 全量补分类、资格恢复、v5 抽样与构建 | [v3→v4→v5 构建工作记录](/home/data3/txy/docs/data/construction.md#record-0355) | 已有探索历史作为冻结决策证据；后续构建调整集中在此续写 |
| v3 基线实现、评测及分类指南修订 | [v3 基线工作记录](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0233) | 分类规则正文仍在分类指南；这里只记修改经过、原因与证据 |
| M4/M5 安装、独立入口与历史RRF配置 | [安装与接入记录](/home/data3/txy/docs/baselines/medrag.md#record-0254) | BASELINES正文已合入第16节；正式v5实施回到下一项 |
| v5 M0–M5 评测、格式诊断与修复试验、工程优化 | [评测实施与复现记录](/home/data3/txy/docs/evaluation/v5.md#record-0084) | 含M6 formatter、M7离线候选与控制流程真实试验；各运行包保留原始证据 |
| M6/M7 方法接入、MedGENIE替代候选、开发验收、正式运行与后端优化 | [M6/M7 实现与调整记录](/home/data3/txy/docs/workspace.md#record-0174) | 格式候选试验引用上一项；应用到方法或运行后的变化与结果记在此处 |
| v5 五方法比较表、图与汇总结论 | [最新比较结果](/home/data3/txy/docs/evaluation/v5.md#record-0410) | 维护汇总结果和来源链接；实验尝试与实施经过回到上述评测主记录 |
| 医疗反事实优化研究总览（2026-09-14起） | [优化研究总览](/home/data3/txy/docs/research/optimization.md) | 文献取舍、跨类诊断、其他head构建经验及起步探索 |
| R2独立支持重算head（2026-09-14拆分） | [R2主记录](/home/data3/txy/docs/research/r2_support_head.md) | 独立接口、成功与失败实验、跨方法分析；[拆分记录](/home/data3/txy/docs/research/r2_support_head.md#r2-documentation-split) |

本指南承担导航和当前状态摘要，不复制完整实验过程。已完成或暂停的旧研究方向
沿用下文链接的对应历史记录；新的独立阶段或方向确需另建主记录时，在本入口登记。
主记录里的最新状态应带日期，旧计划、运行中描述和旧结果保留为对应阶段的历史。

首次维护记录（2026-09-13，正文合并前）：因用户要求跨对话自动记录实验过程，在共享
`AGENTS.md` 加入持续记录、失败保留、优先续写和合并保留证据的要求；在本指南
集中明确上述续写归属。已检查的主记录有阶段衔接内容，也有各自独有的决策与证据，
本次保留其正文和原路径，通过明确主记录减少后续重复维护。未新建记录文档，
未改动实验数据、方法、预测或评分，未启动或中断实验。

<a id="record-0003"></a>

## 2026-09-13 历史对话追溯与正文合并

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第52行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 2026-09-13 历史对话追溯与正文合并

用户进一步要求从之前对话回复中寻找补写的记录并实际合并。本次只读检索本地会话历史中的用户请求与最终回复，再对照现有源文件；未将其他对话的授权当作本次启动实验或发布的指令。找到的论文记录回复包括：

| 对话 / 请求轮次 | 回复指向的记录 | 本次处理 |
|---|---|---|
| `01a0897c-63e4-7803-b918-7910e00692e7` / `01a09728-34a0-7241-809b-7925a1525fd4` | M4_M5_INSTALLATION_REPORT.md | 补入主入口；合并BASELINES，移除与评测主记录重复的后续M4过程 |
| `01a0947c-10a2-7502-ab27-d1d1c2ab699a` / `01a0972a-65d5-7b32-9e9c-c29f0f69ec25` | PAPER_REPRODUCTION_RECORD.md | 合入后来的吞吐诊断、vLLM实现、失败重试和完整验证 |
| `01a08d17-5e95-7b53-b9bc-ef78270281b9` / `01a09761-1950-7a42-8e08-392e0eda63df`；`01a09944-a2e1-7391-9dbf-c4774e5009da`；`01a09aae-b416-7312-8deb-1e79dd7062cf` | EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md及M4/M6修复详情 | 合入六份过程文档；原有第17节发布记录、第18节M7候选修复及最新第19节控制流程真实试验继续保留 |
| `01a08a2f-3fd4-7650-9e3e-9e7590b5cc34` / `01a08ba2-2279-7d81-ac50-f0b04d2589c6`；`01a09764-ccce-7e70-b792-7a3523bcc1bf` | EXPLORATION_HISTORY.md及v3→v4→v5总记录 | 合并七来源排除预览、比例配额表、五轮讨论及实际抽样 |
| `01a0855b-01f3-7490-94fa-7838abbf595b` / `01a09763-1055-7123-8bf1-773ea90a4167` | R1_R5_V3_BASELINES_WORK_RECORD.md | 保留v3实施阶段主记录，区别于v5 |
| `01a07e59-984e-7580-a306-3d6c68815e99` / `01a09764-ebfa-7730-b982-809ad03fb59a` | 工作过程与调整记录_论文参考.md | 保留早期收集、704条AMQA调整及172项审核修正证据 |

本地检索来源为 `/home/data3/txy/.codex/thread_history_1.sqlite` 的用户消息与最终回复；上表保存可追溯的线程和轮次ID，不复制整段聊天。历史发布回复另指向56份文档、584份来源制品的GitHub快照（`476c6ba`），以及后续文档更新（`0f4d1e3`）；本次从服务器源文档合并，公开快照保留发布时内容，没有推送GitHub。

| 原独立叙述（原路径仍可打开） | 合入主记录 |
|---|---|
| `2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v5_20260910/EXPLORATION_HISTORY.md` | [README.md](/home/data3/txy/docs/data/construction.md#record-0355) |
| `2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/BASELINES.md` | [M4_M5_INSTALLATION_REPORT.md](/home/data3/txy/docs/baselines/medrag.md#record-0254) |
| `2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/performance_notes.md` | [EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/docs/baselines/marag.md#record-0100) |
| `2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/old_m4_pilot/README.md` | [EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/docs/baselines/medrag.md#record-0119) |
| `2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_pilot/README.md` | [EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/docs/baselines/medrag.md#record-0120) |
| `2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/README.md` | [EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/docs/baselines/medrag.md#record-0120) |
| `2026-09-11/agent-md-medrgag-workspace-guide-md/m6_formatter_pilot/README.md` | [EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/docs/baselines/imedrag.md#record-0125) |
| `2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/README.md` | [EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/docs/baselines/tcrag.md#record-0136) |
| `2026-09-13/agent-md-medrgag-workspace-guide-md/m6_m7_speed_analysis/README.md` | [PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/docs/workspace.md#record-0213) |
| `2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/README.md` | [PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/docs/baselines/tcrag.md#record-0221) |

共10份独立叙述合入4份已有主记录，原文件改为简短入口。替换主记录原有的重复摘要，保留独有的失败、未采用方案、参数、样本范围和证据位置；M4安装文档中与评测文档重复的运行及完成段落改为引用。输入/评分协议、方法忠实度、开发验收和不同版本的RESULTS保留各自用途，原始制品及发布快照不删除。

合并前的16份原文件集中保存在[单个备份包](/home/data3/txy/Documents/Codex/2026-09-13/agent-md/documentation_before_merge_20260913.tar.gz)，内部按 `/home/data3/txy` 下相对路径保存，用于追溯合并前措辞。未新建主Markdown。合并后检查了431处本地链接，10个旧入口均指向存在的主记录章节；原文中的本地证据链接均已保留在对应主记录。另核对了关键失败、未采用方案和结果（含新补的M7第19节），未发现遗漏；代码围栏完整，16份原文备份可读取。本次没有新推理、重评分、数据修改或GPU操作。

<a id="record-0004"></a>

## 2026-09-14 稳定文档目录方案（初版比较；随后选定B，尚未迁移）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第86行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 2026-09-14 稳定文档目录方案（初版比较；随后选定B，尚未迁移）

用户指出长期记录仍散落在 `Documents/Codex/日期/`，要求提出几个明确的CF/MedRAG文档管理结构供比较。此前合并指定的主文件仍位于日期目录，因此仅要求“续写主文档”不能解决项目归属。本次阅读现有记录入口、方法与结果文档，以及新增优化研究记录后提出以下方案。

用户随后明确：`/home/data3/txy` 整个目录就是当前实验工作区，没有独立的CF/MedRAG项目根目录。现有MedRGAG、MA-RAG及CF代码目录是工作区中的组成部分。撤回另建 `/home/data3/txy/cf-medrag/` 项目入口的建议；以下三种方案统一以 `/home/data3/txy/docs/` 为拟议文档根目录，由 `/home/data3/txy/AGENTS.md` 指向 `docs/README.md`。只整理文档归属，现有代码、数据、运行目录和模型位置由文档引用。`docs/` 尚未因本提案创建或迁入文件。

| 方案 | 文档布局 | 优点与代价 |
|---|---|---|
| A：少量平铺主文档 | `docs/`下的`README.md`、`classification.md`、`data_construction.md`、`baselines.md`、`experiments.md`、`results.md`、`optimization.md`、`history.md` | 文件最少、入口直接；基线和实验记录容易继续增长成大文件 |
| B：按研究内容分组（建议） | `docs/README.md`；`data/{classification,construction}.md`；`baselines/{m0_m3,medrag,imedrag,medgenie,tcrag}.md`；`evaluation/{protocol,v5}.md`；`research/optimization.md`；`archive/` | 数据、方法、统一评测和新研究各有归属；方法名称稳定，跨方法汇总集中维护，需要一次内容归位 |
| C：按阶段分组 | `docs/README.md`；`01_collection/RECORD.md`；`02_v3/RECORD.md`；`03_v4_v5_construction/RECORD.md`；`04_v5_evaluation/RECORD.md`；`05_optimization/RECORD.md`；`archive/` | 便于还原论文工作时间线、迁移旧记录较直接；跨阶段方法和协议容易重复 |

方案B中，每个方法文件同时记录其实现、调整、成功/失败尝试和证据；`evaluation/v5.md`维护跨方法结果与比较结论，不再复制各方法过程。`docs/README.md`集中维护当前状态、方法编号对应、主记录入口及实际代码/数据/运行路径。M0–M3已有基线记录先合并归位，不预先为每个编号创建文件；后续确实增长为独立方向时再拆分。归档保留有实际内容的旧阶段，不预建空文档。

命名依据：当前M6已换为MedGENIE，旧i-MedRAG需保留身份，因此以`imedrag.md`、`medgenie.md`分别维护，M编号在总入口登记并标明适用版本。M7第二版全量结果已存在；MedGENIE全量包已记录启动。这些状态说明需要按方法身份及运行版本管理，不能把旧编号含义覆盖成新方法。

初版比较时只提供结构选择并记录原因，没有选定方案、创建目录、迁移文件、修改运行配置或操作实验进程。用户随后选择B，具体调查与目录提案见下一节。现有入口在方案落地前继续有效；落地时再统一修改AGENTS中的文档归属与旧入口。

<a id="record-0005"></a>

## 2026-09-14 方案B：历史调查与具体目录归属

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第106行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 2026-09-14 方案B：历史调查与具体目录归属

**状态：用户已选择“按研究内容分组”；以下为基于历史内容细化的目录提案，尚未执行迁移。** 文档根目录拟为 `/home/data3/txy/docs/`，覆盖整个txy实验工作区。

###### 调查范围与实际发现

本次检索工作区根文档、`MedRGAG/`、`MA-RAG/`及`Documents/Codex/`中的227个候选Markdown路径，按研究方向阅读主记录、章节、结论和证据入口，并对照本地会话库检索到的30个相关任务、206条最终回复、67个不同的本地Markdown链接。227是候选路径数，含提示模板、发布副本及旧跳转入口，不是227份独立实验记录；206也不是206次实验。对话检索采用MedRGAG、MedRAG、R1–R5、MedEinst、WM、Adapter等研究名称，覆盖当前可定位的历史研究线；没有把全部原始模型轨迹逐条阅读或重新运行实验。

历史回复还补出了被初步文件扫描排除的WM盲审运行包README；旧`r1_r5_full_classification_20260910`链接实际指向v4目录；已不存在的旧`agent.md`/局部`AGENTS.md`名称需结合现有归档合同解释，不能当作活动指令恢复。会话来源是本地`.codex/thread_history_1.sqlite`，原始内容保留在原库，不批量复制聊天到新文档。

调查确认需要覆盖这些阶段：早期Direct与完整MedRGAG复现；原WM代理实验；CF-WM Gate与修正版；DeltaRev、DeltaRank、CFShift、CF-KADS-MoE、RiskRoute；CF-Residual Adapter/MA-RAG；原生来源baseline screening及全量比较；医学CF收集、R1–R5分类与v2/v3/v4/v5构建；各基线接入、格式修复和性能调整；v5统一评测；最新优化研究；发布与交接。

发现三项具体的归属问题：

1. 本指南约155KB，混有大量方法过程和多个已经过时的“当前”描述。新的总入口应只保留带日期的状态与导航，完整历史按内容归位。
2. M1是MedRGAG初始检索的retrieval-only对照，不能并入独立MedRAG的M4/M5身份；M6先指i-MedRAG、后指MedGENIE。文件名使用方法名称，编号表标明评测版本及变更日期。
3. CF包的`results/summary.md`存在真实的跨方向覆盖：当前正文是DeltaRev；本地提交`b714735`中的同路径是修正版CF-WM报告。已用只读`git show b714735:cf_medrgag_validation_pack/results/summary.md`读取前版，确认303条gold-unseen分析、方法对照、解析失败修正和负结论均可追溯。迁移时分别归入CF-WM和CF方法探索，不能按当前文件名把两个研究混为一项。

###### 具体目录

下列22份主文档均有现存内容可承接；其中7份归档历史方向。数量针对长期叙述主记录，不要求删除原始运行包README、冻结报告或机器可读证据。不为日期、对话、单次重试再开主文档。

```text
/home/data3/txy/
├── AGENTS.md                         # 持续记录要求；指向docs/README.md
├── docs/
│   ├── README.md                     # 唯一总入口：当前状态、方法身份、主记录导航
│   ├── workspace.md                  # 实际代码/数据/模型/环境路径，公共接口与发布沿革
│   ├── data/
│   │   ├── sources.md                # 来源清单、获取状态、原生任务与本地资源
│   │   ├── classification.md         # R1–R5定义、规则、实例与规则修订
│   │   └── construction.md           # 收集审核→v2/v3→v4→v5，资格/抽样/数据沿革
│   ├── baselines/
│   │   ├── direct_retrieval.md       # M0 Direct、M1 retrieval-only
│   │   ├── medrgag.md                # M2全Llama MedRGAG，实现与跨版本适配
│   │   ├── marag.md                  # M3 MA-RAG原生基线，接口、运行与性能调整
│   │   ├── medrag.md                 # M4/M5；安装、检索、骨干差异、格式修复
│   │   ├── imedrag.md                # 旧M6 i-MedRAG，试跑、失败、优化与暂停
│   │   ├── medgenie.md               # 当前M6 MedGENIE，替代决策、试跑与全量
│   │   └── tcrag.md                  # M7 TC-RAG，控制流程、熵、修复与全量
│   ├── evaluation/
│   │   ├── protocol.md              # 原生输入、证据权限、评分、分母、复用与比较规则
│   │   └── v5.md                    # v5全局运行进度、版本选择、跨方法表图与结论
│   ├── research/
│   │   └── optimization.md          # 当前文献筛选、错误分析、机制假设及后续实验
│   └── archive/
│       ├── medrgag_reproduction.md  # 早期Direct/Table 1/all-Llama v15复现历史
│       ├── wm_medrgag.md            # 原始WM代理、盲审、匹配对照与停止结论
│       ├── cf_wm.md                 # CF-WM Gate、无效oracle、修正版与负结果
│       ├── cf_method_trials.md      # DeltaRev→DeltaRank→CFShift→CFMoE→RiskRoute
│       ├── cf_residual_adapter.md   # Adapter设计、MA-RAG迁移、消融与结论范围
│       ├── native_baseline_screening.md # 早期来源筛选、M2全量、M0/M1/M2比较
│       └── r1_r5_early_evaluation.md # 初期R1–R4、旧rubric、v2/v3评分与结果
├── MedRGAG/                         # 现有代码与运行证据
├── MA-RAG/
├── MedRAG-upstream/
├── models/
└── Documents/Codex/...              # 现有数据、代码、运行包、历史发布快照及证据
```

相比初版B，把过大的`m0_m3.md`按实际方法拆成Direct/retrieval-only、MedRGAG和MA-RAG三份；M4/M5仍共用一份MedRAG文档；五个连续CF探索方法共用一份历史文档。数据沿革和实验暴露放在`construction.md`的专节，不再额外拆一个账本。已有Methods草稿归入对应数据/方法/评测文档的论文表述部分；目前不预建空的`paper/`目录。

###### 现有材料到新主文档的对应

以下路径缩写只用于本次来源表，均相对于 `/home/data3/txy/`；它们指向现有目录，不表示搬迁代码或运行制品：

| 缩写 | 现有位置 |
|---|---|
| W | `Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/` |
| C | `Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/` |
| P | `C/cf_medrgag_validation_pack/` |
| D | `Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/` |
| B | `Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/` |
| M | `Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/` |
| E | `Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/` |
| I | `Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/` |
| N | `Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/` |

| 新主文档（均在拟议docs下） | 现有正文来源与明确归属 |
|---|---|
| `README.md` | 本指南记录入口、方法映射、最新结果入口；AGENTS中不断增长的Project documentation摘要。保留当前结果版本及证据链接，旧状态送回相应历史章节 |
| `workspace.md` | 本指南目录图、代码接口、模型输入、MA-RAG环境、制品位置、发布/交接段落；`C/chatgpt_handoff_2026-09-05/README.md`的环境与路径；`E/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md`第17节发布；本指南9月13日合并和本次目录决策。发布副本和清单仍留原位置 |
| `data/sources.md` | `D/医学CF资源清单.md`及各`parts/`来源报告；`P/datasets/DATASET_MATRIX.md`；`B/r1_r5_benchmark_sources_20260910.md`；v4来源范围、可取得/缺失资源说明。历史取得状态带日期，来源ID沿用已有编号 |
| `data/classification.md` | 根目录`R1_R5_CLASSIFICATION_GUIDE.md`为规则正文；吸收`R1_R5_V3_BASELINES_WORK_RECORD.md`中规则文本变化与依据；早期分类说明仅合入独有内容。逐项审核结果仍引用原审计制品 |
| `data/construction.md` | `D/工作过程与调整记录_论文参考.md`、分类与抽样说明、审计/704条AMQA/172项修正；`B/paper_work_record_20260913/README.md`、v4 DELIVERY/资格恢复/未采用范围预览、v5抽样历史；v2/v3材料化README。历史MedEinst dev/cal/test及先前暴露沿革也在此统一登记 |
| `baselines/direct_retrieval.md` | 根v3记录第3.1节，`P/results_cf_screening/`和`results_cf_full_comparison/`的M0/M1调用合同，E中的M0复用与运行细节。早期直接回答的两次Table 1实验结果引用复现归档 |
| `baselines/medrgag.md` | `MedRGAG/REPRODUCE_ALL_LLAMA.md`的有效运行接口、v3记录第3.2节、P中M2 baseline_contract、E中v5 M2配置与复用；早期论文/代码差异和v15历史证据引用复现归档 |
| `baselines/marag.md` | 根v3记录第3.3节、`P/results_r1_r5_v3_m3_20260909/`运行材料、E中M3接口与性能优化、`E/results_v5_m3/`。早期带CF sidecar的MA-RAG实验独立留Adapter归档 |
| `baselines/medrag.md` | `M/M4_M5_INSTALLATION_REPORT.md`及已合入的BASELINES；E主记录M4/M5配置、无效率、旧M4与结构修复、真实运行；`N/results_v5_m4_structured/`。原RRF安装配置、v5检索配置、新M4输出协议分别保留身份 |
| `baselines/imedrag.md` | `I/PAPER_REPRODUCTION_RECORD.md`、method_fidelity及acceptance_report中的i-MedRAG部分；E主记录第12节formatter；N旧M6试跑/吞吐/正式暂停记录。保留缓存复验、离线重放与新推理区别 |
| `baselines/medgenie.md` | I主记录后续MedGENIE替代与适配段落；`N/results_v5_m6_m7/m6_medgenie_fresh/`和`m6_medgenie_v5_full/`的开发/正式证据。与旧i-MedRAG各自续写 |
| `baselines/tcrag.md` | I主记录TC-RAG及相关忠实度/验收；E第14、18–24节的审计、控制流程修复、第二版和仅异常恢复消融；N中M7试跑、暂停包、`m7_typed_v5_full/`。共用后端配置在workspace描述，TC熵和控制行为归本文 |
| `evaluation/protocol.md` | E主记录数据/复用/原生评分、各方法已有输入合同及I第5节；统一source→unit→target→input、证据可见性、labels/evaluation_labels、计分与比较限制。旧rubric协议仅留历史，不成为当前默认 |
| `evaluation/v5.md` | E主记录全局调度、复用/新增覆盖及跨方法结果；`N/v5_benchmark_latest/README.md`五方法表、M7完整第二版六方法图、之后MedGENIE完成报告。原版M4/旧M7仍是历史结果，不能混入最新版而省略身份 |
| `research/optimization.md` | [现有优化主记录](/home/data3/txy/docs/research/optimization.md#record-0255)，并接入E第15–16节相关问题定位；原附件中的外部研究报告与文献JSON作为来源。后续同方向机制实现、失败和成功实验继续在此更新 |
| `archive/medrgag_reproduction.md` | `MedRGAG/LLAMA31_REPRODUCTION_HISTORY.md`为主，合并REPRODUCE_LLAMA、RESULTS_LLAMA、REPRODUCE_MEDRGAG、ALL_LLAMA_V15_AUDIT的独有历史；保留原始版本运行结果和成本 |
| `archive/wm_medrgag.md` | `W/medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md`、PROJECT_PLAN、归档合同；补入盲审包及mrg-handoff-upload中的独有交接信息。保留85例、matched比较和停止结论 |
| `archive/cf_wm.md` | P的PROJECT_PLAN、归档CF合同、GATE_A_RESULTS、GATE_B_D_RESULTS、handoff/EXPERIMENT_CHRONOLOGY及AGENT_HANDOFF；加上提交`b714735`的修正版results/summary.md。保留M12 label oracle无效、后续gold-free修正、负结果和解析失败 |
| `archive/cf_method_trials.md` | P当前`results/summary.md`（DeltaRev）、`results_deltarank/summary.md`、`results_cfshift/summary.md`、`results_cfmoe/summary.md`、`results_riskroute/summary.md`，以及9月5日handoff相关段落。按五个方法分节，保留负结果、微弱收益及未获支持的主张 |
| `archive/cf_residual_adapter.md` | `P/results_marag_cf/summary.md`、9月5日handoff的Adapter主体，以及本指南第11–16节的实现、pilot/dev/cal/frozen test、失败恢复、成本与限制。跨框架迁移结果和未支持MA-RAG synergy的结论一起保留 |
| `archive/native_baseline_screening.md` | 根及C下RESEARCH_PLAN；`P/results_cf_screening/`、`results_cf_full_test/`、`results_cf_full_comparison/`的计划、来源选择、数据检查、smoke、findings、summary。合并共有正文，保留三个实际阶段和原生任务与四选一敏感性分析区别 |
| `archive/r1_r5_early_evaluation.md` | 早期R1–R5暂停转R1–R4；`P/results_r1_r4_m0_m1_20260908/`的rubric/category_summary/automatic_only；v2重算和v3 M0–M3结果；根v3工作记录第4节。构建规则回链data，方法实现回链baselines |

###### 同一事实的归属与原文处理

- **方法文档**记录该方法的设计、实现、配置变化、试跑、失败、修复、成本及运行结果摘要；不另建“失败集”“成功集”或逐日总结。一个方法跨v3/v5时在同文档分阶段续写。
- **评测文档**记录冻结协议、全局运行/复用情况、跨方法表图及比较结论。比如M4结构修复过程归`medrag.md`，修复版被选入v5主表的日期和结果归`v5.md`；双方只链接所需细节。
- **研究文档**承接提出新机制的文献、错误分析与实验；已停止且不再推进的方向归档。归档文档顶部明确停止/历史状态，保存当时的计划、失败和最后结论。
- **数据文档**分别负责“有哪些来源”“类别如何定义”“数据如何形成和变化”。labels语义、evaluation_labels入选、输入数和评分映射数不可混成一个样本数。
- 每份主文档顶部写带日期的最新状态、适用版本和证据入口，正文按阶段保留目标、实际尝试、结果、决策与下一步。同一阶段继续追加现有章节，历史失败不被成功结果覆盖。

原路径按其用途处理：根分类指南和旧过程文档在独有内容合入后改成指向新主文档的短入口；原总指南最终只保留新总入口链接。运行包README保留启动/恢复方法和本包制品导航，链接方法主记录；其冻结RESULTS仍可随包保留，新增分析和结论统一进入docs。上游README、可执行prompt、数据说明、JSON/CSV/日志、图表及发布快照保留原用途，不能为了Markdown数量少而删掉。先前10个跳转入口最终修正到新主文档，避免形成多级跳转。

AGENTS落地时需明确写出：**本工作区论文过程与分析的主记录只能在 `/home/data3/txy/docs/` 对应文件中创建或续写；`Documents/Codex/日期/`可保留运行包及原始证据，不作为新增长期叙述主记录的位置；每次工作先读docs/README.md并按归属续写。** 实际迁移和新入口可用后再切换这条规则，避免指向尚不存在的目录。

###### 后续落地顺序及本次交付

落地时先归位当前data/baselines/evaluation/research主记录并修复相对链接，再合并历史archive；对正在被其他任务续写的源文件，以迁移当时最新内容为准。之后切换AGENTS和根入口、缩短旧过程文档、修正引用。逐份核对独有决策、失败、结论和证据已收录；对跨阶段覆盖的文件使用对应Git版本。保留原始实验制品与已有备份，不移动活跃运行依赖的代码/数据路径。

本次只更新本指南，记录用户已选方案、历史调查、22份主文档的具体归属和后续处理方式；没有创建docs目录或迁移文件。旧主记录在迁移落地前继续有效。本次未重新推理、重评分、修改数据或操作GPU进程。MedGENIE全量包已有启动记录，M7完整第二版已有完成报告；这里只据文档定位，不另行监控或改写运行状态。

<a id="record-0023"></a>

## 2. Data flow

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1026行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 2. Data flow

```text
paper + upstream MedRGAG
          |
          v
/home/data3/txy/MedRGAG
completed five-dataset all-Llama v15 baseline
          |
          | frozen selected documents and item results
          v
archived WM workspace/private_data/.../stage-b-real-20260823-seed13-37-v4
          |
          | 85-item input -> state/cards/rankings -> reader outputs
          v
matched direct-ranking vs WM-planner result and stop decision
          |
          v
mrg-handoff-upload -> https://github.com/xiotakut/mrg

current full-release baseline path:

MedEinst + MedPIC + CPV + Cultural + MedCounterFact
   -> independent native inputs -> Direct / initial retrieval-only / full MedRGAG
   -> complete three-method comparison -> cf_mrg/benchmarks/<dated-run>/

historical pair-aware CF path:

MedEinst control/trap pairs + DDXPlus profiles
          |
          +-> DeltaRev -> DeltaRank -> CFShift -> CF-KADS-MoE -> RiskRoute
          |                      (iterative MedRGAG-side experiments)
          |
          +-> frozen Profile/CPG sidecar ---------------------+
          |                                                   |
          +-> MedRGAG-style four-option base scores ----------+-> linear
          |                                                   |   option fusion
          +-> external MA-RAG Qwen3-8B candidate pools -------+
                                                              |
                                                              v
                                      frozen 500-pair MedEinst later test
                                      + legacy-exposure caveat
                                      + transfer / no-synergy conclusion
```

<a id="record-0024"></a>

## 3. Top-level directory map

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1071行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 3. Top-level directory map

| Path | What it is | Main interface |
|---|---|---|
| `$CF_ITERATIVE` | **M6 = i-MedRAG** (`imedrag`), **M7 = TC-RAG** (`tcrag`), registered in the existing CF pack; 19 tests and 24 real development inputs per method completed, with output/scoring and coverage limitations still recorded. Preserves all pilots and source snapshots; no formal full run. | [Paper implementation and adjustment record](/home/data3/txy/docs/workspace.md#record-0174), `README.md`, `method_fidelity.md`, `acceptance_report.md`, `configs/*runtime_v4.json` |
| `/home/data3/txy/MedRGAG` | Upstream `ll0ruc/MedRGAG` checkout plus the local all-Llama reproduction, corpora, indexes, v15 runner, logs, and outputs. | `REPRODUCE_ALL_LLAMA.md`, `run_medrgag_all_llama.sh`, completed v15 `metrics.json` |
| `/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag` | Standalone `gzxiong/MedRAG` installation: **M4 = MedRAG-Llama-3.1-8B** (`medrag_llama31`), **M5 = MedRAG-Qwen3-8B** (`medrag_qwen3`). Original M4 RRF-4 passed Textbooks smoke; Wikipedia MedCPT completed, Contriever/SPECTER stopped with partial files retained. Subsequent V5 uses matching full-MedCorp BM25/MedCPT settings for M4/M5 and completed 13,905 inputs each; use the V5 run configs for those results. The report now maintains the action history, before/after changes, evidence and paper methods drafts (updated 2026-09-13); append subsequent M4/M5 work there as requested by the user. | [Installation and paper implementation record](/home/data3/txy/docs/baselines/medrag.md#record-0254), `BASELINES.md`, historical `configs/m4.json` / `configs/m5.json` |
| `$CF_REPO` | Git repository `https://github.com/xiotakut/cf_mrg`; later CF experiments, integration scripts, compact public results, and handoffs. | `$CF_FULL/findings.md`, `$CF_BENCHMARKS/README.md`, `$CF_PACK/README.md` |
| `$MARAG` | External official MA-RAG checkout at upstream commit `423f031cc0ffca679a047c885be999b9604100a9`; not vendored into `cf_mrg`. | upstream `ma_rag_entropy.py` plus the two recorded patches in `$CF_ADAPTER` |
| `/home/data3/txy/Documents` | User documents; its `Codex/2026-08-23/...ponytail-skill` child is the archived WM experiment workspace. | See section 5 |
| `/home/data3/txy/models` | Local model weights. These are runtime inputs, not source code. | Pass a local path through `P4_MODEL` or the MedRGAG runner's model argument |
| `$CF_REPO/chatgpt_handoff_2026-09-05` | Historical adapter evidence handoff, including the dataset reuse audit and timing decomposition. | `README.md` |
| `/home/data3/txy/Li - 2026 - From Retrieval to Generation Unifying External and Parametric Knowledge for Medical Question Answer.pdf` | The research paper being reproduced/extended. | Read-only research source |
| `/home/data3/txy/.codex` | Codex application state, installed skills, plugins, and thread metadata. Ponytail is installed under `.codex/skills/ponytail`. | Managed by Codex; not a project source tree |
| `/home/data3/txy/.local` | User-installed binaries and libraries; GitHub CLI is `.local/bin/gh`. | Runtime/tooling only |
| `/home/data3/txy/.cache` | Hugging Face, Python, and application caches. | Reusable cache; not authoritative output |
| `/home/data3/txy/.config`, `.copilot`, `.dotnet`, `.modelscope`, `.nv`, `.vscode-server` | Per-user tool/runtime configuration. | Not MedRGAG source |
| `/home/data3/txy/.ssh` | SSH configuration and credentials. | Outside project scope unless explicitly requested |
| shell dotfiles such as `.bashrc`, `.profile`, `.gitconfig` | User shell and Git configuration. | Environment configuration, not experiment evidence |

<a id="record-0034"></a>

## 6. GitHub handoff

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1277行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 6. GitHub handoff

Local clone:

```text
/home/data3/txy/Documents/Codex/2026-08-23/
  https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload
```

Remote: `https://github.com/xiotakut/mrg`, branch `main`.

The handoff entry is
`handoff/medrgag-wm-2026-08-23/README.md`; `FILE_INDEX.md` describes all
104 handoff files, and `CONVERSATION_HISTORY.md` contains only user/assistant
visible conversation. The handoff is a transfer copy, while the sibling
workspace paths in section 5 are the canonical local archive. Its copied results
record is `medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md`.

<a id="record-0035"></a>

## 7. Model inputs

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1295行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 7. Model inputs

| Path | Use |
|---|---|
| `models/LLM-Research-Meta-Llama-3.1-8B-Instruct` | Complete local reader/generator checkpoint used by the v15 and P4 runs |
| `models/NousResearch-Meta-Llama-3.1-8B-Instruct` | Alternate downloaded Llama repository; do not silently substitute it for the recorded checkpoint |
| `models/Qwen3-8B` | Backbone used by the external MA-RAG intrinsic runs |
| `models/ncbi-MedCPT-Cross-Encoder` | Local MedCPT reranker |

Models are large runtime dependencies and should not be copied into Git
handoffs.

<a id="record-0036"></a>

## 8. Fast start for a new conversation

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1307行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 8. Fast start for a new conversation

1. Read this file.
2. Run `git status --short` in the source tree you will touch. Several project
   trees coexist, and another agent's uncommitted work must be preserved.
3. Decide whether the request concerns the v15 baseline, archived WM study,
   later CF experiments, MA-RAG integration, i-MedRAG/TC-RAG reproduction, or a
   GitHub handoff. For i-MedRAG/TC-RAG, use `$CF_ITERATIVE/PAPER_REPRODUCTION_RECORD.md`
   and the implementation/development entry in section 1; it records actual
   changes and paper-writing evidence without requiring new inference.
4. For the latest expanded classification, read `$CF_CLASSIFIED_FULL/DELIVERY.md` and
   `exports/all_reviewed_target_annotations.jsonl.gz`. For completed v3 evaluation results, read `$CF_BENCH_V3/README.md`,
   `manifest.json`, `units.jsonl` and `results/category_scores.csv`. Use the
   tested read-only loading example in section 1. For a request specifically
   about the full-release comparison, use `$CF_FULL`; the 2026-09-05 handoff
   and `$CF_ADAPTER` describe historical adapter work.
5. For result questions, inspect the existing JSON/CSV output; do not launch a
   model. For weight, threshold, category, or subgroup analysis, reuse saved
   per-item scores and predictions offline.
6. For current baseline code, trace the entry and contract in section 1.
   Section 11 describes historical adapter interfaces.
   Keep upstream MA-RAG external and keep baseline and native-variant outputs
   under distinct method names/directories.
7. Run a new experiment only when the user explicitly requests one. State the
   full cumulative work, remaining ETA, and whether it is core or supplemental
   before starting a multi-hour block.
8. Use a new output/run identity unless explicitly resuming the same frozen run
   after a technical failure. Never overwrite canonical results.

The old shorter rule still applies to the archived WM branch:

1. Decide whether the request concerns the v15 baseline, the WM experiment,
   or the historical `mrg` GitHub handoff.
2. Read only the corresponding authoritative document from section 1.
3. For result questions, inspect the existing summary JSON; do not launch a
   model.
4. For code changes, trace the relevant public interface listed above and
   preserve the canonical v4 artifacts.
5. Run a new experiment only when the user explicitly asks for one; use a new
   output/run identity rather than overwriting recorded results.

<a id="record-0046"></a>

## 12. MA-RAG environment and execution contract

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1641行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 12. MA-RAG environment and execution contract

The external checkout is `/home/data3/txy/MA-RAG` at upstream commit
`423f031cc0ffca679a047c885be999b9604100a9`. The two intentional upstream
runtime changes are stored as reproducible patches in `$CF_ADAPTER`:

- `marag_logging.patch`: preserves detailed per-round candidate and cost logs;
- `marag_retriever_compat.patch`: supports the locally available corpus/index
  layout and MedCorp3 naming.

The checkout also had an untracked local corpus symlink. Do not clean or reset
it without inspecting the exact targets. Do not copy the checkout into
`cf_mrg`.

<a id="record-0047"></a>

## 12.1 Actual main configuration

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1655行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 12.1 Actual main configuration

```text
MA-RAG variant: intrinsic
backbone: local Qwen3-8B
candidate pool N: 8
maximum rounds T: 4
solver thinking: disabled
solver temperature: 0.7
solver max new tokens: 2048
query-generator thinking: enabled
query temperature: 0
query max new tokens: 8192
retrieval: BM25 + MedCPT-Cross-Encoder
corpus: MedCorp3 = PubMed + textbooks + Wikipedia
```

The checked-out MA-RAG script defaults to `T=8`; the experiment explicitly
used `T=4` as the user-approved cost-effective setting. It is not an exact
full-table reproduction. The extrinsic evaluator was not run because its
official checkpoint was unavailable.

The local StatPearls archive was truncated/corrupt: `gzip -t` failed and
`tar -tzf` stopped after 48 members. It was therefore excluded and the corpus
is correctly called **MedCorp3**, never full MedCorp. Do not silently claim
otherwise.

The 100-item original MedQA operational check used N=4/T=2 and returned 72.0%
accuracy. It verified candidate generation, retrieval, round logging, stopping,
and strict-majority evaluation; it is not a paper-table reproduction. A
textbooks-only 76% diagnostic was also observed but is not the official main
check.

<a id="record-0048"></a>

## 12.2 Service layout used

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1688行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 12.2 Service layout used

```text
GPU 0: Llama sidecar during fresh scoring
GPU 1: Qwen3-8B OpenAI-compatible service on port 8011
GPU 2: Qwen3-8B OpenAI-compatible service on port 8012
GPU 3: MedCorp3 BM25/MedCPT retriever on port 8993
```

Qwen service settings were bfloat16, max model length 32,768, max 16 sequences,
GPU memory utilization 0.82, seed 223, and prefix caching enabled. Four
disjoint data shards ran concurrently, two client runners per Qwen endpoint,
with eight client workers each. The Llama sidecar used GPU utilization 0.55.

The base environment eventually contained Transformers 5.16.1, which was
incompatible with vLLM 0.8.5 for this Llama checkpoint. The successful sidecar
run prepended `/home/data3/txy/.cache/marag_pydeps`, which pins Transformers
4.51.3. Reuse the exact command record instead of rediscovering this failure.

All task Qwen/retriever services were stopped after the final push. Ports
8011, 8012, and 8993 had no listeners at handoff. Other users' GPU processes
were deliberately left untouched.

<a id="record-0059"></a>

## 17. Takeover checklist for another agent

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2016行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 17. Takeover checklist for another agent

Current CF state checked on 2026-09-08: remote `main` contains the published
medical CF classification archive at `cfe8246`. It was committed and pushed
from the isolated worktree
`/home/data3/txy/Documents/Codex/2026-09-08/medical_cf_publish`, branch
`publish/medical-cf-five-labels-20260908`. The original `$CF_REPO` local `main`
remains at `d922324`, with its unrelated documentation migration changes
preserved. These are different checkouts of the same repository. Full
M0/M1/M2 model results remain complete in `$CF_FULL`; the later release only
adds collection, classification, audit and offline analysis results.

Historical workspace snapshot from 2026-09-06:

- `cf_mrg` local and remote `main` were both at `1e01b3a`, with a pre-existing
  documentation migration in progress: the old pack `AGENTS.md` was deleted,
  `ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md` was untracked, and the
  two handoff documents had matching link updates. These changes were not made
  or staged by this guide update; preserve and inspect them.
- MA-RAG still had the two expected modified runtime files
  (`ma_rag_entropy.py`, `microservice/RetrievalSystem.py`) and the local
  untracked `corpus` link.
- MedRGAG still had the local reproduction scripts, reports, tests, and runtime
  logs as untracked additions. They are the implementation described in
  section 4, not disposable clutter.
- This guide lives at `/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md`, outside the
  three Git repositories. Updating it does not stage or commit project files.

That status is a dated snapshot, not a reason to assume the trees remain
unchanged. Always inspect them again.

1. Read `/home/data3/txy/AGENTS.md`, then this file.
2. Run `git status --short` in `$CF_REPO`, `/home/data3/txy/MedRGAG`, and
   `$MARAG` before editing. Preserve all unrelated user/agent changes.
3. For expanded classification, read `$CF_CLASSIFIED_FULL/DELIVERY.md`; for
   completed v3 benchmark and M0/M1 results, read
   `$CF_BENCH_V3/README.md`, `manifest.json`, `units.jsonl`, and `results/`;
   follow the read-only loading example in section 1. The medical CF collection
   README, correction/R5 reports and publication receipt describe the source
   annotation archive. `$CF_FULL` describes a separate full-release comparison;
   the 2026-09-05 handoff is historical.
4. Treat archived world-model contracts as history. Do not resume their stages
   or make a world-model claim.
5. Prefer the selected benchmark's existing predictions and score files for analysis.
   The current v3 package is local and untracked. Do not start
   Qwen, Llama, or the retriever to answer a result/status question.
6. If an inference run is explicitly requested, state the total planned
   item-runs, candidate budget, estimated wall time, GPU allocation, and which
   supplemental blocks are opt-in before starting.
7. `$CF_FULL/commands.sh` records prepare/readers/analyze/audit for the full
   comparison. Read its existing artifacts for status questions. Historical
   MA-RAG commands under `$CF_ADAPTER` describe a separate experiment.
8. Keep official MA-RAG baseline behavior and outputs separate from native CF
   variants. Never use gold in a prompt/query/ranking feature, resolve a tie
   with gold, or replace an invalid output with a baseline prediction.
9. Preserve the chosen run's frozen output/parser policy. The full comparison
   used zero format repairs; malformed outputs count wrong and unmapped
   diagnoses are reported separately. Never repair with gold.
10. Before committing, run only checks that could detect a failure introduced
    by the change. Documentation-only changes need link/path checks and diff
    checks, not a multi-hour model run.

Useful read-only commands:

```bash
CF_REPO=/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg
CF_PACK="$CF_REPO/cf_medrgag_validation_pack"
CF_FULL="$CF_PACK/results_cf_full_comparison"

cd "$CF_REPO"
git status --short
git log --oneline -10

wc -l "$CF_FULL/predictions.jsonl"
jq '{status, required_methods, planned_unique_inputs, completed_unique_method_predictions, completion_rate}' "$CF_FULL/metrics.json"
cat "$CF_FULL/validation.json"

/home/data3/txy/MedRGAG/.venv/bin/python -m unittest discover \
  -s "$CF_PACK/tests" -v
```

The last test command is appropriate after relevant code changes. It is not a
prerequisite for reading existing results.

<a id="record-0063"></a>

## v5 实施与复现总记录（2026-09-13）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2168行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v5 实施与复现总记录（2026-09-13）

[五方法评测实施、调整与复现记录](/home/data3/txy/docs/evaluation/v5.md#record-0084)：供论文和后续交接使用，包含配置差异、优化证据、GPU 调度、五方法结果总表、文件索引与复现步骤。仅补充文档，未重启已完成任务。

<a id="record-0064"></a>

## v5 M6/M7 正式输入小批量试跑与上游兼容性修复（2026-09-13）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2172行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v5 M6/M7 正式输入小批量试跑与上游兼容性修复（2026-09-13）

用户新授权先试跑原始M6/M7，使用GPU1/2/3。新包：[results_v5_m6_m7/README.md](/home/data3/txy/docs/evaluation/v5.md#record-0404)。每方法12条（11来源各一条中位长度输入＋全库最长输入），全量27,810方法输入尚未启动。保留前次源码与输出，使用独立副本；没有CF/WM/adapter附加模块。

M7原12条1有效/11无效；补回锁定上游的无动作关键词输出→Final Answer提议处理后9有效/3无效/0运行失败，原sigma1.2与步数条件不变。复用60次LLM请求，新增10次；全部轨迹审计和原生诊断评分已完成。M7已释放GPU3。M6原第一个6条分片已完成，862秒、25.06输入/小时；第二分片长输入仍运行。M6独立修复取消上游没有的查询逐字匹配门槛，并允许解析失败轮次跳过后返回合法最终答案，14项方法测试通过；修复分片自动接续，只复用依赖未变化请求。M7修复亦14项方法测试通过。后续进展以制品为准，勿把本段时间点当作实时状态。

进度：在新包执行 `python3 status.py`。tmux socket `v5-m6-m7`；原始小批量、M6修复接续及自动汇总已安排。完成后生成 `RESULTS.md`、`fixed_pilot_summary.json`、`diagnostics/M6/`、`diagnostics/M7/`；未出现结果文件表示汇总尚未完成，先查日志和进程，不重复启动。方法修复与前后证据同时追加至原 `PAPER_REPRODUCTION_RECORD.md`。

M6/M7小批量后续完成：新包 `RESULTS.md` 和 `fixed_pilot_summary.json` 已生成。修复后M6 11/12有效，M7 9/12有效，均0运行失败；M6新增40次LLM请求、复用222次，M7新增10次、复用60次。全部诊断评分及轨迹审计完成，试跑进程已退出；没有启动全量。M0–M5既有输出有效率核对见新包 `VALIDITY_COMPARISON.md`，采用独立输入去重口径，M1仅有v3结果。

<a id="record-0065"></a>

## v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2182行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）

用户明确授权使用三张卡运行全量。运行包：[/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal/README.md](/home/data3/txy/docs/evaluation/v5.md#record-0407)。每方法13,905独立输入，其中12条修复试跑结果原样复用、13,893条新运行，覆盖6,104单元和13,000入选判断。每方法109个128输入分片（末片不足128）；GPU1/2优先M6，GPU3优先M7，优先方法队列领完后自动领取另一方法。GPU0不动。使用已验证的M6/M7上游兼容性修复，无CF/WM/adapter附加模块，权重、提示、轮数、阈值、检索与阶段预算保持试跑配置。合并方法15项测试及1项调度测试通过。

三个模型已进入真实推理，M7产生首条新有效终态，初始GPU1/2/3利用率约97–98%。tmux socket `v5-m6-m7-full`，会话gpu1/gpu2/gpu3/monitor。在formal目录执行 `python3 status.py`；`logs/supervision.jsonl`每五分钟记录GPU及进度。各分片完成后审计，最后一片触发完整汇总和原生评分，完成标记为formal/complete.json，最终报告为formal/RESULTS.md。健康进程勿重复启动或中断。

耗时估计纠正：先前4–7天偏乐观；按已完成两个M6分片和M7试跑吞吐分配三卡，直接投影约11天。该试跑非代表性且含最长输入，不是完工承诺，后续以全量滚动吞吐更新。

<a id="record-0066"></a>

## v5 M6/M7 提高并发后接续（2026-09-13 06:37）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2190行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v5 M6/M7 提高并发后接续（2026-09-13 06:37）

用户要求提高正式测试的显存利用与吞吐。活动运行改为 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_fast/README.md](/home/data3/txy/docs/evaluation/v5.md#record-0408)，tmux socket `v5-m6-m7-fast`，GPU1/2=M6每卡32线程/128000合批token，GPU3=M7每卡16线程/96000合批token。原 `formal/`三队列已停止，记录和缓存保留，勿重启。方法、权重、提示、预算、阈值及评分不变，执行参数单独覆盖以保留原请求缓存键/随机种子。

相同32条正式请求微基准：M6批量4→32 token吞吐83.47→96.69/s；M7批量4→16为37.81→44.65/s，增到32下降至40.18/s，因此选择不同并发。微基准使用128生成token，不直接当作完整方法加速比。方法与队列16项测试通过。接续已复用旧正式请求并无模型重放完整终态，一致性检查通过。SIGTERM后0.33秒内产生的4个M6人工关闭异常已保存原制品、明确记录并重排同输入，未按答案正确性筛选。新进度06:37 M6=44/13905，M7=70/13905，均无真实运行失败，显存约38.55/43.23/36.64 GiB。

在formal_fast执行 `python3 status.py`。监控与自动审计/全量评分继续，新结果最终写入formal_fast/RESULTS.md。每五分钟向用户报告两方法累计、新计算、剩余及GPU0–3显存/利用率。

<a id="record-0067"></a>

## v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2198行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）

当前活动目录 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/README.md](/home/data3/txy/docs/evaluation/v5.md#record-0409)，tmux socket `v5-m6-m7-balanced`。单纯提高批量在正式混合长度请求上造成大量补齐与长尾等待，实际M6约37–44、M7约10 token/s，不能称全量提速。相同28请求分组微基准40.31→33.16秒、88.91→108.08 token/s；有效输入补齐量减少31%。因此按原生答案类型、生成阶段、token长度2倍区间合批，并把等待池提高至M6每卡64、M7每卡32，token上限保持128000/96000。模型、方法预算和阈值不变；batch_group不进入prompt、缓存键或随机种子。17项测试通过。

接续无模型/检索重放原M6 32条、M7 68条正式终态，输出和状态一致；加上各12条试跑后进度M6=44、M7=80。原成功阶段收据全部保留复用，未完成响应重算。本次先冻结调度器再终止模型，没有产生新的关闭异常。formal与formal_fast为历史目录，勿重启；源结果、先前4条人工关闭异常和递归成本链完整保留。五分钟报告、自动审计和全量评分继续在formal_balanced执行。

<a id="record-0074"></a>

## M4/M6修复实施文档汇总（2026-09-13）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2236行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M4/M6修复实施文档汇总（2026-09-13）

[统一实施与复现记录](/home/data3/txy/docs/evaluation/v5.md#record-0084)已补齐阅读入口及第13节：逐文件修改、280条新增试验输出与52条离线转换的区别、指标分母、无需模型的复核命令、论文措辞和未部署范围。详细证据仍在各试验README及JSON中；本次只整理文档，没有修改预测或运行配置。

<a id="record-0078"></a>

## 最新v5五方法文档与图表同步（2026-09-13）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2260行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 最新v5五方法文档与图表同步（2026-09-13）

[统一benchmark文档](/home/data3/txy/docs/evaluation/v5.md#record-0410)已合并M0/M2/M3/新M4/M5全量结果。只将M4切换为13,905条结构约束修复版，其他方法预测/评分不变。补齐格式/原生有效率、最新分类主图及错误分解PNG/PDF/SVG、完整精度CSV和复现脚本。五方法输入集合一致（各13,905输入、15,616映射），25个方法×类别得分与分解一致，各分解行合计100。ALL为48.10/48.81/51.61/48.20/47.35%；五方法分类均值从低到高R3 21.36、R2 24.30、R1 28.90、R4 47.69、R5 66.73。

旧五方法报告及旧M4图表保留为历史版本并添加新入口；工作区指南、AGENTS、方法结果和实施记录同步。新M4/M5输出协议不同，不能沿用仅骨干不同的描述；旧M4配对统计不适用于新M4。此次只读评分、离线构图，无新增模型请求。M6/M7保持暂停。

<a id="record-0079"></a>

## 近期文档与 GitHub 首页发布完成（2026-09-13）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2266行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 近期文档与 GitHub 首页发布完成（2026-09-13）

已推送至 https://github.com/xiotakut/cf_mrg 的 main，提交 476c6ba7f2c1334ff89e99f6afd1bb8de6ded581。发布目录 benchmarks/2026-09-13_v5_complete，汇集56份来源文档、584份来源制品，包含修复M4全量结果、最新五方法图表、M0/M2/M3/M4/M5正式评测、M4/M6修复试验、M7暂停诊断、GPU调度和吞吐观察、构建记录及论文贡献边界。根README已重做，旧首页保留README_HISTORY.md。

发布验证：30个方法×类别分数从单元CSV重算一致，25行错误分解和5方法有效率一致，584个本地Markdown链接可解析；未调用模型或操作运行进程。完整原始响应、数据正文、权重和大型缓存继续留本地，逐文件源位置和未上传引用已列CSV。GitHub发布工作区：/home/data3/txy/Documents/Codex/2026-09-13/v5_github_publish。复核命令：python3 benchmarks/2026-09-13_v5_complete/check_publication.py。

<a id="record-0080"></a>

## M6/M7与新M4吞吐差异诊断（2026-09-13）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2272行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M6/M7与新M4吞吐差异诊断（2026-09-13）

[完整诊断与复核脚本](/home/data3/txy/docs/workspace.md#record-0213)。离线读取M4全13,905结果、M7十个无前缀复用的完整128题分片、M6的40个完成输入及两片新阶段。M4约3,869.88题/GPU小时；M7六个32路分片94.81、四个64路73.69。M7每题6.20次生成/753输出tokens，有效引擎吞吐20.03tokens/s；M4一次/312tokens/348.47tokens/s。M6完成样本平均21.93调用、7,779输出tokens，不作全库外推。

主要实现问题：HF静态整批返回造成长尾，答案类型/阶段/长度分桶使实际batch仅2.92或4.30，逐token全词表熵回传CPU和逐请求采样循环有额外同步/调度开销。熵没有额外模型forward；具体熵开销比例尚未profile。vLLM0.8.5 V1普通top-k/温度前logprobs不能替代TC-RAG温度后全词表熵。建议M6先迁移常驻连续调度；M7先验证熵轨迹GPU缓冲再做正确熵hook与连续调度。此次仅诊断，未改活动推理代码、无新模型请求，M6/M7保持暂停。

<a id="record-0081"></a>

## M6/M7 vLLM 优化验证（2026-09-13 20:00，完成）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2278行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M6/M7 vLLM 优化验证（2026-09-13 20:00，完成）

用户授权尝试优化，实施保存在 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/README.md](/home/data3/txy/docs/baselines/tcrag.md#record-0221)。独立验证包使用既有 vLLM0.8.5 V0 连续调度；方法代码、模型、检索、提示和预算保持，M7 使用温度后 FP32 全词表熵及原后缀/阈值。HF 仅缓冲熵回传微测约1%收益；真正的连续调度 M7 同32题完整流程1,725.73→110.74秒（15.58倍），原生有效14/32→19/32，两边0运行失败。扩大128题369.93秒、81协议有效/54原生有效/0失败；833次生成轨迹审计通过。跨引擎轨迹不同，不声称token等价或纯内核因果加速。

M6同128题以70%显存预留从头运行已完成：2,069.41秒（34分29秒），222.67题/GPU小时，102协议有效/87原v5格式有效/78原生有效，0运行失败；2,810次生成、1,026,610输出tokens，512轮历史回写、1,525次有序检索QA、128次最终历史审计全部通过。M6没有同输入旧HF完整对照，不报告其加速倍数。初次85%预留OOM试验472.77秒及570条完成生成收据独立保留，未复用到重跑。18项测试及真实sampler全词表熵验证通过（146位置，最大差1.31e-6）。

本次四项完整验证均0运行失败、无LLM阶段复用；原生无效仍保留分母。后续M6/M7默认显存预留均70%，实际vLLM每步prefill上限16384，最大并行序列128，建议命令M6 workers128、M7 workers64。方法文件与原balanced逐字节一致，没有加入额外模块或formatter修复。GPU1/2/3已20:00释放，GPU0未操作。原formal_balanced的M6 52条、M7 1,646条及暂停队列保持，没有恢复全量或合入试验输出。完整结果、复现命令和限制见本包README及reports/full_method_results.json。

<a id="record-0092"></a>

## 3. 方法设置：哪些属于实验定义

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第74行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 3. 方法设置：哪些属于实验定义

<a id="record-0095"></a>

## 3.3 上下文与推理后端

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第101行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 3.3 上下文与推理后端

M4/M5 从安装验证用的 Transformers 路径转为本机 vLLM 0.8.5 批量推理，BF16，启用 prefix caching；复用现有 Transformers 4.51.3 环境。后端或批处理调度变化不保证逐 token 输出一致。

M5 存在超过 32K 的完整原生输入（已记录最长 69,721 token）。运行脚本将 M4/M5 的实际 `max_length` 覆盖为 **131,072**，M5 加入静态 YaRN factor=4、original context=32,768。**M5 JSON 文件仍写着 32,768，不能只复制该 JSON 来声称复现了运行上下文。** 实际依据为[运行脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/run_medrag.py)。M4 上下文也是 131,072。追加检索片段最多 30,000 个各自模型 token；原题要求的固定证据不裁剪，完整阶段溢出时报错。

<a id="record-0097"></a>

## 4. 工程调整与性能证据

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第130行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 4. 工程调整与性能证据

<a id="record-0102"></a>

## 4.5 未采用的提速方案与参考来源

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第183行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 4.5 未采用的提速方案与参考来源

曾核对 [MA-RAG 官方仓库](https://github.com/NJU-RL/MA-RAG)、[官方服务脚本](https://github.com/NJU-RL/MA-RAG/blob/main/scripts/vllm_qwen3_8b.sh)和[论文](https://arxiv.org/html/2603.03292v1)。此前调查记录指出论文 Appendix G 讨论多轮推理成本；官方示例的并发容量不是本机最终配置。本次保留先前已验证的本地 max-num-seqs=32，而不是直接复制示例 16。

未实施：减少 N/T、截短完整必需证据、降低 query 预算、减少历史或查询多样性、把 intrinsic 换成 extrinsic verifier、修改检索服务批等待或重排批结构。论文引用的精确章节/版本应在投稿时重新核对；本地复现的代码版本依据配置中的 commit。

<a id="record-0110"></a>

## 7. 修改与证据的文件索引

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第268行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 7. 修改与证据的文件索引

以下是本次工作涉及的主要文件及作用，不代表这些文件的每一行均由本次新写。原有实现、续测新增实现和运行配置共同决定最终行为。

| 文件或位置 | 本次调整 / 用途 | 核查入口 |
|---|---|---|
| [M4 配置](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/configs/m4.json)、[M5 配置](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/configs/m5.json) | M4 检索、语料、k、温度与上下文预算向本次 M5 方案对齐；骨干保留各自模型 | [配置变更审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_configuration_change.json)；有效运行参数还需结合启动代码 |
| [run_medrag.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/run_medrag.py) | 统一正式输入构造、原生回答输出及运行时长上下文配置 | [prompt 验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/medrag_prompt_validation.json) |
| MedCorp PubMed 对应的行偏移文件 | 补齐已有随机读取机制需要的 offset 数据，避免逐命中整片扫描 | [全量 offset 验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/pubmed_offsets_full_validation.json)、[输入等价验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m5_input_equivalence_validation.json) |
| [M4 GPU0 guard](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/run_m4_gpu0_guard.py) | 保护其他用户进程；供 M3 调用时支持显式最小空闲显存参数，默认仍为 25 GiB | [M3 4 GiB guard 验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu0_guard_validation_4gib.json) |
| [M4 并行协调](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/run_m4_parallel.py) | 基于已有完成结果切分剩余输入、锁与汇合审计 | [四方法覆盖审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/artifact_audit.json) |
| [M3 prepare.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/prepare.py)、[prepare_v5.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/prepare_v5.py) | 对齐 v5 输入、建立严格复用与剩余任务清单 | [复用审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/reuse_audit.json)、[计划](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/plan.json) |
| [M3 run_m3.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/run_m3.py) | 原生任务适配、完整 intrinsic 流程、阶段缓存、断点恢复与耗时记录 | [正式样本 smoke 审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/smoke_audit.json)、逐题 cache |
| [response_processing.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/response_processing.py)、[check_response_processing.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/check_response_processing.py) | 向量化熵计算、保留不规则长度回退、比较旧新解析结果 | [真实响应验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/response_processing_validation.json)、[微基准](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/entropy_microbenchmark.json) |
| [parallel_gpu0.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/parallel_gpu0.py)、[parallel_gpu3.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/parallel_gpu3.py)、[resume_6_gpu2.sh](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/resume_6_gpu2.sh) | 现有分片交接、GPU0 扩容与退出、利用空闲 GPU 接续 | [GPU0 事件流](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu0_parallel_events.jsonl)、[GPU3 交接](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu3_handoff.json) |
| [finish.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/finish.py)、[status.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/status.py) | 最终汇合、完整性检查、状态统计和自身资源释放 | [最终审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/artifact_audit.json)、[检索器清理](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/retriever_cleanup.json) |
| [四方法分析](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/code/analyze_v5.py)、[M3 分析](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/analyze_v5.py) | 冻结原生评分、单元/来源聚合、结果表输出 | 两个结果目录的 validation.json、category_scores.csv、unit_scores.csv |
| 本文、各结果 README / RESULTS、工作区指南 | 汇总过程与最终结果；保留历史日志，避免将中间状态当最终状态 | 本文中的原始证据链接 |

M3 原始候选回复、query、prompt、检索结果、阶段耗时及最终逐题结果保存在 `results_v5_m3/cache/items/<item_id>/`；完整预测、复用预测与新增预测分别保存在 `m3_predictions.jsonl`、`cache/reused.jsonl`、`M3/predictions.jsonl`。抽查模型回复应查看原始阶段缓存，而不是把评分用的序列化 `raw_response` 当作完整模型输出。

<a id="record-0143"></a>

## 17. 近期记录归档与 GitHub README 更新（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第678行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 17. 近期记录归档与 GitHub README 更新（2026-09-13）

本节补充文档整理与发布操作，继续沿用本实施记录作为总账。已有专题 README 保存详细证据，后续实际调整仍更新本文，不以新的独立总记录替代。

<a id="record-0144"></a>

## 17.1 本轮实际完成的工作

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第682行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 17.1 本轮实际完成的工作

| 对象 | 调整前 | 具体调整与原因 |
|---|---|---|
| 近期记录收集 | 文档散布在数据构建、M4/M5 安装、正式评测、M6/M7 复现等工作区 | 汇集 09-09 至 09-13 的 56 份来源文档及配套文件，共 584 份来源制品；保留具体配置、失败尝试、验证证据和方法版本，方便论文追溯 |
| 当前结果入口 | GitHub 首页仍以 09-07 的完整测试及早期 CF adapter 实验为主 | 改为 M0/M2/M3/修复 M4/M5 的完整 v5 表格和图；展示 13,905 输入、15,616 映射、6,104 单元、13,000 判断及指标含义 |
| 本实施记录的状态说明 | 开头仍有 M4 仅完成 100 题试验、尚未替换正式比较的描述 | 更新为修复 M4 已完成全量，并将第 1 节标明为原 M4 阶段历史结果；保留第 11 节试验和后续全量记录，避免混用版本 |
| README 阅读导航 | 数据、方法、修复、资源调度与论文讨论入口分散 | 按用途增加最新结果、构建定义、安装配置、性能分析、有效率诊断、论文复现及历史归档链接；列明 M6/M7 暂停与 M6 候选补丁未部署 |
| 文档路径 | 部分 Markdown 链接指向服务器绝对路径，GitHub 无法直接访问 | 已归档目标改为仓库相对链接；未上传的原始制品保留本地路径说明，集中列入 LOCAL_ARTIFACT_REFERENCES.csv |
| 历史版本 | 原首页包含早期独立协议结果 | 原首页完整保留为 README_HISTORY.md；原 M4 图表、配置、评分及试验独立保留，新的首页不把历史 CF/WM 结果并入 v5 |
| 来源与复现 | 各文档原始位置需要人工追溯 | SOURCE_MANIFEST.csv 逐文件记录源路径与源文件字节数；配置、实现快照、补丁、审计收据及 PNG/PDF/SVG 一并归档 |
| 发布核验 | 缺少能在公开仓库独立运行的归档一致性检查 | 增加标准库 check_publication.py，仅读取已发布的 CSV/JSON/Markdown，核对分数、分母、完成收据和本地链接，无模型依赖 |

<a id="record-0145"></a>

## 17.2 发布范围、验证及提交

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第695行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 17.2 发布范围、验证及提交

发布到 `xiotakut/cf_mrg` 的 `main`，主发布提交为 `476c6ba7f2c1334ff89e99f6afd1bb8de6ded581`。目录为 `benchmarks/2026-09-13_v5_complete/`，根 `README.md` 和 `benchmarks/README.md` 同步更新。使用基于远端 `c71581f` 的独立工作区整理，常规推送后核对远端 main 提交和 README 已更新。

本轮验证通过：

- 从已发布单元 CSV 重新汇总五方法 × 六类别（含 ALL）的 30 个分数，与最新表格一致；各类别单元数一致，组内单元无重复。
- 25 行方法×类别错误分解与准确率一致，行内合计 100%；五方法有效率的计数、13,905 输入和 15,616 映射分母一致。
- 新 M4 完成收据中的零缺失、零重复及格式/原生有效数与表格一致。
- 首次发布核对 61 份 Markdown 中 584 个本地目标链接；主图已目视检查。后续链接数量以 publication_validation.json 为准。
- 待发布文本的凭据模式及 JSON 凭据字段扫描未发现非占位凭据；本次编写的页面与验证脚本通过差异空白检查。历史 CSV/SVG 和源码快照保留其原格式。

复核命令（仓库根目录）：

```bash
python3 benchmarks/2026-09-13_v5_complete/check_publication.py
```

该检查复核公开表格和已归档完成证据，不重新审计未上传的完整逐题缓存。全文推理、历史绘图脚本仍需原环境路径、依赖与本地数据；不能将归档脚本描述为下载仓库后即可全量运行的环境。

<a id="record-0146"></a>

## 17.3 对实验与论文的影响

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第715行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 17.3 对实验与论文的影响

本轮是文档和研究制品整理，没有新增模型请求、修改标签或原生评分器、覆盖正式预测，也没有启动、停止或迁移 GPU 进程。M4 全量修复和最新图表是本轮核实并收集的既有成果，其实际实验调整见前文对应记录，不计为本轮新增计算。

原始 benchmark 正文、全部逐题响应、模型权重、密集索引和大型请求缓存继续保留于服务器；发布文档提供来源和恢复位置。文档明示不同有效率分母、新 M4/M5 输出协议差异、v5 方案选择与独立验证的区别，以及工程优化与研究候选的贡献边界。这些整理用于论文 Methods、实现附录和可复现性说明，本身不构成新的实验结果或算法贡献。

<a id="record-0174"></a>

## PAPER_REPRODUCTION_RECORD.md

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

### M6 i-MedRAG 与 M7 TC-RAG：实现、调整及论文写作记录

**最新全量完成（2026-09-14 11:48）：新版M6 MedGENIE v2全量13,905输入和15,616原生评分映射完成；全部新生成，0运行失败/重试/阶段复用，109分片、83,430次真实生成轨迹检查通过。协议97.45%、格式96.49%、原生有效77.32%，ALL原生准确率48.02%。推理含初始化2小时41分46秒，GPU0/1/3本轮模型已正常退出。[最终结果及七方法图](/home/data3/txy/docs/baselines/medgenie.md#record-0399)；详见[本轮记录](/home/data3/txy/docs/baselines/medgenie.md#record-0232)。**

**最新试跑完成（2026-09-14 09:00）：用户指定新版M6 MedGENIE，384题全新生成、0复用/运行失败/重试，GPU0/1/3均已释放本轮模型。协议96.61%、格式95.31%、原生有效74.74%；含启动5分19秒。412条原生评分映射、384条流程及2304次生成审计通过。[结果](/home/data3/txy/docs/baselines/medgenie.md#record-0397)；详见[本次主记录](/home/data3/txy/docs/baselines/medgenie.md#record-0231)。旧i-MedRAG保持历史身份，正式13905题MedGENIE全量未启动。**

**此前开发完成状态（2026-09-14）：MedGENIE四来源核查、Llama3.1/v5适配实现及小规模运行已完成。24题开发JSON有效24/24（MedQA 11/12正确；诊断12/12未通过现有canonical匹配）；多选/关系/鲁棒性各1题的独立接口复验3/3合法。原生诊断效果仍有限制，未启动13905题全量；旧M6结果保留。完整配置、失败尝试及证据见文末MedGENIE段。**

**历史状态（2026-09-13）：正式全量队列仍暂停，M6保存52条、M7保存1,646条。独立vLLM优化验证已完成：M7同32题1,725.73→110.74秒；M6首次128题85%显存预留OOM，降至70%后同128题重跑完成；M7扩大128题也完成。详见[第10节诊断](/home/data3/txy/docs/workspace.md#record-0213)和[第11节实现、失败与结果](/home/data3/txy/docs/baselines/tcrag.md#record-0221)。这些验证不是13,905题全量结果。**

2026-09-13将吞吐诊断及优化验证两份独立正文合入本文，旧路径保留入口。第1–9节及其开发Methods草稿描述24题开发阶段，后续带日期记录覆盖正式启动、暂停和优化；历史“未启动正式评测”不代表最新状态。格式候选试验仍由[评测实施主记录](/home/data3/txy/docs/evaluation/v5.md#record-0084)第12、14、18–19节维护，本文引用其结果，不重复维护方案细节。

更新日期：2026-09-13（Asia/Shanghai）。本文根据已保存的源码快照、配置、请求收据、运行日志和离线报告整理本轮实际工作，供论文 Methods、Implementation Details、实验记录和局限性部分使用。后续修改继续追加日期、改动原因及对应制品，不覆盖本次记录。

**编号约定（用户2026-09-13指定）：M6 = i-MedRAG（`imedrag`），M7 = TC-RAG（`tcrag`）。** 本轮R1–R5比较和后续论文使用这两个编号；代码、配置及历史制品继续使用括号中的执行标识。旧MedRGAG消融及Gate D实验中的同名编号保留其历史实验含义。

**初始开发阶段结论：两种方法已接入现有项目，通过19项自动测试，并分别完成24条固定开发输入的真实模型运行及轨迹审计。i-MedRAG有19条有效、5条无效；TC-RAG有9条有效、15条无效。输出格式和开放诊断评分兼容性仍有问题，尚未完成全部来源的真实验收及正式评测。**

新增方法只有 `imedrag`、`tcrag`。M20＝MedCounterFact、M22＝MedRGB、M23＝BioRAB是项目原有的**数据来源编号**，出现在输入适配和评分记录中，不是新增方法。没有新增 CF 方法、CF adapter、专项 verifier 或更强的辅助模型。用户所述论文的7个医疗QA benchmark属于来源论文设置；本次继续使用服务器已确认的 R1–R5 v5，没有重新选择 benchmark。

<a id="record-0175"></a>

## 1. 实际完成的工作及代码位置

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第21行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 1. 实际完成的工作及代码位置

服务器运行包位于本文件所在目录；项目入口为 [run_iterative_baselines.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/run_iterative_baselines.py)。入口用 `runpy` 调用本运行包，支持 `CF_ITERATIVE_BASELINES` 指定部署位置。沿用已有 dated-run-pack 组织方式。

| 工作 | 实际实现 / 复用内容 | 证据入口 |
|---|---|---|
| 来源固定 | 阅读原论文及官方实现，记录版本、SHA、许可证和论文/代码差异 | [method_fidelity.md](/home/data3/txy/docs/workspace.md#record-0374)、[source_resolution.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/source_resolution.json)、`upstream/` |
| i-MedRAG | 4轮追问、逐问检索和回答、跨轮QA历史、最终分析与格式化；安全解析和确定顺序 | [methods.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/methods.py)：`imedrag`、`parse_queries`、`final_json` |
| TC-RAG | 独立活动栈、真实工具、Backtrack、Summary替换、状态监控、接受及步数终止 | [methods.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/methods.py)：`tcrag`、`parse_action`、`state_signal` |
| 同权重生成和熵 | 增加 Transformers 后端，生成时计算完整分布熵；请求合批和独立随机数流 | [backend.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/backend.py)：`HFBackend`、`BatchingBackend`、`entropy_from_scores` |
| 检索接入 | `Retriever` 调用已有 MedRAG `src.baselines.make_retriever`；复用完整MedCorp、BM25及MedCPT | [backend.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/backend.py)、[resources.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/resources.json) |
| 输入和资源冻结 | 接入已有v5物化输入，保留source→unit→target→input展开映射；固定开发包、模型、索引和环境身份 | [prepare.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/prepare.py)、[check.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/check.py)、[input_lock.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_lock.json) |
| 请求与恢复 | 保存完整prompt、原始响应、finish_reason、真实检索材料、尝试和终态；原子写入、请求级恢复和配置漂移拒绝 | [runtime.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/runtime.py)、[run.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/run.py) |
| 评分、审计和成本 | 接入已有原生评分器；离线重算历史、栈和熵；分别统计逻辑请求、新增计算、缓存及正式成本 | [score.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/score.py)、[report.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/report.py)、[cost.py](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/code/cost.py) |
| 执行入口和验证 | 环境准备、开发运行、恢复、离线评分及验收命令；19项隔离回放测试 | [run.sh](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/run.sh)、[acceptance.sh](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance.sh)、[tests/](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/tests)、[README.md](/home/data3/txy/docs/workspace.md#record-0387) |

已有模型权重、MedRAG环境、语料、索引和重排序器直接复用；本轮没有训练模型或重新建设完整知识库。实际生成使用既有 MedRAG 基线环境：Python 3.10.12、torch 2.6.0、Transformers 4.51.3、accelerate 1.10.1、pyserini 1.0.0、Java 21；数据准备复用另一个已有环境。完整版本和路径见 [environment.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/environment.json)、[requirements.lock.txt](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/requirements.lock.txt)。

<a id="record-0176"></a>

## 2. 固定来源与最终配置

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第39行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 2. 固定来源与最终配置

<a id="record-0177"></a>

## 2.1 方法依据

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第41行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2.1 方法依据

| 方法 | 原论文版本 | 官方仓库固定提交 | 许可证记录 |
|---|---|---|---|
| i-MedRAG | [2408.00727v3](https://arxiv.org/html/2408.00727v3)，2024-10-11，§3.2–3.3、Algorithm 1 | [gzxiong/MedRAG](https://github.com/gzxiong/MedRAG/tree/7599a728a28789fd601728c08d313b1148051f41)，`7599a728a28789fd601728c08d313b1148051f41` | NCBI US Government Work公有领域声明；GitHub API为NOASSERTION，不写成MIT |
| TC-RAG | [2408.09199v3](https://arxiv.org/html/2408.09199v3)，2026-09-03，§5、Appendix 8.6 Algorithm 1 | [Artessay/TC-RAG](https://github.com/Artessay/TC-RAG/tree/dd8f32f90832eeb452680cfdb02ca604988648d0)，`dd8f32f90832eeb452680cfdb02ca604988648d0` | checkout没有LICENSE、API为null；参考源码独立适配，不替上游声明授权 |

i-MedRAG论文中的作者仓库用户名与定位链接不同；本次API实际解析为 `gzxiong/MedRAG`，原始和resolved URL均已记录。引用代码时使用上表固定SHA。逐组件上游函数和本地函数对应关系以 [method_fidelity.md](/home/data3/txy/docs/workspace.md#record-0374) 为准。

<a id="record-0178"></a>

## 2.2 最终执行参数及来源

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第50行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2.2 最终执行参数及来源

最终配置为 [imedrag_runtime_v4.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/imedrag_runtime_v4.json)、[tcrag_runtime_v4.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/tcrag_runtime_v4.json)，`method_version=iterative-v4`。部分后续语法修复仍沿用这个版本字符串，因此论文制品身份还应引用各run的 `resolved_config.json`、`code_snapshot/` 和其中的源码哈希，不能只写“v4”。

| 条件 | 最终值 | 来源 / 说明 |
|---|---|---|
| i-MedRAG backbone | `meta-llama/Llama-3.1-8B-Instruct` | 当前项目M4设置；追问、解析、QA和最终格式化使用同一模型 |
| TC-RAG backbone | `Qwen/Qwen3-8B`，`enable_thinking=false` | 用户明确指定；Adaptive RAG baseline，状态也来自该模型 |
| i-MedRAG轮数 | `n_rounds=4`、每轮请求 `n_queries=3` | 官方函数/README默认；实际数由模型及解析结果决定 |
| TC-RAG控制 | `max_loop=8`、`topK=4`、`sigma=1.2`、初值100000 | 固定官方执行器；topK不是检索条数；最早第5次动作生成接受 |
| 模型精度/引擎 | BF16、Transformers、SDPA | 本地同权重执行后端；权重与tokenizer身份见 [resources.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/resources.json) |
| 采样 | temperature=0.7、top_p=1、top_k=0、repetition_penalty=1、num_beams=1、seed=42 | 当前v5生成设置及后端固定参数；请求种子独立记录 |
| 模型窗口 | 131072 tokens；Qwen YaRN factor=4、original=32768 | 沿用当前M4/M5上下文配置 |
| 知识库和检索 | 完整MedCorp四库；BM25每库32，k1=0.9、b=0.4；MedCPT-Cross-Encoder重排top8 | 复用当前v5统一检索设置及已有索引；配置遗留 `rrf_k=100` 不参与本BM25＋MedCPT路径 |
| 追加证据预算 | 30000模型tokens | 当前v5追加检索上下文预算；原题及必需证据保留 |
| 阶段生成预算 | query/parse/QA各1024；final/format/TC action各2048 | 本项目分阶段工程配置，不写成两论文共同默认 |
| 请求重试 | 最多2次传输重试，退避1/2秒 | 本项目规则；OOM不当作传输重试 |
| 格式处理 | 查询提取最多1次同模型纯格式修复；最终最多1次确定性字面量转JSON | 本项目接口修复，完整记录原始输出与额外调用 |
| 并发和显存 | 4个输入工作线程，合批上限32000 padded tokens，`expandable_segments:True` | 真实共享GPU下的OOM修复；单个合法长请求仍完整执行 |
| 设备分层 | 实测用物理GPU1/2；Llama层12/20，Qwen层14/22 | 按共享显存余量分配；不是量化或更换小模型 |

TC论文附录另有 `uct=20 / cppl=10`、temperature=0.6、500 tokens等设置；本实现选择已核对的代码默认阈值和本项目统一生成配置，并在差异表披露，没有混用成所谓“论文原配置”。

<a id="record-0179"></a>

## 3. 对方法具体做了什么调整

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第73行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 3. 对方法具体做了什么调整

<a id="record-0183"></a>

## 4. 实际试跑、修复和复验顺序

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第128行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 4. 实际试跑、修复和复验顺序

以下目录及失败制品均保留。目录后缀是操作顺序标记，不能代替其resolved配置和源码快照。v1/v2/v3的配置仍写 `iterative-v1`；v4及之后写 `iterative-v4`。

| 顺序 / run目录（均在 `runs/`） | 当时完成情况 | 对应处理 | 新增有输出LLM请求，不含参考对照 |
|---|---|---|---:|
| `imedrag_dev_v1` | 未完成，保存1条终态 | 收紧查询完整边界；从逐输入串行改为输入并发及后端合批 | 29 |
| `imedrag_dev_v2` | 未完成，无完整输入终态；另有startup OOM日志 | 支持实际Markdown语法；将请求随机种子/缓存身份与运行目录分离 | 20 |
| `imedrag_dev_v3` | 未完成，保存1条failed终态及OOM尝试 | 真实共享显存不足，调整层分配、合批上限和分配器 | 59 |
| `imedrag_dev_v4` | 首次24条完整终态：7 ok / 17 invalid / 0 failed | 使用显存修复、单QA收据和有序回填；成为完整真实生成时间来源 | 509 |
| `imedrag_dev` | 24条：11 ok / 13 invalid | 扩展实际查询语法包装；试改flat JSON最终提示；只重算受影响依赖及格式化 | 60 |
| `imedrag_dev_final` | 24条：2 ok / 22 invalid | 恢复官方最终格式化提示；所有24条重新执行格式化 | 24 |
| `imedrag_dev_accepted` | 24条：19 ok / 5 invalid | 用同一规则重放全部真实收据；只加完整字典字面量→JSON语法转换 | 0 |
| `tcrag_dev` | 24条：9 ok / 15 invalid | 最终源码下的一次完整真实开发运行；sigma固定1.2 | 144 |

`accepted`是目录名，不表示所有验收项通过。上表是不同工程版本的开发记录，不能当作受控算法消融或独立测试集成绩。

<a id="record-0184"></a>

## 4.1 并发、随机数和显存修复的具体变化

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第145行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 4.1 并发、随机数和显存修复的具体变化

v1→v2新增4输入工作线程和 `BatchingBackend`，初始上限60000 padded tokens。各阶段随机数流独立，避免不同输入因合批共用一个抽样流。v2→v3使请求身份和种子不再受 `run_id`、`code_hashes`、`inputs_hash`、`input_path`、`physical_gpu_selection` 等运行位置元数据影响；模型、tokenizer、完整prompt、证据、角色、生成参数和方法语义配置仍参与身份。run级完整配置和源码仍锁定，改变后拒绝续写同一run。

v3→v4把合批上限60000改为32000，启用可扩展显存分配器，Llama由16/16层调整为12/20，Qwen采用14/22层；每条QA独立收据并按序写回，拆分大批次时继续使用各序列自己的随机数流。单个合法长输入不会按合批上限截短。后续又在加载模型前增加worker数漂移拒绝检查。

这些修改解决实际OOM、调度及恢复问题，未减少4轮追问、8步上限、检索条数、输入范围或阶段输出预算。小模型固定响应/采样测试检查单独与合批token序列一致；BF16在不同硬件和张量形状下仍可能产生数值差异。

<a id="record-0186"></a>

## 4.3 曾准备但未执行的工作

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第161行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 4.3 曾准备但未执行的工作

早期准备过15条正式输入盲检查清单和一个有限TC阈值计划（1.2、5、10、20）。用户要求专注两方法复现后，撤下额外队列并保留历史文件；未启动盲测、校准或整套正式推理。依据为 [scope_correction.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/scope_correction.json)、[unused_tcrag_calibration_plan.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/unused_tcrag_calibration_plan.json)、[acceptance_execution_complete.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/acceptance_execution_complete.json)。`data/blind*.jsonl`及暴露说明是未执行准备记录，不是新增实验结果。

<a id="record-0192"></a>

## 6. 验证证据和最终真实开发结果

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第197行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 6. 验证证据和最终真实开发结果

<a id="record-0193"></a>

## 6.1 自动测试与轨迹审计

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第199行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 6.1 自动测试与轨迹审计

[tests_final_syntax.log](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/tests_final_syntax.log)记录19项自动测试通过：i-MedRAG跨轮QA历史、查询语法和并发顺序；TC工具/回退/总结/过早结论/合格结论/耗尽；FP32熵公式与特殊token位置；样本隔离、gold哨兵、证据差异和缓存；请求与终态恢复、配置漂移拒绝；原生格式、失败分母和复用成本。固定响应均隔离在tests，未进入真实benchmark。

真实审计核对i-MedRAG的521次模型身份、96轮前后历史、279次QA及24次最终历史；TC核对144次prompt/活动栈、97次熵重算、44次接受边界、3次Summary移除/状态恢复及3次耗尽。结果见 [i-MedRAG执行审计](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/execution_report.json)、[TC-RAG执行审计](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/execution_report.json)。

<a id="record-0194"></a>

## 6.2 最终终态及方法运行量

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第205行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 6.2 最终终态及方法运行量

| 指标 | M6 i-MedRAG | M7 TC-RAG |
|---|---:|---:|
| 计划 / 终态 | 24 / 24 | 24 / 24 |
| ok / invalid / failed / pending | 19 / 5 / 0 / 0 | 9 / 15 / 0 / 0 |
| 运行有效率 | 79.17% | 37.50% |
| 未知ID / 正式重复 | 0 / 0 | 0 / 0 |
| 实际轮次 / 动作数 | 每题4轮，共96轮 | 平均6步，范围3–8，中位6 |
| 逻辑LLM请求 | 521 | 144 |
| 输入 / 生成tokens | 1093381 / 169363 | 354715 / 18918 |
| 检索请求 | 279 | 40（34后端、6同查询缓存） |
| 自然Summary / Backtrack | 不适用 | 3 / 0 |
| 输出截断 / 传输重试 / 无命中 | 均0 | 均0 |
| 预算耗尽 | 0 | 3，12.5% |

i-MedRAG实际279条查询均逐条检索和作答，单题6–15条，不保证每轮恰好3条。5条invalid中，3条涉及追问提取问题、3条涉及最终格式问题，交集1条。TC的15条invalid包括12条动作解析失败（9条缺动作标签、3条空Thought）和3条预算耗尽。真实模型未自然触发Backtrack，其行为由固定响应测试核对，未为增加动作率强迫回退。

TC的44次Final Answer提议中，17次因步数过早拒绝、18次因熵拒绝、9次接受。97次状态值中位数22.38、p95=60.04、范围0.0121–109.88。阈值始终为1.2，没有根据这些开发结果重新选阈值。

<a id="record-0195"></a>

## 6.3 按来源的完整分母评分

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第225行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 6.3 按来源的完整分母评分

| 来源 / split | 方法 | 运行有效 / 计划 | 当前既定评分器正确 / 计划 |
|---|---|---:|---:|
| MedQA validation | i-MedRAG | 11 / 12 | 11 / 12 |
| MedEinst train | i-MedRAG | 8 / 12 | 0 / 12 |
| MedQA validation | TC-RAG | 3 / 12 | 2 / 12 |
| MedEinst train | TC-RAG | 6 / 12 | 0 / 12 |

i-MedRAG的8条运行有效诊断中，6条嵌套结构字符串被旧解析器拒绝、1条未映射、1条歧义；TC的6条运行有效诊断均未进入既定canonical映射。这里的0/12不等于医学语义准确率为0。两个阶段的有效性及错误保留在 [i-MedRAG评分](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/scores/summary.json)、[TC-RAG评分](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/scores/summary.json)，未基于gold改词或修改映射。

<a id="record-0196"></a>

## 7. 已发生的计算成本及正式成本估算

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第236行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 7. 已发生的计算成本及正式成本估算

<a id="record-0197"></a>

## 7.1 开发累计新增计算

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第238行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 7.1 开发累计新增计算

[formal_cost_estimate.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/formal_cost_estimate.json)分别保存失败pilot、缓存来源运行、最终新增计算及参考对照。成本脚本曾只匹配 `superseded.json` 而漏掉v1/v2的 `superseded_development_pilot.json`；已改为识别 `superseded*.json` 并重算。这是成本清单修复，不影响预测或评分。

按这些互不重复的新增计算组汇总：**845个有输出的实际LLM请求＋10个后端参考请求＝855个请求**；输入tokens为1929371＋394＝1929765，生成tokens为231389＋206＝231595。406份新增检索收据含同查询缓存，不能写成406次访问检索后端。中断后没有输出的生成，其未知token不作猜测；这些数字是已保存收据能证明的累计量，不是包括所有启动失败开销的精确资源账单。

最终两方法24条制品的逻辑请求数为521＋144＝665，不等于开发累计855个真实请求。i-MedRAG最终目录复用800份收据后耗时1.60秒，不能当作模型推理速度。

| 实测时间 / 调度指标 | i-MedRAG完整真实来源运行 `imedrag_dev_v4` | TC-RAG `tcrag_dev` |
|---|---:|---:|
| 24条wall time | 11914秒，3.31小时 | 2792秒，46.53分钟 |
| 共享GPU输入吞吐 | 7.25输入/小时 | 30.95输入/小时 |
| 单题延迟p50 / p95 | 1875 / 2401秒 | 476 / 787秒 |
| 合批行数中位 / 最大 | 4 / 10 | 3 / 4 |

i-MedRAG后续接口复验另用约1057秒和241秒，产生60＋24次新模型调用；纯语法重放不增加生成。最终i制品中的物理batch ID来自不同来源阶段，不宜当作一次冷运行的批处理测量。TC的144个逻辑请求对应49个物理生成批次。吞吐均包含无效及提前解析失败的输入，不表示相同有效输出质量下的效率。

<a id="record-0198"></a>

## 7.2 正式规模及尚不能估出的部分

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第255行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 7.2 正式规模及尚不能估出的部分

每方法正式计划13905个唯一输入。i-MedRAG标准恰好12条QA且无重试的情景为305910个LLM请求、166860次检索；TC最多111240个动作请求，所有输入最早第5步接受的情景为69525个。重试另计，不能把13000个判断直接当调用数。

| 方法 | ≤1024必需输入tokens层：正式 / 已测开发 | 该层条件投影 | 1024–8192层未测数量 | >8192层未测数量 |
|---|---:|---:|---:|---:|
| i-MedRAG | 10508 / 24 | 约1398小时 | 3040 | 357 |
| TC-RAG | 10466 / 24 | 约338小时 | 3072 | 367 |

输入长度用各自tokenizer计算，故分层数量不同。投影使用最终逻辑请求成本和原始完整运行的wall/engine比例，不再次除以并发数；仅代表当时共享GPU及短开发输入的执行尝试。未测长度层缺少真实吞吐，因此两个方法完整正式时长仍为 `null`。不把已覆盖层当整套预算，不据此宣称TC-RAG更快。

<a id="record-0199"></a>

## 8. 可用于论文的表述及局限性

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第266行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 8. 可用于论文的表述及局限性

<a id="record-0200"></a>

## 8.1 Methods草稿

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第268行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 8.1 Methods草稿

> 我们在既有医疗问答评测框架中适配i-MedRAG（M6）与TC-RAG（M7）。i-MedRAG使用Llama-3.1-8B-Instruct，执行4轮追问，每轮请求3个查询；每个有效查询独立检索并生成答案，随后按原查询顺序写入历史，最终由原问题及QA历史生成答案。TC-RAG使用关闭thinking的Qwen3-8B，通过活动记忆栈、工具检索、回退和总结替换维护推理上下文，并以完整生成分布的逐token熵之和监控状态；沿用官方执行器的8步上限、topK=4及sigma=1.2。两个方法复用完整MedCorp及BM25每库32条候选、MedCPT重排top8的检索配置。所有角色在各自方法内使用同一backbone，输入权限、原生答案空间与评分规则沿用冻结v5协议。

<a id="record-0201"></a>

## 8.2 实现验证草稿

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第272行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 8.2 实现验证草稿

> 我们通过固定响应测试核对跨轮QA依赖、活动记忆回退与总结、熵计算、终止边界、输入隔离及断点恢复，并在24条固定训练/开发输入上分别执行真实模型验证。19项自动测试通过，两个模型的生成时熵与同后端output_scores参考一致。i-MedRAG与TC-RAG分别获得19/24和9/24运行有效输出；其余输入及失败原因保留在完整计划分母中。开发结果用于报告实现行为、接口兼容性和实际成本，正式v5全量比较尚未执行。

<a id="record-0202"></a>

## 8.3 当前证据的局限

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第276行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 8.3 当前证据的局限

1. **适配实现的边界**：名称应为“统一实验框架下的适配实现”。i-MedRAG固定4轮后终止、TC工具集合迁移及Summary补齐均已披露；不能声称直接复现两篇原论文的表格分数或原样运行完整上游系统。
2. **对照配置差异**：i-MedRAG与TC-RAG使用不同backbone，不能把两者差异全部归因于算法；与既有M4/M5比较也须披露Transformers/vLLM及阶段预算差异。旧M0/M2的64-token预测不是完全受控的共同预算对照。
3. **开发与测试区别**：24条开发输入在工程修复中反复使用，不是独立测试集；各版解析/提示/随机数/调度变更交织，不能把版本得分差写成受控消融。
4. **兼容问题仍在**：i-MedRAG有5条invalid，TC有15条invalid，开放诊断还存在解析及canonical映射问题；不能把终态齐全称为全部验收通过，也不能把canonical未命中直接解释为语义答错。
5. **覆盖和协议**：真实开发只覆盖两类来源和短输入；其余格式、长输入及证据干预尚无完整真实覆盖。M22使用项目的固定受扰动证据＋额外检索协议，不等价于原生静态证据任务。v5是已确认预算抽样范围，不是全部来源原始全量。
6. **数值及成本外推**：熵对照只证明已测同后端序列一致；不同硬件、引擎及BF16批次形状可能改变分布。实测共享GPU吞吐包含invalid，未测长度层不能可靠外推，因此尚无完整正式预算。

<a id="record-0203"></a>

## 9. 制品导航及记录维护

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第285行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 9. 制品导航及记录维护

| 论文写作所需信息 | 制品 |
|---|---|
| 固定出处、组件对应、非等价修改 | [method_fidelity.md](/home/data3/txy/docs/workspace.md#record-0374) |
| 最终状态、错误及实测结果 | [acceptance_report.md](/home/data3/txy/docs/workspace.md#record-0379) |
| 原生输入/证据/评分权限 | [evidence_protocol.md](/home/data3/txy/docs/evaluation/protocol.md#record-0386) |
| 最终配置、模型和环境 | [configs/](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs)、各run的 `resolved_config.json` 与 `code_snapshot/` |
| 正式映射、开发来源及隔离审计 | [data/input_lock.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_lock.json)、[data/dev_provenance.jsonl](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_provenance.jsonl)、[reports/dev_question_overlap.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/dev_question_overlap.json) |
| 逐题最终预测 | [i-MedRAG predictions](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/predictions.jsonl)、[TC-RAG predictions](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/predictions.jsonl) |
| 完整prompt/输出/检索/活动栈 | `runs/<run>/items/<input>/{requests,attempts,events}`；输入、配置和文档身份随记录保存 |
| 历史修复和新增成本 | [runs/](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs)、各run的缓存来源和源码快照、[formal_cost_estimate.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/formal_cost_estimate.json) |
| 已验证命令 | [README.md](/home/data3/txy/docs/workspace.md#record-0387)、[acceptance_final_commands.log](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/acceptance_final_commands.log) |
| 总工作区功能入口 | [MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/docs/workspace.md#record-0001)，由 [/home/data3/txy/AGENTS.md](/home/data3/txy/AGENTS.md) 链接 |

README中的准备、检查、19项测试、开发运行、终态恢复和离线评分命令已有本机执行证据；正式全量命令已接入入口，尚未执行全量GPU验证。模型权重、受限制原始材料、凭据及巨型轨迹不随代码发布，服务器保留可恢复路径和身份记录。

2026-09-13本次更新为文档整理：新增本文并更新README及AGENTS.md链接的工作区功能记录。数值来自已有制品和源码快照；没有在本次文档更新中运行模型、改变方法配置、修改评分或新增实验。

2026-09-13后续命名调整：按用户指令将i-MedRAG命名为M6、TC-RAG命名为M7，同步README、方法忠实性、验收、输入协议及工作区功能记录。该调整仅确定论文/比较编号；原执行标识、配置、源码、预测、缓存与运行目录保持原有身份。

<a id="record-0205"></a>

## 本次试跑发现的上游行为遗漏（2026-09-13）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第310行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 本次试跑发现的上游行为遗漏（2026-09-13）

M7原12条试跑为1有效/11无效/0失败，404.71秒；9条无动作标签输出在本地直接失败。锁定上游 `model/TCRAG.py::process_no_regular_output` 实际会将无关键词输出加上Final Answer标签，再经过原步数/熵判断。独立 `results_v5_m6_m7/tc_upstream_fix` 补回此处理，保持原始生成token熵、sigma1.2和topK4，保留适配的Plan/Summary及DOC_RAG查询参数，不照搬会破坏参数的query全局替换。14项方法测试通过；复用77份旧请求收据，新增10次LLM请求后，同12条为9有效/3无效/0失败。新增运行50.19秒不可称冷吞吐。70次模型身份/活动栈、57次熵重算、33次接受边界检查通过，原生诊断评分19条映射已完成。

M6锁定上游 `src/medrag.py::i_medrag_answer` 直接使用抽取列表，查询解析异常时跳过该轮；旧适配的逐字匹配门槛及任一解析问题使整题invalid并非上游行为。独立 `results_v5_m6_m7/m6_upstream_fix` 恢复这两项行为，保留JSON类型检查和运行失败记录，14项方法测试通过。当前原始M6试跑继续运行，修复分片已排队接续。只复用首个查询列表改变之前的请求，之后QA和依赖重算；全量尚未启动。完成状态以新包 `RESULTS.md`、`fixed_pilot_summary.json` 和各run制品为准。

<a id="record-0213"></a>

## 10. M6/M7与新M4吞吐差异诊断（合并原独立分析）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第364行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 10. M6/M7与新M4吞吐差异诊断（合并原独立分析）

2026-09-13。仅离线读取已保存的正式运行记录和当前源码，没有启动模型、修改推理代码或恢复队列。M6仍暂停52条，M7仍暂停1,646条。

结论：M6有很高的多阶段固有成本；M7约六轮的成本之外，当前HF静态批处理、过细分组、逐token熵值回传与逐请求采样循环进一步压低执行效率。M4使用常驻vLLM并一次提交128个独立单轮输入，两者不是同一执行引擎。单纯把显存或等待线程数调大，不能消除这些差异。

<a id="record-0214"></a>

## 实测对照

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第370行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 实测对照

| 指标 | 新 M4 | M6 | M7：32路 | M7：64路 |
|---|---:|---:|---:|---:|
| 统计范围 | 全部13,905输入 | 40个正式完成输入；另读两片的新阶段 | 6个完整新分片，768输入 | 4个完整新分片，512输入 |
| 平均LLM调用/输入 | 1 | 21.93 | 6.20 | 6.14 |
| 平均累计输入tokens/输入 | 3,773 | 55,461 | 24,347 | 27,083 |
| 平均累计输出tokens/输入 | 312 | 7,779 | 753 | 768 |
| 引擎内有效输出tokens/秒 | 348.47 | 65.76–68.07（新阶段） | 20.03 | 15.85 |
| 实际合批规模 | 每次提交128，最后81；内部连续调度 | 平均6.37–6.94 | 平均2.92 | 平均4.30 |
| 题/GPU小时 | 3,869.88 | 未给全方法外推 | 94.81 | 73.69 |

M4按三卡预留墙钟计算题/GPU小时，含初次模型加载；109个批次平均生成114.14秒，全部生成墙钟71.86分钟。M7用各分片开始至审计结束的单卡耗时合并计算，包含无效终态。M7排除跨阶段复用的000和未完成分片，避免把接续缓存重放当冷启动速度；001/002/003/008/009/010为32路，004–007为64路。M6完成较早的40题存在完成速度选择偏差，不代表全库成本分布，也不能用恢复后的result.seconds推算完整耗时。

粗略归一化，M7的32路正式吞吐比M4低40.82倍：每题输出量2.41倍 × 有效token吞吐差17.40倍，量级吻合。这个乘法只是描述性拆分，不是独立因果归因；有效token吞吐的分母包括prefill、decode和引擎内CPU等待，不能把17.40倍全部归给vLLM。两方法的模型、提示、采样约束和样本范围也不同。

所有统计见[measurements.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/m6_m7_speed_analysis/measurements.json)，在 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/m6_m7_speed_analysis` 下可用 `python3 analyze.py` 从原制品复核。

<a id="record-0215"></a>

## 1. 方法本身需要多少工作

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第388行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 1. 方法本身需要多少工作

M4一题一次LLM生成；新M4重用了原完整检索消息，71.86分钟不含重新建立检索证据的成本，所有最终预测均新生成。

M6正常执行4轮，每轮查询生成1次、查询解析1次、三个检索QA各1次，再加最终回答1次、格式转换1次：4×(1+1+3)+2=22次LLM调用、约12次检索。解析修复或实际查询数量会使调用量上下变化，不把22当硬上限。已完成40题实际调用18–25次，平均输出7,779tokens，约M4的25倍。因此即使执行引擎同样高效，M6通常也不会接近M4的单题成本。[当前方法代码](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/code/methods.py:79)

M7最多8步，当前topK=4按零起始step判断，最早在第5次生成接受最终答案；还必须通过sigma=1.2的熵阈值，平均约6.2次生成。每轮把当前问题、思考和工具观察重新组成完整prompt，累计输入tokens是M4的约6.45倍。提前减少步数、放宽熵阈值或削减输出预算会改变方法，不能当作等价工程优化。[停止规则](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/code/methods.py:279)

<a id="record-0216"></a>

## 2. 主要执行瓶颈：静态批次等待最长输出

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第396行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 2. 主要执行瓶颈：静态批次等待最长输出

当前M6/M7的BatchingBackend先收集一组请求，再同步调用HFBackend.generate；只有整批model.generate返回后，才给每个future写回结果。中途结束的短序列无法腾出位置接收新请求，它所属输入也无法开始下一阶段。当前Transformers4.51.3的常规generate保持批维度，并对结束序列补pad直到全批结束；这与连续调度不同。[本地合批/写回实现](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/code/backend.py:172)；[固定版本上游代码](https://github.com/huggingface/transformers/blob/v4.51.3/src/transformers/generation/utils.py)。

真实M7批次：6个输出长度为223、7、2048、107、10、169tokens，整批耗时273.6秒，有效decode位置只占20.9%。7token和10token的任务同样等待整批返回。32路完整分片有效decode位置比例45.2%–52.5%；64路降到35.6%–41.4%。这不是显存容量不足，而是已经分配的批次有大量位置在做补齐计算。

新M4一次给vLLM提交128个请求，内部可以在序列结束后调度其他待生成请求。当前M4外层仍整片返回，但每题只有一次生成，没有M7那样的多轮future依赖链。连续批处理会逐步移除结束请求并补入等待请求，机制见[Hugging Face官方说明](https://huggingface.co/docs/transformers/v5.6.2/continuous_batching)；该较新API不是当前4.51.3安装已经启用的功能。

<a id="record-0217"></a>

## 3. 等待池很大，实际批次仍小

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第404行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 3. 等待池很大，实际批次仍小

合批同时要求生成预算一致、是否计算熵一致、答案类型一致、生成阶段一致，以及prompt长度落在同一个2倍区间。M7全是action阶段，但答案类型和长度桶仍把32个并发输入切成很多小队列；这些输入还会在不同时间等待检索。实际均值只有2.92条。

64路把实际均值提高到4.30，却让长尾与排队更严重：完整分片吞吐94.81→73.69题/GPU小时，下降22.27%。这是不同随机分片的观察，不是严格配对试验，但没有支持继续加线程的证据。先前20分钟正式诊断里，接近96,000合批token上限的批次占0%–2.2%；直接把上限加大不解决队列碎片和长尾。[原始诊断](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/logs/m7_throughput_diagnosis.json)

M6恢复后的两片已新执行720＋777=1,497次LLM阶段请求，但只各进入4次final/format，即新增8个最终结果；其他计算积累在多轮查询与QA里。这解释了“GPU工作很久，每轮新增终态却很少”，不能用终态新增数当已经完成的阶段工作量。

<a id="record-0218"></a>

## 4. M7的熵采集和采样循环有额外开销

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第412行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 4. M7的熵采集和采样循环有额外开销

当前每个生成token都执行全词表FP32 softmax/log/sum，然后立即`.detach().cpu().tolist()`回传熵值。此处会造成逐步设备同步；HF采样本身还需概率计算，当前collector没有复用该概率张量。两方法的自定义采样又在每个token上按请求循环调用torch.multinomial，再拼接结果，以保留各请求独立随机数流。[熵采集与采样](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/code/backend.py:55)

这些路径由源码确认，但日志没有将其与模型forward分别计时，不能声称熵采集占某个确定百分比。scoring_forward_calls实际为0：当前熵来自生成时已有logits，并未每步额外重跑一次模型。问题是额外分布计算、CPU循环和同步，而不是第二次模型forward。

低改动候选是把每步的每序列熵标量保留在GPU，生成完成后一次性传回CPU，保持原FP32公式、特殊token过滤和后缀选择。只保留标量轨迹，不保留完整词表scores；此改动的速度收益尚未测量。

M7迁移到vLLM需要专门处理熵：本地vLLM0.8.5 V1的普通logprobs来自温度和惩罚之前，且通常只返回top-k＋采样token，不能替代当前温度后全词表熵。应在采样器正确位置计算同一全词表信号，并返回每token熵标量；不能拿top-20近似熵或采样token负logprob冒充原指标。[本地V1采样器](/home/data3/txy/MedRGAG/.venv/lib/python3.10/site-packages/vllm/v1/sample/sampler.py:27)

<a id="record-0220"></a>

## 建议的实施顺序

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第429行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 建议的实施顺序

1. M6先独立接入现有vLLM连续调度服务、每卡模型常驻，沿用原提示、四轮三查询、解析/QA/formatter、每阶段预算与失败规则。它不依赖M7的熵信号，迁移最直接；需要验证native适配、独立请求seed与阶段缓存版本，不能宣称HF/vLLM逐token一致。
2. M7先做GPU侧熵轨迹延迟回传，固定同批prompt/seed，验证token输出、逐token熵、后缀选择和停止判定一致；同时量出该修改对完整阶段耗时的实际收益。
3. M7再迁移连续调度，提供正确的全词表、温度后熵hook。请求完成后立即释放对应输入的下一阶段，不再等待整个静态批次。确认HF/vLLM熵信号约定和阈值含义，不用截断top-k概率代替。
4. 引擎替换后再调并发与token上限；用预先固定的正式请求做阶段性能验证，再用单独128题完整方法分片测新终态/小时、有效率、截断、步骤分布与成本。验收以完整方法吞吐为准，不能用短输出微基准代替全量效率。

目前只完成原因诊断和可复核测量，未实施以上提速改造、未重启M6/M7；不能承诺具体提速倍数。原M7吞吐外推三卡跑13,905题约49小时，但它不是全量已测时长，也不是优化后的预计时长。

后续实施和验证见[第11节](/home/data3/txy/docs/baselines/tcrag.md#record-0221)；上面的“未实施”保留诊断时点。

<a id="record-0222"></a>

## 实现

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第448行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 实现

- [vllm_backend.py](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/code/vllm_backend.py)：单卡常驻 vLLM 0.8.5 V0，连续调度、prefix cache、chunked prefill。每个请求完成便交还其题目线程，允许下一步进入引擎，移除旧 HF 的整批长尾等待和题型/阶段/长度分桶。最大并行序列 128、每步 prefill token 上限 16,384；模型及 MedCPT 检索共用该卡。后续默认 M6/M7 显存预留均为 70%；M7 默认配置与已经完成 128 题验证的 scale 配置一致，旧 32 题实际 85% 配置保留在该 run 的 resolved_config.json。
- [runtime.py](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/code/runtime.py)：相同输入消息保留原阶段种子；新增引擎执行字段不改变种子。vLLM 请求仍使用独立缓存身份，没有把 HF 生成收据当作新计算。
- [backend.py](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/code/backend.py)：HF 全词表熵留在 GPU，到生成结束统一回传。四个固定请求 ABBA 微测试只快约 1%，说明消除这一同步本身不能解决整体慢的问题。
- M7 logits hook 保留温度后 FP32 全词表 `-sum(p*log(p+1e-10))`，按原 token 后缀计算状态，原阈值及栈操作不变。对 V0 sampler 作本进程 FP32 输入适配，避免 BF16 将温度 0.7 舍入为 0.69921875；退出后恢复，没有修改安装的库文件。异步输出可能多计算一步，熵只记录实际输出 token 的位置。
- [methods.py](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/code/methods.py) 与原 balanced 方法文件一致：M6 四轮、每轮请求三个问题，原 QA/最终格式化流程；M7 八步预算、`topK=4`、严格 `H<1.2` 接受规则。模型、检索、提示、完整生成预算均保持。没有加入 CF/WM、Schema 约束或另一个对话中的 M6 formatter 修复。

`configs/*vllm*.json` 和 M6 配置中的 `max_batch_tokens=32000` 是为保留历史阶段种子的既有语义字段，**不是 vLLM 的实际调度上限**；实际引擎参数见上述说明和 `execution_report.json/effective_execution`。配置的历史 `sampling_rng` 字段也不代表 vLLM 使用 HF 的采样实现；实际引擎见各 run 的 `actual_backend.json`。不同引擎的随机采样和数值内核会改变具体输出，不能声称逐 token 等价。

<a id="record-0223"></a>

## 验证设计与证据

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第458行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 验证设计与证据

[plan.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/plan.json) 在生成前按可见题型和固定随机种子选定输入；无效输出保留在分母。先运行 M6 五题全流程，再运行固定 128 题；M7 使用同一组 32 题作旧 HF 与 vLLM 对照，再用之前已选定的 128 题验证完整分片规模。四项完整流程运行均使用原预算，128-token/64-token 探针仅验证实现，不充作 benchmark 加速比。

| 运行 | 输入与并发 | 状态 |
|---|---|---|
| `m6_smoke` | 五种格式各一题 | 5/5 协议有效，110 次调用，全部流程审计通过；早期工程 smoke |
| `m6_vllm_128` | 128 题 / 128 线程，显存预留 85% | OOM，128 条失败；保留全部收据，不计入成功吞吐 |
| `m6_vllm_128_mem70` | 同 128 题 / 128 线程，显存预留 70% | 2,069.41 秒，102 协议有效 / 26 无效 / 0 失败；原生有效 78/128 |
| `m7_baseline_32` | 同组 32 题 / 32 线程，原 HF | 1,725.73 秒，19 协议有效 / 13 无效 / 0 失败；原生有效 14/32 |
| `m7_vllm_32` | 同组 32 题 / 32 线程，显存预留 85% | 110.74 秒，21 协议有效 / 11 无效 / 0 失败 |
| `m7_vllm_128` | 预选 128 题 / 64 线程，显存预留 70% | 369.93 秒，81 协议有效 / 47 无效 / 0 失败；原生有效 54/128 |

M6 首次 128 题在检索重排与生成峰值叠加时显存不足；[重试记录](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/m6_memory_retry.json)保留失败原因和原运行。将 KV 预留降至 70%，全部相同输入从头运行，不复用失败试验已生成的 LLM 阶段。填满显存本身不是优化目标，必须给重排和生成激活留空间。

- [HF 熵缓冲微测试](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/entropy_probe_validation.json)：四请求、ABBA，各模式两次；token、熵、状态完全一致；中位 8.3269→8.2463 秒，1.0098 倍。
- [vLLM 熵验证](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/vllm_entropy_validation.json)：对真实 sampler 的完整 softmax 分布核对 146 个位置，最大绝对差 1.31e-6；开启/关闭采集的 token 相同、后缀阈值决策相同。三个固定请求，不宣称 HF/vLLM 输出相同。
- 完整方法审计逐条核对实际消息、检索与 QA 顺序、M6 历史回写、M7 活动栈和完整熵状态、接受边界与预算耗尽。原生有效率由冻结的 v5 原生分析器离线计算，生成代码不读取答案。
- `tests/` 覆盖既有方法、批量执行和新增种子/熵约定；最终 18 项全部通过，见 [测试日志](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/unit_tests.log)。

<a id="record-0224"></a>

## 完成结果

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第478行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 完成结果

M6 的128题完整耗时 **34分29秒**，**222.67题/GPU小时**；2,810次生成、1,026,610输出tokens、7,535,275输入tokens、1,525次检索问答。512次轮次/历史回写、1,525次检索与有序QA、128次最终历史、2,810次模型/token身份检查全部通过；没有LLM阶段复用，检索实际后端调用1,227次、缓存命中298次。存在7次生成长度截断，保留原预算与输出。

M6协议有效 **102/128（79.69%）**，v5格式有效 **87/128（67.97%）**，原生有效 **78/128（60.94%）**。原运行协议判定与v5评分入口并不完全相同，不能把102条都称为v5格式有效；具体格式/诊断原因见原生逐题收据。没有同输入的旧HF完整M6对照，因此不报告M6的成对加速倍数。首次85%显存预留失败试验耗时472.77秒，保存570条完成生成/171,094输出tokens，未完成token成本无法完整恢复；该试验独立保留，不合入成功吞吐。70%重跑全128题无运行失败，监督采样显存约82.1GiB峰值。

M6平均每题21.95次生成、8,020输出tokens，M7扩大组平均6.51次生成、748输出tokens。执行加速并不消除M6本身较高的计算量。

###### M7 对照

同组 32 题端到端耗时 1,725.73→110.74 秒，**15.58 倍**；原生有效率 14/32→19/32，两组均无运行失败、无 LLM 阶段复用。生成量 25,514→24,456 tokens（减少约 4.15%），调用数 197→219；因此并非通过减少方法步骤获得这一墙钟差异。检索后端实际调用 43→54，缓存命中 18→13，优化版没有依赖更多检索缓存命中。

独立扩大的 128 题耗时 369.93 秒，**1,245.65 题/GPU 小时**，833 次生成；81/128 协议有效，54/128 原生有效，无运行失败。47 条协议无效加 27 条未映射诊断构成原生无效；原生评分先将协议未通过的输出置空，因此其中 `malformed_json` 是评分入口的失败类别，具体预算耗尽、格式和动作失败须看 `termination` 及逐题事件。32 题与 128 题题型构成不同，不将二者有效率差异解释为并发影响。

完整数字与审计计数见 [结果 JSON](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/full_method_results.json)，失败工程试验成本见 [failed_trial_costs.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/failed_trial_costs.json)。

<a id="record-0225"></a>

## 执行与复核

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第494行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 执行与复核

在原运行目录 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm` 下运行；正式模型命令需要对应 GPU 空闲及新的运行目录。`launch.sh` 使用已有 HF/vLLM 虚拟环境，无新安装。

```bash
bash launch.sh 1 m6 --inputs inputs/m6_128.jsonl --run-dir runs/NEW_M6 --workers 128
bash launch.sh 3 m7_vllm --config configs/tcrag_vllm_scale.json --inputs inputs/m6_128.jsonl --run-dir runs/NEW_M7 --workers 64
bash launch.sh 2 m7_baseline --inputs inputs/m7_32.jsonl --run-dir runs/NEW_HF --workers 32 --max-batch-tokens 96000
python3 code/optimization_status.py
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python code/summarize_optimization.py
```

本次使用 tmux socket `iterative-opt`，验证进程现已结束；[状态](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/status.json)、[监督日志](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/supervision.jsonl)记录 GPU0–3 和累计阶段/终态。每个 run 内保留启动时 `code_snapshot/`、实际配置、原始响应、请求、事件和成本。

<a id="record-0226"></a>

## 解释边界

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第508行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 解释边界

墙钟吞吐从模型和检索初始化完成后计时，包含完整题目流程及现有检索缓存命中，不是冷启动耗时；LLM 阶段全部新生成。vLLM `engine_active_seconds` 是 scheduler step 时间分摊后总和，不应将每请求收据解释为实际 batch=1；报告将无法从收据恢复的物理批数标为 null。

同组输入的端到端耗时可以比较，但跨引擎产生不同轨迹，不能把墙钟比完全归因于内核。128 题仅验证当前样本规模的运行稳定性、有效率和吞吐，不代表全库准确率或无 OOM 保证。论文应写“保持方法流程的 vLLM 工程适配”，不写“逐行运行原作者代码”。

<a id="record-0374"></a>

## method_fidelity.md

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

### M6 i-MedRAG / M7 TC-RAG 方法忠实性记录

用户2026-09-13指定比较编号：**M6 = i-MedRAG（`imedrag`），M7 = TC-RAG（`tcrag`）**。执行标识及已冻结制品不变；编号是本项目命名，不是原论文命名。

名称：**统一实验框架下的适配实现**。本包延续服务器的 dated-run-pack 结构，复用现有 MedRAG 检索实现、v5 物化输入和原生评分器。不是原论文表格分数复现。2026-09-12 核对；本文件在真实验收前建立，运行证据另见 acceptance_report.md。

<a id="record-0375"></a>

## 固定来源

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md)，原文第7行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 固定来源

| 方法 | 原论文 | 官方代码 checkout | 许可证 |
|---|---|---|---|
| i-MedRAG | [2408.00727v3，2024-10-11](https://arxiv.org/html/2408.00727v3)，§3.2–3.3、Algorithm 1 | [gzxiong/MedRAG@7599a728a28789fd601728c08d313b1148051f41](https://github.com/gzxiong/MedRAG/tree/7599a728a28789fd601728c08d313b1148051f41) | LICENSE 为 NCBI US Government Work 公有领域声明，不是 MIT；GitHub API 标记 NOASSERTION |
| TC-RAG | [2408.09199v3，2026-09-03](https://arxiv.org/html/2408.09199v3)，§5、Appendix 8.6 Algorithm 1 | [Artessay/TC-RAG@dd8f32f90832eeb452680cfdb02ca604988648d0](https://github.com/Artessay/TC-RAG/tree/dd8f32f90832eeb452680cfdb02ca604988648d0) | checkout 未发现 LICENSE；API license=null。参考源码独立实现，不替上游声明许可证 |

原始 URL 与 GitHub API resolved URL 在 reports/source_resolution.json。论文里 i-MedRAG 链接作者的新用户名 Teddy-XiongGZ；本次 API 返回 gzxiong/MedRAG。两个 checkout 位于 upstream/，不包含模型权重。

<a id="record-0376"></a>

## 逐组件对应

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md)，原文第16行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 逐组件对应

| 组件 | 论文/上游函数 | 本地函数与保留行为 |
|---|---|---|
| i-MedRAG 追问 | §3.3；src/medrag.py::i_medrag_answer，src/template.py | code/methods.py::imedrag；原题及已有 QA → 分析和追问；轮间串行 |
| 独立检索和追问作答 | Algorithm 1 行 8–11；medrag_answer | imedrag；每个真实追问单独 retrieval → RAG answer；同轮并发，按查询序号写回 |
| 追问解析 | i_medrag_answer 内 LLM 提取调用 | parse_queries；保留同 backbone 的提取调用并记成本；JSONDecoder 替代正则+eval，禁止改写/新增查询 |
| 历史和最终答案 | Algorithm 1 行 14；i_medrag_answer | imedrag；最终使用原题+完整 QA 历史，额外保留同模型格式化调用 |
| TC 工具和栈 | §5.1，TCRAG.py::whitebox_pop_react_executor | tcrag；Thought、Plan、真实 Tool_Observation 入栈；模型生成的 Observation 不执行、不进入活动上下文 |
| 回退和状态 | §5.2，pop_message/backtrack_now_state | tcrag；栈顶 pop，恢复该条入栈前状态；工具及实际 Observation 作为一条复合栈项 |
| Summary | §5.1、Algorithm 1 行 29–31 | tcrag；栈顶替换为模型总结；移除内容仅在审计轨迹保留 |
| cuct | Generator.py::generate_all::compute_entropy；system_score.py::calculate_cuct_from_entropy | code/backend.py::entropy_from_scores；code/methods.py::state_signal；生成时计算全词表逐 token 熵并求和 |
| 结论/终止 | whitebox_pop_react_executor | tcrag；零基 actions_taken >= topK 且 state < sigma 接受；否则转 Thought；max_loop 终止，返回真实栈顶同时保留 budget_exhausted |

<a id="record-0377"></a>

## 默认值及差异（不可混作论文原参数）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md)，原文第30行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 默认值及差异（不可混作论文原参数）

- i-MedRAG **4 轮、请求 3 个追问/轮**：官方函数和 README 默认。上游不保证实际正好 3 个；本地保存请求数、实际数、解析和执行情况，不合成补齐。
- i-MedRAG 保留上游的 LLM 提取步骤。安全解析允许 JSON 空白和代码块；非 ASCII 定界引号等语法错误最多一次纯格式修复，原始输出和修复都入日志。提取后的查询必须能在模型原查询段定位：仅规范化无意义水平空白、换行、Markdown 加粗和查询编号/标题，词句与顺序保持一致；拒绝改写、拆分及合并。相同响应回放覆盖这些语法等价情况。失败轮次记录后继续，历史只加入成功 QA。
- 最终格式化保留上游 `Output the answer in JSON: {'answer': your_answer (A/B/C/D)}` 提示，仅按原生选项和答案类型替换括号说明。实测模型跟随示例生成单引号字典，现有评分器要求严格JSON；`final_json` 用标准库 `ast.literal_eval` 读取完整字典字面量并序列化为JSON，最多一次，拒绝冲突/重复字段或非字面量。此操作不使用 `eval`，不改变答案大小写或内容，不增加LLM调用。原始响应及转换事件保留；TC仅在结论已通过熵检查后使用同一语法转换，预算耗尽不转换成合法结论。
- 上游在 4 轮外允许额外 3 次自由循环，甚至继续追问。本包固定 4 个追问轮次，接一次最终分析和一次格式化；这是明确的终止适配，不声称调用数完全等同任意上游轨迹。满额正常为 **22 次 LLM 请求 + 12 次检索**，语法修复和传输重试另计。
- TC **max_loop=8、topK=4、sigma=1.2、初值100000**：固定官方执行器。最早第 5 次生成接受，sigma 比较严格小于。论文 v3 Appendix 8.7.6 另写 uct=20 / cppl=10、temperature=.6、500 tokens；本包不默默把这些与代码默认混用，不按正式测试分数调阈值。
- 过早Final Answer若带有Thought前缀，会按上游保留该前缀后转为Thought；达到topK后沿用上游的Final Answer片段处理。固定响应测试核对下一轮实际看到的内容及阈值边界。
- TC 官方代码没有独立 Summary 分支；其 Backtrack 文字要求总结，但实现会 pop 后追加反馈，不等价于 Summary 替换。Plan 和 Summary 均来自论文§5.1/Algorithm 1，本地补齐明确动作分支。Backtrack按论文恢复 popped Thought 的前一状态，并修复上游跨题 state_value_list 未清空问题；反馈只入审计，不重新塞回栈导致反复弹反馈。
- 论文Algorithm 1会把低于sigma的Thought状态钳制到sigma，配合while条件避免过早结束；官方执行器没有该钳制，只在Final Answer分支检查阈值。本地沿用后者，保存真实未钳制熵，普通Thought不会结束循环。Summary替换Thought时恢复下面栈项的状态快照，是本项目保持活动记忆/状态一致的记录约定；论文Summary伪代码没有明确写出这项状态恢复。状态数值不写入模型prompt，接受结论时重新计算当前生成的熵，因此这项快照约定不增加接受条件或模型调用。
- TC 默认 token 范围保留官方 `update_status_value` 的精确 token 字符串匹配：剔除全部特殊 ID 后，循环 `range(len(tokens)-3)`，首次 `Thought` 后偏移2，或 `Final` 后下一 token 精确为 `Answer` 时偏移3；扫描失败从0开始，边界失败取全部。**不 strip token 的前导空格**，因此某 tokenizer 的 ` Answer` 不匹配。每次保存 start、selected_positions、匹配状态、真实 token 文本；这是上游口径，不能写成完美截取 Final Answer 正文。
- 分数取 Transformers 生成处理器和采样变换之后、抽样之前的完整词表分布；自然对数，`-sum(p*log(p+1e-10))`，FP32，token 级再求和。特殊 token 分布不从词表重归一化，只排除生成位置。无 top-k logprob 近似、单 token NLL、口头自信度或更小评分模型。
- 生成时熵收集器不修改分数；与同后端 `generate(output_scores=True)` 对照测试。选 cuct 后不计算 attention、其他指标及完整词表导出；日志仅需逐 token 熵。主路径没有额外打分前向。
- 上游依赖锁为 Transformers 4.44.0 / torch2.4.0。本包4.51.3 / torch2.6.0支持Qwen3。已核对4.44.0的 [生成器](https://github.com/huggingface/transformers/blob/v4.44.0/src/transformers/generation/utils.py) 保存的是处理器和warper之后的scores；其 [Qwen2](https://github.com/huggingface/transformers/blob/v4.44.0/src/transformers/models/qwen2/modeling_qwen2.py)（Qwen1.5架构路径）及 [Llama](https://github.com/huggingface/transformers/blob/v4.44.0/src/transformers/models/llama/modeling_llama.py) forward将logits转换为FP32。本包FP32熵公式与此口径一致；未声称不同模型/引擎的分布或阈值判断逐bit相同。
- 工具统一为真实 DOC_RAG → 既有完整 MedCorp 四库 BM25 每库32 + MedCPT top8；不引入上游外部 web/KG/NER 的异构模型。语言改为英文，动作语义按论文；不使用 CF 专项提示。此工具集合迁移属于统一框架适配，不能称上游完整工具系统。
- i-MedRAG 使用当前 M4 的 Llama-3.1-8B-Instruct；TC-RAG 按用户明确指令使用当前 M5 的 Qwen3-8B，`enable_thinking=false`，YaRN factor4 / original32768。BF16、temperature=.7/top_p=1/top_k=0、seed42、131072 上下文和追加检索预算30000沿用当前 v5 M4/M5。查询/解析/QA/TC动作/最终/格式化各阶段 token 上限单独冻结。不同 backbone 的两个新方法不能作为只改变算法的直接因果对照；与旧 M0/M2 的64-token预测和不同生成引擎也不构成全部条件受控的比较。
- 同一轮 QA 并发提交、按查询序号写回，各条 QA 单独保存成功收据；不同输入可共享张量批次，各输入的上下文与随机数流独立。经过共享GPU环境下的实际OOM，执行配置v4将合批上限改为32000 padded tokens（单个合法长请求保留完整输入），使用可扩展显存分配器，并将Llama层分为12/20、Qwen分为14/22，4个输入工作线程。方法轮数、检索条数、输入和生成预算均未减少。小模型回放验证单独/合批的 token 序列一致；BF16 在不同硬件或张量形状下仍可能有数值差异，未声称跨引擎逐 bit 一致。早期pilot及失败记录保留。请求缓存、尝试记录和最终结果均采用原子写入，运行配置改变须新目录。
- 按用户最新范围要求，本轮保留TC官方默认sigma=1.2，不执行阈值校准或正式题盲测。早先登记的有限校准计划未执行；无据此产生的阈值或预测。
- 任务允许的固定证据保留于原问题，检索也按冻结证据权限执行；最终原题自带证据不等于直接合并迭代检索文档。M22 沿用 v5 六档材料，额外检索访问需清晰命名及单独报告，不能冒充原生静态证据协议。

<a id="record-0378"></a>

## 验证证据

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/method_fidelity.md)，原文第50行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 验证证据

19项自动测试、两方法各24条真实开发运行、两个实际模型的熵参考对照以及终态恢复已完成，证据汇总于[acceptance_report.md](/home/data3/txy/docs/workspace.md#record-0379)。全部实际prompt/QA历史/活动栈/状态接受边界已通过离线审计。输出格式与开放诊断评分兼容问题、其他来源及长输入的真实验收仍保留为未完成项。

<a id="record-0379"></a>

## acceptance_report.md

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

### M6 i-MedRAG / M7 TC-RAG 接入验收

按用户2026-09-13命名：**M6 = i-MedRAG（`imedrag`），M7 = TC-RAG（`tcrag`）**。下列结果沿用已有运行制品，仅补充比较编号。

当前状态：两方法实现、19项自动测试、各24条真实开发运行、熵后端对照、终态恢复和离线审计已完成。i-MedRAG为19有效/5无效，TC-RAG为9有效/15无效；输出格式及开放诊断评分兼容仍有未解决项，不能称全部验收通过。正式全量评测未启动。新增方法只有`imedrag`、`tcrag`；M20/MedCounterFact、M22/MedRGB、M23/BioRAB是现有数据集编号。

<a id="record-0380"></a>

## 实现与冻结条件

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md)，原文第7行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 实现与冻结条件

i-MedRAG保留4轮追问、每轮请求3个查询、逐查询真实检索及作答、按原序写入QA历史、最终分析与官方格式化调用。TC保留真实工具、活动栈、回退、Summary替换、全分布熵、最早第5步接受及8步上限。入口已注册在现有项目。

| 条件 | M6 i-MedRAG | M7 TC-RAG |
|---|---|---|
| Backbone | meta-llama/Llama-3.1-8B-Instruct | Qwen/Qwen3-8B，thinking关闭 |
| 执行配置 | [imedrag_runtime_v4.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/imedrag_runtime_v4.json) | [tcrag_runtime_v4.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/tcrag_runtime_v4.json) |
| 方法默认 | 4轮，每轮请求3查询 | max_loop=8，topK=4，sigma=1.2 |
| 生成 | BF16，temperature=.7，top_p=1，top_k=0，seed42 | 同左；YaRN4/original32768 |
| 上下文/合批 | 窗口131072，合批32000 padded tokens，4工作线程 | 同左 |
| 阶段生成上限 | query/parse/QA=1024；final/format=2048 | action=2048 |
| 检索 | 完整MedCorp四库，BM25每库32，MedCPT重排top8，追加上下文30000 tokens | 同左 |

仅使用GPU1/2空余显存，既有任务继续运行。模型/分词器/索引身份见[resources.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/resources.json)，依赖见[environment.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/environment.json)、[requirements.lock.txt](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/configs/requirements.lock.txt)。逐组件固定论文、官方SHA、许可证、补丁及差异见[method_fidelity.md](/home/data3/txy/docs/workspace.md#record-0374)。名称为统一框架适配，不是两论文原表格分数复现。

<a id="record-0381"></a>

## 自动测试与数据审计

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md)，原文第23行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 自动测试与数据审计

[19项自动测试全部通过](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/tests_final_syntax.log)：跨轮QA依赖及并发顺序；安全查询解析；TC工具/回退/总结/接受边界/耗尽；FP32熵数值和位置；样本隔离、gold哨兵、证据差异及缓存；中断收据恢复、终态恢复与配置漂移拒绝；原生格式和失败分母；复用成本不重复计费。synthetic响应仅存在于tests。

冻结现有v5：6104单元、13000入选判断、13905唯一输入、15616原生评分记录、34753行target→input展开映射。[input_lock.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_lock.json)、[input_manifest.jsonl](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_manifest.jsonl)、[source_target_input_mapping.jsonl](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/source_target_input_mapping.jsonl)保留原记录及输入哈希。没有重新抽样或改变evaluation_labels。现有契约审计[通过](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/v5_existing_contract_audit.json)，模型/索引及必需输入长度检查[通过](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/environment_check.json)。

开发包为MedQA validation前12条、MedEinst training排除正式病例/完整输入后的前12条。[来源记录](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_provenance.jsonl)、[病例重叠审计](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_overlap_audit.json)、[题干重叠审计](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/dev_question_overlap.json)可重放：24条与13905正式输入规范化题干精确重叠为0，不声称排除了所有语义近重复。没有正式题模型暴露或阈值校准。

两个真实后端均通过同模型、同token序列的`output_scores`对照：熵最大绝对误差0；收集熵与不收集熵时生成token相同，阈值判断相同。证据：[Llama](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_v4/backend_reference.json)、[Qwen](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/backend_reference.json)。每次对照另计2个真实请求，无额外重放打分前向；不声称跨硬件/引擎逐bit一致。

<a id="record-0384"></a>

## 正式规模和成本

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md)，原文第55行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 正式规模和成本

每方法13905唯一输入。标准i-MedRAG恰好12个QA/题且无重试时为305910个LLM请求、166860次检索；实际查询数可能不同。TC至多111240个动作请求，最早全部第5步接受为69525个；重试另计。

[成本估算](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/formal_cost_estimate.json)按实测请求和输入长度分层，并使用原始完整运行的wall/engine比例，没有再次除以并发数。当前i开发样本全部落在必需输入≤1024 tokens层；该层正式10508条按共享GPU条件投影约1398小时。1024–8192层3040条、>8192层357条没有实测开发样本，完整正式时长保持未估出，不能将已覆盖层当作整套预算。TC的≤1024 tokens层正式10466条、开发24条，投影约338小时；其1024–8192层3072条及>8192层367条未实测。两方法完整正式预算均保持未估出。此投影只代表当时共享GPU、两类短开发输入的执行尝试，不能外推空闲GPU或全部来源的有效完成成本。

<a id="record-0385"></a>

## 命令与限制

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md)，原文第61行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 命令与限制

[README](/home/data3/txy/docs/workspace.md#record-0387)给出本机验证的环境检查、准备、测试、开发运行、原样恢复和离线评分命令。两方法完成后原命令恢复均已验证，无新增推理；`bash acceptance.sh`已实际执行，日志见[acceptance_final_commands.log](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/acceptance_final_commands.log)，[完成标记](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/acceptance_execution_complete.json)同时记录formal/blind/calibration均未启动。评分源码、来源路径及哈希已留存于[scoring_snapshot/sources.json](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/scoring_snapshot/sources.json)。成本脚本已再次实际运行，包含v1/v2/v3全部旧pilot及格式修复来源链；无输出的中断请求只能记录已知时间/尝试，其未知token不作猜测。正式全量命令已接入，但**尚未执行全量GPU验证**；本轮未启动正式评测。

尚未完成：开发包暴露的输出格式和开放诊断评分兼容问题；全部正式来源结构、长输入及证据干预的真实模型覆盖；未观测长度层的可靠完整成本预算。其他格式和核心回退/总结动作已有固定响应测试，不能代替全部来源真实验收。M22继承v5固定受扰动材料＋外部检索，并非MedRGB原生静态证据协议。开放诊断存在上述评分兼容限制。两个backbone、旧64-token预测及生成引擎的可比性限制见[输入与评分协议](/home/data3/txy/docs/evaluation/protocol.md#record-0386)。

<a id="record-0387"></a>

## README.md

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/README.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

### M6 i-MedRAG / M7 TC-RAG 比较方法接入

**2026-09-14最新全量完成：M6已替换为MedGENIE v2，13,905题全部新生成，格式96.49%、原生77.32%、ALL48.02%，0运行失败。[七方法全量结果与图](/home/data3/txy/docs/baselines/medgenie.md#record-0399)。旧i-MedRAG和既有图表作为历史版本保留。**

本目录是 `xiotakut/cf_mrg` 的服务器运行包。按用户2026-09-13命名，**M6 = i-MedRAG，M7 = TC-RAG**。入口已注册至既有 `cf_medrgag_validation_pack/scripts/run_iterative_baselines.py`，执行标识仍为 `imedrag`、`tcrag`。复用现有完整 MedCorp、BM25＋MedCPT 检索实现、冻结 v5 输入与原生评分器；新增同权重 Transformers 生成后端以提供 TC-RAG 所需的完整分布熵。

| 论文/比较编号 | 方法 | 命令与结果中的执行标识 |
|---|---|---|
| M6 | i-MedRAG | `imedrag` |
| M7 | TC-RAG | `tcrag` |

后续论文与比较表统一使用上述编号；既有配置、命令、run目录和预测保留原执行标识，编号调整不改变实验身份或缓存。

TC-RAG 按用户指定使用 **Qwen3-8B，关闭 thinking**；i-MedRAG 使用当前 M4 的 **Llama-3.1-8B-Instruct**。比较各自同 backbone 的 M5/M4 时仍需披露生成引擎和阶段预算差异。论文的7个QA benchmark是方法来源设置，本包继续使用服务器已确认的 R1–R5 v5。

实现依据和补丁见 [method_fidelity.md](/home/data3/txy/docs/workspace.md#record-0374)，输入、证据权限和评分规则见 [evidence_protocol.md](/home/data3/txy/docs/evaluation/protocol.md#record-0386)。实际完成情况、成本及限制以 [acceptance_report.md](/home/data3/txy/docs/workspace.md#record-0379) 为准。

后续论文写作从 [PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/docs/workspace.md#record-0174) 开始：其中记录实际完成的工作、逐项适配、全部试跑与修复顺序、最终配置来源、缓存复验、新增计算量及结论边界。

#### 文件

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

#### 环境与准备

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

#### 开发验收和恢复

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

#### 正式运行

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


#### MedGENIE 替代候选（2026-09-14）

新入口为 `code/run_medgenie.py`，执行标识 `medgenie`。四来源依据、原论文与MedRGAG差异、v5适配及实际试跑结果统一记在 [原有复现记录](/home/data3/txy/docs/workspace.md#record-0174)。旧i-MedRAG结果保留。

```bash
CUDA_VISIBLE_DEVICES=1 VLLM_USE_V1=0 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True /home/data3/txy/MedRGAG/.venv/bin/python -u code/run_medgenie.py --inputs data/dev_inputs.jsonl --run-dir runs/medgenie_dev_new --workers 12
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python code/score.py --split dev --run-dir runs/medgenie_dev_v2
python3 -m unittest discover -s tests -p test_medgenie.py -v
```

相同命令可恢复；修改源码、配置、输入或workers须使用新run目录。完整正式输入可由同一入口读取 `data/inputs.jsonl`，本轮仅执行开发验收。预测字段和评分入口与已有方法兼容。

当前已完成开发结果见 `runs/medgenie_dev_v2`，后续multi序列化修复只复验受影响题型，见 `runs/medgenie_format_smoke_v2_multifix`。上面的推理命令使用新目录；评分命令读取已完成的24题。旧run源码已冻结，当前源码变动后会拒绝写入旧run，属预期行为。

<a id="gpu-reservation-handoff-20260923"></a>

## 2026-09-23：CF-MoA实验空档继续占位并自动交接

用户要求继续新计划，并在不使用GPU时用现有占位脚本保留卡。已核实旧14:44占位不再运行；GPU2/3现有PID1069257/1067639/1070988是其他用户wbc的真实模型任务，未触碰。使用原`.local/bin/gpu_watch.py`，不再另造显存分配工具；初始GPU2/3各一个固定卡watch，沿用`--min-free-gib 50 --gib 80 --hold-hours 0 --wait-hours 0 --interval 5 --log-interval 300 --max-cards 1`。尚未满足条件时仅等待，不能把watch存活写成已成功占卡。

新调度`Documents/Codex/2026-09-21/cf_moa/effect_first_revision_20260923/cycle3/queue_answers_reserved.py`（PID1076402）在18:53:59启动watch PID1076411/1076412。各卡状态位于`cycle3/reserved_gpu_watches/gpu2|gpu3/generation_0001/`，存储launch、status、watch.log及未来holder记录。只把本watch活PID、启动时标、父子关系、ready文件及nvidia实际显存共同证明的占位计入可释放余量；需要运行时在相应generation写STOP、等释放、再按原profile准入检查。若余量被其他进程拿走则恢复watch继续等，不认为显存天然独占。模型运行期间本卡watch停止；明确engine关闭后创建新generation补占。若在GPU0/1运行，也在其结束后补上对应固定卡watch。6项mock交接测试及编译通过；完整真实交接尚待GPU释放后验证。

只替换了已确认无实验launch的CPU等待器PID1071730和未开始评分的收尾等待器PID1073227；没有向GPU模型发信号。原脚本/状态/启动记录及SIGTERM收据保存在`cycle3/scheduler_before_reservation/`。解除原2小时调度与3小时收尾等待期限，固定实验量和解码/模型/KV/上下文不变。新收尾PID1075724带flock，仅允许从waiting续接，任何已评分状态不得自动重算。实验预算仍是冻结的两骨干34×3任务。

当前证据：`cycle3/answer_queue_status.json`、`answer_queue_reserved_events.jsonl`、`finish_status.json`。两个watch于启动后实际快照均holders=[]；GPU2/3尚无新的成功占位。停止占位时应先停止本队列调度，再向相应活跃generation写STOP，避免运行中的调度立即补占；这些操作只适用于核实为本任务记录的进程。占位显存/持续时间留在独立资源日志，不伪装成模型调用或推理token成本。用户资源偏好已登记在`cf_moa/configs/execution_plan.json`，后续继续时读取实际状态，不再仅凭旧holder文件判断。


### 同日18:58：采用profile不变，修正readout调度估算

继续核查发现GPU0虽有59857MiB（58.45GiB）空闲，却被本地readout额外60GiB floor拦住。该floor在resource_admission.json明确属于调度阈值，非模型/vLLM硬条件。已安装V1 0.8.5源码先按profile检查单条131072上下文，再应用16384 KV块override；既有完整公式含权重、固定缓存、最大上下文、utilization reserve及3GiB额外余量，本身向上取整M4为50GiB、M5为55GiB。两骨干固定KV分别32/36GiB，不能错误假设相同；旧query日志真实加载14.9889/15.2898GiB且成功分配262144-token缓存。公式仍是估算，真实峰值与共享卡波动不能由它保证。

因此新增仅用于cycle3的`profile_derived_admission.py`入口：保留原profile所有模型/精度/KV/上下文/批次/解码参数及原公式，移除该额外floor；原全局resource_admission.json、原研究runner和专家源码未修改。resource_admission.json运行收据同时记录原60GiB判定与新公式判定。原尚无answer提交的plan、调度源码/进程记录保存至`cycle3/scheduler_before_profile_derived_admission/`，新plan增加调度入口/资源公式source绑定，SHA`4c60d689b6ecaf61c86b57bd6f306c7b2d47418c44965e151859cee1c122ca57`；任务、inputs、proposals及generation不变。调度器变为PID1077744，已有GPU2/3 watcher继续运行。

18:58:14 M4在GPU0启动PID1077756，原配置下已实际完成首题三臂；后续M5按55GiB同样检查。只按已确认无model launch的CPU等待状态交接，未碰其他用户GPU进程。公式正确性/参数不变检查与6项mock交接回归通过，首批实际入口另存研究包。后续真实加载/调用/退出验收补在CF-MoA研究记录；这不是降低模型资源、修改采样方法或新得分。


19:04实测交付：M4与M5均成功完成并关闭，原engine_kwargs与各自query阶段逐字段相同。M4→M5的gpu0 generation0001曾held、按STOP安全released；M5关闭后generation0002在19:03:46 held 56.4541015625GiB，holder PID1080980，实时nvidia记录约58126MiB进程用量（包含CUDA上下文），未动hzh PID916438。GPU2/3各watch仍holders=[]，等待其他用户真实作业释放。调度PID1077744及离线收尾已结束；独立watch继续运行，停止占位可向对应活跃generation写STOP。完整源码/配置/新旧调度差异、实际固定KV及补占证据见cycle3/profile_memory_live_receipt.json。两次具体成功不是50/55GiB的普适峰值证明，后续依然逐次核对实际余量。


19:10补充实时状态：GPU2/3在其他任务释放后于19:08:24自动各held80GiB，holder分别1082803/1082800。GPU1出现整卡空闲后也按用户“未使用时占位”要求启动同脚本固定watch；导入torch并复查时已有其他新任务，按余量动态held68.0634765625GiB，holder1084444、watcher1084437。GPU0保持56.4541GiB，四个holder活PID与ready均核验，记录在cycle3/gpu_reservations_after_analysis.json。既有脚本hold_hours=0表示无限持有，ready中release_at恰为启动时刻是旧展示字段，不能把它当真实释放期限；未更改脚本行为，停止仍用各活跃generation/STOP。实验进程和离线收尾均已退出，只有资源占位继续。


### 2026-09-23 20:20：第四轮复用占位交接

用户继续新计划，沿用[既定占位策略](#gpu-reservation-handoff-20260923)。第四轮准备前再次核验四个自有watch/holder PID及ready，2/3仍各80GiB。新运行包`effect_first_revision_20260923/cycle4/run_reserved.py`直接复用第三轮调度函数与原占位脚本，接管已结束队列的watch身份；仅按原STOP机制释放实验所需卡，并在engine显式closed后启动新代占位。0/1现有占位继续，未终止其他用户进程。入口继续使用已实测profile公式的50/55GiB调度估计，模型配置和固定KV不改。新队列PID1116086，实时状态归`cycle4/queue_status.json`，旧资源快照保留但不能作当前存活证明。方法和最终费用归[研究主记录](research/cf_moa.md#effect-first-cycle4-20260923)。

第四轮资源终态：M4 PID1116127/GPU2、M5 PID1116212/GPU3均complete且engine_shutdown/journal_closed，调度PID1116086正常结束。每卡关闭后原脚本自动创建cycle4新代占位，2/3各80GiB实际ready+活PID核验通过；holder分别1117789/1118233，0/1仍1080980/1084444。四卡状态记录在`cycle4/gpu_after_models.json`，它是核验快照，不替代下次操作时的活进程核查。此次0其他用户任务干预，0模型配置缩减；研究费用/失败归主记录。


<a id="cf-moa-effect-first-v3-github-20260923"></a>

### 2026-09-23：释放GPU0/1与版本3完整过程发布及验收

用户明确要求释放GPU0/1，并将截至当前全部进展和细节写成文档上传GitHub。核验已结束的C3/C4调度器没有存活、watch/holder属于当前用户且PID/start_ticks/父子关系/参数/ready匹配后，仅向各自状态目录写STOP。GPU0 watch1080975/holder1080980、GPU1 watch1084437/holder1084444均已退出；2/3原watch1117784/1118228与holder1117789/1118233保持。释放后瞬时可用GPU0 59857MiB、GPU1 79425MiB；其他用户仍在使用这些卡，不称整卡空闲。未来自动占位范围改为2/3，禁止无新授权自动重占0/1。旧C4完成收据/资源快照不覆盖，新事实另记[释放收据](../Documents/Codex/2026-09-21/cf_moa/publication_v3_20260923/gpu_release_receipt.json)。

本次在既有CF-MoA完整过程报告增加效果优先四轮研究与当前交付状态；拟发布独立版本3目录，保留版本1/2、正式v5、历史结果和各次失败。公开范围仍为完整过程文档、当前核心计划、来源哈希、精简分数/失败/成本及不含答案正文的逐输入状态；患者全文、gold、隐藏配对端、完整模型响应、SQL、大型语料和模型权重留本地。整理及发布0新模型、0原生重评分、不恢复任何候选推理。


21:57发布完成：[版本3完整报告](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-23_cf_moa_effect_first_v3/docs/research/cf_moa_experiment_report.md)与[公开包](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-23_cf_moa_effect_first_v3)已提交到`xiotakut/cf_mrg`的`main`，提交`31069fca680fd41394777fbf683dd50546ea6c8c`。独立工作树`Documents/Codex/2026-09-23/cf_moa_github_publish_v3`从用户最新远端`74c0cbc`创建，仅新增版本3目录与两处导航；用户新计划及前两版38文件保持逐字不变。原本地main和此前工作树未改。20文件包＋2导航共22远端Git blob经base64解码逐字节核验，远端main/树与本地一致，工作树干净。

报告共1405行，保留1–11章并新增四轮开发与总验收；状态元数据2546行、92质量组、294同范围比较、488配对汇总组，54来源SHA均核对。四轮新增2203次、17716744输入/160997输出token仅为四轮物理小计，不冒称全部历史成本。公开数据不含病例/答案/gold正文；完整trace、模型原文和执行源码保持本地证据索引。独立审阅确认负结果、旧失败分母、C3/C4诊断有限键未实现和独立评估未开展等限制均保留。

发布工程修复：数据验证脚本原先每次重写validation，已改默认只读，显式`--write-report`才生成收据；最终Git空白检查发现CSV使用CRLF及生成脚本一行尾空格，改生成器固定LF、去尾空格，前后CSV全部解析值一致。初次失败日志`initial_diff_check.log`保留，最终`final_diff_check.log`为空且退出0。不是方法或实验数据调整。本次还修正文档520调用的两骨干合计口径、两组应变端点误配及Scope32分母措辞，原评分与配对元数据未改，研究说明见主记录。

本地[发布验收收据](../Documents/Codex/2026-09-21/cf_moa/publication_v3_20260923/publication_receipt.json)、[独立审阅](../Documents/Codex/2026-09-21/cf_moa/publication_v3_20260923/independent_review.json)、[发布检查](../Documents/Codex/2026-09-21/cf_moa/publication_v3_20260923/package_check.stdout.json)和remote_verify下载文件保留。发布新增模型/检索/原生重评分均0。GPU0/1自身进程已退出，2/3各80GiB保留；不自动重占0/1。公开文档为提交前固定快照，发布成功及最终远端收据在本节记录，不为了写回发布身份修改其来源哈希。


### 同日23:02：最简修订两批GPU完成，保留2/3占位

本次用户授权完整执行最简head复用计划，使用2/3完成历史121固定B/F两新seed及自然52三seed。`Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923/run_gpu_phase.py`仅复用既有gpu_watch交接函数，限定GPU2/3，启动前核验owner/PID/start_ticks/卡号/ready，只STOP自有holder，按原readout资源准入复查后并行两骨干。每骨干多seed共享一次原profile引擎；seed、SQL、成本身份分开。第一批与第二批之间均显式engine_shutdown，最终各卡按原脚本补占。

两个phase全部exit0、engine/journal closed，231次真实生成的研究费用和效果见[最简研究记录](research/cf_moa.md#minimal-head-reuse-20260923)。GPU2新watch1167787/holder1167792，GPU3 watch1167250/holder1167255，generation0004各80GiB，23:02活进程/ready联合核验通过；[资源终态收据](../Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923/gpu_final_receipt.json)。GPU0/1始终未启动/重占，未向其他用户任务发信号。持有显存不计为模型计算，后续操作仍需核验真实活状态。


<a id="cf-moa-minimal-v4-github-20260924"></a>

### 2026-09-24：版本4最简复用完整报告与交付索引发布

用户要求将完整报告第14章、代码/配置/逐题trace/成本交付索引及刚完成运行的过程和结果整理上传GitHub。本次在独立工作树`Documents/Codex/2026-09-24/cf_moa_github_publish_v4`从远端main创建新增版本4包，版本1–3保持不变。发布包含完整报告及主记录快照、核心计划、已冻结本轮源码/配置、原99项交付索引和可公开定位映射、逐输入状态及231条调用元数据、质量/成本/错误与未采用决定。完整病例、gold、模型请求/响应正文和SQL仍按既有公开范围留本地，清楚标注未公开，不将元数据称为完整模型trace。准备与验收证据归`Documents/Codex/2026-09-24/cf_moa_publication_v4/`。本次0新模型、0原生评分，不改变采用身份或GPU占位状态；推送和远端核验完成后补充最终收据。


发布完成：`xiotakut/cf_mrg`的`main`提交`378665328e9509ca76a4b09f943b868cc20350b7`，新增[版本4完整报告第14章](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_minimal_v4/docs/research/cf_moa_experiment_report.md#minimal-head-reuse-v4)、[运行过程与交付导航](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_minimal_v4/RUN_AND_DELIVERY.md)及[公开99项索引](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_minimal_v4/data/public_delivery_index.json)。47个包文件＋2处仓库导航共49个GitHub Git blob以base64解码后逐字节一致；远端main/树与本地提交匹配，工作树干净。前3版58文件保持SHA不变，未改远端既有计划或历史成绩。

发布包保留完整报告1544行（含发布说明）、主记录快照、6个冻结源码/配置文件、原始99项索引和逐项公开映射、1384条B/seed状态、231条新增调用元数据，以及16组质量/原生单元/配对与10个run费用。公开标准库校验通过160个相对链接、文件哈希、完整分母与1444680/31047 token加总。源码只作为有限可审查快照，依赖旧head/环境，不称独立可运行软件包；metadata trace不冒充完整模型trace。此次0新模型、0原生评分，不操作GPU。

发布投影守卫在成功导出前拦截工程诊断字段名`reason`与含prompt对象的`engine_accepted`：仅公开字段改为`diagnostic`与布尔受理标记，原实验内容和分数不改。CSV固定LF，校验器只读自身manifest列出的数据，可与原始索引并存；最终Git空白检查、文档审阅与独立数据审阅均通过。完整敏感请求/响应、gold和SQL继续留本地，公开清楚区分byte_identical、metadata_projection、local_only。

旧99项索引不刷新，23日绑定的主文档字节已在本次`source_document_snapshots/`保存，位置与SHA见[source_document_archive.json](../Documents/Codex/2026-09-24/cf_moa_publication_v4/source_document_archive.json)。本次发布后的长期主记录续写不会伪装成当时字节。最终[发布收据](../Documents/Codex/2026-09-24/cf_moa_publication_v4/publication_receipt.json)、[公开包核验](../Documents/Codex/2026-09-24/cf_moa_publication_v4/package_check.stdout.json)、[独立数据审阅](../Documents/Codex/2026-09-24/cf_moa_publication_v4/publication_data_review.json)及remote_verify下载副本保存。研究结论仍为等价B包装通过、普通F重答未采用；不重开实验。

<a id="cf-moa-v4-diagnosis-github-20260924"></a>

### 2026-09-24：v4诊断源码、结果与规划模型阅读入口补发

用户指出仅交本地私有压缩包，其他模型无法通过GitHub阅读。本次直接补发可公开的实际调用链源码、运行版本diff、全部95组合/285 seed记录的分析元数据，以及自包含结论和阅读入口。既有私有294文件包保持原字节，不将省略正文的投影称为完整请求/响应；原病例、检索材料和完整raw/gold附件不默认转为公开。新增发布包`benchmarks/2026-09-24_cf_moa_v4_diagnosis`，独立工作树`Documents/Codex/2026-09-24/cf_moa_github_diagnosis_v4`从远端`3786653`创建，既有四个实验版本不改。发布准备与验收归`Documents/Codex/2026-09-24/cf_moa_diagnosis_publication/`。0新模型/评分、0旧head回放、默认配置与GPU状态保持；推送验收后补记远端提交。

10:23发布验收完成：`main`提交`28ea62fec289780b442dea01b6ba04badd21b3be`；[GitHub阅读入口](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_v4_diagnosis/README.md)与[直接文本入口](https://raw.githubusercontent.com/xiotakut/cf_mrg/main/benchmarks/2026-09-24_cf_moa_v4_diagnosis/README.md)均可供其他模型阅读。101包文件＋2导航共103文件已对远端Git blob身份与本地字节hash核验；入口、诊断报告、源码说明和选择表另做无认证raw逐字节下载校验，前四包105文件SHA保持，工作树干净。[发布收据](../Documents/Codex/2026-09-24/cf_moa_diagnosis_publication/publication_receipt.json)保存提交与逐文件身份。

源码审阅确认73份调用链文件可原字节发布；来源收据中一条通用选项文字的历史parser失败片段保留并说明，不声称没有任何响应片段，但无完整病例/检索/原始请求响应。数据白名单投影16文件保留95组/285行、35修复/40误伤/0新增键覆盖及既有费用；CSV只转LF，解析值与原表完全一致。原diff文件14处空白上下文和导出脚本一处末尾空行触发`git diff --check`，为保持冻结证据原字节明确保留；新文档与数据空白检查通过，警告原文存`preserved_source_whitespace.log`。这不是模型/方法修复。私有zip SHA未变、未上传；没有新推理/评分或GPU操作。

<a id="cf-moa-candidate-verification-github-20260924"></a>

### 2026-09-24：候选验证完整报告、运行过程与交付索引发布

用户要求把已完成新计划的完整报告、代码/配置/逐题trace/成本交付索引和刚刚运作过程整理上传GitHub。本次在既有完整报告增补第15章，独立工作树`Documents/Codex/2026-09-24/cf_moa_github_candidate_verify`从远端main `c4659d5`创建，新增`benchmarks/2026-09-24_cf_moa_candidate_verification`，不把这次研究命名成正式V5。已核验原116项交付哈希，并将其中两份可续写docs字节保存到`Documents/Codex/2026-09-24/cf_moa_candidate_publication/source_document_snapshots`，避免发布后的续写破坏旧索引解释。1171个既有benchmark/plan文件在发布前锁定保留（两处仓库导航单独更新）。

公开范围为完整过程报告与主记录快照、实际推理/分析源码与版本diff、两骨干配置、40组质量与成本、3460逐输入状态/4180原生映射/780新调用/190候选结果等白名单元数据及原116项公私映射。完整病例、检索材料、实际messages/response、gold、输入token IDs、SQL和模型权重继续留私有；公开投影不冒充完整模型trace。原32初始化失败和8回退单列。发布准备与核验收据归`Documents/Codex/2026-09-24/cf_moa_candidate_publication`；本次0新模型/评分、不操作GPU或自动队列，推送及远端核验后补记提交。

准备阶段一次Git文件清单读取使用默认文本转义，含中文文件名被引号/转义导致路径打开失败；改为`git ls-files -z`正确读取，旧文件及实验结果未修改。此发布工具错误保留于preparation_notes.json，不归类为方法运行失败。

15:07发布及远端验收完成：`xiotakut/cf_mrg/main`提交`854f00b8e6df4df774e0cfb94c0db3a2d1a4fb8d`。新增[完整报告第15章](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/docs/research/cf_moa_experiment_report.md#candidate-verification-execution)与[运作过程和交付索引](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/RUN_AND_DELIVERY.md)，79包文件＋2导航共81个GitHub Git blob逐字节与本地一致；远端main/树匹配，隔离工作树干净。1171个既有benchmark/plan文件保持原SHA。另对README、完整报告、运行交付、公开索引四个raw链接作无认证HTTP读取，均200且字节相同，可直接给其他模型阅读。

公开核验通过174相对链接、40结果组、3460逐输入状态、4180原生映射、780真实取分调用及5,504,408/780 token、190候选执行、31旧审阅组和4固定新反例。原116项索引逐项保留路径/哈希并标记42原字节、16投影、58本地，完整私有trace没有伪装成公开。运行时与最终分析版本分别保存，780条output_kind从0到2的vLLM返回模式归一明确解释。方法结论不变：带理由有开发选择收益、仍无稳定默认采用，正式v5与旧B保持。

发布审阅修正第15章一处“自然M5 d00050”为“历史M5”，数据与分母原本正确；两处指向公开反例投影的文字增加“完整内容未公开/服务器制品/仅公开元数据”，原私有制品不动。CSV改LF且3460解析行逐字段相同；两份冻结diff的3个空白上下文保留原字节，其余最终Git空白检查通过。全部初次检查和修复记于publication_preparation_notes、document_review及publication_data_review，不归为新实验失败。

最终收据：[publication_receipt.json](../Documents/Codex/2026-09-24/cf_moa_candidate_publication/publication_receipt.json)、[无认证可读核验](../Documents/Codex/2026-09-24/cf_moa_candidate_publication/anonymous_read_receipt.json)、[公开包一致性核验](../Documents/Codex/2026-09-24/cf_moa_candidate_publication/package_check.stdout.json)。本次发布0模型调用、0原生重评分，不操作GPU或恢复自动队列。运行原116索引及之前文档字节保持历史身份；公开快照固定于提交前，后续主记录续写不反写其哈希。


<a id="cf-moa-rcv-progress-github-20260925"></a>

### 2026-09-25 01:02：RCV收口执行中快照发布

沿用用户明确的GitHub交付授权，在完整v5模型作业运行期间发布可审阅进度包，未将其标为最终完成。[第16章](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-25_cf_moa_rcv_completion_in_progress/docs/research/cf_moa_experiment_report.md#rcv-completion-in-progress)、[开发五表](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-25_cf_moa_rcv_completion_in_progress/data/tables/five_tables.md)、[交付索引](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-25_cf_moa_rcv_completion_in_progress/data/public_delivery_index.json)及本轮实际调用链源码/配置，位于新增`benchmarks/2026-09-25_cf_moa_rcv_completion_in_progress/`。提交`10b699b20769ea61a59d2f4a066e2c6cd9fec32b`，从用户计划所在`d14ba2a`普通快进推送，原benchmarks和plan均不修改。独立工作树为`Documents/Codex/2026-09-24/cf_moa_github_rcv_progress`。

163文件共3,777,360字节；115源码映射去重107实际运行源码/配置，包含补齐的采用F。公开1194配对atom、630家族效应、1730 C1–C5状态元数据、已完成C5与M4 C0新增费用、闭合分片成本和活动状态数值快照。当前db06全量driver与未来未安装callback复用driver分别标识。完整题面/messages/F池/raw/gold/SQL及26组原文引文留私有，并有明确路径索引；公开元数据不冒充完整trace，源码不是跨机器开箱即用环境。

发布前独立检查所有manifest绑定、145原字节副本、56 JSON/JSONL、101 Python AST与公开字段范围；最后仅修五表两处“全v5完成”为“分支完成/全系统未完成”，数字与原表保持。推送后fetch核验远端main同提交、163 Git树文件逐字节相同，五个关键raw入口无需认证HTTP200且字节一致。`SOURCE_MANIFEST.json` SHA256为`3d1af3216ebed55e44fc12149f76e32fc24d0222845c8dacceeb44f677e920d6`。完整收据见[publication_receipt_20260925.json](../Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/public_preparation/publication_receipt_20260925.json)。

此发布0模型/0grader、未操作健康GPU任务，旧默认B保持。完整v5仍在GPU1/M4、GPU2/M5并行，确认未冻结/未运行，M5自然C0四条仍等容量，不能用已完成开发表替代这些未完成分母。研究事实继续归[当前研究记录](research/cf_moa.md#rcv-completion-20260924)，最终结果完成后另行交付。

同日补充两级仓库导航，提交`b58ed3efc12fca206fb8d6dcdfc3f9056ff2088a`：仅在根README及benchmarks/README增加执行中入口，原文本逐字保留、163文件包不变；远端Git与两个raw入口字节验收。证据`public_preparation/navigation_publication_receipt_20260925.json`。


<a id="cf-moa-rcv-full-v5-github-20260926"></a>

### 2026-09-26：RCV完整v5结果、运行过程与交付索引发布

用户要求将新计划报告、代码/配置/逐题trace/成本索引与最近运作结果上传GitHub。在既有独立工作树`Documents/Codex/2026-09-24/cf_moa_github_rcv_progress`从远端`b58ed3e`建立`publish/rcv-full-v5-20260926`，新增包`benchmarks/2026-09-26_cf_moa_rcv_full_v5`，仅另改根/benchmarks导航。普通快进推送提交`d85793470cf75af57217f3fdc73093f494d9f003`；历史benchmark及用户plan不改。

[完整报告](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-26_cf_moa_rcv_full_v5/docs/research/cf_moa_experiment_report.md#rcv-full-v5-results-20260926)保留09-25阶段，新增16.8–16.12完整结果、M4监听错误/恢复、M5两次初始化失败及三卡尾片；[运行与交付索引](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-26_cf_moa_rcv_full_v5/RUN_AND_DELIVERY.md)提供实际源码/profile、六臂质量、166860逐输入状态、成本与私有trace位置。完整原文/SQL留私有，公共持续主记录仅为导航。

269文件，除manifest外7824777字节；134 Python AST、110 JSON、4714普通JSONL行、671756 gzip行检查通过；232原字节副本和10份压缩前哈希一致。107旧运行源码/配置与实际来源一致，19成本状态SHA/字段匹配。远端fetch确认main同提交，269文件逐字一致；7个raw入口含文档/索引/profile和gzip无需认证HTTP200且字节匹配。manifest SHA256 `b3f402d3ec45ea83270cc5870b3a01a812b08309b3b654ccee43dfe3cdc1e803`。

发布初检因旧manifest transformation=null出现一次AttributeError，限定空值处理后通过；本地记录脚本一次f-string引号错误在执行前失败，修正后记录。4份冻结测试源码EOF空行保留原字节，其余Git空白检查通过。报告消除GPU顺序歧义，质量不变。以上均为出版工具/表述处理，不是新实验或方法调参。

[远端收据](../Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/public_preparation/full_v5_publication_20260926/publication_receipt.json)、[成本清单](../Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/public_preparation/full_v5_publication_20260926/cost_inventory.json)、[包内核验](../Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/public_preparation/full_v5_publication_20260926/package_validation.json)。本次0模型/评分/进程操作，不改变GPU占位和自动实验队列。完整回归完成不等于冻结后确认或整个研究计划完成；旧默认B保持。


<a id="cf-moa-transparent-closeout-github-20260928"></a>

### 2026-09-28：完整v5零新增推理透明收尾发布

按用户收尾计划及持续GitHub交付要求，发布[完整六臂结果](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-28_cf_moa_transparent_closeout/full_results.md)、[五张完整表](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-28_cf_moa_transparent_closeout/five_tables.md)、[过程报告第16.13节](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-28_cf_moa_transparent_closeout/docs/research/cf_moa_experiment_report.md#transparent-closeout-20260928)及[公共交付索引](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-28_cf_moa_transparent_closeout/public_delivery_index.json)。研究事实在[CF-MoA主记录](research/cf_moa.md#transparent-closeout-20260928)，本节只记录发布。新包`benchmarks/2026-09-28_cf_moa_transparent_closeout`含71文件，另更新两处仓库导航；原d857934完整结果包逐字保持。新增统计、全来源/格式分层、方法归属费用、166860行费用/覆盖元数据、空客观问题清单、来源收据及脚本均包含。冻结后确认、独立F复本仍未执行/延后，未因阶段结束改为完成。

`main`提交`2d56c7160337ae641fe94a65e8e279e65370f9f1`。首次普通推送因远端并发新增无关`test/`动画提交dead859被拒绝；fetch核实后对该提交clean rebase，普通快进成功，保留其两个文件，未force push。另一次出版验证命令使用缺失的python别名，在执行前退出，改用已有MedRGAG虚拟环境后通过；两者均不改变方法或实验。73个远端Git文件与本地字节一致，manifest全部哈希一致，8个文档/状态/索引/区间raw入口无认证HTTP200且字节相同，工作树干净。验证见[发布收据](../Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/closeout_20260928/publication_receipt.json)。

公开包保留全部六臂、完整分母和负结果；不上传病例、完整messages/响应、gold、私有SQL或含gold派生诊断的costs/projection。成本差异证据中六处候选键以SHA256公开，原值仅留服务器，转换在manifest登记；不将公开元数据声称为完整私有trace。JSON/AST、166860费用行和限定隐私复核通过。本轮0新模型、0grader、0GPU/既有进程操作，不重启自动队列；默认B保持、C3保留研究身份。


<a id="cf-moa-paper-github-private-20261002"></a>

### 2026-10-02：论文包上传与仓库私有化

用户明确要求“github新建个文件夹上传，同时把这个库设置成private”。目标为既有 `xiotakut/cf_mrg`，开始核验时 GitHub API 显示 public、main 分支、当前账户具备 admin/push 权限。准备从远端 `2d56c7160337ae641fe94a65e8e279e65370f9f1` 建立隔离工作树 `Documents/Codex/2026-10-02/cf_moa_paper_github`，新增 `papers/2026-10-02_cf_moa/` 并补仓库首页入口。计划在推送论文前设为 private，随后核对远端内容和可见性。

发布来源为已完成的 `cf_moa_paper_bundle.zip`，260 文件、6,480,946 字节，SHA-256 `cf7684479fc0e40d60dc76d8c41711f601143cc324116d23a00716cbff401877`。独立只读核验 ZIP CRC、259 项原清单及主要制品通过；原本地目录含构建依赖，故严格从 ZIP 提取，不递归复制原目录。GitHub 阅读入口、历史链接与复现命令需做路径适配，原 ZIP 和全部论文/图表/脚本字节保留。证据目录为 `Documents/Codex/2026-10-02/cf_moa_paper_publication/`。论文内容事实与写作过程继续归 [writing_record.md](paper/writing_record.md)。当前为准备阶段；尚未把计划写作远端成功。本次无新模型、评分或 GPU 操作。

2026-10-02 发布中间验证：已执行 `gh repo edit xiotakut/cf_mrg --visibility private --accept-visibility-change-consequences`，退出 0；认证 API 随后确认 `private=true`、`visibility=private`。操作发生在论文提交推送前，收据为 `cf_moa_paper_publication/repository_before.json` 和 `repository_after_private.json`。论文目录适配与上传仍在进行；历史文档中的“公开/匿名可读”描述仅代表对应发布当时的状态。

**发布完成与验收（2026-10-02 22:38:55，Asia/Shanghai）。** 新建 [papers/2026-10-02_cf_moa/](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa)，普通快进推送 main 提交 [`7308479a5b968052b64603080f14b588a5dda30d`](https://github.com/xiotakut/cf_mrg/commit/7308479a5b968052b64603080f14b588a5dda30d)，父提交仍为 `2d56c7160337ae641fe94a65e8e279e65370f9f1`。论文目录共 262 文件、16,026,920 字节，另更新根 README 导航，共 263 个提交文件；全部旧 benchmark、用户文件与既有工作树保留。内含英文 PDF/Word/HTML/Markdown、LaTeX/Typst/BibTeX、中文框架、5 组 PDF/PNG 图、8 组 CSV/LaTeX 表、复现脚本、冻结汇总与审阅证据，以及原始 ZIP。

发布副本仅对 README、REPRODUCE 和冻结写作记录做导航、历史状态说明及跨机器命令适配；256 个其他原制品逐字保持，DELIVERY_MANIFEST 重建为 261 项当前文件哈希。原清单和原始交付字节完整保留在 ZIP；新增 PUBLICATION.json 逐项记录三个文档的前后哈希及转换。旧构建/事实审阅收据仍对应其冻结输入，不冒充本次新增构建或审阅。未上传 `.build_deps`、虚拟环境或新增病例/完整请求。

在新目录实际执行 `python3 scripts/build_figures_tables.py --check-only --raw-root ../../benchmarks/2026-09-26_cf_moa_rcv_full_v5/data/full_v5 --receipt /home/data3/txy/Documents/Codex/2026-10-02/cf_moa_paper_publication/portable_check_receipt.json`，3.911 秒通过，验证 72 分类、132 来源、60 格式、24 配对与 12 方法/臂范围及原记录哈希；未改图表、评分或输入。适配文档包内链接、限定发布范围、全部暂存文件与本地字节、修改文档空白检查通过。

远端 main 与本地提交完全相同；认证 GitHub tree API 检查全部 263 个提交文件的 Git blob SHA 和字节数均匹配。额外通过 Git blob API base64 下载根导航、论文目录 README、PDF、原 ZIP、制图脚本和发布清单，6 个关键文件均与本地逐字及 SHA-256 相同。最终 API 再次确认 `private=true`、`visibility=private`；不带认证的仓库 API 返回 HTTP 404。工作树干净，未使用 force push。完整 [发布收据](../Documents/Codex/2026-10-02/cf_moa_paper_publication/publication_receipt.json)、[包检查](../Documents/Codex/2026-10-02/cf_moa_paper_publication/package_validation.json)和[可移植原记录核验](../Documents/Codex/2026-10-02/cf_moa_paper_publication/portable_check_receipt.json)保留。此次 0 新模型、0 grader、0 GPU/既有进程操作；论文结论、默认 B 及未执行独立确认的范围保持。


<a id="cf-moa-paper-latex-github-20261002"></a>

### 2026-10-02：原生 LaTeX 主稿和实际编译 PDF 更新私有仓库

用户明确要求“你不是用latex 写的？ latex写”。写作迁移、全部排版尝试与内容核验归 [写作主记录](paper/writing_record.md)；本节仅负责 GitHub 更新。沿用既有私有仓库和 `papers/2026-10-02_cf_moa/`，主修订提交 `f43db83447313eea01b0724025f5ee8fd2b7683f` 增加 34 文件的独立 LaTeX 工程、真实编译 PDF、301,880 字节的 Overleaf ZIP 与构建/审查证据。`scripts/build_manuscript.py` 改为 Python 标准库调用 LaTeX，普通构建不依赖 Markdown/Pandoc/Typst；包根 PDF 和 `latex/main.pdf` 字节相同。

正常快进后进一步发现中文框架仍指向旧 Markdown，且图4/5顺序与当前正文不同；已同步框架源入口、真实图序与公式/伪代码描述，并更新文件清单，追加导航提交 `cac3fe455678cb4f4a1b34450b3441183fdabd0f`。没有重写已推送历史或 force push。初始 ZIP、原输入、图表/表格数据及制图脚本逐字保持；旧导出 tex/typ 移至 `legacy_typst/`，旧 Word/HTML/Markdown明确为初稿冻结参考。原 `.tex` 导出未编译的历史状态保留，不冒称旧 PDF 来自 LaTeX。

发布目录现有 312 文件，DELIVERY_MANIFEST 含除自身外311项大小/SHA-256，LaTeX ZIP共34文件、SHA-256 `2dd34ccd9ccfa10a8cef9b138720e77ecf126868001241b194d7190e63c4b865`。适配文档127处本地导航链接检查通过；主修订60个Git变更文件，仅涉及根导航和论文目录。一次 apply_patch 同路径删除/新增操作被工具拒绝，目标脚本未被该失败操作改动；改用quoted heredoc写入后完成。全面空白检查提示7处沿用BibTeX标题行尾空格及3处原始TeX日志空格，作为来源/日志字节保留；其余新增代码和导航空白检查通过。这些是发布工具处理，未引入模型实验或评分。

最终认证 GitHub tree API 核对整个论文包312文件与根导航共313文件，全部 Git blob SHA及本地字节匹配；远端 main 等于最终提交 `cac3fe455678cb4f4a1b34450b3441183fdabd0f`，工作树干净。主修订阶段另经 Git blob base64 下载 `.tex` 主稿、PDF、LaTeX ZIP、BibTeX、构建脚本和清单6文件逐字核验；最终导航提交另下载中文框架、README和清单3文件逐字核验，其余制品由最终完整tree校验保持。API再次确认 `private=true`、`visibility=private`。完整 [发布收据](../Documents/Codex/2026-10-02/cf_moa_paper_latex_build/publication_receipt.json)与[包检查](../Documents/Codex/2026-10-02/cf_moa_paper_latex_build/publication_package_check.json)保存范围。此次0模型/评分/GPU或既有作业操作。

<a id="seven-system-paper-github-20261003"></a>

## 2026-10-03 七系统论文范围修订发布

用户要求查看全流程并指出此前论文遗漏七方法，沿用已明确授权的同仓库论文目录更新。研究范围纠正、数值审阅与编译过程归[写作主记录](paper/writing_record.md#seven-system-scope-correction-20261003)，本文只记发布。隔离 Git 工作区仍为 `Documents/Codex/2026-10-02/cf_moa_paper_github`，目标 `xiotakut/cf_mrg/main` 的 `papers/2026-10-02_cf_moa/`；未 force push，推送前确认与远端无分歧。

主修订提交 [`a03f55c`](https://github.com/xiotakut/cf_mrg/commit/a03f55c86a993163dcd0cd44347b59d3f370b01a)恢复七基线与七系统 R1–R3 实验，添加三表一图、四项方法引用、全流程附录、冻结汇总、来源哈希和离线复现脚本；原五图八表、原始 ZIP、早期格式与实验发布保持。上一版原生 LaTeX ZIP/发布清单另存 `evidence/latex_20261002/`。

发布首轮清单因只按文件名排除自身，漏列了嵌套归档中的同名旧 manifest；该旧文件一直实际存在且远端内容已通过核验。将排除条件收窄到根清单自身后，以 [`bb5a017`](https://github.com/xiotakut/cf_mrg/commit/bb5a0175c64c2030f3b0896f01fc30702220c6b4)补齐。最终包 350 文件，主 manifest 列其他 349 文件；40 个 LaTeX 工程文件与 canonical 逐字一致。`git diff --check` 的例外仅为冻结 CSV 的 CRLF、原 BibTeX 结尾空行与真实 TeX 日志空白，未为消除提示修改来源字节；其他写作/脚本文件检查通过。

最终远端 `main` 为 `bb5a0175c64c2030f3b0896f01fc30702220c6b4`，GitHub API 确认 private=true。350 个包文件及根 README 共 351 文件逐项对上远端 Git blob SHA-1 和字节数，主清单 349 条 SHA-256 全核；7 个关键文件已下载字节核验，最终清单更新后再次下载验证，其余六项字节未变。工作树干净。证据：[最终 GitHub 核验](../Documents/Codex/2026-10-03/paper_scope_audit/github_verification.json)、[首轮内容核验](../Documents/Codex/2026-10-03/paper_scope_audit/github_scope_commit_verification.json)、[本地包检查](../Documents/Codex/2026-10-03/paper_scope_audit/package_check.json)。

交付：[论文 PDF](https://github.com/xiotakut/cf_mrg/blob/main/papers/2026-10-02_cf_moa/manuscript.pdf) · [LaTeX 主稿](https://github.com/xiotakut/cf_mrg/blob/main/papers/2026-10-02_cf_moa/latex/main.tex) · [Overleaf ZIP](https://github.com/xiotakut/cf_mrg/blob/main/papers/2026-10-02_cf_moa/cf_moa_latex.zip) · [复现命令](https://github.com/xiotakut/cf_mrg/blob/main/papers/2026-10-02_cf_moa/REPRODUCE.md)。需仓库授权访问；本次没有模型、grader、GPU 或其他运行作业操作。

<a id="cf-moa-framework-github-20261003"></a>
## 2026-10-03：数据、五类体系与五agent论文框架私有发布

沿用用户已授权的GitHub目录发布和private偏好，将新框架放入[论文目录/framework](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa/framework)，未新建仓库。工作checkout为`Documents/Codex/2026-10-02/cf_moa_paper_github`；普通push到main，提交`80dcbcf234ee0bb211881baadfc77a121914d6d9`。主研究逻辑及选择决策归[论文框架](paper/outline.md)，审计与编译过程归[写作记录](paper/writing_record.md#taxonomy-benchmark-five-agents-20261003)。

发布52个framework文件及独立10成员Overleaf ZIP，包含10页英文原生LaTeX框架、中文全逻辑、三组CSV/TeX数据表、两组PDF/PNG图、冻结输入与脚本、三条审计、独立审阅、相关主记录和两份全过程报告的冻结快照。新框架尚未扩写为新完整稿；上一轮28页PDF、原生main.tex、原40成员LaTeX ZIP及最早bundle全部原字节保持。更新导航和PUBLICATION.json，把“框架”与“上一版完整稿”分开。

远端验收：GitHub API确认`private=true`，main与本地HEAD一致；论文包403文件加根README共404个blob逐项匹配，402项delivery manifest验证，另下载.tex/.pdf/中文框架/ZIP/manifest/主表CSV六文件逐字一致，工作树干净。[验收收据](../Documents/Codex/2026-10-03/paper_story_alignment/github_verification.json)。发布只上传已有数据衍生的框架和证据，无新增模型调用、评分或GPU操作。
