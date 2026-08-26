#!/usr/bin/env python3
"""Offline evaluation and dev-only calibration for DeltaRev-MedRGAG."""

from __future__ import annotations

import argparse
import csv
import json
import random
import unicodedata
from pathlib import Path
from typing import Any, Iterable


THRESHOLD_METHODS = {
    "evidence_verifier_with_standard_retrieval", "evidence_verifier_with_ea_rag_retrieval",
    "full_deltarev", "without_delta", "without_baseline_answer_in_query",
    "refute_only_retrieval", "without_preserve_evidence",
    "without_alternative_support_requirement", "without_entailment_check",
    "without_patient_applicability_check", "kgcc_generated_docs_as_decisive_evidence",
    "shuffled_delta", "shuffled_rule_evidence",
}
RESIDUAL_METHODS = THRESHOLD_METHODS | {"medrgag_proxy", "always_preserve"}
SHARED_CONTROL_METHODS = RESIDUAL_METHODS | {"direct_answer_revision"}
NA = {
    "medpic_metrics": None, "recall_at_5": None, "recall_at_10": None, "mrr": None,
    "refute_evidence_coverage": None, "preserve_evidence_coverage": None,
    "alternative_support_coverage": None, "gold_delta_diagnostic": None,
    "source_rule_upper_bound": None, "without_nice": None,
}
AVAILABILITY_NOTES = {
    "medpic_metrics": "unavailable: local official linked-pair map is absent (0 official pairs)",
    "recall_at_5": "unavailable: no official decisive evidence reference",
    "recall_at_10": "unavailable: no official decisive evidence reference",
    "mrr": "unavailable: no official decisive evidence reference",
    "refute_evidence_coverage": "unavailable: no official decisive evidence reference",
    "preserve_evidence_coverage": "unavailable: no official decisive evidence reference",
    "alternative_support_coverage": "unavailable: no official decisive evidence reference",
    "gold_delta_diagnostic": "unavailable: MedEinst has no official edit metadata",
    "source_rule_upper_bound": "unavailable: MedEinst has no official decisive source span",
    "without_nice": "NA: NICE is unavailable and was not replaced by KGCC",
}
RETRIEVAL_METHODS = (
    "standard_question_retrieval", "candidate_specific_retrieval", "ea_rag_style_retrieval",
    "delta_only_retrieval", "triangular_decision_change_retrieval", "refute_only_retrieval",
    "without_baseline_answer_in_query", "without_preserve_evidence",
)
RULE_METHODS = RETRIEVAL_METHODS + ("shuffled_delta", "shuffled_rule_evidence",
                                    "kgcc_generated_decisive")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def norm(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("answer", value.get("open_answer", ""))
    if isinstance(value, list):
        value = value[0] if len(value) == 1 else " | ".join(map(str, value))
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.strip().casefold().split()).rstrip(" .,:;!?")


def same(left: Any, right: Any) -> bool:
    return bool(norm(left)) and norm(left) == norm(right)


def final_answer(proposal: dict[str, Any], threshold: float) -> Any:
    baseline = proposal["baseline_answer"]
    if proposal.get("status") != "ok":
        return baseline if proposal.get("method") in RESIDUAL_METHODS else None
    if proposal["method"] not in THRESHOLD_METHODS:
        return proposal.get("proposed_answer", baseline)
    if not proposal.get("gate_without_threshold"):
        return baseline
    if float(proposal.get("verifier_score", 0)) < threshold:
        return baseline
    return proposal.get("proposed_answer", baseline)


