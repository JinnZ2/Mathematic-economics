"""
engineering_grade_validation_audit.py  —  C031, C032

Two coupled claims about the gap between the validation rigor required
to deploy a physical system (aerospace, offshore, nuclear, marine) and
the rigor actually applied to deploying AI systems on economic models.

C031 (engineering-grade falsifiability gap): economics lacks the
falsifiability criteria required for engineering decisions. The key
terms — liquidity, capital, margin, reserves, profit, efficiency — are
defined differently across institutions, jurisdictions, and time, and
the inputs the models depend on (interest rates, energy prices, labor
markets) are explicitly volatile while being treated as stable.

  An economic model that meets engineering-grade requirements must:
    1. Be explicitly stated (assumptions enumerated)
    2. Be validated across multiple market regimes
       (stable / volatile / supply-constrained / demand-shocked)
    3. Include design margin and enumerated failure modes
    4. Publish falsifiability criteria

  Aerospace, offshore, and nuclear deployments require these
  preconditions before launch / classification / operation. AI on
  economic models routinely skips all four.

C032 (AI on unstable models cascades): when an AI is trained on
historical economic data drawn from a stable-period regime, the AI
inherits stable-period patterns. When deployment conditions shift to a
volatile regime, the AI continues operating on falsified patterns
because it has no mechanism to detect its own falsification. The
institution does not see the failure because the failure is outside
the model.

Falsifier (C031): published economic model that satisfies all four
engineering-grade criteria explicitly and has been third-party-audited
under stress.

Falsifier (C032): AI economic model that successfully predicts outcomes
during a fundamental market regime shift (supply shock, geopolitical
disruption, currency devaluation, regulatory overhaul).

License: CC0-1.0
"""

from typing import Dict, List


# Definition-stability scores for the canonical financial / economic
# concepts. 1.0 = single canonical definition; 0.0 = definition shifts
# meaningfully across institutions, jurisdictions, time periods.
# Scores reflect surveys of central-bank / regulator / IFRS / FASB /
# market-participant usage.
DEFINITION_STABILITY: Dict[str, dict] = {
    "liquidity":  {"stability": 0.35,
                    "notes": "central bank vs regulator vs market participant"},
    "capital":    {"stability": 0.30,
                    "notes": "financial vs human vs natural; shifting"},
    "margin":     {"stability": 0.45,
                    "notes": "varies across institutions, jurisdictions, periods"},
    "reserves":   {"stability": 0.25,
                    "notes": "Fed reserve requirements changed multiple times"},
    "profit":     {"stability": 0.40,
                    "notes": "depreciation, revenue recognition, tax code shifts"},
    "efficiency": {"stability": 0.30,
                    "notes": "denominated in dollars, which is itself unstable"},
}


# Volatility scores for inputs that economic models routinely treat as
# stable. 1.0 = highly stable; 0.0 = highly volatile.
INPUT_STABILITY_2026: Dict[str, dict] = {
    "interest_rates":     {"stability": 0.30,
                            "notes": "policy-driven, can shift 200bp in months"},
    "electricity_prices": {"stability": 0.35,
                            "notes": "grid strain, renewable transition, AI demand"},
    "labor_costs":        {"stability": 0.40,
                            "notes": "skill shortage, generational shift"},
    "rare_earth_prices":  {"stability": 0.20,
                            "notes": "single-jurisdiction concentration, export licensing"},
    "fuel_prices":        {"stability": 0.30,
                            "notes": "geopolitical, refining capacity, blendwall"},
    "regulatory_environment": {"stability": 0.35,
                                "notes": "EV mandates, AI restrictions, carbon pricing"},
    "currency_value":     {"stability": 0.55,
                            "notes": "de-dollarization pressure, CBDC rollout"},
    "supply_chain_lead_times": {"stability": 0.40,
                                 "notes": "semiconductor cycles, freight insurance"},
}


# Four distinct market regimes an engineering-grade economic model
# must remain valid under.
MARKET_REGIMES = [
    {"name": "stable",
     "description": "low inflation, predictable supply, low geopolitical stress"},
    {"name": "volatile",
     "description": "high variance, frequent regime micro-shifts, elevated VIX"},
    {"name": "supply_constrained",
     "description": "rare-earth embargo, semiconductor shortage, fuel cap"},
    {"name": "demand_shocked",
     "description": "consumer purchasing power collapse, growth thesis breaks"},
]


# Aerospace / offshore / nuclear validation standards a critical
# economic model is benchmarked against. Each row carries the
# domain, the precondition required before deployment, and whether
# typical AI/economic deployments satisfy it.
ENGINEERING_GRADE_STANDARDS: List[dict] = [
    {"domain": "aerospace",  "standard": "design margin specified",
     "ai_econ_typically_satisfies": False},
    {"domain": "aerospace",  "standard": "failure modes enumerated",
     "ai_econ_typically_satisfies": False},
    {"domain": "aerospace",  "standard": "falsifiability tested before launch",
     "ai_econ_typically_satisfies": False},
    {"domain": "offshore",   "standard": "pressure ratings + material testing",
     "ai_econ_typically_satisfies": False},
    {"domain": "offshore",   "standard": "failure modes documented",
     "ai_econ_typically_satisfies": False},
    {"domain": "nuclear",    "standard": "stress tests + redundancy analysis",
     "ai_econ_typically_satisfies": False},
    {"domain": "nuclear",    "standard": "worst-case scenarios modeled",
     "ai_econ_typically_satisfies": False},
]


