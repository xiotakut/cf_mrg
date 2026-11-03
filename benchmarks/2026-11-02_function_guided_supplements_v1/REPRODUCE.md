# 离线复核与源码范围（v2）

标准库检查，无需模型、GPU或联网：

```bash
cd benchmarks/2026-11-02_function_guided_supplements_v1
python3 verify_saved_results.py
python3 verify_delivery.py
```

第一条核验总清单、E1保存OOF/单元平均、E4a/E4b/E5多分母表和2045调用账本；第二条从补交逐项输入复算E3主表/配对点估计/覆盖，重放E5的111项指纹匹配，并核对E2原清单。这不是临床金标重判，也不重新解析全量原始模型回答。

可选CPU统计复现，需要numpy、scipy、scikit-learn（已实际使用的版本见`e1_corrected/fixed_fold_reproduction.json`）：

```bash
OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 python3 reproduce_e1_fixed_folds.py
python3 verify_delivery.py --with-intervals
```

第一条按保存的4216家族fold重拟合10个逻辑回归模型，重新构造原单元权重；不调用GroupKFold重新分折，也不覆盖原结果。第二条复现8项E3 profile bootstrap区间（2000次）。依赖版本是当前成功复核环境，不是声称找回了原运行时锁文件。无需安装任何LLM运行框架。

`source_snapshots/`逐字保留当时执行脚本及绝对路径/外部资源依赖；不能直接在任意机器运行全链。新增顶层核验器可以直接读取公开文件。原生评分投影保留标识、类别、可用性和全部评分字段；E3保持面板则按`delivery_provenance.json`列明字段投影。只另公开明确标出的QA展示例，不声称全量原始请求/回答都随包提供。

E5的指纹足以在公开端复现指定的相等性比较和排除集合；不能独立证明其枚举覆盖了所有历史文件或文章级关联。源文件hash和旧扫描时间身份保留。

`MANIFEST.json`覆盖v2全部payload，包括E2与其原有内部ZIP，排除顶层自身、下载索引和两个顶层分发ZIP。v2 ZIP包含payload与manifest。`DOWNLOADS.json`分别记录v1/v2校验。v1旧包按字节不变，历史清单不应用于v2新目录。
