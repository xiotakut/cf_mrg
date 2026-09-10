"""Build both read-only scope scenarios from final v4 target eligibility."""
import csv,gzip,json
from collections import defaultdict,Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

OUT=Path(__file__).resolve().parent
RUN=OUT.parent.parent
REMOVE={'M23','M10','M12','M17','M22','M11','M20'}
LABELS=['R1','R2','R3','R4','R5']
DEFINITIONS={'R1':'新增支持','R2':'撤销支持','R3':'重新比较','R4':'推导后果','R5':'保持判断'}
with (RUN/'source_scope_inventory.csv').open() as f:inventory=list(csv.DictReader(f))
NAMES={r['resource_id']:r['benchmark'] for r in inventory}
with (RUN/'exports/archive_unit_coverage.csv').open() as f:archive=list(csv.DictReader(f))
TOTAL=Counter(r['resource_id'] for r in archive)
source_units=defaultdict(set);category_units=defaultdict(set);all_category_units=defaultdict(set);target_count=Counter();category_targets=Counter()
with gzip.open(RUN/'exports/all_reviewed_target_annotations.jsonl.gz','rt') as f:
    for line in f:
        r=json.loads(line);src=r['resource_id'];uid=r['unit_id']
        for label in r['labels']:all_category_units[(src,label)].add(uid)
        if not r['evaluation_eligible']:continue
        source_units[src].add(uid);target_count[src]+=1
        for label in r['labels']:
            category_units[(src,label)].add(uid);category_targets[(src,label)]+=1
assert sum(map(len,source_units.values()))==38123
assert sum(target_count.values())==77781
assert len(source_units)==11
REASONS={
'M01':'无变化参照；前后文本不足以支持具体关系；实际编辑与声明不符、关键上下文删除等构造无效。并非随机抽样。',
'M02':'12个目标缺少明确前态或风险支持撤销依据；4个目标的病例、变化方向与参考规则不一致。这里每单元一个目标，共16个单元未采用。',
'M05':'30个有标签单元的新答案需人工/rubric语义评分；另2个依据不足、1个题干构造无效。',
'M06':'5个单元缺少改变前提到结果的充分依据；2个干预指代/构造无效。',
'M10':'患者性别等实际文本冲突、比较构造无效；无法确认具体不变关系；必要图像缺失。含已分类但仍缺图的4个目标，不能把相同gold当评分资格。',
'M11':'173个分类关系依据不足、2个仅格式修改、9个需要缺失图像，共184个单元。',
'M12':'508个单元未能确立具体分类关系；15个单元依赖缺失图片，共523个单元。',
'M14':'297个依据不足、112个构造无效、11个五类外；另225个已分类目标因缺图或参考等资格问题未采用，共645个单元。',
'M16':'新答案需人工语义评分；另包含作者因处理错误撤回的配对及依据不足子目标。已发布历史人评分不能用于新模型答案。',
'M17':'原有无变化参照与新增查明的编辑性声明控制；截断/错改正文等无效构造；分类依据不足；必要图像缺失。按VISIT、MANAGE、RESOURCE分别判断，至少一个合格目标才计采用单元。',
'M20':'21个单元的治疗臂替换后无法恢复清晰的比较指代；数字保留不代表仍有有效对照关系。',
'M22':'200个单元对应长答案语义rubric，57个单元依赖缺失图片，共257个单元未采用。保留单元中的错误文档定位/自由纠正等辅助目标另判资格，不能从主问继承。',
'M23':'8个分类依据不足，16个已分类目标存在原参考冲突、文本截断或结论缺失等评分限制，共24个单元。',
'M24':'3,215个作者train/valid实际编辑不混入test；797个已分类暂缓单元需要原生知识编辑步骤，当前文本问答协议未执行；另1个旧test记录未能定类。',
'M25':'2,497个eval比较单元缺少当前任务需要的图像，文本方法不能执行；其中子目标是否已分类另行保留。',
}


