#!/usr/bin/env python3
"""
grounding_check.py – Validate a claim against physical conservation laws and constraint layers.
CC0. Stdlib only.

Checks:
  1. Energy conservation
  2. Mass conservation
  3. Entropy bounds
  4. Shannon information limits
  5. Earth-system constraint layers (placeholder for Layer 0-7 checks)

Usage:
  python inquiry_engine/grounding_check.py --claim I001
  python inquiry_engine/grounding_check.py --statement "Perpetual motion machine"
"""

import argparse
import json
import math
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# Simple keywords that often signal a physical impossibility
VIOLATION_KEYWORDS = {
    "energy": ["perpetual motion", "infinite energy", "free energy", "over unity"],
    "mass":   ["materialize from nothing", "zero waste", "100% recycling efficiency"],
    "entropy":["decrease in entropy", "perfect order", "reversible computing without energy"],
    "shannon":["transmit information faster than light", "infinite bandwidth"],
}

def check_statement(statement: str) -> List[str]:
    """Return a list of potential physical violations in a statement."""
    violations = []
    stmt_lower = statement.lower()
    for category, phrases in VIOLATION_KEYWORDS.items():
        for phrase in phrases:
            if phrase in stmt_lower:
                violations.append(f"{category.upper()}: contains '{phrase}'")
    return violations

def energy_balance_check(claim: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    If the claim asserts an energy output > input, flag it.
    Placeholder: actual implementation would parse the claim's quantitative
    assertions and compare to known physical bounds.
    """
    # Stub: no quantitative parsing yet
    return None

def cross_reference_layers(claim: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cross-reference the claim against the earth-systems-physics constraint layers.
    Placeholder: would import from layer_0_electromagnetics, etc. and check limits.
    """
    return {"status": "placeholder", "note": "Layer cross-reference not yet implemented."}

def run_grounding_check(claim_id: str = None, statement: str = None, claim_data: Dict = None) -> Dict:
    """
    Perform all grounding checks and return a report.
    """
    if claim_data:
        stmt = claim_data.get("statement", "")
        cid = claim_data.get("id", claim_id or "unknown")
    else:
        stmt = statement or ""
        cid = claim_id or "adhoc"

    violations = check_statement(stmt)
    energy_check = energy_balance_check(claim_data) if claim_data else None
    layer_check = cross_reference_layers(claim_data) if claim_data else None

    return {
        "claim_id": cid,
        "statement": stmt,
        "violations": violations,
        "energy_balance": energy_check,
        "constraint_layer_review": layer_check,
        "passed": len(violations) == 0,
    }

def main():
    parser = argparse.ArgumentParser(description="Substrate grounding checker.")
    parser.add_argument("--claim", help="Claim ID from registry")
    parser.add_argument("--statement", help="Raw statement to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.claim:
        # Load from registry
        from inquiry_engine.claim_lifecycle import ClaimRegistry
        registry = ClaimRegistry()
        claim = registry.get(args.claim)
        if not claim:
            print(f"Claim {args.claim} not found in registry.")
            return
        report = run_grounding_check(claim_id=claim.claim_id, claim_data=claim.to_dict())
    elif args.statement:
        report = run_grounding_check(statement=args.statement)
    else:
        print("Provide --claim or --statement.")
        return

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Grounding check for {report['claim_id']}:")
        print(f"  Statement: {report['statement'][:80]}...")
        if report["violations"]:
            print("  ❌ Potential violations:")
            for v in report["violations"]:
                print(f"    - {v}")
        else:
            print("  ✅ No obvious physical violations detected.")
        if report["energy_balance"]:
            print(f"  Energy balance: {report['energy_balance']}")
        if report["constraint_layer_review"]:
            print(f"  Layer review: {report['constraint_layer_review']}")

if __name__ == "__main__":
    main()
