# M4新增R1 Bronchitis残留误差：固定六例审核

2026-09-16。冻结目录头全1100中，Bronchitis为原12/321、校正13/321：298例仍错、10例误伤、11例修复、2例保留正确。此报告只审核六例，不推算各根因在321例中的占比；不修改head、目录、prior或评分。

抽样以seed20260919，在各层按item_id排序后随机选2仍错、2误伤、1修复、1保留正确。名单及抽样池计数见`bronchitis_selection.json`；六例完整当前题面、原M4 JSON解释、原原生消息、未校正/校正六票及概率保存在`bronchitis_evidence.jsonl`。本次实读了全部六例当前题面、原解释及两组六票；没有据检索标题猜测未读取的段落作用。新增模型调用0。

## 六例逐项结果

**s004665，原错仍错。** 88岁，颈侧/头顶/咽/颞部痛、疲劳、寒战、有色或增多痰、咳嗽，吸烟、免疫抑制；疼痛起始为0突发至10渐进量表的3。原解释最终为肺腺癌，明确把年龄、吸烟/免疫抑制与肺癌联系，并将颈/头/咽部痛概括为“localized to the respiratory system”，进一步联想到cachexia或respiratory failure；后二者不是原题明确事实。原解释不是简单漏看咳嗽，存在可定位的部位概括和背景推断。未校正六票为Pneumonia/Pneumonia/Pneumonia/Influenza/Pneumonia/Pneumonia；校正为Pneumonia/Pneumonia/Pulmonary neoplasm/Pulmonary neoplasm/Pneumonia/Pneumonia。头从肿瘤转向肺炎仍未命中标签，不能据它只输出编号认定同一原推理继续起因。

**s009108，原错仍错，但校正独立误伤了未校正结果。** 27岁，腹部/上腹痉挛痛“gradually (over hours to days)”、黄色肿胀皮疹、有痰咳嗽明确持续3个月；吸烟、超重及胰腺癌家族史。原解释把明确渐进发作写为“acute onset”，在Chikungunya/pancreatitis间反复转折，最终Pancreatitis。这里有直接可核的时间事实改写，不只是名称范围问题。未校正票Pneumonia/Bronchitis/Bronchitis/Scombroid food poisoning/Pancreatic neoplasm/Pulmonary neoplasm，汇总Bronchitis正确；校正票Sarcoidosis/Bronchitis/Pancreatic neoplasm/Viral pharyngitis/Pancreatic neoplasm/Bronchiolitis，汇总Pancreatic neoplasm错误。相同原始患者分数经固定prior运算已足以翻转，属于已观察到的校正决策问题。家族史对头造成牵引仅是待检假说；头无新解释，不能由结果反推因果。

**s004027，原对被改错。** 48岁，有色/增多痰、呼吸困难、发热、咳嗽；静脉药物、糖尿病、酒精、无近期境外旅行。原解释完整列出主要症状并比较pneumonia/bronchitis，最终bronchitis。未校正六票全部Pneumonia；校正为Sarcoidosis/Pneumonia/Pulmonary neoplasm/Pulmonary neoplasm/Pneumonia/Pneumonia，仍Pneumonia。原名已被冻结评分接受，头没有修格式的必要；六票一致也不能保证标签正确。这是目录内竞争诊断决策变化，非排列随机波动足以解释；仅凭本审核不能判定临床上必须Bronchitis。

**s005879，原对被改错。** 63岁，同上四个主要呼吸症状；HIV、皮质激素、糖尿病、无近期境外旅行。原解释承认pneumonia和其他病的可能，最终bronchitis，但还使用了未给定的“persistent cough”概括。未校正Bronchitis/Bronchitis/Pneumonia/Pneumonia/Pneumonia/Bronchitis，3:3平票由平均概率Pneumonia0.31885对Bronchitis0.27687决定；校正Sarcoidosis/Pneumonia/Pneumonia/Bronchitis/Pneumonia/Bronchitis，3:2票仍Pneumonia，尽管校正平均概率Bronchitis0.22605略高于Pneumonia0.22326。这里能够具体解释聚合规则怎样得到答案，不能等同临床依据。R3已经做过平均概率控制，不能凭这一例重选策略。

