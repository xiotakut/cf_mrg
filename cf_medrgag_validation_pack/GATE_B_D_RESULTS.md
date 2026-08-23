# Gate B–D 实验结果

## 结论

balanced60、seed 13 的真实 pilot 已完成。Gate C 的 oracle 检查通过，但 Gate D 只满足 1/4 个冻结推进条件，因此 **NO-GO：停止在 Gate D，不进入 Gate E 的全量三种子实验，也不支持 textual clinical world model 表述**。

Gate C：M12 oracle 为 30/60（50.00%），M2 为 17/60（28.33%），提升 13 题、21.67 pp，超过 2 pp 门槛。

Gate D 的最佳非 oracle 方法是 M10，而不是完整方法 M9：M10 为 23/60（38.33%）、PairAcc 7/18（38.89%）；M9 为 21/60（35.00%）、PairAcc 5/18（27.78%）。

## 主结果

所有方法使用同一组 60 个 item；PairAcc 只统计其中 18 个成员完整的 pair。

| 方法 | Accuracy | PairAcc |
|---|---:|---:|
| M0 | 21/60 (35.00%) | 6/18 (33.33%) |
| M1 | 21/60 (35.00%) | 6/18 (33.33%) |
| M2 | 17/60 (28.33%) | 4/18 (22.22%) |
| M3 | 17/60 (28.33%) | 3/18 (16.67%) |
| M4 | 15/60 (25.00%) | 4/18 (22.22%) |
| M5 | 20/60 (33.33%) | 6/18 (33.33%) |
| M6 | 21/60 (35.00%) | 6/18 (33.33%) |
| M7 | 22/60 (36.67%) | 6/18 (33.33%) |
| M8 | 22/60 (36.67%) | 6/18 (33.33%) |
| M9 | 21/60 (35.00%) | 5/18 (27.78%) |
| M10 | 23/60 (38.33%) | 7/18 (38.89%) |
| M11 | 22/60 (36.67%) | 6/18 (33.33%) |
| M12 | 30/60 (50.00%) | 5/18 (27.78%) |

M9 相对 M2 为 +4/60（+6.67 pp）和 +1/18 pair（+5.56 pp），但这不足以通过机制检验：

| 冻结条件 | 结果 | 判定 |
|---|---|---|
| M9 严格优于 M3 和 M5 | 21 > 17，21 > 20 | PASS |
| shuffle 使完整 PairAcc 至少下降 1/18 | M9 5/18，M11 6/18；反而上升 1 pair | FAIL |
| MedEinst trap 至少 +1/10，control 不下降 | M2 为 1/10、1/10；M9 为 1/10、0/10 | FAIL |
| CLIR t6+t7+t8+t10 比最佳等预算基线至少 +1/8 | M9 3/8，M8 3/8 | FAIL |

M9 还低于 M8 的整体 22/60、6/18；去掉 grounding/provenance gate 的 M10 又高于 M9。这组 pilot 没有显示完整 transition/comparator 机制带来稳定收益。

## 运行与验收

- 样本：MedPIC 10、CLIR 10、MedEinst 20、MedCounterFact 16、ReMedQA 2、CPV 2。
- 模型：本地 Meta-Llama-3.1-8B-Instruct，32k context，reader temperature 0。
- M3–M11 各 60/60 unique；预测 null/empty 均为 0，reader 540/540 均 `finish=stop`。
- state/action 共 254 个候选；retrieval 1,016 条 query record；每题固定 5 个 context 槽位。
- grounded cards 254/254、parametric cards 254/254 均通过严格 schema；M11 的 254 个 action/effect bundle 全部实际错配且 action 本身保持不变。
- M4 的 60 题 auxiliary completion 与 M9 逐题等 token，总计 258,356 tokens，误差为 0。
- Gate D 总 LLM token：4,108,920。
- 单元测试 27/27 通过；`py_compile`、`git diff --check` 通过；GPU 0–2 已释放。

## 产物与复现

- 汇总：`results/gate-b-real-20260824-seed13-v4/canonical-comparison-M0-M12.json`
- 原始预测、逐项评分、summary 和中间缓存：`results/gate-b-real-20260824-seed13-v4/`
- 固定样本：`configs/balanced60_seed13.json`，SHA-256 `c16f7828466ca5dc1165e255f2a9d42fc2b3b8cf211503595a35490bb7f0a0f9`
- Gate D runner SHA-256：`f49e91f22cbc67940912bc01dd3058495fd53df4e4af7db4e385f4efad9921d8`
- 汇总 SHA-256：`3141c60ff63efc9065cf277249babcd27a5410c2d9966bd10c9fb82f89c15f1e`

重新聚合现有评分结果：

```bash
python3 scripts/summarize_gate_results.py \
  --inference results/balanced60-seed13/pilot.inference.jsonl \
  --gold results/balanced60-seed13/pilot.gold.jsonl \
  --run-dir results/gate-b-real-20260824-seed13-v4 \
  --methods M0 M1 M2 M3 M4 M5 M6 M7 M8 M9 M10 M11 M12 \
  --output results/gate-b-real-20260824-seed13-v4/canonical-comparison-M0-M12.json
```

## 结果边界

这是单种子 60-item pilot，只能用于推进/停止决策。当前公开资产没有 MedPIC 官方 pair mapping，也没有 CLIR Full-TS 和官方 edit pairs；ReMedQA/CPV 在本样本中也没有完整 pair。因此不报告这些缺失单元对应的正式机制指标或显著性结论。
