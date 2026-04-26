"""
money_semantic_audit.py

Reality check on how money is being defined, used, by whom, and with
what structural results. Complements the numerical diagnostics in
business_resilience_framework by naming the SEMANTIC framing that the
firm's behavior reveals -- a dollar can be functioning as an extraction
token, a leverage instrument, an accounting fiction, an exchange
medium, productive substrate capital, or a pure investor signal.
The same accounting line item carries different physical consequences
depending on which framing is active.

Connects to the project's broader semantic-decontamination thesis
(AI/semantic_decontamination.py): economic terminology obscures
structural reality; this module exposes the structural reality
underneath the term "money" for a given firm.

Closed set of six framings (each falsifiable from BusinessState
observables):

  extraction_token  - money as upward-claim accumulator
  debt_lever        - money as leverage instrument
  accounting_fiction - money as legal-arbitrage / signal-decoupled book entry
  exchange_medium   - textbook transactional function
  substrate_capital - money as future-production base
  quarterly_signal  - money as investor signal, decoupled from substrate

A firm typically exhibits 2-3 framings simultaneously; the highest-
scored is the primary. When the metabolic and money_signal bridges
are active, their outputs reinforce or contradict the BusinessState
heuristics and are surfaced under structural_consequences.

License: CC0 1.0 Universal
"""

from typing import Any, Dict, List, Optional, Tuple

from business_resilience_framework import (
    BusinessState,
    cascade_vulnerability_scan,
    check_metabolic_health,
    extraction_ratio_measurement,
    reference_profiles,
    substrate_health_audit,
)

# Optional money_signal bridge (system-level baseline, not business-specific)
try:
    from money_signal_bridge import money_signal_metrics
    _HAS_MONEY_SIGNAL_BRIDGE = True
except Exception:
    _HAS_MONEY_SIGNAL_BRIDGE = False


# -----------------------------------------------------------------------------
# FRAMING DETECTION
# -----------------------------------------------------------------------------

