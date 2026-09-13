# v5 M6 / M7 全量测试

> 发布状态（2026-09-13）：[最新五方法结果](../../v5_benchmark_latest/README.md)已全量完成，M4 采用修复版；M6/M7 均暂停。下文过程状态与执行命令按其原记录时间理解。

**06:57更新：当前活动全量为 [按阶段和长度合批的接续](<../formal_balanced/README.md>)；formal、formal_fast均已停止，勿重启。**

**2026-09-13 06:37更新：活动全量已切换至 [提高并发后的接续](<../formal_fast/README.md>)，旧formal队列已停止，勿重启。**

2026-09-13用户明确授权：用三张空闲卡运行M6、M7全量测试。约05:46（Asia/Shanghai）开始真实推理。GPU1/2初始运行M6，GPU3运行M7，GPU0保留其他用户进程。

每方法13,905个独立输入，覆盖6,104单元、13,000入选判断、15,616条原生评分映射，使用冻结v5的evaluation_labels。每方法复用12条已完成修复试跑结果（包含其无效输出），新增13,893条，共27,786条新增方法输入。

## 冻结方法

M6采用Llama-3.1-8B-Instruct，M7采用Qwen3-8B且关闭thinking，均单卡BF16 Transformers、完整MedCorp BM25+MedCPT。配置与修复试跑一致：4个输入线程、32,000 padded token合批上限；M6四轮追问、每轮请求3条；M7最多8步、topK4、sigma1.2、完整分布熵。各阶段生成预算及检索预算不变。没有CF、WM、adapter等额外模块。

`code/methods.py` 合并小批量验证的两项上游兼容性修复：M6直接消费提取模型的查询列表，允许解析失败轮次跳过后返回合法最终答案；M7无动作关键词输出作为Final Answer提议，仍经过步数及熵阈值。旧试跑源码和结果保留。`backend.py`、`runtime.py`、`common.py`与修复试跑逐字节一致；配置字段逐项一致。复用结果保留原run/config/trace来源，不重新生成答案。

标准M6全量约305,910次LLM请求和166,860次检索（实际查询数及修复/重试另计）；M7最多111,240次动作生成。已复用试跑不重复计算。M6小批量两分片吞吐分别25.06与17.29输入/小时/卡，M7旧试跑106.74输入/小时/卡。按此直接投影三卡总工作量约11天；这是非代表性小样本（包含全库最长输入）的容量估算，不是完工承诺。先前4–7天口头粗估偏乐观，全量滚动吞吐才是后续估算依据。

## 调度与恢复

剔除每方法已完成的12条试跑输入后，用固定seed20260913打乱剩余输入。每128条一个分片，每方法109个分片，总218个。已核对分片互不重叠，且与试跑合起来完整覆盖13,905输入。随机打乱只改变执行顺序，不改变benchmark选择或每题随机数规格。

`worker.py` 在队列锁下认领分片。GPU1/2优先M6，GPU3优先M7；优先方法没有待领分片后，自动领取另一方法。每张卡只有一个调度器和一个模型进程；分片结束后模型退出，再加载下一分片，避免大单片进度文件反复扫描带来的开销。每个分片完成后执行既有轨迹与成本审计。

进程级异常会将分片记为error并停止该卡工作；其他卡继续健康任务。题目级invalid/failed保留在分母，按终态完成计数。进程被外部中断而队列仍为running时，在原GPU执行同一启动命令，会继续原分片并使用已有请求和终态。error分片需先查具体日志，不能直接改成done。运行中的配置和源码不修改。

tmux socket：`v5-m6-m7-full`；会话：`gpu1`、`gpu2`、`gpu3`、`monitor`。

```bash
cd /home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal
python3 status.py
tmux -L v5-m6-m7-full list-sessions
```

实际启动入口（健康进程运行中勿重复启动）：

```bash
bash launch_gpu.sh 1
bash launch_gpu.sh 2
bash launch_gpu.sh 3
```

`logs/status.json`与`logs/supervision.jsonl`每五分钟记录进度及GPU0–3快照。每GPU调度日志为`logs/gpu*.log`，分片模型日志为`logs/imedrag_*.log`或`tcrag_*.log`；队列状态在`jobs/`。

## 完成与结果

最后一个分片通过审计后，`finish.py`自动汇总全部新结果与已复用试跑结果，再执行既有原生评分器。缺失、重复和范围错误会阻止完成标记。无效输出、运行失败均保留分母。

最终产物：`complete.json`、`RESULTS.md`、`results/imedrag/`、`results/tcrag/`。按来源、R1–R5单元平均、原题/变体和保持/改变配对分别报告；类别允许重叠。开放诊断仍采用既有canonical映射；M22仍为固定受扰动证据加外部检索协议。各分片`execution_report.json`记录新计算成本，试跑复用成本需追溯`plan.json`引用的原目录及其递归来源，不能把缓存重放时间当成模型吞吐。
