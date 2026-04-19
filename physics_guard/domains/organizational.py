"""
PhysicsGuard v2 — Organizational Constraint Module
Checks social/organizational structure claims against:
- Resilience physics (distributed vs concentrated)
- Enforcement energy cost (maintenance overhead)
- Adaptive capacity (slack vs rigidity)
- Cascade failure risk (interdependency load)
CC0 — github.com/JinnZ2/physicsguard

References:
  Urban Resilience Simulator — phi resilience threshold (0.62).
  Thermodynamic Accountability Framework (JinnZ2/thermodynamic-accountability-framework)
    — parasitic enforcement, friction ratio, and collapse-threshold semantics
    reinforce the thresholds below. See domains/thermodynamic_accountability.py
    for the energy-balance equations that these ratios approximate.
"""

from dataclasses import dataclass
from typing import List

# -- Constraint Thresholds -----------------------------------------------------
# Organizational ratios are unitless proxies for thermodynamic quantities
# computed in domains/thermodynamic_accountability.py. A system failing here
# will generally also fail the energy-balance check there.

PHI_RESILIENCE_THRESHOLD    = 0.62   # Urban Resilience Simulator
MAX_ENFORCEMENT_RATIO       = 0.30   # TAF: >30% enforcement → parasitic friction regime
MIN_ADAPTIVE_SLACK          = 0.15   # TAF: <15% slack → distance_to_collapse < 0 under load
MAX_INTERDEPENDENCY_LOAD    = 0.75   # TAF: >75% single-point deps → cascade geometry

# -- Data Structures -----------------------------------------------------------

@dataclass
class OrgClaim:
    raw:                str
    structure_type:     str    # hierarchical | distributed | mixed
    enforcement_ratio:  float  # fraction of resources spent maintaining control
    adaptive_slack:     float  # fraction of capacity available for adaptation
    node_count:         int    # number of decision nodes
    single_point_deps:  int    # number of single-point-of-failure dependencies
    justification:      str    # claimed reason for structure

@dataclass
class OrgConstraintResult:
    claim:              OrgClaim
    resilience_score:   float
    enforcement_waste:  float
    cascade_risk:       float
    verdict:            str
    flags:              List[str]
    audit:              List[dict]

# -- Constraint Checkers -------------------------------------------------------

def check_resilience(claim: OrgClaim) -> dict:
    """
    Distributed systems above phi threshold are self-correcting.
    Hierarchical systems below threshold require external enforcement to survive.
    """
    if claim.structure_type == "hierarchical":
        score = claim.node_count / max(claim.node_count * 3, 1)
    elif claim.structure_type == "distributed":
        score = min(claim.node_count / 10, 1.0)
    else:
        score = 0.45

    passed = score >= PHI_RESILIENCE_THRESHOLD
    return {
        "law"     : "resilience_threshold",
        "score"   : score,
        "passed"  : passed,
        "detail"  : f"Resilience score {score:.3f} vs threshold {PHI_RESILIENCE_THRESHOLD}",
        "fix_hint": "Distribute decision nodes — increase count, reduce dependencies" if not passed else "OK",
    }

def check_enforcement_cost(claim: OrgClaim) -> dict:
    """
    If >30% of resources go to maintaining hierarchy rather than output,
    the structure is parasitic — consuming more than it produces.
    """
    passed = claim.enforcement_ratio <= MAX_ENFORCEMENT_RATIO
    waste  = max(0.0, claim.enforcement_ratio - MAX_ENFORCEMENT_RATIO)
    return {
        "law"     : "enforcement_energy_cost",
        "score"   : claim.enforcement_ratio,
        "passed"  : passed,
        "detail"  : f"Enforcement ratio {claim.enforcement_ratio:.2%} vs max {MAX_ENFORCEMENT_RATIO:.2%}",
        "fix_hint": f"Reduce enforcement overhead by {waste:.2%} — redistribute control" if not passed else "OK",
    }

def check_adaptive_slack(claim: OrgClaim) -> dict:
    """
    Systems with <15% adaptive slack cannot respond to novel constraints.
    Brittle under cascade pressure.
    """
    passed = claim.adaptive_slack >= MIN_ADAPTIVE_SLACK
    return {
        "law"     : "adaptive_slack",
        "score"   : claim.adaptive_slack,
        "passed"  : passed,
        "detail"  : f"Adaptive slack {claim.adaptive_slack:.2%} vs minimum {MIN_ADAPTIVE_SLACK:.2%}",
        "fix_hint": "Free capacity from enforcement overhead to restore adaptive slack" if not passed else "OK",
    }

def check_cascade_risk(claim: OrgClaim) -> dict:
    """
    Single-point dependencies above 75% of total nodes = cascade failure geometry.
    One node failure propagates system-wide.
    """
    if claim.node_count == 0:
        ratio = 1.0
    else:
        ratio = claim.single_point_deps / claim.node_count

    passed = ratio <= MAX_INTERDEPENDENCY_LOAD
    return {
        "law"     : "cascade_failure_risk",
        "score"   : ratio,
        "passed"  : passed,
        "detail"  : f"Single-point dependency ratio {ratio:.2%} vs max {MAX_INTERDEPENDENCY_LOAD:.2%}",
        "fix_hint": "Add redundant pathways — reduce single-point dependencies" if not passed else "OK",
    }

def check_justification(claim: OrgClaim) -> dict:
    """
    Common false justifications for hierarchy that fail physics:
    - 'efficiency' claims in systems with high enforcement overhead
    - 'security' claims in low-resilience systems
    - 'natural order' claims without evolutionary basis
    """
    FALSE_JUSTIFICATIONS = {
        "efficiency"   : claim.enforcement_ratio > 0.20,
        "security"     : claim.single_point_deps > claim.node_count * 0.5,
        "natural order": claim.structure_type == "hierarchical" and claim.adaptive_slack < 0.20,
        "necessary"    : claim.enforcement_ratio > MAX_ENFORCEMENT_RATIO,
    }
    j = claim.justification.lower()
    triggered = [k for k, v in FALSE_JUSTIFICATIONS.items() if k in j and v]
    passed = len(triggered) == 0
    return {
        "law"     : "justification_validity",
        "score"   : 1.0 if passed else 0.0,
        "passed"  : passed,
        "detail"  : f"False justification detected: {triggered}" if not passed else "Justification consistent",
        "fix_hint": f"Claims of {triggered} contradict org physics — remove justification" if not passed else "OK",
    }

# -- Main Entry ----------------------------------------------------------------

def check_organization(claim: OrgClaim) -> OrgConstraintResult:
    checks = [
        check_resilience(claim),
        check_enforcement_cost(claim),
        check_adaptive_slack(claim),
        check_cascade_risk(claim),
        check_justification(claim),
    ]

    failed  = [c for c in checks if not c["passed"]]
    total   = len(checks)
    score   = len(failed) / total
    flags   = [c["law"] for c in failed]

    if score == 0.0:   verdict = "CLEAN"
    elif score < 0.5:  verdict = "SUSPECT"
    else:              verdict = "CORRUPTED"

    return OrgConstraintResult(
        claim            = claim,
        resilience_score = checks[0]["score"],
        enforcement_waste= checks[1]["score"],
        cascade_risk     = checks[3]["score"],
        verdict          = verdict,
        flags            = flags,
        audit            = checks,
    )
