#!/usr/bin/env python3
"""
auto_falsify.py – Automatically test claims whose test procedure is a runnable function.
CC0. Stdlib only.

Expected claim structure includes a 'test_procedure' field with:
  "test_procedure": {
      "module": "modules.scope_geometry",
      "function": "check_jaccard",
      "args": {}
  }

Usage:
  python inquiry_engine/auto_falsify.py --claim I001
  python inquiry_engine/auto_falsify.py --all
"""

import argparse
import importlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Adjust path so we can import from sibling inquiry_engine and automation_scope_audit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inquiry_engine.claim_lifecycle import ClaimLifecycle, ClaimRegistry, ClaimState

REGISTRY_PATH = "claims_registry.json"

def run_test_procedure(claim: ClaimLifecycle) -> Dict[str, Any]:
    """
    Execute the claim's test_procedure and return a result dict.
    """
    test = claim.test_procedure
    if not test:
        return {"result": "skipped", "reason": "No test procedure defined."}

    module_name = test.get("module")
    function_name = test.get("function")
    args = test.get("args", {})

    if not module_name or not function_name:
        return {"result": "skipped", "reason": "Incomplete test procedure."}

    try:
        mod = importlib.import_module(module_name)
        func = getattr(mod, function_name)
        result = func(**args)
        # Assume function returns a dict with 'passed' boolean or 'threshold_met'
        if isinstance(result, dict):
            passed = not result.get("threshold_met", False)
            return {
                "type": "auto_test",
                "result": "passed" if passed else "failed",
                "source": f"{module_name}.{function_name}",
                "details": result,
            }
        elif isinstance(result, bool):
            return {
                "type": "auto_test",
                "result": "passed" if result else "failed",
                "source": f"{module_name}.{function_name}",
            }
        else:
            return {
                "type": "auto_test",
                "result": "inconclusive",
                "source": f"{module_name}.{function_name}",
                "reason": "Unexpected return type.",
            }
    except Exception as e:
        return {
            "type": "auto_test",
            "result": "error",
            "source": f"{module_name}.{function_name}",
            "error": str(e),
        }

def process_claim(claim_id: str, registry: ClaimRegistry) -> bool:
    claim = registry.get(claim_id)
    if not claim:
        print(f"Claim {claim_id} not found.")
        return False
    print(f"Testing {claim_id}: {claim.statement[:60]}...")
    evidence = run_test_procedure(claim)
    if evidence["result"] == "passed":
        claim.survive_round(evidence)
        print(f"  PASSED (round {claim.rounds_survived})")
    elif evidence["result"] == "failed":
        claim.falsify(evidence)
        print(f"  FALSIFIED")
    else:
        claim.add_evidence(evidence)
        print(f"  {evidence['result'].upper()}: {evidence.get('reason', evidence.get('error',''))}")
    registry.save()
    return evidence["result"] == "passed"

def main():
    parser = argparse.ArgumentParser(description="Automated claim testing harness.")
    parser.add_argument("--claim", help="Test a specific claim ID")
    parser.add_argument("--all", action="store_true", help="Test all active claims")
    args = parser.parse_args()

    registry = ClaimRegistry(REGISTRY_PATH)

    if args.claim:
        process_claim(args.claim, registry)
    elif args.all:
        active = registry.get_active()
        print(f"Testing {len(active)} active claims...")
        for claim in active:
            process_claim(claim.claim_id, registry)
            print()
    else:
        # List claims available for auto-test
        active = registry.get_active()
        testable = [c for c in active if c.test_procedure]
        print(f"Testable claims ({len(testable)}):")
        for c in testable:
            print(f"  {c.claim_id}: {c.statement[:60]}...")
        print("\nUse --claim <id> to test one, or --all to test all.")

if __name__ == "__main__":
    main()
