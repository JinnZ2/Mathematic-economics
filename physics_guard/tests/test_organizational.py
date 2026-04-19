"""Test suite for PhysicsGuard v2 organizational constraint module."""

import pytest

from domains.organizational import OrgClaim, check_organization


@pytest.fixture
def parasitic_hierarchy():
    return OrgClaim(
        raw="Centralized corporate hierarchy is necessary for efficiency",
        structure_type="hierarchical",
        enforcement_ratio=0.45,
        adaptive_slack=0.08,
        node_count=10,
        single_point_deps=8,
        justification="necessary for efficiency",
    )


@pytest.fixture
def healthy_distributed():
    return OrgClaim(
        raw="Distributed team with clear protocols",
        structure_type="distributed",
        enforcement_ratio=0.10,
        adaptive_slack=0.30,
        node_count=12,
        single_point_deps=2,
        justification="adaptability",
    )


def test_parasitic_hierarchy_is_corrupted(parasitic_hierarchy):
    result = check_organization(parasitic_hierarchy)
    assert result.verdict == "CORRUPTED"
    assert len(result.flags) > 0


def test_healthy_distributed_is_clean(healthy_distributed):
    result = check_organization(healthy_distributed)
    assert result.verdict == "CLEAN"
    assert result.flags == []


def test_enforcement_flag(parasitic_hierarchy):
    result = check_organization(parasitic_hierarchy)
    assert "enforcement_energy_cost" in result.flags


def test_cascade_risk_flag(parasitic_hierarchy):
    result = check_organization(parasitic_hierarchy)
    assert "cascade_failure_risk" in result.flags


def test_justification_flag(parasitic_hierarchy):
    result = check_organization(parasitic_hierarchy)
    assert "justification_validity" in result.flags


def test_audit_trail_length(parasitic_hierarchy):
    result = check_organization(parasitic_hierarchy)
    assert len(result.audit) == 5  # 5 checks
