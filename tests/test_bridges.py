"""Integration tests for the three PhysicsGuard bridges.

Run from the repo root:
    python tests/test_bridges.py

Uses unittest (no pytest dependency) so it runs identically locally and in
CI without extra installs. Each test is defensive: if the underlying module
can't be imported in the environment (e.g. numpy missing for equation_bridge),
the test skips rather than fails. The goal is to prove the bridge wiring
works whenever its dependencies are present, not to retest the upstream
modules themselves.
"""

from __future__ import annotations

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (
    REPO_ROOT,
    os.path.join(REPO_ROOT, "audit"),
    os.path.join(REPO_ROOT, "AI"),
    os.path.join(REPO_ROOT, "physics_guard"),
):
    if p not in sys.path:
        sys.path.insert(0, p)


class BridgeEfficiencyReport(unittest.TestCase):
    """audit/efficiency_report_audit.py routes headline claims through
    PhysicsGuard before the Six Sigma audit."""

    def test_physics_guard_detected(self):
        import efficiency_report_audit as era
        self.assertTrue(era._HAS_PHYSICS_GUARD,
                        "physics_guard should be importable in a default checkout")

    def test_audit_includes_physics_verdict(self):
        import efficiency_report_audit as era
        from system_audit import SixSigmaAudit
        result = era.audit_efficiency_report("precision_ag", SixSigmaAudit())
        self.assertIn("physics_verdict", result)
        verdict = result["physics_verdict"]
        self.assertIsNotNone(verdict, "physics_verdict should be populated when PG is present")
        for key in ("verdict", "score", "flags", "reason", "confidence"):
            self.assertIn(key, verdict)
        self.assertIn(verdict["verdict"], {"CLEAN", "SUSPECT", "CORRUPTED"})

    def test_audit_still_returns_when_pg_absent(self):
        """Monkey-patch _HAS_PHYSICS_GUARD=False and confirm graceful fallback."""
        import efficiency_report_audit as era
        from system_audit import SixSigmaAudit
        original = era._HAS_PHYSICS_GUARD
        try:
            era._HAS_PHYSICS_GUARD = False
            result = era.audit_efficiency_report("precision_ag", SixSigmaAudit())
            self.assertIsNone(result["physics_verdict"])
            self.assertIn("audit", result)  # rest of audit still present
        finally:
            era._HAS_PHYSICS_GUARD = original


class BridgeDelusionChecker(unittest.TestCase):
    """audit/ai_delusion_econ_checker.py keeps the regex path and adds
    a PhysicsGuard verdict per entry via analyze_dataset_with_physics."""

    SAMPLE = [
        "The company maximized efficiency beyond 100%.",
        "Top-down management ensures market price is the true value.",
        "Productivity and optimization drive economic success.",
    ]

    def test_physics_guard_detected(self):
        import ai_delusion_econ_checker as adec
        self.assertTrue(adec._HAS_PHYSICS_GUARD)

    def test_augmented_output_shape(self):
        import ai_delusion_econ_checker as adec
        augmented = adec.analyze_dataset_with_physics(self.SAMPLE)
        self.assertTrue(augmented["physics_available"])
        self.assertIn("delusion_counts", augmented)
        self.assertIn("plausibility_flags", augmented)
        self.assertEqual(len(augmented["physics_verdicts"]), len(self.SAMPLE))
        for v in augmented["physics_verdicts"]:
            self.assertIn(v["verdict"], {"CLEAN", "SUSPECT", "CORRUPTED"})

    def test_regex_path_unchanged(self):
        """The original analyze_dataset output must be preserved intact."""
        import ai_delusion_econ_checker as adec
        augmented = adec.analyze_dataset_with_physics(self.SAMPLE)
        original = adec.analyze_dataset(self.SAMPLE)
        self.assertEqual(augmented["delusion_counts"], original["delusion_counts"])
        self.assertEqual(augmented["plausibility_flags"], original["plausibility_flags"])


