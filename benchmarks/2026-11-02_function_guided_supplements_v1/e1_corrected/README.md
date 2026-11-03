# E1：来源/格式控制后的功能异质性

7 配置，各 6,104 单元、8,798 非 reference 评分映射；4,216 保守家族隔离的 5 折 OOF。原题根、MedPIC 对照题干及规范化 reference 联结后，采用当前家族映射；初版及中间版只作历史。

基础错误预测含方法、来源、格式；扩展加入多标签功能与方法×功能交互。Brier 0.177944929 → 0.176789214，改善 0.001155715，家族区间 [0.000311530, 0.001993726]。固定超参数，无搜索；区间条件于已拟合 OOF 模型，不包含重新选模变异。

[总览](summary.json)、[同来源/格式对照](supported_within_source_contrasts.csv)、[MedEinst组成](diagnosis_composition.csv)、[家族映射](family_mapping.json)、[OOF预测](out_of_fold.jsonl.gz)、[单元分数](unit_scores.csv.gz)、[诊断图](functional_diagnostics.pdf)。预测概率对应错误事件（1−correct）。

零新增模型推理、零原生评分重算。该分析提供关联性的增量预测信息；不能消除历史开发暴露，极小样本及完全混杂类别仍不可独立识别。来源内任务组成和评分形式差异仍需保留解释边界。
