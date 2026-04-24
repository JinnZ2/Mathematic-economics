"""Tests for audit/compute_paradigm.py — ternary encoding + registry.

Run from the repo root:
    python tests/test_compute_paradigm.py

Stdlib-only. Covers the two tiers independently so the ternary layer
doesn't require the registry and vice versa.
"""

from __future__ import annotations

import os
import sys
import unittest
from enum import Enum

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (REPO_ROOT, os.path.join(REPO_ROOT, "audit"),
          os.path.join(REPO_ROOT, "calibration")):
    if p not in sys.path:
        sys.path.insert(0, p)


class TernaryEncodingFromEnums(unittest.TestCase):

    def test_threshold_status(self):
        from compute_paradigm import encode_ternary

        class ThresholdStatus(Enum):
            BELOW = "below_threshold"
            WITHIN = "within_range"
            ABOVE = "above_threshold"
            UNKNOWN = "unknown"

        self.assertEqual(encode_ternary(ThresholdStatus.ABOVE), +1)
        self.assertEqual(encode_ternary(ThresholdStatus.WITHIN), 0)
        self.assertEqual(encode_ternary(ThresholdStatus.BELOW), -1)
        self.assertIsNone(encode_ternary(ThresholdStatus.UNKNOWN))

    def test_coupling_and_regime_and_scope(self):
        from compute_paradigm import encode_ternary
        from study_scope_audit import Coupling, Regime, ScopeStatus
        self.assertEqual(encode_ternary(Coupling.TIGHT), +1)
        self.assertEqual(encode_ternary(Coupling.MODERATE), 0)
        self.assertEqual(encode_ternary(Coupling.LOOSE), -1)
        self.assertIsNone(encode_ternary(Coupling.UNKNOWN))

        self.assertEqual(encode_ternary(Regime.STATIONARY), +1)
        self.assertEqual(encode_ternary(Regime.NON_STATIONARY), -1)
        self.assertIsNone(encode_ternary(Regime.UNKNOWN))

        self.assertEqual(encode_ternary(ScopeStatus.IN_SCOPE), +1)
        self.assertEqual(encode_ternary(ScopeStatus.OUT_OF_SCOPE), -1)
        self.assertIsNone(encode_ternary(ScopeStatus.SCOPE_UNDECLARED))

    def test_calibration_band(self):
        from compute_paradigm import encode_ternary
        from schema import Band
        self.assertEqual(encode_ternary(Band.GREEN), +1)
        self.assertEqual(encode_ternary(Band.YELLOW), 0)
        self.assertEqual(encode_ternary(Band.RED), -1)
        self.assertIsNone(encode_ternary(Band.EXTINCT))

    def test_verdict_band_strings(self):
        """Metabolic bridge returns raw strings, not enums."""
        from compute_paradigm import encode_ternary
        self.assertEqual(encode_ternary("GREEN"), +1)
        self.assertEqual(encode_ternary("AMBER"), 0)
        self.assertEqual(encode_ternary("RED"), -1)
        self.assertIsNone(encode_ternary("BLACK"))

    def test_unknown_inputs_raise(self):
        from compute_paradigm import encode_ternary

        class Bogus(Enum):
            FOO = "foo"

        with self.assertRaises(ValueError):
            encode_ternary(Bogus.FOO)
        with self.assertRaises(ValueError):
            encode_ternary("MAGENTA")
        with self.assertRaises(TypeError):
            encode_ternary(3.14)

    def test_register_new_mapping(self):
        from compute_paradigm import encode_ternary, register_ternary_mapping

        class NewState(Enum):
            HIGH = "h"
            MID = "m"
            LOW = "l"
            OFF = "off"

        register_ternary_mapping("NewState", {
            "HIGH": +1, "MID": 0, "LOW": -1, "OFF": None,
        })
        self.assertEqual(encode_ternary(NewState.HIGH), +1)
        self.assertIsNone(encode_ternary(NewState.OFF))

    def test_register_rejects_invalid_values(self):
        from compute_paradigm import register_ternary_mapping
        with self.assertRaises(ValueError):
            register_ternary_mapping("Bad", {"X": 2})


