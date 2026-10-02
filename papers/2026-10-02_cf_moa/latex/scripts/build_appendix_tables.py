#!/usr/bin/env python3
"""Render frozen existing scores; this program never invokes a model or grader."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = [('original_C0', 'C0'), ('strong_B', 'B'), ('candidate_only', 'C2'),
        ('candidate_with_rationales', 'C3'), ('pool_old_plus_three', 'C4'), ('joint_selector', 'C5')]
SOURCES = [('M01', 'MedEinst'), ('M02', 'MedPIC-Bench'), ('M06', 'HIV scenarios'),
           ('M10', 'CPV-MedQA'), ('M11', 'Cultural Cues'), ('M12', 'FairMedQA/AMQA'),
           ('M14', 'DiversityMedQA'), ('M17', 'MedPerturb'), ('M20', 'MedCounterFact'),
           ('M22', 'MedRGB'), ('M23', 'BioRAB')]

def table(caption, label, spec, header, rows):
    return '\n'.join([
        '% Generated from frozen full-v5 summaries; no new scoring.',
        r'\begin{table}[htbp]', r'\centering\small',
        r'\caption{' + caption + '}', r'\label{' + label + '}',
        r'\setlength{\tabcolsep}{6pt}', r'\begin{tabular}{@{}' + spec + '@{}}',
        r'\toprule', ' & '.join(header) + r' \\', r'\midrule',
        *[' & '.join(map(str, row)) + r' \\' for row in rows],
        r'\bottomrule', r'\end{tabular}', r'\end{table}', ''])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=ROOT / 'inputs' / 'full_results')
    parser.add_argument('--output', type=Path, default=ROOT / 'draft' / 'tables')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    audit = {'operation': 'render_existing_scores', 'inputs': {}, 'tables': {}}
    def read(name):
        data = (args.inputs / name).read_bytes()
        audit['inputs'][name] = hashlib.sha256(data).hexdigest()
        return json.loads(data)
    cats = read('all_category_results.json')
    sources = read('all_source_results.json')
    formats = read('format_input_results.json')
    categories = ['ALL', 'R1', 'R2', 'R3', 'R4', 'R5']
    actual_arms = sorted({x['arm'] for x in cats})
    expected = {x[0] for x in ARMS}
    if set(actual_arms) != expected:
        raise ValueError(f'Unexpected arm identities: {actual_arms}')
    ci = {(x['method'], x['arm'], x['category']): x for x in cats}
    rows = []
    for method, model in [('M4', 'Llama'), ('M5', 'Qwen')]:
        for arm, short in ARMS:
            assert ci[method, arm, 'ALL']['units'] == 6104
            rows.append([model, short] + [f"{100*ci[method,arm,c]['mean_native_unit_score']:.2f}" for c in categories])
    contents = table('Full six-arm category scores (percent). ALL and category scores use native unit means; categories overlap.', 'tab:full-categories', 'llrrrrrr', ['Backbone', 'Arm']+categories, rows)
    (args.output / 'full_categories.tex').write_text(contents)
    audit['tables']['full_categories'] = {'rows': len(rows), 'cells': 72}
    si = {(x['method'], x['arm'], x['source']): x for x in sources}
    rows = []
    for source, name in SOURCES:
        n = si['M4', 'strong_B', source]['units']
        values = [si[m,a,source]['mean_native_unit_score']*100 for m in ['M4','M5'] for a in ['original_C0','strong_B']]
        rows.append([name, f'{n:,}']+[f'{v:.2f}' for v in values])
    assert sum(si['M4','strong_B',s]['units'] for s,_ in SOURCES) == 6104
    contents = table('Source-specific native unit means (percent) for the original system and adopted controller. Source sizes are comparison units.', 'tab:source-breakdown', 'lrrrrr', ['Source', 'Units', 'Llama C0', 'Llama B', 'Qwen C0', 'Qwen B'], rows)
    (args.output / 'source_breakdown.tex').write_text(contents)
    audit['tables']['source_breakdown'] = {'rows': len(rows), 'cells': 44}
    fi = {(x['method'], x['arm'], x['answer_format']):x for x in formats}
    names = sorted({x['answer_format'] for x in formats})
    rows=[]
    for fmt in names:
        n=fi['M4','strong_B',fmt]['inputs']
        vals=[fi[m,a,fmt]['input_accuracy']*100 for m in ['M4','M5'] for a in ['original_C0','strong_B']]
        rows.append([fmt.replace('_', r'\_'), f'{n:,}']+[f'{v:.2f}' for v in vals])
    assert sum(fi['M4','strong_B',f]['inputs'] for f in names)==13905
    contents=table('Native input-format accuracy (percent), including reference inputs. This input-level metric differs from ALL.', 'tab:format-breakdown', 'lrrrrr', ['Format', 'Inputs', 'Llama C0', 'Llama B', 'Qwen C0', 'Qwen B'], rows)
    (args.output/'format_breakdown.tex').write_text(contents)
    audit['tables']['format_breakdown']={'rows':len(rows),'cells':len(rows)*4}
    (args.output/'appendix_table_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))

if __name__ == '__main__':
    main()
