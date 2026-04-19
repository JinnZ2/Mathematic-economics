"""
Four-corner semantic validation.
Tests claim, negation, opposite, and opposite-negation.
Surfaces scope boundaries where each claim holds true.
"""

def test_four_corners(base_claim: str, structure_type: str = "organizational") -> dict:
    claims = {
        "claim_1"  : base_claim,
        "claim_2"  : _negate(base_claim),
        "claim_3"  : _opposite(base_claim),
        "claim_4"  : _opposite(_negate(base_claim)),
    }

    results = {}
    for key, claim in claims.items():
        results[key] = {
            "claim"   : claim,
            "verdict" : _run_through_physicsguard(claim),
            "scope"   : _extract_scope(claim, key),
        }

    return {
        "base_claim"      : base_claim,
        "four_corners"    : results,
        "scope_map"       : _map_scopes(results),
        "contradiction"   : _check_contradiction(results),
    }

def _negate(claim: str) -> str:
    """Flip the valence: enable->disable, speed->slowness"""
    neg_map = {
        "enable"   : "disable",
        "fast"     : "slow",
        "speed"    : "slowness",
        "efficient": "wasteful",
        "produce"  : "prevent",
    }
    result = claim
    for orig, negated in neg_map.items():
        result = result.replace(orig, negated)
    return result

def _opposite(claim: str) -> str:
    """Flip the subject: hierarchies->distributed"""
    opp_map = {
        "hierarchies"        : "distributed systems",
        "centralized"        : "decentralized",
        "top-down"           : "bottom-up",
        "command structure"  : "protocol-based structure",
    }
    result = claim
    for orig, opposite in opp_map.items():
        result = result.replace(orig, opposite)
    return result

def _run_through_physicsguard(claim: str) -> dict:
    """Import and run the main PhysicsGuard verdict"""
    from main import run
    return run(claim)

def _extract_scope(claim: str, corner: str) -> dict:
    scope_keywords = ["during", "under", "when", "if", "only", "requires", "depends"]
    conditions = [word for word in claim.split() if word.lower() in scope_keywords]

    return {
        "corner"          : corner,
        "has_conditions"  : len(conditions) > 0,
        "scope_words"     : conditions,
        "implicit_scope"  : _infer_implicit_scope(claim, corner),
    }

def _infer_implicit_scope(claim: str, corner: str) -> list:
    scope_inferences = {
        "claim_1": [
            "peacetime / stable resource conditions",
            "low rate of environmental change",
            "predictable threat model",
            "information already centralized",
        ],
        "claim_2": [
            "crisis / resource scarcity",
            "high rate of change",
            "novel threats",
            "information distributed across field",
        ],
        "claim_3": [
            "real-time adaptation required",
            "high information density",
            "parallel decision-making",
            "failure tolerance critical",
        ],
        "claim_4": [
            "command authority required",
            "sequential decisions",
            "centralized information",
            "failure intolerance",
        ],
    }
    return scope_inferences.get(corner, [])

def _map_scopes(results: dict) -> dict:
    verdicts = {k: v["verdict"]["verdict"] for k, v in results.items()}

    return {
        "agreement"        : _find_agreement(verdicts),
        "conflicts"        : _find_conflicts(verdicts),
        "scope_boundaries" : _map_boundaries(results),
        "robust_claims"    : _extract_robust(verdicts),
    }

def _find_agreement(verdicts: dict) -> list:
    clean = [k for k, v in verdicts.items() if v == "CLEAN"]
    return clean if clean else ["No universal agreement"]

def _find_conflicts(verdicts: dict) -> list:
    conflicts = []
    if verdicts["claim_1"] != verdicts["claim_2"]:
        conflicts.append("Claim 1 and 2 (direct negation) disagree — scope-dependent")
    if verdicts["claim_3"] != verdicts["claim_4"]:
        conflicts.append("Claim 3 and 4 (opposite negation) disagree — scope-dependent")
    return conflicts if conflicts else ["No conflicts detected"]

def _map_boundaries(results: dict) -> dict:
    return {
        "hierarchies_work_when" : results["claim_1"]["scope"]["implicit_scope"],
        "distributed_works_when": results["claim_3"]["scope"]["implicit_scope"],
        "transition_point"      : _estimate_transition(results),
    }

def _estimate_transition(results: dict) -> str:
    return "Rate of environmental change + information distribution density"

def _extract_robust(verdicts: dict) -> list:
    robust = []
    for claim, verdict in verdicts.items():
        if verdict == "CLEAN":
            robust.append(claim)
    return robust if robust else ["No claims robust across all scopes"]

def _check_contradiction(results: dict) -> dict:
    verdicts = {k: v["verdict"]["verdict"] for k, v in results.items()}
    has_contradiction = verdicts["claim_1"] != verdicts["claim_2"]
    return {
        "detected": has_contradiction,
        "detail": (
            "Direct negation yields different verdict — claim is scope-dependent"
            if has_contradiction else "Consistent across negation"
        ),
    }

def print_four_corners(results: dict):
    print("\n" + "="*70)
    print("FOUR-CORNER CONTRAPOSITIVE TEST")
    print("="*70)
    print(f"\nBase Claim: {results['base_claim']}\n")

    for corner, data in results["four_corners"].items():
        verdict = data["verdict"]["verdict"]
        icon = "+" if verdict == "CLEAN" else "x"
        print(f"{icon} {corner.upper()}")
        print(f"   Claim  : {data['claim']}")
        print(f"   Verdict: {verdict}")
        print(f"   Scope  : {data['scope']['implicit_scope'][:2]}")
        print()

    scope_map = results["scope_map"]
    print("-"*70)
    print("SCOPE ANALYSIS:")
    print(f"  Agreement     : {scope_map['agreement']}")
    print(f"  Conflicts     : {scope_map['conflicts']}")
    print(f"  Robust claims : {scope_map['robust_claims']}")
    print(f"  Boundary      : {scope_map['scope_boundaries']['transition_point']}")
    print("="*70 + "\n")