def _score_framings(b: BusinessState) -> List[Dict[str, Any]]:
    """
    Score each candidate framing 0..1 against observable BusinessState
    signals. Multiple framings can score high simultaneously -- they
    are not mutually exclusive (extraction_token and debt_lever often
    co-occur). Each evidence string is a falsifiable claim; flipping
    the underlying observable would flip the score component.
    """
    framings = []

    # ---- extraction_token ----
    score = 0.0
    evidence = []
    if b.profit_extracted_to_holding_pct > 0.5:
        score += 0.4
        evidence.append(f"profit_extracted_to_holding_pct={b.profit_extracted_to_holding_pct}")
    if b.executive_to_median_pay_ratio > 50:
        score += 0.3
        evidence.append(f"executive_to_median_pay_ratio={b.executive_to_median_pay_ratio}")
    if b.profit_recirculated_local_pct < 0.20:
        score += 0.3
        evidence.append(f"profit_recirculated_local_pct={b.profit_recirculated_local_pct}")
    framings.append({
        "framing": "extraction_token",
        "score": round(min(1.0, score), 3),
        "evidence": evidence,
    })

    # ---- debt_lever ----
    score = 0.0
    evidence = []
    if b.debt_loaded_for_extraction:
        score += 0.5
        evidence.append("debt_loaded_for_extraction=True")
    if b.quarterly_pressure_index > 0.7:
        score += 0.3
        evidence.append(f"quarterly_pressure_index={b.quarterly_pressure_index}")
    if b.cash_runway_months < 3:
        score += 0.2
        evidence.append(f"cash_runway_months={b.cash_runway_months}")
    framings.append({
        "framing": "debt_lever",
        "score": round(min(1.0, score), 3),
        "evidence": evidence,
    })

    # ---- accounting_fiction ----
    # Without an explicit subsidiary-shuffling field on BusinessState,
    # this framing is evidenced by: bare regulatory compliance,
    # debt-loaded-extraction structure, and large profit_gap if available.
    score = 0.0
    evidence = []
    if b.regulatory_compliance_only:
        score += 0.30
        evidence.append("regulatory_compliance_only=True")
    if b.debt_loaded_for_extraction and b.profit_extracted_to_holding_pct > 0.7:
        score += 0.40
        evidence.append("debt_loaded + extracted>0.70 (legal-arbitrage shape)")
    if b.quarterly_pressure_index > 0.85 and b.capex_reinvestment_pct < 0.10:
        score += 0.30
        evidence.append("quarterly>0.85 + capex<0.10 (signal decoupled from substrate)")
    framings.append({
        "framing": "accounting_fiction",
        "score": round(min(1.0, score), 3),
        "evidence": evidence,
    })

    # ---- exchange_medium ----
    ext = extraction_ratio_measurement(b)
    score = 0.0
    evidence = []
    if abs(ext["net_flow"]) < 0.15:
        score += 0.35
        evidence.append(f"net_flow={ext['net_flow']:+.3f} (balanced)")
    if 0.30 <= b.profit_recirculated_local_pct <= 0.80:
        score += 0.30
        evidence.append(f"profit_recirculated_local_pct={b.profit_recirculated_local_pct}")
    if not b.debt_loaded_for_extraction and b.quarterly_pressure_index < 0.5:
        score += 0.35
        evidence.append("no debt-loading; quarterly_pressure_index<0.50")
    framings.append({
        "framing": "exchange_medium",
        "score": round(min(1.0, score), 3),
        "evidence": evidence,
    })

    # ---- substrate_capital ----
    score = 0.0
    evidence = []
    if b.capex_reinvestment_pct > 0.30:
        score += 0.35
        evidence.append(f"capex_reinvestment_pct={b.capex_reinvestment_pct}")
    if b.avg_tenure_years > 7:
        score += 0.25
        evidence.append(f"avg_tenure_years={b.avg_tenure_years}")
    if b.deferred_maintenance_pct < 0.20:
        score += 0.20
        evidence.append(f"deferred_maintenance_pct={b.deferred_maintenance_pct}")
    if b.apprenticeship_pipeline:
        score += 0.20
        evidence.append("apprenticeship_pipeline=True")
    framings.append({
        "framing": "substrate_capital",
        "score": round(min(1.0, score), 3),
        "evidence": evidence,
    })

    # ---- quarterly_signal ----
    score = 0.0
    evidence = []
    if b.quarterly_pressure_index > 0.70:
        score += 0.40
        evidence.append(f"quarterly_pressure_index={b.quarterly_pressure_index}")
    if b.capex_reinvestment_pct < 0.15:
        score += 0.30
        evidence.append(f"capex_reinvestment_pct={b.capex_reinvestment_pct}")
    if b.voluntary_turnover_pct > 50:
        score += 0.30
        evidence.append(f"voluntary_turnover_pct={b.voluntary_turnover_pct}")
    framings.append({
        "framing": "quarterly_signal",
        "score": round(min(1.0, score), 3),
        "evidence": evidence,
    })

    return framings


# -----------------------------------------------------------------------------
# USE PATTERN
# -----------------------------------------------------------------------------

def _use_pattern(b: BusinessState) -> str:
    """
    Single dominant pattern for HOW money is being moved through the firm.
    """
    if b.capex_reinvestment_pct > 0.30 and b.profit_extracted_to_holding_pct < 0.30:
        return "productive_investment"
    if b.executive_to_median_pay_ratio > 100 and b.quarterly_pressure_index > 0.70:
        return "speculative"
    if b.profit_extracted_to_holding_pct > 0.60:
        return "accumulation"
    return "transaction"


# -----------------------------------------------------------------------------
# CONTROL LOCUS (BY WHOM)
# -----------------------------------------------------------------------------