**s009398，head修复控制。** 39岁，同四个主要呼吸症状；静脉药物、低BMI、无近期境外旅行。原解释先提出acute bronchitis，再因静脉药物/低体重转向TB，进一步谈到drug-resistant TB，后者不是题面给定事实；原最终Tuberculosis (TB)。未校正Pneumonia/Bronchitis/Pneumonia/Bronchitis/Acute COPD exacerbation / infection/Bronchitis，汇总Bronchitis。校正Sarcoidosis/Pneumonia/Bronchitis/Tuberculosis/Tuberculosis/Bronchitis，2:2平票由平均概率Bronchitis0.18653对Tuberculosis0.17873决定。修复不是TB到Bronchitis的别名归一；但结果较脆弱，也不能据此声称head识别并纠正了原背景推断。

**s007388，保留正确控制。** 18岁，同四个主要呼吸症状；酒精、低BMI、无近期境外旅行。原解释考虑bronchitis、pneumonia等后选择bronchitis。未校正Bronchitis/Bronchitis/Pneumonia/Bronchitis/Pneumonia/Bronchitis；校正Sarcoidosis/Pneumonia/Bronchitis/Bronchitis/Tuberculosis/Bronchitis，最终均Bronchitis。和两误伤例共享四个主要症状，但背景不同，不能用这六个自然病例把差值归因于年龄或单一背景；也不能简单去掉全部背景。

## 可支持的错因边界

- **名称范围：** 本六例没有“同一疾病只因表面包装不被识别”的修复证据。原肺腺癌可与目录中的Pulmonary neoplasm形成粒度关系，但其gold为Bronchitis；Pancreatitis与Pancreatic neoplasm更不能当别名。更大样本原始未映射仍可能包含名称问题，本抽样不足以估计其占比。
- **可见事实使用：** s009108渐进→acute onset为明确文本不一致；s004665疼痛部位概括及s005879 persistent等超出原题明确陈述。多数例原解释实际提及了咳嗽/痰，不能统一归因“没读到新增事实”。
- **背景牵引：** s004665和s009398原解释明确依赖年龄/吸烟/免疫、静脉药物/低BMI来引向肿瘤或TB，且加入额外推断。背景在实际诊断中也可能有用；六例没有删除/替换背景的干预，不能把它概括为因果证据或全删背景的理由。
- **目录内歧义与汇总：** 两误伤均是已接受Bronchitis被目录内Pneumonia替换；一例未校正6/6一致错、一例3:3平票。一例未校正正确被校正改错、修复例则依赖2:2平票。目录、投票和prior均未解决所有相对判断。当前事实与原模型解释不足以独立临床复核gold，标签不自动证明哪条临床路径“真实错误”。

## 唯一建议的下一步小对照（尚未执行）

先对**这六例的原生reference/variant成对变化与目标一致性**作离线对照：从已冻结来源读取各自参考端，逐条对齐原文，列新增/保留/删除的可见观察及两端作者标签，核对本地当前输入与作者变化完全一致。参考端、变更标记和标签仅用于离线审核，不加入head输入，不新增GPU。

理由是四个样本当前主要症状几乎同一模式，但原解释、目录票和标签之间存在不同分歧；目前尚未知道“新增支持”具体改了哪个观察。先确认来源实际变化与R1目标，才能区分病例事实漏用、目标标签过粗和竞争诊断难辨，避免立即重跑已失败的背景删除、事实关系计数、草稿复核或换聚合器。此对照即使通过也只证明数据/变化一致，不充当临床金标准验证。本次按任务约束只提出该一个有界对照，未实施也未扩大到其他病例。

## 上述六组成对对照已完成（主代理随后授权，2026-09-16）

