"""
scaling_audit.py  —  C021

Scaling creates hidden energy costs masked by amortization accounting.

Narrative claim: "Scale to 10,000 vehicles, backend cost per vehicle
drops 10x."

Physics reality: larger organisms have fundamentally different energy
budgets. Below a certain size the per-unit metabolic rate is high; in
the middle the curve flattens (economies of scale); above the optimum
the absolute consumption rises and infrastructure / coordination /
cascade-risk costs dominate.

The true scaling curve is NOT linear or logarithmic:

    energy_cost(n) = backend_cost / n
                   + coordination_overhead * n
                   + infrastructure_sprawl * sqrt(n)
                   + regulatory_complexity * n
                   + cascade_risk * n^2

There is an optimal scale point. Current accounting hides it by counting
only the descending (backend/n) term and presenting cost as "per-vehicle"
when the costs that grow with n are "per-system".

Falsifier: audited multi-scale deployment data showing total energy cost
per ton-mile monotonically decreasing across at least three orders of
magnitude of fleet size.

License: CC0-1.0
"""

import math
from typing import Callable, Dict, List


# Default cost coefficients. Units are kWh per truck per year for the
# leading term; per-system terms scale per-vehicle differently:
#   backend_amortizing:    kWh/year as a pool, divided by n -> kWh/truck/year
#   coordination_per_truck: kWh/truck/year added linearly with n
#   infrastructure_sqrt:    kWh/truck/year scales with sqrt(n)
#   regulatory_per_truck:   kWh/truck/year added linearly with n
#   cascade_quadratic:      kWh/truck/year scales with n
# All terms expressed as cost-per-truck so that the optimum is a fleet
# size where d(total)/dn = 0. The user's spec uses cascade_risk * n^2 as
# *total* system cost; per-truck that becomes cascade_quadratic * n.
DEFAULT_COST_COEFFICIENTS: Dict[str, float] = {
    "backend_amortizing_kwh":        4_000_000.0,   # fixed pool, divided by n
    "coordination_per_truck_kwh":          1.5,     # adds with n
    "infrastructure_sqrt_kwh":           120.0,     # adds with sqrt(n)
    "regulatory_per_truck_kwh":            0.8,     # adds with n
    "cascade_quadratic_kwh":               0.0008,  # adds with n
}


def enumerate_scaling_costs(fleet_size: int,
                            coefficients: Dict[str, float] | None = None
                            ) -> dict:
    """Decompose total cost into per-vehicle / per-system / cascade terms.

    Returns a dict with each component's contribution in kWh per truck
    per year, the total, and a categorical tag.
    """
    if fleet_size <= 0:
        raise ValueError("fleet_size must be > 0")
    c = {**DEFAULT_COST_COEFFICIENTS, **(coefficients or {})}

    backend           = c["backend_amortizing_kwh"] / fleet_size
    coordination      = c["coordination_per_truck_kwh"] * fleet_size
    infrastructure    = c["infrastructure_sqrt_kwh"] * math.sqrt(fleet_size)
    regulatory        = c["regulatory_per_truck_kwh"] * fleet_size
    cascade           = c["cascade_quadratic_kwh"] * fleet_size

    total = (backend + coordination + infrastructure + regulatory + cascade)
    return {
        "fleet_size":           fleet_size,
        "backend_amortizing":   backend,
        "coordination":         coordination,
        "infrastructure_sprawl": infrastructure,
        "regulatory":           regulatory,
        "cascade_risk":         cascade,
        "total_per_truck_kwh":  total,
        "total_system_kwh":     total * fleet_size,
        "descending_terms":     {"backend_amortizing": backend},
        "ascending_terms":      {
            "coordination":          coordination,
            "infrastructure_sprawl": infrastructure,
            "regulatory":            regulatory,
            "cascade_risk":          cascade,
        },
    }


