"""
Maps parsed premises to physical constraint equations.

Each constraint models a real conservation law where lhs and rhs represent
actual physical quantities. When a claim violates conservation, lhs != rhs
and the delta measures the severity of the violation.

Constraint dict shape:
    law:        str   — which physical law
    lhs:        float — input/source side of the equation
    rhs:        float — output/sink side of the equation
    tolerance:  float — acceptable imbalance (measurement uncertainty)
    reason:     str   — why this constraint was generated
"""


def map_to_constraints(parsed: dict) -> list:
    """Generate conservation constraints based on the parsed claim."""
    constraints = []
    t = parsed["type"]
    pattern = parsed["claim_pattern"]

    # Always check the claim pattern first — it's more specific than type
    pattern_constraints = _from_claim_pattern(parsed, pattern)
    if pattern_constraints:
        constraints.extend(pattern_constraints)

    # Add domain-specific constraints if the pattern didn't already cover them
    covered_laws = {c["law"] for c in constraints}

    if t == "thermodynamic":
        if "first_law_thermodynamics" not in covered_laws:
            constraints.append(_first_law(parsed))
        if "second_law_thermodynamics" not in covered_laws:
            constraints.append(_second_law(parsed))
    elif t == "mass_balance":
        if "mass_conservation" not in covered_laws:
            constraints.append(_mass_conservation(parsed))
    elif t == "information":
        if "information_conservation" not in covered_laws:
            constraints.append(_information_conservation(parsed))

    # Fallback: ensure at least one constraint
    if not constraints:
        constraints.append(_generic_balance(parsed))

    return constraints


# -- Pattern-based constraint generation ---------------------------------------

def _from_claim_pattern(parsed, pattern):
    """Generate constraints directly from the identified claim pattern."""
    mag = sum(parsed["magnitude"])

    if pattern == "creation_from_nothing":
        # Claiming output with zero input → first law violation
        return [
            {
                "law": "first_law_thermodynamics",
                "lhs": 0.0,           # input: nothing
                "rhs": mag,            # output: claimed quantity
                "tolerance": 0.01,
                "reason": "Claim asserts creation from nothing — zero input, nonzero output",
            },
            {
                "law": "second_law_thermodynamics",
                "lhs": 0.0,           # entropy cost paid: none
                "rhs": mag,            # entropy cost required: positive
                "tolerance": 0.0,
                "reason": "Spontaneous creation implies entropy decrease in isolated system",
            },
        ]

    if pattern == "infinite_claim":
        # Claiming infinite output from finite system
        return [{
            "law": "first_law_thermodynamics",
            "lhs": mag,               # finite input
            "rhs": float("inf"),       # infinite output claimed
            "tolerance": 0.01,
            "reason": "Infinite output from finite input violates energy conservation",
        }]

    if pattern == "output_without_cost":
        # Claiming extraction/production with explicitly denied cost
        return [{
            "law": "second_law_thermodynamics",
            "lhs": 0.0,               # entropy/cost paid: zero
            "rhs": mag,               # entropy/cost required by physics: positive
            "tolerance": 0.0,
            "reason": "Extraction without entropy cost violates second law",
        }]

    if pattern == "perfect_efficiency":
        # 100% efficiency violates second law (some energy always lost to entropy)
        return [{
            "law": "second_law_thermodynamics",
            "lhs": 1.0,               # claimed efficiency
            "rhs": 0.99,              # maximum physically possible (Carnot limit)
            "tolerance": 0.0,
            "reason": "Perfect efficiency violates second law — entropy always increases",
        }]

    if pattern == "conservation_statement":
        # "X cannot be destroyed" — this is VALID physics
        return [{
            "law": "conservation_affirmation",
            "lhs": 1.0,
            "rhs": 1.0,
            "tolerance": 0.01,
            "reason": "Premise affirms conservation — consistent with physics",
        }]

    if pattern == "transfer_claim":
        # "X moves from A to B" — valid if balanced
        return [{
            "law": "first_law_thermodynamics",
            "lhs": mag,               # energy leaving source
            "rhs": mag,               # energy arriving at sink
            "tolerance": 0.01,
            "reason": "Transfer claim — balanced if input equals output",
        }]

    if pattern == "entropy_reversal":
        # Claiming entropy decrease without external work
        return [{
            "law": "second_law_thermodynamics",
            "lhs": -1.0,              # claimed: entropy decreases
            "rhs": 0.0,               # required: entropy >= 0 in isolated system
            "tolerance": 0.0,
            "reason": "Entropy reversal without external work violates second law",
        }]

    if pattern == "perpetual_motion":
        return [
            {
                "law": "first_law_thermodynamics",
                "lhs": 0.0,
                "rhs": mag,
                "tolerance": 0.01,
                "reason": "Perpetual motion requires energy from nothing",
            },
            {
                "law": "second_law_thermodynamics",
                "lhs": 0.0,
                "rhs": mag,
                "tolerance": 0.0,
                "reason": "Perpetual motion requires zero entropy production",
            },
        ]

    if pattern == "energy_extraction_without_return":
        # First-law accounting at the source boundary: outflow is positive
        # but return/replenishment inflow is explicitly zero. Indefinite
        # extraction implies the source holds infinite reserves.
        # (See domains/thermodynamic_accountability.py for the full
        # energy-balance formulation.)
        return [{
            "law": "first_law_thermodynamics",
            "lhs": 0.0,            # return flow to source: denied
            "rhs": mag,            # outflow from source: asserted
            "tolerance": 0.01,
            "reason": (
                "Extraction without return flow — source cannot sustain "
                "indefinite outflow with zero replenishment"
            ),
        }]

    return None  # no pattern-specific constraints


