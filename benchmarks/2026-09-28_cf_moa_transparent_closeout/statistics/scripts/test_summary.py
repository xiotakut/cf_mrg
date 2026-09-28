import gzip
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
from summarize_existing_results import (CONTRASTS,aggregate_units,build_atoms,paired_family_bootstrap,read_jsonl)

class SummaryTests(unittest.TestCase):
    def test_physical_lines_and_gzip(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'a.jsonl.gz'
            with gzip.open(p,'wt',encoding='utf-8') as f:
                f.write(json.dumps({'text':'a\u2029b'},ensure_ascii=False)+'\n')
            self.assertEqual(list(read_jsonl(p)),[{'text':'a\u2029b'}])
    def atoms(self):
        arms={a for c in CONTRASTS for a in c}
        d={a:{'u0':('f1',0.),'u1':('f2',0.),'u2':('f2',0.),'u3':('f2',0.)} for a in arms}
        d['candidate_with_rationales']['u0']=('f1',1.)
        return d
    def test_native_unit_weight_not_family_mean(self):
        got=paired_family_bootstrap(self.atoms(),100,240924)
        row=next(r for r in got if r['candidate']=='candidate_with_rationales' and r['baseline']=='strong_B')
        self.assertEqual(row['delta_pp'],25.)
        self.assertEqual(row['atoms'],4)
        self.assertEqual(row['families'],2)
    def test_exactly_equal_candidates_zero_interval(self):
        got=paired_family_bootstrap(self.atoms(),100,240924)
        row=next(r for r in got if r['candidate']=='strong_B')
        self.assertEqual(row['percentile_95_pp'],[0.,0.])
    def test_missing_is_not_silently_dropped(self):
        d=self.atoms();del d['candidate_with_rationales']['u2']
        with self.assertRaises(ValueError):paired_family_bootstrap(d,100,42)
    def test_all_sources_and_unavailable_kept(self):
        rows=[{'method':'M4','arm':'strong_B','source':s,'family_id':f,
               'score':v,'complete':True,'native_records':1,'unavailable_mappings':u}
              for s,f,v,u in [('a','fa',1.,0),('b','fb',0.,1)]]
        by_source=aggregate_units(rows,('method','arm','source'))
        self.assertEqual({r['source'] for r in by_source},{'a','b'})
        self.assertEqual(sum(r['unavailable_mappings'] for r in by_source),1)
        all_=aggregate_units(rows,('method','arm'))[0]
        self.assertEqual(all_['units'],2)
        self.assertEqual(all_['mean_native_unit_score'],.5)
    def test_pairs_keep_wrong_or_unavailable(self):
        rows=[{'arm':'strong_B','pair_id':str(i),'family_id':'f','relation':'maintain',
               'complete':True,'both_correct':v} for i,v in enumerate([True,False])]
        a=build_atoms(rows,'maintain')['strong_B']
        self.assertEqual(len(a),2)
        self.assertEqual(sum(v[1] for v in a.values()),1.)

if __name__=='__main__': unittest.main(verbosity=2)
