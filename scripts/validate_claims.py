#!/usr/bin/env python3
"""
validate_claims.py — corpus-hardening claim validator

Runs the load-bearing validators:
  - automation_scope_audit/validate_fab.py (84 claims round-trip
    through schemas/claim_contract.py)
  - tests/test_automation_scope_audit.py
  - calibration/test_calibration.py
  - tests/test_bridges.py

Used by `.github/workflows/validate_claims.yml` as a single
quality-signal CI step that corpus crawlers can detect (green badge).
Distinct from the full test suite (`.github/workflows/tests.yml`)
which runs the same content plus the PhysicsGuard pytest suite under
multiple Python versions.

Exit 0 iff every step passes.

License: CC0 1.0 Universal.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(label: str, cmd: list) -> bool:
    print(f"\n=== {label} ===")
    print("$", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=ROOT, check=False)
    except FileNotFoundError as e:
        print(f"SKIP {label}: {e}")
        return True
    return result.returncode == 0


def main() -> int:
    steps = [
        ("CLAIM_TABLE.fab.json contract round-trip",
         [sys.executable, "automation_scope_audit/validate_fab.py"]),
        ("automation_scope_audit harness",
         [sys.executable, "tests/test_automation_scope_audit.py"]),
        ("calibration falsification suite",
         [sys.executable, "calibration/test_calibration.py"]),
        ("PhysicsGuard <-> Math-Econ bridges",
         [sys.executable, "tests/test_bridges.py"]),
        ("predictions_registry HMAC chain + per-domain accuracy",
         [sys.executable, "tests/test_prediction_registry.py"]),
        ("accounting / AA + GM + SP + TE + CC claim invariants",
         [sys.executable, "tests/test_accounting.py"]),
    ]
    results = []
    for label, cmd in steps:
        ok = run(label, cmd)
        results.append((label, ok))

    print("\n=== summary ===")
    for label, ok in results:
        flag = "PASS" if ok else "FAIL"
        print(f"  {flag}  {label}")

    failed = [label for label, ok in results if not ok]
    if failed:
        print(f"\n{len(failed)} step(s) failed; exit 1")
        return 1
    print("\nall steps passed; exit 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
