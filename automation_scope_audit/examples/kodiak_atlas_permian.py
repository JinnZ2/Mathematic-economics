"""
kodiak_atlas_permian.py  —  works case

Stylized deployment matching the public profile of the Kodiak Robotics /
Atlas Energy Permian Basin frac-sand haul pilot: fixed depot-to-pad routes
in a consolidated play, on existing paved roads, with a narrow, repetitive
task surface. This is the geometry the autonomous trucking narrative was
designed for.

Even here, the audit exposes residual scope-collapse, unpriced
condition-monitoring labor, externalized interface costs, missing
constraint-validation authority, and the legal/regulatory framework
premium. The point is not that this case fails outright — it is that the
surplus is much smaller than the marketing implies, and the structural
claims still register.

Run: python automation_scope_audit/examples/kodiak_atlas_permian.py

License: CC0-1.0
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from automation_scope_audit.modules import (
    meta_scope_guard,
    scope_geometry,
    infrastructure_precondition,
    embedded_labor_audit,
    lifecycle_eroi,
    stranded_asset_risk,
    condition_monitoring_audit,
    scope_collapse_detector,
    interface_externalization_audit,
    constraint_validation_audit,
    legal_liability_audit,
    cognitive_monoculture_audit,
    thermodynamic_accounting_audit,
    scaling_audit,
    institutional_dynamics_audit,
    systemic_precondition_audit,
    economic_energy_grounding_audit,
    unified_capital_accounting_audit,
    engineering_grade_validation_audit,
)


def build_route_log() -> list[dict]:
    """50 weekly cycles of two fixed depot-to-pad routes."""
    log = []
    for _ in range(25):
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
    # C001 - geometry (Jaccard-based)
    c001 = scope_geometry.c001_verdict(
        build_route_log(),
        infrastructure_state={"paved_pct": 0.98, "mapped_pct": 0.97},
    )

    # C003 - infrastructure precondition with existing-state discounts
    c003 = infrastructure_precondition.c003_verdict(
        route_miles=42.0, well_density=0.05,
        existing_state={
            "existing_pavement_pct":  0.98,
            "existing_marking_pct":   0.92,
            "existing_mapping_pct":   0.85,
            "existing_receiving_pct": 0.80,
            "existing_comms_pct":     0.95,
            "existing_drainage_pct":  0.88,
            "existing_signage_pct":   0.92,
        },
        projected_revenue=120_000_000.0,
        vehicle_fleet_cost=22_000_000.0,
    )

    # C002 - embedded labor with automation-status map
    c002 = embedded_labor_audit.c002_verdict(
        status_map={
            "interstate_haul":           "fully_automated",
            "intrastate_haul":           "fully_automated",
            "rural_lead_in_navigation":  "fully_automated",
            "lease_road_navigation":     "partially_automated",
            "wellsite_positioning":      "remote_operator",
            "pump_hookup_disconnect":    "human_required",
            "pump_operation_monitoring": "human_required",
            "load_securement":           "human_required",
            "pretrip_inspection":        "remote_operator",
            "posttrip_inspection":       "remote_operator",
            "fluid_and_tire_checks":     "human_required",
            "regulatory_paperwork":      "partially_automated",
            "customer_interaction":      "remote_operator",
        },
        pre_hours=8.0, post_hours=6.0,
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

    # C006 / C007 — vendor language is typically broad even in works case
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

    # C011 / C012 / C013 — interface externalization
    c011 = interface_externalization_audit.c011_verdict()
    c012 = interface_externalization_audit.c012_verdict(
        # Works case: customer-receiving is consolidated (a few Atlas pads),
        # so heterogeneity miss-rate is lower.
        miss_rates={**interface_externalization_audit.DEFAULT_VARIANT_MISS_RATE,
                    "customer_receiving": 0.05,
                    "roadside_services":  0.10})
    c013 = interface_externalization_audit.c013_verdict(
        multipliers={"mobile_tech_share": 0.6,
                     "customer_service_share": 0.5})

    # C014 / C015 / C016 — constraint validation
    c014 = constraint_validation_audit.c014_verdict()
    c015 = constraint_validation_audit.c015_verdict()
    c016 = constraint_validation_audit.c016_verdict(
        # Works case: a few corridor-specific overrides are well-handled
        coverage_pct={"weather_proactive_shutdown": 0.55,
                      "novel_collision_avoidance": 0.60,
                      "load_settlement_response":  0.40})

    # C017 — legal/regulatory framework
    c017 = legal_liability_audit.c017_verdict(fleet_size=60)

    # C018 / C019 — cognitive monoculture (works case: early in transition,
    # dispatchers still see enough variant routes that retention is higher)
    early_transition_skills = {
        "manual_route_planning":     0.10,
        "anomaly_diagnosis":         0.20,
        "field_mechanical_repair":   0.20,
        "customer_negotiation":      0.20,
        "regulatory_field_judgment": 0.15,
        "degraded_mode_operation":   0.15,
    }
    c018 = cognitive_monoculture_audit.c018_verdict(
        skill_weights=early_transition_skills,
        years_into_transition=2.0)
    c019 = cognitive_monoculture_audit.c019_verdict(
        skill_weights=early_transition_skills,
        years_into_transition=2.0,
        edge_case_profile={"annual_frequency_per_vehicle": 0.3})

    # C020 — thermodynamic accounting (works case: short corridor, lower
    # telemetry hours, fewer sensors per truck)
    c020 = thermodynamic_accounting_audit.c020_verdict(
        fleet_size=60,
        sensor_inventory={"lidar_unit": 3, "camera_unit": 6,
                          "radar_unit": 4, "thermal_imager": 1,
                          "imu_unit": 2},
        backend_location="cellular",
        fuel_saved_kwh=7_500.0,           # consolidated corridor: bigger savings
        truck_operations_kwh=32_000.0)

    # C000 — meta-claim: works case pitch is the marketing language
    permian_pitch = (
        "Our autonomous trucks now run revenue freight on the Atlas "
        "dedicated lane, replacing the driver and addressing the driver "
        "shortage."
    )
    c000 = meta_scope_guard.c000_verdict(permian_pitch)

    # C021 — scaling: works case is a 60-truck fleet, well below the
    # default optimum (~970), so the structural concern about over-scaling
    # does not register here but amortization-gymnastics still does
    # because the pitch language uses generic "scale" framing.
    c021 = scaling_audit.c021_verdict(60, claim_text=permian_pitch)

    # C022 / C024 — institutional dynamics: Atlas Energy is a major
    # operator, so the consolidated-corridor deployment sits inside a
    # large-institution context. Use 6,000 as the relevant unit count.
    c022 = institutional_dynamics_audit.c022_verdict(6_000)
    c023 = institutional_dynamics_audit.c023_verdict()
    c024 = institutional_dynamics_audit.c024_verdict(6_000,
        adaptive_response="partial")

    # C025 / C026 — systemic preconditions. Works case uses
    # hybrid-with-safety-driver to model the realistic Permian pilot
    # configuration: an on-board safety operator backs up the autonomy
    # stack. Earth-system trends use defaults.
    c025 = systemic_precondition_audit.c025_verdict(
        deployment_scale=60,
        deployment_type="hybrid_with_safety_driver",
        claim_text=permian_pitch)
    c026 = systemic_precondition_audit.c026_verdict(claim_text=permian_pitch)

    # C027 — energy-grounding validity of the pitch text
    c027 = economic_energy_grounding_audit.c027_verdict(permian_pitch)

    # C028 — institutional blindness: Atlas / Kodiak operate inside a
    # mid-sized institutional context with limited but nonzero pivot
    # capacity (they pivoted from owner-operator to autonomous, so the
    # institution has shown some adaptability).
    c028 = economic_energy_grounding_audit.c028_verdict(
        model_claims=[permian_pitch,
                       "scaling reduces per-vehicle cost"],
        external_constraints=[
            "climate-driven route closure rate",
            "semiconductor supply chain volatility",
            "rare-earth export licensing",
            "FMCSA rule volatility",
            "labor displacement and demand contraction",
        ],
        organization_type="hierarchical",
        model_dependence=0.70,
        alternative_models_available=2)

    # C029 / C030 — unified capital accounting. Permian works-case
    # deployment scaled to 60-truck fleet equivalent.
    permian_deployment = {
        "name": "kodiak_atlas_permian_60_truck",
        "annual_financial_gain_usd": 18_000_000.0,
        "capitals": {
            "financial":     18_000_000.0,
            "labor":          80.0,
            "environmental":  6_500.0,    # tons CO2/yr for backend + manufacturing
            "biological":     0.005,
            "thermodynamic":  18_000.0,   # exergy_kwh/yr off-vehicle
            "social":         0.020,
            "temporal":       12.0,
            "health":         2.0,
            "regulatory":     0.010,
        },
    }
    # C029 takes the *reported* accounting, not the auditor's full picture
    # — to model what the marketing / financial report actually counts.
    permian_reported = {
        "capitals": {"financial": 18_000_000.0, "labor": 80.0},
    }
    c029 = unified_capital_accounting_audit.c029_verdict(permian_reported)
    # C030 takes the auditor's full picture: the unified accounting that
    # reveals the deficit the reported picture omits.
    c030 = unified_capital_accounting_audit.c030_verdict(
        permian_deployment, time_horizon=30,
        model_claims=[permian_pitch])

    # C031 / C032 — engineering-grade validation. Works case: the Kodiak/
    # Atlas pilot models corridor economics on 5 years of Permian sand-haul
    # data, all drawn from a single regime (stable / mild-volatile). No
    # documented stress test against supply-constrained or demand-shocked
    # regimes.
    c031 = engineering_grade_validation_audit.c031_verdict(
        permian_pitch)
    c032 = engineering_grade_validation_audit.c032_verdict(
        model={"regimes_validated": ["stable"]},
        training_regime="stable",
        deployment_regime="volatile",
        claim=permian_pitch)

    return {
        "scenario": "kodiak_atlas_permian (works case)",
        "C000": c000,
        "C001": c001, "C002": c002, "C003": c003, "C004": c004,
        "C005": c005, "C006": c006, "C007": c007, "C008": c008,
        "C009": c009, "C010": c010, "C011": c011, "C012": c012,
        "C013": c013, "C014": c014, "C015": c015, "C016": c016,
        "C017": c017, "C018": c018, "C019": c019, "C020": c020,
        "C021": c021, "C022": c022, "C023": c023, "C024": c024,
        "C025": c025, "C026": c026, "C027": c027, "C028": c028,
        "C029": c029, "C030": c030, "C031": c031, "C032": c032,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
