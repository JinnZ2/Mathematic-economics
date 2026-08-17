"""Tests for schemas/claim_contract.py at CONTRACT_VERSION 1.1.0.

Covers the pre-existing shape (Claim/ClaimBounds/CycleClass) plus the
1.1.0 additions: CanonStatus, Confidence, Graduation, the
canon-status -> graduation coherence rule, and is_validated() /
needs_graduation() semantics.

License: CC0
"""

import os
import sys
import unittest

# Same bootstrap as tests/test_bridges.py and tests/test_accounting.py, so
# `python tests/test_claim_contract.py` works from the repo root without
# PYTHONPATH. The repo is intentionally not packaged.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from schemas.claim_contract import (
    CONTRACT_VERSION,
    Claim,
    ClaimBounds,
    CycleClass,
    CanonStatus,
    Confidence,
    Graduation,
)


VALID_BOUNDS = ClaimBounds(
    spatial="US commercial trucking corridors",
    temporal="quarterly",
    scale="fleet-level aggregate",
)


def _minimal_claim(**overrides) -> Claim:
    """Construct a valid Claim; overrides can substitute any field."""
    defaults = dict(
        observable="labor share",
        rate_equation="d(labor_share)/dt",
        bounds=VALID_BOUNDS,
        conditions=["fully-employed labor market"],
        invalid_if=["labor share ceases to be well-defined"],
        measured_by=["BLS PRS85006173"],
        cycle_class=CycleClass.SEASON,
    )
    defaults.update(overrides)
    return Claim(**defaults)


class VersionSurface(unittest.TestCase):
    def test_version_bumped_to_1_1_0(self):
        self.assertEqual(CONTRACT_VERSION, "1.1.0")


class CanonStatusEnum(unittest.TestCase):
    def test_five_states(self):
        self.assertEqual(len(CanonStatus), 5)
        self.assertEqual(
            {s.value for s in CanonStatus},
            {"mainstream", "emerging", "contested", "frontier", "revolutionary"},
        )


class ConfidenceEnum(unittest.TestCase):
    def test_four_states(self):
        self.assertEqual(len(Confidence), 4)
        self.assertEqual(
            {s.value for s in Confidence},
            {"unverified", "low", "medium", "high"},
        )


class GraduationValidation(unittest.TestCase):
    def test_valid_graduation(self):
        g = Graduation(
            justification="Reason spanning multiple lines of evidence.",
            provenance=["Smith 2020", "Jones 2022 replication"],
            passing_tests=["tests.test_x::test_y"],
        )
        self.assertFalse(g.validated)

    def test_empty_justification_rejected(self):
        with self.assertRaisesRegex(ValueError, "justification"):
            Graduation(
                justification="   ",
                provenance=["Smith 2020"],
                passing_tests=["tests.test_x"],
            )

    def test_empty_provenance_rejected(self):
        with self.assertRaisesRegex(ValueError, "provenance"):
            Graduation(
                justification="A reason.",
                provenance=[],
                passing_tests=["tests.test_x"],
            )

    def test_empty_passing_tests_rejected(self):
        with self.assertRaisesRegex(ValueError, "passing_tests"):
            Graduation(
                justification="A reason.",
                provenance=["Smith 2020"],
                passing_tests=[],
            )


class BackwardCompatibility(unittest.TestCase):
    """Claims constructed with the 1.0.0 field set must still work."""

    def test_minimal_claim_no_new_fields(self):
        c = _minimal_claim()
        self.assertIsNone(c.canon_status)
        self.assertIsNone(c.graduation)
        self.assertIsNone(c.confidence)

    def test_is_validated_defaults_true_when_canon_unspecified(self):
        c = _minimal_claim()
        # No canon_status -> treated as validated by construction
        self.assertTrue(c.is_validated())

    def test_needs_graduation_false_when_canon_unspecified(self):
        c = _minimal_claim()
        self.assertFalse(c.needs_graduation())


