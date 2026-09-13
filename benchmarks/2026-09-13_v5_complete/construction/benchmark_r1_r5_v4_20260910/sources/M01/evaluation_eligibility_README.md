# 最终评分资格 sidecar

此次仅填写资格，不改 annotations、原题、原参考或语义裁决。evaluation_eligibility.jsonl 与 inputs/annotations 的 unit_id 精确相等且唯一；annotations 的 SHA256 保存在逐条记录和 summary 中，生成前后校验相同。每条记录携带原生输入定位、固定评分接口和逐目标资格。

规则：只有 classified 目标、原生字段完整、必要模态齐备且没有已有评分禁用的目标可评。原父级或 judgment 的明确 false 均保留，空值不当作 gold 已独立认证。仅检查有可执行固定评分，不重新认证所有医学参考。父级资格表示至少一个目标可评，all_targets_eligible 另列；本批没有部分可评的混合父记录。

pending_units=0 表示资格检查全部完成，并不表示原先的证据不足、无效题或参考冲突已经解决。它们明确作为排除项保留，原理由仍位于 annotations。统计中排除原因可以重叠，不能将各原因计数相加当排除总数。

M01 保留开放诊断任务。两端 narrative/ground_truth 非空、control/trap 配对完整。沿用既有本地 evaluate.py 的 NFKC、大小写、空白及尾标点归一化精确匹配，不增造四选项，不新增同义词匹配或模型裁判。该指标不宣称覆盖作者所有语义正确性标准；自然语言同义诊断可能被固定文本匹配计错。937 个已分类单元可按此指标评分，1,403 个证据不足及460个无效源单元不进入R类评测。
