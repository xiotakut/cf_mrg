# CF-MoA v4 公开结果与元数据

范围：2026-09-23 已完成的最简 head 复用修订；本包在 2026-09-24 从保存制品导出。发布过程不运行模型、不执行原生评分，不改变正式 v5、历史失败或原生分母。

## 结果与采用状态

| 面板／骨干 | 固定旧 B | seed 42 | seed 43 | seed 44 |
|---|---:|---:|---:|---:|
| historical121／M4 | 87/121 | 89/121 | 88/121 | 88/121 |
| historical121／M5 | 82/121 | 83/121 | 84/121 | 84/121 |
| natural52／M4 | 35/52 | 34/52 | 31/52 | 32/52 |
| natural52／M5 | 26/52 | 25/52 | 23/52 | 24/52 |

历史 121 的 seed 42 与 B/F 复用已保存结果；仅 seed 43/44 新增 108 调用。自然 52 的 B/F 复用保存轨迹，三个 seed 新增 123 调用。合计 **231 次新增物理调用、1,444,680 输入 token、31,047 输出 token**，累计模型 586.498 秒；无新增运行失败、格式修复或未知提交/用量。累计模型秒不是独占时延或能耗。实际新增原生评分映射为 247，本次发布未重评分。

自然 52 是按事先规则从已暴露 F 开发池选择的 18 个完整家族，不是盲测或独立临床验证。其中包括 4 个既有 M23_control 前提控制端点。每个新 seed 都固定 B/F，仅改变新增一步；不能称完整流水线跨 seed 验证。

121 的小幅开发收益没有迁移到自然 52，两骨干三个 seed 均退步，原生单元均分也均下降。家族 bootstrap 区间跨零，不能声称总体必然有益或有害。旧 Scope32 反例也保留：M4 31/32→30/32，M5 31/32 不变。

默认交付等价旧 B 的 `adopted_B_five_operations_v1`；普通 F 分歧重答保留为默认关闭的控制开关，未采用为稳定增量。A1/A2 是同一旧规则核的正负操作分解，不是两个新模型；A3/A4/F 直通，取消全局生成式改答。全部既有负结果保留。

## 文件与口径

- [quality_summary.json](quality_summary.json)：两个面板 × 两骨干 × B/三个 seed，16 组完整计数、修复/误伤、家族/来源/格式分层、原生均分与 bootstrap。
- [per_input_status.csv](per_input_status.csv)：1,384 条逐输入元数据；历史 968＋自然 416。含分母成员、方法/seed、来源家族、评分状态、修复/误伤、调用数量和答案摘要哈希，不含答案正文。M5 d00050 在 B 与三个 seed 均为 unavailable/not_scored，保留分母，不归为答案错误。
- [new_model_call_trace.csv](new_model_call_trace.csv)：本轮 231 条真实物理调用的元数据、引擎受理标记、实际采样 seed、参数、token、耗时、finish 状态与请求/响应 SHA-256。`engine_accepted` 是原引擎受理对象存在的布尔值；不公开其含 prompt 的对象。`physical_request_hash` 沿用私有日志原哈希；其他 `*_sha256` 按导出脚本注明的字节或规范 JSON 算法计算。历史 seed42 调用不冒充本轮新调用。
- [cost_summary.json](cost_summary.json)：每个方法的旧 B/F 成本归属与每 seed 额外费用，另列本轮物理总账。不能把跨 seed 重复归属的 B 费用相加为新增成本；自然旧 F 的未记录时间保留 null。
- [pair_summary.json](pair_summary.json)：固定配对 ID、端点 ID、关系与保存的计数。配对和关系元数据只用于离线分析，不进入推理。历史 121 的 4 个应变对均不受 F 支持；自然仅 2 对受支持，不能以小组 0/2 确认总体能力为零。
- [native_unit_metrics.json](native_unit_metrics.json)：已保存的逐原生单元得分与汇总，74/18 个非参考 ALL 单元；R 分类是离线分组且相互重叠，不能相加或视为在线路由输入。
- [failure_and_limitations.json](failure_and_limitations.json)：采用决定、旧不可用身份、缓存准备错误、家族聚类修复与限制。初次 historical121 错把 source_family 当 family，得到 31；修正为 group_id 的 40 家族，只重聚合既有得分，修正过程 0 次重评分。
- [source_manifest.json](source_manifest.json)：来源文件标识/字节数/SHA-256 与公开制品哈希。
- [verification_receipt.json](verification_receipt.json)：下面离线校验器的实际通过收据。

## 公开核验

在本发布包根目录执行，Python 标准库即可，无网络或模型依赖：

```bash
python3 scripts/verify_publication_data.py --data-dir data
```

校验器默认只读，JSON 输出到 stdout，不在 Git 工作树写文件。它核对公开制品哈希、1,384 行、16 组质量/原生单元/配对汇总、10 个新增运行成本组、231 调用、token 与费用归属；不从患者输入重算临床正确性。发布数据没有完整原文/提示、模型回答、gold 标签、token ID、SQL；因此公开核验是保存统计的一致性检查，不是独立重现实验。

重建导出需要原始私有保存目录；`scripts/build_publication_data.py` 只做字段白名单投影与哈希，不调用模型或 scorer。来源元数据含哈希/标识不表示原始病例和回答在本包公开。

发布准备期白名单守卫先后拦截了工程诊断字段名 `reason` 和包含请求对象的 `engine_accepted`。前者改名 `diagnostic`，后者改为布尔受理标记；成功导出前没有接受含原文的数据。这是发布投影代码修正，原模型输出、评分、成本及全部实验身份均未变化。
