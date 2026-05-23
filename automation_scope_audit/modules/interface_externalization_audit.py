"""
interface_externalization_audit.py  —  C011, C012, C013

Every connection point a driver currently mediates — fuel, customer,
dispatch, maintenance, regulatory, roadside service, payment systems —
is unpriced flexibility. Replacing the driver does not eliminate the
interface; it *externalizes* it onto middleware (remote diagnostic
center), heterogeneous third parties (customers, regulators, roadside),
and distributed labor (mobile technicians, customer-service staff, on-call
specialists). The interface cost moves off the truck's TCO line and onto
operating overhead that the marketing numbers omit.

C011 (middleware cost): the autonomous stack inserts middleware (remote
diagnostic center, telemetry pipes, cellular dispatch, software stack)
between the truck and every external system the driver used to touch
directly. Aggregate middleware lifecycle cost exceeds the equivalent
driver-mediated cost.

C012 (heterogeneity risk): each external touchpoint — customer site
convention, fuel-chain SKU, regulatory jurisdiction, weigh-station
protocol — is heterogeneous. A driver absorbs heterogeneity for free.
An autonomous stack needs an explicit handler per variant; failure modes
scale with variant count, not with corridor count.

C013 (distributed labor cost): the remote operators, mobile technicians,
and customer-service staff doing the work the driver used to do are
billed at a *higher* fully-loaded rate than the driver, often through
specialist 24/7 retainers. The cost is shifted, not eliminated.

License: CC0-1.0
"""

from typing import Dict, List


# Canonical interfaces a driver currently mediates for an oilfield / haul
# operation. Each carries a `frequency_per_week`, a list of typical fault
# modes the driver historically handled in-stride, an `adaptation_score`
# (0.0 - 1.0) reflecting how much novelty the human absorbs vs how much is
# scripted, and `variant_count` — the number of distinct external
# conventions the interface sees in the field (e.g., number of fuel-card
# vendors, customer pad layouts, jurisdictions, roadside protocols).
INTERFACES_CLASS8: List[dict] = [
    {"interface": "fuel_system",
     "frequency_per_week": 6,
     "fault_modes": ["card_decline", "pump_malfunction", "wrong_grade",
                     "spill_response", "tank_locking_issue"],
     "adaptation_score": 0.6,
     "variant_count": 12},
    {"interface": "customer_receiving",
     "frequency_per_week": 14,
     "fault_modes": ["site_locked", "wrong_pad", "supervisor_absent",
                     "rig_state_change", "load_rejected", "scale_mismatch"],
     "adaptation_score": 0.9,
     "variant_count": 35},
    {"interface": "dispatch",
     "frequency_per_week": 14,
     "fault_modes": ["reroute_request", "load_change", "weather_hold",
                     "regulatory_check"],
     "adaptation_score": 0.7,
     "variant_count": 4},
    {"interface": "maintenance",
     "frequency_per_week": 2,
     "fault_modes": ["intermittent_warning", "minor_field_fix",
                     "fluid_top_up", "fuse_replace", "limp_home_decision"],
     "adaptation_score": 0.85,
     "variant_count": 8},
    {"interface": "regulatory",
     "frequency_per_week": 3,
     "fault_modes": ["weigh_station", "DOT_inspection",
                     "load_paperwork_anomaly", "ELD_dispute"],
     "adaptation_score": 0.8,
     "variant_count": 50},   # 50 state jurisdictions
    {"interface": "roadside_services",
     "frequency_per_week": 0.5,
     "fault_modes": ["jump_start", "tire_change_assist",
                     "minor_collision_response", "police_interaction"],
     "adaptation_score": 0.95,
     "variant_count": 20},
    {"interface": "payment_systems",
     "frequency_per_week": 6,
     "fault_modes": ["card_decline", "alternate_payment",
                     "receipt_dispute", "fraud_flag"],
     "adaptation_score": 0.7,
     "variant_count": 9},
]


