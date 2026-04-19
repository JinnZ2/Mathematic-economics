"""
self_audit.py — run the pipeline on itself

The calibration-audit repo must pass its own diagnostic, or the framework
is ceremonial skill (Q3 failure: practiced for observation, not use).

TWO RUNS:
1. OPTIMISTIC: inputs as the authors might describe their own work.
2. HONEST:     inputs including the fragility points the authors see.

The delta between the two runs is the propaganda-of-skill signal.
"""

import json
from pipeline import run_unified_audit

# ─── RUN 1: OPTIMISTIC (author self-description) ─────────────────────────────

OPTIMISTIC = {
"system_id": "calibration-audit (optimistic self-description)",
"cliff_threshold": 10.0,
"feedback_events": [
{"type": "impersonal", "count": 11},
{"type": "personal", "count": 0},
],
"decisions": [
{"decision_maker": "user_running_audit", "consequence_hops": 0},
],
"skills_observed": [
{"skill": "scoring", "requires_witness": False},
{"skill": "falsifier_checking", "requires_witness": False},
{"skill": "report_generation", "requires_witness": False},
],
"memorialized_skills": [
{"skill": "falsifiability_promise", "praise_volume": 50,
"estimated_prevalence": 1.0},
],
"friction_events": [
{"name": "test_suite", "domain": "institutional",
"initial_load": 0.7, "removed": False,
"years_since_removed": 0.0},
{"name": "falsifier_claims", "domain": "cognitive",
"initial_load": 0.8, "removed": False,
"years_since_removed": 0.0},
{"name": "stdlib_only_constraint", "domain": "physical",
"initial_load": 0.6, "removed": False,
"years_since_removed": 0.0},
],
"skill_log": [
{"skill": "run_audit", "timestamp": "2026-04-16",
"context": "silent", "consequence_real": True},
{"skill": "run_tests", "timestamp": "2026-04-16",
"context": "silent", "consequence_real": True},
],
}

# ─── RUN 2: HONEST (actual fragility points) ─────────────────────────────────

HONEST = {
"system_id": "calibration-audit (honest self-description)",
"cliff_threshold": 10.0,
# Q1: feedback comes from tests (impersonal) but also from how results
# "feel" to the author. Real ratio is not 11:0.
"feedback_events": [
    {"type": "impersonal", "count": 11},
    {"type": "personal", "count": 4},
],

# Q2: when used on OTHERS (orgs, teams), consequence is sheltered —
# the auditor's output reaches people who had no voice in calibration.
"decisions": [
    {"decision_maker": "self_audit_user", "consequence_hops": 0},
    {"decision_maker": "org_auditor", "consequence_hops": 2},
    {"decision_maker": "consultant_deploying", "consequence_hops": 3},
],

# Q3: the framework IS witness-dependent when used as signaling
# rather than for private navigation.
"skills_observed": [
    {"skill": "scoring", "requires_witness": False},
    {"skill": "falsifier_checking", "requires_witness": False},
    {"skill": "report_generation", "requires_witness": False},
    {"skill": "sharing_the_json_output", "requires_witness": True},
    {"skill": "citing_framework_in_argument", "requires_witness": True},
],

# Q4: the framework memorializes concepts near-extinct in practice.
# Stated purpose, but also a high-memorialization signal.
"memorialized_skills": [
    {"skill": "falsifiability_discipline", "praise_volume": 200,
     "estimated_prevalence": 0.15},
    {"skill": "friction_preservation_in_orgs", "praise_volume": 150,
     "estimated_prevalence": 0.10},
    {"skill": "consequence_alignment", "praise_volume": 300,
     "estimated_prevalence": 0.20},
],

# Q5: the framework removes some friction from its user:
# mathematical verdicts replace the discomfort of sitting with ambiguity.
"friction_events": [
    {"name": "test_suite", "domain": "institutional",
     "initial_load": 0.7, "removed": False,
     "years_since_removed": 0.0},
    {"name": "falsifier_claims", "domain": "cognitive",
     "initial_load": 0.8, "removed": False,
     "years_since_removed": 0.0},
    {"name": "stdlib_only_constraint", "domain": "physical",
     "initial_load": 0.6, "removed": False,
     "years_since_removed": 0.0},
    {"name": "sitting_with_unscored_ambiguity", "domain": "cognitive",
     "initial_load": 0.5, "removed": True,
     "years_since_removed": 0.0},
    {"name": "subjective_judgment_calibration", "domain": "cognitive",
     "initial_load": 0.4, "removed": True,
     "years_since_removed": 0.0},
],

"skill_log": [
    {"skill": "run_audit", "timestamp": "2026-04-16",
     "context": "silent", "consequence_real": True},
    {"skill": "run_tests", "timestamp": "2026-04-16",
     "context": "silent", "consequence_real": True},
    {"skill": "falsifier_check", "timestamp": "2026-04-16",
     "context": "silent", "consequence_real": True},
    {"skill": "cite_in_discussion", "timestamp": "2026-04-16",
     "context": "recorded", "consequence_real": False},
    {"skill": "share_json_output", "timestamp": "2026-04-16",
     "context": "witnessed", "consequence_real": False},
],
}

def _print_report(result, label):
    print("=" * 70)
    print(f"  {label}")
    print("=" * 70)
    print(f"  Unified band:  {result['unified_band']}")
    print(f"  Unified score: {result['unified_score']:.3f}")
    print()
    print("  Per-module:")
    for mod, rep in result["module_reports"].items():
        print(f"    {mod:20s} {rep['aggregate_score']:.3f}  "
f"[{rep['aggregate_band']}]")
    print()
    if result["all_failing_dimensions"]:
        print("  Failing dimensions:")
        for d in result["all_failing_dimensions"]:
            print(f"    - {d}")
    else:
        print("  No failing dimensions.")
        print()

if __name__ == "__main__":
    opt = run_unified_audit(OPTIMISTIC)
    hon = run_unified_audit(HONEST)
    _print_report(opt, "RUN 1: OPTIMISTIC SELF-DESCRIPTION")
    _print_report(hon, "RUN 2: HONEST SELF-DESCRIPTION")

    delta = hon["unified_score"] - opt["unified_score"]
    print("=" * 70)
    print("  DELTA (propaganda-of-skill signal)")
    print("=" * 70)
    print(f"  Score delta: {delta:+.3f}")
    print()
    if delta > 0.15:
        print("  READING: Gap exceeds 0.15. This is the signal the framework")
        print("  is designed to catch. The framework is partially ceremonial")
        print("  when used as self-description. It calibrates best when used")
        print("  on OTHER systems by operators with skin in the game.")
elif delta > 0.05:
    print("  READING: Moderate gap. Framework is mostly honest but has")
    print("  soft spots.")
else:
    print("  READING: No significant gap. Either well-calibrated OR the")
    print("  honest input was still self-flattering.")
print()

with open("self_audit_optimistic.json", "w") as f:
    json.dump(opt, f, indent=2)
with open("self_audit_honest.json", "w") as f:
    json.dump(hon, f, indent=2)
print("  Reports saved: self_audit_optimistic.json, self_audit_honest.json")
