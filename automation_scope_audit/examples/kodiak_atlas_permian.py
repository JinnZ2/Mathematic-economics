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

DEPLOYMENT_SPEC = {
    "beneficiary":        "fleet_operator_share_60pct_and_atlas_pad_operator_40pct",
    "conditions":         [
        "stable_diesel_supply",
        "no_FMCSA_rule_shift_in_corridor",
        "weather_within_30yr_envelope",
    ],
    "time_period":        "7yr_equipment_lifecycle_amortization",
    "resource":           "diesel_energy_joules_with_off_vehicle_kwh_overhead",
    "externalized_cost":  "rural_road_maintenance_to_state_DOT_and_carbon_burden",
    "profit_allocation":  ["operator_60pct", "atlas_energy_40pct"],
    "falsifier":          "fuel_intensity_per_ton_mile_increase_post_deployment",
    # Substrate-primacy fraction: in the consolidated Permian corridor
    # with a safety driver in cab and physical interlocks at the pad,
    # ~25% of operations can proceed without electricity / internet /
    # computers (manual driving + paper bills of lading + visual
    # weighing). Not great, but non-zero.
    "substrate_primacy_fraction": 0.25,
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
    regulatory_dynamics_audit,
    roi_baseline_integrity_audit,
    system_integration_audit,
    substrate_care_audit,
    credential_inversion_audit,
    adoption_curve_audit,
    lifecycle_design_audit,
    framework_reflexivity_audit,
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

    # C033-C041 — substrate primacy. Works case has a safety driver in
    # cab and a relatively stable corridor; defaults are appropriate.
    c033 = substrate_primacy_audit.c033_verdict()
    c034 = substrate_primacy_audit.c034_verdict()
    c035 = substrate_primacy_audit.c035_verdict()
    c036 = substrate_primacy_audit.c036_verdict(training_span_days=730.0)
    c037 = substrate_primacy_audit.c037_verdict()
    c038 = substrate_primacy_audit.c038_verdict()
    c039 = substrate_primacy_audit.c039_verdict(workforce_size=60,
                                                  fleet_size=60)
    # Works case retains some manual-fallback capacity due to in-cab
    # safety driver; nominal GPS/cloud failures still leave physical
    # driving + paper-trail backup operational.
    c040 = substrate_primacy_audit.c040_verdict(
        operational_capacity_by_failure={
            "gps_down": 0.50, "cloud_down": 0.35,
            "electricity_down": 0.10, "fuel_unavailable": 0.0,
        })
    c041 = substrate_primacy_audit.c041_verdict()

    # C042 — adversarial overhead. The Permian deployment is largely
    # cooperative (Atlas + Kodiak + carrier alignment) but operates in
    # the broader mixed-model regulatory / market environment.
    c042 = adversarial_overhead_audit.c042_verdict("threat_mixed",
                                                    overhead_per_day=0.006)

    # C043-C048 — governance thermodynamics. The audited deployment
    # operates inside the US regulatory / institutional environment.
    # Population basis for C043 is the relevant federal jurisdiction.
    c043 = governance_thermodynamics_audit.c043_verdict(
        population=330_000_000)
    c044 = governance_thermodynamics_audit.c044_verdict()
    # Works-case has slightly better legitimacy parameters than default
    # (Atlas dedicated lane has explicit operator + carrier reciprocity
    # within the corridor, even though the broader culture is extractive).
    c045 = governance_thermodynamics_audit.c045_verdict(
        equal_enforcement=0.50,    cultural_reciprocity=0.45,
        wealth_immunity=0.70,      extraction_incentives=0.75)
    c046 = governance_thermodynamics_audit.c046_verdict()
    c047 = governance_thermodynamics_audit.c047_verdict()
    c048 = governance_thermodynamics_audit.c048_verdict()

    # C049-C053 — regulatory dynamics. Systemic claims about the US
    # regulatory environment; register in both scenarios.
    c049 = regulatory_dynamics_audit.c049_verdict()
    c050 = regulatory_dynamics_audit.c050_verdict(
        max_capability_hours=11.0, min_capability_hours=11.0,
        n_operators=60, operator_autonomy=0.35)
    c051 = regulatory_dynamics_audit.c051_verdict()
    c052 = regulatory_dynamics_audit.c052_verdict()
    c053 = regulatory_dynamics_audit.c053_verdict(
        year_since_deployment=4,
        regulation_intensity=0.45,
        high_capability_share_remaining=0.30)

    # C054-C058 — ROI baseline integrity. Works case has a slightly more
    # favorable POR than fails case (consolidated corridor, fewer
    # exceptions), but the structural concerns still register.
    c054 = roi_baseline_integrity_audit.c054_verdict()
    c055 = roi_baseline_integrity_audit.c055_verdict()
    c056 = roi_baseline_integrity_audit.c056_verdict(
        autonomous_overhead={
            "pretrip_diagnostics_h":      0.50,
            "posttrip_diagnostics_h":     0.50,
            "charging_or_fueling_h":      2.00,
            "maintenance_h":              0.75,
            "interface_integration_h":    0.50,
            "cloud_diagnostic_latency_h": 0.25,
            "exception_resolution_h":     1.00,
        })
    c057 = roi_baseline_integrity_audit.c057_verdict()
    c058 = roi_baseline_integrity_audit.c058_verdict(
        fleet_size=60, lifecycle_years=5)

    # C059 — integrated thermodynamic synthesis. Works case has modest
    # degraded-mode capacity (safety driver in cab) and one extra
    # integrated function (adaptation handled by the human, not the AI).
    c059 = system_integration_audit.c059_verdict(
        autonomous_function_status={
            "transport": "integrated",
            "adaptation_to_novel_conditions": "integrated",
        },
        autonomous_degraded_mode_capacity=0.30)

    # C060-C064 — substrate care. Works case has slightly more
    # substrate experience in the management coalition (Kodiak founders
    # are engineers) but still fails the precondition gate because the
    # broader institutional context defunds care work.
    c060 = substrate_care_audit.c060_verdict(
        role_mix={
            "MBA_trained_executive":   0.25,
            "consultant_external":     0.05,
            "domain_engineer":         0.30,
            "operations_engineer":     0.15,
            "site_supervisor":         0.10,
            "factory_floor_operator":  0.10,
            "experienced_driver":      0.05,
        },
        elite_overproduction_share=0.35)
    c061 = substrate_care_audit.c061_verdict()
    c062 = substrate_care_audit.c062_verdict()
    c063 = substrate_care_audit.c063_verdict()
    # Works case: safety driver in cab maintains some care work; failure
    # cost is partially modeled; substrate-experienced engineer signed
    # off on the deployment. But care work isn't separately costed.
    c064 = substrate_care_audit.c064_verdict(
        care_work_continued=True,
        care_work_costed_visibly=False,
        failure_cost_known=True,
        decision_authority_holder_has_substrate_knowledge=True,
        approval_required_from_substrate_experienced_operator=False)

    # C065-C069 — credential inversion. Works case has somewhat better
    # credential / substrate-knowledge alignment (Kodiak founders are
    # engineers with operational experience) but still operates in a
    # broader credential-biased AI training corpus.
    c065 = credential_inversion_audit.c065_verdict(
        decision_maker_credentials=[
            "domain_PhD", "operational_experience_20yr", "MBA",
            "AI_researcher_PhD", "venture_capitalist",
        ])
    c066 = credential_inversion_audit.c066_verdict()
    c067 = credential_inversion_audit.c067_verdict()
    c068 = credential_inversion_audit.c068_verdict()
    c069 = credential_inversion_audit.c069_verdict(
        attributed_blame=[
            "AI_not_ready_training_data",
            "decision_maker_lacked_substrate_knowledge",
            "edge_case_complexity",
        ])

    # C070-C072 — adoption-curve. Autonomous trucking deployment cohort
    # is in phase 2-3 of the canonical curve. Works case has slightly
    # better substrate metrics due to consolidated corridor + safety
    # driver, but the systemic divergence still registers.
    c070 = adoption_curve_audit.c070_verdict(
        substrate_trend={
            "energy_cost_per_unit_trend":    -0.12,
            "failure_rate_trend":            -0.08,
            "resilience_to_disruption":      -0.05,
            "human_skill_retention":         -0.08,
            "biodiversity_substrate_health": -0.06,
            "knowledge_preservation":        -0.05,
            "edge_case_robustness":          -0.06,
        })
    c071 = adoption_curve_audit.c071_verdict()
    c072 = adoption_curve_audit.c072_verdict(
        decision_maker_class="fortune_500_ceo",
        cycle_timescale_years=20.0)

    # C073 / C074 — lifecycle design. Works case uses module defaults
    # (conventional financial model; designer not accountable for EoL).
    c073 = lifecycle_design_audit.c073_verdict(fleet_size=60)
    c074 = lifecycle_design_audit.c074_verdict()

    # C075 — framework reflexivity. Static state at audit time.
    c075 = framework_reflexivity_audit.c075_verdict()

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
        "C033": c033, "C034": c034, "C035": c035, "C036": c036,
        "C037": c037, "C038": c038, "C039": c039, "C040": c040,
        "C041": c041, "C042": c042, "C043": c043, "C044": c044,
        "C045": c045, "C046": c046, "C047": c047, "C048": c048,
        "C049": c049, "C050": c050, "C051": c051, "C052": c052,
        "C053": c053, "C054": c054, "C055": c055, "C056": c056,
        "C057": c057, "C058": c058, "C059": c059,
        "C060": c060, "C061": c061, "C062": c062, "C063": c063,
        "C064": c064, "C065": c065, "C066": c066, "C067": c067,
        "C068": c068, "C069": c069, "C070": c070, "C071": c071,
        "C072": c072, "C073": c073, "C074": c074, "C075": c075,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
