"""
infrastructure_precondition.py  —  C003

Infrastructure precondition capex exceeds vehicle capex for dispersed small
wells.

Falsifier: cost data showing dispersed-well infrastructure < vehicle fleet
cost.

The autonomous trucking narrative typically prices the truck and omits the
road. For a depot-to-Class-I-corridor route the road already exists. For
dispersed small wells most of the route does not exist as a paved,
lane-marked, HD-mappable surface, and the marginal cost of producing one
is borne by whoever wants automation — not by the road authority that
built the existing corridor.

Default unit costs are conservative US averages for 2025-era rural
construction. Override via the `unit_costs` keyword.

License: CC0-1.0
"""

from typing import Dict


# Conservative US 2025 rural construction defaults, USD.
DEFAULT_UNIT_COSTS: Dict[str, float] = {
    "rural_two_lane_paving_per_mile":   2_000_000.0,
    "lane_marking_per_mile":               25_000.0,
    "hd_mapping_per_mile":                 12_000.0,
    "receiving_pad_per_site":             150_000.0,
    "comms_tower_per_5_miles":            300_000.0,
}


def infrastructure_capex(route_miles: float,
                         well_density: float,
                         existing_pavement_pct: float,
                         unit_costs: Dict[str, float] | None = None) -> dict:
    """Estimate infrastructure capex required to make a route autonomous-viable.

    Args:
        route_miles: total route-mile inventory the deployment must cover.
        well_density: receiving sites per route-mile. Dispersed plays run
            0.05 - 0.2; consolidated frac pads run 1-5 per mile of in-pad
            road but only 0.01-0.05 along the haul corridor.
        existing_pavement_pct: 0.0 - 1.0, fraction of route already paved.

    Returns a dict with line items and per-route-mile totals.
    """
    uc = {**DEFAULT_UNIT_COSTS, **(unit_costs or {})}

    paving_miles  = route_miles * max(0.0, 1.0 - existing_pavement_pct)
    marking_miles = route_miles                       # always required
    mapping_miles = route_miles                       # always required
    receiving_sites = route_miles * well_density
    comms_towers  = max(1.0, route_miles / 5.0)

    paving   = paving_miles  * uc["rural_two_lane_paving_per_mile"]
    marking  = marking_miles * uc["lane_marking_per_mile"]
    mapping  = mapping_miles * uc["hd_mapping_per_mile"]
    receivers = receiving_sites * uc["receiving_pad_per_site"]
    comms    = comms_towers  * uc["comms_tower_per_5_miles"]

    total = paving + marking + mapping + receivers + comms
    per_route_mile = total / route_miles if route_miles > 0 else 0.0

    return {
        "line_items": {
            "paving":          paving,
            "lane_marking":    marking,
            "hd_mapping":      mapping,
            "receiving_pads":  receivers,
            "comms_towers":    comms,
        },
        "total_capex_usd":   total,
        "per_route_mile_usd": per_route_mile,
        "route_miles":       route_miles,
        "well_density":      well_density,
        "existing_pavement_pct": existing_pavement_pct,
    }


def precondition_threshold(capex: float, projected_revenue: float) -> bool:
    """C003 gate.

    Returns True (claim *unfalsified*, i.e. infrastructure is gating ROI) when
    per-route-mile infrastructure capex exceeds the threshold of $500k or
    when total capex exceeds projected revenue.
    """
    return capex > 500_000.0 or capex > projected_revenue


def c003_verdict(route_miles: float, well_density: float,
                 existing_pavement_pct: float, projected_revenue: float,
                 vehicle_fleet_cost: float,
                 unit_costs: Dict[str, float] | None = None) -> dict:
    cx = infrastructure_capex(route_miles, well_density,
                              existing_pavement_pct, unit_costs)
    per_mile = cx["per_route_mile_usd"]
    total = cx["total_capex_usd"]
    per_mile_threshold = per_mile > 500_000.0
    exceeds_fleet = total > vehicle_fleet_cost
    return {
        "claim_id": "C003",
        "per_route_mile_usd": per_mile,
        "total_capex_usd":    total,
        "vehicle_fleet_cost_usd": vehicle_fleet_cost,
        "infrastructure_exceeds_fleet": exceeds_fleet,
        "per_mile_threshold_met": per_mile_threshold,
        "infrastructure_exceeds_revenue": total > projected_revenue,
        "threshold_met":       per_mile_threshold or exceeds_fleet,
        "line_items": cx["line_items"],
        "falsifier": "cost data showing dispersed-well infrastructure < vehicle fleet cost",
    }


if __name__ == "__main__":
    # Consolidated corridor (Permian sand-haul style)
    print("consolidated:", c003_verdict(
        route_miles=40.0, well_density=0.05,
        existing_pavement_pct=0.95,
        projected_revenue=80_000_000.0,
        vehicle_fleet_cost=20_000_000.0,
    ))
    # Dispersed Bakken-style small wells
    print("dispersed:", c003_verdict(
        route_miles=180.0, well_density=0.18,
        existing_pavement_pct=0.15,
        projected_revenue=12_000_000.0,
        vehicle_fleet_cost=8_000_000.0,
    ))
