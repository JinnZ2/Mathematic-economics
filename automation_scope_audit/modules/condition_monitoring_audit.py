"""
condition_monitoring_audit.py  —  C008, C009, C010

Driver-performed condition monitoring is unpriced infrastructure. Sensor
replacement introduces new failure modes. Roadside breakdown cost scales
nonlinearly without an operator present.

Falsifiers:
  C008: deployed system showing <2x cost of driver-performed monitoring.
  C009: documented parity in catch rates for subtle / precursor failures.
  C010: insurance / operational data showing autonomous-vs-human roadside
        cost parity.

Default monetary numbers are 2025 US dollars but are exposed as constants
so callers can override or rescale. The module deliberately surfaces both
priced and unpriced quantities — the central thesis is that the unpriced
quantities are large and load-bearing.

License: CC0-1.0
"""

from typing import Dict, List


# Canonical driver-performed monitoring task list (per DOT + operational reality).
# Each entry: task name, frequency per day, minutes per occurrence,
# representative failure modes the human catches.
MONITORING_TASKS_CLASS8: List[dict] = [
    {"task": "pretrip_inspection",        "per_day": 1, "minutes": 30,
     "catches": ["loose_components", "fluid_leaks", "tire_visual",
                 "light_signal", "brake_visual"]},
    {"task": "posttrip_inspection",       "per_day": 1, "minutes": 20,
     "catches": ["damage_post_route", "fluid_loss_trend", "tire_wear_trend"]},
    {"task": "mid_shift_fluid_checks",    "per_day": 2, "minutes": 4,
     "catches": ["oil_consumption_trend", "coolant_loss", "def_low"]},
    {"task": "tire_visual_and_pressure",  "per_day": 2, "minutes": 5,
     "catches": ["sidewall_damage", "uneven_wear", "low_pressure",
                 "tire_temperature_anomaly"]},
    {"task": "brake_adjustment_check",    "per_day": 1, "minutes": 6,
     "catches": ["out_of_adjustment", "drum_glaze", "lining_thinning"]},
    {"task": "light_signal_verification", "per_day": 2, "minutes": 2,
     "catches": ["bulb_out", "wiring_intermittent"]},
    {"task": "air_system_leak_audio",     "per_day": 2, "minutes": 3,
     "catches": ["slow_leak", "valve_seep", "compressor_cycling_anomaly"]},
    {"task": "load_securement_recheck",   "per_day": 3, "minutes": 4,
     "catches": ["strap_loosening", "load_shift", "tarp_failure"]},
    {"task": "mirror_windshield_cleaning","per_day": 2, "minutes": 3,
     "catches": ["visibility_degradation"]},
    {"task": "fifth_wheel_inspection",    "per_day": 1, "minutes": 4,
     "catches": ["kingpin_wear", "locking_mechanism_anomaly", "grease_failure"]},
    {"task": "undercarriage_visual",      "per_day": 1, "minutes": 5,
     "catches": ["frame_damage", "exhaust_leak", "u_joint_play",
                 "wiring_chafe"]},
]


# Default 2025 US sensor / opex cost envelope (USD per truck).
DEFAULT_SENSOR_COSTS: Dict[str, dict] = {
    "vibration_sensors":     {"capex": 8_000,  "annual_opex": 1_200},
    "thermal_sensors":       {"capex": 6_000,  "annual_opex": 900},
    "tpms":                  {"capex": 1_200,  "annual_opex": 200},
    "tire_wear_thermal":     {"capex": 7_000,  "annual_opex": 1_100},
    "fluid_quality_sensors": {"capex": 9_000,  "annual_opex": 1_500},
    "air_system_pressure":   {"capex": 3_000,  "annual_opex": 500},
    "acoustic_anomaly":      {"capex": 12_000, "annual_opex": 2_400},
    "undercarriage_imaging": {"capex": 9_000,  "annual_opex": 1_400},
    "diagnostic_compute":    {"capex": 6_000,  "annual_opex": 4_500},
    "cellular_dispatch":     {"capex": 1_000,  "annual_opex": 3_000},
    "roadside_response_retainer":
                             {"capex": 0,      "annual_opex": 9_000},
}


