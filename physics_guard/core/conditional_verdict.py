"""
PhysicsGuard v1.1 — Scope-Conditional Verdict Layer
Replaces binary CLEAN/CORRUPTED with condition-mapped truth boundaries.
CC0 — github.com/JinnZ2/physicsguard
"""

from dataclasses import dataclass
from typing import Any, Dict, List

# -- Scope Parameters ---------------------------------------------------------

@dataclass
class ScopeCondition:
    parameter:   str        # what variable determines truth
    value:       Any        # current value
    threshold:   Any        # boundary value
    direction:   str        # "above" | "below" | "equals"
    description: str        # human readable

@dataclass
class ConditionalVerdict:
    claim:           str
    base_verdict:    str                    # CLEAN | SUSPECT | CORRUPTED
    score:           float
    true_if:         List[ScopeCondition]   # conditions where claim holds
    false_if:        List[ScopeCondition]   # conditions where claim breaks
    current_scope:   Dict[str, Any]         # measured current conditions
    verdict_now:     str                    # verdict under current conditions
    boundary_map:    Dict[str, str]         # parameter -> transition point
    summary:         str                    # one-line human output

# -- Scope Condition Library ---------------------------------------------------

SCOPE_CONDITIONS = {

    "hierarchy_works": {
        "true_if": [
            ScopeCondition("layers",            2,    3,      "below",  "2-3 decision layers max"),
            ScopeCondition("branching_factor",  3,    4,      "below",  "3-4 direct reports per node"),
            ScopeCondition("novelty_rate",      0.0,  0.05,   "below",  "near-zero novel inputs"),
            ScopeCondition("change_rate",       0.0,  0.10,   "below",  "near-zero environmental change"),
            ScopeCondition("enforcement_cost",  0.05, 0.10,   "below",  "enforcement overhead under 10%"),
            ScopeCondition("info_completeness", 1.0,  0.95,   "above",  "near-perfect information at top"),
        ],
        "false_if": [
            ScopeCondition("layers",            7,    4,      "above",  "4+ layers add exponential latency"),
            ScopeCondition("novelty_rate",      0.3,  0.05,   "above",  "novel inputs exceed 5%"),
            ScopeCondition("change_rate",       0.5,  0.10,   "above",  "environment changing faster than 10%/cycle"),
            ScopeCondition("enforcement_cost",  0.45, 0.10,   "above",  "enforcement consuming 45%+ of resources"),
            ScopeCondition("cascade_risk",      0.80, 0.75,   "above",  "single-point dependency above 75%"),
        ],
    },

    "distributed_works": {
        "true_if": [
            ScopeCondition("novelty_rate",        0.3,  0.05,  "above",  "novel inputs common"),
            ScopeCondition("change_rate",         0.5,  0.10,  "above",  "environment changing rapidly"),
            ScopeCondition("protocol_clarity",    0.9,  0.80,  "above",  "pre-agreed protocols clear"),
            ScopeCondition("node_autonomy",       0.8,  0.70,  "above",  "nodes have local decision authority"),
            ScopeCondition("info_distribution",   0.8,  0.70,  "above",  "knowledge distributed across nodes"),
        ],
        "false_if": [
            ScopeCondition("protocol_clarity",    0.2,  0.80,  "below",  "protocols unclear — coordination fails"),
            ScopeCondition("node_count",          500,  200,   "above",  "routing overhead explodes beyond 200 nodes"),
            ScopeCondition("network_reliability", 0.7,  0.95,  "below",  "message loss cascades through system"),
        ],
    },

    "patriarchy_works": {
        "true_if": [
            ScopeCondition("layers",          2,   3,    "below",  "church + work + family only (2-3 layers)"),
            ScopeCondition("change_rate",     0.0, 0.05, "below",  "conditions fully stable"),
            ScopeCondition("domain_count",    3,   3,    "below",  "3 domains max: church, work, family"),
            ScopeCondition("novelty_rate",    0.0, 0.02, "below",  "zero novel social inputs"),
            ScopeCondition("role_ambiguity",  0.0, 0.05, "below",  "roles fully predefined"),
        ],
        "false_if": [
            ScopeCondition("layers",         7,    3,    "above",  "govt + corps + institutions exceeds envelope"),
            ScopeCondition("domain_count",   7,    3,    "above",  "7 domains exceed 3-layer optimum"),
            ScopeCondition("change_rate",    0.6,  0.05, "above",  "modern economic/social volatility"),
            ScopeCondition("workforce_dist", 0.5,  0.10, "above",  "50%+ workforce outside predefined roles"),
            ScopeCondition("novelty_rate",   0.4,  0.02, "above",  "continuous novel social/tech inputs"),
        ],
    },

    "nomadic_egalitarian_works": {
        "true_if": [
            ScopeCondition("change_rate",        0.7,  0.30, "above",  "high environmental variability"),
            ScopeCondition("survival_pressure",  0.8,  0.50, "above",  "survival is primary optimization target"),
            ScopeCondition("info_distribution",  0.9,  0.70, "above",  "knowledge distributed across group"),
            ScopeCondition("resource_mobility",  0.9,  0.70, "above",  "resources require active location"),
            ScopeCondition("decision_speed",     0.8,  0.60, "above",  "rapid local decision required"),
        ],
        "false_if": [
            ScopeCondition("fixed_geography",    1.0,  0.20, "above",  "fixed to reservation/grid — removes mobility"),
            ScopeCondition("external_hierarchy", 1.0,  0.10, "above",  "imposed hierarchy overrides local authority"),
        ],
    },
}

