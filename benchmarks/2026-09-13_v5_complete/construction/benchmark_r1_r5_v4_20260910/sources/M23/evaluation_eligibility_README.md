# 最终评分资格 sidecar

此次仅填写资格，不改 annotations、原题、原参考或语义裁决。evaluation_eligibility.jsonl 与 inputs/annotations 的 unit_id 精确相等且唯一；annotations 的 SHA256 保存在逐条记录和 summary 中，生成前后校验相同。每条记录携带原生输入定位、固定评分接口和逐目标资格。

规则：只有 classified 目标、原生字段完整、必要模态齐备且没有已有评分禁用的目标可评。原父级或 judgment 的明确 false 均保留，空值不当作 gold 已独立认证。仅检查有可执行固定评分，不重新认证所有医学参考。父级资格表示至少一个目标可评，all_targets_eligible 另列；本批没有部分可评的混合父记录。

pending_units=0 表示资格检查全部完成，并不表示原先的证据不足、无效题或参考冲突已经解决。它们明确作为排除项保留，原理由仍位于 annotations。统计中排除原因可以重叠，不能将各原因计数相加当排除总数。

M23 两端 context/response 一致，原 response 属于 positive/negative，固定原 instruction/context 对照保留。20个原 judgment 禁用全部传播；同一当前context及同一原response的禁用在其他演示视图间传播并保留来源。row5423与对应row6118截断假说在两噪声条件下均禁用。10,095可评，20排除；其中7条语义证据不足，其他13条虽classified仍有参考缺口、矛盾或截断。禁用不会改写原gold，也不把有完整字段等同参考已被独立认证。
