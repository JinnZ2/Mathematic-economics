# iam_audit/scenarios/dice_rcp85.py
"""
DICE‑2023R baseline assumptions for RCP8.5 forcing, packaged for audit.
"""

ASSUMPTIONS = {
    "scope": {
        "time_horizon": 2300,
        "geographic": "global",
        "sectors": ["energy", "agriculture", "industry"],
        "excluded": ["institutions", "governance", "substrate_care", "cascade"]
    },
    "energy": {
        "abatement_cost_curve": "smooth quadratic",
        "co2_capture": "backstop technology available",
        "energy_cost_of_mitigation": "not counted (financial cost only)",
        "full_energy_stack_included": False
    },
    "engineering": {
        "design_margin": 0.0,
        "enumerated_failure_modes": [],
        "falsifiability_test": "none (calibrated to past data)",
        "ai_training_data": "stable period 1960-2015"
    },
    "systemic_preconditions": {
        "climate_stable": True,
        "supply_chain_uninterrupted": True,
        "geopolitical_stability": True,
        "grid_reliability": True,
        "satellite_coverage": True,
        "regulatory_continuity": True,
        "currency_stability": True
    },
    "scaling": {
        "returns_to_scale": "constant",
        "institutional_costs": "ignored"
    },
    "governance": {
        "enforcement_model": "none (single agent)",
        "care_work_visible": False,
        "knowledge_authority_inversion": "irrelevant"
    }
}
