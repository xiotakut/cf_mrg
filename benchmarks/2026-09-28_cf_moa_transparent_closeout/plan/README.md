# CF-MoA 全量结果：零新增推理的收尾包

日期：2026-09-26。

## 内容

- `01_Closeout_Without_Outcome_Filtering.md`：采用版核心与RCV的真实结果、范围调整原则、论文结论与收尾步骤。
- `02_CODING_AGENT_CLOSEOUT.md`：点到点执行任务，不增加head、模型调用或原生重评分。
- `03_Verified_Aggregate_Contrasts.md`：由公开汇总数值核对的完整R类算术差值。
- `verified_summary_excerpt.json`：公开质量JSON中的选定均值字段摘录，非完整源数据下载。
- `summarize_existing_results.py`：读取已保存的JSONL/GZ，输出所有来源、所有格式与配对家族区间，不筛选优胜子集。
- `test_summary.py`：6项合成测试已通过。没有运行真实全量元数据，也没有生成真实置信区间。

## 使用

Python 3.10+，需要numpy。代码不会联网、调用模型、调用grader或修改来源数据。

```bash
python -m unittest -v test_summary.py
python summarize_existing_results.py \
  --root /实际已有目录/data/full_v5 \
  --out /新建收尾目录/results \
  --draws 5000 --seed 240924
```

`--root` 下需有 `m4/` 和 `m5/`；每个目录包含 `native_units.jsonl[.gz]`、`pairs.jsonl[.gz]`、`per_input_status.jsonl[.gz]`，可选已有 `quality_summary.json` 用于均值核对。字段按当前公开 `analyze_full.py` 核对。根目录和输出目录使用实际路径，不按本文占位符创建不存在的数据。

输出包含完整六臂各来源，不会生成建议删题名单。置信区间只描述已暴露开发样本，不消除事后选择。方法冻结和阶段收尾可以完成，但尚未运行的独立确认仍必须明确记录。
