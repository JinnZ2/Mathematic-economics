"""
dispersed_wellsite.py  —  fails case

Stylized deployment for dispersed Bakken / Powder River small-pad service:
many short-life wells, variable lease-road routing, sparse paving, weather
volatility, owner-operator service economy. This is the geometry the
autonomous trucking narrative is most often *applied to* in investor
decks but where the structural claims register most strongly.

Run: python automation_scope_audit/examples/dispersed_wellsite.py

License: CC0-1.0
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from automation_scope_audit.modules import (
    scope_geometry,
    infrastructure_precondition,
    embedded_labor_audit,
    lifecycle_eroi,
    stranded_asset_risk,
    condition_monitoring_audit,
    scope_collapse_detector,
    interface_labor_audit,
)


def build_route_log() -> list[dict]:
    """120 service runs across a rotating set of dispersed wellsites."""
    log = []
    well_ids = [f"well_{i:02d}" for i in range(35)]
    for i in range(120):
        wid = well_ids[(i * 7) % len(well_ids)]
        # waypoint sequence rotates with seasonal mud / closures
        wp = [f"lease_seg_{(i + j * 3) % 11}" for j in range(3)]
        log.append({
            "origin": "service_yard",
            "destination": wid,
            "waypoints": wp,
        })
    return log


def run() -> dict:
    deployment_spec = {"deployment": "dispersed_wellsite_service"}

    c001 = scope_geometry.c001_verdict(
        build_route_log(),
        infrastructure_state={"paved_pct": 0.18, "mapped_pct": 0.10},
    )

    c003 = infrastructure_precondition.c003_verdict(
        route_miles=220.0,
        well_density=0.22,
        existing_pavement_pct=0.18,
        projected_revenue=14_000_000.0,
        vehicle_fleet_cost=9_000_000.0,
    )

    # Only haul gets automated; site_work is what dispersed service IS.
    c002 = embedded_labor_audit.c002_verdict(
        deployment_spec,
        automated_tasks=["interstate_haul"],
        pre_hours=10.5,
        post_hours=11.0,
    )

    # Steep shale-style decline against 7yr depreciation
    decline = [1.0, 0.28, 0.16, 0.11, 0.08, 0.06]
    c004 = lifecycle_eroi.c004_verdict(
        energy_input={"capex": 1.0e12, "opex": 0.7e12, "fuel": 0.6e12},
        energy_output={"delivered_oil": 4.8e12},
        decline_curve=decline,
        depreciation_years=7,
    )

    c005 = stranded_asset_risk.c005_verdict(
        years_elapsed=5,
        equipment_type="autonomous_retrofit",
        equipment_lifespan=7,
        well_decline_curve=decline,
    )

    c008 = condition_monitoring_audit.c008_verdict()
    c009 = condition_monitoring_audit.c009_verdict(
        human_caught=condition_monitoring_audit.HUMAN_ONLY_PRECURSOR_CATCHES,
        sensor_caught=["low_pressure", "thermal_anomaly"],
    )
    c010 = condition_monitoring_audit.c010_verdict("engine", 0.85)

    pitch = ("Driverless trucks fully automate oilfield logistics, ending "
             "the driver shortage and replacing the trucker.")
    c006 = scope_collapse_detector.c006_verdict(pitch, {
        "automated_categories": ["haul"],
        "route_variance": c001["variance"],
        "infrastructure_state": {"paved_pct": 0.18, "mapped_pct": 0.10},
        "well_decline_years": len(decline),
        "equipment_lifespan_years": 7,
    })
    c007 = scope_collapse_detector.c007_verdict(pitch,
                                                 wage_change_pct=-22.0,
                                                 productivity_change_pct=2.0,
                                                 region="bakken")

    c011 = interface_labor_audit.c011_verdict()
    c012 = interface_labor_audit.c012_verdict(
        {"fleet_size": 12,
         "multipliers": {"mobile_tech_fleet_share": 2.5,
                         "remote_diagnostic_center": 1.5}},
        reported_vehicle_tco_per_truck_usd=65_000.0)
    c013 = interface_labor_audit.c013_verdict(autonomous_handled_per_year=120)

    return {
        "scenario": "dispersed_wellsite (fails case)",
        "C001": c001, "C002": c002, "C003": c003, "C004": c004,
        "C005": c005, "C006": c006, "C007": c007, "C008": c008,
        "C009": c009, "C010": c010, "C011": c011, "C012": c012,
        "C013": c013,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
