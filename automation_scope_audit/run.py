"""
run.py  —  automation_scope_audit entrypoint

Runs the works-case and fails-case examples, summarizes which falsifiable
claims registered as threshold-met (i.e. the claim survives — would require
a falsifier to refute), and emits a compact verdict table.

Usage:
    python automation_scope_audit/run.py
    python automation_scope_audit/run.py --json     # raw JSON output

License: CC0-1.0
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation_scope_audit.examples import (
    kodiak_atlas_permian,
    dispersed_wellsite,
)


CLAIM_ORDER = ["C000"] + [f"C{n:03d}" for n in range(1, 33)]

# Per-claim threshold polarity. True semantics differ:
#  C001 / C004: threshold_met = deployment satisfies the claim's prescription
#               (low variance / lease outlives equipment). Concern is FALSE.
#  others:      threshold_met = the structural concern registers against
#               the deployment. Concern is TRUE.
CONCERN_INVERTED = {"C001", "C004"}


def _threshold_met(verdict: dict) -> bool | None:
    if "threshold_met" in verdict:
        return bool(verdict["threshold_met"])
    if "scope_collapse_detected" in verdict:
        return bool(verdict["scope_collapse_detected"])
    return None


def _concern_registers(cid: str, threshold_met: bool | None) -> bool | None:
    if threshold_met is None:
        return None
    return (not threshold_met) if cid in CONCERN_INVERTED else threshold_met


def summarize(report: dict) -> dict:
    rows = []
    for cid in CLAIM_ORDER:
        v = report.get(cid)
        if v is None:
            rows.append({"claim": cid, "threshold_met": None,
                         "concern_registers": None,
                         "notes": "not evaluated"})
            continue
        tm = _threshold_met(v)
        rows.append({
            "claim":             cid,
            "threshold_met":     tm,
            "concern_registers": _concern_registers(cid, tm),
            "falsifier":         v.get("falsifier"),
        })
    return {"scenario": report.get("scenario"), "rows": rows}


def print_table(summary: dict) -> None:
    print(f"\n=== {summary['scenario']} ===")
    print(f"{'claim':<6}  {'concern':<10}  falsifier")
    print("-" * 78)
    for r in summary["rows"]:
        concern = ("YES" if r["concern_registers"] else
                   "no"  if r["concern_registers"] is False else "—")
        falsifier = r.get("falsifier") or ""
        print(f"{r['claim']:<6}  {concern:<10}  {falsifier}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true",
                    help="emit raw JSON report instead of summary table")
    ap.add_argument("--scenario", choices=["works", "fails", "both"],
                    default="both")
    args = ap.parse_args()

    reports = []
    if args.scenario in ("works", "both"):
        reports.append(kodiak_atlas_permian.run())
    if args.scenario in ("fails", "both"):
        reports.append(dispersed_wellsite.run())

    if args.json:
        print(json.dumps(reports, indent=2, default=str))
        return 0

    for r in reports:
        print_table(summarize(r))
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
