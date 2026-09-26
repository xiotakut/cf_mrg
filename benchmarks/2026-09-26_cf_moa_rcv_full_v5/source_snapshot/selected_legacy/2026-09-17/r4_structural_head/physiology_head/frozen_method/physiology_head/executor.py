"""CPU execution of the unmodified author patient, using visible state only.

execute(native_input, full_plan, no_do=False) returns two glucose values, their
difference, the predicate answer, and both trajectories. Full-plan basal values
are multipliers of the visible factual basal; boluses are U over one minute.
No patient-name lookup, outcome reference, or parameter-table read occurs here.
"""
from functools import lru_cache
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from physiology_probe.smoke import load_patient


@lru_cache(maxsize=1)
def _author():
    return load_patient()


def _minute(value, horizon, *, endpoint=False):
    maximum = horizon if endpoint else horizon - 1
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Time must be a numeric integer minute")
    if not math.isfinite(value) or int(value) != value or not 0 <= value <= maximum:
        raise ValueError(f"Minute must lie in [0,{maximum}]")
    return int(value)


def _nonnegative(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Amount must be a finite nonnegative number")
    if not math.isfinite(value) or value < 0:
        raise ValueError("Amount must be a finite nonnegative number")
    return float(value)


def _segments(segments, horizon, field):
    values = [None] * horizon
    for segment in segments:
        start = _minute(segment["start_min"], horizon)
        end = _minute(segment["end_min"], horizon, endpoint=True)
        if start >= end:
            raise ValueError("Basal intervals must have positive duration")
        value = _nonnegative(segment[field])
        for minute in range(start, end):
            if values[minute] is not None:
                raise ValueError("Basal intervals must not overlap")
            values[minute] = value
    if any(v is None for v in values):
        raise ValueError("Basal intervals must cover the whole horizon")
    return values


def expand_schedule(native_input, full_plan=None):
    """Expand only visible regimens; factual rates and boluses remain separate."""
    horizon = native_input["horizon_min"]
    if type(horizon) is not int or horizon != 120:
        raise ValueError("The present experiment requires horizon_min=120")
    meals = [0.0] * horizon
    for meal in native_input["meal_announcements"]:
        minute = _minute(meal["time_min"], horizon)
        meals[minute] += _nonnegative(meal["grams"])
    basal = _segments(native_input["factual_basal"], horizon, "rate_U_per_min")
    boluses = native_input["factual_boluses"]
    if full_plan is not None:
        factors = _segments(full_plan["basal"], horizon, "multiplier")
        basal = [rate * factor for rate, factor in zip(basal, factors)]
        boluses = full_plan["boluses"]
    insulin = basal.copy()
    for bolus in boluses:
        minute = _minute(bolus["time_min"], horizon)
        # Patient.sample_time is one minute, so U / one minute gives U/min.
        insulin[minute] += _nonnegative(bolus["units"])
    return meals, insulin


def simulate(native_input, full_plan=None, *, rtol=1e-6, atol=1e-12):
    """Integrate a visible initial condition and factual or full counterfactual plan."""
    import numpy as np
    import pandas as pd

    horizon = native_input["horizon_min"]
    meals, insulin = expand_schedule(native_input, full_plan)
    state = np.asarray(native_input["initial_state"], dtype=float)
    if state.shape != (13,) or not np.isfinite(state).all():
        raise ValueError("All 13 finite initial state values must be visible")
    params = pd.Series(native_input["params"])
    module = _author()
    patient = module.T1DPatient(
        params, init_state=state.copy(), random_init_bg=False, seed=0, t0=0,
    )
    aux = native_input["reset_auxiliary"]
    patient._last_Qsto = aux["last_Qsto_mg"]
    patient._last_foodtaken = aux["last_foodtaken_g"]
    patient._last_action = module.Action(**aux["last_action"])
    patient.is_eating = aux["is_eating"]
    patient.planned_meal = aux["planned_meal_g"]
    patient._odesolver.set_integrator("dopri5", rtol=rtol, atol=atol)
    patient._odesolver.set_initial_value(state.copy(), 0)

    trajectory, actions = [], []
    for minute in range(horizon + 1):
        if not patient._odesolver.successful() or not np.isfinite(patient.state).all():
            raise RuntimeError(f"Author integration failed at minute {minute}")
        trajectory.append({
            "t_min": minute,
            "state": patient.state.tolist(),
            "Gsub_mg_dL": float(patient.observation.Gsub),
            "plasma_glucose_mg_dL": float(patient.state[3] / params.Vg),
        })
        if minute == horizon:
            break
        action = module.Action(CHO=meals[minute], insulin=insulin[minute])
        patient.step(action)
        actions.append({
            "start_min": minute, "end_min": minute + 1,
            "announced_CHO_g": float(action.CHO),
            "consumed_CHO_g": float(patient._last_action.CHO),
            "insulin_U_per_min": float(action.insulin),
        })
    return {"trajectory": trajectory, "actions": actions,
            "solver": {"name": "dopri5", "rtol": rtol, "atol": atol}}


def project(factual, counterfactual, query):
    """Evaluate a declared query on already computed trajectories, without gold."""
    if query["readout"] != "gsub":
        raise ValueError("Only the specified gsub readout is supported")
    minute = _minute(query["time_min"], 120, endpoint=True)
    factual_value = factual["trajectory"][minute]["Gsub_mg_dL"]
    counterfactual_value = counterfactual["trajectory"][minute]["Gsub_mg_dL"]
    difference = counterfactual_value - factual_value
    if query["quantity"] not in ("counterfactual", "difference"):
        raise ValueError("Unknown query quantity")
    value = counterfactual_value if query["quantity"] == "counterfactual" else difference
    threshold = query["threshold"]
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold):
        raise ValueError("Threshold must be a finite number")
    comparison = query["comparison"]
    if comparison == "ge":
        truth = value >= threshold
    elif comparison == "le":
        truth = value <= threshold
    elif comparison == "lt":
        truth = value < threshold
    else:
        raise ValueError("Unknown comparison")
    return {"counterfactual_value": counterfactual_value, "factual_value": factual_value,
            "difference": difference, "answer_choice": "yes" if truth else "no",
            "predicate_value": value, "threshold_margin": abs(value - threshold)}


