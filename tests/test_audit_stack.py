"""Smoke tests for the audit-stack modules landed on the
`claude/ai-externality-economics` branch series.

Each module carries its own `__main__`-block self-test with
assertions. This test file runs each as a subprocess and fails if
any exits non-zero, giving CI a single hook that covers all 20+
audit modules without requiring a rewrite into pytest-shaped
functions.

Modules are chosen for coverage of the entire branch series: the
externality meta-layer, the four delta-dimension trackers, the
validation layer, the trajectory-emitting audits, the disruption
survey, and the sanctuary module.

License: CC0
"""

import pathlib
import subprocess
import sys
import unittest


AUDIT_DIR = pathlib.Path(__file__).parent.parent / "audit"

MODULES = [
    # meta-layer + four delta-dimension trackers
    "withholding_externality",
    "skill_substrate_decay",
    "dependency_cascade_ledger",
    "training_corpus_degradation",
    # validation + downstream survey
    "self_measurement_compromise",
    "economics_disruption_map",
    # trajectory-emitting audits
    "scope_exemption_audit",
    "feedback_coupling_audit",
    "monoculture_collapse_predictor",
    "substrate_scope_validator",
    "substrate_scope_envelopes",
    "legacy_trap_detector",
    "breadcrumb_preservation",
    "temporal_compression",
    "structural_recurrence",
    "echo_collapse",
    "continuance_dynamics",
    # meta-audit + sanctuary + forensic
    "knowledge_decay_audit",
    "coherence_playground",
    "forensic_eroi",
]


class AuditStackSmoke(unittest.TestCase):
    """Run each audit module as `python audit/<name>.py` and require exit 0.

    Each module's `__main__` block exercises its own falsification /
    discrimination gates via `assert` statements. A non-zero exit
    means one of those gates fired.
    """

    def _run(self, module_name: str) -> None:
        path = AUDIT_DIR / f"{module_name}.py"
        self.assertTrue(path.exists(), f"module not found: {path}")
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode, 0,
            msg=(
                f"{module_name} exited {result.returncode}\n"
                f"--- stdout tail ---\n{result.stdout[-2000:]}\n"
                f"--- stderr tail ---\n{result.stderr[-2000:]}"
            ),
        )


def _make_test(module_name: str):
    def test(self):
        self._run(module_name)
    test.__name__ = f"test_{module_name}"
    test.__doc__ = f"Run audit/{module_name}.py; require exit 0."
    return test


for _m in MODULES:
    setattr(AuditStackSmoke, f"test_{_m}", _make_test(_m))


if __name__ == "__main__":
    unittest.main()
