"""
constraint_validation_audit.py  —  C014, C015, C016

A human driver carries three forms of authority that the marketing
narrative for autonomous trucking does not price:

C014 (refusal authority): the legally and contractually recognized right
to decline an unsafe dispatch, refuse an overweight or improperly
secured load, refuse to enter conditions that violate FMCSA hours-of-
service, or refuse to operate equipment with safety defects. CDL drivers
exercise this hundreds of times per year per fleet, silently, and the
operation absorbs the cost.

C015 (liability void): when something goes wrong with an autonomous
truck, the liability chain is unsettled — OEM, software vendor,
sensor vendor, HD-map provider, fleet operator, remote operator,
insurer. The result is a "liability void" where injured parties may
face indeterminate or unreachable defendants, and the fleet operator
faces uninsurable residual risk.

C016 (override hierarchy): drivers exercise on-the-spot override
authority for the dozens of decision points that emerge in field
operations — refusing a customer site that is unsafe, ignoring a
dispatch reroute that adds dangerous miles, taking emergency action
that contradicts standard protocol. Autonomous stacks resolve override
conflicts through a fixed hierarchy that has to be designed in
advance; novel conflicts default to escalation or to brittle defaults.

Falsifiers:
  C014: documented autonomous deployment with legally recognized
        refusal authority at parity with a CDL driver.
  C015: settled liability chain with insurance markets pricing
        autonomous-specific coverage at less than 2x conventional rates.
  C016: documented autonomous override-resolution coverage of
        >90% of historical driver override events.

License: CC0-1.0
"""

from typing import Dict, List


# Typical driver refusal events per truck per year, by category.
# Each entry: refusal type, annual rate, value if successful (cost averted).
REFUSAL_EVENTS_CLASS8: List[dict] = [
    {"refusal_type": "unsafe_load_securement",       "annual_rate":  8.0,
     "value_per_event_usd": 2_500.0,
     "legal_basis": "FMCSA 392.9"},
    {"refusal_type": "fatigue_hours_of_service",     "annual_rate": 15.0,
     "value_per_event_usd": 4_200.0,
     "legal_basis": "FMCSA 395"},
    {"refusal_type": "vehicle_safety_defect",        "annual_rate":  6.0,
     "value_per_event_usd": 3_800.0,
     "legal_basis": "FMCSA 396.7"},
    {"refusal_type": "weather_unsafe_operation",     "annual_rate": 11.0,
     "value_per_event_usd": 5_500.0,
     "legal_basis": "FMCSA 392.14"},
    {"refusal_type": "overweight_or_improper_load",  "annual_rate":  4.0,
     "value_per_event_usd": 1_900.0,
     "legal_basis": "state weight + bridge formula"},
    {"refusal_type": "customer_site_unsafe",         "annual_rate":  3.0,
     "value_per_event_usd": 3_100.0,
     "legal_basis": "OSHA general duty + carrier policy"},
    {"refusal_type": "dispatch_unsafe_routing",      "annual_rate":  5.0,
     "value_per_event_usd": 2_700.0,
     "legal_basis": "FMCSA 392 + carrier policy"},
    {"refusal_type": "whistleblower_protected",      "annual_rate":  1.0,
     "value_per_event_usd": 8_000.0,
     "legal_basis": "STAA 49 USC 31105"},
]


# Liability stack participants and the probability that the participant
# successfully disclaims liability in a typical autonomous incident,
# leaving residual void. Numbers reflect 2024-2025 insurance-industry
# discussion of the autonomous trucking liability question; they are
# illustrative defaults, not actuarial estimates.
LIABILITY_PARTICIPANTS: List[dict] = [
    {"participant": "vehicle_oem",
        "coverage_share": 0.20, "disclaim_probability": 0.55},
    {"participant": "autonomy_software_vendor",
        "coverage_share": 0.25, "disclaim_probability": 0.65},
    {"participant": "sensor_vendor",
        "coverage_share": 0.05, "disclaim_probability": 0.80},
    {"participant": "hd_map_provider",
        "coverage_share": 0.05, "disclaim_probability": 0.75},
    {"participant": "fleet_operator",
        "coverage_share": 0.25, "disclaim_probability": 0.40},
    {"participant": "remote_operator_employer",
        "coverage_share": 0.10, "disclaim_probability": 0.50},
    {"participant": "insurer_excess_layer",
        "coverage_share": 0.10, "disclaim_probability": 0.35},
]


# Override-resolution coverage: the fraction of historical driver-exercised
# overrides that current autonomous stacks can resolve without escalation
# to a remote operator. Numbers are illustrative; pass `coverage_pct`
# to override.
DEFAULT_OVERRIDE_CATEGORIES: List[dict] = [
    {"category": "customer_site_safety_refusal",  "annual_rate":  3.0,
     "default_coverage_pct": 0.05},
    {"category": "dispatch_override_emergency",   "annual_rate":  4.0,
     "default_coverage_pct": 0.10},
    {"category": "fueling_payment_dispute",       "annual_rate":  6.0,
     "default_coverage_pct": 0.20},
    {"category": "regulatory_inspection_dispute", "annual_rate":  3.0,
     "default_coverage_pct": 0.05},
    {"category": "weather_proactive_shutdown",    "annual_rate":  7.0,
     "default_coverage_pct": 0.25},
    {"category": "novel_collision_avoidance",     "annual_rate": 14.0,
     "default_coverage_pct": 0.40},
    {"category": "load_settlement_response",      "annual_rate":  9.0,
     "default_coverage_pct": 0.15},
]


