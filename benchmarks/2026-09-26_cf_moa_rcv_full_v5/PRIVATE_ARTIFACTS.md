# 完整trace与公开范围

本包公开完整分母的状态、原生单元、配对及家族效应元数据，完整当前输入、检索材料、F每条实际候选、模型请求/响应、verification trace、SQL和gold仍在服务器。

精确位置见[data/private_artifact_index.json](data/private_artifact_index.json)，沿模型、request_id、arm查询对应proposals及journal。原始请求没有为了发布重生成，F早停未产生的票不存在，也没有补跑。

旧121/52、26组原文变更审阅的私有位置继续见[前一交付索引](../2026-09-25_cf_moa_rcv_completion_in_progress/data/private_artifact_index.json)。历史包与新全量范围分开，不能将旧子集代替新全量。

本次没有重新哈希巨型SQL；已有transfer/分析收据绑定的hash标明来源，未提供hash的记录明确为null及原因，不伪造完整重新核验。公开gzip的解压前后hash可由SOURCE_MANIFEST复核。