def csvfile(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

scenarios={}
for key,excluded in [('v4',set()),('reduced_preview',REMOVE)]:
    active=[s for s in sorted(TOTAL) if source_units[s] and s not in excluded]
    cats=[]
    for label in LABELS:
        contributors=[s for s in active if category_units[(s,label)]]
        cats.append(dict(category=label,meaning=DEFINITIONS[label],adopted_units=sum(len(category_units[(s,label)]) for s in active),adopted_targets=sum(category_targets[(s,label)] for s in active),benchmark_count=len(contributors),contributors='；'.join(f'{NAMES[s]}：{len(category_units[(s,label)]):,}' for s in contributors)))
    srcrows=[]
    for s in sorted(TOTAL):
        base=len(source_units[s]);used=base if s not in excluded else 0
        srcrows.append(dict(resource_id=s,benchmark=NAMES[s],archive_units=TOTAL[s],adopted_units=used,not_adopted_units=TOTAL[s]-used,previously_ineligible_units=TOTAL[s]-base,new_scope_excluded_units=base-used,adopted_targets=target_count[s] if used else 0,**{l:len(category_units[(s,l)]) if used else 0 for l in LABELS},reason=('本方案人为整来源排除；这是范围选择，不是新增技术不合格。v4已有未采用原因：' if s in excluded else '')+REASONS[s]))
    scenarios[key]=dict(benchmark_count=len(active),adopted_units=sum(r['adopted_units'] for r in srcrows),adopted_targets=sum(r['adopted_targets'] for r in srcrows),categories=cats,sources=srcrows)
    csvfile(key+'_categories.csv',cats);csvfile(key+'_sources.csv',srcrows)
assert scenarios['reduced_preview']['adopted_units']==7611
assert scenarios['reduced_preview']['adopted_targets']==8662
assert scenarios['reduced_preview']['benchmark_count']==4
assert len(REMOVE)==7 and all(source_units[s] for s in REMOVE)
for label in ('R2','R4'):
    assert next(r for r in scenarios['v4']['categories'] if r['category']==label)['adopted_units']==next(r for r in scenarios['reduced_preview']['categories'] if r['category']==label)['adopted_units']
(OUT/'summary.json').write_text(json.dumps(scenarios,ensure_ascii=False,indent=2)+'\n')

font=FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
plt.rcParams.update({'font.family':font.get_name(),'font.size':11,'axes.unicode_minus':False})
for key,title in [('v4','方案一：当前 v4'),('reduced_preview','方案二：排除七个来源后的预览')]:
    data=scenarios[key]
    fig,(ax,bx)=plt.subplots(1,2,figsize=(16,8),gridspec_kw={'width_ratios':[1,1.6]})
    vals=[r['adopted_units'] for r in data['categories']];ax.barh(LABELS,vals,color='#187c75');ax.invert_yaxis();ax.set_xlim(0,35872*1.24)
    for i,v in enumerate(vals):ax.text(v+35872*.02,i,f'{v:,}',va='center')
    ax.set_title('各类别采用单元（允许重叠）',pad=15);ax.set_xlabel('比较单元数')
    rows=data['sources'];left=[0]*len(rows)
    for field,label,color in [('adopted_units','采用','#187c75'),('new_scope_excluded_units','本方案新增排除','#df9a3c'),('previously_ineligible_units','v4原已未采用','#cbd5e1')]:
        vals=[r[field] for r in rows];bx.barh(range(len(rows)),vals,left=left,height=.65,color=color,label=label);left=[a+b for a,b in zip(left,vals)]
    bx.set_yticks(range(len(rows)),[r['resource_id']+' '+({'M05':'LabTest','M06':'HIV情景','M11':'Cultural Cues'}.get(r['resource_id'],r['benchmark'])) for r in rows]);bx.invert_yaxis()
    for i,r in enumerate(rows):bx.text(r['archive_units']+170,i,f"采用 {r['adopted_units']:,}",va='center',fontsize=9)
    bx.set_xlim(0,16000);bx.set_title('15个已取得来源：采用与未采用',pad=15);bx.set_xlabel('母库比较单元数');bx.legend(loc='upper center',bbox_to_anchor=(.42,-.09),ncol=3,frameon=False,fontsize=9)
    for a in (ax,bx):a.spines[['top','right','left']].set_visible(False);a.grid(axis='x',alpha=.15);a.set_axisbelow(True);a.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4));a.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    fig.suptitle(f"{title}｜{data['benchmark_count']} 个采用来源 · {data['adopted_units']:,} 个去重单元",x=.04,ha='left',fontsize=19)
    fig.subplots_adjust(left=.05,right=.98,top=.88,bottom=.14,wspace=.70)
    fig.text(.04,.025,'采用 = 至少一个具体目标分类与评分资格合格；不是独立模型输入数。方案二仅为预览，v4未修改。',fontsize=10,color='#475569')
    for ext in ('png','pdf'):fig.savefig(OUT/(key+'.'+ext),dpi=160)
    plt.close(fig)