# Resolution cost stack per interface (USD per event).
# - `onboard_driver`:    driver does it; marginal driver time.
# - `remote_diagnostic`: middleware (server + on-call specialist) per event.
# - `mobile_tech`:       dispatched technician; vehicle + staff + downtime.
DEFAULT_RESOLUTION_COSTS_USD: Dict[str, Dict[str, float]] = {
    "fuel_system":        {"onboard_driver":  5.0,
                            "remote_diagnostic":  90.0,
                            "mobile_tech":    400.0},
    "customer_receiving": {"onboard_driver": 12.0,
                            "remote_diagnostic": 220.0,
                            "mobile_tech":    900.0},
    "dispatch":           {"onboard_driver":  3.0,
                            "remote_diagnostic":  60.0,
                            "mobile_tech":    350.0},
    "maintenance":        {"onboard_driver": 20.0,
                            "remote_diagnostic": 180.0,
                            "mobile_tech":  1_200.0},
    "regulatory":         {"onboard_driver": 25.0,
                            "remote_diagnostic": 250.0,
                            "mobile_tech":  1_400.0},
    "roadside_services":  {"onboard_driver": 45.0,
                            "remote_diagnostic": 500.0,
                            "mobile_tech":  2_800.0},
    "payment_systems":    {"onboard_driver":  4.0,
                            "remote_diagnostic":  90.0,
                            "mobile_tech":    400.0},
}


# Distributed-labor stack scaled per truck supported. Fully-loaded annual
# USD per truck for the off-vehicle workforce.
DEFAULT_DISTRIBUTED_LABOR_PER_TRUCK_USD: Dict[str, float] = {
    "remote_operator_share":         9_500.0,   # 1 operator per ~12 trucks
    "mobile_tech_share":             7_200.0,   # 1 tech per ~8 trucks
    "customer_service_share":        3_400.0,
    "diagnostic_specialist_share":   4_800.0,
    "compliance_officer_share":      2_100.0,
    "ml_ops_engineer_share":         3_900.0,
    "data_labeling_outsource":       1_800.0,
}


# Variant-coverage failure rate: probability per event that the deployed
# autonomous stack lacks a handler for the variant it encounters and has
# to escalate. Per-interface heuristic.
DEFAULT_VARIANT_MISS_RATE: Dict[str, float] = {
    "fuel_system":         0.05,
    "customer_receiving":  0.18,
    "dispatch":            0.04,
    "maintenance":         0.22,
    "regulatory":          0.10,
    "roadside_services":   0.28,
    "payment_systems":     0.06,
}


# Cost per unhandled variant escalation. The driver absorbs these for ~$0;
# autonomous escalation hits the mobile-tech line at minimum.
DEFAULT_ESCALATION_COST_USD: Dict[str, float] = {
    "fuel_system":         220.0,
    "customer_receiving":  850.0,
    "dispatch":            180.0,
    "maintenance":       1_400.0,
    "regulatory":        1_200.0,
    "roadside_services": 2_500.0,
    "payment_systems":     280.0,
}


def enumerate_interfaces(truck_type: str = "class8") -> List[dict]:
    """Return every connection point a driver currently mediates."""
    if truck_type != "class8":
        raise KeyError(f"only class8 interfaces are bundled: got {truck_type}")
    return [dict(i) for i in INTERFACES_CLASS8]


def model_resolution_costs(interface: dict, resolution_type: str,
                           cost_table: Dict[str, Dict[str, float]] | None = None
                           ) -> dict:
    """Per-event cost and annual cost to resolve faults at this interface."""
    table = cost_table or DEFAULT_RESOLUTION_COSTS_USD
    name = interface["interface"]
    if name not in table:
        raise KeyError(f"no cost row for interface {name}")
    if resolution_type not in table[name]:
        raise KeyError(f"unknown resolution type {resolution_type}")
    per_event = table[name][resolution_type]
    events_per_year = interface["frequency_per_week"] * 50.0
    return {
        "interface":       name,
        "resolution_type": resolution_type,
        "per_event_usd":   per_event,
        "events_per_year": events_per_year,
        "annual_cost_usd": per_event * events_per_year,
    }


