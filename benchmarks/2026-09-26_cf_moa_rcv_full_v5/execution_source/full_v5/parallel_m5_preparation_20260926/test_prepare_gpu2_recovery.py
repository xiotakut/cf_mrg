from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gpu2_recovery',HERE/'prepare_gpu2_recovery.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
import partial_prefix_transfer as transfer
from test_partial_prefix_transfer import fixture,call


def failed_status():
    return dict(status='stopped_on_systemic_error',complete=1,
        first_systemic_error=dict(error_category='infrastructure',message='Shared engine initialization failed'),
        cost=dict(new_model_requests=0,physical_model_requests=0,unresolved_model_usage=0,failed_attempts=1))


class RecoveryTests(unittest.TestCase):
    def test_zero_physical_initialization_failure_only(self):
        raw=call();prefix=dict(zip(('request_id','ordinal','request','reserved_tokens','phase','status','result','physical','error','started','finished'),transfer.replay_callback(raw,{'journal':'original'})))
        failure=dict(prefix,ordinal=1,status='failed',phase='initializing',result=None)
        rows=[prefix,failure];counts={raw['request_id']:1}
        self.assertEqual(len(m.validate_failure(failed_status(),{'exit_code':1},rows,counts)),1)
        for field in ('new_model_requests','physical_model_requests','unresolved_model_usage'):
            status=failed_status();status['cost'][field]=1
            with self.subTest(field=field),self.assertRaises(ValueError):m.validate_failure(status,{'exit_code':1},rows,counts)
        changed=deepcopy(rows);changed[1]['phase']='submitted'
        with self.assertRaises(ValueError):m.validate_failure(failed_status(),{'exit_code':1},changed,counts)
        with self.assertRaises(ValueError):m.validate_failure(failed_status(),{'exit_code':1},rows,{raw['request_id']:2})

    def test_separate_recovery_exact_plan_prefix_and_old_failure_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.mkdir();(source/'run.lock').touch()
            inputs=root/'inputs.jsonl';inputs.write_text('')
            local=fixture();local['scheduler_source']['path']='/home/data3/txy/cf_moa/evaluation/run_moa_rcv_batched.py'
            local['protocol']['code_sources']={}
            local['protocol']['methods']['M5'].update(inputs=str(inputs),inputs_sha256=transfer.sha(inputs))
            journal=transfer.RunJournal(source/'journal.sqlite3',local)
            raw=call()
            with journal.db:
                journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',tuple(raw[k] for k in (
                    'request_id','ordinal','request','reserved_tokens','phase','status','result','physical','error','started','finished')))
            journal.db.close()
            transfer.write(source/'status.json',dict(status='stopped_by_request',first_systemic_error=None,cost={'unresolved_model_usage':0}))
            transfer.write(source/'supervisor_result.json',{'exit_code':1})
            receipt=transfer.prepare(source,root/'split',(2,1,3));shard=receipt['shards'][0]
            failed=Path(shard['output']);(failed/'run.lock').touch()
            same_local=json.loads((failed/'plan.json').read_text())
            journal=transfer.RunJournal(failed/'journal.sqlite3',same_local,resume=True)
            row=list(journal.db.execute('SELECT * FROM calls').fetchone());row[1]=1;row[4]='initializing';row[5]='failed';row[6]=None
            with journal.db:
                journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',tuple(row))
                journal.db.execute('INSERT INTO meta VALUES (?,?)',('first_error','{"preserve":true}'))
                journal.db.execute('INSERT INTO outputs VALUES (?,?)',('done:strong_B',json.dumps({'status':'complete','result':{'native_answer':'synthetic'}})))
            journal.db.close()
            transfer.write(failed/'status.json',failed_status())
            transfer.write(failed/'supervisor_result.json',{'exit_code':1,'plan_sha256':shard['plan_sha256']})
            oldsha=transfer.sha(failed/'journal.sqlite3');source_sha=transfer.sha(source/'journal.sqlite3')
            destination=root/'split/gpu2_recovery1'
            result=m.prepare(root/'split/transfer_receipt.json',destination)
            self.assertTrue(result['failed_source_SQL_unchanged'])
            self.assertEqual(transfer.sha(failed/'journal.sqlite3'),oldsha)
            self.assertEqual(transfer.sha(source/'journal.sqlite3'),source_sha)
            self.assertEqual((destination/'plan.json').read_bytes(),Path(shard['plan']).read_bytes())
            journal=transfer.RunJournal(destination/'runs/m5/journal.sqlite3',same_local,resume=True)
            self.assertEqual(journal.db.execute('SELECT COUNT(*) FROM outputs').fetchone()[0],0)
            self.assertEqual(journal.db.execute('SELECT COUNT(*) FROM calls').fetchone()[0],1)
            self.assertIsNone(journal.db.execute("SELECT value FROM meta WHERE key='first_error'").fetchone())
            copied=journal.db.execute('SELECT request,physical,result FROM calls').fetchone()
            self.assertEqual(copied[0],raw['request']);self.assertEqual(copied[1],'[]')
            self.assertEqual(json.loads(copied[2])['value'],json.loads(raw['result'])['value'])
            journal.db.close()
            with self.assertRaises(ValueError):m.prepare(root/'split/transfer_receipt.json',destination)


if __name__=='__main__':unittest.main()
