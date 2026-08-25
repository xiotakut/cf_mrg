#!/usr/bin/env python3
"""Evaluate consolidated experiment predictions and write compact result files."""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


BASELINES = ("medrgag_proxy", "direct_rank", "structured_no_transition")
COMPARISONS = (
    ("full_transition", "medrgag_proxy"),
    ("full_transition", "direct_rank"),
    ("full_transition", "structured_no_transition"),
    ("full_transition", "effect_shuffle"),
    ("full_transition", "full_card_shuffle"),
    ("full_transition", "parametric_transition"),
    ("full_transition", "equal_token_reasoning"),
    ("full_transition", "transition_no_comparator"),
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{number}: expected JSON object")
        rows.append(row)
    return rows


def item_id(row: dict[str, Any]) -> str:
    value = row.get("id", row.get("item_id"))
    if value is None or str(value) == "":
        raise ValueError("prediction row is missing id/item_id")
    return str(value)


def validate(rows: list[dict[str, Any]]) -> None:
    seen = set()
    for row in rows:
        key = (item_id(row), str(row.get("method", "")))
        if not all(field in row for field in ("dataset", "method", "correct")):
            raise ValueError(f"{key}: dataset, method, and correct are required")
        if not isinstance(row["correct"], bool):
            raise ValueError(f"{key}: correct must be boolean")
        if key in seen:
            raise ValueError(f"duplicate id/method: {key}")
        seen.add(key)


def normalized(value: Any) -> Any:
    if isinstance(value, list):
        return sorted(normalized(item) for item in value)
    if isinstance(value, dict):
        for key in ("answer_choice", "answer_choices", "open_answer", "evidence_conditioned_answer", "answer", "selected", "reader_output"):
            if key in value:
                return normalized(value[key])
    return " ".join(unicodedata.normalize("NFKC", str(value)).strip().casefold().split()).rstrip(".,;:!?。；：，！？")


def canonical(value: Any, options: Any) -> Any:
    if isinstance(value, list):
        return sorted(canonical(item, options) for item in value)
    value = normalized(value)
    if isinstance(options, dict):
        mapping = {normalized(key): normalized(text) for key, text in options.items()}
        value = mapping.get(value, value)
    return "no difference" if value == "same" else value


def canonical_tokens(value: Any, options: Any = None) -> list[str]:
    if isinstance(value, dict):
        value = normalized(value)
    values = value if isinstance(value, list) else [value]
    return [canonical(item, options) for item in values if item is not None]


def answer_correct(predicted: Any, expected: Any, dataset: str, options: Any = None) -> bool:
    predicted_tokens, expected_tokens = canonical_tokens(predicted, options), canonical_tokens(expected, options)
    if dataset.casefold().replace("-", "").replace("_", "") in {"medpic", "medpicbench"}:
        return bool(expected_tokens) and set(predicted_tokens) == set(expected_tokens)
    return len(predicted_tokens) == len(expected_tokens) == 1 and predicted_tokens[0] == expected_tokens[0]


def join_gold(rows: list[dict[str, Any]], gold_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gold = {item_id(row): row for row in gold_rows}
    if len(gold) != len(gold_rows):
        raise ValueError("gold contains duplicate IDs")
    result = []
    for row in rows:
        identifier = item_id(row)
        if identifier not in gold:
            raise ValueError(f"prediction absent from gold: {identifier}")
        expected = gold[identifier]
        answer = expected.get("gold", expected.get("answer"))
        enriched = dict(row)
        enriched.update({key: value for key, value in expected.items() if key not in {"prediction", "method", "token_usage", "usage"}})
        enriched["id"] = identifier
        enriched["gold"] = answer
        predicted = row.get("prediction", row.get("reader_output"))
        enriched["prediction"] = predicted
        enriched["correct"] = answer_correct(predicted, answer, str(expected.get("dataset", row.get("dataset", ""))), expected.get("options"))
        reader = row.get("reader_output") if isinstance(row.get("reader_output"), dict) else predicted
        safety_gold = expected.get("real_world_safety_flag", expected.get("safety_flag"))
        if isinstance(reader, dict) and safety_gold is not None:
            enriched["safety_flag_correct"] = normalized(reader.get("real_world_safety_flag")) == normalized(safety_gold)
        result.append(enriched)
    return result


def cell(rows: list[dict[str, Any]]) -> dict[str, Any]:
    correct = sum(row["correct"] for row in rows)
    return {"n": len(rows), "correct": correct, "accuracy": correct / len(rows) if rows else None}


def token_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        per_row: dict[str, float] = defaultdict(float)
        usage = row.get("token_usage") or row.get("usage") or {}
        top_total = usage.get("total_tokens") if isinstance(usage, dict) else None

        def collect(value: Any, *, root: bool = False) -> None:
            if isinstance(value, dict):
                for key in ("prompt_tokens", "completion_tokens"):
                    if isinstance(value.get(key), (int, float)):
                        per_row[key] += float(value[key])
                children = [child for child in value.values() if isinstance(child, (dict, list))]
                if top_total is None and not children and isinstance(value.get("total_tokens"), (int, float)):
                    per_row["total_tokens"] += float(value["total_tokens"])
                for child in value.values():
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)
        collect(usage, root=True)
        if isinstance(top_total, (int, float)):
            per_row["total_tokens"] = float(top_total)
        elif "total_tokens" not in per_row and ("prompt_tokens" in per_row or "completion_tokens" in per_row):
            per_row["total_tokens"] = per_row["prompt_tokens"] + per_row["completion_tokens"]
        for key, value in per_row.items():
            values[key].append(value)
    return {
        key: {"total": sum(nums), "mean": statistics.fmean(nums), "n": len(nums)}
        for key, nums in sorted(values.items())
    }


def paired_bootstrap(a: dict[str, dict[str, Any]], b: dict[str, dict[str, Any]], seed: int, samples: int) -> dict[str, Any]:
    ids = sorted(key for key in a.keys() & b.keys() if b[key].get("shuffle_applicable") is not False)
    if not ids:
        return {"n": 0, "delta": None, "ci95": None}
    differences = [int(a[key]["correct"]) - int(b[key]["correct"]) for key in ids]
    delta = statistics.fmean(differences)
    rng = random.Random(seed)
    boot = sorted(statistics.fmean(rng.choice(differences) for _ in differences) for _ in range(samples))
    low = boot[int(0.025 * (samples - 1))]
    high = boot[int(0.975 * (samples - 1))]
    return {"n": len(ids), "delta": delta, "ci95": [low, high]}


def pair_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("pair_id") is not None:
            groups[(str(row["dataset"]), str(row["pair_id"]))].append(row)
    pairs = [values for values in groups.values() if len(values) == int(values[0].get("pair_size", 2))]
    result: dict[str, Any] = {
        "complete_pairs": len(pairs),
        "both_correct": cell([{"correct": all(row["correct"] for row in pair)} for pair in pairs]),
    }
    changed, invariant, persistence = [], [], []
    for pair in pairs:
        role = lambda row: str(row.get("pair_role", row.get("variant", row.get("role", row.get("condition", ""))))).casefold()
        ordered = sorted(pair, key=role)
        before = next((row for row in pair if role(row) in {"original", "control", "before", "pre"}), ordered[0])
        after = next((row for row in pair if role(row) in {"counterfactual", "trap", "edited", "after", "post"}), ordered[-1])
        should_change = after.get("answer_should_change", after.get("should_answer_change", before.get("answer_should_change", before.get("should_answer_change"))))
        if should_change is None and before.get("gold") is not None and after.get("gold") is not None:
            should_change = canonical_tokens(before["gold"], before.get("options")) != canonical_tokens(after["gold"], after.get("options"))
        did_change = canonical_tokens(before.get("prediction"), before.get("options")) != canonical_tokens(after.get("prediction"), after.get("options"))
        if should_change is True:
            changed.append({"correct": did_change and after["correct"], "raw_change": did_change})
        elif should_change is False:
            invariant.append({"correct": not did_change})
            if did_change:
                pass
        original_gold = before.get("gold")
        if original_gold is not None:
            persistence.append({"correct": canonical_tokens(after.get("prediction"), after.get("options")) == canonical_tokens(original_gold, before.get("options"))})
    if changed:
        result["correct_change"] = cell(changed)
        result["raw_change_rate"] = sum(row["raw_change"] for row in changed) / len(changed)
    if invariant:
        result["answer_invariance"] = cell(invariant)
        result["incorrect_change"] = cell([{"correct": not row["correct"]} for row in invariant])
    if persistence:
        result["old_answer_persistence"] = cell(persistence)
    return result


def bias_trap_rate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Persistence on trap rows, conditioned on a correct official-pair control."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("pair_id") is not None:
            groups[str(row["pair_id"])].append(row)
    outcomes = []
    for pair in groups.values():
        if len(pair) != int(pair[0].get("pair_size", 2)):
            continue
        role = lambda row: str(row.get("pair_role", row.get("variant", ""))).casefold()
        control = next((row for row in pair if role(row) == "control"), None)
        trap = next((row for row in pair if role(row) == "trap"), None)
        if control is None or trap is None or not control["correct"]:
            continue
        outcomes.append({
            "correct": canonical_tokens(trap.get("prediction"), trap.get("options"))
            == canonical_tokens(control.get("gold"), control.get("options")),
        })
    return cell(outcomes)


def optional_slices(method_rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    by_dataset = defaultdict(list)
    for row in method_rows:
        dataset = str(row["dataset"]).casefold().replace("-", "").replace("_", "")
        dataset = {"mcf": "medcounterfact", "medeinstbench": "medeinst", "medpicbench": "medpic", "clirbench": "clir"}.get(dataset, dataset)
        by_dataset[dataset].append(row)
    medpic = by_dataset.get("medpic", [])
    if medpic:
        labels = {
            "guideline_following": "guideline_following",
            "counterfactual": "counterfactual",
            "activation": "activation",
            "deactivation": "deactivation",
            "warning_persistence": "warning_persistence",
            "exact_set": "exact_set",
        }
        metrics = {"exact_set": cell(medpic)}
        for name, flag in labels.items():
            if name == "exact_set":
                continue
            selected = [row for row in medpic if flag in (row.get("metric_labels") or [])]
            if selected:
                metrics[name] = cell(selected)
        if metrics:
            result["medpic"] = metrics
    clir = by_dataset.get("clir", [])
    if clir:
        by_task = defaultdict(list)
        aliases = {
            "t6": "intervention_response", "t7": "threshold_forecasting",
            "t8": "forecast_interval", "t10": "next_action",
        }
        for row in clir:
            raw = str(row.get("task_family", row.get("variant", row.get("task_type", "unknown")))).lower()
            name = next((value for prefix, value in aliases.items() if raw.startswith(prefix)), raw)
            by_task[name].append(row)
        result["clir"] = {name: cell(values) for name, values in sorted(by_task.items())}
        timestamped = [row for row in clir if isinstance(row.get("evidence_timestamp_correct"), bool)]
        if timestamped:
            result["clir"]["evidence_timestamp"] = cell([{"correct": row["evidence_timestamp_correct"]} for row in timestamped])
    medeinst = by_dataset.get("medeinst", [])
    if medeinst:
        values = {}
        for role in ("control", "trap"):
            selected = [row for row in medeinst if row.get("pair_role", row.get("variant")) == role]
            if selected:
                values[role] = cell(selected)
        values.update(pair_metrics(medeinst))
        values["bias_trap_rate"] = bias_trap_rate(medeinst)
        result["medeinst"] = values
    mcf = by_dataset.get("medcounterfact", [])
    if mcf:
        values: dict[str, Any] = {"evidence_conditioned_answer": cell(mcf)}
        values.update(pair_metrics(mcf))
        safety = [row for row in mcf if isinstance(row.get("safety_flag_correct"), bool)]
        normalized = [row for row in mcf if isinstance(row.get("counterfactual_normalized"), bool)]
        contaminated = [row for row in mcf if isinstance(row.get("generated_context_contaminated"), bool)]
        if safety:
            values["real_world_safety_flag"] = cell([{"correct": row["safety_flag_correct"]} for row in safety])
        if normalized:
            values["counterfactual_normalization_rate"] = sum(row["counterfactual_normalized"] for row in normalized) / len(normalized)
        if contaminated:
            values["generated_context_contamination_rate"] = sum(row["generated_context_contaminated"] for row in contaminated) / len(contaminated)
        result["medcounterfact"] = values
    return result


def evaluate(rows: list[dict[str, Any]], seed: int = 13, bootstrap_samples: int = 1000) -> dict[str, Any]:
    validate(rows)
    by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_method[str(row["method"])].append(row)
    coverage = {method: {item_id(row) for row in values} for method, values in by_method.items()}
    if coverage and any(ids != next(iter(coverage.values())) for ids in coverage.values()):
        raise ValueError("all methods must cover identical item IDs")
    methods = {}
    indices = {}
    for method, values in sorted(by_method.items()):
        by_dataset, by_task = defaultdict(list), defaultdict(list)
        for row in values:
            by_dataset[str(row["dataset"])].append(row)
            by_task[str(row.get("task_type", "unknown"))].append(row)
        methods[method] = {
            "overall": cell(values),
            "parse_failures": sum(bool(row.get("parse_failure")) for row in values),
            "datasets": {key: cell(value) for key, value in sorted(by_dataset.items())},
            "task_types": {key: cell(value) for key, value in sorted(by_task.items())},
            "pairs": pair_metrics(values),
            "slices": optional_slices(values),
            "token_usage": token_metrics(values),
        }
        indices[method] = {item_id(row): row for row in values}
    pairs = list(COMPARISONS)
    pairs += [(method, baseline) for method in indices for baseline in BASELINES if method != baseline]
    comparisons = {}
    for method, baseline in dict.fromkeys(pairs):
        if method in indices and baseline in indices:
            comparisons[f"{method}-{baseline}"] = paired_bootstrap(indices[method], indices[baseline], seed, bootstrap_samples)
    def compact_metrics(selected: list[dict[str, Any]]) -> dict[str, Any]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in selected:
            grouped[str(row["method"])].append(row)
        indexed = {method: {item_id(row): row for row in values} for method, values in grouped.items()}
        comparison_metrics = {}
        for method, baseline in COMPARISONS:
            if method in indexed and baseline in indexed:
                comparison_metrics[f"{method}-{baseline}"] = paired_bootstrap(
                    indexed[method], indexed[baseline], seed, bootstrap_samples,
                )
        return {
            "methods": {method: cell(values) for method, values in sorted(grouped.items())},
            "comparisons": comparison_metrics,
        }

    failure_ids = {item_id(row) for row in rows if row.get("parse_failure")}
    complete_case = {}
    for method, baseline in COMPARISONS:
        if method not in indices or baseline not in indices:
            continue
        a = {
            identifier: row for identifier, row in indices[method].items()
            if not row.get("parse_failure") and not indices[baseline][identifier].get("parse_failure")
        }
        b = {identifier: indices[baseline][identifier] for identifier in a}
        complete_case[f"{method}-{baseline}"] = paired_bootstrap(a, b, seed, bootstrap_samples)
    sensitivity = {
        "exclude_medeinst": compact_metrics([row for row in rows if str(row["dataset"]) != "medeinst"]),
        "common_no_parse_failure_items": compact_metrics([row for row in rows if item_id(row) not in failure_ids]),
        "pairwise_complete_case": complete_case,
    }
    return {
        "bootstrap_samples": bootstrap_samples, "methods": methods, "comparisons": comparisons,
        "sensitivity": sensitivity,
    }


def hypothesis_conclusion(result: dict[str, Any]) -> str:
    comparisons = result["comparisons"]
    names = (
        "full_transition-medrgag_proxy", "full_transition-direct_rank",
        "full_transition-structured_no_transition", "full_transition-effect_shuffle",
        "full_transition-full_card_shuffle", "full_transition-parametric_transition",
    )
    deltas = [comparisons.get(name, {}).get("delta") for name in names]
    if any(value is None for value in deltas):
        return "not_evaluable"
    mechanism = result.get("transition_mechanism")
    grounding_ok = bool(mechanism) and (
        mechanism.get("claim_citation_rate") is not None
        and mechanism.get("claim_entailment_rate") is not None
        and mechanism.get("unsupported_claim_rate") is not None
        and mechanism.get("contradiction_rate") is not None
        and mechanism["claim_citation_rate"] >= .50
        and mechanism["claim_entailment_rate"] >= .70
        and mechanism["unsupported_claim_rate"] <= .50
        and mechanism["contradiction_rate"] <= .10
    )
    quantitative_ok = all(value > 0 for value in deltas[:5]) and deltas[1] >= .03 and deltas[4] >= .03
    methods = result.get("methods", {})
    transition_dataset_gain = any(
        all(method in methods and dataset in methods[method].get("datasets", {}) for method in ("full_transition", "direct_rank", "structured_no_transition"))
        and methods["full_transition"]["datasets"][dataset]["accuracy"] > methods["direct_rank"]["datasets"][dataset]["accuracy"]
        and methods["full_transition"]["datasets"][dataset]["accuracy"] > methods["structured_no_transition"]["datasets"][dataset]["accuracy"]
        for dataset in ("medpic", "clir")
    )
    if quantitative_ok and deltas[5] >= 0 and grounding_ok and transition_dataset_gain:
        return "positive"
    return "mixed" if any(value > 0 for value in deltas[:5]) else "negative"


def write_outputs(result: dict[str, Any], csv_path: Path, json_path: Path, summary_path: Path) -> None:
    for path in (csv_path, json_path, summary_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("method", "scope", "name", "n", "correct", "accuracy"))
        for method, metrics in result["methods"].items():
            for scope in ("overall", "datasets", "task_types"):
                values = {"all": metrics[scope]} if scope == "overall" else metrics[scope]
                for name, value in values.items():
                    writer.writerow((method, scope, name, value["n"], value["correct"], value["accuracy"]))
    lines = ["# Experiment summary", "", "## Main results", "", "| Method | n | Accuracy | Parse failures |", "|---|---:|---:|---:|"]
    for method, metrics in result["methods"].items():
        value = metrics["overall"]
        lines.append(f"| {method} | {value['n']} | {value['accuracy']:.3f} | {metrics['parse_failures']} |")
    lines += ["", "## Paired comparisons", "", "| Comparison | n | Delta (pp) | 95% CI (pp) |", "|---|---:|---:|---:|"]
    for name, value in result["comparisons"].items():
        ci = value["ci95"]
        lines.append(f"| {name} | {value['n']} | {100 * value['delta']:.1f} | [{100 * ci[0]:.1f}, {100 * ci[1]:.1f}] |")
    conclusion = hypothesis_conclusion(result)
    result["world_model_hypothesis"] = conclusion
    result["world_model_hypothesis_reason"] = (
        "Positive additionally requires a strict full_transition gain over both direct_rank and structured_no_transition on MedPIC or CLIR."
        if conclusion == "positive" else
        "At least one required overall, shuffle, parametric, grounding, or MedPIC/CLIR transition-task condition was not met."
    )
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines += ["", "## Interpretation", "", f"World-model hypothesis: **{conclusion}**. {result['world_model_hypothesis_reason']}", "", "Positive evidence requires full_transition to beat retrieval, ranking, and structured controls; effect/full-card shuffle drops of the expected sign (including at least 3 pp for full-card shuffle); no loss versus parametric_transition; a strict gain over both direct_rank and structured_no_transition on MedPIC or CLIR; and judged grounding with citation >=50%, entailment among cited claims >=70%, unsupported <=50%, and contradiction <=10%. Missing mechanism judgment cannot yield a positive conclusion. Dataset, task, pair, token, and supported dataset-specific metrics are in `metrics.json`.", ""]
    mechanism = result.get("transition_mechanism")
    if mechanism:
        lines += ["## Transition grounding", "", f"Claim citation rate: {mechanism.get('claim_citation_rate')}; entailment among cited claims: {mechanism.get('claim_entailment_rate')}; unsupported rate: {mechanism.get('unsupported_claim_rate')}; contradiction rate: {mechanism.get('contradiction_rate')}.", ""]
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=Path("results/predictions.jsonl"))
    parser.add_argument("--gold", type=Path, help="Gold-only JSONL; required when predictions omit correct/gold")
    parser.add_argument("--scored-predictions", type=Path, help="Optional joined predictions output")
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/metrics.csv"))
    parser.add_argument("--metrics-json", type=Path, default=Path("results/metrics.json"))
    parser.add_argument("--summary", type=Path, default=Path("results/summary.md"))
    parser.add_argument("--mechanism-metrics", type=Path, help="Optional inspect_mechanism.py summary JSON")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    args = parser.parse_args()
    rows = load_jsonl(args.predictions)
    if args.gold:
        rows = join_gold(rows, load_jsonl(args.gold))
    if args.scored_predictions:
        args.scored_predictions.parent.mkdir(parents=True, exist_ok=True)
        args.scored_predictions.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    result = evaluate(rows, args.seed, args.bootstrap_samples)
    if args.mechanism_metrics:
        result["transition_mechanism"] = json.loads(args.mechanism_metrics.read_text(encoding="utf-8"))
    write_outputs(result, args.metrics_csv, args.metrics_json, args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