def execute(native_input, full_plan, *, no_do=False, rtol=1e-6, atol=1e-12):
    """Use only the caller's visible model boundary and action/query objects."""
    # Validate the declared plan even when the offline ablation removes its action.
    expand_schedule(native_input, full_plan)
    factual = simulate(native_input, rtol=rtol, atol=atol)
    counterfactual = factual if no_do else simulate(native_input, full_plan, rtol=rtol, atol=atol)
    return {**project(factual, counterfactual, full_plan["query"]),
            "factual_trajectory": factual, "counterfactual_trajectory": counterfactual,
            "no_do": no_do}


def check():
    """Small non-integrating check of dose composition, intervals and predicates."""
    native = {"horizon_min": 120, "meal_announcements": [{"time_min": 0, "grams": 30}],
              "factual_basal": [{"start_min": 0, "end_min": 120, "rate_U_per_min": .02}],
              "factual_boluses": [{"time_min": 0, "units": 2}]}
    plan = {"basal": [{"start_min": 0, "end_min": 60, "multiplier": .5},
                      {"start_min": 60, "end_min": 120, "multiplier": 1}],
            "boluses": [{"time_min": 30, "units": 2}]}
    meals, rates = expand_schedule(native, plan)
    assert sum(meals) == 30 and meals[0] == 30
    assert rates[0] == .01 and rates[30] == 2.01 and rates[60] == .02
    assert math.isclose(math.fsum(rates), 3.8)
    malformed = {"basal": plan["basal"][:1], "boluses": []}
    try:
        expand_schedule(native, malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("Incomplete basal schedule accepted")
    factual = {"trajectory": [{"Gsub_mg_dL": 150}] * 121}
    counterfactual = {"trajectory": [{"Gsub_mg_dL": 140}] * 121}
    query = {"time_min": 30, "readout": "gsub", "quantity": "difference",
             "comparison": "le", "threshold": -5}
    assert project(factual, counterfactual, query)["answer_choice"] == "yes"
    assert project(factual, factual, query)["answer_choice"] == "no"
    print("executor schedule/projection check passed (no integration)")


if __name__ == "__main__":
    check()
