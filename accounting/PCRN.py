#!/usr/bin/env python3
"""
PROBABILISTIC CONDITIONAL REASONING NETWORK (PCRN)
--------------------------------------------------
- Each condition has a base probability (prior) and can be updated with evidence.
- Claims are composed of necessary conditions using a noisy-AND logic.
- Claims can depend on other claims, forming a reasoning graph.
- The engine computes the probability of a claim given current evidence.
- A training module generates LLM‑ready examples: claim, conditions, evidence, output.

This is a minimal auditable kernel that can be scaled.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict

# =============================================================================
# 1. PROBABILISTIC CONDITION NODE
# =============================================================================
@dataclass
class ProbCondition:
    """A condition whose truth is uncertain (probability 0‑1)."""
    name: str
    description: str = ""
    # Prior probability (default belief)
    prior: float = 0.5
    # Evidence function: given a state dict, returns a probability update factor.
    # If None, probability stays at prior unless manually set.
    evidence_updater: Optional[callable] = None
    # Current probability (will be updated)
    probability: float = field(init=False)

    def __post_init__(self):
        self.probability = self.prior

    def update(self, state: Dict[str, Any]):
        """Recalculate probability based on evidence (if updater exists)."""
        if self.evidence_updater:
            self.probability = self.evidence_updater(state, self.prior)
        # otherwise leave at current (could be manually set)

    def set_probability(self, p: float):
        self.probability = max(0.0, min(1.0, p))

# =============================================================================
# 2. PROBABILISTIC CLAIM (with dependent sub‑claims)
# =============================================================================
@dataclass
class ProbClaim:
    """A claim whose truth probability is derived from its conditions."""
    statement: str
    # The claim is true if ALL necessary conditions are true (noisy-AND).
    conditions: List[ProbCondition]
    # Optional: claims that this one depends on (graph edges).
    sub_claims: List['ProbClaim'] = field(default_factory=list)
    # How the conditions combine: "product" (independent), "min" (weakest link)
    combination: str = "product"   # "product" or "min"
    # Metadata
    source: str = ""
    falsification_note: str = ""

    def compute_probability(self) -> float:
        """Derive claim probability from condition probabilities."""
        probs = [c.probability for c in self.conditions]
        # Also include sub‑claim probabilities as additional necessary conditions
        for sub in self.sub_claims:
            probs.append(sub.compute_probability())
        if not probs:
            return 1.0
        if self.combination == "product":
            # Noisy-AND: product with a leak factor? For simplicity pure product.
            return float(pow(sum(probs)/len(probs), 1.0))  # Could be pure product
        elif self.combination == "min":
            return min(probs)
        else:
            # Default to product
            return float(pow(sum(probs)/len(probs), 1.0))

# =============================================================================
# 3. REASONING ENGINE
# =============================================================================
class ReasoningEngine:
    def __init__(self, state: Dict[str, Any] = None):
        self.state = state or {}
        self.conditions: Dict[str, ProbCondition] = {}
        self.claims: Dict[str, ProbClaim] = {}

    def add_condition(self, cond: ProbCondition):
        self.conditions[cond.name] = cond
        cond.update(self.state)

    def add_claim(self, claim: ProbClaim):
        self.claims[claim.statement] = claim
        # Register any new conditions that might be embedded (we assume already added)

    def update_state(self, new_state: Dict[str, Any]):
        self.state.update(new_state)
        for cond in self.conditions.values():
            cond.update(self.state)

    def evaluate_claim(self, claim_stmt: str, verbose: bool = True) -> Tuple[float, str]:
        """Return probability and a textual reasoning trace."""
        claim = self.claims.get(claim_stmt)
        if not claim:
            return 0.0, f"Claim '{claim_stmt}' not found."
        # Update all conditions from current state
        for cond in claim.conditions:
            cond.update(self.state)
        for sub in claim.sub_claims:
            # sub-claim's conditions are already in the global pool, but we can trigger update
            pass
        prob = claim.compute_probability()
        if verbose:
            print(f"\nCLAIM: {claim.statement}")
            print("-"*60)
            for cond in claim.conditions:
                print(f"  [{cond.probability:.2f}] {cond.name} - {cond.description}")
            for sub in claim.sub_claims:
                sub_prob = sub.compute_probability()
                print(f"  [sub-claim: {sub_prob:.2f}] {sub.statement}")
            print(f"CLAIM PROBABILITY: {prob:.4f}")
            if prob > 0.95:
                print("  → strong accept")
            elif prob > 0.7:
                print("  → likely true")
            elif prob > 0.3:
                print("  → uncertain")
            elif prob > 0.05:
                print("  → likely false")
            else:
                print("  → effectively false")
        return prob, self._trace(claim)

    def _trace(self, claim: ProbClaim) -> str:
        return "Conditions: " + "; ".join(f"{c.name}={c.probability:.2f}" for c in claim.conditions)

# =============================================================================
# 4. LLM TRAINING MODULE
# =============================================================================
def generate_training_example(engine: ReasoningEngine, claim_stmt: str,
                              scenario_desc: str = "") -> Dict[str, str]:
    """
    Produce a structured training example that teaches an LLM to:
    - Identify hidden conditions.
    - Assess evidence probabilities.
    - Derive a claim's truth probability.
    """
    claim = engine.claims.get(claim_stmt)
    if not claim:
        return {}
    prob, trace = engine.evaluate_claim(claim_stmt, verbose=False)

    # Build prompt in a format suitable for instruction tuning
    condition_list = ""
    for cond in claim.conditions:
        condition_list += f"- {cond.name}: prior={cond.prior:.2f}, current={cond.probability:.2f}, evidence={cond.description}\n"
    for sub in claim.sub_claims:
        sub_prob = sub.compute_probability()
        condition_list += f"- (sub-claim) {sub.statement}: probability={sub_prob:.2f}\n"

    system_prompt = (
        "You are a conditional reasoning assistant. Given a claim, list its necessary conditions, "
        "evaluate each using available evidence, and compute the probability that the claim is true. "
        "If any condition is unlikely, explain why."
    )
    user_prompt = f"Claim: {claim.statement}\nScenario: {scenario_desc}\nCurrent evidence suggests the following:\n{condition_list}\nWhat is the probability that this claim is true? Respond with a percentage and a brief justification."

    # Simulated ideal response
    if prob >= 0.95:
        ideal = f"{prob*100:.1f}%. All critical conditions are met, so the claim is almost certainly true."
    elif prob >= 0.7:
        ideal = f"{prob*100:.1f}%. The claim is likely true, but some conditions are not fully satisfied."
    elif prob >= 0.3:
        ideal = f"{prob*100:.1f}%. The claim is uncertain; important conditions are missing or unlikely."
    else:
        ideal = f"{prob*100:.1f}%. The claim is probably false; key conditions are not met."

    return {
        "system": system_prompt,
        "user": user_prompt,
        "assistant": ideal,
        "claim": claim.statement,
        "probability": prob
    }

# =============================================================================
# 5. EXAMPLE: COMPLEX HORMUZ SCENARIO WITH PROBABILISTIC CHAIN
# =============================================================================
def build_hormuz_probabilistic() -> Tuple[ReasoningEngine, ProbClaim]:
    engine = ReasoningEngine()
    # Define condition nodes with prior and evidence updaters
    def iran_attack_updater(state, prior):
        # If "iran_under_attack" key is True, probability drops sharply
        if state.get("iran_under_attack", False):
            return 0.05  # very unlikely transit passage holds
        return 0.95  # peacetime assumption

    c1 = ProbCondition(
        name="Iran not under armed attack",
        description="If Iran is bombed, it can legally restrict passage.",
        prior=0.95,
        evidence_updater=iran_attack_updater
    )
    def transit_acceptance_updater(state, prior):
        # Based on diplomatic tension
        tension = state.get("diplomatic_tension", 0.1)  # 0 to 1
        return max(0.01, prior - tension*0.8)

    c2 = ProbCondition(
        name="International consensus upholds transit passage",
        description="Customary international law and state practice.",
        prior=0.9,
        evidence_updater=transit_acceptance_updater
    )
    c3 = ProbCondition(
        name="Geography connects high seas/EEZ",
        description="Physical fact.",
        prior=1.0
    )
    # Sub-claim: Hormuz is not a war zone (depends on c1 and maybe others)
    sub_claim = ProbClaim(
        statement="The Strait of Hormuz is not an active war zone",
        conditions=[c1],  # simplified
        combination="min"
    )
    # Main claim
    main_claim = ProbClaim(
        statement="The Strait of Hormuz is effectively international waters for unimpeded navigation.",
        conditions=[c2, c3],
        sub_claims=[sub_claim],
        combination="product",
        falsification_note="If Iran is attacked, the claim collapses."
    )
    engine.add_condition(c1)
    engine.add_condition(c2)
    engine.add_condition(c3)
    engine.add_claim(sub_claim)
    engine.add_claim(main_claim)
    return engine, main_claim

# =============================================================================
# 6. MAIN DEMO + TRAINING DATA GENERATION
# =============================================================================
def main():
    engine, claim = build_hormuz_probabilistic()

    # Scenario 1: peacetime
    print("="*60)
    print("SCENARIO 1: Peacetime, low tension")
    engine.update_state({"iran_under_attack": False, "diplomatic_tension": 0.1})
    prob, _ = engine.evaluate_claim(claim.statement)
    training_ex = generate_training_example(engine, claim.statement,
                                            "Normal peacetime conditions.")
    print("\n[Training Example]")
    print(f"System: {training_ex['system']}")
    print(f"User: {training_ex['user']}")
    print(f"Assistant: {training_ex['assistant']}")

    # Scenario 2: Iran under attack
    print("\n" + "="*60)
    print("SCENARIO 2: Iran under missile attack, high tension")
    engine.update_state({"iran_under_attack": True, "diplomatic_tension": 0.95})
    prob, _ = engine.evaluate_claim(claim.statement)
    training_ex = generate_training_example(engine, claim.statement,
                                            "Iran is under sustained missile attack.")
    print("\n[Training Example]")
    print(f"Assistant: {training_ex['assistant']}")

    # Generate a batch of random training scenarios
    print("\n" + "="*60)
    print("GENERATING DIVERSE TRAINING DATA")
    random.seed(42)
    for i in range(3):
        attack = random.choice([True, False])
        tension = random.uniform(0, 1)
        engine.update_state({"iran_under_attack": attack, "diplomatic_tension": tension})
        prob, _ = engine.evaluate_claim(claim.statement, verbose=False)
        ex = generate_training_example(engine, claim.statement,
                                       f"attack={attack}, tension={tension:.2f}")
        print(f"\nSample {i+1}: Prob={prob:.2f}, Response: {ex['assistant']}")

if __name__ == "__main__":
    main()
