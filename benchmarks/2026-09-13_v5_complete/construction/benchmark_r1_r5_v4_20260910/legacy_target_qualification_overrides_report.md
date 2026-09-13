# M17 旧目标资格补充：实际无变化控制

逐条复核固定 resource_queue.jsonl 的两端完整文本后，确认下列 10 个 unit 没有实施临床或人口属性变化。它们的原始字符串并不完全相同：新增的是生成器的编辑说明，另有空白变化；usmle_derm_997 还附带条件句引出的假如示例。

本文件及 legacy_target_qualification_overrides.jsonl 仅追加资格否决，适用于各 unit 全部目标（包括 VISIT、MANAGE、RESOURCE）。旧标签、判断、理由、证据和 resolution 不变；源 annotations、v3 和导出脚本未修改。上层导出需应用这些资格覆盖，不能仅查看源标签决定纳入。

| unit_id | 根索引 | baseline CSV record | variant CSV record | 具体核查 |
|---|---:|---:|---:|---|
| M17:askdocs_103:gender_swap | 1797 | 402 | 4566 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:askdocs_108:gender_swap | 1799 | 406 | 4570 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:askdocs_141:gender_swap | 1804 | 435 | 4599 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:askdocs_146:gender_swap | 1805 | 440 | 4604 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:askdocs_151:gender_swap | 1807 | 444 | 4608 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:askdocs_171:gender_swap | 1810 | 461 | 4625 | 另有逗号后空格删除和行尾空白整理，剂量、症状、就诊经过不变；编辑说明明确未执行性别交换。 |
| M17:askdocs_177:gender_swap | 1813 | 466 | 4630 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:askdocs_185:gender_swap | 1818 | 473 | 4637 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:askdocs_188:gender_swap | 1819 | 476 | 4640 | 仅追加未执行性别交换的编辑说明；原始临床事实未改变。 |
| M17:usmle_derm_997:gender_swap | 1834 | 1283 | 5442 | 保留原病例并明确声明output remains the same；追加女性病例由If the input text were to contain...the output would be条件句引入，是编辑性假如示例，未被指定为实际实施的变体。 |

计数：10 unit；全部目标 evaluation_eligible=false；未读 pending=0；新增语义标注=0。两端完整证据及固定原件 revision/定位保存在 JSONL。

适用范围按 unit_id 精确匹配，不扩张到整个原题根或来源。RESOURCE 新判断中的 outside_scope 保留在原分片；本覆盖文件没有改写任何旧目标的语义处置。
