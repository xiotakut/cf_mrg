"""Synthetic closed-file handoff checks; no models, graders or SQL connections."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('handoff_analysis',Path(__file__).with_name('analysis_plan.py'))
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)


def dump(path,value,lines=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(json.dumps(v) for v in value)+'\n' if lines else json.dumps(value))


class HandoffAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.all_ids=['x'+str(i)+':strong_B' for i in range(6)]
        self.analyzer=self.root/'analyze_full.py';self.analyzer.write_text('# synthetic identity only\n')
        self.sizepatch=patch.object(api,'EXPECTED_TASK_ROWS',6);self.sizepatch.start();self.addCleanup(self.sizepatch.stop)
        self.patcher=patch.object(api,'ANALYZER_SHA256',api.sha(self.analyzer));self.patcher.start();self.addCleanup(self.patcher.stop)
        self.original=self.root/'original_plan.json';dump(self.original,self.plan(self.all_ids))
        self.old=self.make_run('old',self.all_ids,self.all_ids[:2],True)
        self.left=self.make_run('left',self.all_ids[2:4],self.all_ids[2:4])
        self.right=self.make_run('right',self.all_ids[4:],self.all_ids[4:])
        self.output=self.root/'analysis/m5';self.output.mkdir(parents=True)
        (self.output/'native_score_cache.sqlite3').write_text('synthetic existing score cache')
        self.prior=self.root/'earlier/proposals.jsonl';dump(self.prior,[{'synthetic':'prior'}],True)
        self.before=dict(methods=['M5'],script_sha256=api.ANALYZER_SHA256,status='partial',**api.DENOMINATORS,
            input_sources=[dict(**api.ref(self.prior),terminal_rows=1)])
        dump(self.output/'receipt.json',self.before)
        self.config=dict(schema_version='M5_multi_shard_incremental_analysis_v1',original_stage_plan=str(self.original),
            old_stopped_source=self.old,new_shards=[self.left,self.right],analyzer=str(self.analyzer),
            analysis_output=str(self.output),python='/synthetic/python')

    def plan(self,ids):return dict(methods={'M5':{'tasks':[dict(task_id=i) for i in ids]}})

    def make_run(self,name,planned,finished,old=False):
        p=self.root/name;plan=p/'plan.json';dump(plan,self.plan(planned))
        dump(p/'status.json',dict(status='stopped_by_request' if old else 'complete',planned=len(planned),
            complete=len(finished),unavailable=0,failed=0,not_submitted=len(planned)-len(finished),first_systemic_error=None,
            cost=dict(model_usage_complete=True,unresolved_model_usage=0,unfinished_call_wall_unknown=0)))
        dump(p/'supervisor_result.json',dict(method='M5',exit_code=1 if old else 0,finished_at='2026-09-25T12:00:00+08:00'))
        dump(p/'proposals.jsonl',[dict(method='M5',request_id=i.split(':')[0],arm='strong_B',task_id=i,
            input_hash='synthetic_'+i,status='complete',result={'native_answer':{'synthetic':True}}) for i in finished],True)
        (p/'journal.sqlite3').write_text('synthetic closed journal '+name)
        return dict(run_dir=str(p),stage_plan=str(plan))

    def test_stopped_closed_plus_two_complete_shards_produce_one_existing_cache_command(self):
        p=api.prepare(self.config);self.assertEqual(p['terminal_union_rows'],6)
        self.assertEqual(p['command'].count('--proposals'),3)
        self.assertIn(str(self.output),p['command']);self.assertFalse(p['SQL_opened'])
        self.assertEqual(len(p['physical_journal_additions']),3)

    def test_running_source_is_rejected(self):
        path=Path(self.old['run_dir'])/'status.json';v=api.read(path);v['status']='running';dump(path,v)
        with self.assertRaisesRegex(ValueError,'closed'):api.prepare(self.config)

    def test_new_partial_shard_is_rejected(self):
        path=Path(self.left['run_dir'])/'status.json';v=api.read(path);v['not_submitted']=1;dump(path,v)
        with self.assertRaisesRegex(ValueError,'denominator'):api.prepare(self.config)

    def test_overlap_between_old_and_new_is_rejected(self):
        self.config['new_shards'][0]=self.make_run('overlap',[self.all_ids[0],self.all_ids[2]],[self.all_ids[0],self.all_ids[2]])
        with self.assertRaisesRegex(ValueError,'overlap'):api.prepare(self.config)

    def test_missing_old_task_cannot_drop_from_denominator(self):
        self.config['new_shards'][1]=self.make_run('missing',[self.all_ids[4]],[self.all_ids[4]])
        with self.assertRaisesRegex(ValueError,'omits'):api.prepare(self.config)

    def test_unknown_submission_prevents_closure(self):
        path=Path(self.old['run_dir'])/'status.json';v=api.read(path);v['cost']['unresolved_model_usage']=1;dump(path,v)
        with self.assertRaisesRegex(ValueError,'Unresolved'):api.prepare(self.config)

    def test_previous_source_change_is_not_silently_rebound(self):
        self.prior.write_text('changed')
        with self.assertRaisesRegex(ValueError,'registered'):api.prepare(self.config)

    def test_copied_sql_cannot_be_counted_twice(self):
        (Path(self.right['run_dir'])/'journal.sqlite3').write_bytes((Path(self.left['run_dir'])/'journal.sqlite3').read_bytes())
        with self.assertRaisesRegex(ValueError,'copied'):api.prepare(self.config)

    def test_nonempty_wal_is_not_closed_source(self):
        (Path(self.old['run_dir'])/'journal.sqlite3-wal').write_text('active')
        with self.assertRaisesRegex(ValueError,'checkpointed'):api.prepare(self.config)

    def test_final_full_receipt_retains_all_old_and_new_sources(self):
        p=api.prepare(self.config)
        r=dict(status='complete',methods=['M5'],script_sha256=api.ANALYZER_SHA256,inference_calls=0,
            new_native_grader_calls=3,**api.DENOMINATORS,input_sources=p['prior_registered_sources']+
            [dict(**s['proposals'],terminal_rows=s['terminal_rows']) for s in p['sources']])
        self.assertEqual(api.validate_final(p,r)['new_grader_calls'],3)
        r['input_sources']=r['input_sources'][1:]
        with self.assertRaisesRegex(ValueError,'omitted'):api.validate_final(p,r)


    def test_three_shards_are_supported_without_cost_duplication(self):
        self.config['new_shards']=[self.make_run('a',[self.all_ids[2]],[self.all_ids[2]]),
            self.make_run('b',[self.all_ids[3]],[self.all_ids[3]]),self.right]
        p=api.prepare(self.config)
        self.assertEqual(p['terminal_union_rows'],6)
        self.assertEqual(p['command'].count('--proposals'),4)
        self.assertEqual(len(p['physical_journal_additions']),4)

    def test_wrong_original_task_denominator_is_rejected(self):
        with patch.object(api,'EXPECTED_TASK_ROWS',47689):
            with self.assertRaisesRegex(ValueError,'denominator'):api.prepare(self.config)

    def test_unsupported_number_of_shards_is_rejected(self):
        self.config['new_shards']=[self.left]
        with self.assertRaisesRegex(ValueError,'two or three'):api.prepare(self.config)

if __name__=='__main__':unittest.main()

