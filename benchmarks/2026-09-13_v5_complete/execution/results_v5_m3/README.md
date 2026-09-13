# M3 v5 continuation

Continues the existing MA-RAG intrinsic Qwen3-8B baseline: N=8, T=4,
MedCorp3 BM25 + MedCPT, solver temperature 0.7 / 2048 tokens / thinking off,
query temperature 0 / 8192 tokens / thinking on, top-20 entropy history.

13,905 total inputs; 3,690 exact-input results reused from the completed v3 M3
run; 10,215 pending inputs. Completed invalid/vote-tie answers are retained.
Eight disjoint client shards alternate between GPUs 1 and 2, four per service.
Each service supports 32 sequences and reserves 75% GPU memory. GPU 1 also
hosts the existing MedCorp3 retrieval service. Other users' GPU 0/3 processes
are not touched. Recheck GPU availability during supervision.

`plan.json` freezes all shard memberships. `cache/reused.jsonl` records original
source IDs and paths. `cache/items/` preserves each new stage and native outputs.
For v5 robustness inputs, prompts request D-numbered factual-error corrections;
answer voting remains unchanged, with errors preserved from the first final
candidate carrying the winning answer. No gold labels enter inference.

`code/run_all.sh` waits for services, validates smoke and longest inputs, runs
all shards, then executes coverage audit and native v5 scoring. Smoke outputs
are reused. `code/finish.py` releases only this run's verified service PIDs.
Services and controller run in tmux socket `v5-m3`.

Generation stage timings separate input preparation, API request (generation
plus transport), response processing, and cache writes. Retrieval stages record
wall time. These support performance analysis without changing prompts or
sampling. Existing prefix caching and parallel query retrieval are retained.

### GPU0 protected parallel continuation — 2026-09-12 12:53

User authorized borrowing GPU0 while dpc remains paused, using the previous
M4 automatic yield rules. `code/parallel_gpu0.py` imports that existing guard:
check every 2 seconds; yield on resumed incumbent, another GPU process, or less
than 25 GiB free. Only our new service process group is terminated on yield;
its three clients resume from their saved stages on GPU1/2. No signal is sent
to dpc's processes.

GPU0 serves the same Qwen model and frozen generation settings at port 8010,
with 0.60 GPU memory allocation. Original shards 0, 3, 4 were handed to this
endpoint; the other five workers, GPU1/2 model services, and retriever continued.
The original eight disjoint ID lists are unchanged. Three original client
processes were terminated only after GPU0 health passed; completed results and
stage caches are reused, while an unsaved in-flight stage may be regenerated.
The resumed clients now also load the previously validated vectorized entropy
parser; the other five still use their already-loaded original parser.

`tmux -L v5-m3` session `gpu0-parallel` runs the new coordinator. It takes over
finalization because the original controller records the intentional client
exits as nonzero. It checks full pending-ID coverage before invoking the same
`finish.py` audit/scorer and releasing our services. See `gpu0_handoff.json`,
`gpu0_parallel_events.jsonl`, `gpu0_parallel_status.json`, and
`run_{0,3,4}_gpu0_resume.log`. No benchmark inputs or method settings changed.

#### GPU0 memory update — 2026-09-12 12:59

User explicitly requested approximately 75 GiB for our GPU0 model and authorized
lowering its free-memory yield threshold to **10 GiB**. Incumbent-resume and
new-external-process checks remain unchanged. This supersedes the 0.60 / 25 GiB
settings above. GPU0 uses memory fraction 0.875: this installed vLLM counts the
incumbent allocation during profiling, so 0.75 would not give our process 75 GiB.
Only GPU0's own service and three clients were restarted, via
`parallel_gpu0.sh --resume`; GPU1/2 and the other five clients continued.
`gpu0_guard_validation.json` verifies the changed threshold while the shared
M4 guard's default remains 25 GiB. `gpu0_memory_upgrade.json` records coverage
at the second handoff. Five-minute updates now include all four GPUs, cumulative
M3 progress, remaining inputs, and newly completed inputs since the last report.

#### GPU0 additional 6 GiB — 2026-09-12 15:29

User explicitly approved lowering free-memory yield to **4 GiB** and adding
approximately 6 GiB to our GPU0 process. Allocation fraction is now 0.9378,
targeting about 81 GiB for our model while retaining the dpc-resume and
new-external-process yield triggers. Only our GPU0 coordinator, service, and
three clients were restarted; all other workers/services continued. Exact
original shard IDs and existing caches are reused. See
`gpu0_guard_validation_4gib.json`, `gpu0_pre_upgrade_81gib_status.json`, and
`gpu0_memory_upgrade_81gib.json`. This supersedes the previous 10 GiB threshold.

### GPU3 joins — 2026-09-12 17:59

GPU3's other-user vLLM exited. Following the user's standing instruction to use
available GPUs in parallel, `code/parallel_gpu3.py` launched the same frozen
Qwen server on 8013 (memory fraction .75), then handed original shards 1/2/5
to it after health passed. Only these three original clients restarted; all
model services and other shards continued. Exact original eight shard lists
remain unchanged. Current placement: GPU0=0/3/4, GPU1=6, GPU2=7, GPU3=1/2/5.
The resumed GPU3 clients load the validated vectorized entropy parser; only
original shards 6/7 still have the older parser in memory.

Tmux socket `v5-m3`, session `gpu3-parallel`; see `gpu3_handoff.json` and
`run_{1,2,5}_gpu3_resume.log`. GPU0 coordinator still owns final coverage audit
and scoring. `finish.py` now also releases only our verified port-8013 service.
GPU1/2 also host another workspace's iMedRAG dev task; do not signal it.

### GPU0 guard yielded — 2026-09-12 19:13–19:18

The guard detected dpc's new active GPU0 PID 1889151 and automatically stopped
only our GPU0 model group. Shards 0/4 resumed on 8011, shard 3 on 8012, with
saved stages retained. No dpc processes were signalled. Current placement:
GPU1=0/4/6, GPU2=3/7, GPU3=1/2/5. GPU0 coordinator remains alive in `fallback`
state and still owns finalization. Do not restart its original handoff script
or reclaim GPU0 while the external job exists. Events and new worker PIDs are
in `gpu0_parallel_status.json` and `gpu0_parallel_events.jsonl`.

### Remaining-tail balance — 2026-09-12 20:55

Shards 1/3/7 completed. The original shard6 client was handed from GPU1 to the
already-running GPU2 endpoint8012, reusing its saved stages and exact ID list.
Only that client restarted; all model services and other active shards continued.
Tmux session `shard6-gpu2`, script `code/resume_6_gpu2.sh`, record
`gpu2_shard6_handoff.json`. Active placement: GPU1=0/4, GPU2=6, GPU3=2/5.
GPU0 coordinator in fallback mode still owns full-coverage finalization.
All original controller clients have now exited; its intentional nonzero exit
is expected and is not the active completion controller.

### Completed — 2026-09-12 23:48

See [RESULTS.md](<RESULTS.md>). All 13,905 predictions and 15,616 scoring records validated, zero missing/duplicates. All our model and retriever GPU allocations released. No M3 work remains running.

## 实施与复现总记录（2026-09-13）

[五方法评测实施、调整与复现记录](<../EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>)汇总实际配置变更、工程加速验证、资源调度时间线、最终结果及论文表述边界；历史日志中的中间状态以该记录及最终审计为准。
