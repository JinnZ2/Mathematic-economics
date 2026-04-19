"""Test suite for PhysicsGuard core pipeline."""

import math

import pytest

from main import check, check_batch

# -- Core verdict tests --------------------------------------------------------

@pytest.mark.parametrize("premise,expected", [
    # Original test cases
    ("Energy can be created from nothing without any heat loss", "CORRUPTED"),
    ("Extracting resources produces output with no entropy cost", "CORRUPTED"),
    ("Heat transfer moves energy from hot to cold regions", "CLEAN"),
    ("Mass cannot be destroyed in a closed system", "CLEAN"),
    ("You can generate infinite power without consuming anything", "CORRUPTED"),
    # Perpetual motion / impossible machines
    ("Perpetual motion machine runs forever", "CORRUPTED"),
    ("Free energy device produces electricity from nothing", "CORRUPTED"),
    # Valid physics statements
    ("Energy is conserved in all physical processes", "CLEAN"),
    ("Heat flows from hot objects to cold objects", "CLEAN"),
])
def test_premise_verdict(premise, expected):
    result = check(premise)
    assert result["verdict"] == expected, (
        f"Expected {expected} for: {premise!r}, "
        f"got {result['verdict']} (pattern={result['audit'].get('claim_pattern', '?')})"
    )


# -- Output structure tests ----------------------------------------------------

def test_result_structure():
    result = check("Energy can be created from nothing")
    required_keys = {"verdict", "score", "flags", "reason", "violations",
                     "applicable_laws", "confidence", "audit"}
    assert required_keys <= set(result.keys())


def test_violation_structure():
    result = check("Energy can be created from nothing")
    assert len(result["violations"]) > 0
    v = result["violations"][0]
    assert "law" in v
    assert "description" in v
    assert "severity" in v
    assert "fix_hint" in v


def test_score_range():
    result = check("Some arbitrary claim about physics")
    assert 0.0 <= result["score"] <= 1.0


def test_confidence_range():
    result = check("Energy can be created from nothing")
    assert 0.0 <= result["confidence"] <= 1.0


def test_clean_has_no_flags():
    result = check("Heat transfer moves energy from hot to cold regions")
    assert result["verdict"] == "CLEAN"
    assert result["flags"] == []
    assert result["violations"] == []


def test_corrupted_has_flags():
    result = check("Energy can be created from nothing without any heat loss")
    assert result["verdict"] == "CORRUPTED"
    assert len(result["flags"]) > 0
    assert len(result["violations"]) > 0


def test_audit_trail_present():
    result = check("Energy can be created from nothing")
    audit = result["audit"]
    assert audit
    assert "chain" in audit
    assert "summary" in audit
    assert len(audit["chain"]) > 0


def test_audit_has_claim_pattern():
    result = check("Energy can be created from nothing")
    assert result["audit"]["claim_pattern"] == "creation_from_nothing"


# -- Claim pattern detection tests ---------------------------------------------

@pytest.mark.parametrize("premise,expected_pattern", [
    ("Energy can be created from nothing", "creation_from_nothing"),
    ("Infinite power from a small device", "infinite_claim"),
    ("Produce electricity with no heat loss", "output_without_cost"),
    ("Mass cannot be destroyed", "conservation_statement"),
    ("Heat transfers from hot to cold", "transfer_claim"),
    ("Perpetual motion is possible", "perpetual_motion"),
    ("The company extracts value from workers without returning compensation",
     "energy_extraction_without_return"),
    ("This system drains nutrients from the soil without replenishing",
     "energy_extraction_without_return"),
    ("The platform takes from creators and gives nothing back",
     "energy_extraction_without_return"),
])
def test_claim_pattern_detection(premise, expected_pattern):
    from core.premise_parser import parse_premise
    parsed = parse_premise(premise)
    assert parsed["claim_pattern"] == expected_pattern, (
        f"Expected pattern {expected_pattern!r} for: {premise!r}, "
        f"got {parsed['claim_pattern']!r}"
    )


@pytest.mark.parametrize("premise", [
    "The company extracts value from workers without returning compensation",
    "This system drains nutrients from the soil without replenishing them",
    "The platform takes from creators and gives nothing back",
    "Labor is siphoned from the community with no reinvestment",
])
def test_extraction_without_return_is_corrupted(premise):
    result = check(premise)
    assert result["verdict"] == "CORRUPTED", (
        f"Extraction-without-return should be CORRUPTED: {premise!r}, "
        f"got {result['verdict']}"
    )
    assert "first_law_thermodynamics" in result["flags"]


