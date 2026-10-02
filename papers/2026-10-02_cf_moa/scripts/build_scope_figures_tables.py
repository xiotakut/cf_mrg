#!/usr/bin/env python3
"""Reproduce seven-system tables/figure from frozen aggregate evidence, offline.

python scripts/build_scope_figures_tables.py --check-only
python scripts/build_scope_figures_tables.py --output-dir path/to/latex
No model calls, native scoring, network requests, or raw predictions are used.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

METHODS = ['M0', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7']
CATEGORIES = ['ALL', 'R1', 'R2', 'R3', 'R4', 'R5']
NAMES = {'M0': 'Direct', 'M2': 'MedRGAG', 'M3': 'MA-RAG',
         'M4': 'MedRAG--L', 'M5': 'MedRAG--Q', 'M6': 'MedGENIE', 'M7': 'TC-RAG'}
DISPLAY = {'M0': 'M0  Direct', 'M2': 'M2  MedRGAG', 'M3': 'M3  MA-RAG',
           'M4': 'M4  MedRAG (Llama)', 'M5': 'M5  MedRAG (Qwen)',
           'M6': 'M6  MedGENIE', 'M7': 'M7  TC-RAG'}
BACKBONES = {'M0': 'L', 'M2': 'L', 'M3': 'Q', 'M4': 'L', 'M5': 'Q', 'M6': 'L', 'M7': 'Q'}
DENOMINATORS = {'ALL': 6104, 'R1': 2866, 'R2': 79, 'R3': 733, 'R4': 13, 'R5': 3600}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b):
    assert math.isclose(float(a), float(b), rel_tol=0, abs_tol=1e-10), (a, b)


def validate(input_dir, manifest_path):
    manifest = json.loads(manifest_path.read_text())
    for item in manifest['inputs']:
        path = input_dir / item['filename']
        assert path.is_file(), str(path)
        assert sha256(path) == item['sha256'], f'Input hash mismatch: {path}'
    baseline = json.loads((input_dir / 'seven_methods_audit.json').read_text())
    heads = json.loads((input_dir / 'head_research_audit.json').read_text())
    with (input_dir / 'category_comparison.csv').open(newline='') as stream:
        category_rows = {row['category']: row for row in csv.DictReader(stream)}
    methods = {row['method']: row for row in baseline['methods']}
    assert set(methods) == set(METHODS)
    assert len({row['method_family'] for row in methods.values()}) == 6
    assert set(category_rows) == set(CATEGORIES)
    baseline_checks = 0
    for method in METHODS:
        assert methods[method]['unique_inputs'] == 13905
        for category in CATEGORIES:
            row = category_rows[category]
            audit = methods[method]['categories'][category]
            assert int(row['units']) == audit['units'] == DENOMINATORS[category]
            close(row[method], audit['reported_accuracy_percent'])
            close(row[method], audit['accuracy_percent'])
            baseline_checks += 1
    with (input_dir / 'head_results.csv').open(newline='') as stream:
        head_csv = {(row['category'], row['method']): row for row in csv.DictReader(stream)}
    assert len(head_csv) == 21
    head_checks = 0
    for category in ['R1', 'R2', 'R3']:
        assert {row['method'] for row in heads['verified_results'][category]} == set(METHODS)
        for row in heads['verified_results'][category]:
            csv_row = head_csv[category, row['method']]
            assert row['n'] == DENOMINATORS[category]
            for key in ['n', 'baseline_correct', 'head_correct', 'repairs', 'harms']:
                assert int(csv_row[key]) == row[key]
            for key in ['baseline_pct', 'head_pct', 'delta_pp']:
                close(csv_row[key], row[key])
            assert 0 <= row['baseline_correct'] <= row['n']
            assert 0 <= row['head_correct'] <= row['n']
            assert row['head_correct'] - row['baseline_correct'] == row['repairs'] - row['harms']
            close(row['baseline_pct'], row['baseline_correct'] / row['n'] * 100)
            close(row['head_pct'], row['head_correct'] / row['n'] * 100)
            close(row['head_pct'] - row['baseline_pct'], row['delta_pp'])
            close(row['baseline_pct'], category_rows[category][row['method']])
            assert row['original_vs_formal_baseline_mismatches'] == 0
            head_checks += 1
    assert baseline_checks == 42 and head_checks == 21
    controls = heads['r3_diagnosis_controls']
    assert len(controls) == 28
    for method in METHODS:
        rows = [row for row in controls if row['method'] == method]
        assert {row['variant'] for row in rows} == {'original', 'order0', 'uncalibrated_majority', 'calibrated_majority'}
        assert all(row['n'] == 680 and 0 <= row['correct'] <= 680 for row in rows)
    r2_controls = heads['r2_constant_control']['rows']
    assert len(r2_controls) == 7
    for row in r2_controls:
        assert row['n'] == 79 and row['covered_n'] == 55 and row['uncovered_n'] == 24
        assert row['remaining_support_n'] == 9 and row['covered_none_n'] == 46
        assert row['constant_remaining_support_correct'] == 0
        assert row['head_correct'] == int(head_csv['R2', row['method']]['head_correct'])
    assert heads['overlap']['unique_union'] == 2941
    assert heads['overlap']['R1_intersect_R3'] == 733
    return baseline, heads, category_rows, {
        'input_hashes_verified': len(manifest['inputs']),
        'baseline_values_verified': baseline_checks, 'head_before_after_pairs_verified': head_checks,
        'head_integer_counts_verified': head_checks * 2,
        'r3_control_cells_verified': 28, 'r2_control_rows_verified': 7,
        'new_model_calls': 0, 'new_grading_calls': 0, 'new_native_scoring': 0,
    }


def write_tables(output_dir, baseline, heads, rows):
    table_dir = output_dir / 'tables'
    table_dir.mkdir(parents=True, exist_ok=True)
    line = r' \\'
    lines = [r'% Generated by scripts/build_scope_figures_tables.py; percentages.',
             r'\begin{table}[tb]', r'\centering', r'\small',
             r'\setlength{\tabcolsep}{3.5pt}',
             r'\caption{Formal v5 results for seven system configurations spanning six method families. Values are percentages of native unit scores. ALL uses 6,104 unique units; category sets overlap. Each configuration covers 13,905 inputs. L: Llama-3.1-8B-Instruct; Q: Qwen3-8B. M4 uses the repaired structured output; M5 retains its original output configuration. Corpora, retrieval procedures, and inference budgets also differ, so these are descriptive system comparisons.}',
             r'\label{tab:seven-baselines}',
             r'\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}llrrrrrr@{}}',
             r'\toprule', 'System & LM & ALL & R1 & R2 & R3 & R4 & R5' + line,
             r' & & (6,104) & (2,866) & (79) & (733) & (13) & (3,600)' + line,
             r'\midrule']
    for method in METHODS:
        vals = [f'{float(rows[category][method]):.2f}' for category in CATEGORIES]
        lines.append(f'{method} {NAMES[method]} & {BACKBONES[method]} & ' + ' & '.join(vals) + line)
    lines += [r'\bottomrule', r'\end{tabular*}', r'\end{table}', '']
    (table_dir / 'seven_baselines.tex').write_text('\n'.join(lines))
    per_category = {c: {r['method']: r for r in heads['verified_results'][c]} for c in ['R1', 'R2', 'R3']}
    lines = [r'% Generated from existing archived head outcomes; correct counts.',
             r'\begin{table}[tb]', r'\centering', r'\small',
             r'\caption{Archived original $\rightarrow$ head correct counts on R1--R3 for all seven configurations. The head combines candidate re-decision with rule support and preserves original answers outside coverage. These are analyses of exposed development data, using saved method-context decisions and shared backbone-level rule facts; they are not seven new upstream pipeline reruns. R3 is contained in R1; the three sets contain 2,941 distinct units.}',
             r'\label{tab:seven-heads}',
             r'\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lrrr@{}}',
             r'\toprule', r'System & R1 ($n=2{,}866$) & R2 ($n=79$) & R3 ($n=733$)' + line,
             r'\midrule']
    for method in METHODS:
        cells = [f"${per_category[c][method]['baseline_correct']:,} \\rightarrow {per_category[c][method]['head_correct']:,}$" for c in ['R1','R2','R3']]
        lines.append(f'{method} {NAMES[method]} & ' + ' & '.join(cells) + line)
    lines += [r'\bottomrule', r'\end{tabular*}', r'\end{table}', '']
    (table_dir / 'seven_heads.tex').write_text('\n'.join(lines))
    r3 = {(r['method'],r['variant']):r['correct'] for r in heads['r3_diagnosis_controls']}
    r2 = {r['method']:r for r in heads['r2_constant_control']['rows']}
    lines = [r'% Generated from archived controls; all cells are correct counts.',
             r'\begin{table}[tb]', r'\centering', r'\small',
             r'\caption{Controls expose limits of attributing the head gains. (a) R3 diagnosis subset ($n=680$): original, one catalog order (order 0), majority across catalog orders without calibration, and calibrated majority. Calibration does not improve every system. (b) R2 ($n=79$): the same-coverage None control predicts None on 55 covered inputs and preserves 24 original answers. Its higher aggregate score reflects 46 covered None targets; it misses all nine covered cases with remaining support. The last two columns isolate these nine cases.}',
             r'\label{tab:head-controls}',
             r'\textbf{(a) R3: correct out of 680}\par\smallskip',
             r'\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lrrrr@{}}',
             r'\toprule', r'System & Original & Order 0 & Majority & Calibrated' + line, r'\midrule']
    for method in METHODS:
        vals = [str(r3[method,v]) for v in ['original','order0','uncalibrated_majority','calibrated_majority']]
        lines.append(f'{method} {NAMES[method]} & ' + ' & '.join(vals) + line)
    lines += [r'\bottomrule',r'\end{tabular*}', r'\medskip',
              r'\textbf{(b) R2: aggregate and remaining-support subset}\par\smallskip',
              r'\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lrrrr@{}}',
              r'\toprule', r'System & Head /79 & None /79 & Head /9 & None /9' + line, r'\midrule']
    for method in METHODS:
        row = r2[method]
        vals = [str(row[k]) for k in ['head_correct','same_coverage_none_correct','head_remaining_support_correct','constant_remaining_support_correct']]
        lines.append(f'{method} {NAMES[method]} & ' + ' & '.join(vals) + line)
    lines += [r'\bottomrule',r'\end{tabular*}',r'\end{table}','']
    (table_dir / 'head_controls.tex').write_text('\n'.join(lines))


def write_figure(output_dir, heads):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size': 10, 'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.8), sharey=True)
    for ax, category in zip(axes, ['R1', 'R2', 'R3']):
        rows = {r['method']:r for r in heads['verified_results'][category]}
        for i, method in enumerate(METHODS):
            a,b = rows[method]['baseline_pct'],rows[method]['head_pct']
            ax.plot([a,b], [i,i], color='#aab5c2', linewidth=2.3, zorder=1)
            ax.scatter(a,i,color='#354a62',s=33,label='Original' if i == 0 else None,zorder=3)
            ax.scatter(b,i,color='#d16a27',marker='D',s=30,label='Head' if i == 0 else None,zorder=3)
        ax.set_title(f'{category}  (n = {DENOMINATORS[category]:,})',fontweight='bold',pad=12)
        ax.set_xlim(0,70)
        ax.set_xticks([0,20,40,60])
        ax.xaxis.set_major_formatter(PercentFormatter(100,decimals=0))
        ax.set_xlabel('Correct units (%)')
        ax.grid(axis='x',color='#e6e9ed',linewidth=.8)
        ax.set_axisbelow(True)
        for spine in ['top','right','left']:
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_color('#aab5c2')
        ax.tick_params(axis='y',length=0,pad=9)
    axes[0].set_yticks(range(7),[DISPLAY[m] for m in METHODS])
    axes[0].invert_yaxis()
    axes[0].set_ylim(6.5,-0.5)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.59,.98),ncol=2,frameon=False)
    fig.text(.5,.03,'Exposed development data. R3 is contained in R1; R1–R3 overlap (2,941 distinct units).',
             ha='center',fontsize=9,color='#4a4a4a')
    fig.subplots_adjust(left=.21,right=.985,bottom=.19,top=.83,wspace=.16)
    figure_dir = output_dir / 'figures'
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_dir/'seven_system_heads.pdf',metadata={'Title':'Seven-system archived head comparisons','CreationDate':None,'ModDate':None})
    fig.savefig(figure_dir/'seven_system_heads.png',dpi=200)
    plt.close(fig)


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,default=root/'inputs')
    parser.add_argument('--manifest',type=Path,default=root/'input_manifest.json')
    parser.add_argument('--output-dir',type=Path,default=root/'generated')
    parser.add_argument('--receipt',type=Path,default=root/'scope_build_receipt.json')
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    baseline,heads,rows,checks=validate(args.input_dir,args.manifest)
    outputs=[]
    if not args.check_only:
        write_tables(args.output_dir,baseline,heads,rows)
        write_figure(args.output_dir,heads)
        for name in ['tables/seven_baselines.tex','tables/seven_heads.tex','tables/head_controls.tex',
                     'figures/seven_system_heads.pdf','figures/seven_system_heads.png']:
            path=args.output_dir/name
            outputs.append({'path':str(path.resolve()),'bytes':path.stat().st_size,'sha256':sha256(path)})
    receipt={'created_at':datetime.now(timezone.utc).isoformat(),'passed':True,
             'mode':'check-only' if args.check_only else 'build','checks':checks,
             'input_dir':str(args.input_dir.resolve()),'manifest_sha256':sha256(args.manifest),
             'script_sha256':sha256(Path(__file__)),'outputs':outputs}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    main()
