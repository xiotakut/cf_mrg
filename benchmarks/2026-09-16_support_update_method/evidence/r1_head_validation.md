# R1冻结后验证与归因对照

2026-09-16完成。1660次新调用；本轮模型推理和离线分析全部结束。主记录：[optimization.md](../docs/research/optimization.md#r1-frozen-validation)。本包保存冻结方法、原生输入、资格、模型输出、评分与成本，不另承担长期研究叙述。

- `plan.json`：模型预测前冻结的范围与处理原则。
- `frozen_head/`：既有R1候选的代码、49目录、71规则及配置/先验快照；不按新结果修改。
- `diagnosis/`：ASCENT范围、暴露/重合及逐例R1资格；已完成47病例两骨干原生回答/目录评分及94条原输出审核；prepared.json固定指标与控制。
- `rules/`：新用药验证来源核查；旧MedPIC全467已暴露，probes/保留33端新受控机制试验及被排除初版。
- `relations_control/`：固定201问句族的普通重答与目标提示匹配对照，两骨干804新调用及配对分析完成。

准备期曾误读不存在的旧`diagnosis/experiment.py`得到文件缺失，随后按实际`run_diagnosis.py`与`audit_prepare.py`读取；没有生成错误请求。

诊断命令（既有依赖环境，GPU0持久队列）：

```bash
/home/data3/txy/MedRGAG/.venv/bin/python diagnosis/run_validation.py prepare
CUDA_VISIBLE_DEVICES=0 VLLM_USE_V1=0 TOKENIZERS_PARALLELISM=false /home/data3/txy/MedRGAG/.venv/bin/python -u diagnosis/run_validation.py queue --gpu 0
```

当前已完成，勿覆盖重跑；实际PID、日志、启动资源见`diagnosis/launch.json`、`queue_runtime.json`。首次兼容路径失败与逐字请求比较见`diagnosis/failures/initial_transformers_incompatibility/`。prepare和新队列用于空运行目录；不能在已有预测上覆盖运行。关系和规则命令由各子目录README列出。

最终机器结果见`summary.json`，成本复现：

```bash
python3 summarize_validation.py
```

诊断细节与语义审核：`diagnosis/summary.json`、`diagnosis/result_audit.md`；规则：`rules/probes/summary.json`与`RESULTS.md`；关系：`relations_control/summary.json`、`invalid_audit.json`和`offline_analysis.json`。完整结论归[长期主记录](../docs/research/optimization.md#r1-frozen-validation-complete)。三个任务的不同准确率不合成一个总分。
