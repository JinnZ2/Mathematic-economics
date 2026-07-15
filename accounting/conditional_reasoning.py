#!/usr/bin/env python3
"""
CONDITIONAL REASONING ENGINE — Falsifiability Layer
-----------------------------------------------------
Every assertion is a function of its necessary conditions.
If a condition is falsified, the assertion is suspended.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any, Optional
import inspect

# ----------------------------------------------------------------------
# 1. The Core Data Structure
# ----------------------------------------------------------------------
@dataclass
class Condition:
    """A single necessary condition for a claim to be true."""
    name: str                       # human-readable label
    test: Callable[[], bool]        # function that returns True if condition holds
    description: str = ""           # why this condition matters
    last_result: Optional[bool] = None
    evidence: str = ""              # supporting data source

    def evaluate(self) -> bool:
        """Run the test and store the result."""
        self.last_result = self.test()
        return self.last_result

@dataclass
class ConditionalClaim:
    """A claim that is true ONLY IF all its conditions are satisfied."""
    statement: str
    conditions: List[Condition]
    # Metadata
    source: str = ""
    falsification_note: str = ""    # what would disprove the whole claim

    def evaluate(self, verbose: bool = True) -> str:
        """Evaluate all conditions and return the claim's status."""
        if verbose:
            print(f"\nCLAIM: {self.statement}")
            print("-" * 60)
        all_true = True
        for cond in self.conditions:
            result = cond.evaluate()
            if verbose:
                status = "✅ TRUE" if result else "❌ FALSE"
                print(f"  [{status}] {cond.name}")
                if cond.description:
                    print(f"          {cond.description}")
                if cond.evidence:
                    print(f"          Evidence: {cond.evidence}")
            if not result:
                all_true = False
        if verbose:
            print("-" * 60)
            if all_true:
                print("RESULT: Claim stands (all preconditions met).")
            else:
                print("RESULT: Claim is SUSPENDED — necessary conditions not satisfied.")
        return "TRUE" if all_true else ("FALSE" if any(c.last_result == False for c in self.conditions) else "UNCERTAIN")

# ----------------------------------------------------------------------
# 2. Example: Hormuz Strait "International Waters"
# ----------------------------------------------------------------------
def build_hormuz_claim() -> ConditionalClaim:
    # Condition 1: The coastal state is not under armed attack.
    def coastal_state_not_under_attack() -> bool:
        # In a real system, this would query a live database of ongoing conflicts.
        # For demonstration, we'll assume it's a variable we can set.
        return not _global_state.get("iran_under_attack", False)

    # Condition 2: The strait connects two parts of the high seas/EEZ.
    def connects_high_seas() -> bool:
        # Geographical fact, always true.
        return True

    # Condition 3: The right of transit passage is respected by all parties.
    def transit_passage_accepted() -> bool:
        # Customary international law condition.
        return _global_state.get("transit_passage_accepted", True)

    return ConditionalClaim(
        statement="The Strait of Hormuz is effectively international waters for navigation.",
        conditions=[
            Condition(
                name="Coastal state (Iran) not under armed attack",
                test=coastal_state_not_under_attack,
                description="If Iran is bombed, it can legally restrict passage.",
                evidence="Corfu Channel (1949): right of passage exists 'in time of peace'."
            ),
            Condition(
                name="Geography: strait connects high seas/EEZ",
                test=connects_high_seas,
                description="UNCLOS Part III requires this geographical criterion.",
                evidence="Physical geography; Persian Gulf to Gulf of Oman."
            ),
            Condition(
                name="International consensus upholds transit passage",
                test=transit_passage_accepted,
                description="Even if law exists, lack of enforcement or recognition matters.",
                evidence="US Freedom of Navigation operations; global shipping practice."
            )
        ],
        source="UNCLOS, customary international law",
        falsification_note="If Iran is under missile attack, the claim becomes FALSE for enemy warships."
    )

# ----------------------------------------------------------------------
# 3. Example: Office AC "For Customers"
# ----------------------------------------------------------------------
def build_office_ac_claim() -> ConditionalClaim:
    # Condition 1: Customers actually visit unannounced.
    def customers_visit_unannounced() -> bool:
        # Real data would be visitor logs.
        return _global_state.get("unannounced_customer_visits_per_year", 0) > 12

    # Condition 2: Full HVAC is required to impress customers.
    def hvac_impresses_customers() -> bool:
        return _global_state.get("customer_complaints_about_temp", 0) < 2

    return ConditionalClaim(
        statement="We must keep the office fully air-conditioned year-round because customers visit.",
        conditions=[
            Condition(
                name="Unannounced customer visits are frequent (≥1/month)",
                test=customers_visit_unannounced,
                description="If customers schedule visits, AC can be adjusted in advance.",
                evidence="Visitor logbook; reception records."
            ),
            Condition(
                name="Customers care about office temperature",
                test=hvac_impresses_customers,
                description="If no complaints ever, AC might not be necessary.",
                evidence="Customer feedback forms."
            )
        ],
        falsification_note="If unannounced visits are rare and no complaints exist, the AC is wasted."
    )

# ----------------------------------------------------------------------
# 4. Global State (for demonstration)
# ----------------------------------------------------------------------
_global_state: Dict[str, Any] = {
    "iran_under_attack": False,            # toggle to test
    "transit_passage_accepted": True,
    "unannounced_customer_visits_per_year": 3,
    "customer_complaints_about_temp": 0,
}

# ----------------------------------------------------------------------
# 5. Interactive Audit
# ----------------------------------------------------------------------
def main():
    print("=" * 60)
    print("CONDITIONAL REASONING ENGINE — LIVE AUDIT")
    print("=" * 60)

    # Build and evaluate claims
    hormuz = build_hormuz_claim()
    office = build_office_ac_claim()

    # First run: peacetime
    print("\n[Scenario: Peacetime, no attacks]")
    hormuz.evaluate()

    print("\n[Scenario: Office with rare visitors]")
    office.evaluate()

    # Change the global state: Iran under attack
    print("\n" + "=" * 60)
    print("CHANGING STATE: Iran comes under missile attack...")
    _global_state["iran_under_attack"] = True
    print("=" * 60)
    hormuz.evaluate()

    # Change office scenario: customers suddenly appear weekly
    print("\n" + "=" * 60)
    print("CHANGING STATE: Unannounced customer visits increase to 20/year...")
    _global_state["unannounced_customer_visits_per_year"] = 20
    print("=" * 60)
    office.evaluate()

    print("\n" + "=" * 60)
    print("FALSIFIABILITY NOTE:")
    print(f"  {hormuz.falsification_note}")
    print(f"  {office.falsification_note}")

if __name__ == "__main__":
    main()
