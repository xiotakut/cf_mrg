#!/usr/bin/env python3
"""Rebuild paper-story assets from frozen, audited summaries; no inference/grading.

Usage from any working directory:
  /path/to/MedRGAG/.venv/bin/python /path/to/build_story_assets.py
  /path/to/MedRGAG/.venv/bin/python /path/to/build_story_assets.py --check-only

Use --freeze-inputs only to explicitly refresh the two audited input snapshots.
Custom --input-dir and --output-dir make the package portable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUT_NAMES = ("five_agent_framework_audit.json", "benchmark_contribution_audit.json")
CATEGORIES = ("ALL", "R1", "R2", "R3", "R4", "R5")
METHOD_NAMES = {
    "M0": "Direct", "M2": "MedRGAG", "M3": "MA-RAG", "M4": "MedRAG",
    "M5": "MedRAG", "M6": "MedGENIE", "M7": "TC-RAG",
}
SOURCE_NAMES = {
    "M01": "MedEinst", "M02": "MedPIC-Bench", "M06": "HIV causal scenarios",
    "M10": "CPV-MedQA", "M11": "Counterfactual Cultural Cues",
    "M12": "FairMedQA/AMQA", "M14": "DiversityMedQA", "M17": "MedPerturb",
    "M20": "MedCounterFact", "M22": "MedRGB", "M23": "BioRAB",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def freeze_inputs(input_dir: Path, source_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name in INPUT_NAMES:
        source = (source_dir / name).resolve()
        target = input_dir / name
        shutil.copyfile(source, target)
        records.append({"file": name, "sha256": sha256(target), "bytes": target.stat().st_size,
                        "source_path": str(source), "source_sha256": sha256(source)})
    write_json(input_dir / "manifest.json", {
        "schema_version": 1,
        "purpose": "Frozen audited metadata only; no raw patient text, inference or grading.",
        "files": records,
    })


def validate_inputs(input_dir: Path):
    manifest = read_json(input_dir / "manifest.json")
    by_name = {row["file"]: row for row in manifest["files"]}
    if set(by_name) != set(INPUT_NAMES):
        raise ValueError("Input manifest must contain exactly the two audited summaries")
    for name in INPUT_NAMES:
        p = input_dir / name
        if sha256(p) != by_name[name]["sha256"] or p.stat().st_size != by_name[name]["bytes"]:
            raise ValueError(f"Frozen input changed: {name}")
    return [read_json(input_dir / name) for name in INPUT_NAMES]


def backbone_name(value: str) -> str:
    return "Llama" if "Llama" in value else "Qwen"


def build_rows(framework, benchmark):
    systems = []
    for row in framework["primary_main_table"]["rows"]:
        baseline = row["kind"] == "formal_baseline"
        method = row["system"].split()[0] if baseline else row["system"].split("(")[1].rstrip(")")
        systems.append({"configuration": method if baseline else f"CF-MoA-B-{method}",
                        "system": METHOD_NAMES[method] if baseline else "CF-MoA (B)",
                        "backbone": backbone_name(row["backbone"]),
                        "unique_inputs": row["unique_inputs"],
                        "ALL_units": row["native_ALL_units"],
                        **{f"{cat}_percent": row["percent"][cat] for cat in CATEGORIES}})
    pairs = []
    for row in framework["strong_system_evidence"]["paired_counts"]:
        for arm in ("C0", "B"):
            pairs.append({"configuration": row["method"],
                          "backbone": "Llama" if row["method"] == "M4" else "Qwen",
                          "system": "MedRAG (C0)" if arm == "C0" else "CF-MoA (B)",
                          "arm": arm,
                          **{key: value for metric in ("maintain", "respond") for key, value in (
                              (metric + "_correct", row[metric + "_" + arm]),
                              (metric + "_pairs", row[metric + "_n"]),
                              (metric + "_percent", 100 * row[metric + "_" + arm] / row[metric + "_n"]))}})
    sources = [{"source_id": row["resource_id"], "source": SOURCE_NAMES[row["resource_id"]],
                "units": int(row["adopted_units"]), "target_judgments": int(row["adopted_targets"]),
                **{cat: int(row[cat]) for cat in CATEGORIES[1:]}}
               for row in benchmark["tables"]["v5_sources"]]
    assert len(systems) == 9 and len(pairs) == 4 and len(sources) == 11
    assert all(row["unique_inputs"] == 13905 and row["ALL_units"] == 6104 for row in systems)
    assert sum(row["units"] for row in sources) == 6104
    assert sum(row["target_judgments"] for row in sources) == 13000
    assert [sum(row[cat] for row in sources) for cat in CATEGORIES[1:]] == [2866, 79, 733, 13, 3600]
    return systems, pairs, sources


def csv_text(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def latex_escape(text: str) -> str:
    return str(text).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def latex_table(caption, label, spec, headings, rows, notes):
    lines = ["% Generated by scripts/build_story_assets.py from frozen audited summaries.",
             r"\begin{table}[tb]", r"\centering", r"\small",
             r"\setlength{\tabcolsep}{4pt}", r"\caption{" + caption + "}",
             r"\label{" + label + "}", r"\resizebox{\linewidth}{!}{%",
             r"\begin{tabular}{" + spec + "}", r"\toprule",
             " & ".join(headings) + r" \\", r"\midrule"]
    for row in rows:
        if row is None:
            lines.append(r"\midrule")
        else:
            lines.append(" & ".join(row) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}}", r"\par\smallskip",
              r"\begin{minipage}{\linewidth}\footnotesize " + notes + r"\end{minipage}",
              r"\end{table}", ""]
    return "\n".join(lines)


def text_assets(systems, pairs, sources):
    sysrows = []
    for idx, row in enumerate(systems):
        if idx == 7:
            sysrows.append(None)
        name = latex_escape(row["system"])
        if idx >= 7:
            name = r"\textbf{" + name + "}"
        sysrows.append([name, row["backbone"], *[f"{row[cat + '_percent']:.2f}" for cat in CATEGORIES]])
    pairrows = []
    for row in pairs:
        pairrows.append([row["backbone"], latex_escape(row["system"]),
                         *[f"{row[metric + '_correct']:,}/{row[metric + '_pairs']:,} ({row[metric + '_percent']:.2f}\\%)"
                           for metric in ("maintain", "respond")]])
    sourcerows = [[r["source_id"], latex_escape(r["source"]),
                   *[f"{r[k]:,}" for k in ("units", "target_judgments", *CATEGORIES[1:])]] for r in sources]
    sourcerows += [None, [r"\textbf{Total}", "", *[f"{sum(r[k] for r in sources):,}"
                                                   for k in ("units", "target_judgments", *CATEGORIES[1:])]]]
    return {
        "system_comparison.csv": csv_text(systems),
        "paired_behavior.csv": csv_text(pairs),
        "benchmark_composition.csv": csv_text(sources),
        "system_comparison.tex": latex_table(
            "Complete v5 comparison of seven baseline configurations and two CF-MoA core instantiations. Scores are percentages of native-unit means.",
            "tab:story-systems", "llrrrrrr", ["System", "Backbone", *CATEGORIES], sysrows,
            "Each row covers 13,905 inputs. ALL uses 6,104 non-reference units; R1--R5 use 2,866, 79, 733, 13, and 3,600 units. "
            "Categories overlap. These are complete system comparisons with different resources and inference budgets. "
            "Llama: Llama-3.1-8B-Instruct; Qwen: Qwen3-8B. The two MedRAG baselines retain their selected output configurations. "
            "All values describe the exposed development benchmark."),
        "paired_behavior.tex": latex_table(
            "Maintaining and changing answers appropriately: both endpoints must be correct.",
            "tab:story-pairs", "llll", ["Backbone", "System", "Maintain", "Respond"], pairrows,
            "Counts and percentages use 6,838 maintain pairs and 1,780 respond pairs. "
            "Endpoints are inferred independently; pair relations are used only for evaluation. "
            "Pairs may share endpoints or families. All planned pairs remain in the denominator."),
        "benchmark_composition.tex": latex_table(
            "Complete v5 benchmark composition by source. R1--R5 columns count units bearing each category label.",
            "tab:story-benchmark", "llrrrrrrr", ["ID", "Source", "Units", "Judgments", *CATEGORIES[1:]], sourcerows,
            "The benchmark contains 6,104 unique units and 13,000 target judgments. "
            "Category memberships overlap and must not be summed as independent units. "
            "Target judgments are distinct from the 13,905 inference inputs and 15,616 native scoring mappings per system. "
            "The separate supplied-model A4 panel is not added to this table."),
    }


def init_plotting():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "pdf.fonttype": 42, "ps.fonttype": 42,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.labelcolor": "#263445",
                         "text.color": "#263445", "axes.edgecolor": "#AEB8C1",
                         "savefig.facecolor": "white"})
    return plt


def save_figure(fig, stem: Path):
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight",
                metadata={"Creator": "build_story_assets.py", "CreationDate": None, "ModDate": None})
    fig.savefig(stem.with_suffix(".png"), bbox_inches="tight", dpi=240,
                metadata={"Software": "build_story_assets.py"})


def plot_system_results(systems, pairs, output_dir):
    plt = init_plotting()
    import numpy as np
    fig = plt.figure(figsize=(12.8, 6.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.44, 1], hspace=0.64, wspace=0.42,
                          left=0.18, right=0.97, top=0.88, bottom=0.16)
    ax = fig.add_subplot(gs[:, 0])
    base_color, B_color = "#91A5B8", "#147D82"
    scores = [r["ALL_percent"] for r in systems]
    ax.barh(range(9), scores, color=[base_color] * 7 + [B_color] * 2, height=0.67)
    ax.set_yticks(range(9), [r["system"] + " / " + r["backbone"] for r in systems])
    ax.invert_yaxis()
    ax.set_xlim(0, 70)
    ax.set_xlabel("Native-unit mean (%)")
    ax.set_title("(a) Complete v5: all nine systems", loc="left", pad=25, fontsize=11)
    ax.text(0, 1.015, "6,104 non-reference units per system", transform=ax.transAxes,
            fontsize=9, color="#5D6B78")
    ax.axhline(6.5, color="#C6CDD4", lw=0.8)
    for y, score in enumerate(scores):
        ax.text(score + 0.7, y, f"{score:.2f}", va="center", fontsize=9)
    ax.xaxis.grid(True, color="#E6EBEF", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    for idx, metric in enumerate(("maintain", "respond")):
        ax2 = fig.add_subplot(gs[idx, 1])
        denom = pairs[0][metric + "_pairs"]
        ax2.set_title(f"({chr(98 + idx)}) {metric.capitalize()}: both correct", loc="left", pad=25, fontsize=11)
        ax2.text(0, 1.04, f"{denom:,} pairs per system", transform=ax2.transAxes, fontsize=9, color="#5D6B78")
        y = np.arange(2)
        for offset, arm, color, label in [(-0.18, "C0", base_color, "MedRAG (C0)"),
                                           (0.18, "B", B_color, "CF-MoA (B)")]:
            values = [next(r[metric + "_percent"] for r in pairs if r["backbone"] == b and r["arm"] == arm)
                      for b in ("Llama", "Qwen")]
            ax2.barh(y + offset, values, height=0.31, color=color, label=label)
            for yy, value in zip(y + offset, values):
                ax2.text(value + (0.7 if metric == "maintain" else 0.3), yy,
                         f"{value:.2f}", va="center", fontsize=9)
        ax2.set_yticks(y, ["Llama", "Qwen"])
        ax2.invert_yaxis()
        ax2.set_xlim(0, 80 if metric == "maintain" else 26)
        ax2.set_xlabel("Pair both-correct rate (%)")
        ax2.xaxis.grid(True, color="#E6EBEF", linewidth=0.6)
        ax2.set_axisbelow(True)
        ax2.tick_params(axis="y", length=0)
        ax2.spines["left"].set_visible(False)
    handles, labels = ax2.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.65, 0.065),
               ncol=2, frameon=False, fontsize=9)
    fig.text(0.18, 0.02, "Same complete benchmark and native scoring; resources differ. All results are exposed development evaluations.",
             fontsize=8.4, color="#5D6B78")
    save_figure(fig, output_dir / "system_results")
    plt.close(fig)


def plot_story_map(benchmark, output_dir):
    plt = init_plotting()
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig, ax = plt.subplots(figsize=(13.2, 7.0))
    fig.subplots_adjust(left=0.015, right=0.985, top=0.97, bottom=0.05)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    teal, navy, grey = "#147D82", "#263445", "#70818F"

    def box(x, y, w, h, title, body="", color="#EDF4F7", edge="#B1C5D0", dashed=False):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.007,rounding_size=0.014",
                          linewidth=1.1, facecolor=color, edgecolor=edge,
                          linestyle="--" if dashed else "-")
        ax.add_patch(p)
        if body:
            ax.text(x + w / 2, y + h * 0.71, title, ha="center", va="center", fontsize=10.1,
                    fontweight="bold", color=navy)
            ax.text(x + w / 2, y + h * 0.32, body, ha="center", va="center", fontsize=9.0,
                    linespacing=1.35, color=navy)
        else:
            ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=10.2, fontweight="bold")

    def arrow(start, end, color=grey):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11,
                                    lw=1.15, color=color, shrinkA=2, shrinkB=2))

    top_y, top_h, width = 0.80, 0.155, 0.218
    boxes = [
        (0.01, "Source landscape", f"{benchmark['counts']['catalog_sources']} resources catalogued\nprovenance and eligibility"),
        (0.263, "Reasoning taxonomy", "R1–R5 target-level labels\noverlapping reasoning relations"),
        (0.516, "Qualified benchmark", "11 sources · 6,104 units\n13,000 target judgments"),
        (0.769, "Seven-system comparison", "6 families · 2 backbones\nlocate capability gaps"),
    ]
    for x, title, body in boxes:
        box(x, top_y, width, top_h, title, body)
    for x1, x2 in zip([b[0] for b in boxes], [b[0] for b in boxes][1:]):
        arrow((x1 + width + 0.002, top_y + top_h / 2), (x2 - 0.004, top_y + top_h / 2))
    arrow((0.878, 0.79), (0.878, 0.69), teal)
    ax.text(0.5, 0.708, "CF-MoA: five operation roles, selected by visible capability", ha="center",
            fontsize=13, fontweight="bold", color=teal)
    ax.text(0.5, 0.662, "The adopted core B uses one eligible branch per input; A1 and A2 share one execution.",
            ha="center", fontsize=9.6, color=grey)
    box(0.018, 0.32, 0.20, 0.17, "Capability router", "current legal input\noriginal answer / context", color="#E9F3F0", edge="#69A39D")
    arrow((0.221, 0.405), (0.288, 0.405), teal)
    ax.plot([0.29, 0.29], [0.16, 0.56], color=teal, linewidth=1.2)
    branch_y = [0.56, 0.43, 0.30, 0.17]
    branch_data = [
        ("A1 Establish + A2 Withdraw", "shared support kernel → original set assembly", False),
        ("A3 Compare candidates", "public catalog → native diagnostic decision", False),
        ("A4 Execute consequences", "supplied model · separate 288-task panel", True),
        ("A5 Robust readout (F)", "NLI paths / native-answer sampling", False),
    ]
    for yy, (title, body, dashed) in zip(branch_y, branch_data):
        arrow((0.291, yy), (0.338, yy), teal)
        box(0.343, yy - 0.048, 0.379, 0.096, title, body,
            color="#F3EEF8" if dashed else "#E9F3F0", edge="#9F83BC" if dashed else "#69A39D", dashed=dashed)
        arrow((0.725, yy), (0.786, yy), "#9F83BC" if dashed else teal)
    box(0.790, 0.12, 0.195, 0.49, "Native output", "preserve adopted\ncomponent decision\n\nno global\nLLM rewriting", color="#F0F3F6", edge="#A8B7C5")
    # The fallback is a separate legal route, not an extra agent activation.
    ax.text(0.118, 0.259, "No supported branch:\noriginal native fallback", ha="center", va="center",
            fontsize=8.8, color=grey)
    ax.text(0.015, 0.045, "R labels are used for evaluation, not online routing. Clinical v5 activates rules, catalog, F or passthrough; A4 has zero clinical-v5 coverage.",
            fontsize=8.6, color=grey)
    ax.text(0.015, 0.008, "The A4 panel uses 24 supplied-model profiles × 12 questions per backbone and is reported separately from the benchmark.",
            fontsize=8.6, color=grey)
    save_figure(fig, output_dir / "story_map")
    plt.close(fig)


def check_outputs(input_dir, output_dir, expected_text):
    build = read_json(output_dir / "build_manifest.json")
    if build["input_manifest_sha256"] != sha256(input_dir / "manifest.json"):
        raise ValueError("Generated assets belong to a different input freeze")
    for name, expected in expected_text.items():
        if (output_dir / name).read_text(encoding="utf-8") != expected:
            raise ValueError(f"Generated table disagrees with frozen summaries: {name}")
    for row in build["outputs"]:
        if sha256(output_dir / row["file"]) != row["sha256"]:
            raise ValueError(f"Generated artifact changed: {row['file']}")
    return build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "inputs")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "generated")
    parser.add_argument("--source-dir", type=Path, default=ROOT,
                        help="Audits to copy only when --freeze-inputs is explicitly given")
    parser.add_argument("--freeze-inputs", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only and args.freeze_inputs:
        parser.error("--check-only cannot change the frozen inputs")
    if args.freeze_inputs:
        freeze_inputs(args.input_dir, args.source_dir)
    framework, benchmark = validate_inputs(args.input_dir)
    systems, pairs, sources = build_rows(framework, benchmark)
    expected = text_assets(systems, pairs, sources)
    if args.check_only:
        build = check_outputs(args.input_dir, args.output_dir, expected)
        print(json.dumps({"status": "verified", "tables": 3, "figures": 2,
                          "system_rows": 9, "pair_rows": 4, "source_rows": 11,
                          "outputs": len(build["outputs"]), "new_model_calls": 0, "new_grading_calls": 0}))
        return
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, text in expected.items():
        (args.output_dir / name).write_text(text, encoding="utf-8")
    plot_story_map(benchmark, args.output_dir)
    plot_system_results(systems, pairs, args.output_dir)
    names = [*expected, "story_map.pdf", "story_map.png", "system_results.pdf", "system_results.png"]
    import matplotlib
    write_json(args.output_dir / "build_manifest.json", {
        "schema_version": 1, "script_sha256": sha256(Path(__file__)),
        "input_manifest_sha256": sha256(args.input_dir / "manifest.json"),
        "python_version": sys.version.split()[0], "matplotlib_version": matplotlib.__version__,
        "metrics": "stored native-unit means and stored paired both-correct counts; no rescoring",
        "new_model_calls": 0, "new_grading_calls": 0,
        "outputs": [{"file": name, "sha256": sha256(args.output_dir / name),
                     "bytes": (args.output_dir / name).stat().st_size} for name in names],
    })
    check_outputs(args.input_dir, args.output_dir, expected)
    print(json.dumps({"status": "generated_and_verified", "output_dir": str(args.output_dir.resolve()),
                      "tables": 3, "figures": 2, "outputs": len(names)}))


if __name__ == "__main__":
    main()
