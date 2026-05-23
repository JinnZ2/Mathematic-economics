"""
unified_capital_accounting_audit.py  —  C029, C030

Conventional financial models count two forms of capital (financial,
labor) and externalize seven others (environmental, biological,
thermodynamic, social, temporal, health, regulatory). When the
externalized forms are added back in, "scaling" is no longer the
creation of value but the *reallocation* of value from environmental /
biological / temporal reserves into financial accounts, with the
transfer marked as profit.

C029 (selective capital accounting): a financial model that counts only
financial + labor capital and ignores the other seven forms is
structurally incomplete. Its profit projection cannot be reconciled
with the substrate cost of producing that profit.

C030 (scaling as reallocation): under unified capital accounting with a
common denominator (joules-equivalent, years-to-recovery, or
regeneration-cycles), large-scale automation deployments routinely
exhibit financial_capital_gained << sum(all_other_capital_losses).
"Scaling" is then a transfer, not a creation, of capital.

Falsifier (C029): financial deployment publishing audited per-period
accounting that includes nonzero entries against all nine capital
forms with comparable denominators.

Falsifier (C030): large-scale automation deployment where
financial_capital_gained > sum(all_other_capital_losses) when all
capitals are denominated in comparable units (joules-equivalent or
years-to-recovery).

License: CC0-1.0
"""

from typing import Dict, List


# The nine capital forms and their canonical denominators / conversion
# factors to a common joules-equivalent unit. Conversion factors are
# illustrative defaults; callers may override.
CAPITAL_FORMS: List[dict] = [
    {"form": "financial",     "denominator": "usd",
     "joules_per_unit":  3.6e6,    # ~1 kWh/USD (US economy primary energy / GDP, 2024)
     "regen_years":      0.0,
     "counted_conventionally": True},
    {"form": "labor",         "denominator": "person_years",
     "joules_per_unit":  6.3e9,    # ~2000hr/yr * 100W * 3600s
     "regen_years":      0.0,
     "counted_conventionally": True},
    {"form": "environmental", "denominator": "co2_equivalent_tons",
     "joules_per_unit":  3.0e9,    # ~3 GJ/ton sequestration cost
     "regen_years":     50.0,
     "counted_conventionally": False},
    {"form": "biological",    "denominator": "species_diversity_index",
     "joules_per_unit":  5.0e10,   # heuristic biosphere maintenance energy
     "regen_years":    200.0,
     "counted_conventionally": False},
    {"form": "thermodynamic", "denominator": "exergy_kwh",
     "joules_per_unit":  3.6e6,
     "regen_years":      0.0,      # depletion is irreversible at human scale
     "counted_conventionally": False},
    {"form": "social",        "denominator": "trust_index_unit",
     "joules_per_unit":  1.0e10,
     "regen_years":     30.0,
     "counted_conventionally": False},
    {"form": "temporal",      "denominator": "generation_debt_years",
     "joules_per_unit":  1.0e11,
     "regen_years":     25.0,
     "counted_conventionally": False},
    {"form": "health",        "denominator": "QALY_lost",
     "joules_per_unit":  6.3e9,    # ~one labor-year per QALY lost
     "regen_years":      0.0,      # not regen-able (loss is permanent)
     "counted_conventionally": False},
    {"form": "regulatory",    "denominator": "social_license_index",
     "joules_per_unit":  5.0e9,
     "regen_years":     15.0,
     "counted_conventionally": False},
]


def enumerate_capital_forms() -> List[dict]:
    """Return all nine capital forms with denominators and conventionality."""
    return [dict(c) for c in CAPITAL_FORMS]


def capital_denominator(capital_form: str) -> str:
    """Native denominator (unit) for the named capital form."""
    for c in CAPITAL_FORMS:
        if c["form"] == capital_form:
            return c["denominator"]
    raise KeyError(f"unknown capital form: {capital_form!r}")