class CanonGraduationCoherence(unittest.TestCase):
    def test_mainstream_claim_no_graduation_required(self):
        c = _minimal_claim(canon_status=CanonStatus.MAINSTREAM)
        self.assertTrue(c.is_validated())
        self.assertFalse(c.needs_graduation())

    def test_emerging_claim_no_graduation_required(self):
        c = _minimal_claim(canon_status=CanonStatus.EMERGING)
        self.assertTrue(c.is_validated())

    def test_contested_claim_no_graduation_required(self):
        c = _minimal_claim(canon_status=CanonStatus.CONTESTED)
        self.assertTrue(c.is_validated())

    def test_frontier_without_graduation_raises(self):
        with self.assertRaisesRegex(ValueError, "Graduation"):
            _minimal_claim(canon_status=CanonStatus.FRONTIER)

    def test_revolutionary_without_graduation_raises(self):
        with self.assertRaisesRegex(ValueError, "Graduation"):
            _minimal_claim(canon_status=CanonStatus.REVOLUTIONARY)

    def test_frontier_with_graduation_ok_but_unvalidated(self):
        g = Graduation(
            justification="Novel mechanism, sparse but converging evidence.",
            provenance=["Kosmyna 2025", "internal replication log 2026-04"],
            passing_tests=["tests.test_skill_substrate_decay::test_S5"],
        )
        c = _minimal_claim(canon_status=CanonStatus.FRONTIER, graduation=g)
        self.assertTrue(c.needs_graduation())
        # Cannot self-validate: graduation.validated is False
        self.assertFalse(c.is_validated())

    def test_frontier_with_validated_graduation(self):
        g = Graduation(
            justification="Novel mechanism, sparse but converging evidence.",
            provenance=["Kosmyna 2025"],
            passing_tests=["tests.test_skill_substrate_decay::test_S5"],
            validated=True,
        )
        c = _minimal_claim(canon_status=CanonStatus.FRONTIER, graduation=g)
        self.assertTrue(c.is_validated())

    def test_revolutionary_with_graduation_ok_but_unvalidated(self):
        g = Graduation(
            justification=(
                "Proposes a substrate-side externality dimension that has no "
                "correspondence in mainstream economic accounting. The physics "
                "departure is not against a conservation law but against the "
                "canon of measurement."
            ),
            provenance=[
                "Shumailov 2023 model collapse",
                "Kosmyna 2025 EEG",
                "internal audit stack: audit/withholding_externality.py",
            ],
            passing_tests=[
                "tests.test_audit_stack::test_withholding_externality",
                "tests.test_audit_stack::test_training_corpus_degradation",
            ],
        )
        c = _minimal_claim(canon_status=CanonStatus.REVOLUTIONARY, graduation=g)
        self.assertTrue(c.needs_graduation())
        self.assertFalse(c.is_validated())


class ConfidenceOnClaim(unittest.TestCase):
    def test_confidence_optional(self):
        c1 = _minimal_claim()
        self.assertIsNone(c1.confidence)
        c2 = _minimal_claim(confidence=Confidence.MEDIUM)
        self.assertEqual(c2.confidence, Confidence.MEDIUM)

    def test_unverified_is_distinct_from_none(self):
        # Explicit UNVERIFIED signals "checked and found not-yet-verified"
        # while None signals "field never set."
        c_none = _minimal_claim()
        c_unv = _minimal_claim(confidence=Confidence.UNVERIFIED)
        self.assertIsNone(c_none.confidence)
        self.assertEqual(c_unv.confidence, Confidence.UNVERIFIED)


class Serialization(unittest.TestCase):
    def test_to_from_dict_roundtrip_no_new_fields(self):
        c1 = _minimal_claim()
        d = c1.to_dict()
        c2 = Claim.from_dict(d)
        self.assertEqual(c1, c2)

    def test_to_from_dict_roundtrip_with_canon_and_confidence(self):
        c1 = _minimal_claim(
            canon_status=CanonStatus.EMERGING,
            confidence=Confidence.MEDIUM,
        )
        d = c1.to_dict()
        self.assertEqual(d["canon_status"], "emerging")
        self.assertEqual(d["confidence"], "medium")
        c2 = Claim.from_dict(d)
        self.assertEqual(c1.canon_status, c2.canon_status)
        self.assertEqual(c1.confidence, c2.confidence)

    def test_to_from_dict_roundtrip_frontier_with_graduation(self):
        g = Graduation(
            justification="Novel mechanism with converging evidence.",
            provenance=["src 1", "src 2"],
            passing_tests=["t1"],
            validated=True,
        )
        c1 = _minimal_claim(
            canon_status=CanonStatus.FRONTIER,
            graduation=g,
            confidence=Confidence.HIGH,
        )
        d = c1.to_dict()
        c2 = Claim.from_dict(d)
        self.assertEqual(c2.canon_status, CanonStatus.FRONTIER)
        self.assertIsNotNone(c2.graduation)
        self.assertEqual(c2.graduation.justification, g.justification)
        self.assertEqual(c2.graduation.provenance, g.provenance)
        self.assertEqual(c2.graduation.passing_tests, g.passing_tests)
        self.assertTrue(c2.graduation.validated)
        self.assertEqual(c2.confidence, Confidence.HIGH)
        self.assertTrue(c2.is_validated())


class ExistingValidationStillHolds(unittest.TestCase):
    """The 1.0.0 required-field checks still fire."""

    def test_empty_observable_rejected(self):
        with self.assertRaisesRegex(ValueError, "observable"):
            _minimal_claim(observable="")

    def test_empty_conditions_rejected(self):
        with self.assertRaisesRegex(ValueError, "conditions"):
            _minimal_claim(conditions=[])

    def test_empty_invalid_if_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid_if"):
            _minimal_claim(invalid_if=[])

    def test_empty_measured_by_rejected(self):
        with self.assertRaisesRegex(ValueError, "measured_by"):
            _minimal_claim(measured_by=[])


if __name__ == "__main__":
    unittest.main()