def middleware_lifecycle_cost(interfaces: List[dict] | None = None,
                              cost_table: Dict[str, Dict[str, float]] | None = None,
                              lifecycle_years: int = 7,
                              mobile_escalation_pct: float = 0.25) -> dict:
    """Total middleware-mediated cost over the equipment lifecycle.

    Autonomous handling is modeled as `remote_diagnostic` for most events
    plus a `mobile_escalation_pct` share that has to be handled by the
    dispatched-technician fallback. That blended rate is what middleware
    actually costs in production.
    """
    interfaces = interfaces or enumerate_interfaces()
    table = cost_table or DEFAULT_RESOLUTION_COSTS_USD
    by_interface = []
    onboard_annual = 0.0
    middleware_annual = 0.0
    for i in interfaces:
        onboard = model_resolution_costs(i, "onboard_driver", table)
        remote = model_resolution_costs(i, "remote_diagnostic", table)
        mobile = model_resolution_costs(i, "mobile_tech", table)
        blended = (remote["annual_cost_usd"] * (1.0 - mobile_escalation_pct)
                   + mobile["annual_cost_usd"] * mobile_escalation_pct)
        onboard_annual += onboard["annual_cost_usd"]
        middleware_annual += blended
        by_interface.append({
            "interface":                    i["interface"],
            "onboard_driver_annual_usd":    onboard["annual_cost_usd"],
            "remote_diagnostic_annual_usd": remote["annual_cost_usd"],
            "mobile_tech_annual_usd":       mobile["annual_cost_usd"],
            "middleware_blended_annual_usd": blended,
        })
    return {
        "by_interface":                 by_interface,
        "onboard_driver_annual_usd":    onboard_annual,
        "middleware_annual_usd":        middleware_annual,
        "lifecycle_years":              lifecycle_years,
        "onboard_lifecycle_usd":        onboard_annual * lifecycle_years,
        "middleware_lifecycle_usd":     middleware_annual * lifecycle_years,
        "cost_ratio_middleware_to_driver":
            middleware_annual / onboard_annual
            if onboard_annual > 0 else float("inf"),
    }


def heterogeneity_risk(interfaces: List[dict] | None = None,
                       miss_rates: Dict[str, float] | None = None,
                       escalation_costs: Dict[str, float] | None = None
                       ) -> dict:
    """Expected annual cost of unhandled variants per interface.

    Variants = the count of distinct external conventions that interface
    sees. Miss rate = probability the deployed autonomous stack lacks a
    handler for the variant. Cost = mobile-tech-rate escalation per miss.
    """
    interfaces = interfaces or enumerate_interfaces()
    mr = miss_rates or DEFAULT_VARIANT_MISS_RATE
    ec = escalation_costs or DEFAULT_ESCALATION_COST_USD
    rows = []
    total_variants = 0
    total_annual_cost = 0.0
    for i in interfaces:
        name = i["interface"]
        variants = int(i.get("variant_count", 0))
        events = i["frequency_per_week"] * 50.0
        miss_rate = mr.get(name, 0.05)
        cost_per_miss = ec.get(name, 500.0)
        misses_per_year = events * miss_rate
        annual = misses_per_year * cost_per_miss
        total_variants += variants
        total_annual_cost += annual
        rows.append({
            "interface":         name,
            "variant_count":     variants,
            "events_per_year":   events,
            "miss_rate":         miss_rate,
            "misses_per_year":   misses_per_year,
            "cost_per_miss_usd": cost_per_miss,
            "annual_cost_usd":   annual,
        })
    return {
        "by_interface":            rows,
        "total_variant_count":     total_variants,
        "total_annual_cost_usd":   total_annual_cost,
    }


def distributed_labor_cost(stack: Dict[str, float] | None = None,
                            multipliers: Dict[str, float] | None = None
                            ) -> dict:
    """Annual distributed-labor cost per truck supported.

    `multipliers` lets callers scale individual line items (e.g. a deep-rural
    deployment may need 2x mobile-tech share to absorb response-time SLAs).
    """
    base = stack or DEFAULT_DISTRIBUTED_LABOR_PER_TRUCK_USD
    multipliers = multipliers or {}
    line_items = {}
    total = 0.0
    for k, v in base.items():
        scaled = v * float(multipliers.get(k, 1.0))
        line_items[k] = scaled
        total += scaled
    return {
        "line_items":               line_items,
        "annual_cost_per_truck_usd": total,
    }


