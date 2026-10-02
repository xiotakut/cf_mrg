# CF-MoA完整v5零新增推理收尾

本目录是2026-09-28冻结分析制品，持续研究叙述归工作区 docs/research/cf_moa.md 的 transparent-closeout-20260928。以 d857934 原完整结果为唯一主范围，历史运行及分数不覆盖。

交付入口：[完整结果](full_results.md)、[完整五表](five_tables.md)、[成本](attributed_costs.md)、[范围与限制](scope_and_limitations.md)、[最终状态](final_status.json)。所有来源/格式/家族区间分别见同名JSON。data_issues.jsonl为空文件，其含义与未执行部分见范围说明。

统计命令及源哈希见statistics/execution_receipt.json，实际5000次、seed240924；成本来自costs/sources.json绑定的只读SQL，真实命令与校验见costs下收据。脚本只是汇总已存在结果；不执行模型或grader。原数据/源码快照在此前2026-09-26公开包，本包通过commit和哈希引用，避免复制为一套新算法。
