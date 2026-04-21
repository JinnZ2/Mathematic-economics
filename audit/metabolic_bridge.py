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
#   commit: 437e8551634ed33a613cdb41c41f28a51136eec7
#   date:   2026-04-21
# To upgrade, fetch the new HEAD, re-run `python tests/test_bridges.py`
# with that checkout in place, and bump UPSTREAM_PINNED_COMMIT below.

import os
import sys
from typing import Any, Dict, Optional, Tuple

UPSTREAM_PINNED_COMMIT = "437e8551634ed33a613cdb41c41f28a51136eec7"
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
    basin_overrides: Optional[Dict[str, Dict[str, float]]] = None,
) -> Optional[Dict[str, Any]]:
    """Run a single-step metabolic-accounting verdict.

    Constructs a fresh four-basin Site (soil/air/water/biology), optionally
    overrides individual basin `state[metric]` values from `basin_overrides`
    to reflect steady-state degradation, applies `stress` (or DEFAULT_STRESS)
    as a single-step shock, computes glucose flow, and returns the Verdict
    normalized to a plain dict.

    `basin_overrides` keys are basin names ("site_soil", "site_air",
    "site_water", "site_biology") and values are partial state dicts:

        {"site_soil": {"carbon_fraction": 0.02}}

    Metrics not listed retain their upstream defaults. Use
    `basins_from_field_scenario(...)` to derive these from a Math-Econ
    `field_system` scenario (sets steady-state damage that moves
    regeneration_debt and the sustainable_yield_signal). Use `stress` for
    single-step shock events (hits reserves first — see
    `stress_from_field_scenario` docstring for why steady-state scenarios
    should prefer `basin_overrides`).

    The dict's `sustainable_yield_signal` field carries the
    GREEN/AMBER/RED/BLACK band; BLACK is reserved for irreversibility,
    not "very RED".

    Returns None when metabolic-accounting is not importable.
    """
    if not _HAS_METABOLIC_ACCOUNTING:
        return None

    basins = {
        "site_soil": new_soil_basin(),
        "site_air": new_air_basin(),
        "site_water": new_water_basin(),
        "site_biology": new_biology_basin(),
    }
    if basin_overrides:
        for basin_name, metric_overrides in basin_overrides.items():
            basin = basins.get(basin_name)
            if basin is None or not metric_overrides:
                continue
            # BasinState.state is a plain Dict[str, float]; mutating
            # contents is allowed even on a frozen dataclass, since the
            # dict reference itself is unchanged.
            for metric_key, new_value in metric_overrides.items():
                if metric_key in basin.state:
                    basin.state[metric_key] = new_value

    site = Site(name="math_econ_bridge", basins=basins)
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

    Multipliers (100 / 10 / 10 / 10) calibrated so a typical degraded
    scenario (e.g. precision_ag: soil_trend=-0.05, water_retention=0.48,
    disturbance=0.30, nutrient_density=0.40) yields stress values of
    5.0 / 3.0 / 5.2 / 6.0 — matching the O(3-6) range used by
    metabolic-accounting's own integration test fixture.

    ----
    Calibration note: what this mapping discriminates and what it does not.

    Upstream's `Site.step(stress, regenerate=False)` partitions stress
    through primary/secondary/tertiary reserves before any excess reaches
    basin state. In a fresh Site, a single step of stress in the 3-6 range
    (and even 100x that) is almost entirely absorbed by reserves. Verified
    behavior at `UPSTREAM_PINNED_COMMIT`:

        zero stress     -> metabolic_profit=386.7, regen_debt=13.30, AMBER
        precision_ag    -> metabolic_profit=371.4, regen_debt=13.30, AMBER
        100x stress     -> metabolic_profit= 55.9, regen_debt=13.30, AMBER

    So `metabolic_profit` DOES discriminate scenarios (via reserve
    drawdown cost), but `regeneration_debt` and `sustainable_yield_signal`
    reflect the basin baseline and do not vary with stress at these
    magnitudes. The constant 13.30 is the regeneration cost of a fresh
    default Site's baseline degradation (soil carbon_fraction=0.05/0.08,
    air particulates=0.04, etc.), not something our stress is touching.

    To drive scenario-dependent `regeneration_debt` or signal transitions,
    a caller would need to modify basin `state[metric]` values directly
    rather than routing through `stress`. That is a deliberate
    follow-up — this helper covers the shock / stress-event path only.
    Scenarios describing steady-state degradation (which is what the
    field_system scenarios are) should treat `metabolic_profit` as the
    primary discriminator from this bridge.
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


def basins_from_field_scenario(
    scenario: Dict[str, float],
) -> Dict[str, Dict[str, float]]:
    """Derive per-basin `state[metric]` overrides from a Math-Econ
    `field_system` scenario — the steady-state degradation companion to
    `stress_from_field_scenario`.

    Unlike stress (absorbed by reserves before reaching basins), these
    overrides set the basin state directly so upstream's
    `required_regeneration_cost` sees real scenario-dependent damage. At
    the pinned upstream commit, a single step of stress in the 3-6 range
    leaves `regeneration_debt` pinned at the fresh-basin baseline (13.30);
    applying these overrides instead makes that field discriminate.

    Mapping (baseline -> healthy -> degraded state values):

        soil_trend: scenario + 0.05, clamped to [0, 0.08]
            positive trend -> carbon_fraction above 0.05 baseline
            strongly negative trend -> near 0 (cliff at 0.02)
        disturbance (0..1): particulate_load = disturbance (high_is_bad)
            0.0 -> clean, 1.0 -> saturated
        water_retention (0..1): aquifer_level = water_retention
            1.0 -> full, 0.0 -> empty (cliff at 0.5)
        nutrient_density (0..1): pollinator_index = nutrient_density
            1.0 -> rich, 0.0 -> depleted (cliff at 0.4)

    Metrics the scenario doesn't describe (microbial_load, permeability,
    chemical_load, surface_flow, etc.) retain their upstream defaults.
    """
    soil_trend = scenario.get("soil_trend", 0.0)
    disturbance = scenario.get("disturbance", 0.0)
    water_retention = scenario.get("water_retention", 1.0)
    nutrient_density = scenario.get("nutrient_density", 1.0)

    return {
        "site_soil": {
            "carbon_fraction": max(0.0, min(0.08, 0.05 + soil_trend)),
        },
        "site_air": {
            "particulate_load": max(0.0, min(1.0, disturbance)),
        },
        "site_water": {
            "aquifer_level": max(0.0, min(1.0, water_retention)),
        },
        "site_biology": {
            "pollinator_index": max(0.0, min(1.0, nutrient_density)),
        },
    }
