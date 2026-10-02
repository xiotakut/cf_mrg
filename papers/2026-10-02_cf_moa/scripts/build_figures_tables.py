#!/usr/bin/env python3
"""Rebuild paper figures/tables from saved CF-MoA scores; never run a model/grader.

Python >=3.10; matplotlib, numpy, pandas. --check-only writes only its receipt.
Use --raw-root for an independent aggregation of the optional original JSONL.gz
records. Without it, checks use the small, hash-locked inputs shipped here.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import platform
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
ARMS = ("original_C0", "strong_B", "candidate_only", "candidate_with_rationales",
        "pool_old_plus_three", "joint_selector")
CODE = dict(zip(ARMS, ("C0", "B", "C2", "C3", "C4", "C5")))
LABEL = dict(zip(ARMS, ("Original system", "Adopted core", "Candidate-only",
                       "With rationales", "Pool + three", "Joint selector")))
MODELS = ("M4", "M5")
MODEL_LABEL = {"M4": "M4: Llama-3.1-8B", "M5": "M5: Qwen3-8B"}
COLORS = ("#9299A3", "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")


def close(a, b):
    assert math.isclose(float(a), float(b), abs_tol=1e-11, rel_tol=1e-11), (a, b)


def index(rows, fields):
    result = {tuple(r[f] for f in fields): r for r in rows}
    assert len(result) == len(rows), ("duplicate keys", fields)
    return result


def check_inputs(input_root):
    manifest = load(input_root / "manifest.json")
    data = {}
    for name, record in manifest["files"].items():
        file = input_root / name
        assert sha(file) == record["sha256"], ("input hash mismatch", file)
        assert file.stat().st_size == record["bytes"]
        data[name.removesuffix(".json")] = load(file)
    cat = index(data["all_category_results"], ("method", "arm", "category"))
    src = index(data["all_source_results"], ("method", "arm", "source"))
    fmt = index(data["format_input_results"], ("method", "arm", "answer_format"))
    pairs = index(data["pair_summary"], ("method", "arm", "relation"))
    summary = index(data["validation_receipt"]["checks"], ("method", "arm"))
    cost = index(data["per_method_costs"]["rows"], ("method", "arm"))
    assert [len(cat), len(src), len(fmt), len(pairs), len(summary), len(cost)] == [72,132,60,24,12,12]
    assert len(data["family_effect_intervals"]) == 36
    expected_units = {"ALL":6104,"R1":2866,"R2":79,"R3":733,"R4":13,"R5":3600}
    for m in MODELS:
        for a in ARMS:
            r = summary[(m,a)]
            assert (r["inputs"],r["native_mappings"],r["native_ALL_units"],r["pending_inputs"]) == (13905,15616,6104,0)
            for k,n in expected_units.items():
                assert cat[(m,a,k)]["units"] == n
            assert cat[(m,a,"ALL")]["families"] == 4766
            ss = [r for (mm,aa,_),r in src.items() if (mm,aa)==(m,a)]
            ff = [r for (mm,aa,_),r in fmt.items() if (mm,aa)==(m,a)]
            assert len(ss)==11 and len(ff)==5
            assert sum(r["units"] for r in ss)==6104
            close(sum(r["units"]*r["mean_native_unit_score"] for r in ss)/6104,
                  cat[(m,a,"ALL")]["mean_native_unit_score"])
            assert sum(r["inputs"] for r in ff)==13905
            assert sum(r["correct"] for r in ff)==summary[(m,a)]["correct_inputs"]
            assert sum(r["unavailable"] for r in ff)==summary[(m,a)]["unavailable_inputs"]
            for f in ff:
                close(f["input_accuracy"],f["correct"]/f["inputs"])
            for rel,n in [("maintain",6838),("respond",1780)]:
                p=pairs[(m,a,rel)]
                assert p["pairs"]==p["completed_pairs"]==n
                close(p["full_both_correct_rate"],p["both_correct"]/n)
            assert cost[(m,a)]["inputs"] == cost[(m,a)]["terminal"] == 13905
            assert cost[(m,a)]["end_to_end_total"] is None
            if a != "original_C0":
                c=cost[(m,a)]["cost"]
                for unit in ["model_requests","input_tokens","output_tokens"]:
                    close(c["base_cost_once"][unit]["total"]+c["extra_cost"][unit]["total"],
                          c["method_attributed_cost"][unit]["total"])
                assert c["method_attributed_cost"]["model_seconds"]["total"] is None
                assert c["method_attributed_cost"]["model_seconds"]["unknown_rows"]==2503
    for r in data["family_effect_intervals"]:
        m,a,b=r["method"],r["candidate"],r["baseline"]
        if r["metric"]=="native_ALL":
            delta=(cat[(m,a,"ALL")]["mean_native_unit_score"]-cat[(m,b,"ALL")]["mean_native_unit_score"])*100
            assert (r["atoms"],r["families"])==(6104,4766)
        else:
            delta=(pairs[(m,a,r["metric"])]["full_both_correct_rate"]-pairs[(m,b,r["metric"])]["full_both_correct_rate"])*100
            assert r["atoms"]=={"maintain":6838,"respond":1780}[r["metric"]]
        close(delta,r["delta_pp"])
        assert r["resamples"]==5000 and r["seed"]==240924 and r["paired"]
        assert r["percentile_95_pp"][0] <= r["percentile_95_pp"][1]
    assert len(data["operation_ablations_reused"])==6
    for r in data["operation_ablations_reused"]:
        assert r["inputs"]==123
        close(r["native_ALL_mean"],r["correct"]/123)
        assert r["correct"]+r["incorrect"]+r["unavailable"]==123
    status=data["final_status"]
    assert status["independent"] is False and status["incremental_RCV_adopted_as_default"] is False
    assert status["denominators_each_model_arm"]==dict(inputs=13905,native_mappings=15616,
        ALL_units=6104,families=4766,maintain_pairs=6838,respond_pairs=1780)
    return data, manifest, dict(category_rows=72,source_rows=132,format_rows=60,
        paired_rows=24,contrast_rows=36,cost_rows=12,ablation_rows=6,
        all_denominators_valid=True,all_input_hashes_valid=True,
        all_summary_cross_checks_passed=True)


def verify_raw(raw_root, data):
    """Independently aggregate saved scores. No scoring function is imported."""
    expected_cat=index(data["all_category_results"],("method","arm","category"))
    expected_src=index(data["all_source_results"],("method","arm","source"))
    expected_fmt=index(data["format_input_results"],("method","arm","answer_format"))
    expected_pairs=index(data["pair_summary"],("method","arm","relation"))
    expected_summary=index(data["validation_receipt"]["checks"],("method","arm"))
    files=[]
    for m in MODELS:
        cats=defaultdict(list); families=defaultdict(set); sources=defaultdict(list)
        formats=defaultdict(lambda:[0,0,0]); inputs=defaultdict(lambda:[0,0,0,0]); pairs=defaultdict(lambda:[0,0])
        keys=set()
        for stem in ["native_units","per_input_status","pairs"]:
            p=raw_root/m.lower()/(stem+".jsonl.gz")
            before=sha(p)
            with gzip.open(p,"rt",encoding="utf-8") as f:
                for line in f:
                    r=json.loads(line); a=r["arm"]
                    assert a in ARMS and r["method"]==m
                    if stem=="native_units":
                        k=(stem,a,r["category"],r["unit_id"])
                        assert r["complete"] and r["score"] is not None
                        cats[(a,r["category"])].append(r["score"])
                        families[(a,r["category"])].add(r["family_id"])
                        if r["category"]=="ALL":sources[(a,r["source"])].append(r["score"])
                    elif stem=="per_input_status":
                        k=(stem,a,r["request_id"])
                        v=inputs[a]; v[0]+=1;v[1]+=int(r["correct"] is True);v[2]+=int(r["unavailable"]);v[3]+=r["native_mapping_count"]
                        v=formats[(a,r["answer_format"])];v[0]+=1;v[1]+=int(r["correct"] is True);v[2]+=int(r["unavailable"])
                    else:
                        k=(stem,a,r["pair_id"])
                        assert r["complete"]
                        v=pairs[(a,r["relation"])];v[0]+=1;v[1]+=int(r["both_correct"] is True)
                    assert k not in keys,("duplicate raw key",k)
                    keys.add(k)
            assert sha(p)==before
            files.append(dict(path=str(p),sha256=before,bytes=p.stat().st_size,unchanged=True))
        for (a,c),values in cats.items():
            ex=expected_cat[(m,a,c)]
            assert len(values)==ex["units"] and len(families[(a,c)])==ex["families"]
            close(math.fsum(values)/len(values),ex["mean_native_unit_score"])
        for (a,s),values in sources.items():
            ex=expected_src[(m,a,s)]
            assert len(values)==ex["units"]
            close(math.fsum(values)/len(values),ex["mean_native_unit_score"])
        for (a,f),values in formats.items():
            ex=expected_fmt[(m,a,f)]
            assert values==[ex["inputs"],ex["correct"],ex["unavailable"]]
        for a,values in inputs.items():
            ex=expected_summary[(m,a)]
            assert values==[13905,ex["correct_inputs"],ex["unavailable_inputs"],15616]
        for (a,rel),values in pairs.items():
            ex=expected_pairs[(m,a,rel)]
            assert values==[ex["pairs"],ex["both_correct"]]
        assert len(cats)==36 and len(sources)==66 and len(formats)==30 and len(pairs)==12
    return dict(status="passed",raw_root=str(raw_root),files=files,
                category_checks=72,source_checks=132,format_checks=60,pair_checks=24,
                method_arm_checks=12,duplicate_keys=0,model_calls=0,grader_calls=0)


def write_tables(data, out):
    import pandas as pd
    out.mkdir(parents=True,exist_ok=True)
    cat=index(data["all_category_results"],("method","arm","category"))
    checks=index(data["validation_receipt"]["checks"],("method","arm"))
    main=[]
    for m in MODELS:
        for a in ARMS:
            r=checks[(m,a)]
            main.append(dict(backbone=m,arm=CODE[a],method=LABEL[a],inputs=r["inputs"],
                correct=r["correct_inputs"],unavailable=r["unavailable_inputs"],
                native_mappings=r["native_mappings"],ALL_units=r["native_ALL_units"],
                ALL_percent=cat[(m,a,"ALL")]["mean_native_unit_score"]*100))
    contrasts=[dict(backbone=r["method"],metric=r["metric"],candidate=CODE[r["candidate"]],
        baseline=CODE[r["baseline"]],atoms=r["atoms"],families=r["families"],
        delta_pp=r["delta_pp"],CI_low_pp=r["percentile_95_pp"][0],
        CI_high_pp=r["percentile_95_pp"][1],resamples=r["resamples"],seed=r["seed"])
        for r in data["family_effect_intervals"]]
    costs=[]
    for r in data["per_method_costs"]["rows"]:
        c=r["cost"];t=c["method_attributed_cost"]
        costs.append(dict(backbone=r["method"],arm=CODE[r["arm"]],inputs=r["inputs"],
            base_requests=c.get("base_cost_once",{}).get("model_requests",{}).get("total"),
            extra_requests=c.get("extra_cost",{}).get("model_requests",{}).get("total"),
            attributed_requests=t["model_requests"]["total"],input_tokens=t["input_tokens"]["total"],
            output_tokens=t["output_tokens"]["total"],model_seconds_total=t["model_seconds"]["total"],
            model_seconds_known_subtotal=t["model_seconds"]["known_subtotal"],
            time_unknown_inputs=t["model_seconds"]["unknown_rows"],
            end_to_end_total=None,upstream_C0_cost="unknown"))
    tables={"main_results":main,"contrasts":contrasts,"sources":data["all_source_results"],
        "categories":data["all_category_results"],"formats":data["format_input_results"],
        "paired":data["pair_summary"],"costs":costs,"ablations":data["operation_ablations_reused"]}
    for name,rows in tables.items():
        frame=pd.DataFrame(rows)
        frame.to_csv(out/(name+".csv"),index=False,na_rep="unknown",float_format="%.12g")
    # Presentation-ready LaTeX; all CSVs retain the complete machine fields.
    maintex=pd.DataFrame(main)[["backbone","arm","correct","unavailable","ALL_percent"]]
    maintex.columns=["Backbone","Arm","Correct / 13,905","Unavailable","ALL (\\%)"]
    maintex.to_latex(out/"main_results.tex",index=False,escape=False,float_format="%.2f",
                    caption="Full development results; ALL averages 6,104 non-reference units.",label="tab:main_results")
    ctex=pd.DataFrame(contrasts)[["backbone","metric","candidate","baseline","delta_pp","CI_low_pp","CI_high_pp"]]
    ctex.columns=["Model","Metric","Arm","Reference","Delta (pp)","95% lower","95% upper"]
    ctex.to_latex(out/"contrasts.tex",index=False,longtable=True,escape=True,float_format="%.4f",
        caption="All paired family bootstrap contrasts (percentage points; 5,000 resamples).",label="tab:contrasts")
    for name,key,dim in [("sources","all_source_results","source"),("categories","all_category_results","category")]:
        rows=[]
        for m in MODELS:
            for d in sorted({r[dim] for r in data[key]}):
                rr={r["arm"]:r for r in data[key] if r["method"]==m and r[dim]==d}
                rows.append({"Backbone":m,dim:d,"Units":rr[ARMS[0]]["units"],
                             **{CODE[a]:100*rr[a]["mean_native_unit_score"] for a in ARMS}})
        pd.DataFrame(rows).to_latex(out/(name+".tex"),index=False,longtable=True,float_format="%.2f",
            caption=f"All {name}: native non-reference unit means (percent).",label=f"tab:{name}")
    rows=[]
    for m in MODELS:
        for f in sorted({r["answer_format"] for r in data["format_input_results"]}):
            rr={r["arm"]:r for r in data["format_input_results"] if r["method"]==m and r["answer_format"]==f}
            rows.append({"Backbone":m,"Format":f,"Inputs":rr[ARMS[0]]["inputs"],
                         **{CODE[a]:100*rr[a]["input_accuracy"] for a in ARMS}})
    pd.DataFrame(rows).to_latex(out/"formats.tex",index=False,longtable=True,float_format="%.2f",
        caption="All answer formats: input accuracy (percent), not native unit means.",label="tab:formats")
    for name,cols,headers,caption in [
        ("paired",["method","arm","relation","pairs","both_correct","full_both_correct_rate"],
         ["Model","Arm","Relation","Pairs","Both correct","Percent"],
         "Qualified paired outcomes; both endpoints must be correct. Rates are percentages."),
        ("costs",["backbone","arm","base_requests","extra_requests","attributed_requests","time_unknown_inputs"],
         ["Model","Arm","Base calls","Extra calls","Total calls","Unknown time rows"],
         "Head/readout request attribution. Historical upstream costs remain unknown."),
        ("ablations",["method","arm","inputs","correct","unavailable","native_ALL_mean"],
         ["Model","Operation","Inputs","Correct","Unavailable","ALL percent"],
         "Existing shared-rule operation ablations on 123 inputs. ALL is a percentage.")]:
        f=pd.DataFrame(tables[name])[cols]
        if "arm" in f:f["arm"]=f["arm"].replace(CODE)
        for col in ["full_both_correct_rate","native_ALL_mean"]:
            if col in f:f[col]=f[col]*100
        if name=="costs":
            for col in ["base_requests","extra_requests","attributed_requests"]:
                f[col]=f[col].map(lambda x:"unknown" if pd.isna(x) else str(int(x)))
        f.columns=headers
        f.to_latex(out/(name+".tex"),index=False,longtable=True,escape=True,na_rep="unknown",float_format="%.4f",
                   caption=caption,label=f"tab:{name}")
    return {name:len(rows) for name,rows in tables.items()}


def figures(data,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.titlesize":11,
        "axes.labelsize":10,"xtick.labelsize":9,"ytick.labelsize":9,"legend.fontsize":9,
        "axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42,
        "ps.fonttype":42,"savefig.dpi":300})
    out.mkdir(parents=True,exist_ok=True)
    cat=index(data["all_category_results"],("method","arm","category"))
    def score(m,a):return 100*cat[(m,a,"ALL")]["mean_native_unit_score"]
    def save(fig,name):
        fig.savefig(out/(name+".pdf"),bbox_inches="tight",metadata={"Title":name,"Creator":"CF-MoA saved-score renderer"})
        fig.savefig(out/(name+".png"),bbox_inches="tight",dpi=300)
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10.5,4),sharey=True)
    for ax,m in zip(axes,MODELS):
        vals=[score(m,a) for a in ARMS]
        bars=ax.bar(np.arange(6),vals,color=COLORS,width=.7)
        ax.bar_label(bars,fmt="%.2f",padding=3,fontsize=9)
        ax.set_xticks(np.arange(6),[CODE[a] for a in ARMS]);ax.set_title(MODEL_LABEL[m])
        ax.set_ylim(0,70);ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
    axes[0].set_ylabel("Native ALL unit mean (%)")
    fig.text(.5,.02,"C0: original | B: adopted core | C2: candidate-only | C3: with rationales | C4: pool + three | C5: joint selector",ha="center",fontsize=8)
    fig.subplots_adjust(bottom=.2,wspace=.12)
    save(fig,"main_results")
    fig,axes=plt.subplots(1,3,figsize=(12,3.7),sharey=True)
    for ax,metric,title in zip(axes,["native_ALL","maintain","respond"],["Native ALL","Maintain: both correct","Respond: both correct"]):
        for j,(m,b) in enumerate([(m,b) for m in MODELS for b in ["strong_B","candidate_only"]]):
            r=next(r for r in data["family_effect_intervals"] if r["method"]==m and r["metric"]==metric and r["candidate"]=="candidate_with_rationales" and r["baseline"]==b)
            lo,hi=r["percentile_95_pp"];y=3-j
            ax.errorbar(r["delta_pp"],y,xerr=[[r["delta_pp"]-lo],[hi-r["delta_pp"]]],fmt="o",capsize=4,color="#0072B2" if m=="M4" else "#D55E00",markersize=5)
        ax.axvline(0,color=".35",ls="--",lw=.8);ax.set_title(title);ax.set_xlabel("Difference (percentage points)");ax.grid(axis="x",alpha=.18)
        if metric=="respond":ax.set_xlim(-.6,.6)
    axes[0].set_yticks([3,2,1,0],["M4: C3 − B","M4: C3 − C2","M5: C3 − B","M5: C3 − C2"])
    axes[0].set_ylim(-.6,3.6)
    fig.text(.5,.015,"95% paired family bootstrap intervals; exposed development data; no selection or multiplicity adjustment",ha="center",fontsize=8)
    fig.tight_layout(rect=(0,.06,1,1));save(fig,"verification_forest")
    src=index(data["all_source_results"],("method","arm","source"))
    ids=sorted({r["source"] for r in data["all_source_results"]});yy=np.arange(len(ids))
    fig,ax=plt.subplots(figsize=(8.3,5.5))
    for m,off,color in [("M4",-.16,"#0072B2"),("M5",.16,"#D55E00")]:
        vals=[100*(src[(m,"candidate_with_rationales",s)]["mean_native_unit_score"]-src[(m,"strong_B",s)]["mean_native_unit_score"]) for s in ids]
        ax.scatter(vals,yy+off,label=MODEL_LABEL[m],color=color,s=35,zorder=3)
        ax.hlines(yy+off,0,vals,color=color,alpha=.55,lw=1.3)
    ax.set_yticks(yy,[f"{s} (n={src[('M4','strong_B',s)]['units']:,})" for s in ids]);ax.invert_yaxis()
    ax.axvline(0,color=".35",lw=.8);ax.set_xlabel("C3 − B native unit mean (percentage points)")
    ax.grid(axis="x",alpha=.2);ax.legend(loc="lower left",frameon=False)
    ax.set_title("All 11 sources; source IDs preserved")
    fig.tight_layout();save(fig,"source_heterogeneity")
    cost=index(data["per_method_costs"]["rows"],("method","arm"))
    fig,axes=plt.subplots(1,2,figsize=(10.6,4.3))
    offsets={"M4":{"strong_B":(5,-14),"candidate_only":(-22,-16),"candidate_with_rationales":(5,4),"pool_old_plus_three":(5,5),"joint_selector":(5,5)},
             "M5":{"strong_B":(5,-15),"candidate_only":(5,-16),"candidate_with_rationales":(5,4),"pool_old_plus_three":(5,4),"joint_selector":(5,-15)}}
    for ax,m in zip(axes,MODELS):
        for a,col in zip(ARMS[1:],COLORS[1:]):
            x=cost[(m,a)]["cost"]["method_attributed_cost"]["model_requests"]["total"]/1000
            ax.scatter(x,score(m,a),s=75,color=col,edgecolor="white",lw=.5,zorder=3)
            ax.annotate(CODE[a],(x,score(m,a)),xytext=offsets[m][a],textcoords="offset points",fontsize=9)
        ax.set_title(MODEL_LABEL[m]);ax.set_xlabel("Attributed head/readout requests (thousands)")
        ax.grid(alpha=.18);ax.margins(x=.15,y=.2)
    axes[0].set_ylabel("Native ALL unit mean (%)")
    fig.text(.5,.02,"Upstream C0/retrieval costs unknown for every arm; C0 has no known x-coordinate. Shared B counted once per method.",ha="center",fontsize=8)
    fig.tight_layout(rect=(0,.07,1,1));save(fig,"cost_quality")
    ab=index(data["operation_ablations_reused"],("method","arm"))
    aa=["strong_B","disable_add","disable_remove"]
    fig,axes=plt.subplots(1,2,figsize=(9.5,3.9),sharey=True)
    for ax,m in zip(axes,MODELS):
        vals=[100*ab[(m,a)]["native_ALL_mean"] for a in aa]
        bars=ax.bar(range(3),vals,color=[COLORS[1],COLORS[2],COLORS[5]],width=.6)
        ax.bar_label(bars,labels=[f"{ab[(m,a)]['correct']}/123\n({v:.1f}%)" for a,v in zip(aa,vals)],padding=3,fontsize=9)
        ax.set_xticks(range(3),["B","Disable add","Disable remove"]);ax.set_title(MODEL_LABEL[m]);ax.set_ylim(0,72)
        ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
    axes[0].set_ylabel("Native unit mean (%)")
    fig.text(.5,.015,"Existing shared-rule kernel ablations, 123 inputs per backbone; unavailable outputs retained",ha="center",fontsize=8)
    fig.tight_layout(rect=(0,.06,1,1));save(fig,"rule_ablations")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root",type=Path,default=PACKAGE/"inputs")
    parser.add_argument("--output-root",type=Path,default=PACKAGE)
    parser.add_argument("--raw-root",type=Path,help="Optional original full_v5 directory containing m4/ and m5/ saved JSONL.gz files")
    parser.add_argument("--check-only",action="store_true",help="Validate inputs and optional raw records; do not render figures/tables")
    parser.add_argument("--receipt",type=Path,help="Default: output-root/validation/build_receipt.json or check_receipt.json")
    args=parser.parse_args()
    started=datetime.now(timezone.utc).isoformat();tick=time.perf_counter()
    receipt=dict(started_at=started,command=sys.argv,python=sys.executable,python_version=platform.python_version(),
        script_sha256=sha(Path(__file__)),model_calls=0,grader_calls=0,score_changes=0,
        data_scope="previously exposed full-v5 development; no new confirmatory experiment",
        check_only=args.check_only,raw_validation=dict(status="not_requested"))
    path=args.receipt or args.output_root/"validation"/("check_receipt.json" if args.check_only else "build_receipt.json")
    try:
        data,manifest,checks=check_inputs(args.input_root)
        receipt["input_manifest_sha256"]=sha(args.input_root/"manifest.json")
        receipt["summary_checks"]=checks
        if args.raw_root:receipt["raw_validation"]=verify_raw(args.raw_root,data)
        if not args.check_only:
            import matplotlib,numpy,pandas
            receipt["dependencies"]={"matplotlib":matplotlib.__version__,"numpy":numpy.__version__,"pandas":pandas.__version__}
            receipt["table_rows"]=write_tables(data,args.output_root/"tables")
            figures(data,args.output_root/"figures")
            outputs=[]
            generated={"tables":(receipt["table_rows"].keys(),("csv","tex")),
                "figures":(("main_results","verification_forest","source_heterogeneity","cost_quality","rule_ablations"),("pdf","png"))}
            for folder,(stems,extensions) in generated.items():
                for stem in stems:
                    for ext in extensions:
                        f=args.output_root/folder/(stem+"."+ext)
                        outputs.append(dict(path=str(f.relative_to(args.output_root)),sha256=sha(f),bytes=f.stat().st_size))
            receipt["artifacts"]=outputs
            assert sum(r["path"].endswith(".pdf") for r in outputs)==5
            assert sum(r["path"].endswith(".png") for r in outputs)==5
        check_inputs(args.input_root)
        receipt["input_hashes_after_valid"]=True
        receipt["status"]="passed"
    except Exception as error:
        receipt["status"]="failed";receipt["error"]=repr(error)
        raise
    finally:
        receipt["elapsed_seconds"]=time.perf_counter()-tick
        receipt["finished_at"]=datetime.now(timezone.utc).isoformat()
        dump(path,receipt)
    print(json.dumps({"status":receipt["status"],"receipt":str(path),"elapsed_seconds":receipt["elapsed_seconds"]}))


if __name__=="__main__":
    main()
