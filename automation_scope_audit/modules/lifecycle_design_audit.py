"""
lifecycle_design_audit.py  —  C073, C074

Two claims about end-of-life design accountability in automation
deployments.

C073 Lifecycle design is invisible in conventional financial models.
     Capex + opex + linear depreciation + nominal salvage value misses
     the dominant cost of obsolescence (10,000 trucks * $400k = $4B
     stranded at next-generation transition; ~3-4x lifecycle energy
     vs designed-for-lifecycle).
C074 End-of-life accountability is externalized from decision authority.
     Designer is optimized for first-life performance; nobody is
     accountable for waste stream. The fix: require designer to declare
     second-life pathway, third-life materials recovery, and accept
     liability for end-of-life cost at design phase.

License: CC0-1.0
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# Default lifecycle cost models (USD per unit unless noted)
# ---------------------------------------------------------------------------

DEFAULT_CONVENTIONAL_MODEL = {
    "capex_usd":                          400_000.0,
    "opex_per_year_usd":                   55_000.0,
    "lifecycle_years":                          7,
    "linear_depreciation":                   True,
    "salvage_value_usd":                   50_000.0,
    "end_of_life_cost_externalized":         True,
    "second_life_designed":                  False,
    "materials_recovery_designed":           False,
    "designer_accountable_for_eol":          False,
}

DEFAULT_LIFECYCLE_DESIGNED_MODEL = {
    "capex_usd":                          450_000.0,    # higher upfront for redesign capability
    "opex_per_year_usd":                   55_000.0,
    "lifecycle_phase1_years":                   7,
    "refurbishment_cost_usd":              80_000.0,    # vs buying new $400k
    "lifecycle_phase2_years":                  10,
    "materials_recovery_value_usd":        90_000.0,
    "end_of_life_cost_externalized":         False,
    "second_life_designed":                  True,
    "materials_recovery_designed":           True,
    "designer_accountable_for_eol":          True,
}


# Embodied energy / waste-stream constants (USD per unit; placeholders for
# downstream calibration via Token Price Index, EPA Superfund averages,
# etc.). Default captures both disposal cost AND stranded-asset reality
# (per C005: autonomous trucks worth ~$0 to non-consolidated operators
# at next-generation transition, so the conventional $50k salvage is
# itself unmeasured optimism).
DEFAULT_EOL_EXTERNALIZED_COST_USD = 130_000.0   # disposal + stranded-asset + carbon liability


# ---------------------------------------------------------------------------
# C073  Lifecycle design invisible in financial models
# ---------------------------------------------------------------------------

def conventional_lifecycle_cost(
    model: Dict[str, object] | None = None,
    fleet_size: int = 1,
    eol_externalized_cost_usd: float = DEFAULT_EOL_EXTERNALIZED_COST_USD,
) -> dict:
    """Compute the visible (reported) and total (true) lifecycle cost."""
    m = {**DEFAULT_CONVENTIONAL_MODEL, **(model or {})}
    years = int(m["lifecycle_years"])
    capex = float(m["capex_usd"]) * fleet_size
    opex = float(m["opex_per_year_usd"]) * years * fleet_size
    salvage = float(m["salvage_value_usd"]) * fleet_size
    visible_total = capex + opex - salvage
    eol_hidden = eol_externalized_cost_usd * fleet_size
    true_total = visible_total + eol_hidden
    return {
        "fleet_size":             fleet_size,
        "lifecycle_years":        years,
        "visible_capex_usd":      capex,
        "visible_opex_usd":       opex,
        "visible_salvage_usd":    salvage,
        "visible_total_usd":      visible_total,
        "externalized_eol_usd":   eol_hidden,
        "true_total_usd":         true_total,
        "externalization_share":  eol_hidden / true_total if true_total else 0.0,
    }


def designed_for_lifecycle_cost(
    model: Dict[str, object] | None = None,
    fleet_size: int = 1,
) -> dict:
    """Compute lifecycle cost for a designed-for-lifecycle deployment."""
    m = {**DEFAULT_LIFECYCLE_DESIGNED_MODEL, **(model or {})}
    p1 = int(m["lifecycle_phase1_years"])
    p2 = int(m["lifecycle_phase2_years"])
    capex = float(m["capex_usd"]) * fleet_size
    opex = float(m["opex_per_year_usd"]) * (p1 + p2) * fleet_size
    refurb = float(m["refurbishment_cost_usd"]) * fleet_size
    recovery = float(m["materials_recovery_value_usd"]) * fleet_size
    total = capex + opex + refurb - recovery
    return {
        "fleet_size":             fleet_size,
        "lifecycle_total_years":  p1 + p2,
        "capex_usd":              capex,
        "opex_usd":               opex,
        "refurbishment_usd":      refurb,
        "materials_recovery_usd": recovery,
        "total_lifecycle_usd":    total,
    }


def c073_verdict(model: Dict[str, object] | None = None,
                 fleet_size: int = 1,
                 eol_externalized_cost_usd: float = DEFAULT_EOL_EXTERNALIZED_COST_USD,
                 ) -> dict:
    """C073: concern registers when externalized EOL > 10% of visible total."""
    res = conventional_lifecycle_cost(model, fleet_size, eol_externalized_cost_usd)
    return {
        "claim_id":      "C073",
        **res,
        "threshold_met": res["externalization_share"] > 0.10,
        "falsifier":
            "published financial model where end-of-life disposal, "
            "materials recovery, waste-stream liability, and obsolescence-"
            "transition cost are each itemized AND the total lifecycle "
            "cost matches the visible total within 10%",
    }


# ---------------------------------------------------------------------------
# C074  End-of-life accountability
# ---------------------------------------------------------------------------

def end_of_life_accountability_check(
    design_doc: Dict[str, bool] | None = None,
) -> dict:
    """Check the three preconditions for end-of-life accountability."""
    doc = {**DEFAULT_CONVENTIONAL_MODEL, **(design_doc or {})}
    checks = {
        "second_life_designed":           bool(doc.get("second_life_designed", False)),
        "materials_recovery_designed":    bool(doc.get("materials_recovery_designed", False)),
        "designer_accountable_for_eol":   bool(doc.get("designer_accountable_for_eol", False)),
    }
    passed = sum(1 for v in checks.values() if v)
    return {
        "preconditions":  checks,
        "passed":         passed,
        "total":          3,
        "all_pass":       passed == 3,
    }


def c074_verdict(design_doc: Dict[str, bool] | None = None) -> dict:
    """C074: concern registers when ANY of the 3 preconditions fails."""
    res = end_of_life_accountability_check(design_doc)
    return {
        "claim_id":      "C074",
        **res,
        "threshold_met": not res["all_pass"],
        "falsifier":
            "automation deployment with declared second-life pathway, "
            "third-life materials recovery, AND designer contractually "
            "accountable for end-of-life cost, sustained over a full "
            "obsolescence-transition cycle",
    }


if __name__ == "__main__":
    print("conventional (1 truck):",
          conventional_lifecycle_cost(fleet_size=1))
    print("conventional (10000 trucks):",
          conventional_lifecycle_cost(fleet_size=10_000))
    print()
    print("designed-for-lifecycle (10000 trucks):",
          designed_for_lifecycle_cost(fleet_size=10_000))
    print()
    print("C073:", c073_verdict()["threshold_met"])
    print("C074 default:", c074_verdict()["threshold_met"])
    print("C074 designed:", c074_verdict({
        "second_life_designed": True,
        "materials_recovery_designed": True,
        "designer_accountable_for_eol": True})["threshold_met"])
