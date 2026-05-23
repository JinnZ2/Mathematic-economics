"""
substrate_care_audit.py  —  C060-C064

Five structural claims about why automation deployments keep failing on
substrate grounds even when the technical work is competent: elite
overproduction shifts management incentives toward abstraction, care
work becomes structurally invisible, knowledge and authority decouple,
blame externalizes to those executing instead of those designing, and
none of the deployments preserve care + authority as non-negotiable
preconditions.

C060 Elite overproduction shifts management incentive structure toward
     abstract value creation instead of substrate stewardship. Once
     elite share exceeds a threshold, management is recruited from
     abstraction-trained pool (MBA / consulting / finance) and the
     substrate is no longer the decision domain.
C061 Care work (driver pretrip, quality inspection, preventive
     maintenance, teacher attention, nurse observation, farmer soil
     management, manager knowing their team) is *structurally* invisible
     because it prevents problems that never show up in reports. It is
     therefore the first thing cut in any "efficiency" exercise.
C062 Knowledge-authority inversion: people with substrate knowledge
     have no decision authority; people with decision authority have
     no substrate knowledge. Decisions are made far from substrate,
     requiring expensive infrastructure to communicate back to it.
C063 Accountability misdirection: when systems fail on substrate
     grounds, blame falls on engineers ("poor execution"), operators
     ("couldn't adapt"), or AI systems ("hallucination"); not on the
     MBA decision-maker who eliminated care work in the first place.
C064 Substrate care and substrate authority are non-negotiable
     preconditions for any automation deployment. A deployment that
     eliminates care work, OR places authority away from substrate
     knowledge, OR both, is structurally guaranteed to fail on
     substrate grounds.

License: CC0-1.0
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# C060  Elite overproduction shifts management incentive structure
# ---------------------------------------------------------------------------

# Per-management-role: abstraction distance from substrate (0.0 = at
# the substrate; 1.0 = fully abstract, never on the operation floor).
# Default mapping is illustrative; the audit just needs the calling
# context's mix of role types.
DEFAULT_ROLE_ABSTRACTION: Dict[str, float] = {
    "factory_floor_operator":           0.05,
    "domain_expert_engineer":           0.20,
    "operations_engineer":              0.25,
    "site_supervisor":                  0.30,
    "domain_specialist_manager":        0.40,
    "general_manager":                  0.55,
    "MBA_trained_executive":            0.85,
    "consultant_external":              0.90,
    "financial_analyst":                0.95,
    "PE_VC_principal":                  0.98,
}


def measure_abstraction_distance(
    role_mix: Dict[str, float],
    role_abstraction: Dict[str, float] | None = None,
) -> dict:
    """Weighted mean abstraction distance of the management coalition."""
    table = {**DEFAULT_ROLE_ABSTRACTION, **(role_abstraction or {})}
    total_weight = sum(role_mix.values())
    if total_weight <= 0:
        return {"mean_abstraction": 0.0, "by_role": {}}
    weighted = sum(table.get(r, 0.5) * w for r, w in role_mix.items())
    return {
        "mean_abstraction":  weighted / total_weight,
        "by_role":           {r: {"weight": w, "abstraction": table.get(r, 0.5)}
                              for r, w in role_mix.items()},
        "total_weight":      total_weight,
    }


def c060_verdict(
    role_mix: Dict[str, float] | None = None,
    elite_overproduction_share: float = 0.40,
) -> dict:
    """C060: concern registers when mean abstraction > 0.6 OR elite share > 0.3."""
    mix = role_mix or {
        "MBA_trained_executive":   0.40,
        "consultant_external":     0.15,
        "financial_analyst":       0.10,
        "domain_expert_engineer":  0.10,
        "operations_engineer":     0.10,
        "site_supervisor":         0.10,
        "factory_floor_operator":  0.05,
    }
    res = measure_abstraction_distance(mix)
    return {
        "claim_id":               "C060",
        **res,
        "elite_overproduction_share": elite_overproduction_share,
        "threshold_met":          res["mean_abstraction"] > 0.6
                                   or elite_overproduction_share > 0.3,
        "falsifier":
            "automation deployment with management coalition dominated by "
            "substrate-experienced operators AND elite-overproduction share "
            "below 0.3, sustained for 5+ years",
    }


# ---------------------------------------------------------------------------
# C061  Care work invisibility
# ---------------------------------------------------------------------------

# Canonical care-work categories across substrates. Each row tracks
# whether the category is line-itemed in management's cost-accounting
# (visible) and whether prevented failures attributable to that category
# are counted in benefit accounting (rare).
CARE_WORK_INVENTORY: List[dict] = [
    {"category": "driver_pretrip_inspection",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "quality_inspector_walks",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "preventive_maintenance",
     "visible_cost": True,  "prevented_failure_counted": False},
    {"category": "teacher_one_on_one_attention",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "nurse_continuous_observation",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "farmer_soil_management",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "manager_knowing_team",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "operator_landmark_familiarity",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "field_mechanic_intuition",
     "visible_cost": False, "prevented_failure_counted": False},
    {"category": "customer_relationship_context",
     "visible_cost": False, "prevented_failure_counted": False},
]


def care_work_invisibility_score(
    inventory: List[dict] | None = None,
) -> dict:
    """Fraction of care work that is invisible in cost OR benefit accounting."""
    inv = inventory or CARE_WORK_INVENTORY
    total = len(inv)
    invisible_cost = sum(1 for c in inv if not c["visible_cost"])
    uncounted_benefit = sum(1 for c in inv if not c["prevented_failure_counted"])
    fully_invisible = sum(1 for c in inv
                           if (not c["visible_cost"])
                              and (not c["prevented_failure_counted"]))
    return {
        "total_categories":       total,
        "invisible_cost":         invisible_cost,
        "uncounted_benefit":      uncounted_benefit,
        "fully_invisible":        fully_invisible,
        "invisibility_score":     fully_invisible / total if total else 0.0,
    }


def c061_verdict(inventory: List[dict] | None = None) -> dict:
    """C061: concern registers when > 50% of care work is fully invisible."""
    res = care_work_invisibility_score(inventory)
    return {
        "claim_id":      "C061",
        **res,
        "threshold_met": res["invisibility_score"] > 0.50,
        "falsifier":
            "cost-accounting framework that line-items each care-work "
            "category AND counts prevented failures as benefit; sustained "
            "in published reports over 3+ years",
    }


# ---------------------------------------------------------------------------
# C062  Knowledge-authority inversion
# ---------------------------------------------------------------------------

# Default role inventory with substrate knowledge and decision authority
# on [0, 1]. Inversion = high knowledge with low authority, OR high
# authority with low knowledge.
DEFAULT_ROLE_KNOWLEDGE_AUTHORITY: List[dict] = [
    {"role": "experienced_driver",            "knowledge": 0.90, "authority": 0.10},
    {"role": "field_mechanic",                "knowledge": 0.85, "authority": 0.05},
    {"role": "domain_engineer",               "knowledge": 0.80, "authority": 0.25},
    {"role": "dispatcher_operations",         "knowledge": 0.60, "authority": 0.30},
    {"role": "operations_manager",            "knowledge": 0.55, "authority": 0.50},
    {"role": "MBA_VP_operations",             "knowledge": 0.20, "authority": 0.75},
    {"role": "C_suite_executive",             "knowledge": 0.10, "authority": 0.90},
    {"role": "board_director",                "knowledge": 0.05, "authority": 0.95},
]


def knowledge_authority_inversion(
    roles: List[dict] | None = None,
) -> dict:
    """Per-role inversion = abs(knowledge - authority); weighted mean across roles."""
    r = roles or DEFAULT_ROLE_KNOWLEDGE_AUTHORITY
    inversions = [abs(x["knowledge"] - x["authority"]) for x in r]
    mean_inv = sum(inversions) / len(inversions) if inversions else 0.0
    high_inv = [x for x in r
                if abs(x["knowledge"] - x["authority"]) > 0.50]
    return {
        "by_role":           [{"role": x["role"],
                                "knowledge": x["knowledge"],
                                "authority": x["authority"],
                                "inversion": abs(x["knowledge"] - x["authority"])}
                               for x in r],
        "mean_inversion":    mean_inv,
        "high_inversion_roles": [x["role"] for x in high_inv],
    }


def c062_verdict(roles: List[dict] | None = None) -> dict:
    """C062: concern registers when mean inversion > 0.4 OR >= 2 roles at high inversion."""
    res = knowledge_authority_inversion(roles)
    return {
        "claim_id":      "C062",
        **res,
        "threshold_met": res["mean_inversion"] > 0.40
                         or len(res["high_inversion_roles"]) >= 2,
        "falsifier":
            "organization where role-level knowledge and authority are "
            "co-distributed (correlation > 0.7 across roles) AND substrate "
            "decisions are made by substrate-knowledgeable roles",
    }


# ---------------------------------------------------------------------------
# C063  Accountability misdirection / blame externalization
# ---------------------------------------------------------------------------

# Six-step blame cascade observed in post-failure post-mortems. Each
# step has a `target_role` and a `culpability_share` (where the actual
# decision-causation responsibility lies, summing to ~1.0 ideally).
DEFAULT_BLAME_CASCADE: List[dict] = [
    {"step": 1, "target_role": "MBA_decision_maker_who_cut_care_work",
     "actual_culpability_share": 0.55, "narrative_blame_share": 0.05},
    {"step": 2, "target_role": "consultant_who_recommended_cuts",
     "actual_culpability_share": 0.15, "narrative_blame_share": 0.02},
    {"step": 3, "target_role": "executives_who_approved",
     "actual_culpability_share": 0.15, "narrative_blame_share": 0.03},
    {"step": 4, "target_role": "engineers_who_built_replacement",
     "actual_culpability_share": 0.05, "narrative_blame_share": 0.35},
    {"step": 5, "target_role": "operators_who_deployed",
     "actual_culpability_share": 0.05, "narrative_blame_share": 0.30},
    {"step": 6, "target_role": "AI_system_that_hallucinated",
     "actual_culpability_share": 0.05, "narrative_blame_share": 0.25},
]


def blame_cascade_analysis(
    cascade: List[dict] | None = None,
) -> dict:
    """Compare actual culpability share to narrative blame share."""
    c = cascade or DEFAULT_BLAME_CASCADE
    rows = []
    misdirection = 0.0
    for s in c:
        delta = s["narrative_blame_share"] - s["actual_culpability_share"]
        misdirection += abs(delta)
        rows.append({**s, "delta_narrative_minus_actual": delta})
    return {
        "by_step":              rows,
        "total_misdirection":   misdirection / 2.0,    # /2 because each unit
                                                       # of misdirection appears
                                                       # twice (subtracted from
                                                       # one role, added to other)
    }


def c063_verdict(cascade: List[dict] | None = None) -> dict:
    """C063: concern registers when total misdirection > 0.30 (substantial reallocation)."""
    res = blame_cascade_analysis(cascade)
    return {
        "claim_id":      "C063",
        **res,
        "threshold_met": res["total_misdirection"] > 0.30,
        "falsifier":
            "published post-mortem of an automation-substrate failure where "
            "the MBA decision-maker who eliminated the care-work line item "
            "receives the largest narrative blame share, with the cause-effect "
            "chain documented",
    }


# ---------------------------------------------------------------------------
# C064  Substrate care + authority as non-negotiable preconditions
# ---------------------------------------------------------------------------

def substrate_preconditions_check(
    care_work_continued: bool,
    care_work_costed_visibly: bool,
    failure_cost_known: bool,
    decision_authority_holder_has_substrate_knowledge: bool,
    approval_required_from_substrate_experienced_operator: bool,
) -> dict:
    """Five preconditions for any automation deployment to be admissible."""
    checks = {
        "care_work_continued":                          care_work_continued,
        "care_work_costed_visibly":                     care_work_costed_visibly,
        "failure_cost_known":                           failure_cost_known,
        "decision_authority_substrate_knowledge":       decision_authority_holder_has_substrate_knowledge,
        "substrate_experienced_operator_approval":      approval_required_from_substrate_experienced_operator,
    }
    passed = sum(1 for v in checks.values() if v)
    return {
        "preconditions":   checks,
        "passed":          passed,
        "total":           len(checks),
        "all_pass":        passed == len(checks),
    }


def c064_verdict(
    care_work_continued: bool = False,
    care_work_costed_visibly: bool = False,
    failure_cost_known: bool = False,
    decision_authority_holder_has_substrate_knowledge: bool = False,
    approval_required_from_substrate_experienced_operator: bool = False,
) -> dict:
    """C064: concern registers when ANY of the 5 preconditions fails."""
    res = substrate_preconditions_check(
        care_work_continued,
        care_work_costed_visibly,
        failure_cost_known,
        decision_authority_holder_has_substrate_knowledge,
        approval_required_from_substrate_experienced_operator)
    return {
        "claim_id":      "C064",
        **res,
        "threshold_met": not res["all_pass"],
        "falsifier":
            "automation deployment in any domain that was approved by "
            "someone with substrate operational experience AND maintains "
            "care work as a costed line item AND has documented failure-"
            "cost-if-care-skipped numbers; sustained without substrate "
            "failure for 5+ years",
    }


if __name__ == "__main__":
    print("C060:", c060_verdict()["threshold_met"])
    print("C061:", c061_verdict()["threshold_met"])
    print("C062:", c062_verdict()["threshold_met"])
    print("C063:", c063_verdict()["threshold_met"])
    print("C064 default-all-false:", c064_verdict()["threshold_met"])
    print("C064 all-pass:", c064_verdict(True, True, True, True, True)["threshold_met"])
