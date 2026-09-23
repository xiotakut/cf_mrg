"""Check public saved metadata only. Stdlib; no source data, model or re-scoring."""
from collections import Counter
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


A1_FIELDS = "method request_id variant baseline_variant expert_variant arm run_status native_valid audit_status decision failure_type audit_failure_codes a1_qualified_proposals adjudication_calls method_score correct new_model_requests input_tokens output_tokens model_seconds cost_basis".split()
A3_FIELDS = "method request_id variant correct native_mapping_count native_available method_score applicability shared_experiment_valid_edits shared_experiment_rejected_edits edit_semantic_invalid run_status zero_probe_fallback actual_final_generation own_requests logical_model_requests logical_input_tokens logical_output_tokens logical_model_seconds cost_basis new_a3_candidate_adopted".split()
VARIANTS = ["strong_old_native_interface_v2", "same_readout_shared_prefix", "critical_edit", "random_edit", "original_rescore"]
EXPECTED_COUNTS = {"M4": [3, 3, 4, 3, 4], "M5": [4, 4, 3, 3, 4]}
EXPECTED_UNIT_MEANS = {"M4": [.5, .5, .75, .5, .75], "M5": [.5, .5, .25, .25, .5]}
FORBIDDEN_KEYS = {"native_answer", "native_proposal", "raw_response", "messages", "semantic_gold", "gold", "patient", "evidence_text", "step_by_step_thinking", "answer_choice"}
EXPECTED_EXPORTS = {"baseline_interface_summary.json", "a2_parser_summary.json", "trace_attribution_summary.json", "a1_delta_summary.json", "a3_development_summary.json", "cost_summary.json", "readiness_summary.json", "a1_arm_status.csv", "a3_input_status.csv"}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def near(a, b):
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-6)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def read_json(root, name):
    return json.loads((root / name).read_text(encoding="utf-8"))


def read_csv(root, name, fields):
    with (root / name).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == fields, f"{name}: exact CSV field allowlist")
        rows = list(reader)
    require(all(set(r) == set(fields) and None not in r.values() for r in rows), f"{name}: malformed CSV")
    return rows


