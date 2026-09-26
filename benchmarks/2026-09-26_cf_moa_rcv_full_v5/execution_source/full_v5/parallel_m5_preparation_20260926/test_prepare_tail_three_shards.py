from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('tail_transfer',HERE/'prepare_tail_three_shards.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
import partial_prefix_transfer as original
from test_partial_prefix_transfer import fixture,call
from test_prepare_gpu2_recovery import failed_status


class TailTransferTests(unittest.TestCase):
    def test_balanced_input_groups_all_arms_and_metadata_independent(self):
        tasks=fixture()['protocol']['methods']['M5']['tasks']
        shards,proof=m.split_tasks(tasks)
        self.assertEqual([proof['shard_input_counts'][str(g)] for g in (2,1,3)],[2,2,2])
        for gpu,part in shards.items():
            for row in part:
                self.assertEqual(sum(x['request_id']==row['request_id'] for x in part),2)
        changed=[dict(t,family='arbitrary',source_id='arbitrary',gold='never consumed') for t in tasks]
        newer,_=m.split_tasks(changed)
        self.assertEqual({g:[t['task_id'] for t in p] for g,p in shards.items()},
                         {g:[t['task_id'] for t in p] for g,p in newer.items()})
        with self.assertRaises(ValueError):m.split_tasks(tasks+[tasks[0]])

    def test_whole_tail_keeps_cached_tasks_zero_physical_and_parent_union(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.mkdir();(source/'run.lock').touch()
            inputs=root/'inputs.jsonl';inputs.write_text('')
            saved=root/'F.jsonl';saved.write_text(original.serialized({'request_id':'fresh0','proposal':{'native_proposal':{'answer':'synthetic'}}})+'\n')
            local=fixture();local['scheduler_source']['path']='/home/data3/txy/cf_moa/evaluation/run_moa_rcv_batched.py'
            local['protocol']['code_sources']={}
            local['protocol']['methods']['M5'].update(inputs=str(inputs),inputs_sha256=original.sha(inputs),
                saved_f_proposals=str(saved),saved_f_proposals_sha256=original.sha(saved))
            journal=original.RunJournal(source/'journal.sqlite3',local);raw=call()
            with journal.db:journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',tuple(raw[k] for k in (
                'request_id','ordinal','request','reserved_tokens','phase','status','result','physical','error','started','finished')))
            journal.db.close()
            original.write(source/'status.json',dict(status='stopped_by_request',first_systemic_error=None,cost={'unresolved_model_usage':0}))
            original.write(source/'supervisor_result.json',{'exit_code':1})
            receipt=original.prepare(source,root/'split',(2,1,3))
            for shard in receipt['shards']:
                run=Path(shard['output']);run.mkdir(exist_ok=True,parents=True);(run/'run.lock').touch()
                protocol=json.loads(Path(shard['plan']).read_text());tasks=protocol['methods']['M5']['tasks']
                selected=original.local_for_shard(local,protocol,tasks)
                journal=original.RunJournal(run/'journal.sqlite3',selected,resume=(run/'journal.sqlite3').exists())
                if shard['gpu']==2:
                    row=list(journal.db.execute('SELECT * FROM calls').fetchone());row[1]=1;row[4]='initializing';row[5]='failed';row[6]=None
                    with journal.db:
                        journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',tuple(row))
                        journal.db.execute('INSERT INTO meta VALUES (?,?)',('first_error','{"preserve":true}'))
                        journal.db.execute('INSERT INTO outputs VALUES (?,?)',(raw['request_id'],json.dumps(dict(status='complete',result={'native_answer':{'answer':'synthetic'}}))))
                    status=failed_status();exit_code=1;recovery=run
                else:
                    with journal.db:
                        for t in tasks:journal.db.execute('INSERT INTO outputs VALUES (?,?)',(t['task_id'],json.dumps(dict(status='complete'))))
                    status=dict(status='complete',cost={'unresolved_model_usage':0});exit_code=0
                journal.db.close()
                original.write(run/'status.json',status)
                original.write(run/'supervisor_result.json',dict(exit_code=exit_code,plan_sha256=shard['plan_sha256']))
            sources=[source/'journal.sqlite3']+[Path(s['output'])/'journal.sqlite3' for s in receipt['shards']]
            before={str(p):original.sha(p) for p in sources}
            result=m.prepare(root/'split/transfer_receipt.json',recovery,root/'tail')
            self.assertEqual(before,{str(p):original.sha(p) for p in sources})
            self.assertEqual(result['partition']['parent_selected_tasks'],12)
            self.assertEqual(result['partition']['parent_closed_tasks']+result['partition']['remaining_tasks'],12)
            self.assertEqual(result['partition']['known_cache_only_terminal_tasks'],1)
            self.assertEqual(result['cache_only_evidence']['native_answer_hashes'][raw['request_id']],original.digest({'answer':'synthetic'}))
            prefix_total=0;new_task_ids=set()
            for shard in result['shards']:
                protocol=json.loads(Path(shard['plan']).read_text())
                new_local=original.local_for_shard(local,protocol,protocol['methods']['M5']['tasks'])
                journal=original.RunJournal(Path(shard['output'])/'journal.sqlite3',new_local,resume=True)
                self.assertEqual(journal.db.execute('SELECT COUNT(*) FROM outputs').fetchone()[0],0)
                self.assertIsNone(journal.db.execute("SELECT value FROM meta WHERE key='first_error'").fetchone())
                for row in journal.db.execute('SELECT request,physical,result FROM calls'):
                    self.assertEqual(row[0],raw['request']);self.assertEqual(row[1],'[]')
                    self.assertEqual(json.loads(row[2])['events'][0]['mode'],'replay');prefix_total+=1
                journal.db.close()
                ids={t['task_id'] for t in protocol['methods']['M5']['tasks']}
                self.assertFalse(new_task_ids&ids);new_task_ids|=ids
            self.assertEqual(prefix_total,1)
            self.assertIn(raw['request_id'],new_task_ids)  # Known cached output retained, CPU reconstructed.
            with self.assertRaises(ValueError):m.prepare(root/'split/transfer_receipt.json',recovery,root/'tail')


if __name__=='__main__':unittest.main()