主代理要求继续这一离线对照后，已逐段读取全部12个作者control/trap叙述及v5的六条具体判断（同时核对selected_targets和全target_annotations）。原始来源实际为冻结00-test.jsonl（本地来源：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl`），revision `354f4b527e764a8f2bebea8f71be55e0a6966402`。记录逐行保存在`bronchitis_source_rows.jsonl`，作者标签与本地输入/评分/具体判断的映射及逐行diff保存在`bronchitis_pair_audit.json`；分类原行在`bronchitis_classification_rows.jsonl`。

| 当前item / 作者case | 源control,trap行 | 作者标签control→trap | 实际语义变化 |
|---|---|---|---|
| s004665 / case_60638 | 7629,7630 | Influenza→Bronchitis | 整块粉色皮疹及部位/大小/痒痛/无脱屑/无肿胀描述，替换为有色或增多痰的咳嗽 |
| s009108 / case_14055 | 3041,3042 | Pancreatic neoplasm→Bronchitis | 三个月非自愿体重下降，替换为三个月有色或增多痰的咳嗽 |
| s004027 / case_133178 | 2867,2868 | Tuberculosis→Bronchitis | 咳血，替换为有色或增多痰的咳嗽 |
| s005879 / case_116624 | 1405,1406 | Tuberculosis→Bronchitis | 咳血，替换为有色或增多痰的咳嗽 |
| s009398 / case_27364 | 4417,4418 | Tuberculosis→Bronchitis | 咳血，替换为有色或增多痰的咳嗽 |
| s007388 / case_76039 | 8883,8884 | Tuberculosis→Bronchitis | 咳血，替换为有色或增多痰的咳嗽 |

**数据与本地映射可确认：** 12/12个作者叙述与本地items.question逐字一致，12/12个作者ground_truth与本地gold一致；6/6个reference链接、judgment_id与当前v5判断对应。背景Antecedents全部保持，未发现本地拼接、截断或标签映射造成这六例低分。六组都包含旧症状删除和新症状引入；不能把R1简称“只往原病例后面追加一句”。删除旧症状也不能作当前明确否认该症状的事实。

**分类语义可确认：** 现v5所选判断的目标是“Bronchitis：咳痰/痰量或痰色变化的相容依据”，理由针对原control没有同类咳痰肯定陈述、trap明确给出。五条full_review记录明确写“支持仅表示候选的相容依据，不等于确诊；删句不等于明确阴性……未作临床专家验收”；s009108既有review记录同样写“不修改官方诊断gold，也不保证原病例生成质量”。这些限制与分类指南（本地来源：`/home/data3/txy/docs/data/classification.md:142`）一致。现有R1不是作者标签名称，而是本地对具体支持关系的分类；不能因为作者把最终gold从A改成B就自动再加R2/R3。

**本轮评价范围因此要区分：** 13/321是M4头在这些R1成员上的作者原生完整诊断准确率；它不是“是否识别新增咳痰支持Bronchitis”的专门准确率。两者有关但不等价。原解释实际提及新咳痰，却仍选别的候选，可能包含支持权衡、目录约束、原标签粒度/病例生成充分性等问题；本六例不能仅按错误标签断定是哪一项临床真因。尤其s009108校正答案恰等于作者control的Pancreatic neoplasm，只能说明输出回到该标签，不能证明模型看到了隐藏control或检索了源病例——本次模型输入没有control、变更标记或gold。

**临床有效性尚未确认：** 作者control/trap标签是否在这些合成病例的全部保留背景下具有唯一、充分的临床依据，本次未做独立临床专家判定。能确认的是来源文字、标签传递、当前具体分类目标以及模型可见事实使用；不能因分类成立就宣布唯一诊断gold的临床排他性已经验证，也不能反过来把head错答直接算成数据错误。评分分母、目录与正式标签全部不变。

该六组成对离线对照已结束，人工样本到此停止扩展。新增GPU调用0，没有向任何head请求补入reference或gold，也没有新增按病例编号/类别的规则。
