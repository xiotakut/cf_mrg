# CF-MoA 共同作者研究底稿

这是供所有作者共同写作使用的 raw 研究材料：让没有参加全程的人理解项目为何开始、实际做过什么、结果如何促成下一步，以及这些事实可以怎样组成论文。

**[完整中文底稿](research_dossier.md) · [41页 PDF](research_dossier.pdf) · [LaTeX 阅读版](research_dossier.tex) · [完整下载包](../cf_moa_author_dossier.zip)**

正文约3.1万汉字、八章、33张表；记录实验事实截至2026-09-28，10-03只做核验、整理和排版。论文主线是来源收集与五类功能体系 → benchmark → 七系统诊断 → 五head → 五操作CF-MoA。

| 章节 | 读完应能回答的问题 |
|---|---|
| 一、共同认识 | 最初研究目的是什么，R/head/A/M/B/F各指什么，各分母怎样区分？ |
| 二、研究前史 | 医学RAG、WM、CF-WM、Adapter如何推进，为什么转向原生任务与功能关系？ |
| 三、数据与分类 | 26候选怎样变成15取得来源，经过哪些审核纠错与版本变化，最终11来源如何进入v5？ |
| 四、七系统和五head | 七配置怎么实现，每个head为什么提出，哪些对照支持它，哪些候选失败或停止？ |
| 五、CF-MoA | 五角色怎样包装与路由，真实聚合尝试了什么，为何采用B，双骨干六臂全量怎样收尾？ |
| 六、作者逻辑与数据取舍 | 哪些贡献成立，哪些完整结果优先进入正文，怎样突出优势并保留必要控制？ |
| 七、完成状态和复现 | 哪些已完成、未采用或未执行，资源与协议差异为何重要？ |
| 八、证据地图 | 如何找到连续工作汇报、原记录、原始表和逐题证据？ |

## 原记录与核验

- `records/`：29份科研主记录的冻结快照，正文保留原工作区路径；[SOURCE_MAP.json](SOURCE_MAP.json)记录原路径、复制位置与哈希。
- [148阶段索引](evidence/head_stage_register.csv)：R1–R5全过程报告逐阶段定位；[主记录标题索引](evidence/section_register.csv)来自初始快照，后增R3更正见该记录顶部。
- `sources/`：本文直接引用的审计、采样、修正与原始计划小型证据；后期完整收尾数字链接仓库中已有的冻结交付。
- [全文与数表核验](evidence/final_review.json)、[数据/方法独审](evidence/data_heads_review.json)、[CF-MoA独审](evidence/cf_review.json)、[排版验收](evidence/layout_review.json)。阅读范围区分本轮直接再读与此前审计复用。
- 原始82MB输入文件、模型权重、索引和全部运行日志不重复镜像入本文材料；[大型依赖说明](LOCAL_DEPENDENCIES.md)保留位置与哈希。源数据、标签、预测和评分未修改。

**一项新更正：** 旧框架把早期40题患者目录选择写成两骨干18/18，混合了不同配置。本底稿第4.5节及[R3主记录补记](records/research/r3_candidate_comparison.md#r3-name-control-identity-correction-20261003)列出准确六臂和128/384 token预算；应以这里为准。旧框架保留原历史身份。

## 阅读版重建

此底稿的协作源为中文Markdown，LaTeX/PDF由Pandoc导出；正式英文论文继续以[原生LaTeX](../latex/main.tex)维护。这里只构建文档，不运行实验。

安装Pandoc、Tectonic及文泉驿/DejaVu字体后，在本目录执行：

```bash
python3 build_dossier.py --input research_dossier.md --output research_dossier.tex \
  --link-base-url https://github.com/xiotakut/cf_mrg/blob/main/papers/2026-10-02_cf_moa/author_dossier/
```

可以用`--pandoc`、`--tectonic`、`--font`、`--main-font`和`--mono-font`覆盖本地路径/字体。已有Tectonic缓存时可加`--only-cached`；直接运行`tectonic research_dossier.tex`也可编译交付的独立LaTeX。PDF外部链接指向私有GitHub，需相应仓库访问权限。

[此前论文框架](../framework/README.md)与[已有完整英文稿](../latex/README.md)各自保留。本轮交付是作者研究底稿，不表示新增模型实验或完成最终独立确认。
