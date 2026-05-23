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

# Deliberately partial — the dispersed-wellsite vendor pitch does NOT
# publish scope. The gate fails this spec; run.py refuses to audit
# unless `--allow-missing-scope` is set. This is the correct fail-safe
# behavior the framework exists to enforce.
DEPLOYMENT_SPEC = {
    "beneficiary":        "scaling efficiency",                  # narrative
    "conditions":         None,                                  # absent
    "time_period":        "long-term",                           # narrative
    "resource":           "capital",                             # ambiguous
    "externalized_cost":  None,                                  # absent
    "profit_allocation":  None,                                  # absent
    "falsifier":          None,                                  # absent
}


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
    substrate_primacy_audit,
    adversarial_overhead_audit,
    governance_thermodynamics_audit,
)


def build_route_log() -> list[dict]:
    """120 service runs across a rotating set of dispersed wellsites."""
    log = []
    well_ids = [f"well_{i:02d}" for i in range(35)]
    for i in range(120):
        wid = well_ids[(i * 7) % len(well_ids)]
        # waypoint set rotates with seasonal mud / closures
        wp = [f"lease_seg_{(i + j * 3) % 11}" for j in range(3)]
        log.append({
            "origin": "service_yard",
            "destination": wid,
            "waypoints": wp,
        })
    return log