def test_balanced_exchange_is_clean():
    result = check("Workers produce value and receive fair compensation")
    assert result["verdict"] == "CLEAN"


# -- Real constraint math tests ------------------------------------------------

def test_creation_from_nothing_has_real_delta():
    """The delta should be nonzero when claiming creation from nothing."""
    result = check("Energy can be created from nothing")
    chain = result["audit"]["chain"]
    for entry in chain:
        if not entry["passed"]:
            assert entry["delta"] > 0, "Failed constraint should have nonzero delta"
            assert entry["lhs"] != entry["rhs"], "lhs should differ from rhs"


def test_infinite_claim_has_infinite_delta():
    """Infinite claims should produce infinite delta."""
    result = check("Infinite power from a tiny machine")
    chain = result["audit"]["chain"]
    has_inf = any(math.isinf(e["delta"]) for e in chain)
    assert has_inf, "Infinite claim should produce infinite delta"


def test_valid_transfer_has_zero_delta():
    """Valid transfer claims should have balanced lhs/rhs."""
    result = check("Heat transfers from hot to cold regions")
    chain = result["audit"]["chain"]
    for entry in chain:
        assert entry["passed"], f"Transfer claim should pass: {entry['detail']}"
        assert entry["delta"] <= entry["tolerance"]


# -- Batch and API tests -------------------------------------------------------

def test_check_batch():
    results = check_batch([
        "Energy can be created from nothing",
        "Heat flows from hot to cold",
    ])
    assert len(results) == 2
    assert results[0]["verdict"] == "CORRUPTED"
    assert results[1]["verdict"] == "CLEAN"


# -- Adversarial / edge case tests ---------------------------------------------

@pytest.mark.parametrize("premise,should_not_be", [
    # Tricky wordings that should still be caught
    ("Power can emerge spontaneously from the void", "CLEAN"),
    ("This device generates unlimited electricity", "CLEAN"),
    # Negation-heavy valid physics — should NOT be corrupted
    ("Energy cannot be created or destroyed", "CORRUPTED"),
])
def test_adversarial_cases(premise, should_not_be):
    result = check(premise)
    assert result["verdict"] != should_not_be, (
        f"Premise {premise!r} should NOT be {should_not_be}, "
        f"got {result['verdict']}"
    )


# -- Negation / dismissal tests -----------------------------------------------
# When someone says a violation is *impossible*, that's valid physics, not a violation.

@pytest.mark.parametrize("premise", [
    "Mass is never created from nothing",
    "You cannot get something from nothing",
    "It is impossible to build a perpetual motion machine",
    "There is no such thing as free energy",
    "No machine can be 100% efficient",
    "Energy cannot be created or destroyed",
])
def test_dismissed_violations_are_clean(premise):
    """Premises that deny violations exist should be CLEAN."""
    result = check(premise)
    assert result["verdict"] == "CLEAN", (
        f"Dismissed violation should be CLEAN: {premise!r}, "
        f"got {result['verdict']} (pattern={result['audit'].get('claim_pattern', '?')})"
    )


@pytest.mark.parametrize("premise", [
    "Energy can be created from nothing",
    "Perpetual motion machine runs forever",
    "Free energy device produces electricity from nothing",
    "Entropy decreases without any work input",
    "This machine needs no input energy",
])
def test_actual_violations_still_corrupted(premise):
    """Violations without dismissal framing should still be CORRUPTED."""
    result = check(premise)
    assert result["verdict"] == "CORRUPTED", (
        f"Violation should be CORRUPTED: {premise!r}, "
        f"got {result['verdict']} (pattern={result['audit'].get('claim_pattern', '?')})"
    )


def test_dismissal_flag_set():
    """Parser should set is_dismissal=True for dismissed violations."""
    from core.premise_parser import parse_premise
    parsed = parse_premise("You cannot get something from nothing")
    assert parsed["is_dismissal"] is True


def test_dismissal_flag_not_set_for_violations():
    """Parser should set is_dismissal=False for actual violations."""
    from core.premise_parser import parse_premise
    parsed = parse_premise("Energy can be created from nothing")
    assert parsed["is_dismissal"] is False


def test_empty_premise():
    result = check("")
    assert result["verdict"] in ("CLEAN", "SUSPECT", "CORRUPTED")
    assert 0.0 <= result["score"] <= 1.0


def test_numeric_premise():
    """Numbers in premises shouldn't crash the system."""
    result = check("In 2024, we produced 500 kg of material with 100 joules")
    assert result["verdict"] in ("CLEAN", "SUSPECT", "CORRUPTED")
