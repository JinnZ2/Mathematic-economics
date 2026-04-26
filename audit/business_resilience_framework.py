"""
business_resilience_framework.py

Self-audit framework for individual businesses to measure
their own resilience, extraction ratio, and substrate health
honestly -- and to find a falsifiable transition pathway forward.

Sits between the municipal scoring layer and labor thermodynamics.
A business can run this on itself, see the actual math, and get
a phased transition path that satisfies all stakeholders without
requiring all-at-once disruption.

Five coupled diagnostics:

  1. Substrate health audit (the labor + knowledge + community base)
  2. Extraction ratio measurement (where value flows)
  3. Cascade vulnerability scan (single points of failure)
  4. Discretionary effort indicator (the leading signal of decay)
  5. Transition pathway generator (phased, falsifiable, costed)

License: CC0 1.0 Universal
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Optional metabolic-accounting bridge. metabolic_bridge always imports;
# whether it does anything at runtime is gated on
# metabolic_bridge._HAS_METABOLIC_ACCOUNTING. The metabolic side filters
# its verdict through its own money_signal/audit, so calling this gives
# us a band signal (GREEN/AMBER/RED/BLACK irreversibility) and
# regeneration_debt that the existing diagnostics don't surface.
try:
    from metabolic_bridge import metabolic_check
    _HAS_METABOLIC_BRIDGE = True
except Exception:
    _HAS_METABOLIC_BRIDGE = False


# -----------------------------------------------------------------------------
# BUSINESS STATE
# -----------------------------------------------------------------------------

@dataclass
class BusinessState:
    name: str

    # --- workforce substrate ---
    headcount: int
    avg_tenure_years: float
    pension_or_equivalent: bool
    health_coverage_quality: float        # 0..1
    apprenticeship_pipeline: bool
    voluntary_turnover_pct: float         # leading indicator
    safety_reports_per_employee: float    # higher = healthier reporting culture
    discretionary_effort_index: float     # 0..1

    # --- knowledge substrate ---
    documented_processes_pct: float       # 0..1
    cross_trained_pct: float              # 0..1
    knowledge_holders_within_5yr_retire: float  # 0..1 (risk fraction)
    succession_plan_coverage: float       # 0..1

    # --- community substrate ---
    local_supplier_pct: float             # 0..1
    local_payroll_pct: float              # 0..1
    profit_recirculated_local_pct: float  # 0..1
    community_contracts_honored_pct: float  # 0..1

    # --- extraction signals ---
    profit_extracted_to_holding_pct: float  # 0..1
    debt_loaded_for_extraction: bool
    quarterly_pressure_index: float       # 0..1 (1 = pure quarterly extraction)
    executive_to_median_pay_ratio: float

    # --- physical / operational ---
    single_supplier_dependencies: int     # count of SPOFs
    deferred_maintenance_pct: float       # 0..1
    energy_dependency: float              # 0..1
    regulatory_compliance_only: bool      # vs. exceeds compliance

    # --- financial reality ---
    cash_runway_months: float
    revenue_concentration_top_3_clients: float  # 0..1
    capex_reinvestment_pct: float         # 0..1 of profit


# -----------------------------------------------------------------------------
# DIAGNOSTIC 1: SUBSTRATE HEALTH
# -----------------------------------------------------------------------------

def substrate_health_audit(b: BusinessState) -> dict:
    workforce = (
        min(b.avg_tenure_years / 7.0, 1.0) * 0.20 +
        (0.15 if b.pension_or_equivalent else 0.0) +
        b.health_coverage_quality * 0.10 +
        (0.10 if b.apprenticeship_pipeline else 0.0) +
        max(0.0, 1.0 - b.voluntary_turnover_pct / 30.0) * 0.15 +
        min(b.safety_reports_per_employee / 2.0, 1.0) * 0.10 +
        b.discretionary_effort_index * 0.20
    )

    knowledge = (
        b.documented_processes_pct * 0.25 +
        b.cross_trained_pct * 0.25 +
        (1.0 - b.knowledge_holders_within_5yr_retire) * 0.25 +
        b.succession_plan_coverage * 0.25
    )

    community = (
        b.local_supplier_pct * 0.25 +
        b.local_payroll_pct * 0.25 +
        b.profit_recirculated_local_pct * 0.25 +
        b.community_contracts_honored_pct * 0.25
    )

    composite = (workforce * 0.45 + knowledge * 0.30 + community * 0.25)

    return {
        "workforce": round(workforce, 3),
        "knowledge": round(knowledge, 3),
        "community": round(community, 3),
        "composite": round(composite, 3),
        "rating": (
            "healthy"      if composite > 0.65 else
            "at_risk"      if composite > 0.40 else
            "degrading"    if composite > 0.20 else
            "collapsing"
        ),
    }


# -----------------------------------------------------------------------------
# DIAGNOSTIC 2: EXTRACTION RATIO
# -----------------------------------------------------------------------------

def extraction_ratio_measurement(b: BusinessState) -> dict:
    extraction = (
        b.profit_extracted_to_holding_pct * 0.35 +
        (0.20 if b.debt_loaded_for_extraction else 0.0) +
        b.quarterly_pressure_index * 0.25 +
        min(b.executive_to_median_pay_ratio / 100.0, 1.0) * 0.20
    )

    contribution = (
        b.capex_reinvestment_pct * 0.40 +
        b.local_payroll_pct * 0.20 +
        b.profit_recirculated_local_pct * 0.20 +
        b.community_contracts_honored_pct * 0.20
    )

    net = round(contribution - extraction, 3)
    return {
        "extraction_index": round(extraction, 3),
        "contribution_index": round(contribution, 3),
        "net_flow": net,
        "direction": (
            "value_returning_to_substrate" if net > 0.15 else
            "balanced"                     if net > -0.15 else
            "value_leaving_substrate"
        ),
    }


# -----------------------------------------------------------------------------
# DIAGNOSTIC 3: CASCADE VULNERABILITY
# -----------------------------------------------------------------------------

def cascade_vulnerability_scan(b: BusinessState) -> dict:
    spofs = []
    if b.single_supplier_dependencies > 0:
        spofs.append({
            "type": "supplier",
            "count": b.single_supplier_dependencies,
            "weight": min(b.single_supplier_dependencies * 0.10, 0.40),
        })
    if b.knowledge_holders_within_5yr_retire > 0.30:
        spofs.append({
            "type": "knowledge_loss",
            "fraction": b.knowledge_holders_within_5yr_retire,
            "weight": b.knowledge_holders_within_5yr_retire * 0.50,
        })
    if b.deferred_maintenance_pct > 0.20:
        spofs.append({
            "type": "deferred_maintenance",
            "fraction": b.deferred_maintenance_pct,
            "weight": b.deferred_maintenance_pct * 0.40,
        })
    if b.revenue_concentration_top_3_clients > 0.50:
        spofs.append({
            "type": "revenue_concentration",
            "fraction": b.revenue_concentration_top_3_clients,
            "weight": b.revenue_concentration_top_3_clients * 0.45,
        })
    if b.energy_dependency > 0.70:
        spofs.append({
            "type": "energy_dependency",
            "fraction": b.energy_dependency,
            "weight": b.energy_dependency * 0.30,
        })
    if b.cash_runway_months < 3:
        spofs.append({
            "type": "cash_fragility",
            "months": b.cash_runway_months,
            "weight": 0.40,
        })

    total_weight = sum(s["weight"] for s in spofs)
    return {
        "single_points_of_failure": spofs,
        "vulnerability_index": round(min(total_weight, 1.0), 3),
        "rating": (
            "robust"     if total_weight < 0.30 else
            "fragile"    if total_weight < 0.60 else
            "critical"   if total_weight < 0.90 else
            "imminent_failure_risk"
        ),
    }


# -----------------------------------------------------------------------------
# DIAGNOSTIC 4: DISCRETIONARY EFFORT (LEADING INDICATOR)
# -----------------------------------------------------------------------------

def discretionary_effort_signal(b: BusinessState) -> dict:
    """
    Discretionary effort is the EARLIEST signal of substrate decay.
    Workers withdraw effort before they withdraw labor.
    Falling discretionary effort = 6-18 months ahead of turnover spike.
    """
    signals = {
        "current_effort": b.discretionary_effort_index,
        "safety_reporting_health": min(b.safety_reports_per_employee / 2.0, 1.0),
        "voluntary_turnover_pressure": b.voluntary_turnover_pct / 30.0,
    }

    # composite leading-indicator score
    leading = (
        b.discretionary_effort_index * 0.5 +
        signals["safety_reporting_health"] * 0.3 +
        max(0.0, 1.0 - signals["voluntary_turnover_pressure"]) * 0.2
    )

    return {
        "signals": {k: round(v, 3) for k, v in signals.items()},
        "leading_indicator": round(leading, 3),
        "forecast": (
            "stable_or_improving" if leading > 0.65 else
            "early_decay_warning" if leading > 0.45 else
            "decay_in_progress"   if leading > 0.25 else
            "advanced_decay_imminent_failure"
        ),
    }


# -----------------------------------------------------------------------------
# DIAGNOSTIC 5: TRANSITION PATHWAY
# -----------------------------------------------------------------------------

def transition_pathway(b: BusinessState) -> dict:
    """
    Builds a phased, falsifiable transition path from current state
    toward substrate-contributor status. Each phase has measurable
    targets and estimated payback windows.
    """
    sub = substrate_health_audit(b)
    ext = extraction_ratio_measurement(b)
    cas = cascade_vulnerability_scan(b)
    eff = discretionary_effort_signal(b)

    phases = []

    # Phase 1: Stop the bleeding (0-6 months)
    p1 = {"phase": 1, "window_months": 6, "actions": [], "cost_signal": "low"}
    if eff["leading_indicator"] < 0.50:
        p1["actions"].append("Immediate worker safety/voice channel -- Lean Six Sigma "
                             "style empowerment without retaliation. Restores discretionary effort.")
    if cas["vulnerability_index"] > 0.60:
        p1["actions"].append("Identify top 3 SPOFs; allocate emergency redundancy budget.")
    if b.deferred_maintenance_pct > 0.30:
        p1["actions"].append("Catch up on critical deferred maintenance before cascade triggers.")
    if not p1["actions"]:
        p1["actions"].append("Maintain current floor; document baseline for transition tracking.")
    phases.append(p1)

    # Phase 2: Substrate rebuild (6-24 months)
    p2 = {"phase": 2, "window_months": 24, "actions": [], "cost_signal": "medium"}
    if not b.pension_or_equivalent:
        p2["actions"].append("Worker-controlled retirement vehicle, vested. Long-tenure incentive structure.")
    if sub["knowledge"] < 0.50:
        p2["actions"].append("Cross-training program + process documentation. Apprenticeship pipeline if absent.")
    if b.local_supplier_pct < 0.30:
        p2["actions"].append("Local supplier development program -- phased substitution where viable.")
    if b.capex_reinvestment_pct < 0.30:
        p2["actions"].append("Increase reinvestment ratio; reduce dividend extraction.")
    phases.append(p2)

    # Phase 3: Structural realignment (24-60 months)
    p3 = {"phase": 3, "window_months": 60, "actions": [], "cost_signal": "high_but_payback_positive"}
    if ext["extraction_index"] > 0.40:
        p3["actions"].append("Restructure ownership/financing to remove debt-loaded extraction. "
                             "Consider employee ownership or stewardship trust.")
    if b.executive_to_median_pay_ratio > 50:
        p3["actions"].append("Compensation realignment -- ratio target under 25:1, "
                             "ties leadership to substrate health.")
    if b.quarterly_pressure_index > 0.5:
        p3["actions"].append("Renegotiate investor expectations or transition off "
                             "quarterly-extraction capital. Long-cycle financing alignment.")
    phases.append(p3)

    # Expected outcome
    estimated_resilience_gain = round(
        (1.0 - sub["composite"]) * 0.6 +
        max(0.0, -ext["net_flow"]) * 0.5 +
        cas["vulnerability_index"] * 0.4,
    3)

    return {
        "current_state_summary": {
            "substrate": sub["rating"],
            "extraction": ext["direction"],
            "cascade_risk": cas["rating"],
            "effort_forecast": eff["forecast"],
        },
        "phases": phases,
        "estimated_resilience_gain": estimated_resilience_gain,
        "falsifiable_targets": {
            "phase_1": "discretionary_effort_index > 0.55, top_spofs_redundant",
            "phase_2": "substrate_composite > 0.55, local_supplier_pct > 0.30",
            "phase_3": "extraction_index < 0.30, exec_pay_ratio < 25",
        },
    }


# -----------------------------------------------------------------------------
# OPTIONAL: METABOLIC VERDICT (defensive bridge to metabolic-accounting)
# -----------------------------------------------------------------------------

def check_metabolic_health(
    b: BusinessState,
    revenue: float = 100.0,
    stress: Optional[Dict[Tuple[str, str], float]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Optional metabolic-accounting verdict for the business.

    Mirrors the equation_bridge mapping, with operating cost and
    regeneration_paid derived from BusinessState observables:

      extraction_index from extraction_ratio_measurement(b)
        higher extraction -> less paid downward to substrate
      operating_cost = revenue * (1 - extraction_index)
      regeneration_paid = operating_cost
                          * capex_reinvestment_pct
                          * (1 - deferred_maintenance_pct)
        what's actually deployed for substrate regeneration after
        the deferred-maintenance shortfall

    The metabolic side filters this through its own money_signal/audit
    before issuing a verdict, so the returned band (GREEN/AMBER/RED/BLACK)
    reflects both physical-substrate state AND money-signal coherence.
    BLACK is reserved for IRREVERSIBILITY -- distinct from "very RED" --
    which the existing cascade_vulnerability_scan does not capture.

    Returns None when metabolic-accounting is not importable at the
    bridge level. Absolute revenue is not meaningful (the band signal and
    basin trajectory are); revenue=100.0 is the conventional default.
    """
    if not _HAS_METABOLIC_BRIDGE:
        return None
    ext = extraction_ratio_measurement(b)
    extraction_index = ext["extraction_index"]
    operating_cost = revenue * (1.0 - min(1.0, max(0.0, extraction_index)))
    regeneration_paid = (
        operating_cost
        * b.capex_reinvestment_pct
        * (1.0 - b.deferred_maintenance_pct)
    )
    return metabolic_check(
        revenue=revenue,
        direct_operating_cost=operating_cost,
        regeneration_paid=regeneration_paid,
        stress=stress,
    )