def enumerate_refusal_events(vehicle_class: str = "class8") -> List[dict]:
    if vehicle_class != "class8":
        raise KeyError(f"only class8 inventory bundled: got {vehicle_class}")
    return [dict(e) for e in REFUSAL_EVENTS_CLASS8]


def refusal_value(events: List[dict]) -> dict:
    """Total annual value of refusals exercised by a CDL driver.

    This is the cost the operation is *not* incurring because the driver
    refused. An autonomous stack without legally-recognized refusal
    authority either has to absorb this cost or replicate the authority
    via a remote operator (who is then a CDL-equivalent expense).
    """
    by_type = []
    annual_total = 0.0
    annual_event_count = 0.0
    for e in events:
        annual = e["annual_rate"] * e["value_per_event_usd"]
        annual_total += annual
        annual_event_count += e["annual_rate"]
        by_type.append({
            "refusal_type":   e["refusal_type"],
            "annual_rate":    e["annual_rate"],
            "annual_value_usd": annual,
            "legal_basis":    e["legal_basis"],
        })
    return {
        "by_type":            by_type,
        "annual_value_usd":   annual_total,
        "annual_event_count": annual_event_count,
    }


def liability_void_share(participants: List[dict] | None = None) -> dict:
    """Estimate the expected residual unrecovered share in an autonomous incident.

    Each participant has a nominal `coverage_share` (their part of the
    liability stack, summing across participants) and a
    `disclaim_probability` (the chance they successfully disclaim in
    litigation). Expected unrecovered = sum(share * disclaim_probability).
    The threshold for C015 is met when the expected void exceeds 10% —
    at that level, no insurer can write standard primary coverage and
    the fleet operator is structurally self-insured for the long tail.
    """
    p = participants or LIABILITY_PARTICIPANTS
    total_share = sum(float(x.get("coverage_share", 0.0)) for x in p)
    if total_share <= 0:
        return {"participants": p, "void_share": 0.0,
                "share_normalization": 0.0}
    void = 0.0
    for x in p:
        share = float(x.get("coverage_share", 0.0)) / total_share
        void += share * float(x["disclaim_probability"])
    return {
        "participants":        p,
        "void_share":          void,
        "share_normalization": total_share,
    }


def override_hierarchy_coverage(categories: List[dict] | None = None,
                                coverage_pct: Dict[str, float] | None = None
                                ) -> dict:
    """Coverage ratio across historical driver-exercised overrides.

    `coverage_pct` lets callers override per-category coverage. Returns
    weighted coverage = sum(annual_rate * coverage) / sum(annual_rate),
    and the per-category breakdown.
    """
    cats = categories or DEFAULT_OVERRIDE_CATEGORIES
    cov = coverage_pct or {}
    rows = []
    weighted_num = 0.0
    weighted_den = 0.0
    uncovered_events = 0.0
    for c in cats:
        name = c["category"]
        rate = float(c["annual_rate"])
        pct = float(cov.get(name, c["default_coverage_pct"]))
        weighted_num += rate * pct
        weighted_den += rate
        uncovered_events += rate * (1.0 - pct)
        rows.append({
            "category":        name,
            "annual_rate":     rate,
            "coverage_pct":    pct,
            "uncovered_rate":  rate * (1.0 - pct),
        })
    weighted_coverage = (weighted_num / weighted_den) if weighted_den else 0.0
    return {
        "by_category":             rows,
        "weighted_coverage_pct":   weighted_coverage,
        "uncovered_events_per_year": uncovered_events,
    }


def c014_verdict(vehicle_class: str = "class8") -> dict:
    events = enumerate_refusal_events(vehicle_class)
    value = refusal_value(events)
    return {
        "claim_id":               "C014",
        "annual_refusal_events":  value["annual_event_count"],
        "annual_refusal_value_usd": value["annual_value_usd"],
        "by_refusal_type":        value["by_type"],
        # Threshold: refusal authority absent in autonomous stack means
        # this value evaporates. Met whenever annual value > $10k —
        # a trivial bar that signals the issue is structural, not
        # actuarial.
        "threshold_met":          value["annual_value_usd"] > 10_000.0,
        "falsifier": "documented autonomous deployment with legally recognized refusal authority at parity with a CDL driver",
    }


def c015_verdict(participants: List[dict] | None = None) -> dict:
    void = liability_void_share(participants)
    return {
        "claim_id":      "C015",
        "participants":  void["participants"],
        "void_share":    void["void_share"],
        # Threshold met when expected unrecovered share > 10%; at that
        # level no standard insurance market can write primary cover.
        "threshold_met": void["void_share"] > 0.10,
        "falsifier": "settled liability chain with insurance markets pricing autonomous-specific coverage at less than 2x conventional rates",
    }


def c016_verdict(coverage_pct: Dict[str, float] | None = None) -> dict:
    res = override_hierarchy_coverage(coverage_pct=coverage_pct)
    return {
        "claim_id":               "C016",
        "by_category":            res["by_category"],
        "weighted_coverage_pct":  res["weighted_coverage_pct"],
        "uncovered_events_per_year": res["uncovered_events_per_year"],
        "threshold_met":          res["weighted_coverage_pct"] < 0.90,
        "falsifier": "documented autonomous override-resolution coverage of >90% of historical driver override events",
    }


if __name__ == "__main__":
    print("C014:", c014_verdict())
    print("C015:", c015_verdict())
    print("C016:", c016_verdict())
