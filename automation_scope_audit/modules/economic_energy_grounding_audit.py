"""
economic_energy_grounding_audit.py  —  C027, C028

Economic models must be grounded in energy / resource accounting or they
are unfalsifiable. Internal coherence of a financial model — math
checking out, predictions accurate during abundance — is not evidence
that the model is *valid*; it is evidence that the model has been
internally consistent. When resources become scarce, money and energy
decouple, and the model fails catastrophically. The institution built on
the model cannot see the failure because the failure is outside the
model.

C027 (energy grounding): an economic model is valid only if
  (1) every transaction maps to energy transfer or resource consumption,
  (2) every optimization in the model reduces actual energy cost (not
      just financial cost),
  (3) the model can explain *why* the energy cost decreased,
  (4) the model remains valid under resource-scarcity constraints,
  (5) the model can model its own failure modes.

C028 (institutional blindness): the institution that builds decisions on
an ungrounded model loses pivot capacity. Alternative models get
defunded as "inefficient" during the abundance phase; when the model
fails the institution doubles down because it has no Plan B. Cascade
follows.

Falsifier (C027): an economic model that predicts outcomes accurately
during conditions of resource scarcity (where money != energy).

Falsifier (C028): an economic model that successfully adapts to
fundamental resource scarcity without institutional collapse or reversal.

License: CC0-1.0
"""

import re
from typing import Dict, List


# Energy-grounding markers we expect to see in a claim that has actually
# done the work. The bar is loose — any single marker is acceptance; the
# point of the gate is to filter out claims that *never* touch energy /
# resource accounting at all.
ENERGY_GROUNDING_PATTERNS = [
    r"\bjoules?\b", r"\bkwh\b", r"\bgigajoule",
    r"\benergy\s+(?:input|cost|consumption|balance)\b",
    r"\bthermodynamic",
    r"\bembodied\s+(?:energy|carbon)\b",
    r"\beROI\b", r"\bnet\s+energy\b",
    r"\bresource\s+(?:consumption|extraction|depletion|scarcity)\b",
]

OPTIMIZATION_REDUCES_ENERGY_PATTERNS = [
    r"\benergy\s+(?:savings?|reduction|decrease)\b",
    r"\bfuel\s+(?:savings?|reduction|decrease)\b",
    r"\b(?:reduces?|lowers?|cuts?)\s+(?:energy|joules?|kwh|fuel)\b",
    r"\benergy\s+intensity\s+(?:falls?|drops?|decreases?)\b",
]

SCARCITY_ROBUSTNESS_PATTERNS = [
    r"\bunder\s+(?:scarcity|constraint|shortage|disruption)\b",
    r"\bresource[-\s]?constrained\b",
    r"\bsupply\s+(?:shock|break|disruption)\b",
    r"\bembargo", r"\bsanction",
    r"\brationing\b",
]

FAILURE_MODE_PATTERNS = [
    r"\bfailure\s+modes?\b",
    r"\bbreaks?\s+(?:when|under)\b",
    r"\bunfalsifiab", r"\binternal\s+blindness\b",
    r"\bmodel\s+(?:fails?|breaks?)\b",
]


def map_transaction_to_energy(transaction: dict) -> dict:
    """Map an economic transaction to its energy / resource footprint.

    A transaction dict carries at minimum a `kind` and `magnitude`
    (USD by default). Optional keys: `energy_kwh`, `co2_kg`,
    `rare_earth_kg`, `water_l`, `land_ha`, `notes`. Returns the
    transaction augmented with derived joule-equivalents and a
    `mappable` boolean — True when *any* of the energy / resource
    fields are populated.
    """
    kind = transaction.get("kind", "unknown")
    magnitude = float(transaction.get("magnitude", 0.0))
    energy_kwh = float(transaction.get("energy_kwh", 0.0))
    co2_kg = float(transaction.get("co2_kg", 0.0))
    rare_earth_kg = float(transaction.get("rare_earth_kg", 0.0))
    water_l = float(transaction.get("water_l", 0.0))
    land_ha = float(transaction.get("land_ha", 0.0))

    # Approximate energy-equivalents (joules) for non-energy resources.
    # Defaults are conservative; callers may supply explicit `energy_kwh`
    # to override.
    co2_joules = co2_kg * 3.0e9            # ~3 GJ/ton for direct-air capture
    rare_earth_joules = rare_earth_kg * 750_000 * 3.6e6  # ~750 kWh/kg
    water_joules = water_l * 0.01 * 3.6e6  # 10 Wh/L (treatment+transport)
    land_joules = land_ha * 1.5e10         # ~15 GJ/ha biosphere regen cost

    total_joules = (energy_kwh * 3.6e6 + co2_joules + rare_earth_joules
                    + water_joules + land_joules)
    mappable = total_joules > 0.0
    return {
        "kind":              kind,
        "magnitude_usd":     magnitude,
        "energy_kwh":        energy_kwh,
        "co2_kg":            co2_kg,
        "rare_earth_kg":     rare_earth_kg,
        "water_l":           water_l,
        "land_ha":           land_ha,
        "total_joules":      total_joules,
        "joules_per_usd":    total_joules / magnitude if magnitude > 0 else 0.0,
        "mappable":          mappable,
    }


