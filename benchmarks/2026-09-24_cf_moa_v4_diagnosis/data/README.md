# v4 定向诊断：公开数据投影

本目录用于审阅已经完成的离线诊断，不是新实验。保留95个完整触发题目—骨干组合及285个输入—骨干—seed结果；没有新增模型调用、原生评分或旧head回放。旧实验完整121/52分母未被触发子集替代。

- `selection_decomposition.csv`：12行面板×骨干×seed选择分解。
- `per_trigger_seed.csv` / `.jsonl`：285行逐组合逐seed答案键、旧池覆盖、修复/误伤、既有评分与成本。
- `stratified_decomposition.csv`：格式/路径分层；`full_panel_existing_results.csv`：原完整面板成绩；`trigger_baseline_comparison.csv`：触发与非触发旧B正确性。
- `three_seed_oracle.jsonl`：95组离线三seed联合候选覆盖，花费三次补充调用，不能当作一次重答或可部署方法。
- `nli_candidate_details.jsonl`：7组NLI的映射、已存在top1与概率。非零概率不计为已生成答案；不与生成票简单相加。
- `auxiliary_field_comparison.jsonl`：42行辅助字段一致性及保存/推断指标的区别；自然旧B缺失的指标不补写为历史测量。
- `sample_manifest_metadata.json`：全部95组标识、私有样本/离线文件SHA与字节数、430次旧F请求计数、三seed身份。引用哈希不表示原文件已经公开。
- `analysis_attempts.json`、`analysis_receipt_metadata.json`、`sample_crosscheck_metadata.json`：准备错误、原分析访问边界与交叉核验摘要；原loader曾附带读取全量canonical标签表，但本批无diagnosis、未查询其标签，不进入模型消息。当前窄parser脚本修正后没有重算结果。
- `summary.json`：原有汇总；`public_data_manifest.json`：此次投影的字段白名单、文件SHA、来源SHA与检查结果。

公开内容为标识、答案键、概率、计数、现有评分、费用和元数据。省略题面/选项正文、检索全文、messages、渲染prompt、模型理由、完整原生对象、gold自由文本和原始病例文件；完整受限材料仍在本地私有压缩包。这些公开表不能替代逐病例医学语义核读。

核对结果：旧F正确43组、旧池有正确键但F错35组、旧池全错17组；候选覆盖78/95。285份已有补充回答新增正确键覆盖0，35修复/40误伤，其中39次误伤使用旧池已有错误键。35/40不是独立患者数；95只是触发组；oracle只描述固定保存候选池。成本1,863,555输入/37,019输出token属于已经发生的285次补充回答，含54次旧seed42与231次v4调用，本次新增为0。
