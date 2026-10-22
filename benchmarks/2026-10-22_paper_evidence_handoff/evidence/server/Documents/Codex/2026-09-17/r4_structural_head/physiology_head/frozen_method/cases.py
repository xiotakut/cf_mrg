"""Frozen action/time predicate grid; generate only the explicitly requested split.

Build with the existing numerical Python environment:
    python cases.py build --split dev
The heldout branch is implemented; the parent task will release its execution
after the development freeze. This is a team-plan boundary, not user approval.
"""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import executor

HERE = Path(__file__).resolve().parent
PROBE = HERE.parent / "physiology_probe"
TIMES = [30, 60, 120]
SCENES = ["A", "B", "C", "D"]


def freeze_plan():
    prior = json.loads((PROBE / "plan.json").read_text())
    plan = {
        "version": "simglucose_visible_state_v1",
        "source_commit": prior["source_commit"],
        "development_patient_ids": prior["development_patient_ids"],
        "held_out_patient_ids": prior["held_out_patient_ids"],
        "horizon_min": 120, "times_min": TIMES,
        "initialization": "all 13 author x0 values plus explicit author reset auxiliary values; no randomization",
        "factual": "author basal throughout [0,120); one 30g meal announcement at t=0; one 2U bolus over [0,1)",
        "scenes": {
            "A": "basal multiplier .5 on [0,60), then 1; original bolus retained",
            "B": "remove t=0 bolus; basal unchanged",
            "C": "move 2U bolus from t=0 to t=30; basal unchanged",
            "D": "increase t=0 bolus from 2U to 4U; basal unchanged",
        },
        "predicate_rule": "(scene_index + time_index) % 3, indices reset for each profile",
        "predicates": [
            {"quantity": "counterfactual", "comparison": "ge", "threshold": 180},
            {"quantity": "difference", "comparison": "le", "threshold": -5},
            {"quantity": "counterfactual", "comparison": "lt", "threshold": 140},
        ],
        "readout": "gsub; state[12]/Vg; mg/dL; no sensor",
        "questions_per_profile": 12, "development_questions": 72, "held_out_questions": 288,
        "solver": {"rtol": 1e-6, "atol": 1e-12},
        "tighter_solver": {"rtol": 1e-9, "atol": 1e-13},
        "selection": "no filtering, answer balancing, threshold adjustment or post-result replacement",
        "inference_visibility": "native_input and question only; oracle_ir/oracle_patch/results in separate evaluation file",
    }
    path = HERE / "case_plan.json"
    if path.exists():
        saved = json.loads(path.read_text())
        if {k: v for k, v in saved.items() if k != "created_at"} != plan:
            raise ValueError("Existing frozen plan differs from this implementation")
        return saved
    plan["created_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(plan, indent=2) + "\n")
    return plan


def native_input(row):
    params = {key: value if key == "Name" else float(value) for key, value in row.items()}
    state = [params[key] for key in list(row)[2:15]]
    return {
        "params": params,
        "initial_state": state,
        "reset_auxiliary": {
            "last_Qsto_mg": state[0] + state[1], "last_foodtaken_g": 0,
            "last_action": {"CHO": 0, "insulin": 0},
            "is_eating": False, "planned_meal_g": 0,
        },
        "horizon_min": 120,
        "meal_announcements": [{"time_min": 0, "grams": 30}],
        "factual_basal": [{"start_min": 0, "end_min": 120,
                           "rate_U_per_min": params["u2ss"] * params["BW"] / 6000}],
        "factual_boluses": [{"time_min": 0, "units": 2}],
    }


def action_and_patch(scene):
    basal = [{"start_min": 0, "end_min": 120, "multiplier": 1}]
    boluses = [{"time_min": 0, "units": 2}]
    patch = {"basal_changes": [], "bolus_changes": []}
    if scene == "A":
        basal = [{"start_min": 0, "end_min": 60, "multiplier": .5},
                 {"start_min": 60, "end_min": 120, "multiplier": 1}]
        patch["basal_changes"] = [{"start_min": 0, "end_min": 60, "multiplier": .5}]
    elif scene == "B":
        boluses = []
        patch["bolus_changes"] = [{"from_time_min": 0, "to_time_min": 0, "units": 0}]
    elif scene == "C":
        boluses = [{"time_min": 30, "units": 2}]
        patch["bolus_changes"] = [{"from_time_min": 0, "to_time_min": 30, "units": 2}]
    elif scene == "D":
        boluses = [{"time_min": 0, "units": 4}]
        patch["bolus_changes"] = [{"from_time_min": 0, "to_time_min": 0, "units": 4}]
    else:
        raise ValueError(scene)
    return {"basal": basal, "boluses": boluses}, patch


def question(scene, query):
    action = {
        "A": "the basal insulin rate were halved during minutes [0,60) and restored to its factual rate during [60,120), while the original 2 U bolus at minute 0 were retained",
        "B": "the original 2 U bolus at minute 0 were omitted, while the factual basal insulin schedule were retained",
        "C": "the original 2 U bolus were moved from minute 0 to minute 30, while the factual basal insulin schedule were retained",
        "D": "the bolus at minute 0 were increased from 2 U to 4 U, while the factual basal insulin schedule were retained",
    }[scene]
    minute = query["time_min"]
    predicate = {
        ("counterfactual", "ge"): f"counterfactual subcutaneous glucose (Gsub) be at least 180 mg/dL at minute {minute}",
        ("difference", "le"): f"counterfactual subcutaneous glucose (Gsub) be at least 5 mg/dL lower than factual Gsub at minute {minute}",
        ("counterfactual", "lt"): f"counterfactual subcutaneous glucose (Gsub) be below 140 mg/dL at minute {minute}",
    }[(query["quantity"], query["comparison"])]
    return (
        "Use the supplied physiological model, complete initial state, patient parameters, "
        "and factual meal/insulin program. Keep the meal and initial state unchanged. "
        "Each bolus is delivered over the single one-minute interval beginning at its stated time, "
        "in addition to basal insulin. "
        f"Report counterfactual Gsub at minute {minute} in mg/dL and its difference "
        "(counterfactual minus factual) from Gsub under the supplied factual program at the same minute. "
        f"Would {predicate} if {action}?"
    )


def _line(handle, value):
    handle.write(json.dumps(value, allow_nan=False) + "\n")


def build(split):
    started = time.monotonic()
    plan = freeze_plan()  # Written before any patient construction or trajectory.
    profiles = plan["development_patient_ids" if split == "dev" else "held_out_patient_ids"]
    destination = HERE / split
    destination.mkdir(exist_ok=True)
    if (destination / "inputs.jsonl").exists():
        raise FileExistsError("Existing case artifacts retained; build in a fresh authorized split")
    with (PROBE / "author/simglucose/params/vpatient_params.csv").open() as handle:
        rows = {row["Name"]: row for row in csv.DictReader(handle) if row["Name"] in profiles}
    if set(rows) != set(profiles):
        raise ValueError("A preselected source patient is missing")
    numerical = {"split": split, "profiles": profiles, "normal_solver": plan["solver"],
                 "tighter_solver": plan["tighter_solver"], "trajectories": [], "items": []}
    count, yes_count, max_error = 0, 0, 0.0
    with (destination / "inputs.jsonl").open("w") as inputs, \
         (destination / "evaluation.jsonl").open("w") as evaluation, \
         (destination / "oracle_trajectories.jsonl").open("w") as trajectories:
        for profile in profiles:
            native = native_input(rows[profile])
            factual = executor.simulate(native, **plan["solver"])
            factual_tight = executor.simulate(native, **plan["tighter_solver"])

            def record_trace(scene, normal, tight):
                nonlocal max_error
                error = max(abs(a["Gsub_mg_dL"] - b["Gsub_mg_dL"])
                            for a, b in zip(normal["trajectory"], tight["trajectory"]))
                max_error = max(max_error, error)
                numerical["trajectories"].append({"profile": profile, "scene": scene,
                                                    "max_gsub_abs_error_mg_dL": error})
                _line(trajectories, {"profile": profile, "scene": scene, **normal})

            record_trace("factual", factual, factual_tight)
            for scene_index, scene in enumerate(SCENES):
                action, patch = action_and_patch(scene)
                cf = executor.simulate(native, action, **plan["solver"])
                cf_tight = executor.simulate(native, action, **plan["tighter_solver"])
                record_trace(scene, cf, cf_tight)
                for time_index, minute in enumerate(TIMES):
                    predicate = plan["predicates"][(scene_index + time_index) % 3]
                    query = {"time_min": minute, "readout": "gsub", **predicate}
                    result = executor.project(factual, cf, query)
                    tight_result = executor.project(factual_tight, cf_tight, query)
                    item_id = f"phys_{split}_{profile.replace('#', '_')}_{scene}_t{minute:03}"
                    meta = {"item_id": item_id, "profile": profile, "scene": scene}
                    _line(inputs, {**meta, "native_input": native, "question": question(scene, query)})
                    _line(evaluation, {**meta, "oracle_ir": {**action, "query": query},
                                       "oracle_patch": {**patch, "query": query},
                                       "counterfactual_value": result["counterfactual_value"],
                                       "factual_value": result["factual_value"],
                                       "difference": result["difference"],
                                       "gold": result["answer_choice"],
                                       "threshold_margin": result["threshold_margin"]})
                    errors = {key: abs(result[key] - tight_result[key])
                              for key in ["counterfactual_value", "factual_value", "difference", "predicate_value"]}
                    numerical["items"].append({**meta, "query": query, "absolute_errors": errors,
                                              "normal_margin": result["threshold_margin"],
                                              "tight_margin": tight_result["threshold_margin"],
                                              "normal_answer": result["answer_choice"],
                                              "tight_answer": tight_result["answer_choice"],
                                              "binary_changed": result["answer_choice"] != tight_result["answer_choice"]})
                    yes_count += result["answer_choice"] == "yes"
                    count += 1
    assert count == len(profiles) * 12
    numerical.update({
        "questions": count, "unique_profiles_simulated": len(profiles),
        "integrations": len(profiles) * 5 * 2,
        "one_minute_integration_steps": len(profiles) * 5 * 2 * 120,
        "held_out_profiles_simulated": len(profiles) if split == "heldout" else 0,
        "max_trajectory_gsub_abs_error_mg_dL": max_error,
        "max_query_quantity_abs_error_mg_dL": max(i["absolute_errors"]["predicate_value"] for i in numerical["items"]),
        "minimum_threshold_margin_mg_dL": min(i["normal_margin"] for i in numerical["items"]),
        "binary_changed_ids": [i["item_id"] for i in numerical["items"] if i["binary_changed"]],
        "yes_count": yes_count, "no_count": count - yes_count,
        "elapsed_seconds": time.monotonic() - started,
    })
    (destination / "numerical_check.json").write_text(json.dumps(numerical, indent=2) + "\n")
    print(json.dumps({k: v for k, v in numerical.items() if k not in ["items", "trajectories"]}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["build"])
    parser.add_argument("--split", choices=["dev", "heldout"], required=True)
    args = parser.parse_args()
    build(args.split)


if __name__ == "__main__":
    main()
