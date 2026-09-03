#!/usr/bin/env python3
"""Fit and apply the portable CF-Residual Adapter to MA-RAG and MedRGAG scores."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import minimize_scalar


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results_marag_cf"
REGULARIZATION = (0.0, 0.01, 0.1, 1.0)


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CF = load_script("marag_cf_eval", ROOT / "scripts/evaluate_cfshift.py")
MOE = load_script("marag_cf_moe", ROOT / "scripts/run_cfmoe.py")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8")


def scores(row: dict[str, Any], name: str, control: bool = False) -> dict[int, float]:
    source = row["control_scores"] if control else row["option_scores"]
    return {int(key): float(value) for key, value in source.get(name, {}).items()}


def zscore(values: dict[int, float]) -> dict[int, float]:
    array = np.asarray(list(values.values()), dtype=float)
    scale = float(array.std())
    return {key: (float(value) - float(array.mean())) / (scale + 1e-6)
            for key, value in values.items()}


def margin(values: dict[int, float]) -> float:
    ordered = sorted(values.values(), reverse=True)
    return ordered[0] - ordered[1]


def vote_scores(row: dict[str, Any]) -> dict[int, float]:
    count = {label: 0 for label in row["option_to_label_id"].values()}
    for candidate in row["final_candidates"]:
        if candidate["label_id"] in count:
            count[candidate["label_id"]] += 1
    n = len(row["final_candidates"])
    return {label: math.log((value + 0.5) / (n + 2.0)) for label, value in count.items()}


def entropy_scores(row: dict[str, Any], temperature: float) -> dict[int, float]:
    values = {label: 1e-6 for label in row["option_to_label_id"].values()}
    for candidate in row["final_candidates"]:
        label = candidate["label_id"]
        if label in values:
            values[label] += math.exp(-candidate["mean_token_entropy"] / temperature)
    total = sum(values.values())
    return {label: math.log(value / total) for label, value in values.items()}


def scorable_marag(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    if row["status"] == "ok":
        return True
    candidates = row.get("final_candidates", [])
    return bool(row.get("error") == "vote tie" and row.get("vote_tie")
                and candidates and sum(row.get("vote_counts", {}).values()) == len(candidates)
                and len(row.get("vote_scores", {})) == 4
                and all(math.isfinite(value) for value in row["vote_scores"].values())
                and all(candidate.get("label_id") is not None
                        and candidate.get("mean_token_entropy") is not None
                        and math.isfinite(candidate["mean_token_entropy"])
                        for candidate in candidates))


def export_option_scores(marag_path: Path, config_path: Path, output: Path) -> dict[str, int]:
    temperature = float(json.loads(config_path.read_text(encoding="utf-8"))["entropy_temperature"])
    rows = []
    scorable = 0
    for row in read_jsonl(marag_path):
        value = {key: row.get(key) for key in (
            "pair_id", "source_case_id", "split", "member", "status", "error",
            "official_prediction", "official_label_id", "vote_tie", "consensus_strength",
            "rounds_used",
        )}
        if scorable_marag(row):
            votes = vote_scores(row)
            entropy = entropy_scores(row, temperature)
            mapping = row["option_to_label_id"]
            value["score_status"] = "ok"
            value["vote_scores"] = {letter: votes[label] for letter, label in mapping.items()}
            value["entropy_vote_scores"] = {
                letter: entropy[label] for letter, label in mapping.items()
            }
            assert all(math.isfinite(score) for name in ("vote_scores", "entropy_vote_scores")
                       for score in value[name].values())
            scorable += 1
        else:
            value["score_status"] = "invalid"
            value["vote_scores"] = None
            value["entropy_vote_scores"] = None
        rows.append(value)
    write_jsonl(output, rows)
    return {"rows": len(rows), "scorable": scorable, "non_scorable": len(rows) - scorable}


def fit_entropy_temperature(rows: list[dict[str, Any]], pairs: dict[str, dict[str, Any]]) -> float:
    rows = [row for row in rows if scorable_marag(row)]
    if not rows:
        raise ValueError("no valid development MA-RAG trap rows for entropy temperature")

    def loss(log_temperature: float) -> float:
        temperature = math.exp(log_temperature)
        nll = []
        for row in rows:
            score = entropy_scores(row, temperature)
            probability = CF.softmax(score)
            nll.append(-math.log(max(probability[pairs[row["pair_id"]]["trap"]["label_id"]], 1e-12)))
        return sum(nll) / len(nll)
    return math.exp(float(minimize_scalar(loss, bounds=(math.log(0.05), math.log(5.0)),
                                           method="bounded").x))


def marag_rows(path: Path, method: str = "marag_int") -> dict[tuple[str, str, str], dict[str, Any]]:
    rows = [row for row in read_jsonl(path) if row.get("method", "marag_int") == method]
    result = {(row["split"], row["pair_id"], row["member"]): row for row in rows}
    if len(result) != len(rows):
        raise ValueError("duplicate MA-RAG rows")
    return result


def valid_cpg(row: dict[str, Any]) -> tuple[dict[int, float], float]:
    value = scores(row, "cpg_core")
    if value:
        return value, 1.0
    if row.get("cpg_structurally_not_applicable"):
        return {label: 0.0 for label in row["option_label_ids"]}, 0.0
    return {}, 0.0


def feature_tensor(base: str, pairs: list[dict[str, Any]], expert: dict[str, dict[str, Any]],
                   marag: dict[tuple[str, str, str], dict[str, Any]], entropy_temperature: float,
                   profile_name: str = "profile_no_document", cpg_name: str = "cpg_core",
                   without_base: bool = False) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    values, gold, ids = [], [], []
    names: list[str] | None = None
    for pair in pairs:
        pair_id, labels = pair["pair_id"], [item["label_id"] for item in pair["views"]["four_way"].values()]
        sidecar = expert.get(pair_id)
        if not sidecar or sidecar["status"] != "ok" or sidecar.get("fusion_status") != "ok":
            continue
        profile, (cpg, cpg_available) = scores(sidecar, profile_name), valid_cpg(sidecar)
        if cpg_name != "cpg_core":
            cpg = scores(sidecar, cpg_name)
            cpg_available = float(bool(cpg))
            if not cpg and sidecar.get("shuffled_cpg_status") == "not_applicable":
                cpg = {label: 0.0 for label in labels}
        if set(profile) != set(labels) or set(cpg) != set(labels):
            continue
        zp, zc = zscore(profile), zscore(cpg)
        profile_margin = margin(profile)
        if base == "marag":
            base_row = marag.get((pair["split"], pair_id, "trap"))
            if not scorable_marag(base_row):
                continue
            primary, secondary = vote_scores(base_row), entropy_scores(base_row, entropy_temperature)
            if set(primary) != set(labels):
                continue
            zb, ze = zscore(primary), zscore(secondary)
            agreement = float(CF.argmax(profile) == base_row["official_label_id"])
            consensus = float(base_row["consensus_strength"])
            rounds = float(base_row["rounds_used"]) / 4.0
            if without_base:
                names = ["profile", "cpg", "profile_x_margin", "cpg_x_available"]
                matrix = [[zp[label], zc[label], zp[label] * profile_margin,
                           zc[label] * cpg_available] for label in labels]
            else:
                names = ["marag_vote", "marag_entropy_vote", "profile", "cpg",
                         "vote_x_consensus", "entropy_x_rounds", "profile_x_agreement",
                         "profile_x_margin", "cpg_x_available"]
                matrix = [[zb[label], ze[label], zp[label], zc[label],
                           zb[label] * consensus, ze[label] * rounds, zp[label] * agreement,
                           zp[label] * profile_margin, zc[label] * cpg_available] for label in labels]
        else:
            primary = scores(sidecar, "medrgag")
            if set(primary) != set(labels):
                continue
            zb = zscore(primary)
            agreement = float(CF.argmax(profile) == sidecar["baseline_label_id"])
            base_margin = margin(primary)
            if without_base:
                names = ["profile", "cpg", "profile_x_margin", "cpg_x_available"]
                matrix = [[zp[label], zc[label], zp[label] * profile_margin,
                           zc[label] * cpg_available] for label in labels]
            else:
                names = ["medrgag", "profile", "cpg", "medrgag_x_margin",
                         "profile_x_agreement", "profile_x_margin", "cpg_x_available"]
                matrix = [[zb[label], zp[label], zc[label], zb[label] * base_margin,
                           zp[label] * agreement, zp[label] * profile_margin,
                           zc[label] * cpg_available] for label in labels]
        values.append(matrix)
        gold.append(labels.index(pair["trap"]["label_id"]))
        ids.append(pair_id)
    return np.asarray(values), np.asarray(gold), names or [], ids


def fit_variant(base: str, dev: list[dict[str, Any]], calibration: list[dict[str, Any]],
                expert: dict[str, dict[str, Any]], marag: dict[tuple[str, str, str], dict[str, Any]],
                temperature: float, without_base: bool) -> dict[str, Any]:
    x_dev, y_dev, names, _ = feature_tensor(base, dev, expert, marag, temperature,
                                             without_base=without_base)
    x_cal, y_cal, cal_names, _ = feature_tensor(base, calibration, expert, marag, temperature,
                                                 without_base=without_base)
    if names != cal_names:
        raise ValueError("feature order differs")
    variants = []
    for penalty in REGULARIZATION:
        weights = MOE.fit_weights(x_dev, y_dev, penalty, False)
        variants.append({"regularization": penalty, "weights": list(map(float, weights)),
                         "calibration_accuracy": MOE.accuracy(MOE.predict(x_cal, weights), y_cal)})
    chosen = max(variants, key=lambda row: (row["calibration_accuracy"], -row["regularization"]))
    return {"feature_names": names, "regularization": chosen["regularization"],
            "weights": chosen["weights"],
            "calibration_variants": [{key: value for key, value in row.items() if key != "weights"}
                                     for row in variants]}


def fit(pairs_paths: list[Path], expert_path: Path, marag_path: Path, output: Path,
        dev_limit: int | None = None, calibration_limit: int | None = None) -> dict[str, Any]:
    pairs = [row for path in pairs_paths for row in read_jsonl(path)]
    by_split = {name: [row for row in pairs if row["split"] == name]
                for name in ("dev", "calibration")}
    by_split["dev"] = by_split["dev"][:dev_limit]
    by_split["calibration"] = by_split["calibration"][:calibration_limit]
    expert = {row["case_id"]: row for row in read_jsonl(expert_path)}
    marag = marag_rows(marag_path)
    dev_trap = [marag[("dev", row["pair_id"], "trap")] for row in by_split["dev"]]
    temperature = fit_entropy_temperature(dev_trap, {row["pair_id"]: row for row in by_split["dev"]})
    config = {
        "status": "frozen_before_fresh_test_selection",
        "entropy_temperature": temperature,
        "regularization_candidates": list(REGULARIZATION),
        "marag": fit_variant("marag", *by_split.values(), expert, marag, temperature, False),
        "marag_without_base": fit_variant("marag", *by_split.values(), expert, marag,
                                            temperature, True),
        "medrgag": fit_variant("medrgag", *by_split.values(), expert, marag, temperature, False),
        "medrgag_without_base": fit_variant("medrgag", *by_split.values(), expert, marag,
                                              temperature, True),
        "profile_score": "unchanged profile_no_document (weight=2.0)",
        "cpg_score": "unchanged cpg_core; structurally inapplicable edits are neutral",
        "invalid_policy": "core runtime or numeric failure is invalid; never replace with base prediction",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return config


def learned_predictions(base: str, pairs: list[dict[str, Any]], expert: dict[str, dict[str, Any]],
                        marag: dict[tuple[str, str, str], dict[str, Any]], config: dict[str, Any],
                        without_base: bool = False, profile_name: str = "profile_no_document",
                        cpg_name: str = "cpg_core") -> dict[str, int | None]:
    key = base + ("_without_base" if without_base else "")
    x, _, names, ids = feature_tensor(base, pairs, expert, marag, config["entropy_temperature"],
                                      profile_name, cpg_name, without_base)
    if names != config[key]["feature_names"]:
        raise ValueError("frozen feature order changed")
    predictions = {row["pair_id"]: None for row in pairs}
    if len(ids):
        positions = MOE.predict(x, np.asarray(config[key]["weights"]))
        pair_map = {row["pair_id"]: row for row in pairs}
        predictions.update({pair_id: pair_map[pair_id]["views"]["four_way"]
                            ["ABCD"[int(position)]]["label_id"]
                            for pair_id, position in zip(ids, positions)})
    return predictions


def simple_predictions(pairs: list[dict[str, Any]], expert: dict[str, dict[str, Any]],
                       marag: dict[tuple[str, str, str], dict[str, Any]], config: dict[str, Any],
                       method: str) -> dict[str, int | None]:
    result = {}
    for pair in pairs:
        pair_id = pair["pair_id"]; row = expert.get(pair_id)
        marag_row = marag.get((pair["split"], pair_id, "trap"))
        if method == "marag_int_trap":
            result[pair_id] = marag_row.get("official_label_id") if marag_row else None
            continue
        if method == "marag_int_pair_prompt":
            pair_row = marag.get((pair["split"], pair_id, "pair_prompt"))
            result[pair_id] = pair_row.get("official_label_id") if pair_row else None
            continue
        if not row or row["status"] != "ok":
            result[pair_id] = None; continue
        if method == "medrgag_baseline":
            result[pair_id] = row["baseline_label_id"]; continue
        name = {"profile_only": "profile_no_document", "cpg_core": "cpg_core"}.get(method)
        if name:
            value = scores(row, name)
            result[pair_id] = CF.argmax(value); continue
        medrgag_uniform = method.startswith("medrgag_profile_")
        if medrgag_uniform:
            base_score = scores(row, "medrgag")
        elif scorable_marag(marag_row):
            base_score = vote_scores(marag_row)
        else:
            result[pair_id] = None; continue
        profile = scores(row, "profile_no_document")
        cpg, _ = valid_cpg(row)
        values = [zscore(base_score), zscore(profile)]
        if method.endswith("profile_cpg_uniform"):
            values.append(zscore(cpg))
        result[pair_id] = CF.argmax({label: sum(value[label] for value in values) / len(values)
                                     for label in profile})
    return result


def predict(pairs_paths: list[Path], expert_path: Path, marag_path: Path, config_path: Path,
            output: Path) -> dict[str, Any]:
    pairs = [row for path in pairs_paths for row in read_jsonl(path)]
    expert = {row["case_id"]: row for row in read_jsonl(expert_path)}
    marag = marag_rows(marag_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    methods = {}
    for method in ("marag_int_trap", "marag_int_pair_prompt", "medrgag_baseline",
                   "profile_only", "cpg_core", "marag_profile_uniform",
                   "marag_profile_cpg_uniform", "medrgag_profile_uniform",
                   "medrgag_profile_cpg_uniform"):
        methods[method] = simple_predictions(pairs, expert, marag, config, method)
    methods.update({
        "marag_cf_learned": learned_predictions("marag", pairs, expert, marag, config),
        "marag_cf_without_marag": learned_predictions("marag", pairs, expert, marag, config, True),
        "marag_cf_shuffled_delta": learned_predictions("marag", pairs, expert, marag, config,
                                                         profile_name="shuffled_delta"),
        "marag_cf_shuffled_profile": learned_predictions("marag", pairs, expert, marag, config,
                                                           profile_name="shuffled_profile"),
        "marag_cf_shuffled_cpg": learned_predictions("marag", pairs, expert, marag, config,
                                                       cpg_name="shuffled_cpg_edit"),
        "medrgag_cf_learned": learned_predictions("medrgag", pairs, expert, marag, config),
        "medrgag_cf_without_medrgag": learned_predictions("medrgag", pairs, expert, marag,
                                                            config, True),
    })
    available = {row.get("method", "marag_int") for row in read_jsonl(marag_path)}
    for name in sorted(available - {"marag_int"}):
        values = marag_rows(marag_path, name)
        methods[name] = {
            pair["pair_id"]: (values.get((pair["split"], pair["pair_id"], "trap")) or {})
            .get("official_label_id") for pair in pairs
        }
        if name == "full_cf_marag_native":
            methods["full_cf_marag_native_plus_adapter"] = learned_predictions(
                "marag", pairs, expert, values, config)

    marag_control = {(split, pair_id): row for (split, pair_id, member), row in marag.items()
                     if member == "control"}
    direct_control = marag_rows(marag_path, "direct_qwen3") if "direct_qwen3" in available else {}
    controls: dict[str, dict[str, int | None]] = {}
    for name in methods:
        values = {}
        for pair in pairs:
            pair_id, split = pair["pair_id"], pair["split"]
            sidecar = expert.get(pair_id, {})
            if name.startswith("medrgag"):
                value = sidecar.get("baseline_control_label_id")
            elif name == "direct_qwen3":
                value = (direct_control.get((split, pair_id, "control")) or {}).get("official_label_id")
            elif name in ("profile_only", "cpg_core"):
                direct = scores(sidecar, "direct_logprob", True) if sidecar else {}
                value = CF.argmax(direct)
            else:
                value = (marag_control.get((split, pair_id)) or {}).get("official_label_id")
            values[pair_id] = value
        controls[name] = values
    rows = [{"pair_id": pair["pair_id"], "source_case_id": pair["source_case_id"],
             "split": pair["split"], "gold_label_id": pair["trap"]["label_id"],
             "predictions": {name: values[pair["pair_id"]] for name, values in methods.items()},
             "control_predictions": {name: values[pair["pair_id"]]
                                     for name, values in controls.items()}}
            for pair in pairs]
    write_jsonl(output, rows)
    return {"rows": len(rows), "methods": len(methods),
            "invalid": {name: sum(value is None for value in prediction.values())
                        for name, prediction in methods.items()}}


def smoke(pairs_path: Path, expert_path: Path, marag_path: Path, limit: int) -> dict[str, Any]:
    pairs = read_jsonl(pairs_path)[:limit]
    expert = {row["case_id"]: row for row in read_jsonl(expert_path)}
    marag = marag_rows(marag_path)
    checked = invalid = 0
    for pair in pairs:
        key = (pair["split"], pair["pair_id"], "trap")
        row, sidecar = marag[key], expert[pair["pair_id"]]
        labels = {item["label_id"] for item in pair["views"]["four_way"].values()}
        assert len(row["final_candidates"]) == 4
        assert sum(row["vote_counts"].values()) == 4
        assert set(vote_scores(row)) == labels
        assert all(math.isfinite(value) for value in vote_scores(row).values())
        assert ((row["status"] == "ok" and row["official_label_id"] in labels)
                or (row["status"] == "invalid" and row["official_label_id"] is None))
        assert set(scores(sidecar, "profile_no_document")) == labels
        cpg, _ = valid_cpg(sidecar); assert set(cpg) == labels
        invalid += row["status"] != "ok"
        checked += 1
    return {"pairs": checked, "invalid": invalid, "status": "ok"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("fit", "predict"):
        command = sub.add_parser(name)
        command.add_argument("--pairs", type=Path, action="append", required=True)
        command.add_argument("--experts", type=Path, required=True)
        command.add_argument("--marag-rounds", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        if name == "fit":
            command.add_argument("--dev-limit", type=int)
            command.add_argument("--calibration-limit", type=int)
        if name == "predict":
            command.add_argument("--config", type=Path, required=True)
    check = sub.add_parser("smoke")
    check.add_argument("--pairs", type=Path, required=True)
    check.add_argument("--experts", type=Path, required=True)
    check.add_argument("--marag-rounds", type=Path, required=True)
    check.add_argument("--limit", type=int, default=20)
    export = sub.add_parser("export-scores")
    export.add_argument("--marag-rounds", type=Path, required=True)
    export.add_argument("--config", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "fit":
        value = fit(args.pairs, args.experts, args.marag_rounds, args.output,
                    args.dev_limit, args.calibration_limit)
    elif args.command == "predict":
        value = predict(args.pairs, args.experts, args.marag_rounds, args.config, args.output)
    elif args.command == "export-scores":
        value = export_option_scores(args.marag_rounds, args.config, args.output)
    else:
        value = smoke(args.pairs, args.experts, args.marag_rounds, args.limit)
    print(json.dumps(value, sort_keys=True))
