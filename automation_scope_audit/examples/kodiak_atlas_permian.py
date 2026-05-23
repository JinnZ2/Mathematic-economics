"""
kodiak_atlas_permian.py  —  works case

Stylized deployment matching the public profile of the Kodiak Robotics /
Atlas Energy Permian Basin frac-sand haul pilot: fixed depot-to-pad routes
in a consolidated play, on existing paved roads, with a narrow, repetitive
task surface. This is the geometry the autonomous trucking narrative was
designed for.

Even here, the audit exposes residual scope-collapse and unpriced
condition-monitoring / interface labor. The point is not that this case
fails outright — it is that the surplus is much smaller than the
marketing implies, and the structural claims still register.

Run: python automation_scope_audit/examples/kodiak_atlas_permian.py

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
    """50 weekly cycles of two fixed depot-to-pad routes."""
    log = []
    for i in range(25):
        log.append({
            "origin": "kingdom_depot",
            "destination": "atlas_pad_alpha",
            "waypoints": ["us285_south", "frac_road_7", "pad_alpha_gate"],
        })
        log.append({
            "origin": "kingdom_depot",
            "destination": "atlas_pad_bravo",
            "waypoints": ["us285_south", "frac_road_12", "pad_bravo_gate"],
        })
    return log


def run() -> dict:
    deployment_spec = {"deployment": "kodiak_atlas_permian"}

    # C001 - geometry
    route_log = build_route_log()
    c001 = scope_geometry.c001_verdict(
        route_log,
        infrastructure_state={"paved_pct": 0.98, "mapped_pct": 0.97},
    )

    # C003 - infrastructure precondition
    c003 = infrastructure_precondition.c003_verdict(
        route_miles=42.0,
        well_density=0.05,
        existing_pavement_pct=0.95,
        projected_revenue=120_000_000.0,
        vehicle_fleet_cost=22_000_000.0,
    )

    # C002 - embedded labor
    c002 = embedded_labor_audit.c002_verdict(
        deployment_spec,
        automated_tasks=["interstate_haul",
                         "rural_lead_in_navigation",
                         "lease_road_navigation"],
        pre_hours=8.0,
        post_hours=6.0,
    )

    # C004 - lifecycle EROI; consolidated Permian wells have meaningful tails
    c004 = lifecycle_eroi.c004_verdict(
        energy_input={"capex": 1.0e12, "opex": 2.5e12, "fuel": 1.2e12},
        energy_output={"delivered_oil": 2.6e13},
        decline_curve=[1.0, 0.55, 0.40, 0.31, 0.25, 0.21, 0.18, 0.16],
        depreciation_years=7,
    )

    # C005 - stranded asset
    c005 = stranded_asset_risk.c005_verdict(
        years_elapsed=5,
        equipment_type="purpose_built_autonomous",
        equipment_lifespan=7,
        well_decline_curve=[1.0, 0.55, 0.40, 0.31, 0.25, 0.21, 0.18, 0.16],
    )

    # C008 / C009 / C010
    c008 = condition_monitoring_audit.c008_verdict()
    c009 = condition_monitoring_audit.c009_verdict(
        human_caught=(condition_monitoring_audit.HUMAN_ONLY_PRECURSOR_CATCHES
                      + ["tire_visual", "low_pressure"]),
        sensor_caught=["low_pressure", "tire_visual",
                       "vibration_signature_match", "thermal_anomaly"],
    )
    c010 = condition_monitoring_audit.c010_verdict("engine", 0.3)

    # C006 / C007 — vendor language is typically broad even in the works case
    pitch = ("Our fully autonomous trucks now run revenue freight on the "
             "Atlas dedicated lane, replacing the driver and addressing the "
             "driver shortage.")
    c006 = scope_collapse_detector.c006_verdict(pitch, {
        "automated_categories": ["haul", "navigation"],
        "route_variance": c001["variance"],
        "infrastructure_state": {"paved_pct": 0.98, "mapped_pct": 0.97},
    })
    c007 = scope_collapse_detector.c007_verdict(pitch,
                                                 wage_change_pct=-4.0,
                                                 productivity_change_pct=8.0,
                                                 region="permian")

    # C011 / C012 / C013
    c011 = interface_labor_audit.c011_verdict()
    c012 = interface_labor_audit.c012_verdict(
        {"fleet_size": 60, "multipliers": {"customer_service_staff": 0.6}},
        reported_vehicle_tco_per_truck_usd=75_000.0)
    c013 = interface_labor_audit.c013_verdict(autonomous_handled_per_year=900)

    return {
        "scenario": "kodiak_atlas_permian (works case)",
        "C001": c001, "C002": c002, "C003": c003, "C004": c004,
        "C005": c005, "C006": c006, "C007": c007, "C008": c008,
        "C009": c009, "C010": c010, "C011": c011, "C012": c012,
        "C013": c013,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
