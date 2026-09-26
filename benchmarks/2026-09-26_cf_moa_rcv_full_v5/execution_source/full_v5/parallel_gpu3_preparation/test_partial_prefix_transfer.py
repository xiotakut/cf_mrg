"""Synthetic-only migration plus actual unchanged db06 resume mechanism."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('partial_transfer',HERE/'partial_prefix_transfer.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from cf_moa.evaluation.run_moa_rcv_batched import FrontierBackend, NeedCallback
from cf_moa.evaluation.journal import JournalConflict
from cf_moa.evaluation.effect_first_runner import ResearchJournal
from cf_moa.evaluation.run_moa_rcv import stream_cost


def fixture():
    tasks=[dict(task_id=rid+':'+arm,request_id=rid,arm=arm) for rid in ('done','partial','fresh0','fresh1','fresh2','fresh3') for arm in ('strong_B','candidate_with_rationales')]
    local=dict(protocol={'methods':{'M4':{'tasks':tasks}}},method='M4',mode='live_batched',role='readout',batch_size=16,max_inputs=None,
        scheduler_source={'path':'synthetic','sha256':m.DB06},selected_input_ids=list(dict.fromkeys(t['request_id'] for t in tasks)),selected_task_ids=[t['task_id'] for t in tasks])
    return local


def call(ordinal=0):
    event=dict(mode='live',model='synthetic',config_hash='config',input_tokens=12,output_tokens=1,elapsed_seconds=2.)
    request=dict(messages=[{'role':'user','content':'synthetic only'}],seed=42,kind='score',codes=['A','B'],max_tokens=1)
    return dict(request_id='partial:candidate_with_rationales',ordinal=ordinal,request=m.serialized(request),reserved_tokens=12,
        phase='submitted',status='complete',result=m.serialized(dict(value={'A':-1.,'B':-2.},events=[event])),physical=m.serialized([dict(event=event,submission_state='accepted')]),error=None,started=1.,finished=2.)


class TransferTests(unittest.TestCase):
    def test_partition_old_complete_plus_disjoint_remaining_and_touched_stays(self):
        plan=fixture();term={'done:strong_B','done:candidate_with_rationales','partial:strong_B'}
        shards,proof=m.partition_tasks(plan,term,{'partial:candidate_with_rationales'})
        one={t['request_id'] for t in shards[1]};three={t['request_id'] for t in shards[3]}
        self.assertEqual(one,{'partial','fresh0','fresh2'})
        self.assertEqual(three,{'fresh1','fresh3'})
        self.assertEqual(proof['original_tasks'],12)
        self.assertEqual(proof['old_terminal_tasks']+proof['remaining_tasks'],12)
        self.assertEqual(proof['touched_unfinished_inputs'],1)
        self.assertTrue(proof['disjoint'] and proof['exhaustive'])

    def test_terminal_without_callbacks_still_counts_as_touched_input(self):
        plan=fixture();shards,_=m.partition_tasks(plan,{'fresh1:strong_B'},set())
        self.assertIn('fresh1',{t['request_id'] for t in shards[1]})
        self.assertNotIn('fresh1',{t['request_id'] for t in shards[3]})

    def test_unknown_task_cannot_be_ignored(self):
        with self.assertRaises(ValueError):m.partition_tasks(fixture(),{'outside'},set())

    def test_replay_zero_physical_preserves_request_original_event_and_source(self):
        original=call();saved=deepcopy(original)
        payload=m.replay_callback(original,{'journal':'closed.sqlite3','journal_sha256':'hash'})
        self.assertEqual(original,saved)
        self.assertEqual(payload[2],saved['request']);self.assertEqual(payload[7],'[]')
        event=json.loads(payload[6])['events'][0]
        self.assertEqual(event['mode'],'replay');self.assertEqual(event['elapsed_seconds'],0.)
        self.assertEqual(event['original_event']['elapsed_seconds'],2.)
        self.assertEqual(event['source_reference']['new_physical_requests'],0)

    def test_unknown_failed_or_inconsistent_physical_prefix_rejected(self):
        for field,value in [('status','started'),('status','failed'),('finished',None),('physical',None),('physical','[]')]:
            row=call();row[field]=value
            with self.assertRaises(ValueError):m.replay_callback(row,{'journal':'synthetic'})

    def test_unchanged_db06_replays_then_reaches_only_next_missing_callback(self):
        row=call();request=json.loads(row['request']);plan=fixture()
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'journal.sqlite3'
            journal=ResearchJournal(path,plan)
            with journal.db:journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',m.replay_callback(row,{'journal':'old'}))
            journal.db.close()
            journal=ResearchJournal(path,deepcopy(plan),resume=True)
            class Runtime:
                def count_tokens(self,request):return 12
            backend=FrontierBackend(journal,lambda:Runtime())
            backend.begin_item(row['request_id'])
            self.assertEqual(backend.count_tokens(request),12)
            replay=backend(request)
            self.assertEqual(replay.value,{'A':-1.,'B':-2.})
            self.assertEqual(replay.events[0]['mode'],'replay')
            backend.finish_item()
            with self.assertRaises(NeedCallback) as raised:backend(dict(request,seed=43))
            self.assertEqual(raised.exception.ordinal,1)
            cost=stream_cost(journal)
            self.assertEqual(cost['new_model_requests'],0);self.assertEqual(cost['physical_model_requests'],0)
            self.assertEqual(cost['submission_attempts'],1) # metadata row, not a new send
            journal.db.close()

    def test_new_plan_or_exact_request_drift_rejected_by_original_interfaces(self):
        row=call();plan=fixture()
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'journal.sqlite3';journal=ResearchJournal(path,plan)
            with journal.db:journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',m.replay_callback(row,{'journal':'old'}))
            backend=FrontierBackend(journal,lambda:None);backend.begin_item(row['request_id'])
            with self.assertRaises(JournalConflict):backend(dict(json.loads(row['request']),seed=99))
            journal.db.close()
            changed=deepcopy(plan);changed['batch_size']=8
            with self.assertRaises(JournalConflict):ResearchJournal(path,changed,resume=True)

    def test_local_plan_exact_grouping_and_unchanged_scheduler(self):
        old=fixture();tasks=old['protocol']['methods']['M4']['tasks'][2:]
        protocol=deepcopy(old['protocol']);protocol['allowed_gpus']=[1]
        local=m.local_for_shard(old,protocol,tasks)
        self.assertEqual(local['selected_task_ids'],[t['task_id'] for t in tasks])
        self.assertEqual(local['selected_input_ids'],['partial','fresh0','fresh1','fresh2','fresh3'])
        self.assertEqual(local['scheduler_source'],old['scheduler_source'])
        self.assertEqual(local['batch_size'],16)


if __name__=='__main__':unittest.main()