class BridgeOrganizationalPhysics(unittest.TestCase):
    """AI/equation_bridge.py: SystemMeasurement.check_organizational_physics
    maps measured equations into a PhysicsGuard OrgClaim and runs
    check_organization."""

    def setUp(self):
        try:
            import equation_bridge  # noqa: F401
        except ModuleNotFoundError as e:
            self.skipTest(f"equation_bridge import requires numpy: {e}")
        except Exception as e:
            self.skipTest(f"equation_bridge not importable in this env: {e}")

    def test_returns_none_when_pg_absent(self):
        import equation_bridge as eb
        sm = eb.SystemMeasurement()
        original = eb._HAS_PHYSICS_GUARD
        try:
            eb._HAS_PHYSICS_GUARD = False
            self.assertIsNone(sm.check_organizational_physics(node_count=5))
        finally:
            eb._HAS_PHYSICS_GUARD = original

    def test_hhi_derives_hierarchical_structure(self):
        import equation_bridge as eb
        sm = eb.SystemMeasurement()
        # HHI uses percentage-points squared (standard convention), so
        # thresholds are 1500 / 2500. 80/10/10 market shares -> HHI = 6600.
        sm.add(eb.compute_hhi([80.0, 10.0, 10.0]))
        result = sm.check_organizational_physics(
            node_count=10, single_point_deps=8, justification="efficiency"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["derived_structure_type"], "hierarchical")
        self.assertIn(result["verdict"], {"CLEAN", "SUSPECT", "CORRUPTED"})

    def test_er_maps_to_enforcement_ratio(self):
        import equation_bridge as eb
        sm = eb.SystemMeasurement()
        sm.add(eb.compute_er(revenue=100.0, labor_costs=20.0))  # ER = 0.80
        result = sm.check_organizational_physics(node_count=5, single_point_deps=2)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["derived_enforcement_ratio"], 0.80, places=2)
        self.assertAlmostEqual(result["derived_adaptive_slack"], 0.20, places=2)
        self.assertIn("enforcement_energy_cost", result["flags"])

    def test_low_hhi_derives_distributed(self):
        import equation_bridge as eb
        sm = eb.SystemMeasurement()
        # 10 equal competitors -> HHI = 10 * 10^2 = 1000, below 1500.
        sm.add(eb.compute_hhi([10.0] * 10))
        result = sm.check_organizational_physics(node_count=10)
        self.assertEqual(result["derived_structure_type"], "distributed")