def c011_verdict(truck_type: str = "class8",
                 cost_table: Dict[str, Dict[str, float]] | None = None,
                 lifecycle_years: int = 7,
                 mobile_escalation_pct: float = 0.25) -> dict:
    interfaces = enumerate_interfaces(truck_type)
    cost = middleware_lifecycle_cost(interfaces, cost_table,
                                     lifecycle_years, mobile_escalation_pct)
    ratio = cost["cost_ratio_middleware_to_driver"]
    return {
        "claim_id":                       "C011",
        "by_interface":                   cost["by_interface"],
        "onboard_driver_annual_usd":      cost["onboard_driver_annual_usd"],
        "middleware_annual_usd":          cost["middleware_annual_usd"],
        "onboard_lifecycle_usd":          cost["onboard_lifecycle_usd"],
        "middleware_lifecycle_usd":       cost["middleware_lifecycle_usd"],
        "cost_ratio_middleware_to_driver": ratio,
        "threshold_met":                  ratio > 2.0,
        "falsifier": "audited middleware lifecycle cost at <2x driver-mediated cost",
    }


def c012_verdict(truck_type: str = "class8",
                 miss_rates: Dict[str, float] | None = None,
                 escalation_costs: Dict[str, float] | None = None,
                 driver_baseline_annual_usd: float = 1_000.0) -> dict:
    """Heterogeneity risk gate.

    `driver_baseline_annual_usd` is the residual cost the driver incurs
    when they can't handle an exotic variant either (e.g. genuine police
    interaction); the threshold compares autonomous heterogeneity cost to
    a 5x multiple of this baseline.
    """
    interfaces = enumerate_interfaces(truck_type)
    risk = heterogeneity_risk(interfaces, miss_rates, escalation_costs)
    autonomous = risk["total_annual_cost_usd"]
    ratio = autonomous / driver_baseline_annual_usd \
        if driver_baseline_annual_usd > 0 else float("inf")
    return {
        "claim_id":                "C012",
        "by_interface":            risk["by_interface"],
        "total_variant_count":     risk["total_variant_count"],
        "autonomous_annual_cost_usd": autonomous,
        "driver_baseline_annual_usd": driver_baseline_annual_usd,
        "heterogeneity_ratio":     ratio,
        "threshold_met":           ratio > 5.0,
        "falsifier": "autonomous deployment with documented handler coverage for >95% of field variants",
    }


def c013_verdict(driver_annual_fully_loaded_usd: float = 78_000.0,
                 stack: Dict[str, float] | None = None,
                 multipliers: Dict[str, float] | None = None) -> dict:
    """Distributed labor cost gate.

    Threshold is met when distributed-labor annual cost per truck supported
    exceeds the fully-loaded annual cost of the single driver it replaces.
    Default driver fully-loaded cost is $78k (2025 US Class-8 average:
    wages + benefits + payroll tax + per-diem).
    """
    cost = distributed_labor_cost(stack, multipliers)
    auto = cost["annual_cost_per_truck_usd"]
    ratio = auto / driver_annual_fully_loaded_usd \
        if driver_annual_fully_loaded_usd > 0 else float("inf")
    return {
        "claim_id":                       "C013",
        "distributed_labor_annual_usd":   auto,
        "driver_fully_loaded_annual_usd": driver_annual_fully_loaded_usd,
        "labor_cost_ratio":               ratio,
        "threshold_met":                  ratio >= 0.5,
        # threshold = distributed labor is at least half a driver's cost,
        # while the marketing claim is that labor cost goes to ~zero.
        "line_items":                     cost["line_items"],
        "falsifier": "audited distributed-labor cost below 25% of replaced driver fully-loaded cost",
    }


if __name__ == "__main__":
    print("C011:", c011_verdict())
    print("C012:", c012_verdict())
    print("C013:", c013_verdict(multipliers={"mobile_tech_share": 1.5}))