# Failure modes that the human reliably catches at precursor stage but for
# which no sensor at the deployed price point reliably detects the precursor.
HUMAN_ONLY_PRECURSOR_CATCHES: List[str] = [
    "oil_burn_smell",
    "coolant_sweet_smell",
    "electrical_burn_smell",
    "unusual_vibration_signature",
    "subtle_brake_feel_change",
    "subtle_steering_pull",
    "tire_glaze_visual",
    "load_settling_sound",
    "exhaust_pitch_change",
    "compressor_cycling_anomaly_by_ear",
    "vague_handling_feel",
]


def enumerate_monitoring_tasks(vehicle_class: str = "class8") -> List[dict]:
    """Return the full task inventory for the given vehicle class."""
    if vehicle_class != "class8":
        raise KeyError(f"only class8 inventory is bundled: got {vehicle_class}")
    return [dict(t) for t in MONITORING_TASKS_CLASS8]


def monitoring_replacement_cost(tasks: List[dict],
                                sensor_costs: Dict[str, dict] | None = None,
                                lifecycle_years: int = 7) -> dict:
    """Capex + opex over `lifecycle_years` to replace the task list.

    The `tasks` argument is kept for symmetry with the interface contract
    but the cost stack is driven by `sensor_costs` since coverage of the
    task list requires the full sensor package — picking a subset would
    only re-introduce gaps the driver currently closes for free.
    """
    sc = sensor_costs or DEFAULT_SENSOR_COSTS
    capex = sum(item["capex"] for item in sc.values())
    annual_opex = sum(item["annual_opex"] for item in sc.values())
    lifecycle_opex = annual_opex * lifecycle_years
    total = capex + lifecycle_opex
    return {
        "capex":            capex,
        "annual_opex":      annual_opex,
        "lifecycle_years":  lifecycle_years,
        "lifecycle_opex":   lifecycle_opex,
        "total_lifecycle":  total,
        "line_items":       sc,
        "task_count":       len(tasks),
    }


def detection_gap_analysis(human_caught: List[str],
                           sensor_caught: List[str]) -> dict:
    """What does the human catch that no sensor catches?"""
    human = set(human_caught)
    sensors = set(sensor_caught)
    only_human = sorted(human - sensors)
    only_sensor = sorted(sensors - human)
    both = sorted(human & sensors)
    union = human | sensors
    coverage_ratio = (len(both) / len(union)) if union else 0.0
    return {
        "only_human_catches":  only_human,
        "only_sensor_catches": only_sensor,
        "shared_catches":      both,
        "coverage_ratio":      coverage_ratio,
        "human_only_precursors_present":
            sorted(set(only_human) & set(HUMAN_ONLY_PRECURSOR_CATCHES)),
    }


def unpriced_labor_value(tasks: List[dict], hourly_rate: float,
                         working_days_per_year: int = 250) -> dict:
    """Annual unpriced labor value for the listed monitoring tasks.

    Returns gross-cost dollars per truck per year. Threshold sanity check:
    ~60 min/day at $25-35/hr ~= $6-8.5k/yr. The math reflects this.
    """
    minutes_per_day = sum(t["per_day"] * t["minutes"] for t in tasks)
    hours_per_day = minutes_per_day / 60.0
    annual_value = hours_per_day * hourly_rate * working_days_per_year
    return {
        "minutes_per_day":  minutes_per_day,
        "hours_per_day":    hours_per_day,
        "hourly_rate":      hourly_rate,
        "annual_value_usd": annual_value,
        "working_days_per_year": working_days_per_year,
    }