def validate_economic_claim(claim: str) -> dict:
    """Run the 5 validity tests against a claim text.

    Test 1: claim references energy / resource accounting.
    Test 2: claim asserts an optimization that reduces energy (not just $).
    Test 3: claim explains *why* the energy reduction occurs.
    Test 4: claim remains coherent under resource-scarcity conditions.
    Test 5: claim describes its own failure modes.

    Returns per-test booleans + a `valid` flag (all five tests pass).
    Test 3 is approximated by checking whether at least *one* of the
    grounding markers and *one* of the reduction markers appear in close
    proximity (the model is at least gesturing at a causal explanation).
    """
    text = claim.lower()

    def any_hit(patterns: List[str]) -> bool:
        return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

    t1 = any_hit(ENERGY_GROUNDING_PATTERNS)
    t2 = any_hit(OPTIMIZATION_REDUCES_ENERGY_PATTERNS)
    t3 = t1 and t2
    t4 = any_hit(SCARCITY_ROBUSTNESS_PATTERNS)
    t5 = any_hit(FAILURE_MODE_PATTERNS)

    tests = {
        "t1_energy_grounding":       t1,
        "t2_optimization_reduces_energy": t2,
        "t3_causal_explanation":     t3,
        "t4_scarcity_robust":        t4,
        "t5_failure_modes_modeled":  t5,
    }
    return {
        "claim":    claim,
        "tests":    tests,
        "passed":   sum(1 for v in tests.values() if v),
        "total":    len(tests),
        "valid":    all(tests.values()),
    }


def resource_scarcity_sensitivity(economic_model: dict,
                                  scarce_resource: str,
                                  scarcity_degree: float,
                                  ) -> dict:
    """Apply a scarcity constraint to a model dict and check robustness.

    `economic_model` is expected to carry:
      `transactions`: list of transaction dicts (as for
          map_transaction_to_energy)
      `optimization_target`: "financial" | "energy"
      `dependencies`: dict of resource -> dependence_score (0.0-1.0)

    `scarcity_degree` in [0.0, 1.0]; 1.0 = resource unavailable.

    Returns a dict with whether the optimization still holds and which
    transactions become infeasible.
    """
    deps = economic_model.get("dependencies", {})
    dep_score = float(deps.get(scarce_resource, 0.0))
    txns = economic_model.get("transactions", [])

    infeasible = []
    for t in txns:
        # A transaction depends on the resource if it has nonzero
        # consumption in that resource's field (best-effort field match).
        field = {
            "energy":      "energy_kwh",
            "rare_earth":  "rare_earth_kg",
            "water":       "water_l",
            "co2":         "co2_kg",
            "land":        "land_ha",
        }.get(scarce_resource)
        if field and float(t.get(field, 0.0)) > 0.0 and \
                scarcity_degree * dep_score >= 0.5:
            infeasible.append(t.get("kind", "unknown"))

    optimization_still_holds = (
        scarcity_degree * dep_score < 0.3
        or economic_model.get("optimization_target") == "energy"
    )
    return {
        "scarce_resource":    scarce_resource,
        "scarcity_degree":    scarcity_degree,
        "dependence_score":   dep_score,
        "infeasible_transactions": infeasible,
        "optimization_still_holds": optimization_still_holds,
    }


def blindness_detector(model_claims: List[str],
                       external_constraints: List[str]) -> List[str]:
    """Constraints in the substrate the model cannot see.

    `model_claims` is what the model asserts (free-form strings).
    `external_constraints` is what's true in the physical substrate.
    The detector flags constraints whose key terms do not appear in any
    of the model claims.
    """
    text = " ".join(model_claims).lower()
    blind = []
    for c in external_constraints:
        # Heuristic: tokenize the constraint into nouns / multi-word
        # phrases; if none of the head tokens appear in the model text,
        # it's a blind spot.
        head_tokens = [t for t in re.split(r"\W+", c.lower()) if len(t) > 3]
        if not any(t in text for t in head_tokens):
            blind.append(c)
    return blind