def _control_locus(b: BusinessState) -> Dict[str, str]:
    """
    Read the loci of control off observable signals:

      pricing          - whose terms set the prices the firm transacts on
      compensation     - how concentrated is the firm's distribution decision
      optionality      - can the firm say no to bad terms (cash buffer)
    """
    if b.revenue_concentration_top_3_clients > 0.65:
        pricing = "buyer_dictates"
    elif b.revenue_concentration_top_3_clients < 0.30:
        pricing = "firm_or_market_setting"
    else:
        pricing = "concentrated_but_balanced"

    if b.executive_to_median_pay_ratio > 100:
        compensation = "extreme_concentration"
    elif b.executive_to_median_pay_ratio > 25:
        compensation = "concentrated"
    else:
        compensation = "balanced"

    if b.cash_runway_months < 3:
        optionality = "captive_to_creditors"
    elif b.cash_runway_months < 12:
        optionality = "limited_optionality"
    else:
        optionality = "can_opt_out_of_bad_terms"

    return {
        "pricing": pricing,
        "compensation_distribution": compensation,
        "optionality": optionality,
    }


# -----------------------------------------------------------------------------
# STRUCTURAL CONSEQUENCES (RESULTS)
# -----------------------------------------------------------------------------

def _structural_consequences(b: BusinessState) -> Dict[str, Any]:
    sub = substrate_health_audit(b)
    cas = cascade_vulnerability_scan(b)
    ext = extraction_ratio_measurement(b)
    out: Dict[str, Any] = {
        "substrate_rating": sub["rating"],
        "cascade_rating": cas["rating"],
        "extraction_direction": ext["direction"],
        "metabolic_band": None,
        "regeneration_debt": None,
        "irreversible_metrics": None,
        "money_signal_minsky": None,
        "money_signal_has_sign_flips": None,
        "money_signal_magnitude": None,
    }

    # metabolic verdict already filtered through money_audit upstream
    metabolic = check_metabolic_health(b)
    if metabolic is not None:
        out["metabolic_band"] = metabolic.get("sustainable_yield_signal")
        out["regeneration_debt"] = metabolic.get("regeneration_debt")
        out["irreversible_metrics"] = metabolic.get("irreversible_metrics") or None

    # money_signal direct (system-level baseline, not business-specific)
    if _HAS_MONEY_SIGNAL_BRIDGE:
        ms = money_signal_metrics()
        if ms is not None:
            out["money_signal_minsky"] = ms.get("minsky")
            out["money_signal_has_sign_flips"] = ms.get("has_sign_flips")
            out["money_signal_magnitude"] = ms.get("magnitude")

    return out


# -----------------------------------------------------------------------------
# VERDICT NARRATIVE
# -----------------------------------------------------------------------------

_FRAMING_NARRATIVE = {
    "extraction_token":
        "Money is functioning here primarily as an extraction instrument: "
        "an upward-flowing claim accumulator. The 'value-creation' framing "
        "is semantically contaminated -- the actual flow is upward claim "
        "accumulation, not exchange or productive investment.",
    "debt_lever":
        "Money is functioning here primarily as a leverage instrument. "
        "The firm is structured to amplify ownership returns through "
        "debt obligations imposed on the operating substrate.",
    "accounting_fiction":
        "Money is functioning here primarily as a legal-arbitrage and "
        "signal-decoupled book entry. The reported figures and the "
        "physical flows are not the same object.",
    "exchange_medium":
        "Money is functioning here in its textbook role: a medium of "
        "exchange between balanced producers and consumers, with a "
        "substantial fraction recirculated locally.",
    "substrate_capital":
        "Money is functioning here as substrate capital: reinvested in "
        "the productive base (people, knowledge, equipment) that "
        "generates future flows. The framing supports continuation, "
        "not extraction.",
    "quarterly_signal":
        "Money is functioning here primarily as an investor signal, "
        "decoupled from the firm's physical substrate. The reporting "
        "cycle, not the production cycle, is driving allocation.",
}