# -- Domain-specific fallback constraints --------------------------------------

def _first_law(parsed):
    """First Law of Thermodynamics: dU = Q - W (energy in = energy out)."""
    mag = sum(parsed["magnitude"])
    is_impossible = parsed["is_impossibility_claim"]
    cost_denied = parsed.get("cost_negated", False)

    if is_impossible or cost_denied:
        return {
            "law": "first_law_thermodynamics",
            "lhs": 0.0,
            "rhs": mag,
            "tolerance": 0.01,
            "reason": "Claim implies energy output without corresponding input",
        }

    return {
        "law": "first_law_thermodynamics",
        "lhs": mag,
        "rhs": mag,
        "tolerance": 0.01,
        "reason": "Energy balance appears conserved",
    }


def _second_law(parsed):
    """Second Law: entropy of isolated system never decreases."""
    is_impossible = parsed["is_impossibility_claim"]
    cost_denied = parsed.get("cost_negated", False)

    has_extraction = any(
        k in parsed["keywords"] for k in ["extract", "produce", "generate", "convert", "create"]
    )

    if is_impossible or (has_extraction and cost_denied):
        return {
            "law": "second_law_thermodynamics",
            "lhs": 0.0,
            "rhs": 1.0,
            "tolerance": 0.0,
            "reason": "Process claimed without entropy cost — violates second law",
        }

    return {
        "law": "second_law_thermodynamics",
        "lhs": 1.0,
        "rhs": 1.0,
        "tolerance": 0.0,
        "reason": "Entropy production appears accounted for",
    }


def _mass_conservation(parsed):
    """Conservation of mass: mass in = mass out in closed system."""
    mag = sum(parsed["magnitude"])
    is_impossible = parsed["is_impossibility_claim"]

    if is_impossible:
        return {
            "law": "mass_conservation",
            "lhs": 0.0,
            "rhs": mag,
            "tolerance": 0.01,
            "reason": "Claim implies mass creation or destruction",
        }

    if parsed.get("is_conservation_statement", False):
        return {
            "law": "mass_conservation",
            "lhs": mag,
            "rhs": mag,
            "tolerance": 0.01,
            "reason": "Premise affirms mass conservation",
        }

    return {
        "law": "mass_conservation",
        "lhs": mag,
        "rhs": mag,
        "tolerance": 0.01,
        "reason": "Mass balance appears conserved",
    }


def _information_conservation(parsed):
    """Information conservation: cannot create information from nothing."""
    mag = sum(parsed["magnitude"])
    is_impossible = parsed["is_impossibility_claim"]
    cost_denied = parsed.get("cost_negated", False)

    if is_impossible or cost_denied:
        return {
            "law": "information_conservation",
            "lhs": 0.0,
            "rhs": mag,
            "tolerance": 0.01,
            "reason": "Claim implies information creation without source",
        }

    return {
        "law": "information_conservation",
        "lhs": mag,
        "rhs": mag,
        "tolerance": 0.01,
        "reason": "Information flow appears balanced",
    }


def _generic_balance(parsed):
    """Fallback: general conservation check based on claim structure."""
    if parsed["is_impossibility_claim"]:
        return {
            "law": "generic_conservation",
            "lhs": 0.0,
            "rhs": 1.0,
            "tolerance": 0.1,
            "reason": "Claim structure implies something from nothing",
        }

    if parsed.get("cost_negated", False):
        return {
            "law": "generic_conservation",
            "lhs": 0.0,
            "rhs": 1.0,
            "tolerance": 0.1,
            "reason": "Claim explicitly denies associated cost",
        }

    return {
        "law": "generic_conservation",
        "lhs": 1.0,
        "rhs": 1.0,
        "tolerance": 0.1,
        "reason": "No conservation violation detected in claim structure",
    }
