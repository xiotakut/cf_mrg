# 医学CF资源清单：完整库与分析子集

2026-09-08。所有已选28,243个单元完成首轮审阅；有标签指至少一个具体目标成立，不是临床专家验收。26项是资源目录，表中0表示目标数据尚未取得，不表示其科学范围被排除。

|编号|资源|完整比较记录|分析已审|有标签|无标签|
|---|---|---:|---:|---:|---:|
|M01|MedEinst|5,383|2,500|843|1,657|
|M02|MedPIC-Bench|183|183|167|16|
|M03|MamaBench|0|0|0|0|
|M04|肿瘤临床CF评测|0|0|0|0|
|M05|临床检验因果推理评测|33|33|30|3|
|M06|HIV治疗因果情景研究|20|20|13|7|
|M07|CLIR-Bench|0|0|0|0|
|M08|ECG-Expert-QA|0|0|0|0|
|M09|GenMedicalEval|0|0|0|0|
|M10|CPV-MedQA|10,225|2,500|1,111|1,389|
|M11|Counterfactual Cultural Cues|1,349|1,349|1,174|175|
|M12|FairMedQA/AMQA|4,806|4,806|4,298|508|
|M13|MedEqualQA|0|0|0|0|
|M14|DiversityMedQA|6,296|2,500|2,378|122|
|M15|CLIMB|0|0|0|0|
|M16|EquityMedQA|323|323|302|21|
|M17|MedPerturb|3,759|3,745|3,615|130|
|M18|DeVisE|0|0|0|0|
|M19|MedFuzz|0|0|0|0|
|M20|MedCounterFact|809|809|788|21|
|M21|MediEval|0|0|0|0|
|M22|MedRGB|3,680|3,680|3,680|0|
|M23|BioRAB|12,615|2,500|2,499|1|
|M24|MedCF|4,013|798|797|1|
|M25|MedMKEB|2,497|2,497|2,497|0|
|M26|COLLECT|0|0|0|0|

标签分布与审阅方法见[分类审阅报告](reports/来源与标签计数.md)；M25缺图元数据单列，不计文本数量。

## 已取得范围与限制