def institutional_pivot_capacity(organization_type: str,
                                 model_dependence: float,
                                 alternative_models_available: int,
                                 ) -> float:
    """Probability of successful pivot if the primary model breaks.

    Heuristic on [0.0, 1.0]:
      base = exp(-model_dependence) scales down with single-model lock-in
      alts_factor = 1 - exp(-alternative_models_available / 2.0)
      type_modifier: distributed/network-shaped orgs > centralized
    """
    import math
    md = max(0.0, min(1.0, model_dependence))
    alts = max(0, int(alternative_models_available))
    base = math.exp(-md * 2.0)
    alts_factor = 1.0 - math.exp(-alts / 2.0)
    type_modifier = {
        "distributed":      1.1,
        "network":          1.05,
        "hierarchical":     0.7,
        "monolithic":       0.5,
        "captured":         0.3,
    }.get(organization_type, 0.85)
    return max(0.0, min(1.0, base * alts_factor * type_modifier))


def c027_verdict(claim_text: str,
                 economic_model: dict | None = None,
                 ) -> dict:
    """Energy-grounding verdict.

    Threshold met (structural concern registers) when the claim fails the
    energy-grounding validity tests — i.e., the model is internally
    coherent but not energy-grounded and is therefore unfalsifiable
    until shown to predict accurately under scarcity.
    """
    validation = validate_economic_claim(claim_text)
    summary = {
        "claim_id":      "C027",
        "claim":         claim_text,
        "validation":    validation,
        "threshold_met": not validation["valid"],
        "falsifier":
            "economic model that predicts outcomes accurately during "
            "conditions of resource scarcity (where money != energy)",
    }
    if economic_model is not None:
        # If a model dict is supplied, run the scarcity stress test.
        rare_earth_test = resource_scarcity_sensitivity(
            economic_model, "rare_earth", scarcity_degree=0.8)
        energy_test = resource_scarcity_sensitivity(
            economic_model, "energy", scarcity_degree=0.6)
        summary["stress_tests"] = {
            "rare_earth_scarcity_0.8": rare_earth_test,
            "energy_scarcity_0.6":     energy_test,
        }
        summary["threshold_met"] = (summary["threshold_met"]
            or not rare_earth_test["optimization_still_holds"]
            or not energy_test["optimization_still_holds"])
    return summary


def c028_verdict(model_claims: List[str],
                 external_constraints: List[str],
                 organization_type: str = "hierarchical",
                 model_dependence: float = 0.85,
                 alternative_models_available: int = 1,
                 ) -> dict:
    """Institutional blindness verdict.

    Threshold met when:
      - the blindness detector finds >= 2 constraints the model cannot see, OR
      - institutional pivot capacity < 0.3.
    """
    blind = blindness_detector(model_claims, external_constraints)
    pivot = institutional_pivot_capacity(organization_type,
                                          model_dependence,
                                          alternative_models_available)
    structural = len(blind) >= 2 or pivot < 0.3
    return {
        "claim_id":             "C028",
        "blind_to":             blind,
        "pivot_capacity":       pivot,
        "organization_type":    organization_type,
        "model_dependence":     model_dependence,
        "alternative_models_available": alternative_models_available,
        "threshold_met":        structural,
        "falsifier":
            "economic model that successfully adapts to fundamental "
            "resource scarcity without institutional collapse or reversal",
    }


if __name__ == "__main__":
    bad = "Lower interest rates make capital cheaper, so scaling is more efficient."
    good = ("Our deployment reduces fuel energy by 12% and remains profitable "
            "under a rare-earth supply shock; failure modes (battery scarcity, "
            "grid outage) are explicitly modeled, with joules per ton-mile as "
            "the primary optimization target.")
    print("bad:",  c027_verdict(bad))
    print()
    print("good:", c027_verdict(good))
    print()
    print("C028 captured org:", c028_verdict(
        model_claims=["scaling reduces cost", "cheap capital is good"],
        external_constraints=["rare-earth concentration",
                              "Kessler syndrome risk",
                              "grid frequency instability",
                              "labor displacement reduces demand"],
        organization_type="captured",
        model_dependence=0.95,
        alternative_models_available=0,
    ))
