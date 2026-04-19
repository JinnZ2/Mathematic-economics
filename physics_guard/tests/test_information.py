"""Test suite for PhysicsGuard information conservation domain."""

import pytest

from domains.information import InfoClaim, check_information


@pytest.fixture
def learning_from_nothing():
    return InfoClaim(
        raw="Model learns patterns without any training data",
        claim_type="learning",
        input_information=0.0,
        output_information=1.0,
        noise_level=0.0,
        justification="emergent intelligence",
    )


@pytest.fixture
def valid_learning():
    return InfoClaim(
        raw="Model trained on large dataset achieves good accuracy",
        claim_type="learning",
        input_information=1000.0,
        output_information=800.0,
        noise_level=0.1,
        justification="supervised learning",
    )


@pytest.fixture
def impossible_compression():
    return InfoClaim(
        raw="Lossless compression achieves 1000:1 ratio on random data",
        claim_type="compression",
        input_information=1.0,
        output_information=1000.0,
        noise_level=0.5,
        justification="novel algorithm",
    )


def test_learning_from_nothing_is_corrupted(learning_from_nothing):
    result = check_information(learning_from_nothing)
    assert result.verdict == "CORRUPTED"
    assert "no_free_lunch" in result.flags


def test_valid_learning_is_clean(valid_learning):
    result = check_information(valid_learning)
    assert result.verdict == "CLEAN"
    assert result.flags == []


def test_impossible_compression_caught(impossible_compression):
    result = check_information(impossible_compression)
    assert result.verdict != "CLEAN"
    assert "data_processing_inequality" in result.flags


def test_audit_trail(learning_from_nothing):
    result = check_information(learning_from_nothing)
    assert len(result.audit) == 4  # 4 checks
