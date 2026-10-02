> 发布前冻结历史（2026-10-02）：此 GitHub 副本仅增加本说明并调整链接，正文保留发布前的状态和决定；文中的“未发布到 GitHub”及“不上传论文”描述当时状态。未改动的原件保存在 [原始 ZIP](cf_moa_paper_bundle.zip) 中。持续写作记录仍维护于本地 `/home/data3/txy/docs/paper/writing_record.md`。

# CF-MoA 会议论文写作记录

最新状态：2026-10-02（Asia/Shanghai），已完成通用英文会议论文初稿、中文框架、5 组实验图、8 组表格及复现脚本。英文 PDF 18 页（含声明、附录与参考文献），20 条参考文献已核验，正文结果经独立事实检查及一次定向审阅修订。用户指定历史对话 `01a0c3d0-3536-7e00-9d80-443d757d3153`，并明确本次交付为已有实验的论文表格、图和复现脚本；本次 0 新模型、0 native grader、0 GPU 操作。

交付：[英文 PDF](manuscript.pdf) · [Word](manuscript.docx) · [中文框架](outline.zh.md) · [持续正文](manuscript.md) · [制品和复现入口](README.md)。仍是可审阅初稿，作者/单位/贡献、资助、冲突及适用伦理声明待作者填写，未选择投稿 venue 或发布到 GitHub。

