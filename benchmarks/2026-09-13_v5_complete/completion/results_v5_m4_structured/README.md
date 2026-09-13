# 新 M4：v5 全量结构约束修复重测

[最新M0/M2/M3/新M4/M5 v5完整对照](<../v5_benchmark_latest/README.md>)（2026-09-13）。

**已完成：2026-09-13 15:04:49，13,905/13,905全部新生成并完成原生评分。格式有效99.09%、原生有效79.42%、整体单元平均准确率48.20%。GPU1/2/3已释放；M6/M7保持暂停。详见[最终结果](<RESULTS.md>)。**

2026-09-13 13:52启动，用户明确授权保存M7后改用GPU1/2/3全力运行新M4，并额外监督有效率。M7已暂停，M6保持暂停。GPU0不使用。

## 范围与修复

13,905个唯一输入全部新生成，不复用旧M4或100条试跑预测。沿用冻结v5的6,104单元、13,000入选判断和15,616原生评分映射，使用evaluation_labels。已按seed20260913打散为109个不重叠分片，每片128条，末片81条。

修复源：2026-09-11工作区 `results_v5_m0_m2_m4_m5/code/m4_format_pilot.py` 的明确输出契约，以及 `m4_output_schema.py` 的逐题可见输入JSON Schema。源代码已复制到本包code/。原M4每题完整archived messages和检索证据复用，并在原system/user末尾追加同一输出契约。所有13,905输入的retrieval_question与冻结question相等，required evidence完整保留；未重新检索或更换证据。修改后的消息、schema、原生可见item及上下文截断元数据保存在inputs/。

Llama-3.1-8B-Instruct、BF16、temperature0.7、top_p1、top_k=-1、seed42、输出2048 tokens、总上下文131072。约束解码使用已安装vLLM0.8.5/xgrammar。约束会改变允许采样的token，是明确记录的方法实现修复，不宣称与原输出等价。没有添加CF/WM/adapter模块，没有修改M5。

## 三卡执行

每卡一个常驻vLLM实例，gpu_memory_utilization=.90，max_num_seqs=128，max_num_batched_tokens=16384，prefix cache和chunked prefill启用。与M7静态HF批处理不同，本运行使用vLLM调度。初次模型加载后每卡约84.2GiB整卡显存占用。GPU1/2/3共用带文件锁的分片队列，完成后自动领取下一片，不重复生成。每个分片预测原子保存；分片切换不重新加载模型。

`config.json`保存所有参数；`plan.json`保存范围、队列和100条方案选择样本ID。原始M4正式目录及M7结果保持独立。耗时等待首批正式分片测量，不用M7或试跑耗时推断完成承诺。

## 有效率监督与最终评分

每五分钟记录logs/status.json、logs/supervision.jsonl，并在对话中报告当前完成/新增/剩余、GPU0–3显存和利用率、格式有效率及原生有效率。监控按完成的唯一输入去重，所有无效和截断输出保留分母；额外记录严格JSON/Schema有效率、截断数、原因与题型分布。

格式有效与原生有效沿用既定评分器；原生有效还要求诊断进入冻结canonical映射，不等于回答正确。Schema约束结构，不能保证语义正确或避免2048token截断。100条原试跑用于方案选择，包含在全库中；`outside_selection_pilot_inputs`另列其余输入的有效率，不把该口径称为完全独立来源病例确认集。

队列不重复领取/恢复检查，以及监控对已有100条修复结果的核对通过：98格式有效、84原生有效、99Schema有效、1截断。原v5有3个共享输入对应不同gold映射，监控只去重统计与gold无关的有效性；最终评分保留所有15,616映射，不去掉冲突或修改标签。

全部分片完成后，finish.py验证13,905输入零缺失/重复，合并到M4/predictions.jsonl，调用复制的原analyze_v5.py做全部R1–R5原生评分、来源、任务和R5配对分析。最终写scores/、validity.json、complete.json和RESULTS.md。未出现complete.json表示未完成。

## 操作

```bash
cd /home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured
/home/data3/txy/MedRGAG/.venv/bin/python code/status.py
tmux -L v5-m4-structured list-sessions
```

tmux会话gpu1/gpu2/gpu3/monitor；启动命令`bash launch_gpu.sh 1`（或2/3）仅用于该卡进程退出后的恢复，勿重复启动健康进程。运行错误会保留job.error并停止该卡，先检查日志。恢复error前需记录并修正原因，将对应job置回queued；已完整保存的预测不重做。

## M7 保存点

M7在13:45暂停于1,646/13,905条（1,634正式新结果＋12复用），1,026有效、620无效、0运行失败，11个完整分片。独立汇总保存于`../results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/`；逐题terminal文件与汇总数量一致。原runs/阶段请求、事件和未完成输入缓存保留，`m7_pause.json`记录原队列状态及所属进程。M6保持52条暂停。两者均不自动恢复。
