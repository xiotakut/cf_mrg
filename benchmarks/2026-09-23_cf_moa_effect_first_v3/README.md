# CF-MoA 版本3：完整过程与四轮效果优先开发

2026-09-23发布快照。涵盖原Router＋五专家实现、版本2增量修订，以及其后四轮效果优先实验。当前新增方法均未取得采用资格；正式v5、原生评分和已采用A2/A3/A4/F保持原身份，尚未共同冻结或开展独立质量评估。

从[完整过程报告](docs/research/cf_moa_experiment_report.md)开始阅读。第1–11章保留历史，第12–13章补全四轮实验、错误与处理、成本、验收和剩余缺口。持续细节见[主记录快照](docs/research/cf_moa.md)；采用范围见[核心计划](plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)和[执行配置](plan/execution_plan.json)。历史暂停/资源状态按各段时点解释。

| 材料 | 内容与限制 |
|---|---|
| [质量摘要](data/quality_summary.json) | 92个骨干/臂/面板组、294个同范围比较；不把不同权重的指标混用 |
| [逐输入状态](data/per_input_status.csv) | 2546条保存状态，包括复用、组合与事后诊断；不是2546个独立病例或新调用 |
| [配对摘要](data/pair_summary.json) | 488个原有汇总组；不同覆盖层可重叠，不能加总 |
| [实际成本](data/cost_summary.json) | 四轮新增2203次模型调用、17716744输入/160997输出token；历史与共享费用单列 |
| [失败和未完成项](data/failure_and_limitations.json) | 未采用身份、截断、不可用分母、诊断自由字符串读出缺口与解释限制 |
| [数据说明](data/README.md) | 面板、分母、来源和验证方法 |
| [GPU释放记录](data/gpu_release_summary.json) | 已释放GPU0/1自有占位，GPU2/3各保留80GiB；不自动重新占用0/1 |
| [来源与转换](SOURCE_MANIFEST.json) | 本地来源及公开文件SHA-256；[数据来源](data/source_manifest.json)另列54份元数据源 |
| [独立发布审阅](evidence/independent_review.json) | 文件、计数、成本、来源和公开范围核验；不是独立科学重现 |

第四轮主臂M4/M5为18/34、15/34，低于同范围B的23/34、19/34；普通重答20/34、14/34，去理由对照20/34、15/34。诊断读出仍有自由字符串、长解释和截断问题。新的目录键读出只处于建议阶段，未实施，未把旧失败响应恢复为成功。此前各轮结果完整保留，不能将工程完成等同于方法增益。

成本总数仅指效果优先四轮，不能称为全项目累计费用；累计模型执行秒也不是独占端到端时延或GPU能耗。面板重叠，历史121题及各轮固定分母不替换、不合并为新的独立集。

本次发布新增模型调用和原生重评分均为0。公开包包含完整过程文档和白名单状态/汇总，不包含完整患者题面、模型请求/响应、gold、隐藏配对正文、SQL、权重或语料库。原始证据保留在服务器，未上传项在[本地制品索引](LOCAL_ARTIFACT_REFERENCES.csv)中明确注明；本包不是可独立重跑模型的源码发行版。

下载仓库后可在本目录验证公开文件哈希、链接及已保存计数：

```sh
python3 check_publication.py
```

该检查不启动GPU、不访问本地原始病例、不重新评分。[数据重建脚本](scripts/build_publication_data.py)仅在拥有原始元数据的服务器运行；[公开验证脚本](scripts/verify_publication_data.py)可独立核对导出数据。来源文件哈希校验不能替代原生评分重现。

前两次快照保留：[版本1](../2026-09-23_cf_moa_process/README.md)、[版本2](../2026-09-23_cf_moa_incremental_v2/README.md)。本版本新增内容，不覆盖历史负结果、失败记录或旧发布包。
