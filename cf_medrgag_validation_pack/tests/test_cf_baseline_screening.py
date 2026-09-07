"""One compact contract check: leakage, native parsing, paired identities."""
import sys
from pathlib import Path
import unittest
import json
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_cf_baseline_screening import solver_input, task_question, reader_prompt, stable_seed, task_profile
from analyze_cf_baseline_screening import parse, four_grid, method_comparison

class Tokenizer:
    def apply_chat_template(self,messages,**kwargs):return '\n'.join(m['content'] for m in messages)

class Contract(unittest.TestCase):
    def test_reader_completion_stops_before_m2_stages(self):
        from types import SimpleNamespace
        from run_cf_baseline_screening import Runner
        runner=Runner.__new__(Runner);runner.args=SimpleNamespace(mode='readers')
        runner.methods=['M0','M1','M2'];runner.cached={};runner.hits=Counter()
        runner.backend=SimpleNamespace(tokenizer=Tokenizer());calls=[]
        item={'item_id':'s000001','question':'Patient and question','options':{'A':'x','B':'y'},'fixed_evidence':['mandatory'],'answer_format':'single'}
        runner.retrieve=lambda items:{item['item_id']:[{'contents':'initial evidence'}]}
        runner.llm=lambda stage,entries:calls.append((stage,entries))
        runner.save_runtime=lambda:None
        runner.run_chunk([item])
        self.assertEqual([stage for stage,_ in calls],['M0','M1'])
        self.assertNotIn('initial evidence',calls[0][1][0]['prompt'])
        self.assertIn('initial evidence',calls[1][1][0]['prompt'])
        self.assertTrue(all('mandatory' in entries[0]['prompt'] for _,entries in calls))
        runner.cached={m:{item['item_id']:{}} for m in ['M0','M1']};calls.clear()
        runner.run_chunk([item]);self.assertEqual(calls,[])

    def test_full_release_coverage_and_exact_reuse(self):
        root=Path(__file__).resolve().parents[1];out=root/'results_cf_full_test'
        if not (out/'screening_items.jsonl').exists():self.skipTest('full release assets not prepared locally')
        from prepare_cf_baseline_screening import read
        import pyarrow.parquet as pq
        sources=json.loads((out/'acquisition.json').read_text());labels=read(out/'evaluation_labels.jsonl')
        native=lambda ds:[r for r in labels if r['dataset']==ds and r['protocol']=='native']
        med=read(sources['medeinst']['paths'][0]);self.assertEqual(Counter(r['source_id'] for r in native('medeinst')),Counter(r['case_id'] for r in med))
        cpv=pq.read_table(sources['cpv']['paths'][0]).to_pylist();expected=Counter(r['case_id'] for r in cpv);expected.update(expected.keys())
        self.assertEqual(Counter(r['source_id'] for r in native('cpv')),expected)
        world=[r for p in sources['medcounterfact']['paths'] for r in read(p)]
        self.assertEqual(Counter(r['source_id'] for r in native('medcounterfact')),Counter(str(r['metadata']['id']) for r in world))
        self.assertEqual(len(native('medpic')),len(json.loads(Path(sources['medpic']['paths'][0]).read_text())))
        self.assertEqual(len(native('cultural')),10*len(json.loads(Path(sources['cultural']['paths'][0]).read_text())))
        old=read(root/'results_cf_screening/screening_items.jsonl');new=read(out/'screening_items.jsonl')
        self.assertEqual(new[:len(old)],old)
        self.assertEqual({r['item_id'] for r in labels},{r['item_id'] for r in new})
        import csv
        method_count=len(json.loads((out/'method_scope.json').read_text())['methods']) if (out/'method_scope.json').exists() else 3
        with (out/'benchmark_summary.csv').open() as summary:
            for row in csv.DictReader(summary):
                self.assertEqual(int(row['planned_method_predictions']),method_count*int(row['unique_inputs']))

    def test_visible_task_and_native_contracts(self):
        raw={'item_id':'s000001','question':'Patient vignette and final question','options':{'A':'x','B':'y','E':'z'},'fixed_evidence':['mandatory article'],'answer_format':'multi','gold':['A'],'role':'trap','paired_text':'SECRET','taxonomy':'SECRET'}
        item=solver_input(raw);self.assertEqual(set(item),{'item_id','question','options','fixed_evidence','answer_format'})
        for docs in [[],[{'contents':'external'}]]:
            p=reader_prompt(Tokenizer(),item,docs);self.assertIn('mandatory article',p);self.assertIn('E: z',p);self.assertNotIn('SECRET',p)
        self.assertEqual(parse('{"answer":["E","A"]}',item,{})[0],('A','E'))
        self.assertIsNotNone(parse('{"answer":"A"}',item,{})[1])
        self.assertIsNotNone(parse('{"answer":["A"]} {"answer":["B"]}',item,{})[1])
        item['options']={};item['answer_format']='diagnosis'
        p=reader_prompt(Tokenizer(),item,[]);self.assertIn('exactly one most likely diagnosis',p)
        self.assertNotIn('multiple-choice question',task_profile(item).generation_prompt)
        canon={'bronchitis':'Bronchitis'}
        self.assertEqual(parse('{"answer":"Bronchitis"}',item,canon)[0],'Bronchitis')
        self.assertIsNotNone(parse('{"answer":"chronic bronchitis"}',item,canon)[1])
        self.assertIsNotNone(parse('{"answer":"Bronchitis or pneumonia"}',item,canon)[1])
        item['answer_format']='relation';self.assertEqual(parse('{"answer":"uncertainty"}',item,{})[0],'uncertainty')
        self.assertEqual(parse('{"answer":"I cannot provide medical advice"}',item,{})[1],'refusal')
        self.assertNotEqual(stable_seed(1,'s000001','generate',0),stable_seed(1,'s000002','generate',0))
        self.assertEqual(stable_seed(20260906,'s000911','generate',0),20352939)
        primary={stable_seed(20260906,'s000911','generate',j) for j in range(5)}
        repeat={stable_seed(20260907,'s000911','generate',j,repeat_stream=True) for j in range(5)}
        self.assertTrue(primary.isdisjoint(repeat))

    def test_metrics_identities_and_invalid_persistence(self):
        a=[True,True,False,False];b=[True,False,True,False]
        c=method_comparison(a,b);self.assertEqual(c['net_gain'],(sum(b)-sum(a))/4);self.assertEqual(c['OCP'],1-c['conditional_harm_rate'])
        pairs=[{'ref':{'correct':x,'semantic_gold':'old'},'var':{'correct':y,'semantic_prediction':'new' if y else None},'group':str(i),'relation':'change'} for i,(x,y) in enumerate(zip(a,b))]
        g=four_grid(pairs);self.assertEqual(g['N'],sum(g[k] for k in ['n11','n10','n01','n00']));self.assertEqual(g['drop_micro'],g['A_ref']-g['A_var']);self.assertEqual(g['BTR'],0);self.assertEqual(g['conditional_success']+g['conditional_failure'],1)
        empty=method_comparison([],[]);self.assertIsNone(empty['net_gain']);self.assertIsNone(empty['OCP'])

if __name__=='__main__':unittest.main()