def optimal_fleet_size(coefficients: Dict[str, float] | None = None,
                       search_min: int = 1,
                       search_max: int = 100_000,
                       ) -> dict:
    """Find the fleet size that minimizes per-truck total cost.

    Uses a logarithmic scan + linear refinement; the cost surface is
    unimodal under the default coefficients so the discrete minimum is
    unique. Returns the optimum, the cost at the optimum, the full
    sampled curve, and a flag indicating whether the curve has a
    well-defined interior minimum.
    """
    c = {**DEFAULT_COST_COEFFICIENTS, **(coefficients or {})}

    # Log scan
    samples = []
    n = max(1, search_min)
    while n <= search_max:
        cost = enumerate_scaling_costs(n, c)["total_per_truck_kwh"]
        samples.append((n, cost))
        n = max(n + 1, int(n * 1.4))

    best = min(samples, key=lambda x: x[1])
    best_n, best_cost = best

    # Local refinement around the log-scan winner
    lo = max(search_min, int(best_n / 2))
    hi = min(search_max, int(best_n * 2) + 1)
    for n in range(lo, hi + 1):
        cost = enumerate_scaling_costs(n, c)["total_per_truck_kwh"]
        if cost < best_cost:
            best_n, best_cost = n, cost

    interior = search_min < best_n < search_max
    return {
        "optimal_fleet_size":     best_n,
        "cost_at_optimum_kwh":    best_cost,
        "interior_minimum":       interior,
        "sampled_curve":          samples,
        "coefficients":           c,
        "search_range":           (search_min, search_max),
    }


# Patterns that signal a scaling claim is using per-vehicle metrics to
# obscure per-system cost rises.
AMORTIZATION_PATTERNS = [
    r"per[-\s]vehicle\s+cost\s+(?:drops|falls|decreases)",
    r"backend\s+cost\s+per\s+vehicle\s+(?:drops|falls)",
    r"at\s+scale.{0,40}(?:cheaper|efficient|optim)",
    r"economies?\s+of\s+scale",
    r"scal(?:e|ing).{0,40}(?:divides|amortiz)",
    r"(?:10|hundred|thousand)x?\s+(?:cheaper|less)",
]

# Patterns that, if present, indicate the claim is at least *trying* to
# acknowledge per-system costs.
SYSTEM_COST_PATTERNS = [
    r"coordination\s+overhead",
    r"infrastructure\s+sprawl",
    r"cascade\s+risk",
    r"regulatory\s+complexity",
    r"per[-\s]system\s+cost",
    r"super[-\s]?linear",
    r"diseconom(?:y|ies)\s+of\s+scale",
]


def amortization_gymnastics_detection(claim: str) -> dict:
    """Detect when scaling claims use per-vehicle metrics to hide per-system costs."""
    import re
    text = claim.lower()
    amort_hits  = [m.group(0) for p in AMORTIZATION_PATTERNS
                   for m in re.finditer(p, text)]
    system_hits = [m.group(0) for p in SYSTEM_COST_PATTERNS
                   for m in re.finditer(p, text)]
    flags: List[str] = []
    if amort_hits and not system_hits:
        flags.append("per_vehicle_framing_without_per_system_acknowledgment")
    if amort_hits and "n vehicles" not in text and "fleet size" not in text:
        flags.append("scale_unspecified")
    return {
        "amortization_markers": amort_hits,
        "system_cost_markers":  system_hits,
        "flags":                flags,
        "gymnastics_detected":  bool(flags),
    }


