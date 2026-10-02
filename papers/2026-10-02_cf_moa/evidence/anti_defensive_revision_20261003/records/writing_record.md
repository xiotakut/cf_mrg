# CF-MoA 医学反事实论文写作记录

2026-10-03 用户指定Kiterlin anti-defensive-writing的全文修订已完成：[19页PDF](latex/main.pdf) · [LaTeX](latex/main.tex) · [工程ZIP](../../Documents/Codex/2026-10-03/cf_moa_full_manuscript/anti_defensive_revision/cf_moa_latex.zip)。14章节修订，3图/14表/29引用与实验结果保持，独立内容审阅和编译通过；[本轮记录](#kiterlin-manuscript-revision-20261003)。

2026-10-03 写作skill补充检索完成：[高star去防御性写作工具比较](#anti-defensive-skill-search-20261003)。本轮核验相关独立工具Humanizer 53,578★、专用Anti-Defensive Writing最高2,052★；同时比较学术适配；补查规则更新时间，Kiterlin 09-30晚于Humanizer 09-28；另确认[Defensive Writing Governance](#governance-skill-identification-20261003)同名插件与skill。仅检索、读取指令和记录选型，未安装或修改论文。

2026-10-03 完整论文已重写并核验：[20页英文PDF](latex/main.pdf) · [原生LaTeX](latex/main.tex) · [Overleaf工程ZIP](../../Documents/Codex/2026-10-03/cf_moa_full_manuscript/cf_moa_latex.zip)。五类体系、benchmark、七系统诊断、五head与CF-MoA主线现已展开为全文，3图、14表、29引用；独立事实/写作审阅、异目录编译与全部页面文字/像素一致性通过。[本轮全过程](#full-manuscript-rewrite-20261003)。同日下方28页/框架条目为之前阶段。

2026-10-03 投稿准备度评估：[当前实验证据与顶会主张的对应](#submission-readiness-20261003)。判断为已有完整成文基础，benchmark/功能诊断路线比“新MoA协同算法普遍领先”更受现有证据支持；独立系统确认、资源对齐归因与taxonomy质量验证是优先补强建议，尚未执行。

2026-10-03 作者研究底稿已完成：[research_dossier.md](research_dossier.md)共31,393汉字、八章、33表，[LaTeX/PDF阅读版](latex/research_dossier.pdf)41页。汇总原始目的、数据、版本、各方法/阶段、成功失败、证据与写作逻辑，供全体作者共同写作。已上传私有GitHub，提交`787e63c`；[完成与验收](#author-research-dossier-20261003)。

2026-10-03 主线框架已完成：用户进一步明确“反事实资源收集→五类体系→benchmark构建→多RAG诊断→五head/五agent→CF-MoA”才是研究目的。已交付完整逻辑链、10页原生LaTeX框架与已有证据选用方案；当前28页稿是上一轮版本，不视为已经按新框架完成重写。

2026-10-03 范围纠正已完成：[28 页 LaTeX 论文](latex/main.pdf)已恢复七配置正式基线、七系统 R1–R3 优化与后期双配置六臂研究三层主线，共 11 表、6 图、24 条引用；[LaTeX 主稿](latex/main.tex)、[中文框架](outline.md)及[Overleaf ZIP](../../Documents/Codex/2026-10-03/paper_scope_audit/cf_moa_latex.zip)已更新至私有 GitHub。数值、独立审阅、整稿和异目录编译、远端字节核验均通过。完整过程见[本轮记录](#seven-system-scope-correction-20261003)。

上一版状态：2026-10-02，已按用户要求改为直接维护 [LaTeX 主稿](latex/main.tex)及分章节 `.tex`；[21 页英文 PDF](latex/main.pdf)由 Tectonic 0.17.0（XeTeX + BibTeX + xdvipdfmx）实际编译。提供 [Overleaf 工程 ZIP](../../Documents/Codex/2026-10-02/cf_moa_paper_latex_build/cf_moa_latex.zip)，引用、数字、页面及异目录重新编译检查通过。旧 Markdown/Typst 为冻结历史。

初稿历史状态：2026-10-02（Asia/Shanghai），已完成通用英文会议论文初稿、中文框架、5 组实验图、8 组表格及复现脚本。英文 PDF 18 页（含声明、附录与参考文献），20 条参考文献已核验，正文结果经独立事实检查及一次定向审阅修订。用户指定历史对话 `01a0c3d0-3536-7e00-9d80-443d757d3153`，并明确本次交付为已有实验的论文表格、图和复现脚本；本次 0 新模型、0 native grader、0 GPU 操作。

初稿历史交付：[英文 PDF](../../Documents/Codex/2026-10-02/cf_moa_paper/manuscript.pdf) · [Word](../../Documents/Codex/2026-10-02/cf_moa_paper/manuscript.docx) · [中文框架](outline.md) · [冻结 Markdown 正文](manuscript.md) · [制品和复现入口](../../Documents/Codex/2026-10-02/cf_moa_paper/README.md)。仍是可审阅初稿，作者/单位/贡献、资助、冲突及适用伦理声明待作者填写，未选择投稿 venue。随后已按用户要求发布到 [GitHub 论文目录](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa)，仓库已设为 private；[发布与可见性验收](../workspace.md#cf-moa-paper-github-private-20261002)归工作区主记录。

本文负责论文组织、主张与证据映射、写作工具选择及交付验证。正式进入论文写作，需分别维护正文、中文框架与写作记录，故新增 `docs/paper/`；实验事实及历史仍以 [CF-MoA 主记录](../research/cf_moa.md#transparent-closeout-20260928)、[统一协议](../evaluation/protocol.md)和[数据构建](../data/construction.md)为准，不迁移或重复维护运行历史。

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

有效对比包括 K-Dense scientific-agent-skills 47,362、Orchestra AI-Research-SKILLs 13,190、Master-cai Research-Paper-Writing-Skills 7,210。更高 star 的通用文章/技术文档/awesome 清单在本次检查中未找到直接适用的学术论文写作 skill，未列入同一排名。候选、API 原件、检索范围及时间保存在 [skill_selection.json](../../Documents/Codex/2026-10-02/cf_moa_paper/evidence/skill_selection.json)。

使用预装 skill-installer 的安装脚本，以固定 commit 安装到 `/home/data3/txy/.codex/skills/academic-paper/`；本轮直接读取并应用，下轮可由 skill 发现机制加载。固定源 `shared/`、写作 skill、许可及只读缩写脚本另作 161 文件归档，160 个 Git blob 和完整 SHA 清单核验通过；未安装或执行 Claude 专用 hook/命令，没有设置额外 API 密钥。

实际采用配置记录→文献来源→结构和证据映射→正文→引用/摘要→独立审阅→格式导出流程。用户已授权完整可审阅初稿并确认语言/范围，依当前会话授权完成可逆写作，不重复停在阶段批准门。未声称用户逐条批准大纲，也未声称运行了上游 12-agent 编排、完整 generator/evaluator 合同认证或特定会议审核。适配边界记入 [paper_configuration.json](../../Documents/Codex/2026-10-02/cf_moa_paper/evidence/paper_configuration.json)。

## 已完成的证据、写作和审阅

只读提取指定对话两份 session 的用户决定和最后交付，确认 09-28 明确停止新增实验、默认 B 保持。独立从两骨干 `native_units.jsonl.gz`、`per_input_status.jsonl.gz` 和 `pairs.jsonl.gz` 重汇总，72 类别、132 来源、60 格式、24 配对及12臂总量与冻结 JSON 一致；没有导入 grader。原始六个压缩文件前后哈希不变。

正文围绕核心 B、同池 C2/C3、扩池 C4、整体选择 C5 构建，明确写出主指标公式、家族 bootstrap、失败分母、全部来源、资源归属和负结果。保留 A1/A2 共享核、123规则消融、A4临床覆盖0，以及旧24-profile条件面板的独立范围。没有将早期七方法、121/52开发面板拼成全量主成绩。

独立事实审计核验22项方法/数字、47行手写结果表，以及10个方法源码与 full-v5 resolved spec 的哈希对应；收据 [manuscript_fact_check.json](../../Documents/Codex/2026-10-02/cf_moa_paper/validation/manuscript_fact_check.json)绑定当时稿件版本。发现的两条精确化已修复：完成的验证才使用完整2K逻辑请求；F补齐seed42–46、五票后plurality与平票规则。

另一独立写作审阅按五维标准标为 `NOT_CALIBRATED`、`criteria_binding_unavailable`。两项主要问题是v5构建/抽样说明和MedCorp额外检索权限；另补family定义、修复/误伤解释与C4两个ALL点估计均正的准确措辞。全部修复保留[原审阅](../../Documents/Codex/2026-10-02/cf_moa_paper/evidence/peer_review.json)和[修订复核](../../Documents/Codex/2026-10-02/cf_moa_paper/evidence/revision_resolution.json)。后续将表3分母写回caption，补分类未报告临床专家一致性、DDXPlus上游归属、simglucose实际软件版本；不改结果行。

20条参考包括7项方法/模型背景、11来源、DDXPlus和simglucose。官方论文/数据卡/软件metadata逐项核验，记录版本差异及访问限制：MedEinst用ACL正式作者顺序，AMQA保留2025 v1，Llama保留v1身份，CPV论文与作者MedQA扩展区别明写；simglucose引用实际0.2.11和固定commit，不把README旧0.2.1推荐署名冒充实际版本。OpenReview部分直接访问受阻，官方PDF搜索可见信息与arXiv导出相互核验，未假称成功直接抓取。完整依据见 [reference_verification.json](../../Documents/Codex/2026-10-02/cf_moa_paper/evidence/reference_verification.json)。

## 图表、构建验证及失败记录

新包复制12个小型原汇总JSON（159,971字节），逐项记录原路径与SHA。使用原有MedRGAG venv 的 matplotlib3.10.9、numpy1.26.4、pandas2.3.3生成5组矢量PDF/300dpi PNG和8组CSV/LaTeX表，共26个图表制品。完整构建加原始记录核验9.6476秒；只检查加原始记录核验3.9469秒；[构建收据](../../Documents/Codex/2026-10-02/cf_moa_paper/validation/build_receipt.json)与[检查收据](../../Documents/Codex/2026-10-02/cf_moa_paper/validation/check_receipt.json)保存命令、版本、hash。五图已实际目视检查。

论文渲染依赖仅安装到本包 `.build_deps`：pypandoc_binary1.17（Pandoc3.9）、Typst0.15.0、PyMuPDF1.28.2，不修改模型实验环境。提供PDF、DOCX、自包含HTML、渲染Markdown、LaTeX和Typst；PDF实际由Typst编译。LaTeX源码引用矢量图，但环境无TeX引擎，未编译，不将源码导出冒称LaTeX编译通过。20引用键双向匹配、PDF关键数字/章节存在、18页页面边界检查通过；已目视查看全部页面缩略图和首面/数据表/附录放大页。

保留实际构建失败：[build_attempts.json](../../Documents/Codex/2026-10-02/cf_moa_paper/validation/build_attempts.json)。`uv venv`因snap用户目录权限失败，`python -m venv`因ensurepip缺失失败，改用本包 `pip --target`；不修改权限或系统依赖。首次Typst编译遇Pandoc输出旧`sect`交集别名，构建器仅替换为当前`inter`，原LaTeX的集合交集不改；随后编译通过。表格关闭两端对齐并缩短表头，保留caption分母。

上游缩写脚本已实际只读运行；原始报告包含对算法ID、模型名及连字符RAG定义的机械提示，无须把这些提示当研究失败。MIRAGE/CRediT已补展开；最终报告与人工处置随包保存。PDF、引用和输出hash的最终结果见 [manuscript_build_receipt.json](../../Documents/Codex/2026-10-02/cf_moa_paper/validation/manuscript_build_receipt.json)及[最终编辑检查](../../Documents/Codex/2026-10-02/cf_moa_paper/validation/final_editorial_checks.json)。

## 交付边界与后续

本次完整完成用户明确要求的初稿和已有实验图表/脚本。当前不运行补充实验，不恢复队列，不上传论文。独立新家族确认、第二份F候选池仍未执行；本次离线重建不能升级为新推理复现或独立泛化。下一步是作者审阅贡献措辞、填写真实作者和声明，并在选定会议后按其格式调整；是否实际恢复独立确认属于另一次研究决定。

## 2026-10-02 GitHub 交付

用户追加要求在既有 GitHub 仓库新建目录上传并设为 private，现已完成。论文/图表/代码和原始 ZIP 保持冻结，仅发布副本的导航、历史说明与复现命令作路径适配；持续正文不变。提交、文件转换、远端字节核验和私有化证据统一见 [工作区发布主记录](../workspace.md#cf-moa-paper-github-private-20261002)，不在本记录重复维护发布过程。

## 2026-10-02 改为 LaTeX 主稿（已完成）

用户指出应直接用 LaTeX 写作。此前 PDF 确实来自 Typst，`.tex` 只是未编译导出；本轮纠正为直接维护 `latex/main.tex`、分章节 LaTeX、BibTeX 与矢量图，并真实编译验证。只迁移写作格式和交付入口，不修改实验证据。沿用已授权私有 GitHub 论文目录更新交付；旧 ZIP 与发布提交保留历史。

当前 shell 未发现 xelatex、lualatex、pdflatex、latexmk 或 tectonic。选择官方 Tectonic 0.17.0 的 Linux musl 独立二进制，以 GitHub release API 的 SHA-256 核对下载后安装到用户目录 `.local/opt/tectonic-0.17.0/`，不改系统或模型实验环境。官方文档经 web 工具访问返回不可访问，改由官方 GitHub release API 核验资产及版本；安装证据为 `Documents/Codex/2026-10-02/cf_moa_paper_latex_build/toolchain_install.json`。尚待正文实际编译和页面检查，不将安装成功写成论文构建成功。

**实际完成。** 权威正文改为 `docs/paper/latex/main.tex`、14 个章节文件和 8 个原生表格文件，连同 5 个矢量 PDF、BibTeX、构建说明/脚本与已编译 PDF 共 34 个工程文件。已有 Markdown 仅做一次 Pandoc `--natbib` 迁移底稿，然后拆分整理为可直接编辑的 LaTeX；正常 `bash build.sh` 不依赖 Markdown、Pandoc 或 Typst。采用通用单栏 11pt/A4，不伪造会议模板或作者。20 条引文实际使用 natbib/BibTeX，标题仅增加花括号保护大小写，事实字段保持；4 公式与图表/章节引用改为 LaTeX 标签。旧 Markdown 加冻结说明前的完整字节另存 `cf_moa_paper_latex_build/prior_manuscript.md`，使先前审查哈希仍能回溯。

**实际编译与纠正。** 共五轮正文编译：第 1 轮成功但长 `scripts/build_figures_tables.py` 产生 119.35pt 溢出，改可折行 `\path` 并移除 XeTeX 不需要的 inputenc；第 2 轮零日志警告，目视发现声明尾段单独占页和伪代码跨页；收紧段距并以 minipage 保持代码后，第 3 轮出现 17pt 段首缩进溢出，添加 `\noindent` 修复。第 4 轮无警告，后将历史模型附录与其表格放到同页；第 5 轮形成最终 21 页 PDF。真实 TeX/BibTeX 日志、前后尝试及安装来源保存在 `cf_moa_paper_latex_build/`，没有将排版问题改写为未发生。

**最终验收。** PDF metadata 为 `LaTeX with hyperref` / `xdvipdfmx (0.1)`，SHA-256 `3c48023e95da9c93a84693ebe6cb09c50a336d5b96c9b3dc59b1bc6c929388f9`。BibTeX 0.99d 解析 20 条文献，最终日志无警告、Overfull/Underfull、缺字和未定义引用；页面文字均在页面范围内。已目视全部 21 页缩略图及首页、主表、区间图、历史模型表关键页。独立核查 8 表、54 数据行、228 单元、4 公式与 5 矢量图均与原稿/原制品一致；43 标签无重复或悬空。开发暴露、M4 负结果、默认 B 与独立确认未执行等限制保留。声明只更新真实私有发布状态，附录更新为直接 LaTeX 构建命令。

从独立目录解压 LaTeX ZIP 后，实际运行新的 Python 标准库入口调用 LaTeX；21 页、20 引用、零警告，PDF 逐页抽取文字与权威 PDF 完全相同。PDF 时间戳可使跨次构建的二进制哈希不同，未声称每次 PDF 字节必同。原结果输入、图表、制图脚本及初始 ZIP 均逐字保留。本轮 0 模型、0 grader、0 GPU/既有作业操作。

[构建收据](../../Documents/Codex/2026-10-02/cf_moa_paper_latex_build/latex_build_receipt.json) · [独立源码/页面审查](../../Documents/Codex/2026-10-02/cf_moa_paper_latex_build/source_audit.json) · [异目录编译](../../Documents/Codex/2026-10-02/cf_moa_paper_latex_build/portable_build_receipt.json) · [失败与修复](../../Documents/Codex/2026-10-02/cf_moa_paper_latex_build/latex_build_attempts.json)。GitHub 更新与私有状态验收归 [工作区发布记录](../workspace.md#cf-moa-paper-latex-github-20261002)。


<a id="seven-system-scope-correction-20261003"></a>

## 2026-10-03：七系统与全流程范围纠正（已完成）

用户要求查看项目全流程，并质疑为何论文只重点对比两个。当前检查确认这是写作范围选择失当：09-14 已完成 M0/M2/M3/M4/M5/M6/M7 七系统配置的正式 v5，09-15/16 还完成跨七系统的 R1/R2/R3 head 开发交付；后期 CF-MoA 六臂实验才限定 M4/M5 两种 MedRAG 配置。原记录 `r3_candidate_comparison.md#r3-result-status` 已明确承认七系统开发收益，不能以尚缺归因/泛化消解已有成果。

本轮按早期复现/WM/CF历史、数据分类与版本沿革、七方法基线及修复、R1–R5针对性研究、CF-MoA组合及候选验证到最终收尾分工核验；阅读边界与逐文件证据留在 `Documents/Codex/2026-10-03/paper_scope_audit/`，不把标题扫描或未读取的原始巨型日志声称为逐字通读。已从冻结评分文件只读重汇总七系统42项分类/ALL值并与正式CSV对应；其他组件整数与重合范围正在核对。本轮没有启动模型、grader、训练或GPU任务。

计划修订：以七系统 v5 主比较和 R1–R3 七系统优化结果恢复论文主线，之后单列双配置 CF-MoA 六臂及机制对照。用 seven evaluated system configurations，明确 M4/M5 同为 MedRAG，不声称七种独立算法或七个独立骨干。全量13,905输入、类别面板和外部/仿真范围分别报告，不把重合类别相加，也不将末端head复用伪称七条完整检索链全部重跑。论文直接改 LaTeX，完成后编译和同期更新已授权私有 GitHub 目录。

**全流程与数值核查已完成（2026-10-03）。** 七配置的 42 个原生类别/ALL 值从完整评分文件重汇总，均与正式 CSV 一致；各配置输入 ID 相同，均为 13,905 输入、15,616 映射、6,104 ALL 单元。R1/R2/R3 的 21 组前后整数也逐项连接正式基线，20,062/553/5,131 条方法×类别观察的原正确性无差异；R1/R2/R3 合计 3,678 个类别成员实际只有 2,941 个唯一单元，不相加当独立样本。诊断头保留各系统实际上下文和原模型新末端取分；规则事实由两骨干生成后与七种既有答案离线组合，不写成全部检索链重新运行。

准确身份为 Direct、MedRGAG、MA-RAG、MedRAG-Llama、MedRAG-Qwen、MedGENIE、TC-RAG 七系统配置、六方法家族、两骨干。M1 是早期初始检索对照，没有完整 v5；旧 M6 i-MedRAG 52/13,905 暂停后由 MedGENIE 替代，不能同时凑入当前七行。M4 结构输出修复与 M5 旧协议并存，资源、预算和接口不等同，不能把差值全归为算法。七基线旧 bootstrap 的 4,378 病例组与后期 CF-MoA 的 4,766 families 不混作同一统计设计。

专项成果与控制同时呈现：七系统 R1/R2/R3 均净增；R3 680 诊断主要增量来自目录重决策，投票/先验校正并非普遍更好。R2 同覆盖恒 None 总分七系统均超过默认头，但保留药物 9 题均 0/9；两边一起报告。R4 最终 288/288 是给定模型的仿真范围；R5 208 单元有限开发及未执行确认继续按真实状态交代。早期 WM/CF-WM/Adapter、v2/v3、v4分类/v5抽样与后期 CF-MoA 多轮负结果按实际阶段连接，不把旧协议高分并入正式 v5。后期 162,979 次物理调用只属于该全量阶段，不是整个项目总成本。

审计证据：[七基线与原始评分核验](../../Documents/Codex/2026-10-03/paper_scope_audit/seven_methods_audit.json)、[七系统头与归因控制](../../Documents/Codex/2026-10-03/paper_scope_audit/head_research_audit.json)、[早期与R4/R5阶段](../../Documents/Codex/2026-10-03/paper_scope_audit/early_r45_audit.json)、[根任务定向阅读范围](../../Documents/Codex/2026-10-03/paper_scope_audit/root_record_review.json)。阅读范围如实区分全文、定向章节和标题导航，没有声称逐字重读全部巨型运行日志。

新增四项方法引用使用一手来源核验：MedRGAG 的 WWW 2026 出版 PDF、MA-RAG 的作者固定仓库与 ICML 2026 官方目录、MedGENIE/TC-RAG 的 ACL 官方记录。ACM 403、Crossref 404、OpenReview 验证页面均保留访问限制，不冒称 DOI 全部在线解析成功；[核验记录](../../Documents/Codex/2026-10-03/paper_scope_audit/baseline_reference_verification.json)。

**正文与框架修订完成。** 题目改为 *Support Updating and Candidate Re-decision Across Seven Medical Question-Answering Systems*。摘要、引言、方法、设置、结果、讨论、局限和结论统一为七基线→七末端系统→后期双配置组合；新增研究发展附录，涵盖早期复现/WM/Adapter、数据/基线沿革、失败与撤回、R4/R5及后期组合取舍。原 8 表/5 图完整保留，新加七基线表、七 head 表、组件控制表和七系统三面板图，共 11 表/6 图。三张新增表、PDF/PNG 和冻结输入由 `scripts/build_scope_figures_tables.py` 离线重建；4 个输入哈希、42 基线值、21 组前后计数及 R3/R2 控制通过检查。原始评分核验与仅从汇总重画明确区分，实际复现命令随包交付。

**独立内容审查完成。** 审阅旧 14 节与新 15 节、main 和中文框架；数字和范围均通过。具体修订保留：MA-RAG 为每轮 8 候选、最多 4 轮；CUPCase 两骨干计数各以 18 为分母；R5 208 已含 64+128+16；ASCENT 47 来自源 train42/test5，冻结组件检查已执行，但后续定向研发暴露不能被消除。ASCENT/CUPCase 脚注补固定 source revision。新增引用使总数为 24，55 个 LaTeX 标签无重复或未定义引用。[独立审查](../../Documents/Codex/2026-10-03/paper_scope_audit/scope_manuscript_review.json)标明一般会议、未绑定具体 venue，不是外部同行评审认证。

**实际排版与验证。** 三轮整稿 LaTeX 编译均退出 0、日志零警告。前两轮 29 页，声明尾部落在几乎空白页；精简可用性/伦理/AI辅助声明且保留实质信息后，最终 28 页。验证脚本先遇系统 Python 缺 Pillow，改用已有 MedRGAG venv；随后 PDF 数学模式千分位逗号后提取出空格，修正检查的空白规范化，不改实验数字。全部页面文字边界通过，已目视 28 页缩略图及新增表、外部来源脚注和声明分页。完整记录见[构建尝试](../../Documents/Codex/2026-10-03/paper_scope_audit/build_attempts.json)与[编译收据](../../Documents/Codex/2026-10-03/paper_scope_audit/latex_build_receipt.json)。

最终 PDF SHA-256 为 `50a250296d3b8514183eee06580e7ea725cb11d6655dbd12eae5c99523b2f03e`。工程 40 文件，ZIP 476,084 字节；异目录解压并由 Python 标准库入口调用 Tectonic 成功，28 页/24 引用/零警告，逐页抽取文字与权威 PDF 完全相同。[异目录收据](../../Documents/Codex/2026-10-03/paper_scope_audit/portable_build_receipt.json)。缩写脚本也已运行，PDF提取/参考文献带来名称、软件、常量和 URL 片段提示，人工分类处置随包保留，不声称机械报告零提示。

**交付完成。** 已授权私有仓库同步见[工作区发布主记录](../workspace.md#seven-system-paper-github-20261003)。原始初稿 ZIP 和上一版 LaTeX ZIP/发布清单保留；完整 v5、head 预测及评分均未更改。本轮 0 模型、0 native grader、0 GPU 操作。最终稿仍需作者填写真实作者、单位和声明，并按选定会议调整格式；已完成七系统开发成果与尚未执行最终组合确认分别陈述。

<a id="taxonomy-benchmark-five-agents-20261003"></a>

## 2026-10-03：回到五类 benchmark 与五 agent CF-MoA 主线（框架完成）

用户指出上一轮仅补七方法仍未充分体现原始目的，要求从完整过程记录梳理研究路径，先形成整篇论文框架，再优先选择有利且真实的既有数据。此次按明确授权执行 outline-only：沿用 academic-paper 的结构/论证/证据映射工作流，不新增模型、grader、训练或数据改写。可以把强且完整的成果放主文，把更细的失败和扩展放附录；不删除会改变贡献解释的必要对照，不把适用小面板拼成完整临床验证，不把后验论证順序说成预注册历史。

分工核验：数据来源与R1–R5/构建沿革；最初Router+五专家目标与最终采用版身份；两份完整过程报告及各阶段连续记录。原七系统框架保存于 `Documents/Codex/2026-10-03/paper_story_alignment/prior_seven_system_outline.md`。长期框架继续使用 `docs/paper/outline.md`，本次证据清单与审计收据放同一运行证据目录，不另建重复研究主文档。计划提供原生 LaTeX 的独立框架文件及 PDF，保留上一版全文身份；最终采用数据须逐项给出分母、对照、来源和选用理由。

### 审计结论、框架与验证

已完成三条独立证据线：[数据贡献审计](../../Documents/Codex/2026-10-03/paper_story_alignment/benchmark_contribution_audit.json)、[五agent及数值审计](../../Documents/Codex/2026-10-03/paper_story_alignment/five_agent_framework_audit.json)、[完整研究路径](../../Documents/Codex/2026-10-03/paper_story_alignment/research_path_audit.json)。数据线重放8×450抽样，核验109,599判断语义保留、R1–R4全量集合及33原文件哈希；路径线定位09-08原始用户意图、148阶段head报告与CF-MoA后续报告，阅读范围在收据中明确，不冒称逐行重读所有原始日志。

主张定位已改为taxonomy＋benchmark＋七系统诊断＋五操作CF-MoA。采用B作为主方法身份，完整九行表保留全部类别；B−C0完整ALL +10.0934/+12.0129pp、保持和应变六组区间均正。五agent对应功能合同，A1/A2共享内核、A4条件面板、稀疏路由与原实际生成聚合负结果分别说明。C3是后续扩展，不能用两骨干择优拼新方法。R2恒None、A3目录控制、R4临床下降与F多数票对照保留相邻解释；有利数据选择的是完整已采用范围，不改分母、不重标数据。

交付为[中文完整框架](outline.md)、[framework.tex](latex/framework.tex)、[10页英文框架PDF](latex/framework.pdf)，新增三组CSV/LaTeX数据表与两张PDF/PNG图。main.tex及28页main.pdf未修改。生成脚本及冻结输入在证据包scripts/inputs/generated；`--check-only`从异目录验证通过，0模型/评分/GPU操作。Tectonic0.17.0直接编译，5张总表（含2张手写结构表）、2图、8实际引用；无未解析引用、overfull或出页文字，3条underfull表格警告为非阻断排版提示。十页联系图与关键页已目视检查。

独立[中英框架审阅](../../Documents/Codex/2026-10-03/paper_story_alignment/framework_review.json)通过。修正了无显著性检验时“显著”措辞、A4 no-do具体臂身份，补充40例名称规范/患者目录重决策的协议差别。acronym脚本已运行，其方法名拆分、图中文字顺序与参考文献缩写误报按项人工解释，未宣称机械零警告。最终PDF SHA-256：`9a8b97fc56f775eb9da52a6f89f0cf3a95db165ba4e3e0bf1dd71d602cb6a475`。异目录打包及私有GitHub发布验收另记workspace，框架尚未扩写成新全文。

异目录编译验证补记：首次要求PDF逐字节相同的断言失败；查明两个PDF的creationDate不同。改为实际复现验收后，10页提取文字和全部渲染像素逐页一致，源码/ZIP成员一致，编译通过；原失败与两个哈希保存在`paper_story_alignment/validation/isolated_build_receipt.json`。未改内容、分数或PDF元数据来迎合校验。

发布已完成：新框架及证据在[私有GitHub框架目录](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa/framework)，提交`80dcbcf`。403包文件＋根README共404个blob核验，六关键制品下载逐字一致，工作树干净；完整发布事实归[workspace](../workspace.md#cf-moa-framework-github-20261003)。此前完整稿和数据未变。

<a id="author-research-dossier-20261003"></a>
## 2026-10-03：作者共享raw研究底稿（已完成）

触发：用户明确上一轮交付的框架不足以让其他作者全面理解项目。本轮交付对象改为研究底稿：解释为什么做、实际怎样做、哪些实验属于哪个版本/分母、观察与转向、各项贡献怎样被已有证据支持、尚缺什么。保留完整研究事实，论文取舍建议另列；不再用“建议某节写什么”代替已完成工作的叙述。

新文档`docs/paper/research_dossier.md`职责为作者入组/共同写作的自足研究材料与跨方向论证，区别于`outline.md`的章节/主张布局，也不替代数据、方法、评测和研究主记录。该独立读者用途与具体交付符合新增主文档标准；完成时登记统一入口。沿用academic-paper的证据映射/事实审阅能力，当前不是正式论文全文或标准流水线认证。

并行整理数据与分类/构建、七基线与五head、CF-MoA全过程；主任务负责早期archive、全局时间线/版本与术语、证据导航、作者逻辑、合并与独立核验。审计输入和临时段稿在`Documents/Codex/2026-10-03/author_research_dossier/`，仅作为本次制品证据。0新模型/评分/训练/仿真，不操作GPU队列；沿用已授权私有GitHub发布。

### 本次内容及交叉核验

已将七份段稿合为八章：共同认识、研究前史、数据与分类、七系统与五head、CF-MoA、作者逻辑与数据取舍、完成状态和证据地图。包含完整26候选来源去向、11来源/五类分母、七系统42指标、21组head优化前后、六臂全类别72格/来源132格/格式60格、完整配对及费用；并解释WM、CF-WM、Adapter、head和聚合的失败与协议差异。29份科研主记录、初始2,199标题与148个head阶段建索引，阅读收据明确本轮直接再读与同会话既有审计复用，不声称重新逐行阅读所有原始大日志。

独立交叉审阅覆盖全部段稿。修正方法篇R2保留侧“五提高、一持平、一下降”的叙述；将辅助纠错、34题控制的双骨干并列数展开分母。新增发现：旧R3后期汇总18/18混合了40题探索配置，改为原始六臂表并写明128/384 token额度；该事实完整更正归[R3主记录](../research/r3_candidate_comparison.md#r3-name-control-identity-correction-20261003)，原历史汇总与原始成绩保留。本次不改任何实验输出。

中文Markdown为作者底稿协作源，Pandoc只负责导出LaTeX阅读版；正式英文论文仍直接维护原生`.tex`。导出使用现有Pandoc、Tectonic和文泉驿字体，没有安装模型环境。13页小样通过后，完整稿首次出现23处表格overfull，主要为长标识符与成本大整数；排版修复及复核在本轮构建收据中保存。先前英文main.tex/PDF与framework.tex/PDF不因本次整理而改写。

### 完成制品、验证及发布

最终[作者底稿](research_dossier.md)953行、31,393汉字、八章、54小节、33表（368个表格行含表头/分隔）。七份段稿逐行表格保全验证通过，唯一预先声明的表内文字修正是`format_input_results`文件名。初次严格相等检查因该正确指针替换而失败，纳入已批准变换后通过；没有改数或删除不利行。独立审阅、字段分母与来源核对见[最终审阅](../../Documents/Codex/2026-10-03/author_research_dossier/evidence/final_review.json)。

[LaTeX](latex/research_dossier.tex)及[PDF](latex/research_dossier.pdf)均已生成。最终41页、0 overfull、0缺字警告、7个嵌入字体、62书签和228链接；封面、目录、宽表及末页已目视检查。[排版收据](../../Documents/Codex/2026-10-03/author_research_dossier/evidence/layout_review.json)保存最初越界、修复和最终哈希。本地Markdown SHA256为`6dc191f0945756e81b3cd0ddb25e94772cc8d97d9cf7568c347ce28853f39adb`；PDF为`ad6f02dc220a9e5723eba563b6779c02069df8e89e3998b9cbe3d2a474532e42`。

GitHub阅读版只转换链接和一个大型原始输入的依赖说明，内容、数字与章节保持同一身份；PDF链接指向私有仓库并重新编译，仍41页、0缺字/越界。包内提供29份科研主记录快照、初始索引、独立审阅和来源映射，原始82MB输入保留路径/哈希而未重复镜像。旧框架关于40题R3的18/18混写在新入口明确标为被本底稿完整六臂更正，旧制品保持历史字节。

[私有GitHub作者材料](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa/author_dossier)已发布，提交`787e63c`。80文件作者包与ZIP逐字一致；完整论文目录484文件＋根README共485个远端blob核验通过，另下载六关键文件逐字核对、确认private和干净工作树。发布主事实与GitHub收据归[工作区发布记录](../workspace.md#author-dossier-github-20261003)，不再复制原实验结果。本轮任务完成，未启动任何未执行的模型确认或新实验。

<a id="submission-readiness-20261003"></a>
## 2026-10-03：当前实验是否足够支撑顶会论文

**触发与性质。** 用户询问当前实验是否足够、能否支撑顶会论文。本节为基于作者底稿及原核验的投稿准备度判断，不是实际会议评审、录用概率预测，也不是批准启动新实验。0新增推理、评分、训练、仿真或GPU操作；原稿、数据与发布快照不改。

**已有支撑。** 跨11来源的v5、五类功能定义及构建沿革、七配置完整比较、21组R1–R3 head提升、两骨干采用B的ALL +10.09/+12.01个百分点以及保持/应变改善，足以构成完整实证材料。来源/格式/成本/家族区间、正负结果和若干机制对照已经完成。ASCENT、CUPCase、规则探针及给定模型新profile验证也确实完成，不能概括为从未做外部或冻结后验证。细节归[作者底稿](research_dossier.md)，本节不重复维护数表。

**评审依据。** 2026-10-03查阅[NeurIPS 2026一般评审指南](https://neurips.cc/Conferences/2026/ReviewerGuidelines)、[Evaluations & Datasets指南](https://neurips.cc/Conferences/2026/EvaluationsDatasetsReviewerGuidelines)及[ARR评审指南](https://aclrollingreview.org/reviewerguidelines)。前两者强调主张获得支持、评测设计可靠、贡献价值及与既有工作的区别；E&D明确benchmark/分析的原创性可以来自任务、评测和揭示既有benchmark性质，不要求击败基线。ARR区分soundness、excitement与总体推荐，资源价值可构成贡献。这些是评估参照，不表示本次做过全部近邻文献新颖性检索，也不构成某一届次的投稿安排或承诺。

**判断。** 实验数量和材料厚度已有成文基础。以“功能taxonomy＋可追溯benchmark＋跨系统失败诊断＋功能专门化系统”为主线，比把论文押在“五个独立agent协作的新算法”上更贴合证据。当前不能称顶会主会竞争力已经充分确立；是否录用取决于最终主张、独立证据、近邻文献区别与评审，不给伪精确概率。采用既有组件本身并不否定创新，关键是产生什么可迁移设计或新见解。

主要缺口及其影响：

1. 完整B的当前主收益来自已暴露开发的v5，最终新家族确认未执行；旧数据重划分或旧随机seed不能恢复未见身份。已有组件验证也不能直接替代全系统确认。bootstrap区间并不校正长期开发选择。
2. B的收益尚不能全部归因于agent组织：A1/A2共享规则核，A4在临床v5零覆盖，真实生成聚合未优于B。目录/规则/额外取分或采样的作用已被部分控制揭示，但完整同工具单agent对照尚不完备。因此五角色框架可描述，五独立agent协同增益不能直接宣称。
3. taxonomy作为主要贡献，需要证明标签能被独立复核，且提供超出来源、题型、答案格式差异的诊断价值。已有构建/来源审计不能等同独立医学专家标签一致性或原生gold审查；本次未在现有主记录中找到足以替代该验证的全套材料。R2 79、R4 13的稀疏覆盖和参考含义亦须保留，不要求人为平衡或补造病例。
4. 七配置是六方法家族，主要建立在两种8B骨干上。较强模型参照与资源对齐的简单控制，对判断功能缺口是否持续、收益是否只来自候选/格式/计算增量较有价值；这不是声称顶会规定固定模型数量，也不否定当前小模型实证。

**优先补强建议（未执行、待另行形成运行计划）。** 最多集中三项：①冻结最终B及协议，在按母题/患者/家族隔离的新范围做端到端确认，预先固定分母和评价，报告ALL、保持/应变、误伤及成本；样本量依据目标效应与家族依赖设计，不以随意数量冒称足够。②在同范围使用相同合法资料、候选、输出合同和清楚的预算对照简单目录/规则/采样组合或单agent；增加一个较强模型参照检验任务价值，已有控制能精确复用时优先复用。若简单组装与B实际等价，应收窄创新归因而非制造形式不同的伪控制。③对分层样本进行独立双人关系标注与医学争议裁决，报告多标签一致性、无法判定和参考可靠性，并在可识别范围内检查同来源/同格式下五类是否仍揭示不同失败模式。现有来源无法识别的类别效应如实标注，不能用统计调整制造不存在的对照。

论文可同步写作，优先将预算放在这些会改变核心结论可信度的证据上。若暂不增加实验，则保留benchmark与已暴露开发研究定位，明确五角色为操作组织、R4条件模型边界及未完成独立系统确认；不把更吸引人的叙事当作这些验证的替代。


<a id="full-manuscript-rewrite-20261003"></a>
## 2026-10-03：基于作者底稿的完整LaTeX论文重写（已完成）

用户授权依据当前材料写完整LaTeX论文，沿用此前论文skill，并要求避免防御性写作与过度强调。语言/通用会议格式及私有GitHub发布授权沿用会话，不重复索要配置和提纲许可。使用已选academic-paper固定源的配置、文献核验、结构/证据、正文、摘要/引用、独立审阅和排版流程；采用field-general审阅，未选特定venue，criteria_binding_unavailable，不宣称通过上游完整编排认证。

本次制品证据在`Documents/Codex/2026-10-03/cf_moa_full_manuscript/`，其`paper_configuration.json`/`outline.json`记配置与主线；`archive/`冻结重写前28页英文稿。原作者raw底稿和原预测/评分不改。本次主稿直接写.tex，图表由冻结汇总生成矢量制品；图像模型虽获授权，可按图型需要选择，数字与结构以可精确核验方式呈现。不会因上一轮建议补实验而自行执行模型确认。


### 全文内容与写作取舍

论文题为 **CF-MoA: Taxonomy-Guided Benchmarking and Agent Orchestration for Counterfactual Medical Reasoning**。原生`.tex`构成摘要、引言、相关工作、benchmark、方法、实验设置、结果、讨论/结论、集中限制/伦理和五项附录；主文约5,347英文词、附录约2,951词（机械近似含标题/图注/表格，不含参考文献）。采用通用10pt双栏正文，附录单栏，共20页。作者名/单位及资助、贡献和冲突声明待真实作者补入；不虚构投稿会议或作者信息。

内容以五类功能体系和benchmark作为研究对象，七个配置的完整主表与21组head比较作为问题诊断及操作证据，再展开五角色实际机制和两MedRAG配置完整B结果。B−C0 10.09/12.01pp与maintain/respond配对收益为主要结果；R2恒None、目录/校正分解、临床R4回退、C3双骨干方向不同、成本和开发数据暴露保留在相应结果或集中限制处，不在每段反复添加免责语。共14表含全六臂、五类、11来源、5输入格式、配对/区间和成本；3图为真实结构和数据生成的矢量图，未调用图像模型捏造科学图。没有改原预测、gold、评分或运行模型。

### Skill执行、引用与独立审阅

沿用[academic-paper skill](/home/data3/txy/.codex/skills/academic-paper/SKILL.md)及已核验上游固定commit。配置/提纲和发布授权沿用用户既有要求；英文单语摘要、通用会议格式。独立writer先在不读稿/数据时完成7维预承诺，再写benchmark/method；主任务写其余章节。文献核验、图表数值/目视审阅、独立事实核查和字段通用五维审阅实际完成。审阅者写过related_work与bib，明确非完全盲审；另一事实审阅者独立核对正文/附录。criteria_binding_unavailable，未宣称完整12-agent认证、特定会议审查或校准得分。流程及主张—证据映射保存于`skill/workflow_record.json`。

原24条引用保留key并复用已核验身份；新增CheckList、Contrast Sets、Dynabench，以及规则来源2023 AGS Beers Criteria和可执行指南先例MedGuideX，主来源核验后共29条。长模型作者表规范为前三作者and others，完整旧作者记录仍保留。引用解析/编译全部29条一致，未编造first/SOTA或系统检索穷尽主张。

独立事实审阅核对224个数值、21组提升、4个正向配对区间与A1/A2/A3/A4/F代码。发现并修正：bootstrap的ALL/保持/应变家族分别4,766/2,806/1,780；R2九例只指覆盖内仍有药物支持的子集；MedRGB采用本地固定受扰动材料＋动态检索；CUPCase对照为候选字符长度归一似然，非对原答案字符串归一。附录写明1,780应变对来自MedEinst。写作审阅另要求明确语言模型agent标注/交叉复核、71规则的真实指南来源、将“超出generic revision”的标题收窄为add/remove消融实际支持的结论。三条必修均已解决，D1–D5分类审阅通过，无未处理blocker。

### 制品、失败修复与验收

[制品目录](../../Documents/Codex/2026-10-03/cf_moa_full_manuscript/)保存旧28页稿快照、配置、冻结输入、脚本和审阅收据。65成员[LaTeX ZIP](../../Documents/Codex/2026-10-03/cf_moa_full_manuscript/cf_moa_latex.zip)含所有正文/表格/3图、BibTeX、编译脚本及可携带的图表输入/复现脚本；中文作者底稿及框架保持原身份。新正文已同步到`docs/paper/latex/`，编译入口仍为`main.tex`。

初编译曾因缺build目录、标题换行误写为数学起始符失败，均已修复；双栏初版6处overfull通过缩短标题和改写长词修复。一次文字修改用了错误cwd，未改源文件，改绝对路径后成功；系统Python缺Pillow导致联系图未生成，改用现有绘图库环境解决。首次图脚本正常运行仍读本机dossier，已将其元信息冻结，只有显式freeze-inputs才读原工作区；把WORKSPACE改为不存在且禁止外部研究文件访问的独立重建通过，12制品逐字节相同。首轮ZIP独立验收恰与后续浮动图排版修改相交，旧ZIP对新PDF页8–12不同；失败收据保留，最终ZIP按冻结版本重新验证通过。

最终Tectonic0.17.0实际编译，29源/编译引文双向匹配、38标签、3图/14表、依赖闭包通过；无overfull、undefined引用、missing-character或PDF缺字标记。一般underfull间距提示保留，不夸称TeX日志完全无提示。检查正文和英文摘要的acronym脚本已执行；系统/数据集名、ALL与CF-MoA拆词误报有明确allowlist，RAG连字符识别限制人工核验其引言定义。结果图已留在Results范围，联系图与首页/架构/关键结果页面目视检查通过。

最终PDF SHA-256为`6cd22fbb13b9d591b83fd2cbe0d0ca7a90db705b87d5b9726ac844a5f6c4f581`；ZIP SHA-256为`40f00e641f98a130f29e317e8e07bb1e87fc7f7c94ae51ab69248cee65f6814a`。独立/tmp解压后真实编译退出0，65文件清单一致，全部20页提取文字与108dpi RGB像素逐页相同。对应`review/manuscript_integrity.json`、`isolated_build_receipt.json`、`fact_audit_round1.json`、`manuscript_review_round1.json`与`figure_portability_check.json`。GitHub发布及远端验收归workspace下一条记录。

发布已完成：已推送[原私有GitHub论文目录](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa)，提交`fb628e3`。573包文件与根README共574个远端blob核对，六关键制品下载逐字相同；旧作者底稿和框架ZIP未改。[完整发布事实](../workspace.md#cf-moa-full-manuscript-github-20261003)。暂存检查发现派生缩略语Markdown表格尾部空白，修复该派生文本并重跑检查后通过，原生论文/ZIP未改。


<a id="anti-defensive-skill-search-20261003"></a>
## 2026-10-03：去防御性写作skill检索与选型

用户要求联网寻找能修防御性写作的skill，并尽量选择GitHub star多的。本轮只做检索和适配评价，不把“找一下”扩成安装、执行第三方代码或自动重写整篇论文。已有academic-paper写作流程和已交付论文不变。

使用网页检索、GitHub按stars降序的repository search和官方REST元数据交叉核验。专用`anti-defensive-writing in:name`返回10库，`"defensive writing" in:description`返回9库，二者最高均为Adkid-Zephyr；`humanizer skill in:name,description`返回676库，首项为blader/humanizer。检索覆盖并不等于穷尽所有不同命名的skill，因此结论限定为本轮核验的相关仓库。star按仓库计，不把综合skill合集的总星数冒充某个写作skill的独立受欢迎程度。

北京时间10月3日03:40–03:41的GitHub API核验与实际SKILL读取结果如下：

| 仓库 | stars | 实际能力与本项目适配 |
|---|---:|---|
| [blader/humanizer](https://github.com/blader/humanizer) | 53,578 | 当前v3.1.0；第5项专门处理回应假想异议，第9项处理限定堆叠；保留来源事实并区分技术/事实体裁。相关独立写作编辑skill中本轮核验最高 |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | 18,839 | 中文改写方向，非当前英文稿的优先项；本轮核README/元数据 |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | 17,712 | 精简AI表达，真实SKILL还要求去全部副词/被动句、使用面向读者的语气，学术论文不能机械照搬 |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | 4,831 | 体裁/声音适配与编辑保真；本轮定向读有关必要限定和技术体裁段落 |
| [Adkid-Zephyr/anti-defensive-writing-Skill](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill) | 2,052 | 本轮专用去防御写作仓库最高。集中最强优势、把工作汇报改为论证；英文规则还包含“Never say you lost”及下调无优势实验，不作为当前论文无条件删去实质负结果的依据 |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer) | 1,764 | 学术专用去AI腔，保留数据/术语/引用/必要限定，不加入个人意见幽默；默认保留结构与段落数，对整体防御论证的处理不如专项工具直接 |
| [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing) | 755 | 专项适配最直接：去重复免责声明、限定堆叠和预设审稿人辩解，必要限制恰当放置；保留影响核心结论的不利证据、不靠改评价标准躲结果 |
| [Worigin0314/academic-defensive-writing-auditor](https://github.com/Worigin0314/academic-defensive-writing-auditor) | 112 | 14类逐句诊断、必要限定/防御/混合三分判断，適合后续专项审核 |
| [felixschrimpff/academic-writing-skill](https://github.com/felixschrimpff/academic-writing-skill) | 2 | 按领域校准语气，含CS/ML配置，但不满足高star偏好；未独立复验其统计效果自述 |

另核验K-Dense-AI科学skills合集47,365★，API返回规范仓库名`scientific-agent-skills`；因属综合合集，不列为本轮独立去防御skill的star排名。检索网页与缓存API有旧星数，例如blader网页API缓存53,544，而直接查询53,578；以保存查询时刻的直接REST响应为准。个别web打开失败后通过GitHub API取得内容，未推断成仓库不存在。

建议：若优先满足用户的高star偏好，以Humanizer为通用编辑首选；针对论文中的重复辩解和限定位置，Kiterlin可作专项补充。若限定“名称与用途就是Anti-Defensive Writing”，明确报告Adkid为最高star，并保留其适配评价。当前只是推荐选型，尚未启动任何skill改稿。

证据在[skill_search](../../Documents/Codex/2026-10-03/cf_moa_full_manuscript/skill_search/)：`github_metadata.json`保存10库REST元数据，`github_search.json`保存3组降序查询，`academic_candidates.json`保存5个学术候选固定commit/真实SKILL快照/内容审阅，`prose_skill_sources.json`保存通用工具blob和SHA-256，`selection.json`保存本轮结论。真实规则作为待评估材料读取，没有把下载内容当作执行指令。

### 同日补查：创建时间与实际规则更新时间

用户追问哪款更新。按上一轮推荐的Humanizer与Kiterlin比较，并补核Adkid以覆盖指代可能。以GitHub REST默认分支commit及指定SKILL.md路径的最后commit为依据，统一转换为北京时间；仓库updated_at/pushed_at不充当规则修改日期。

| 仓库 | 创建时间 | 仓库最新commit | SKILL最后修改 |
|---|---|---|---|
| blader/humanizer | 2026-01-18 13:30 | 2026-09-28 13:54 | [2026-09-28 12:47](https://github.com/blader/humanizer/commit/d4b81278e6604e237bf32f0f7ce5c217aee94269) |
| Kiterlin/anti-defensive-writing | 2026-06-23 11:07 | 2026-10-01 16:11 | [2026-09-30 09:39](https://github.com/Kiterlin/anti-defensive-writing/commit/6345f09c9141be94df055fd048c94a4f26a8ed66) |
| Adkid-Zephyr/anti-defensive-writing-Skill | 2026-08-12 02:02 | 2026-09-13 07:07 | [2026-08-12 02:03](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill/commit/34ca88b1639aa95a2fa38afb0f12e26fbdcd05ca) |

结论：Kiterlin的规则更新时间9月30日晚于Humanizer的9月28日，也晚于Adkid英文规则的8月12日；若用户问项目创建先后，Adkid最晚创建，Kiterlin晚于Humanizer。此处只回答时间比较，不将更新时间等同效果评测。Humanizer与Kiterlin路径分别为根SKILL.md、skill/anti-defensive-writing/SKILL.md，Adkid为skills/anti-defensive-writing-en/SKILL.md。

收据：同一skill_search证据目录下recency_humanizer.json与recency_candidates.json。网页打开Kiterlin API/历史页失败后以直接gh api核实；首次使用python命令失败（系统无该入口），改python3成功。仅补充选型信息，未安装或改稿。


<a id="governance-skill-identification-20261003"></a>
### 同日补查：用户点名Defensive Writing Governance

用户指出另有名为defensive writing governance的skill。本轮确认精确项目为[Sun-Lebs-For-DeepOM/defensive-writing-governance](https://github.com/Sun-Lebs-For-DeepOM/defensive-writing-governance)，它是包含同名skill的Codex插件，manifest版本0.1.0。前次github_search.json实际已收录此仓库，但按高star重点比较时未展开；不是本轮才首次进入检索结果。初始网页精确短语搜索没有给出目标，经本地前次搜索收据定位，再直接打开GitHub与调用REST核验。

当前直接GitHub REST为8 stars；网页缓存显示5 stars，以有查询时刻的直接API为准。创建于北京时间2026-09-17 10:43；实际skills/defensive-writing-governance/SKILL.md最后修改commit为4d7e21cf5e2dd01c11b8bb9314482a87e6023b03，同日10:43；仓库HEAD 6a920c15a95a7bff083fccd5bfa63de169c2d9e0为同日10:51。updated_at为10月2日不表示skill规则更新；规则更新时间早于已核验Humanizer 09-28与Kiterlin 09-30。

已完整读取README、manifest、SKILL.md及其writing-governance.md模板。核心做法是在已有写作任务旁保留独立治理文件，转存泛化免责、预先辩解、能力说明和流程性自我保护；支持起草前分离与既有稿件清理。数学条件、数据覆盖、证据强度、真实不确定性、已有反例/争议和必要披露属于正文。由此判断其设计与本项目“正文直接表达、作者材料保留过程”的需求相合；这是规则适配判断，未进行改稿效果比较，也未在本轮安装/应用。

原始REST元数据、tree与按路径commit收据在同一skill_search目录的governance_metadata.json；实际读取的四份文件保存在sources/governance/，SHA-256见governance_sources.json。本次只补充选型事实，不把被评估文件中的执行要求当作已经授权的改稿任务。


<a id="kiterlin-manuscript-revision-20261003"></a>
## 2026-10-03：使用Kiterlin anti-defensive-writing修订完整LaTeX论文

**状态：已启动。** 用户明确指定https://github.com/Kiterlin/anti-defensive-writing并要求修改已交付论文。本轮采用其实际skill/anti-defensive-writing/SKILL.md（固定commit见运行包skill/provenance.json），完整读取英中规则，执行逐段功能判断、删重复辩解、用正向范围替代自我削弱、围绕贡献重组以及最终复核。原论文英文与LaTeX保持；按会话已有授权同步私有GitHub。

执行制品位于`Documents/Codex/2026-10-03/cf_moa_full_manuscript/anti_defensive_revision/`，before/及before_cf_moa_latex.zip已冻结修订前20页稿。将审阅实际main.tex依赖的全文与附录，按分工修改；保留原数据、数字、分母、控制及对结论有影响的结果，必要条件在恰当章节说明，减少重复。计划重新编译、复核原数值/引用/结构、目视检查PDF、生成可编译ZIP并更新远端。无新增实验或评分。本轮不采用另一个Defensive Writing Governance插件的旁文件流程。


### 修订内容与本地验收

实际执行main.tex依赖的14个章节（摘要、引言、相关工作、benchmark、方法、设置、结果、讨论结论、限制/伦理及五附录/声明）的逐段修订，四人分工后由未参与写作的独立审阅者检查全文。摘要先建立taxonomy→operations主贡献，并用一句development benchmark准确界定结果；引言正向讲明支持路径和所需计算；结果直接给变化与含义，去掉“此处保留退步”等呈现旁白；方法和附录将“不是X”“不应混淆”改为资源、接口和复现条件。必要定义/输入权限/数学条件不机械删否定词。C2/C5均低于B的更精确表述经全精度表核验，Qwen C2=59.3562、B=59.3616，不能只比较同为59.36的显示值。

原数字结果、公式、引用、类别/来源/格式分母与有实质意义的负结果保留。机械检查29个实际依赖tex、55个受保护图表/数值输入/复现脚本/BibTeX/构建脚本通过；仅删除附录“288 independent patients”句中一次重复288，288问题/24虚拟profile/每profile12题仍完整。独立审阅确认开发暴露、两完整系统与七head配置、A4独立受限panel、R2常数None、临床R4下滑、C3异向、成本缺项及临床验证条件的含义保持，未发现新增无依据主张或内容blocker。审阅绑定33个源依赖文件SHA-256。

Tectonic 0.17.0重新编译为19页（修订前20页），3图/14表/29引用/38标签。正文近似英文词5,347→5,119，附录2,951→2,845（沿用含标题/表格的机械统计口径）。首轮出现benchmark一句3.08775pt横向溢出，改“MedEinst requires open diagnosis”为“MedEinst uses open diagnosis”后第二轮通过；引用/缺字/overfull检查无错误，一般underfull提示保留。首轮失败收据未覆盖。19页联系图及首页/主表页目视检查完成。

环境只读检查发现工作区根不是Git仓库，转用既有隔离发布仓库；系统和模型环境均无PyMuPDF，检索旧临时安装未找到且遇到他人/tmp目录权限提示，随后将冻结版本PyMuPDF1.28.2装入独立/tmp/cf_moa_anti_defensive_deps完成检查，未改模型环境或其他人的权限。未进行新模型调用、训练、评分或图表数值重算。

新ZIP使用原已验收65成员依赖闭包，从当前权威LaTeX更新所有内容并刷新清单；旧20页ZIP和来源快照在本轮before/与before_cf_moa_latex.zip保留。当前PDF SHA-256为`45808db27c1be8a2a6adc6c156f3612c92ba4e93da3174c05142b35e53753905`；ZIP为`9ec079736394f8d749ca5681db7a4daa4c83d3d7afc9c2c73663795e3df4a88d`。运行包review/含逐分工编辑说明、revision_diff.patch、revision_preservation.json、independent_review.json、两轮编译/检查和visual_review.json；skill/含固定源、许可与commit/hash。独立ZIP验收已通过：65成员/64清单行hash与size一致，在/tmp解压后Tectonic真实编译退出0，全部19页文字与108dpi RGB像素逐页等于canonical PDF；收据为review/isolated_build_receipt.json。GitHub验收随后补记。
