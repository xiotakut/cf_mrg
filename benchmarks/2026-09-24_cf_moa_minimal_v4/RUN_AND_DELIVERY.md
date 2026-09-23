# 本轮运行过程、结果与代码／配置／trace／成本交付

发布日2026-09-24；运行和分析于2026-09-23完成。本文是发布包的操作与证据导航，研究正文为[完整报告第14章](docs/research/cf_moa_experiment_report.md#minimal-head-reuse-v4)。原始[99项交付索引](data/delivery_index.json)在23:12生成，10个固定运行全部结束；[公开映射](data/public_delivery_index.json)逐项区分原样公开、元数据投影和未公开制品。它保留当时SHA，不因本次发布改写历史身份。

## 1. 实际完成的顺序

1. **更新核心计划和保留旧版本。** 当前方案为`minimal_head_reuse_revision_20260923`；正式v5、原生评分、旧采用A2/A3/A4/F和全部失败身份保持。旧知识审计A1、自由诊断改写、全局生成式聚合和多轮提示网格不再进入默认路径。
2. **包装旧B，分解同一个规则核。** A1导出MET补入，A2导出CONTRADICTED撤销；共享一次事实提取和规则执行。特殊分支仍由旧assemble决定。目录、模型执行和F直接返回采用输出。242条保存B接口相同，18次同响应规则回放通过，F开关纳入后17项局部测试通过。这是包装等价证据，不是新增正确题。
3. **精确绑定唯一F普通重答控制。** 复用cycle1实际触发、消息、profile、0.7温度、512输出上限、原解析及一次格式修复政策。对原54条触发请求核对入口；两新增seed的108条物理请求除seed外保持。18项局部入口/runner测试通过，实际grammar接受。
4. **GPU2/M4与GPU3/M5并行执行历史121面板。** 预定seed43/44，旧B/F与seed42复用；每seed仅M4的28题和M5的26题生成。共108新调用，837,750输入／12,802输出token。每骨干每seed保留完整121分母，M5旧d00050仍不可用。
5. **预先固定另一批自然来源开发家族。** 从既有656输入池按支持格式、完整家族和固定SHA顺序选择18家族52输入，排除历史121重合家族/输入；成员锁定在读取新结果前。旧F104份完整响应由409缓存回调重建后逐字一致，0新B/F。仍属已暴露开发，既有基准扰动和作者控制单列，不冒充新的独立临床病例。
6. **两骨干执行自然52的三个seed。** seed42/43/44分别只在原F分歧的M4 25题、M5 16题生成；共123新调用，606,930输入／18,245输出token。六个运行各52题完整保存。
7. **评分、波动和采用判断。** 只对新触发回答执行247条原生评分映射；原B、历史seed42及未变化答案复用旧评分。修复/误伤、配对双正确、原生74/18单元、40/18家族分别计算。独立算术/来源复核通过；不据此声称重新完成原生医学评分或独立复现。
8. **收束和资源交接。** 全部10个运行明确`engine_shutdown`、journal关闭，231新调用0新增运行失败、0格式修复、0未知用量。默认F增量关闭。23日23:02记录GPU2/3各80GiB恢复占位，0/1未重占；本次发布不操作GPU，历史快照不冒充实时状态。

## 2. 全部固定seed的结果

| 范围／骨干 | 旧B正确 | seed42 | seed43 | seed44 | 三seed平均净正确数 |
|---|---:|---:|---:|---:|---:|
| 历史121／M4 | 87 | 89 | 88 | 88 | +1.333 |
| 历史121／M5 | 82 | 83 | 84 | 84 | +1.667 |
| 自然52／M4 | 35 | 34 | 31 | 32 | −2.667 |
| 自然52／M5 | 26 | 25 | 23 | 24 | −2.000 |

历史121的seed42为保存成绩；自然52三个seed均为本轮新触发计算。两个面板分别保留原成员与分母，不合并冒充独立样本。自然52两骨干三seed全部低于B，三seed平均原生单元差M4 −7.778、M5 −4.815个百分点。历史121平均原生单元差为+1.201、+3.153个百分点。完整原生表、修复/误伤、配对和家族分层见[质量摘要](data/quality_summary.json)及[报告14.7](docs/research/cf_moa_experiment_report.md#minimal-head-reuse-v4)。

先平均三seed再等权两骨干，家族bootstrap95%区间：历史准确率差+1.240个百分点，区间[−1.755,+4.386]；自然−4.487个百分点，区间[−9.936,+1.042]。两者跨0，证据仍弱，不能宣称总体收益或损失已确定。已有Scope32反例保持：M4 31/32→30/32，M5 31/32不变。

**默认系统为`adopted_B_five_operations_v1`，F普通分歧重答不开启。** 该候选及负结果完整保留；不把A1/A2同核操作分解称为两个新训练模型，不把普通控制复用称为新反事实算法，也不因五个职责槽就声称验证了五专家协作增益。

## 3. 实际错误及修复

- 自然缓存准备三次断言停止：最初未识别旧F追加投票指令；之后相同messages/schema的NLI direct与equal_path样本取错臂，第三次仅增加定位信息。使用旧请求构造器并明确head/equal_path来源后104份完整响应一致。没有修改采用F或新增采样来匹配旧答案。[准备记录](evidence/natural_scope/preparation_attempts.json)
- 自然manifest最初列seed42，真实自然推理前改为预定42/43/44；成员、提示、预算不变，原manifest/plan留存。[事前修订](evidence/natural_scope/seed_amendment_receipt.json)
- 初版家族聚类用了粗粒度`source_family`，历史40家族被合成31组。改为`group_id`，保留错版，仅重算分组/区间；已完成124条原生评分直接复用，0额外评分。另在自然评分前将F覆盖身份绑定回manifest，未改成员。[分析错误记录](evidence/analysis/analysis_errors.json)
- M5旧d00050在所有历史seed仍不可用；不记为新运行错误，不删除分母。本轮新增调用均成功不代表方法质量成功。

## 4. 费用口径

| 新增计算 | 模型调用 | 输入token | 输出token | 累计模型秒 |
|---|---:|---:|---:|---:|
| 历史121，seed43/44 | 108 | 837750 | 12802 | 284.7579 |
| 自然52，seed42/43/44 | 123 | 606930 | 18245 | 301.7403 |
| 本轮合计 | 231 | 1444680 | 31047 | 586.4981 |

231不包含历史seed42的54调用，更不是全CF-MoA历史费用。旧B/F在方法账归属，不能因本次缓存读取就写成方法成本为0；历史不可恢复的逐题模型秒保留unknown/null。累计模型秒不是并行墙钟、GPU能耗或占位耗时。本次文档发布0新模型、0原生评分。[完整成本](data/cost_summary.json)

## 5. 代码、配置和逐题证据在哪里

| 交付对象 | 公开位置与边界 |
|---|---|
| 五操作系统与F开关 | [minimal_operations.py](source_snapshot/cf_moa/controller/minimal_operations.py)；冻结源码原样复制 |
| 固定seed runner | [minimal_f_runner.py](source_snapshot/cf_moa/evaluation/minimal_f_runner.py)；真实入口绑定、SQL记账和停止范围 |
| 本次局部回归 | [test_minimal_operations.py](source_snapshot/cf_moa/tests/test_minimal_operations.py)；合成fixture，没有真实病例 |
| 默认系统配置 | [minimal_system.json](source_snapshot/cf_moa/configs/minimal_system.json)；增量开关false |
| 最终执行配置 | [execution_plan.json](source_snapshot/cf_moa/configs/execution_plan.json)；原路径与版本身份保持 |
| 方法与统计计划 | [用户核心计划](plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)／[分析计划](plan/analysis_plan.json) |
| 全部原始制品定位 | [原99项索引](data/delivery_index.json)／[公开映射](data/public_delivery_index.json) |
| 逐输入状态 | [per_input_status.csv](data/per_input_status.csv)；B加全部seed共1384行，含复用、不可用和正确性布尔值，没有答案正文 |
| 新调用元数据trace | [new_model_call_trace.csv](data/new_model_call_trace.csv)；231物理调用，可核对ID/seed/用量和来源hash，不是完整模型trace |
| 原SQL/请求/响应/提议 | 保留服务器原路径和SHA，未上传正文；`local_only`或`metadata_projection`明确区分 |
| 真实入口与关闭收据 | [历史121](evidence/seeds/live_receipt.json)／[自然52](evidence/natural_scope/live_receipt.json) |
| 同响应等价与开关测试 | [规则回放](evidence/operations/replay/receipt.json)／[F开关](evidence/operations/f_toggle_receipt.json) |
| 统计独立核对 | [独审收据](evidence/analysis/independent_review.json)；仅保存结果算术和来源一致性 |
| 发布前内容核验 | [文档审阅](evidence/document_review.json)／[公开数据独审](evidence/publication_data_review.json)／[原99项哈希核验](evidence/original_delivery_verified.json) |

六个源码/配置快照来自原交付目录，保留精确字节；可审查本轮改动，但依赖未随包发布的旧head、数据和环境，不是独立可运行的完整软件发行版。原始绝对路径在索引中是证据地址，不是GitHub可下载链接。Markdown未公开引用集中在[本地制品引用表](LOCAL_ARTIFACT_REFERENCES.csv)。

公开文件完整性由[PACKAGE_MANIFEST.json](PACKAGE_MANIFEST.json)校验，来源转换见[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)。哈希校验只证明文件一致，不证明医学答案正确；所有分数仍是原生评测已保存的开发结果。
