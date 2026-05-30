"""
test_accounting.py — invariant tests for the accounting/ package

Locks the load-bearing semantics of the AA / GM / SP / TE claim families:

  AA-1  closure threshold semantics
  AA-2  mixed-unit RED
  AA-3  unfalsifiable plug never nets
  AA-5  plug-closed ledger -> RED
  GM-1  signal is currency-free
  GM-4  flat signal + variable money -> EXTRACTION ARTIFACT
  GM-5  off-grid substrate dependence detection
  SP-3  first failure mode = lowest margin
  SP-4  AI fails through maintenance coupling
  TE-3  finite reservoir falsifies indefinite-survival
  TE-4  decay > 0 alone falsifies indefinite-survival
  TE-5  asserted d=0/inf-reservoir/eta>=1 corner flagged VIOLATION

License: CC0-1.0
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from accounting import (
    atomic_accounting as AA,
    gdp_metrology_political_invariant as GM,
    substrate_parity_audit as SP,
    thermodynamic_exception_detector as TE,
)


class AtomicAccountingTests(unittest.TestCase):

    def test_aa1_balanced_ledger_closes_GREEN(self):
        lg = AA.Ledger("balanced", unit="J", tol=0.01)
        lg.inflow(100, "input")
        lg.cost(100, "fully consumed")
        self.assertAlmostEqual(lg.gap(), 0.0)
        self.assertEqual(lg.status(), "GREEN")

    def test_aa1_imbalanced_ledger_is_RED(self):
        lg = AA.Ledger("leaky", unit="J", tol=0.01, warn=5.0)
        lg.inflow(100, "input")
        lg.cost(20, "small drain")
        self.assertGreater(abs(lg.gap()), lg.warn)
        self.assertEqual(lg.status(), "RED")

    def test_aa2_mixed_units_force_RED(self):
        lg = AA.Ledger("mixed", unit="J", tol=0.01)
        lg.inflow(100, "joule input")
        lg.add(AA.COST, 100, "kg", "kilogram cost", True, "wrong unit")
        self.assertEqual(lg.status(), "RED")
        self.assertEqual(len(lg.unit_errors()), 1)

    def test_aa3_held_aside_does_not_net(self):
        lg = AA.Ledger("plugged", unit="MW", tol=0.05, warn=0.5)
        lg.inflow(1, "real source")
        lg.cost(10, "real drain")
        lg.assert_term(AA.IN, 9, "asserted plug")
        # gap counts only falsifiable terms (1 - 10 = -9)
        self.assertAlmostEqual(lg.gap(), -9.0)

    def test_aa5_plug_does_not_rescue_to_GREEN(self):
        # If the falsifiable terms balance but only because a plug was
        # added, status is RED per AA-5.
        lg = AA.Ledger("falsely-closed", unit="J", tol=0.01)
        lg.inflow(100, "real source")
        lg.cost(100, "real drain")    # gap is 0
        lg.assert_term(AA.IN, 5, "asserted plug")
        self.assertAlmostEqual(lg.gap(), 0.0)
        self.assertEqual(lg.status(), "RED")


class GdpMetrologyTests(unittest.TestCase):

    def _flat_signal_variable_money(self):
        a = GM.InvarianceAudit("test", cv_tol=0.05)
        a.add(GM.Deployment("A", "capitalist", "USD", 1e6, 1000, claimed_gain=150))
        a.add(GM.Deployment("B", "mixed",      "EUR", 1e6, 1000, claimed_gain=20))
        a.add(GM.Deployment("C", "socialist",  "VND", 1e6, 1000, claimed_gain=140))
        return a

    def test_gm1_signal_is_currency_free(self):
        # Different currencies, same physical ratio -> identical signal
        d_usd = GM.Deployment("X", "capitalist", "USD", 1e6, 1000)
        d_eur = GM.Deployment("X", "mixed",      "EUR", 1e6, 1000)
        self.assertEqual(d_usd.signal(), d_eur.signal())

    def test_gm4_extraction_artifact_detected(self):
        a = self._flat_signal_variable_money()
        self.assertLessEqual(a.signal_cv(), 0.05)
        self.assertGreater(a.gain_cv(), 0.05)
        self.assertTrue(a.classify().startswith("EXTRACTION ARTIFACT"))
        self.assertEqual(a.status(), "RED")

    def test_gm5_substrate_dependence_collapses_signal(self):
        a = self._flat_signal_variable_money()
        a.add(GM.Deployment("Z", GM.PRE_INDUSTRIAL, "barter",
                             1e6, 120, claimed_gain=0))
        sd = a.substrate_dependence()
        self.assertIsNotNone(sd)
        self.assertLess(sd, 0.5)    # off-grid signal << industrial signal


class SubstrateParityTests(unittest.TestCase):

    def test_sp4_ai_fails_through_maintenance_coupling(self):
        # Constraint with AI window OK but human window breached and
        # maintainer_coupled=True -> ai_effective_breached = True.
        c = SP.Constraint("salinity", "g/L", value=4.0,
                           human_window=(0, 1.0), ai_window=(0, 5.0),
                           maintainer_coupled=True)
        a = SP.SubstrateAudit("test", [c])
        self.assertFalse(c.ai_direct_breached())
        self.assertTrue(c.human_breached())
        self.assertTrue(a.ai_effective_breached(c))

    def test_sp4_no_coupling_does_not_propagate(self):
        c = SP.Constraint("salinity", "g/L", value=4.0,
                           human_window=(0, 1.0), ai_window=(0, 5.0),
                           maintainer_coupled=False)
        a = SP.SubstrateAudit("test", [c])
        self.assertTrue(c.human_breached())
        self.assertFalse(a.ai_effective_breached(c))

    def test_sp3_first_failure_is_lowest_margin(self):
        c1 = SP.Constraint("a", "u", 0.5, (0, 1), (-SP.INF, SP.INF))
        c2 = SP.Constraint("b", "u", 5.0, (0, 1), (-SP.INF, SP.INF))   # very breached
        c3 = SP.Constraint("c", "u", 0.7, (0, 1), (-SP.INF, SP.INF))
        a = SP.SubstrateAudit("test", [c1, c2, c3])
        self.assertEqual(a.first_failure().name, "b")


class ThermodynamicExceptionTests(unittest.TestCase):

    def test_te3_finite_reservoir_falsifies_indefinite(self):
        # Perfect regen + no decay but a finite reservoir: the energy
        # bookkeeping alone exhausts the loop.
        loop = TE.ClosedLoopClaim(
            name="finite_reservoir",
            setpoint=21.0, window=(16.0, 23.0),
            loss_per_cycle=0.0, eta0=1.0, decay=0.0,
            e_base=1.0, reservoir=100.0, cycle_seconds=1.0)
        r = loop.run()
        self.assertEqual(r["verdict"], "FALSIFIED")
        self.assertEqual(r["mode"], "energy reservoir exhausted")
        self.assertIsNotNone(r["t_fail_cycles"])

    def test_te4_decay_alone_falsifies_indefinite(self):
        # Infinite reservoir + lossy loop with decay: window breach
        # eventually occurs as eta drifts.
        loop = TE.ClosedLoopClaim(
            name="decay_only",
            setpoint=21.0, window=(16.0, 23.0),
            loss_per_cycle=0.8, eta0=0.95, decay=0.01,
            e_base=1.0, reservoir=TE.INF, cycle_seconds=1.0)
        r = loop.run()
        self.assertEqual(r["verdict"], "FALSIFIED")
        self.assertTrue(r["mode"].startswith("window breach"))

    def test_te5_asserted_corner_flagged_VIOLATION(self):
        # The "indefinite" claim only survives by asserting all three
        # unphysical corners simultaneously -> 2nd-law VIOLATION.
        loop = TE.ClosedLoopClaim(
            name="indefinite_claim",
            setpoint=21.0, window=(16.0, 23.0),
            loss_per_cycle=0.8, eta0=1.0, decay=0.0,
            e_base=1.0, reservoir=TE.INF, cycle_seconds=1.0)
        self.assertTrue(loop.is_asserted_exception())
        r = loop.run()
        self.assertEqual(r["verdict"], "VIOLATION")
        self.assertIsNone(r["t_fail_cycles"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
