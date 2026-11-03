# E4a：同事实、同规则的统一执行对照

123 个已暴露规则输入×M4/M5，新增246次终端生成；上游检索和事实提取复用。两臂共享事实、规则、状态、问句作用域、选项及初答。功能臂为已有A1/A2程序支持执行，统一LLM臂使用相同中间信息和输出合同。

| 配置 | 程序B | 统一LLM | 程序−LLM | 95%家族区间 |
|---|---:|---:|---:|---|
| M4 | 69/123 | 50/123 | +15.45pp | [+3.31,+26.98]pp |
| M5 | 71/123 | 71/123 | 0pp | 见配对收据 |

[总分](analysis/overall.csv)、[功能子集](analysis/by_function.csv)、[M4配对](analysis/m4_paired.json)、[M5配对](analysis/m5_paired.json)、[可用性分解](analysis/availability_decomposition.csv)、[操作要求](analysis/operation_requirements.csv)、[逐项分数](analysis/native_scored.jsonl)、[图](analysis/terminal_execution_comparison.pdf)。66个保守情景家族、2000次整家族bootstrap。

M5两个相反方向各25题；总分相同不表示相同行为。M4/M5程序不可用1/14，LLM不可用10/5；全部仍在123分母。7次生成长度/解析失败保留，未语义重试。操作忠实度是相对冻结状态的检查，不是独立医学正确率。

输入685,648、输出109,383 tokens。[实际调用账本](call_ledger.jsonl)保留246个请求的来源hash、共享信息hash、接受提示hash和采样参数；原始提示正文不重复发布。原执行代码见上级`source_snapshots/`。
