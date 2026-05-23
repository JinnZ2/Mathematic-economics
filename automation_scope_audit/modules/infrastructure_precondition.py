"""
infrastructure_precondition.py  —  C003

Infrastructure precondition capex exceeds vehicle capex for dispersed small
wells.

Falsifier: cost data showing dispersed-well infrastructure < vehicle fleet
cost.

The autonomous trucking narrative typically prices the truck and omits the
road. For a depot-to-Class-I-corridor route the road already exists; for
dispersed small wells most of the route does not exist as a paved,
lane-marked, HD-mappable surface, and the marginal cost of producing one
is borne by whoever wants automation — not by the road authority that
built the existing corridor.

Existing-state discounts: every line item has an `existing_*_pct` field on
[0.0, 1.0]. Only the *missing* fraction is priced. Defaults assume nothing
is in place; pass a richer state dict to model a brownfield deployment.

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
    "drainage_per_mile":                   80_000.0,
    "signage_per_mile":                    18_000.0,
}


def _missing_fraction(existing_state: Dict[str, float], key: str) -> float:
    """Returns the fraction of the line item that must be built. Clamped."""
    pct = float(existing_state.get(key, 0.0))
    return max(0.0, min(1.0, 1.0 - pct))


def infrastructure_capex(route_miles: float,
                         well_density: float,
                         existing_state: Dict[str, float] | None = None,
                         unit_costs: Dict[str, float] | None = None) -> dict:
    """Estimate infrastructure capex required to make a route autonomous-viable.

    Args:
        route_miles: total route-mile inventory the deployment must cover.
        well_density: receiving sites per route-mile.
        existing_state: dict with any of:
              `existing_pavement_pct`, `existing_marking_pct`,
              `existing_mapping_pct`, `existing_receiving_pct`,
              `existing_comms_pct`, `existing_drainage_pct`,
              `existing_signage_pct`
            each in [0.0, 1.0]. Missing keys default to 0.0 (nothing in
            place, full build required).

    Returns a dict with line items (before-discount and after-discount),
    line-item discounts, totals, and per-route-mile totals.
    """
    uc = {**DEFAULT_UNIT_COSTS, **(unit_costs or {})}
    state = existing_state or {}

    receiving_sites = route_miles * well_density
    comms_towers   = max(1.0, route_miles / 5.0)

    gross = {
        "paving":         route_miles * uc["rural_two_lane_paving_per_mile"],
        "lane_marking":   route_miles * uc["lane_marking_per_mile"],
        "hd_mapping":     route_miles * uc["hd_mapping_per_mile"],
        "receiving_pads": receiving_sites * uc["receiving_pad_per_site"],
        "comms_towers":   comms_towers * uc["comms_tower_per_5_miles"],
        "drainage":       route_miles * uc["drainage_per_mile"],
        "signage":        route_miles * uc["signage_per_mile"],
    }
    missing = {
        "paving":         _missing_fraction(state, "existing_pavement_pct"),
        "lane_marking":   _missing_fraction(state, "existing_marking_pct"),
        "hd_mapping":     _missing_fraction(state, "existing_mapping_pct"),
        "receiving_pads": _missing_fraction(state, "existing_receiving_pct"),
        "comms_towers":   _missing_fraction(state, "existing_comms_pct"),
        "drainage":       _missing_fraction(state, "existing_drainage_pct"),
        "signage":        _missing_fraction(state, "existing_signage_pct"),
    }
    net = {k: gross[k] * missing[k] for k in gross}
    total_gross = sum(gross.values())
    total_net   = sum(net.values())
    per_route_mile = total_net / route_miles if route_miles > 0 else 0.0

    return {
        "gross_line_items":   gross,
        "missing_fraction":   missing,
        "net_line_items":     net,
        "total_gross_usd":    total_gross,
        "total_capex_usd":    total_net,
        "per_route_mile_usd": per_route_mile,
        "route_miles":        route_miles,
        "well_density":       well_density,
        "existing_state":     dict(state),
    }


def precondition_threshold(per_route_mile_capex: float,
                            total_capex: float,
                            projected_revenue: float) -> bool:
    """C003 gate.

    Returns True when per-route-mile infrastructure capex exceeds the
    threshold of $500k, or when total capex exceeds projected revenue.
    """
    return per_route_mile_capex > 500_000.0 or total_capex > projected_revenue


def c003_verdict(route_miles: float, well_density: float,
                 existing_state: Dict[str, float] | None,
                 projected_revenue: float,
                 vehicle_fleet_cost: float,
                 unit_costs: Dict[str, float] | None = None) -> dict:
    cx = infrastructure_capex(route_miles, well_density, existing_state,
                              unit_costs)
    per_mile = cx["per_route_mile_usd"]
    total = cx["total_capex_usd"]
    per_mile_threshold = per_mile > 500_000.0
    exceeds_fleet = total > vehicle_fleet_cost
    return {
        "claim_id": "C003",
        "per_route_mile_usd": per_mile,
        "total_capex_usd":    total,
        "total_gross_usd":    cx["total_gross_usd"],
        "vehicle_fleet_cost_usd": vehicle_fleet_cost,
        "infrastructure_exceeds_fleet": exceeds_fleet,
        "per_mile_threshold_met": per_mile_threshold,
        "infrastructure_exceeds_revenue": total > projected_revenue,
        "threshold_met":       per_mile_threshold or exceeds_fleet,
        "net_line_items":      cx["net_line_items"],
        "missing_fraction":    cx["missing_fraction"],
        "existing_state":      cx["existing_state"],
        "falsifier": "cost data showing dispersed-well infrastructure < vehicle fleet cost",
    }


if __name__ == "__main__":
    # Consolidated corridor (Permian sand-haul style)
    print("consolidated:", c003_verdict(
        route_miles=40.0, well_density=0.05,
        existing_state={
            "existing_pavement_pct": 0.95,
            "existing_marking_pct":  0.90,
            "existing_mapping_pct":  0.85,
            "existing_receiving_pct": 0.80,
            "existing_comms_pct":    0.95,
            "existing_drainage_pct": 0.85,
            "existing_signage_pct":  0.90,
        },
        projected_revenue=80_000_000.0,
        vehicle_fleet_cost=20_000_000.0,
    ))
    # Dispersed Bakken-style small wells
    print("dispersed:", c003_verdict(
        route_miles=180.0, well_density=0.18,
        existing_state={
            "existing_pavement_pct": 0.15,
            "existing_marking_pct":  0.05,
            "existing_mapping_pct":  0.02,
            "existing_receiving_pct": 0.10,
            "existing_comms_pct":    0.30,
            "existing_drainage_pct": 0.10,
            "existing_signage_pct":  0.20,
        },
        projected_revenue=12_000_000.0,
        vehicle_fleet_cost=8_000_000.0,
    ))
