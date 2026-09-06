"""One compact contract check: leakage, native parsing, paired identities."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_cf_baseline_screening import solver_input, task_question, reader_prompt, stable_seed, task_profile
from analyze_cf_baseline_screening import parse, four_grid, method_comparison

class Tokenizer:
    def apply_chat_template(self,messages,**kwargs):return '\n'.join(m['content'] for m in messages)

class Contract(unittest.TestCase):
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
        self.assertNotEqual(stable_seed(1,'s000001','generate',0),stable_seed(1,'s000002','generate',0))

    def test_metrics_identities_and_invalid_persistence(self):
        a=[True,True,False,False];b=[True,False,True,False]
        c=method_comparison(a,b);self.assertEqual(c['net_gain'],(sum(b)-sum(a))/4);self.assertEqual(c['OCP'],1-c['conditional_harm_rate'])
        pairs=[{'ref':{'correct':x,'semantic_gold':'old'},'var':{'correct':y,'semantic_prediction':'new' if y else None},'group':str(i),'relation':'change'} for i,(x,y) in enumerate(zip(a,b))]
        g=four_grid(pairs);self.assertEqual(g['N'],sum(g[k] for k in ['n11','n10','n01','n00']));self.assertEqual(g['drop_micro'],g['A_ref']-g['A_var']);self.assertEqual(g['BTR'],0);self.assertEqual(g['conditional_success']+g['conditional_failure'],1)
        empty=method_comparison([],[]);self.assertIsNone(empty['net_gain']);self.assertIsNone(empty['OCP'])

if __name__=='__main__':unittest.main()
