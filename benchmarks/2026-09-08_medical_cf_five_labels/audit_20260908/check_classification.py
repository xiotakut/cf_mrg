#!/usr/bin/env python3
"""Read-only structural audit plus replayable, explicitly bounded semantic review.

Run: python3 medical_cf_collection/audit_20260908/check_classification.py
No model calls, prediction reads, new labels, or sampling changes.
"""
import argparse
import collections
import csv
import json
from pathlib import Path
import re
import sys

LABELS = {"R1", "R2", "R3", "R4", "R5"}
RESOLUTIONS = {"classified", "insufficient_evidence", "invalid_source", "outside_five_labels"}
METHODS = {"semantic_item_review", "semantic_group_review", "structural_verification"}
HERE = Path(__file__).resolve().parent


def read_jsonl(path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def check_record(row):
    """These are necessary structural conditions, never a semantic pass."""
    errors = []
    uid = row.get("unit_id")

    def add(code, detail, jid=None):
        errors.append(dict(unit_id=uid, judgment_id=jid, resource_id=row.get("resource_id"),
                           issue_code=code, severity="error", layer="structure", detail=detail))

    parents = row.get("labels", [])
    if not isinstance(parents, list) or set(parents) - LABELS or len(parents) != len(set(parents)):
        add("invalid_parent_labels", repr(parents))
        if not isinstance(parents, list):
            parents = []
    judgments = row.get("judgments")
    if not isinstance(judgments, list) or not judgments:
        add("missing_judgments", "每个比较单元须有具体判断，空标签也应保留已审理由。")
        return errors
    union = set()
    seen = set()
    for j in judgments:
        jid = j.get("judgment_id")
        labs = j.get("labels", [])
        if not jid or jid in seen:
            add("missing_or_duplicate_judgment_id", repr(jid), jid)
        seen.add(jid)
        if not isinstance(labs, list) or set(labs) - LABELS or len(labs) != len(set(labs)):
            add("invalid_child_labels", repr(labs), jid)
            continue
        union.update(labs)
        for key in ("target", "rationale", "cannot_infer"):
            if not isinstance(j.get(key), str) or not j[key].strip():
                add("missing_" + key, "具体判断缺少 " + key, jid)
        evidence = j.get("evidence", [])
        if labs and not any(isinstance(e, dict) and e.get("source_locator") and
                            any(e.get(k) for k in ("quote", "paraphrase", "derived_diff"))
                            for e in evidence):
            add("unlocated_label_evidence", "有标签但没有内容与原文位置同时存在的依据。", jid)
        if j.get("review_state") != "reviewed":
            add("unreviewed_judgment", str(j.get("review_state")), jid)
        resolution = j.get("review_resolution")
        if resolution not in RESOLUTIONS or bool(labs) != (resolution == "classified"):
            add("child_resolution_mismatch", str(resolution), jid)
        if j.get("status") != ("labeled" if labs else "uncertain"):
            add("child_status_mismatch", str(j.get("status")), jid)
        if j.get("review_method") not in METHODS:
            add("unknown_review_method", str(j.get("review_method")), jid)
        if "scoring_eligible" in j:
            if not isinstance(j["scoring_eligible"], bool) or not j.get("gold_review_status"):
                add("invalid_scoring_review", "评分可用性须为布尔值并有 gold 审阅状态。", jid)
            if j["scoring_eligible"] is False and not j.get("scoring_exclusion_reason"):
                add("unexplained_scoring_exclusion", "禁用原参考评分须注明原因。", jid)
    if union != set(parents):
        add("label_union_mismatch", f"parent={parents}; children={sorted(union)}")
    if row.get("review_state") != "reviewed":
        add("unreviewed_parent", str(row.get("review_state")))
    if bool(parents) != (row.get("review_resolution") == "classified"):
        add("parent_resolution_mismatch", str(row.get("review_resolution")))
    if row.get("status") != ("labeled" if parents else "uncertain"):
        add("parent_status_mismatch", str(row.get("status")))
    n = sum(bool(j.get("labels")) for j in judgments)
    for field, expected in (("reviewed_target_count", len(judgments)),
                            ("classified_target_count", n),
                            ("unclassified_target_count", len(judgments) - n)):
        if row.get(field) != expected:
            add("target_count_mismatch", f"{field}={row.get(field)}, expected={expected}")
    return errors


def run(input_path=None, output_dir=None):
    input_path = Path(input_path or HERE.parent / "分析子集.jsonl")
    output_dir = Path(output_dir or HERE / "classification")
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = list(read_jsonl(input_path))
    index = {r["unit_id"]: r for r in rows}
    errors = [e for row in rows for e in check_record(row)]
    if len(index) != len(rows):
        errors.append(dict(issue_code="duplicate_unit_ids", layer="structure", severity="error"))
    frozen = list(read_jsonl(HERE.parent / "review_20260908/input_manifest.jsonl"))
    if [r["unit_id"] for r in rows] != [r["unit_id"] for r in frozen]:
        errors.append(dict(issue_code="frozen_cohort_order_or_members_changed", layer="structure", severity="error"))

    # A review queue is not an automatic semantic rejection. Negated cautions in
    # rationale are deliberately not treated as the prohibited inference itself.
    queue = []
    for r in rows:
        for j in r["judgments"]:
            why = j.get("rationale", "")
            text = re.sub(r"[^。；;]*?(?:不能|不因|不是|并非|未|而非)[^。；;]*[。；;]?", "", why)
            codes = []
            if set(j["labels"]) & {"R1", "R2", "R3"} and re.search(r"(?:因为|由于|根据|由).{0,12}(?:答案|gold).{0,8}(?:变化|改变|翻转)", text):
                codes.append("possible_answer_flip_only_reason")
            if "R4" in j["labels"] and r["resource_id"] in {"M24", "M25"}:
                if j["judgment_id"].rsplit(":", 1)[-1] in {"prompt", "rephrase_prompt", "src", "rephrase"}:
                    codes.append("possible_direct_edit_restatement_as_R4")
            if not j["labels"] and re.search(r"^(?:尚未审阅|尚未逐题|未读题|待处理)", why):
                codes.append("possible_unreviewed_placeholder")
            if codes:
                queue.append(dict(unit_id=r["unit_id"], judgment_id=j["judgment_id"],
                                  resource_id=r["resource_id"], checks=codes, verdict="needs_semantic_review"))

    # Exact natural-language identity after removing only BioNLI entity markers.
    # Entity marker differences are preserved in the raw source; this is a gold
    # consistency warning, not a claim of byte-identical prompts.
    targets = collections.defaultdict(list)
    for r in rows:
        if r["resource_id"] == "M23":
            rec = r["original_records"][0]
            key = " ".join(re.sub(r"<(?:el|le|re|er)>", "", rec["context"]).split())
            targets[key].append((r, rec["response"]))
    gold_conflicts = []
    for items in targets.values():
        if len({gold for _, gold in items}) > 1:
            gold_conflicts.append(dict(issue_code="same_BioNLI_text_conflicting_gold",
                                       layer="source_gold_consistency", severity="review",
                                       comparison="ignore entity marker tags and whitespace only",
                                       units=[dict(unit_id=r["unit_id"], gold=gold) for r, gold in items],
                                       detail="相同自然语言前提/假设存在不同参考标签；不能据两端同一原参考保证正确保持。"))

    semantic_path = output_dir / "semantic_review.jsonl"
    semantic = list(read_jsonl(semantic_path)) if semantic_path.exists() else []
    sample_path = output_dir / "sample_manifest.jsonl"
    sample = list(read_jsonl(sample_path)) if sample_path.exists() else []
    reviewed_ids = {n["judgment_id"] for n in semantic}
    missing_sample = [n["judgment_id"] for n in sample if n["judgment_id"] not in reviewed_ids]
    incomplete_reasons = []
    if not sample:
        incomplete_reasons.append("固定语义抽查名单缺失或为空")
    if not semantic:
        incomplete_reasons.append("语义审核记录缺失或为空")
    if missing_sample:
        incomplete_reasons.append("固定抽查名单尚未全部审阅")
    if {r["resource_id"] for r in rows} - {n["resource_id"] for n in semantic}:
        incomplete_reasons.append("语义审核未覆盖全部实际收录来源")
    # Historical reviews stay immutable. A correction proposal merely requires a
    # new review; equality with the proposed `after` is never semantic approval.
    corrections = {}
    for path in sorted((HERE / "corrections").glob("*.jsonl")):
        for patch in read_jsonl(path):
            if "before" not in patch or "after" not in patch:
                continue
            jid = patch["judgment_id"]
            if jid in corrections:
                incomplete_reasons.append("重复修正子判断: " + jid)
            corrections[jid] = patch
    correction_path = output_dir / "correction_review.jsonl"
    correction_reviews = list(read_jsonl(correction_path)) if correction_path.exists() else []
    post = {}
    invalid_correction_reviews = []
    for note in correction_reviews:
        jid = note.get("judgment_id")
        r = index.get(note.get("unit_id"))
        j = next((x for x in r["judgments"] if x["judgment_id"] == jid), None) if r else None
        if (jid in post or not j or note.get("reviewed_annotation") != j
                or note.get("reviewed_original_records") != r.get("original_records")
                or not note.get("issue_code") or note.get("resource_id") != r.get("resource_id")
                or note.get("verdict") not in {"resolved", "unresolved"}
                or note.get("review_method") not in {"semantic_item_review", "semantic_group_review"}
                or not note.get("detail") or not note.get("grounding_sources")
                or note.get("classification_verdict") not in {"supported", "appropriately_unclassified", "needs_review"}
                or note.get("source_quality_status") not in {"no_open_issue", "excluded_original_reference"}
                or (note.get("verdict") == "resolved" and note.get("classification_verdict") == "needs_review")
                or (note.get("source_quality_status") == "excluded_original_reference"
                    and j.get("scoring_eligible") is not False)):
            invalid_correction_reviews.append(jid)
        else:
            post[jid] = note
    missing_correction_reviews = sorted(set(corrections) - set(post))
    if missing_correction_reviews:
        incomplete_reasons.append("修正清单尚未全部在最终导出记录上独立再审")
    if invalid_correction_reviews:
        incomplete_reasons.append("修正再审记录无效或与当前完整子判断不一致")
    unapplied_corrections = []
    for jid, patch in corrections.items():
        r = index.get(patch["unit_id"])
        j = next((x for x in r["judgments"] if x["judgment_id"] == jid), None) if r else None
        if j != patch["after"]:
            unapplied_corrections.append(jid)
    if unapplied_corrections:
        incomplete_reasons.append("部分修正补丁与当前导出不一致")
    stale = []
    findings, resolved = [], []
    historical_ids = {n["judgment_id"] for n in semantic}
    for note in semantic:
        r = index.get(note["unit_id"])
        j = next((x for x in r["judgments"] if x["judgment_id"] == note["judgment_id"]), None) if r else None
        changed = not j or any(j.get(k) != note["reviewed_annotation"].get(k)
                               for k in ("labels", "target", "rationale", "evidence"))
        current = post.get(note["judgment_id"])
        if changed and not current:
            stale.append(note["judgment_id"])
        if note["verdict"] != "supported":
            if current and current["verdict"] == "resolved":
                resolved.append(dict(note, resolution=current))
            elif not current:
                findings.append(dict(note, layer="semantic", severity="review"))
    for note in post.values():
        if note["verdict"] == "unresolved":
            findings.append(dict(note, layer="semantic", severity="review"))
        if note["source_quality_status"] == "excluded_original_reference":
            findings.append(dict(note, layer="source_gold_quality", severity="excluded_from_scoring",
                                 verdict="scoring_excluded", detail=note.get("source_quality_detail", note["detail"])))
    # Keep duplicate-gold group warnings separate, so group count cannot inflate
    # the count of concrete problematic judgments already represented above.
    for group in gold_conflicts:
        group["handling_status"] = ("reviewed_per_judgment" if all(
            u["unit_id"] + ":target_relation" in post for u in group["units"])
            else "needs_review")
    write_jsonl(output_dir / "source_gold_groups.jsonl", gold_conflicts)
    write_jsonl(output_dir / "resolved_findings.jsonl", resolved)
    write_jsonl(output_dir / "structure_findings.jsonl", errors)
    write_jsonl(output_dir / "review_queue.jsonl", queue)
    write_jsonl(output_dir / "findings.jsonl", findings)
    with (output_dir / "问题清单.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["来源", "unit_id", "judgment_id", "问题类别", "当前标签", "判断对象",
                         "理由", "审查结论", "问题说明", "建议", "依据链接"])
        for note in findings:
            r = index.get(note["unit_id"], {})
            annotation = next((j for j in r.get("judgments", []) if j["judgment_id"] == note["judgment_id"]),
                              note["reviewed_annotation"])
            source_url = r.get("source", {}).get("url", "")
            writer.writerow([note["resource_id"], note["unit_id"], note["judgment_id"], note["issue_code"],
                             ",".join(annotation["labels"]), annotation["target"], annotation["rationale"],
                             note["verdict"], note["detail"], note.get("recommendation", ""),
                             "\n".join(dict.fromkeys([source_url] + note.get("grounding_sources", [])))])
    source_counts = collections.Counter(r["resource_id"] for r in rows)
    # A single meaningful checker test: a changed parent union must be detected.
    labeled = next(r for r in rows if r["labels"])
    assert any(e["issue_code"] == "label_union_mismatch"
               for e in check_record(dict(labeled, labels=[])))
    audit_status = ("structural_failure" if errors else "incomplete" if incomplete_reasons or stale
                    else "issues_found" if findings or queue or any(g["handling_status"] == "needs_review" for g in gold_conflicts) else "passed_within_review_scope")
    summary = dict(
        input_file=str(input_path), audit_kind="read_only_classification_audit",
        audit_status=audit_status,
        units=len(rows), resources=len(source_counts), units_by_resource=dict(source_counts),
        judgments=sum(len(r["judgments"]) for r in rows),
        full_structure=dict(errors=len(errors), checked_units=len(rows),
                            verdict="pass" if not errors else "fail", semantic_validity_proved=False),
        label_counts=dict(collections.Counter(l for r in rows for l in r["labels"])),
        judgment_resolution_counts=dict(collections.Counter(j["review_resolution"] for r in rows for j in r["judgments"])),
        heuristic_review_queue=len(queue), source_gold_conflict_groups=len(gold_conflicts),
        semantic_review=dict(record_role="pre_correction_historical_review",
                             reviewed_judgments=len(semantic),
                             reviewed_units=len({n["unit_id"] for n in semantic}),
                             reviewed_resources=len({n["resource_id"] for n in semantic}),
                             base_sample_judgments=sum(n["selection_method"] == "fixed_stratified_sample" for n in semantic),
                             rule_expansion_judgments=sum(n["selection_method"] == "targeted_rule_expansion" for n in semantic),
                             verdict_counts=dict(collections.Counter(n["verdict"] for n in semantic)),
                             base_sample_verdict_counts=dict(collections.Counter(n["verdict"] for n in semantic if n["selection_method"] == "fixed_stratified_sample")),
                             issue_counts=dict(collections.Counter(n["issue_code"] for n in semantic if n.get("issue_code"))),
                             missing_sample_judgments=missing_sample,
                             incomplete_reasons=incomplete_reasons,
                             stale_reviews=stale, all_units_semantically_audited=False,
                             selection="冻结文件物理顺序；按来源×标签取首个三分位、首/后三分位/末位，另取空标签中位；发现规则错误后明确扩查。未用模型结果。"),
        correction_review=dict(
            proposed_corrections=len(corrections), reviewed_judgments=len(post),
            additional_to_historical_review=len(set(post) - historical_ids),
            unique_reviewed_judgments_across_rounds=len(set(post) | historical_ids),
            verdict_counts=dict(collections.Counter(n["verdict"] for n in post.values())),
            historical_problems_resolved=len(resolved),
            remaining_label_problems=sum(n["layer"] == "semantic" for n in findings),
            gold_scoring_exclusions=sum(n["layer"] == "source_gold_quality" for n in findings),
            missing_reviews=missing_correction_reviews,
            invalid_reviews=invalid_correction_reviews,
            unapplied_corrections=unapplied_corrections,
            history_file=str(semantic_path), current_review_file=str(correction_path),
            procedure="独立读取最终原题、原参考、编辑内容与当前完整子判断后审阅；修正声明和 before/after 相等不等于语义通过。"),
        limitations=["结构通过只证明字段、目标绑定和审阅状态自洽，不证明医学关系或 gold 正确。",
                     "语义审核为非概率、按来源与标签的固定目的抽查及规则扩查，不能把发现比例估计成全库错误率。",
                     "R5 的原任务保持要求与原参考事实可靠性分别检查；未临床专家验收。",
                     "2497 条缺图多模态单元只审核已发布元数据；未进行图像真实性或图像诊断验收。"],
        predictions_read=False, source_or_labels_modified=False)
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    result = run(args.input, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit({"passed_within_review_scope": 0, "issues_found": 1,
              "structural_failure": 2, "incomplete": 3}[result["audit_status"]])