def run() -> dict:
    c001 = scope_geometry.c001_verdict(
        build_route_log(),
        infrastructure_state={"paved_pct": 0.18, "mapped_pct": 0.10},
    )

    c003 = infrastructure_precondition.c003_verdict(
        route_miles=220.0, well_density=0.22,
        existing_state={
            "existing_pavement_pct":  0.18,
            "existing_marking_pct":   0.08,
            "existing_mapping_pct":   0.02,
            "existing_receiving_pct": 0.10,
            "existing_comms_pct":     0.30,
            "existing_drainage_pct":  0.10,
            "existing_signage_pct":   0.18,
        },
        projected_revenue=14_000_000.0,
        vehicle_fleet_cost=9_000_000.0,
    )

    # Only interstate haul gets automated; site_work is what dispersed service IS.
    c002 = embedded_labor_audit.c002_verdict(
        status_map={"interstate_haul": "fully_automated"},
        pre_hours=10.5, post_hours=11.0,
    )

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

    # C011 / C012 / C013 — dispersed deployments stress every dimension.
    c011 = interface_externalization_audit.c011_verdict(
        mobile_escalation_pct=0.45)
    c012 = interface_externalization_audit.c012_verdict(
        # Many small operators -> high customer-receiving variance;
        # multi-jurisdictional -> higher regulatory miss-rate.
        miss_rates={**interface_externalization_audit.DEFAULT_VARIANT_MISS_RATE,
                    "customer_receiving": 0.32,
                    "regulatory":         0.18,
                    "roadside_services":  0.45})
    c013 = interface_externalization_audit.c013_verdict(
        multipliers={"mobile_tech_share": 2.5,
                     "remote_operator_share": 1.4,
                     "customer_service_share": 1.5,
                     "diagnostic_specialist_share": 1.3})

    # C014 / C015 / C016 — constraint validation
    c014 = constraint_validation_audit.c014_verdict()
    c015 = constraint_validation_audit.c015_verdict()
    c016 = constraint_validation_audit.c016_verdict()  # use defaults

    # C017 — legal/regulatory framework (small fleet)
    c017 = legal_liability_audit.c017_verdict(fleet_size=12)

    # C018 / C019 — cognitive monoculture (fails case: deep into transition,
    # variable routes mean dispatchers have lost the most-needed skills)
    c018 = cognitive_monoculture_audit.c018_verdict(
        years_into_transition=6.0)
    c019 = cognitive_monoculture_audit.c019_verdict(
        years_into_transition=6.0,
        edge_case_profile={"annual_frequency_per_vehicle": 1.6,
                            "downstream_cascade_usd": 60_000.0})

    # C020 — thermodynamic accounting (fails case: small fleet pays heavier
    # fixed-pool overhead, sat backhaul where cellular doesn't reach,
    # higher sensor count for terrain handling)
    c020 = thermodynamic_accounting_audit.c020_verdict(
        fleet_size=12,
        sensor_inventory={"lidar_unit": 5, "camera_unit": 10,
                          "radar_unit": 8, "thermal_imager": 3,
                          "imu_unit": 3},
        backend_location="satellite",
        fuel_saved_kwh=2_500.0,
        truck_operations_kwh=38_000.0)

    # C000 — meta-claim: dispersed-case marketing pitch
    c000 = meta_scope_guard.c000_verdict(pitch)

    # C021 — scaling: fails case is small (12 trucks); structural concern
    # about over-scaling does not register but amortization-gymnastics
    # framing in the pitch does. To exercise the over-scale path, the
    # downstream caller can rerun with a megafleet hypothesis; the
    # default here represents the actual deployment.
    c021 = scaling_audit.c021_verdict(12, claim_text=pitch)

    # C022 / C023 / C024 — institutional dynamics: dispersed deployments
    # are typically run by small operators, but the *narrative* about
    # autonomous trucking is set by very-large institutions. Score the
    # narrative-setting institutions (50,000-unit equivalent), not the
    # operator.
    c022 = institutional_dynamics_audit.c022_verdict(50_000)
    c023 = institutional_dynamics_audit.c023_verdict()
    c024 = institutional_dynamics_audit.c024_verdict(50_000,
        adaptive_response="doubled_down")

    # C025 / C026 — fails case is the autonomous-no-driver hypothesis
    # being marketed at dispersed wellsites: zero degraded-mode capability,
    # so even a small fleet (12) registers the structural concern because
    # any single precondition failure is sufficient.
    c025 = systemic_precondition_audit.c025_verdict(
        deployment_scale=12,
        deployment_type="autonomous_no_driver",
        claim_text=pitch)
    c026 = systemic_precondition_audit.c026_verdict(claim_text=pitch)

    # C027 — fails case pitch fails energy grounding
    c027 = economic_energy_grounding_audit.c027_verdict(pitch)

    # C028 — captured / monolithic institution with zero alternative
    # models available (the narrative-setting institutions in autonomous
    # trucking have systematically defunded distributed and human-driver
    # alternatives over the past decade)
    c028 = economic_energy_grounding_audit.c028_verdict(
        model_claims=[pitch,
                       "autonomous always wins at scale",
                       "automation is more efficient than human operation"],
        external_constraints=[
            "rare-earth concentration in single jurisdiction",
            "Kessler syndrome risk to satellite navigation",
            "grid frequency instability under renewable transition",
            "labor displacement reduces consumer demand",
            "climate-driven route closure rate",
            "FMCSA / state DOT rule volatility",
        ],
        organization_type="captured",
        model_dependence=0.95,
        alternative_models_available=0)

    # C029 / C030 — unified capital accounting, scaled for the 12-truck
    # dispersed deployment but with backend-pool overheads that don't
    # amortize at this scale.
    dispersed_deployment = {
        "name": "dispersed_wellsite_12_truck",
        "annual_financial_gain_usd": 1_800_000.0,
        "capitals": {
            "financial":     1_800_000.0,
            "labor":         20.0,
            "environmental": 4_800.0,    # backend + manufacturing scaled
            "biological":    0.003,
            "thermodynamic": 9_000.0,
            "social":        0.030,
            "temporal":      8.0,
            "health":        1.2,
            "regulatory":    0.020,
        },
    }
    # C029 takes only the reported (financial + labor) picture
    dispersed_reported = {
        "capitals": {"financial": 1_800_000.0, "labor": 20.0},
    }
    c029 = unified_capital_accounting_audit.c029_verdict(dispersed_reported)
    # C030 takes the full audit picture
    c030 = unified_capital_accounting_audit.c030_verdict(
        dispersed_deployment, time_horizon=30,
        model_claims=[pitch])

    # C031 / C032 — engineering-grade validation. Fails case: the
    # dispersed-wellsite economic model is calibrated against 10-yr
    # carrier economics drawn entirely from a stable / mild-volatile
    # regime. Deployment conditions in 2026+ are simultaneously
    # supply-constrained (rare-earth, semiconductor) AND demand-shocked
    # (well decline acceleration); the model has been validated against
    # neither.
    c031 = engineering_grade_validation_audit.c031_verdict(pitch)
    c032 = engineering_grade_validation_audit.c032_verdict(
        model={"regimes_validated": ["stable"]},
        training_regime="stable",
        deployment_regime="supply_constrained",
        claim=pitch)

    # C033-C041 — substrate primacy. Fails case is the autonomous-no-driver
    # hypothesis at dispersed wellsites: every substrate-primacy layer
    # collapses because there's no in-cab human, no consolidated route,
    # no apprenticeship pipeline.
    c033 = substrate_primacy_audit.c033_verdict()
    c034 = substrate_primacy_audit.c034_verdict()
    c035 = substrate_primacy_audit.c035_verdict()
    c036 = substrate_primacy_audit.c036_verdict(training_span_days=365.0)
    c037 = substrate_primacy_audit.c037_verdict(
        in_season_accuracy=0.92,
        held_out_season_accuracy=0.68)        # bad winter transfer
    c038 = substrate_primacy_audit.c038_verdict()
    c039 = substrate_primacy_audit.c039_verdict(workforce_size=12,
                                                  fleet_size=12)
    c040 = substrate_primacy_audit.c040_verdict()    # use module defaults
    c041 = substrate_primacy_audit.c041_verdict()

    # C042 — adversarial overhead. Dispersed-wellsite vendors operate
    # under sustained adversarial pressure (small operators vs major
    # carriers, regulatory volatility, predatory acquisition climate).
    c042 = adversarial_overhead_audit.c042_verdict("threat_mixed",
                                                    overhead_per_day=0.015)

    # C043-C048 — governance thermodynamics. Fails case uses defaults
    # (no operator-side reciprocity carve-out).
    c043 = governance_thermodynamics_audit.c043_verdict(
        population=330_000_000)
    c044 = governance_thermodynamics_audit.c044_verdict()
    c045 = governance_thermodynamics_audit.c045_verdict()
    c046 = governance_thermodynamics_audit.c046_verdict()
    c047 = governance_thermodynamics_audit.c047_verdict()
    c048 = governance_thermodynamics_audit.c048_verdict()

    return {
        "scenario": "dispersed_wellsite (fails case)",
        "C000": c000,
        "C001": c001, "C002": c002, "C003": c003, "C004": c004,
        "C005": c005, "C006": c006, "C007": c007, "C008": c008,
        "C009": c009, "C010": c010, "C011": c011, "C012": c012,
        "C013": c013, "C014": c014, "C015": c015, "C016": c016,
        "C017": c017, "C018": c018, "C019": c019, "C020": c020,
        "C021": c021, "C022": c022, "C023": c023, "C024": c024,
        "C025": c025, "C026": c026, "C027": c027, "C028": c028,
        "C029": c029, "C030": c030, "C031": c031, "C032": c032,
        "C033": c033, "C034": c034, "C035": c035, "C036": c036,
        "C037": c037, "C038": c038, "C039": c039, "C040": c040,
        "C041": c041, "C042": c042, "C043": c043, "C044": c044,
        "C045": c045, "C046": c046, "C047": c047, "C048": c048,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
