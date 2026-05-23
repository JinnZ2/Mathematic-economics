"""
test_prediction_registry.py — emit + chain integrity invariants

Covers:
  - emit produces a chain whose chain_hash verifies under
    compute_calibration.verify_chain
  - tampering with any past entry breaks the chain at that point
  - per-domain accuracy is computed independently (no aggregate
    cross-domain scores)
  - override outcomes count correctly when human_override.occurred
    is True and an actual_outcome is recorded

License: CC0-1.0
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import emit_prediction        # noqa: E402
import compute_calibration    # noqa: E402


class EmitChainIntegrityTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = Path(self.tmpdir) / "predictions_registry.jsonl"

    def tearDown(self):
        for p in Path(self.tmpdir).iterdir():
            p.unlink()
        os.rmdir(self.tmpdir)

    def _emit(self, **kwargs):
        defaults = dict(
            domain="test_domain",
            claim="test claim",
            probability=0.75,
            interval_low=0.6,
            interval_high=0.9,
            evidence=["test evidence"],
            falsifier="test falsifier",
            window="P1Y",
            model_id="test-model",
            path=self.path,
            secret="test-secret",
        )
        defaults.update(kwargs)
        return emit_prediction.emit(**defaults)

    def test_empty_registry_verifies(self):
        entries = compute_calibration.load_entries(self.path)
        ok, errors = compute_calibration.verify_chain(entries, "test-secret")
        self.assertTrue(ok)
        self.assertEqual(entries, [])

    def test_single_entry_chain_verifies(self):
        self._emit()
        entries = compute_calibration.load_entries(self.path)
        ok, errors = compute_calibration.verify_chain(entries, "test-secret")
        self.assertTrue(ok, msg=errors)
        self.assertEqual(len(entries), 1)

    def test_multi_entry_chain_verifies(self):
        for i in range(5):
            self._emit(claim=f"claim {i}")
        entries = compute_calibration.load_entries(self.path)
        ok, errors = compute_calibration.verify_chain(entries, "test-secret")
        self.assertTrue(ok, msg=errors)
        self.assertEqual(len(entries), 5)

    def test_tampering_breaks_chain(self):
        for i in range(3):
            self._emit(claim=f"claim {i}")
        entries = compute_calibration.load_entries(self.path)
        # Tamper with entry 1's claim
        entries[1]["claim"] = "modified claim"
        with open(self.path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        reloaded = compute_calibration.load_entries(self.path)
        ok, errors = compute_calibration.verify_chain(reloaded, "test-secret")
        self.assertFalse(ok)
        self.assertTrue(any("entry 1" in e for e in errors))

    def test_wrong_secret_fails_verification(self):
        self._emit()
        entries = compute_calibration.load_entries(self.path)
        ok, _ = compute_calibration.verify_chain(entries, "wrong-secret")
        self.assertFalse(ok)


class AttestationTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = Path(self.tmpdir) / "predictions_registry.jsonl"

    def tearDown(self):
        for p in Path(self.tmpdir).iterdir():
            p.unlink()
        os.rmdir(self.tmpdir)

    def _emit(self, **kwargs):
        defaults = dict(
            domain="test_domain",
            claim="test claim",
            probability=0.75,
            interval_low=0.6, interval_high=0.9,
            evidence=["test"], falsifier="test",
            window="P1Y", model_id="test",
            path=self.path, secret="s",
        )
        defaults.update(kwargs)
        return emit_prediction.emit(**defaults)

    def _resolve_last(self, assessment, override_occurred=False):
        """Hand-edit the last entry to add a resolution. Used only
        for testing the calibration computation."""
        entries = compute_calibration.load_entries(self.path)
        entries[-1]["accuracy_assessment"] = assessment
        entries[-1]["actual_outcome"] = "resolved by test"
        if override_occurred:
            entries[-1]["human_override"] = {
                "occurred": True,
                "reasoning": "test override",
                "decision": "human chose otherwise",
            }
        with open(self.path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

    def test_per_domain_accuracy_no_cross_domain_aggregate(self):
        self._emit(domain="weather", probability=0.8)
        self._resolve_last("correct")
        self._emit(domain="finance", probability=0.7)
        self._resolve_last("incorrect")
        entries = compute_calibration.load_entries(self.path)
        attest = compute_calibration.compose_attestation(entries)
        self.assertIn("weather", attest["domain_accuracy"])
        self.assertIn("finance", attest["domain_accuracy"])
        self.assertEqual(attest["domain_accuracy"]["weather"]["correct"], 1)
        self.assertEqual(attest["domain_accuracy"]["finance"]["incorrect"], 1)
        # No aggregate field
        self.assertNotIn("aggregate_accuracy", attest)

    def test_override_outcome_counted_when_model_was_right(self):
        self._emit(domain="d1", probability=0.8)
        self._resolve_last("correct", override_occurred=True)
        entries = compute_calibration.load_entries(self.path)
        attest = compute_calibration.compose_attestation(entries)
        self.assertEqual(
            attest["override_outcomes"]["human_overrode_and_was_wrong"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
