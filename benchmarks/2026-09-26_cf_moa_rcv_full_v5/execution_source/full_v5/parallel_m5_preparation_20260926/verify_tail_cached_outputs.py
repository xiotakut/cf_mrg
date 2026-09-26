"""Read-only exact-entry replay of only the 12 already complete cache tasks."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0,'/home/data3/txy')
from cf_moa.contracts import digest
from cf_moa.controller import moa_rcv, strong_legacy
from cf_moa.evaluation.run_moa_rcv import ARM_ALIASES, _initial_native, load_plan
from cf_moa.evaluation.run_moa_rcv_batched import FrontierBackend
from cf_moa.tools.f_pool_replica import session_for_plan


class MissingSavedCallback(BaseException):pass


def no_runtime():
    raise MissingSavedCallback('Known complete cached output requested a missing callback; no tokenizer/model runtime is allowed')


class ReadOnlyPrefixJournal:
    def __init__(self,path):
        self.db=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
        self.db.row_factory=sqlite3.Row
        if self.db.execute("SELECT 1 FROM meta WHERE key='first_error'").fetchone():
            raise ValueError('Use newly prepared prefix journal, never failed source')
    def ensure_running(self):pass
    def lookup(self,key,ordinal):
        return self.db.execute('SELECT * FROM calls WHERE request_id=? AND ordinal=?',(key,ordinal)).fetchone()
    def count(self,key):
        return self.db.execute('SELECT COUNT(*) FROM calls WHERE request_id=?',(key,)).fetchone()[0]


def verify(transfer):
    receipt=json.loads(Path(transfer).read_text())
    expected=receipt['cache_only_evidence']['native_answer_hashes']
    seen={};callback_count=0
    for shard in receipt['shards']:
        known=set(shard['known_cache_only_task_ids'])
        if not known:continue
        plan,selected,packets,pools,bases,tasks=load_plan(Path(shard['plan']),'M5')
        journal=ReadOnlyPrefixJournal(Path(shard['output'])/'journal.sqlite3')
        backend=FrontierBackend(journal,no_runtime)
        try:
            for task in tasks:
                key=task['task_id']
                if key not in known:continue
                packet=packets[task['request_id']]
                if strong_legacy.select(packet)[0]!='F':raise ValueError('Bound cache replay only covers F')
                backend.begin_item(key)
                session=session_for_plan(packet,backend,plan)
                result=moa_rcv.run(packet,session,method='M5',mode=ARM_ALIASES.get(task['arm'],task['arm']),
                    seed=plan.get('verification_seed',42),saved_f_proposal=pools.get(packet.request_id),
                    saved_base=None,**_initial_native(packet))
                backend.finish_item()
                if result['f_proposal'] is not None:pools[packet.request_id]=result['f_proposal']
                got=digest(result['native_answer'])
                if got!=expected[key] or key in seen:
                    raise ValueError('Cached whole native answer differs or duplicated: '+key)
                seen[key]=dict(gpu=shard['gpu'],native_answer_hash=got,matched=True,exact_prefix_callbacks=backend.ordinal)
                callback_count+=backend.ordinal
            if {k for k in seen if k in known}!=known:raise ValueError('Known cache task was omitted')
        finally:journal.db.close()
    if set(seen)!=set(expected):raise ValueError('Known cache scope differs')
    return dict(status='passed',known_complete_tasks=len(seen),exact_prefix_callbacks=callback_count,
        new_model_calls=0,new_tokenizer_calls=0,new_grader_calls=0,SQL_writes=0,
        actual_entry='moa_rcv.run + session_for_plan + unmodified FrontierBackend',
        missing_callback_policy='BaseException abort before runtime construction',checks=seen)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transfer',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=verify(args.transfer)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
