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
from automation_scope_audit import correlation
from automation_scope_audit.modules import scope_gate

try:
    from epistemic_ledger import AuditLedger
    _HAS_LEDGER = True
except Exception:
    AuditLedger = None  # type: ignore[assignment]
    _HAS_LEDGER = False


# Per-scenario deployment spec used by the scope gate. Each example is
# expected to publish a `DEPLOYMENT_SPEC` dict declaring the 7 required
# scope fields. The spec lives in the example module; we default to a
# blank dict that fails the gate, which is the correct fail-safe
# behavior for unannotated examples.
SCENARIO_SPECS: dict = {
    "kodiak_atlas_permian": getattr(
        kodiak_atlas_permian, "DEPLOYMENT_SPEC", {}),
    "dispersed_wellsite": getattr(
        dispersed_wellsite, "DEPLOYMENT_SPEC", {}),
}


CLAIM_ORDER = ["C000"] + [f"C{n:03d}" for n in range(1, 59)]

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


def _record_to_ledger(report: dict, ledger_path: str | None = None) -> int:
    """Append every verdict in `report` to the epistemic ledger.

    Returns the number of entries written. Silent no-op when the ledger
    module is unimportable (e.g. metrological_bounds.py missing).
    """
    if not _HAS_LEDGER or AuditLedger is None:
        return 0
    ledger = AuditLedger(path=ledger_path)
    scenario = report.get("scenario", "")
    written = 0
    for cid in CLAIM_ORDER:
        v = report.get(cid)
        if v is None:
            continue
        # The verdict dict itself is the input/output payload that
        # downstream readers care about reconstructing.
        ledger.append(claim_id=cid, verdict=v, inputs={"scenario": scenario},
                       scenario=scenario)
        written += 1
    return written


def _gate_then_run(scenario_key: str, runner, allow_missing_scope: bool
                   ) -> dict | None:
    """Run scope-gate first; if admitted (or override), execute the audit.

    Returns the audit report dict, OR a MISSING_SCOPE report stub if the
    spec doesn't pass and `--allow-missing-scope` was not set.
    """
    spec = SCENARIO_SPECS.get(scenario_key) or {}
    gate = scope_gate.scope_gate_verdict(spec)
    if not gate["admissible"] and not allow_missing_scope:
        print(f"\n=== {scenario_key}: {gate['report']} ===")
        for field in gate["missing"]:
            print(f"  missing scope field: {field}")
        print("audit skipped. Re-run with --allow-missing-scope to override "
              "(legacy examples).")
        return None
    report = runner()
    # Replace C000 verdict with the spec-level gate verdict so the table
    # reflects deployment-spec admissibility, not just pitch-text scope.
    report["C000"] = gate
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true",
                    help="emit raw JSON report instead of summary table")
    ap.add_argument("--scenario", choices=["works", "fails", "both"],
                    default="both")
    ap.add_argument("--no-ledger", action="store_true",
                    help="skip appending verdicts to epistemic_ledger.jsonl")
    ap.add_argument("--ledger-path", default=None,
                    help="override path for the ledger file (default: repo root)")
    ap.add_argument("--allow-missing-scope", action="store_true",
                    help="run audit even if scope_gate would block it "
                         "(legacy / un-annotated example specs)")
    ap.add_argument("--clusters", action="store_true",
                    help="also print cross-claim cluster report")
    args = ap.parse_args()

    reports = []
    if args.scenario in ("works", "both"):
        r = _gate_then_run("kodiak_atlas_permian",
                            kodiak_atlas_permian.run,
                            args.allow_missing_scope)
        if r is not None:
            reports.append(r)
    if args.scenario in ("fails", "both"):
        r = _gate_then_run("dispersed_wellsite",
                            dispersed_wellsite.run,
                            args.allow_missing_scope)
        if r is not None:
            reports.append(r)

    if not args.no_ledger:
        total = sum(_record_to_ledger(r, args.ledger_path) for r in reports)
        if not _HAS_LEDGER:
            print("(ledger module unavailable; skipping persistence)")
        elif not args.json:
            print(f"(ledger: appended {total} verdict entries)")

    if args.json:
        print(json.dumps(reports, indent=2, default=str))
        return 0

    for r in reports:
        print_table(summarize(r))
    if args.clusters:
        for r in reports:
            correlation.print_clusters(correlation.detect_clusters(r))
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