class BridgeMetabolicAccounting(unittest.TestCase):
    """audit/metabolic_bridge.py is a defensive bridge to JinnZ2/metabolic-accounting.

    Unlike physics_guard, metabolic-accounting is NOT vendored in this repo,
    so the bridge gracefully reports _HAS_METABOLIC_ACCOUNTING=False on a
    default checkout. These tests assert the bridge is always importable
    and that its consumers degrade cleanly.
    """

    def test_bridge_module_always_importable(self):
        import metabolic_bridge as mb
        self.assertIsInstance(mb._HAS_METABOLIC_ACCOUNTING, bool)

    def test_metabolic_check_returns_none_when_absent(self):
        import metabolic_bridge as mb
        original = mb._HAS_METABOLIC_ACCOUNTING
        try:
            mb._HAS_METABOLIC_ACCOUNTING = False
            self.assertIsNone(mb.metabolic_check(revenue=1000.0,
                                                direct_operating_cost=600.0))
        finally:
            mb._HAS_METABOLIC_ACCOUNTING = original

    def test_stress_mapping_scales_field_scenario(self):
        """stress_from_field_scenario does not require the upstream package."""
        import metabolic_bridge as mb
        scenario = {"soil_trend": -0.05, "water_retention": 0.45,
                    "disturbance": 0.30, "nutrient_density": 0.40}
        stress = mb.stress_from_field_scenario(scenario)
        self.assertAlmostEqual(stress[("site_soil", "carbon_fraction")], 5.0)
        self.assertAlmostEqual(stress[("site_air", "particulate_load")], 3.0)
        self.assertAlmostEqual(stress[("site_water", "aquifer_level")], 5.5)
        self.assertAlmostEqual(stress[("site_biology", "pollinator_index")], 6.0)
        # Positive soil_trend should not register as stress.
        s2 = mb.stress_from_field_scenario({"soil_trend": 0.1})
        self.assertEqual(s2[("site_soil", "carbon_fraction")], 0.0)

    def test_efficiency_audit_includes_metabolic_key(self):
        """The audit result must always include a 'metabolic_verdict' key,
        whether or not metabolic-accounting is importable."""
        import efficiency_report_audit as era
        from system_audit import SixSigmaAudit
        result = era.audit_efficiency_report("precision_ag", SixSigmaAudit())
        self.assertIn("metabolic_verdict", result)
        verdict = result["metabolic_verdict"]
        if verdict is None:
            return  # bridge inactive on this checkout — graceful degrade
        for key in ("sustainable_yield_signal", "basin_trajectory",
                    "metabolic_profit", "regeneration_debt"):
            self.assertIn(key, verdict)
        self.assertIn(verdict["sustainable_yield_signal"],
                      {"GREEN", "AMBER", "RED", "BLACK"})

    def test_equation_bridge_metabolic_check_returns_none_when_absent(self):
        try:
            import equation_bridge as eb
        except ModuleNotFoundError as e:
            self.skipTest(f"equation_bridge import requires numpy: {e}")
        sm = eb.SystemMeasurement()
        original = eb._HAS_METABOLIC_BRIDGE
        try:
            eb._HAS_METABOLIC_BRIDGE = False
            self.assertIsNone(sm.check_metabolic_health())
        finally:
            eb._HAS_METABOLIC_BRIDGE = original

    def test_equation_bridge_uses_er_for_operating_cost(self):
        """When ER is measured, operating_cost should be revenue * (1-ER).
        We verify the derivation by mocking metabolic_check to capture args."""
        try:
            import equation_bridge as eb
        except ModuleNotFoundError as e:
            self.skipTest(f"equation_bridge import requires numpy: {e}")
        sm = eb.SystemMeasurement()
        sm.add(eb.compute_er(revenue=100.0, labor_costs=20.0))  # ER = 0.80

        captured = {}

        def fake_check(**kwargs):
            captured.update(kwargs)
            return {"sustainable_yield_signal": "RED", "basin_trajectory": "STABLE"}

        original_has = eb._HAS_METABOLIC_BRIDGE
        original_mb = eb._mb
        try:
            eb._HAS_METABOLIC_BRIDGE = True

            class _StubBridge:
                _HAS_METABOLIC_ACCOUNTING = True
                metabolic_check = staticmethod(fake_check)

            eb._mb = _StubBridge
            result = sm.check_metabolic_health(revenue=100.0)
            self.assertIsNotNone(result)
            # ER = 0.80 -> operating_cost = 100 * (1 - 0.80) = 20.0
            self.assertAlmostEqual(captured["direct_operating_cost"], 20.0)
            self.assertAlmostEqual(captured["revenue"], 100.0)
        finally:
            eb._HAS_METABOLIC_BRIDGE = original_has
            eb._mb = original_mb


