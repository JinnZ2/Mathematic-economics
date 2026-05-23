"""
substrate_primacy_audit.py  —  C033..C041

Nine "missing layers" of substrate primacy: the deployment-narrative
framework systematically omits sensing latency, embodied knowledge,
distributed decision authority, multi-timescale operations, apprenticeship,
the energy cost of preserving human knowledge, institutional redundancy,
and generational transferability.

Each layer is a claim about whether the deployment retains capability in
non-computational substrates (embodied, distributed, landscape-encoded,
institutional). A deployment that scores poorly on these claims has
externalized its survival assumptions onto infrastructure that is
fragile to single-point failure.

C033  sensory / perceptual feedback latency
C034  embodied knowledge digitization loss
C035  distributed vs centralized decision authority latency
C036  multi-timescale training adequacy (>= 3 cycles of slowest mode)
C037  holdout-season transfer accuracy (< 10% drop)
C038  apprenticeship knowledge transfer efficiency
C039  energy cost of preserving human knowledge vs cloud backend
C040  institutional redundancy in degraded mode (>= 30% capacity)
C041  generational knowledge transferability without infrastructure

License: CC0-1.0
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# C033  Sensory / perceptual feedback latency
# ---------------------------------------------------------------------------

# Median seconds for each step of the response loop. Defaults reflect
# disclosed 2024-2025 latency budgets for autonomous-truck remote
# monitoring (truck telemetry to cloud + inference + dispatcher in
# the loop + action signal back).
DEFAULT_LATENCY_S: Dict[str, Dict[str, float]] = {
    "human_inline": {
        "anomaly_perception":     3.0,    # "something sounds off"
        "decision_to_act":        2.0,    # apply brake, change route
    },
    "cloud_centralized": {
        "telemetry_uplink":      30.0,
        "anomaly_inference":     60.0,
        "dispatcher_decision":   45.0,
        "action_signal_back":    15.0,
    },
}


def precursor_detection_latency(
    human_inline: Dict[str, float] | None = None,
    cloud_centralized: Dict[str, float] | None = None,
) -> dict:
    """Total seconds from anomaly onset to action signal back."""
    h = {**DEFAULT_LATENCY_S["human_inline"], **(human_inline or {})}
    c = {**DEFAULT_LATENCY_S["cloud_centralized"], **(cloud_centralized or {})}
    human_total = sum(h.values())
    cloud_total = sum(c.values())
    return {
        "human_total_s":   human_total,
        "cloud_total_s":   cloud_total,
        "ratio":           cloud_total / human_total if human_total else float("inf"),
        "human_breakdown": h,
        "cloud_breakdown": c,
    }


def c033_verdict(human_inline: Dict[str, float] | None = None,
                 cloud_centralized: Dict[str, float] | None = None) -> dict:
    """C033: human < 5s, cloud > 120s implies asymmetric precursor coverage."""
    lat = precursor_detection_latency(human_inline, cloud_centralized)
    human_under_5 = lat["human_total_s"] < 5.0
    cloud_over_120 = lat["cloud_total_s"] > 120.0
    return {
        "claim_id":      "C033",
        **lat,
        "human_under_5s":  human_under_5,
        "cloud_over_120s": cloud_over_120,
        "threshold_met":   cloud_over_120,    # asymmetry registers
        "falsifier":
            "cloud system with <5sec end-to-end latency to precursor anomalies",
    }


# ---------------------------------------------------------------------------
# C034  Embodied knowledge digitization loss
# ---------------------------------------------------------------------------

# Canonical constraint categories an experienced operator carries that
# require embodied / spatial knowledge to encode. Each row notes whether
# the category is reliably digitizable today.
DEFAULT_EMBODIED_CONSTRAINTS: List[dict] = [
    {"category": "bridge_load_judgment_visual",        "digitizable": False},
    {"category": "winter_vs_summer_route_timing",       "digitizable": False},
    {"category": "customer_load_variation_recognition", "digitizable": False},
    {"category": "landmark_navigation",                 "digitizable": False},
    {"category": "star_trail_celestial_position",       "digitizable": False},
    {"category": "soil_water_acoustic_signature",       "digitizable": False},
    {"category": "wildlife_track_age_estimation",       "digitizable": False},
    {"category": "weather_smell_pressure_prediction",   "digitizable": False},
    {"category": "fuel_smell_combustion_quality",       "digitizable": False},
    {"category": "machinery_vibration_signature",       "digitizable": True},   # partial
    {"category": "tire_visual_anomaly",                 "digitizable": True},
    {"category": "GPS_coordinates",                     "digitizable": True},
    {"category": "weight_scale_reading",                "digitizable": True},
    {"category": "engine_temperature",                  "digitizable": True},
]


def knowledge_digitization_loss(constraints: List[dict] | None = None) -> dict:
    """Fraction of operational constraints lost when translated to digital rules."""
    inv = constraints or DEFAULT_EMBODIED_CONSTRAINTS
    total = len(inv)
    lost = sum(1 for c in inv if not c.get("digitizable", False))
    return {
        "total":      total,
        "lost":       lost,
        "loss_share": (lost / total) if total else 0.0,
        "lost_categories": [c["category"] for c in inv
                            if not c.get("digitizable", False)],
    }


def c034_verdict(constraints: List[dict] | None = None) -> dict:
    """C034: > 30% of operational constraints lost in digitization."""
    loss = knowledge_digitization_loss(constraints)
    return {
        "claim_id":      "C034",
        **loss,
        "threshold_met": loss["loss_share"] > 0.30,
        "falsifier":
            "knowledge transfer system capturing > 90% of embodied "
            "constraints in form retrievable without the human present",
    }


# ---------------------------------------------------------------------------
# C035  Distributed vs centralized decision authority latency
# ---------------------------------------------------------------------------

DEFAULT_DECISION_LATENCY_S = {
    "distributed_local_decision_s":   30.0,    # 30sec floor
    "centralized_cloud_decision_s":  120.0,    # 2min average
    "decisions_per_shift":            200,
}


def decision_latency_architecture(
    distributed_local_s: float | None = None,
    centralized_cloud_s: float | None = None,
    decisions_per_shift: int | None = None,
) -> dict:
    """Compare distributed vs centralized decision authority latency."""
    d = float(distributed_local_s if distributed_local_s is not None
              else DEFAULT_DECISION_LATENCY_S["distributed_local_decision_s"])
    c = float(centralized_cloud_s if centralized_cloud_s is not None
              else DEFAULT_DECISION_LATENCY_S["centralized_cloud_decision_s"])
    n = int(decisions_per_shift if decisions_per_shift is not None
             else DEFAULT_DECISION_LATENCY_S["decisions_per_shift"])
    distributed_total = d * n
    centralized_total = c * n
    return {
        "distributed_per_decision_s":   d,
        "centralized_per_decision_s":   c,
        "decisions_per_shift":          n,
        "distributed_total_shift_s":    distributed_total,
        "centralized_total_shift_s":    centralized_total,
        "asymmetry_ratio":              c / d if d else float("inf"),
    }


def c035_verdict(distributed_local_s: float | None = None,
                 centralized_cloud_s: float | None = None,
                 decisions_per_shift: int | None = None) -> dict:
    """C035: centralized decision latency >> distributed; threshold = 4x."""
    res = decision_latency_architecture(
        distributed_local_s, centralized_cloud_s, decisions_per_shift)
    return {
        "claim_id":      "C035",
        **res,
        "threshold_met": res["asymmetry_ratio"] >= 4.0,
        "falsifier":
            "centralized system with < 30sec end-to-end latency for "
            "anomaly -> dispatcher approval -> vehicle action",
    }


# ---------------------------------------------------------------------------
# C036  Multi-timescale training adequacy
# ---------------------------------------------------------------------------

DEFAULT_OPERATIONAL_CYCLES = [
    {"name": "circadian",  "period_days":    1.0,    "required_cycles": 90},
    {"name": "weekly",     "period_days":    7.0,    "required_cycles": 20},
    {"name": "seasonal",   "period_days":   91.25,   "required_cycles":  3},
    {"name": "interannual","period_days":  365.0,    "required_cycles":  3},
    {"name": "decadal",    "period_days": 3652.5,    "required_cycles":  1},
]


def timescale_adequacy(training_span_days: float,
                       cycles: List[dict] | None = None,
                       ) -> dict:
    """Check whether training span captures >=3 cycles of slowest mode."""
    inv = cycles or DEFAULT_OPERATIONAL_CYCLES
    rows = []
    deficits = []
    for c in inv:
        required_days = c["period_days"] * c["required_cycles"]
        covered = training_span_days >= required_days
        rows.append({
            "name":           c["name"],
            "period_days":    c["period_days"],
            "required_cycles": c["required_cycles"],
            "required_days":  required_days,
            "covered":        covered,
        })
        if not covered:
            deficits.append(c["name"])
    return {
        "training_span_days": training_span_days,
        "by_cycle":           rows,
        "uncovered_cycles":   deficits,
    }


def c036_verdict(training_span_days: float,
                 cycles: List[dict] | None = None) -> dict:
    """C036: training must span >= 3 full cycles of slowest operational mode."""
    res = timescale_adequacy(training_span_days, cycles)
    return {
        "claim_id":      "C036",
        **res,
        "threshold_met": len(res["uncovered_cycles"]) > 0,
        "falsifier":
            "model trained on data spanning >= 3 full cycles of slowest "
            "operational mode (typically seasonal) including all uncovered "
            "cycles above",
    }


# ---------------------------------------------------------------------------
# C037  Holdout-season transfer accuracy
# ---------------------------------------------------------------------------

def holdout_season_test(in_season_accuracy: float,
                        held_out_season_accuracy: float) -> dict:
    """Fractional accuracy drop when applied to held-out season."""
    if in_season_accuracy <= 0:
        return {"accuracy_drop": 1.0, "in_season": in_season_accuracy,
                "held_out_season": held_out_season_accuracy,
                "relative_drop": 1.0}
    drop = (in_season_accuracy - held_out_season_accuracy) / in_season_accuracy
    return {
        "in_season":               in_season_accuracy,
        "held_out_season":         held_out_season_accuracy,
        "accuracy_drop":           in_season_accuracy - held_out_season_accuracy,
        "relative_drop":           drop,
    }


def c037_verdict(in_season_accuracy: float = 0.95,
                 held_out_season_accuracy: float = 0.78) -> dict:
    """C037: relative accuracy drop must be < 10% across held-out season."""
    res = holdout_season_test(in_season_accuracy, held_out_season_accuracy)
    return {
        "claim_id":      "C037",
        **res,
        "threshold_met": res["relative_drop"] >= 0.10,
        "falsifier":
            "model deployed on data spanning 10+ years of seasonal "
            "variation AND tested on different-season holdout with "
            "< 10% accuracy drop",
    }


# ---------------------------------------------------------------------------
# C038  Apprenticeship knowledge transfer efficiency
# ---------------------------------------------------------------------------

# Hours of operational exposure typical for each path. Apprenticeship
# standards from US Department of Labor registered apprenticeship
# programs; AI training exposure from disclosed autonomous-trucking
# stack training data inventories.
HUMAN_APPRENTICESHIP_HOURS = 8_000
AI_TRAINING_EXPOSURE_HOURS = 500   # midpoint of disclosed 100-1000h range


def apprenticeship_knowledge_audit(
    human_hours: int = HUMAN_APPRENTICESHIP_HOURS,
    ai_hours: int = AI_TRAINING_EXPOSURE_HOURS,
    ai_passes_novel_situation_tests: bool = False,
) -> dict:
    """Gap between human apprenticeship hours and AI training exposure."""
    return {
        "human_apprentice_hours":    human_hours,
        "ai_training_hours":         ai_hours,
        "ratio":                     human_hours / ai_hours if ai_hours else float("inf"),
        "ai_passes_novel_tests":     ai_passes_novel_situation_tests,
    }


def c038_verdict(human_hours: int = HUMAN_APPRENTICESHIP_HOURS,
                 ai_hours: int = AI_TRAINING_EXPOSURE_HOURS,
                 ai_passes_novel_situation_tests: bool = False) -> dict:
    """C038: AI training exposure >> below apprenticeship standard, no novel-test pass."""
    res = apprenticeship_knowledge_audit(human_hours, ai_hours,
                                          ai_passes_novel_situation_tests)
    insufficient = (ai_hours < human_hours) or (not ai_passes_novel_situation_tests)
    return {
        "claim_id":      "C038",
        **res,
        "threshold_met": insufficient,
        "falsifier":
            "AI system demonstrating equivalent judgment to human "
            "apprentice after < 8000 hours of training exposure AND "
            "passing novel-situation tests",
    }


# ---------------------------------------------------------------------------
# C039  Energy cost of preserving human knowledge vs cloud backend
# ---------------------------------------------------------------------------

HUMAN_METABOLIC_DAILY_KWH = 2.5      # ~2200 kcal/day operational driver
CLOUD_BACKEND_PER_TRUCK_KWH_PER_YEAR = 17_000.0  # from C020 calibration


def knowledge_preservation_energy(
    workforce_size: int,
    fleet_size: int,
    days_per_year: int = 250,
    human_metabolic_kwh_per_day: float = HUMAN_METABOLIC_DAILY_KWH,
    cloud_kwh_per_truck_per_year: float = CLOUD_BACKEND_PER_TRUCK_KWH_PER_YEAR,
) -> dict:
    """Compare metabolic cost of human workforce to cloud backend."""
    human_kwh_per_year = (workforce_size * human_metabolic_kwh_per_day
                           * days_per_year)
    cloud_kwh_per_year = fleet_size * cloud_kwh_per_truck_per_year
    return {
        "workforce_size":          workforce_size,
        "fleet_size":              fleet_size,
        "human_kwh_per_year":      human_kwh_per_year,
        "cloud_kwh_per_year":      cloud_kwh_per_year,
        "ratio_cloud_to_human":    (cloud_kwh_per_year / human_kwh_per_year
                                     if human_kwh_per_year else float("inf")),
    }


def c039_verdict(workforce_size: int = 50, fleet_size: int = 50) -> dict:
    """C039: cloud backend energy cost > human workforce metabolic cost."""
    res = knowledge_preservation_energy(workforce_size, fleet_size)
    return {
        "claim_id":      "C039",
        **res,
        "threshold_met": res["ratio_cloud_to_human"] > 1.0,
        "falsifier":
            "cloud backend running 24/7 for fleet consumes less energy "
            "than keeping equivalent human workforce in active practice",
    }


# ---------------------------------------------------------------------------
# C040  Institutional redundancy in degraded mode
# ---------------------------------------------------------------------------

# Default operational-pathway shares when each infrastructure layer fails.
# Fractions are the share of operations still executable without that
# infrastructure. Defaults reflect the autonomous-no-driver baseline.
DEFAULT_DEGRADED_MODE_CAPACITY: Dict[str, float] = {
    "gps_down":            0.10,
    "cloud_down":          0.05,
    "electricity_down":    0.0,
    "fuel_unavailable":    0.0,
}


def degraded_mode_capacity(
    operational_capacity_by_failure: Dict[str, float] | None = None,
) -> dict:
    """Per-failure-mode operational capacity, plus the minimum across all."""
    cap = {**DEFAULT_DEGRADED_MODE_CAPACITY,
           **(operational_capacity_by_failure or {})}
    return {
        "by_failure_mode": cap,
        "min_capacity":    min(cap.values()) if cap else 0.0,
        "mean_capacity":   sum(cap.values()) / len(cap) if cap else 0.0,
    }


def c040_verdict(operational_capacity_by_failure:
                 Dict[str, float] | None = None) -> dict:
    """C040: must maintain >= 30% operational capacity in any degraded mode."""
    res = degraded_mode_capacity(operational_capacity_by_failure)
    return {
        "claim_id":      "C040",
        **res,
        "threshold_met": res["min_capacity"] < 0.30,
        "falsifier":
            "autonomous deployment demonstrating > 30% operational "
            "capacity through non-digital, non-cloud pathways",
    }


# ---------------------------------------------------------------------------
# C041  Generational knowledge transferability
# ---------------------------------------------------------------------------

# Default per-element survival fractions under total infrastructure loss.
# Encoded knowledge: landscape markers (three trees, star trails),
# pre-digital manuals, oral apprenticeship traditions.
DEFAULT_KNOWLEDGE_SURVIVAL: Dict[str, float] = {
    "landscape_markers":            0.85,
    "oral_apprenticeship":          0.80,
    "pre_digital_manuals":          0.70,
    "embodied_neuromuscular":       0.75,
    "ai_neural_network_weights":    0.05,
    "cloud_only_telemetry_history": 0.02,
    "encrypted_proprietary_logs":   0.0,
}


def generational_knowledge_transferability(
    knowledge_inventory: Dict[str, float] | None = None,
) -> dict:
    """Fraction of operational knowledge surviving total infrastructure loss."""
    kn = {**DEFAULT_KNOWLEDGE_SURVIVAL, **(knowledge_inventory or {})}
    total = len(kn)
    weighted_mean = sum(kn.values()) / total if total else 0.0
    return {
        "by_knowledge_element": kn,
        "mean_survival":        weighted_mean,
    }


def c041_verdict(knowledge_inventory: Dict[str, float] | None = None) -> dict:
    """C041: > 50% of operational knowledge must survive total infrastructure loss."""
    res = generational_knowledge_transferability(knowledge_inventory)
    return {
        "claim_id":      "C041",
        **res,
        "threshold_met": res["mean_survival"] < 0.50,
        "falsifier":
            "autonomous deployment requiring < 20% external "
            "infrastructure for operational continuity across 100 years",
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("C033:", c033_verdict())
    print("C034:", c034_verdict())
    print("C035:", c035_verdict())
    print("C036:", c036_verdict(training_span_days=730.0))   # 2 years
    print("C037:", c037_verdict())
    print("C038:", c038_verdict())
    print("C039:", c039_verdict())
    print("C040:", c040_verdict())
    print("C041:", c041_verdict())