本文负责论文组织、主张与证据映射、写作工具选择及交付验证。正式进入论文写作，需分别维护正文、中文框架与写作记录，故新增 `docs/paper/`；实验事实及历史仍以 [CF-MoA 主记录的 09-28 快照](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-28_cf_moa_transparent_closeout/docs/research/cf_moa.md#transparent-closeout-20260928)、本地统一协议 `/home/data3/txy/docs/evaluation/protocol.md`和本地数据构建记录 `/home/data3/txy/docs/data/construction.md`为准，不迁移或重复维护运行历史。

## 范围与证据冻结

主范围为 2026-09-28 完整 v5 透明收尾：每骨干 13,905 输入、15,616 评分映射、6,104 非参考原生单元，两骨干六臂。原始收尾包为 `/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/closeout_20260928/`，公开提交 `2d56c71`，其所引全量推理版本为 `d857934`。论文图表仅重新整理已有汇总与区间；不重算模型或原生 grader，不改原始分数、标签、方法默认或 GPU 状态。

论文须区分既有采用核心 B 与新增候选验证 C3。B−C0 的整体收益不能写成 C3 的贡献；C3−B 的两骨干方向不一致。全 v5 是已暴露开发评测，冻结后确认与独立 F 复本未执行。A4 在临床 v5 覆盖为 0，旧模型内工具验证只能单列。

## 本次工作与交付位置

- 计划：核验历史对话与机器可读汇总；联网比较含真实论文写作 SKILL.md 的 GitHub 仓库 stars；固定工具版本并依其工作流形成框架、正文、核验引用与审稿检查。
- 计划：正文写入 `docs/paper/manuscript.md`，中文框架与主张映射写入 `docs/paper/outline.md`。
- 计划：图表、LaTeX/PDF、参考文献、复现脚本和来源哈希置于 `/home/data3/txy/Documents/Codex/2026-10-02/cf_moa_paper/`。运行包 README 仅承担命令与制品导航。
- 已发现环境细节：shell 无 `python` 命令；后续使用 `python3` 或已有 `MedRGAG/.venv/bin/python`，不因该检查安装或改变实验环境。

所有尚未完成项目保持“计划”；选定 skill、实际结果和验证在本记录后续补齐。

## 2026-10-02 选定写作 skill 与实际应用

联网搜索直接包含学术论文写作 `SKILL.md` 的仓库，并用 GitHub API 核验 stars。选定 [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) 的 [academic-paper](https://github.com/Imbad0202/academic-research-skills/blob/9201425a88d729a74aadd75c114f2f34851a93e9/academic-paper/SKILL.md)：首次选定 50,152 stars，存档重查 50,154；固定 commit 为 `9201425a88d729a74aadd75c114f2f34851a93e9`。这是仓库 star，不是单 skill 评分，也不声称穷尽互联网。

有效对比包括 K-Dense scientific-agent-skills 47,362、Orchestra AI-Research-SKILLs 13,190、Master-cai Research-Paper-Writing-Skills 7,210。更高 star 的通用文章/技术文档/awesome 清单在本次检查中未找到直接适用的学术论文写作 skill，未列入同一排名。候选、API 原件、检索范围及时间保存在 [skill_selection.json](evidence/skill_selection.json)。

使用预装 skill-installer 的安装脚本，以固定 commit 安装到 `/home/data3/txy/.codex/skills/academic-paper/`；本轮直接读取并应用，下轮可由 skill 发现机制加载。固定源 `shared/`、写作 skill、许可及只读缩写脚本另作 161 文件归档，160 个 Git blob 和完整 SHA 清单核验通过；未安装或执行 Claude 专用 hook/命令，没有设置额外 API 密钥。

实际采用配置记录→文献来源→结构和证据映射→正文→引用/摘要→独立审阅→格式导出流程。用户已授权完整可审阅初稿并确认语言/范围，依当前会话授权完成可逆写作，不重复停在阶段批准门。未声称用户逐条批准大纲，也未声称运行了上游 12-agent 编排、完整 generator/evaluator 合同认证或特定会议审核。适配边界记入 [paper_configuration.json](evidence/paper_configuration.json)。

## 已完成的证据、写作和审阅

只读提取指定对话两份 session 的用户决定和最后交付，确认 09-28 明确停止新增实验、默认 B 保持。独立从两骨干 `native_units.jsonl.gz`、`per_input_status.jsonl.gz` 和 `pairs.jsonl.gz` 重汇总，72 类别、132 来源、60 格式、24 配对及12臂总量与冻结 JSON 一致；没有导入 grader。原始六个压缩文件前后哈希不变。

正文围绕核心 B、同池 C2/C3、扩池 C4、整体选择 C5 构建，明确写出主指标公式、家族 bootstrap、失败分母、全部来源、资源归属和负结果。保留 A1/A2 共享核、123规则消融、A4临床覆盖0，以及旧24-profile条件面板的独立范围。没有将早期七方法、121/52开发面板拼成全量主成绩。

独立事实审计核验22项方法/数字、47行手写结果表，以及10个方法源码与 full-v5 resolved spec 的哈希对应；收据 [manuscript_fact_check.json](validation/manuscript_fact_check.json)绑定当时稿件版本。发现的两条精确化已修复：完成的验证才使用完整2K逻辑请求；F补齐seed42–46、五票后plurality与平票规则。

另一独立写作审阅按五维标准标为 `NOT_CALIBRATED`、`criteria_binding_unavailable`。两项主要问题是v5构建/抽样说明和MedCorp额外检索权限；另补family定义、修复/误伤解释与C4两个ALL点估计均正的准确措辞。全部修复保留[原审阅](evidence/peer_review.json)和[修订复核](evidence/revision_resolution.json)。后续将表3分母写回caption，补分类未报告临床专家一致性、DDXPlus上游归属、simglucose实际软件版本；不改结果行。

20条参考包括7项方法/模型背景、11来源、DDXPlus和simglucose。官方论文/数据卡/软件metadata逐项核验，记录版本差异及访问限制：MedEinst用ACL正式作者顺序，AMQA保留2025 v1，Llama保留v1身份，CPV论文与作者MedQA扩展区别明写；simglucose引用实际0.2.11和固定commit，不把README旧0.2.1推荐署名冒充实际版本。OpenReview部分直接访问受阻，官方PDF搜索可见信息与arXiv导出相互核验，未假称成功直接抓取。完整依据见 [reference_verification.json](evidence/reference_verification.json)。

## 图表、构建验证及失败记录

新包复制12个小型原汇总JSON（159,971字节），逐项记录原路径与SHA。使用原有MedRGAG venv 的 matplotlib3.10.9、numpy1.26.4、pandas2.3.3生成5组矢量PDF/300dpi PNG和8组CSV/LaTeX表，共26个图表制品。完整构建加原始记录核验9.6476秒；只检查加原始记录核验3.9469秒；[构建收据](validation/build_receipt.json)与[检查收据](validation/check_receipt.json)保存命令、版本、hash。五图已实际目视检查。

论文渲染依赖仅安装到本包 `.build_deps`：pypandoc_binary1.17（Pandoc3.9）、Typst0.15.0、PyMuPDF1.28.2，不修改模型实验环境。提供PDF、DOCX、自包含HTML、渲染Markdown、LaTeX和Typst；PDF实际由Typst编译。LaTeX源码引用矢量图，但环境无TeX引擎，未编译，不将源码导出冒称LaTeX编译通过。20引用键双向匹配、PDF关键数字/章节存在、18页页面边界检查通过；已目视查看全部页面缩略图和首面/数据表/附录放大页。

保留实际构建失败：[build_attempts.json](validation/build_attempts.json)。`uv venv`因snap用户目录权限失败，`python -m venv`因ensurepip缺失失败，改用本包 `pip --target`；不修改权限或系统依赖。首次Typst编译遇Pandoc输出旧`sect`交集别名，构建器仅替换为当前`inter`，原LaTeX的集合交集不改；随后编译通过。表格关闭两端对齐并缩短表头，保留caption分母。

上游缩写脚本已实际只读运行；原始报告包含对算法ID、模型名及连字符RAG定义的机械提示，无须把这些提示当研究失败。MIRAGE/CRediT已补展开；最终报告与人工处置随包保存。PDF、引用和输出hash的最终结果见 [manuscript_build_receipt.json](validation/manuscript_build_receipt.json)及[最终编辑检查](validation/final_editorial_checks.json)。

## 交付边界与后续

本次完整完成用户明确要求的初稿和已有实验图表/脚本。当前不运行补充实验，不恢复队列，不上传论文。独立新家族确认、第二份F候选池仍未执行；本次离线重建不能升级为新推理复现或独立泛化。下一步是作者审阅贡献措辞、填写真实作者和声明，并在选定会议后按其格式调整；是否实际恢复独立确认属于另一次研究决定。
