# ASCENT47 单答案接口归因冻结结果

2026-09-16。本包仅是运行证据与冻结报告；长期主记录见 [optimization.md](../docs/research/optimization.md)。

新增94次原骨干调用全部完成，两worker退出；已完整阅读94个新回答。旧输入、评分、49目录、投票与先验没有改变。先前47验证病例现在是已暴露开发，不能把本轮结果称作新独立holdout。

## 已固定的对照

在每个完整原生ASCENT Text后追加同一条无目录指令，要求最终Findings阶段最支持的单个疾病或相关系统，粒度有据，boxed中只给单名。没有向模型提供49目录、gold、评价信息或原答案。两原骨干与旧自由生成同为temperature0.7、seed42、top_p1、top_k−1、max_tokens2048、batch8。eager和2048 KV固定；GPU总卡预算由.95改为.45用于并行资源安排。原生任务允许多个impression，这个单名约束是任务接口归因对照，不是原任务的等价实现。

prepared.json在新预测前记录了完整prompt、评分与解释边界。继续使用原last-complete-box解析和canonical评分；不按结果新增别名、不从多答案中挑gold。纯名称、粒度、列表和不同疾病/阶段按事前解释类别人工审阅，不把这些类别重新当医学准确率。

## 固定评分

以下均为同47范围内的项目canonical正确数，不是ASCENT官方语义F1。

| 范围 | 骨干 | 原生自由答 | 无目录单名 | 旧单次目录 | 旧校正头 |
|---|---|---:|---:|---:|---:|
| all (n=47) | M4 | 4 | 27 | 38 | 38 |
| all (n=47) | M5 | 20 | 22 | 39 | 39 |
| test (n=5) | M4 | 1 | 1 | 4 | 4 |
| test (n=5) | M5 | 2 | 1 | 4 | 4 |
| train (n=42) | M4 | 3 | 26 | 34 | 34 |
| train (n=42) | M5 | 18 | 21 | 35 | 35 |
| prior_target_named (n=23) | M4 | 2 | 17 | 22 | 23 |
| prior_target_named (n=23) | M5 | 14 | 13 | 23 | 23 |
| prior_target_not_named (n=24) | M4 | 2 | 10 | 16 | 15 |
| prior_target_not_named (n=24) | M5 | 6 | 9 | 16 | 16 |

原生→单名修复/误伤M4为23/0，M5为8/6；单名→旧order0为13/2与17/0。94/94都有完整盒，人工复核均为单一最终答案，0截断。单名canonical未映射18/23条依然不能写成盒格式失败或医学错误。

## 归因

M4的23条分数修复全部来自原答已经包含目标身份：19个含目标列表、2个同疾病附描述、2个纯名称变体；没有一条来自旧审阅归为另一疾病/阶段的答案。故只修改单答案接口即可产生4→27的大幅canonical提高，它不足以证明临床推理被增强。

M5单名净增只有2题（8修复、6误伤）。8修复含名称变体3、粒度/系统4、另一疾病/阶段1；6误伤包括支气管扩张→囊性纤维化、细支气管炎→呼吸窘迫综合征，也含贫血→亚型、肺炎→肺部感染这种评分粒度改变。

新回答人工解释分类（不改分）：

| 类别 | M4 | M5 |
|---|---:|---:|
| frozen_exact_correct | 27 | 22 |
| name_or_acronym_only | 3 | 4 |
| granularity_or_related_system | 5 | 10 |
| different_disease_or_stage | 12 | 11 |

目录仍优于无目录单名，但余下差额仍混合名称、疾病层级和实际疾病/阶段选择：M4 order0的13修复由3名称、4粒度/系统、6另一疾病/阶段组成；M5的17修复由3名称、8粒度/系统、6另一疾病/阶段组成。单名与目录还分别使用自由生成和一token似然选择，目录请求重复题干，不能把差额当作单一目录因果效应。

已有校正头与单次目录总体仍同分。校正对单名也各有2次误伤：M4 train129贫血→结核、train367肺栓塞→疑似心梗；M5 train367肺栓塞→自发气胸、train2243肺炎→COPD。没有据本轮结果选择新门控、混合策略或改先验。

## 官方评价的具体缺口

已完整核对作者evaluation.py、postprocessing.py、config/evaluation.yaml的评价prompt及utils/utils.py。作者协议用GPT-4.1、temperature0，每回答评5次，对每个impression分别给1=等价正确、2=过细、3=过粗、4=不同；逐位置多数票后按正确实体与错误实体计算micro precision/recall/F1。作者代码另允许人工修正评判输出格式。

本地没有可忠实执行GPT-4.1的离线后端，也没有这批新臂的5次既存判断；本轮没有外部付费API授权，因此没有调用外部评价服务或尝试鉴权，不声称遇到了已证实的认证错误。即使未来跑语义judge，这47也只是选定目录兼容子集（作者test5/train42），不等于官方全test分数。本次仅报告既有项目分数与解释性人工分类。

## 成本与失败

新增94调用：输入35677、输出932token；M4 worker48.009s、M5 worker23.923s，合计71.932s，queue墙钟86.965s。加载占M4 45.346s、M5 20.754s；模型均成功，未重复生成。现有282条free/order0/calibrated评分为离线复用。

审阅汇总脚本初次运行有一次重复harms关键字SyntaxError，0模型调用、未改预测；字段改为harm_details后离线汇总成功。失败见execution_notes.json，源码保留当前可运行修复；该修复未改变模型请求或主评分。

证据：prepared.json、m4/m5/direct_requests.jsonl、direct_predictions.jsonl、direct_runtime.json、gpu1.log、queue_runtime.json、summary.json、scored.jsonl、answer_review.jsonl、result_audit.json。run_refinement.py负责准备/运行/原评分，audit_refinement.py保留人工解释归类与一致性断言。