class WeightedTernaryScore(unittest.TestCase):

    def test_all_positive_yields_plus_one(self):
        from compute_paradigm import weighted_ternary_score
        self.assertAlmostEqual(
            weighted_ternary_score([(+1, 0.5), (+1, 0.5)]), 1.0)

    def test_all_negative_yields_minus_one(self):
        from compute_paradigm import weighted_ternary_score
        self.assertAlmostEqual(
            weighted_ternary_score([(-1, 0.3), (-1, 0.7)]), -1.0)

    def test_mixed_weighted(self):
        from compute_paradigm import weighted_ternary_score
        # +1 * 0.3 + 0 * 0.2 + -1 * 0.5 = -0.2
        self.assertAlmostEqual(
            weighted_ternary_score([(+1, 0.3), (0, 0.2), (-1, 0.5)]), -0.2)

    def test_none_entries_skipped_and_weight_renormalized(self):
        from compute_paradigm import weighted_ternary_score
        # (+1, 0.5) + skipped (None, 0.5) => +1 after renormalization
        self.assertAlmostEqual(
            weighted_ternary_score([(+1, 0.5), (None, 0.5)]), 1.0)

    def test_all_none_returns_none(self):
        from compute_paradigm import weighted_ternary_score
        self.assertIsNone(weighted_ternary_score([(None, 0.5), (None, 0.5)]))

    def test_zero_total_weight_returns_none(self):
        from compute_paradigm import weighted_ternary_score
        self.assertIsNone(weighted_ternary_score([(+1, 0.0)]))


class RegistryAPI(unittest.TestCase):

    def test_singleton_is_stable(self):
        from compute_paradigm import ComputeParadigmRegistry
        a = ComputeParadigmRegistry.instance()
        b = ComputeParadigmRegistry.instance()
        self.assertIs(a, b)

    def test_defaults_seed_13_equations(self):
        from compute_paradigm import ComputeParadigm, ComputeParadigmRegistry
        reg = ComputeParadigmRegistry.instance()
        for eq in ("VE_VL", "SID", "MSI", "MM", "HHI", "SD"):
            paradigms = reg.paradigms_for(eq)
            self.assertIn(ComputeParadigm.BINARY, paradigms)
            self.assertIn(ComputeParadigm.TERNARY, paradigms)
            self.assertIn(ComputeParadigm.STOCHASTIC, paradigms)

    def test_paradigms_for_unknown_is_empty(self):
        from compute_paradigm import ComputeParadigmRegistry
        self.assertEqual(
            ComputeParadigmRegistry.instance().paradigms_for("NotAThing"),
            [])

    def test_primitives_for_paradigm_includes_13_equations(self):
        from compute_paradigm import ComputeParadigm, ComputeParadigmRegistry
        primitives = ComputeParadigmRegistry.instance().primitives_for_paradigm(
            ComputeParadigm.TERNARY)
        for eq in ("VE_VL", "SID", "HHI", "OSDI"):
            self.assertIn(eq, primitives)

    def test_register_adds_binary_implicitly(self):
        from compute_paradigm import ComputeParadigm, ComputeParadigmRegistry
        reg = ComputeParadigmRegistry()  # fresh, not singleton
        reg.register("TestPrim", [ComputeParadigm.ANNEALING])
        paradigms = reg.paradigms_for("TestPrim")
        self.assertIn(ComputeParadigm.BINARY, paradigms)
        self.assertIn(ComputeParadigm.ANNEALING, paradigms)

    def test_summary_contains_all_primitives(self):
        from compute_paradigm import ComputeParadigmRegistry
        reg = ComputeParadigmRegistry.instance()
        summary = reg.summary()
        self.assertIn("VE_VL", summary)
        self.assertIn("OSDI", summary)
        self.assertIn("ternary", summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
