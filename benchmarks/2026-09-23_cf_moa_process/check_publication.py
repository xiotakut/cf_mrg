"""Check this documentation package; no inference, labels, or native re-scoring."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def anchors(path):
    content = path.read_text(encoding="utf-8")
    found = set(re.findall(r'<a\s+id=["\']([^"\']+)', content))
    repeated = Counter()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", content, flags=re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        suffix = "" if not repeated[slug] else "-" + str(repeated[slug])
        found.add(slug + suffix)
        repeated[slug] += 1
    return found


def main():
    checked_json = 0
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
        checked_json += 1

    manifest = read_json("SOURCE_MANIFEST.json")
    for row in manifest:
        path = ROOT / row["published_path"]
        assert path.is_file(), str(path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["published_sha256"], str(path)

    with (ROOT / "data/per_input_status.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 242
    assert len({(r["method"], r["request_id"]) for r in rows}) == 242
    summary = read_json("data/comparison_summary.json")
    assert summary["independent_evaluation"] is False
    assert summary["method_adopted"] is False
    assert summary["strict_realized_compute_matching"] is False
    for bone in summary["summaries"]:
        selected = [r for r in rows if r["method"] == bone["method"]]
        assert len(selected) == 121
        for name, result in {"candidate": bone["candidate"], **bone["controls"]}.items():
            actual = Counter(r[name] for r in selected)
            assert {k: actual[k] for k in ("correct", "incorrect", "unavailable")} == result["unique_states"]
            assert result["unique_inputs"] == 121 and result["native_mappings"] == 157
        for control in bone["controls"]:
            actual = {a: {b: 0 for b in ("correct", "incorrect", "unavailable")}
                      for a in ("correct", "incorrect", "unavailable")}
            for row in selected:
                actual[row[control]][row["candidate"]] += 1
            assert actual == bone["comparisons"][control]["unique"]["matrix"]

    evidence = read_json("data/evidence_use_summary.json")
    for bone in ("m4", "m5"):
        item = evidence["by_backbone"][bone]
        assert sum(item["initial_activation_distribution"].values()) == 121
        assert item["cohorts"]["all"]["denominator"] == 121
    assert evidence["combined"]["cohorts"]["all"]["denominator"] == 242
    assert evidence["new_model_calls"] == evidence["native_rescoring_calls"] == 0

    ep = read_json("data/ep_execution_receipt.json")
    c3 = read_json("data/fixed3_execution_receipt.json")
    for field in ("model_requests", "input_tokens", "output_tokens"):
        assert sum(b["candidate"]["cost"]["new"][field] for b in summary["summaries"]) == ep["actual_new_cost"][field]
        assert sum(b["candidate"]["cost"]["historical_reused_head"][field] for b in summary["summaries"]) == ep["historical_cost"][field]
    assert c3["new_draws"] == 481 and c3["historical_sampling_draws"] == 245
    assert c3["logical_draws"] == 726
    assert sum(b["controls"]["fixed3_sampling"]["cost"]["new"]["model_requests"] for b in summary["summaries"]) == 481
    assert read_json("data/non_adoption_decision.json")["decision"] == "not_adopted_preserve_negative_development_result"
    assert read_json("data/development_delivery_index.json")["all_goal_requirements_completed"] is False

    checked_links = 0
    link_pattern = re.compile(r"!?\[[^\]\n]+\]\((<[^>]+>|[^)\n]+)\)")
    for source in ROOT.rglob("*.md"):
        content = source.read_text(encoding="utf-8")
        targets = [m.group(1) for m in link_pattern.finditer(content)]
        targets += re.findall(r"^\[[^\]\n]+\]:\s*(\S+)\s*$", content, flags=re.M)
        for raw_target in targets:
            target = raw_target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//"):
                continue
            assert not target.startswith("/"), (str(source), target)
            dest = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
            assert dest.exists(), (str(source), target)
            if parsed.fragment and dest.suffix == ".md":
                assert unquote(parsed.fragment) in anchors(dest), (str(source), target)
            checked_links += 1

    print(json.dumps({"status": "passed", "json_files": checked_json,
                      "source_manifest_entries": len(manifest), "unique_rows": len(rows),
                      "local_links": checked_links, "new_model_calls": 0,
                      "native_rescoring_calls": 0,
                      "scope": "Publication hashes, existing state counts/transitions/costs and Markdown links; not a new scientific validation."},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