def score_method(gold: list[dict[str, Any]], baselines: dict[str, dict[str, Any]],
                 proposals: dict[tuple[str, str], dict[str, Any]], method: str,
                 threshold: float, split: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows, pairs = [], [row for row in gold if row["split"] == split]
    explicit_control_supported = any(
        proposals.get((row["pair_id"], method), {}).get("control_prediction") is not None
        for row in pairs)
    method_control_supported = method in SHARED_CONTROL_METHODS or explicit_control_supported
    for row in pairs:
        pair_id = row["pair_id"]
        baseline = baselines[pair_id]["members"]
        if (pair_id, method) not in proposals:
            raise ValueError(f"missing proposal row: {(pair_id, method)}")
        proposal = proposals[(pair_id, method)]
        control_prediction = proposal.get("control_prediction")
        control_available = method_control_supported
        if control_prediction is None and method in SHARED_CONTROL_METHODS:
            control_prediction = baseline["control"]["baseline_answer"]
        trap_baseline = baseline["trap"]["baseline_answer"]
        trap_prediction = final_answer(proposal, threshold)
        rows.append({
            "pair_id": pair_id, "split": split, "method": method,
            "control_prediction": control_prediction, "trap_prediction": trap_prediction,
            "control_gold": row["control_answer"], "trap_gold": row["trap_answer"],
            "trap_baseline": trap_baseline,
            "control_available": control_available,
            "control_correct": same(control_prediction, row["control_answer"]) if control_available else None,
            "baseline_correct": same(trap_baseline, row["trap_answer"]),
            "final_correct": same(trap_prediction, row["trap_answer"]),
            "revised": not same(trap_prediction, trap_baseline),
            "gate_passed": ((proposal.get("status") == "ok"
                             and bool(proposal.get("gate_without_threshold"))
                             and float(proposal.get("verifier_score", 0)) >= threshold)
                            if method in THRESHOLD_METHODS else None),
            "old_answer_persisted": same(trap_prediction, control_prediction) if control_available else None,
            "bias_trap": same(trap_prediction, row["control_answer"]) if control_available else None,
            "correct_change": (not same(trap_prediction, control_prediction) and same(trap_prediction, row["trap_answer"]))
                              if control_available else None,
        })
    n = len(rows)
    if not n:
        raise ValueError(f"no {split} gold rows")
    repairs = sum(not row["baseline_correct"] and row["final_correct"] for row in rows)
    harms = sum(row["baseline_correct"] and not row["final_correct"] for row in rows)
    changes = sum(row["revised"] for row in rows)
    baseline_wrong = sum(not row["baseline_correct"] for row in rows)
    baseline_correct = n - baseline_wrong
    control_rows = [row for row in rows if row["control_available"]]
    control_correct = sum(bool(row["control_correct"]) for row in control_rows)
    trap_correct = sum(row["final_correct"] for row in rows)
    wrong_different_wrong = sum(not row["baseline_correct"] and not row["final_correct"] and row["revised"] for row in rows)
    correct_different_correct = sum(row["baseline_correct"] and row["final_correct"] and row["revised"] for row in rows)
    btr_denominator = sum(bool(row["control_correct"]) for row in control_rows)
    missing_controls = sum(proposals[(row["pair_id"], method)].get("control_prediction") is None
                           for row in pairs) if explicit_control_supported else 0
    statuses = [proposals[(row["pair_id"], method)].get("status") for row in pairs]
    metrics = {
        "pairs": n, "accuracy": trap_correct / n,
        "member_accuracy": ((control_correct + trap_correct) / (2 * n) if len(control_rows) == n else None),
        "control_accuracy": (control_correct / n if len(control_rows) == n else None),
        "trap_accuracy": trap_correct / n,
        "pair_accuracy": (sum(row["control_correct"] and row["final_correct"] for row in rows) / n
                          if len(control_rows) == n else None),
        "both_correct_pair_accuracy": (sum(row["control_correct"] and row["final_correct"] for row in rows) / n
                                       if len(control_rows) == n else None),
        "bias_trap_rate": ((sum(row["control_correct"] and row["bias_trap"] for row in control_rows)
                            / btr_denominator if btr_denominator else None)
                           if len(control_rows) == n else None),
        "bias_trap_denominator": btr_denominator,
        "original_diagnosis_persistence": (sum(bool(row["old_answer_persisted"]) for row in rows) / n
                                           if len(control_rows) == n else None),
        "old_answer_persistence": (sum(bool(row["old_answer_persisted"]) for row in rows) / n
                                   if len(control_rows) == n else None),
        "correct_change": (sum(bool(row["correct_change"]) for row in rows) / n
                           if len(control_rows) == n else None),
        "correct_invariance": None,
        "control_metric_note": (f"method-specific control prediction; {missing_controls} missing counted incorrect"
                                if explicit_control_supported
                                else "shared unchanged M2 control for direct answer-revision baseline"
                                if method == "direct_answer_revision"
                                else "shared unchanged M2 control for residual method" if len(control_rows) == n
                                else "NA: target-only method has no method-specific control prediction"),
        "missing_control_prediction_count": missing_controls if explicit_control_supported else None,
        "repairs": repairs, "harms": harms,
        "error_correction_rate": repairs / baseline_wrong if baseline_wrong else 0.0,
        "harm_rate": harms / n,
        "original_correct_preservation": (baseline_correct - harms) / baseline_correct if baseline_correct else 1.0,
        "revision_coverage": (sum(bool(row["gate_passed"]) for row in rows) / n
                              if method in THRESHOLD_METHODS else None),
        "answer_change_coverage": changes / n,
        "beneficial_revision_precision": repairs / changes if changes else 0.0,
        "net_correction": (repairs - harms) / n,
        "final_accuracy": trap_correct / n,
        "baseline_correct_preserved_correct": sum(row["baseline_correct"] and row["final_correct"]
                                                    and not row["revised"] for row in rows),
        "baseline_correct_revised_wrong": harms,
        "baseline_wrong_preserved_wrong": sum(not row["baseline_correct"] and not row["final_correct"] and not row["revised"] for row in rows),
        "baseline_wrong_revised_correct": repairs,
        "wrong_to_different_wrong": wrong_different_wrong,
        "correct_to_different_correct": correct_different_correct,
        "missing_count": 0,
        "parse_failure_count": sum(status == "parse_failure" for status in statuses),
        "contract_failure_count": sum(status == "contract_failure" for status in statuses),
        "missing_or_contract_failure_count": sum(status != "ok" for status in statuses),
    }
    return metrics, rows


def threshold_curve(gold: list[dict[str, Any]], baselines: dict[str, dict[str, Any]],
                    proposals: dict[tuple[str, str], dict[str, Any]], method: str = "full_deltarev") -> list[dict[str, Any]]:
    curve = []
    for step in range(21):
        threshold = step / 20
        metrics, _ = score_method(gold, baselines, proposals, method, threshold, "dev")
        curve.append({"method": method, "threshold": threshold, **metrics})
    return curve


def select_threshold(curve: list[dict[str, Any]], harm_budget: float) -> dict[str, Any] | None:
    eligible = [row for row in curve if row["harm_rate"] <= harm_budget]
    if not eligible:
        return None
    return max(eligible, key=lambda row: (row["net_correction"], row["beneficial_revision_precision"], row["threshold"]))


def paired_bootstrap(rows_a: list[dict[str, Any]], rows_b: list[dict[str, Any]],
                     samples: int = 1000, seed: int = 13) -> dict[str, Any]:
    if [row["pair_id"] for row in rows_a] != [row["pair_id"] for row in rows_b]:
        raise ValueError("bootstrap pair identities differ")
    differences = [float(a["final_correct"]) - float(b["final_correct"]) for a, b in zip(rows_a, rows_b)]
    rng = random.Random(seed)
    values = []
    for _ in range(samples):
        values.append(sum(rng.choice(differences) for _ in differences) / len(differences))
    values.sort()
    return {"difference": sum(differences) / len(differences),
            "ci95": [values[int(.025 * samples)], values[min(samples - 1, int(.975 * samples))]],
            "samples": samples}


def artifact_diagnostics(pair_ids: set[str], delta_rows: list[dict[str, Any]],
                         retrieval_rows: list[dict[str, Any]], rule_rows: list[dict[str, Any]],
                         proposal_rows: list[dict[str, Any]]) -> dict[str, Any]:
    def exact(rows: list[dict[str, Any]], fields: tuple[str, ...], expected: set[tuple[Any, ...]], label: str):
        keys = [tuple(row.get(field) for field in fields) for row in rows]
        if len(keys) != len(set(keys)) or set(keys) != expected:
            raise ValueError(f"{label} artifact coverage differs from proposal pairs")
        return {key: row for key, row in zip(keys, rows)}
    deltas = exact(delta_rows, ("pair_id",), {(pair_id,) for pair_id in pair_ids}, "delta")
    retrievals = exact(retrieval_rows, ("pair_id", "artifact_type"),
                       {(pair_id, kind) for pair_id in pair_ids for kind in ("base", "shuffled_delta")},
                       "retrieval")
    rules = exact(rule_rows, ("pair_id", "retrieval_method"),
                  {(pair_id, method) for pair_id in pair_ids for method in RULE_METHODS}, "rule")
    for pair_id in pair_ids:
        if set(retrievals[(pair_id, "base")].get("results", {})) != set(RETRIEVAL_METHODS):
            raise ValueError(f"base retrieval method coverage differs: {pair_id}")

    n = len(pair_ids)
    delta_result = {}
    for method, field in (("deterministic", "deterministic"), ("llm_only", "llm_only"), ("hybrid", "hybrid")):
        nonempty = sum(bool(deltas[(pair_id,)].get(field, {}).get("changed_variables")) for pair_id in pair_ids)
        values = {"nonempty_count": nonempty, "nonempty_coverage": nonempty / n}
        if method != "deterministic":
            usage_name = "llm" if method == "llm_only" else "hybrid"
            usages = [deltas[(pair_id,)].get("usage", {}).get(usage_name, {}) for pair_id in pair_ids]
            failures = sum(bool(row.get("contract_failure")) for row in usages)
            values.update({"contract_failure_count": failures,
                           "usable_output_count": n - failures,
                           "contract_failure_rate": failures / n,
                           "retry_rate": sum(int(row.get("retry_count", 0)) > 0 for row in usages) / n})
        delta_result[method] = values

    retrieval_result = {}
    for method in RETRIEVAL_METHODS + ("shuffled_delta",):
        documents, errors = [], []
        for pair_id in pair_ids:
            artifact = retrievals[(pair_id, "shuffled_delta" if method == "shuffled_delta" else "base")]
            documents.append(artifact.get("results", []) if method == "shuffled_delta"
                             else artifact.get("results", {}).get(method, []))
            stored_errors = artifact.get("errors", []) if method == "shuffled_delta" else artifact.get("errors", {}).get(method, [])
            errors.append(stored_errors)
        retrieval_result[method] = {
            "error_count": sum(map(len, errors)),
            "error_pair_count": sum(bool(row) for row in errors),
            "error_pair_rate": sum(bool(row) for row in errors) / n,
            "ten_document_count": sum(len(row) == 10 for row in documents),
            "ten_document_coverage": sum(len(row) == 10 for row in documents) / n,
            "average_documents": sum(map(len, documents)) / n,
        }
    audit_rows = [audit for pair_id in pair_ids
                  for audit in retrievals[(pair_id, "base")].get("ea_rag_style", {}).get("coverage_audit", [])]
    retrieval_result["ea_rag_style_retrieval"]["coverage_audit_proxy_covered_rate"] = (
        sum(bool(row.get("covered")) for row in audit_rows) / len(audit_rows) if audit_rows else None)
    retrieval_result["ea_rag_style_retrieval"]["coverage_audit_variable_count"] = len(audit_rows)

    def rule_stats(selected: list[dict[str, Any]]) -> dict[str, Any]:
        extractors = [row.get("usage", {}).get("extractor") for row in selected
                      if isinstance(row.get("usage", {}).get("extractor"), dict)
                      and not row.get("usage", {}).get("extractor", {}).get("skipped")]
        verifiers = [row.get("usage", {}).get("verifier") for row in selected
                     if isinstance(row.get("usage", {}).get("verifier"), dict)
                     and (row.get("usage", {}).get("verifier", {}).get("calls", 0) > 0
                          or row.get("usage", {}).get("verifier", {}).get("contract_failure"))]
        return {
            "rows": len(selected),
            "extractor_applicable_rows": len(extractors),
            "extractor_contract_failure_rate": (sum(bool(row.get("contract_failure")) for row in extractors) / len(extractors)
                                                 if extractors else None),
            "extractor_retry_rate": (sum(int(row.get("retry_count", 0)) > 0 for row in extractors) / len(extractors)
                                     if extractors else None),
            "nonempty_rule_set_coverage": sum(bool(row.get("rules")) for row in selected) / len(selected),
            "rule_count": sum(len(row.get("rules", [])) for row in selected),
            "average_rules": sum(len(row.get("rules", [])) for row in selected) / len(selected),
            "verifier_applicable_rows": len(verifiers),
            "verifier_contract_failure_rate": (sum(bool(row.get("contract_failure")) for row in verifiers) / len(verifiers)
                                                if verifiers else None),
            "verifier_retry_rate": (sum(int(row.get("retry_count", 0)) > 0 for row in verifiers) / len(verifiers)
                                    if verifiers else None),
            "verification_count": sum(len(row.get("verifications", [])) for row in selected),
            "average_verifications": sum(len(row.get("verifications", [])) for row in selected) / len(selected),
        }
    rule_result = {method: rule_stats([rules[(pair_id, method)] for pair_id in pair_ids])
                   for method in RULE_METHODS}
    rule_result["overall"] = rule_stats(list(rules.values()))
    failure_counts: dict[str, int] = {}
    for proposal in proposal_rows:
        for stage in proposal.get("details", {}).get("stage_failures", []):
            failure_counts[str(stage)] = failure_counts.get(str(stage), 0) + 1
    highest = max(failure_counts, key=lambda stage: (failure_counts[stage], stage)) if failure_counts else None
    return {"expected_pairs": n, "delta_rows": len(delta_rows), "retrieval_rows": len(retrieval_rows),
            "rule_rows": len(rule_rows), "delta": delta_result, "retrieval": retrieval_result,
            "rules": rule_result, "proposal_failure_stages": failure_counts,
            "highest_failure_stage": ({"stage": highest, "count": failure_counts[highest]} if highest else None),
            "interpretation": "coverage/contract diagnostics only; not official delta accuracy or retrieval Recall/MRR"}


def evaluate(gold_path: Path, baseline_path: Path, proposal_path: Path, delta_path: Path,
             retrieval_path: Path, rule_path: Path, output_dir: Path,
             bootstrap_samples: int = 1000) -> dict[str, Any]:
    gold = read_jsonl(gold_path)
    baseline_rows = read_jsonl(baseline_path)
    proposal_rows = read_jsonl(proposal_path)
    delta_rows, retrieval_rows, rule_rows = read_jsonl(delta_path), read_jsonl(retrieval_path), read_jsonl(rule_path)
    proposal_keys = [(row.get("pair_id"), row.get("method")) for row in proposal_rows]
    if len(proposal_keys) != len(set(proposal_keys)):
        raise ValueError("duplicate proposal pair/method rows")
    baseline_keys = [row.get("pair_id") for row in baseline_rows]
    if len(baseline_keys) != len(set(baseline_keys)):
        raise ValueError("duplicate baseline pair rows")
    gold_keys = [row.get("pair_id") for row in gold]
    if len(gold_keys) != len(set(gold_keys)):
        raise ValueError("duplicate gold pair rows")
    if set(baseline_keys) != set(gold_keys):
        raise ValueError("baseline/gold pair coverage differs")
    baselines = {row["pair_id"]: row for row in baseline_rows}
    proposals = {(row["pair_id"], row["method"]): row for row in proposal_rows}
    proposal_pair_ids = {str(row["pair_id"]) for row in proposal_rows}
    if proposal_pair_ids != set(gold_keys):
        raise ValueError("proposal/gold pair coverage differs")
    diagnostics = artifact_diagnostics(proposal_pair_ids, delta_rows, retrieval_rows, rule_rows, proposal_rows)
    methods = sorted({row["method"] for row in proposal_rows if row.get("status") != "unavailable"})
    curve = threshold_curve(gold, baselines, proposals)
    primary = select_threshold(curve, .02)
    strict = select_threshold(curve, .01)
    if primary is None or strict is None:
        raise ValueError("no threshold satisfies harm budgets")
    selected = float(primary["threshold"])
    llm_delta_failures = diagnostics["delta"]["llm_only"]["contract_failure_count"]
    expected_pairs = diagnostics["expected_pairs"]
    metrics: dict[str, Any] = {"availability": NA, "availability_notes": AVAILABILITY_NOTES,
                               "artifact_diagnostics": diagnostics,
                               "evaluation_policy": {
                                   "answer_matching": "strict normalized exact match (NFKC, casefold, whitespace collapse, terminal punctuation trim)",
                                   "clinical_equivalence_rescoring": False,
                               },
                               "limitations": {
                                   "delta_quality_comparison": (
                                       "not valid: official delta metadata is unavailable; "
                                       f"LLM-only extraction had {llm_delta_failures}/{expected_pairs} contract failures; "
                                       "the full path used deterministic/hybrid delta output and is not evidence of LLM-only delta success"
                                   ),
                                   "answer_matching": (
                                       "strict normalized exact match may count clinically related wording such as "
                                       "Bronchitis versus Chronic Bronchitis as different; no post-hoc rescoring was applied"
                                   ),
                               },
                               "selected_threshold": selected,
                               "strict_threshold": float(strict["threshold"]), "methods": {}}
    prediction_rows, scored_rows = [], {}
    for method in methods:
        test_metrics, test_rows = score_method(gold, baselines, proposals, method, selected, "test")
        dev_metrics, dev_rows = score_method(gold, baselines, proposals, method, selected, "dev")
        metrics["methods"][method] = {"dev": dev_metrics, "test": test_metrics}
        scored_rows[method] = test_rows
        for row in dev_rows + test_rows:
            proposal = proposals[(row["pair_id"], method)]
            prediction_rows.append({
                "pair_id": row["pair_id"], "dataset": "medeinst", "split": row["split"],
                "method": method, "control_prediction": row["control_prediction"],
                "baseline_answer": proposal["baseline_answer"],
                "proposed_answer": proposal.get("proposed_answer"),
                "final_answer": row["trap_prediction"], "trap_prediction": row["trap_prediction"],
                "decision": "REVISE" if row["revised"] else "PRESERVE",
                "decisive_rule_ids": (proposal.get("details", {}).get("decisive_rule_ids", [])
                                      if row["revised"] else []),
                "reason": (proposal.get("details", {}).get("reason")
                           if row["revised"] else "threshold/gate required exact baseline preservation"),
                "verifier_score": proposal.get("verifier_score"),
                "gate_without_threshold": proposal.get("gate_without_threshold"),
                "gate_passed": row["gate_passed"],
                "stage_failures": proposal.get("details", {}).get("stage_failures", []),
                "status": proposal.get("status"), "threshold": selected,
            })
    unavailable_rows = [row for row in proposal_rows if row.get("status") == "unavailable"
                        and row.get("method") not in methods]
    unavailable_counts: dict[str, int] = {}
    split_by_pair = {row["pair_id"]: row["split"] for row in gold}
    for proposal in unavailable_rows:
        method = proposal["method"]
        unavailable_counts[method] = unavailable_counts.get(method, 0) + 1
        prediction_rows.append({
            "pair_id": proposal["pair_id"], "dataset": "medeinst",
            "split": split_by_pair[proposal["pair_id"]], "method": method,
            "control_prediction": proposal.get("control_prediction"),
            "baseline_answer": proposal.get("baseline_answer"),
            "proposed_answer": proposal.get("proposed_answer"),
            "final_answer": None, "trap_prediction": None, "decision": "UNAVAILABLE",
            "decisive_rule_ids": [], "reason": AVAILABILITY_NOTES.get(method, "unavailable"),
            "verifier_score": proposal.get("verifier_score"),
            "gate_without_threshold": proposal.get("gate_without_threshold"),
            "gate_passed": None,
            "stage_failures": proposal.get("details", {}).get("stage_failures", []),
            "status": "unavailable", "threshold": None,
        })
    metrics["unavailable_prediction_rows"] = unavailable_counts
    comparisons = ("always_preserve", "medrgag_proxy", "evidence_verifier_with_standard_retrieval",
                   "evidence_verifier_with_ea_rag_retrieval", "direct_answer_revision")
    metrics["paired_bootstrap"] = {
        f"full_deltarev_vs_{method}": paired_bootstrap(scored_rows["full_deltarev"], scored_rows[method], bootstrap_samples)
        for method in comparisons if "full_deltarev" in scored_rows and method in scored_rows
    }
    strict_test, _ = score_method(gold, baselines, proposals, "full_deltarev",
                                  float(strict["threshold"]), "test")
    metrics["primary_operating_point_test"] = {
        "threshold": selected,
        **{key: metrics["methods"]["full_deltarev"]["test"][key]
           for key in ("repairs", "harms", "harm_rate", "net_correction", "final_accuracy",
                       "revision_coverage", "answer_change_coverage", "wrong_to_different_wrong")},
    }
    metrics["strict_operating_point_test"] = {
        "threshold": float(strict["threshold"]),
        **{key: strict_test[key] for key in ("repairs", "harms", "harm_rate", "net_correction",
                                             "final_accuracy", "revision_coverage",
                                             "answer_change_coverage", "wrong_to_different_wrong")},
    }
    # Gold-label diagnostic only: best possible gate over the already proposed full answer.
    oracle_repairs = oracle_harms = 0
    for row in [value for value in gold if value["split"] == "test"]:
        proposal = proposals[(row["pair_id"], "full_deltarev")]
        baseline_correct = same(proposal["baseline_answer"], row["trap_answer"])
        proposed_correct = same(proposal.get("proposed_answer"), row["trap_answer"])
        oracle_repairs += int(not baseline_correct and proposed_correct)
        oracle_harms += 0
    metrics["oracle_revision_gate_gold_label_diagnostic"] = {
        "repairs": oracle_repairs, "harms": oracle_harms,
        "note": "outside the main method table; test gold was used only for this labeled diagnostic",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "tradeoff.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(curve[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(curve)
    with (output_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["method", "split", "accuracy", "member_accuracy", "control_accuracy", "trap_accuracy",
                  "pair_accuracy", "both_correct_pair_accuracy", "correct_change", "correct_invariance",
                  "old_answer_persistence", "original_diagnosis_persistence", "repairs", "harms",
                  "error_correction_rate", "harm_rate", "original_correct_preservation", "net_correction",
                  "revision_coverage", "answer_change_coverage", "beneficial_revision_precision", "bias_trap_rate",
                  "baseline_correct_preserved_correct", "baseline_correct_revised_wrong",
                  "baseline_wrong_preserved_wrong", "baseline_wrong_revised_correct",
                  "wrong_to_different_wrong", "correct_to_different_correct", "missing_count",
                  "missing_control_prediction_count", "parse_failure_count", "contract_failure_count"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n"); writer.writeheader()
        for method, splits in metrics["methods"].items():
            for split, values in splits.items():
                writer.writerow({key: method if key == "method" else split if key == "split" else values[key] for key in fields})
    (output_dir / "predictions.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in prediction_rows), encoding="utf-8")
    full = metrics["methods"].get("full_deltarev", {}).get("test", {})
    preserve = metrics["methods"].get("always_preserve", {}).get("test", {})
    standard = metrics["methods"].get("standard_question_retrieval", {}).get("test", {})
    triangular = metrics["methods"].get("triangular_decision_change_retrieval", {}).get("test", {})
    ea = metrics["methods"].get("ea_rag_style_retrieval", {}).get("test", {})
    evidence_standard = metrics["methods"].get("evidence_verifier_with_standard_retrieval", {}).get("test", {})
    evidence_ea = metrics["methods"].get("evidence_verifier_with_ea_rag_retrieval", {}).get("test", {})
    support = (full.get("net_correction", 0) > 0 and full.get("harm_rate", 1) <= .02
               and (not evidence_standard or full.get("accuracy", 0) >= evidence_standard.get("accuracy", 1))
               and (not evidence_ea or full.get("accuracy", 0) >= evidence_ea.get("accuracy", 1)))
    metrics["hypothesis_supported"] = support
    metrics["hypothesis_support_criteria"] = {
        "positive_test_net_correction": full.get("net_correction", 0) > 0,
        "test_harm_rate_at_most_2_percent": full.get("harm_rate", 1) <= .02,
        "not_worse_than_standard_evidence_revision": (not evidence_standard or full.get("accuracy", 0) >= evidence_standard.get("accuracy", 1)),
        "not_worse_than_ea_evidence_revision": (not evidence_ea or full.get("accuracy", 0) >= evidence_ea.get("accuracy", 1)),
        "note": "test was used only for reporting these post-calibration criteria, never for threshold selection",
    }
    def comparison(left: dict[str, Any], right: dict[str, Any], metric: str = "accuracy") -> str:
        if metric not in left or metric not in right:
            return "NA"
        difference = left[metric] - right[metric]
        relation = "higher" if difference > 0 else "lower" if difference < 0 else "tied"
        return f"{relation} ({left[metric]:.4f} vs {right[metric]:.4f}; difference {difference:+.4f})"
    main_methods = ("direct", "medrgag_proxy", "decomposition_only",
                    "direct_counterfactual_prompt", "direct_answer_revision",
                    "standard_question_retrieval", "candidate_specific_retrieval",
                    "ea_rag_style_retrieval", "delta_only_retrieval",
                    "triangular_decision_change_retrieval", "always_preserve", "always_revise",
                    "llm_verifier_without_evidence",
                    "evidence_verifier_with_standard_retrieval",
                    "evidence_verifier_with_ea_rag_retrieval", "full_deltarev")
    table = ["| Method | Strict exact-match accuracy | Harm | Net correction | Repairs | Harms | Failures |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for method in main_methods:
        values = metrics["methods"].get(method, {}).get("test")
        if values:
            failures = values["parse_failure_count"] + values["contract_failure_count"]
            table.append(f"| `{method}` | {values['accuracy']:.4f} | {values['harm_rate']:.4f} | "
                         f"{values['net_correction']:.4f} | {values['repairs']} | {values['harms']} | {failures} |")
    ablation_methods = ("without_delta", "without_baseline_answer_in_query", "refute_only_retrieval",
                        "without_preserve_evidence", "without_alternative_support_requirement",
                        "without_entailment_check", "without_patient_applicability_check",
                        "shuffled_delta", "shuffled_rule_evidence",
                        "kgcc_generated_docs_as_decisive_evidence")
    ablations = []
    for method in ablation_methods:
        values = metrics["methods"].get(method, {}).get("test")
        if values:
            ablations.append((full.get("net_correction", 0) - values["net_correction"], method, values))
    largest = max(ablations, default=None)
    bottleneck = (f"largest observed net-correction drop was {largest[0]:+.4f} for `{largest[1]}`; "
                  "this is a diagnostic association, not causal attribution"
                  if largest and largest[0] > 0 else
                  "no ablation produced a positive net-correction drop; inspect contract failures and routing before attributing a component")
    highest_failure = diagnostics.get("highest_failure_stage")
    failure_note = (f" The most frequent recorded failure stage was `{highest_failure['stage']}` "
                    f"({highest_failure['count']} proposal rows)." if highest_failure else
                    " No proposal stage failures were recorded.")
    overall_rules = diagnostics["rules"]["overall"]
    hybrid_delta = diagnostics["delta"]["hybrid"]
    llm_delta = diagnostics["delta"]["llm_only"]
    retrieval_error_count = sum(value.get("error_count", 0)
                                for value in diagnostics["retrieval"].values())
    artifact_note = (
        f" Atomic-rule extraction contract failure was {overall_rules['extractor_contract_failure_rate']:.4f} "
        f"with nonempty rule sets on {overall_rules['nonempty_rule_set_coverage']:.4f} of rows; verifier "
        f"contract failure was {overall_rules['verifier_contract_failure_rate']:.4f}. LLM-only delta extraction "
        f"failed on {llm_delta['contract_failure_rate']:.4f}, while the full method's hybrid delta failed on "
        f"{hybrid_delta['contract_failure_rate']:.4f}. Retrieval recorded {retrieval_error_count} query errors."
    )
    ablation_lines = [f"- `{method}`: net={values['net_correction']:.4f}, harm={values['harm_rate']:.4f}, "
                      f"failures={values['parse_failure_count'] + values['contract_failure_count']}"
                      for _, method, values in ablations]
    ablation_failure_notes = []
    for method, stage in (("without_delta", "without_delta_relevance"),
                          ("shuffled_delta", "shuffled_relevance")):
        values = metrics["methods"].get(method, {}).get("test")
        if values:
            ablation_failure_notes.append(
                f"`{method}` had {values['contract_failure_count']}/{values['pairs']} test contract failures "
                f"and {diagnostics['proposal_failure_stages'].get(stage, 0)}/{diagnostics['expected_pairs']} "
                "overall relevance-stage failures"
            )
    ablation_caveat = (("; ".join(ablation_failure_notes) +
                        ". Their zero net correction reflects fail-closed preservation, not successful mechanism evidence. ")
                       if ablation_failure_notes else
                       "A zero net correction from a fully failed ablation would reflect fail-closed preservation, not successful mechanism evidence. ") + (
        "More generally, the high atomic-rule extraction failure rate makes null ablation effects non-informative.")
    bootstrap_lines = [f"- `{name}`: accuracy difference={value['difference']:+.4f}, "
                       f"paired-bootstrap 95% CI=[{value['ci95'][0]:+.4f}, {value['ci95'][1]:+.4f}]"
                       for name, value in metrics["paired_bootstrap"].items()]
    primary_test = metrics["primary_operating_point_test"]
    strict_point = metrics["strict_operating_point_test"]
    persistence = metrics["methods"].get("medrgag_proxy", {}).get("test", {}).get("old_answer_persistence", "NA")
    medeinst = metrics["methods"].get("medrgag_proxy", {}).get("test", {})
    summary = f"""# DeltaRev-MedRGAG pilot

The paired main pilot contains 200 MedEinst pairs (40 development, 160 test). MedPIC is unavailable for the paired pilot because the local official linked-pair map is absent. NICE is unavailable and was not replaced by KGCC. All answer accuracies use strict normalized exact match (NFKC, casefold, whitespace collapse, and terminal-punctuation trimming); no post-hoc clinical-equivalence rescoring was performed.

1. Old-answer persistence: {persistence} on test, defined as the M2 trap prediction equaling its paired M2 control prediction.
2. Official changed-variable recovery: NA; MedEinst has no official edit metadata. The requested deterministic/LLM-only/hybrid three-way delta-quality comparison is not valid: LLM-only extraction had {llm_delta['contract_failure_count']}/{diagnostics['expected_pairs']} contract failures ({llm_delta['usable_output_count']} usable outputs). The main full path used deterministic/hybrid delta output and must not be read as LLM-only delta success.
3. Decision-change retrieval versus normal retrieval: ordinary triangular retrieval was {comparison(triangular, standard)}; full residual revision versus standard-evidence revision was {comparison(full, evidence_standard)}. Recall/MRR remain NA without decisive evidence references.
4. EA-RAG-style comparison: ordinary triangular retrieval was {comparison(triangular, ea)}; full residual revision versus EA-evidence revision was {comparison(full, evidence_ea)}. EA-RAG-style is a deterministic coverage-audit proxy, not an exact reproduction.
5. Source-rule upper bound: NA; no official decisive source span is local.
6. Selective revision positive net correction: {full.get('net_correction', 0) > 0}; test net={full.get('net_correction', 'NA')}, harm={full.get('harm_rate', 'NA')}, preserve net={preserve.get('net_correction', 'NA')}, standard-evidence net={evidence_standard.get('net_correction', 'NA')}, EA-evidence net={evidence_ea.get('net_correction', 'NA')}.
7. Harm-budget operating points were selected on development only. At the <=2% dev-budget threshold {selected}, test harm={primary_test['harm_rate']}, repairs={primary_test['repairs']}, harms={primary_test['harms']}, revision coverage={primary_test['revision_coverage']}, and answer-change coverage={primary_test['answer_change_coverage']}. At the <=1% dev-budget threshold {strict['threshold']}, test harm={strict_point['harm_rate']}, repairs={strict_point['repairs']}, harms={strict_point['harms']}, revision coverage={strict_point['revision_coverage']}, and answer-change coverage={strict_point['answer_change_coverage']}. Threshold comparison is inclusive (`score >= threshold`), so threshold 1.0 can still revise score-1.0 cases. The development budget is not a guarantee on test.
8. Baseline errors repaired: {full.get('repairs', 'NA')}.
9. Baseline-correct answers damaged: {full.get('harms', 'NA')}.
10. Component diagnosis: {bottleneck}.{failure_note}{artifact_note} These are coverage/contract diagnostics only; retrieval attribution remains limited by missing official evidence references.
11. Selective counterfactual decision revision supported: {support}. This is {'preliminary support under the stated post-calibration criteria' if support else 'not supported under the stated conservative criteria'}, not proof of a latent state model.
12. World-model claim: no; this is selective evidence-constrained revision.

## Main test metrics

{chr(10).join(table)}

MedEinst paired baseline diagnostics: control accuracy={medeinst.get('control_accuracy', 'NA')}, trap accuracy={medeinst.get('trap_accuracy', 'NA')}, both-correct pair accuracy={medeinst.get('both_correct_pair_accuracy', 'NA')}, Bias Trap Rate={medeinst.get('bias_trap_rate', 'NA')} among {medeinst.get('bias_trap_denominator', 'NA')} control-correct pairs, and original-diagnosis persistence={medeinst.get('old_answer_persistence', 'NA')}. Correct invariance is NA because all MedEinst pairs are change/trap pairs.

## Ablation diagnostics

{chr(10).join(ablation_lines) if ablation_lines else '- No supported ablation rows were available.'}

{ablation_caveat}

## Paired bootstrap comparisons

{chr(10).join(bootstrap_lines) if bootstrap_lines else '- No requested comparison rows were available.'}

## Gold-label oracle gate diagnostic (outside the main table)

The oracle gate could repair {oracle_repairs} baseline errors among already proposed full-method alternatives, with harms fixed to zero by construction because it uses test labels to revise only when correctness improves. This is analysis only and was not used for inference, threshold selection, or the main method table.

## Limitations and expansion decision

This is a single MedEinst pilot using a local all-Llama MedRGAG proxy. MedPIC official linked pairs, official delta metadata, decisive source references, retrieval Recall/MRR, the source-rule upper bound, and NICE are unavailable. The three-way delta-quality comparison is invalid because there is no official delta reference and LLM-only extraction produced {llm_delta['usable_output_count']}/{diagnostics['expected_pairs']} usable outputs. Delta nonempty coverage, document coverage, EA audit coverage, and rule contract rates are operational artifact diagnostics—not official delta accuracy, evidence recall, or MRR. Accuracy is strict normalized exact match: clinically related or potentially equivalent-in-context labels such as `Bronchitis` and `Chronic Bronchitis` count as different, and no post-hoc rescoring was performed. EA-RAG-style is a proxy reproduction. Thresholds were selected on development, while test was used only for final reporting. MedCounterFact and MediEval were not run under the frozen pilot; {'positive results make extension the next experiment' if support else 'the conservative stop decision is to diagnose the reported bottleneck before extension'}. CLIR remains a separate optional transition experiment.
"""
    (output_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "summary.md").write_text(summary, encoding="utf-8")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--proposals", type=Path, required=True)
    parser.add_argument("--deltas", type=Path, required=True)
    parser.add_argument("--retrieval", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics = evaluate(args.gold, args.baseline, args.proposals, args.deltas,
                       args.retrieval, args.rules, args.output_dir, args.bootstrap_samples)
    print(json.dumps({"selected_threshold": metrics["selected_threshold"],
                      "strict_threshold": metrics["strict_threshold"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