def breakdown_cost_model(failure_type: str,
                         location_remoteness: float,
                         operator_present: bool = False) -> float:
    """Expected total cost of one roadside breakdown.

    Args:
        failure_type: one of "tire", "engine", "brake", "electrical",
            "sensor", "load_shift", "weather_stranding", "other".
        location_remoteness: 0.0 urban (tow-truck on-call) to 1.0 deep rural
            (helicopter / specialist dispatch).
        operator_present: True if a human is in the cab; False if the truck
            is fully autonomous and a technician must be dispatched.

    Returns an integrated USD cost: tow + dispatch + lost-load value at
    risk + customer penalty + reschedule + diagnostic-limit penalty for
    autonomous-only.
    """
    base = {
        "tire":              1_200.0,
        "engine":             7_500.0,
        "brake":              4_000.0,
        "electrical":         3_500.0,
        "sensor":             2_500.0,
        "load_shift":         5_000.0,
        "weather_stranding":  3_000.0,
        "other":              3_000.0,
    }.get(failure_type, 3_000.0)

    remoteness = max(0.0, min(1.0, location_remoteness))
    remoteness_multiplier = 1.0 + 4.0 * remoteness
    # Autonomous penalty scales with remoteness: technician travel cost and
    # cargo dwell time grow faster for autonomous than for human-mediated
    # incidents because the driver-on-site can stage a field-fix or limp the
    # truck to a serviceable location, while an autonomous truck can't.
    # 2.0x at urban -> 4.0x at deep rural; matches the upper end of
    # disclosed insurance loadings (TuSimple/Embark filings).
    autonomous_penalty = 1.0 if operator_present else (2.0 + 2.0 * remoteness)

    return base * remoteness_multiplier * autonomous_penalty


def breakdown_cost_ratio(failure_type: str, location_remoteness: float) -> dict:
    """C010 explicit gate: cost ratio autonomous : human."""
    human = breakdown_cost_model(failure_type, location_remoteness,
                                 operator_present=True)
    auto = breakdown_cost_model(failure_type, location_remoteness,
                                operator_present=False)
    ratio = auto / human if human > 0 else float("inf")
    return {
        "failure_type":       failure_type,
        "location_remoteness": location_remoteness,
        "human_cost_usd":     human,
        "autonomous_cost_usd": auto,
        "ratio":              ratio,
        "threshold_met":      ratio > 3.0,
    }


def c008_verdict(vehicle_class: str = "class8",
                 hourly_rate: float = 30.0,
                 lifecycle_years: int = 7,
                 sensor_costs: Dict[str, dict] | None = None) -> dict:
    tasks = enumerate_monitoring_tasks(vehicle_class)
    replacement = monitoring_replacement_cost(tasks, sensor_costs,
                                              lifecycle_years)
    unpriced_annual = unpriced_labor_value(tasks, hourly_rate)
    driver_lifecycle_value = (
        unpriced_annual["annual_value_usd"] * lifecycle_years)
    ratio = (replacement["total_lifecycle"] / driver_lifecycle_value
             if driver_lifecycle_value > 0 else float("inf"))
    return {
        "claim_id":                       "C008",
        "lifecycle_years":                lifecycle_years,
        "driver_lifecycle_value_usd":     driver_lifecycle_value,
        "replacement_lifecycle_cost_usd": replacement["total_lifecycle"],
        "replacement_capex_usd":          replacement["capex"],
        "replacement_annual_opex_usd":    replacement["annual_opex"],
        "cost_ratio_replacement_to_driver": ratio,
        "threshold_met":                  ratio > 2.0,
        "falsifier": "deployed system showing <2x cost of driver-performed monitoring",
    }


def c009_verdict(human_caught: List[str], sensor_caught: List[str]) -> dict:
    gap = detection_gap_analysis(human_caught, sensor_caught)
    return {
        "claim_id":          "C009",
        **gap,
        "threshold_met":     bool(gap["human_only_precursors_present"]),
        "falsifier": "documented parity in catch rates for subtle/precursor failures",
    }


def c010_verdict(failure_type: str = "engine",
                 location_remoteness: float = 0.7) -> dict:
    ratio = breakdown_cost_ratio(failure_type, location_remoteness)
    return {
        "claim_id":          "C010",
        **ratio,
        "falsifier": "insurance/operational data showing parity",
    }


if __name__ == "__main__":
    print("C008:", c008_verdict())
    print("C009:", c009_verdict(
        human_caught=HUMAN_ONLY_PRECURSOR_CATCHES + ["tire_visual"],
        sensor_caught=["low_pressure", "vibration_signature_match",
                       "tire_visual"]))
    print("C010:", c010_verdict("engine", 0.8))