def check_json_fields(value, where):
    if isinstance(value, dict):
        require(not FORBIDDEN_KEYS.intersection(value), f"{where}: prohibited content field")
        for key, child in value.items():
            check_json_fields(child, where + "/" + key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            check_json_fields(child, where + f"/{i}")


def anchors(path):
    content = path.read_text(encoding="utf-8")
    found = set(re.findall(r'<a\s+id=["\']([^"\']+)', content, flags=re.I))
    repeated = Counter()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", content, flags=re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        suffix = "" if not repeated[slug] else "-" + str(repeated[slug])
        found.add(slug + suffix)
        repeated[slug] += 1
    return found


def check_links(root):
    checked = 0
    pattern = re.compile(r"!?\[[^\]\n]+\]\((<[^>]+>|[^)\n]+)\)")
    for source in root.rglob("*.md"):
        content = source.read_text(encoding="utf-8")
        targets = [m.group(1) for m in pattern.finditer(content)]
        targets += re.findall(r"^\[[^\]\n]+\]:\s*(\S+)\s*$", content, flags=re.M)
        for target in targets:
            target = target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            else:
                target = re.sub(r'\s+["\'][^"\']*["\']$', "", target)
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//"):
                continue
            require(not target.startswith("/"), f"absolute local Markdown link: {source.name}: {target}")
            dest = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
            require(dest.is_relative_to(root.parent), f"Markdown link leaves package/sibling bundle: {target}")
            require(dest.exists(), f"missing Markdown target: {source}: {target}")
            if parsed.fragment and dest.suffix.lower() == ".md":
                require(unquote(parsed.fragment) in anchors(dest), f"missing Markdown anchor: {source}: {target}")
            checked += 1
    return checked


def check_manifest(root):
    manifest = read_json(root, "SOURCE_MANIFEST.json")
    require(isinstance(manifest, list) and manifest, "SOURCE_MANIFEST must be a nonempty list")
    paths = set()
    for row in manifest:
        require(isinstance(row, dict), "manifest row must be object")
        name = row["published_path"]
        dest = (root / name).resolve()
        require(not Path(name).is_absolute() and dest.is_relative_to(root), "published path escapes package")
        require(name not in paths, "duplicate published path")
        paths.add(name)
        require(dest.is_file(), f"published file missing: {name}")
        require(is_sha(row["published_sha256"]) and sha(dest) == row["published_sha256"], f"published hash: {name}")
        require(isinstance(row["source_path"], str) and is_sha(row["source_sha256"]), f"source metadata missing: {name}")
        # Source paths are provenance strings. Never resolve or open them.
    require({"data/" + name for name in EXPECTED_EXPORTS}.issubset(paths), "manifest misses required public data")
    export = read_json(root, "DATA_EXPORT_MANIFEST.json")
    require(export["new_model_calls"] == export["new_native_scoring_calls"] == 0, "export unexpectedly ran inference/scoring")
    require(EXPECTED_EXPORTS == set(export["exports"]), "export file set")
    for name, record in export["exports"].items():
        dest = root / "data" / name
        require(sha(dest) == record["sha256"], f"export hash: {name}")
        require(dest.stat().st_size == record["bytes"], f"export bytes: {name}")
        require(record["transformation"] and record["source_names"], f"export provenance: {name}")
        for src in record["source_names"]:
            item = export["sources"][src]
            require(isinstance(item["path"], str) and is_sha(item["sha256"]), f"source hash metadata: {src}")
    return len(manifest)


def check_a1(root):
    rows = read_csv(root, "data/a1_arm_status.csv", A1_FIELDS)
    summary = read_json(root, "data/a1_delta_summary.json")
    require(len(rows) == len({(r["method"], r["request_id"], r["arm"]) for r in rows}) == 24, "A1 24 unique input-arm records")
    require(summary["diagnostic_denominator"] == summary["audit_unavailable"] == 6, "A1 diagnostic denominator/failure")
    require(summary["qualified_support_proposals"] == summary["adjudication_model_calls"] == 0, "A1 qualification")
    require(summary["quality_scored"] is False, "A1 never quality-scored")
    expected_arms = {"baseline", "targeted_reanswer", "delta_adjudication", "unconditional_reanswer"}
    for method in ("M4", "M5"):
        chosen = [r for r in rows if r["method"] == method]
        require(len(chosen) == 12 and len({r["request_id"] for r in chosen}) == 3, "A1 bone denominator")
        for request_id in {r["request_id"] for r in chosen}:
            require({r["arm"] for r in chosen if r["request_id"] == request_id} == expected_arms, "A1 exact four arms")
        receipt = next(r for r in summary["per_backbone"] if r["method"] == method)
        for col, field in [("new_model_requests", "new_model_requests"), ("input_tokens", "live_input_tokens"), ("output_tokens", "live_output_tokens"), ("model_seconds", "live_model_seconds")]:
            require(near(sum(float(r[col]) for r in chosen), receipt["actual_cost"][field]), f"A1 cost {method}/{col}")
    require(all(r["method_score"] == "not_scored" and r["correct"] == "" for r in rows), "A1 quality unavailable")
    require(all(r["run_status"] == "complete" and r["native_valid"] == "True" for r in rows), "A1 saved-result availability")
    require(all(r["baseline_variant"] == "strong_old_native_interface_v2" for r in rows), "A1 baseline identity")
    delta = [r for r in rows if r["arm"] == "delta_adjudication"]
    require(len(delta) == 6 and all(r["expert_variant"] == summary["variant"] and r["audit_status"] == "audit_unavailable" and r["decision"] == "audit_unavailable_reuse_B" and r["a1_qualified_proposals"] == r["adjudication_calls"] == "0" for r in delta), "A1 six unavailable audits with zero adjudication")
    drafts = [r for r in rows if r["audit_failure_codes"] == "output_truncation"]
    require(len(drafts) == 2 and all(r["method"] == "M4" and r["request_id"] == "d00003" for r in drafts), "two preserved control draft truncations")
    require(sum(int(r["new_model_requests"]) for r in rows) == 28, "A1/control physical calls")
    return rows


def check_a3(root):
    rows = read_csv(root, "data/a3_input_status.csv", A3_FIELDS)
    summary = read_json(root, "data/a3_development_summary.json")
    require(len(rows) == len({(r["method"], r["request_id"], r["variant"]) for r in rows}) == 80, "A3 80 unique records")
    require(not summary["candidate_adopted"] and not summary["independent_evaluation"] and not summary["full_121_replaced"], "A3 development-only negative identity")
    require(len(summary["native_panel_unit_metrics"]) == 10, "A3 ten unit summaries")
    for method in ("M4", "M5"):
        report = next(r for r in summary["methods"] if r["method"] == method)
        chosen = [r for r in rows if r["method"] == method]
        ids = {r["request_id"] for r in chosen}
        require(len(chosen) == 40 and len(ids) == 8, "A3 backbone panel denominator")
        require(not report["incremental_count_gate"], "A3 gate remains negative")
        by_variant = {}
        for i, variant in enumerate(VARIANTS):
            group = [r for r in chosen if r["variant"] == variant]
            require(len(group) == 8 and {r["request_id"] for r in group} == ids, "A3 exact alternative membership")
            require(all(r["correct"] in {"True", "False", ""} for r in group), "A3 boolean/unknown correctness only")
            count = {"correct": sum(r["correct"] == "True" for r in group), "incorrect": sum(r["correct"] == "False" for r in group), "unavailable": sum(r["correct"] == "" for r in group), "denominator": 8}
            require(count == report["unique_input_counts"][variant], "A3 stored unique counts")
            require(count == report["native_record_counts"][variant] and count["correct"] == EXPECTED_COUNTS[method][i], "A3 native count equality and expected snapshot")
            require(all(r["native_mapping_count"] == "1" and r["method_score"] == "scored" and r["native_available"] == "True" for r in group), "A3 one native mapping per available result")
            metric = next(r for r in summary["native_panel_unit_metrics"] if r["method"] == method and r["variant"] == variant)
            require(metric["panel_nonreference_units"] == 4 and near(metric["panel_mean_native_unit_score"], EXPECTED_UNIT_MEANS[method][i]), "A3 four-unit recorded means")
            by_variant[variant] = {r["request_id"]: r for r in group}
        for variant, comparisons in report["comparison"].items():
            for control, expected in comparisons.items():
                repairs, harms, recovered = [], [], 0
                for rid in ids:
                    new, old = by_variant[variant][rid]["correct"], by_variant[control][rid]["correct"]
                    if old == "False" and new == "True": repairs.append(rid)
                    if old == "True" and new == "False": harms.append(rid)
                    if old == "" and new != "": recovered += 1
                require(len(repairs) == expected["repairs"] and len(harms) == expected["harms"] and recovered == expected["unavailable_recoveries"], "A3 repair/harm/recovery counts")
                require(sorted(repairs) == sorted(expected["repair_ids"]) and sorted(harms) == sorted(expected["harm_ids"]), "A3 transition identities")
    experimental = [r for r in rows if r["variant"] in {"critical_edit", "random_edit", "original_rescore"}]
    require(len(experimental) == 48, "A3 48 experimental arms")
    require(sum(r["actual_final_generation"] == "True" for r in rows) == 45 and sum(r["zero_probe_fallback"] == "True" for r in rows) == 3, "A3 45 actual finals, three zero-probe fallback results")
    for row in experimental:
        fallback = row["zero_probe_fallback"] == "True"
        require((row["actual_final_generation"] == "True") != fallback, "A3 final versus fallback disjoint")
        require(row["new_a3_candidate_adopted"] == "False" and row["cost_basis"] == "logical_arm_includes_shared_prefix_do_not_sum_across_arms", "A3 identity and logical-cost warning")
        require(int(row["logical_model_requests"]) >= int(row["own_requests"]), "A3 logical versus own calls")
        require(float(row["logical_model_seconds"]) >= 0, "A3 nonnegative recorded duration")
        if fallback:
            require(row["method"] == "M5" and row["request_id"] == "d00077" and row["applicability"] == "partial", "A3 fixed preserved zero-probe scope")
    for method in ("M4", "M5"):
        one_per_input = [r for r in experimental if r["method"] == method and r["variant"] == "critical_edit"]
        structure = summary["execution_structure"][method]
        require(sum(int(r["shared_experiment_valid_edits"]) for r in one_per_input) == structure["valid_edits"], "A3 valid edits")
        require(sum(int(r["shared_experiment_rejected_edits"]) for r in one_per_input) == structure["rejected_edits"], "A3 rejected edits")
        require(sum(int(r["shared_experiment_rejected_edits"]) > 0 for r in one_per_input) == structure["inputs_with_rejected_edits"], "A3 affected inputs retained")
    return rows


def check_cost(root, a1rows):
    cost = read_json(root, "data/cost_summary.json")
    require(len(cost["entries"]) == 6 and len({(r["stage"], r["method"]) for r in cost["entries"]}) == 6, "six unique physical run cost entries")
    expected = {"new_model_requests": 254, "live_input_tokens": 924870, "live_output_tokens": 18483, "live_model_seconds": 447.2974530088686}
    for key, total in expected.items():
        require(near(sum(r["cost"][key] for r in cost["entries"]), total) and near(cost["total"][key], total), "physical cost sum " + key)
        a3total = sum(r["cost"][key] for r in cost["entries"] if r["stage"] != "incremental_smoke")
        require(near(a3total, cost["a3_full_panel_physical_cost"]["overall"][key]), "A3 smoke reused once in physical total")
    require(cost["old_head_regeneration_requests"] == cost["independent_evaluation_calls"] == 0 and cost["quality_scoring_calls"] == 1, "recorded call/scoring identities")
    require(sum(int(r["new_model_requests"]) for r in a1rows) + cost["a3_full_panel_physical_cost"]["overall"]["new_model_requests"] == 254, "A1 plus A3 nonduplicated total")
    return cost["total"]


def validate(root):
    root = Path(root).resolve()
    checked_json = 0
    for path in root.rglob("*.json"):
        value = json.loads(path.read_text(encoding="utf-8"))
        if path.is_relative_to(root / "data"):
            check_json_fields(value, str(path.relative_to(root)))
        checked_json += 1
    manifest_entries = check_manifest(root)
    a1rows = check_a1(root)
    a3rows = check_a3(root)
    cost = check_cost(root, a1rows)
    b = read_json(root, "data/baseline_interface_summary.json")
    require(b["answer_values_preserved"] == b["unique_rows"] == 242 and b["native_valid"] == 241 and b["unavailable"] == 1, "B unchanged values and retained invalid result")
    a2 = read_json(root, "data/a2_parser_summary.json")
    require(a2["unique_original_executor_responses"] == 2 and a2["request_comparisons"] == 18 and not a2["actual_model_preflight_passed"], "A2 cache-only acceptance")
    trace = read_json(root, "data/trace_attribution_summary.json")
    require(trace["rows"] == 36 and sum(r["repair_count"] for r in trace["by_method"].values()) == 10 and sum(r["harm_count"] for r in trace["by_method"].values()) == 26, "trace attribution scope")
    ready = read_json(root, "data/readiness_summary.json")
    require(not ready["compact_control"]["control_implemented"] and ready["new_A5"] == "not_implemented_or_run" and ready["no_independent_evaluation"] and ready["common_freeze"] == "not_completed", "uncompleted stages retained")
    links = check_links(root)
    return {"status": "passed", "json_files": checked_json, "manifest_entries": manifest_entries, "a1_input_arm_rows": len(a1rows), "a3_input_alternative_rows": len(a3rows), "a3_real_final_generations": 45, "a3_zero_probe_fallback_results": 3, "physical_cost": cost, "local_markdown_links": links, "new_model_calls": 0, "native_rescoring_calls": 0, "local_original_source_files_opened": False, "scope": "Public-file hashes, strict field sets, recorded counts/transitions/costs and relative Markdown links only.", "limitations": ["No original cases, source manifests' file contents, gold, model calls or native scorer accessed.", "Four-unit means are compared with the fixed published snapshot; original unit/label mapping is not reconstructed from the80-row CSV.", "This is publication consistency checking, not independent scientific replication or method adoption."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(validate(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