lines=['# R1–R5 benchmark：当前 v4 与排除七来源方案对比','',
'本报告以 v4 最终逐目标标注和资格文件复算。**方案一是现有 v4；方案二是用户指定七个来源全部移除后的预览，未修改 v4 或 v3。** 两种方案均包含分类表、每类来源构成、逐来源采用数量、未采用理由和图。','',
'## 统计口径','',
'- **采用单元**：该比较单元至少有一个带R1–R5标签且 `evaluation_eligible=true` 的具体目标。某类别采用数只计该类别有合格目标的单元。',
'- 同一单元可以属于多个类别，因此R1–R5数量不可直接相加；来源之间按原ID分开计，来源采用数可相加得到总数。',
'- **benchmark数量按Mxx来源项目计**，不把文本变体、原题、子目标或MedRGB文档槽位拆成多个benchmark；FairMedQA/AMQA按一个来源计算。不同来源可能共享底层题库，来源数不等于相互独立题库数。',
'- 每个来源的分母是已归档比较母库，**不是作者发布包的全部行数**。普通原题参照、无变化记录、作者train/valid、获取缺口分别说明，不冒充抽样遗漏。',
'- 已分类但无评分资格的内容不进入主表的采用数。评分资格不等于M0–M4运行兼容性已验证；独立输入和评分映射尚未物化。','',
'## 两种方案概览','',
'| 项目 | 方案一：当前v4 | 方案二：排除后预览 |','|---|---:|---:|',
'| 已取得来源范围 | 15 | 同一15个来源用于对照 |','| 实际采用来源 | **11** | **4** |','| 本次新增整来源排除 | 0 | **7** |','| 原本无合格内容的来源 | 4 | 4，保持不变 |','| 去重采用单元 | **38,123** | **7,611** |','| 采用的具体判断 | **77,781** | **8,662** |','| 未取得来源 | 11 | 11，均不进入分母 |','',
'方案二从v4已采用的11个来源中排除7个，因此剩4个；在15个已取得来源范围内，共11个不再/未曾贡献采用内容，即7个新增范围排除加4个既有不合格来源。','']
for key,title in [('v4','方案一：当前 v4'),('reduced_preview','方案二：排除七来源后的预览')]:
    data=scenarios[key];lines+=['## '+title,'',f"实际采用 **{data['benchmark_count']} 个来源、{data['adopted_units']:,} 个去重比较单元、{data['adopted_targets']:,} 个具体判断**。",'',f'![{title}]({key}.png)','',f'[图PDF]({key}.pdf) · [类别表CSV]({key}_categories.csv) · [来源表CSV]({key}_sources.csv)','','### R1–R5 各类内容与来源','','| 类别 | 含义 | 采用单元 | 采用具体判断 | 来源数 | 每来源采用单元 |','|---|---|---:|---:|---:|---|']
    for r in data['categories']:lines.append(f"| {r['category']} | {r['meaning']} | {r['adopted_units']:,} | {r['adopted_targets']:,} | {r['benchmark_count']} | {r['contributors']} |")
    lines+=['','### 每个已取得来源采用了多少内容','','采用数按单元去重；未采用数=母库−采用。表中的未采用包含参照/作者划分以及不合格内容，不能统称题目质量差。完整R1–R5逐来源列及目标数在CSV中。','','| 来源 | 母库单元 | 采用单元 | 未采用单元 | 本次额外排除原合格单元 | 未采用原因 |','|---|---:|---:|---:|---:|---|']
    for r in data['sources']:lines.append(f"| {r['resource_id']} {r['benchmark']} | {r['archive_units']:,} | {r['adopted_units']:,} | {r['not_adopted_units']:,} | {r['new_scope_excluded_units']:,} | {r['reason']} |")
    lines.append('')
