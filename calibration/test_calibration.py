"""
test_calibration.py -- falsification tests

Each test verifies that the falsifier claims actually flip the dimension.
If a test fails, the claim is wrong and the module needs revision.
"""

import unittest
from schema import Band
from calibration_audit import (
    score_bite_source, score_skin_in_game, score_witness_dependence,
    score_memorialization, score_friction_removal, run_calibration_audit,
)
from observation_dependence import run_observation_audit
from adaptation_debt import run_adaptation_debt_audit, compute_event_debt
from pipeline import run_unified_audit


class TestFalsifiers(unittest.TestCase):
    """Each falsifier claim is an empirical prediction. Test it."""

    def test_bite_source_falsifier(self):
        """Claim: impersonal >70% flips to GREEN."""
        events = [
            {"type": "personal", "count": 2},
            {"type": "impersonal", "count": 8},
        ]
        result = score_bite_source(events)
        self.assertEqual(result.band, Band.GREEN,
                         f"Expected GREEN, got {result.band}")

    def test_skin_in_game_falsifier(self):
        """Claim: mean hops <1.2 flips to GREEN."""
        decisions = [
            {"decision_maker": "a", "consequence_hops": 0},
            {"decision_maker": "b", "consequence_hops": 1},
            {"decision_maker": "c", "consequence_hops": 1},
        ]
        result = score_skin_in_game(decisions)
        self.assertEqual(result.band, Band.GREEN)

    def test_witness_dependence_falsifier(self):
        """Claim: >70% silent flips to GREEN."""
        skills = [
            {"skill": f"s{i}", "requires_witness": False} for i in range(8)
        ] + [
            {"skill": f"s{i}", "requires_witness": True} for i in range(2)
        ]
        result = score_witness_dependence(skills)
        self.assertEqual(result.band, Band.GREEN)

    def test_memorialization_high_prevalence_kills_signal(self):
        """Claim: high prevalence zeros out extinction signal."""
        memorialized = [
            {"skill": "s1", "praise_volume": 1000,
             "estimated_prevalence": 0.9},
        ]
        result = score_memorialization(memorialized)
        # signal = 1.0 * 0.1 = 0.1 -> GREEN
        self.assertLess(result.score, 0.3)

    def test_friction_preservation_flips(self):
        """Claim: >70% preserved flips adaptation_debt preservation to GREEN."""
        events = [
            {"name": f"e{i}", "domain": "institutional",
             "initial_load": 0.5, "removed": False,
             "years_since_removed": 0.0}
            for i in range(8)
        ] + [
            {"name": f"e{i}", "domain": "institutional",
             "initial_load": 0.5, "removed": True,
             "years_since_removed": 2.0}
            for i in range(2)
        ]
        report = run_adaptation_debt_audit({
            "system_id": "t", "friction_events": events,
        })
        preservation = next(d for d in report.dimensions
                            if d.name == "friction_preservation")
        self.assertEqual(preservation.band, Band.GREEN)


class TestCompoundingModel(unittest.TestCase):
    """The debt compounding is a concrete prediction. Verify the math."""

    def test_zero_time_equals_initial_load(self):
        """At t=0, debt = initial_load exactly."""
        event = {"initial_load": 0.5, "removed": True,
                 "years_since_removed": 0.0, "domain": "institutional"}
        self.assertAlmostEqual(compute_event_debt(event), 0.5, places=5)

    def test_preserved_friction_has_zero_debt(self):
        """Preserved friction = 0 debt regardless of time."""
        event = {"initial_load": 1.0, "removed": False,
                 "years_since_removed": 100.0, "domain": "institutional"}
        self.assertEqual(compute_event_debt(event), 0.0)

    def test_compounding_is_monotonic(self):
        """Debt must grow with time for removed events."""
        e1 = {"initial_load": 0.5, "removed": True,
              "years_since_removed": 1.0, "domain": "institutional"}
        e2 = {"initial_load": 0.5, "removed": True,
              "years_since_removed": 10.0, "domain": "institutional"}
        self.assertLess(compute_event_debt(e1), compute_event_debt(e2))


class TestPipeline(unittest.TestCase):
    """End-to-end pipeline coherence."""

    def test_minimal_input_produces_valid_output(self):
        """Pipeline must not crash on sparse input."""
        result = run_unified_audit({"system_id": "sparse"})
        self.assertIn("unified_score", result)
        self.assertIn("unified_band", result)

    def test_calibrated_system_scores_green(self):
        """A fully calibrated system must score GREEN."""
        calibrated_system = {
            "system_id": "calibrated",
            "feedback_events": [
                {"type": "personal", "count": 1},
                {"type": "impersonal", "count": 9},
            ],
            "decisions": [
                {"decision_maker": "a", "consequence_hops": 0},
                {"decision_maker": "b", "consequence_hops": 0},
            ],
            "skills_observed": [
                {"skill": f"s{i}", "requires_witness": False}
                for i in range(8)
            ],
            "friction_events": [
                {"name": f"f{i}", "domain": "institutional",
                 "initial_load": 0.5, "removed": False,
                 "years_since_removed": 0.0}
                for i in range(5)
            ],
            "skill_log": [
                {"skill": f"s{i}", "timestamp": "2026-01",
                 "context": "silent", "consequence_real": True}
                for i in range(10)
            ],
        }
        result = run_unified_audit(calibrated_system)
        self.assertIn(result["unified_band"], ("calibrating", "drifting"),
                      f"Calibrated system scored {result['unified_band']}")

    def test_domesticated_system_scores_red(self):
        """A fully domesticated system must score RED or EXTINCT."""
        domesticated = {
            "system_id": "domesticated",
            "feedback_events": [
                {"type": "personal", "count": 9},
                {"type": "impersonal", "count": 1},
            ],
            "decisions": [
                {"decision_maker": "a", "consequence_hops": 5},
                {"decision_maker": "b", "consequence_hops": 6},
            ],
            "skills_observed": [
                {"skill": f"s{i}", "requires_witness": True}
                for i in range(8)
            ],
            "memorialized_skills": [
                {"skill": "basic_competence", "praise_volume": 900,
                 "estimated_prevalence": 0.05},
            ],
            "friction_events": [
                {"name": f"f{i}", "domain": "institutional",
                 "initial_load": 0.8, "removed": True,
                 "years_since_removed": 10.0}
                for i in range(5)
            ],
        }
        result = run_unified_audit(domesticated)
        self.assertIn(result["unified_band"], ("mauling", "memorialized_only"),
                      f"Domesticated system scored {result['unified_band']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
