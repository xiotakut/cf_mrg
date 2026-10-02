# Direct与retrieval-only基线（M0/M1）

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。M0是Llama-3.1-8B直接回答，仍保留题目规定的固定证据；M1使用MedRGAG初始检索、MedCPT重排和reader。M1不是独立MedRAG M4/M5。M0已完成v5；M1的已完成比较主要在早期评测及v3。

## 实现、运行与复用记录

M0使用Llama-3.1-8B-Instruct；只移除新增检索，不删除数据集要求的固定证据。M1复用M2首次标准BM25检索和MedCPT重排的top-5文档及reader，不执行KGCC、补充知识生成或KADS；原题和变体独立推理，不向模型暴露配对gold。

v5中M0复用8,877条已有预测，新增5,028条，合计13,905条；ALL为48.10%。旧结果中无效答案仍保留，复用按实际可见字段和运行条件匹配，不能只看题号。完整运行和评分证据见[v5记录](/home/data3/txy/docs/evaluation/v5.md)及[协议](/home/data3/txy/docs/evaluation/protocol.md)。M1保留早期完整来源比较和v3结果，没有据M0完成状态推断M1也完成v5。

实际脚本/模型/检索配置及早期M0/M1调用合同已合入[原生baseline screening历史](/home/data3/txy/docs/archive/native_baseline_screening.md)。早期Direct两次复现的配置差异、结果及成本见[MedRGAG复现历史](/home/data3/txy/docs/archive/medrgag_reproduction.md)。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [3.1 方法编号与论文归属](#record-0237)

<a id="record-0237"></a>

## 3.1 方法编号与论文归属

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第46行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 3.1 方法编号与论文归属

| 编号 | 本项目 v3 实际方法 | 论文中合适的身份表述 |
|---|---|---|
| M0 | Llama-3.1-8B-Instruct 直接回答；原题指定的固定证据仍随题提供 | 本地直接回答基线；“无新增检索”不表示删除原生题目证据 |
| M1 | MedRGAG 初始 BM25 检索、MedCPT 重排、top-5 文档，再由 Llama 回答 | 本项目 retrieval-only / Vanilla RAG 对照；工程上可作去掉后续增强流程的对照 |
| M2 | 全 Llama MedRGAG：初始检索 → KGCC → 缺失知识探索/生成 → KADS → 最终重排 → 阅读器 | 明确参数和资源的本地全 Llama MedRGAG 复现配置；保留原方法组成 |
| M3 | 本地 MA-RAG intrinsic：Qwen3-8B、N=8/T=4、分歧驱动查询、检索、熵与历史、停止和投票 | 本地 MA-RAG 基线，并披露骨干、语料、任务接口及上下文适配 |

**M1 的澄清是名称和归属修正，不是重新实现或重新运行一个方法。** 它没有对齐独立 MedRAG 论文的全部实现，也未证实与 MedRGAG 某项官方消融在所有设置上相同。后续真正从 `gzxiong/MedRAG` 接入的方法编号为 M4/M5，不能拿其名称、语料或参数倒写 M1。