class BridgeMoneySignal(unittest.TestCase):
    """audit/money_signal_bridge.py links Math-Econ to the money_signal
    subsystem of metabolic-accounting. Like metabolic_bridge, the upstream
    is NOT vendored, so the default-checkout behavior is _HAS_MONEY_SIGNAL=False.
    """

    def test_bridge_module_always_importable(self):
        import money_signal_bridge as msb
        self.assertIsInstance(msb._HAS_MONEY_SIGNAL, bool)
        self.assertTrue(msb.UPSTREAM_PINNED_COMMIT)

    def test_metrics_returns_none_when_absent(self):
        import money_signal_bridge as msb
        original = msb._HAS_MONEY_SIGNAL
        try:
            msb._HAS_MONEY_SIGNAL = False
            self.assertIsNone(msb.money_signal_metrics())
            self.assertIsNone(msb.default_context())
        finally:
            msb._HAS_MONEY_SIGNAL = original

    def test_efficiency_audit_includes_money_signal_key(self):
        """The audit result must always include a 'money_signal_metrics' key,
        whether or not money_signal is importable."""
        import efficiency_report_audit as era
        from system_audit import SixSigmaAudit
        result = era.audit_efficiency_report("precision_ag", SixSigmaAudit())
        self.assertIn("money_signal_metrics", result)
        metrics = result["money_signal_metrics"]
        if metrics is None:
            return  # bridge inactive — graceful degrade
        for key in ("minsky", "magnitude", "has_sign_flips"):
            self.assertIn(key, metrics)
        self.assertIsInstance(metrics["has_sign_flips"], bool)

    def test_equation_bridge_money_signal_returns_none_when_absent(self):
        try:
            import equation_bridge as eb
        except ModuleNotFoundError as e:
            self.skipTest(f"equation_bridge import requires numpy: {e}")
        sm = eb.SystemMeasurement()
        original = eb._HAS_MONEY_SIGNAL_BRIDGE
        try:
            eb._HAS_MONEY_SIGNAL_BRIDGE = False
            self.assertIsNone(sm.check_money_signal())
        finally:
            eb._HAS_MONEY_SIGNAL_BRIDGE = original

    def test_equation_bridge_money_signal_delegates(self):
        """When the bridge is active, check_money_signal forwards ctx to
        money_signal_bridge.money_signal_metrics."""
        try:
            import equation_bridge as eb
        except ModuleNotFoundError as e:
            self.skipTest(f"equation_bridge import requires numpy: {e}")
        sm = eb.SystemMeasurement()

        captured = {}

        def fake_metrics(ctx=None):
            captured["ctx"] = ctx
            return {"minsky": 1.0, "magnitude": 0.5, "has_sign_flips": False}

        original_has = eb._HAS_MONEY_SIGNAL_BRIDGE
        original_msb = eb._msb
        try:
            eb._HAS_MONEY_SIGNAL_BRIDGE = True

            class _StubBridge:
                _HAS_MONEY_SIGNAL = True
                money_signal_metrics = staticmethod(fake_metrics)

            eb._msb = _StubBridge
            sentinel = object()
            result = sm.check_money_signal(ctx=sentinel)
            self.assertEqual(result["minsky"], 1.0)
            self.assertIs(captured["ctx"], sentinel)
        finally:
            eb._HAS_MONEY_SIGNAL_BRIDGE = original_has
            eb._msb = original_msb


class ImportDirectionInvariant(unittest.TestCase):
    """Vendored subtrees must not runtime-import Math-Econ.

    Math-Econ has no requirements.txt and is not pip-installable; it is
    intentionally research code. The vendored snapshots (physics_guard/,
    calibration/, core/) must stay pure so they can be re-synced from
    their upstream repos without accidentally pulling Math-Econ with them.

    This test scans every .py file under each vendored subtree and asserts
    that none of them import Math-Econ-specific modules.
    """

    # Module names that are unique to Math-Econ. If a vendored file imports
    # any of these at the top level, it has crossed the boundary.
    ME_MODULE_NAMES = frozenset({
        # audit/
        "field_system", "system_audit", "accountability_protocol",
        "certification_protocol", "deflection_pattern_analyzer",
        "epistemic_cascade", "implementation_layer", "incentive_structure",
        "incentives_audit", "efficiency_report_audit",
        "ai_delusion_econ_checker", "metabolic_bridge",
        "money_signal_bridge",
        # AI/
        "money_free_model", "semantic_decontamination", "temporal_energy",
        "equation_bridge",
        # schemas/
        "schemas", "field_system_contract",
        # data/
        "fetch_and_compute", "sensitivity_analysis",
    })

    VENDORED_SUBTREES = ("physics_guard", "calibration", "core")

    def _collect_imports(self, path):
        """Return the set of top-level module names imported by `path`."""
        import ast
        with open(path, "r", encoding="utf-8") as fh:
            try:
                tree = ast.parse(fh.read(), filename=path)
            except SyntaxError:
                return set()
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    names.add(node.module.split(".")[0])
        return names

    def test_vendored_subtrees_do_not_import_math_econ(self):
        repo_root = REPO_ROOT
        offenders = []
        for subtree in self.VENDORED_SUBTREES:
            subtree_path = os.path.join(repo_root, subtree)
            if not os.path.isdir(subtree_path):
                continue
            for dirpath, _, filenames in os.walk(subtree_path):
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    fp = os.path.join(dirpath, fn)
                    leaked = self._collect_imports(fp) & self.ME_MODULE_NAMES
                    if leaked:
                        rel = os.path.relpath(fp, repo_root)
                        offenders.append((rel, sorted(leaked)))

        self.assertEqual(
            offenders,
            [],
            "Vendored subtrees must not import Math-Econ modules. "
            "Offenders: " + ", ".join(f"{f} imports {mods}" for f, mods in offenders),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