def _build_verdict(
    primary: str,
    framings: List[Dict[str, Any]],
    consequences: Dict[str, Any],
    use_pattern: str,
    control: Dict[str, str],
) -> str:
    parts = [_FRAMING_NARRATIVE.get(primary, f"Primary framing: {primary}.")]

    secondary = [
        f["framing"] for f in framings
        if f["framing"] != primary and f["score"] >= 0.50
    ]
    if secondary:
        parts.append(f"Secondary framings active: {', '.join(secondary)}.")

    parts.append(
        f"Use pattern: {use_pattern}. "
        f"Pricing: {control['pricing']}. "
        f"Distribution: {control['compensation_distribution']}. "
        f"Optionality: {control['optionality']}."
    )

    if consequences["metabolic_band"]:
        line = f"Metabolic verdict (filtered through money_audit): {consequences['metabolic_band']}"
        if consequences["metabolic_band"] == "BLACK":
            line += " (IRREVERSIBILITY -- distinct from very RED)"
        parts.append(line + ".")

    if consequences["money_signal_minsky"] is not None:
        parts.append(
            f"System money-signal baseline: minsky={consequences['money_signal_minsky']}, "
            f"sign_flips={consequences['money_signal_has_sign_flips']}, "
            f"magnitude={consequences['money_signal_magnitude']}."
        )

    parts.append(
        f"Substrate is {consequences['substrate_rating']}, "
        f"cascade risk is {consequences['cascade_rating']}, "
        f"value is {consequences['extraction_direction']}."
    )

    return " ".join(parts)


# -----------------------------------------------------------------------------
# UNIFIED REPORT
# -----------------------------------------------------------------------------

def money_semantic_audit(b: BusinessState) -> Dict[str, Any]:
    """
    Reality check on how money is being defined, used, by whom, and with
    what structural results, for a single business.

    Returns a structured report with:

      framings_evidenced    closed-set framings, each scored with evidence
      primary_framing       highest-scored framing
      use_pattern           dominant flow pattern
      control_locus         pricing / compensation / optionality readouts
      structural_consequences  substrate / cascade / metabolic / money-signal
      bridge_evidence_active   whether external bridges contributed
      verdict               plain-language summary
    """
    framings = _score_framings(b)
    framings_sorted = sorted(framings, key=lambda f: f["score"], reverse=True)
    primary = framings_sorted[0]["framing"]

    use_pattern = _use_pattern(b)
    control = _control_locus(b)
    consequences = _structural_consequences(b)
    bridge_active = (
        consequences["metabolic_band"] is not None
        or consequences["money_signal_minsky"] is not None
    )
    verdict = _build_verdict(primary, framings_sorted, consequences, use_pattern, control)

    return {
        "name": b.name,
        "framings_evidenced": framings_sorted,
        "primary_framing": primary,
        "use_pattern": use_pattern,
        "control_locus": control,
        "structural_consequences": consequences,
        "bridge_evidence_active": bridge_active,
        "verdict": verdict,
    }


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    for b in reference_profiles():
        rep = money_semantic_audit(b)
        print(f"\n{'='*72}")
        print(f"  {rep['name']}")
        print(f"{'='*72}")

        print(f"  PRIMARY FRAMING: {rep['primary_framing']}")
        print(f"  ALL FRAMINGS (scored):")
        for f in rep["framings_evidenced"]:
            print(f"    {f['score']:.2f}  {f['framing']:18s}  evidence: {f['evidence']}")

        print(f"  USE PATTERN:  {rep['use_pattern']}")
        cl = rep["control_locus"]
        print(f"  CONTROL LOCUS:")
        print(f"    pricing:                  {cl['pricing']}")
        print(f"    compensation_distribution: {cl['compensation_distribution']}")
        print(f"    optionality:              {cl['optionality']}")

        print(f"  STRUCTURAL CONSEQUENCES:")
        sc = rep["structural_consequences"]
        print(f"    substrate_rating:    {sc['substrate_rating']}")
        print(f"    cascade_rating:      {sc['cascade_rating']}")
        print(f"    extraction_direction: {sc['extraction_direction']}")
        print(f"    metabolic_band:      {sc['metabolic_band']}")
        print(f"    regeneration_debt:   {sc['regeneration_debt']}")
        print(f"    money_signal_minsky: {sc['money_signal_minsky']}")

        print(f"  BRIDGE EVIDENCE ACTIVE: {rep['bridge_evidence_active']}")
        print(f"\n  VERDICT:")
        print(f"    {rep['verdict']}")
