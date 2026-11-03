# 离线复核与源码范围

无需模型、GPU、外网或第三方Python库：

```bash
cd benchmarks/2026-11-02_function_guided_supplements_v1
python3 verify_saved_results.py
```

核验SHA-256清单、E1的OOF/单元平均和家族折隔离、E4a/E4b各臂逐项分数与配对、E5多分母主表及配对、2045实际调用的token合计和接受参数摘要。该入口重算保存分数的汇总，不重新判断临床答案，也不生成模型回答。区间由已保存原分析脚本与收据追溯；不把只重算平均数称为重做全套原生评分。

`source_snapshots/`逐字保存当时运行/分析脚本，内含提示模板、抽样、统计和运行设置。它们沿用原环境绝对路径，以及本地`cf_moa`实现、冻结上游结果、原生评分器、规则/候选资源和模型权重；不能直接在任意机器运行。来源hash见各preparation/receipt及provenance。复原原环境后应从运行根执行原脚本；不要直接在本公开目录运行会重写结果的历史脚本。

公开的`native_scored.jsonl`仅删除`native_answer`字段；标识、类别、可用性、全部评分字段原样保留。完整病例、自由文本响应、请求正文、上游资源未在本次重复分发。调用账本保留原文件hash和实际接受的提示hash/采样参数，支持计算量/接口追踪；提示hash本身不能证明被省略正文的医学内容。

`MANIFEST.json`覆盖本次新增payload（不含自身、ZIP与已独立发布的E2）；ZIP内含同一payload和manifest。`DOWNLOADS.json`给出ZIP校验。E2沿用其自身清单和ZIP。