- **M01 MedEinst**：完整保留5,383官方对；83对未见临床文字变化，保留问题构造标志并从分析池剔除。分析按原trap诊断分层取2,500。 [原始入口](https://huggingface.co/datasets/zhui711/MedEinst)；[发布来源核查](reports/source_release_notes.json)。
- **M02 MedPIC-Bench**：183 CF全收；284 GF保留原文件与旧输入索引，不猜配对。 [原始入口](https://huggingface.co/datasets/TIM0927/MedPIC-Bench)；[发布来源核查](reports/source_release_notes.json)。
- **M03 MamaBench**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://huggingface.co/datasets/HelpMum-Personal/MamaBench)；[发布来源核查](reports/source_release_notes.json)。
- **M04 肿瘤临床CF评测**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://arxiv.org/html/2605.30590v1)；[发布来源核查](reports/source_release_notes.json)。
- **M05 临床检验因果推理评测**：33 CF全收；第一99题块的66道非CF题作原序列参照，第二模型评价块不重复算题。 [原始入口](https://github.com/balubhasuran/LLM_Causality_LabTest)；[发布来源核查](reports/source_release_notes.json)。
- **M06 HIV治疗因果情景研究**：20道CF附录情景全收；参考答案可靠性逐项标记。 [原始入口](https://www.nature.com/articles/s41746-026-02771-7)；[发布来源核查](reports/source_release_notes.json)。
- **M07 CLIR-Bench**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://huggingface.co/datasets/winall/CLIR-Bench)；[发布来源核查](reports/source_release_notes.json)。
- **M08 ECG-Expert-QA**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/Zaozzz/ECG-Expert-QA)；[发布来源核查](reports/source_release_notes.json)。
- **M09 GenMedicalEval**：仅已发布文档示例另存；目录声称的12,000不能计作已取得数据。 [原始入口](https://github.com/MediaBrain-SJTU/GenMedicalEval)；[发布来源核查](reports/source_release_notes.json)。
- **M10 CPV-MedQA**：12,310发布变体中2,085文字与原题相同，10,225实际变化完整收录；分析取2,500。1,202原题根单列。 [原始入口](https://huggingface.co/datasets/kenza-ily/medqa-cpv)；[发布来源核查](reports/source_release_notes.json)。
- **M11 Counterfactual Cultural Cues**：1,350发布变体中1条无变化另存；1,349实际变化全部分析，150原题根。 [原始入口](https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs)；[发布来源核查](reports/source_release_notes.json)。
- **M12 FairMedQA/AMQA**：801根×6固定攻击=4,806比较，全收；中性和原题作为参照；已按实际新增临床线索、原题目标及明确的实施条件裁决。 [原始入口](https://github.com/XY-Showing/AMQA)；[发布来源核查](reports/source_release_notes.json)。
- **M13 MedEqualQA**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://aclanthology.org/2025.sciprodllm-1.4/)；[发布来源核查](reports/source_release_notes.json)。
- **M14 DiversityMedQA**：6,380候选变体中84无变化；6,296完整归档，分析2,500。保留author_train/author_test、缺选项与性别矛盾。 [原始入口](https://aclanthology.org/2024.nlp4pi-1.29/)；[发布来源核查](reports/source_release_notes.json)。
- **M15 CLIMB**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/uscnlp-lime/climb)；[发布来源核查](reports/source_release_notes.json)。
- **M16 EquityMedQA**：323对全收：123 CC-Manual＋200 CC-LLM，关联145个问题。逐项保留相同/不同理想答案评定，不整包R5。 [原始入口](https://www.nature.com/articles/s41591-024-03258-2)；[发布来源核查](reports/source_release_notes.json)。
- **M17 MedPerturb**：3,759发布变体与1,884基线全收；14文字无变化另作对照，3,745实际变化全部分析。VISIT/MANAGE分别判断。 [原始入口](https://huggingface.co/datasets/abinitha/MedPerturb)；[发布来源核查](reports/source_release_notes.json)。
- **M18 DeVisE**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/camztag/DeVisE)；[发布来源核查](reports/source_release_notes.json)。
- **M19 MedFuzz**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://arxiv.org/html/2406.06573v2)；[发布来源核查](reports/source_release_notes.json)。
- **M20 MedCounterFact**：已复用完整809个替换比较及203个原始证据根，809条全收全审；保留假设证据与现实合理性的区别。 [原始入口](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence)；[发布来源核查](reports/source_release_notes.json)。
- **M21 MediEval**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://github.com/ZhanQu945/MediEval)；[发布来源核查](reports/source_release_notes.json)。
- **M22 MedRGB**：3,680原问CF组全收，组内36,800 DOC位置完整保留；36,601完整、199缺字段。3,480个options元数据占位另存，不计CF。 [原始入口](https://arxiv.org/html/2411.09213)；[发布来源核查](reports/source_release_notes.json)。
- **M23 BioRAB**：两强度12,616发布记录中1个输入未变，12,615完整归档；实际11,125种可见配对、5,563个不同目标。分析取2,500，重复不当独立病例。 [原始入口](https://arxiv.org/html/2405.08151v3)；[发布来源核查](reports/source_release_notes.json)。
- **M24 MedCF**：4,028编辑根各split全保留：15个新旧值相同另存，4,013实际编辑；分析取test798实际编辑，另保留4个test未改值记录。 [原始入口](https://github.com/quqxui/MedLaSA)；[发布来源核查](reports/source_release_notes.json)。
- **M25 MedMKEB**：2,497 eval编辑元数据全收、全部缺图，单列多模态，不加入文本题量；train/attack原文件留存但不充评测数。 [原始入口](https://arxiv.org/html/2508.05083v1)；[发布来源核查](reports/source_release_notes.json)。
- **M26 COLLECT**：本轮目标固定单元尚未取得；原始入口、访问状态与缺口保留，不从文献目录删除。 [原始入口](https://doi.org/10.5683/SP3/KXYCNY)；[发布来源核查](reports/source_release_notes.json)。

来源详情中的旧selected_units/labeled_units是归档试点历史字段；当前完整/分析规模以本表、资源目录.json的full_counts/analysis_selection和reports/collection_counts.json为准。各来源full_counts.json提供发布行、实际变体、参照与重复规模。