# -- Conditional Verdict Engine ------------------------------------------------

def evaluate_conditional(
    claim_key:     str,
    current_scope: Dict[str, Any],
    base_result:   dict,
) -> ConditionalVerdict:
    if claim_key not in SCOPE_CONDITIONS:
        return _unknown_scope(claim_key, base_result)

    conditions   = SCOPE_CONDITIONS[claim_key]
    true_if      = conditions["true_if"]
    false_if     = conditions["false_if"]

    true_met     = _evaluate_conditions(true_if,  current_scope)
    false_met    = _evaluate_conditions(false_if, current_scope)

    verdict_now  = _current_verdict(true_met, false_met, base_result)
    boundary_map = _build_boundary_map(true_if, false_if)
    summary      = _build_summary(claim_key, true_met, false_met, current_scope)

    return ConditionalVerdict(
        claim        = claim_key,
        base_verdict = base_result["verdict"],
        score        = base_result["score"],
        true_if      = true_if,
        false_if     = false_if,
        current_scope= current_scope,
        verdict_now  = verdict_now,
        boundary_map = boundary_map,
        summary      = summary,
    )

def _evaluate_conditions(conditions: List[ScopeCondition], scope: Dict) -> List[dict]:
    results = []
    for c in conditions:
        if c.parameter not in scope:
            results.append({"condition": c, "met": None, "note": "parameter not measured"})
            continue
        val = scope[c.parameter]
        if c.direction == "above": met = val >= c.threshold
        elif c.direction == "below": met = val <= c.threshold
        else: met = val == c.threshold
        results.append({"condition": c, "met": met, "actual": val})
    return results

def _current_verdict(true_met, false_met, base_result) -> str:
    true_count  = sum(1 for r in true_met  if r.get("met") is True)
    false_count = sum(1 for r in false_met if r.get("met") is True)
    true_total  = len([r for r in true_met  if r.get("met") is not None])
    false_total = len([r for r in false_met if r.get("met") is not None])

    true_ratio  = true_count  / true_total  if true_total  else 0
    false_ratio = false_count / false_total if false_total else 0

    if false_ratio > 0.5:
        return "CORRUPTED_IN_CURRENT_SCOPE"
    elif true_ratio > 0.7:
        return "VALID_IN_CURRENT_SCOPE"
    else:
        return "SCOPE_BOUNDARY — conditional"

def _build_boundary_map(true_if, false_if) -> Dict[str, str]:
    boundaries = {}
    for c in true_if:
        boundaries[c.parameter] = f"True if {c.direction} {c.threshold} — {c.description}"
    for c in false_if:
        if c.parameter in boundaries:
            boundaries[c.parameter] += f" | False if {c.direction} {c.threshold}"
        else:
            boundaries[c.parameter] = f"False if {c.direction} {c.threshold} — {c.description}"
    return boundaries

def _build_summary(claim_key, true_met, false_met, scope) -> str:
    broken = [r["condition"].description for r in false_met if r.get("met") is True]
    holding = [r["condition"].description for r in true_met if r.get("met") is True]

    if broken:
        return (
            f"'{claim_key}' fails under current conditions: "
            f"{broken[0]}. "
            f"Would hold if: {holding[0] if holding else 'conditions reversed'}."
        )
    boundaries = list(_build_boundary_map(true_met, false_met).values())[:1]
    return f"'{claim_key}' holds under current conditions. Boundary: {boundaries}"

def _unknown_scope(claim_key, base_result) -> ConditionalVerdict:
    return ConditionalVerdict(
        claim        = claim_key,
        base_verdict = base_result["verdict"],
        score        = base_result["score"],
        true_if      = [],
        false_if     = [],
        current_scope= {},
        verdict_now  = "UNKNOWN_SCOPE",
        boundary_map = {},
        summary      = f"No scope conditions defined for '{claim_key}' — add to SCOPE_CONDITIONS",
    )

def print_conditional_verdict(cv: ConditionalVerdict):
    print("\n" + "="*70)
    print(f"CONDITIONAL VERDICT: {cv.claim}")
    print("="*70)
    print(f"Base verdict     : {cv.base_verdict}  (score {cv.score:.3f})")
    print(f"Verdict NOW      : {cv.verdict_now}")
    print(f"\nSummary: {cv.summary}")
    print("\nTRUE IF:")
    for r in cv.true_if:
        met = "+" if r.parameter in cv.current_scope else "?"
        print(f"  {met} {r.description}  (threshold: {r.direction} {r.threshold})")
    print("\nFALSE IF:")
    for r in cv.false_if:
        broken = ""
        if r.parameter in cv.current_scope:
            v = cv.current_scope[r.parameter]
            if r.direction == "above" and v >= r.threshold: broken = "  <- TRIGGERED"
            if r.direction == "below" and v <= r.threshold: broken = "  <- TRIGGERED"
        print(f"  {r.description}  (threshold: {r.direction} {r.threshold}){broken}")
    print("\nBOUNDARY MAP:")
    for param, boundary in cv.boundary_map.items():
        print(f"  {param:25}: {boundary}")
    print("="*70 + "\n")