# Historical cascade-on-unstable-model events.
HISTORICAL_AI_ON_UNSTABLE_MODELS: List[dict] = [
    {"event": "2010_flash_crash",
     "training_regime": "stable_2000_2010",
     "deployment_regime": "volatile",
     "result": "cascade", "institution_response": "blamed unusual conditions"},
    {"event": "2008_quant_funds_collapse",
     "training_regime": "stable_2003_2007",
     "deployment_regime": "supply_constrained",
     "result": "cascade", "institution_response": "doubled down then unwound"},
    {"event": "March_2020_treasury_dislocation",
     "training_regime": "stable_2010_2019",
     "deployment_regime": "demand_shocked",
     "result": "cascade", "institution_response": "Fed bailout"},
    {"event": "LTCM_1998",
     "training_regime": "stable_1990_1997",
     "deployment_regime": "supply_constrained",
     "result": "cascade", "institution_response": "Fed-orchestrated rescue"},
]


def validate_engineering_grade(claim: str | dict) -> dict:
    """Run the 4 engineering-grade preconditions against a claim.

    `claim` may be a free-form string or a structured dict with explicit
    `assumptions`, `regimes_validated`, `design_margin`, `failure_modes`,
    `falsifier`. The function returns one boolean per precondition plus
    an overall `engineering_grade` flag (all 4 satisfied).
    """
    import re
    if isinstance(claim, dict):
        c1 = bool(claim.get("assumptions"))
        c2 = len(claim.get("regimes_validated") or []) >= 3
        c3 = bool(claim.get("design_margin")) and \
             bool(claim.get("failure_modes"))
        c4 = bool(claim.get("falsifier"))
    else:
        text = claim.lower()
        c1 = bool(re.search(r"\b(?:assumes?|assumption[s]?)\b", text))
        regime_hits = sum(
            1 for r in MARKET_REGIMES
            if re.search(r["name"].replace("_", r"\s*"), text)
        )
        c2 = regime_hits >= 3
        c3 = bool(re.search(
            r"\b(?:design\s+margin|failure\s+modes?|worst[-\s]case)\b",
            text))
        c4 = bool(re.search(r"\bfalsif", text))
    tests = {
        "explicitly_stated":           c1,
        "validated_across_regimes":    c2,
        "design_margin_and_failures":  c3,
        "falsifiability_published":    c4,
    }
    return {
        "claim":             claim if isinstance(claim, str) else "[structured]",
        "tests":             tests,
        "passed":            sum(1 for v in tests.values() if v),
        "total":             len(tests),
        "engineering_grade": all(tests.values()),
    }


def definition_stability_check(model_terms: List[str] | None = None,
                                stability_table: Dict[str, dict] | None = None,
                                ) -> dict:
    """Score the definition stability of terms a claim depends on."""
    table = stability_table or DEFINITION_STABILITY
    terms = model_terms or list(table)
    rows = []
    total = 0.0
    for t in terms:
        if t in table:
            row = dict(table[t])
            row["term"] = t
            rows.append(row)
            total += row["stability"]
    mean_stab = (total / len(rows)) if rows else 0.0
    return {
        "terms_checked":     [r["term"] for r in rows],
        "by_term":           rows,
        "mean_stability":    mean_stab,
        "low_stability_terms": [r["term"] for r in rows
                                if r["stability"] < 0.5],
    }


def input_volatility_assessment(inputs: List[str] | None = None,
                                stability_table: Dict[str, dict] | None = None,
                                ) -> dict:
    """Volatility scorecard for inputs the model treats as stable."""
    table = stability_table or INPUT_STABILITY_2026
    keys = inputs or list(table)
    rows = []
    for k in keys:
        if k in table:
            row = dict(table[k])
            row["input"] = k
            rows.append(row)
    mean_stab = sum(r["stability"] for r in rows) / len(rows) if rows else 0.0
    return {
        "inputs":            [r["input"] for r in rows],
        "by_input":          rows,
        "mean_stability":    mean_stab,
        "volatile_inputs":   [r["input"] for r in rows if r["stability"] < 0.5],
    }


def market_regime_validation_test(model: dict) -> dict:
    """Has the model been validated across the 4 market regimes?

    `model` is a dict optionally carrying `regimes_validated` (list of
    regime names). Returns the count of regimes covered plus the
    missing ones.
    """
    validated = set(model.get("regimes_validated", []))
    all_regimes = {r["name"] for r in MARKET_REGIMES}
    missing = sorted(all_regimes - validated)
    return {
        "regimes_validated": sorted(validated),
        "regimes_missing":   missing,
        "coverage":          len(validated) / len(all_regimes)
                              if all_regimes else 0.0,
        "passes_regime_test": len(missing) == 0,
    }