def _joules(form: str, magnitude: float) -> float:
    for c in CAPITAL_FORMS:
        if c["form"] == form:
            return magnitude * c["joules_per_unit"]
    raise KeyError(f"unknown capital form: {form!r}")


def _regen_years(form: str) -> float:
    for c in CAPITAL_FORMS:
        if c["form"] == form:
            return c["regen_years"]
    raise KeyError(f"unknown capital form: {form!r}")


def extraction_profile(deployment: dict) -> dict:
    """For each capital form, per-year extraction in native units and joules.

    `deployment` carries a `capitals` dict with form -> annual extraction
    in native units. Missing forms default to 0.
    """
    capitals = deployment.get("capitals", {})
    rows = []
    total_extracted_joules = 0.0
    total_regen_debt_years = 0.0
    for c in CAPITAL_FORMS:
        form = c["form"]
        magnitude = float(capitals.get(form, 0.0))
        joules = _joules(form, magnitude)
        regen = _regen_years(form)
        regen_debt = magnitude * regen
        total_extracted_joules += joules
        total_regen_debt_years += regen_debt
        rows.append({
            "form":             form,
            "denominator":      c["denominator"],
            "annual_magnitude": magnitude,
            "annual_joules":    joules,
            "regen_years":      regen,
            "regen_debt_years": regen_debt,
            "counted_conventionally": c["counted_conventionally"],
        })
    return {
        "deployment":              deployment.get("name", "unnamed"),
        "by_capital":              rows,
        "total_extraction_joules_per_year":     total_extracted_joules,
        "total_regen_debt_years_per_year":      total_regen_debt_years,
    }


def deficit_calculation(deployment: dict, time_horizon: int = 30) -> dict:
    """Financial gain vs sum of all other capital losses.

    `deployment` must carry:
      - `annual_financial_gain_usd`: float
      - `capitals`: dict of form -> annual extraction in native units

    Returns the deficit denominated in joules-equivalent over `time_horizon`.
    """
    prof = extraction_profile(deployment)
    fin_gain = float(deployment.get("annual_financial_gain_usd", 0.0))
    fin_gain_joules = _joules("financial", fin_gain)

    non_financial_joules_per_year = sum(
        r["annual_joules"] for r in prof["by_capital"]
        if r["form"] != "financial"
    )
    total_financial_gain_joules = fin_gain_joules * time_horizon
    total_non_financial_loss_joules = (
        non_financial_joules_per_year * time_horizon)

    deficit_joules = (total_non_financial_loss_joules
                      - total_financial_gain_joules)
    return {
        "deployment":             deployment.get("name", "unnamed"),
        "time_horizon_years":     time_horizon,
        "annual_financial_gain_usd": fin_gain,
        "annual_financial_gain_joules": fin_gain_joules,
        "annual_non_financial_loss_joules": non_financial_joules_per_year,
        "total_financial_gain_joules": total_financial_gain_joules,
        "total_non_financial_loss_joules": total_non_financial_loss_joules,
        "deficit_joules":         deficit_joules,
        "deficit_positive":       deficit_joules > 0.0,
        "extraction_profile":     prof,
    }


def internal_consistency_check(model_claims: List[str],
                               unified_accounting: dict,
                               ) -> List[str]:
    """Flag contradictions between model claims and unified accounting.

    Heuristic. If the claim asserts profitability / efficiency without
    qualifications, and the unified accounting shows a positive deficit
    (losses > gains across capitals), flag it.
    """
    import re
    flags = []
    text = " ".join(model_claims).lower()
    profitability_terms = [r"\bprofitab", r"\befficient\b", r"\bvalue\s+creat",
                            r"\bROI\b", r"\bcheap"]
    qualification_terms = [r"\bexcluding\b", r"\bnet\s+of\b",
                            r"\bunaccounted\b", r"\bexternaliz"]
    asserts_profit = any(re.search(p, text) for p in profitability_terms)
    has_qualifier = any(re.search(p, text) for p in qualification_terms)

    deficit_positive = unified_accounting.get("deficit_positive", False)
    if asserts_profit and not has_qualifier and deficit_positive:
        flags.append("profit_claim_without_externalization_qualifier_"
                     "while_unified_accounting_shows_deficit")
    if asserts_profit and unified_accounting.get(
            "annual_non_financial_loss_joules", 0.0) == 0.0:
        flags.append("profit_claim_with_no_documented_non_financial_extraction")
    return flags


