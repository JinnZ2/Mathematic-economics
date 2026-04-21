# metabolic_bridge.py
# Defensive bridge: Math-Econ -> JinnZ2/metabolic-accounting (CC0).
#
# Companion to the three PhysicsGuard bridges. metabolic-accounting is NOT
# vendored: this module probes a few conventional locations and falls back
# to _HAS_METABOLIC_ACCOUNTING = False if the upstream package can't be
# imported. Every helper returns None in the False case so consumers can
# wire the call in unconditionally.
#
# To make the bridge active, place a checkout adjacent to this repo:
#   <parent>/metabolic-accounting/    (default git clone name)
# or vendor a snapshot inside this repo:
#   <repo_root>/metabolic_accounting/
#
# The upstream uses flat package imports (`from basin_states import ...`),
# matching the physics_guard pattern, so we add the package directory to
# sys.path rather than importing it as a subpackage.
#
# Pinned upstream version (the API surface this bridge was written against):
#   repo:   https://github.com/JinnZ2/metabolic-accounting
#   commit: 09382a66ce6ee63d84038c8ee35a1fbc28cda58d
#   date:   2026-04-21
# To upgrade, fetch the new HEAD, re-run `python tests/test_bridges.py`
# with that checkout in place, and bump UPSTREAM_PINNED_COMMIT below.

import os
import sys
from typing import Any, Dict, Optional, Tuple

UPSTREAM_PINNED_COMMIT = "09382a66ce6ee63d84038c8ee35a1fbc28cda58d"
UPSTREAM_PINNED_DATE = "2026-04-21"

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CANDIDATES = (
    os.path.join(_REPO_ROOT, "metabolic_accounting"),
    os.path.abspath(os.path.join(_REPO_ROOT, "..", "metabolic-accounting")),
    os.path.abspath(os.path.join(_REPO_ROOT, "..", "metabolic_accounting")),
)
for _p in _CANDIDATES:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
        break

try:
    from basin_states import (  # type: ignore
        new_air_basin,
        new_biology_basin,
        new_soil_basin,
        new_water_basin,
    )
    from reserves import Site  # type: ignore
    from accounting import compute_flow  # type: ignore
    from verdict import assess  # type: ignore
    _HAS_METABOLIC_ACCOUNTING = True
except Exception:
    _HAS_METABOLIC_ACCOUNTING = False


# Stress vector keys mirror metabolic-accounting's integration-test fixture.
# Magnitudes in the upstream test are O(3-6) per metric.
StressVector = Dict[Tuple[str, str], float]

DEFAULT_STRESS: StressVector = {
    ("site_soil", "carbon_fraction"): 0.0,
    ("site_air", "particulate_load"): 0.0,
    ("site_water", "aquifer_level"): 0.0,
    ("site_biology", "pollinator_index"): 0.0,
}


def _normalize_verdict(v: Any) -> Dict[str, Any]:
    """Flatten verdict.Verdict to a plain dict so callers don't need
    metabolic-accounting installed to consume the result."""
    return {
        "sustainable_yield_signal": v.sustainable_yield_signal,
        "basin_trajectory": v.basin_trajectory,
        "time_to_red": v.time_to_red,
        "forced_drawdown": v.forced_drawdown,
        "regeneration_debt": v.regeneration_debt,
        "metabolic_profit": v.metabolic_profit,
        "reported_profit": v.reported_profit,
        "profit_gap": v.profit_gap,
        "extraordinary_item_flagged": v.extraordinary_item_flagged,
        "extraordinary_item_amount": v.extraordinary_item_amount,
        "irreversible_metrics": list(v.irreversible_metrics),
        "warnings": list(v.warnings),
    }


def metabolic_check(
    revenue: float,
    direct_operating_cost: float,
    regeneration_paid: float = 0.0,
    stress: Optional[StressVector] = None,
) -> Optional[Dict[str, Any]]:
    """Run a single-step metabolic-accounting verdict.

    Constructs a fresh four-basin Site (soil/air/water/biology), applies
    `stress` (or DEFAULT_STRESS), computes glucose flow, and returns the
    Verdict normalized to a plain dict. The dict's
    `sustainable_yield_signal` field carries the GREEN/AMBER/RED/BLACK
    band; BLACK is reserved for irreversibility, not "very RED".

    Returns None when metabolic-accounting is not importable.
    """
    if not _HAS_METABOLIC_ACCOUNTING:
        return None

    site = Site(
        name="math_econ_bridge",
        basins={
            "site_soil": new_soil_basin(),
            "site_air": new_air_basin(),
            "site_water": new_water_basin(),
            "site_biology": new_biology_basin(),
        },
    )
    site.attach_defaults()
    step_result = site.step(stress or DEFAULT_STRESS, regenerate=False)
    flow = compute_flow(
        revenue=revenue,
        direct_operating_cost=direct_operating_cost,
        regeneration_paid=regeneration_paid,
        basins=site.basins,
        systems=[],
        site=site,
        step_result=step_result,
    )
    return _normalize_verdict(assess(site.basins, flow))


def stress_from_field_scenario(scenario: Dict[str, float]) -> StressVector:
    """Derive a four-basin stress vector from a Math-Econ field_system
    scenario. The mapping is heuristic — adjust as the contract evolves.

    soil_trend  (negative=degradation) -> site_soil/carbon_fraction
    disturbance                        -> site_air/particulate_load
    1 - water_retention                -> site_water/aquifer_level
    1 - nutrient_density               -> site_biology/pollinator_index

    Multipliers chosen so a typical degraded scenario yields stress in the
    O(3-6) range used by metabolic-accounting's integration test.
    """
    return {
        ("site_soil", "carbon_fraction"):
            max(0.0, -scenario.get("soil_trend", 0.0)) * 100.0,
        ("site_air", "particulate_load"):
            scenario.get("disturbance", 0.0) * 10.0,
        ("site_water", "aquifer_level"):
            max(0.0, 1.0 - scenario.get("water_retention", 1.0)) * 10.0,
        ("site_biology", "pollinator_index"):
            max(0.0, 1.0 - scenario.get("nutrient_density", 1.0)) * 10.0,
    }