def cascade_failure_energy_cost(fleet_size: int,
                                failure_probability_per_vehicle: float,
                                mean_vehicles_affected: float,
                                recovery_cost_per_vehicle: float,
                                ) -> dict:
    """Expected annual cascade-recovery energy cost.

    Models cascades as: independent vehicle failures each propagate to
    `mean_vehicles_affected` other vehicles, capped at fleet_size. Expected
    annual events = fleet_size * failure_probability_per_vehicle. Each
    event costs recovery_cost_per_vehicle * mean_affected. The result
    is sub-linear at small n (effective propagation < 1) and super-linear
    at large n (where propagation saturates and frequency dominates).
    """
    if fleet_size <= 0:
        raise ValueError("fleet_size must be > 0")
    fp = max(0.0, min(1.0, failure_probability_per_vehicle))
    affected = max(1.0, min(float(fleet_size), mean_vehicles_affected))
    events_per_year = fleet_size * fp
    per_event_cost = recovery_cost_per_vehicle * affected
    annual_cost = events_per_year * per_event_cost
    return {
        "fleet_size":           fleet_size,
        "events_per_year":      events_per_year,
        "mean_vehicles_affected": affected,
        "per_event_cost":       per_event_cost,
        "annual_cascade_cost":  annual_cost,
        "annual_per_truck":     annual_cost / fleet_size if fleet_size else 0.0,
    }


def organism_size_analogy(fleet_size: int,
                          coefficients: Dict[str, float] | None = None,
                          ) -> dict:
    """Map fleet size onto biological scaling-law tiers."""
    opt = optimal_fleet_size(coefficients)
    optimum = opt["optimal_fleet_size"]
    ratio = fleet_size / optimum if optimum > 0 else float("inf")

    if ratio < 0.1:
        tier = "microorganism"
        notes = ("Backend pool not amortized; per-truck cost dominated by "
                 "fixed overhead. Like a small animal: high per-unit "
                 "metabolic rate, resilient to local failures, can pivot.")
    elif ratio < 0.5:
        tier = "small_animal"
        notes = ("Below optimum; amortization not fully captured. Coordination "
                 "overhead still negligible. Adaptive, low cascade risk.")
    elif ratio < 1.5:
        tier = "optimal_range"
        notes = ("Near the optimum: amortization captured, coordination "
                 "manageable, cascade risk priced in. The sweet spot.")
    elif ratio < 5.0:
        tier = "large_animal"
        notes = ("Above optimum. Coordination overhead rising; infrastructure "
                 "sprawl becoming material. Per-truck cost climbing.")
    else:
        tier = "megafauna"
        notes = ("Far above optimum. Quadratic cascade term dominates; "
                 "system is brittle, expensive, and resource-concentrated. "
                 "Catastrophic failure mode if any single resource becomes "
                 "scarce.")
    return {
        "fleet_size":     fleet_size,
        "optimum":        optimum,
        "ratio_to_optimum": ratio,
        "tier":           tier,
        "notes":          notes,
    }


def c021_verdict(fleet_size: int,
                 coefficients: Dict[str, float] | None = None,
                 claim_text: str = "",
                 ) -> dict:
    costs = enumerate_scaling_costs(fleet_size, coefficients)
    opt = optimal_fleet_size(coefficients)
    organism = organism_size_analogy(fleet_size, coefficients)
    gym = amortization_gymnastics_detection(claim_text)

    above_optimum = fleet_size > opt["optimal_fleet_size"]
    ascending_share = sum(costs["ascending_terms"].values()) \
        / costs["total_per_truck_kwh"] if costs["total_per_truck_kwh"] > 0 else 0.0
    return {
        "claim_id":          "C021",
        "fleet_size":        fleet_size,
        "optimum":           opt["optimal_fleet_size"],
        "ratio_to_optimum":  organism["ratio_to_optimum"],
        "ascending_cost_share": ascending_share,
        "above_optimum":     above_optimum,
        "amortization_gymnastics": gym,
        "organism_tier":     organism["tier"],
        "cost_breakdown":    costs,
        "threshold_met":     above_optimum or gym["gymnastics_detected"],
        "falsifier":
            "audited multi-scale deployment data showing total energy cost "
            "per ton-mile monotonically decreasing across at least three "
            "orders of magnitude of fleet size",
    }


if __name__ == "__main__":
    print("optimum:", optimal_fleet_size())
    print("---")
    print("small fleet (50):", c021_verdict(50,
        claim_text="At scale our backend cost per vehicle drops 10x"))
    print("---")
    print("large fleet (50000):", c021_verdict(50_000))
