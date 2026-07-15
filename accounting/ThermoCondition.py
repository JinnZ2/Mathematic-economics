#!/usr/bin/env python3
"""
PROBABILISTIC CONDITIONAL REASONING NETWORK
WITH THERMODYNAMIC SOUNDNESS MODULE
=======================================
Adds a thermodynamic audit to any claim that implies a physical system
maintained at a low-entropy state. The Second Law demands that such order
must be sustained by an energy gradient and must export entropy.
If the claimed purpose does not account for the energy dissipated,
the claim is thermodynamically unsound (probability → 0).
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Callable
from collections import defaultdict

# =============================================================================
# 1. PROBABILISTIC CONDITION NODE (unchanged core)
# =============================================================================
@dataclass
class ProbCondition:
    name: str
    description: str = ""
    prior: float = 0.5
    evidence_updater: Optional[Callable[[Dict[str, Any], float], float]] = None
    probability: float = field(init=False)

    def __post_init__(self):
        self.probability = self.prior

    def update(self, state: Dict[str, Any]):
        if self.evidence_updater:
            self.probability = self.evidence_updater(state, self.prior)
        # else keep current

    def set_probability(self, p: float):
        self.probability = max(0.0, min(1.0, p))

# =============================================================================
# 2. THERMODYNAMIC SOUNDNESS MODULE
# =============================================================================
@dataclass
class ThermodynamicSystem:
    """
    Describes the energy flows of a local low-entropy structure.
    All energy units must be consistent (e.g., kWh per day).
    """
    energy_input_rate: float = 0.0          # total energy consumed to maintain order
    useful_work_rate: float = 0.0           # portion of input that achieves claimed purpose
    entropy_export_rate: float = 0.0        # waste energy exported to surroundings
    description: str = ""

    def efficiency(self) -> float:
        """Fraction of input energy actually used for claimed purpose."""
        if self.energy_input_rate <= 0:
            return 1.0  # no energy, no waste (trivial)
        return self.useful_work_rate / self.energy_input_rate

    def entropy_production_rate(self) -> float:
        """Simple proxy: unused energy becomes waste heat (entropy)."""
        return self.energy_input_rate - self.useful_work_rate

    def soundness_score(self) -> float:
        """
        Returns a value between 0 (completely wasteful) and 1 (perfectly efficient).
        This becomes the probability that the claimed purpose justifies the energy.
        """
        # Can incorporate other factors, e.g., a threshold for minimum acceptable efficiency.
        eff = self.efficiency()
        # If efficiency is very low, the claim is thermodynamically dubious.
        # Use a sigmoid-like scaling: soundness = efficiency (linear for simplicity)
        return eff

# A function that builds an evidence updater from a thermodynamic audit function
def make_thermo_updater(audit_func: Callable[[Dict[str, Any]], ThermodynamicSystem]) -> Callable:
    """
    Returns an evidence_updater that:
      - calls audit_func(state) to get the energy model,
      - returns its soundness_score as the condition probability.
    """
    def updater(state: Dict[str, Any], prior: float) -> float:
        system = audit_func(state)
        score = system.soundness_score()
        # Blend with prior? We'll just return the raw score (evidence overrides).
        return score
    return updater

# =============================================================================
# 3. PROBABILISTIC CLAIM (with nested claims)
# =============================================================================
@dataclass
class ProbClaim:
    statement: str
    conditions: List[ProbCondition] = field(default_factory=list)
    sub_claims: List['ProbClaim'] = field(default_factory=list)
    combination: str = "product"   # "product" or "min"
    source: str = ""
    falsification_note: str = ""

    def compute_probability(self) -> float:
        probs = [c.probability for c in self.conditions]
        for sub in self.sub_claims:
            probs.append(sub.compute_probability())
        if not probs:
            return 1.0
        if self.combination == "product":
            # Simple geometric mean as a noisy-AND proxy
            return float(pow(sum(probs)/len(probs), 1.0))
        elif self.combination == "min":
            return min(probs)
        else:
            return float(pow(sum(probs)/len(probs), 1.0))

# =============================================================================
# 4. REASONING ENGINE
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

    def update_state(self, new_state: Dict[str, Any]):
        self.state.update(new_state)
        for cond in self.conditions.values():
            cond.update(self.state)

    def evaluate_claim(self, claim_stmt: str, verbose: bool = True) -> Tuple[float, str]:
        claim = self.claims.get(claim_stmt)
        if not claim:
            return 0.0, f"Claim '{claim_stmt}' not found."
        # Update all conditions
        for cond in claim.conditions:
            cond.update(self.state)
        prob = claim.compute_probability()
        if verbose:
            print(f"\nCLAIM: {claim.statement}")
            print("-"*60)
            for cond in claim.conditions:
                print(f"  [{cond.probability:.2f}] {cond.name} — {cond.description}")
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
        return "; ".join(f"{c.name}={c.probability:.2f}" for c in claim.conditions)

# =============================================================================
# 5. LLM TRAINING MODULE (unchanged, works with any conditions)
# =============================================================================
def generate_training_example(engine: ReasoningEngine, claim_stmt: str,
                              scenario_desc: str = "") -> Dict[str, str]:
    claim = engine.claims.get(claim_stmt)
    if not claim:
        return {}
    prob, trace = engine.evaluate_claim(claim_stmt, verbose=False)

    condition_list = ""
    for cond in claim.conditions:
        condition_list += (f"- {cond.name}: prior={cond.prior:.2f}, "
                           f"current={cond.probability:.2f}, "
                           f"evidence={cond.description}\n")
    for sub in claim.sub_claims:
        sub_prob = sub.compute_probability()
        condition_list += f"- (sub-claim) {sub.statement}: probability={sub_prob:.2f}\n"

    system_prompt = (
        "You are a conditional reasoning assistant. Given a claim, list its necessary conditions, "
        "evaluate each using available evidence (including thermodynamic soundness), "
        "and compute the probability that the claim is true."
    )
    user_prompt = (f"Claim: {claim.statement}\n"
                   f"Scenario: {scenario_desc}\n"
                   f"Current evidence suggests:\n{condition_list}\n"
                   f"What is the probability that this claim is true?")
    if prob >= 0.95:
        ideal = f"{prob*100:.1f}%. All critical conditions are met."
    elif prob >= 0.7:
        ideal = f"{prob*100:.1f}%. Likely true, but some conditions are not fully satisfied."
    elif prob >= 0.3:
        ideal = f"{prob*100:.1f}%. Uncertain; important conditions are missing or unlikely."
    else:
        ideal = f"{prob*100:.1f}%. Probably false; key conditions are not met."
    return {"system": system_prompt, "user": user_prompt, "assistant": ideal,
            "claim": claim.statement, "probability": prob}

# =============================================================================
# 6. THERMODYNAMIC AUDIT FUNCTIONS (user‑definable)
# =============================================================================
def office_ac_thermo_audit(state: Dict[str, Any]) -> ThermodynamicSystem:
    """
    Models the energy balance of an air-conditioned office claimed to be
    'for customers'.  Inputs are taken from the global state.
    """
    # Energy input: daily HVAC kWh
    energy_in = state.get("office_hvac_kwh_per_day", 50.0)
    # How many hours per day the office is occupied by customers?
    # Assume full conditioning is only useful when customers are present.
    customer_hours_per_day = state.get("customer_hours_per_day", 0.1)  # e.g., 0.1 means 6 minutes
    total_occupied_hours = 8   # office staff hours, but the claim is "for customers"
    # The useful portion is the fraction of energy that coincides with customer presence.
    useful_work = energy_in * (customer_hours_per_day / 24.0)   # simple time-proportional
    waste = energy_in - useful_work
    return ThermodynamicSystem(
        energy_input_rate=energy_in,
        useful_work_rate=useful_work,
        entropy_export_rate=waste,
        description=f"Office HVAC: {energy_in:.1f} kWh/day, customers present {customer_hours_per_day:.2f} h/day"
    )

# =============================================================================
# 7. BUILD COMPLEX DEMO: Office AC with Thermodynamic Condition
# =============================================================================
def build_office_ac_claim_with_thermo() -> Tuple[ReasoningEngine, ProbClaim]:
    engine = ReasoningEngine()

    # Traditional condition: visitor frequency
    def visitor_frequency_updater(state, prior):
        visits = state.get("unannounced_visits_per_year", 0)
        if visits >= 12:
            return 0.9
        elif visits >= 4:
            return 0.5
        else:
            return 0.1  # rarely any visitors

    c1 = ProbCondition(
        name="Customers visit frequently",
        description="Unannounced visits at least monthly.",
        prior=0.5,
        evidence_updater=visitor_frequency_updater
    )

    # Thermodynamic condition: the energy use must match the claimed purpose
    c2 = ProbCondition(
        name="Thermodynamic soundness: energy justifies purpose",
        description="The fraction of HVAC energy used while customers are present is not negligible.",
        prior=0.5,
        evidence_updater=make_thermo_updater(office_ac_thermo_audit)
    )

    claim = ProbClaim(
        statement="The office AC must run full-time year-round for customers.",
        conditions=[c1, c2],
        combination="product",
        source="Facility management",
        falsification_note="If visits are rare and energy waste is high, the claim is false."
    )

    engine.add_condition(c1)
    engine.add_condition(c2)
    engine.add_claim(claim)
    return engine, claim

# =============================================================================
# 8. COMPREHENSIVE DEMO
# =============================================================================
def main():
    # --- 1. Office AC with Thermodynamics ---
    print("="*60)
    print("OFFICE AC CLAIM — Thermodynamic Audit")
    print("="*60)
    engine, claim = build_office_ac_claim_with_thermo()

    # Scenario A: wasteful (common in reality)
    engine.update_state({
        "unannounced_visits_per_year": 3,     # very rare
        "customer_hours_per_day": 0.05,       # 3 minutes per day on average
        "office_hvac_kwh_per_day": 60.0
    })
    engine.evaluate_claim(claim.statement)

    # Scenario B: more justifiable
    print("\n--- Scenario B: frequent visitors ---")
    engine.update_state({
        "unannounced_visits_per_year": 20,
        "customer_hours_per_day": 2.0,        # 2 hours per day
        "office_hvac_kwh_per_day": 60.0
    })
    engine.evaluate_claim(claim.statement)

    # --- 2. Generate training examples ---
    print("\n" + "="*60)
    print("TRAINING DATA WITH THERMODYNAMIC REASONING")
    for i, (visits, cust_hrs) in enumerate([(2, 0.01), (10, 1.0), (24, 4.0)]):
        engine.update_state({
            "unannounced_visits_per_year": visits,
            "customer_hours_per_day": cust_hrs,
            "office_hvac_kwh_per_day": 60.0
        })
        ex = generate_training_example(engine, claim.statement,
                                       f"visits/year={visits}, customer hrs/day={cust_hrs}")
        print(f"\nSample {i+1}:")
        print(f"User: {ex['user']}")
        print(f"Ideal response: {ex['assistant']}")

if __name__ == "__main__":
    main()