def c029_verdict(deployment: dict | None = None) -> dict:
    """Selective capital accounting verdict.

    Threshold met when fewer than half the nine capital forms have
    nonzero entries in the deployment's `capitals` dict — meaning the
    other forms have been externalized rather than accounted for.
    """
    capitals = (deployment or {}).get("capitals", {})
    forms_with_entries = [c["form"] for c in CAPITAL_FORMS
                           if float(capitals.get(c["form"], 0.0)) != 0.0]
    counted_share = len(forms_with_entries) / len(CAPITAL_FORMS)
    conventional_only = all(
        c["form"] in {"financial", "labor"}
        or float(capitals.get(c["form"], 0.0)) == 0.0
        for c in CAPITAL_FORMS
    )
    return {
        "claim_id":             "C029",
        "total_capital_forms":  len(CAPITAL_FORMS),
        "forms_with_entries":   forms_with_entries,
        "counted_share":        counted_share,
        "conventional_only":    conventional_only,
        "threshold_met":        counted_share < 0.5,
        "falsifier":
            "financial deployment publishing audited per-period accounting "
            "that includes nonzero entries against all nine capital forms "
            "with comparable denominators",
    }


def c030_verdict(deployment: dict,
                 time_horizon: int = 30,
                 model_claims: List[str] | None = None,
                 ) -> dict:
    """Scaling-as-reallocation verdict.

    Threshold met when total non-financial capital loss exceeds total
    financial capital gain over `time_horizon`, denominated in
    joules-equivalent.
    """
    deficit = deficit_calculation(deployment, time_horizon)
    inconsistencies = internal_consistency_check(
        model_claims or [], deficit) if model_claims else []
    return {
        "claim_id":             "C030",
        "deployment":           deployment.get("name", "unnamed"),
        "time_horizon_years":   time_horizon,
        "deficit":              deficit,
        "inconsistencies":      inconsistencies,
        "threshold_met":        deficit["deficit_positive"],
        "falsifier":
            "large-scale automation deployment where financial_capital_gained > "
            "sum(all_other_capital_losses) when all capitals are denominated "
            "in comparable units (joules-equivalent or years-to-recovery)",
    }


if __name__ == "__main__":
    # Stylized data-center-style deployment (numbers from the spec example).
    deployment = {
        "name": "stylized_50mw_data_center",
        "annual_financial_gain_usd": 50_000_000.0,
        "capitals": {
            "financial":     50_000_000.0,
            "labor":          500.0,        # FTE
            "environmental":  150_000.0,    # tons CO2/yr
            "biological":      0.05,        # species diversity index loss
            "thermodynamic":  438_000.0,    # 50 MW * 8760 h = exergy_kwh / yr
            "social":          0.10,        # community trust delta
            "temporal":      200.0,         # generation_debt_years/yr accrued
            "health":         50.0,         # QALY/yr in mining + grid regions
            "regulatory":      0.05,        # social license erosion
        },
    }
    c029 = c029_verdict({"capitals": {"financial": 50e6, "labor": 500.0}})
    c030 = c030_verdict(deployment, time_horizon=30,
                        model_claims=["scales beautifully and is profitable"])
    print("C029 conventional-only:", c029)
    print()
    print("C030 deficit_joules:", c030["deficit"]["deficit_joules"])
    print("C030 threshold_met:", c030["threshold_met"])
    print("C030 inconsistencies:", c030["inconsistencies"])
