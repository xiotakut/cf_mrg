# E1：来源/格式控制后的功能异质性

7 配置，各 6,104 单元、8,798 非 reference 评分映射；4,216 保守家族隔离的 5 折 OOF。原题根、MedPIC 对照题干及规范化 reference 联结后，采用当前家族映射；初版及中间版只作历史。

基础错误预测含方法、来源、格式；扩展加入多标签功能与方法×功能交互。Brier 0.177944929 → 0.176789214，改善 0.001155715，家族区间 [0.000311530, 0.001993726]。固定超参数，无搜索；区间条件于已拟合 OOF 模型，不包含重新选模变异。

[总览](summary.json)、[同来源/格式对照](supported_within_source_contrasts.csv)、[MedEinst组成](diagnosis_composition.csv)、[家族映射](family_mapping.json)、[OOF预测](out_of_fold.jsonl.gz)、[单元分数](unit_scores.csv.gz)、[诊断图](functional_diagnostics.pdf)。预测概率对应错误事件（1−correct）。

零新增模型推理、零原生评分重算。该分析提供关联性的增量预测信息；不能消除历史开发暴露，极小样本及完全混杂类别仍不可独立识别。来源内任务组成和评分形式差异仍需保留解释边界。

## 冻结折复现与标准化范围

逐行fold原已保存在`out_of_fold.jsonl.gz`。新增[家族—折映射](frozen_family_folds.json)和[可移植复现脚本](../reproduce_e1_fixed_folds.py)，显式读取原折分，避免跨环境重新生成GroupKFold的并列分配差异。脚本只拟合10个CPU逻辑回归模型，不调用LLM。新复核预测与保存值最大绝对差约5×10⁻¹¹，[结果和当前依赖版本](fixed_fold_reproduction.json)。这些版本是本次复核环境，不冒充原运行时锁文件。

MedEinst未标准化比较为1100个R1-only与680个R1∩R3单元；共同诊断标准化只覆盖9种诊断、562/680单元。不能把标准化后的差异说成对原1100/680全体的完全控制。M12同格式对比方向相反；两者都不建立普适功能难度排序。
