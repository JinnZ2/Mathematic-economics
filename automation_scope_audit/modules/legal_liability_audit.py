"""
legal_liability_audit.py  —  C017

Autonomous trucking deployments operate inside an *uncodified* legal and
regulatory framework. The framework cost — litigation defense for novel
liability cases, regulatory engagement across 50+ state jurisdictions
plus federal, FMCSA petition activity, lobbying for liability shields,
insurance navigation, and ongoing legal-precedent monitoring — is
real, ongoing, and not present in the conventional-trucking baseline.

C017: Litigation + regulatory framework cost is a structural operating
expense, not a one-time startup cost.

Falsifier: deployed autonomous trucking operation showing legal and
regulatory framework cost at less than 50% premium over a comparable
conventional trucking operation, sustained over 3 consecutive years.

License: CC0-1.0
"""

from typing import Dict, List


# Default 2025 USD annual cost stack per fleet, for an autonomous deployment.
# Each line item carries the conventional-baseline cost too, so the *premium*
# can be surfaced separately from the absolute cost.
DEFAULT_FRAMEWORK_COSTS: List[dict] = [
    {"line_item": "in_house_legal_counsel",
     "autonomous_annual_usd": 1_200_000.0,
     "conventional_annual_usd": 350_000.0},
    {"line_item": "outside_litigation_defense_reserve",
     "autonomous_annual_usd": 3_500_000.0,
     "conventional_annual_usd":   600_000.0},
    {"line_item": "regulatory_affairs_staff",
     "autonomous_annual_usd":   900_000.0,
     "conventional_annual_usd":  150_000.0},
    {"line_item": "state_by_state_compliance_consulting",
     "autonomous_annual_usd":   650_000.0,
     "conventional_annual_usd":   90_000.0},
    {"line_item": "federal_FMCSA_petition_engagement",
     "autonomous_annual_usd":   450_000.0,
     "conventional_annual_usd":   40_000.0},
    {"line_item": "lobbying_industry_associations",
     "autonomous_annual_usd":   800_000.0,
     "conventional_annual_usd":  120_000.0},
    {"line_item": "insurance_navigation_brokers",
     "autonomous_annual_usd":   550_000.0,
     "conventional_annual_usd":  140_000.0},
    {"line_item": "legal_precedent_monitoring",
     "autonomous_annual_usd":   220_000.0,
     "conventional_annual_usd":   30_000.0},
    {"line_item": "incident_investigation_specialists",
     "autonomous_annual_usd":   480_000.0,
     "conventional_annual_usd":   80_000.0},
    {"line_item": "data_subpoena_response",
     "autonomous_annual_usd":   310_000.0,
     "conventional_annual_usd":   25_000.0},
]


# Pending or anticipated litigation categories specific to autonomous
# trucking, with rough probability per fleet-year and expected defense cost.
LITIGATION_CATEGORIES: List[dict] = [
    {"category": "wrongful_death_novel_failure_mode",
     "annual_probability": 0.35, "expected_defense_usd": 4_500_000.0},
    {"category": "cargo_loss_unrecoverable_chain",
     "annual_probability": 0.50, "expected_defense_usd":   850_000.0},
    {"category": "regulatory_enforcement_action",
     "annual_probability": 0.40, "expected_defense_usd": 1_100_000.0},
    {"category": "OEM_indemnification_dispute",
     "annual_probability": 0.30, "expected_defense_usd": 2_200_000.0},
    {"category": "labor_law_remote_operator_class_action",
     "annual_probability": 0.15, "expected_defense_usd": 3_000_000.0},
    {"category": "data_breach_telemetry",
     "annual_probability": 0.20, "expected_defense_usd": 1_400_000.0},
]


def enumerate_framework_costs() -> List[dict]:
    return [dict(c) for c in DEFAULT_FRAMEWORK_COSTS]


def framework_premium(items: List[dict] | None = None) -> dict:
    """Compute annual autonomous premium over conventional baseline."""
    items = items or enumerate_framework_costs()
    auto_total = sum(i["autonomous_annual_usd"] for i in items)
    conv_total = sum(i["conventional_annual_usd"] for i in items)
    premium = auto_total - conv_total
    ratio = (auto_total / conv_total) if conv_total > 0 else float("inf")
    return {
        "items":             items,
        "autonomous_total":  auto_total,
        "conventional_total": conv_total,
        "annual_premium":    premium,
        "premium_ratio":     ratio,
    }


def expected_litigation_load(categories: List[dict] | None = None) -> dict:
    """Expected annual litigation expense across novel categories."""
    cats = categories or LITIGATION_CATEGORIES
    rows = []
    annual_expected = 0.0
    for c in cats:
        ev = c["annual_probability"] * c["expected_defense_usd"]
        annual_expected += ev
        rows.append({
            "category":            c["category"],
            "annual_probability":  c["annual_probability"],
            "expected_defense_usd": c["expected_defense_usd"],
            "annual_expected_usd": ev,
        })
    return {
        "by_category":          rows,
        "annual_expected_usd":  annual_expected,
    }


def c017_verdict(framework_items: List[dict] | None = None,
                 litigation_categories: List[dict] | None = None,
                 fleet_size: int = 50) -> dict:
    fw = framework_premium(framework_items)
    lit = expected_litigation_load(litigation_categories)
    total_autonomous = fw["autonomous_total"] + lit["annual_expected_usd"]
    total_conventional = fw["conventional_total"]
    total_premium = total_autonomous - total_conventional
    per_truck_premium = total_premium / fleet_size if fleet_size > 0 else 0.0
    premium_ratio = (total_autonomous / total_conventional
                     if total_conventional > 0 else float("inf"))
    return {
        "claim_id":                       "C017",
        "framework_premium":              fw,
        "litigation_load":                lit,
        "autonomous_annual_total_usd":    total_autonomous,
        "conventional_annual_total_usd":  total_conventional,
        "annual_premium_usd":             total_premium,
        "premium_ratio":                  premium_ratio,
        "fleet_size":                     fleet_size,
        "annual_premium_per_truck_usd":   per_truck_premium,
        "threshold_met":                  premium_ratio > 1.5,
        "falsifier": "deployed autonomous trucking operation showing legal and regulatory framework cost at <1.5x conventional, sustained over 3 consecutive years",
    }


if __name__ == "__main__":
    print("C017 (50-truck fleet):", c017_verdict(fleet_size=50))
    print("C017 (500-truck fleet):", c017_verdict(fleet_size=500))
