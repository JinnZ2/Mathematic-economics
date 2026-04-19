"""
PhysicsGuard — Physics-grounded logic verification
Detects corrupted premises via conservation law checking.
CC0 — github.com/JinnZ2/physicsguard
"""

import json
import sys

from core.conservation_checker import check_conservation
from core.constraint_mapper import map_to_constraints
from core.flag_engine import score_and_flag
from core.premise_parser import parse_premise


def check(premise: str) -> dict:
    """
    Check a single premise against physical conservation laws.

    Returns a verdict dict with:
        verdict, score, flags, reason, violations,
        applicable_laws, confidence, audit
    """
    parsed = parse_premise(premise)
    constraints = map_to_constraints(parsed)
    results = check_conservation(constraints)
    return score_and_flag(results, parsed, constraints)


def check_batch(premises: list) -> list:
    """Check multiple premises. Returns list of verdict dicts."""
    return [check(p) for p in premises]


# Keep backward compatibility
run = check


def _print_verdict(v):
    """Pretty-print a verdict to stdout."""
    print("\n[PhysicsGuard]")
    print(f"Verdict       : {v['verdict']}")
    print(f"Score         : {v['score']:.3f}")
    print(f"Confidence    : {v['confidence']:.0%}")
    print(f"Flags         : {v['flags']}")
    print(f"Reason        : {v['reason']}")

    if v.get("violations"):
        print("\nViolations:")
        for viol in v["violations"]:
            print(f"  [{viol['law']}] severity={viol['severity']:.2f}")
            print(f"    {viol['description']}")
            print(f"    Fix: {viol['fix_hint']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="PhysicsGuard — physics-grounded premise verification",
    )
    parser.add_argument("premise", nargs="*", help="Premise to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--batch", type=str, metavar="FILE",
        help="Check premises from file (one per line)",
    )
    parser.add_argument(
        "--pipe", action="store_true",
        help="Read premises from stdin (one per line)",
    )
    args = parser.parse_args()

    # Batch mode: read from file
    if args.batch:
        with open(args.batch) as f:
            premises = [line.strip() for line in f if line.strip()]
        results = check_batch(premises)
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            for v in results:
                _print_verdict(v)
        return

    # Pipe mode: read from stdin
    if args.pipe:
        premises = [line.strip() for line in sys.stdin if line.strip()]
        results = check_batch(premises)
        if args.json:
            for v in results:
                print(json.dumps(v, default=str))
        else:
            for v in results:
                _print_verdict(v)
        return

    # Single premise from args or interactive
    if args.premise:
        premise = " ".join(args.premise)
    else:
        premise = input("Premise: ")

    v = check(premise)
    if args.json:
        print(json.dumps(v, indent=2, default=str))
    else:
        _print_verdict(v)


if __name__ == "__main__":
    main()
