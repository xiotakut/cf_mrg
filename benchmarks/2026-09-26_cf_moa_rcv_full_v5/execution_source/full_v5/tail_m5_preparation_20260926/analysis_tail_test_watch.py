"""Synthetic listener checks with a fake CPU child; never start a subprocess."""
from types import SimpleNamespace
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('two_shard_listener',Path(__file__).with_name('analysis_tail_watch.py'))
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)


def put(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))


class ListenerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.old=self.root/'old';self.a=self.root/'a';self.b=self.root/'b';self.output=self.root/'analysis';self.folder=self.root/'listener';self.folder.mkdir()
        self.state=dict(status='complete',planned=2,complete=2,failed=0,unavailable=0,not_submitted=0,first_systemic_error=None,
                        cost=dict(model_usage_complete=True,unresolved_model_usage=0,unfinished_call_wall_unknown=0))
        self.all_shards=[self.a,self.b,self.root/'c',self.root/'d',self.root/'e']
        for p in self.all_shards:
            put(p/'status.json',self.state);put(p/'supervisor_result.json',dict(method='M5',exit_code=0,finished_at='done'))
            put(p/'plan.json',{'methods':{'M5':{'tasks':[{'task_id':'x:strong_B'},{'task_id':'y:strong_B'}]}}})
        put(self.old/'status.json',dict(self.state,status='stopped_by_request'))
        put(self.old/'supervisor_result.json',dict(method='M5',exit_code=1,finished_at='done'))
        self.config=dict(schema_version='M5_five_complete_shard_incremental_analysis_v1',old_stopped_source={'run_dir':str(self.old)},
            new_shards=[dict(run_dir=str(p),stage_plan=str(p/'plan.json')) for p in self.all_shards],analysis_output=str(self.output))
        put(self.output/'receipt.json',{'status':'partial'})
        self.prepared={'command':['/fake/python','unchanged_analyze_full.py','--method','M5','--grade-missing']}

    def ready(self):return w.readiness(self.config)

    def test_both_closed_required_not_just_task_status(self):
        (self.b/'supervisor_result.json').unlink()
        self.assertEqual(self.ready()['state'],'waiting')
        self.assertFalse((self.folder/'analysis_once').exists())

    def test_ordinary_failures_are_terminal_not_systemic_block(self):
        put(self.a/'status.json',dict(self.state,complete=1,failed=1))
        self.assertEqual(self.ready()['state'],'ready')

    def test_systemic_stop_blocks(self):
        put(self.a/'status.json',dict(self.state,status='stopped_on_systemic_error',first_systemic_error={'synthetic':True}))
        self.assertEqual(self.ready()['state'],'blocked')

    def test_nonzero_supervisor_blocks(self):
        put(self.b/'supervisor_result.json',dict(method='M5',exit_code=1,finished_at='done'))
        self.assertEqual(self.ready()['state'],'blocked')

    def test_poll_under_thirty_seconds(self):self.assertTrue(0<w.POLL_SECONDS<=30)

    def test_once_success_and_reentry_never_launch_twice(self):
        calls=[]
        def popen(cmd,**kwargs):
            calls.append(cmd);self.assertEqual(kwargs['env']['CUDA_VISIBLE_DEVICES'],'')
            def wait():put(self.output/'receipt.json',{'status':'complete'});return 0
            return SimpleNamespace(pid=999,wait=wait)
        def validate(prepared,receipt):self.assertEqual(receipt['status'],'complete');return {'checked':True}
        args=dict(popen=popen,prepare=lambda config:self.prepared,validate=validate)
        result,code=w.run_once(self.config,self.folder,self.ready(),**args)
        self.assertEqual((result['status'],code),('complete',0));self.assertEqual(len(calls),1)
        result,code=w.run_once(self.config,self.folder,self.ready(),**args)
        self.assertEqual(code,3);self.assertEqual(len(calls),1)

    def test_failed_child_is_not_retried(self):
        calls=[]
        def popen(cmd,**kw):calls.append(cmd);return SimpleNamespace(pid=999,wait=lambda:1)
        args=dict(popen=popen,prepare=lambda config:self.prepared,validate=lambda *x:self.fail('cannot validate failure'))
        result,code=w.run_once(self.config,self.folder,self.ready(),**args)
        self.assertEqual((result['status'],code),('blocked_analysis_failed_no_retry',2))
        w.run_once(self.config,self.folder,self.ready(),**args);self.assertEqual(len(calls),1)

    def test_existing_complete_union_skips_analyzer(self):
        put(self.output/'receipt.json',{'status':'complete'})
        result,code=w.run_once(self.config,self.folder,self.ready(),
            popen=lambda *a,**k:self.fail('no additional grader'),prepare=lambda c:self.prepared,
            validate=lambda p,r:{'same_union':True})
        self.assertEqual(result['status'],'already_analyzed_no_new_grader');self.assertEqual(code,0)
        self.assertEqual(result['analysis_submissions'],0)

    def test_prepare_failure_keeps_claim_no_submit(self):
        def bad(c):raise ValueError('synthetic conflicting union')
        result,code=w.run_once(self.config,self.folder,self.ready(),prepare=bad,
                              popen=lambda *a,**k:self.fail('must not launch'))
        self.assertEqual((result['status'],code),('blocked_no_retry',2))
        self.assertTrue((self.folder/'analysis_once/result.json').is_file())


    def test_all_five_shards_require_closure(self):
        fifth=self.all_shards[-1]
        (fifth/'supervisor_result.json').unlink()
        self.assertEqual(self.ready()['state'],'waiting')
        put(fifth/'supervisor_result.json',dict(method='M5',exit_code=0,finished_at='done'))
        self.assertEqual(self.ready()['state'],'ready')

    def test_persistent_malformed_status_fails_with_exact_path(self):
        path=self.b/'status.json';path.write_text('{')
        from unittest.mock import patch
        original=w.helper.reader.read_json
        with patch.object(w.helper.reader,'read_json',side_effect=lambda p: original(p,delays=(0,0),sleeper=lambda _:None)):
            with self.assertRaises(w.helper.reader.PersistentJSONReadError) as err:self.ready()
        self.assertEqual(err.exception.diagnostic['path'],str(path))
        self.assertEqual(err.exception.diagnostic['attempts'],3)

    def test_transient_in_progress_status_read_recovers_without_analysis(self):
        from unittest.mock import patch
        path=self.b/'status.json';original=Path.read_bytes;attempts=[];events=[]
        def read_bytes(p):
            if p==path and not attempts:
                attempts.append(str(p));return b''
            return original(p)
        reader=w.helper.reader.read_json
        with patch.object(Path,'read_bytes',read_bytes),patch.object(w.helper.reader,'read_json',
                side_effect=lambda p: reader(p,delays=(0,),sleeper=lambda _:None,audit=events.append)):
            self.assertEqual(self.ready()['state'],'ready')
        self.assertEqual(events[0]['status'],'transient_json_read_recovered')
        self.assertEqual(events[0]['attempts'],2)
        self.assertFalse((self.folder/'analysis_once').exists())

if __name__=='__main__':unittest.main()