# -----------------------------------------------------------------------------
# UNIFIED REPORT
# -----------------------------------------------------------------------------

def full_audit(b: BusinessState) -> dict:
    report = {
        "name": b.name,
        "substrate_health": substrate_health_audit(b),
        "extraction_ratio": extraction_ratio_measurement(b),
        "cascade_vulnerability": cascade_vulnerability_scan(b),
        "discretionary_effort": discretionary_effort_signal(b),
        "transition_pathway": transition_pathway(b),
    }
    metabolic = check_metabolic_health(b)
    if metabolic is not None:
        report["metabolic_verdict"] = metabolic
    return report


# -----------------------------------------------------------------------------
# REFERENCE PROFILES
# -----------------------------------------------------------------------------

def reference_profiles() -> List[BusinessState]:
    return [
        BusinessState(
            name="Mid-size manufacturer (legacy committed model)",
            headcount=420, avg_tenure_years=11.0, pension_or_equivalent=True,
            health_coverage_quality=0.80, apprenticeship_pipeline=True,
            voluntary_turnover_pct=8.0, safety_reports_per_employee=1.8,
            discretionary_effort_index=0.78,
            documented_processes_pct=0.65, cross_trained_pct=0.55,
            knowledge_holders_within_5yr_retire=0.25,
            succession_plan_coverage=0.50,
            local_supplier_pct=0.45, local_payroll_pct=0.85,
            profit_recirculated_local_pct=0.55,
            community_contracts_honored_pct=0.90,
            profit_extracted_to_holding_pct=0.20,
            debt_loaded_for_extraction=False,
            quarterly_pressure_index=0.30,
            executive_to_median_pay_ratio=18,
            single_supplier_dependencies=2,
            deferred_maintenance_pct=0.10,
            energy_dependency=0.60,
            regulatory_compliance_only=False,
            cash_runway_months=8,
            revenue_concentration_top_3_clients=0.30,
            capex_reinvestment_pct=0.40,
        ),
        BusinessState(
            name="PE-acquired roll-up under quarterly extraction",
            headcount=1100, avg_tenure_years=1.4, pension_or_equivalent=False,
            health_coverage_quality=0.30, apprenticeship_pipeline=False,
            voluntary_turnover_pct=72.0, safety_reports_per_employee=0.2,
            discretionary_effort_index=0.20,
            documented_processes_pct=0.30, cross_trained_pct=0.15,
            knowledge_holders_within_5yr_retire=0.55,
            succession_plan_coverage=0.10,
            local_supplier_pct=0.05, local_payroll_pct=0.40,
            profit_recirculated_local_pct=0.05,
            community_contracts_honored_pct=0.40,
            profit_extracted_to_holding_pct=0.92,
            debt_loaded_for_extraction=True,
            quarterly_pressure_index=0.95,
            executive_to_median_pay_ratio=180,
            single_supplier_dependencies=6,
            deferred_maintenance_pct=0.55,
            energy_dependency=0.85,
            regulatory_compliance_only=True,
            cash_runway_months=2,
            revenue_concentration_top_3_clients=0.65,
            capex_reinvestment_pct=0.05,
        ),
    ]


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    for b in reference_profiles():
        r = full_audit(b)
        print(f"\n{'='*72}")
        print(f"  {r['name']}")
        print(f"{'='*72}")

        s = r["substrate_health"]
        print(f"  SUBSTRATE HEALTH:    composite={s['composite']:.3f}  rating={s['rating']}")

        e = r["extraction_ratio"]
        print(f"  EXTRACTION RATIO:    net_flow={e['net_flow']:+.3f}  direction={e['direction']}")

        c = r["cascade_vulnerability"]
        print(f"  CASCADE RISK:        index={c['vulnerability_index']:.3f}  rating={c['rating']}")

        d = r["discretionary_effort"]
        print(f"  DISCRETIONARY EFFORT: lead={d['leading_indicator']:.3f}  forecast={d['forecast']}")

        t = r["transition_pathway"]
        print(f"  TRANSITION PATHWAY (estimated resilience gain: {t['estimated_resilience_gain']}):")
        for p in t["phases"]:
            print(f"    Phase {p['phase']} ({p['window_months']} months, cost={p['cost_signal']}):")
            for a in p["actions"]:
                print(f"       - {a}")
        print(f"  FALSIFIABLE TARGETS:")
        for k, v in t["falsifiable_targets"].items():
            print(f"    {k}: {v}")

        m = r.get("metabolic_verdict")
        if m is not None:
            print(f"  METABOLIC VERDICT (via metabolic-accounting bridge):")
            print(f"    sustainable_yield_signal: {m['sustainable_yield_signal']}  "
                  f"(BLACK = irreversibility, distinct from very RED)")
            print(f"    regeneration_debt:        {m['regeneration_debt']}")
            print(f"    metabolic_profit:         {m['metabolic_profit']}")
            print(f"    profit_gap:               {m['profit_gap']}")
            if m.get("irreversible_metrics"):
                print(f"    irreversible_metrics:     {m['irreversible_metrics']}")
        else:
            print(f"  METABOLIC VERDICT: not available "
                  f"(metabolic-accounting checkout not found; bridge inactive)")
