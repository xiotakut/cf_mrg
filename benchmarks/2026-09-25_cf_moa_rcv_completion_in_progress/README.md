# CF-MoA RCV收口计划：执行中快照

**本包不是最终交付。完整v5仍在运行，共同冻结、新家族验证与独立F候选生成复本尚未完成。旧默认B保持。** 这是运行期间的公开快照，非最终交付；具体版本以Git提交为准。

先读[第16章](docs/research/cf_moa_experiment_report.md#rcv-completion-in-progress)、[五张开发主表](data/tables/five_tables.md)及[交付索引](data/public_delivery_index.json)。原用户计划位于[plan/](plan/01_Progress_and_Point_to_Point_MoA_Plan.md)，运行身份见[runtime_identity.json](runtime_identity.json)。

已完成1194个配对atom、630个家族效应、26组私有变更审阅、190缓存整答接线、两骨干live连通、C5真实176次取分、123规则输入的同核操作消融。自然M4 C0补齐52条，M5仍48/52、完整ALL为null。1730行C1–C5逐输入状态只含公开元数据；完整模型原文与gold不在本包。

唯一主研究候选是带理由逐候选验证；候选全部保留、两编码归一后平均、精确平票保留F，返回已有完整响应。A1/A2共享旧规则核；A3/A4直接返回采用结果。NLI保持F，不叠加普通重答，不增加全局裁决。

源码清单原有114映射去重为106文件，显式补上遗漏的实际采用F后为115映射、107个唯一运行源码/配置文件。F直接依赖仅Python标准库。另附本轮有限离线分析脚本。所有静态导入中的历史A1/A3等文件不表示这些旧候选被启用。

当前全v5 driver为`db06c973…`；callback复用的未来暂存driver未启用、未冻结。公开代码是本地研究入口与依赖快照，依赖已采用目录、模型、vLLM环境和合法私有输入，**不是跨机器开箱即用安装包**。

本地接口（PLAN/OUT须由合法运行计划提供）：

```bash
python -m cf_moa.evaluation.run_moa_rcv --plan PLAN --method M4 --mode cached --output OUT
python -m cf_moa.evaluation.run_moa_rcv --plan PLAN --method M5 --mode live --gpu AUTHORIZED_GPU --output OUT
```

完整v5状态仅取数值快照；`completed`是C1–C5任务输出行，不是病例数。M5四条C0的固定容量监听、两骨干固定CPU收尾监听属于当前已授权工作；旧一般自动实验队列仍stopped。时延为共享条件下模型batch事件wall分摊，不是独占GPU时间。历史初答/检索未知成本不记为零。

公开边界与私有位置见[PRIVATE_ARTIFACTS.md](PRIVATE_ARTIFACTS.md)。[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)绑定本包逐文件hash；不包含该manifest自身以避免循环。全量/确认未运行行保持partial，现有开发区间不能解释为未见泛化，最终采用尚待完整结果。
