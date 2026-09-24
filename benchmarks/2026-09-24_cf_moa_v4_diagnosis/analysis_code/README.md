# 导出与离线分析的实际脚本

这些文件只供源码审阅；本次发布没有执行它们，也没有新模型／评分。脚本依赖服务器原运行包，公开元数据不是私有完整输入的替代品。

- `export_samples.py`：完整95组合的一次性stdlib导出，原私有JSON不在本GitHub目录。
- `decompose_saved_choices_executed.py`：实际完成分解时运行的脚本，曾经通过原loader附带读取全量canonical诊断标签依赖。95题均非diagnosis，未查询该表；文件读取事实保留。
- `decompose_saved_choices.py`：后来将原parse/norm装载限制为本批三种格式，不加载无关全表；未据此重新计算结果。

采用方法和原生grader没有改动。文件SHA见根`PUBLIC_MANIFEST.json`；结论与限制见[报告](../DIAGNOSTIC_REPORT.md)。