lines+=['## 七个新增排除来源的影响','','以下是用户指定的范围排除，不把数量较多改写成数据无法评分的正式理由。该方案移除30,512个原合格单元，涉及69,119个具体判断；不改变任何保留目标的分类。','','| 排除来源 | 原合格单元 | 减少R1 | 减少R2 | 减少R3 | 减少R4 | 减少R5 |','|---|---:|---:|---:|---:|---:|---:|']
for r in scenarios['v4']['sources']:
    if r['resource_id'] in REMOVE:lines.append('| '+r['benchmark']+' | '+f"{r['adopted_units']:,}"+' | '+' | '.join(f"{r[l]:,}" for l in LABELS)+' |')
lines+=['','R2保持79、R4保持13；R1减少990、R3减少43、R5减少30,225。保留的R5全部来自DiversityMedQA，覆盖7,611个单元的约74.2%；R4全部来自HIV情景研究。类别和来源的关联更强，不能把这直接解释为类别难度差异。','',
'## 为什么分母不等于作者发布包全量','','以下是母库之外的参照/划分边界，未被重复计作母库内未采用单元。','',
'| 来源 | 发布范围与归档边界 |','|---|---|']
for r in inventory:
    if r['acquisition_status']=='obtained':lines.append(f"| {r['resource_id']} {r['benchmark']} | {r['formal_scope_and_exclusion_basis']} |")
lines+=['','## 11个获取缺口','','这些来源没有取得所需固定输入，属于获取缺口；不计作本次排除的7个，也不计入55,991母库分母。状态沿用本地获取记录，本报告没有重新联网获取。','','| 来源 | 缺口 |','|---|---|']
for r in inventory:
    if r['acquisition_status']!='obtained':lines.append(f"| {r['resource_id']} {r['benchmark']} | {r['acquisition_gap']} |")
lines+=['','## 复算与文件入口','','[当前v4说明](../../DELIVERY.md) · [分类规则和示例](/home/data3/txy/R1_R5_CLASSIFICATION_GUIDE.md) · [机器可读汇总](summary.json)','','本报告采用已保存的分类与资格记录，没有用旧模型预测反推标签。源级原因是逐目标裁决的归纳；同一未采用单元可同时存在多个原因，主表不将不同原因重复相加。MedPerturb的RESOURCE与VISIT/MANAGE独立计目标，单元只计一次；MedRGB主问合格不会自动使所有辅助目标合格。','',f'本地权威目录：`{RUN}`。读取 `exports/all_reviewed_target_annotations.jsonl.gz` 与 `exports/archive_unit_coverage.csv`；来源及原件定位见 `source_scope_inventory.csv`。旧无变化控制资格覆盖已经包含在最终导出中。','','`build_report.py`保留复算过程；在本地 v4 的 `reports/two_scenarios/` 下，用已有Matplotlib环境运行。本GitHub目录只发布说明、汇总和图表，不发布完整病例正文。']
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:{a:v[a] for a in ('benchmark_count','adopted_units','adopted_targets')} for k,v in scenarios.items()},ensure_ascii=False))
