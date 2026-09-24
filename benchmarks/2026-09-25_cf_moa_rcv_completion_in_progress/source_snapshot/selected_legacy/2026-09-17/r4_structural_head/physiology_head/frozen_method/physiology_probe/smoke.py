"""One preselected virtual patient; author ODE and step, no gym or sensor."""
import csv
import importlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent


def load_patient():
    # Use the existing OS setuptools helper; do not install into either environment.
    if importlib.util.find_spec("pkg_resources") is None:
        sys.path.append("/usr/lib/python3/dist-packages")
    # Skip only simglucose's gym registration; load the original patient submodule.
    root = HERE / "author" / "simglucose"
    spec = importlib.util.spec_from_file_location(
        "simglucose", root / "__init__.py", submodule_search_locations=[str(root)]
    )
    sys.modules["simglucose"] = importlib.util.module_from_spec(spec)
    return importlib.import_module("simglucose.patient.t1dpatient")


def auxiliary(patient):
    return {
        "last_Qsto_mg": float(patient._last_Qsto),
        "last_foodtaken_g": float(patient._last_foodtaken),
        "last_action": patient._last_action._asdict(),
        "is_eating": bool(patient.is_eating),
        "planned_meal_g": float(patient.planned_meal),
    }


def main():
    started = time.monotonic()
    plan = json.loads((HERE / "plan.json").read_text())
    name = plan["smoke_patient_id"]
    assert name == "adult#001" and name in plan["development_patient_ids"]
    assert len(plan["held_out_patient_ids"]) == 24
    module = load_patient()
    import numpy as np
    import pandas as pd
    import scipy

    # Only this parameter row is instantiated or simulated.
    with open(module.PATIENT_PARA_FILE) as handle:
        row = next(r for r in csv.DictReader(handle) if r["Name"] == name)
    params = pd.Series({k: v if k == "Name" else float(v) for k, v in row.items()})
    columns = list(row)[2:15]
    initial = np.array([params[k] for k in columns], dtype=float)
    assert len(initial) == 13 and np.isfinite(initial).all()
    basal = float(params.u2ss * params.BW / 6000)

    def new_patient():
        return module.T1DPatient(
            params.copy(), init_state=initial.copy(), random_init_bg=False,
            seed=plan["seed"], t0=plan["t0_minutes"],
        )

    patient = new_patient()
    initial_aux = auxiliary(patient)
    integrator = patient._odesolver._integrator
    derivative = module.T1DPatient.model(
        0, initial, module.Action(CHO=0, insulin=basal), params,
        initial_aux["last_Qsto_mg"], initial_aux["last_foodtaken_g"],
    )
    inputs = {
        "patient_id": name, "source_commit": plan["source_commit"],
        "parameters": params.to_dict(), "state_columns": columns,
        "initial_state": initial.tolist(), "initial_auxiliary": initial_aux,
        "basal_U_per_min": basal, "basal_U_per_hour": basal * 60,
        "initial_derivative_no_meal_at_basal": derivative.tolist(),
        "solver": {"name": "scipy.integrate.ode/dopri5",
                   "rtol": float(integrator.rtol), "atol": float(integrator.atol)},
        "plan": plan,
    }
    (HERE / "inputs.json").write_text(json.dumps(inputs, indent=2, allow_nan=False) + "\n")

    def trajectory(multiplier):
        patient = new_patient()
        assert auxiliary(patient) == initial_aux
        snapshots, actions = [], []
        for minute in range(plan["horizon_minutes"] + 1):
            assert patient.t == minute
            assert patient._odesolver.successful()
            assert np.isfinite(patient.state).all()
            snapshots.append({
                "t_min": minute, "state": patient.state.tolist(),
                "Gsub_mg_dL": float(patient.observation.Gsub),
                "plasma_glucose_mg_dL": float(patient.state[3] / params.Vg),
                "auxiliary": auxiliary(patient),
            })
            if minute == plan["horizon_minutes"]:
                break
            announced = plan["meal_announcement_g"].get(str(minute), 0)
            act = module.Action(CHO=announced, insulin=basal * multiplier)
            patient.step(act)
            actions.append({
                "start_min": minute, "end_min": minute + 1,
                "announced_CHO_g": announced,
                "consumed_CHO_g": float(patient._last_action.CHO),
                "insulin_U_per_min": float(act.insulin),
                "delivered_insulin_U": float(act.insulin * patient.sample_time),
            })
        return {"snapshots": snapshots, "actions": actions}

    factual = trajectory(1)
    counterfactual = trajectory(2)
    # One exact repeat detects accidental random initialization or mutable-state carryover.
    repeat = trajectory(1)
    assert factual == repeat
    assert factual["snapshots"][0] == counterfactual["snapshots"][0]
    for a, b in zip(factual["actions"], counterfactual["actions"]):
        assert a["announced_CHO_g"] == b["announced_CHO_g"]
        assert a["consumed_CHO_g"] == b["consumed_CHO_g"]
    assert sum(a["announced_CHO_g"] for a in factual["actions"]) == 30
    assert sum(a["consumed_CHO_g"] for a in factual["actions"]) == 30
    factual_dose = math.fsum(a["delivered_insulin_U"] for a in factual["actions"])
    cf_dose = math.fsum(a["delivered_insulin_U"] for a in counterfactual["actions"])
    assert math.isclose(factual_dose, 120 * basal, rel_tol=1e-12)
    assert math.isclose(cf_dose, 2 * factual_dose, rel_tol=1e-12)
    for label, trace in [("factual", factual), ("intervention", counterfactual)]:
        (HERE / f"{label}_trajectory.json").write_text(
            json.dumps(trace, indent=2, allow_nan=False) + "\n"
        )
    endpoints = []
    for minute in plan["readout_minutes"]:
        f, c = factual["snapshots"][minute], counterfactual["snapshots"][minute]
        endpoints.append({
            "t_min": minute, "factual_Gsub_mg_dL": f["Gsub_mg_dL"],
            "intervention_Gsub_mg_dL": c["Gsub_mg_dL"],
            "delta_Gsub_mg_dL": c["Gsub_mg_dL"] - f["Gsub_mg_dL"],
        })
    summary = {
        "status": "complete", "patient_id": name,
        "unique_patients_simulated": 1, "integrations": 3,
        "integration_steps": 360, "held_out_patients_simulated": 0,
        "checks": {key: True for key in plan["checks"]},
        "identical_action_repeat": "exactly identical all states/actions",
        "factual_total_insulin_U": factual_dose, "intervention_total_insulin_U": cf_dose,
        "meal_announced_and_consumed_g": 30,
        "initial_derivative_max_abs": float(np.max(np.abs(derivative))),
        "readouts": endpoints,
        "python": sys.executable, "versions": {"numpy": np.__version__,
        "pandas": pd.__version__, "scipy": scipy.__version__},
        "elapsed_seconds": time.monotonic() - started,
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
