"""
test_automation_scope_audit.py

Smoke + invariant tests for automation_scope_audit. Two layers:

  1. Module standalone runnability — every module's `if __name__ ==
     '__main__':` block executes without exception.
  2. Scenario invariants — works case and fails case produce expected
     discrimination patterns. Specifically: every claim has a verdict,
     every verdict has a threshold_met (or scope_collapse_detected for
     C006), and the cluster report fires fewer clusters on the works
     case than on the fails case.

Run:
    python tests/test_automation_scope_audit.py

License: CC0-1.0
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from automation_scope_audit.examples import (
    kodiak_atlas_permian, dispersed_wellsite)
from automation_scope_audit import correlation
from automation_scope_audit.modules import scope_gate


CLAIM_IDS = ["C000"] + [f"C{n:03d}" for n in range(1, 49)]


class ScopeGateTests(unittest.TestCase):

    def test_empty_spec_blocked(self):
        v = scope_gate.scope_gate_verdict({})
        self.assertFalse(v["admissible"])
        # 8 required fields: 7 declarative + substrate_primacy_fraction
        self.assertEqual(len(v["missing"]), 8)

    def test_complete_spec_admitted(self):
        spec = {
            "beneficiary":        "per_ton_mile_energy_efficiency",
            "conditions":         ["stable_diesel"],
            "time_period":        "7yr_lifecycle",
            "resource":           "diesel_energy_joules",
            "externalized_cost":  "rural_road_maintenance_to_state_DOT",
            "profit_allocation":  ["operator_60pct"],
            "falsifier":          "fuel_intensity_increase_post_deployment",
            "substrate_primacy_fraction": 0.30,
        }
        v = scope_gate.scope_gate_verdict(spec)
        self.assertTrue(v["admissible"], msg=v["missing"])

    def test_one_word_value_rejected(self):
        spec = {f: "yes" for f in scope_gate.REQUIRED_SPEC_FIELDS}
        v = scope_gate.scope_gate_verdict(spec)
        # short string -> non-measurable
        self.assertFalse(v["admissible"])

    def test_deliberate_open_sentinel_accepted_except_substrate(self):
        # 7 declarative fields accept "unspecified"; substrate_primacy_fraction
        # cannot use a sentinel because it must be a positive number.
        spec = {f: "unspecified" for f in scope_gate.REQUIRED_SPEC_FIELDS
                if f != "substrate_primacy_fraction"}
        spec["substrate_primacy_fraction"] = 0.50
        v = scope_gate.scope_gate_verdict(spec)
        self.assertTrue(v["admissible"], msg=v["missing"])

    def test_zero_substrate_primacy_blocks_admission(self):
        spec = {f: "fully specified value text" for f in scope_gate.REQUIRED_SPEC_FIELDS}
        spec["substrate_primacy_fraction"] = 0.0
        v = scope_gate.scope_gate_verdict(spec)
        self.assertFalse(v["admissible"])
        self.assertIn("substrate_primacy_fraction", v["missing"])


class WorksCaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.report = kodiak_atlas_permian.run()

    def test_all_claims_evaluated(self):
        for cid in CLAIM_IDS:
            self.assertIn(cid, self.report, msg=f"missing {cid}")

    def test_every_verdict_has_threshold(self):
        for cid in CLAIM_IDS:
            v = self.report[cid]
            has = ("threshold_met" in v) or ("scope_collapse_detected" in v)
            self.assertTrue(has, msg=f"{cid} has no threshold flag: {v}")

    def test_c001_fixed_corridor_below_threshold(self):
        c001 = self.report["C001"]
        self.assertLess(c001["variance"], 0.05)
        self.assertEqual(c001["tier"], "fixed")
        self.assertTrue(c001["threshold_met"])

    def test_c003_consolidated_corridor_under_500k_per_mile(self):
        # Atlas-style: most infrastructure already present
        c003 = self.report["C003"]
        self.assertLess(c003["per_route_mile_usd"], 500_000.0)
        self.assertFalse(c003["threshold_met"])

    def test_c021_below_optimum_does_not_register(self):
        # 60-truck fleet is far below the scaling optimum (~970)
        c021 = self.report["C021"]
        self.assertFalse(c021["above_optimum"])


class FailsCaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.report = dispersed_wellsite.run()

    def test_all_claims_evaluated(self):
        for cid in CLAIM_IDS:
            self.assertIn(cid, self.report)

    def test_c001_dispersed_routes_above_chaotic_threshold(self):
        c001 = self.report["C001"]
        self.assertGreaterEqual(c001["variance"], 0.20)
        self.assertIn(c001["tier"], {"variable", "chaotic"})
        self.assertFalse(c001["threshold_met"])

    def test_c003_dispersed_capex_dominates_fleet_cost(self):
        c003 = self.report["C003"]
        self.assertGreater(c003["per_route_mile_usd"], 500_000.0)
        self.assertTrue(c003["threshold_met"])

    def test_c020_honest_eroi_below_threshold(self):
        c020 = self.report["C020"]
        self.assertLess(c020["honest_eroi"], 1.5)
        self.assertTrue(c020["threshold_met"])


class ClusterTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.works = kodiak_atlas_permian.run()
        cls.fails = dispersed_wellsite.run()
        cls.works_clusters = correlation.detect_clusters(cls.works)
        cls.fails_clusters = correlation.detect_clusters(cls.fails)

    def test_fails_case_fires_more_clusters_than_works(self):
        self.assertGreater(
            len(self.fails_clusters["triggered_clusters"]),
            len(self.works_clusters["triggered_clusters"]),
            msg="fails case should trigger strictly more clusters than works")

    def test_fails_case_fires_infrastructure_inadequacy(self):
        self.assertIn("infrastructure_inadequacy_cluster",
                       self.fails_clusters["triggered_clusters"])

    def test_works_case_does_not_fire_infrastructure_inadequacy(self):
        self.assertNotIn("infrastructure_inadequacy_cluster",
                          self.works_clusters["triggered_clusters"])


class ContractValidatedTests(unittest.TestCase):

    def test_fab_table_round_trips(self):
        from schemas.claim_contract import Claim, CONTRACT_VERSION
        path = os.path.join(ROOT, "automation_scope_audit",
                             "CLAIM_TABLE.fab.json")
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(data["contract_version"], CONTRACT_VERSION)
        for cid, payload in data["claims"].items():
            claim = Claim.from_dict(payload)
            roundtrip = Claim.from_dict(claim.to_dict())
            self.assertEqual(claim, roundtrip,
                              msg=f"round-trip mismatch for {cid}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