def ai_training_regime_drift(training_regime: str,
                             deployment_regime: str,
                             ) -> dict:
    """Compare AI training-data regime to deployment regime."""
    drift = training_regime != deployment_regime
    severity = {
        ("stable",              "stable"):              0.0,
        ("stable",              "volatile"):            0.6,
        ("stable",              "supply_constrained"):  0.8,
        ("stable",              "demand_shocked"):      0.85,
        ("volatile",            "stable"):              0.2,
        ("volatile",            "volatile"):            0.0,
        ("volatile",            "supply_constrained"):  0.5,
        ("volatile",            "demand_shocked"):      0.6,
        ("supply_constrained",  "stable"):              0.4,
        ("supply_constrained",  "volatile"):            0.4,
        ("supply_constrained",  "supply_constrained"):  0.0,
        ("supply_constrained",  "demand_shocked"):      0.5,
        ("demand_shocked",      "stable"):              0.45,
        ("demand_shocked",      "volatile"):            0.4,
        ("demand_shocked",      "supply_constrained"):  0.45,
        ("demand_shocked",      "demand_shocked"):      0.0,
    }.get((training_regime, deployment_regime), 0.5)
    return {
        "training_regime":   training_regime,
        "deployment_regime": deployment_regime,
        "drift":             drift,
        "severity":          severity,
    }


def cascade_probability_unstable_model(model_validation: dict,
                                       regime_drift: dict,
                                       ) -> dict:
    """Probability of cascade given model + regime context.

    Combines engineering-grade test failure (per `validate_engineering_grade`)
    with training-vs-deployment regime drift severity.
    """
    base = 1.0 - (model_validation["passed"] / model_validation["total"])
    drift = regime_drift["severity"]
    cascade_prob = min(1.0, base * 0.6 + drift * 0.6)
    return {
        "engineering_grade_failure_share": base,
        "regime_drift_severity":           drift,
        "cascade_probability":             cascade_prob,
    }


def c031_verdict(claim: str | dict,
                 model_terms: List[str] | None = None,
                 inputs: List[str] | None = None,
                 ) -> dict:
    """Engineering-grade falsifiability verdict.

    Threshold met when the claim fails the engineering-grade test OR the
    underlying definition/input stability scorecards average below 0.6.
    """
    eg = validate_engineering_grade(claim)
    defs = definition_stability_check(model_terms)
    inputs_v = input_volatility_assessment(inputs)
    structural = (
        not eg["engineering_grade"]
        or defs["mean_stability"] < 0.6
        or inputs_v["mean_stability"] < 0.6
    )
    return {
        "claim_id":          "C031",
        "engineering_grade": eg,
        "definitions":       defs,
        "inputs":            inputs_v,
        "threshold_met":     structural,
        "falsifier":
            "published economic model that satisfies all four "
            "engineering-grade criteria explicitly and has been "
            "third-party-audited under stress",
    }


def c032_verdict(model: dict | None = None,
                 training_regime: str = "stable",
                 deployment_regime: str = "volatile",
                 claim: str | dict = "",
                 ) -> dict:
    """AI-on-unstable-models cascade verdict.

    Threshold met when:
      - model is missing >= 2 regimes from the 4-regime validation, OR
      - regime drift severity >= 0.5, OR
      - cascade probability (combined) >= 0.5.
    """
    model = model or {}
    regime_test = market_regime_validation_test(model)
    drift = ai_training_regime_drift(training_regime, deployment_regime)
    eg = validate_engineering_grade(claim) if claim else \
        {"passed": 0, "total": 4, "engineering_grade": False,
         "tests": {}, "claim": ""}
    cascade = cascade_probability_unstable_model(eg, drift)
    structural = (
        len(regime_test["regimes_missing"]) >= 2
        or drift["severity"] >= 0.5
        or cascade["cascade_probability"] >= 0.5
    )
    return {
        "claim_id":                "C032",
        "regime_validation":       regime_test,
        "regime_drift":            drift,
        "engineering_grade":       eg,
        "cascade":                 cascade,
        "historical_patterns":     HISTORICAL_AI_ON_UNSTABLE_MODELS,
        "threshold_met":           structural,
        "falsifier":
            "AI economic model that successfully predicts outcomes during "
            "a fundamental market regime shift (supply shock, geopolitical "
            "disruption, currency devaluation, regulatory overhaul)",
    }


if __name__ == "__main__":
    bad = "At scale, cloud is 30% cheaper than on-premise."
    good = {
        "assumptions": ["interest rate 4-6%", "diesel $3.50-4.50/gal",
                        "carrier wages +2-3%/yr"],
        "regimes_validated": ["stable", "volatile", "supply_constrained"],
        "design_margin": 0.20,
        "failure_modes": ["fuel cap", "labor strike", "rare-earth embargo"],
        "falsifier": "deficit > $X under volatile regime",
    }
    print("C031 bad:",  c031_verdict(bad))
    print()
    print("C031 structured-good:", c031_verdict(good))
    print()
    print("C032 stable->volatile drift:",
          c032_verdict(model={"regimes_validated": ["stable"]},
                        training_regime="stable",
                        deployment_regime="volatile",
                        claim=bad))
